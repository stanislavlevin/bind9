#!/bin/sh
#
# Copyright (C) Internet Systems Consortium, Inc. ("ISC")
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at https://mozilla.org/MPL/2.0/.
#
# See the COPYRIGHT file distributed with this work for additional
# information regarding copyright ownership.

if [ -n "${SOFTHSM2_CONF:-}" ] && command -v softhsm2-util >/dev/null; then
    SOFTHSM2_DIR=$(dirname "$SOFTHSM2_CONF")
    mkdir -p "${SOFTHSM2_DIR}/tokens"
    echo "directories.tokendir = ${SOFTHSM2_DIR}/tokens" > "${SOFTHSM2_CONF}"
    echo "objectstore.backend = file" >> "${SOFTHSM2_CONF}"
    echo "log.level = DEBUG" >> "${SOFTHSM2_CONF}"
    softhsm2-util --init-token --free --pin 1234 --so-pin 1234 --label "softhsm2" | awk '/^The token has been initialized and is reassigned to slot/ { print $NF }'

    if [ -n "${PKCS11_ENGINE:-}" ]; then
        OPENSSL_CONF_DIR=$(dirname "$OPENSSL_CONF")
        mkdir -p "${OPENSSL_CONF_DIR}"
        cat > "$OPENSSL_CONF"<<EOF
openssl_conf = openssl_init

[openssl_init]
engines = engine_section

[engine_section]
pkcs11 = pkcs11_section

[pkcs11_section]
engine_id = pkcs11
MODULE_PATH = $SOFTHSM_MODULE_PATH
init=0
EOF
    fi
fi
exit 0
