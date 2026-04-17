from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    packaged_dir: Path


@dataclass(frozen=True)
class Agent:
    name: str
    skills_dir: Path


@dataclass(frozen=True)
class PointerInstallResult:
    installed_harnesses: list[str]
    skipped_skills: list[str]
    kept_harnesses: list[str]
