%global oname libdrm

Summary:	Direct Rendering Manager runtime library (for Poulsbo)
Name:		libdrm-poulsbo
Version:	2.3.0
Release:	9%{?dist}
License:	MIT
Group:		System Environment/Libraries
URL:		http://ppa.launchpad.net/ubuntu-mobile/ubuntu/pool/main/libd/libdrm-poulsbo/
Source0:	http://ppa.launchpad.net/ubuntu-mobile/ubuntu/pool/main/libd/libdrm-poulsbo/%{name}_%{version}.orig.tar.gz
# Extra sources are extracted from Ubuntu diff
Source1:	psb_drm.h
Source2:	psb_drv.h
Source3:	psb_reg.h
Source4:	psb_schedule.h
Patch0:		libdrm-poulsbo_configure_debian.patch
Patch1:		libdrm-poulsbo_headers_debian.patch
Patch2:		libdrm-poulsbo-relocate_headers.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%if 0%{?fedora} > 11
ExclusiveArch:  i686
%else %if 0%{?fedora} > 10
ExclusiveArch:  i586
%else
ExclusiveArch:  i386
%endif

Requires:	udev
Requires:	kernel
BuildRequires:	pkgconfig
BuildRequires:	libtool
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	kernel-headers
BuildRequires:	libxcb-devel
BuildRequires:	libudev-devel
# For the file we can't carry in both
Requires:	libdrm

%description
Direct Rendering Manager runtime library. This build is specifically
for the xorg-x11-drv-psb driver, for Intel Poulsbo graphics chipsets.
As it is versioned lower than the normal build of libdrm, it is set to
obsolete that version, so it can be installed smoothly. If you wish to
revert to the regular version of libdrm for any reason, you will need
to force the removal of this version with 'rpm -e --nodeps' before you
are able to.

%package devel
Summary:	Direct Rendering Manager development package
Group:		Development/Libraries

Requires:	%{name} = %{version}-%{release}
Requires:	kernel-headers
Requires:	pkgconfig

%description devel
Direct Rendering Manager development package. This build is
specifically for the xorg-x11-drv-psb driver, for Intel Poulsbo
graphics chipsets. 

%prep
%setup -q -n %{oname}-%{version}
install -m 0644 %{SOURCE1} shared-core/
install -m 0644 %{SOURCE2} shared-core/
install -m 0644 %{SOURCE3} shared-core/
install -m 0644 %{SOURCE4} shared-core/
%patch0 -p1
%patch1 -p1 -b .headers
%patch2 -p1 -b .relocate

%build
autoreconf -i
%configure --libdir=%{_libdir}/psb
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
# SUBDIRS=libdrm
mkdir -p %{buildroot}%{_sysconfdir}/udev/rules.d/

# NOTE: We intentionally don't ship *.la files
find %{buildroot} -type f -name '*.la' | xargs rm -f -- || :
for i in i915 mach64 mga nouveau r128 radeon savage sis via; do rm -f %{buildroot}%{_includedir}/psb/drm/$i"_drm.h"; done
for i in drm_sarea.h r300_reg.h via_3d_reg.h
do
rm -f %{buildroot}%{_includedir}/psb/drm/$i
done

# clean up for relocation
mkdir -p %{buildroot}%{_libdir}/pkgconfig
mv %{buildroot}%{_libdir}/psb/pkgconfig/libdrm.pc %{buildroot}%{_libdir}/pkgconfig/libdrm-poulsbo.pc
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
cat > %{buildroot}%{_sysconfdir}/ld.so.conf.d/psb.conf << EOF
%{_libdir}/psb
EOF

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc MIT_License.txt README
%{_libdir}/psb/libdrm.so.2
%{_libdir}/psb/libdrm.so.2.3.0
%config %{_sysconfdir}/ld.so.conf.d/psb.conf

%files devel
%defattr(-,root,root,-)
%doc MIT_License.txt
%dir %{_includedir}/psb
%dir %{_includedir}/psb/drm
# NOTE: Headers are listed explicitly, so we can monitor additions/removals.
%{_includedir}/psb/drm/drm.h
%{_includedir}/psb/drm/psb_drv.h
%{_includedir}/psb/drm/psb_drm.h
%{_includedir}/psb/drm/psb_reg.h
%{_includedir}/psb/drm/psb_schedule.h
# FIXME should be in drm/ too
%{_includedir}/psb/xf86drm.h
%{_includedir}/psb/xf86drmMode.h
%{_includedir}/psb/xf86mm.h
%{_libdir}/psb/libdrm.so
%{_libdir}/pkgconfig/libdrm-poulsbo.pc

%changelog
* Mon Aug 24 2009 Adam Williamson <awilliam@redhat.com> 2.3.0-9
- correct exclusivearch for rpmfusion buildsystem
- don't install 91-drm-modeset.rules only to delete it later

* Thu Aug 20 2009 Adam Williamson <awilliam@redhat.com> 2.3.0-8
- exclusivearch ix86 (there's no 64-bit poulsbo hardware)
- mark config file as config

* Wed Aug 19 2009 Adam Williamson <awilliam@redhat.com> 2.3.0-7
- put the license in as documentation

* Tue Aug 11 2009 Adam Williamson <awilliam@redhat.com> 2.3.0-6
- The Let's Stop Smoking Crack release: move the library to libdir/psb
  and use an ld.so.conf.d file, thus avoiding all the obsoletes /
  provides tomfoolery and co-existing peacefully with main libdrm 
  thanks lkundrak for the suggestion

* Mon Aug 10 2009 Adam Williamson <awilliam@redhat.com> 2.3.0-5
- more outrageous lies in the -devel package

* Mon Aug 10 2009 Adam Williamson <awilliam@redhat.com> 2.3.0-4
- use ldconfig -X in %post and %postun to (hopefully) work around the
  nasty #513224 in normal use of these packages (this should be the
  only library installed in the initial transaction people use)

* Mon Aug 10 2009 Adam Williamson <awilliam@redhat.com> 2.3.0-3
- lie outrageously about what we provide to satisfy some dependencies

* Mon Aug 10 2009 Adam Williamson <awilliam@redhat.com> 2.3.0-2
- obsolete / provide regular libdrm

* Wed May 13 2009 Adam Williamson <awilliam@redhat.com> 2.3.0-1
- initial poulsbo libdrm package (from ubuntu-mobile repos)

