from pathlib import Path
from pwd import getpwnam
import os
import stat
import subprocess

import pytest


@pytest.fixture
def chroot_var_mode(control_debug):
    chroot_var = Path("/var/lib/bind/var")
    original_status = control_debug.status()

    def _chroot_var_mode(mode):
        chroot_var.chmod(mode)

    yield _chroot_var_mode

    if original_status != "unknown":
        getattr(control_debug, original_status)()


def find_writable_paths(root):
    cmd_args = ["runuser", "-u", "named", "--", "touch"]
    writable_paths = []

    def _writable_dir(d_path):
        f_path = d_path / ".test_write"
        res = subprocess.run(cmd_args + [f_path], check=False)
        if res.returncode == 0:
            f_path.unlink()
            return True
        return False

    def _writable_file(f_path):
        res = subprocess.run(cmd_args + [f_path], check=False)
        return res.returncode == 0

    d_path = Path(root)
    if _writable_dir(d_path):
        return [d_path]

    for root, dirs, files in os.walk(root):
        for f in files:
            f_path = Path(root) / f
            if _writable_file(f_path):
                writable_paths.append(str(f_path))

        for d in dirs:
            d_path = Path(root) / d
            if _writable_dir(d_path):
                writable_paths.append(str(d_path))
                dirs.remove(d)

    return writable_paths


@pytest.mark.parametrize("state", (0o710,))
def test_status_enabled(state, chroot_var_mode, control_debug):
    chroot_var_mode(state)
    assert control_debug.status() == "enabled"


@pytest.mark.parametrize("state", (0o700,))
def test_status_disabled(state, chroot_var_mode, control_debug):
    chroot_var_mode(state)
    assert control_debug.status() == "disabled"


@pytest.mark.parametrize("state", (0o770, 0o750, 0o755))
def test_status_unknown(state, chroot_var_mode, control_debug):
    chroot_var_mode(state)
    assert control_debug.status() == "unknown"


@pytest.mark.parametrize("initial", ("enabled", "disabled"))
@pytest.mark.parametrize("state", ("enabled", "disabled"))
def test_state_from_initial(control_debug, initial, state):
    getattr(control_debug, initial)()
    assert control_debug.status() == initial
    getattr(control_debug, state)()
    assert control_debug.status() == state


@pytest.mark.parametrize("state", ("enabled", "disabled"))
def test_state_from_unknown(control_debug, chroot_var_mode, state):
    chroot_var_mode(0o770)
    assert control_debug.status() == "unknown"
    getattr(control_debug, state)()
    assert control_debug.status() == state


def test_state_runtime_debug_enabled(control_debug, named_service):
    control_debug.enabled()
    mstat = Path("/var/lib/bind/var").stat()
    assert mstat.st_uid == 0
    assert mstat.st_gid == getpwnam("named").pw_gid
    assert stat.S_ISDIR(mstat.st_mode)
    assert stat.S_IMODE(mstat.st_mode) == 0o710
    named_service.restart()


def test_state_runtime_debug_disabled(control_debug, named_service):
    control_debug.disabled()
    mstat = Path("/var/lib/bind/var").stat()
    assert mstat.st_uid == 0
    assert mstat.st_gid == getpwnam("named").pw_gid
    assert stat.S_ISDIR(mstat.st_mode)
    assert stat.S_IMODE(mstat.st_mode) == 0o700
    named_service.restart()


def test_readonly_chroot_var(control_debug):
    """
    read-only chroot's var is controlled by bind-debug control,
    enabled => writable (chmod g+x /var/lib/bind/var)

    [root@783b5f746978 alt]# ls -la /var/lib/bind/var/
    drwx--x--- 4 root named 4096 Mar  6 15:14 .
    drwx--x--- 1 root named 4096 Mar  6 14:16 ..
    drwx--x--- 3 root named 4096 Mar  6 15:14 log
    drwx--x--- 3 root named 4096 Mar  6 14:47 run

    disabled => read-only (chmod g-x /var/lib/bind/var) (default)

    [root@783b5f746978 alt]# ls -la /var/lib/bind/var/
    total 20
    drwx------ 4 root named 4096 Mar  6 15:14 .
    drwx--x--- 1 root named 4096 Mar  6 14:16 ..
    drwx--x--- 3 root named 4096 Mar  6 15:14 log
    drwx--x--- 3 root named 4096 Mar  6 14:47 run
    """
    control_debug.disabled()
    writable_paths = sorted(find_writable_paths("/var/lib/bind"))
    assert writable_paths == sorted(
        ["/var/lib/bind/zone", "/var/lib/bind/etc/zone"]
    )


def test_writable_chroot_var(control_debug):
    control_debug.enabled()
    writable_paths = sorted(find_writable_paths("/var/lib/bind"))
    assert writable_paths == sorted(
        [
            "/var/lib/bind/zone",
            "/var/lib/bind/etc/zone",
            "/var/lib/bind/var/log/named",
            "/var/lib/bind/var/run/named",
        ]
    )
