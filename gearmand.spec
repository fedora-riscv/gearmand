Name:           gearmand
Version:        1.1.19.1
Release:        8%{?dist}
Summary:        A distributed job system

License:        BSD
URL:            http://www.gearman.org
Source0:        https://github.com/gearman/%{name}/releases/download/%{version}/gearmand-%{version}.tar.gz
Source1:        gearmand.init
Source2:        gearmand.sysconfig
Source3:        gearmand.service
Patch0:         gearmand-1.1.12-ppc64le.patch
Patch1:         https://github.com/gearman/gearmand/pull/273.patch
# Fails to build on PPC.
# See https://bugzilla.redhat.com/987104 and https://bugzilla.redhat.com/987109
ExcludeArch:    ppc

BuildRequires:  gcc-c++
BuildRequires:  chrpath
BuildRequires:  libuuid-devel
BuildRequires:  boost-devel >= 1.37.0, boost-thread
BuildRequires:  sqlite-devel
BuildRequires:  tokyocabinet-devel
BuildRequires:  libevent-devel
BuildRequires:  libmemcached-devel, memcached
BuildRequires:  hiredis-devel
BuildRequires:  gperf
BuildRequires:  mariadb-connector-c-devel openssl-devel
BuildRequires:  libpq-devel
BuildRequires:  zlib-devel
BuildRequires:  systemd

# For %%check
# https://github.com/gearman/gearmand/issues/278
#BuildRequires:  curl-devel

# google perftools available only on these
%ifarch %{ix86} x86_64 ppc64 ppc64le aarch64 %{arm}
BuildRequires:  gperftools-devel
%endif
BuildRequires: make
Requires(pre):  shadow-utils
Requires:       procps
%{?systemd_requires}

%description
Gearman provides a generic framework to farm out work to other machines
or dispatch function calls to machines that are better suited to do the work.
It allows you to do work in parallel, to load balance processing, and to
call functions between languages. It can be used in a variety of applications,
from high-availability web sites to the transport for database replication.
In other words, it is the nervous system for how distributed processing
communicates.


%package -n libgearman
Summary:        Development libraries for gearman
Provides:       libgearman-1.0 = %{version}-%{release}
Obsoletes:      libgearman-1.0 < %{version}-%{release}

%description -n libgearman
Development libraries for %{name}.

%package -n libgearman-devel
Summary:        Development headers for libgearman
Requires:       pkgconfig, libgearman = %{version}-%{release}
Requires:       libevent-devel
Provides:       libgearman-1.0-devel = %{version}-%{release}
Obsoletes:      libgearman-1.0-devel < %{version}-%{release}

%description -n libgearman-devel
Development headers for %{name}.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%configure --disable-static --disable-silent-rules --enable-ssl

make %{_smp_mflags}


%install
make install DESTDIR=%{buildroot}
rm -v %{buildroot}%{_libdir}/libgearman*.la
chrpath --delete %{buildroot}%{_bindir}/gearman
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/gearmand

# install systemd unit file
mkdir -p %{buildroot}%{_unitdir}
install -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service


%check
# https://github.com/gearman/gearmand/issues/279
# https://github.com/gearman/gearmand/issues/277
#make test


%pre
getent group gearmand >/dev/null || groupadd -r gearmand
getent passwd gearmand >/dev/null || \
        useradd -r -g gearmand -d / -s /sbin/nologin \
        -c "Gearmand job server" gearmand
exit 0

%post
%systemd_post gearmand.service


%preun
%systemd_preun gearmand.service

%postun
%systemd_postun_with_restart gearmand.service

%ldconfig_scriptlets -n libgearman

