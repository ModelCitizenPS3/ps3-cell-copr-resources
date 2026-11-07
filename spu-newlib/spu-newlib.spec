%undefine optflags
%undefine build_cflags
%undefine build_cxxflags
%undefine build_ldflags
%undefine _hardened_build
%undefine _annotated_build
# newlib/libgloss contain SPU ELF objects: host strip/debuginfo/brp scripts must not touch them
%global debug_package %{nil}
%global __os_install_post %{nil}
%global _build_id_links none

%ifarch x86_64
%define _prefix /opt/cell/toolchain
%endif

Name:           spu-newlib
Version:        2.5.0
Release:        1.CELL
Summary:        newlib C library for the Cell Broadband Engine SPU
License:        BSD and GPLv2+ and LGPLv2+ and others
URL:            https://sourceware.org/newlib/
Source0:        https://sourceware.org/pub/newlib/newlib-%{version}.tar.gz
ExclusiveArch:  ppc64 x86_64

BuildRequires:  spu-binutils, gcc, cpp, gcc-c++, make, texinfo
BuildRequires:  gmp-devel, mpfr-devel, libmpc-devel, isl-devel
BuildRequires:  spu-gcc, spu-gcc-c++
Requires:       gmp, mpfr, libmpc, isl
Obsoletes:      spu-gcc <= 9.5.0-2.CELL
Obsoletes:      spu-gcc-c++ <= 9.5.0-2.CELL
AutoReq:        no
AutoProv:       no

%description
newlib C library (libc, libm) and libgloss start files (crt0.o etc.) for the
Cell SPU (spu target), built with the installed spu-gcc rather than inside
the gcc source tree.


%prep
%setup -q -n newlib-%{version}


%build
rm -rf build
mkdir -p build
pushd build
CC=gcc \
CXX=g++ \
CFLAGS="-O2 -g" \
CXXFLAGS="-O2 -g" \
LDFLAGS= \
CC_FOR_TARGET=%{_prefix}/bin/spu-gcc \
CXX_FOR_TARGET=%{_prefix}/bin/spu-g++ \
AR_FOR_TARGET=%{_prefix}/bin/spu-ar \
AS_FOR_TARGET=%{_prefix}/bin/spu-as \
LD_FOR_TARGET=%{_prefix}/bin/spu-ld \
NM_FOR_TARGET=%{_prefix}/bin/spu-nm \
RANLIB_FOR_TARGET=%{_prefix}/bin/spu-ranlib \
../configure \
    --target=spu \
    --prefix=%{_prefix} \
    --libdir=%{_prefix}/lib \
    --disable-nls
make -j1
popd


%check


%install
rm -rf %{buildroot}
make -C build DESTDIR=%{buildroot} -j1 install


%files
%dir %{_prefix}/spu/include
%{_prefix}/spu/include/*
%dir %{_prefix}/spu/lib
%{_prefix}/spu/lib/*


%changelog
* Sat Nov 7 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.5.0-1
- Initial build - https://ps3linux.net

