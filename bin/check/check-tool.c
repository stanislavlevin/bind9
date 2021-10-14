/*
 * Copyright (C) Internet Systems Consortium, Inc. ("ISC")
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, you can obtain one at https://mozilla.org/MPL/2.0/.
 *
 * See the COPYRIGHT file distributed with this work for additional
 * information regarding copyright ownership.
 */

/*! \file */

#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>

#ifdef _WIN32
#include <Winsock2.h>
#endif /* ifdef _WIN32 */

#include <isc/buffer.h>
#include <isc/log.h>
#include <isc/mem.h>
#include <isc/net.h>
#include <isc/netdb.h>
#include <isc/print.h>
#include <isc/region.h>
#include <isc/stdio.h>
#include <isc/string.h>
#include <isc/symtab.h>
#include <isc/types.h>
#include <isc/util.h>

#include <dns/db.h>
#include <dns/dbiterator.h>
#include <dns/fixedname.h>
#include <dns/log.h>
#include <dns/name.h>
#include <dns/rdata.h>
#include <dns/rdataclass.h>
#include <dns/rdataset.h>
#include <dns/rdatasetiter.h>
#include <dns/rdatatype.h>
#include <dns/result.h>
#include <dns/types.h>
#include <dns/zone.h>

#include <isccfg/log.h>

#include <ns/log.h>

#include "check-tool.h"

#ifndef CHECK_SIBLING
#define CHECK_SIBLING 1
#endif /* ifndef CHECK_SIBLING */

#ifndef CHECK_LOCAL
#define CHECK_LOCAL 1
#endif /* ifndef CHECK_LOCAL */

#define CHECK(r)                             \
	do {                                 \
		result = (r);                \
		if (result != ISC_R_SUCCESS) \
			goto cleanup;        \
	} while (0)

#define ERR_IS_CNAME	   1
#define ERR_NO_ADDRESSES   2
#define ERR_LOOKUP_FAILURE 3
#define ERR_EXTRA_A	   4
#define ERR_EXTRA_AAAA	   5
#define ERR_MISSING_GLUE   5
#define ERR_IS_MXCNAME	   6
#define ERR_IS_SRVCNAME	   7

static const char *dbtype[] = { "rbt" };

int debug = 0;
const char *journal = NULL;
bool nomerge = true;
#if CHECK_LOCAL
bool docheckmx = true;
bool dochecksrv = true;
bool docheckns = true;
#else  /* if CHECK_LOCAL */
bool docheckmx = false;
bool dochecksrv = false;
bool docheckns = false;
#endif /* if CHECK_LOCAL */
dns_zoneopt_t zone_options = DNS_ZONEOPT_CHECKNS | DNS_ZONEOPT_CHECKMX |
			     DNS_ZONEOPT_MANYERRORS | DNS_ZONEOPT_CHECKNAMES |
			     DNS_ZONEOPT_CHECKINTEGRITY |
#if CHECK_SIBLING
			     DNS_ZONEOPT_CHECKSIBLING |
#endif /* if CHECK_SIBLING */
			     DNS_ZONEOPT_CHECKWILDCARD |
			     DNS_ZONEOPT_WARNMXCNAME | DNS_ZONEOPT_WARNSRVCNAME;

/*
 * This needs to match the list in bin/named/log.c.
 */
static isc_logcategory_t categories[] = { { "", 0 },
					  { "unmatched", 0 },
					  { NULL, 0 } };

static isc_symtab_t *symtab = NULL;
static isc_mem_t *sym_mctx;

static void
freekey(char *key, unsigned int type, isc_symvalue_t value, void *userarg) {
	UNUSED(type);
	UNUSED(value);
	isc_mem_free(userarg, key);
}

