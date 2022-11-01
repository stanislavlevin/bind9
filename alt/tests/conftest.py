from pathlib import Path
from tempfile import mkstemp
import os
import re
import shutil
import subprocess

import pytest


class NamedService:
    def systemctl(self, *args, check=True):
        cmd_args = ["systemctl"]
        cmd_args.extend(args)
        cmd_args.append("bind")
        return subprocess.run(cmd_args, check=check)

    def start(self):
        self.systemctl("start")

    def restart(self):
        self.systemctl("restart")

    def stop(self):
        self.systemctl("stop")

    def disable(self):
        self.systemctl("disable")

    def is_active(self):
        return self.systemctl("is-active", check=False).returncode == 0


class BindControl:
    def __init__(self, facility):
        self.facility = facility

    def _run(self, args=[]):
        cmd_args = ["control", self.facility]
        cmd_args.extend(args)
        result = subprocess.run(
            cmd_args, check=True, text=True, capture_output=True
        )
        return result.stdout.strip()

    def status(self):
        return self._run(["status"])

    def enabled(self):
        self._run(["enabled"])

    def disabled(self):
        self._run(["disabled"])


class BindSysconfigOption:
    def __init__(self, name, enable, disable):
        self.sysconf_path = Path("/etc/sysconfig/bind")

        self.name = name
        self._enabled = enable
        self._disabled = disable

        # backup
        self._orig_stat = self.sysconf_path.stat()
        self._sysconf_path_backup = self.sysconf_path.with_name("bind.backup")
        shutil.copy2(self.sysconf_path, self._sysconf_path_backup)

    def restore(self):
        shutil.copy2(self._sysconf_path_backup, self.sysconf_path)
        os.chown(
            self.sysconf_path, self._orig_stat.st_uid, self._orig_stat.st_gid
        )

    def clean(self):
        orig_stat = self.sysconf_path.stat()
        _, tmp_file = mkstemp()
        tmp_path = Path(tmp_file)
        with tmp_path.open("w") as nf:
            with self.sysconf_path.open() as f:
                for l in f:
                    if not any(
                        (x for x in (self._enabled, self._disabled) if x in l)
                    ):
                        nf.write(l)
        shutil.copy2(tmp_path, self.sysconf_path)
        os.chown(self.sysconf_path, orig_stat.st_uid, orig_stat.st_gid)
        self.sysconf_path.chmod(orig_stat.st_mode)
        tmp_path.unlink()

    def _append(self, data):
        with self.sysconf_path.open("a") as f:
            f.write(data + "\n")

    def enabled(self):
        self.clean()
        self._append(self._enabled)

    def disabled(self):
        self.clean()
        self._append(self._disabled)

    def unknown(self):
        self.clean()

    def value(self):
        with self.sysconf_path.open() as f:
            for l in f:
                m = re.match(rf"\s*{self.name}=(.*)$", l)
                if m is not None:
                    return m.group(1)
        return None


@pytest.fixture
def caps_sysconfig():
    caps_sysconf = BindSysconfigOption(
        "RETAIN_CAPS", enable='RETAIN_CAPS="-r"', disable='#RETAIN_CAPS="-r"'
    )
    yield caps_sysconf
    caps_sysconf.restore()


@pytest.fixture
def chroot_sysconfig():
    chroot_sysconf = BindSysconfigOption(
        "CHROOT",
        enable='#CHROOT="-t /"',
        disable='CHROOT="-t /"',
    )
    yield chroot_sysconf
    chroot_sysconf.restore()


@pytest.fixture
def extraoptions_sysconfig():
    extraoptions_sysconf = BindSysconfigOption(
        "EXTRAOPTIONS", enable='EXTRAOPTIONS="-4"', disable='EXTRAOPTIONS=""'
    )
    yield extraoptions_sysconf
    extraoptions_sysconf.restore()


@pytest.fixture
def named_service():
    return NamedService()


@pytest.fixture(
    params=(
        pytest.param("enabled", id="enabled_caps"),
        pytest.param("disabled", id="disabled_caps"),
    ),
)
def caps(request, named_service):
    named_service.stop()
    subprocess.run(["control", "bind-caps", request.param], check=True)


@pytest.fixture(
    params=(
        pytest.param("enabled", id="enabled_chroot"),
        pytest.param("disabled", id="disabled_chroot"),
    ),
)
def chroot(request, named_service):
    named_service.stop()
    subprocess.run(["control", "bind-chroot", request.param], check=True)


@pytest.fixture
def control_caps():
    yield BindControl("bind-caps")


@pytest.fixture
def control_chroot():
    yield BindControl("bind-chroot")
