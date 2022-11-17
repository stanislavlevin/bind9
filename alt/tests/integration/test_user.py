from pathlib import Path
from pwd import getpwnam
import re
import subprocess


def named_ids():
    """Parse /proc/xxx/status for Uid and Gid"""
    named_pid = subprocess.run(
        ["pidof", "named"], check=True, text=True, capture_output=True
    ).stdout.strip()
    ids = {"uids": (), "gids": ()}
    pattern = re.compile(r"^(Uid|Gid):\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)$")
    with (Path("/proc") / named_pid / "status").open() as f:
        for l in f:
            m = pattern.match(l)
            if m is not None:
                groups = m.groups()
                if not ids["uids"] and groups[0] == "Uid":
                    ids["uids"] = groups[1:]
                if not ids["gids"] and groups[0] == "Gid":
                    ids["gids"] = groups[1:]
                if ids["uids"] and ids["gids"]:
                    break
    return ids


def test_default_named_user(chroot, caps, named_service):
    """Check if named run as `named` user"""
    named_service.restart()
    ids = named_ids()
    named_pw = getpwnam("named")
    assert ids["uids"] == (f"{named_pw.pw_uid}",) * 4
    assert ids["gids"] == (f"{named_pw.pw_gid}",) * 4
