%undefine _hardened_build
%define optflags -O2
# Don't strip as the host binutils may be unable to handle SPU/PPU objects.
%define __os_install_post /usr/lib/rpm/brp-compress
%define _use_internal_dependency_generator 0

%define package_prefix spu

Name:           %{package_prefix}-gcc
Version:        9.5.0
Release:        1.CELL
Summary:        GNU Compiler Collection for Cell Broadband Engine SPU
License:        GPL
Group:          Cell Development Tools
Source0:        https://ftp.gnu.org/gnu/gcc/gcc-%{version}/gcc-%{version}.tar.xz
Source1:        https://sourceware.org/pub/newlib/newlib-2.5.0.tar.gz
Source2:        gcc-9.5.0-format-security-syntax-fix.patch
ExclusiveArch:  ppc64 x86_64

BuildRequires:  zlib-devel, gettext, dejagnu, bison, flex, texinfo, isl-devel
BuildRequires:  gcc, gcc-c++, binutils, cpp, gmp-devel, mpfr-devel, libmpc-devel
BuildRequires:  %{package_prefix}-binutils
Requires:       %{package_prefix}-binutils
Requires:       gmp, mpfr, libmpc, isl
AutoProv:       no
AutoReq:        no

%description 
The GNU Compiler Collection version %{version}.

# When building the cross-toolchain, reset prefix directory and use sysroot
%define _prefix /opt/cell/toolchain
%define _libdir %{_prefix}/lib
%define _mandir %{_prefix}/man
%define _infodir %{_prefix}/info

%package -n %{package_prefix}-gcc-c++
Summary:    C++ support for %{package_prefix}-gcc
Group:      Cell Development Tools
Requires:   %{package_prefix}-gcc = %{version}-%{release}
AutoProv:   no
AutoReq:    yes

%description -n %{package_prefix}-gcc-c++
GNU Compiler Collection C++ compiler for Cell Broadband Engine.


%prep
%setup -c -q
pushd gcc-%{version}
tar -xf %{SOURCE1} -C ../
ln -s ../newlib-2.5.0/newlib newlib
ln -s ../newlib-2.5.0/libgloss libgloss
patch -p1 < %{SOURCE2}
popd


%build
%define target_platform %{package_prefix}

rm -fr build
mkdir build
pushd build

CC="gcc -m64" CXX="g++ -m64" \
CFLAGS="-O2 -g" CXXFLAGS="-O2 -g" \
../gcc-%{version}/configure \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir} \
    --infodir=%{_infodir} \
	--disable-shared \
    --disable-threads \
    --disable-checking \
	--with-system-zlib \
    --with-newlib \
	--enable-languages=c,c++ \
    --disable-nls \
	--enable-version-specific-runtime-libs \
    --disable-libssp \
	--program-prefix=%{package_prefix}- \
	--disable-hosted-libstdcxx \
    --enable-cxx-flags='-fno-exceptions' \
    --build=`gcc -dumpmachine` \
    --host=`gcc -dumpmachine` \
	--target=%{target_platform} \
    --with-gmp=/usr \
    --with-mpfr=/usr \
    --with-mpc=/usr \
    --with-isl=/usr \
    --with-as=/opt/cell/toolchain/bin/spu-as \
    --with-ar=/opt/cell/toolchain/bin/spu-ar \
    --with-ld=/opt/cell/toolchain/bin/spu-ld \
    --with-nm=/opt/cell/toolchain/bin/spu-nm \
    --with-ranlib=/opt/cell/toolchain/bin/spu-ranlib \
    --disable-werror \
    --enable-obsolete
popd
make -C build %{?_smp_mflags}


%install
rm -fr %{buildroot}
make -C build DESTDIR=%{buildroot} install

