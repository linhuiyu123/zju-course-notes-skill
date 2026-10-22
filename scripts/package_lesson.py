#!/usr/bin/env python3
"""Create a one-lesson ZIP from materials that are already on disk."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_ROOT / "references" / "chatgpt-prompt-template.md"
VIDEO_SUFFIXES = {".3gp", ".avi", ".flv", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".webm", ".wmv"}
INSTALLER_SUFFIXES = {".apk", ".appx", ".deb", ".dmg", ".exe", ".msi", ".pkg", ".rpm"}
SECRET_NAMES = {
    ".env", ".env.local", "config.json", "credentials.json", "cookies.txt",
    ".session.json", "token.json",
}
SKIP_DIRS = {".git", ".codex", "__pycache__", "node_modules"}


def safe_stem(value: str) -> str:
    """Keep output filenames ASCII and portable across Windows/macOS/Linux."""
    chars = [c if c.isascii() and (c.isalnum() or c in "-_ ") else "-" for c in value]
    slug = "".join(chars).strip(" -_")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:64] or "lesson"


def collect_files(root: Path) -> tuple[list[Path], list[tuple[Path, str]]]:
    included: list[Path] = []
    skipped: list[tuple[Path, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS or part.startswith(".") for part in relative.parts):
            skipped.append((relative, "hidden or generated directory/file"))
        elif path.name.casefold() in SECRET_NAMES:
            skipped.append((relative, "sensitive configuration"))
        elif path.suffix.casefold() in VIDEO_SUFFIXES:
            skipped.append((relative, "video; excluded by default"))
        elif path.suffix.casefold() in INSTALLER_SUFFIXES:
            skipped.append((relative, "software installer; excluded by default"))
        else:
            included.append(path)
    return included, skipped


def build_prompt(course: str, lesson_date: str, lesson: str, teacher: str, files: list[Path], root: Path) -> str:
    prompt = TEMPLATE.read_text(encoding="utf-8")
    teacher_line = f"- 教师：`{teacher}`\n" if teacher else ""
    material_names = "\n".join(f"  - `materials/{p.relative_to(root).as_posix()}`" for p in files)
    prompt = prompt.replace("<课程名>", course)
    prompt = prompt.replace("<YYYY-MM-DD>", lesson_date)
    prompt = prompt.replace("<课次或主题>", lesson)
    prompt = prompt.replace("- 教师：`<教师；未知则删除此行>`\n", teacher_line)
    prompt = prompt.replace("<逐项列出本次上传的文件名>", "\n" + material_names)
    return prompt


def create_archive(args: argparse.Namespace) -> Path:
    source = Path(args.materials_dir).expanduser().resolve(strict=True)
    if not source.is_dir():
        raise ValueError("--materials-dir must point to a directory")
    try:
        date.fromisoformat(args.date)
    except ValueError as exc:
        raise ValueError("--date must use YYYY-MM-DD") from exc

    files, skipped = collect_files(source)
    if not files:
        raise ValueError("No eligible local material files were found")

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_dir == source or source in output_dir.parents:
        raise ValueError("--output-dir must be outside --materials-dir")
    archive = output_dir / f"{args.date}-{safe_stem(args.lesson)}.zip"
    if archive.exists() and not args.overwrite:
        raise FileExistsError(f"Output already exists: {archive} (pass --overwrite to replace it)")

    prompt = build_prompt(args.course, args.date, args.lesson, args.teacher or "", files, source)
    expected = {"prompt.md", *(f"materials/{p.relative_to(source).as_posix()}" for p in files)}
    with tempfile.TemporaryDirectory(prefix="zju-course-notes-") as temp_name:
        temp_archive = Path(temp_name) / "package.zip"
        with zipfile.ZipFile(temp_archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            zf.writestr("prompt.md", prompt)
            for path in files:
                zf.write(path, f"materials/{path.relative_to(source).as_posix()}")
        with zipfile.ZipFile(temp_archive, "r") as zf:
            actual = set(zf.namelist())
            damaged = zf.testzip()
            if damaged:
                raise ValueError(f"ZIP integrity check failed at {damaged}")
            if actual != expected:
                raise ValueError("ZIP contents do not match the selected materials")
            # Reading the decoded names verifies Python's UTF-8 filename handling.
            for name in zf.namelist():
                name.encode("utf-8").decode("utf-8")
        if archive.exists():
            archive.unlink()
        shutil.move(str(temp_archive), archive)

    print(f"Created: {archive}")
    print(f"Included {len(files)} material file(s); ZIP size {archive.stat().st_size:,} bytes")
    for relative, reason in skipped:
        print(f"Skipped: {relative} ({reason})", file=sys.stderr)
    return archive


def main() -> int:
    parser = argparse.ArgumentParser(description="Package one locally available ZJU lesson for manual ChatGPT upload")
    parser.add_argument("--course", required=True, help="Course name")
    parser.add_argument("--date", required=True, help="Lesson date, YYYY-MM-DD")
    parser.add_argument("--lesson", required=True, help="Lesson number or topic")
    parser.add_argument("--teacher", help="Teacher name, if known")
    parser.add_argument("--materials-dir", required=True, help="Folder containing this lesson's local materials")
    parser.add_argument("--output-dir", default=".", help="Directory for the ZIP (default: current directory)")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing ZIP with the same name")
    args = parser.parse_args()
    try:
        create_archive(args)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
