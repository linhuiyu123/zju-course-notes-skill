# ZJU Course Notes Skill

A Codex skill for turning locally available Zhejiang University lecture slides and transcripts into one ChatGPT-ready ZIP per lesson. The student reviews and uploads each lesson manually.

## Install

Copy this repository folder into your Codex skills directory:

```text
~/.codex/skills/zju-course-notes/
```

On Windows, the default location is usually:

```text
%USERPROFILE%\.codex\skills\zju-course-notes\
```

Restart Codex or start a new task, then ask for example: “Use the zju-course-notes skill to package the 2026-10-22 lecture from my local course materials.”

## What it does

- Finds and matches local lesson slides/PDFs and transcripts.
- Produces a separate prompt and ZIP for each lesson.
- Emphasizes clear structure, rendered formulas, syntax-highlighted code, and careful use of diagrams.
- Verifies the archive contents and reports missing or ambiguous materials.

## Create a lesson package

Put one lesson's locally available files in its own folder, then run:

```bash
python scripts/package_lesson.py --course "Course name" --date 2026-10-22 --lesson "Lesson 3-4" --materials-dir "./materials/lesson-03" --output-dir "./packages"
```

The script creates an ASCII-named ZIP with `prompt.md` and the selected source files under `materials/`. It reads files from disk only, includes PPT/PPTX/PDF files regardless of size, skips videos, software installers, and common credential files, and verifies the ZIP before reporting success. Check its skipped-file report and inspect the package before uploading.

The skill does not include any student's account configuration, course roster, transcripts, notes, or downloaded materials. It does not automate ChatGPT submission or bypass course-platform download permissions.