ln -sf %{package_prefix}-gcc $RPM_BUILD_ROOT%{_prefix}/bin/%{package_prefix}-cc
rm -f $RPM_BUILD_ROOT%{_prefix}/bin/vxaddr2line
rm -f $RPM_BUILD_ROOT%{_prefix}/bin/%{target_platform}-%{package_prefix}-*
rm -f $RPM_BUILD_ROOT%{_prefix}/bin/%{package_prefix}-gcc-%{version}
rm -f $RPM_BUILD_ROOT%{_prefix}/bin/%{package_prefix}-gccbug
rm -f $RPM_BUILD_ROOT%{_prefix}/lib*/libiberty.a
rm -f $RPM_BUILD_ROOT%{_prefix}/lib*/*/libiberty.a
rm -f $RPM_BUILD_ROOT%{_prefix}/%{target_platform}/lib*/libiberty.a
rm -f $RPM_BUILD_ROOT%{_prefix}/%{target_platform}/lib*/*/libiberty.a
rm -rf $RPM_BUILD_ROOT%{_prefix}/lib/gcc/%{target_platform}/%{version}/install-tools
rm -rf $RPM_BUILD_ROOT%{_prefix}/libexec/gcc/%{target_platform}/%{version}/install-tools
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/gcc/%{target_platform}/%{version}/*.la
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/gcc/%{target_platform}/%{version}/*/*.la
rm -f %{buildroot}%{_prefix}/libexec/gcc/%{target_platform}/%{version}/liblto_plugin.la
rm -f %{buildroot}%{_prefix}/lib64/libcc1.la

for h in \
  `find $RPM_BUILD_ROOT%{_prefix}/lib/gcc/%{target_platform}/%{version}/include -name \*.h`
do
  if grep -q 'It has been auto-edited by fixincludes from' $h; then
    rh=`grep -A2 'It has been auto-edited by fixincludes from' $h | tail -1 | sed 's|^.*"\(.*\)".*$|\1|'`
    diff -up $rh $h || :
    rm -f $h
  fi
done

cat > $RPM_BUILD_ROOT%{_prefix}/bin/%{package_prefix}-c89 <<"EOF"
#!/bin/sh
fl="-std=c89"
for opt; do
  case "$opt" in
    -ansi|-std=c89|-std=iso9899:1990) fl="";;
    -std=*) echo "`basename $0` called with non ANSI/ISO C option $opt" >&2
	    exit 1;;
  esac
done
exec %{_prefix}/bin/%{package_prefix}-gcc $fl ${1+"$@"}
EOF
cat > $RPM_BUILD_ROOT%{_prefix}/bin/%{package_prefix}-c99 <<"EOF"
#!/bin/sh
fl="-std=c99"
for opt; do
  case "$opt" in
    -std=c99|-std=iso9899:1999) fl="";;
    -std=*) echo "`basename $0` called with non ISO C99 option $opt" >&2
	    exit 1;;
  esac
done
exec %{_prefix}/bin/%{package_prefix}-gcc $fl ${1+"$@"}
EOF
chmod 755 $RPM_BUILD_ROOT%{_prefix}/bin/%{package_prefix}-c?9

