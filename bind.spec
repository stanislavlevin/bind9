Name: bind
%define vers_num 9.2.4
%define vers_rc rel
Version: %vers_num.%vers_rc
Release: alt2

Summary: The ISC BIND server
License: BSD-like
Group: System/Servers
Url: http://www.isc.org/products/BIND/

#%define srcname %name-%vers_num%vers_rc
%define srcname %name-%vers_num
Source0: ftp://ftp.isc.org/isc/bind9/%vers_num/%srcname.tar.bz2
Source1: nslookup.1
Source2: resolver.5
Source3: rfc1912.txt
Source4: bind.README.bind-devel
Source5: bind.README.ALT

Source11: bind.init
Source12: lwresd.init

Source21: rndc.conf
Source22: rndc.key

Source31: bind.named.conf
Source32: bind.options.conf
Source33: bind.rndc.conf
Source34: bind.local.conf
Source35: bind.rfc1912.conf
Source36: bind.rfc1918.conf

Source41: bind.localhost
Source42: bind.localdomain
Source43: bind.127.in-addr.arpa
Source44: bind.empty

Patch1: bind-9.2.4rc5-alt-man.patch
Patch2: bind-9.2.4rc5-alt-isc-config.patch
Patch3: bind-9.2.4rc5-alt-rndc-confgen.patch
Patch4: bind-9.2.4rc5-alt-chroot.patch
Patch5: bind-9.2.4rc5-obsd-pidfile.patch
Patch6: bind-9.2.4rc5-obsd-chroot_default.patch
Patch7: bind-9.2.4rc5-owl-checkconf_chroot.patch
Patch8: bind-9.2.4-alt-queryperf-configure.patch

# root directory for chrooted environment.
%define ROOT %_localstatedir/bind

# common directory for bind docs.
%define docdir %_docdir/bind-%version

%ifndef timestamp
%define timestamp %(LC_TIME=C date +%%Y%%m%%d)
%endif

Provides: bind-chroot(%ROOT)
Obsoletes: bind-chroot, caching-nameserver
# Because of /etc/syslog.d/ feature.
Conflicts: syslogd < 1.4.1-alt11
PreReq: chrooted, chkconfig, shadow-utils, coreutils, grep, syslogd-daemon
PreReq: %__subst, %post_service, %preun_service
PreReq: libdns16 = %version-%release
PreReq: libisc7 = %version-%release
PreReq: libisccc0 = %version-%release
PreReq: libisccfg0 = %version-%release
PreReq: liblwres1 = %version-%release

# due to %ROOT/dev/log
BuildPreReq: coreutils

# due to broken configure script
BuildPreReq: gcc-c++

BuildPreReq: libssl-devel openjade

%package slave
Summary: The chroot jail part for ISC BIND slave server
Group: System/Servers
PreReq: %name = %version-%release

%package debug
Summary: The chroot jail part for debugging ISC BIND server
Group: System/Servers
PreReq: %name = %version-%release

%package utils
Summary: Utilities provided with BIND
Group: Networking/Other
Requires: libdns16 = %version-%release
Requires: libisc7 = %version-%release
Requires: liblwres1 = %version-%release

%package devel
Summary: BIND development libraries and headers
Group: Development/C
Requires: libdns16 = %version-%release
Requires: libisc7 = %version-%release
Requires: libisccc0 = %version-%release
Requires: libisccfg0 = %version-%release
Requires: liblwres1 = %version-%release

%package devel-static
Summary: BIND static development libraries
Group: Development/C
Requires: %name-devel = %version-%release

%package doc
Summary: Documentation for BIND
Group: Development/Other
Prefix: %prefix

%package -n libdns16
Summary: DNS shared library used by BIND
Group: System/Libraries
Provides: libdns = %version-%release

%package -n libisc7
Summary: ISC shared library used by BIND
Group: System/Libraries
Provides: libisc = %version-%release

