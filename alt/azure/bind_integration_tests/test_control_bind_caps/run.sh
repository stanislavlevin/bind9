#!/bin/bash -exu

source ./common/service
source ./common/assertions

function teardown {
    stop
}
trap teardown EXIT

function named_caps() {
    caps_report="$(getpcaps $(pidof named) 2>&1)"
    printf "${caps_report#Capabilities for *: =}"
}

function main() {
    # disabled caps
    echo 'Caps disabled'
    control bind-caps disabled
    restart

    actual_caps=$(named_caps)
    assert_str_equal "$actual_caps" ''

    ###

    # retained caps
    echo 'Caps enabled'
    control bind-caps enabled
    restart

    actual_caps=$(named_caps)
    assert_str_equal "$actual_caps" ' cap_net_bind_service,cap_sys_resource+ep'
}

echo 'Checking bind-caps with chrooted named'
enable_chroot
main

echo 'Checking bind-caps with unchrooted named'
disable_chroot
main
