import subprocess

import typer

from spur_skills.agents import all_agents, installed_agents, resolve_agents
from spur_skills.packaged import load_packaged_skills
from spur_skills.sync import (
    install_pointers,
    install_references,
    remove_pointers,
    remove_reference_home,
    show_install_summary,
    show_summary,
)


def install_command(yes: bool) -> None:
    """Install references and pointers for all packaged skills."""
    skills = load_packaged_skills()
    installed_skills = install_references(skills)
    pointer_result = install_pointers(skills, installed_agents(), yes)
    show_install_summary(
        installed_skills,
        pointer_result.installed_harnesses,
        pointer_result.kept_harnesses,
    )


def update_command(yes: bool) -> None:
    """Upgrade the tool in place and rerun install."""
    subprocess.run(["uv", "tool", "upgrade", "spur-skills"], check=True)
    argv = ["spur-skills", "install"]
    if yes:
        argv.append("--yes")
    subprocess.run(argv, check=True)


def uninstall_command(agent_names: list[str]) -> None:
    """Remove pointers for selected agents, or everything when no agents are given.

    Args:
        agent_names: CLI agent names. Empty means full uninstall.
    """
    if agent_names:
        removed_skills, removed_harnesses = remove_pointers(resolve_agents(agent_names))
        show_summary("removed", removed_skills, removed_harnesses)
        return

    removed_pointer_skills, removed_harnesses = remove_pointers(all_agents())
    removed_reference_skills = remove_reference_home()
    removed_skills = sorted(set(removed_pointer_skills) | set(removed_reference_skills))
    show_summary("removed", removed_skills, removed_harnesses, "removed ~/.spur-skills")


def main() -> None:
    app = typer.Typer(add_completion=False, no_args_is_help=True)

    @app.command("install")
    def install(
        yes: bool = typer.Option(
            False,
            "--yes",
            "-y",
            help="Auto-accept overrides.",
        ),
    ) -> None:
        install_command(yes)

    @app.command("update")
    def update(
        yes: bool = typer.Option(
            False,
            "--yes",
            "-y",
            help="Auto-accept overrides.",
        ),
    ) -> None:
        update_command(yes)

    @app.command("uninstall")
    def uninstall(
        agent_names: list[str] | None = typer.Argument(None, metavar="[AGENT]..."),
    ) -> None:
        uninstall_command(agent_names or [])

    app()