static void
add(char *key, int value) {
	isc_result_t result;
	isc_symvalue_t symvalue;

	if (sym_mctx == NULL) {
		isc_mem_create(&sym_mctx);
	}

	if (symtab == NULL) {
		result = isc_symtab_create(sym_mctx, 100, freekey, sym_mctx,
					   false, &symtab);
		if (result != ISC_R_SUCCESS) {
			return;
		}
	}

	key = isc_mem_strdup(sym_mctx, key);

	symvalue.as_pointer = NULL;
	result = isc_symtab_define(symtab, key, value, symvalue,
				   isc_symexists_reject);
	if (result != ISC_R_SUCCESS) {
		isc_mem_free(sym_mctx, key);
	}
}

static bool
logged(char *key, int value) {
	isc_result_t result;

	if (symtab == NULL) {
		return (false);
	}

	result = isc_symtab_lookup(symtab, key, value, NULL);
	if (result == ISC_R_SUCCESS) {
		return (true);
	}
	return (false);
}

static bool
checkns(dns_zone_t *zone, const dns_name_t *name, const dns_name_t *owner,
	dns_rdataset_t *a, dns_rdataset_t *aaaa) {
	dns_rdataset_t *rdataset;
	dns_rdata_t rdata = DNS_RDATA_INIT;
	struct addrinfo hints, *ai, *cur;
	char namebuf[DNS_NAME_FORMATSIZE + 1];
	char ownerbuf[DNS_NAME_FORMATSIZE];
	char addrbuf[sizeof("xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:123.123.123.123")];
	bool answer = true;
	bool match;
	const char *type;
	void *ptr = NULL;
	int result;

	REQUIRE(a == NULL || !dns_rdataset_isassociated(a) ||
		a->type == dns_rdatatype_a);
	REQUIRE(aaaa == NULL || !dns_rdataset_isassociated(aaaa) ||
		aaaa->type == dns_rdatatype_aaaa);

	if (a == NULL || aaaa == NULL) {
		return (answer);
	}

	memset(&hints, 0, sizeof(hints));
	hints.ai_flags = AI_CANONNAME;
	hints.ai_family = PF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = IPPROTO_TCP;

	dns_name_format(name, namebuf, sizeof(namebuf) - 1);
	/*
	 * Turn off search.
	 */
	if (dns_name_countlabels(name) > 1U) {
		strlcat(namebuf, ".", sizeof(namebuf));
	}
	dns_name_format(owner, ownerbuf, sizeof(ownerbuf));

	result = getaddrinfo(namebuf, NULL, &hints, &ai);
	dns_name_format(name, namebuf, sizeof(namebuf) - 1);
	switch (result) {
	case 0:
		/*
		 * Work around broken getaddrinfo() implementations that
		 * fail to set ai_canonname on first entry.
		 */
		cur = ai;
		while (cur != NULL && cur->ai_canonname == NULL &&
		       cur->ai_next != NULL) {
			cur = cur->ai_next;
		}
		if (cur != NULL && cur->ai_canonname != NULL &&
		    strcasecmp(cur->ai_canonname, namebuf) != 0 &&
		    !logged(namebuf, ERR_IS_CNAME))
		{
			dns_zone_log(zone, ISC_LOG_ERROR,
				     "%s/NS '%s' (out of zone) "
				     "is a CNAME '%s' (illegal)",
				     ownerbuf, namebuf, cur->ai_canonname);
			/* XXX950 make fatal for 9.5.0 */
			/* answer = false; */
			add(namebuf, ERR_IS_CNAME);
		}
		break;
	case EAI_NONAME:
#if defined(EAI_NODATA) && (EAI_NODATA != EAI_NONAME)
	case EAI_NODATA:
#endif /* if defined(EAI_NODATA) && (EAI_NODATA != EAI_NONAME) */
		if (!logged(namebuf, ERR_NO_ADDRESSES)) {
			dns_zone_log(zone, ISC_LOG_ERROR,
				     "%s/NS '%s' (out of zone) "
				     "has no addresses records (A or AAAA)",
				     ownerbuf, namebuf);
			add(namebuf, ERR_NO_ADDRESSES);
		}
		/* XXX950 make fatal for 9.5.0 */
		return (true);

	default:
		if (!logged(namebuf, ERR_LOOKUP_FAILURE)) {
			dns_zone_log(zone, ISC_LOG_WARNING,
				     "getaddrinfo(%s) failed: %s", namebuf,
				     gai_strerror(result));
			add(namebuf, ERR_LOOKUP_FAILURE);
		}
		return (true);
	}

	/*
	 * Check that all glue records really exist.
	 */
	if (!dns_rdataset_isassociated(a)) {
		goto checkaaaa;
	}
	result = dns_rdataset_first(a);
	while (result == ISC_R_SUCCESS) {
		dns_rdataset_current(a, &rdata);
		match = false;
		for (cur = ai; cur != NULL; cur = cur->ai_next) {
			if (cur->ai_family != AF_INET) {
				continue;
			}
			ptr = &((struct sockaddr_in *)(cur->ai_addr))->sin_addr;
			if (memcmp(ptr, rdata.data, rdata.length) == 0) {
				match = true;
				break;
			}
		}
		if (!match && !logged(namebuf, ERR_EXTRA_A)) {
			dns_zone_log(zone, ISC_LOG_ERROR,
				     "%s/NS '%s' "
				     "extra GLUE A record (%s)",
				     ownerbuf, namebuf,
				     inet_ntop(AF_INET, rdata.data, addrbuf,
					       sizeof(addrbuf)));
			add(namebuf, ERR_EXTRA_A);
			/* XXX950 make fatal for 9.5.0 */
			/* answer = false; */
		}
		dns_rdata_reset(&rdata);
		result = dns_rdataset_next(a);
	}

checkaaaa:
	if (!dns_rdataset_isassociated(aaaa)) {
		goto checkmissing;
	}
	result = dns_rdataset_first(aaaa);
	while (result == ISC_R_SUCCESS) {
		dns_rdataset_current(aaaa, &rdata);
		match = false;
		for (cur = ai; cur != NULL; cur = cur->ai_next) {
			if (cur->ai_family != AF_INET6) {
				continue;
			}
			ptr = &((struct sockaddr_in6 *)(cur->ai_addr))
				       ->sin6_addr;
			if (memcmp(ptr, rdata.data, rdata.length) == 0) {
				match = true;
				break;
			}
		}
		if (!match && !logged(namebuf, ERR_EXTRA_AAAA)) {
			dns_zone_log(zone, ISC_LOG_ERROR,
				     "%s/NS '%s' "
				     "extra GLUE AAAA record (%s)",
				     ownerbuf, namebuf,
				     inet_ntop(AF_INET6, rdata.data, addrbuf,
					       sizeof(addrbuf)));
			add(namebuf, ERR_EXTRA_AAAA);
			/* XXX950 make fatal for 9.5.0. */
			/* answer = false; */
		}
		dns_rdata_reset(&rdata);
		result = dns_rdataset_next(aaaa);
	}

checkmissing:
	/*
	 * Check that all addresses appear in the glue.
	 */
	if (!logged(namebuf, ERR_MISSING_GLUE)) {
		bool missing_glue = false;
		for (cur = ai; cur != NULL; cur = cur->ai_next) {
			switch (cur->ai_family) {
			case AF_INET:
				rdataset = a;
				ptr = &((struct sockaddr_in *)(cur->ai_addr))
					       ->sin_addr;
				type = "A";
				break;
			case AF_INET6:
				rdataset = aaaa;
				ptr = &((struct sockaddr_in6 *)(cur->ai_addr))
					       ->sin6_addr;
				type = "AAAA";
				break;
			default:
				continue;
			}
			match = false;
			if (dns_rdataset_isassociated(rdataset)) {
				result = dns_rdataset_first(rdataset);
			} else {
				result = ISC_R_FAILURE;
			}
			while (result == ISC_R_SUCCESS && !match) {
				dns_rdataset_current(rdataset, &rdata);
				if (memcmp(ptr, rdata.data, rdata.length) == 0)
				{
					match = true;
				}
				dns_rdata_reset(&rdata);
				result = dns_rdataset_next(rdataset);
			}
			if (!match) {
				dns_zone_log(zone, ISC_LOG_ERROR,
					     "%s/NS '%s' "
					     "missing GLUE %s record (%s)",
					     ownerbuf, namebuf, type,
					     inet_ntop(cur->ai_family, ptr,
						       addrbuf,
						       sizeof(addrbuf)));
				/* XXX950 make fatal for 9.5.0. */
				/* answer = false; */
				missing_glue = true;
			}
		}
		if (missing_glue) {
			add(namebuf, ERR_MISSING_GLUE);
		}
	}
	freeaddrinfo(ai);
	return (answer);
}

