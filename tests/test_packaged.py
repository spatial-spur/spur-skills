from pathlib import Path

import pytest

from spur_skills import packaged
from spur_skills.types import Skill


class FakeDistribution:
    def __init__(self, root: Path, files: list[Path]) -> None:
        self.files = files
        self.root = root

    def locate_file(self, file: Path) -> Path:
        return self.root / file


def test_parse_skill_reads_spatial_analysis() -> None:
    skill = packaged.parse_skill(Path("skills/spatial-analysis"))
    assert skill.name == "spatial-analysis"
    assert skill.description.startswith("Use this skill if asked")


def test_parse_skill_rejects_missing_frontmatter(tmp_path: Path) -> None:
    skill_dir = tmp_path / "broken"
    skill_dir.mkdir()
    skill_dir.joinpath("SKILL.md").write_text("broken", encoding="utf-8")

    with pytest.raises(ValueError):
        packaged.parse_skill(skill_dir)


def test_load_packaged_skills_uses_top_level_skill_dirs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill_dir = tmp_path / "spatial-analysis"
    skill_dir.mkdir()
    skill_dir.joinpath("SKILL.md").write_text(
        "---\nname: spatial-analysis\ndescription: spatial skill\n---\n",
        encoding="utf-8",
    )

    fake = FakeDistribution(
        tmp_path,
        [
            Path("spatial-analysis/SKILL.md"),
            Path("spatial-analysis/agents/openai.yaml"),
            Path("spatial-analysis/references/example-r.md"),
            Path("nested/path/SKILL.md"),
        ],
    )
    monkeypatch.setattr(packaged.metadata, "distribution", lambda _: fake)

    skills = packaged.load_packaged_skills()

    assert skills == [
        Skill(
            name="spatial-analysis",
            description="spatial skill",
            packaged_dir=skill_dir,
        )
    ]
