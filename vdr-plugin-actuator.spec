
%define plugin	actuator
%define name	vdr-plugin-%plugin
%define version	1.1.1
%define rel	6

Summary:	VDR plugin: Linear or h-h actuator control
Name:		%name
Version:	%version
Release:	%mkrel %rel
Group:		Video
License:	GPL
URL:		https://ventoso.org/luca/vdr/
Source:		http://ventoso.org/luca/vdr/vdr-%plugin-%version.tgz
Patch0:		actuator-linux-config.patch
Patch1:		actuator-format-string.patch
Patch2:		actuator-recent-kernels.patch
BuildRoot:	%{_tmppath}/%{name}-buildroot
BuildRequires:	vdr-devel >= 1.6.0
Requires:	vdr-abi = %vdr_abi
Requires:	kmod(actuator)

%description
With this plugin you can control a linear or an horizon to horizon actuator
controlled through the parallel port.
This kind of actuator usually needs a 36V supply (I drive mine at 12V to
reduce noise) and has a reed relay that gives pulses while the motor is
running. By counting the pulses you know the position of the actuator
(and the position of the dish).

%package -n dkms-%plugin
Summary:	Driver for an actuator connected to a parallel port
Group:		System/Kernel and hardware
Requires(pre):	dkms
Requires(preun): dkms
Requires:	dkms

%description -n dkms-%plugin
Driver for an actuator controlled thorough a parallel port. Use this
with the VDR actuator plugin.

%prep
%setup -q -n %plugin-%version
%patch0 -p1
%patch1 -p1
%patch2 -p1
mv module/README README.module
%vdr_plugin_prep

%build
%vdr_plugin_build

%install
rm -rf %{buildroot}
%vdr_plugin_install

install -d -m755 %{buildroot}%{_usrsrc}/%{plugin}-%{version}-%{release}
install -m644 module/actuator.c module/actuator.h module/Makefile %{buildroot}%{_usrsrc}/%{plugin}-%{version}-%{release}

cat > %{buildroot}%{_usrsrc}/%{plugin}-%{version}-%{release}/dkms.conf <<EOF
PACKAGE_NAME="%{plugin}"
PACKAGE_VERSION="%{version}-%{release}"
DEST_MODULE_LOCATION[0]="/kernel/drivers/char"
BUILT_MODULE_NAME[0]="actuator"
MAKE[0]="make -C \${kernel_source_dir} M=\\\$(pwd)"
AUTOINSTALL="yes"
EOF

%clean
rm -rf %{buildroot}

%post
%vdr_plugin_post %plugin

%postun
%vdr_plugin_postun %plugin

%post -n dkms-%{plugin}
dkms add     -m %{plugin} -v %{version}-%{release} --rpm_safe_upgrade &&
dkms build   -m %{plugin} -v %{version}-%{release} --rpm_safe_upgrade &&
dkms install -m %{plugin} -v %{version}-%{release} --rpm_safe_upgrade

%preun -n dkms-%{plugin}
dkms remove -m %{plugin} -v %{version}-%{release} --all --rpm_safe_upgrade

%files -f %plugin.vdr
%defattr(-,root,root)
%doc README README.module HISTORY patches module/*.png module/*.sch
%doc module/*.py module/printioctls.c

%files -n dkms-%plugin
%doc README.module
%{_usrsrc}/%{plugin}-%{version}-%{release}


