"""Package only the authored integration, reference docs, tests, and helpers."""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT.parent / "jetson-home-assistant.zip"
EXCLUDED = {"__pycache__", ".ruff_cache", ".pytest_cache", ".venv", ".git"}
ALLOWED_SUFFIXES = {".py", ".json", ".md", ".toml", ".txt", ".png"}


def main():
    files = sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and not EXCLUDED.intersection(path.relative_to(ROOT).parts)
        and (
            path.suffix in ALLOWED_SUFFIXES
            or path.name in {".gitignore", ".gitattributes", "LICENSE"}
        )
        and not path.name.startswith(("capture", "credentials"))
    )
    with zipfile.ZipFile(DESTINATION, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, str(Path(ROOT.name) / path.relative_to(ROOT)))
    with zipfile.ZipFile(DESTINATION) as archive:
        assert archive.testzip() is None
        assert all("__pycache__" not in name for name in archive.namelist())
    print(f"Packaged {len(files)} files: {DESTINATION}")


if __name__ == "__main__":
    main()
