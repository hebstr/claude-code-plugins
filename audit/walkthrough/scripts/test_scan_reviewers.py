import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("scan-reviewers.py")


def load_module():
    spec = importlib.util.spec_from_file_location("scan_reviewers", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def write_json(path, data):
    return write(path, json.dumps(data))


def skill(directory, name, description):
    return write(
        directory / "SKILL.md", f"---\nname: {name}\ndescription: {description}\n---\nbody\n"
    )


def git(*args):
    if shutil.which("git") is None:
        pytest.skip("git not installed")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    subprocess.run(["git", *args], check=True, env=env)


def git_init(path):
    path.mkdir(parents=True, exist_ok=True)
    git("init", "-q", str(path))
    return path


@pytest.fixture
def home(tmp_path):
    return tmp_path / "home"


@pytest.fixture
def project(tmp_path):
    path = tmp_path / "project"
    path.mkdir()
    return path


@pytest.fixture
def scan(home, project, monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "PLUGINS_MANIFEST", home / "installed_plugins.json")
    monkeypatch.setattr(module, "KNOWN_MARKETPLACES", home / "known_marketplaces.json")
    monkeypatch.setattr(module, "USER_SKILLS_DIR", home / "skills")
    monkeypatch.setattr(
        module,
        "SETTINGS_FILES",
        (
            home / "settings.json",
            Path(".claude/settings.json"),
            Path(".claude/settings.local.json"),
        ),
    )
    monkeypatch.setattr(module, "MANAGED_SETTINGS_DIR", home / "managed")
    monkeypatch.chdir(project)
    return module


def install(scan, plugins):
    write_json(scan.PLUGINS_MANIFEST, {"version": 2, "plugins": plugins})


def user_install(path):
    return [{"scope": "user", "installPath": str(path)}]


def run_main(scan, capsys):
    scan.main()
    return json.loads(capsys.readouterr().out)


def make_monorepo(root):
    write_json(
        root / ".claude-plugin" / "marketplace.json",
        {
            "plugins": [
                {"name": "posit-dev", "source": "./", "skills": ["./posit-dev/code-reviewer"]},
                {"name": "ggsql", "source": "./", "skills": ["./ggsql/ggsql"]},
            ]
        },
    )
    skill(root / "posit-dev" / "code-reviewer", "code-reviewer", "Review code.")
    skill(root / "ggsql" / "ggsql", "ggsql", "Write SQL.")
    skill(root / "tests" / "fixtures" / "skills" / "fake-review", "fake-review", "Review code.")


def test_marketplace_entry_scopes_monorepo_skills(scan, tmp_path):
    posit, ggsql = tmp_path / "cache" / "posit-dev", tmp_path / "cache" / "ggsql"
    make_monorepo(posit)
    make_monorepo(ggsql)
    install(scan, {"posit-dev@m": user_install(posit), "ggsql@m": user_install(ggsql)})

    assert scan.collect_skill_files() == [
        (str(posit / "posit-dev" / "code-reviewer" / "SKILL.md"), "posit-dev"),
        (str(ggsql / "ggsql" / "ggsql" / "SKILL.md"), "ggsql"),
    ]


def test_marketplace_entry_skills_as_string(scan, tmp_path):
    root = tmp_path / "cache" / "a"
    write_json(
        root / ".claude-plugin" / "marketplace.json",
        {"plugins": [{"name": "a", "source": "./", "skills": "./a/r"}]},
    )
    skill(root / "a" / "r", "r-review", "Review code.")
    skill(root / "skills" / "b-review", "b-review", "Review code.")
    install(scan, {"a@m": user_install(root)})

    assert scan.collect_skill_files() == [(str(root / "a" / "r" / "SKILL.md"), "a")]


def test_root_source_without_existing_listed_path_scans_default(scan, tmp_path):
    root = tmp_path / "cache" / "a"
    write_json(
        root / ".claude-plugin" / "marketplace.json",
        {"plugins": [{"name": "a", "source": "./", "skills": ["./missing"]}]},
    )
    skill(root / "skills" / "code-review", "code-review", "Review code.")
    install(scan, {"a@m": user_install(root)})

    assert scan.collect_skill_files() == [(str(root / "skills" / "code-review" / "SKILL.md"), "a")]


def test_bundled_marketplace_takes_precedence_over_known_catalog(scan, home, tmp_path):
    catalog = tmp_path / "marketplaces" / "m"
    write_json(
        catalog / ".claude-plugin" / "marketplace.json",
        {"plugins": [{"name": "a", "source": "./", "skills": ["./other"]}]},
    )
    write_json(home / "known_marketplaces.json", {"m": {"installLocation": str(catalog)}})
    root = tmp_path / "cache" / "a"
    write_json(
        root / ".claude-plugin" / "marketplace.json",
        {"plugins": [{"name": "a", "source": "./", "skills": ["./mine"]}]},
    )
    skill(root / "mine", "mine", "Review code.")
    skill(root / "other", "other", "Review code.")
    install(scan, {"a@m": user_install(root)})

    assert scan.collect_skill_files() == [(str(root / "mine" / "SKILL.md"), "a")]


def test_missing_known_catalog_entry_scans_default(scan, home, tmp_path):
    write_json(home / "known_marketplaces.json", {"other": {"installLocation": "/nowhere"}})
    plugin = tmp_path / "cache" / "plug"
    skill(plugin / "skills" / "code-review", "code-review", "Review code.")
    install(scan, {"plug@m": user_install(plugin)})

    assert scan.collect_skill_files() == [
        (str(plugin / "skills" / "code-review" / "SKILL.md"), "plug")
    ]


def test_plugin_json_skills_string_and_escaping_paths(scan, tmp_path):
    plugin = tmp_path / "cache" / "plug"
    write_json(plugin / ".claude-plugin" / "plugin.json", {"skills": "./single"})
    skill(plugin / "single", "single", "Review code.")
    skill(tmp_path / "cache" / "outside", "outside", "Review code.")
    install(scan, {"plug@m": user_install(plugin)})

    assert [path for path, _ in scan.collect_skill_files()] == [str(plugin / "single" / "SKILL.md")]
    assert scan.skill_dirs(plugin, ["../outside", str(tmp_path / "cache" / "outside")]) == []


def test_plugin_json_skills_add_to_default_skills_dir(scan, tmp_path):
    plugin = tmp_path / "cache" / "plug"
    write_json(plugin / ".claude-plugin" / "plugin.json", {"skills": ["./extra/", "./single"]})
    skill(plugin / "skills" / "a-review", "a-review", "Review code.")
    skill(plugin / "extra" / "b-review", "b-review", "Review code.")
    skill(plugin / "single", "single", "Review code.")
    install(scan, {"plug@m": user_install(plugin)})

    assert [path for path, _ in scan.collect_skill_files()] == [
        str(plugin / "skills" / "a-review" / "SKILL.md"),
        str(plugin / "extra" / "b-review" / "SKILL.md"),
        str(plugin / "single" / "SKILL.md"),
    ]


def test_first_install_in_manifest_order_wins(scan, tmp_path, capsys):
    newer, older = tmp_path / "cache" / "plug" / "1.10.0", tmp_path / "cache" / "plug" / "1.9.0"
    skill(newer / "skills" / "code-review", "code-review", "Review code.")
    skill(older / "skills" / "code-review", "code-review", "Review code.")
    install(scan, {"plug@m": user_install(older) + user_install(newer)})

    candidates = run_main(scan, capsys)["candidates"]

    assert [c["path"] for c in candidates] == [str(older / "skills" / "code-review" / "SKILL.md")]


def test_project_skills_found_up_to_repo_root(scan, project, capsys, monkeypatch):
    git_init(project)
    sub = project / "sub"
    skill(project / ".claude" / "skills" / "team-review", "team-review", "Review code.")
    skill(sub / ".claude" / "skills" / "sub-review", "sub-review", "Review code.")
    skill(scan.USER_SKILLS_DIR / "team-review", "team-review", "Review code for bugs.")
    monkeypatch.chdir(sub)

    candidates = run_main(scan, capsys)["candidates"]

    assert [(c["name"], c["path"]) for c in candidates] == [
        ("sub-review", str(sub / ".claude" / "skills" / "sub-review" / "SKILL.md")),
        ("team-review", str(scan.USER_SKILLS_DIR / "team-review" / "SKILL.md")),
    ]


def test_project_skills_outside_git_scan_cwd_only(scan, project):
    assert scan.project_skill_dirs() == [project / ".claude" / "skills"]


def test_project_skills_walk_stops_at_git_file(scan, project, monkeypatch):
    write(project / ".git", "gitdir: /elsewhere\n")
    sub = project / "sub"
    sub.mkdir()
    monkeypatch.chdir(sub)

    assert scan.project_skill_dirs() == [sub / ".claude" / "skills", project / ".claude" / "skills"]


def test_skill_without_frontmatter_name_falls_back_to_directory(scan, tmp_path, capsys):
    plugin = tmp_path / "cache" / "plug"
    write(plugin / "skills" / "code-review" / "SKILL.md", "---\ndescription: Review code.\n---\n")
    write(
        scan.USER_SKILLS_DIR / "mine-review" / "SKILL.md", "---\ndescription: Review code.\n---\n"
    )
    install(scan, {"plug@m": user_install(plugin)})

    names = [c["name"] for c in run_main(scan, capsys)["candidates"]]

    assert names == ["mine-review", "plug:code-review"]


def test_main_applies_every_exclusion(scan, home, tmp_path, capsys):
    other = git_init(tmp_path / "other")
    cache = tmp_path / "cache"
    for plugin in ("kept", "off", "elsewhere"):
        skill(cache / plugin / "skills" / "code-review", "code-review", "Review code.")
    skill(cache / "kept" / "skills" / "table-review", "table-review", "Formats tables.")
    write_json(home / "settings.json", {"enabledPlugins": {"off@m": False}})
    elsewhere = {
        "scope": "project",
        "projectPath": str(other),
        "installPath": str(cache / "elsewhere"),
    }
    install(
        scan,
        {
            "kept@m": user_install(cache / "kept"),
            "off@m": user_install(cache / "off"),
            "elsewhere@m": [elsewhere],
        },
    )

    names = [c["name"] for c in run_main(scan, capsys)["candidates"]]

    assert names == ["kept:code-review"]


def test_catalog_entry_scopes_subdir_plugin_skills(scan, home, tmp_path):
    catalog = tmp_path / "marketplaces" / "official"
    write_json(
        catalog / ".claude-plugin" / "marketplace.json",
        {
            "plugins": [
                {
                    "name": "bundle",
                    "source": {"source": "git-subdir", "path": "skills"},
                    "skills": ["./code-review"],
                }
            ]
        },
    )
    write_json(home / "known_marketplaces.json", {"official": {"installLocation": str(catalog)}})
    plugin = tmp_path / "cache" / "bundle"
    skill(plugin / "code-review", "code-review", "Review code.")
    skill(plugin / "undeclared", "undeclared", "Review code.")
    install(scan, {"bundle@official": user_install(plugin)})

    assert scan.collect_skill_files() == [(str(plugin / "code-review" / "SKILL.md"), "bundle")]


def test_catalog_entry_with_subdir_source_adds_to_skills_dir(scan, home, tmp_path):
    catalog = tmp_path / "marketplaces" / "official"
    write_json(
        catalog / ".claude-plugin" / "marketplace.json",
        {"plugins": [{"name": "box", "source": {"source": "url"}, "skills": "./extra"}]},
    )
    write_json(home / "known_marketplaces.json", {"official": {"installLocation": str(catalog)}})
    plugin = tmp_path / "cache" / "box"
    skill(plugin / "skills" / "a-review", "a-review", "Review code.")
    skill(plugin / "extra", "extra", "Review code.")
    install(scan, {"box@official": user_install(plugin)})

    assert [path for path, _ in scan.collect_skill_files()] == [
        str(plugin / "skills" / "a-review" / "SKILL.md"),
        str(plugin / "extra" / "SKILL.md"),
    ]


def test_falls_back_to_skills_dir_without_marketplace_entry(scan, tmp_path):
    plugin = tmp_path / "cache" / "plug"
    skill(plugin / "skills" / "code-review", "code-review", "Review code.")
    skill(plugin / "nested" / "deep", "deep-review", "Review code.")
    install(scan, {"plug@m": user_install(plugin)})

    assert scan.collect_skill_files() == [
        (str(plugin / "skills" / "code-review" / "SKILL.md"), "plug")
    ]


def test_plugin_skills_named_after_directory_user_skills_after_frontmatter(scan, tmp_path, capsys):
    plugin = tmp_path / "cache" / "plug"
    skill(plugin / "skills" / "code-review", "something-else", "Review code for bugs.")
    skill(scan.USER_SKILLS_DIR / "mine", "my-review", "Review code for bugs.")
    install(scan, {"plug@m": user_install(plugin)})

    names = [c["name"] for c in run_main(scan, capsys)["candidates"]]

    assert names == ["my-review", "plug:code-review"]


def test_same_skill_name_in_two_plugins_is_kept_twice(scan, tmp_path, capsys):
    a, b = tmp_path / "cache" / "a", tmp_path / "cache" / "b"
    skill(a / "skills" / "code-review", "code-review", "Review code.")
    skill(b / "skills" / "code-review", "code-review", "Review code.")
    install(scan, {"a@m": user_install(a), "b@m": user_install(b)})

    names = [c["name"] for c in run_main(scan, capsys)["candidates"]]

    assert names == ["a:code-review", "b:code-review"]


def test_blacklist_matches_qualified_name(scan, tmp_path, capsys, monkeypatch):
    plugin = tmp_path / "cache" / "audit"
    skill(plugin / "skills" / "code-review", "code-review", "Review code.")
    skill(plugin / "skills" / "other-review", "other-review", "Review code.")
    install(scan, {"audit@m": user_install(plugin)})
    monkeypatch.setattr(scan, "BLACKLIST", {"audit:code-review"})

    names = [c["name"] for c in run_main(scan, capsys)["candidates"]]

    assert names == ["audit:other-review"]


def test_enabled_plugins_later_settings_files_win(scan, home, project, tmp_path):
    write_json(
        home / "settings.json", {"enabledPlugins": {"a@m": False, "b@m": False, "c@m": True}}
    )
    write_json(project / ".claude" / "settings.json", {"enabledPlugins": {"b@m": True}})
    write_json(project / ".claude" / "settings.local.json", {"enabledPlugins": {"c@m": False}})
    install(scan, {key: user_install(tmp_path / key) for key in ("a@m", "b@m", "c@m", "d@m")})

    assert scan.disabled_plugins() == {"a@m", "c@m"}
    assert [plugin for plugin, _, _ in scan.installed_plugins()] == ["b", "d"]


def test_enabled_plugins_managed_settings_win(scan, home, project):
    write_json(project / ".claude" / "settings.local.json", {"enabledPlugins": {"a@m": True}})
    write_json(home / "managed" / "managed-settings.json", {"enabledPlugins": {"a@m": False}})
    write_json(
        home / "managed" / "managed-settings.d" / "10-team.json",
        {"enabledPlugins": {"b@m": False}},
    )

    assert scan.disabled_plugins() == {"a@m", "b@m"}


@pytest.fixture
def repos(project, tmp_path):
    git_init(project)
    subdir = project / "sub"
    plain = tmp_path / "plain"
    subdir.mkdir()
    plain.mkdir()
    return {"subdir": subdir, "other": git_init(tmp_path / "other"), "plain": plain}


@pytest.mark.parametrize(
    ("inst", "expected"),
    [
        ({"scope": "user"}, True),
        ({"scope": "managed"}, True),
        ({"scope": "project", "projectPath": "{cwd}"}, True),
        ({"scope": "local", "projectPath": "{subdir}"}, True),
        ({"scope": "project", "projectPath": "{other}"}, False),
        ({"scope": "project", "projectPath": "{plain}"}, False),
        ({"scope": "project"}, False),
        ({}, False),
    ],
)
def test_installed_here(scan, repos, inst, expected):
    cwd = str(Path.cwd())
    paths = {"cwd": cwd, **{key: str(value) for key, value in repos.items()}}
    resolved = {key: value.format(**paths) for key, value in inst.items()}

    assert scan.installed_here(resolved, cwd, scan.repo_id(cwd)) is expected


def test_installed_here_matches_worktree_of_install_project(scan, tmp_path):
    main = git_init(tmp_path / "main")
    git(
        "-C",
        str(main),
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "init",
    )
    worktree = tmp_path / "worktree"
    git("-C", str(main), "worktree", "add", "-q", str(worktree))

    inst = {"scope": "local", "projectPath": str(main)}
    assert scan.installed_here(inst, str(worktree), scan.repo_id(str(worktree)))


def test_repo_id_ignores_inherited_git_dir(scan, tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_DIR", str(git_init(tmp_path / "other") / ".git"))

    assert scan.repo_id(str(Path.cwd())) is None


def test_installed_here_outside_git_matches_exact_path_only(scan, tmp_path):
    cwd = str(Path.cwd())
    other = str(git_init(tmp_path / "other"))

    assert scan.repo_id(cwd) is None
    assert scan.installed_here({"scope": "project", "projectPath": cwd}, cwd, None)
    assert not scan.installed_here({"scope": "project", "projectPath": other}, cwd, None)


@pytest.mark.parametrize(
    ("content", "warning"),
    [
        ('{"version": 2, "plugins": {', "unreadable plugin manifest"),
        ('{"version": 2, "plugins": []}', "unreadable plugin manifest"),
        ("[]", "unreadable plugin manifest"),
        (
            '{"version": 1, "plugins": {"audit@hebstr": {"installPath": "/x"}}}',
            "skipping malformed manifest entry audit@hebstr",
        ),
    ],
)
def test_malformed_manifest_warns_and_yields_nothing(scan, capsys, content, warning):
    write(scan.PLUGINS_MANIFEST, content)

    assert scan.installed_plugins() == []
    assert warning in capsys.readouterr().err


def test_malformed_manifest_still_emits_json(scan, capsys):
    write(scan.PLUGINS_MANIFEST, "{")

    assert run_main(scan, capsys)["count"] == 0


def test_non_dict_install_is_skipped_silently(scan, tmp_path, capsys):
    target = tmp_path / "cache" / "a"
    install(scan, {"a@m": ["oops", {"scope": "user", "installPath": str(target)}]})

    assert scan.installed_plugins() == [("a", "m", target)]
    assert capsys.readouterr().err == ""


def test_wrongly_typed_install_fields_are_skipped(scan, tmp_path):
    install(
        scan,
        {
            "a@m": [{"scope": "user", "installPath": 5}],
            "b@m": [{"scope": "project", "projectPath": ["x"], "installPath": str(tmp_path)}],
        },
    )

    assert scan.installed_plugins() == []


def test_load_json_accepts_byte_order_mark(scan, tmp_path):
    path = tmp_path / "data.json"
    path.write_bytes(b'\xef\xbb\xbf{"a": "\xc3\xa9"}')

    assert scan.load_json(path) == {"a": "é"}


def test_load_json_rejects_non_utf8(scan, tmp_path):
    path = tmp_path / "data.json"
    path.write_bytes(b'{"a": "\xe9"}')

    assert scan.load_json(path) is None


def test_missing_manifest_is_silent(scan, capsys):
    assert scan.installed_plugins() == []
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ("Code reviewer. Not for SKILL.md files.", "code"),
        ("Reviews Claude Code hooks and settings.json", "unknown"),
        ("Formats tables. Not for code review (e.g. PR audits).", "unknown"),
        (
            'User-invocable ONLY via `/x`. Does not auto-trigger on "audit MCP server". '
            "Adversarial reviewer for MCP servers: reads tool descriptions and code.",
            "skill-tool",
        ),
    ],
)
def test_classify_ignores_disclaimed_words(scan, description, expected):
    assert scan.classify(scan.clean_description(description)) == expected


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ("Does not auto-trigger on review", False),
        ("Critical code review; see tutorial link", True),
        ("An interactive tutorial to review code", False),
        (
            'Formats tables. Does not auto-trigger on "is it wrong?", "review it", or e.g. audit.',
            False,
        ),
        ('Formats tables. Do NOT trigger on "is it wrong? Review this" requests.', False),
        ("Formats tables. Not for writing a parser. or any code review.", False),
        ("Formats tables. Not for tables. Adversarial reviewer of code.", True),
        ('Does not auto-trigger on 5" screens. Adversarial reviewer of code.', True),
        ("Not for drafts (see docs. Adversarial reviewer of code.", True),
        ("Formats tables. Does not auto-trigger on “is it wrong? Review this” requests.", False),
        ("Formats tables. Does not auto-trigger on « c'est faux ? Audit » requests.", False),
        ("Not for PRs. posit reviewer that audits R code.", True),
        ("Formats tables. Do not use for code review.", False),
        ("Formats tables. Don't use for code review.", False),
        ("Formats tables. Not for code, i.e. review tools.", False),
        ("Formats tables. Not for linting, cf. review guides.", False),
        ("Formats tables. Not for docs vs. review tools.", False),
    ],
)
def test_is_reviewer_filters(scan, description, expected):
    assert scan.is_reviewer("x-review", scan.clean_description(description)) is expected


