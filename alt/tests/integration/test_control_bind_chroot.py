from pathlib import Path
import subprocess

import pytest


def named_root():
    named_pid = subprocess.run(
        ["pidof", "named"], check=True, text=True, capture_output=True
    ).stdout.strip()
    return (Path("/proc") / named_pid / "root").resolve(strict=True)


@pytest.mark.parametrize("state", ("enabled", "disabled", "unknown"))
def test_status(chroot_sysconfig, control_chroot, state):
    getattr(chroot_sysconfig, state)()
    assert control_chroot.status() == state


@pytest.mark.parametrize("data", ("@CHROOT=", "CHROOT=@"))
def test_status_unknown_broken(chroot_sysconfig, control_chroot, data):
    chroot_sysconfig.clean()
    chroot_sysconfig._append(data)
    assert control_chroot.status() == "unknown"


@pytest.mark.parametrize("initial", ("enabled", "disabled"))
@pytest.mark.parametrize("state", ("enabled", "disabled"))
def test_state_from_initial(chroot_sysconfig, control_chroot, initial, state):
    getattr(chroot_sysconfig, initial)()
    getattr(control_chroot, state)()
    assert control_chroot.status() == state


@pytest.mark.parametrize("state", ("enabled", "disabled"))
def test_state_from_unknown(chroot_sysconfig, control_chroot, state):
    chroot_sysconfig.unknown()
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        getattr(control_chroot, state)()
    assert exc_info.value.stderr.strip() == (
        f"control: bind-chroot: Requested {state}, got unknown"
    )


@pytest.mark.parametrize(
    "state, exp_root",
    [("enabled", "/var/lib/bind"), ("disabled", "/")],
    ids=["enabled_chroot", "disabled_chroot"],
)
def test_state_runtime(caps, named_service, control_chroot, state, exp_root):
    getattr(control_chroot, state)()
    named_service.restart()
    assert named_root() == Path(exp_root)
