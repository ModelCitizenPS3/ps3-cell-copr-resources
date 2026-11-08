%undefine optflags
%undefine build_cflags
%undefine build_cxxflags
%undefine build_ldflags
%undefine _hardened_build
%undefine _annotated_build
%undefine _auto_set_build_flags

%define _build_id_links none

Summary:        GNU binary utilities for the Cell/B.E. SPU
Name:           spu-binutils
Version:        2.32
Release:        1.CELL
License:        GPL
Group:          Cell Development Tools
Source0:        https://ftp.gnu.org/gnu/binutils/binutils-%{version}.tar.xz
ExclusiveArch:  ppc64 x86_64

BuildRequires:  dejagnu, bison, flex, texinfo
BuildRequires:  gcc, cpp, gcc-c++

%description
The GNU binutils version %{version} for the Cell/B.E. SPU cores.

# Don't strip as the host binutils may be unable to handle SPU objects.
%define __os_install_post /usr/lib/rpm/brp-compress

# When building the cross-toolchain, reset prefix directory and use sysroot
%ifarch x86_64
%define _prefix /opt/cell/toolchain
%define _libdir %{_prefix}/lib
%define _mandir %{_prefix}/man
%define _infodir %{_prefix}/info
%define with_sysroot --with-sysroot=/opt/cell/sysroot
%endif
%ifarch ppc64
%define _libdir %{_prefix}/lib
%endif


%prep
%setup -c -q


%build
%ifarch ppc64
%define mcpu_mtune -mcpu=cell -mtune=cell
%else
%define mcpu_mtune -mcpu=x86_64 -mtune=generic
%endif
%define configuration --target=spu
rm -rf build
mkdir -p build
pushd build
CC="gcc -m64 -O2 -g" \
CXX="g++ -m64 -O2 -g" \
CFLAGS="%{mcpu_mtune} -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64" \
CXXFLAGS="%{mcpu_mtune} -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64" \
LDFLAGS= \
../binutils-%{version}/configure --prefix=%{_prefix} --libdir=%{_libdir} --mandir=%{_mandir}  \
    --infodir=%{_infodir} %{?with_sysroot} %{configuration} --program-prefix=spu- \
    --disable-shared --disable-nls --disable-werror --enable-64-bit-bfd
make -j1
popd


%check


%install
rm -fr %{buildroot}
pushd build
make DESTDIR=%{buildroot} -j1 install
popd
rm -f %{buildroot}%{_mandir}/man1/spu-{dlltool,windres,windmc}*
rm -rf %{buildroot}%{_infodir}


%files
%defattr(-,root,root)
%dir %{_prefix}
%ifarch x86_64
%dir %{_prefix}/bin
%endif
%{_prefix}/bin/spu-addr2line
%{_prefix}/bin/spu-ar
%{_prefix}/bin/spu-as
%{_prefix}/bin/spu-c++filt
%{_prefix}/bin/spu-gprof
%{_prefix}/bin/spu-ld
%{_prefix}/bin/spu-nm
%{_prefix}/bin/spu-objcopy
%{_prefix}/bin/spu-objdump
%{_prefix}/bin/spu-ranlib
%{_prefix}/bin/spu-readelf
%{_prefix}/bin/spu-size
%{_prefix}/bin/spu-strings
%{_prefix}/bin/spu-strip
%{_prefix}/bin/spu-elfedit
%{_prefix}/bin/spu-ld.bfd
%ifarch x86_64
%dir %{_prefix}/man
%dir %{_prefix}/man/man1
%{_prefix}/man/man1/spu-addr2line.1
%{_prefix}/man/man1/spu-ar.1
%{_prefix}/man/man1/spu-as.1
%{_prefix}/man/man1/spu-c++filt.1
%{_prefix}/man/man1/spu-gprof.1
%{_prefix}/man/man1/spu-ld.1
%{_prefix}/man/man1/spu-nm.1
%{_prefix}/man/man1/spu-objcopy.1
%{_prefix}/man/man1/spu-objdump.1
%{_prefix}/man/man1/spu-ranlib.1
%{_prefix}/man/man1/spu-readelf.1
%{_prefix}/man/man1/spu-size.1
%{_prefix}/man/man1/spu-strings.1
%{_prefix}/man/man1/spu-strip.1
%{_prefix}/man/man1/spu-elfedit.1
%endif
%ifarch ppc64
%{_prefix}/share/man/man1/spu-addr2line.1.gz
%{_prefix}/share/man/man1/spu-ar.1.gz
%{_prefix}/share/man/man1/spu-as.1.gz
%{_prefix}/share/man/man1/spu-c++filt.1.gz
%{_prefix}/share/man/man1/spu-elfedit.1.gz
%{_prefix}/share/man/man1/spu-gprof.1.gz
%{_prefix}/share/man/man1/spu-ld.1.gz
%{_prefix}/share/man/man1/spu-nm.1.gz
%{_prefix}/share/man/man1/spu-objcopy.1.gz
%{_prefix}/share/man/man1/spu-objdump.1.gz
%{_prefix}/share/man/man1/spu-ranlib.1.gz
%{_prefix}/share/man/man1/spu-readelf.1.gz
%{_prefix}/share/man/man1/spu-size.1.gz
%{_prefix}/share/man/man1/spu-strings.1.gz
%{_prefix}/share/man/man1/spu-strip.1.gz
%endif
%dir %{_prefix}/spu
%dir %{_prefix}/spu/bin
%{_prefix}/spu/bin/ar
%{_prefix}/spu/bin/as
%{_prefix}/spu/bin/ld
%{_prefix}/spu/bin/nm
%{_prefix}/spu/bin/objcopy
%{_prefix}/spu/bin/objdump
%{_prefix}/spu/bin/ranlib
%{_prefix}/spu/bin/strip
%{_prefix}/spu/bin/ld.bfd
%{_prefix}/spu/bin/readelf
%dir %{_prefix}/spu/lib
%dir %{_prefix}/spu/lib/ldscripts
%{_prefix}/spu/lib/ldscripts/elf32_spu.x
%{_prefix}/spu/lib/ldscripts/elf32_spu.xbn
%{_prefix}/spu/lib/ldscripts/elf32_spu.xc
%{_prefix}/spu/lib/ldscripts/elf32_spu.xn
%{_prefix}/spu/lib/ldscripts/elf32_spu.xr
%{_prefix}/spu/lib/ldscripts/elf32_spu.xu
%{_prefix}/spu/lib/ldscripts/elf32_spu.xw
%{_prefix}/spu/lib/ldscripts/elf32_spu.xce
%{_prefix}/spu/lib/ldscripts/elf32_spu.xe
%{_prefix}/spu/lib/ldscripts/elf32_spu.xwe


%changelog
* Sun Nov 8 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.32-1
- Initial build

