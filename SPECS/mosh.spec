Name:		mosh
Version:	1.3.2
Release:	1%{?dist}
Summary:	Mobile shell that supports roaming and intelligent local echo

License:	GPLv3+
Group:		Applications/Internet
URL:		https://mosh.org/
Source0:	https://github.com/downloads/keithw/mosh/mosh-%{version}.tar.gz

BuildRequires:	protobuf-compiler
BuildRequires:	protobuf-devel
BuildRequires:	libutempter-devel
BuildRequires:	zlib-devel
BuildRequires:	ncurses-devel
BuildRequires:	openssl-devel
Requires:	openssh-clients
Requires:	openssl
Requires:	perl-IO-Socket-IP

%description
Mosh is a remote terminal application that supports:
  - intermittent network connectivity,
  - roaming to different IP address without dropping the connection, and
  - intelligent local echo and line editing to reduce the effects
    of "network lag" on high-latency connections.


%prep
%setup -q


%build
# Use upstream's more aggressive hardening instead of Fedora's defaults
export CFLAGS="-g -O2" CXXFLAGS="-g -O2"
%configure --enable-compile-warnings=error
make %{?_smp_mflags}


%install
make install DESTDIR=$RPM_BUILD_ROOT


%files
%doc README.md COPYING ChangeLog
%{_bindir}/mosh
%{_bindir}/mosh-client
%{_bindir}/mosh-server
%{_mandir}/man1/mosh.1.gz
%{_mandir}/man1/mosh-client.1.gz
%{_mandir}/man1/mosh-server.1.gz
