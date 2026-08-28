#!/usr/bin/env python3
"""Repo-level validation for the FormBharo skill.

`npx skills add ARTPARK-SAHAI-ORG/formbharo-skills` serves the default branch
live, so `main` must always be installable. This gate runs in CI on every push
and pull request:

  - every SKILL.md has YAML frontmatter that parses, with name + description
  - skill `name` matches its directory name (npx skills resolves by name)
  - every SKILL.md tells the agent to update itself before running
  - no broken relative links between skill files

Needs PyYAML, because the installer reads the frontmatter as YAML and skips a
file it cannot parse. Run with `python3 scripts/check_skills.py` from the repo
root.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"


def check_frontmatter(problems: list[str]) -> None:
    for f in sorted(SKILLS.rglob("SKILL.md")):
        rel = f.relative_to(ROOT)
        m = re.match(r"^---\n(.*?)\n---\n", f.read_text(encoding="utf-8"), re.DOTALL)
        if not m:
            problems.append(f"{rel}: missing YAML frontmatter")
            continue
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            problems.append(f"{rel}: frontmatter is not valid YAML: {e}")
            continue
        if not isinstance(fm, dict):
            problems.append(f"{rel}: frontmatter is not a set of keys and values")
            continue
        name = fm.get("name")
        if not name:
            problems.append(f"{rel}: frontmatter missing `name`")
        elif name != f.parent.name:
            problems.append(f"{rel}: name '{name}' != directory '{f.parent.name}'")
        if not fm.get("description"):
            problems.append(f"{rel}: frontmatter missing `description`")


def check_update_line(problems: list[str]) -> None:
    """Every skill must tell the agent to pull the latest copy of itself first.

    `main` is served live, so a user's installed SKILL.md can be months old.
    The fix is in the skill itself: each one opens by updating itself, then
    re-reading the file from disk.
    """
    for f in sorted(SKILLS.rglob("SKILL.md")):
        name = f.parent.name
        want = f"npx -y skills update {name} -g -y ; npx -y skills update {name} -p -y"
        if want not in f.read_text(encoding="utf-8"):
            problems.append(
                f"{f.relative_to(ROOT)}: missing the self-update line "
                f"`{want}` (copy the 'Get the latest instructions' section "
                f"from another skill)"
            )


def check_links(problems: list[str]) -> None:
    """Every relative markdown link must point at a file that exists.

    Installing copies the whole skill directory, so a link to a file that is not
    there is broken for everyone who installs it.
    """
    for f in sorted(SKILLS.rglob("*.md")):
        for m in re.finditer(r"\]\(([^)#]+)(?:#[^)]*)?\)", f.read_text(encoding="utf-8")):
            target = m.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (f.parent / target).exists():
                problems.append(f"{f.relative_to(ROOT)}: broken link -> {target}")


def main() -> int:
    if not SKILLS.is_dir():
        print(f"No skills directory at {SKILLS}", file=sys.stderr)
        return 1

    problems: list[str] = []
    check_frontmatter(problems)
    check_update_line(problems)
    check_links(problems)

    if problems:
        print("Problems found:\n", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    count = len(list(SKILLS.rglob("SKILL.md")))
    print(f"{count} skill(s) checked, no problems.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
