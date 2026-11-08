%undefine optflags
%undefine build_cflags
%undefine build_cxxflags
%undefine build_ldflags
%undefine _hardened_build
%undefine _annotated_build
%undefine _auto_set_build_flags

%define _build_id_links none

Summary:        GNU binary utilities for the Cell/B.E. PPU
Name:           ppu-binutils
Version:        2.32
Release:        1.CELL
License:        GPL
Group:          Cell Development Tools
Source0:        https://ftp.gnu.org/gnu/binutils/binutils-%{version}.tar.xz
ExclusiveArch:  ppc64 x86_64

BuildRequires:  dejagnu, bison, flex, texinfo
BuildRequires:  gcc, cpp, gcc-c++

%description
The GNU binutils version %{version} for the Cell Broadband Engine PPU.

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
%define configuration --enable-install-libbfd --target=powerpc64-linux --enable-targets=spu
%define mcpu_mtune -mcpu=cell -mtune=cell
%endif
%ifarch x86_64
%define configuration --disable-install-libbfd --target=powerpc64-linux --enable-targets=spu
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
    --infodir=%{_infodir} %{?with_sysroot} %{configuration} --program-prefix=ppu- \
    --disable-shared --disable-nls --disable-werror --enable-64-bit-bfd
make -j1
popd


%check


%install
rm -rf %{buildroot}
pushd build
make DESTDIR=%{buildroot} -j1 install
popd

rm -f %{buildroot}%{_mandir}/man1/ppu-{dlltool,windres,windmc}*
rm -rf %{buildroot}%{_infodir}
%ifarch ppc64
rm %{buildroot}%{_prefix}/lib64/lib{bfd,opcodes}.la
mv %{buildroot}%{_prefix}/lib64/lib{bfd,opcodes}.a %{buildroot}%{_prefix}/powerpc64-linux/lib
mv %{buildroot}%{_prefix}/include %{buildroot}%{_prefix}/powerpc64-linux
%endif


