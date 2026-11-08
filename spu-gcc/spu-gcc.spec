# banish all Fedora/RedHat compile flags from the build
%undefine optflags
%undefine build_cflags
%undefine build_cxxflags
%undefine build_ldflags
%undefine _hardened_build
%undefine _annotated_build
%undefine _auto_set_build_flags

# dwz runs slow as hell on the PS3
%ifarch ppc64
%undefine _find_debuginfo_dwz_opts
%endif

Name:           spu-gcc
Version:        9.5.0
Release:        4.CELL
Summary:        GNU Compiler Collection for Cell/B.E. SPU
License:        GPL
Group:          Cell Development Tools
Source0:        https://ftp.gnu.org/gnu/gcc/gcc-%{version}/gcc-%{version}.tar.xz
Source2:        gcc-9.5.0-format-security-syntax-fix.patch
ExclusiveArch:  ppc64 x86_64

BuildRequires:  zlib-devel, gettext, dejagnu, bison, flex, texinfo, isl-devel, spu-binutils
BuildRequires:  gcc, gcc-c++, binutils, cpp, gmp-devel, mpfr-devel, libmpc-devel
BuildRequires:  spu-newlib
Requires:       spu-binutils, gmp, mpfr, libmpc, isl
Requires:       spu-newlib
AutoProv:       no
AutoReq:        no

%description 
The GNU Compiler Collection version %{version} for Cell Broadband Engine SPU.

# Don't strip as the host binutils may be unable to handle SPU/PPU objects.
%define __os_install_post /usr/lib/rpm/brp-compress

# When building the cross-toolchain, reset prefix directory and use sysroot
%ifarch x86_64
%define _prefix /opt/cell/toolchain
%define _libdir %{_prefix}/lib
%define _mandir %{_prefix}/man
%define _infodir %{_prefix}/info
%define with_sysroot --with-sysroot=/opt/cell/sysroot
%else
%define _libdir %{_prefix}/lib
%endif

%package -n spu-gcc-c++
Summary:    C++ support for spu-gcc
Group:      Cell Development Tools
Requires:   spu-gcc = %{version}-%{release}
AutoProv:   no
AutoReq:    yes

%description -n spu-gcc-c++
GNU Compiler Collection C++ compiler for Cell Broadband Engine.

%package -n spu-gcc-fortran
Summary:    Fortran support for spu-gcc
Group:      Cell Development Tools
Requires:   spu-gcc = %{version}-%{release}
AutoProv:   no
AutoReq:    yes

%description -n spu-gcc-fortran
GNU Compiler Collection Fortran compiler for Cell Broadband Engine.


%prep
%setup -c -q
pushd gcc-%{version}
patch -p1 < %{SOURCE2}
popd


%build
%ifarch ppc64
%define build_arch powerpc64-unknown-linux-gnu
%define mcpu_mtune -mcpu=cell -mtune=cell
%else
%define build_arch x86_64-unknown-linux-gnu
%define mcpu_mtune -mcpu=x86_64 -mtune=generic
%endif

rm -rf build
mkdir build
pushd build

CC="gcc -m64" \
CXX="g++ -m64" \
CFLAGS="-O2 -g %{mcpu_mtune} -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64" \
CXXFLAGS="-O2 -g %{mcpu_mtune} -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64" \
LDFLAGS= \
../gcc-%{version}/configure --prefix=%{_prefix} --libdir=%{_libdir} --mandir=%{_mandir} \
    --infodir=%{_infodir} %{?with_sysroot} --disable-shared --disable-threads --disable-checking \
    --with-headers --with-system-zlib --with-newlib --enable-languages=c,c++,fortran --disable-nls \
    --enable-version-specific-runtime-libs --disable-libssp --program-prefix=spu- \
    --disable-hosted-libstdcxx --enable-cxx-flags='-fno-exceptions' --target=spu \
    --disable-werror --disable-libcc1 --enable-obsolete 
make -j1
popd


%check


%install
rm -fr %{buildroot}
pushd build
make DESTDIR=%{buildroot} -j1 install
popd

ln -sf spu-gcc %{buildroot}%{_prefix}/bin/spu-cc

