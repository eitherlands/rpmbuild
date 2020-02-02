%global _hardened_build 1
%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}}

%define GPG_CHECK 1
%define VERSION 5.0.0
%define repodir %{_builddir}/%{name}-%{version}
%define NINJA ninja-build

Name:           knot-resolver
Version:        %{VERSION}
Release:        1%{?dist}
Summary:        Caching full DNS Resolver

License:        GPLv3
URL:            https://www.knot-resolver.cz/
Source0:        https://secure.nic.cz/files/%{name}/%{name}-%{version}.tar.xz

# LuaJIT only on these arches
%if 0%{?rhel}
# RHEL 7 does not have aarch64 LuaJIT
ExclusiveArch:	%{ix86} x86_64
%else
ExclusiveArch:	%{arm} aarch64 %{ix86} x86_64
%endif

%if 0%{GPG_CHECK}
Source1:        https://secure.nic.cz/files/%{name}/%{name}-%{version}.tar.xz.asc
# PGP keys used to sign upstream releases
# Export with --armor using command from https://fedoraproject.org/wiki/PackagingDrafts:GPGSignatures
# Don't forget to update %%prep section when adding/removing keys
Source100:	gpgkey-B6006460B60A80E782062449E747DF1F9575A3AA.gpg.asc
Source101:	gpgkey-BE26EBB9CBE059B3910CA35BCE8DD6A1A50A21E4.gpg.asc
Source102:	gpgkey-4A8BA48C2AED933BD495C509A1FBA5F7EF8C4869.gpg.asc
BuildRequires:  gnupg2
%endif

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  meson
BuildRequires:  pkgconfig(cmocka)
BuildRequires:  pkgconfig(gnutls)
BuildRequires:  pkgconfig(libedit)
BuildRequires:  pkgconfig(libknot) >= 2.8
BuildRequires:  pkgconfig(libzscanner) >= 2.8
BuildRequires:  pkgconfig(libdnssec) >= 2.8
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(libcap-ng)
BuildRequires:  pkgconfig(libuv)
BuildRequires:  pkgconfig(luajit) >= 2.0

Requires:       systemd
Requires(post): systemd

# Distro-dependent dependencies
%if 0%{?rhel}
BuildRequires:  lmdb-devel
# Lua 5.1 version of the libraries have different package names
Requires:       lua-basexx
Requires:       lua-psl
Requires:       lua-http
Requires(pre):  shadow-utils
%endif
%if 0%{?fedora}
BuildRequires:  pkgconfig(lmdb)
BuildRequires:  python3-sphinx
Requires:       lua5.1-basexx
Requires:       lua5.1-cqueues
Requires:       lua5.1-http
Recommends:     lua5.1-psl
Requires(pre):  shadow-utils
%endif

# we do not build HTTP module on SuSE so the build requires is not needed
%if "x%{?suse_version}" == "x"
BuildRequires:  openssl-devel
%endif

%if 0%{?suse_version}
%define NINJA ninja
BuildRequires:  lmdb-devel
BuildRequires:  python3-Sphinx
Requires(pre):  shadow
%endif

%if "x%{?rhel}" == "x"
# dependencies for doc package
# NOTE: doc isn't possible to build on CentOS 7
#       python2-sphinx is too old and python36-breathe is broken
BuildRequires:  doxygen
BuildRequires:  python3-breathe
BuildRequires:  python3-sphinx_rtd_theme
%endif

%description
The Knot Resolver is a DNSSEC-enabled caching full resolver implementation
written in C and LuaJIT, including both a resolver library and a daemon.
Modular architecture of the library keeps the core tiny and efficient, and
provides a state-machine like API for extensions.

The package is pre-configured as local caching resolver.
To start using it, start a single kresd instance:
$ systemctl start kresd@1.service

%package devel
Summary:        Development headers for Knot Resolver
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The package contains development headers for Knot Resolver.

%if "x%{?rhel}" == "x"
%package doc
Summary:        Documentation for Knot Resolver
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}

%description doc
Documentation for Knot Resolver
%endif

%if "x%{?suse_version}" == "x"
%package module-http
Summary:        HTTP/2 module for Knot Resolver
Requires:       %{name} = %{version}-%{release}
%if 0%{?fedora}
Requires:       lua5.1-http
Requires:       lua5.1-mmdb
%else
Requires:       lua-http
Requires:       lua-mmdb
%endif

%description module-http
HTTP/2 module for Knot Resolver has multiple uses. It enables use of
DNS-over-HTTP, can serve as API ednpoint for other modules or provide a web
interface for local visualization of the resolver cache and queries.
%endif

%prep
%if 0%{GPG_CHECK}
export GNUPGHOME=./gpg-keyring
mkdir ${GNUPGHOME}
gpg2 --import %{SOURCE100} %{SOURCE101} %{SOURCE102}
gpg2 --verify %{SOURCE1} %{SOURCE0}
%endif
%setup -q -n %{name}-%{version}

%build
CFLAGS="%{optflags}" LDFLAGS="%{?__global_ldflags}" meson build_rpm \
%if "x%{?rhel}" == "x"
    -Ddoc=enabled \
