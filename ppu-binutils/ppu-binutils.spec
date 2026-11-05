%undefine optflags
%undefine build_ldflags
%global package_prefix ppu
%global target_platform powerpc64-linux-gnu
%global _prefix /opt/cell/toolchain
%global _libdir /opt/cell/toolchain/lib64
%global _mandir %{_prefix}/man
%global _infodir %{_prefix}/info
%global __os_install_post /usr/lib/rpm/brp-compress

Summary:        GNU binary utilities for the Cell/B.E. PPU
Name:           %{package_prefix}-binutils
Version:        2.32
Release:        1.CELL
License:        GPL
Group:          Cell Development Tools
Source0:        https://ftp.gnu.org/gnu/binutils/binutils-%{version}.tar.xz
ExclusiveArch:  ppc64 x86_64

BuildRequires:  dejagnu, bison, flex, texinfo
BuildRequires:  gcc, cpp

%description
The GNU binutils version %{version} for the Cell/B.E. PPU (powerpc64) core.


%prep
%setup -c -q


%build
rm -rf build
mkdir -p build
pushd build
CC="gcc -m64 -O2 -g" \
CFLAGS="-mtune=generic -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64" \
LDFLAGS= \
../binutils-%{version}/configure \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir}  \
    --infodir=%{_infodir} \
	--build=`gcc -dumpmachine` \
    --host=`gcc -dumpmachine` \
    --target=%{target_platform} \
    --enable-targets=spu \
    --with-sysroot=/opt/cell/sysroot \
    --with-lib-path=/opt/cell/toolchain/lib64 \
    --disable-install-libbfd \
    --program-prefix=%{package_prefix}- \
    --disable-nls \
    --disable-werror \
    --enable-64-bit-bfd
make -j1
popd


%check


%install
rm -rf %{buildroot}
pushd build
make DESTDIR=%{buildroot} -j1 install
popd
rm -f %{buildroot}%{_mandir}/man1/%{package_prefix}-{dlltool,nlmconv,windres,windmc}*
rm -rf %{buildroot}%{_infodir}
rm -rf %{buildroot}%{_mandir}/man7


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
* Thu Nov 5 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.32-1
- Initial build - https://ps3linux.net

