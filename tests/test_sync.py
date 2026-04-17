from pathlib import Path

import pytest

from spur_skills import sync
from spur_skills.types import Agent, PointerInstallResult, Skill


def make_skill(tmp_path: Path) -> Skill:
    skill_dir = tmp_path / "spatial-analysis"
    (skill_dir / "agents").mkdir(parents=True)
    (skill_dir / "references").mkdir()
    skill_dir.joinpath("SKILL.md").write_text(
        "---\nname: spatial-analysis\ndescription: spatial skill\n---\n",
        encoding="utf-8",
    )
    skill_dir.joinpath("agents", "openai.yaml").write_text(
        "interface:\n  display_name: Spatial Analysis\n",
        encoding="utf-8",
    )
    skill_dir.joinpath("references", "example-r.md").write_text(
        "example", encoding="utf-8"
    )
    return Skill(
        name="spatial-analysis",
        description="spatial skill",
        packaged_dir=skill_dir,
    )


def test_install_references_copies_full_skill_tree(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / ".spur-skills" / "skills"
    monkeypatch.setattr(sync, "reference_root", lambda: root)

    skill = make_skill(tmp_path)
    installed = sync.install_references([skill])

    reference_dir = root / "spatial-analysis"
    assert installed == ["spatial-analysis"]
    assert reference_dir.joinpath("SKILL.md").exists()
    assert reference_dir.joinpath("agents", "openai.yaml").exists()
    assert reference_dir.joinpath("references", "example-r.md").exists()


def test_install_pointers_writes_pointer_and_agents_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / ".spur-skills" / "skills"
    monkeypatch.setattr(sync, "reference_root", lambda: root)

    skill = make_skill(tmp_path)
    sync.install_references([skill])
    agent = Agent("codex", tmp_path / ".codex" / "skills")

    installed = sync.install_pointers([skill], [agent], yes=True)

    pointer_dir = agent.skills_dir / "spatial-analysis"
    assert installed == PointerInstallResult(["codex"], [], [])
    assert pointer_dir.joinpath("SKILL.md").exists()
    assert str(root / "spatial-analysis" / "SKILL.md") in pointer_dir.joinpath(
        "SKILL.md"
    ).read_text(encoding="utf-8")
    assert pointer_dir.joinpath("agents", "openai.yaml").exists()
    assert not pointer_dir.joinpath("references").exists()


def test_install_pointers_skips_when_user_declines(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / ".spur-skills" / "skills"
    monkeypatch.setattr(sync, "reference_root", lambda: root)

    skill = make_skill(tmp_path)
    sync.install_references([skill])
    agent = Agent("codex", tmp_path / ".codex" / "skills")
    pointer_dir = agent.skills_dir / "spatial-analysis"
    pointer_dir.mkdir(parents=True)
    pointer_dir.joinpath("SKILL.md").write_text("old", encoding="utf-8")

    monkeypatch.setattr(sync.typer, "confirm", lambda *args, **kwargs: False)
    installed = sync.install_pointers([skill], [agent], yes=False)

    assert installed == PointerInstallResult([], ["spatial-analysis"], ["codex"])
    assert pointer_dir.joinpath("SKILL.md").read_text(encoding="utf-8") == "old"


def test_install_pointers_yes_overwrites_without_prompt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / ".spur-skills" / "skills"
    monkeypatch.setattr(sync, "reference_root", lambda: root)

    skill = make_skill(tmp_path)
    sync.install_references([skill])
    agent = Agent("codex", tmp_path / ".codex" / "skills")
    pointer_dir = agent.skills_dir / "spatial-analysis"
    pointer_dir.mkdir(parents=True)
    pointer_dir.joinpath("SKILL.md").write_text("old", encoding="utf-8")

    monkeypatch.setattr(
        sync.typer,
        "confirm",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("unexpected confirm")
        ),
    )
    installed = sync.install_pointers([skill], [agent], yes=True)

    assert installed == PointerInstallResult(["codex"], [], [])
    assert sync.POINTER_MARKER in pointer_dir.joinpath("SKILL.md").read_text(
        encoding="utf-8"
    )


def test_install_pointers_tracks_kept_harnesses_for_declined_overrides(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / ".spur-skills" / "skills"
    monkeypatch.setattr(sync, "reference_root", lambda: root)

    skill = make_skill(tmp_path)
    sync.install_references([skill])
    codex = Agent("codex", tmp_path / ".codex" / "skills")
    claude = Agent("claude", tmp_path / ".claude" / "skills")
    hermes = Agent("hermes", tmp_path / ".hermes" / "skills")

    for agent in [codex, claude, hermes]:
        pointer_dir = agent.skills_dir / "spatial-analysis"
        pointer_dir.mkdir(parents=True)
        pointer_dir.joinpath("SKILL.md").write_text("old", encoding="utf-8")

    monkeypatch.setattr(sync.typer, "confirm", lambda *args, **kwargs: False)

    installed = sync.install_pointers([skill], [codex, claude, hermes], yes=False)

    assert installed == PointerInstallResult(
        [],
        ["spatial-analysis"],
        ["claude", "codex", "hermes"],
    )
    for agent in [codex, claude, hermes]:
        assert (agent.skills_dir / "spatial-analysis" / "SKILL.md").read_text(
            encoding="utf-8"
        ) == "old"


def test_select_pointer_agents_skips_opencode_when_claude_exists() -> None:
    selected = sync.select_pointer_agents(
        [
            Agent("codex", Path("/codex")),
            Agent("claude", Path("/claude")),
            Agent("opencode", Path("/opencode")),
        ]
    )

    assert [agent.name for agent in selected] == ["codex", "claude"]


def test_is_spur_pointer_matches_generated_pointer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / ".spur-skills" / "skills"
    monkeypatch.setattr(sync, "reference_root", lambda: root)

    pointer_dir = tmp_path / ".codex" / "skills" / "spatial-analysis"
    pointer_dir.mkdir(parents=True)
    pointer_dir.joinpath("SKILL.md").write_text(
        sync.render_pointer(
            Skill("spatial-analysis", "spatial skill", tmp_path / "spatial-analysis")
        ),
        encoding="utf-8",
    )

    assert sync.is_spur_pointer(pointer_dir)


def test_remove_pointers_removes_only_spur_generated_pointers(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / ".spur-skills" / "skills"
    monkeypatch.setattr(sync, "reference_root", lambda: root)

    agent = Agent("codex", tmp_path / ".codex" / "skills")
    spur_pointer = agent.skills_dir / "spatial-analysis"
    other_skill = agent.skills_dir / "other-skill"
    spur_pointer.mkdir(parents=True)
    other_skill.mkdir(parents=True)
    spur_pointer.joinpath("SKILL.md").write_text(
        sync.render_pointer(
            Skill("spatial-analysis", "spatial skill", tmp_path / "spatial-analysis")
        ),
        encoding="utf-8",
    )
    other_skill.joinpath("SKILL.md").write_text("not a spur pointer", encoding="utf-8")

    removed_skills, removed_harnesses = sync.remove_pointers([agent])

    assert removed_skills == ["spatial-analysis"]
    assert removed_harnesses == ["codex"]
    assert not spur_pointer.exists()
    assert other_skill.exists()


def test_remove_reference_home_removes_spur_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    home = tmp_path / ".spur-skills"
    root = home / "skills" / "spatial-analysis"
    root.mkdir(parents=True)
    monkeypatch.setattr(sync, "spur_home", lambda: home)
    monkeypatch.setattr(sync, "reference_root", lambda: home / "skills")

    removed = sync.remove_reference_home()

    assert removed == ["spatial-analysis"]
    assert not home.exists()


def test_install_summary_lines_use_box_content() -> None:
    assert sync.install_summary_lines(
        ["spatial-analysis"],
        ["hermes", "claude", "codex"],
        [],
    ) == [
        "Installed skills: spatial-analysis",
        "In harnesses: claude, codex, hermes",
        "Reference: ~/.spur-skills/skills",
    ]


def test_install_summary_lines_include_kept_harnesses() -> None:
    assert sync.install_summary_lines(
        ["spatial-analysis"],
        [],
        ["hermes", "claude", "codex"],
    ) == [
        "Installed skills: spatial-analysis",
        "Kept harnesses: claude, codex, hermes",
        "Reference: ~/.spur-skills/skills",
    ]


def test_show_install_summary_prints_rich_panel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeConsole:
        def print(self, obj: object) -> None:
            captured["obj"] = obj

    monkeypatch.setattr(sync, "Console", FakeConsole)

    sync.show_install_summary(
        ["spatial-analysis"],
        ["hermes", "claude", "codex"],
        [],
    )

    panel = captured["obj"]
    assert panel.title == "spur-skills installed"
    assert panel.renderable == (
        "Installed skills: spatial-analysis\n"
        "In harnesses: claude, codex, hermes\n"
        "Reference: ~/.spur-skills/skills"
    )
