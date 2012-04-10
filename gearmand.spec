
Name:           gearmand
Version:        0.31
Release:        1%{?dist}
Summary:        A distributed job system

Group:          System Environment/Daemons
License:        BSD
URL:            http://www.gearman.org
Source0:        http://launchpad.net/gearmand/trunk/%{version}/+download/gearmand-%{version}.tar.gz 
#Source1:        gearmand.init
Source2:        gearmand.sysconfig
Source3:        gearmand.service
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libevent-devel, libuuid-devel, libmemcached-devel, memcached
BuildRequires:  boost-devel >= 1.37.0
BuildRequires:  systemd-units

# google perftools available only on these
%ifarch %{ix86} x86_64 ppc
BuildRequires: google-perftools-devel
%endif
Requires(pre):   shadow-utils
Requires:        procps

# This is actually needed for the %triggerun script but Requires(triggerun)
# is not valid.  We can use %post because this particular %triggerun script
# should fire just after this package is installed.
Requires(post): systemd-sysv
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

#Patch0: gearmand-0.27-lp914495.patch 
Patch1: gearmand-0.28-lp932994.patch

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
Group:          Development/Libraries

%description -n libgearman
Development libraries for %{name}.

%package -n libgearman-devel
Summary:        Development headers for libgearman
Requires:       pkgconfig, libgearman = %{version}-%{release}
Group:          Development/Libraries
Requires:       libevent-devel

%description -n libgearman-devel
Development headers for %{name}.

%package -n libgearman-1.0
Summary:        Development libraries for gearman 1.0
Group:          Development/Libraries

%description -n libgearman-1.0
Development libraries for %{name} 1.0.

%package -n libgearman-1.0-devel
Summary:        Development headers for libgearman 1.0
Requires:       pkgconfig, libgearman = %{version}-%{release}
Group:          Development/Libraries
Requires:       libevent-devel

%description -n libgearman-1.0-devel
Development headers for %{name} 1.0.


%prep
%setup -q
%patch1 -p1 -b .lp932994

%build
%ifarch ppc64 sparc64
# no tcmalloc
%configure --disable-static --disable-rpath
%else
%configure --disable-static --disable-rpath --enable-tcmalloc
%endif

sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{_smp_mflags}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
rm -v %{buildroot}%{_libdir}/libgearman*.la
#install -p -D -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/gearmand
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/gearmand
mkdir -p    %{buildroot}/var/run/gearmand \
            %{buildroot}%{_unitdir}

# For systemd
install -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service

%clean
rm -rf %{buildroot}


%pre
getent group gearmand >/dev/null || groupadd -r gearmand
getent passwd gearmand >/dev/null || \
        useradd -r -g gearmand -d / -s /sbin/nologin \
        -c "Gearmand job server" gearmand
exit 0

%post
if [ $1 -eq 1 ] ; then 
    # Initial installation 
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable gearmand.service > /dev/null 2>&1 || :
    /bin/systemctl stop gearmand.service > /dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart gearmand.service >/dev/null 2>&1 || :
fi

%triggerun -- gearmand < 0.20-1
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply gearmand 
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save gearmand >/dev/null 2>&1 ||:

#Run these because the SysV package being removed won't do them
/sbin/chkconfig --del gearmand >/dev/null 2>&1 || :
/bin/systemctl try-restart gearmand.service >/dev/null 2>&1 || :

%post -n libgearman -p /sbin/ldconfig

%postun -n libgearman -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING README
%ghost %attr(755,gearmand,gearmand) /var/run/gearmand
%config(noreplace) %{_sysconfdir}/sysconfig/gearmand
%{_sbindir}/gearmand
%{_bindir}/gearman
%{_bindir}/gearadmin
#%%{_initrddir}/gearmand
%{_unitdir}/%{name}.service
%{_mandir}/man1/gearman.1*
%{_mandir}/man8/gearmand.8*
%{_mandir}/man1/gearadmin.1*
%{_mandir}/man3/gearman*.3*

%files -n libgearman
%defattr(-,root,root,-)
%doc COPYING
%{_libdir}/libgearman.so.6
%{_libdir}/libgearman.so.6.0.0

%files -n libgearman-devel
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING README
%dir %{_includedir}/libgearman
%{_includedir}/libgearman/*.h
%{_libdir}/pkgconfig/gearmand.pc
%{_mandir}/man3/libgearman*.3*

%files -n libgearman-1.0
%defattr(-,root,root,-)
%{_libdir}/libgearman.so

%files -n libgearman-1.0-devel
%defattr(-,root,root,-)
%{_includedir}/libgearman-1.0/

%changelog
* Tue Apr 10 2012 BJ Dierkes <wdierkes@rackspace.com> - 0.31-1
- Latest sources from upstream.  Release notes here:
  https://launchpad.net/gearmand/trunk/0.31
  https://launchpad.net/gearmand/trunk/0.29

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

