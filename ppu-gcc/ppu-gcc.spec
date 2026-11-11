%undefine optflags
%undefine build_cflags
%undefine build_cxxflags
%undefine build_ldflags
%undefine _hardened_build
%undefine _annotated_build
%undefine _auto_set_build_flags

%global debug_package %{nil}
%global _build_id_links none
%global __strip /bin/true
%global __os_install_post %{nil}

# Prevent RPM from extracting requirements from the target toolchain paths
%ifarch x86_64
%global __requires_exclude_from ^/opt/cell/toolchain/.*$
%endif

Name:           ppu-gcc
Version:        9.5.0
Release:        1.CELL
Summary:        GNU Compiler Collection for Cell Broadband Engine PPU
License:        GPL
Group:          Cell Development Tools
Source0:        https://ftp.gnu.org/gnu/gcc/gcc-%{version}/gcc-%{version}.tar.xz
Patch1:         gcc-9.5.0-add-ppu-target.patch
Patch2:         gcc-9.5.0-format-security-syntax-fix.patch
ExclusiveArch:  ppc64 x86_64

BuildRequires:  zlib-devel, gettext, dejagnu, bison, flex, texinfo
BuildRequires:  gmp-devel, mpfr-devel, libmpc-devel, isl-devel
BuildRequires:  ppu-binutils, gcc, gcc-c++, cpp, glibc-devel
%ifarch x86_64
BuildRequires:  ppu-sysroot64
Requires:       ppu-sysroot64
%endif
Requires:       ppu-binutils, gmp, mpfr, libmpc, isl, glibc-devel
AutoProv:       no
AutoReq:        no

%description 
The GNU Compiler Collection version %{version}.

# Don't strip as the host binutils may be unable to handle SPU/PPU objects.
%define __os_install_post /usr/lib/rpm/brp-compress

# When building the cross-toolchain, reset prefix directory and use sysroot
%ifarch x86_64
%define _prefix /opt/cell/toolchain
%define _libdir %{_prefix}/lib64
%define _mandir %{_prefix}/man
%define _infodir %{_prefix}/info
%define with_sysroot --with-sysroot=/opt/cell/sysroot
%else
%define _libdir %{_prefix}/lib64
%endif

%package -n ppu-gcc-c++
Summary:    C++ support for ppu-gcc
Group:      Cell Development Tools
Requires:   ppu-gcc = %{version}-%{release}
AutoProv:   no
AutoReq:    yes

%description -n ppu-gcc-c++
GNU Compiler Collection C++ compiler for Cell Broadband Engine.

%package -n ppu-gcc-fortran
Summary:    Fortran support for %{package_prefix}-gcc
Group:      Cell Development Tools
Requires:   ppu-gcc = %{version}-%{release}
AutoProv:   no
AutoReq:    yes

%description -n ppu-gcc-fortran
GNU Compiler Collection Fortran compiler for Cell Broadband Engine.


%prep
%setup -q -n gcc-%{version}
patch -p1 < %{PATCH1}
patch -p1 < %{PATCH2}


%build
%ifarch x86_64
%define build_arch x86_64-unknown-linux-gnu
%define with_as /opt/cell/toolchain/bin/ppu-as
%define with_ld /opt/cell/toolchain/bin/ppu-ld
export AR_FOR_TARGET=/opt/cell/toolchain/bin/ppu-ar
export RANLIB_FOR_TARGET=/opt/cell/toolchain/bin/ppu-ranlib
export NM_FOR_TARGET=/opt/cell/toolchain/bin/ppu-nm
%endif
%ifarch ppc64
%define build_arch powerpc64-unknown-linux-gnu
%define with_as /usr/bin/ppu-as
%define with_ld /usr/bin/ppu-ld
%endif

rm -rf build
mkdir -p build
pushd build

CC="gcc -m64" CXX="g++ -m64" LDFLAGS= \
../configure \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir} \
    --infodir=%{_infodir} \
	%{?with_sysroot} \
	--with-as=%{with_as} \
	--with-ld=%{with_ld} \
	--enable-threads \
    --with-system-zlib \
    --disable-checking \
	--enable-__cxa_atexit \
    --disable-libunwind-exceptions \
	--enable-languages=c,c++,fortran \
    --disable-nls \
	--enable-clocale=gnu \
	--enable-version-specific-runtime-libs \
	--with-long-double-128 \
    --program-prefix=ppu- \
	--disable-bootstrap \
