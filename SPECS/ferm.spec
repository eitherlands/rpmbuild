Summary:        For Easy Rule Making
Name:           ferm
Version:        2.5.1
Release:        1%{?dist}
Group:          Applications/System
License:        GPLv2+
Source:         http://ferm.foo-projects.org/download/2.2/%{name}-%{version}.tar.gz
URL:            http://ferm.foo-projects.org/
BuildArchitectures: noarch

BuildRequires:          perl-generators
BuildRequires:          perl(Data::Dumper)
BuildRequires:          perl(File::Spec)
BuildRequires:          systemd
BuildRequires:          /usr/bin/pod2text
BuildRequires:          /usr/bin/pod2man
BuildRequires:          /usr/bin/pod2html
Requires(post):         systemd
Requires(preun):        systemd
Requires(postun):       systemd

%description
Ferm is a tool to maintain complex firewalls, without having the
trouble to rewrite the complex rules over and over again. Ferm
allows the entire firewall rule set to be stored in a separate
file, and to be loaded with one command. The firewall configuration
resembles structured programming-like language, which can contain
levels and lists.

%prep
%setup -q

%build

%install
make install PREFIX=$RPM_BUILD_ROOT%{_prefix} DOCDIR=$RPM_BUILD_ROOT%{_pkgdocdir} MANDIR=$RPM_BUILD_ROOT%{_mandir}/man1

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun

%files
# %doc AUTHORS README TODO NEWS examples/
%{_pkgdocdir}
%exclude %{_pkgdocdir}/COPYING
%license COPYING
%{_mandir}/man1/*
%{_unitdir}/%{name}.service
%{_sbindir}/import-ferm
%{_sbindir}/ferm