static bool
checkmx(dns_zone_t *zone, const dns_name_t *name, const dns_name_t *owner) {
	struct addrinfo hints, *ai, *cur;
	char namebuf[DNS_NAME_FORMATSIZE + 1];
	char ownerbuf[DNS_NAME_FORMATSIZE];
	int result;
	int level = ISC_LOG_ERROR;
	bool answer = true;

	memset(&hints, 0, sizeof(hints));
	hints.ai_flags = AI_CANONNAME;
	hints.ai_family = PF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = IPPROTO_TCP;

	dns_name_format(name, namebuf, sizeof(namebuf) - 1);
	/*
	 * Turn off search.
	 */
	if (dns_name_countlabels(name) > 1U) {
		strlcat(namebuf, ".", sizeof(namebuf));
	}
	dns_name_format(owner, ownerbuf, sizeof(ownerbuf));

	result = getaddrinfo(namebuf, NULL, &hints, &ai);
	dns_name_format(name, namebuf, sizeof(namebuf) - 1);
	switch (result) {
	case 0:
		/*
		 * Work around broken getaddrinfo() implementations that
		 * fail to set ai_canonname on first entry.
		 */
		cur = ai;
		while (cur != NULL && cur->ai_canonname == NULL &&
		       cur->ai_next != NULL) {
			cur = cur->ai_next;
		}
		if (cur != NULL && cur->ai_canonname != NULL &&
		    strcasecmp(cur->ai_canonname, namebuf) != 0)
		{
			if ((zone_options & DNS_ZONEOPT_WARNMXCNAME) != 0) {
				level = ISC_LOG_WARNING;
			}
			if ((zone_options & DNS_ZONEOPT_IGNOREMXCNAME) == 0) {
				if (!logged(namebuf, ERR_IS_MXCNAME)) {
					dns_zone_log(zone, level,
						     "%s/MX '%s' (out of zone)"
						     " is a CNAME '%s' "
						     "(illegal)",
						     ownerbuf, namebuf,
						     cur->ai_canonname);
					add(namebuf, ERR_IS_MXCNAME);
				}
				if (level == ISC_LOG_ERROR) {
					answer = false;
				}
			}
		}
		freeaddrinfo(ai);
		return (answer);

	case EAI_NONAME:
#if defined(EAI_NODATA) && (EAI_NODATA != EAI_NONAME)
	case EAI_NODATA:
#endif /* if defined(EAI_NODATA) && (EAI_NODATA != EAI_NONAME) */
		if (!logged(namebuf, ERR_NO_ADDRESSES)) {
			dns_zone_log(zone, ISC_LOG_ERROR,
				     "%s/MX '%s' (out of zone) "
				     "has no addresses records (A or AAAA)",
				     ownerbuf, namebuf);
			add(namebuf, ERR_NO_ADDRESSES);
		}
		/* XXX950 make fatal for 9.5.0. */
		return (true);

	default:
		if (!logged(namebuf, ERR_LOOKUP_FAILURE)) {
			dns_zone_log(zone, ISC_LOG_WARNING,
				     "getaddrinfo(%s) failed: %s", namebuf,
				     gai_strerror(result));
			add(namebuf, ERR_LOOKUP_FAILURE);
		}
		return (true);
	}
}

