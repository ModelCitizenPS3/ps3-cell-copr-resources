# Don't strip as the host binutils may be unable to handle SPU objects.
%define __os_install_post /usr/lib/rpm/brp-compress
# When building the cross-toolchain, reset prefix directory and use sysroot
%define _build_id_links none

%bcond_with ppu
%bcond_with spu

%if %{with ppu} && %{with spu}
%{error: Cannot specify both --with ppu and --with spu}
%endif
%if !%{with ppu} && !%{with spu}
%{error: Must specify either --with ppu or --with spu}
%endif

#%%ifarch ppc64
#%%if %%{with ppu}
#%%define package_prefix ppu
#%%define target powerpc64-linux-gnu
#%%define configuration --enable-install-libbfd --target=%%{target} --enable-targets=spu
#%%endif
#%%if %%{with spu}
#%%define package_prefix spu
#%%define target spu-elf
#%%define _libdir %%{_prefix}/lib
#%%define configuration --target=%%{target}
#%%endif
#%%endif

#%%ifarch x86_64
%define _prefix /opt/cell/toolchain
%define _mandir %{_prefix}/man
%define _infodir %{_prefix}/info
%define with_sysroot --with-sysroot=/opt/cell/sysroot
%if %{with ppu}
%define package_prefix ppu
%define target powerpc64-linux-gnu
%define configuration --disable-install-libbfd --target=%{target} --enable-targets=spu
%endif
%if %{with spu}
%define package_prefix spu
%define target spu-elf
%define _libdir %{_prefix}/lib
%define configuration --target=%{target}
%endif
#%%endif

Name:           %{package_prefix}-binutils
Version:        2.36.1
Release:        1%{?dist}
%if %{with ppu}
Summary:        GNU binary utilities for the Cell/B.E. PPU
%endif
%if %{with spu}
Summary:        GNU binary utilities for the Cell/B.E. SPU
%endif
License:        GPL
Group:          Cell Development Tools
Source0:        https://ftp.gnu.org/gnu/binutils/binutils-%{version}.tar.xz
#ExclusiveArch:  ppc64 x86_64

BuildRequires:  dejagnu, bison, flex, texinfo, gcc

%description
The GNU binutils version %{version}.


%prep
%setup -q -n binutils-%{version}


%build
rm -rf obj-%{target}
mkdir -p obj-%{target}
pushd obj-%{target}

i#%%ifarch ppc64
#OPT_FLAGS="-O2 -g -mcpu=cell -mtune=cell"
#TARGET_OPT_FLAGS="$OPT_FLAGS -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64"
#%%endif
#%%ifarch x86_64
OPT_FLAGS="-O2 -g -march=x86-64 -mtune=generic"
TARGET_OPT_FLAGS="$OPT_FLAGS -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64"
#%%endif
CC="gcc -m64"
CXX="g++ -m64"
CC="$CC" CXX="$CXX" \
CFLAGS="$TARGET_OPT_FLAGS" CXXFLAGS="$TARGET_OPT_FLAGS" \
XCFLAGS="$OPT_FLAGS" TCFLAGS="$TARGET_OPT_FLAGS" LDFLAGS= \
../configure \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir} \
    --infodir=%{_infodir} \
	%{?with_sysroot} \
    %{configuration} \
    --program-prefix=%{package_prefix}- \
    --disable-shared \
    --enable-64-bit-bfd \
    --disable-nls \
    --disable-werror
popd
make -C obj-%{target} %{?_smp_mflags}


%check


%install
rm -rf %{buildroot}
make -C obj-%{target} DESTDIR=%{buildroot} -j1 install

find %{buildroot}%{_libdir} -name *.la -delete
rm -f %{buildroot}%{_mandir}/man1/%{package_prefix}-{dlltool,nlmconv,windres,windmc}*
rm -rf %{buildroot}%{_infodir}
rm -f %{buildroot}%{_infodir}/dir


%files
%defattr(-,root,root)
%{_bindir}/%{package_prefix}-addr2line
%{_bindir}/%{package_prefix}-ar
%{_bindir}/%{package_prefix}-as
%{_bindir}/%{package_prefix}-c++filt
%{_bindir}/%{package_prefix}-ld
%{_bindir}/%{package_prefix}-nm
%{_bindir}/%{package_prefix}-objcopy
%{_bindir}/%{package_prefix}-objdump
%{_bindir}/%{package_prefix}-ranlib
%{_bindir}/%{package_prefix}-readelf
%{_bindir}/%{package_prefix}-size
%{_bindir}/%{package_prefix}-strings
%{_bindir}/%{package_prefix}-strip
%{_bindir}/%{package_prefix}-gprof
%{_bindir}/%{package_prefix}-elfedit
%{_bindir}/%{package_prefix}-ld.bfd
%if %{with ppu}
%{_bindir}/%{package_prefix}-embedspu
%endif
%dir %{_prefix}/%{target}
%dir %{_prefix}/%{target}/bin
%dir %{_prefix}/%{target}/lib
%{_prefix}/%{target}/bin/*
%{_prefix}/%{target}/lib/ldscripts
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
%dir %{_libdir}/bfd-plugins
%{_libdir}/bfd-plugins/libdep.a
#%%ifarch ppc64
#%%if %%{with ppu}
#%%{_prefix}/include/ansidecl.h
#%%{_prefix}/include/bfd.h
#%%{_prefix}/include/bfd_stdint.h
#%%{_prefix}/include/bfdlink.h
#%%{_prefix}/include/ctf-api.h
#%%{_prefix}/include/ctf.h
#%%{_prefix}/include/diagnostics.h
#%%{_prefix}/include/dis-asm.h
#%%{_prefix}/include/plugin-api.h
#%%{_prefix}/include/symcat.h
#%%{_libdir}/libbfd.a
#%%{_libdir}/libctf-nobfd.a
#%%{_libdir}/libctf.a
#%%{_libdir}/libopcodes.a
#%%endif
#%%endif


%changelog
* Fri Oct 16 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.36.1-1
- Initial build for PS3LINUX on the Cell/B.E. https://ps3linux.net

