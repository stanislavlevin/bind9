Name: bind
Version: 8.3.1
Release: alt1

Summary: A DNS (Domain Name System) server
License: distributable
Group: System/Servers
Url: http://www.isc.org/%name.html

Source0: ftp://ftp.isc.org/isc/%name/src/%version/%name-src.tar.bz2
Source1: ftp://ftp.isc.org/isc/%name/src/%version/%name-doc.tar.bz2
Source2: ftp://ftp.isc.org/isc/%name/src/%version/%name-contrib.tar.bz2
Source3: named.init
Source4: %name.chroot.lib
Source5: %name.chroot.conf
Source6: %name.chroot.all

Patch0: %name-8.2.2-makefile.patch
Patch1: %name-8.1.2-nonlist.patch
Patch2: %name-8.1.2-fds.patch
Patch4: %name-8.2-host.patch
Patch5: %name-8.8.2p5-hostmx.patch
Patch6: %name-8.8.2p5-ttl.patch
Patch7: %name-8.3.1-restart.patch
Patch10: %name-8.2.2-resolv.patch
Patch11: %name-8.2-desttmp.patch
Patch12: %name-8.2.2-install.patch
Patch13: %name-8.2.2-xfer.patch
Patch14: %name-8.2.3-db_defs.patch
Patch15: %name-8.2.4-named-norestart.patch
Patch16: %name-8.2.4-manpages.patch
Patch17: %name-8.3.1-alt-daemon_fd.patch

# root directory for chrooted environment.
%define	ROOT %_localstatedir/named

PreReq: %name-utils = %version-%release
PreReq: chrooted, chkconfig, shadow-utils, fileutils, grep, perl-base, syslogd-daemon
Provides: bind-chroot(%ROOT)
Obsoletes: bind-chroot
Conflicts: %name-devel < %version-%release, %name-devel > %version-%release
Conflicts: %name-doc < %version-%release, %name-doc > %version-%release
Conflicts: %name-utils < %version-%release, %name-utils > %version-%release
# Because of /etc/syslog.d/ feature.
Conflicts: syslogd < 1.4.1-alt9

%package utils
Summary: Utilities for querying DNS name servers
Group: Networking/Other
Prefix: %prefix
Conflicts: %name < %version-%release, %name > %version-%release
Conflicts: %name-devel < %version-%release, %name-devel > %version-%release
Conflicts: %name-doc < %version-%release, %name-doc > %version-%release

%package devel
Summary: Include files and libraries needed for %name DNS development
Group: Development/C
Conflicts: %name < %version-%release, %name > %version-%release
Conflicts: %name-doc < %version-%release, %name-doc > %version-%release
Conflicts: %name-utils < %version-%release, %name-utils > %version-%release
Prefix: %prefix

%package doc
Summary: %name documentation
Group: Development/Other
Conflicts: %name < %version-%release, %name > %version-%release
Conflicts: %name-devel < %version-%release, %name-devel > %version-%release
Conflicts: %name-utils < %version-%release, %name-utils > %version-%release
Prefix: %prefix

%package contrib
Summary: %name tools and examples from various individual contributors.
Group: Development/Other
AutoReqProv: yes, perl
Requires: %name-doc = %version-%release
Prefix: %prefix

%description
BIND (Berkeley Internet Name Domain) is an implementation of the DNS
(Domain Name System) protocols. BIND includes a DNS server (named),
which resolves host names to IP addresses, and a resolver library
(routines for applications to use when interfacing with DNS).  A DNS
server allows clients to name resources or objects and share the
information with other network machines.  The named DNS server can be
used on workstations as a caching name server, but is generally only
needed on one machine for an entire network.  Note that the
configuration files for making BIND act as a simple caching nameserver
are included in the caching-nameserver package.

This package also contains chrooted environment for DNS server.
If you want %name to act a caching name server, you will also need
to install the caching-nameserver package.