%files
%defattr(-,root,root)
%ifarch x86_64
%dir %{_prefix}
%dir %{_prefix}/bin
%endif
%{_prefix}/bin/ppu-addr2line
%{_prefix}/bin/ppu-ar
%{_prefix}/bin/ppu-as
%{_prefix}/bin/ppu-c++filt
%{_prefix}/bin/ppu-embedspu
%{_prefix}/bin/ppu-gprof
%{_prefix}/bin/ppu-ld
%{_prefix}/bin/ppu-nm
%{_prefix}/bin/ppu-objcopy
%{_prefix}/bin/ppu-objdump
%{_prefix}/bin/ppu-ranlib
%{_prefix}/bin/ppu-readelf
%{_prefix}/bin/ppu-size
%{_prefix}/bin/ppu-strings
%{_prefix}/bin/ppu-strip
%{_prefix}/bin/ppu-elfedit
%{_prefix}/bin/ppu-ld.bfd
%ifarch x86_64
%dir %{_prefix}/man
%dir %{_prefix}/man/man1
%{_prefix}/man/man1/ppu-addr2line.1
%{_prefix}/man/man1/ppu-ar.1
%{_prefix}/man/man1/ppu-as.1
%{_prefix}/man/man1/ppu-c++filt.1
%{_prefix}/man/man1/ppu-gprof.1
%{_prefix}/man/man1/ppu-ld.1
%{_prefix}/man/man1/ppu-nm.1
%{_prefix}/man/man1/ppu-objcopy.1
%{_prefix}/man/man1/ppu-objdump.1
%{_prefix}/man/man1/ppu-ranlib.1
%{_prefix}/man/man1/ppu-readelf.1
%{_prefix}/man/man1/ppu-size.1
%{_prefix}/man/man1/ppu-strings.1
%{_prefix}/man/man1/ppu-strip.1
%{_prefix}/man/man1/ppu-elfedit.1
%endif
%dir %{_prefix}/powerpc64-linux
%dir %{_prefix}/powerpc64-linux/bin
%{_prefix}/powerpc64-linux/bin/ar
%{_prefix}/powerpc64-linux/bin/as
%{_prefix}/powerpc64-linux/bin/ld
%{_prefix}/powerpc64-linux/bin/nm
%{_prefix}/powerpc64-linux/bin/objcopy
%{_prefix}/powerpc64-linux/bin/objdump
%{_prefix}/powerpc64-linux/bin/ranlib
%{_prefix}/powerpc64-linux/bin/strip
%{_prefix}/powerpc64-linux/bin/ld.bfd
%{_prefix}/powerpc64-linux/bin/readelf
%dir %{_prefix}/powerpc64-linux/lib
%dir %{_prefix}/powerpc64-linux/lib/ldscripts
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32_spu.x
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32_spu.xbn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32_spu.xc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32_spu.xn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32_spu.xr
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32_spu.xu
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32_spu.xw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.x
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xbn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xd
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xdc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xdw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xr
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xs
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xsc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xsw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xu
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.x
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xbn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xd
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xdc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xdw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xr
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xs
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xsc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xsw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xu
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.x
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xbn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xd
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xdc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xdw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xr
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xs
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xsc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xsw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xu
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.x
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xbn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xd
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xdc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xdw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xr
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xs
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xsc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xsw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xu
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32_spu.xce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32_spu.xe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32_spu.xwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.x
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xbn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xd
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xdc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xdce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xde
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xdw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xdwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xr
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xs
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xsc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xsce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xse
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xsw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xswe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xu
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppc.xwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.x
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xbn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xd
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xdc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xdce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xde
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xdw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xdwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xr
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xs
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xsc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xsce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xse
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xsw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xswe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xu
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppclinux.xwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.x
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xbn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xd
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xdc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xdce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xde
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xdw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xdwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xr
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xs
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xsc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xsce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xse
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xsw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xswe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xu
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32lppcsim.xwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xdce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xde
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xdwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xsce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xse
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xswe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppc.xwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xdce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xde
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xdwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xsce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xse
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xswe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppclinux.xwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xdce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xde
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xdwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xsce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xse
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xswe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf32ppcsim.xwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.x
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xbn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xd
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xdc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xdce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xde
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xdw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xdwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xn
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xr
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xs
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xsc
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xsce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xse
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xsw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xswe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xu
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xw
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64lppc.xwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xdce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xde
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xdwe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xsce
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xse
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xswe
%{_prefix}/powerpc64-linux/lib/ldscripts/elf64ppc.xwe
%ifarch ppc64
%{_prefix}/powerpc64-linux/include/ansidecl.h
%{_prefix}/powerpc64-linux/include/bfd.h
%{_prefix}/powerpc64-linux/include/bfd_stdint.h
%{_prefix}/powerpc64-linux/include/bfdlink.h
%{_prefix}/powerpc64-linux/include/diagnostics.h
%{_prefix}/powerpc64-linux/include/dis-asm.h
%{_prefix}/powerpc64-linux/include/plugin-api.h
%{_prefix}/powerpc64-linux/include/symcat.h
%{_prefix}/powerpc64-linux/lib/libbfd.a
%{_prefix}/powerpc64-linux/lib/libopcodes.a
%{_prefix}/share/man/man1/ppu-addr2line.1.gz
%{_prefix}/share/man/man1/ppu-ar.1.gz
%{_prefix}/share/man/man1/ppu-as.1.gz
%{_prefix}/share/man/man1/ppu-c++filt.1.gz
%{_prefix}/share/man/man1/ppu-elfedit.1.gz
%{_prefix}/share/man/man1/ppu-gprof.1.gz
%{_prefix}/share/man/man1/ppu-ld.1.gz
%{_prefix}/share/man/man1/ppu-nm.1.gz
%{_prefix}/share/man/man1/ppu-objcopy.1.gz
%{_prefix}/share/man/man1/ppu-objdump.1.gz
%{_prefix}/share/man/man1/ppu-ranlib.1.gz
%{_prefix}/share/man/man1/ppu-readelf.1.gz
%{_prefix}/share/man/man1/ppu-size.1.gz
%{_prefix}/share/man/man1/ppu-strings.1.gz
%{_prefix}/share/man/man1/ppu-strip.1.gz
%endif


%changelog
* Sun Nov 8 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.32-1
- Initial build

