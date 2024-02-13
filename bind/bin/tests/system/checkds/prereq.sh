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

SYSTEMTESTTOP=..
. $SYSTEMTESTTOP/conf.sh

if test -n "$PYTHON"; then
  if [ "$($PYTHON -c "import dns.version; print(dns.version.MAJOR)" 2>/dev/null)" -ge 2 ]; then
    :
  else
    echo_i "This test requires the dnspython >= 2.0.0 module." >&2
    exit 1
  fi
else
  echo_i "This test requires Python and the dnspython module." >&2
  exit 1
fi

exit 0
