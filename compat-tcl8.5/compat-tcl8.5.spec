%global _libdir %{_prefix}/lib64/tcltk
%global _includedir %{_prefix}/lib64/tcltk/include

Name:           compat-tcl8.5
Version:        8.5.19
Release:        1%{?dist}
Summary:        Compatibility Tcl 8.5 runtime library
License:        TCL
URL:            http://tcl.sourceforge.net/
Source0:        https://downloads.sourceforge.net/tcl/tcl%{version}-src.tar.gz
ExclusiveArch:  x86_64

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  zlib-devel

%description
This package provides the shared Tcl 8.5 runtime library (libtcl8.5.so) and
its script library for binaries that were linked against Tcl 8.5.

It is a runtime-only compatibility package: it ships no tclsh, no man
pages and no development files, and everything lives under %{_libdir}
so it can be installed alongside the current tcl package.


%prep
%setup -q -n tcl%{version}


%build
cd unix
CC="gcc -m64" \
CFLAGS="-O2 -g -mcpu=x86_64 -mtune=generic -std=gnu89 -D_GNU_SOURCE" \
LDFLAGS= \
./configure  \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --includedir=%{_includedir} \
    --enable-threads \
    --enable-shared \
    --enable-64bit
make -j1 CFLAGS="-O2 -g -mcpu=x86_64 -mtune=generic -std=gnu89 -D_GNU_SOURCE"


%check


%install
rm -rf %{buildroot}
cd unix
make INSTALL_ROOT=%{buildroot} -j1 install install-private-headers

rm -rf %{buildroot}%{_bindir}
rm -rf %{buildroot}%{_prefix}/man
rm -rf %{buildroot}%{_prefix}/lib
rm -rf %{buildroot}%{_libdir}/pkgconfig
rm -f  %{buildroot}%{_libdir}/libtclstub8.5.a

mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%license license.terms
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf
%dir %{_libdir}
%{_libdir}/*


%changelog
* Tue Nov 10 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 8.5.19-1
- Initial compat-tcl8.5 package built from tcl8.5.19-src.tar.gz
- Installs libraries in /usr/lib64/tcltk
- Adds /etc/ld.so.conf.d/compat-tcl8.5-x86_64.conf