static bool
checksrv(dns_zone_t *zone, const dns_name_t *name, const dns_name_t *owner) {
	struct addrinfo hints, *ai, *cur;
	char namebuf[DNS_NAME_FORMATSIZE + 1];
	char ownerbuf[DNS_NAME_FORMATSIZE];
	int result;
	int level = ISC_LOG_ERROR;
	bool answer = true;

	memset(&hints, 0, sizeof(hints));
	hints.ai_flags = AI_CANONNAME;
	hints.ai_family = PF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = IPPROTO_TCP;

	dns_name_format(name, namebuf, sizeof(namebuf) - 1);
	/*
	 * Turn off search.
	 */
	if (dns_name_countlabels(name) > 1U) {
		strlcat(namebuf, ".", sizeof(namebuf));
	}
	dns_name_format(owner, ownerbuf, sizeof(ownerbuf));

	result = getaddrinfo(namebuf, NULL, &hints, &ai);
	dns_name_format(name, namebuf, sizeof(namebuf) - 1);
	switch (result) {
	case 0:
		/*
		 * Work around broken getaddrinfo() implementations that
		 * fail to set ai_canonname on first entry.
		 */
		cur = ai;
		while (cur != NULL && cur->ai_canonname == NULL &&
		       cur->ai_next != NULL) {
			cur = cur->ai_next;
		}
		if (cur != NULL && cur->ai_canonname != NULL &&
		    strcasecmp(cur->ai_canonname, namebuf) != 0)
		{
			if ((zone_options & DNS_ZONEOPT_WARNSRVCNAME) != 0) {
				level = ISC_LOG_WARNING;
			}
			if ((zone_options & DNS_ZONEOPT_IGNORESRVCNAME) == 0) {
				if (!logged(namebuf, ERR_IS_SRVCNAME)) {
					dns_zone_log(zone, level,
						     "%s/SRV '%s'"
						     " (out of zone) is a "
						     "CNAME '%s' (illegal)",
						     ownerbuf, namebuf,
						     cur->ai_canonname);
					add(namebuf, ERR_IS_SRVCNAME);
				}
				if (level == ISC_LOG_ERROR) {
					answer = false;
				}
			}
		}
		freeaddrinfo(ai);
		return (answer);

	case EAI_NONAME:
#if defined(EAI_NODATA) && (EAI_NODATA != EAI_NONAME)
	case EAI_NODATA:
#endif /* if defined(EAI_NODATA) && (EAI_NODATA != EAI_NONAME) */
		if (!logged(namebuf, ERR_NO_ADDRESSES)) {
			dns_zone_log(zone, ISC_LOG_ERROR,
				     "%s/SRV '%s' (out of zone) "
				     "has no addresses records (A or AAAA)",
				     ownerbuf, namebuf);
			add(namebuf, ERR_NO_ADDRESSES);
		}
		/* XXX950 make fatal for 9.5.0. */
		return (true);

	default:
		if (!logged(namebuf, ERR_LOOKUP_FAILURE)) {
			dns_zone_log(zone, ISC_LOG_WARNING,
				     "getaddrinfo(%s) failed: %s", namebuf,
				     gai_strerror(result));
			add(namebuf, ERR_LOOKUP_FAILURE);
		}
		return (true);
	}
}

