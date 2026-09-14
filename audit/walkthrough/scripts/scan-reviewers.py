#!/usr/bin/env python3
"""Discover available reviewer skills at runtime.

Scans installed Claude Code skills (user skills under ~/.claude/skills/,
project skills under .claude/skills/ from the working directory up to its
repository root, and the skills each plugin in
~/.claude/plugins/installed_plugins.json declares in its marketplace entry or
plugin.json, unless disabled in enabledPlugins), filters for
skills whose name and description match reviewer patterns, classifies each
candidate as `code`, `skill-tool`, or `unknown`, and emits JSON to stdout.
Plugin skills are named `plugin:skill`.

Used by agents/orchestrator.md when --reviewer is omitted.
"""

import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PLUGINS_MANIFEST = Path("~/.claude/plugins/installed_plugins.json").expanduser()
KNOWN_MARKETPLACES = Path("~/.claude/plugins/known_marketplaces.json").expanduser()
USER_SKILLS_DIR = Path("~/.claude/skills").expanduser()
SETTINGS_FILES = (
    Path("~/.claude/settings.json").expanduser(),
    Path(".claude/settings.json"),
    Path(".claude/settings.local.json"),
)

BLACKLIST = {
    "audit:walkthrough",
    "audit:blindspot",
}

NAME_PAT = re.compile(r"\b(review|adversary|audit|critic)", re.IGNORECASE)
DESC_PAT = re.compile(
    r"\b(review|audit|critique|find\s+issues|find\s+flaws|adversarial|critic|critical)",
    re.IGNORECASE,
)
EXCLUDE_DESC = re.compile(
    r"\b(blog\s+post|release\s+announcement|interactive\s+tutorial|setup\s+wizard|first.?touch)",
    re.IGNORECASE,
)
SKILL_TOOL_SIGNALS = re.compile(
    r"\b(SKILL\.md|MCP\s+servers?|skill\s+descriptions?|tool\s+descriptions?|skill's\s+full\s+directory)\b",
    re.IGNORECASE,
)
BOILERPLATE_SENTENCE = re.compile(
    r"^(User-invocable\s+ONLY|Does\s+not\s+auto-trigger|Do\s+NOT\s+trigger|Not\s+for)\b",
    re.IGNORECASE,
)
ABBREVIATION_END = re.compile(r"\b(e\.g|i\.e|cf|vs)\.$", re.IGNORECASE)
CLAUDE_CODE = re.compile(r"\bClaude\s+Code\b", re.IGNORECASE)
CODE_SIGNALS = re.compile(
    r"\b(code|PR|pull\s+request|python|R\s|javascript|typescript|SQL)\b",
    re.IGNORECASE,
)


def installed_plugins():
    if not PLUGINS_MANIFEST.exists():
        return []
    data = load_json(PLUGINS_MANIFEST)
    if not isinstance(data, dict) or not isinstance(data.get("plugins"), dict):
        print(f"scan-reviewers: unreadable plugin manifest {PLUGINS_MANIFEST}", file=sys.stderr)
        return []
    disabled = disabled_plugins()
    cwd = str(Path.cwd())
    cwd_repo = repo_id(cwd)
    plugins = []
    for key, installs in data["plugins"].items():
        if not isinstance(installs, list):
            print(f"scan-reviewers: skipping malformed manifest entry {key}", file=sys.stderr)
            continue
        if key in disabled:
            continue
        plugin, _, marketplace = key.partition("@")
        for inst in installs:
            if not isinstance(inst, dict):
                continue
            p = inst.get("installPath")
            if p and installed_here(inst, cwd, cwd_repo):
                plugins.append((plugin, marketplace, Path(p)))
    return plugins


