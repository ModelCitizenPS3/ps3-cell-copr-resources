%undefine optflags
%undefine build_cflags
%undefine build_cxxflags
%undefine build_ldflags
%undefine _hardened_build
%undefine _annotated_build
%undefine _auto_set_build_flags

# newlib/libgloss contain SPU ELF objects: host strip/debuginfo/brp scripts must not touch them
%global debug_package %{nil}
%global __os_install_post %{nil}
%global _build_id_links none

%ifarch x86_64
%define _prefix /opt/cell/toolchain
%define spu_gcc_path /opt/cell/toolchain/bin/spu-gcc
%endif
%ifarch ppc64
%define spu_gcc_path /usr/bin/spu-gcc
%endif

%global bootstrap_gcc %{expand:%(if [ -x %{spu_gcc_path} ]; then echo 0; else echo 1; fi)}

Name:           spu-newlib
Version:        2.5.0
Release:        1.CELL
Summary:        newlib C library for the Cell Broadband Engine SPU
License:        BSD and GPLv2+ and LGPLv2+ and others
URL:            https://sourceware.org/newlib/
Source0:        https://sourceware.org/pub/newlib/newlib-%{version}.tar.gz
Source1:        https://ftp.gnu.org/gnu/gcc/gcc-9.5.0/gcc-9.5.0.tar.xz
ExclusiveArch:  ppc64 x86_64

BuildRequires:  spu-binutils, gcc, cpp, gcc-c++, make, texinfo
BuildRequires:  gmp-devel, mpfr-devel, libmpc-devel, isl-devel
%if ! %{bootstrap_gcc}
%ifarch x86_64
BuildRequires:  /opt/cell/toolchain/bin/spu-gcc
%endif
%ifarch ppc64
BuildRequires:  /usr/bin/spu-gcc
%endif
%endif

Requires:       gmp, mpfr, libmpc, isl
AutoReq:        no
AutoProv:       no

%description
newlib C library (libc, libm) and libgloss start files (crt0.o etc.) for the
Cell SPU (spu target), built with the installed spu-gcc rather than inside
the gcc source tree.


%prep
%setup -q -n newlib-%{version}
%if %{bootstrap_gcc}
cd ..
tar -xf %{SOURCE1}
cd gcc-9.5.0
ln -s ../newlib-%{version}/newlib newlib
ln -s ../newlib-%{version}/libgloss libgloss
%endif


%build
%if %{bootstrap_gcc}
    cd ../
    mkdir -p gcc-bootstrap
    cd gcc-bootstrap
    AR_FOR_TARGET=%{_prefix}/bin/spu-ar \
    AS_FOR_TARGET=%{_prefix}/bin/spu-as \
    LD_FOR_TARGET=%{_prefix}/bin/spu-ld \
    RANLIB_FOR_TARGET=%{_prefix}/bin/spu-ranlib \
    ../gcc-9.5.0/configure \
        --target=spu \
        --prefix=/usr \
        --with-newlib \
        --disable-nls \
        --enable-languages=c \
        --enable-obsolete \
        %ifarch x86_64
        --with-as=/opt/cell/toolchain/bin/spu-as \
        --with-ld=/opt/cell/toolchain/bin/spu-ld
        %endif
        %ifarch ppc64
        --with-as=/usr/bin/spu-as \
        --with-ld=/usr/bin/spu-ld
        %endif
    make -j1
    mkdir -p %{_builddir}/bootstrap
    make -j1 DESTDIR=%{_builddir}/bootstrap install
    %define spu_gcc_path %{_builddir}/bootstrap/usr/bin/spu-gcc
%endif
    cd ../
    mkdir -p newlib-build
    cd newlib-build
    export CFLAGS="-O2 -g"
    export CXXFLAGS="-O2 -g"
    export LDFLAGS=
    export CC_FOR_TARGET=%{spu_gcc_path}
    export AR_FOR_TARGET=%{_prefix}/bin/spu-ar
    export AS_FOR_TARGET=%{_prefix}/bin/spu-as
    export LD_FOR_TARGET=%{_prefix}/bin/spu-ld
    export NM_FOR_TARGET=%{_prefix}/bin/spu-nm
    export RANLIB_FOR_TARGET=%{_prefix}/bin/spu-ranlib
    ../newlib-%{version}/configure \
        --target=spu \
        --prefix=%{_prefix} \
        --libdir=%{_prefix}/lib \
        --disable-nls
    make -j1


%check


%install
rm -rf %{buildroot}
cd ../newlib-build
make DESTDIR=%{buildroot} -j1 install


%files
%dir %{_prefix}/spu/include
%{_prefix}/spu/include/*
%dir %{_prefix}/spu/lib
%{_prefix}/spu/lib/*


%changelog
* Sat Nov 7 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.5.0-1
- Initial build

