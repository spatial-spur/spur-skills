# How It Works

`spur-skills` installs skills in two layers.

### 1. Shared skill files

First, it writes the full skill files into a shared directory:

```text
~/.spur-skills/skills/
```

This is the canonical copy of the installed skills.

### 2. Agent-specific pointers

Then it writes small `SKILL.md` pointer files into agent-specific skill folders,
for example:

```text
~/.codex/skills/
~/.claude/skills/
~/.hermes/skills/
~/.agents/skills/
$XDG_CONFIG_HOME/opencode/skills/  (usually ~/.config/opencode/skills/)
```

Those pointer files tell the agent to read the shared copy in `~/.spur-skills/skills/`.
They pointers preserve the original YAML headers so agents are triggered under
the same conditions as the full skill.

They also tell the agent to run `spur-skills update -y` before reading the
shared `SKILL.md`, so its guaranteed to have the latest references.