isc_result_t
setup_logging(isc_mem_t *mctx, FILE *errout, isc_log_t **logp) {
	isc_logdestination_t destination;
	isc_logconfig_t *logconfig = NULL;
	isc_log_t *log = NULL;

	isc_log_create(mctx, &log, &logconfig);
	isc_log_registercategories(log, categories);
	isc_log_setcontext(log);
	dns_log_init(log);
	dns_log_setcontext(log);
	cfg_log_init(log);
	ns_log_init(log);

	destination.file.stream = errout;
	destination.file.name = NULL;
	destination.file.versions = ISC_LOG_ROLLNEVER;
	destination.file.maximum_size = 0;
	isc_log_createchannel(logconfig, "stderr", ISC_LOG_TOFILEDESC,
			      ISC_LOG_DYNAMIC, &destination, 0);

	RUNTIME_CHECK(isc_log_usechannel(logconfig, "stderr", NULL, NULL) ==
		      ISC_R_SUCCESS);

	*logp = log;
	return (ISC_R_SUCCESS);
}

/*% scan the zone for oversize TTLs */
static isc_result_t
check_ttls(dns_zone_t *zone, dns_ttl_t maxttl) {
	isc_result_t result;
	dns_db_t *db = NULL;
	dns_dbversion_t *version = NULL;
	dns_dbnode_t *node = NULL;
	dns_dbiterator_t *dbiter = NULL;
	dns_rdatasetiter_t *rdsiter = NULL;
	dns_rdataset_t rdataset;
	dns_fixedname_t fname;
	dns_name_t *name;
	name = dns_fixedname_initname(&fname);
	dns_rdataset_init(&rdataset);

	CHECK(dns_zone_getdb(zone, &db));
	INSIST(db != NULL);

	CHECK(dns_db_newversion(db, &version));
	CHECK(dns_db_createiterator(db, 0, &dbiter));

	for (result = dns_dbiterator_first(dbiter); result == ISC_R_SUCCESS;
	     result = dns_dbiterator_next(dbiter))
	{
		result = dns_dbiterator_current(dbiter, &node, name);
		if (result == DNS_R_NEWORIGIN) {
			result = ISC_R_SUCCESS;
		}
		CHECK(result);

		CHECK(dns_db_allrdatasets(db, node, version, 0, &rdsiter));
		for (result = dns_rdatasetiter_first(rdsiter);
		     result == ISC_R_SUCCESS;
		     result = dns_rdatasetiter_next(rdsiter))
		{
			dns_rdatasetiter_current(rdsiter, &rdataset);
			if (rdataset.ttl > maxttl) {
				char nbuf[DNS_NAME_FORMATSIZE];
				char tbuf[255];
				isc_buffer_t b;
				isc_region_t r;

				dns_name_format(name, nbuf, sizeof(nbuf));
				isc_buffer_init(&b, tbuf, sizeof(tbuf) - 1);
				CHECK(dns_rdatatype_totext(rdataset.type, &b));
				isc_buffer_usedregion(&b, &r);
				r.base[r.length] = 0;

				dns_zone_log(zone, ISC_LOG_ERROR,
					     "%s/%s TTL %d exceeds "
					     "maximum TTL %d",
					     nbuf, tbuf, rdataset.ttl, maxttl);
				dns_rdataset_disassociate(&rdataset);
				CHECK(ISC_R_RANGE);
			}
			dns_rdataset_disassociate(&rdataset);
		}
		if (result == ISC_R_NOMORE) {
			result = ISC_R_SUCCESS;
		}
		CHECK(result);

		dns_rdatasetiter_destroy(&rdsiter);
		dns_db_detachnode(db, &node);
	}

	if (result == ISC_R_NOMORE) {
		result = ISC_R_SUCCESS;
	}

cleanup:
	if (node != NULL) {
		dns_db_detachnode(db, &node);
	}
	if (rdsiter != NULL) {
		dns_rdatasetiter_destroy(&rdsiter);
	}
	if (dbiter != NULL) {
		dns_dbiterator_destroy(&dbiter);
	}
	if (version != NULL) {
		dns_db_closeversion(db, &version, false);
	}
	if (db != NULL) {
		dns_db_detach(&db);
	}

	return (result);
}

