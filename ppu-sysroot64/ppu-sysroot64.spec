# Cross build: the host's hardened/annobin flags must not reach the target toolchain
%undefine _auto_set_build_flags

%global gnu_target   ppu
%global tool_prefix  ppu-
%global sysroot      /opt/cell/sysroot

%global glibc_ver    2.32
%global gcc_ver      9.5.0
%global kver         5.8.18

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

BuildRequires:  ppu-binutils
BuildRequires:  gcc, gcc-c++, cpp, make, bison, flex, gawk, sed, perl-interpreter
BuildRequires:  texinfo, rsync
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
TOP=$PWD
BOOT=$TOP/bootstrap
STAGE=$TOP/kernel-headers
P=%{tool_prefix}

# --- 1. Kernel headers ------------------------------------------------------
make -C linux-%{kver} ARCH=powerpc headers_install INSTALL_HDR_PATH=$STAGE

# --- 2. Bootstrap cross gcc (C only, static libgcc, no libc) ----------------
mkdir build-gcc && pushd build-gcc
../gcc-%{gcc_ver}/configure \
    --prefix=$BOOT \
    --build=%{_build} --host=%{_build} \
    --target=%{gnu_target} \
    --program-prefix=$P \
    --with-as=/opt/cell/toolchain/bin/${P}as \
    --with-ld=/opt/cell/toolchain/bin/${P}ld \
    --with-ar=/opt/cell/toolchain/bin/${P}ar \
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
make all-gcc all-target-libgcc
make install-gcc install-target-libgcc
popd

# glibc links with -lgcc_eh, which a --disable-shared libgcc does not build
# separately. The unwinder is inside libgcc.a, so alias it.
LIBGCC=$($BOOT/bin/${P}gcc -print-libgcc-file-name)
ln -sf libgcc.a "$(dirname "$LIBGCC")/libgcc_eh.a"

# --- 3. glibc ---------------------------------------------------------------
mkdir build-glibc && pushd build-glibc

# ppc64 big-endian glibc uses /lib64 and /usr/lib64.
cat > configparms <<EOF
slibdir=/lib64
rtlddir=/lib64
libdir=/usr/lib64
BUILD_CC=gcc
EOF

CC="$BOOT/bin/${P}gcc" \
AR=${P}ar RANLIB=${P}ranlib NM=${P}nm \
OBJDUMP=${P}objdump OBJCOPY=${P}objcopy READELF=${P}readelf \
CFLAGS="-O2 -pipe -mcpu=cell -mtune=cell" \
libc_cv_forced_unwind=yes \
libc_cv_c_cleanup=yes \
../glibc-%{glibc_ver}/configure \
    --prefix=/usr \
    --build=%{_build} \
    --host=powerpc64-linux-gnu \
    --with-headers=$STAGE/include \
    --enable-kernel=5.8 \
    --disable-werror --disable-profile --disable-nscd \
    --without-selinux --without-gd
make
popd


%check


%install
TOP=$PWD
P=%{tool_prefix}

# Kernel headers first, glibc installs over/alongside them.
install -d %{buildroot}%{sysroot}/usr
cp -a kernel-headers/include %{buildroot}%{sysroot}/usr/

make -C build-glibc install install_root=%{buildroot}%{sysroot}

# Cross-sysroot housekeeping: no info dir, no locale catalogs (cannot run
# localedef for the target on the build host).
rm -rf %{buildroot}%{sysroot}/usr/share/info
rm -rf %{buildroot}%{sysroot}/usr/share/locale

# Strip debug info using the *target* strip; the host strip cannot handle
# ppc64 objects. --strip-debug is safe for ld.so, archives and crt objects.
find %{buildroot}%{sysroot} -type f \( -name '*.a' -o -name '*.o' -o -name '*.so' -o -name '*.so.*' \) \
    -exec %{tool_prefix}strip --strip-debug {} + 2>/dev/null || :


%files
%license glibc-%{glibc_ver}/COPYING glibc-%{glibc_ver}/COPYING.LIB glibc-%{glibc_ver}/LICENSES
%{sysroot}

%changelog
* Sat Nov 07 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.32-1
- Initial build

