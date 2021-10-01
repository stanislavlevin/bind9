#!/bin/bash -eux

source ./common/assertions
source ./common/service

BIND_SYSCONFIG='/etc/sysconfig/bind'
DEFAULT_CHROOT='CHROOT="-t /var/lib/bind"'
DISABLED_CHROOT="#$DEFAULT_CHROOT"
ENABLED_CAPS='RETAIN_CAPS="-r"'
DEFAULT_CAPS="#$ENABLED_CAPS"
DEFAULT_EXTRA='EXTRAOPTIONS=""'

RPMS_DIR='/root/rpms'

function remove_bind() {
    apt-get remove -y bind libbind bind-control
}

function install_new_bind() {
    apt-get install -y \
	"$RPMS_DIR"/bind-9*.rpm \
	"$RPMS_DIR"/libbind-9*.rpm
}

function install_current_bind() {
    apt-get install -y bind
}

function remove_bind_sysconfig() {
    rm -fv "$BIND_SYSCONFIG"*
}

function set_sysconf_extraoptions() {
    sed -i '/^EXTRAOPTIONS=/d' "$BIND_SYSCONFIG"
    cat >> "$BIND_SYSCONFIG" <<< "EXTRAOPTIONS=\"$1\""
}

function sysconf_extraoptions() {
    printf '%s' "$(grep '^EXTRAOPTIONS=' "$BIND_SYSCONFIG")"
}

function sysconf_chroot() {
    printf '%s' "$(grep '^#\?CHROOT=' "$BIND_SYSCONFIG")"
}

function sysconf_caps() {
    printf '%s' "$(grep '^#\?RETAIN_CAPS=' "$BIND_SYSCONFIG")"
}

function teardown() {
    echo "Clean up upgrade tests"
    remove_bind >/dev/null 2>&1 ||:
    remove_bind_sysconfig
    install_new_bind >/dev/null 2>&1 ||:
    apt-get install -y "$RPMS_DIR"/bind-utils-9*.rpm
}

# usually there is no cache in Docker container
apt-get update
trap teardown EXIT


# clean installation
echo 'Checking clean installation'
remove_bind
remove_bind_sysconfig
install_new_bind
assert_str_equal "$(sysconf_extraoptions)" "$DEFAULT_EXTRA"
assert_str_equal "$(sysconf_chroot)" "$DEFAULT_CHROOT"
assert_str_equal "$(sysconf_caps)" "$DEFAULT_CAPS"
restart

# upgrade of default installation
echo 'Checking upgrade (default installation)'
remove_bind
remove_bind_sysconfig
install_current_bind
install_new_bind
assert_str_equal "$(sysconf_extraoptions)" "$DEFAULT_EXTRA"
assert_str_equal "$(sysconf_chroot)" "$DEFAULT_CHROOT"
assert_str_equal "$(sysconf_caps)" "$DEFAULT_CAPS"
restart

echo 'Checking upgrade (customized installation: disabled chroot)'
remove_bind
remove_bind_sysconfig
install_current_bind
control bind-chroot disabled
install_new_bind
assert_str_equal "$(sysconf_extraoptions)" "$DEFAULT_EXTRA"
assert_str_equal "$(sysconf_chroot)" "$DISABLED_CHROOT"
assert_str_equal "$(sysconf_caps)" "$DEFAULT_CAPS"
restart

echo 'Checking upgrade (customized installation: enabled caps)'
remove_bind
remove_bind_sysconfig
install_current_bind
control bind-caps enabled
install_new_bind
assert_str_equal "$(sysconf_extraoptions)" "$DEFAULT_EXTRA"
assert_str_equal "$(sysconf_chroot)" "$DEFAULT_CHROOT"
assert_str_equal "$(sysconf_caps)" "$ENABLED_CAPS"
restart

echo 'Checking upgrade (customized installation: extraoptions)'
remove_bind
remove_bind_sysconfig
install_current_bind
set_sysconf_extraoptions '-4'
install_new_bind
assert_str_equal "$(sysconf_extraoptions)" 'EXTRAOPTIONS="-4"'
assert_str_equal "$(sysconf_chroot)" "$DEFAULT_CHROOT"
assert_str_equal "$(sysconf_caps)" "$DEFAULT_CAPS"
restart

echo 'Checking upgrade (customized installation: all)'
remove_bind
remove_bind_sysconfig
install_current_bind
control bind-chroot disabled
control bind-caps enabled
set_sysconf_extraoptions '-4'
install_new_bind
assert_str_equal "$(sysconf_chroot)" "$DISABLED_CHROOT"
assert_str_equal "$(sysconf_caps)" "$ENABLED_CAPS"
assert_str_equal "$(sysconf_extraoptions)" 'EXTRAOPTIONS="-4"'
restart
