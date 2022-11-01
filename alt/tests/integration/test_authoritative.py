from pathlib import Path
import os
import pwd
import shutil
import subprocess
import textwrap

import pytest


NAMED_DIR = Path("/etc/bind")
LOCAL_CONF = NAMED_DIR / "local.conf"
ZONE_DIR = NAMED_DIR / "zone"

ZONE_CONF = textwrap.dedent(
    """\
    zone "{}" {{
        type master;
        file "{}";
    }};
    """
)

ZONE_TEXT = textwrap.dedent(
    """\
    $TTL    1D
    @       IN      SOA     server root.server (
                                    1397051952      ; serial
                                    5               ; refresh
                                    5               ; retry
                                    1814400         ; expire
                                    3600            ; ncache
                            )
            IN      NS      server
    server          A       127.0.0.1
    server          AAAA    ::1
    """
)


def get_rrecord(name, nameserver="localhost", rrtype="A"):
    cmd_args = ["dig", f"@{nameserver}", name, rrtype, "+short"]
    res = subprocess.run(cmd_args, check=True, capture_output=True, text=True)
    return sorted(res.stdout.splitlines()) if res.stdout else []


def named_file(path):
    """Set owner root:named and 0640 for file"""
    named_uid = pwd.getpwnam("named").pw_uid
    os.chown(path, 0, named_uid)
    path.chmod(0o640)


@pytest.fixture
def zone(request, named_service):
    named_service.stop()

    # backup local.conf
    orig_stat = LOCAL_CONF.stat()
    local_conf_bckup = LOCAL_CONF.with_name("local.conf.backup")
    shutil.copy2(LOCAL_CONF, local_conf_bckup)

    zone = "bind.test"
    zone_conf_path = NAMED_DIR / "local_test.conf"
    zone_path = ZONE_DIR / zone
    zone_conf_path.write_text(ZONE_CONF.format(zone, zone_path))
    named_file(zone_conf_path)

    with LOCAL_CONF.open("a") as f:
        f.write('include "{}";\n'.format(zone_conf_path))

    zone_path.write_text(ZONE_TEXT)
    named_file(zone_path)
    yield
    named_service.stop()
    shutil.copy2(local_conf_bckup, LOCAL_CONF)
    os.chown(LOCAL_CONF, orig_stat.st_uid, orig_stat.st_gid)
    zone_path.unlink(missing_ok=True)
    zone_conf_path.unlink(missing_ok=True)


def test_zone(zone, chroot, caps, named_service):
    named_service.restart()
    assert ["server.bind.test."] == get_rrecord("bind.test.", rrtype="NS")
    assert ["127.0.0.1"] == get_rrecord("server.bind.test.", rrtype="A")
    assert ["::1"] == get_rrecord("server.bind.test.", rrtype="AAAA")