rm -rf $RPM_BUILD_ROOT%{_infodir}
rm -rf $RPM_BUILD_ROOT%{_mandir}/man7
rm -f %{buildroot}%{_prefix}/bin/spu-gcc-{ar,nm,ranlib}
rm -f %{buildroot}%{_prefix}/bin/spu-gcov-{dump,tool}


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
%{_mandir}/man1/%{package_prefix}-gcc.1*
%{_mandir}/man1/%{package_prefix}-gcov.1*
%{_mandir}/man1/%{package_prefix}-cpp.1*
%{_mandir}/man1/%{target_platform}-gcov-dump.1
%{_mandir}/man1/%{target_platform}-gcov-tool.1
%{_prefix}/lib64/libcc1.so
%{_prefix}/lib64/libcc1.so.0
%{_prefix}/lib64/libcc1.so.0.0.0
%dir %{_prefix}/libexec
%dir %{_prefix}/libexec/gcc
%dir %{_prefix}/libexec/gcc/%{target_platform}
%dir %{_prefix}/libexec/gcc/%{target_platform}/%{version}
%{_prefix}/libexec/gcc/%{target_platform}/%{version}/cc1
%{_prefix}/libexec/gcc/%{target_platform}/%{version}/collect2
%{_prefix}/libexec/gcc/%{target_platform}/%{version}/liblto_plugin.so
%{_prefix}/libexec/gcc/%{target_platform}/%{version}/liblto_plugin.so.0
%{_prefix}/libexec/gcc/%{target_platform}/%{version}/liblto_plugin.so.0.0.0
%{_prefix}/libexec/gcc/%{target_platform}/%{version}/lto-wrapper
%{_prefix}/libexec/gcc/%{target_platform}/%{version}/lto1
%{_prefix}/libexec/gcc/%{target_platform}/%{version}/plugin/gengtype
%dir %{_prefix}/lib
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{target_platform}
%dir %{_prefix}/lib/gcc/%{target_platform}/%{version}
%dir %{_prefix}/lib/gcc/%{target_platform}/%{version}/include
%{_prefix}/lib/gcc/%{target_platform}/%{version}/include/*
%{_prefix}/lib/gcc/%{target_platform}/%{version}/include-fixed/README
%{_prefix}/lib/gcc/%{target_platform}/%{version}/include-fixed/limits.h
%{_prefix}/lib/gcc/%{target_platform}/%{version}/include-fixed/syslimits.h
%dir %{_prefix}/lib/gcc/%{target_platform}/%{version}/plugin
%{_prefix}/lib/gcc/%{target_platform}/%{version}/plugin/*
%{_prefix}/lib/gcc/%{target_platform}/%{version}/*crt*.o
%{_prefix}/lib/gcc/%{target_platform}/%{version}/libgcc.a
%{_prefix}/lib/gcc/%{target_platform}/%{version}/libgcov.a
%{_prefix}/lib/gcc/%{target_platform}/%{version}/libgcc_*.a
%dir %{_prefix}/lib/gcc/%{target_platform}/%{version}/mea64
%{_prefix}/lib/gcc/%{target_platform}/%{version}/mea64/*crt*.o
%{_prefix}/lib/gcc/%{target_platform}/%{version}/mea64/libgcc.a
%{_prefix}/lib/gcc/%{target_platform}/%{version}/mea64/libgcov.a
%{_prefix}/lib/gcc/%{target_platform}/%{version}/mea64/libgcc_*.a
%{_prefix}/%{target_platform}/lib/crt1.o
%{_prefix}/%{target_platform}/lib/crt2.o
%{_prefix}/%{target_platform}/lib/crti.o
%{_prefix}/%{target_platform}/lib/crtn.o
%{_prefix}/%{target_platform}/lib/gcrt1.o
%{_prefix}/%{target_platform}/lib/gcrt2.o
%{_prefix}/%{target_platform}/lib/libc.a
%{_prefix}/%{target_platform}/lib/libg.a
%{_prefix}/%{target_platform}/lib/libgloss.a
%{_prefix}/%{target_platform}/lib/libm.a
%{_prefix}/%{target_platform}/lib/mea64/crt1.o
%{_prefix}/%{target_platform}/lib/mea64/crt2.o
%{_prefix}/%{target_platform}/lib/mea64/crti.o
%{_prefix}/%{target_platform}/lib/mea64/crtn.o
%{_prefix}/%{target_platform}/lib/mea64/gcrt1.o
%{_prefix}/%{target_platform}/lib/mea64/gcrt2.o
%{_prefix}/%{target_platform}/lib/mea64/libc.a
%{_prefix}/%{target_platform}/lib/mea64/libg.a
%{_prefix}/%{target_platform}/lib/mea64/libgloss.a
%{_prefix}/%{target_platform}/lib/mea64/libm.a
%dir %{_prefix}/%{target_platform}/include
%{_prefix}/%{target_platform}/include/*


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
%dir %{_prefix}/libexec/gcc/%{target_platform}
%dir %{_prefix}/libexec/gcc/%{target_platform}/%{version}
%{_prefix}/libexec/gcc/%{target_platform}/%{version}/cc1plus
%dir %{_prefix}/lib
%dir %{_prefix}/lib/gcc
%dir %{_prefix}/lib/gcc/%{target_platform}
%dir %{_prefix}/lib/gcc/%{target_platform}/%{version}
%dir %{_prefix}/lib/gcc/%{target_platform}/%{version}/include
%{_prefix}/lib/gcc/%{target_platform}/%{version}/include/c++
%{_prefix}/lib/gcc/%{target_platform}/%{version}/libsupc++.a
%dir %{_prefix}/lib/gcc/%{target_platform}/%{version}/mea64
%{_prefix}/lib/gcc/%{target_platform}/%{version}/mea64/libsupc++.a


%changelog
* Sun Oct 18 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 9.5.0-1
- Initial build - https://ps3linux.net

