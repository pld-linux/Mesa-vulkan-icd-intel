#
# The driver will be merged into mainstream Mesa. Will will build it then
# from the Mesa.spec and use Mesa version number.
#
# Conditional build:
%bcond_without	wayland		# Wayland WSI support
#
%define snap	20160228
Summary:	Vulkan driver for Intel GPUs
Name:		Mesa-vulkan-icd-intel
Version:	0.s%{snap}
Release:	1
License:	MIT (core) and others - see license.html file
Group:		X11/Libraries
# git archive --format=tar --prefix=Mesa-vulkan-s20160228/ vulkan | xz > ../Mesa-vulkan-s20160228.tar.xz
Source0:	Mesa-vulkan-s%{snap}.tar.xz
# Source0-md5:	631e3e030ae3d6397c2da27def59417a
Patch0:		keep_git_sha.patch
URL:		http://www.mesa3d.org/
BuildRequires:	autoconf >= 2.60
BuildRequires:	automake
BuildRequires:	elfutils-devel
BuildRequires:	expat-devel
BuildRequires:	gcc >= 6:4.2.0
BuildRequires:	git-core
BuildRequires:	libdrm-devel >= %{libdrm_ver}
BuildRequires:	libstdc++-devel >= 6:4.2.0
BuildRequires:	libtalloc-devel >= 2:2.0.1
BuildRequires:	libtool >= 2:2.2
BuildRequires:	libxcb-devel >= 1.10
BuildRequires:	llvm-devel >= 3.4.2
# for SHA1 (could use also libmd/libsha1/libgcrypt/openssl instead)
BuildRequires:	libxcb-devel
BuildRequires:	libxcb-devel
BuildRequires:	nettle-devel
BuildRequires:	perl-base
BuildRequires:	pixman-devel
BuildRequires:	pkgconfig
BuildRequires:	python >= 2
BuildRequires:	python-Mako >= 0.3.4
BuildRequires:	python-modules >= 2
BuildRequires:	rpmbuild(macros) >= 1.470
BuildRequires:	sed >= 4.0
BuildRequires:	talloc-devel >= 2.0.1
%{?with_wayland:BuildRequires:	wayland-devel >= 1.2.0}
BuildRequires:	xorg-lib-libXdamage-devel
BuildRequires:	xorg-lib-libXext-devel >= 1.0.5
BuildRequires:	xorg-lib-libXfixes-devel
BuildRequires:	xorg-lib-libXt-devel
BuildRequires:	xorg-lib-libXvMC-devel >= 1.0.6
BuildRequires:	xorg-lib-libXxf86vm-devel
BuildRequires:	xorg-lib-libxshmfence-devel >= 1.1
BuildRequires:	xorg-proto-dri3proto-devel >= %{dri3proto_ver}
BuildRequires:	xorg-util-makedepend
Suggests:	vulkan(loader)
Provides:	vulkan(icd) = 1.0.3
ExclusiveArch:	%x8664 x32
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Mesa Vulkan driver for Intel GPUs.

%package devel
Summary:	Header files for %{name} Intel Vulkan driver
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for %{name} Intel Vulkan driver.

%prep
%setup -q -n Mesa-vulkan-s%{snap}
%patch0 -p1

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__automake}

%configure \
	--disable-silent-rules \
	--disable-gbm \
	--disable-glx-tls \
	--disable-osmesa \
	--enable-selinux \
	--enable-shared \
	%{?with_static_libs:--enable-static} \
	%{?with_texture_float:--enable-texture-float} \
	--enable-egl \
	--disable-gles1 \
	--disable-gles2 \
	--with-egl-platforms=x11%{?with_wayland:,wayland} \
	--disable-gallium-llvm \
	--disable-nine \
	--disable-opencl \
	--disable-vdpau \
	--disable-xvmc \
	--without-gallium-drivers \
	--with-dri-drivers=i965 \
	--with-dri-driverdir=%{_libdir}/xorg/modules/dri \
	--with-sha1=libnettle \
	--with-va-libdir=%{_libdir}/libva/dri

echo "#define MESA_GIT_SHA1 \"$(xzcat %{SOURCE0}|git get-tar-commit-id|cut -c-7)\"" > src/mesa/main/git_sha1.h

%{__make}

%{?with_tests:%{__make} check}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
icdconfdir=%{_datadir}/vulkan/icd.d \
	DESTDIR=$RPM_BUILD_ROOT

sed -e's@%{_libdir}/@@' \
	$RPM_BUILD_ROOT%{_datadir}/vulkan/icd.d/intel_icd.json \
	> $RPM_BUILD_ROOT%{_datadir}/vulkan/icd.d/Mesa-intel_icd.json
rm $RPM_BUILD_ROOT%{_datadir}/vulkan/icd.d/intel_icd.json

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.intel-vulkan.txt docs/license.html
%{_libdir}/libvulkan_intel.so
%{_datadir}/vulkan/icd.d/*.json

%files devel
%defattr(644,root,root,755)
%doc README.intel-vulkan.txt docs/license.html
%{_libdir}/libvulkan_intel.la
%{_includedir}/vulkan/vulkan_intel.h
