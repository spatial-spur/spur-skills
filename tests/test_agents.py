from pathlib import Path

import pytest
import typer

from spur_skills import agents


def set_home(monkeypatch: pytest.MonkeyPatch, home: Path) -> None:
    monkeypatch.setattr(agents.Path, "home", classmethod(lambda cls: home))


def test_all_agents_returns_supported_agent_names(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    set_home(monkeypatch, tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    found = agents.all_agents()

    assert [agent.name for agent in found] == [
        "codex",
        "claude",
        "hermes",
        "agents",
        "opencode",
    ]


def test_installed_agents_returns_existing_agent_homes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    set_home(monkeypatch, tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    (tmp_path / ".codex").mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".hermes").mkdir()
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".config" / "opencode").mkdir(parents=True)

    found = agents.installed_agents()

    assert [agent.name for agent in found] == [
        "codex",
        "claude",
        "hermes",
        "agents",
        "opencode",
    ]
    assert found[-1].skills_dir == tmp_path / ".config" / "opencode" / "skills"


def test_installed_agents_uses_xdg_path_for_legacy_opencode_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    set_home(monkeypatch, tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    (tmp_path / ".opencode").mkdir()

    found = agents.installed_agents()

    assert found == [
        agents.Agent("opencode", tmp_path / ".config" / "opencode" / "skills")
    ]


def test_resolve_agents_returns_agents_in_requested_order(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    set_home(monkeypatch, tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    found = agents.resolve_agents(["claude", "codex"])

    assert [agent.name for agent in found] == ["claude", "codex"]


def test_resolve_agents_rejects_unknown_names(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    set_home(monkeypatch, tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    with pytest.raises(typer.BadParameter):
        agents.resolve_agents(["bogus"])