%description utils
Bind-utils contains a collection of utilities for querying DNS (Domain
Name Service) name servers to find out information about Internet hosts.
These tools will provide you with the IP addresses for given host names,
as well as other information about registered domains and network
addresses.

You should install %name-utils if you need to get information from DNS name
servers.

%description devel
The %name-devel package contains all the include files and the
library required for DNS (Domain Name Service) development for
BIND versions 8.x.x.

You should install %name-devel if you want to develop %name DNS applications.
If you install %name-devel, you'll also need to install %name.

%description doc
Documentation package contains, among others:
+ BIND Configuration File Guide
+ Name Server Operations Guide
+ set of RFC related to DNS

%description contrib
This package is full of %name tools and examples that various individual
contributors have sent in. Most of them are actually in live
production use somewhere, though they are not of "publication" quality
which is why they are here instead of in comp.sources.unix. Most of
them are not documented other than with comments in the sources. All
of them are fairly clever.

%prep
%setup -q -c -a1 -a2
%patch0 -p0
%patch1 -p0
%patch2 -p1
%patch4 -p1
#%patch5 -p1
#%patch6 -p1
%patch7 -p1
#%patch10 -p1
#%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1

rm -f compat/include/sys/cdefs.h
find -name .cvsignore -print0 |
	xargs -r0 rm -f --

# Now in nslint package.
rm -rf contrib/nslint*

find -type f -name Makefile\* -print0 |
	xargs -r0 grep -Zl '[^a-z_/]install -c' |
	xargs -r0 perl -pi -e 's|([^a-z_/])install -c|$1 \$(INSTALL)|g'
find -type f -name Makefile\* -print0 |
	xargs -r0 grep -lZ '[^a-z_/]install -m' |
	xargs -r0 perl -pi -e 's|([^a-z_/])install -m|$1 \$(INSTALL) -m|g'
find -type f -name Makefile\* -print0 |
	xargs -r0 grep -lZ '$(INSTALL).* -o.* -g' |
	xargs -r0 perl -pi -e 's|(\$\(INSTALL\).*) -o [A-Za-z$(){}]* -g [A-Za-z$(){}]*|$1|g'
find -type f -name Makefile\* -print0 |
	xargs -r0 grep -lZ -e '-o [A-Za-z$(){}]* -g [A-Za-z$(){}]*' |
	xargs -r0 perl -pi -e 's|-o [A-Za-z$(){}]* -g [A-Za-z$(){}]*||g'

# Work around a bind bug: SYSTYPE is always set to bsdos.
find src -name Makefile | xargs -n 1 perl -pi -e "
	s/^SYSTYPE=.*/SYSTYPE=linux/g;
	s/^SYSTYPE =.*/SYSTYPE=linux/g;
	s/^CDEBUG=.*/CDEBUG=$RPM_OPT_FLAGS/g;
	s/^CDEBUG =.*/CDEBUG=$RPM_OPT_FLAGS/g"

# Strip cwd from binaries.
perl -pi -e 's|`pwd`|/|' src/bin/named/Makefile

%build
# SMP-incompatible
make -C src

# Save original makefile
cp -p src/port/linux/Makefile.set src/port/linux/Makefile.set.sav

# Fix ndc to work with chrooted named
perl -pi -e 's|^(DESTRUN=)(/var/run)$|$1%ROOT$2|' src/port/linux/Makefile.set
make clean all -C src SUBDIRS=bin/ndc DESTRUN=%ROOT/var/run

# Restore original makefile
cp -p src/port/linux/Makefile.set.sav src/port/linux/Makefile.set

make clean all -C src SUBDIRS=../doc/man

%install
%__mkdir_p $RPM_BUILD_ROOT{%_bindir,%_sbindir,%_libdir,%_datadir/%name,%_mandir/{man{1,3,5,7,8}},%_localstatedir}

%make_install install DESTDIR=$RPM_BUILD_ROOT -C src
%make_install install DESTDIR=$RPM_BUILD_ROOT -C src SUBDIRS=../doc/man

