%undefine optflags
%undefine build_ldflags
%global _build_id_links none

%define package_prefix ppu

Summary:        GNU binary utilities for the Cell/B.E. PPU
Name:           %{package_prefix}-binutils
Version:        2.32
Release:        2.CELL
License:        GPL
Group:          Cell Development Tools
Source0:        https://ftp.gnu.org/gnu/binutils/binutils-%{version}.tar.xz
ExclusiveArch:  ppc64 x86_64

BuildRequires:  dejagnu, bison, flex, texinfo
BuildRequires:  gcc, cpp, gcc-c++

%description
The GNU binutils version %{version} for the Cell/B.E. PPU (powerpc64) core.

# Don't strip as the host binutils may be unable to handle SPU objects.
%global __os_install_post /usr/lib/rpm/brp-compress

# When building the cross-toolchain, reset prefix directory and use sysroot
%ifarch x86_64
%global _prefix /opt/cell/toolchain
%global _libdir %{_prefix}/lib64
%global _mandir %{_prefix}/man
%global _infodir %{_prefix}/info
%global with_sysroot --with-sysroot=/opt/cell/sysroot
%endif

%prep
%setup -c -q


%build
%ifarch ppc64
%define configuration --enable-install-libbfd --target=powerpc64-linux-gnu --enable-targets=spu
%define target_platform powerpc64-linux-gnu
%define mcpu_mtune -mcpu=cell -mtune=cell
%else
%define configuration --disable-install-libbfd --target=powerpc64-linux-gnu --enable-targets=spu
%define target_platform powerpc64-linux-gnu
%define mcpu_mtune -mcpu=x86_64 -mtune=generic
%endif
rm -rf build
mkdir -p build
pushd build
CC="gcc -m64 -O2 -g" \
CXX="g++ -m64 -O2 -g" \
CFLAGS="%{mcpu_mtune} -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64" \
CXXFLAGS="%{mcpu_mtune} -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64" \
LDFLAGS= \
../binutils-%{version}/configure --prefix=%{_prefix} --libdir=%{_libdir} --mandir=%{_mandir}  \
    --infodir=%{_infodir} %{?with_sysroot} %{configuration} --program-prefix=%{package_prefix}- \
    --disable-shared --disable-nls --disable-werror --enable-64-bit-bfd
make -j1
popd


%check


%install
rm -rf %{buildroot}
pushd build
make DESTDIR=%{buildroot} -j1 install
popd
rm -f %{buildroot}%{_mandir}/man1/%{package_prefix}-{dlltool,windres,windmc}*
rm -rf %{buildroot}%{_infodir}
%ifarch ppc64
rm %{buildroot}%{_prefix}/lib64/lib{bfd,opcodes}.la
mv %{buildroot}%{_prefix}/lib64/lib{bfd,opcodes}.a %{buildroot}%{_prefix}/%{target_platform}/lib
mv %{buildroot}%{_prefix}/include %{buildroot}%{_prefix}/%{target_platform}
%endif


%files
%defattr(-,root,root)
%ifarch x86_64
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_mandir}
%dir %{_mandir}/man1
%endif
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
%{_mandir}/man1/%{package_prefix}-elfedit.1*
%ifarch ppc64
%dir %{_prefix}/%{target_platform}/include
%{_prefix}/%{target_platform}/include/ansidecl.h
%{_prefix}/%{target_platform}/include/bfd.h
%{_prefix}/%{target_platform}/include/bfd_stdint.h
%{_prefix}/%{target_platform}/include/bfdlink.h
%{_prefix}/%{target_platform}/include/diagnostics.h
%{_prefix}/%{target_platform}/include/dis-asm.h
%{_prefix}/%{target_platform}/include/plugin-api.h
%{_prefix}/%{target_platform}/include/symcat.h
%{_prefix}/%{target_platform}/lib/libbfd.a
%{_prefix}/%{target_platform}/lib/libopcodes.a
%endif


%changelog
* Thu Nov 5 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.32-2
- Initial build - https://ps3linux.net

