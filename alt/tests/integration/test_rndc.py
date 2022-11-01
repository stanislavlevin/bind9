from pathlib import Path
from tempfile import mkstemp
import os
import re
import shutil
import subprocess

import pytest


def rndc(args):
    return subprocess.run(
        ["rndc", *args], check=True, text=True, capture_output=True
    ).stdout.strip()


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
    assert "server is up and running" in rndc(["status"])


def test_rndc_keygen(clean_rndc_key, named_service):
    # default template key
    assert rndc_key() == "@RNDC_KEY@"
    # regenerate rndc key
    named_service.restart()
    assert rndc_key() != "@RNDC_KEY@"