def load_json(path):
    try:
        with path.open() as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def repo_id(path):
    # the shared git dir spans worktrees, matching Claude Code's canonical project root
    try:
        out = subprocess.run(
            ["git", "-C", path, "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True,
            text=True,
            check=False,
            env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")},
        )
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip() or None


def installed_here(inst, cwd, cwd_repo):
    if inst.get("scope") in ("user", "managed"):
        return True
    project = inst.get("projectPath")
    if not project:
        return False
    if project == cwd:
        return True
    return cwd_repo is not None and repo_id(project) == cwd_repo


def disabled_plugins():
    enabled = {}
    for path in SETTINGS_FILES:
        settings = load_json(path)
        if isinstance(settings, dict) and isinstance(settings.get("enabledPlugins"), dict):
            enabled.update(settings["enabledPlugins"])
    return {key for key, on in enabled.items() if on is False}


def declared_skill_dirs(plugin, marketplace, install_path):
    # a monorepo install path holds sibling plugins too; only the marketplace entry scopes them
    bundled = catalog_skills(install_path / ".claude-plugin" / "marketplace.json", plugin)
    if bundled is not None:
        return skill_dirs(install_path, bundled)
    catalog = catalog_skills(marketplace_catalog(marketplace), plugin) or []
    return skill_dirs(install_path, ["skills", *catalog, *manifest_skills(install_path)])


def skill_dirs(install_path, paths):
    dirs = []
    for path in paths:
        directory = install_path / path
        if (directory / "SKILL.md").is_file():
            dirs.append(directory)
        else:
            dirs.extend(Path(d) for d in sorted(glob.glob(f"{glob.escape(str(directory))}/*/")))  # noqa: PTH207
    return dirs


def manifest_skills(install_path):
    manifest = load_json(install_path / ".claude-plugin" / "plugin.json")
    skills = manifest.get("skills") if isinstance(manifest, dict) else None
    if isinstance(skills, str):
        return [skills]
    return [s for s in skills if isinstance(s, str)] if isinstance(skills, list) else []


def marketplace_catalog(marketplace):
    known = load_json(KNOWN_MARKETPLACES)
    entry = known.get(marketplace) if isinstance(known, dict) else None
    location = entry.get("installLocation") if isinstance(entry, dict) else None
    return (
        Path(location) / ".claude-plugin" / "marketplace.json"
        if isinstance(location, str)
        else None
    )


def catalog_skills(catalog, plugin):
    data = load_json(catalog) if catalog else None
    entries = data.get("plugins", []) if isinstance(data, dict) else []
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("name") != plugin:
            continue
        skills = entry.get("skills")
        if isinstance(skills, list):
            return [s for s in skills if isinstance(s, str)]
    return None


def project_skill_dirs():
    cwd = Path.cwd()
    dirs = []
    for directory in (cwd, *cwd.parents):
        dirs.append(directory / ".claude" / "skills")
        if (directory / ".git").exists():
            return dirs
    return dirs[:1]


def collect_skill_files():
    # insertion order is precedence: personal over project skills, then plugins in manifest order
    files = {}
    for skills_dir in (USER_SKILLS_DIR, *project_skill_dirs()):
        for path in sorted(glob.glob(f"{glob.escape(str(skills_dir))}/*/SKILL.md")):  # noqa: PTH207
            files.setdefault(path, None)
    for plugin, marketplace, install_path in installed_plugins():
        for skill_dir in declared_skill_dirs(plugin, marketplace, install_path):
            skill_file = skill_dir / "SKILL.md"
            if skill_file.is_file():
                files.setdefault(str(skill_file), plugin)
    return list(files.items())


def parse_frontmatter(path):
    try:
        text = Path(path).read_text(encoding="utf-8-sig", errors="ignore")
    except OSError:
        return None
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    fm = m.group(1)
    name = frontmatter_value(fm, "name")
    desc = frontmatter_value(fm, "description")
    return {"path": path, "name": name, "description": desc}


def frontmatter_value(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.*)$", fm, re.MULTILINE)
    if not m:
        return ""
    first = m.group(1).strip()
    parts = [] if re.fullmatch(r"([|>][+-]?)?", first) else [first]
    for line in fm[m.end() :].split("\n")[1:]:
        if line and not line[0].isspace():
            break
        parts.append(line.strip())
    value = " ".join(part for part in parts if part)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def clean_description(description):
    # trigger and exclusion clauses name the very words the skill must not match on
    kept = " ".join(s for s in sentences(description) if not BOILERPLATE_SENTENCE.match(s))
    return " ".join(CLAUDE_CODE.sub("", kept).split())


def sentences(text):
    parts = []
    for fragment in re.split(r"(?<=[.!?])\s+", " ".join(text.split())):
        if parts and continues_sentence(parts[-1], fragment):
            parts[-1] = f"{parts[-1]} {fragment}"
        else:
            parts.append(fragment)
    return parts


def continues_sentence(previous, fragment):
    return bool(
        ABBREVIATION_END.search(previous)
        or previous.count('"') % 2
        or previous.count("(") > previous.count(")")
        or fragment[:1].islower()
    )


def classify(description):
    if SKILL_TOOL_SIGNALS.search(description):
        return "skill-tool"
    if CODE_SIGNALS.search(description):
        return "code"
    return "unknown"


def is_reviewer(name, description):
    if not (NAME_PAT.search(name) and DESC_PAT.search(description)):
        return False
    return not EXCLUDE_DESC.search(description)


def main():
    seen_names = set()
    candidates = []
    for path, plugin in collect_skill_files():
        meta = parse_frontmatter(path)
        if not meta:
            continue
        directory = Path(path).parent.name
        # Claude Code registers plugin skills under their directory name, not the frontmatter name
        name = f"{plugin}:{directory}" if plugin else meta["name"] or directory
        if name in seen_names or name in BLACKLIST:
            continue
        seen_names.add(name)
        description = clean_description(meta["description"])
        if not is_reviewer(name.split(":")[-1], description):
            continue
        candidates.append(
            {
                "name": name,
                "category": classify(description),
                "path": meta["path"],
                "description_excerpt": description[:200],
            }
        )
    candidates.sort(key=lambda c: c["name"])
    json.dump({"candidates": candidates, "count": len(candidates)}, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