%package -n libisccc0
Summary: Command channel library used by BIND
Group: System/Libraries
Provides: libisccc = %version-%release

%package -n libisccfg0
Summary: Config file handling library used by BIND
Group: System/Libraries
Provides: libisccfg = %version-%release

%package -n liblwres1
Summary: Lightweight resolver shared library used by BIND
Group: System/Libraries
Provides: liblwres = %version-%release

%package -n lwresd
Summary: Lightweight resolver daemon
Group: System/Servers
PreReq: /var/resolv, chkconfig, shadow-utils
Requires: libdns16 = %version-%release
Requires: libisc7 = %version-%release
Requires: libisccc0 = %version-%release
Requires: libisccfg0 = %version-%release
Requires: liblwres1 = %version-%release

%description
The Berkeley Internet Name Domain (BIND) implements an Internet domain
name server.  BIND is the most widely-used name server software on the
Internet, and is supported by the Internet Software Consortium (ISC).

This package provides the server and related configuration files.

%description slave
This package contains chroot jail part necessary for configuring BIND
to operate as slave DNS.

%description debug
This package contains chroot jail part necessary for debugging BIND.

%description utils
This package contains various utilities related to DNS that are
derived from the BIND source tree, including dig, host, nslookup
and nsupdate.

%description devel
This package contains development libraries, header files, and API man
pages for libdns, libisc, libisccc, libisccfg and liblwres.  These are
only needed  if you want to compile packages that need more nameserver
API than the resolver code provided in libc.

%description devel-static
This package contains development static libraries, header files, and API man
pages for libdns, libisc, libisccc, libisccfg and liblwres.  These are
only needed  if you want to compile statically linked  packages that
need more nameserver API than the resolver code provided in libc.

%description doc
This package provides various documents that are useful for maintaining a
working BIND installation.

%description -n libdns16
This package contains the libdns shared library used by BIND's daemons
and clients.

%description -n libisc7
This package contains the libisc shared library used by BIND's daemons
and clients.

%description -n libisccc0
This package contains the libisccc shared library used by BIND's daemons
and clients, particularly rndc.

%description -n libisccfg0
This package contains the libisccfg shared library used by BIND's daemons
and clients to read and write ISC-style configuration files like
named.conf and rndc.conf.

%description -n liblwres1
This package contains the liblwres shared library used by BIND's daemons
and clients.

%description -n lwresd
This package contains lwresd, the daemon providing name lookup services
to clients that use the BIND 9 lightweight resolver library.  It is
essentially a stripped-down, caching-only name server that answers
queries using the BIND 9 lightweight resolver protocol rather than
the DNS protocol.

%prep
%setup -q -n %srcname
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
find -type f -name \*.orig -delete -print

%__install -p -m644 $RPM_SOURCE_DIR/rfc1912.txt doc/rfc/
%__install -p -m644 $RPM_SOURCE_DIR/bind.README.bind-devel README.bind-devel
%__install -p -m644 $RPM_SOURCE_DIR/bind.README.ALT README.ALT

%__mkdir_p alt
%__cp -p $RPM_SOURCE_DIR/{nslookup.1,resolver.5} alt/
%__cp -p $RPM_SOURCE_DIR/{bind,lwresd}.init alt/
%__cp -p $RPM_SOURCE_DIR/rndc.{conf,key} alt/
%__cp -p $RPM_SOURCE_DIR/bind.{named,options,rndc,local,rfc1912,rfc1918}.conf alt/
%__cp -p $RPM_SOURCE_DIR/bind.{localhost,localdomain,127.in-addr.arpa,empty} alt/

find -type f -print0 |
	xargs -r0 %__grep -FZl '@ROOT@' -- |
	xargs -r0 %__subst -p 's|@ROOT@|%ROOT|g' --

find -type f -print0 |
	xargs -r0 %__grep -FZl '@DOCDIR@' -- |
	xargs -r0 %__subst -p 's|@DOCDIR@|%docdir|g' --

