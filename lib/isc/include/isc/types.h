/*
 * Copyright (C) 1999, 2000  Internet Software Consortium.
 * 
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS" AND INTERNET SOFTWARE CONSORTIUM DISCLAIMS
 * ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL INTERNET SOFTWARE
 * CONSORTIUM BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
 * DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
 * PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
 * ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
 * SOFTWARE.
 */

#ifndef ISC_TYPES_H
#define ISC_TYPES_H 1

#include <isc/int.h>
#include <isc/boolean.h>
#include <isc/list.h>

/***
 *** Core Types.  Alphabetized by defined type.
 ***/

typedef struct isc_bitstring		isc_bitstring_t;
typedef struct isc_buffer		isc_buffer_t;
typedef ISC_LIST(isc_buffer_t)		isc_bufferlist_t;
typedef struct isc_event		isc_event_t;
typedef ISC_LIST(struct isc_event)	isc_eventlist_t;
typedef unsigned int			isc_eventtype_t;
typedef struct isc_interface		isc_interface_t;
typedef struct isc_interfaceiter	isc_interfaceiter_t;
typedef struct isc_interval		isc_interval_t;
typedef struct isc_lex			isc_lex_t;
typedef struct isc_log 			isc_log_t;
typedef struct isc_logcategory		isc_logcategory_t;
typedef struct isc_logconfig		isc_logconfig_t;
typedef struct isc_logmodule		isc_logmodule_t;
typedef struct isc_mem			isc_mem_t;
typedef struct isc_mempool		isc_mempool_t;
typedef struct isc_msgcat		isc_msgcat_t;
typedef struct isc_netaddr		isc_netaddr_t;
typedef struct isc_region		isc_region_t;
typedef unsigned int			isc_result_t;
typedef struct isc_rwlock		isc_rwlock_t;
typedef struct isc_sockaddr		isc_sockaddr_t;
typedef struct isc_socket		isc_socket_t;
typedef struct isc_socketevent		isc_socketevent_t;
typedef struct isc_socketmgr		isc_socketmgr_t;
typedef struct isc_task			isc_task_t;
typedef struct isc_taskmgr		isc_taskmgr_t;
typedef struct isc_textregion		isc_textregion_t;
typedef struct isc_time			isc_time_t;
typedef struct isc_timer		isc_timer_t;
typedef struct isc_timermgr		isc_timermgr_t;

typedef void (*isc_taskaction_t)(isc_task_t *, isc_event_t *);

#endif /* ISC_TYPES_H */