SWEEP_DESCRIPTION = (
    "Full project review: detects project type and size, spawns specialist background "
    "agents with disjoint scopes (architecture, quality, tests, docs), consolidates "
    "findings into one deduplicated report sorted by severity, then offers an "
    "interactive walkthrough. Not for: single-file reviews, PR or diff reviews, or "
    "non-code document reviews (papers, resumes, CVs)."
)


def test_project_wide_reviewer_named_sweep_is_scanned(scan):
    assert scan.is_reviewer("sweep", scan.clean_description(SWEEP_DESCRIPTION)) is True


def test_project_wide_reviewer_named_sweep_classifies_as_code(scan):
    assert scan.classify(scan.clean_description(SWEEP_DESCRIPTION)) == "code"


def test_clean_description_drops_leading_boilerplate(scan):
    description = (
        "User-invocable ONLY via `/audit:x`. Does not auto-trigger on mentions of y.\n"
        "  Adversarial reviewer."
    )

    assert scan.clean_description(description) == "Adversarial reviewer."


@pytest.mark.parametrize(
    ("frontmatter", "name", "description"),
    [
        ("name: a\ndescription: |\n  Review code block.", "a", "Review code block."),
        ("name: a\ndescription: >-\n  Review code\n  folded.", "a", "Review code folded."),
        ("name: a\ndescription: |2\n  Review code.", "a", "Review code."),
        ("name: a\ndescription:\nallowed-tools: Read", "a", ""),
        ("name: a\ndescription: Review code.\nallowedTools: Read", "a", "Review code."),
        (
            'name: "walkthrough"\ndescription: "Review code quoted."',
            "walkthrough",
            "Review code quoted.",
        ),
    ],
)
def test_parse_frontmatter_forms(scan, tmp_path, frontmatter, name, description):
    path = write(tmp_path / "SKILL.md", f"---\n{frontmatter}\n---\nbody\n")

    meta = scan.parse_frontmatter(str(path))

    assert meta is not None
    assert (meta["name"], meta["description"]) == (name, description)


def test_parse_frontmatter_with_byte_order_mark(scan, tmp_path):
    path = tmp_path / "SKILL.md"
    path.write_bytes(b"\xef\xbb\xbf" + b"---\nname: a\ndescription: Review code.\n---\n")

    meta = scan.parse_frontmatter(str(path))

    assert meta is not None
    assert meta["name"] == "a"


def test_parse_frontmatter_without_frontmatter(scan, tmp_path):
    path = write(tmp_path / "SKILL.md", "no frontmatter\n")

    assert scan.parse_frontmatter(str(path)) is None
