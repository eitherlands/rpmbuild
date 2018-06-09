Name: docker-gc
Version: 0.1.1
Release: 1%{?dist}
Summary: Docker garbage collection of containers and images.
BuildArch: noarch
Requires: bash
License: Apache
Source0: https://github.com/spotify/docker-gc/archive/master.tar.gz

%description
Docker garbage collection of containers and images.

%prep
%setup -q -n docker-gc-master

%build

%install

mkdir -p %{buildroot}/%{_bindir}

install -m 0755 %{name} %{buildroot}/%{_bindir}/%{name}

%files
%license LICENSE
%{_bindir}/%{name}