/*% load the zone */
isc_result_t
load_zone(isc_mem_t *mctx, const char *zonename, const char *filename,
	  dns_masterformat_t fileformat, const char *classname,
	  dns_ttl_t maxttl, dns_zone_t **zonep) {
	isc_result_t result;
	dns_rdataclass_t rdclass;
	isc_textregion_t region;
	isc_buffer_t buffer;
	dns_fixedname_t fixorigin;
	dns_name_t *origin;
	dns_zone_t *zone = NULL;

	REQUIRE(zonep == NULL || *zonep == NULL);

	if (debug) {
		fprintf(stderr, "loading \"%s\" from \"%s\" class \"%s\"\n",
			zonename, filename, classname);
	}

	CHECK(dns_zone_create(&zone, mctx));

	dns_zone_settype(zone, dns_zone_primary);

	isc_buffer_constinit(&buffer, zonename, strlen(zonename));
	isc_buffer_add(&buffer, strlen(zonename));
	origin = dns_fixedname_initname(&fixorigin);
	CHECK(dns_name_fromtext(origin, &buffer, dns_rootname, 0, NULL));
	CHECK(dns_zone_setorigin(zone, origin));
	dns_zone_setdbtype(zone, 1, (const char *const *)dbtype);
	CHECK(dns_zone_setfile(zone, filename, fileformat,
			       &dns_master_style_default));
	if (journal != NULL) {
		CHECK(dns_zone_setjournal(zone, journal));
	}

	DE_CONST(classname, region.base);
	region.length = strlen(classname);
	CHECK(dns_rdataclass_fromtext(&rdclass, &region));

	dns_zone_setclass(zone, rdclass);
	dns_zone_setoption(zone, zone_options, true);
	dns_zone_setoption(zone, DNS_ZONEOPT_NOMERGE, nomerge);

	dns_zone_setmaxttl(zone, maxttl);

	if (docheckmx) {
		dns_zone_setcheckmx(zone, checkmx);
	}
	if (docheckns) {
		dns_zone_setcheckns(zone, checkns);
	}
	if (dochecksrv) {
		dns_zone_setchecksrv(zone, checksrv);
	}

	CHECK(dns_zone_load(zone, false));

	/*
	 * When loading map files we can't catch oversize TTLs during
	 * load, so we check for them here.
	 */
	if (fileformat == dns_masterformat_map && maxttl != 0) {
		CHECK(check_ttls(zone, maxttl));
	}

	if (zonep != NULL) {
		*zonep = zone;
		zone = NULL;
	}

cleanup:
	if (zone != NULL) {
		dns_zone_detach(&zone);
	}
	return (result);
}

