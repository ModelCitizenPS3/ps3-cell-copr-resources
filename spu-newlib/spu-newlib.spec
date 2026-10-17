# newlib/libgloss contain SPU ELF objects: host strip/debuginfo/brp scripts must not touch them
%global debug_package %{nil}
%global __os_install_post %{nil}
%global _build_id_links none
%global _prefix /opt/cell/toolchain

Name:           spu-newlib
Version:        2.5.0
Release:        1%{?dist}
Summary:        newlib C library for the Cell Broadband Engine SPU
License:        BSD and GPLv2+ and LGPLv2+ and others
URL:            https://sourceware.org/newlib/
Source0:        ftp://sourceware.org/pub/newlib/newlib-%{version}.tar.gz
Source1:        https://ftp.gnu.org/gnu/gcc/gcc-9.5.0/gcc-9.5.0.tar.xz
Source2:        gcc-9.5.0-add-ppu-target.patch
Source3:        gcc-9.5.0-spu-nop-syntax.patch
ExclusiveArch:  x86_64

BuildRequires:  ppu-sysroot
BuildRequires:  spu-binutils
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cpp
BuildRequires:  gmp-devel
BuildRequires:  mpfr-devel
BuildRequires:  libmpc-devel
BuildRequires:  isl-devel
BuildRequires:  make
BuildRequires:  texinfo
AutoReq:        no
AutoProv:       no

%description
newlib C library (libc, libm) and libgloss start files (crt0.o etc.) for the
Cell SPU (spu target), built with the installed spu-elf-gcc rather than
inside the gcc source tree.


%prep
%setup -q -n newlib-%{version}
%setup -q -b 1 -T -D -n gcc-9.5.0
patch -p1 < %{SOURCE2}
patch -p1 < %{SOURCE3}


%build
mkdir -p build
pushd build
export AR="/opt/cell/toolchain/bin/spu-ar"
export LD="/opt/cell/toolchain/bin/spu-ld"
export AS="/opt/cell/toolchain/bin/spu-as"
export RANLIB="/opt/cell/toolchain/bin/spu-ranlib"
export NM="/opt/cell/toolchain/bin/spu-nm"
%undefine _auto_set_build_flags
%undefine _hardened_build
%undefine _annotated_build
%global _lto_cflags %{nil}
%global optflags -O2
%global build_cflags -O2
%global build_cxxflags -O2
%global build_ldflags %{nil}
unset CFLAGS CXXFLAGS FFLAGS FCFLAGS LDFLAGS LT_SYS_LIBRARY_PATH
export AR=ar RANLIB=ranlib NM=nm
CFLAGS="-std=gnu17 -Wno-error=format-security" CXXFLAGS="-Wno-error=format-security"
../configure --prefix=%{_builddir}/usr --build=$(gcc -dumpmachine) --host=$(gcc -dumpmachine) --target=spu-elf --program-prefix=spu- --without-headers --with-newlib --enable-languages=c --disable-libcc1 --disable-shared --disable-threads --disable-libssp --disable-libgomp --disable-libquadmath --disable-libatomic --disable-decimal-float --disable-multilib --with-multilib-list=m64 --enable-obsolete --with-gmp=/usr --with-mpfr=/usr --with-mpc=/usr --with-isl=/usr --with-ar=/opt/cell/toolchain/bin/spu-ar --with-as=/opt/cell/toolchain/bin/spu-as --with-ld=/opt/cell/toolchain/bin/spu-ld --with-ranlib=/opt/cell/toolchain/bin/spu-ranlib AR_FOR_TARGET="/opt/cell/toolchain/bin/spu-ar" RANLIB_FOR_TARGET="/opt/cell/toolchain/bin/spu-ranlib" RANLIB_FOR_TARGET="/opt/cell/toolchain/bin/spu-ranlib" AS_FOR_TARGET="/opt/cell/toolchain/bin/spu-as" LD_FOR_TARGET="/opt/cell/toolchain/bin/spu-ld" NM_FOR_TARGET="/opt/cell/toolchain/bin/spu-nm"

# INJECTION: Force-create the libcc1 directory and build-stub so make doesn't break
mkdir -p libcc1
echo -e "all:\n\t@echo 'Skipping libcc1 build'\ninstall:\n\t@echo 'Skipping libcc1 install'" > libcc1/Makefile

make all-gcc all-target-libgcc
make install-gcc install-target-libgcc
popd

pushd ../newlib-2.5.0
mkdir -p build
pushd build
export CC=gcc
export CXX=g++
export CC_FOR_TARGET=%{_builddir}/usr/bin/spu-gcc
export CFLAGS=-O2
export CXXFLAGS=-O2
export CFLAGS_FOR_TARGET=-O2
export LDFLAGS=
shim=%{_builddir}/shim
rm -rf $shim && mkdir -p $shim
for t in ar as ld nm ranlib strip objcopy objdump; do
    [ -x /opt/cell/toolchain/bin/spu-$t ] && ln -s /opt/cell/toolchain/bin/spu-$t $shim/spu-elf-$t
done
# Fix undefined macro fallback logic for stage1 variable
ln -s %{_builddir}/usr/bin/spu-gcc $shim/spu-elf-gcc
export PATH=$shim:%{_builddir}/usr/bin:$PATH
../configure \
    --target=spu-elf \
    --prefix=/opt/cell/toolchain \
    --disable-libcc1 \
    --disable-nls
make DESTDIR=%{buildroot} %{?_smp_mflags}
popd


%check


%install
rm -rf %{buildroot}
cd ../newlib-%{version}
export PATH=%{_builddir}/shim:/opt/cell/toolchain/bin:$PATH

# INJECTION: Re-verify dummy stub exists in the newlib directory scope if needed
mkdir -p build/libcc1
echo -e "all:\n\t@echo 'Skipping libcc1 build'\ninstall:\n\t@echo 'Skipping libcc1 install'" > build/libcc1/Makefile

make -C build DESTDIR=%{buildroot} -j1 install


%files
%dir %{_prefix}/spu-elf/include
%{_prefix}/spu-elf/include/*
%dir %{_prefix}/spu-elf/lib
%{_prefix}/spu-elf/lib/*


%changelog
* Sat Oct 10 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.5.0-1
- For Cell/B.E. Linux https://ps3linux.net

