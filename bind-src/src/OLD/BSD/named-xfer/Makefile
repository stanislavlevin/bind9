# $Id: Makefile,v 1.1 1996/11/12 03:18:52 vixie Exp $

.PATH:	${.CURDIR}/../BIND/named \
	${.CURDIR}/../named/obj \
	${.CURDIR}/../BIND/man

PROG=	named-xfer
SRCS=	named-xfer.c db_glue.c storage.c dmalloc.c version.c
#LDADD+=	-lutil
#DPADD+=	${LIBUTIL}

BINDIR=	/usr/libexec

.include <bsd.prog.mk>
.include "${.CURDIR}/../Makefile.maninc"
