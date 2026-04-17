import os
from pathlib import Path

import typer

from spur_skills.types import Agent


def all_agents() -> list[Agent]:
    """Return the fixed supported agent homes.

    Returns:
        Supported agent definitions in stable CLI-name order.
    """
    home = Path.home()
    xdg = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    return [
        Agent("codex", home / ".codex" / "skills"),
        Agent("claude", home / ".claude" / "skills"),
        Agent("hermes", home / ".hermes" / "skills"),
        Agent("agents", home / ".agents" / "skills"),
        Agent("opencode", xdg / "opencode" / "skills"),
    ]


def installed_agents() -> list[Agent]:
    """Return only agent homes that currently exist."""
    home = Path.home()
    xdg = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    installed: list[Agent] = []

    if (home / ".codex").exists():
        installed.append(Agent("codex", home / ".codex" / "skills"))
    if (home / ".claude").exists():
        installed.append(Agent("claude", home / ".claude" / "skills"))
    if (home / ".hermes").exists():
        installed.append(Agent("hermes", home / ".hermes" / "skills"))
    if (home / ".agents").exists():
        installed.append(Agent("agents", home / ".agents" / "skills"))
    if (xdg / "opencode").exists() or (home / ".opencode").exists():
        installed.append(Agent("opencode", xdg / "opencode" / "skills"))

    return installed


def resolve_agents(agent_names: list[str]) -> list[Agent]:
    """Resolve CLI agent names into concrete install destinations.

    Args:
        agent_names: User-supplied agent names from the CLI.

    Returns:
        Matching agent definitions in the requested order.
    """
    by_name = {agent.name: agent for agent in all_agents()}
    missing = [name for name in agent_names if name not in by_name]
    if missing:
        raise typer.BadParameter(f"unknown agent(s): {', '.join(missing)}")
    return [by_name[name] for name in agent_names]
