%define debug_package %%{nil}
%define _build_id_links none
%define optflags %{nil}
%undefine _fortify_level
# Don't strip as the host binutils may be unable to handle SPU/PPU objects.
%define __os_install_post /usr/lib/rpm/brp-compress
# Don't check rpaths
%define __arch_install_post /usr/lib/rpm/check-buildroot

%define package_prefix ppu
%define target powerpc64-linux-gnu

Name:           %{package_prefix}-gcc
Version:        9.5.0
Release:        1%{dist}
Summary:        GNU Compiler Collection for Cell Broadband Engine PPU
License:        GPL
Group:          Cell Development Tools
Source0:        https://ftp.gnu.org/gnu/gcc/gcc-%{version}/gcc-%{version}.tar.xz
Patch1:         gcc-9.5.0-add-ppu-target.patch
ExclusiveArch:  x86_64

BuildRequires:  zlib-devel, gettext, dejagnu, bison, flex, texinfo
BuildRequires:  gmp-devel, mpfr-devel, libmpc-devel, isl-devel
BuildRequires:  ppu-binutils, ppu-sysroot, gcc, gcc-c++, cpp
BuildRequires:  %{package_prefix}-binutils
Requires:       %{package_prefix}-binutils
Requires:       gmp, mpfr, libmpc, isl
BuildRequires:  ppu-sysroot
Requires:       ppu-sysroot
AutoProv:       no
AutoReq:        no

%description 
The GNU Compiler Collection version %{version}.

%package -n %{package_prefix}-gcc-c++
Summary:    C++ support for %{package_prefix}-gcc
Group:      Cell Development Tools
Requires:   %{package_prefix}-gcc = %{version}-%{release}
AutoProv:   no
AutoReq:    yes

%description -n %{package_prefix}-gcc-c++
GNU Compiler Collection C++ compiler for Cell Broadband Engine.

%package -n %{package_prefix}-gcc-fortran
Summary:    Fortran support for %{package_prefix}-gcc
Group:      Cell Development Tools
Requires:   %{package_prefix}-gcc = %{version}-%{release}
AutoProv:   no
AutoReq:    yes

%description -n %{package_prefix}-gcc-fortran
GNU Compiler Collection Fortran compiler for Cell Broadband Engine.

%package -n %{package_prefix}-gcc-testsuite
Summary:    DejaGnu testsuite for %{package_prefix}-gcc
Group:      Cell Development Tools
Requires:   %{package_prefix}-gcc = %{version}-%{release}
Requires:   dejagnu
AutoProv:   no
AutoReq:    no

%description -n %{package_prefix}-gcc-testsuite
Testsuite driver for the Cell Broadband Engine version of GCC.

# gcc-gnat broke compatibility with itsself; modern gcc-gnat can't bootstrap older releases... Lovely.
%if 0
%package -n %{package_prefix}-gcc-gnat
Summary:        Ada support for PPU compiler
Group:          Cell Development Tools
Requires:       %{package_prefix}-gcc = %{version}-%{release}
# ppu-gnat version will not compile
# Fedora 44's gcc-gnat is too new; it will not bootstrap our build
%if 0
BuildRequires:  %{package_prefix}-gcc-gnat
#%%else
BuildRequires:  gcc-gnat
%endif
AutoProv:       no
AutoReq:        no

%description -n %{package_prefix}-gcc-gnat
GNU Compiler Collection Ada compiler for Cell Broadband Engine.
%endif


%prep
%setup -q -n gcc-%{version}
patch -p1 < %{PATCH1}


%build
%define _prefix /opt/cell/toolchain
%define _libdir %{_prefix}/lib64
%define _mandir %{_prefix}/man
%define _infodir %{_prefix}/info
%define with_sysroot --with-sysroot=/opt/cell/sysroot
# No need for these ppu- wrappers for the gcc gnat programs; we cannot build the compiler
%if 0
%ifarch ppc64
rm -rf build-tools
mkdir build-tools
for I in gnat gnatbind gnatmake gnatlink gnatchop gnatls
do
  cat > build-tools/ppu-$I <<EOF
#!/bin/sh
exec $I \${1+"\$@"}
EOF
  chmod 755 build-tools/ppu-$I
