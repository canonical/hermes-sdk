import hashlib
import os
from pathlib import Path

EXPECTED = {
    "hermes_bootstrap.py": "f242036b2d35b92283b9a7e97c7059e537607fc4b02026f657a6d00cb4683f69",
    "pm/environments.py": "ac5a9f09bc622a60aa616880be0906b07bec95bb8ad934924e931aa28dc8b777",
    "hermes_cli/_launchers.py": "9cf612547558a28a7840544a44c5f5ab866ee527a05f96000aefdf51cd7fcbcd",
    "hermes_cli/steward.py": "d365372909dd2b14d769c8df2972f7b0871e8ce294c7b18707f70e1f310ff8a7",
}

repo = Path(os.environ["HERMES_HOME"]) / "hermes-agent"
changed = []
for name, expected in EXPECTED.items():
    try:
        actual = hashlib.sha256((repo / name).read_bytes()).hexdigest()
    except OSError:
        actual = None
    if actual != expected:
        changed.append(name)

if changed:
    raise SystemExit(
        "Hermes packaging compatibility check failed. Upstream files changed or are unreadable:\n  "
        + "\n  ".join(changed)
        + "\nThe sealing script relies on behavior reviewed against Hermes 0.22.2.\n"
        "Review sealed-manifest resolution, dependency activation, launcher behavior, and external-update ownership.\n"
        "Adapt scripts/seal-hermes.py if needed, then verify a relocated, read-only SDK with a fresh HERMES_HOME.\n"
        "Only after that review, update EXPECTED in scripts/check-hermes-compatibility.py using sha256sum.\n"
        "Do not refresh the fingerprints merely to bypass this failure."
    )