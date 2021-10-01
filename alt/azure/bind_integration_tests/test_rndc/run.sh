#!/bin/bash -exu

source ./common/service
source ./common/assertions

RNDC_KEY_PATH='/etc/bind/rndc.key'

function teardown {
    stop
    # let named regenerate rndc.key
    echo -e 'key "rndc-key" {\n\tsecret "@RNDC_KEY@";\n};' > "$RNDC_KEY_PATH"
}
trap teardown EXIT

TEST_DIR="$(dirname "${BASH_SOURCE[0]}")"

function main() {
    # tests
    echo 'Checking rndc status'
    status="$(rndc status)"
    assert_str_in 'server is up and running' "$status"
}

echo 'Checking rndc with chrooted named'
enable_chroot
main

echo 'Checking rndc with unchrooted named'
disable_chroot
main

echo 'Checking rndc warns about weak hmac-md5'
warn_message='warning: use of hmac-md5 for RNDC keys is deprecated; hmac-sha256 is now recommended'
stop
# generate weak key
confgen_status=$(rndc-confgen -A hmac-md5 -a -c "$RNDC_KEY_PATH" 2>&1)
assert_str_in "$warn_message" "$confgen_status"
start
status="$(rndc status 2>&1)"
assert_str_in "$warn_message" "$status"

# regenerate default
stop
confgen_status=$(rndc-confgen -a -c "$RNDC_KEY_PATH" 2>&1)
assert_str_not_in "$warn_message" "$confgen_status"
