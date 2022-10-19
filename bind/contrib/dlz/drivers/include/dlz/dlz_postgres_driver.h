/*
 * Copyright (C) 2002 Stichting NLnet, Netherlands, stichting@nlnet.nl.
 * Copyright (C) Internet Systems Consortium, Inc. ("ISC")
 *
 * SPDX-License-Identifier: MPL-2.0
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0.  If a copy of the MPL was not distributed with this
 * file, you can obtain one at https://mozilla.org/MPL/2.0/.
 *
 * See the COPYRIGHT file distributed with this work for additional
 * information regarding copyright ownership.
 */

#ifndef DLZ_POSTGRES_DRIVER_H
#define DLZ_POSTGRES_DRIVER_H

isc_result_t
dlz_postgres_init(void);

void
dlz_postgres_clear(void);

#endif /* ifndef DLZ_POSTGRES_DRIVER_H */
