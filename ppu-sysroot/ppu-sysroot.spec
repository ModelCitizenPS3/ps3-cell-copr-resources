# ppu-sysroot: Linux 6.18 UAPI headers + glibc 2.40 for ppc64 (Cell/B.E. PPU)
#
# Stage 1 compiler is Fedora's cross gcc (gcc-powerpc64-linux-gnu); the
# assembler/linker/archiver are our own ppu-binutils (/opt/cell/toolchain),
# which are substituted for Fedora's binutils through a shim directory.
# Nothing here depends on ppu-gcc.  Build order:
#
#   ppu-binutils  ->  ppu-sysroot (Fedora cross gcc + ppu-binutils)  ->  ppu-gcc
#
# Everything is installed under /opt/cell/sysroot and is consumed through
# --with-sysroot by the final ppu-gcc / ppu-binutils.

# Target-architecture ELF objects: host strip/debuginfo/brp scripts must not touch them
%global debug_package %{nil}
%global _debugsource_packages 0
%global __os_install_post %{nil}
%global __arch_install_post %{nil}
%global _build_id_links none
%global _missing_build_ids_terminate_build 0
%undefine _auto_set_build_flags
%undefine _lto_cflags

%global toolchain   /opt/cell/toolchain
%global sysroot     /opt/cell/sysroot
%global xtarget     powerpc64-linux-gnu
%global glibc_ver   2.40
%global kernel_ver  6.18.52

Name:           ppu-sysroot
Version:        %{glibc_ver}
Release:        1%{?dist}
Summary:        Linux %{kernel_ver} headers and glibc %{glibc_ver} sysroot for the Cell/B.E. PPU
License:        GPLv2+ and LGPLv2+ and others
Group:          Cell Development Tools
URL:            https://www.gnu.org/software/libc/
Source0:        https://ftp.gnu.org/gnu/glibc/glibc-%{glibc_ver}.tar.xz
Source1:        https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-%{kernel_ver}.tar.xz
ExclusiveArch:  x86_64

BuildRequires:  gcc-powerpc64-linux-gnu
BuildRequires:  ppu-binutils
BuildRequires:  gcc, make, gawk, sed, bison, gettext, texinfo
BuildRequires:  python3, perl-interpreter, rsync, flex, bc
AutoReqProv:    no

%description
Target sysroot for the Cell Broadband Engine PPU (big-endian ppc64):
Linux %{kernel_ver} user-space headers and glibc %{glibc_ver}, installed under
%{sysroot}.  Built with Fedora's powerpc64-linux-gnu cross compiler and the
ppu-binutils assembler/linker.


%prep
%setup -q -n glibc-%{glibc_ver} -a 1


%build
KHDR=$PWD/kheaders
rm -rf "$KHDR"
make -C linux-%{kernel_ver} ARCH=powerpc HOSTCC=gcc \
    INSTALL_HDR_PATH="$KHDR/usr" headers_install
find "$KHDR/usr/include" -name '.*' -delete

# ---- Binutils shim: make the Fedora cross gcc use ppu-binutils -------------
# gcc finds as/ld through -B first; configure/make find ar, nm, ranlib, ...
# through <triplet>-<tool> names on PATH.  Both resolve to this directory.
SHIM=$PWD/ppu-tools
rm -rf "$SHIM"
mkdir -p "$SHIM"
for t in addr2line ar as c++filt elfedit gprof ld ld.bfd nm objcopy objdump \
         ranlib readelf size strings strip; do
    if [ -x %{toolchain}/bin/ppu-$t ]; then
        ln -s %{toolchain}/bin/ppu-$t "$SHIM/%{xtarget}-$t"
    fi
done
ln -s %{toolchain}/bin/ppu-as "$SHIM/as"
ln -s %{toolchain}/bin/ppu-ld "$SHIM/ld"
export PATH="$SHIM:$PATH"

# ---- libatomic_asneeded stub ------------------------------------------------
# The Fedora cross gcc driver adds -latomic_asneeded to shared links, but the
# cross package does not ship that library, so every `gcc -shared` fails with
# "cannot find -latomic_asneeded".  glibc does not use libatomic, so an empty
# archive is enough to satisfy the driver.
STUB=$PWD/ppu-stub
rm -rf "$STUB"
mkdir -p "$STUB"
%{toolchain}/bin/ppu-ar crs "$STUB/libatomic_asneeded.a"

# Log which tools are actually in use
echo "=== stage 1 tools ==="
%{xtarget}-gcc -B"$SHIM/" -print-prog-name=as
%{xtarget}-gcc -B"$SHIM/" -print-prog-name=ld
"$SHIM/ld" --version | head -n1
"$SHIM/as" --version | head -n1

# ---- glibc, cross-built ------------------------------------------------------
# -mcpu=cell is explicit so a distro default (e.g. POWER7/VSX) can never leak
# into code that has to run on the PPU.
CELL_FLAGS="-O2 -pipe -mcpu=cell -mtune=cell"

rm -rf build-ppu
mkdir build-ppu
pushd build-ppu

BUILD_CC=gcc \
CC="%{xtarget}-gcc -m64 -B$SHIM/ -L$STUB" \
CFLAGS="$CELL_FLAGS" \
libc_cv_slibdir=/lib64 \
libc_cv_rtlddir=/lib64 \
../configure \
    --build=%{_build} \
    --host=%{xtarget} \
    --prefix=/usr \
    --libdir=/usr/lib64 \
    --with-headers="$KHDR/usr/include" \
    --enable-kernel=%{kernel_ver} \
    --enable-shared \
    --disable-werror \
    --disable-profile \
    --disable-systemtap \
    --disable-nscd \
    --without-gd \
    --without-selinux
make %{?_smp_mflags}
popd


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{sysroot}

# Same tool environment as %%build (rpm runs each section in a fresh shell)
SHIM=$PWD/ppu-tools
export PATH="$SHIM:$PATH"

# Kernel headers
cp -a kheaders/usr %{buildroot}%{sysroot}/

# glibc (cross: no ldconfig/localedef is run on the target)
make -C build-ppu install_root=%{buildroot}%{sysroot} install

# Sysroot is not meant to carry docs/gettext data
rm -rf %{buildroot}%{sysroot}/usr/share/info
rm -rf %{buildroot}%{sysroot}/usr/share/man
rm -rf %{buildroot}%{sysroot}/usr/share/locale


%check


%files
%dir /opt/cell
%{sysroot}


%changelog
* Sat Oct 17 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.40-1
- Initial build

