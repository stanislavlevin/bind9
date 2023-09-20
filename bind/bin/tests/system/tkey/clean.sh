#!/bin/sh

# Copyright (C) Internet Systems Consortium, Inc. ("ISC")
#
# SPDX-License-Identifier: MPL-2.0
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.  If a copy of the MPL was not distributed with this
# file, you can obtain one at https://mozilla.org/MPL/2.0/.
#
# See the COPYRIGHT file distributed with this work for additional
# information regarding copyright ownership.

set -e

rm -f ./K*
rm -f ./dig.out.*
rm -f ./rndc.out.*
rm -f ns*/K*
rm -f ns*/_default.tsigkeys
rm -f ns*/managed-keys.bind*
rm -f ns*/named.conf
rm -f ns*/named.conf-e
rm -f ns*/named.lock
rm -f ns*/named.memstats
rm -f ns*/named.run