%endif
    -Dsystemd_files=enabled \
    -Dclient=enabled \
    -Dunit_tests=enabled \
    -Dmanaged_ta=enabled \
    -Dkeyfile_default="%{_sharedstatedir}/knot-resolver/root.keys" \
    -Dinstall_root_keys=enabled \
    -Dinstall_kresd_conf=enabled \
    --buildtype=plain \
    --prefix="%{_prefix}" \
    --sbindir="%{_sbindir}" \
    --libdir="%{_libdir}" \
    --includedir="%{_includedir}" \
    --sysconfdir="%{_sysconfdir}" \

%{NINJA} -v -C build_rpm
%if "x%{?rhel}" == "x"
%{NINJA} -v -C build_rpm doc
%endif

%check
meson test -C build_rpm

%install
DESTDIR="${RPM_BUILD_ROOT}" %{NINJA} -v -C build_rpm install

# add kresd.target to multi-user.target.wants to support enabling kresd services
install -m 0755 -d %{buildroot}%{_unitdir}/multi-user.target.wants
ln -s ../kresd.target %{buildroot}%{_unitdir}/multi-user.target.wants/kresd.target

# remove modules with missing dependencies
rm %{buildroot}%{_libdir}/knot-resolver/kres_modules/etcd.lua

%if 0%{?suse_version}
rm %{buildroot}%{_libdir}/knot-resolver/kres_modules/experimental_dot_auth.lua
rm -r %{buildroot}%{_libdir}/knot-resolver/kres_modules/http
rm %{buildroot}%{_libdir}/knot-resolver/kres_modules/http*.lua
rm %{buildroot}%{_libdir}/knot-resolver/kres_modules/prometheus.lua
%endif

# # rename doc directory for centos, opensuse
# %if "x%{?fedora}" == "x"
# install -m 755 -d %{buildroot}/%{_pkgdocdir}
# mv %{buildroot}/%{_datadir}/doc/%{name}/* %{buildroot}/%{_pkgdocdir}/
# %endif

%pre
getent group knot-resolver >/dev/null || groupadd -r knot-resolver
getent passwd knot-resolver >/dev/null || useradd -r -g knot-resolver -d %{_sysconfdir}/knot-resolver -s /sbin/nologin -c "Knot Resolver" knot-resolver

%if "x%{?rhel}" == "x"
# upgrade-4-to-5
if [ -f %{_unitdir}/kresd.socket ] ; then
	export UPG_DIR=%{_sharedstatedir}/knot-resolver/.upgrade-4-to-5
	mkdir -p ${UPG_DIR}
	touch ${UPG_DIR}/.unfinished

	for sock in kresd.socket kresd-tls.socket kresd-webmgmt.socket kresd-doh.socket ; do
		if systemctl is-enabled ${sock} 2>/dev/null | grep -qv masked ; then
			systemctl show ${sock} -p Listen > ${UPG_DIR}/${sock}
			case "$(systemctl show ${sock} -p BindIPv6Only)" in
			*ipv6-only)
				touch ${UPG_DIR}/${sock}.v6only
				;;
			*default)
				if cat /proc/sys/net/ipv6/bindv6only | grep -q 1 ; then
					touch ${UPG_DIR}/${sock}.v6only
				fi
				;;
			esac
		fi
	done
fi
%endif


%post
# upgrade-4-to-5
%if "x%{?rhel}" == "x"
export UPG_DIR=%{_sharedstatedir}/knot-resolver/.upgrade-4-to-5
if [ -f ${UPG_DIR}/.unfinished ] ; then
	rm -f ${UPG_DIR}/.unfinished
	kresd -c %{_libdir}/knot-resolver/upgrade-4-to-5.lua &>/dev/null
	echo -e "\n   !!! WARNING !!!"
	echo -e "Knot Resolver configuration file requires manual upgrade.\n"
	cat ${UPG_DIR}/kresd.conf.net 2>/dev/null
fi
%endif

# in case service files are updated
systemctl daemon-reload &>/dev/null ||:
%systemd_post 'kresd@*.service'
%tmpfiles_create %{_tmpfilesdir}/knot-resolver.conf
%if "x%{?fedora}" == "x"
/sbin/ldconfig
%endif

%preun
%systemd_preun kres-cache-gc.service kresd.target

%postun
%systemd_postun_with_restart 'kresd@*.service'
%if "x%{?fedora}" == "x"
/sbin/ldconfig
%endif

