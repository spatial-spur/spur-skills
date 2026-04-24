![Tests](https://github.com/DGoettlich/spur-skills/actions/workflows/test.yaml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.11+-blue)

```text
███████ ██████  ██    ██ ██████        ███████ ██   ██ ██ ██      ██      ███████ 
██      ██   ██ ██    ██ ██   ██       ██      ██  ██  ██ ██      ██      ██      
███████ ██████  ██    ██ ██████  █████ ███████ █████   ██ ██      ██      ███████ 
     ██ ██      ██    ██ ██   ██            ██ ██  ██  ██ ██      ██           ██ 
███████ ██       ██████  ██   ██       ███████ ██   ██ ██ ███████ ███████ ███████ 
                                                                                  
```

# SPUR-Skills

This repo contains 
1. installable skills for the spur-family of packages.
2. A `uv tool` for installing, updating, and uninstalling the skills.

## Quick start

To get started, just point your agent at the install section:

```bash
codex --dangerously-bypass-approvals-and-sandbox "Install spur-skills by following https://github.com/spatial-spur/spur-skills#install, then inspect the spatial-analysis skill and provide the user with a very short two-section overview: 1) how to apply the spur procedure using the spur() Python wrapper as minimal example, 2) an itemized list of what the applied tests actually do. focus on clarity and brevity"
```

```bash
claude --dangerously-skip-permissions "Install spur-skills by following https://github.com/spatial-spur/spur-skills#install, then inspect the spatial-analysis skill and provide the user with a very short two-section overview: 1) how to apply the spur procedure using the spur() Python wrapper as minimal example, 2) an itemized list of what the applied tests actually do. focus on clarity and brevity"
```

After installation, ask your agent anything about the ecosystem and it should know where to find the answer.

## Install

If you haven't already, install `uv` with:

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

Update tool and skills:

```bash
spur-skills update
```

After install, you will see a short summary like this:

```text
╭─────── spur-skills installed ───────╮
│ Installed skills: spatial-analysis  │
│ In harnesses: claude, codex, hermes │
│ Reference: ~/.spur-skills/skills    │
╰─────────────────────────────────────╯
```

## Supported Agents

- `codex`
- `claude`
- `hermes`
- `opencode`
- other agents reading from `agents`