rm -f %{buildroot}%{_prefix}/bin/vxaddr2line
rm -f %{buildroot}%{_prefix}/bin/spu-spu-*
rm -f %{buildroot}%{_prefix}/bin/spu-gcc-%{version}
rm -f %{buildroot}%{_prefix}/bin/spu-gccbug

rm -f %{buildroot}%{_prefix}/lib*/libiberty.a
rm -f %{buildroot}%{_prefix}/lib*/*/libiberty.a
rm -f %{buildroot}%{_prefix}/spu/lib*/libiberty.a
rm -f %{buildroot}%{_prefix}/spu/lib*/*/libiberty.a

rm -rf %{buildroot}%{_prefix}/lib/gcc/spu/%{version}/install-tools
rm -rf %{buildroot}%{_prefix}/libexec/gcc/spu/%{version}/install-tools

rm -f %{buildroot}%{_prefix}/lib/gcc/spu/%{version}/*.la
rm -f %{buildroot}%{_prefix}/lib/gcc/spu/%{version}/*/*.la

rm -f %{buildroot}%{_prefix}/libexec/gcc/spu/%{version}/liblto_plugin.la

for h in \
  `find $RPM_BUILD_ROOT%{_prefix}/lib/gcc/spu/%{version}/include -name \*.h`
do
  if grep -q 'It has been auto-edited by fixincludes from' $h; then
    rh=`grep -A2 'It has been auto-edited by fixincludes from' $h | tail -1 | sed 's|^.*"\(.*\)".*$|\1|'`
    diff -up $rh $h || :
    rm -f $h
  fi
done

cat > $RPM_BUILD_ROOT%{_prefix}/bin/spu-c89 <<"EOF"
#!/bin/sh
fl="-std=c89"
for opt; do
  case "$opt" in
    -ansi|-std=c89|-std=iso9899:1990) fl="";;
    -std=*) echo "`basename $0` called with non ANSI/ISO C option $opt" >&2
	    exit 1;;
  esac
done
exec %{_prefix}/bin/spu-gcc $fl ${1+"$@"}
EOF
cat > $RPM_BUILD_ROOT%{_prefix}/bin/spu-c99 <<"EOF"
#!/bin/sh
fl="-std=c99"
for opt; do
  case "$opt" in
    -std=c99|-std=iso9899:1999) fl="";;
    -std=*) echo "`basename $0` called with non ISO C99 option $opt" >&2
	    exit 1;;
  esac
done
exec %{_prefix}/bin/spu-gcc $fl ${1+"$@"}
EOF
chmod 755 $RPM_BUILD_ROOT%{_prefix}/bin/spu-c?9

rm -rf %{buildroot}%{_infodir}
rm -rf %{buildroot}%{_mandir}/man7
rm -f %{buildroot}%{_prefix}/bin/spu-gcc-{ar,nm,ranlib}
rm -f %{buildroot}%{_prefix}/bin/spu-gcov-{dump,tool}