%__mkdir_p $RPM_BUILD_ROOT%_initdir
sed -e 's|%%ROOT|%ROOT|g' <%SOURCE3 >$RPM_BUILD_ROOT%_initdir/named
touch -r %SOURCE3 $RPM_BUILD_ROOT%_initdir/named

# Create chrooted environment
%__mkdir_p $RPM_BUILD_ROOT%ROOT/{dev,etc,lib,usr/sbin,var/{lib,run,tmp},zone/slave}
for n in named-xfer; do
	mv "$RPM_BUILD_ROOT%_sbindir/$n" "$RPM_BUILD_ROOT%ROOT%_sbindir/$n"
	ln -s "%ROOT%_sbindir/$n" "$RPM_BUILD_ROOT%_sbindir/$n"
done
ln -s / $RPM_BUILD_ROOT%ROOT%ROOT
touch $RPM_BUILD_ROOT%ROOT/etc/{localtime,hosts,passwd,group}
/usr/sbin/mksock $RPM_BUILD_ROOT%ROOT/dev/log
chmod 666 $RPM_BUILD_ROOT%ROOT/dev/log
for f in `ldd $RPM_BUILD_ROOT%ROOT%_sbindir/* |awk '{print $3}' |sort -u`; do
	touch "$RPM_BUILD_ROOT%ROOT$f"
done
install -p -m750 -D %SOURCE4 $RPM_BUILD_ROOT%_sysconfdir/chroot.d/%name.lib
install -p -m750 -D %SOURCE5 $RPM_BUILD_ROOT%_sysconfdir/chroot.d/%name.conf
install -p -m750 -D %SOURCE6 $RPM_BUILD_ROOT%_sysconfdir/chroot.d/%name.all
perl -pi -e 's|%%ROOT|%ROOT|g' $RPM_BUILD_ROOT%_sysconfdir/chroot.d/%name.*

# Make use of syslogd-1.4.1-alt9 /etc/syslog.d/ feature.
%__mkdir_p $RPM_BUILD_ROOT%_sysconfdir/syslog.d
ln -s %ROOT/dev/log $RPM_BUILD_ROOT%_sysconfdir/syslog.d/%name

# Package docs
%__mkdir_p $RPM_BUILD_ROOT$RPM_DOC_DIR/%name-%version
cp -a src/{README,INSTALL,Version,CHANGES,LICENSE*,SUPPORT,DNSSEC,TODO} \
	doc/{bog,html,misc,notes,rfc,tmac} \
	$RPM_BUILD_ROOT$RPM_DOC_DIR/%name-%version

# Package contrib
find contrib -type f |xargs -r fgrep -l /etc/named.pid |
	xargs perl -pi -e 's|/etc/named\.pid|%ROOT/var/run/named.pid|'
find contrib -type f |xargs -r grep -l '^#! */bin/make' |
	xargs perl -pi -e 's|^#! */bin/make|#!/usr/bin/make|'
find contrib -type f |xargs -r fgrep -l /usr/sbin/lsattr |
	xargs perl -pi -e 's|/usr/sbin/lsattr|/usr/bin/lsattr|'
find contrib -type f |xargs -r file |fgrep perl |cut -d: -f1 |
	xargs -r perl -pi -e 's|^#![^a-z/@]*/.*/perl.*|#! /usr/bin/perl|g'
find contrib -type f |xargs -r file |fgrep PERL |cut -d: -f1 |
	xargs -r perl -pi -e 's|^#![^a-z/@]*\@PERL.*|#! /usr/bin/perl|g'
find -type f |xargs -r file |fgrep PostScript |cut -d: -f1 |xargs -r bzip2 -9
find contrib -type d -name win -print0 |
	xargs -r0 rm -rf --
cp -a contrib $RPM_BUILD_ROOT%_datadir/%name

# These pages come from man-pages package
rm -f $RPM_BUILD_ROOT%_mandir/{man7/mailaddr.7,man3/{getaddrinfo,gethostbyname,getipnodebyname,getnameinfo,getnetent,resolver}.3}

