%{!?luaver: %global luaver %(lua -e "print(string.sub(_VERSION, 5))" || echo 0)}
%global luapkgdir %{_datadir}/lua/%{luaver}

%global luacompatver 5.1
%global luacompatpkgdir %{_datadir}/lua/%{luacompatver}

%global luapkgname lpeg-patterns

Name:           lua-%{luapkgname}
Version:        0.5
Release:        2%{?dist}
Summary:        A collection of LPEG patterns

License:        MIT
URL:            https://github.com/daurnimator/lpeg_patterns
Source0:        https://github.com/daurnimator/lpeg_patterns/archive/v%{version}/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  lua

Requires:       lua-lpeg

%description
A collection of LPEG patterns for validating/searching user input.

%if 0%{?fedora} || 0%{?rhel} > 7
%package -n lua%{luacompatver}-%{luapkgname}
Summary:        A collection of LPEG patterns
Requires:       compat-lua-lpeg

%description -n lua%{luacompatver}-%{luapkgname}
A collection of LPEG patterns for validating/searching user input.
%endif

%prep
%setup -q -n lpeg_patterns-%{version}

%install
install -d -m 0755 %{buildroot}%{luapkgdir}/lpeg_patterns
install -p -m 0644 lpeg_patterns/* -t %{buildroot}%{luapkgdir}/lpeg_patterns/

%if 0%{?fedora} || 0%{?rhel} > 7
install -d -m 0755 %{buildroot}%{luacompatpkgdir}/lpeg_patterns
install -p -m 0644 lpeg_patterns/* -t %{buildroot}%{luacompatpkgdir}/lpeg_patterns/
%endif

%files
%doc README.md
%license LICENSE.md
%{luapkgdir}/lpeg_patterns

%if 0%{?fedora} || 0%{?rhel} > 7
%files -n lua%{luacompatver}-%{luapkgname}
%doc README.md
%license LICENSE.md
%{luacompatpkgdir}/lpeg_patterns
%endif

%changelog
* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Apr 08 2019 Tomas Krizek <tomas.krizek@nic.cz> - 0.5-1
- Initial package for Fedora 28+ and EPEL 7+
