# Pi SDK for Workshop

This SDK provides the Pi Coding Agent for AI-assisted coding within a
workshop. The agent is sandboxed in the workshop container. Credentials are
persisted between workshop updates.

---

## Reference workshop

A minimal workshop:

```yaml
# workshop.yaml
name: pi-env
base: ubuntu@24.04
sdks:
  - name: pi
    channel: latest/stable

actions:
  pi: pi "$@"
  pi-prompt: pi -p "$@"
```

This creates a basic Pi environment.
The agent is sandboxed by the workshop.

---

## Using the SDK

### Prerequisites, project layout

1. No prerequisite SDKs are required.
2. Place your project files in your project directory. No special layout is
   required; Pi works with any codebase.
3. On launch, the SDK puts `pi` on the `PATH`, installs `fd` and `ripgrep`
   for pi's search tools, and adds a hint about the workshop environment to
   `~/.pi/agent/AGENTS.md`. An existing `AGENTS.md` is kept; the hint is
   appended once.

### Start a coding session

Once the workshop is ready:

```bash
workshop shell
pi
```

This opens an interactive Pi session inside the workshop. You can ask
pi to read files, write code, run commands, and navigate your project.

---

## Plugs (resources this SDK consumes)

### `pi-config`

- Interface: `mount`
- Workshop target: `/home/workshop/.pi`
- Purpose: Preserves Pi coding agent's credentials and settings between workshop updates.
  You can also use `workshop remount` to control its contents on the host.
  To mount your existing `~/.pi` settings into the workshop, stop
  the workshop first, remount, then start it again. The workshop hint is then
  appended to your host `~/.pi/agent/AGENTS.md` as well:

  ```bash
  workshop stop <workshop-name>
  workshop remount <workshop-name>/pi:pi-config ~/.pi
  workshop start <workshop-name>
  ```

## Slots (resources this SDK provides)

This SDK doesn't define any slots.

---

## Documentation and guidance

- [Pi documentation](https://pi.dev/docs/latest)
- [Workshop documentation](https://ubuntu.com/workshop/docs/)

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
  [official repository](https://github.com/canonical/pi-sdk).

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

[Pi Coding Agent](https://pi.dev) is subject to MIT license.
