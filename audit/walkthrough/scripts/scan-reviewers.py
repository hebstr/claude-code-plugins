#!/usr/bin/env python3
"""Discover available reviewer skills at runtime.

Scans active Claude Code skills (user-installed under ~/.claude/skills/ and
plugins listed in ~/.claude/plugins/installed_plugins.json), filters for
skills whose name and description match reviewer patterns, classifies each
candidate as `code`, `skill-tool`, or `unknown`, and emits JSON to stdout.

Used by agents/orchestrator.md when --reviewer is omitted.
"""

import glob
import json
import os
import re
import sys
from pathlib import Path

PLUGINS_MANIFEST = os.path.expanduser("~/.claude/plugins/installed_plugins.json")
USER_SKILLS_DIR = os.path.expanduser("~/.claude/skills")

BLACKLIST = {
    "walkthrough",
    "blindspot",
}

NAME_PAT = re.compile(r"\b(review|adversary|audit|critic)", re.IGNORECASE)
DESC_PAT = re.compile(
    r"\b(review|audit|critique|find\s+issues|find\s+flaws|adversarial|critic|critical)",
    re.IGNORECASE,
)
EXCLUDE_DESC = re.compile(
    r"\b(blog\s+post|release\s+announcement|interactive\s+tutorial|setup\s+wizard|first.?touch|tutorial)",
    re.IGNORECASE,
)
SKILL_TOOL_SIGNALS = re.compile(
    r"\b(SKILL\.md|MCP\s+server|skill\s+description|tool\s+description|skill's\s+full\s+directory)\b",
    re.IGNORECASE,
)
CODE_SIGNALS = re.compile(
    r"\b(code|PR|pull\s+request|python|R\s|javascript|typescript|SQL)\b",
    re.IGNORECASE,
)


def active_install_paths():
    if not os.path.exists(PLUGINS_MANIFEST):
        return []
    with open(PLUGINS_MANIFEST) as f:
        data = json.load(f)
    paths = []
    for installs in data.get("plugins", {}).values():
        for inst in installs:
            p = inst.get("installPath")
            if p:
                paths.append(p)
    return paths


def collect_skill_files():
    files = set()
    for p in active_install_paths():
        files.update(glob.glob(f"{p}/**/SKILL.md", recursive=True))
    files.update(glob.glob(f"{USER_SKILLS_DIR}/*/SKILL.md"))
    return sorted(files)


def parse_frontmatter(path):
    try:
        text = Path(path).read_text(errors="ignore")
    except OSError:
        return None
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    fm = m.group(1)
    nm = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    dm = re.search(
        r"^description:\s*>?\s*\n?(.*?)(?=\n[a-z_-]+:|\Z)",
        fm,
        re.DOTALL | re.MULTILINE,
    )
    if not dm:
        dm = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
    name = nm.group(1).strip() if nm else ""
    desc = dm.group(1).strip() if dm else ""
    return {"path": path, "name": name, "description": desc}


def classify(description):
    if SKILL_TOOL_SIGNALS.search(description):
        return "skill-tool"
    if CODE_SIGNALS.search(description):
        return "code"
    return "unknown"


def is_reviewer(name, description):
    base = name.split(":")[-1] if ":" in name else name
    if base in BLACKLIST:
        return False
    if not (NAME_PAT.search(name) and DESC_PAT.search(description)):
        return False
    if EXCLUDE_DESC.search(description):
        return False
    return True


def main():
    seen_names = set()
    candidates = []
    for path in collect_skill_files():
        meta = parse_frontmatter(path)
        if not meta or not meta["name"]:
            continue
        if meta["name"] in seen_names:
            continue
        seen_names.add(meta["name"])
        if not is_reviewer(meta["name"], meta["description"]):
            continue
        candidates.append(
            {
                "name": meta["name"],
                "category": classify(meta["description"]),
                "path": meta["path"],
                "description_excerpt": " ".join(meta["description"].split())[:200],
            }
        )
    candidates.sort(key=lambda c: c["name"])
    json.dump(
        {"candidates": candidates, "count": len(candidates)}, sys.stdout, indent=2
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
