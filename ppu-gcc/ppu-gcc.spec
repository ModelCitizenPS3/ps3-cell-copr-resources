# banish all Fedora/RedHat compile flags from the build
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

%if 0
%package -n ppu-gcc-fortran
Summary:    Fortran support for ppu-gcc
Group:      Cell Development Tools
Requires:   ppu-gcc = %{version}-%{release}
AutoProv:   no
AutoReq:    yes

%description -n ppu-gcc-fortran
GNU Compiler Collection Fortran compiler for Cell Broadband Engine.

%package -n ppu-gcc-testsuite
Summary:    DejaGnu testsuite for ppu-gcc
Group:      Cell Development Tools
Requires:   ppu-gcc = %{version}-%{release}
Requires:   dejagnu
AutoProv:   no
AutoReq:    no

%description -n ppu-gcc-testsuite
Testsuite driver for the Cell Broadband Engine version of GCC.

%package -n ppu-gcc-gnat
Summary:        Ada support for PPU compiler
Group:          Cell Development Tools
Requires:       ppu-gcc = %{version}-%{release}
# ppu-gnat version will not compile
# Fedora 44's gcc-gnat is too new; it will not bootstrap our build
%if 0
BuildRequires:  ppu-gcc-gnat
%else
BuildRequires:  gcc-gnat
%endif
AutoProv:       no
AutoReq:        no

%description -n ppu-gcc-gnat
GNU Compiler Collection Ada compiler for Cell Broadband Engine.
%endif


%prep
%setup -q -n gcc-%{version}
patch -p1 < %{PATCH1}
patch -p1 < %{PATCH2}


%build
%ifarch ppc64
%define build_arch powerpc64-unknown-linux-gnu
%else
%define build_arch x86_64-unknown-linux-gnu
export PATH=/opt/cell/toolchain/bin:$PATH
%endif

rm -rf obj-powerpc64-linux-gnu
mkdir -p obj-powerpc64-linux-gnu
pushd obj-powerpc64-linux-gnu

#PPU_OPT_FLAGS="-O2 -g -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64"
%ifarch ppc64
CC="ppu-gcc -m64"
%else
CC="gcc -m64"
%endif
#CC="$CC" CFLAGS="$PPU_OPT_FLAGS" CXXFLAGS="$PPU_OPT_FLAGS" XCFLAGS="$OPT_FLAGS" TCFLAGS="$PPU_OPT_FLAGS" \
LDFLAGS= ../configure --prefix=%{_prefix} --libdir=%{_libdir} --mandir=%{_mandir} --infodir=%{_infodir} \
	%{?with_sysroot} \
	--with-as=`which ppu-as` \
	--with-ld=`which ppu-ld` \
	--enable-threads --with-system-zlib --disable-checking \
	--enable-__cxa_atexit --disable-libunwind-exceptions \
	--enable-languages=c,c++ --disable-nls \
	--enable-clocale=gnu \
	--enable-version-specific-runtime-libs \
	--with-long-double-128 --program-prefix=ppu- \
	--disable-bootstrap \
%ifarch ppc64
	--host=ppu \
%endif
	--build=%{build_arch} \
	--target=ppu \
    --disable-libssp \
    --disable-multilib \
    --with-multiliib-list=m64 \
    --disable-libsanitizer
make -j1
popd


%install
rm -rf %{buildroot}
make -C obj-powerpc64-linux-gnu DESTDIR=%{buildroot} -j1 install

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

mkdir -p %{buildroot}%{_datadir}
cp -R gcc/testsuite %{buildroot}%{_datadir}/ppu-gcc-testsuite
install -m 755 contrib/test_installed %{buildroot}%{_datadir}/ppu-gcc-testsuite/
cat > %{buildroot}%{_bindir}/ppu-gcc-runtests << "EOF"
#!/bin/sh
%{_datadir}/ppu-gcc-testsuite/test_installed \
    --with-testsuite=%{_datadir}/ppu-gcc-testsuite \
    --with-gcc=%{_bindir}/ppu-gcc \
    --with-g++=%{_bindir}/ppu-g++ \
    --with-gfortran=%{_bindir}/ppu-gfortran \
    --without-objc \
%if %{with spu}
    --target spu-unknown-elf \
%endif
%if %{with ppu}
    --target_board unix/-m64
%else
    --target_board compile-only
%endif
EOF
chmod 755 %{buildroot}%{_bindir}/ppu-gcc-runtests

