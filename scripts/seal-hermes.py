import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil

home = Path(os.environ["HERMES_HOME"]).resolve()
repo = home / "hermes-agent"
key = hashlib.sha256(str(repo).encode()).hexdigest()[:16]
facts = json.loads((home / "installs" / key / "facts.json").read_text())
venv = Path(facts["packages"]["venv"]["environment"]).resolve()
tools = json.loads((home / "tools/facts.json").read_text())
python = home / "tools" / tools["packages"]["python"]["entry"] / "bin/python3"
assert venv.joinpath("pyvenv.cfg").is_file(), "Missing dependency environment"
assert python.is_file(), "Missing bundled Python"
(venv.parent / ".lease-managed").unlink(missing_ok=True)
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
stamp_path = repo / "install-stamp.json"
stamp = json.loads(stamp_path.read_text())
stamp["updateMechanism"] = "external"
stamp_path.write_text(json.dumps(stamp) + "\n")
bootstrap = (
    "import os, runpy, sys; "
    "os.environ.pop('PYTHONHOME', None); os.environ.pop('PYTHONPATH', None); "
    "sys.path.insert(0, sys.argv.pop(1)); import hermes_bootstrap; "
    "module = sys.argv.pop(2) if sys.argv[1:2] == ['--run-module'] else 'hermes_cli.main'; "
    "sys.argv[1:2] = [] if sys.argv[1:2] == ['--run-module'] else sys.argv[1:2]; "
    "runpy.run_module(module, run_name='__main__', alter_sys=True)"
)
launcher.write_text(
    '#!/bin/sh\nroot=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd) || exit 1\n'
    f'exec "$root"/{shlex.quote(str(python.relative_to(home)))} -I -c {shlex.quote(bootstrap)} "$root/hermes-agent" "$@"\n'
)
launcher.chmod(0o755)
shutil.rmtree(repo / ".git")