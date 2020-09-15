#!/bin/sh -e
#
# Copyright (C) Internet Systems Consortium, Inc. ("ISC")
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at https://mozilla.org/MPL/2.0/.
#
# See the COPYRIGHT file distributed with this work for additional
# information regarding copyright ownership.

SYSTEMTESTTOP=..
. $SYSTEMTESTTOP/conf.sh

copy_setports ../common/controls.conf.in ns2/controls.conf
copy_setports  ns1/named.conf.in ns1/named.conf
copy_setports  ns2/named01.conf.in ns2/named.conf
copy_setports  ns3/named1.conf.in ns3/named.conf
