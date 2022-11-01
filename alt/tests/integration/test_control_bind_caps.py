import re
import subprocess

import pytest


def named_caps():
    named_pid = subprocess.run(
        ["pidof", "named"], check=True, text=True, capture_output=True
    ).stdout.strip()
    raw_caps = subprocess.run(
        ["getpcaps", named_pid], check=True, text=True, capture_output=True
    ).stderr.strip()
    caps = re.sub("^Capabilities for .*: =( )?", "", raw_caps)
    if not caps:
        return []
    return sorted(caps.split(","))


@pytest.mark.parametrize("state", ("enabled", "disabled", "unknown"))
def test_status(caps_sysconfig, control_caps, state):
    getattr(caps_sysconfig, state)()
    assert control_caps.status() == state


@pytest.mark.parametrize("data", ("@RETAIN_CAPS=", "RETAIN_CAPS=@"))
def test_status_unknown_broken(caps_sysconfig, control_caps, data):
    caps_sysconfig.clean()
    caps_sysconfig._append(data)
    assert control_caps.status() == "unknown"


@pytest.mark.parametrize("initial", ("enabled", "disabled"))
@pytest.mark.parametrize("state", ("enabled", "disabled"))
def test_state_from_initial(caps_sysconfig, control_caps, initial, state):
    getattr(caps_sysconfig, initial)()
    getattr(control_caps, state)()
    assert control_caps.status() == state


@pytest.mark.parametrize("state", ("enabled", "disabled"))
def test_state_from_unknown(caps_sysconfig, control_caps, state):
    caps_sysconfig.unknown()
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        getattr(control_caps, state)()
    assert exc_info.value.stderr.strip() == (
        f"control: bind-caps: Requested {state}, got unknown"
    )


@pytest.mark.parametrize(
    "state, exp_caps",
    [
        ("enabled", ["cap_net_bind_service", "cap_sys_resource+ep"]),
        ("disabled", []),
    ],
    ids=["enabled_caps", "disabled_caps"],
)
def test_state_runtime(chroot, named_service, control_caps, state, exp_caps):
    getattr(control_caps, state)()
    named_service.restart()
    assert named_caps() == exp_caps
