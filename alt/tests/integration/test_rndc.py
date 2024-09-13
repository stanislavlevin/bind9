from pathlib import Path
from tempfile import mkstemp
import os
import re
import shutil
import subprocess

import pytest


def rndc(args):
    return subprocess.run(
        ["rndc", *args], check=False, text=True, capture_output=True
    )


# rndc subcommand and its default configured path
RNDC_PATHS = (
    (["dumpdb"], "/var/run/named/named_dump.db"),  # dump-file
    (["recursing"], "/var/run/named/named.recursing"),  # recursing-file
    (["secroots"], "/var/run/named/named.secroots"),  # secroots-file
    (["stats"], "/var/run/named/named.stats"),  # statistics-file
)


def idrndc_paths(val):
    """return rndc subcommand as test id"""
    return "rndc_" + "_".join(val[0])


@pytest.fixture
def clean_rndc_key():
    rndc_key_path = Path("/var/lib/bind/etc/rndc.key")
    orig_stat = rndc_key_path.stat()
    _, tmp_file = mkstemp()
    tmp_path = Path(tmp_file)

    def _repl(m):
        return m.group(1) + '"@RNDC_KEY@";'

    with tmp_path.open("w") as nf:
        with rndc_key_path.open() as f:
            for l in f:
                if "secret " in l:
                    l = re.sub(r'(\s*secret\s+)"(.*)";$', _repl, l)
                nf.write(l)
    shutil.copy2(tmp_path, rndc_key_path)
    os.chown(rndc_key_path, orig_stat.st_uid, orig_stat.st_gid)
    rndc_key_path.chmod(orig_stat.st_mode)
    tmp_path.unlink()


def rndc_key():
    rndc_key_path = Path("/var/lib/bind/etc/rndc.key")
    with rndc_key_path.open() as f:
        for l in f:
            m = re.match(r'(\s*secret\s+)"(.*)";$', l)
            if m is not None:
                return m.group(2)

    return None


def test_rndc(chroot, caps, named_service):
    named_service.restart()
    rndc_result = rndc(["status"])
    assert rndc_result.returncode == 0
    assert not rndc_result.stderr
    assert "server is up and running" in rndc_result.stdout.splitlines()


def test_rndc_keygen(clean_rndc_key, named_service):
    # default template key
    assert rndc_key() == "@RNDC_KEY@"
    # regenerate rndc key
    named_service.restart()
    assert rndc_key() != "@RNDC_KEY@"


@pytest.mark.parametrize("rndc_paths", RNDC_PATHS, ids=idrndc_paths)
def test_rndc_default_paths_chroot_debug(
    rndc_paths, control_chroot, control_debug, caps, named_service
):
    """
    Check rndc works with default configured paths as follows:
    - control bind-chroot enabled
      - control bind-debug enabled
        - rndc stats (, ...) works (exit code is 0, file appears)
    """
    rndc_cmd, rndc_cmdfile = rndc_paths

    control_chroot.enabled()
    control_debug.enabled()
    named_service.restart()
    chroot_path = Path("/var/lib/bind")
    rndc_cmdfile_path = chroot_path / Path(rndc_cmdfile).relative_to("/")
    rndc_cmdfile_path.unlink(missing_ok=True)

    rndc_result = rndc(rndc_cmd)
    assert rndc_result.returncode == 0, rndc_result
    assert not rndc_result.stderr
    assert not rndc_result.stdout
    assert rndc_cmdfile_path.exists()
    assert rndc_cmdfile_path.is_file()


@pytest.mark.parametrize("rndc_paths", RNDC_PATHS, ids=idrndc_paths)
def test_rndc_default_paths_chroot_nondebug(
    rndc_paths, control_chroot, control_debug, caps, named_service
):
    """
    Check rndc works with default configured paths as follows:
    - control bind-chroot enabled
      - control bind-debug disabled
        - rndc stats (, ...) doesn't work (exit code is not 0, no file appears)
    """
    rndc_cmd, rndc_cmdfile = rndc_paths

    control_chroot.enabled()
    control_debug.disabled()
    named_service.restart()
    chroot_path = Path("/var/lib/bind")
    rndc_cmdfile_path = chroot_path / Path(rndc_cmdfile).relative_to("/")
    rndc_cmdfile_path.unlink(missing_ok=True)

    rndc_result = rndc(rndc_cmd)
    assert rndc_result.returncode == 1, rndc_result
    # actual stderr depends on command
    expected_err_msg = f"rndc: '{rndc_cmd[0]}' failed: permission denied"
    assert expected_err_msg in rndc_result.stderr.splitlines()
    assert not rndc_result.stdout
    assert not rndc_cmdfile_path.exists()


@pytest.mark.parametrize("rndc_paths", RNDC_PATHS, ids=idrndc_paths)
def test_rndc_default_paths_unchroot(
    rndc_paths, control_chroot, debug, caps, named_service
):
    """
    Check rndc works with default configured paths as follows:
    - control bind-chroot disabled
      # bind-debug doesn't impact on non-chrooted bind
      - control bind-debug enabled (, disabled)
        - rndc stats (, ...) works (exit code is 0, file appears)
    """
    rndc_cmd, rndc_cmdfile = rndc_paths

    control_chroot.disabled()
    named_service.restart()
    rndc_cmdfile_path = Path(rndc_cmdfile)
    rndc_cmdfile_path.unlink(missing_ok=True)

    rndc_result = rndc(rndc_cmd)
    assert rndc_result.returncode == 0, rndc_result
    assert not rndc_result.stderr
    assert not rndc_result.stdout
    assert rndc_cmdfile_path.exists()
    assert rndc_cmdfile_path.is_file()
