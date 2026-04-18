from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Skill:
    """file-bundle making up a single packaged skill"""

    name: str
    """folder name of the skill, e.g. `spatial-analysis`"""

    description: str
    """short description from SKILL.md yaml front matter"""

    packaged_dir: Path
    """abs. path to site-packages dir containing skill"""


@dataclass(frozen=True)
class Agent:
    """coding agent harness"""

    name: str
    """name of harness (e.g. `codex`, `claude`)"""

    skills_dir: Path
    """agent's skill folder (e.g. ~/.codex/skills)"""


@dataclass(frozen=True)
class PointerInstallResult:
    """carries result of install pass into agent folders"""

    installed_harnesses: list[str]
    """names of harnesses where install wrote new files"""

    skipped_skills: list[str]
    """names of skills that were skipped bc overwrite was declined"""

    kept_harnesses: list[str]
    """harnesses where install was skipped bc overwrite was declined"""
