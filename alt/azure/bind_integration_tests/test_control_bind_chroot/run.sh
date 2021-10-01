#!/bin/bash -eux

source ./common/assertions
source ./common/service

BIND_SYSCONFIG='/etc/sysconfig/bind'
ENABLE_NEW_CHROOT='CHROOT="-t /var/lib/bind"'
DISABLE_NEW_CHROOT='#CHROOT="-t /var/lib/bind"'

# test bind-chroot

function cleanup_chroot() {
    sed -i '/CHROOT=/d' "$BIND_SYSCONFIG"
}

function assert_status () {
    local status=$(control bind-chroot)
    if [ "$status" != "$1" ]; then
        printf 'Actual status: "%s" is not equal to expected: "%s"\n' "$status" "$1"
        exit 1
    fi
}

function setup_chroot_data() {
    cleanup_chroot
    cat >> "$BIND_SYSCONFIG" <<< "$1"
}

function setup_chrooted() {
    setup_chroot_data "$ENABLE_NEW_CHROOT"
}

function setup_unchrooted() {
    setup_chroot_data "$DISABLE_NEW_CHROOT"
}

function assert_enabled() {
    res="$(grep CHROOT "$BIND_SYSCONFIG")"
    assert_str_equal "$res" "$ENABLE_NEW_CHROOT"
}

function assert_disabled() {
    res="$(grep CHROOT "$BIND_SYSCONFIG")"
    assert_str_equal "$res" "$DISABLE_NEW_CHROOT"
}

function assert_runtime_enabled() {
    cmdline="$(xargs -0 < /proc/$(pidof named)/cmdline)"
    assert_str_in ' -t /var/lib/bind' "$cmdline"
}

function assert_runtime_disabled() {
    cmdline="$(xargs -0 < /proc/$(pidof named)/cmdline)"
    assert_str_not_in ' -t /var/lib/bind' "$cmdline"
}

# status tests
echo 'Running `control bind-chroot status` tests'
cleanup_chroot
assert_status 'unknown'

setup_chroot_data "@$ENABLE_NEW_CHROOT"
assert_status 'unknown'

setup_chroot_data "$ENABLE_NEW_CHROOT@"
assert_status 'unknown'

setup_chrooted
assert_status 'enabled'

setup_unchrooted
assert_status 'disabled'

# enabled tests
echo 'Running `control bind-chroot enabled` tests'
cleanup_chroot
res=$(control bind-chroot enabled 2>&1 ||:)
assert_str_equal "$res" 'control: bind-chroot: Requested enabled, got unknown'

setup_chrooted
enable_chroot
assert_enabled
assert_runtime_enabled

setup_unchrooted
enable_chroot
assert_enabled
assert_runtime_enabled

# disable tests
echo 'Running `control bind-chroot disabled` tests'
cleanup_chroot
res=$(control bind-chroot disabled 2>&1 ||:)
assert_str_equal "$res" 'control: bind-chroot: Requested disabled, got unknown'

setup_chrooted
disable_chroot
assert_disabled
assert_runtime_disabled

setup_unchrooted
disable_chroot
assert_disabled
assert_runtime_disabled

# subsequent change
echo 'Running `control bind-chroot subsequent enabled/disabled` tests'
setup_chrooted
control bind-chroot disabled
assert_status 'disabled'
assert_disabled
control bind-chroot enabled
assert_status 'enabled'
assert_enabled
restart
assert_runtime_enabled

setup_unchrooted
control bind-chroot enabled
assert_status 'enabled'
assert_enabled
control bind-chroot disabled
assert_status 'disabled'
assert_disabled
restart
assert_runtime_disabled
