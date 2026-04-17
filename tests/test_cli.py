from pathlib import Path

import pytest

from spur_skills import cli
from spur_skills.types import Agent, PointerInstallResult


def test_install_command_installs_and_shows_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    skill = object()
    captured: dict[str, object] = {}

    monkeypatch.setattr(cli, "load_packaged_skills", lambda: [skill])
    monkeypatch.setattr(cli, "install_references", lambda skills: ["spatial-analysis"])
    monkeypatch.setattr(
        cli, "installed_agents", lambda: [Agent("codex", Path("/codex"))]
    )
    monkeypatch.setattr(
        cli,
        "install_pointers",
        lambda skills, agents, yes: PointerInstallResult(["codex"], [], []),
    )
    monkeypatch.setattr(
        cli,
        "show_install_summary",
        lambda skills, harnesses, kept_harnesses: captured.update(
            {
                "skills": skills,
                "harnesses": harnesses,
                "kept_harnesses": kept_harnesses,
            }
        ),
    )

    cli.install_command(True)

    assert captured == {
        "skills": ["spatial-analysis"],
        "harnesses": ["codex"],
        "kept_harnesses": [],
    }


def test_update_command_upgrades_and_runs_install(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[list[str], bool]] = []

    monkeypatch.setattr(
        cli.subprocess,
        "run",
        lambda command, check: calls.append((command, check)),
    )

    cli.update_command(True)

    assert calls == [
        (["uv", "tool", "upgrade", "spur-skills"], True),
        (["spur-skills", "install", "--yes"], True),
    ]


def test_uninstall_command_without_agent_names_removes_everything(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    all_found = [Agent("codex", Path("/codex")), Agent("claude", Path("/claude"))]

    monkeypatch.setattr(cli, "all_agents", lambda: all_found)
    monkeypatch.setattr(
        cli,
        "remove_pointers",
        lambda agents: (["spatial-analysis"], ["codex", "claude"]),
    )
    monkeypatch.setattr(cli, "remove_reference_home", lambda: ["spatial-analysis"])
    monkeypatch.setattr(
        cli,
        "show_summary",
        lambda action, skills, harnesses, reference=None: captured.update(
            {
                "action": action,
                "skills": skills,
                "harnesses": harnesses,
                "reference": reference,
            }
        ),
    )

    cli.uninstall_command([])

    assert captured == {
        "action": "removed",
        "skills": ["spatial-analysis"],
        "harnesses": ["codex", "claude"],
        "reference": "removed ~/.spur-skills",
    }


def test_uninstall_command_with_agent_names_removes_only_pointers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    resolved = [Agent("codex", Path("/codex")), Agent("claude", Path("/claude"))]

    monkeypatch.setattr(
        cli,
        "resolve_agents",
        lambda names: resolved if names == ["codex", "claude"] else [],
    )
    monkeypatch.setattr(
        cli,
        "remove_pointers",
        lambda agents: (["spatial-analysis"], ["codex", "claude"]),
    )
    monkeypatch.setattr(
        cli,
        "show_summary",
        lambda action, skills, harnesses, reference=None: captured.update(
            {
                "action": action,
                "skills": skills,
                "harnesses": harnesses,
                "reference": reference,
            }
        ),
    )

    cli.uninstall_command(["codex", "claude"])

    assert captured == {
        "action": "removed",
        "skills": ["spatial-analysis"],
        "harnesses": ["codex", "claude"],
        "reference": None,
    }
