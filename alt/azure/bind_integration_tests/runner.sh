#!/bin/bash -eu

source ./common/service

function run_testsuite() {
    local result=
    tests_dir="$(dirname '${BASH_SOURCE[0]}')"
    for f in $(find "$tests_dir" -maxdepth 1 -type d -name 'test_*'); do
        f="$(basename "$f")"
        printf 'checking: "%s"\n' "$f"
        if ! /bin/bash --norc --noprofile -eu "./$f/run.sh"; then
            result=1
            printf 'test: "%s" failed\n' "$f"
        else
            result=${result:-0}
            printf 'test: "%s" passed\n' "$f"
        fi
    done
    return ${result:-1}
}

result=0

# Default: chrooted named
enable_chroot

run_testsuite
