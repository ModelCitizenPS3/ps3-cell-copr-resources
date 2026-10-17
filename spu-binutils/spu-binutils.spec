# Don't strip as the host binutils may be unable to handle SPU objects.
%define __os_install_post /usr/lib/rpm/brp-compress
%define _build_id_links none

%define _prefix /opt/cell/toolchain
%define _libdir %{_prefix}/lib
%define target spu-elf

Name:           spu-binutils
Version:        2.45
Release:        1%{?dist}
Summary:        GNU binary utilities for the Cell/B.E. SPU
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
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir} \
    --infodir=%{_infodir} \
    --with-sysroot=/opt/cell/sysroot \
    --disable-silent-rules \
    --program-prefix=spu- \
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
rm -f %{buildroot}%{_mandir}/man1/spu-{dlltool,nlmconv,windres,windmc}*
rm -rf %{buildroot}%{_infodir}
rm -f %{buildroot}%{_infodir}/dir


%files
%defattr(-,root,root)
%{_bindir}/spu-addr2line
%{_bindir}/spu-ar
%{_bindir}/spu-as
%{_bindir}/spu-c++filt
%{_bindir}/spu-ld
%{_bindir}/spu-nm
%{_bindir}/spu-objcopy
%{_bindir}/spu-objdump
%{_bindir}/spu-ranlib
%{_bindir}/spu-readelf
%{_bindir}/spu-size
%{_bindir}/spu-strings
%{_bindir}/spu-strip
%{_bindir}/spu-gprof
%{_bindir}/spu-elfedit
%{_bindir}/spu-ld.bfd
%dir %{_prefix}/%{target}
%dir %{_prefix}/%{target}/bin
%dir %{_prefix}/%{target}/lib
%{_prefix}/%{target}/bin/*
%{_prefix}/%{target}/lib/ldscripts
%{_mandir}/man1/spu-addr2line.1*
%{_mandir}/man1/spu-ar.1*
%{_mandir}/man1/spu-as.1*
%{_mandir}/man1/spu-c++filt.1*
%{_mandir}/man1/spu-ld.1*
%{_mandir}/man1/spu-nm.1*
%{_mandir}/man1/spu-objcopy.1*
%{_mandir}/man1/spu-objdump.1*
%{_mandir}/man1/spu-ranlib.1*
%{_mandir}/man1/spu-readelf.1*
%{_mandir}/man1/spu-size.1*
%{_mandir}/man1/spu-strings.1*
%{_mandir}/man1/spu-strip.1*
%{_mandir}/man1/spu-gprof.1*
%{_mandir}/man1/spu-elfedit.1*
%dir %{_libdir}/bfd-plugins
%{_libdir}/bfd-plugins/libdep.a


%changelog
* Fri Oct 16 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 2.45-1
- Initial build for PS3LINUX on the Cell/B.E. https://ps3linux.net