%files
%dir %{_pkgdocdir}
%license %{_pkgdocdir}/COPYING
%doc %{_pkgdocdir}/AUTHORS
%doc %{_pkgdocdir}/NEWS
%doc %{_pkgdocdir}/examples
%attr(755,root,knot-resolver) %dir %{_sysconfdir}/knot-resolver
%attr(644,root,knot-resolver) %config(noreplace) %{_sysconfdir}/knot-resolver/kresd.conf
%attr(644,root,knot-resolver) %config(noreplace) %{_sysconfdir}/knot-resolver/root.hints
%attr(644,root,knot-resolver) %{_sysconfdir}/knot-resolver/icann-ca.pem
%attr(775,root,knot-resolver) %dir %{_sharedstatedir}/knot-resolver
%attr(664,root,knot-resolver) %{_sharedstatedir}/knot-resolver/root.keys
%{_unitdir}/kresd@.service
%{_unitdir}/kres-cache-gc.service
%{_unitdir}/kresd.target
%dir %{_unitdir}/multi-user.target.wants
%{_unitdir}/multi-user.target.wants/kresd.target
%{_mandir}/man7/kresd.systemd.7.gz
%{_tmpfilesdir}/knot-resolver.conf
%ghost /run/%{name}
%ghost %{_localstatedir}/cache/%{name}
%attr(750,knot-resolver,knot-resolver) %dir %{_libdir}/%{name}
%{_sbindir}/kresd
%{_sbindir}/kresc
%{_sbindir}/kres-cache-gc
%{_libdir}/libkres.so.*
%dir %{_libdir}/knot-resolver
%{_libdir}/knot-resolver/*.so
%{_libdir}/knot-resolver/*.lua
%dir %{_libdir}/knot-resolver/kres_modules
%{_libdir}/knot-resolver/kres_modules/*.so
%{_libdir}/knot-resolver/kres_modules/daf
%{_libdir}/knot-resolver/kres_modules/daf.lua
%{_libdir}/knot-resolver/kres_modules/detect_time_jump.lua
%{_libdir}/knot-resolver/kres_modules/detect_time_skew.lua
%{_libdir}/knot-resolver/kres_modules/dns64.lua
%if "x%{?suse_version}" == "x"
%{_libdir}/knot-resolver/kres_modules/experimental_dot_auth.lua
%endif
%{_libdir}/knot-resolver/kres_modules/graphite.lua
%{_libdir}/knot-resolver/kres_modules/policy.lua
%{_libdir}/knot-resolver/kres_modules/predict.lua
%{_libdir}/knot-resolver/kres_modules/prefill.lua
%{_libdir}/knot-resolver/kres_modules/priming.lua
%{_libdir}/knot-resolver/kres_modules/rebinding.lua
%{_libdir}/knot-resolver/kres_modules/renumber.lua
%{_libdir}/knot-resolver/kres_modules/serve_stale.lua
%{_libdir}/knot-resolver/kres_modules/ta_sentinel.lua
%{_libdir}/knot-resolver/kres_modules/ta_signal_query.lua
%{_libdir}/knot-resolver/kres_modules/ta_update.lua
%{_libdir}/knot-resolver/kres_modules/view.lua
%{_libdir}/knot-resolver/kres_modules/watchdog.lua
%{_libdir}/knot-resolver/kres_modules/workarounds.lua
%{_mandir}/man8/kresd.8.gz

%files devel
%{_includedir}/libkres
%{_libdir}/pkgconfig/libkres.pc
%{_libdir}/libkres.so

%if "x%{?rhel}" == "x"
%files doc
%dir %{_pkgdocdir}
%doc %{_pkgdocdir}/html
%endif

%if "x%{?suse_version}" == "x"
%files module-http
%{_libdir}/knot-resolver/debug_opensslkeylog.so
%{_libdir}/knot-resolver/kres_modules/http
%{_libdir}/knot-resolver/kres_modules/http*.lua
%{_libdir}/knot-resolver/kres_modules/prometheus.lua
%endif

%changelog
* Mon Jan 27 2020 Tomas Krizek <tomas.krizek@nic.cz> - 5.0.0-1
- update to new upstream version 5.0.0
- removed systemd socket files (no longer supported)
- add upgrade scriptlets for 5.x
- remove lua-sec, lua-socket, lua-filesystem dependencies
- create tmpfiles dirs with macro

* Wed Dec 04 2019 Tomas Krizek <tomas.krizek@nic.cz> - 4.3.0-1
- update to new upstream version 4.3.0
- make config directory read-only for knot-resolver, relocate root.keys to /var/lib
- http module now depends on the exact same binary version of knot-resolver

* Tue Nov 12 2019 Tomas Krizek <tomas.krizek@nic.cz> - 4.2.2-2
- rebuild for libknot10 (Knot DNS 2.9.1)

* Mon Oct 07 2019 Tomas Krizek <tomas.krizek@nic.cz> - 4.2.2-1
- update to new upstream version 4.2.2

* Thu Sep 26 2019 Tomas Krizek <tomas.krizek@nic.cz> - 4.2.1-1
- update to new upstream version 4.2.1

* Wed Aug 21 2019 Tomas Krizek <tomas.krizek@nic.cz> - 4.2.0-1
- update to new upstream version 4.2.0
- added lua-psl dependency for policy.slice() functionality

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 4.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jul 10 2019 Tomas Krizek <tomas.krizek@nic.cz> - 4.1.0-1
- update to new upstream version 4.1.0
- add kres-cache-gc.service

* Wed May 29 2019 Tomas Krizek <tomas.krizek@nic.cz> - 4.0.0.-1
- rebase to new upstream release 4.0.0
- bump Knot DNS libraries to 2.8 (ABI compat)
- use new upstream build system - meson
- add knot-resolver-module-http package along with new lua dependecies

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Jan 10 2019 Tomas Krizek <tomas.krizek@nic.cz> - 3.2.1-1
Knot Resolver 3.2.1 (2019-01-10)
================================

Bugfixes
--------
- trust_anchors: respect validity time range during TA bootstrap (!748)
- fix TLS rehandshake handling (!739)
- make TLS_FORWARD compatible with GnuTLS 3.3 (!741)
- special thanks to Grigorii Demidov for his long-term work on Knot Resolver!

Improvements
------------
- improve handling of timeouted outgoing TCP connections (!734)
- trust_anchors: check syntax of public keys in DNSKEY RRs (!748)
- validator: clarify message about bogus non-authoritative data (!735)
- dnssec validation failures contain more verbose reasoning (!735)
- new function trust_anchors.summary() describes state of DNSSEC TAs (!737),
  and logs new state of trust anchors after start up and automatic changes
- trust anchors: refuse revoked DNSKEY even if specified explicitly,
  and downgrade missing the SEP bit to a warning


* Mon Dec 17 2018 Tomas Krizek <tomas.krizek@nic.cz> - 3.2.0-1
Knot Resolver 3.2.0 (2018-12-17)
================================

New features
------------
- module edns_keepalive to implement server side of RFC 7828 (#408)
- module nsid to implement server side of RFC 5001 (#289)
- module bogus_log provides .frequent() table (!629, credit Ulrich Wisser)
- module stats collects flags from answer messages (!629, credit Ulrich Wisser)
- module view supports multiple rules with identical address/TSIG specification
  and keeps trying rules until a "non-chain" action is executed (!678)
- module experimental_dot_auth implements an DNS-over-TLS to auth protocol
  (!711, credit Manu Bretelle)
- net.bpf bindings allow advanced users to use eBPF socket filters

Bugfixes
--------
- http module: only run prometheus in parent process if using --forks=N,
  as the submodule collects metrics from all sub-processes as well.
- TLS fixes for corner cases (!700, !714, !716, !721, !728)
- fix build with -DNOVERBOSELOG (#424)
- policy.{FORWARD,TLS_FORWARD,STUB}: respect net.ipv{4,6} setting (!710)
- avoid SERVFAILs due to certain kind of NS dependency cycles, again
  (#374) this time seen as 'circular dependency' in verbose logs
- policy and view modules do not overwrite result finished requests (!678)

Improvements
------------
- Dockerfile: rework, basing on Debian instead of Alpine
- policy.{FORWARD,TLS_FORWARD,STUB}: give advantage to IPv6
  when choosing whom to ask, just as for iteration
- use pseudo-randomness from gnutls instead of internal ISAAC (#233)
- tune the way we deal with non-responsive servers (!716, !723)
- documentation clarifies interaction between policy and view modules (!678, !730)

Module API changes
------------------
- new layer is added: answer_finalize
- kr_request keeps ::qsource.packet beyond the begin layer
- kr_request::qsource.tcp renamed to ::qsource.flags.tcp
- kr_request::has_tls renamed to ::qsource.flags.tls
- kr_zonecut_add(), kr_zonecut_del() and kr_nsrep_sort() changed parameters slightly


* Fri Nov 02 2018 Tomas Krizek <tomas.krizek@nic.cz> - 3.1.0-1
Knot Resolver 3.1.0 (2018-11-02)
================================

Incompatible changes
--------------------
- hints.use_nodata(true) by default; that's what most users want
- libknot >= 2.7.2 is required

Improvements
------------
- cache: handle out-of-space SIGBUS slightly better (#197)
- daemon: improve TCP timeout handling (!686)

Bugfixes
--------
- cache.clear('name'): fix some edge cases in API (#401)
- fix error handling from TLS writes (!669)
- avoid SERVFAILs due to certain kind of NS dependency cycles (#374)

* Mon Aug 20 2018 Tomas Krizek <tomas.krizek@nic.cz> - 3.0.0-1
Knot Resolver 3.0.0 (2018-08-20)
================================

Incompatible changes
--------------------
- cache: fail lua operations if cache isn't open yet (!639)
  By default cache is opened *after* reading the configuration,
  and older versions were silently ignoring cache operations.
  Valid configuration must open cache using `cache.open()` or `cache.size =`
  before executing cache operations like `cache.clear()`.
- libknot >= 2.7.1 is required, which brings also larger API changes
- in case you wrote custom Lua modules, please consult
  https://knot-resolver.readthedocs.io/en/latest/lib.html#incompatible-changes-since-3-0-0
- in case you wrote custom C modules, please see compile against
  Knot DNS 2.7 and adjust your module according to messages from C compiler
- DNS cookie module (RFC 7873) is not available in this release,
  it will be later reworked to reflect development in IEFT dnsop working group
- version module was permanently removed because it was not really used by users;
  if you want to receive notifications abou new releases please subscribe to
  https://lists.nic.cz/cgi-bin/mailman/listinfo/knot-resolver-announce

Bugfixes
--------
- fix multi-process race condition in trust anchor maintenance (!643)
- ta_sentinel: also consider static trust anchors not managed via RFC 5011

Improvements
------------
- reorder_RR() implementation is brought back
- bring in performace improvements provided by libknot 2.7
- cache.clear() has a new, more powerful API
- cache documentation was improved
- old name "Knot DNS Resolver" is replaced by unambiguous "Knot Resolver"
  to prevent confusion with "Knot DNS" authoritative server

* Thu Aug 02 2018 Tomas Krizek <tomas.krizek@nic.cz> - 2.4.1-1
Knot Resolver 2.4.1 (2018-08-02)
================================

Security
--------
- fix CVE-2018-10920: Improper input validation bug in DNS resolver component
  (security!7, security!9)

Bugfixes
--------
- cache: fix TTL overflow in packet due to min_ttl (#388, security!8)
- TLS session resumption: avoid bad scheduling of rotation (#385)
- HTTP module: fix a regression in 2.4.0 which broke custom certs (!632)
- cache: NSEC3 negative cache even without NS record (#384)
  This fixes lower hit rate in NSEC3 zones (since 2.4.0).
- minor TCP and TLS fixes (!623, !624, !626)


* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jul 03 2018 Tomas Krizek <tomas.krizek@nic.cz> - 2.4.0-1
Knot Resolver 2.4.0 (2018-07-03)
================================

Incompatible changes
--------------------
- minimal libknot version is now 2.6.7 to pull in latest fixes (#366)

Security
--------
- fix a rare case of zones incorrectly dowgraded to insecure status (!576)

New features
------------
- TLS session resumption (RFC 5077), both server and client (!585, #105)
  (disabled when compiling with gnutls < 3.5)
- TLS_FORWARD policy uses system CA certificate store by default (!568)
- aggressive caching for NSEC3 zones (!600)
- optional protection from DNS Rebinding attack (module rebinding, !608)
- module bogus_log to log DNSSEC bogus queries without verbose logging (!613)

Bugfixes
--------
- prefill: fix ability to read certificate bundle (!578)
- avoid turning off qname minimization in some cases, e.g. co.uk. (#339)
- fix validation of explicit wildcard queries (#274)
- dns64 module: more properties from the RFC implemented (incl. bug #375)

Improvements
------------
- systemd: multiple enabled kresd instances can now be started using kresd.target
- ta_sentinel: switch to version 14 of the RFC draft (!596)
- support for glibc systems with a non-Linux kernel (!588)
- support per-request variables for Lua modules (!533)
- support custom HTTP endpoints for Lua modules (!527)


* Mon Apr 23 2018 Tomas Krizek <tomas.krizek@nic.cz> - 2.3.0-1
Knot Resolver 2.3.0 (2018-04-23)
================================

Security
--------
- fix CVE-2018-1110: denial of service triggered by malformed DNS messages
  (!550, !558, security!2, security!4)
- increase resilience against slow lorris attack (security!5)

Bugfixes
--------
- validation: fix SERVFAIL in case of CNAME to NXDOMAIN in a single zone (!538)
- validation: fix SERVFAIL for DS . query (!544)
- lib/resolve: don't send unecessary queries to parent zone (!513)
- iterate: fix validation for zones where parent and child share NS (!543)
- TLS: improve error handling and documentation (!536, !555, !559)

Improvements
------------
- prefill: new module to periodically import root zone into cache
  (replacement for RFC 7706, !511)
- network_listen_fd: always create end point for supervisor supplied file descriptor
- use CPPFLAGS build environment variable if set (!547)


* Wed Mar 28 2018 Tomas Krizek <tomas.krizek@nic.cz> - 2.2.0-1
Knot Resolver 2.2.0 (2018-03-28)
================================

New features
------------
- cache server unavailability to prevent flooding unreachable servers
  (Please note that caching algorithm needs further optimization
   and will change in further versions but we need to gather operational
   experience first.)

Bugfixes
--------
- don't magically -D_FORTIFY_SOURCE=2 in some cases
- allow large responses for outbound over TCP
- fix crash with RR sets with over 255 records


* Mon Feb 26 2018 Tomas Krizek <tomas.krizek@nic.cz> - 2.1.1-1
Knot Resolver 2.1.1 (2018-02-23)
================================

Bugfixes
--------
- when iterating, avoid unnecessary queries for NS in insecure parent.
  This problem worsened in 2.0.0. (#246)
- prevent UDP packet leaks when using TLS forwarding
- fix the hints module also on some other systems, e.g. Gentoo.

* Fri Feb 16 2018 Tomas Krizek <tomas.krizek@nic.cz> - 2.1.0-1
- New upstream release 2.1.0

Knot Resolver 2.1.0 (2018-02-16)
================================

Incompatible changes
--------------------
- stats: remove tracking of expiring records (predict uses another way)
- systemd: more chages in default unit files (TODO)
- ta_sentinel: implement protocol draft-ietf-dnsop-kskroll-sentinel-01
  (our draft-ietf-dnsop-kskroll-sentinel-00 implementation had inverted logic)
- libknot: require version 2.6.4 or newer to get bugfixes for DNS-over-TLS

Bugfixes
--------
- detect_time_jump module: don't clear cache on suspend-resume (#284)
- stats module: fix stats.list() returning nothing, regressed in 2.0.0
- policy.TLS_FORWARD: refusal when configuring with multiple IPs (#306)
- cache: fix broken refresh of insecure records that were about to expire
- fix the hints module on some systems, e.g. Fedora (came back on 2.0.0)
- build with older gnutls (conditionally disable features)
- fix the predict module to work with insecure records & cleanup code


Knot Resolver 2.0.0 (2018-01-31)
================================

Incompatible changes
--------------------
- systemd: change unit files to allow running multiple instances,
  deployments with single instance now must use `kresd@1.service`
  instead of `kresd.service`; see kresd.systemd(8) for details
- systemd: the directory for cache is now /var/cache/knot-resolver
- unify default directory and user to `knot-resolver`
- directory with trust anchor file specified by -k option must be writeable
- policy module is now loaded by default to enforce RFC 6761;
  see documentation for policy.PASS if you use locally-served DNS zones
- drop support for alternative cache backends memcached, redis,
  and for Lua bindings for some specific cache operations
- REORDER_RR option is not implemented (temporarily)

New features
------------
- aggressive caching of validated records (RFC 8198) for NSEC zones;
  thanks to ICANN for sponsoring this work.
- forwarding over TLS, authenticated by SPKI pin or certificate.
  policy.TLS_FORWARD pipelines queries out-of-order over shared TLS connection
  Beware: Some resolvers do not support out-of-order query processing.
  TLS forwarding to such resolvers will lead to slower resolution or failures.
- trust anchors: you may specify a read-only file via -K or --keyfile-ro
- trust anchors: at build-time you may set KEYFILE_DEFAULT (read-only)
- ta_sentinel module implements draft ietf-dnsop-kskroll-sentinel-00,
  enabled by default
- serve_stale module is prototype, subject to change
- extended API for Lua modules

Bugfixes
--------
- fix build on osx - regressed in 1.5.3 (different linker option name)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.5.3-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 23 2018 Tomas Krizek <tomas.krizek@nic.cz> - 1.5.3-1
- New upstream release 1.5.3

Knot Resolver 1.5.3 (2018-01-23)
================================

Bugfixes
--------
- fix the hints module on some systems, e.g. Fedora.
  Symptom: `undefined symbol: engine_hint_root_file`


Knot Resolver 1.5.2 (2018-01-22)
================================

Security
--------
- fix CVE-2018-1000002: insufficient DNSSEC validation, allowing
  attackers to deny existence of some data by forging packets.
  Some combinations pointed out in RFC 6840 sections 4.1 and 4.3
  were not taken into account.

Bugfixes
--------
- memcached: fix fallout from module rename in 1.5.1


Knot Resolver 1.5.1 (2017-12-12)
================================

Incompatible changes
--------------------
- script supervisor.py was removed, please migrate to a real process manager
- module ketcd was renamed to etcd for consistency
- module kmemcached was renamed to memcached for consistency

Bugfixes
--------
- fix SIGPIPE crashes (#271)
- tests: work around out-of-space for platforms with larger memory pages
- lua: fix mistakes in bindings affecting 1.4.0 and 1.5.0 (and 1.99.1-alpha),
  potentially causing problems in dns64 and workarounds modules
- predict module: various fixes (!399)

Improvements
------------
- add priming module to implement RFC 8109, enabled by default (#220)
- add modules helping with system time problems, enabled by default;
  for details see documentation of detect_time_skew and detect_time_jump

* Fri Jan 05 2018 Tomas Krizek <tomas.krizek@nic.cz> - 1.5.0-2
- add doc package
- configure tarball signature verification
- add root.hints file
- use upstream systemd unit files, paths and user name
    - migrate configuration to /etc/knot-resolver
    - use user knot-resolver
    - store cache in /var/cache/knot-resolver
    - use systemd alias knot-resolver -> kresd

* Mon Nov 06 2017 Petr Špaček <petr.spacek@nic.cz> - 1.5.0-1
- New upstream release 1.5.0

Knot Resolver 1.5.0 (2017-11-02)
================================

Bugfixes
--------
- fix loading modules on Darwin

Improvements
------------
- new module ta_signal_query supporting Signaling Trust Anchor Knowledge
  using Keytag Query (RFC 8145 section 5); it is enabled by default
- attempt validation for more records but require it for fewer of them
  (e.g. avoids SERVFAIL when server adds extra records but omits RRSIGs)


Knot Resolver 1.4.0 (2017-09-22)
================================

Incompatible changes
--------------------
- lua: query flag-sets are no longer represented as plain integers.
  kres.query.* no longer works, and kr_query_t lost trivial methods
  'hasflag' and 'resolved'.
  You can instead write code like qry.flags.NO_0X20 = true.

Bugfixes
--------
- fix exiting one of multiple forks (#150)
- cache: change the way of using LMDB transactions.  That in particular
  fixes some cases of using too much space with multiple kresd forks (#240).

Improvements
------------
- policy.suffix: update the aho-corasick code (#200)
- root hints are now loaded from a zonefile; exposed as hints.root_file().
  You can override the path by defining ROOTHINTS during compilation.
- policy.FORWARD: work around resolvers adding unsigned NS records (#248)
- reduce unneeded records previously put into authority in wildcarded answers


Knot Resolver 1.3.3 (2017-08-09)
================================

Security
--------
- Fix a critical DNSSEC flaw.  Signatures might be accepted as valid
  even if the signed data was not in bailiwick of the DNSKEY used to
  sign it, assuming the trust chain to that DNSKEY was valid.

Bugfixes
--------
- iterate: skip RRSIGs with bad label count instead of immediate SERVFAIL
- utils: fix possible incorrect seeding of the random generator
- modules/http: fix compatibility with the Prometheus text format

Improvements
------------
- policy: implement remaining special-use domain names from RFC6761 (#205),
  and make these rules apply only if no other non-chain rule applies

* Tue Aug 01 2017 Petr Spacek <petr.spacek@nic.cz> - 1.3.2-1
New upstream release:
Knot Resolver 1.3.2 (2017-07-28)
================================

Security
--------
- fix possible opportunities to use insecure data from cache as keys
  for validation

Bugfixes
--------
- daemon: check existence of config file even if rundir isn't specified
- policy.FORWARD and STUB: use RTT tracking to choose servers (#125, #208)
- dns64: fix CNAME problems (#203)  It still won't work with policy.STUB.
- hints: better interpretation of hosts-like files (#204)
         also, error out if a bad entry is encountered in the file
- dnssec: handle unknown DNSKEY/DS algorithms (#210)
- predict: fix the module, broken since 1.2.0 (#154)

Improvements
------------
- embedded LMDB fallback: update 0.9.18 -> 0.9.21

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.1-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jul 11 2017 Petr Spacek <petr.spacek@nic.cz> - 1.3.1-2
- build experimental command line interface "kresc"

* Tue Jul 11 2017 Petr Spacek <petr.spacek@nic.cz> - 1.3.1-1
New upstream release:
Knot Resolver 1.3.1 (2017-06-23)
================================

Bugfixes
--------
- modules/http: fix finding the static files (bug from 1.3.0)
- policy.FORWARD: fix some cases of CNAMEs obstructing search for zone cuts


Knot Resolver 1.3.0 (2017-06-13)
================================

Security
--------
- Refactor handling of AD flag and security status of resource records.
  In some cases it was possible for secure domains to get cached as
  insecure, even for a TLD, leading to disabled validation.
  It also fixes answering with non-authoritative data about nameservers.

Improvements
------------
- major feature: support for forwarding with validation (#112).
  The old policy.FORWARD action now does that; the previous non-validating
  mode is still avaliable as policy.STUB except that also uses caching (#122).
- command line: specify ports via @ but still support # for compatibility
- policy: recognize 100.64.0.0/10 as local addresses
- layer/iterate: *do* retry repeatedly if REFUSED, as we can't yet easily
  retry with other NSs while avoiding retrying with those who REFUSED
- modules: allow changing the directory where modules are found,
  and do not search the default library path anymore.

Bugfixes
--------
- validate: fix insufficient caching for some cases (relatively rare)
- avoid putting "duplicate" record-sets into the answer (#198)


Knot Resolver 1.2.6 (2017-04-24)
================================

Security
--------
- dnssec: don't set AD flag for NODATA answers if wildcard non-existence
  is not guaranteed due to opt-out in NSEC3

Improvements
------------
- layer/iterate: don't retry repeatedly if REFUSED

Bugfixes
--------
- lib/nsrep: revert some changes to NS reputation tracking that caused
  severe problems to some users of 1.2.5 (#178 and #179)
- dnssec: fix verification of wildcarded non-singleton RRsets
- dnssec: allow wildcards located directly under the root
- layer/rrcache: avoid putting answer records into queries in some cases

* Thu Apr 06 2017 Petr Spacek <petr.spacek@nic.cz> - 1.2.5-1
- new upstream relase
 + security: layer/validate: clear AD if closest encloser proof has opt-outed NSEC3 (#169)
 + security: layer/validate: check if NSEC3 records in wildcard expansion proof has an opt-out
 + security: dnssec/nsec: missed wildcard no-data answers validation has been implemented
 + fix: trust anchors: Improve trust anchors storage format (#167)
 + fix: trust anchors: support non-root TAs, one domain per file
 + fix: policy.DENY: set AA flag and clear AD flag
 + fix: lib/resolve: avoid unnecessary DS queries
 + fix: lib/nsrep: don't treat servers with NOIP4 + NOIP6 flags as timeouted
 + fix: layer/iterate: During packet classification (answer vs. referral) don't analyze
        AUTHORITY section in authoritative answer if ANSWER section contains records
        that have been requested
 + enhancement: modules/dnstap: a DNSTAP support module (Contributed by Vicky Shrestha)
 + enhancement: modules/workarounds: a module adding workarounds for known DNS protocol violators
 + enhancement: layer/iterate: fix logging of glue addresses
 + enhancement: kr_bitcmp: allow bits=0 and consequently 0.0.0.0/0 matches in view and renumber modules.
 + enhancement: modules/padding: Improve default padding of responses (Contributed by Daniel Kahn Gillmor)
 + enhancement: New kresc client utility (experimental; don't rely on the API yet)

* Thu Mar 09 2017 Petr Spacek <petr.spacek@nic.cz> - 1.2.4-1
- new upstream release
 + security: Knot Resolver 1.2.0 and higher could return AD flag for insecure
             answer if the daemon received answer with invalid RRSIG several
             times in a row.
 + fix: layer/iterate: some improvements in cname chain unrolling
 + fix: layer/validate: fix duplicate records in AUTHORITY section in case
 + fix: of WC expansion proof
 + fix: lua: do *not* truncate cache size to unsigned
 + fix: forwarding mode: correctly forward +cd flag
 + fix: fix a potential memory leak
 + fix: don't treat answers that contain DS non-existance proof as insecure
 + fix: don't store NSEC3 and their signatures in the cache
 + fix: layer/iterate: when processing delegations,
                       check if qname is at or below new authority
 + enhancement: modules/policy: allow QTRACE policy to be chained
                                with other policies
 + enhancement: hints.add_hosts(path): a new property
 + enhancement: module: document the API and simplify the code
 + enhancement: policy.MIRROR: support IPv6 link-local addresses
 + enhancement: policy.FORWARD: support IPv6 link-local addresses
 + enhancement: add net.outgoing_{v4,v6} to allow specifying address
                to use for connections

* Mon Feb 27 2017 Petr Spacek <petr.spacek@nic.cz> - 1.2.3-1
- new upstream release
 + security: a cached negative answer from a CD query would be reused
   to construct response for non-CD queries, resulting in Insecure status
   instead of Bogus.
 + fix: lua: make the map command check its arguments
 + fix: -k argument processing to avoid out-of-bounds memory accesses
 + fix: lib/resolve: fix zonecut fetching for explicit DS queries
 + fix: hints: more NULL checks
 + fix: TA bootstrapping for multiple TAs in the IANA XML file
 + fix: Disable storing GLUE records into the cache even in the
 + fix: (non-default) QUERY_PERMISSIVE mode
 + fix: iterate: skip answer RRs that don't match the query
 + fix: layer/iterate: some additional processing for referrals
 + fix: lib/resolve: zonecut fetching error was fixed

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.0-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jan 27 2017 Petr Spacek <petr.spacek@nic.cz> - 1.2.0-2
- rebuild against knot-2.4.0

* Fri Jan 27 2017 Petr Spacek <petr.spacek@nic.cz> - 1.2.0
- new upstream release:
 + fix: reworked DNSSEC Validation, that fixes several know problems with less standard DNS configurations
 + fix: the resolver was setting AD flag when running in a forwarding mode
 + fix: correctly return RCODE=NOTIMPL on meta-queries and non IN class queries
 + fix: crash in hints module when hints file was empty
 + fix: non-lowercase hints
 + features: optional EDNS(0) Padding support for DNS over TLS
 + features: support for debugging DNSSEC with CD bit
 + features: DNS over TLS is now able to create ephemeral certs on the runtime (Thanks Daniel Kahn Gilmore for contributing to DNS over TLS implementation in Knot Resolver.)
 + features: configurable minimum and maximum TTL (default 6 days)
 + features: configurable pseudo-random reordering of RR sets
 + features: new module 'version' that can call home and report new versions and security vulnerabilities to the log file

* Mon Jan 23 2017 Petr Spacek <petr.spacek@nic.cz> - 1.2.0-rc1
- Update to latest upstream version
- Fix packaging bug: depend on proper Lua library versions
- Allow automatic trust anchor management to work

* Sat Nov 19 2016 Peter Robinson <pbrobinson@fedoraproject.org> 1.1.1-3
- Add ExclusiveArch for architectures with LuaJIT

* Mon Aug 29 2016 Igor Gnatenko <ignatenko@redhat.com> - 1.1.1-2
- Rebuild for LuaJIT 2.1.0

* Wed Aug 24 2016 Jan Vcelak <jvcelak@fedoraproject.org> - 1.1.1-1
- new upstream release:
  + fix name server fallback in case some of the servers are unreachable

* Fri Aug 12 2016 Jan Vcelak <jvcelak@fedoraproject.org> - 1.1.0-1
- new upstream release:
  + RFC7873 DNS Cookies
  + RFC7858 DNS over TLS
  + Metrics exported in Prometheus
  + DNS firewall module
  + Explicit CNAME target fetching in strict mode
  + Query minimisation improvements
  + Improved integration with systemd

* Tue May 31 2016 Jan Vcelak <jvcelak@fedoraproject.org> - 1.0.0-1
- final release

* Thu May 05 2016 Jan Vcelak <jvcelak@fedoraproject.org> - 1.0.0-0.3.4f463d7
- update to latest git version
- re-enable unit-test

* Sat Apr 09 2016 Jan Vcelak <jvcelak@fedoraproject.org> - 1.0.0-0.2.79a8440
- update to latest git version
- fix package review issues

* Tue Feb 02 2016 Jan Vcelak <jvcelak@fedoraproject.org> - 1.0.0-0.1.beta3
- initial package
