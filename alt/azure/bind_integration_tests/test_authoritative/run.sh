#!/bin/bash -exu

source ./common/service
source ./common/assertions

LOCAL_CONF='/etc/bind/local.conf'
TEST_CONF='/etc/bind/local_test.conf'
TEST_ZONE='/etc/bind/zone/bind.test'

function teardown {
    sed -i '/local_test.conf/d' "$LOCAL_CONF"
    rm -f "$TEST_CONF"
    rm -f "$TEST_ZONE"
    stop
}
trap teardown EXIT

TEST_DIR="$(dirname "${BASH_SOURCE[0]}")"

# setup
cp "$TEST_DIR/data/local_test.conf" "$TEST_CONF"
printf 'include "%s";' "$TEST_CONF" >> "$LOCAL_CONF"
cp "$TEST_DIR/data/test.zone" "$TEST_ZONE"

enable_chroot

function main() {
    # tests
    local actual
    echo "Checking NS RRs"
    actual="$(dig @localhost +short NS bind.test.)"
    assert_str_equal "$actual" 'server.bind.test.'

    echo "Checking A RRs"
    actual="$(dig @localhost +short A server.bind.test.)"
    assert_str_equal "$actual" '127.0.0.1'

    echo "Checking AAAA RRs"
    actual="$(dig @localhost +short AAAA server.bind.test.)"
    assert_str_equal "$actual" '::1'
}

echo 'Checking own zone with chrooted named'
main

# run twice chrooted+unchrooted
disable_chroot
echo 'Checking own zone with unchrooted named'
main


