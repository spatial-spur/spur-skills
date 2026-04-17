from importlib import metadata
from pathlib import Path
from typing import cast

from spur_skills.types import Skill


def locate_skill_dir(dist: metadata.Distribution, file: metadata.PackagePath) -> Path:
    """Resolve a packaged SKILL.md entry to its containing skill directory."""
    return cast(Path, dist.locate_file(file)).parent


def iter_packaged_skill_dirs() -> list[Path]:
    """Return top-level packaged skill directories from the installed wheel."""
    dist = metadata.distribution("spur-skills")
    files = dist.files or []
    return sorted(
        locate_skill_dir(dist, file)
        for file in files
        if len(Path(file).parts) == 2 and Path(file).name == "SKILL.md"
    )


def parse_skill(skill_dir: Path) -> Skill:
    """Parse required frontmatter from a packaged skill directory.

    Args:
        skill_dir: Packaged skill directory containing `SKILL.md`.

    Returns:
        Parsed skill metadata plus the packaged directory path.
    """
    lines = skill_dir.joinpath("SKILL.md").read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"invalid skill frontmatter: {skill_dir / 'SKILL.md'}")

    end = lines.index("---", 1)
    frontmatter: dict[str, str] = {}
    for line in lines[1:end]:
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip()

    return Skill(
        name=frontmatter["name"],
        description=frontmatter["description"],
        packaged_dir=skill_dir,
    )


def load_packaged_skills() -> list[Skill]:
    """Load all packaged skills shipped with the installed tool."""
    return [parse_skill(skill_dir) for skill_dir in iter_packaged_skill_dirs()]
