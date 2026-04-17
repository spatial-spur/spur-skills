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

## Install

Install the tool from PyPI (coming soon):

```bash
uv tool install spur-skills
spur-skills install
```

Update tool and skills:

```bash
spur-skills update
```

Uninstall `spur-skills` from all supported agent folders:

```bash
spur-skills uninstall
uv tool uninstall spur-skills
```

Or only from selected agents:

```bash
spur-skills uninstall codex claude
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
- `agents`
- `opencode`
