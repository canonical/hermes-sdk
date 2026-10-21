# Hermes SDK for Workshop

This SDK provides the Hermes Agent for AI-assisted coding within a
workshop. The agent is sandboxed in the workshop container. Credentials are
persisted between workshop updates.

---

## Reference workshop

A minimal workshop:

```yaml
# workshop.yaml
name: hermes-env
base: ubuntu@24.04
sdks:
  - name: hermes-sdk
    channel: latest/stable

actions:
  hermes: hermes "$@"
```

This creates a basic Hermes environment.
The agent is sandboxed by the workshop.

---

## Using the SDK

### Prerequisites, project layout

1. No prerequisite SDKs are required.
2. Place your project files in your project directory. No special layout is
  required; Hermes works with any codebase.
3. The SDK puts `hermes` on the `PATH`, installs `git`, `curl`, `ripgrep`,
  and `libatomic1`, and adds a hint about the workshop environment to
  `~/.hermes/SOUL.md`. An existing `SOUL.md` is kept; the hint is
   appended once.

### Start a coding session

Once the workshop is ready:

```bash
workshop shell
hermes
```

This opens an interactive Hermes session inside the workshop. Configure your
model provider and credentials through Hermes before starting your first chat.
You can ask Hermes to read files, write code, run commands, and navigate your
project.

---

## Plugs (resources this SDK consumes)

### `hermes-config`

- Interface: `mount`
- Workshop target: `/home/workshop/.hermes`
- Purpose: Preserves Hermes credentials, settings, and agent state between workshop updates.
  You can also use `workshop remount` to control its contents on the host.
  To mount your existing `~/.hermes` settings into the workshop, stop
  the workshop first, remount, then start it again. The workshop hint is then
  appended to your host `~/.hermes/SOUL.md` as well:

  ```bash
  workshop stop <workshop-name>
  workshop remount <workshop-name>/hermes-sdk:hermes-config ~/.hermes
  workshop start <workshop-name>
  ```

## Slots (resources this SDK provides)

This SDK doesn't define any slots.

---

## Documentation and guidance

- [Hermes Agent documentation](https://hermes-agent.nousresearch.com/docs/)
- [Workshop documentation](https://ubuntu.com/workshop/docs/)

---

## Building and updating

Build the SDK with:

```bash
sdkcraft pack
```

The Hermes release is pinned in [VERSION](VERSION). The build bundles Hermes,
its Python runtime, and its dependencies as a relocatable, externally managed
installation. No dependency repair is required at startup; updates are delivered
through the SDK rather than `hermes update`.

Before sealing the installation,
[the compatibility check](scripts/check-hermes-compatibility.py) verifies
fingerprints of the upstream files used by
[the sealing helper](scripts/seal-hermes.py). If a monitored file changes or is
missing, the build stops with review instructions. Review upstream behavior and
verify the relocated installation before updating the fingerprints; do not
refresh them just to bypass the check.

---

## Community and support

- Workshop forum:
  [Workshop Discourse](https://discourse.canonical.com/c/engineering/workshops/34)
- Please review our
  [Code of Conduct](https://ubuntu.com/community/ethos/code-of-conduct) before
  participating.

---

## Contributions

All contributions, including code, documentation updates, and issue reports,
are welcome!

- Open issues or pull requests on the
  [official repository](https://github.com/canonical/hermes-sdk).

---

## License and copyright

Copyright 2026 Canonical Ltd.

This program is free software: you can redistribute it and/or modify it under
the terms of the
[GNU Lesser General Public License version 2.1 (LGPLv2.1)](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html)
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

[Hermes Agent](https://github.com/NousResearch/hermes-agent) is subject to MIT license.
