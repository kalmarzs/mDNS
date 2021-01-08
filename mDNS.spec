%define build_tar_ball 0
%if ! %{defined _fillupdir}
  %define _fillupdir %{_localstatedir}/adm/fillup-templates
%endif

Name:           mDNS
Version:        0.1
Release:        0
Summary:        mDNS cname service
License:        Apache-2.0
URL:            https://github.com/kalmarzs/mDNS

%if %{build_tar_ball}
Source0:        %{name}-%version.tar.xz
%else
Source0:        _service
%endif

BuildRequires:  systemd-rpm-macros
Requires:       python3
Requires(post): %fillup_prereq
BuildArch:      noarch
%{?systemd_requires}

%description
mDNS cname service

%prep
%if %{build_tar_ball}
 %setup -q
%else
 %setup -q -n %_sourcedir/%name-%version -T -D
%endif

%build
%py3_build

%check

%install
%py3_install

%pre
%service_add_pre mDNS.service

%post
%service_add_post mDNS.service

%preun
%service_del_preun mDNS.service

%files
%doc README
%license LICENSE
%dir %{_datadir}/mDNS
%config(noreplace) %{_sysconfdir}/mDNS/mDNS.conf
%{_unitdir}/mDNS.service

%changelog