%pre
/usr/sbin/groupadd -r -f named >/dev/null 2>&1
/usr/sbin/useradd -r -g named -d %ROOT -s /dev/null -n -c "Domain Name Server" named >/dev/null 2>&1 ||:

%post
SYSLOGD_SCRIPT=/etc/init.d/syslogd
SYSLOGD_CONFIG=/etc/sysconfig/syslogd
if grep -qs '^SYSLOGD_OPTIONS=.*-a %ROOT/dev/log' "$SYSLOGD_CONFIG"; then
	perl -pi -e 's|^(SYSLOGD_OPTIONS=.*) ?-a %ROOT/dev/log|$1|' "$SYSLOGD_CONFIG"
	if [ -x "$SYSLOGD_SCRIPT" ]; then
		"$SYSLOGD_SCRIPT" condrestart
	fi
fi
%_sysconfdir/chroot.d/%name.all force
%post_service named

%triggerpostun -- %name-chroot
/sbin/chkconfig --add named ||:
%_sysconfdir/chroot.d/%name.all ||:
/sbin/service named condrestart ||:

%preun
%preun_service named

%files
%attr(755,root,root) %config %_initdir/named
%_sbindir/*
%_man1dir/dnskeygen.*
%_man5dir/named.conf.*
%_man7dir/*
%_man8dir/named.*
%_man8dir/ndc.*
%_man8dir/named-bootconf.*
%_man8dir/named-xfer.*
#chroot
%_sysconfdir/syslog.d/*
%config %_sysconfdir/chroot.d/*
%defattr(640,root,named,710)
%dir %ROOT
%dir %ROOT/*
%attr(710,root,named) %ROOT%_sbindir
%attr(-,root,root) %ROOT%ROOT
%dir %ROOT%_localstatedir
%dir %attr(1770,root,named) %ROOT/var/run
%dir %attr(1770,root,named) %ROOT/var/tmp
%dir %attr(1770,root,named) %ROOT/zone/slave
%ghost %attr(644,root,root) %ROOT/etc/hosts
%ghost %attr(644,root,root) %ROOT/etc/localtime
%ghost %ROOT/etc/group
%ghost %ROOT/etc/passwd
%ghost %attr(666,root,root) %ROOT/dev/*
%ghost %attr(755,root,root) %ROOT/lib/*

%files utils
%_bindir/*
%dir %_datadir/%name
%_datadir/%name/nslookup.help
%_man1dir/dig.*
%_man1dir/dnsquery.*
%_man1dir/host.*
%_man5dir/irs.conf.*
%_man5dir/resolver.*
%_man8dir/nslookup.*
%_man8dir/nsupdate.*

%files devel
%_libdir/lib*
%_includedir/*
%_man3dir/*

%files doc
%doc %_docdir/%name-%version

%files contrib
%_datadir/%name/contrib

%changelog
* Tue Apr 16 2002 Dmitry V. Levin <ldv@alt-linux.org> 8.3.1-alt1
- Updated code to 8.3.1 release.
- Fixed bind to use /dev/null from core system.
- Make use of syslogd-1.4.1-alt9 /etc/syslog.d/ feature.
- Renamed /etc/chroot.d/named.* to /etc/chroot.d/%name.*
- Relaxed dependencies (conflicts instead of requires).

* Wed Oct 03 2001 Dmitry V. Levin <ldv@altlinux.ru> 8.2.5-alt1
- 8.2.5

* Tue Sep 04 2001 Dmitry V. Levin <ldv@altlinux.ru> 8.2.4-alt3
- Corrected manpages according to chrooted scheme.
- More manpages moved to man-pages package.

* Tue Jul 24 2001 Dmitry V. Levin <ldv@altlinux.ru> 8.2.4-alt2
- Moved chroot from /var/named to %_localstatedir/named (according to FHS).
- Merged %name-chroot into main package.
- Updated scripts to handle new syslogd.
- Removed restart support from named.

* Thu May 31 2001 Dmitry V. Levin <ldv@altlinux.ru> 8.2.4-alt1
- 8.2.4

* Mon Mar 19 2001 Dmitry V. Levin <ldv@altlinux.ru> 8.2.3-ipl4mdk
- Updated PreReqs.

* Mon Feb 05 2001 Dmitry V. Levin <ldv@fandra.org> 8.2.3-ipl3mdk
- Fixed %%devel subpackage.

* Wed Jan 31 2001 Dmitry V. Levin <ldv@fandra.org> 8.2.3-ipl2mdk
- Pacthed db_defs.h to ease finding errors.
- Added %%triggerpostun.
- Added call for chrooted environment adjustment before server start.

* Sun Jan 28 2001 Dmitry V. Levin <ldv@fandra.org> 8.2.3-ipl1mdk
- 8.2.3
- Ported to new chrooted scheme.

* Thu Nov 16 2000 Dmitry V. Levin <ldv@fandra.org> 8.2.2_P7-ipl1mdk
- 8.2.2_P7
- Moved chrooted environment to separate subpackage.
- Removed few manpages, obsoleted by new man-pages package.

* Sat May 13 2000 Dmitry V. Levin <ldv@fandra.org>
- xfer tmpdir patch
- chrooted environment fix

* Fri Mar 10 2000 Dmitry V. Levin <ldv@fandra.org>
- fixed startup script to exit with error if no configuration available
- updated to rpm-3.0.4

* Thu Nov 11 1999 Dmitry V. Levin <ldv@fandra.org>
- 8.2.2-P3

* Sun Oct 31 1999 Dmitry V. Levin <ldv@fandra.org>
- chrooted environment
- doc and contrib packages
- optimal manpage compression
- Fandra adaptions

* Sat Oct 09 1999 Axalon Bloodstone <axalon@linux-mandrake.com>
- Add lame server patch

* Fri Jul 16 1999 Bernhard Rosenkraenzer <bero@mandrakesoft.com>
- 8.2.1

* Tue May 11 1999 Bernhard Rosenkraenzer <bero@mandrakesoft.com>
- Mandrake adaptions

* Wed Mar 31 1999 Bill Nottingham <notting@redhat.com>
- add ISC patch
- add quick hack to make host not crash
- add more docs

* Fri Mar 26 1999 Cristian Gafton <gafton@redhat.com>
- add probing information in the init file to keep linuxconf happy
- dont strip libbind

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com>
- auto rebuild in the new build environment (release 3)

* Wed Mar 17 1999 Preston Brown <pbrown@redhat.com>
- removed 'done' output at named shutdown.

* Tue Mar 16 1999 Cristian Gafton <gafton@redhat.com>
- version 8.2

* Wed Dec 30 1998 Cristian Gafton <gafton@redhat.com>
- patch to use the __FDS_BITS macro
- build for glibc 2.1

* Wed Sep 23 1998 Jeff Johnson <jbj@redhat.com>
- change named.restart to /usr/sbin/ndc restart

* Sat Sep 19 1998 Jeff Johnson <jbj@redhat.com>
- install man pages correctly.
- change K10named to K45named.

* Wed Aug 12 1998 Jeff Johnson <jbj@redhat.com>
- don't start if /etc/named.conf doesn't exist.

* Sat Aug  8 1998 Jeff Johnson <jbj@redhat.com>
- autmagically create /etc/named.conf from /etc/named.boot in %post
- remove echo in %post

* Wed Jun 10 1998 Jeff Johnson <jbj@redhat.com>
- merge in 5.1 mods

* Sun Apr 12 1998 Manuel J. Galan <manolow@step.es>
- Several essential modifications to build and install correctly.
- Modified 'ndc' to avoid deprecated use of '-'

* Mon Dec 22 1997 Scott Lampert <fortunato@heavymetal.org>
- Used buildroot
- patched bin/named/ns_udp.c to use <libelf/nlist.h> for include
  on Redhat 5.0 instead of <nlist.h>
