%global _libdir %{_prefix}/lib64/tcltk

Name:           compat-tk8.5
Version:        8.5.19
Release:        1%{?dist}
Summary:        Compatibility Tk 8.5 runtime library
License:        TCL
URL:            https://sourceforge.net/projects/tktoolkit/
Source0:        https://prdownloads.sourceforge.net/tcl/tk%{version}-src.tar.gz
Patch1:         tk8.5.19-remove-strrchr-declaration.patch
ExclusiveArch:  x86_64

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  zlib-devel
BuildRequires:  compat-tcl8.5
Requires:       compat-tcl8.5

%description
This package provides the shared Tk 8.5 runtime library (libtk8.5.so) for
binaries that were linked against Tk 8.5.

It is a runtime-only compatibility package: it ships no wish, no headers, no
man pages and no development files, and everything lives under %{_libdir}
so it can be installed alongside the current Tk package.


%prep
%setup -q -n tk%{version}
%patch 1 -p1


%build
cd unix
CC="gcc -m64" \
CFLAGS="-O2 -g -mcpu=x86_64 -mtune=generic -std=gnu89 -D_GNU_SOURCE -I/usr/lib64/tcltk/include" \
LDFLAGS=-L/usr/lib64/tcltk \
./configure  \
    --libdir=%{_libdir} \
    --enable-threads \
    --enable-shared \
    --enable-64bit \
    --with-tcl=/usr/lib64/tcltk \
    --with-x
make -j1 CC="gcc -m64" CFLAGS="-O2 -g -mcpu=x86_64 -mtune=generic -std=gnu89 -D_GNU_SOURCE -I/usr/lib64/tcltk/include" LDFLAGS=-L/usr/lib64/tcltk


%install
rm -rf %{buildroot}
cd unix
make INSTALL_ROOT=%{buildroot} -j1 install

# Keep this a runtime-only compat package: drop everything that would
# conflict with, or duplicate, the current tcl/tcl-devel packages.
rm -rf %{buildroot}%{_bindir}
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/pkgconfig
rm -f %{buildroot}%{_libdir}/libtkstub8.5.a
rm -rf %{buildroot}%{_libdir}/tk8.5
rm -f %{buildroot}%{_libdir}/tkConfig.sh
rm -rf %{buildroot}%{_prefix}/lib
rm -rf %{buildroot}%{_prefix}/man

# Make the dynamic linker find libtcl8.5.so in the non-standard directory
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf


%check


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%license license.terms
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf
%dir %{_libdir}
%{_libdir}/*


%changelog
* Tue Nov 10 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 8.5.19-1
- Initial compat-tk8.5 package built from tk8.5.19-src.tar.gz
- Installs libraries in /usr/lib64/tcltk
- Adds /etc/ld.so.conf.d/compat-tk8.5-x86_64.conf

