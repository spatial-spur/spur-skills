import os
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FAKE_HOME = REPO_ROOT / ".pytest_cache" / "HOME"
TOOL_BIN_DIR = FAKE_HOME / ".local" / "bin"


def installed_tool_bin() -> Path:
    candidates = [
        TOOL_BIN_DIR / "spur-skills.exe",
        TOOL_BIN_DIR / "spur-skills",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise AssertionError(f"spur-skills was not installed in {TOOL_BIN_DIR}")


def env() -> dict[str, str]:
    return os.environ | {
        "HOME": str(FAKE_HOME),
        "USERPROFILE": str(FAKE_HOME),
        "XDG_CONFIG_HOME": str(FAKE_HOME / ".config"),
        "UV_TOOL_BIN_DIR": str(TOOL_BIN_DIR),
        "PATH": f"{TOOL_BIN_DIR}{os.pathsep}{os.environ['PATH']}",
    }


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env(),
        text=True,
        capture_output=True,
        check=True,
    )


def reset_fake_home() -> None:
    shutil.rmtree(FAKE_HOME, ignore_errors=True)
    FAKE_HOME.mkdir(parents=True)


def install_tool() -> None:
    run(["uv", "tool", "install", "--reinstall", "--no-cache", "."])
    assert installed_tool_bin().exists()


def scaffold_agents(*names: str) -> None:
    for name in names:
        if name == "opencode":
            (FAKE_HOME / ".config" / "opencode").mkdir(parents=True, exist_ok=True)
        else:
            (FAKE_HOME / f".{name}").mkdir(parents=True, exist_ok=True)


def test_real_install_writes_shared_copy_and_pointers() -> None:
    reset_fake_home()
    scaffold_agents("codex", "hermes", "opencode")
    install_tool()

    result = run([str(installed_tool_bin()), "install", "--yes"])

    # fmt: off
    assert "Installed skills: spatial-analysis" in result.stdout
    assert (FAKE_HOME / ".spur-skills" / "skills" / "spatial-analysis" / "SKILL.md").exists()
    assert (FAKE_HOME / ".codex" / "skills" / "spatial-analysis" / "SKILL.md").exists()
    assert (FAKE_HOME / ".hermes" / "skills" / "spatial-analysis" / "SKILL.md").exists()
    assert (
        FAKE_HOME / ".config" / "opencode" / "skills" / "spatial-analysis" / "SKILL.md").exists() # fmt: skip

    pointer = (FAKE_HOME / ".codex" / "skills" / "spatial-analysis" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "spur-skills update -y" in pointer
    assert str(FAKE_HOME / ".spur-skills" / "skills" / "spatial-analysis" / "SKILL.md") in pointer
    # fmt: off


def test_real_uninstall_removes_only_spur_managed_entries() -> None:
    reset_fake_home()
    scaffold_agents("codex")
    install_tool()
    run([str(installed_tool_bin()), "install", "--yes"])

    other_skill = FAKE_HOME / ".codex" / "skills" / "other-skill"
    other_skill.mkdir(parents=True)
    other_skill.joinpath("SKILL.md").write_text("keep me", encoding="utf-8")

    result = run([str(installed_tool_bin()), "uninstall"])

    assert "Removed skills: spatial-analysis" in result.stdout
    assert not (FAKE_HOME / ".spur-skills").exists()
    assert not (FAKE_HOME / ".codex" / "skills" / "spatial-analysis").exists()
    assert other_skill.exists()
