%global _hardened_build 1

Name:           tmux
Version:        2.9a
Release:        2%{?dist}
Summary:        A terminal multiplexer

# Most of the source is ISC licensed; some of the files in compat/ are 2 and
# 3 clause BSD licensed.
License:        ISC and BSD
URL:            https://tmux.github.io/
Source0:        https://github.com/tmux/%{name}/releases/download/%{version}/%{name}-%{version}.tar.gz
# Examples has been removed - so include the bash_completion here
Source1:        bash_completion_tmux.sh

BuildRequires:  gcc
BuildRequires:  ncurses-devel
BuildRequires:  libevent-devel
BuildRequires:  libutempter-devel

%description
tmux is a "terminal multiplexer."  It enables a number of terminals (or
windows) to be accessed and controlled from a single terminal.  tmux is
intended to be a simple, modern, BSD-licensed alternative to programs such
as GNU Screen.

%prep
%autosetup

%build
%configure
%make_build


%install
%make_install
# bash completion
install -Dpm 644 %{SOURCE1} %{buildroot}%{_datadir}/bash-completion/completions/tmux

%post
if [ "$1" = 1 ]; then
  if [ ! -f %{_sysconfdir}/shells ] ; then
    touch %{_sysconfdir}/shells
  fi
  for binpath in %{_bindir} /bin; do
    if ! grep -q "^${binpath}/tmux$" %{_sysconfdir}/shells; then
       (cat %{_sysconfdir}/shells; echo "$binpath/tmux") > %{_sysconfdir}/shells.new
       mv %{_sysconfdir}/shells{.new,}
    fi
  done
fi

%postun
if [ "$1" = 0 ] && [ -f %{_sysconfdir}/shells ] ; then
  sed -e '\!^%{_bindir}/tmux$!d' -e '\!^/bin/tmux$!d' < %{_sysconfdir}/shells > %{_sysconfdir}/shells.new
  mv %{_sysconfdir}/shells{.new,}
fi

%files
%doc CHANGES TODO
%{_bindir}/tmux
%{_mandir}/man1/tmux.1.*
%{_datadir}/bash-completion/completions/tmux

%changelog
* Sun May 12 2019 Filipe Rosset <rosset.filipe@gmail.com> - 2.9a-2
- update to version 2.9a, fixes rhbz #1692933
- ChangeLog https://raw.githubusercontent.com/tmux/tmux/2.9/CHANGES
- removed upstreamed patch

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Nov 22 2018 Filipe Rosset <rosset.filipe@gmail.com> - 2.8-2
- fixes rhbz #1652128 CVE-2018-19387
- tmux: NULL Pointer Dereference in format_cb_pane_tabs in format.c

* Fri Oct 19 2018 Filipe Rosset <rosset.filipe@gmail.com> - 2.8-1
- update to version 2.8
- ChangeLog https://raw.githubusercontent.com/tmux/tmux/2.8/CHANGES

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Apr 19 2018 Filipe Rosset <rosset.filipe@gmail.com> - 2.7-1
- update to version 2.7, fixes rhbz #1486507
- removed upstreamed patches + spec modernization

* Mon Apr 09 2018 Filipe Rosset <rosset.filipe@gmail.com> - 2.6-4
- added gcc as BR

* Wed Feb 14 2018 Kevin Fenzi <kevin@scrye.com> - 2.6-3
- Rebuild for new libevent

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Jan 26 2018 Andreas Schneider <asn@redhat.com> - 2.6-1
- Update to version 2.6
- Use hardened build

* Sat Aug 05 2017 Filipe Rosset <rosset.filipe@gmail.com> - 2.5-4
- Fixes rhbz #1476851 tmux bell-action other not working
- Fixes rhbz #1476892 tmux update in F26 broke tmuxinator

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Jun 10 2017 Filipe Rosset <rosset.filipe@gmail.com> - 2.5-1
- New upstream release 2.5 - fixes rhbz #1449666
- https://raw.githubusercontent.com/tmux/tmux/2.5/CHANGES

* Fri Apr 21 2017 Filipe Rosset <rosset.filipe@gmail.com> - 2.4-2
- rebuild tmux as PIE  - fixes rhbz #1324104

* Fri Apr 21 2017 Filipe Rosset <rosset.filipe@gmail.com> - 2.4-1
- New upstream release - fixes rhbz #1444011

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Oct 28 2016 Sven Lankes <sven@lank.es> - 2.3-1
- New upstream release - fixes rhbz #1380562
- Adapt shells handling to be atomic and support rpm-ostree - fixes rhbz #1367587

* Tue May 24 2016 Sven Lankes <sven@lank.es> - 2.2-3
- add libutempter-devel as buildrequires to allow writing to utmp
- fixes rhbz #1338936 

