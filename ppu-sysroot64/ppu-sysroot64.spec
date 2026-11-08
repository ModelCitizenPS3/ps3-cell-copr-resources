%undefine optflags
%undefine build_cflags
%undefine build_cxxflags
%undefine build_ldflags
%undefine _hardened_build
%undefine _annotated_build
%undefine _auto_set_build_flags
%undefine _auto_set_build_flags

%global glibc_ver    2.32
%global gcc_ver      9.5.0
%global kver         5.8.18
%global sysroot      /opt/cell/sysroot

# Everything we ship is ppc64 ELF; none of the host-side RPM post-processing
# (strip, debuginfo, build-id links, dependency scanning) may touch it.
%global debug_package %{nil}
%global __os_install_post %{nil}
%global __strip /bin/true
%global _build_id_links none
%global __requires_exclude ^.*$
%global __provides_exclude_from ^%{sysroot}/.*$

Name:           ppu-sysroot64
Version:        %{glibc_ver}
Release:        1.CELL
Summary:        Cross sysroot (glibc + kernel headers) for the Cell PPU, 64-bit
License:        LGPLv2+ and LGPLv2+ with exceptions and GPLv2+ and BSD and Inner-Net and ISC and Public Domain and GFDL
URL:            https://www.gnu.org/software/libc/
Source0:        https://ftp.gnu.org/gnu/glibc/glibc-%{glibc_ver}.tar.xz
Source1:        https://ftp.gnu.org/gnu/gcc/gcc-%{gcc_ver}/gcc-%{gcc_ver}.tar.xz
Source2:        https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-%{kver}.tar.xz
Source3:        gcc-9.5.0-add-ppu-target.patch
Source4:        gcc-9.5.0-format-security-syntax-fix.patch
ExclusiveArch:  x86_64

BuildRequires:  ppu-binutils, texinfo, rsync, python3
BuildRequires:  gcc, gcc-c++, cpp, make, bison, flex, gawk, sed, perl-interpreter
BuildRequires:  gmp-devel, mpfr-devel, libmpc-devel

%description
Target-side root for cross-compiling 64-bit PPU code on x86_64: Linux kernel
headers for powerpc and a cross-built glibc (headers, startfiles, libc.so,
libc.a, ld64.so.1, libm, libpthread, ...). Installed under %{sysroot}.


%prep
%setup -q -c -T -n %{name}-%{version}
tar -xf %{SOURCE0}
tar -xf %{SOURCE1}
tar -xf %{SOURCE2}
pushd gcc-%{gcc_ver}
patch -p1 < %{SOURCE3}
patch -p1 < %{SOURCE4}
popd


%build
BOOT=$PWD/bootstrap
STAGE=$PWD/kernel-headers

# --- 1. Kernel headers ------------------------------------------------------
make -C linux-%{kver} ARCH=powerpc headers_install INSTALL_HDR_PATH=$STAGE

# --- 2. Bootstrap cross gcc (C only, static libgcc, no libc) ----------------
mkdir build-gcc && pushd build-gcc
AR_FOR_TARGET=/opt/cell/toolchain/bin/ppu-ar \
RANLIB_FOR_TARGET=/opt/cell/toolchain/bin/ppu-ranlib \
../gcc-%{gcc_ver}/configure \
    --prefix=$BOOT \
    --build=%{_build} --host=%{_build} \
    --target=ppu \
    --program-prefix=ppu- \
    --with-as=/opt/cell/toolchain/bin/ppu-as \
    --with-ld=/opt/cell/toolchain/bin/ppu-ld \
    --with-cpu=cell \
    --with-long-double-128 \
    --disable-multilib \
    --without-headers --with-newlib \
    --enable-languages=c \
    --disable-shared --disable-threads --disable-nls --disable-bootstrap \
    --disable-decimal-float \
    --disable-libatomic --disable-libgomp --disable-libitm \
    --disable-libquadmath --disable-libsanitizer --disable-libssp \
    --disable-libvtv --disable-libcilkrts \
    --without-isl
make -j1 all-gcc all-target-libgcc
make -j1 install-gcc install-target-libgcc
popd

# glibc links with -lgcc_eh, which a --disable-shared libgcc does not build
# separately. The unwinder is inside libgcc.a, so alias it.
LIBGCC=$($BOOT/bin/ppu-gcc -print-libgcc-file-name)
ln -sf libgcc.a "$(dirname "$LIBGCC")/libgcc_eh.a"

# --- 3. glibc ---------------------------------------------------------------
mkdir build-glibc && pushd build-glibc

# ppc64 big-endian glibc uses /lib64 and /usr/lib64.
cat > configparms <<EOF
slibdir=/lib
rtlddir=/lib
libdir=/usr/lib
BUILD_CC=gcc
EOF

CC="$BOOT/bin/ppu-gcc" \
AR=/opt/cell/toolchain/bin/ppu-ar RANLIB=/opt/cell/toolchain/bin/ppu-ranlib NM=/opt/cell/toolchain/bin/ppu-nm \
OBJDUMP=/opt/cell/toolchain/bin/ppu-objdump OBJCOPY=/opt/cell/toolchain/bin/ppu-objcopy READELF=/opt/cell/toolchain/bin/ppu-readelf \
CFLAGS="-O2 -pipe -mcpu=cell -mtune=cell" \
libc_cv_forced_unwind=yes \
libc_cv_c_cleanup=yes \
../glibc-%{glibc_ver}/configure \
    --prefix=/usr \
    --libdir=/usr/lib \
    --build=%{_build} \
    --host=powerpc64-linux \
    --with-headers=$STAGE/include \
    --enable-kernel=5.8 \
    --disable-werror --disable-profile --disable-nscd \
    --without-selinux --without-gd
make -j1
popd


%check


%install
P=ppu-

# Kernel headers first, glibc installs over/alongside them.
install -d %{buildroot}%{sysroot}/usr
cp -a kernel-headers/include %{buildroot}%{sysroot}/usr/

make -C build-glibc -j1 install install_root=%{buildroot}%{sysroot}

# Cross-sysroot housekeeping: no info dir, no locale catalogs (cannot run
# localedef for the target on the build host).
rm -rf %{buildroot}%{sysroot}/usr/share/info
rm -rf %{buildroot}%{sysroot}/usr/share/locale

# Strip debug info using the *target* strip; the host strip cannot handle
# ppc64 objects. --strip-debug is safe for ld.so, archives and crt objects.
find %{buildroot}%{sysroot} -type f \( -name '*.a' -o -name '*.o' -o -name '*.so' -o -name '*.so.*' \) -exec ppu-strip --strip-debug {} + 2>/dev/null || :


%files
%license glibc-%{glibc_ver}/COPYING glibc-%{glibc_ver}/COPYING.LIB glibc-%{glibc_ver}/LICENSES
%dir %{sysroot}
%{sysroot}/*


%changelog
* Sat Nov 7 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.32-1
- Initial build

