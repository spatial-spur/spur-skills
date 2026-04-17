import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from spur_skills.types import Agent, PointerInstallResult, Skill


POINTER_MARKER = "Treat that file as the source of truth."
REFERENCE_DISPLAY = "~/.spur-skills/skills"
REMOVED_REFERENCE_DISPLAY = "removed ~/.spur-skills"


def spur_home() -> Path:
    """tool home directory."""
    return Path.home() / ".spur-skills"


def reference_root() -> Path:
    """Return the directory containing installed references."""
    return spur_home() / "skills"


def replace_tree(src: Path, dest: Path) -> None:
    """Atomically replace a directory tree by copying through a temp path.

    Args:
        src: Source directory to copy.
        dest: Destination directory to replace.
    """
    tmp = dest.with_name(f".{dest.name}.tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp)
    if dest.exists():
        shutil.rmtree(dest)
    tmp.rename(dest)


def install_references(skills: list[Skill]) -> list[str]:
    """Install full packaged skills into the shared reference directory."""
    root = reference_root()
    root.mkdir(parents=True, exist_ok=True)

    installed: list[str] = []
    for skill in skills:
        dest = root / skill.name
        replace_tree(skill.packaged_dir, dest)
        installed.append(skill.name)

    return installed


def render_pointer(skill: Skill) -> str:
    """Render the pointer SKILL.md content for one skill."""
    reference_dir = reference_root() / skill.name
    return (
        f"---\n"
        f"name: {skill.name}\n"
        f"description: {skill.description}\n"
        f"---\n\n"
        f"Read `{reference_dir / 'SKILL.md'}`.\n\n"
        f"{POINTER_MARKER}\n"
        f"Read any referenced files relative to `{reference_dir}`.\n"
    )


def select_pointer_agents(agents: list[Agent]) -> list[Agent]:
    """opencode reads skills from agents or claude
    --> no need to install in separate opencode dir if either
    of those are present"""
    names = {agent.name for agent in agents}
    if "opencode" in names and ("claude" in names or "agents" in names):
        return [agent for agent in agents if agent.name != "opencode"]
    return agents


def install_pointer(skill: Skill, agent: Agent) -> None:
    """Install one pointer into one agent home."""
    reference_dir = reference_root() / skill.name
    pointer_dir = agent.skills_dir / skill.name
    tmp = pointer_dir.with_name(f".{pointer_dir.name}.tmp")

    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    tmp.joinpath("SKILL.md").write_text(render_pointer(skill), encoding="utf-8")

    agents_dir = reference_dir / "agents"
    if agents_dir.exists():
        shutil.copytree(agents_dir, tmp / "agents")

    if pointer_dir.exists():
        shutil.rmtree(pointer_dir)
    tmp.rename(pointer_dir)


def install_pointers(
    skills: list[Skill], agents: list[Agent], yes: bool
) -> PointerInstallResult:
    """Install pointers into agent homes, prompting on conflicts when needed."""
    selected_agents = select_pointer_agents(agents)
    installed_harnesses: set[str] = set()
    skipped_skills: set[str] = set()
    kept_harnesses: set[str] = set()

    for skill in skills:
        conflicts = [
            agent
            for agent in selected_agents
            if (agent.skills_dir / skill.name).exists()
        ]
        if conflicts and not yes:
            names = ", ".join(agent.name for agent in conflicts)
            if not typer.confirm(
                f"Skill '{skill.name}' already exists in: {names}. Override?",
                default=True,
            ):
                skipped_skills.add(skill.name)
                kept_harnesses.update(agent.name for agent in conflicts)
                continue

        for agent in selected_agents:
            agent.skills_dir.mkdir(parents=True, exist_ok=True)
            install_pointer(skill, agent)
            installed_harnesses.add(agent.name)

    return PointerInstallResult(
        installed_harnesses=sorted(installed_harnesses),
        skipped_skills=sorted(skipped_skills),
        kept_harnesses=sorted(kept_harnesses),
    )


def is_spur_pointer(pointer_dir: Path) -> bool:
    """Return whether a skill directory is a Spur-managed pointer."""
    skill_md = pointer_dir / "SKILL.md"
    if not skill_md.exists():
        return False

    text = skill_md.read_text(encoding="utf-8")
    return POINTER_MARKER in text and str(reference_root()) in text


def list_spur_pointers(agent: Agent) -> list[Path]:
    """List Spur-managed pointers currently installed for one agent."""
    if not agent.skills_dir.exists():
        return []
    return sorted(
        path
        for path in agent.skills_dir.iterdir()
        if path.is_dir() and is_spur_pointer(path)
    )


def remove_pointers(agents: list[Agent]) -> tuple[list[str], list[str]]:
    """Remove all Spur-managed pointers from the given agents."""
    removed_skills: set[str] = set()
    removed_harnesses: set[str] = set()

    for agent in agents:
        for pointer_dir in list_spur_pointers(agent):
            shutil.rmtree(pointer_dir)
            removed_skills.add(pointer_dir.name)
            removed_harnesses.add(agent.name)

    return sorted(removed_skills), sorted(removed_harnesses)


def remove_reference_home() -> list[str]:
    """Remove the shared Spur home when it exists."""
    home = spur_home()
    root = reference_root()

    removed: list[str] = []
    if root.exists():
        removed = sorted(path.name for path in root.iterdir() if path.is_dir())

    if not home.exists():
        return removed

    shutil.rmtree(home)
    return removed


def format_names(names: list[str]) -> str:
    """Format summary names as a comma-separated list."""
    if not names:
        return "none"

    return ", ".join(sorted(set(names)))


def install_summary_lines(
    skills: list[str], installed_harnesses: list[str], kept_harnesses: list[str]
) -> list[str]:
    """Build the boxed install summary lines."""
    lines = [f"Installed skills: {format_names(skills)}"]

    if installed_harnesses:
        lines.append(f"In harnesses: {format_names(installed_harnesses)}")
    if kept_harnesses:
        lines.append(f"Kept harnesses: {format_names(kept_harnesses)}")
    if not installed_harnesses and not kept_harnesses:
        lines.append("In harnesses: none")

    lines.append(f"Reference: {REFERENCE_DISPLAY}")
    return lines


def summary_lines(
    action: str,
    skills: list[str],
    harnesses: list[str],
    reference: str | None = None,
) -> list[str]:
    """Build the boxed summary lines for a command result."""
    lines = [
        f"{action.title()} skills: {format_names(skills)}",
        f"In harnesses: {format_names(harnesses)}",
    ]

    if reference is not None:
        lines.append(f"Reference: {reference}")

    return lines


def show_install_summary(
    skills: list[str], installed_harnesses: list[str], kept_harnesses: list[str]
) -> None:
    """Print the boxed install summary for the command result."""
    body = "\n".join(install_summary_lines(skills, installed_harnesses, kept_harnesses))
    Console().print(Panel.fit(body, title="spur-skills installed"))


def show_summary(
    action: str,
    skills: list[str],
    harnesses: list[str],
    reference: str | None = None,
) -> None:
    """Print the boxed summary for the command result."""
    body = "\n".join(summary_lines(action, skills, harnesses, reference))
    Console().print(Panel.fit(body, title=f"spur-skills {action}"))
