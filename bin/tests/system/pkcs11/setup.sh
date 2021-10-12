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

set -eu

SYSTEMTESTTOP=..
# shellcheck source=conf.sh
. "$SYSTEMTESTTOP/conf.sh"

echo_i "Generating keys for ${PKCS11_ENGINE:-Native PKCS#11}" >&2

infile=ns1/example.db.in

printf '%s' "${HSMPIN:-1234}" > pin
PWD=$(pwd)

copy_setports ns1/named.conf.in ns1/named.conf

get_random() {
    id_format="u2"
    if test -n "$PKCS11_ENGINE"; then
        id_format="x2"
    fi
    dd if=/dev/urandom bs=1 count=2 2>/dev/null | od -t"$id_format" -An | tr -d '[:blank:]'
}

genpkcs() (
    alg="$1"
    bits="$2"
    label="$3"
    alg_type="$5"
    id="$(get_random)"

    if [ -n "${PKCS11_ENGINE:-}" ]; then
        $PK11DEL_OPENSSL --label "$label" --type privkey >/dev/null ||:
        $PK11DEL_OPENSSL --label "$label" --type pubkey >/dev/null ||:
        $PK11GEN_OPENSSL --key-type "$alg_type" --id "$id" --label "$label" >/dev/null
    else
        $PK11DEL -l "$label" -w0 >/dev/null || true
        $PK11GEN -a "$alg" -b "$bits" -l "$label" -i "$id" >/dev/null
    fi
)

keyfrlab() (
    alg="$1"
    bits="$2"
    label="$3"
    zone="$4"
    alt_type="$5"
    shift 5

    $KEYFRLAB ${PKCS11_ENGINE:+-E $PKCS11_ENGINE} -a "$alg" -l "pkcs11:object=$label;pin-source=$PWD/pin" "$@" "$zone"
)

genzsk() (
    genpkcs "$@"
    keyfrlab "$@"
)

genksk() (
    genpkcs "$@"
    keyfrlab "$@" -f ksk
)

algs=

algs_to_check='rsasha256:2048 rsasha512:2048 ecdsap256sha256:256 ecdsap384sha384:384 ed25519:256 ed448:456'
if [ -n "${PKCS11_ENGINE:-}" ]; then
    # ed25519:ec@edwards25519:256 is not supported by libp11 (end of 2021)
    algs_to_check='rsasha256:2048:rsa@2048 rsasha512:2048:rsa@2048 ecdsap256sha256:256:ec@prime256v1 ecdsap384sha384:384:ec@prime384v1'
fi

for algbits in $algs_to_check; do
    alg=$(echo "$algbits" | cut -f 1 -d :)
    bits=$(echo "$algbits" | cut -f 2 -d :)
    alg_type=$(echo "$algbits" | cut -f 3 -d : | tr '@' ':')
    zone="$alg.example"
    zonefile="ns1/$alg.example.db"
    if $SHELL "$SYSTEMTESTTOP/testcrypto.sh" "$alg"; then
	echo "$alg" >> supported
	algs="$algs$alg "

	zsk1=$(genzsk "$alg" "$bits" "pkcs11-$alg-zsk1" "$zone" "$alg_type")
	zsk2=$(genzsk "$alg" "$bits" "pkcs11-$alg-zsk2" "$zone" "$alg_type")
	ksk1=$(genksk "$alg" "$bits" "pkcs11-$alg-ksk1" "$zone" "$alg_type")
	ksk2=$(genksk "$alg" "$bits" "pkcs11-$alg-ksk2" "$zone" "$alg_type")

	cat "$infile" "$zsk1.key" "$ksk1.key" > "$zonefile"
	$SIGNER ${PKCS11_ENGINE:+-E $PKCS11_ENGINE} -a -P -g -o "$zone" "$zonefile" > /dev/null
	cp "$zsk2.key" "ns1/$alg.zsk"
	cp "$ksk2.key" "ns1/$alg.ksk"
	mv "K$alg"* ns1/

	cat >> ns1/named.conf <<EOF
zone "$alg.example." {
	type primary;
	file "$alg.example.db.signed";
	allow-update { any; };
};

EOF
    fi
done
echo_i "Generated keys for ${PKCS11_ENGINE:-Native PKCS#11}: $algs"