%files -n spu-gcc
%defattr(-,root,root)
%ifarch x86_64
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_mandir}
%dir %{_mandir}/man1
%dir %{_prefix}/lib
%endif
%{_prefix}/bin/spu-cc
%{_prefix}/bin/spu-c89
%{_prefix}/bin/spu-c99
%{_prefix}/bin/spu-gcc
%{_prefix}/bin/spu-gcov
%{_prefix}/bin/spu-cpp
%{_mandir}/man1/spu-gcc.1*
%{_mandir}/man1/spu-gcov.1*
%{_mandir}/man1/spu-cpp.1*
%{_mandir}/man1/spu-gcov-dump.1*
%{_mandir}/man1/spu-gcov-tool.1*
%dir %{_prefix}/libexec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/spu
%dir %{_prefix}/libexec/gcc/spu/%{version}
%{_prefix}/libexec/gcc/spu/%{version}/cc1
%{_prefix}/libexec/gcc/spu/%{version}/collect2
%{_prefix}/libexec/gcc/spu/%{version}/liblto_plugin.so
%{_prefix}/libexec/gcc/spu/%{version}/liblto_plugin.so.0
%{_prefix}/libexec/gcc/spu/%{version}/liblto_plugin.so.0.0.0
%{_prefix}/libexec/gcc/spu/%{version}/lto-wrapper
%{_prefix}/libexec/gcc/spu/%{version}/lto1
%{_prefix}/libexec/gcc/spu/%{version}/plugin/gengtype
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/spu
%dir %{_prefix}/lib/gcc/spu/%{version}
%dir %{_prefix}/lib/gcc/spu/%{version}/include
%{_prefix}/lib/gcc/spu/%{version}/include/*
%{_prefix}/lib/gcc/spu/%{version}/include-fixed/README
%{_prefix}/lib/gcc/spu/%{version}/include-fixed/limits.h
%{_prefix}/lib/gcc/spu/%{version}/include-fixed/syslimits.h
%dir %{_prefix}/lib/gcc/spu/%{version}/plugin
%{_prefix}/lib/gcc/spu/%{version}/plugin/*
%{_prefix}/lib/gcc/spu/%{version}/*crt*.o
%{_prefix}/lib/gcc/spu/%{version}/libgcc.a
%{_prefix}/lib/gcc/spu/%{version}/libgcov.a
%{_prefix}/lib/gcc/spu/%{version}/libgcc_*.a
%dir %{_prefix}/lib/gcc/spu/%{version}/mea64
%{_prefix}/lib/gcc/spu/%{version}/mea64/*crt*.o
%{_prefix}/lib/gcc/spu/%{version}/mea64/libgcc.a
%{_prefix}/lib/gcc/spu/%{version}/mea64/libgcov.a
%{_prefix}/lib/gcc/spu/%{version}/mea64/libgcc_*.a

%files -n spu-gcc-c++
%defattr(-,root,root)
%ifarch x86_64
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_mandir}
%dir %{_mandir}/man1
%dir %{_prefix}/lib
%endif
%{_prefix}/bin/spu-g++
%{_prefix}/bin/spu-c++
%{_mandir}/man1/spu-g++.1*
%dir %{_prefix}/libexec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/spu
%dir %{_prefix}/libexec/gcc/spu/%{version}
%{_prefix}/libexec/gcc/spu/%{version}/cc1plus
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/spu
%dir %{_prefix}/lib/gcc/spu/%{version}
%dir %{_prefix}/lib/gcc/spu/%{version}/include
%{_prefix}/lib/gcc/spu/%{version}/include/c++
%{_prefix}/lib/gcc/spu/%{version}/libsupc++.a
%dir %{_prefix}/lib/gcc/spu/%{version}/mea64
%{_prefix}/lib/gcc/spu/%{version}/mea64/libsupc++.a

%files -n spu-gcc-fortran
%defattr(-,root,root)
%ifarch x86_64
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_mandir}
%dir %{_mandir}/man1
%dir %{_prefix}/lib
%endif
%{_prefix}/bin/spu-gfortran
%{_mandir}/man1/spu-gfortran.1*
%dir %{_prefix}/libexec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/spu
%dir %{_prefix}/libexec/gcc/spu/%{version}
%{_prefix}/libexec/gcc/spu/%{version}/f951
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/spu
%dir %{_prefix}/lib/gcc/spu/%{version}
%{_prefix}/lib/gcc/spu/%{version}/libgfortran.a
%dir %{_prefix}/lib/gcc/spu/%{version}/mea64
%{_prefix}/lib/gcc/spu/%{version}/mea64/libgfortran.a
%{_prefix}/lib/gcc/spu/%{version}/libcaf_single.a
%{_prefix}/lib/gcc/spu/%{version}/libgfortran.spec
%{_prefix}/lib/gcc/spu/%{version}/mea64/libcaf_single.a
%{_prefix}/lib/gcc/spu/%{version}/mea64/libgfortran.spec


%changelog
* Sat Nov 7 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 9.5.0-4
- Added fortran to the build

* Sat Nov 7 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 9.5.0-3
- Removed newlib from build and created as a separate package

* Fri Nov 6 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 9.5.0-2
- Added ppc64 to ExclusiveArch tag (for PS3LINUX)

* Mon Nov 2 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 9.5.0-1
- Initial build

