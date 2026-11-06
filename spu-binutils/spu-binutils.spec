%undefine optflags
%undefine build_ldflags
%global _build_id_links none

%define package_prefix spu

Summary:        GNU binary utilities for the Cell/B.E. SPU
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


%prep
%setup -c -q


%build
%ifarch ppc64
%define mcpu_mtune -mcpu=cell -mtune=cell
%else
%define mcpu_mtune -mcpu=x86_64 -mtune=generic
%endif
%define configuration --target=spu
%define target_platform spu
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
rm -fr %{buildroot}
pushd build
make DESTDIR=%{buildroot} -j1 install
popd
rm -f %{buildroot}%{_mandir}/man1/%{package_prefix}-{dlltool,windres,windmc}*
rm -rf %{buildroot}%{_infodir}


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
%{_prefix}/bin/spu-elfedit
%{_prefix}/bin/spu-ld.bfd
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


%changelog
* Thu Nov 5 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.32-2
- Initial build - https://ps3linux.net