* Mon May 09 2016 Sven Lankes <sven@lank.es> - 2.2-2
- Adapt source0 and url for new website (fixes rhbz #1334255)

* Wed Apr 20 2016 Sven Lankes <sven@lank.es> - 2.2-1
- New upstream release

* Tue Feb 23 2016 Sven Lankes <sven@lank.es> - 2.1-3
- use more correct bash completion path (thanks to Carl George)

* Mon Feb 22 2016 Sven Lankes <sven@lank.es> - 2.1-2
- add upstream bash-completion (thanks to Scott Tsai - closes rhbz #1148183)

* Mon Feb 22 2016 Sven Lankes <sven@lank.es> - 2.1-1
- New upstream release 

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu May 07 2015 Filipe Rosset <rosset.filipe@gmail.com> - 2.0-1
- Rebuilt for new upstream version 2.0, fixes rhbz #1219300

* Fri Jan 02 2015 Sven Lankes <sven@lank.es> - 1.9a-5
- Pull in upstream commit to fix Fx-Key issues. rhbz #1177652

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9a-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9a-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Feb 26 2014 Filipe Rosset <rosset.filipe@gmail.com> 1.9a-2
- Fix rhbz #1069950, upstream [tmux:tickets] #105

* Sun Feb 23 2014 Filipe Rosset <rosset.filipe@gmail.com> 1.9a-1
- New upstream release 1.9a

* Sat Feb 22 2014 Filipe Rosset <rosset.filipe@gmail.com> 1.9-1
- New upstream release 1.9
- Fix rhbz #1067860

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jun 10 2013 Petr Šabata <contyk@redhat.com> - 1.8-2
- Remove tmux from the shells file upon package removal (#972633)

* Sat Apr 13 2013 Sven Lankes <sven@lank.es> 1.8-1
- New upstream release

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Oct 13 2012 Sven Lankes <sven@lank.es> 1.7-1
- New upstream release

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jan 31 2012 Sven Lankes <sven@lank.es> 1.6-1
- New upstream release

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Nov 01 2011 Sven Lankes <sven@lank.es> 1.5-1
- New upstream release
- Do the right thing (tm) and revert to $upstream-behaviour: 
   No longer install tmux setgid and no longer use /var/run/tmux 
   for sockets. Use "tmux -S /var/run/tmux/tmux-`id -u`/default attach"
   if you need to access an "old" tmux session
- tmux can be used as a login shell so add it to /etc/shells

* Sat Apr 16 2011 Sven Lankes <sven@lank.es> 1.4-4
- Add /var/run/tmp to tmpdir.d - fixes rhbz 656704 and 697134

* Sun Apr 10 2011 Sven Lankes <sven@lank.es> 1.4-3
- Fix CVE-2011-1496
- Fixes rhbz #693824

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Dec 28 2010 Filipe Rosset <rosset.filipe@gmail.com> 1.4-1
- New upstream release

* Fri Aug 06 2010 Filipe Rosset <filiperosset@fedoraproject.org> 1.3-2
- Rebuild for F-13

* Mon Jul 19 2010 Sven Lankes <sven@lank.es> 1.3-1
- New upstream release

* Sun Mar 28 2010 Sven Lankes <sven@lank.es> 1.2-1
- New upstream release
- rediff writehard patch

* Mon Nov 09 2009 Sven Lankes <sven@lank.es> 1.1-1
- New upstream release

* Sun Nov 01 2009 Sven Lankes <sven@lank.es> 1.0-2
- Add debian patches
- Add tmux group for improved socket handling

* Sat Oct 24 2009 Sven Lankes <sven@lank.es> 1.0-1
- New upstream release

* Mon Jul 13 2009 Chess Griffin <chess@chessgriffin.com> 0.9-1
- Update to version 0.9.
- Remove sed invocation as this was adopted upstream.
- Remove optflags patch since upstream source now uses ./configure and
  detects the flags when passed to make.

* Tue Jun 23 2009 Chess Griffin <chess@chessgriffin.com> 0.8-5
- Note that souce is mostly ISC licensed with some 2 and 3 clause BSD in
  compat/.
- Remove fixiquote.patch and instead use a sed invocation in setup.

* Mon Jun 22 2009 Chess Griffin <chess@chessgriffin.com> 0.8-4
- Add optimization flags by patching GNUmakefile and passing LDFLAGS
  to make command.
- Use consistent macro format.
- Change examples/* to examples/ and add TODO to docs.

* Sun Jun 21 2009 Chess Griffin <chess@chessgriffin.com> 0.8-3
- Remove fixperms.patch and instead pass them at make install stage.

* Sat Jun 20 2009 Chess Griffin <chess@chessgriffin.com> 0.8-2
- Fix Source0 URL to point to correct upstream source.
- Modify fixperms.patch to set 644 permissions on the tmux.1.gz man page.
- Remove wildcards from 'files' section and replace with specific paths and
  filenames.

* Mon Jun 15 2009 Chess Griffin <chess@chessgriffin.com> 0.8-1
- Initial RPM release.