done
# If ppu-gcc is not in PATH, preappend "build-tools" directory to PATH
if type -p ppu-gnat &> /dev/null; then
  export PATH=$(pwd)/build-tools:$PATH
fi
%endif
%endif

rm -rf obj-%{target}
mkdir -p obj-%{target}
pushd obj-%{target}

unset CC CXX CFLAGS CXXFLAGS FCFLAGS FFLAGS LDFLAGS
unset CFLAGS_FOR_TARGET CXXFLAGS_FOR_TARGET FCFLAGS_FOR_TARGET FFLAGS_FOR_TARGET
../configure \
    --build=$(gcc -dumpmachine) \
    --host=$(gcc -dumpmachine) \
	--target=%{target} \
    --prefix=%{_prefix} \
	%{?with_sysroot} \
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
    --program-prefix=%{package_prefix}- \
	--disable-bootstrap \
    --disable-libssp \
    --disable-multilib \
    --disable-libsanitizer \
    --with-multilib-list=m64
popd
make  -C obj-%{target} %{?_smp_mflags}


%install
rm -rf %{buildroot}
make -C obj-%{target} DESTDIR=%{buildroot} -j1 install

ln -sf %{package_prefix}-gcc %{buildroot}%{_prefix}/bin/%{package_prefix}-cc
rm -f %{buildroot}%{_prefix}/bin/vxaddr2line
rm -f %{buildroot}%{_prefix}/bin/%{target}-%{package_prefix}-*
rm -f %{buildroot}%{_prefix}/bin/%{package_prefix}-gcc-%{version}
rm -f %{buildroot}%{_prefix}/bin/%{package_prefix}-gccbug
rm -f %{buildroot}%{_prefix}/lib*/libiberty.a
rm -f %{buildroot}%{_prefix}/lib*/*/libiberty.a
rm -f %{buildroot}%{_prefix}/%{target}/lib*/libiberty.a
rm -f %{buildroot}%{_prefix}/%{target}/lib*/*/libiberty.a
rm -rf %{buildroot}%{_prefix}/lib/gcc/%{target}/%{version}/install-tools
rm -rf %{buildroot}%{_prefix}/libexec/gcc/%{target}/%{version}/install-tools
rm -f %{buildroot}%{_prefix}/lib/gcc/%{target}/%{version}/*.la
rm -f %{buildroot}%{_prefix}/lib/gcc/%{target}/%{version}/*/*.la
rm -f %{buildroot}%{_prefix}/libexec/gcc/%{target}/%{version}/liblto_plugin.la
rm -f %{buildroot}%{_prefix}/lib/gcc/%{target}/%{version}/libgfortran.la
rm -f %{buildroot}%{_prefix}/lib/gcc/%{target}/%{version}/mea64/libcaf_single.la
rm -f %{buildroot}%{_prefix}/lib/gcc/%{target}/%{version}/mea64/libgfortran.la
rm -f %{buildroot}%{_prefix}/lib64/libcc1.la
mv %{buildroot}%{_prefix}/lib/gcc/%{target}/lib64/* %{buildroot}%{_prefix}/lib/gcc/%{target}/%{version}/
rm -rf %{buildroot}%{_prefix}/lib/gcc/%{target}/lib
rm -rf %{buildroot}%{_prefix}/lib/gcc/%{target}/lib64

for h in \
  `find %{buildroot}%{_libdir}/gcc/%{target}/%{version}/include -name \*.h`
do
  if grep -q 'It has been auto-edited by fixincludes from' $h; then
    rh=`grep -A2 'It has been auto-edited by fixincludes from' $h | tail -1 | sed 's|^.*"\(.*\)".*$|\1|'`
    diff -up $rh $h || :
    rm -f $h
  fi
done

cat > %{buildroot}%{_bindir}/%{package_prefix}-c89 <<"EOF"
#!/bin/sh
fl="-std=c89"
for opt; do
  case "$opt" in
    -ansi|-std=c89|-std=iso9899:1990) fl="";;
    -std=*) echo "`basename $0` called with non ANSI/ISO C option $opt" >&2
	    exit 1;;
  esac
done
exec %{_bindir}/%{package_prefix}-gcc $fl ${1+"$@"}
EOF
cat > %{buildroot}%{_bindir}/%{package_prefix}-c99 <<"EOF"
#!/bin/sh
fl="-std=c99"
for opt; do
  case "$opt" in
    -std=c99|-std=iso9899:1999) fl="";;
    -std=*) echo "`basename $0` called with non ISO C99 option $opt" >&2
	    exit 1;;
  esac
done
exec %{_bindir}/%{package_prefix}-gcc $fl ${1+"$@"}
EOF
chmod 755 %{buildroot}%{_bindir}/%{package_prefix}-c?9

mkdir -p %{buildroot}%{_datadir}
cp -R gcc/testsuite %{buildroot}%{_datadir}/%{package_prefix}-gcc-testsuite
install -m 755 contrib/test_installed %{buildroot}%{_datadir}/%{package_prefix}-gcc-testsuite/
cat > %{buildroot}%{_bindir}/%{package_prefix}-gcc-runtests << "EOF"
#!/bin/sh
%{_datadir}/%{package_prefix}-gcc-testsuite/test_installed \
    --with-testsuite=%{_datadir}/%{package_prefix}-gcc-testsuite \
    --with-gcc=%{_bindir}/%{package_prefix}-gcc \
    --with-g++=%{_bindir}/%{package_prefix}-g++ \
    --with-gfortran=%{_bindir}/%{package_prefix}-gfortran \
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
chmod 755 %{buildroot}%{_bindir}/%{package_prefix}-gcc-runtests

rm -rf %{buildroot}%{_infodir}
rm -rf %{buildroot}%{_mandir}/man7
rm -f %{buildroot}%{_libdir}/gcc/%{target}/%{version}/include-fixed/README
rm -f %{buildroot}%{_prefix}/lib/gcc/%{target}/%{version}/libsupc++.la
rm -f %{buildroot}%{_prefix}/lib/gcc/%{target}/%{version}/mea64/libsupc++.la
rm -f %{buildroot}%{_datadir}/%{package_prefix}-gcc-testsuite/ada/acats/run_all.sh


%check


%files -n %{package_prefix}-gcc
%defattr(-,root,root)
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_mandir}
%dir %{_mandir}/man1
%{_prefix}/bin/%{package_prefix}-cc
%{_prefix}/bin/%{package_prefix}-c89
%{_prefix}/bin/%{package_prefix}-c99
%{_prefix}/bin/%{package_prefix}-gcc
%{_prefix}/bin/%{package_prefix}-gcov
%{_prefix}/bin/%{package_prefix}-cpp
%dir %{_prefix}/lib
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{target}
%dir %{_prefix}/lib/gcc/%{target}/%{version}
%dir %{_prefix}/lib/gcc/%{target}/%{version}/include
%{_prefix}/lib/gcc/%{target}/%{version}/include/stddef.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/stdarg.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/varargs.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/float.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/stdbool.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/iso646.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/unwind.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/vec_types.h
%{_prefix}/lib/gcc/%{target}/%{version}/*crt*.o
%{_prefix}/lib/gcc/%{target}/%{version}/libgcc.a
%{_prefix}/lib/gcc/%{target}/%{version}/libgcov.a
%{_prefix}/lib/gcc/%{target}/%{version}/libgcc_*.a
%{_prefix}/lib64/libcc1.so
%{_prefix}/lib64/libcc1.so.0
%{_prefix}/lib64/libcc1.so.0.0.0
%dir %{_prefix}/lib/gcc/%{target}/%{version}/plugin
%{_prefix}/lib/gcc/%{target}/%{version}/plugin/*
%{_mandir}/man1/%{package_prefix}-gcc.1*
%{_mandir}/man1/%{package_prefix}-gcov.1*
%{_mandir}/man1/%{package_prefix}-cpp.1*
%dir %{_prefix}/libexec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{target}
%dir %{_prefix}/libexec/gcc/%{target}/%{version}
%{_prefix}/libexec/gcc/%{target}/%{version}/cc1
%{_prefix}/libexec/gcc/%{target}/%{version}/collect2
%{_prefix}/bin/%{package_prefix}-gcc-ar
%{_prefix}/bin/%{package_prefix}-gcc-nm
%{_prefix}/bin/%{package_prefix}-gcc-ranlib
%{_prefix}/bin/%{package_prefix}-gcov-dump
%{_prefix}/bin/%{package_prefix}-gcov-tool
%{_prefix}/lib/gcc/%{target}/%{version}/include-fixed/limits.h
%{_prefix}/lib/gcc/%{target}/%{version}/include-fixed/syslimits.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/ppc-asm.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/altivec.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/si2vmx.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/spu2vmx.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/ppu_intrinsics.h
%{_prefix}/lib/gcc/%{target}/%{version}/include-fixed/README
%{_prefix}/lib/gcc/%{target}/%{version}/libgcc_s*
%{_prefix}/lib/gcc/%{target}/%{version}/include-fixed/pthread.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/amo.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/bmi2intrin.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/bmiintrin.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/emmintrin.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/htmintrin.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/htmxlintrin.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/mm_malloc.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/mmintrin.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/omp.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/openacc.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/pmmintrin.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/smmintrin.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/tmmintrin.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/xmmintrin.h
%{_prefix}/lib/gcc/%{target}/%{version}/libatomic.a
%{_prefix}/lib/gcc/%{target}/%{version}/libatomic.so
%{_prefix}/lib/gcc/%{target}/%{version}/libatomic.so.1
%{_prefix}/lib/gcc/%{target}/%{version}/libatomic.so.1.2.0
%{_prefix}/lib/gcc/%{target}/%{version}/libgomp.a
%{_prefix}/lib/gcc/%{target}/%{version}/libgomp.so
%{_prefix}/lib/gcc/%{target}/%{version}/libgomp.so.1
%{_prefix}/lib/gcc/%{target}/%{version}/libgomp.so.1.0.0
%{_prefix}/lib/gcc/%{target}/%{version}/libgomp.spec
%{_prefix}/lib/gcc/%{target}/%{version}/include/x86intrin.h
%{_prefix}/man/man1/ppu-gcov-dump.1
%{_prefix}/man/man1/ppu-gcov-tool.1
%{_prefix}/lib/gcc/%{target}/%{version}/include/gcov.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/stdalign.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/stdatomic.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/stdfix.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/stdint-gcc.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/stdint.h
%{_prefix}/lib/gcc/%{target}/%{version}/include/stdnoreturn.h
%{_prefix}/libexec/gcc/%{target}/%{version}/liblto_plugin.so
%{_prefix}/libexec/gcc/%{target}/%{version}/liblto_plugin.so.0
%{_prefix}/libexec/gcc/%{target}/%{version}/liblto_plugin.so.0.0.0
%{_prefix}/libexec/gcc/%{target}/%{version}/lto-wrapper
%{_prefix}/libexec/gcc/%{target}/%{version}/lto1
%{_prefix}/libexec/gcc/%{target}/%{version}/plugin/gengtype

%files -n %{package_prefix}-gcc-c++
%defattr(-,root,root)
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_mandir}
%dir %{_mandir}/man1
%{_prefix}/bin/%{package_prefix}-g++
%{_prefix}/bin/%{package_prefix}-c++
%{_mandir}/man1/%{package_prefix}-g++.1*
%dir %{_prefix}/libexec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{target}
%dir %{_prefix}/libexec/gcc/%{target}/%{version}
%{_prefix}/libexec/gcc/%{target}/%{version}/cc1plus
%dir %{_prefix}/lib
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{target}
%dir %{_prefix}/lib/gcc/%{target}/%{version}
%dir %{_prefix}/lib/gcc/%{target}/%{version}/include
%{_prefix}/lib/gcc/%{target}/%{version}/include/c++
%{_prefix}/lib/gcc/%{target}/%{version}/libsupc++.a
%{_prefix}/lib/gcc/%{target}/%{version}/libstdc++.a
%{_prefix}/lib/gcc/%{target}/%{version}/libstdc++.so*
%{_prefix}/lib/gcc/%{target}/%{version}/libitm.a
%{_prefix}/lib/gcc/%{target}/%{version}/libitm.so
%{_prefix}/lib/gcc/%{target}/%{version}/libitm.so.1
%{_prefix}/lib/gcc/%{target}/%{version}/libitm.so.1.0.0
%{_prefix}/lib/gcc/%{target}/%{version}/libitm.spec
%{_prefix}/lib/gcc/%{target}/%{version}/libstdc++fs.a
%{_prefix}/share/gcc-%{version}/python/libstdcxx/__init__.py
%{_prefix}/share/gcc-%{version}/python/libstdcxx/v6/__init__.py
%{_prefix}/share/gcc-%{version}/python/libstdcxx/v6/printers.py
%{_prefix}/share/gcc-%{version}/python/libstdcxx/v6/xmethods.py

%files -n %{package_prefix}-gcc-fortran
%defattr(-,root,root)
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_mandir}
%dir %{_mandir}/man1
%{_prefix}/bin/%{package_prefix}-gfortran
%{_mandir}/man1/%{package_prefix}-gfortran.1*
%dir %{_prefix}/libexec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{target}
%dir %{_prefix}/libexec/gcc/%{target}/%{version}
%{_prefix}/libexec/gcc/%{target}/%{version}/f951
%dir %{_prefix}/lib
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{target}
%dir %{_prefix}/lib/gcc/%{target}/%{version}
%{_prefix}/lib/gcc/%{target}/%{version}/libgfortran.a
%{_prefix}/lib/gcc/%{target}/%{version}/include/ISO_Fortran_binding.h
%{_prefix}/lib/gcc/%{target}/%{version}/libcaf_single.a
%{_prefix}/lib/gcc/%{target}/%{version}/libgfortran.spec
%{_prefix}/lib/gcc/%{target}/%{version}/libgfortran.so*
%{_prefix}/lib/gcc/%{target}/%{version}/finclude/ieee_arithmetic.mod
%{_prefix}/lib/gcc/%{target}/%{version}/finclude/ieee_exceptions.mod
%{_prefix}/lib/gcc/%{target}/%{version}/finclude/ieee_features.mod
%{_prefix}/lib/gcc/%{target}/%{version}/finclude/omp_lib.f90
%{_prefix}/lib/gcc/%{target}/%{version}/finclude/omp_lib.h
%{_prefix}/lib/gcc/%{target}/%{version}/finclude/omp_lib.mod
%{_prefix}/lib/gcc/%{target}/%{version}/finclude/omp_lib_kinds.mod
%{_prefix}/lib/gcc/%{target}/%{version}/finclude/openacc.f90
%{_prefix}/lib/gcc/%{target}/%{version}/finclude/openacc.mod
%{_prefix}/lib/gcc/%{target}/%{version}/finclude/openacc_kinds.mod
%{_prefix}/lib/gcc/%{target}/%{version}/finclude/openacc_lib.h

# gcc-gnat is currently broken
%if 0
%files -n %{package_prefix}-gcc-gnat
%defattr(-,root,root)
%dir %{_prefix}
%dir %{_prefix}/bin
%{_prefix}/bin/%{package_prefix}-gnatprep
%{_prefix}/bin/%{package_prefix}-gnatchop
%{_prefix}/bin/%{package_prefix}-gnatbind
%{_prefix}/bin/%{package_prefix}-gnat
%{_prefix}/bin/%{package_prefix}-gnatkr
%{_prefix}/bin/%{package_prefix}-gnatls
%{_prefix}/bin/%{package_prefix}-gnatclean
%{_prefix}/bin/%{package_prefix}-gnatmake
%{_prefix}/bin/%{package_prefix}-gnatname
%{_prefix}/bin/%{package_prefix}-gnatfind
%{_prefix}/bin/%{package_prefix}-gnatxref
%{_prefix}/bin/%{package_prefix}-gnatlink
%dir %{_prefix}/lib
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{target}
%dir %{_prefix}/lib/gcc/%{target}/%{version}
%{_prefix}/lib/gcc/%{target}/%{version}/adalib/*
%{_prefix}/lib/gcc/%{target}/%{version}/adainclude/*.ads
%{_prefix}/lib/gcc/%{target}/%{version}/adainclude/*.adb
%dir %{_prefix}/libexec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{target}
%dir %{_prefix}/libexec/gcc/%{target}/%{version}
%{_prefix}/libexec/gcc/%{target}/%{version}/gnat1
%endif

%files -n %{package_prefix}-gcc-testsuite
%defattr(-,root,root)
%dir %{_prefix}
%dir %{_prefix}/bin
%dir %{_prefix}/share
%{_prefix}/bin/%{package_prefix}-gcc-runtests
%{_prefix}/share/%{package_prefix}-gcc-testsuite


%changelog
* Sat Oct 17 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 9.5.0-1
- Initial build for PS3LINUX on the Cell/B.E. https://ps3linux.net