/*% dump the zone */
isc_result_t
dump_zone(const char *zonename, dns_zone_t *zone, const char *filename,
	  dns_masterformat_t fileformat, const dns_master_style_t *style,
	  const uint32_t rawversion) {
	isc_result_t result;
	FILE *output = stdout;
	const char *flags;

	flags = (fileformat == dns_masterformat_text) ? "w" : "wb";

	if (debug) {
		if (filename != NULL && strcmp(filename, "-") != 0) {
			fprintf(stderr, "dumping \"%s\" to \"%s\"\n", zonename,
				filename);
		} else {
			fprintf(stderr, "dumping \"%s\"\n", zonename);
		}
	}

	if (filename != NULL && strcmp(filename, "-") != 0) {
		result = isc_stdio_open(filename, flags, &output);

		if (result != ISC_R_SUCCESS) {
			fprintf(stderr,
				"could not open output "
				"file \"%s\" for writing\n",
				filename);
			return (ISC_R_FAILURE);
		}
	}

	result = dns_zone_dumptostream(zone, output, fileformat, style,
				       rawversion);
	if (output != stdout) {
		(void)isc_stdio_close(output);
	}

	return (result);
}

#ifdef _WIN32
void
InitSockets(void) {
	WORD wVersionRequested;
	WSADATA wsaData;
	int err;

	wVersionRequested = MAKEWORD(2, 0);

	err = WSAStartup(wVersionRequested, &wsaData);
	if (err != 0) {
		fprintf(stderr, "WSAStartup() failed: %d\n", err);
		exit(1);
	}
}

void
DestroySockets(void) {
	WSACleanup();
}
#endif /* ifdef _WIN32 */