%build
%configure \
	--localstatedir=/var \
	--with-libtool \
	--with-openssl \
	--with-randomdev=/dev/random \
	--disable-ipv6 \
	--disable-threads \
	--disable-linux-caps \
	 %{subst_enable static} \
	#
# SMP-incompatible build.
make

# Build queryperf
pushd contrib/queryperf
	subst -p 's/res_mkquery/__&/g' configure*
	%configure
	%make_build
popd # contrib/queryperf

%install
%__mkdir_p $RPM_BUILD_ROOT{%_bindir,%_sbindir,%_libdir,%_mandir/{man{1,3,5,8}},%_localstatedir}

#%__install -p -m644 alt/nslookup.1 $RPM_BUILD_ROOT%_man1dir/
%__install -p -m644 alt/resolver.5 $RPM_BUILD_ROOT%_man5dir/
%make_install install DESTDIR=$RPM_BUILD_ROOT
%__mv $RPM_BUILD_ROOT{%_man8dir,%_man5dir}/named.conf.5

%__install -p -m755 contrib/queryperf/queryperf $RPM_BUILD_ROOT%_sbindir/

%__install -pD -m755 alt/bind.init $RPM_BUILD_ROOT%_initdir/bind
%__install -pD -m755 alt/lwresd.init $RPM_BUILD_ROOT%_initdir/lwresd
%__install -p -m600 alt/rndc.conf $RPM_BUILD_ROOT%_sysconfdir/

# Create chrooted environment
%__mkdir_p $RPM_BUILD_ROOT%ROOT/{dev,etc,var/{run,tmp},zone/slave}
for n in named options rndc local rfc1912 rfc1918; do
	%__install -pD -m640 "alt/bind.$n.conf" "$RPM_BUILD_ROOT%ROOT%_sysconfdir/$n.conf"
done
for n in localhost localdomain 127.in-addr.arpa empty; do
        %__install -pD -m640 "alt/bind.$n" "$RPM_BUILD_ROOT%ROOT/zone/$n"
	%__subst -p s/YYYYMMDDNN/%{timestamp}00/ "$RPM_BUILD_ROOT%ROOT/zone/$n"
done
%__install -p -m640 alt/rndc.key $RPM_BUILD_ROOT%ROOT%_sysconfdir/
%__ln_s %ROOT%_sysconfdir/named.conf $RPM_BUILD_ROOT%_sysconfdir/

# Make use of syslogd-1.4.1-alt11 /etc/syslog.d/ feature.
/usr/bin/mksock $RPM_BUILD_ROOT%ROOT/dev/log
%__mkdir_p $RPM_BUILD_ROOT%_sysconfdir/syslog.d
%__ln_s %ROOT/dev/log $RPM_BUILD_ROOT%_sysconfdir/syslog.d/bind

# ndc compatibility symlinks.
%__ln_s rndc $RPM_BUILD_ROOT%_sbindir/ndc
%__ln_s rndc.8 $RPM_BUILD_ROOT%_man8dir/ndc.8

# Package docs
%__rm -rf $RPM_BUILD_ROOT%docdir
%__mkdir_p $RPM_BUILD_ROOT%docdir
%__cp -a CHANGES COPYRIGHT FAQ README* KNOWN_DEFECTS \
	doc/{arm,draft,misc,rfc} \
	$RPM_BUILD_ROOT%docdir/
%__install -p -m644 contrib/queryperf/README $RPM_BUILD_ROOT%docdir/README.queryperf

