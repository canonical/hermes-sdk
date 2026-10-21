import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil

# Run once after the source installer, with HERMES_HOME pointing into Craft's
# install directory. Turn that mutable source installation into a relocatable
# payload for Workshop's read-only SDK mount; user state lives in a separate home.
# The compatibility check must run first: these layouts are upstream contracts,
# not a general-purpose way to relocate arbitrary Python installations.
home = Path(os.environ["HERMES_HOME"]).resolve()
repo = home / "hermes-agent"

# Hermes keys dependency records by the canonical checkout path, not its version.
# Read the installer's committed environment before relocation changes that key.
# The manifest below will locate this environment without the build-time record.
key = hashlib.sha256(str(repo).encode()).hexdigest()[:16]
facts = json.loads((home / "installs" / key / "facts.json").read_text())
venv = Path(facts["packages"]["venv"]["environment"]).resolve()

# Reuse the installer's pinned interpreter rather than the build host's Python.
# The application and isolated PM runtime must both use this bundled toolchain.
tools = json.loads((home / "tools/facts.json").read_text())
python = home / "tools" / tools["packages"]["python"]["entry"] / "bin/python3"
assert venv.joinpath("pyvenv.cfg").is_file(), "Missing dependency environment"
assert python.is_file(), "Missing bundled Python"

# Leases protect mutable generations from Hermes' garbage collector. SDK updates
# own this immutable generation instead. Removing its opt-in marker makes Hermes
# skip lease creation, which would otherwise write .leases into the read-only SDK.
# The marker is beside the venv, at the generation root, not inside the venv.
(venv.parent / ".lease-managed").unlink(missing_ok=True)

# PM has its own dependency graph, separate from the application's environment.
# A sealed manifest makes Hermes require <payload>/pm-runtime, so move the
# installer's selected PM generation there rather than rebuilding it at startup.
pm_state = home / "installs" / key / "pm-runtime"
selected = json.loads((pm_state / "selected.json").read_text())
runtime = home / "pm-runtime"
shutil.move(str(pm_state / selected["generation"]), runtime)
(runtime / ".lease-managed").unlink(missing_ok=True)

# PM's sealed-runtime marker resolves paths relative to the runtime directory.
# Python may be in the sibling tools directory; site-packages must stay inside
# pm-runtime. PM launches the bundled Python with these packages explicitly,
# avoiding the moved venv's build-time interpreter links and console scripts.
site = next(runtime.glob("lib/python*/site-packages"))
(runtime / "pm-runtime.json").write_text(json.dumps({
    "python": os.path.relpath(python, runtime),
    "sitePackages": str(site.relative_to(runtime)),
}) + "\n")

# Hermes discovers this manifest beside the checkout. Its paths are relative to
# the payload root, unlike the installer's absolute dependency-state paths.
# Keep the application environment in place and point directly to it; no copying
# into the user's HERMES_HOME or rewriting of the old facts record is needed.
launcher = repo / ".hermes/bin/hermes"
manifest = {
    "repo": "hermes-agent",
    "venv": str(venv.relative_to(home)),
    "store": "tools",
    "runtime": {
        "storePython": str(python.relative_to(home)),
        "commands": {"hermes": str(launcher.relative_to(home))},
    },
}
(home / "manifest.json").write_text(json.dumps(manifest) + "\n")

# Preserve the install stamp's other fields, but hand update ownership to the
# SDK. Hermes must not publish source launchers or self-update this payload.
stamp_path = repo / "install-stamp.json"
stamp = json.loads(stamp_path.read_text())
stamp["updateMechanism"] = "external"
stamp_path.write_text(json.dumps(stamp) + "\n")

# Replace the source launcher's absolute paths with a small bootstrap. The shell
# passes the relocated checkout as the first argument; pop it before forwarding
# CLI arguments. Import Hermes' bootstrap before application code so its normal
# dependency activation runs. Preserve --run-module for Hermes child processes.
# -I isolates Python from ambient Python settings; remove inherited overrides
# too, so they cannot leak into commands spawned by Hermes.
bootstrap = (
    "import os, runpy, sys; "
    "os.environ.pop('PYTHONHOME', None); os.environ.pop('PYTHONPATH', None); "
    "sys.path.insert(0, sys.argv.pop(1)); import hermes_bootstrap; "
    "module = sys.argv.pop(2) if sys.argv[1:2] == ['--run-module'] else 'hermes_cli.main'; "
    "sys.argv[1:2] = [] if sys.argv[1:2] == ['--run-module'] else sys.argv[1:2]; "
    "runpy.run_module(module, run_name='__main__', alter_sys=True)"
)

# From hermes-agent/.hermes/bin, three parents reach the payload root. Resolve
# that location at each launch, quote generated shell arguments, and exec the
# bundled Python so arguments, signals, and exit status reach the real process.
launcher.write_text(
    '#!/bin/sh\nroot=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd) || exit 1\n'
    f'exec "$root"/{shlex.quote(str(python.relative_to(home)))} -I -c {shlex.quote(bootstrap)} "$root/hermes-agent" "$@"\n'
)
launcher.chmod(0o755)

# A source checkout's Git metadata enables source-update recovery/completion.
# Neither belongs in an externally managed payload; omit it from the SDK.
shutil.rmtree(repo / ".git")