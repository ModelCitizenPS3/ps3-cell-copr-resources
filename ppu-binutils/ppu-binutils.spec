# Don't strip as the host binutils may be unable to handle SPU objects.
%define __os_install_post /usr/lib/rpm/brp-compress
# When building the cross-toolchain, reset prefix directory and use sysroot
%define _build_id_links none

%define _prefix /opt/cell/toolchain
%define target powerpc64-linux-gnu

Name:           ppu-binutils
Version:        2.36.1
Release:        1%{?dist}
Summary:        GNU binary utilities for the Cell/B.E. PPU
License:        GPL
Group:          Cell Development Tools
Source0:        https://ftp.gnu.org/gnu/binutils/binutils-%{version}.tar.xz

BuildRequires:  dejagnu, bison, flex, texinfo, gcc, gcc-c++

%description
The GNU binutils version %{version}.


%prep
%setup -q -n binutils-%{version}


%build
mkdir -p build
pushd build

OPT_FLAGS="-O2 -g -march=x86-64 -mtune=generic"
TARGET_OPT_FLAGS="$OPT_FLAGS -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64"
CC="gcc -m64"
CXX="g++ -m64"
CC="$CC" CXX="$CXX" \
CFLAGS="$TARGET_OPT_FLAGS" CXXFLAGS="$TARGET_OPT_FLAGS" \
XCFLAGS="$OPT_FLAGS" TCFLAGS="$TARGET_OPT_FLAGS" LDFLAGS= \
../configure \
    --build=%{_build} \
    --host=%{_host} \
    --target=%{target} \
    --with-sysroot=/opt/cell/sysroot \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --disable-install-libbfd \
    --enable-targets=spu \
    --program-prefix=ppu- \
    --disable-shared \
    --enable-64-bit-bfd \
    --disable-nls \
    --disable-werror
popd
make -C build %{?_smp_mflags}


%check


%install
rm -rf %{buildroot}
make -C build DESTDIR=%{buildroot} -j1 install

find %{buildroot}%{_libdir} -name *.la -delete
rm -f %{buildroot}%{_mandir}/man1/ppu-{dlltool,nlmconv,windres,windmc}*
rm -rf %{buildroot}%{_infodir}
rm -f %{buildroot}%{_infodir}/dir


%files
%defattr(-,root,root)
%{_bindir}/ppu-addr2line
%{_bindir}/ppu-ar
%{_bindir}/ppu-as
%{_bindir}/ppu-c++filt
%{_bindir}/ppu-ld
%{_bindir}/ppu-nm
%{_bindir}/ppu-objcopy
%{_bindir}/ppu-objdump
%{_bindir}/ppu-ranlib
%{_bindir}/ppu-readelf
%{_bindir}/ppu-size
%{_bindir}/ppu-strings
%{_bindir}/ppu-strip
%{_bindir}/ppu-gprof
%{_bindir}/ppu-elfedit
%{_bindir}/ppu-ld.bfd
%{_bindir}/ppu-embedspu
%dir %{_prefix}/%{target}
%dir %{_prefix}/%{target}/bin
%dir %{_prefix}/%{target}/lib
%{_prefix}/%{target}/bin/*
%{_prefix}/%{target}/lib/ldscripts
%{_mandir}/man1/ppu-addr2line.1*
%{_mandir}/man1/ppu-ar.1*
%{_mandir}/man1/ppu-as.1*
%{_mandir}/man1/ppu-c++filt.1*
%{_mandir}/man1/ppu-ld.1*
%{_mandir}/man1/ppu-nm.1*
%{_mandir}/man1/ppu-objcopy.1*
%{_mandir}/man1/ppu-objdump.1*
%{_mandir}/man1/ppu-ranlib.1*
%{_mandir}/man1/ppu-readelf.1*
%{_mandir}/man1/ppu-size.1*
%{_mandir}/man1/ppu-strings.1*
%{_mandir}/man1/ppu-strip.1*
%{_mandir}/man1/ppu-gprof.1*
%{_mandir}/man1/ppu-elfedit.1*
%dir %{_libdir}/bfd-plugins
%{_libdir}/bfd-plugins/libdep.a


%changelog
* Fri Oct 16 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.36.1-1
- Initial build for PS3LINUX on the Cell/B.E. https://ps3linux.net