%__bzip2 $RPM_BUILD_ROOT%docdir/{*/*.txt,FAQ,CHANGES}
%__rm -fv $RPM_BUILD_ROOT%docdir/*/{Makefile*,README-SGML,*.dsl*,*.sh*,*.xml}

%post -n libdns16 -p %post_ldconfig
%postun -n libdns16 -p %postun_ldconfig

%post -n libisccc0 -p %post_ldconfig
%postun -n libisccc0 -p %postun_ldconfig

%post -n libisccfg0 -p %post_ldconfig
%postun -n libisccfg0 -p %postun_ldconfig

%post -n libisc7 -p %post_ldconfig
%postun -n libisc7 -p %postun_ldconfig

%post -n liblwres1 -p %post_ldconfig
%postun -n liblwres1 -p %postun_ldconfig

%pre
/usr/sbin/groupadd -r -f named
/usr/sbin/useradd -r -g named -d %ROOT -s /dev/null -n -c "Domain Name Server" named >/dev/null 2>&1 ||:
[ -f %_initdir/named -a ! -L %_initdir/named ] && /sbin/chkconfig --del named ||:

%preun
%preun_service bind

%post
SYSLOGD_SCRIPT=/etc/init.d/syslogd
SYSLOGD_CONFIG=/etc/sysconfig/syslogd
if %__grep -qs '^SYSLOGD_OPTIONS=.*-a %ROOT/dev/log' "$SYSLOGD_CONFIG"; then
	%__subst 's|^\(SYSLOGD_OPTIONS=.*\) \?-a %ROOT/dev/log|\1|' "$SYSLOGD_CONFIG"
	if [ -x "$SYSLOGD_SCRIPT" ]; then
		"$SYSLOGD_SCRIPT" condreload ||:
	fi
fi

%post_service bind

%pre -n lwresd
/usr/sbin/groupadd -r -f lwresd
/usr/sbin/useradd -r -g lwresd -d / -s /dev/null -n -c "Lightweight Resolver Daemon" lwresd >/dev/null 2>&1 ||:

%post -n lwresd
%post_service lwresd

%preun -n lwresd
%preun_service lwresd

%files -n libdns16
%_libdir/libdns.so.*

%files -n libisc7
%_libdir/libisc.so.*

%files -n libisccc0
%_libdir/libisccc.so.*

%files -n libisccfg0
%_libdir/libisccfg.so.*

%files -n liblwres1
%_libdir/liblwres.so.*

%files -n lwresd
%config %_initdir/lwresd
%_sbindir/lwresd
%_man8dir/lwresd.*

%files devel
%_libdir/*.so
%_bindir/isc-config.sh
%_includedir/*
%_man3dir/*
%dir %docdir
%docdir/README.bind-devel

%if_enabled static
%files devel-static
%_libdir/*.a
%endif

%files
%exclude %_sbindir/lwresd
%_sbindir/*

%_sysconfdir/named.conf
%config %_initdir/bind
%config(noreplace) %_sysconfdir/rndc.conf

%_man5dir/named.conf.*
%_man5dir/rndc.conf.*
%_man8dir/dnssec*
%_man8dir/named*
%_man8dir/*ndc*

%dir %docdir
%docdir/COPYRIGHT
%docdir/README*
%docdir/FAQ*
%docdir/misc
%exclude %docdir/README.bind-devel

#chroot
%_sysconfdir/syslog.d/*
%defattr(640,root,named,710)
%dir %ROOT
%dir %ROOT/*
%config(noreplace) %attr(640,root,named) %ROOT/etc/*.conf
%config(noreplace) %attr(640,root,named) %verify(not md5 mtime size) %ROOT/etc/rndc.key
%config %attr(640,root,named) %ROOT/zone/localhost
%config %attr(640,root,named) %ROOT/zone/localdomain
%config %attr(640,root,named) %ROOT/zone/127.in-addr.arpa
%config %attr(640,root,named) %ROOT/zone/empty
%ghost %attr(666,root,root) %ROOT/dev/*

%files slave
%defattr(640,root,named,710)
%dir %ROOT
%dir %ROOT/zone
%dir %attr(1770,root,named) %ROOT/zone/slave

%files debug
%defattr(640,root,named,710)
%dir %ROOT
%dir %ROOT/var
%dir %attr(1770,root,named) %ROOT/var/run
%dir %attr(1770,root,named) %ROOT/var/tmp

%files utils
%_bindir/dig
%_bindir/host
%_bindir/nslookup
%_bindir/nsupdate
%_man1dir/dig.*
%_man1dir/host.*
%_man1dir/nslookup.*
%_man5dir/resolver.*
%_man8dir/nsupdate.*

%files doc
%docdir
%exclude %docdir/README.bind-devel

%changelog
* Sat Feb 12 2005 Dmitry V. Levin <ldv@altlinux.org> 9.2.4.rel-alt2
- Fixed build of queryperf utility on x86_64 platform (closes #6083).

* Fri Sep 24 2004 Dmitry V. Levin <ldv@altlinux.org> 9.2.4.rel-alt1
- Updated to 9.2.4 release (== 9.2.4rc8).

* Sun Sep 05 2004 Dmitry V. Levin <ldv@altlinux.org> 9.2.4.rc8-alt1
- Updated to 9.2.4rc8.
- Renamed subpackage according to soname change:
  libdns11 -> libdns16.
- Updated startup script to make use of new "status --lockfile" option.

* Wed Jun 30 2004 Dmitry V. Levin <ldv@altlinux.org> 9.2.4.rc5-alt1
- Updated to 9.2.4rc5.
- Updated patches.

* Mon May 10 2004 ALT QA Team Robot <qa-robot@altlinux.org> 9.2.3.rel-alt2.1
- Rebuilt with openssl-0.9.7d.

* Wed Mar 10 2004 Dmitry V. Levin <ldv@altlinux.org> 9.2.3.rel-alt2
- Updated build dependencies.
- Do not build static library by default.

* Mon Nov 24 2003 Dmitry V. Levin <ldv@altlinux.org> 9.2.3.rel-alt1
- Updated to 9.2.3 release.
- Rediffed patches.
- Do not package .la files.
- named.8: fixed reference to the BIND 9 Administrator Reference Manual.

* Mon Sep 22 2003 Dmitry V. Levin <ldv@altlinux.org> 9.2.3.rc4-alt1
- Updated to 9.2.3rc4.
- Renamed subpackage according to soname change:
  libdns10 -> libdns11.
- Replaced "delegation-only" defaults implemented in previous release
  with new option, root-delegation-only, and enabled it by default.

* Thu Sep 18 2003 Dmitry V. Levin <ldv@altlinux.org> 9.2.3.rc2-alt1
- Updated to 9.2.3rc2.
- Renamed subpackage according to soname change:
  libdns9 -> libdns10.
- Marked all known gTLDs and ccTLDs as delegation-only by default.

* Thu Sep 11 2003 Dmitry V. Levin <ldv@altlinux.org> 9.2.3.rc1-alt2
- Merged patches from OpenBSD, thanks to Jarno Huuskonen:
  + write pidfile before chroot (#2866);
  + use chroot jailing by default, no -u/-t options are necessary;
- Make named-checkconf use chroot jail by default (Jarno Huuskonen).
- options.conf: added few samples (#2968).

* Tue Aug 26 2003 Dmitry V. Levin <ldv@altlinux.org> 9.2.3.rc1-alt1
- Updated to 9.2.3rc1.
- Removed alt-lib_dns_rootns patch (merged upstream).
- Explicitly disable use of linux capabilities.
- Renamed subpackages according to soname changes:
  libdns8 -> libdns9, libisc4 -> libisc7.

* Tue Jul 29 2003 Dmitry V. Levin <ldv@altlinux.org> 9.2.2.rel-alt2
- Fixed message from 'service bind reload' (#0002411).
- Moved 'include "/etc/rfc1912.conf";' directive
  from bind.conf to local.conf (#0002791).
- Rewritten start/stop script to new rc scheme.

* Tue Mar 04 2003 Dmitry V. Levin <ldv@altlinux.org> 9.2.2.rel-alt1
- Updated to 9.2.2 release.

* Wed Feb 12 2003 Dmitry V. Levin <ldv@altlinux.org> 9.2.2.rc1-alt2
- Relocated initial rndc key generation from %%post to startup script.
- Added some information about ALT specific to named(8) and rndc(8).
- Added README.ALT.

* Thu Feb 06 2003 Dmitry V. Levin <ldv@altlinux.org> 9.2.2.rc1-alt1
- Migrated to 9.2.2rc1.
- Build --with-libtool --with-openssl --disable-ipv6 --disable-threads.
- Do not package contrib.
- Package queryperf utility.
- Package each shared library separately:
  libdns8 libisc4 libisccc0 libisccfg0 liblwres1.
- Package lwresd separately (chrooted to /var/resolv).
- Moved %ROOT/zone/slave to separate subpackage, %name-slave.
- Moved %ROOT/var/run to separate subpackage, %name-debug.
- Added nslookup(1) and resolver(5) manpages from bind8.
- Minor manpage corrections.
- isc-config.sh: fixed --cflags.
- libdns: updated root_ns list to 2002110501.
- rndc-confgen: added "-A" option support.
- Implemented default rndc settings.
- named: patched to get correct chroot jailing support.
- Updated chroot jail and relocated it to /var/lib/bind:
  default CE is now readonly.
- Renamed %_initdir/named to %_initdir/bind.
- Merged caching-nameserver into bind package.
- Split named.conf into several configurations files.
- Added more rfc1912 zones by default.
- Added rfc1918 zones (not enabled by default).

* Wed Nov 13 2002 Dmitry V. Levin <ldv@altlinux.org> 8.3.3-alt2
- Security fixes from ISC:
  + 1469. buffer length calculation for PX was wrong.
  + 1468. ns_name_ntol() could overwite a zero length buffer.
  + 1467. off by one bug in ns_makecannon().
  + 1466. large ENDS UDP buffer size could trigger a assertion.
  + 1465. possible NULL pointer dereference in db_sec.c
  + 1464. the buffer used to construct the -ve record was not
    	  big enough for all possible SOA records.  use pointer
    	  arithmetic to calculate the remaining size in this
    	  buffer.
  + 1463. use serial space arithmetic to determine if a SIG is
    	  too old, in the future or has internally constistant
    	  times.
  + 1462. write buffer overflow in make_rr().
- Changed named.init:
  + added condreload();
  + fixed argument for "-c" option.
- Changed bind chroot jail:
  + removed /var/lib;
  + removed /etc/{host,nsswitch}.conf;
  + added /etc/{protocols,services}.
- Use subst instead of perl in %%post script.
- Dont't calc perl dependencies for -contrib.

* Mon Jul 01 2002 Dmitry V. Levin <ldv@altlinux.org> 8.3.3-alt1
- Updated code to 8.3.3 release.
- Explicitly use mksock from fileutils.
- Fixed build when glibc-core-archopt is installed.
- Updated packager information.

* Tue Apr 16 2002 Dmitry V. Levin <ldv@alt-linux.org> 8.3.1-alt1
- Updated code to 8.3.1 release.
- Fixed bind to use /dev/null from core system.
- Make use of syslogd-1.4.1-alt9 /etc/syslog.d/ feature.
- Renamed /etc/chroot.d/named.* to /etc/chroot.d/bind.*
- Relaxed dependencies (conflicts instead of requires).

* Wed Oct 03 2001 Dmitry V. Levin <ldv@altlinux.ru> 8.2.5-alt1
- 8.2.5

* Tue Sep 04 2001 Dmitry V. Levin <ldv@altlinux.ru> 8.2.4-alt3
- Corrected manpages according to chrooted scheme.
- More manpages moved to man-pages package.

* Tue Jul 24 2001 Dmitry V. Levin <ldv@altlinux.ru> 8.2.4-alt2
- Moved chroot from /var/named to %_localstatedir/named (according to FHS).
- Merged bind-chroot into main package.
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
