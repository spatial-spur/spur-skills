# spur-skills

`spur-skills` is a `uv tool` managing the installation and updating of our agent-skills. 

## Quick start

`spur-skills` is distributed as a `uv` tool.

To get started, just point your favorite agent at the install section, e.g.

with Codex:

```bash
codex --dangerously-bypass-approvals-and-sandbox "Install spur-skills by following https://github.com/spatial-spur/spur-skills#install"
```

with Claude Code:

```bash
claude --dangerously-skip-permissions "Install spur-skills by following https://github.com/spatial-spur/spur-skills#install"
```

## Install

Of course, you can also install the tool yourself in a few steps:

If you haven't already, first install `uv` with:

```bash
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

If you run into issues setting up `uv`, you may want to check the [uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/).

Then, install `spur-skills` from PyPI with:

```bash
uv tool install spur-skills
spur-skills install
```
After install, you will see a short summary like this:

```text
╭─────── spur-skills installed ───────╮
│ Installed skills: spatial-analysis  │
│ In harnesses: claude, codex, hermes │
│ Reference: ~/.spur-skills/skills    │
╰─────────────────────────────────────╯
```

The listed harnesses are only an example. The actual summary depends on which
supported agent homes already exist locally.

## Shipped Skills

`spur-skills` currently packages two skills:

- `spatial-analysis`: core reference for the agent to know its way around the packages' functions 
- `spur-skills`: reference for the agent to know how to use the `spur-skills` tool itself

## Useful commands

One of the skills `spur-skills` installs tells the agent all about 
interacting with the tool so you don't have to. Should you want to
manually use it anyway, here are the core commands:

Install skills into all supported agent folders that already exist:

```bash
spur-skills install
```

Install and auto-accept overwrites:

```bash
spur-skills install --yes
```

To fetch the latest version of the skill and tool:

```bash
spur-skills update
```

Update and auto-accept overwrites:

```bash
spur-skills update --yes
```

Remove installed skill entries from all supported agent folders and remove the
shared skill folder:

```bash
spur-skills uninstall
```

Remove installed skill entries only from selected agents:

```bash
spur-skills uninstall codex claude
```

Then uninstall the tool with:

```bash
uv tool uninstall spur-skills
```

## Supported agents

- `codex`
- `claude`
- `hermes`
- `agents`
- `opencode`

## Next steps:

- [How it works](how-it-works.md): understand what the tool writes and why
