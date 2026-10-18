%define package_prefix ppu
# Don't strip as the host binutils may be unable to handle SPU objects.
%define __os_install_post /usr/lib/rpm/brp-compress

%bcond_with ppc64

Summary: GNU binary utilities for the Cell/B.E. PPU
Name: %{package_prefix}-binutils
Version: 2.33.1
Release: 1.CELL
License: GPL
Group: Cell Development Tools
Source0: https://ftp.gnu.org/gnu/binutils/binutils-%{version}.tar.xz
ExclusiveArch: ppc64 x86_64

BuildRequires: dejagnu, bison, flex, texinfo, bc
BuildRequires: gcc, cpp, binutils, gcc-c++, make

%description
The GNU binutils version %{version}.

# When building the cross-toolchain, reset prefix directory and use sysroot
%define _prefix /opt/cell/toolchain
%define _mandir %{_prefix}/man
%define _infodir %{_prefix}/info
%define with_sysroot --with-sysroot=/opt/cell/sysroot


%prep
%setup -c -q


%build
%define configuration --disable-install-libbfd --target=powerpc64-linux --enable-targets=spu
%define target_platform powerpc64-linux

OPT_FLAGS="-O2 -g -march=x86_64 -mtune=generic -m64"
TARGET_OPT_FLAGS="$OPT_FLAGS -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64"
CC="gcc"

rm -fr obj-%{target_platform}
mkdir obj-%{target_platform}

pushd obj-%{target_platform}
unset CC CXX CFLAGS CXXFLAGS FCFLAGS FFLAGS LDFLAGS
unset CFLAGS_FOR_TARGET CXXFLAGS_FOR_TARGET FCFLAGS_FOR_TARGET FFLAGS_FOR_TARGET
AR=/usr/bin/ar \
AS=/usr/bin/as \
LD=/usr/bin/ld \
NM=/usr/bin/nm \
RANLIB=/usr/bin/ranlib \
CFLAGS_FOR_TARGET="-O2 -g -march=x86_64 -mtune=generic -m64 -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64" \
CXXFLAGS_FOR_TARGET="-O2 -g -march=x86_64 -mtune=generic -m64 -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64" \
../binutils-%{version}/configure \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir}  \
    --infodir=%{_infodir} \
	--build=`gcc -dumpmachine` \
    --host=`gcc -dumpmachine` \
    %{with_sysroot} \
    %{configuration} \
    --program-prefix=%{package_prefix}- \
	--disable-shared \
    --disable-nls \
    --disable-werror \
    --enable-64-bit-bfd
make %{?_smp_mflags} -j1
popd


%check


%install
rm -fr %{buildroot}
pushd obj-%{target_platform}
TARGET_PLATFORM=%{target_platform}
make DESTDIR=%{buildroot} -j1 install
popd
rm -f %{buildroot}%{_mandir}/man1/%{package_prefix}-{dlltool,nlmconv,windres,windmc}*
rm -rf %{buildroot}%{_infodir}
rm -rf %{buildroot}%{_mandir}/man7
cd ../


%files
%defattr(-,root,root)
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_mandir}
%dir %{_mandir}/man1
%{_prefix}/bin/%{package_prefix}-addr2line
%{_prefix}/bin/%{package_prefix}-ar
%{_prefix}/bin/%{package_prefix}-as
%{_prefix}/bin/%{package_prefix}-c++filt
%{_prefix}/bin/%{package_prefix}-ld
%{_prefix}/bin/%{package_prefix}-nm
%{_prefix}/bin/%{package_prefix}-objcopy
%{_prefix}/bin/%{package_prefix}-objdump
%{_prefix}/bin/%{package_prefix}-ranlib
%{_prefix}/bin/%{package_prefix}-readelf
%{_prefix}/bin/%{package_prefix}-size
%{_prefix}/bin/%{package_prefix}-strings
%{_prefix}/bin/%{package_prefix}-strip
%{_prefix}/bin/%{package_prefix}-gprof
%{_prefix}/bin/%{package_prefix}-embedspu
%{_prefix}/bin/ppu-elfedit
%{_prefix}/bin/ppu-ld.bfd
%dir %{_prefix}/%{target_platform}
%dir %{_prefix}/%{target_platform}/bin
%dir %{_prefix}/%{target_platform}/lib
%{_prefix}/%{target_platform}/bin/*
%{_prefix}/%{target_platform}/lib/ldscripts
%{_mandir}/man1/%{package_prefix}-addr2line.1*
%{_mandir}/man1/%{package_prefix}-ar.1*
%{_mandir}/man1/%{package_prefix}-as.1*
%{_mandir}/man1/%{package_prefix}-c++filt.1*
%{_mandir}/man1/%{package_prefix}-ld.1*
%{_mandir}/man1/%{package_prefix}-nm.1*
%{_mandir}/man1/%{package_prefix}-objcopy.1*
%{_mandir}/man1/%{package_prefix}-objdump.1*
%{_mandir}/man1/%{package_prefix}-ranlib.1*
%{_mandir}/man1/%{package_prefix}-readelf.1*
%{_mandir}/man1/%{package_prefix}-size.1*
%{_mandir}/man1/%{package_prefix}-strings.1*
%{_mandir}/man1/%{package_prefix}-strip.1*
%{_mandir}/man1/%{package_prefix}-gprof.1*
%{_prefix}/man/man1/ppu-elfedit.1*


%changelog
* Sat Oct 17 2026  The Model Citizen  <model.citizen.ps3@gmail.com>  2.33.1-1
- Initial build  - https://ps3linux.net

