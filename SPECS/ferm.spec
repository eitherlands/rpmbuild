%global _sourcedir %{_topdir}/SOURCES/ferm

Summary:        For Easy Rule Making
Name:           ferm
Version:        2.4.1
Release:        2%{?dist}
Group:          Applications/System
License:        GPLv2+
Source:         http://ferm.foo-projects.org/download/2.2/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
URL:            http://ferm.foo-projects.org/
BuildArchitectures: noarch

BuildRequires:          systemd
Requires(post):         systemd
Requires(preun):        systemd
Requires(postun):       systemd

%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

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
rm -Rf $RPM_BUILD_ROOT

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
%defattr(-,root,root,-)
%doc AUTHORS COPYING README.rst TODO NEWS examples/
%{_mandir}/man1/*
%{_unitdir}/%{name}.service
%{_sbindir}/import-ferm
%{_sbindir}/ferm
