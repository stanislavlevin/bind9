from pathlib import Path
import subprocess

import pytest


class BindPackage:
    def __init__(self, rpmsdir="/root/rpms"):
        self.rpmsdir = Path(rpmsdir)
        self.sysconf_path = Path("/etc/sysconfig/bind")
        self.update_cache()

    def _apt_get(self, args):
        cmd_args = ["apt-get", *args]
        subprocess.run(cmd_args, check=True, text=True)

    def remove(self):
        self._apt_get(["remove", "-y", "bind", "libbind", "bind-control"])

    def install_new(self):
        self._apt_get(
            ["install", "-y", *sorted(self.rpmsdir.glob("*bind*9*.rpm"))],
        )

    def install_current(self):
        self._apt_get(["install", "-y", "bind"])

    def update_cache(self):
        self._apt_get(["update"])

    def remove_sysconfig(self):
        sysconf_dir = self.sysconf_path.parent
        for f in sysconf_dir.glob(self.sysconf_path.name + "*"):
            f.unlink()


@pytest.fixture
def bind_pkg():
    return BindPackage("/root/rpms")


@pytest.fixture
def purge_bind(bind_pkg):
    bind_pkg.remove()
    bind_pkg.remove_sysconfig()


@pytest.fixture
def install_new(bind_pkg):
    bind_pkg.install_new()


@pytest.fixture
def install_current(bind_pkg):
    bind_pkg.install_current()


@pytest.fixture
def upgrade(purge_bind, install_current, bind_pkg, named_service):
    """Purge bind, install current one, do some changes and upgrade"""

    def _customize(callback_changes=[]):
        for cb in callback_changes:
            cb()
        if callback_changes:
            named_service.restart()

        bind_pkg.install_new()

    return _customize


def test_clean_installation(
    purge_bind, install_new, control_caps, control_chroot
):
    """Default clean installation"""
    assert control_caps.status() == "disabled"
    assert control_chroot.status() == "enabled"


@pytest.mark.parametrize(
    "caps_state",
    ("disabled", "enabled"),
    ids=["disabled_caps", "enabled_caps"],
)
@pytest.mark.parametrize(
    "chroot_state",
    ("disabled", "enabled"),
    ids=["disabled_chroot", "enabled_chroot"],
)
@pytest.mark.parametrize(
    "extraoptions_state",
    (
        {"state": "disabled", "value": '""'},
        {"state": "enabled", "value": '"-4"'},
    ),
    ids=["disabled_extraoptions", "enabled_extraoptions"],
)
def test_upgrade_from_state(
    upgrade,
    control_caps,
    control_chroot,
    extraoptions_sysconfig,
    caps_state,
    chroot_state,
    extraoptions_state,
):
    """Upgrade from state"""
    upgrade(
        [
            getattr(control_chroot, chroot_state),
            getattr(control_caps, caps_state),
            getattr(extraoptions_sysconfig, extraoptions_state["state"]),
        ],
    )
    assert control_caps.status() == caps_state
    assert control_chroot.status() == chroot_state
    assert extraoptions_sysconfig.value() == extraoptions_state["value"]


def test_upgrade_restart_flag(upgrade, named_service):
    upgrade([named_service.disable, named_service.start])
    assert named_service.is_active() is True