%ifarch ppc64
	--host=ppu \
%endif
	--build=%{build_arch} \
	--target=ppu \
    --disable-multilib \
    --with-multiliib-list=m64 \
    --disable-libssp \
    --disable-libsanitizer \
    --disable-libcc1
make -j2
popd


%install
rm -rf %{buildroot}
pushd build
make DESTDIR=%{buildroot} -j1 install
popd

ln -sf ppu-gcc %{buildroot}%{_prefix}/bin/ppu-cc

rm -f %{buildroot}%{_prefix}/bin/vxaddr2line
rm -f %{buildroot}%{_prefix}/bin/powerpc64-linux-gnu-ppu-*
rm -f %{buildroot}%{_prefix}/bin/ppu-gcc-%{version}
rm -f %{buildroot}%{_prefix}/bin/ppu-gccbug
rm -f %{buildroot}%{_prefix}/lib*/libiberty.a
rm -f %{buildroot}%{_prefix}/lib*/*/libiberty.a
rm -f %{buildroot}%{_prefix}/powerpc64-linux-gnu/lib*/libiberty.a
rm -f %{buildroot}%{_prefix}/powerpc64-linux-gnu/lib*/*/libiberty.a
rm -rf %{buildroot}%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/install-tools
rm -rf %{buildroot}%{_prefix}/libexec/gcc/powerpc64-linux-gnu/%{version}/install-tools
rm -f %{buildroot}%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/*.la
rm -f %{buildroot}%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/*/*.la
rm -f %{buildroot}%{_prefix}/libexec/gcc/powerpc64-linux-gnu/%{version}/liblto_plugin.la
rm -f %{buildroot}%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libgfortran.la
rm -f %{buildroot}%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/mea64/libcaf_single.la
rm -f %{buildroot}%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/mea64/libgfortran.la
rm -f %{buildroot}%{_prefix}/lib64/libcc1.la
mv %{buildroot}%{_prefix}/lib64/gcc/ppu/lib64/* %{buildroot}%{_prefix}/lib64/gcc/ppu/%{version}/
rm -rf %{buildroot}%{_prefix}/lib/gcc/powerpc64-linux-gnu/lib
rm -rf %{buildroot}%{_prefix}/lib/gcc/powerpc64-linux-gnu/lib64

for h in \
  `find %{buildroot}%{_libdir}/gcc/powerpc64-linux-gnu/%{version}/include -name \*.h`
do
  if grep -q 'It has been auto-edited by fixincludes from' $h; then
    rh=`grep -A2 'It has been auto-edited by fixincludes from' $h | tail -1 | sed 's|^.*"\(.*\)".*$|\1|'`
    diff -up $rh $h || :
    rm -f $h
  fi
done

cat > %{buildroot}%{_bindir}/ppu-c89 <<"EOF"
#!/bin/sh
fl="-std=c89"
for opt; do
  case "$opt" in
    -ansi|-std=c89|-std=iso9899:1990) fl="";;
    -std=*) echo "`basename $0` called with non ANSI/ISO C option $opt" >&2
	    exit 1;;
  esac
done
exec %{_bindir}/ppu-gcc $fl ${1+"$@"}
EOF
cat > %{buildroot}%{_bindir}/ppu-c99 <<"EOF"
#!/bin/sh
fl="-std=c99"
for opt; do
  case "$opt" in
    -std=c99|-std=iso9899:1999) fl="";;
    -std=*) echo "`basename $0` called with non ISO C99 option $opt" >&2
	    exit 1;;
  esac
done
exec %{_bindir}/ppu-gcc $fl ${1+"$@"}
EOF
chmod 755 %{buildroot}%{_bindir}/ppu-c?9

rm -rf %{buildroot}%{_infodir}
rm -rf %{buildroot}%{_mandir}/man7
rm -f %{buildroot}%{_prefix}/lib64/gcc/ppu/%{version}/include-fixed/README
rm -f %{buildroot}%{_prefix}/lib64/gcc/ppu/%{version}/libsupc++.la
rm -f %{buildroot}%{_prefix}/lib64/gcc/ppu/%{version}/mea64/libsupc++.la
rm -f %{buildroot}%{_datadir}/ppu-gcc-testsuite/ada/acats/run_all.sh
rm -f %{buildroot}/usr/bin/ppu-ppu-*


%check


%files -n ppu-gcc
%defattr(-,root,root)
%ifarch x86_64
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_prefix}/lib64
%dir %{_prefix}/libexec
%dir %{_prefix}/man
%dir %{_prefix}/man/man1
%{_prefix}/man/man1/ppu-cpp.1
%{_prefix}/man/man1/ppu-gcc.1
%{_prefix}/man/man1/ppu-gcov.1
%{_prefix}/man/man1/ppu-gcov-dump.1
%{_prefix}/man/man1/ppu-gcov-tool.1
%endif
%ifarch ppc64
%{_prefix}/lib64/gcc/ppu/%{version}/include-fixed/pthread.h
%{_prefix}/share/man/man1/ppu-cpp.1.gz
%{_prefix}/share/man/man1/ppu-gcc.1.gz
%{_prefix}/share/man/man1/ppu-gcov-dump.1.gz
%{_prefix}/share/man/man1/ppu-gcov-tool.1.gz
%{_prefix}/share/man/man1/ppu-gcov.1.gz
%endif
%{_prefix}/bin/ppu-c89
%{_prefix}/bin/ppu-c99
%{_prefix}/bin/ppu-cc
%{_prefix}/bin/ppu-cpp
%{_prefix}/bin/ppu-gcc
%{_prefix}/bin/ppu-gcov
%{_prefix}/bin/ppu-gcc-ar
%{_prefix}/bin/ppu-gcc-nm
%{_prefix}/bin/ppu-gcc-ranlib
%{_prefix}/bin/ppu-gcov-dump
%{_prefix}/bin/ppu-gcov-tool
%dir %{_prefix}/lib64/gcc
%dir %{_prefix}/lib64/gcc/ppu
%dir %{_prefix}/lib64/gcc/ppu/%{version}
%{_prefix}/lib64/gcc/ppu/%{version}/crtbegin.o
%{_prefix}/lib64/gcc/ppu/%{version}/crtbeginS.o
%{_prefix}/lib64/gcc/ppu/%{version}/crtbeginT.o
%{_prefix}/lib64/gcc/ppu/%{version}/crtend.o
%{_prefix}/lib64/gcc/ppu/%{version}/crtendS.o
%{_prefix}/lib64/gcc/ppu/%{version}/ecrti.o
%{_prefix}/lib64/gcc/ppu/%{version}/ecrtn.o
%dir %{_prefix}/lib64/gcc/ppu/%{version}/include-fixed
%{_prefix}/lib64/gcc/ppu/%{version}/include-fixed/limits.h
%{_prefix}/lib64/gcc/ppu/%{version}/include-fixed/syslimits.h
%dir %{_prefix}/lib64/gcc/ppu/%{version}/include
%{_prefix}/lib64/gcc/ppu/%{version}/include/altivec.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/float.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/iso646.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/ppc-asm.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/ppu_intrinsics.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/si2vmx.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/spu2vmx.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdarg.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdbool.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stddef.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/unwind.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/varargs.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/vec_types.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/amo.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/bmi2intrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/bmiintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/emmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/gcov.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/htmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/htmxlintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/mm_malloc.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/mmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/omp.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/openacc.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/pmmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/smmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdalign.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdatomic.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdfix.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdint-gcc.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdint.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdnoreturn.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/tmmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/x86intrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/xmmintrin.h
%dir %{_prefix}/lib64/gcc/ppu/%{version}/install-tools
%{_prefix}/lib64/gcc/ppu/%{version}/install-tools/fixinc_list
%{_prefix}/lib64/gcc/ppu/%{version}/install-tools/gsyslimits.h
%{_prefix}/lib64/gcc/ppu/%{version}/install-tools/include/README
%{_prefix}/lib64/gcc/ppu/%{version}/install-tools/include/limits.h
%{_prefix}/lib64/gcc/ppu/%{version}/install-tools/macro_list
%{_prefix}/lib64/gcc/ppu/%{version}/install-tools/mkheaders.conf
%{_prefix}/lib64/gcc/ppu/%{version}/libgcc.a
%{_prefix}/lib64/gcc/ppu/%{version}/libgcc_eh.a
%{_prefix}/lib64/gcc/ppu/%{version}/libgcc_s.so
%{_prefix}/lib64/gcc/ppu/%{version}/libgcc_s.so.1
%{_prefix}/lib64/gcc/ppu/%{version}/libgcov.a
%{_prefix}/lib64/gcc/ppu/%{version}/ncrti.o
%{_prefix}/lib64/gcc/ppu/%{version}/ncrtn.o
%{_prefix}/lib64/gcc/ppu/%{version}/libatomic.a
%{_prefix}/lib64/gcc/ppu/%{version}/libatomic.la
%{_prefix}/lib64/gcc/ppu/%{version}/libatomic.so
%{_prefix}/lib64/gcc/ppu/%{version}/libatomic.so.1
%{_prefix}/lib64/gcc/ppu/%{version}/libatomic.so.1.2.0
%{_prefix}/lib64/gcc/ppu/%{version}/libgomp.a
%{_prefix}/lib64/gcc/ppu/%{version}/libgomp.la
%{_prefix}/lib64/gcc/ppu/%{version}/libgomp.so
%{_prefix}/lib64/gcc/ppu/%{version}/libgomp.so.1
%{_prefix}/lib64/gcc/ppu/%{version}/libgomp.so.1.0.0
%{_prefix}/lib64/gcc/ppu/%{version}/libgomp.spec
%dir %{_prefix}/lib64/gcc/ppu/%{version}/plugin
%{_prefix}/lib64/gcc/ppu/%{version}/plugin/*
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/ppu
%dir %{_prefix}/libexec/gcc/ppu/%{version}
%{_prefix}/libexec/gcc/ppu/%{version}/cc1
%{_prefix}/libexec/gcc/ppu/%{version}/collect2
%dir %{_prefix}/libexec/gcc/ppu/%{version}/install-tools
%{_prefix}/libexec/gcc/ppu/%{version}/install-tools/fixinc.sh
%{_prefix}/libexec/gcc/ppu/%{version}/install-tools/fixincl
%{_prefix}/libexec/gcc/ppu/%{version}/install-tools/mkheaders
%{_prefix}/libexec/gcc/ppu/%{version}/install-tools/mkinstalldirs
%{_prefix}/libexec/gcc/ppu/%{version}/liblto_plugin.la
%{_prefix}/libexec/gcc/ppu/%{version}/liblto_plugin.so
%{_prefix}/libexec/gcc/ppu/%{version}/liblto_plugin.so.0
%{_prefix}/libexec/gcc/ppu/%{version}/liblto_plugin.so.0.0.0
%{_prefix}/libexec/gcc/ppu/%{version}/lto-wrapper
%{_prefix}/libexec/gcc/ppu/%{version}/lto1
%dir %{_prefix}/libexec/gcc/ppu/%{version}/plugin
%{_prefix}/libexec/gcc/ppu/%{version}/plugin/gengtype

%files -n ppu-gcc-c++
%defattr(-,root,root)
%ifarch x86_64
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_prefix}/lib64
%dir %{_prefix}/libexec
%{_prefix}/man/man1/ppu-g++.1*
%endif
%ifarch ppc64
%{_prefix}/share/man/man1/ppu-g++.1*
%endif
%{_prefix}/bin/ppu-c++
%{_prefix}/bin/ppu-g++
%dir %{_prefix}/lib64/gcc
%dir %{_prefix}/lib64/gcc/ppu
%dir %{_prefix}/lib64/gcc/ppu/%{version}
%dir %{_prefix}/lib64/gcc/ppu/%{version}/include
%dir %{_prefix}/lib64/gcc/ppu/%{version}/include/c++
%{_prefix}/lib64/gcc/ppu/%{version}/include/c++/*
%{_prefix}/lib64/gcc/ppu/%{version}/libstdc++.a
%{_prefix}/lib64/gcc/ppu/%{version}/libstdc++.so
%{_prefix}/lib64/gcc/ppu/%{version}/libstdc++.so.6
%{_prefix}/lib64/gcc/ppu/%{version}/libsupc++.a
%{_prefix}/lib64/gcc/ppu/%{version}/libitm.a
%{_prefix}/lib64/gcc/ppu/%{version}/libitm.la
%{_prefix}/lib64/gcc/ppu/%{version}/libitm.so
%{_prefix}/lib64/gcc/ppu/%{version}/libitm.so.1
%{_prefix}/lib64/gcc/ppu/%{version}/libitm.so.1.0.0
%{_prefix}/lib64/gcc/ppu/%{version}/libitm.spec
%{_prefix}/lib64/gcc/ppu/%{version}/libstdc++.la
%{_prefix}/lib64/gcc/ppu/%{version}/libstdc++.so.6.0.28
%{_prefix}/lib64/gcc/ppu/%{version}/libstdc++.so.6.0.28-gdb.py
%{_prefix}/lib64/gcc/ppu/%{version}/libstdc++fs.a
%{_prefix}/lib64/gcc/ppu/%{version}/libstdc++fs.la
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/ppu
%dir %{_prefix}/libexec/gcc/ppu/%{version}
%{_prefix}/libexec/gcc/ppu/%{version}/cc1plus
%{_prefix}/share/gcc-%{version}/python/libstdcxx/__init__.py
%{_prefix}/share/gcc-%{version}/python/libstdcxx/v6/__init__.py
%{_prefix}/share/gcc-%{version}/python/libstdcxx/v6/printers.py
%{_prefix}/share/gcc-%{version}/python/libstdcxx/v6/xmethods.py

%files -n ppu-gcc-fortran
%defattr(-,root,root)
%ifarch x86_64
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_prefix}/lib64
%dir %{_prefix}/libexec
%dir %{_prefix}/man
%dir %{_prefix}/man/man1
%{_prefix}/man/man1/ppu-gfortran.1*
%endif
%ifarch ppc64
%{_prefix}/share/man/man1/ppu-gfortran.1*
%endif
%{_prefix}/bin/ppu-gfortran
%dir %{_prefix}/lib64/gcc
%dir %{_prefix}/lib64/gcc/ppu
%dir %{_prefix}/lib64/gcc/ppu/%{version}
%dir %{_prefix}/lib64/gcc/ppu/%{version}/finclude
%{_prefix}/lib64/gcc/ppu/%{version}/finclude/ieee_arithmetic.mod
%{_prefix}/lib64/gcc/ppu/%{version}/finclude/ieee_exceptions.mod
%{_prefix}/lib64/gcc/ppu/%{version}/finclude/ieee_features.mod
%{_prefix}/lib64/gcc/ppu/%{version}/finclude/omp_lib.f90
%{_prefix}/lib64/gcc/ppu/%{version}/finclude/omp_lib.h
%{_prefix}/lib64/gcc/ppu/%{version}/finclude/omp_lib.mod
%{_prefix}/lib64/gcc/ppu/%{version}/finclude/omp_lib_kinds.mod
%{_prefix}/lib64/gcc/ppu/%{version}/finclude/openacc.f90
%{_prefix}/lib64/gcc/ppu/%{version}/finclude/openacc.mod
%{_prefix}/lib64/gcc/ppu/%{version}/finclude/openacc_kinds.mod
%{_prefix}/lib64/gcc/ppu/%{version}/finclude/openacc_lib.h
%dir %{_prefix}/lib64/gcc/ppu/%{version}/include
%{_prefix}/lib64/gcc/ppu/%{version}/include/ISO_Fortran_binding.h
%{_prefix}/lib64/gcc/ppu/%{version}/libcaf_single.a
%{_prefix}/lib64/gcc/ppu/%{version}/libcaf_single.la
%{_prefix}/lib64/gcc/ppu/%{version}/libgfortran.a
%{_prefix}/lib64/gcc/ppu/%{version}/libgfortran.la
%{_prefix}/lib64/gcc/ppu/%{version}/libgfortran.so
%{_prefix}/lib64/gcc/ppu/%{version}/libgfortran.so.5
%{_prefix}/lib64/gcc/ppu/%{version}/libgfortran.so.5.0.0
%{_prefix}/lib64/gcc/ppu/%{version}/libgfortran.spec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/ppu
%dir %{_prefix}/libexec/gcc/ppu/%{version}
%{_prefix}/libexec/gcc/ppu/%{version}/f951


%changelog
* Sat Nov 7 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 9.5.0-1
- Initial build