rm -rf %{buildroot}%{_infodir}
rm -rf %{buildroot}%{_mandir}/man7
rm -f %{buildroot}%{_libdir}/gcc/powerpc64-linux-gnu/%{version}/include-fixed/README
rm -f %{buildroot}%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libsupc++.la
rm -f %{buildroot}%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/mea64/libsupc++.la
rm -f %{buildroot}%{_datadir}/ppu-gcc-testsuite/ada/acats/run_all.sh


%check


%files -n ppu-gcc
%defattr(-,root,root)
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_mandir}
%dir %{_mandir}/man1
%{_prefix}/bin/ppu-cc
%{_prefix}/bin/ppu-c89
%{_prefix}/bin/ppu-c99
%{_prefix}/bin/ppu-gcc
%{_prefix}/bin/ppu-gcov
%{_prefix}/bin/ppu-cpp
%dir %{_prefix}/lib64
%dir %{_prefix}/lib64/gcc
%dir %{_prefix}/lib64/gcc/ppu
%dir %{_prefix}/lib64/gcc/ppu/%{version}
%dir %{_prefix}/lib64/gcc/ppu/%{version}/include
%{_prefix}/lib64/gcc/ppu/%{version}/include/stddef.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdarg.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/varargs.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/float.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdbool.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/iso646.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/unwind.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/vec_types.h
%{_prefix}/lib64/gcc/ppu/%{version}/*crt*.o
%{_prefix}/lib64/gcc/ppu/%{version}/libgcc.a
%{_prefix}/lib64/gcc/ppu/%{version}/libgcov.a
%{_prefix}/lib64/gcc/ppu/%{version}/libgcc_*.a
%{_prefix}/lib64/libcc1.so
%{_prefix}/lib64/libcc1.so.0
%{_prefix}/lib64/libcc1.so.0.0.0
%dir %{_prefix}/lib64/gcc/ppu/%{version}/plugin
%{_prefix}/lib64/gcc/ppu/%{version}/plugin/*
%{_mandir}/man1/ppu-gcc.1*
%{_mandir}/man1/ppu-gcov.1*
%{_mandir}/man1/ppu-cpp.1*
%dir %{_prefix}/libexec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/ppu
%dir %{_prefix}/libexec/gcc/ppu/%{version}
%{_prefix}/libexec/gcc/ppu/%{version}/cc1
%{_prefix}/libexec/gcc/ppu/%{version}/collect2
%{_prefix}/bin/ppu-gcc-ar
%{_prefix}/bin/ppu-gcc-nm
%{_prefix}/bin/ppu-gcc-ranlib
%{_prefix}/bin/ppu-gcov-dump
%{_prefix}/bin/ppu-gcov-tool
%{_prefix}/lib64/gcc/ppu/%{version}/include-fixed/limits.h
%{_prefix}/lib64/gcc/ppu/%{version}/include-fixed/syslimits.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/ppc-asm.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/altivec.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/si2vmx.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/spu2vmx.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/ppu_intrinsics.h
%{_prefix}/lib64/gcc/ppu/%{version}/include-fixed/README
%{_prefix}/lib64/gcc/ppu/%{version}/libgcc_s*
%{_prefix}/lib64/gcc/ppu/%{version}/include/amo.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/bmi2intrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/bmiintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/emmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/htmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/htmxlintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/mm_malloc.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/mmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/omp.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/openacc.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/pmmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/smmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/tmmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/xmmintrin.h
%{_prefix}/lib64/gcc/ppu/%{version}/libatomic.a
%{_prefix}/lib64/gcc/ppu/%{version}/libatomic.so
%{_prefix}/lib64/gcc/ppu/%{version}/libatomic.so.1
%{_prefix}/lib64/gcc/ppu/%{version}/libatomic.so.1.2.0
%{_prefix}/lib64/gcc/ppu/%{version}/libgomp.a
%{_prefix}/lib64/gcc/ppu/%{version}/libgomp.so
%{_prefix}/lib64/gcc/ppu/%{version}/libgomp.so.1
%{_prefix}/lib64/gcc/ppu/%{version}/libgomp.so.1.0.0
%{_prefix}/lib64/gcc/ppu/%{version}/libgomp.spec
%{_prefix}/lib64/gcc/ppu/%{version}/include/x86intrin.h
%{_prefix}/man/man1/ppu-gcov-dump.1
%{_prefix}/man/man1/ppu-gcov-tool.1
%{_prefix}/lib64/gcc/ppu/%{version}/include/gcov.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdalign.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdatomic.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdfix.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdint-gcc.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdint.h
%{_prefix}/lib64/gcc/ppu/%{version}/include/stdnoreturn.h
%{_prefix}/libexec/gcc/ppu/%{version}/liblto_plugin.so
%{_prefix}/libexec/gcc/ppu/%{version}/liblto_plugin.so.0
%{_prefix}/libexec/gcc/ppu/%{version}/liblto_plugin.so.0.0.0
%{_prefix}/libexec/gcc/ppu/%{version}/lto-wrapper
%{_prefix}/libexec/gcc/ppu/%{version}/lto1
%{_prefix}/libexec/gcc/ppu/%{version}/plugin/gengtype

%files -n ppu-gcc-c++
%defattr(-,root,root)
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_mandir}
%dir %{_mandir}/man1
%{_prefix}/bin/ppu-g++
%{_prefix}/bin/ppu-c++
%{_mandir}/man1/ppu-g++.1*
%dir %{_prefix}/libexec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/powerpc64-linux-gnu
%dir %{_prefix}/libexec/gcc/powerpc64-linux-gnu/%{version}
%{_prefix}/libexec/gcc/powerpc64-linux-gnu/%{version}/cc1plus
%dir %{_prefix}/lib
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/powerpc64-linux-gnu
%dir %{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}
%dir %{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/include
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/include/c++
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libsupc++.a
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libstdc++.a
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libstdc++.so*
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libitm.a
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libitm.so
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libitm.so.1
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libitm.so.1.0.0
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libitm.spec
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libstdc++fs.a
%{_prefix}/share/gcc-%{version}/python/libstdcxx/__init__.py
%{_prefix}/share/gcc-%{version}/python/libstdcxx/v6/__init__.py
%{_prefix}/share/gcc-%{version}/python/libstdcxx/v6/printers.py
%{_prefix}/share/gcc-%{version}/python/libstdcxx/v6/xmethods.py

%if 0
%files -n ppu-gcc-fortran
%defattr(-,root,root)
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_mandir}
%dir %{_mandir}/man1
%{_prefix}/bin/ppu-gfortran
%{_mandir}/man1/ppu-gfortran.1*
%dir %{_prefix}/libexec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/powerpc64-linux-gnu
%dir %{_prefix}/libexec/gcc/powerpc64-linux-gnu/%{version}
%{_prefix}/libexec/gcc/powerpc64-linux-gnu/%{version}/f951
%dir %{_prefix}/lib
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/powerpc64-linux-gnu
%dir %{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libgfortran.a
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/include/ISO_Fortran_binding.h
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libcaf_single.a
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libgfortran.spec
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/libgfortran.so*
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/finclude/ieee_arithmetic.mod
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/finclude/ieee_exceptions.mod
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/finclude/ieee_features.mod
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/finclude/omp_lib.f90
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/finclude/omp_lib.h
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/finclude/omp_lib.mod
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/finclude/omp_lib_kinds.mod
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/finclude/openacc.f90
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/finclude/openacc.mod
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/finclude/openacc_kinds.mod
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/finclude/openacc_lib.h

# gcc-gnat is currently broken
%if 0
%files -n ppu-gcc-gnat
%defattr(-,root,root)
%dir %{_prefix}
%dir %{_prefix}/bin
%{_prefix}/bin/ppu-gnatprep
%{_prefix}/bin/ppu-gnatchop
%{_prefix}/bin/ppu-gnatbind
%{_prefix}/bin/ppu-gnat
%{_prefix}/bin/ppu-gnatkr
%{_prefix}/bin/ppu-gnatls
%{_prefix}/bin/ppu-gnatclean
%{_prefix}/bin/ppu-gnatmake
%{_prefix}/bin/ppu-gnatname
%{_prefix}/bin/ppu-gnatfind
%{_prefix}/bin/ppu-gnatxref
%{_prefix}/bin/ppu-gnatlink
%dir %{_prefix}/lib
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/powerpc64-linux-gnu
%dir %{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/adalib/*
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/adainclude/*.ads
%{_prefix}/lib/gcc/powerpc64-linux-gnu/%{version}/adainclude/*.adb
%dir %{_prefix}/libexec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/powerpc64-linux-gnu
%dir %{_prefix}/libexec/gcc/powerpc64-linux-gnu/%{version}
%{_prefix}/libexec/gcc/powerpc64-linux-gnu/%{version}/gnat1
%endif

%files -n ppu-gcc-testsuite
%defattr(-,root,root)
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_prefix}/share
%{_prefix}/bin/ppu-gcc-runtests
%{_prefix}/share/ppu-gcc-testsuite
%endif


%changelog
* Sat Nov 7 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 9.5.0-1
- Initial build