%files
%license COPYING
%doc AUTHORS ChangeLog HACKING THANKS
%config(noreplace) %{_sysconfdir}/sysconfig/gearmand
%{_sbindir}/gearmand
%{_bindir}/gearman
%{_bindir}/gearadmin
%{_mandir}/man1/*
%{_mandir}/man8/*
%{_unitdir}/%{name}.service

%files -n libgearman
%license COPYING
%{_libdir}/libgearman.so.8
%{_libdir}/libgearman.so.8.0.0

%files -n libgearman-devel
%license COPYING
%doc AUTHORS ChangeLog HACKING THANKS
%dir %{_includedir}/libgearman
%{_includedir}/libgearman/
%{_libdir}/pkgconfig/gearmand.pc
%{_libdir}/libgearman.so
%{_includedir}/libgearman-1.0/
%{_mandir}/man3/*


%changelog
* Tue Mar 02 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 1.1.19.1-8
- Rebuilt for updated systemd-rpm-macros
  See https://pagure.io/fesco/issue/2583.

* Mon Feb 08 2021 Pavel Raiskup <praiskup@redhat.com> - 1.1.19.1-7
- rebuild for libpq ABI fix rhbz#1908268

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.19.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Jan 22 2021 Jonathan Wakely <jwakely@redhat.com> - 1.1.19.1-5
- Rebuilt for Boost 1.75

* Tue Sep 15 2020 Robin Lee <cheeselee@fedoraproject.org> - 1.1.19.1-4
- Rebuild for libevent

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.19.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Thu May 28 2020 Jonathan Wakely <jwakely@redhat.com> - 1.1.19.1-2
- Rebuilt for Boost 1.73

* Tue Feb 18 2020 Robin Lee <cheeselee@fedoraproject.org> - 1.1.19.1-1
- Update to 1.1.19.1 (RHBZ#1801575)
- Enable SSL support
- Change to use chrpath to remove rpath, since patching libtool will fail to run tests
- Add patch to fix crashing of tests
- Remove EL8 swithes since all BRs are met in EPEL8
- Remove EL6 swithes since it no longer builds

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.18-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Tue Oct  1 2019 Robin Lee <cheeselee@fedoraproject.org> - 1.1.18-10
- Support building for EL8 (BZ#1756966)
- Remove EL5 support

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.18-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.18-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jan 25 2019 Jonathan Wakely <jwakely@redhat.com> - 1.1.18-7
- Rebuilt for Boost 1.69

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.18-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Sat Mar 10 2018 Robin Lee <cheeselee@fedoraproject.org> - 1.1.18-5
- BR gcc-c++ for http://fedoraproject.org/wiki/Changes/Remove_GCC_from_BuildRoot

* Mon Feb 19 2018 Robin Lee <cheeselee@fedoraproject.org> - 1.1.18-4
- rebuild (libevent)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.18-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 23 2018 Jonathan Wakely <jwakely@redhat.com> - 1.1.18-2
- Rebuilt for Boost 1.66

* Sat Dec 16 2017 Robin Lee <cheeselee@fedoraproject.org> - 1.1.18-1
- Update to 1.1.18 (BZ#1524746)

* Sat Sep 23 2017 Robin Lee <cheeselee@fedoraproject.org> - 1.1.17-3
- Use mariadb client library (BZ#1493685)
- Use syslog

* Tue Sep  5 2017 Robin Lee <cheeselee@fedoraproject.org> - 1.1.17-2
- BR hiredis-devel

* Mon Sep  4 2017 Robin Lee <cheeselee@fedoraproject.org> - 1.1.17-1
- Update to 1.1.17 (BZ#1475805)

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.16-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.16-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jul 19 2017 Jonathan Wakely <jwakely@redhat.com> - 1.1.16-3
- Rebuilt for s390x binutils bug

* Tue Jul 18 2017 Jonathan Wakely <jwakely@redhat.com> - 1.1.16-2
- Rebuilt for Boost 1.64

* Sat Jul  1 2017 Robin Lee <cheeselee@fedoraproject.org> - 1.1.16-1
- Update to 1.1.16 (BZ#1424779, BZ#1423595, BZ#1464646, BZ#1411067)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.14-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sun Jan 08 2017 Ken Dreyer <ktdreyer@ktdreyer.com> - 1.1.14-1
- Update to 1.1.14
- Remove reference to old Fedoras
- New upstream URL
- Update for latest systemd packaging guidelines
- Use %%license macro
- Drop %%defattr macro

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.12-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Feb 02 2016 Ralf Corsépius <corsepiu@fedoraproject.org> - 1.1.12-17
- Rebuilt for Boost 1.60
- Append --disable-silent-rules to %%configure.

* Tue Jan 19 2016 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 1.1.12-16
- gperftools is available on wider selection of architectures - rhbz#1256287

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 1.1.12-15
- Rebuilt for Boost 1.59

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.12-14
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 1.1.12-13
- rebuild for Boost 1.58

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.12-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 1.1.12-11
- Rebuilt for GCC 5 C++11 ABI change

* Wed Mar 18 2015 Adam Jackson <ajax@redhat.com> 1.1.12-10
- Re-add Fedora conditional dropped in 1.1.12-1, which had the (probably)
  unintended side-effect of reverting Fedora to sysvinit from systemd.

* Tue Jan 27 2015 Petr Machata <pmachata@redhat.com> - 1.1.12-9
- Rebuild for boost 1.57.0

* Tue Sep 09 2014 Karsten Hopp <karsten@redhat.com> 1.1.12-8
- enable ppc64

* Tue Sep 09 2014 Karsten Hopp <karsten@redhat.com> 1.1.12-7
- fix library path for ppc64le

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.12-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.12-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 23 2014 Petr Machata <pmachata@redhat.com> - 1.1.12-4
- Rebuild for boost 1.55.0

* Fri May 23 2014 David Tardon <dtardon@redhat.com> - 1.1.12-3
- rebuild for boost 1.55.0

* Fri Apr 25 2014 Ken Dreyer <ktdreyer@ktdreyer.com> - 1.1.12-2
- Add missing Source0 tarball (oops)

* Fri Apr 25 2014 Ken Dreyer <ktdreyer@ktdreyer.com> - 1.1.12-1
- Update to latest upstream release
- Drop Fedora 18 conditional
- Add el5 e2fsprogs-libs minimum version requirement
- Fix bogus changelog date

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.8-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sat Jul 27 2013 pmachata@redhat.com - 1.1.8-3
- Rebuild for boost 1.54.0

* Mon Jul 22 2013 Blake Gardner <blakegardner@cox.net> - 1.1.8-2
- ExcludeArch ppc ppc64

* Thu Jul 18 2013 Ken Dreyer <ktdreyer@ktdreyer.com> - 1.1.8-1
- Update to latest upstream release.
- Add EL5 and EL6 conditionals to unify the spec across all branches.
- Add mandirs.
- Add /var/log/gearmand.log.
- Add tokyocabinet support.
- Remove commented patches.
- rpmlint fixes (macros in comments).

* Sun Feb 10 2013 Denis Arnaud <denis.arnaud_fedora@m4x.org> - 1.1.2-3
- Rebuild for Boost-1.53.0

* Sat Feb 09 2013 Denis Arnaud <denis.arnaud_fedora@m4x.org> - 1.1.2-2
- Rebuild for Boost-1.53.0

* Thu Oct 18 2012 BJ Dierkes <wdierkes@rackspace.com> - 1.1.2-1
- Bumping to 1.2 branch (1.1.2 current development version).
  Release notes are available here:
  https://launchpad.net/gearmand/1.2/1.1.2
- Repackaged libgearman-1.0, and libgearman-1.0-devel under the
  devel sub-package.
- Updated scriptlets per BZ#850127
 
* Mon Sep 24 2012 BJ Dierkes <wdierkes@rackspace.com> - 0.39-1
- Latest sources from upstream. Release notes here:
  https://launchpad.net/gearmand/trunk/0.39
- Added Postgres support
- Added Sqlite support

* Wed Aug 15 2012 BJ Dierkes <wdierkes@rackspace.com> - 0.35-1
- Latest sources from upstream. Release notes here:
  https://launchpad.net/gearmand/trunk/0.35
- Removed Patch3: gearmand-0.33-lp1020778.patch (applied upstream)
- Added zlib support
- Added MySQL support 

* Wed Aug 15 2012 BJ Dierkes <wdierkes@rackspace.com> - 0.33-3
- Rebuilt for latest boost.
- BuildRequires: boost-thread
- Added -lboost_system to LDFLAGS to work around boost issue
  related to boost-thread.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.33-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 03 2012 BJ Dierkes <wdierkes@rackspace.com> - 0.33-1
- Latest sources from upstream.  Release notes here:
  https://launchpad.net/gearmand/trunk/0.33
- Adding Patch3: gearmand-0.33-lp1020778.patch

* Mon Apr 23 2012  Remi Collet <remi@fedoraproject.org> - 0.32-2
- rebuild against libmemcached.so.10

* Wed Apr 18 2012 BJ Dierkes <wdierkes@rackspace.com> - 0.32-1
- Latest sources from upstream.  Release notes here:
  https://launchpad.net/gearmand/trunk/0.32
- Removed Patch2: gearmand-0.31-lp978235.patch (applied upstream)

* Tue Apr 10 2012 BJ Dierkes <wdierkes@rackspace.com> - 0.31-1
- Latest sources from upstream.  Release notes here:
  https://launchpad.net/gearmand/trunk/0.31
  https://launchpad.net/gearmand/trunk/0.29
- Removed Patch1: gearmand-0.28-lp932994.patch (applied upstream)
- Added Patch2: gearmand-0.31-lp978235.patch.  Resolves LP#978235.

* Wed Mar 07 2012 BJ Dierkes <wdierkes@rackspace.com> - 0.28-3
- Adding back _smp_mflags

* Wed Mar 07 2012 BJ Dierkes <wdierkes@rackspace.com> - 0.28-2
- Added Patch1: gearmand-0.28-lp932994.patch.  Resolves: LP#932994

* Fri Jan 27 2012 BJ Dierkes <wdierkes@rackspace.com> - 0.28-1
- Latest sources from upstream.  Release notes here:
  https://launchpad.net/gearmand/trunk/0.28
- Removing Patch0: gearmand-0.27-lp914495.patch (applied upstream)
- Removing _smp_mflags per https://bugs.launchpad.net/bugs/901007

* Thu Jan 12 2012 BJ Dierkes <wdierkes@rackspace.com> - 0.27-2
- Adding Patch0: gearmand-0.27-lp914495.patch Resolves LP#914495

* Tue Jan 10 2012 BJ Dierkes <wdierkes@rackspace.com> - 0.27-1
- Latest sources from upstream.  Release notes here:
  https://launchpad.net/gearmand/trunk/0.27
 
* Tue Nov 22 2011 BJ Dierkes <wdierkes@rackspace.com> - 0.25-1
- Latest sources from upstream.  Release notes here:
  https://launchpad.net/gearmand/trunk/0.25
- Also rebuild against libboost_program_options-mt.so.1.47.0 
- Added libgearman-1.0, libgearman-1.0-devel per upstream 

* Sat Sep 17 2011  Remi Collet <remi@fedoraproject.org> - 0.23-2
- rebuild against libmemcached.so.8

* Thu Jul 21 2011 BJ Dierkes <wdierkes@rackspace.com> - 0.23-1
- Latest source from upstream.  Release information available at:
  https://launchpad.net/gearmand/+milestone/0.23

* Fri Jun 03 2011 BJ Dierkes <wdierkes@rackspace.com> - 0.20-1
- Latest sources from upstream.  
- Add %%ghost to /var/run/gearmand. Resolves BZ#656592
- BuildRequires: boost-devel >= 1.37.0
- Adding gearadmin files
- Converted to Systemd.  Resolves BZ#661643

* Tue Mar 22 2011 Dan Horák <dan[at]danny.cz> - 0.14-4
- switch to %%ifarch for google-perftools as BR

* Thu Feb 17 2011 BJ Dierkes <wdierkes@rackspace.com> - 0.14-3
- Rebuild against latest libevent in rawhide/f15

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.14-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Feb 04 2011 BJ Dierkes <wdierkes@rackspace.com> - 0.14-1
- Latest sources from upstream.  Full changelog available from:
  https://launchpad.net/gearmand/trunk/0.14

* Wed Oct 06 2010 Remi Collet <fedora@famillecollet.com> - 0.13-3
- rebuild against new libmemcached

* Wed May 05 2010 Remi Collet <fedora@famillecollet.com> - 0.13-2
- rebuild against new libmemcached

* Wed Apr 07 2010 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.13-1
- Upstream released new version

* Fri Feb 19 2010 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.12-1
- Upstream released new version

* Wed Feb 17 2010 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.11-2
- Add BR on libtool

* Tue Feb 16 2010 Oliver Falk <oliver@linux-kernel.at> 0.11-1
- Update to latest upstream version (#565808)
- Add missing Req. libevent-devel for libgearman-devel (#565808)
- Remove libmemcache patch - should be fixed in 0.11

* Sun Feb 07 2010 Remi Collet <fedora@famillecollet.com> - 0.9-3
- patch to detect libmemcached

* Sun Feb 07 2010 Remi Collet <fedora@famillecollet.com> - 0.9-2
- rebuilt against new libmemcached

* Fri Jul 31 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.9-1
- Upstream released new version

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.8-1
- Upstream released new version
- Enable libmemcached backend

* Mon Jun 22 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.7-1
- Upstream released new version

* Mon Jun 22 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.6-3
- Don't build with tcmalloc on sparc64

* Sun May 24 2009 Peter Lemenkov <lemenkov@gmail.com> 0.6-2
- Fixed issues, reported in https://bugzilla.redhat.com/show_bug.cgi?id=487148#c9

* Wed May 20 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.6-1
- Upstream released new version

* Mon Apr 27 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.5-1
- Upstream released new version
- Cleanups for review (bz #487148)

* Wed Feb 25 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.3-2
- Add init script

* Sat Feb 07 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 0.3-1
- Initial import

