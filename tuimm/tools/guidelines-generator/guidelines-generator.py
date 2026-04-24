#!/usr/bin/env python3
"""guidelines-generator — Extract conventions from committed files via AI.

Phases:
  1. extract  — Read each source file, extract conventions → .guidelines/raw/{cat}/{file}.md
  2. review   — Deduplicate and consolidate per category → .guidelines/reviewed/{cat}.md
  3. split    — Split into specific + shared → docs/guidelines/

Usage:
  --scan                       Classify files, show table
  --phase extract|review|split|all   Run phase(s)
  --only tests,components      Filter categories
  --dir src/features/booking   Filter directory
  --report                     Show progress
  --reset-phase review|all     Reset progress for a phase
  --to-skills                  Copy testing guidelines to tuimm_testing-nuxt-* skills
  --agent NAME                 Override agent (default: tuimm_default)
  --model NAME                 Override model (default: claude-opus-4.6)
  --workers N                  Parallel workers for phase 1 (default: 3)
  --max-tasks N                Limit extraction tasks
  --bg/--status/--stop/--tail  Background mode via bg
"""
import json, sys, subprocess, re, signal, os, argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.expanduser("~/.kiro/tools/bg"))
sys.path.insert(0, os.path.expanduser("~/.kiro/tools/logd"))

try:
    from bg import setup_bg
    setup_bg()
except ImportError:
    pass

try:
    from loglib import get_logger
    log = get_logger("guidelines-generator")
except ImportError:
    log = None

TIMEOUT = 300
MAX_RETRIES = 2
DEFAULT_AGENT = "tuimm_default"
DEFAULT_MODEL = "claude-opus-4.6"
TEMPLATES_DIR = Path(os.path.expanduser("~/.kiro/skills/tuimm-qg-workflow/assets/templates/guidelines-generator"))
SKILLS_DIR = Path(os.path.expanduser("~/.kiro/skills"))

STOP = False
def _sigint(sig, frame):
    global STOP
    print("\n⏸️  Stopping after current step... (progress saved)")
    STOP = True
signal.signal(signal.SIGINT, _sigint)

# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class FileInfo:
    path: str
    category: str
    sub_category: str = ""
    loc: int = 0
    skip_reason: str = ""

# ── Category map ─────────────────────────────────────────────────────────────

FRONTEND_CATEGORIES = {
    "components": "components", "composables": "composables", "plugins": "plugins",
    "stores": "stores", "pages": "pages", "middleware": "middleware", "utils": "utils",
    "helpers": "utils", "services": "services", "constants": "constants",
    "layouts": "layouts", "server": "server", "shared": "shared", "config": "config",
    "features": "features", "types": "types", "modules": "modules", "layers": "layers",
    "repository": "repository",
}

JAVA_CATEGORIES = {
    "controller": "controllers", "controllers": "controllers",
    "service": "services", "services": "services",
    "repository": "repository", "repositories": "repository",
    "entity": "entities", "entities": "entities",
    "model": "models", "models": "models", "domain": "domain",
    "dto": "dtos", "dtos": "dtos",
    "mapper": "mappers", "mappers": "mappers",
    "config": "configuration", "configuration": "configuration",
    "exception": "exceptions", "exceptions": "exceptions",
    "webclient": "webclient", "client": "webclient", "clients": "webclient",
    "security": "security", "auth": "security",
    "validation": "validation", "validator": "validation",
    "adapter": "adapters", "adapters": "adapters",
    "port": "ports", "ports": "ports",
    "infrastructure": "infrastructure",
    "application": "application",
    "utils": "utils", "util": "utils", "helpers": "utils",
    "middleware": "middleware", "filter": "filters", "filters": "filters",
    "interceptor": "interceptors", "interceptors": "interceptors",
}

PYTHON_CATEGORIES = {
    "models": "models", "model": "models",
    "views": "views", "view": "views",
    "serializers": "serializers", "serializer": "serializers",
    "services": "services", "service": "services",
    "tasks": "tasks", "celery": "tasks",
    "utils": "utils", "helpers": "utils",
    "managers": "managers", "manager": "managers",
    "admin": "admin", "forms": "forms",
    "middleware": "middleware", "signals": "signals",
    "commands": "commands", "management": "commands",
    "config": "configuration", "settings": "configuration",
    "api": "api", "endpoints": "api", "routers": "api", "routes": "api",
    "schemas": "schemas", "schema": "schemas",
    "repository": "repository", "repositories": "repository",
    "domain": "domain", "core": "core",
}

GO_CATEGORIES = {
    "handler": "handlers", "handlers": "handlers",
    "service": "services", "services": "services",
    "repository": "repository", "repositories": "repository",
    "model": "models", "models": "models",
    "middleware": "middleware",
    "config": "configuration", "configuration": "configuration",
    "cmd": "cmd", "internal": "internal", "pkg": "pkg",
    "api": "api", "transport": "transport",
    "domain": "domain", "entity": "entities",
    "utils": "utils", "util": "utils",
}

FRAMEWORK_CATEGORIES = {
    "Java + Maven": JAVA_CATEGORIES,
    "Java + Gradle": JAVA_CATEGORIES,
    "Python": PYTHON_CATEGORIES,
    "Go": GO_CATEGORIES,
}

FRONTEND_EXCLUDES = {"__mocks__", "mock-server", "shim-types", "public", "__snapshots__",
                     "node_modules", ".nuxt", ".output", "dist", "coverage"}

JAVA_EXCLUDES = {"target", "build", ".mvn", ".gradle", "generated", "generated-sources"}

PYTHON_EXCLUDES = {"__pycache__", ".venv", "venv", "migrations", "static", "media", "dist", "build", ".eggs"}

GO_EXCLUDES = {"vendor", "bin", "testdata"}

FRAMEWORK_EXCLUDES = {
    "Java + Maven": JAVA_EXCLUDES,
    "Java + Gradle": JAVA_EXCLUDES,
    "Python": PYTHON_EXCLUDES,
    "Go": GO_EXCLUDES,
}

DEFAULT_CATEGORIES = FRONTEND_CATEGORIES
DEFAULT_EXCLUDES = FRONTEND_EXCLUDES

SHARED_TOPICS = [
    "typescript", "scss-styling", "imports-aliases", "documentation",
    "error-handling", "logging", "async-patterns", "reactivity",
    "testing", "naming", "accessibility",
]

# Test sub-classification markers (detected by reading file content)
TEST_MARKERS = {
    "components": [r"mount\w*\(", r"mountSuspended", r"\.vue['\"]", r"wrapper\.", r"shallowMount"],
    "composables": [r"use[A-Z]\w+", r"composables?/"],
    "stores": [r"createPinia|defineStore|setActivePinia|\.store"],
    "utils": [r"utils?/|helpers?/"],
    "middleware": [r"middleware/"],
    "services": [r"services?/|api/|\$fetch|useFetch|ofetch"],
    "plugins": [r"plugins?/"],
}

# ── Scanner ──────────────────────────────────────────────────────────────────

def detect_framework(repo_root: Path) -> str:
    """Detect framework from project files."""
    pkg = repo_root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "nuxt" in deps:
                ver = deps["nuxt"].lstrip("^~>=")
                major = int(ver.split(".")[0]) if ver[0].isdigit() else 4
                return f"Nuxt {major} + Vue 3 + TypeScript" if major >= 3 else f"Nuxt {major} + Vue 2"
            if "react-native" in deps or "expo" in deps:
                return "React Native + Expo + TypeScript"
            return "TypeScript"
        except Exception:
            return "TypeScript"
    if (repo_root / "pom.xml").exists():
        return "Java + Maven"
    if (repo_root / "build.gradle").exists() or (repo_root / "build.gradle.kts").exists():
        return "Java + Gradle"
    if (repo_root / "pyproject.toml").exists() or (repo_root / "setup.py").exists():
        return "Python"
    if (repo_root / "go.mod").exists():
        return "Go"
    if (repo_root / "Cargo.toml").exists():
        return "Rust"
    return "Unknown"

def load_config(repo_root: Path) -> dict:
    """Load optional .guidelines.json for custom categories/excludes."""
    cfg_file = repo_root / ".guidelines.json"
    if cfg_file.exists():
        try:
            return json.loads(cfg_file.read_text())
        except Exception:
            pass
    return {}

def get_committed_files(repo_root: Path, extensions_re: str | None = None) -> list[str]:
    """Get committed files via git ls-files."""
    result = subprocess.run(["git", "ls-files", "--cached"], capture_output=True, text=True, cwd=repo_root)
    if result.returncode != 0:
        return []
    pattern = extensions_re or r'\.(vue|ts|js|tsx|jsx)$'
    files = []
    for f in result.stdout.strip().split("\n"):
        if not f or not re.search(pattern, f):
            continue
        if "__snapshots__" in f or "/" not in f:
            continue
        files.append(f)
    return sorted(files)

def classify_file(filepath: str, categories: dict, excludes: set) -> str | None:
    """Classify a file by its deepest matching directory."""
    # Strip app/ prefix (Nuxt 4 convention)
    rel = filepath.replace("app/", "", 1) if filepath.startswith("app/") else filepath
    parts = rel.split("/")[:-1]  # dirs only, exclude filename
    if any(p in excludes for p in parts):
        return None
    # Deepest match wins: features/booking/components/ → "components"
    for part in reversed(parts):
        cat = categories.get(part)
        if cat:
            return cat
    return None

def is_test_file(filepath: str) -> bool:
    if re.search(r'\.(test|spec)\.(ts|js|tsx|jsx)$', filepath):
        return True
    if re.search(r'(Test|Tests|IT)\.java$', filepath):
        return True
    if filepath.startswith("test/") or "/test/" in filepath or "/tests/" in filepath:
        if filepath.endswith(".java") or filepath.endswith(".py") or filepath.endswith(".go"):
            return True
    if filepath.endswith("_test.go") or filepath.endswith("_test.py") or filepath.startswith("test_"):
        return True
    return False

def classify_test(filepath: str, content: str, test_subcats: dict | None = None) -> str:
    """Sub-classify a test file by what it tests."""
    rel = filepath.replace("app/", "", 1) if filepath.startswith("app/") else filepath
    parts = rel.split("/")

    # Agent-proposed subcategories: check dir names and filename suffix
    if test_subcats:
        for part in parts[:-1]:
            part_lower = part.lower()
            if part_lower in test_subcats:
                return test_subcats[part_lower]
        # Filename suffix: FooControllerTest.java → "controller" → lookup
        filename = parts[-1] if parts else ""
        name = re.sub(r'\.(java|py|go|ts|js|tsx|jsx)$', '', filename)
        name = re.sub(r'(Test|Tests|IT|Spec|_test|_spec)$', '', name, flags=re.IGNORECASE)
        name_lower = name.lower()
        for key in test_subcats:
            if name_lower.endswith(key.lower()):
                return test_subcats[key]

    # Fallback: path-based (frontend)
    for part in parts:
        if part in ("composables", "composable"):
            return "composables"
        if part in ("stores", "store"):
            return "stores"
        if part in ("utils", "helpers"):
            return "utils"
        if part in ("middleware",):
            return "middleware"
        if part in ("services", "api"):
            return "services"
        if part in ("plugins",):
            return "plugins"
        if part in ("components",):
            return "components"

    # Fallback: content-based detection
    scores = {}
    for cat, markers in TEST_MARKERS.items():
        score = sum(1 for m in markers if re.search(m, content))
        if score > 0:
            scores[cat] = score
    if scores:
        top_score = max(scores.values())
        tied = [c for c, s in scores.items() if s == top_score]
        if len(tied) == 1:
            return tied[0]
        # Tiebreaker: prefer category mentioned anywhere in path
        for c in tied:
            if c in filepath.lower():
                return c
        # Final tiebreaker: specificity order
        priority = ["components", "stores", "services", "composables", "plugins", "middleware", "utils"]
        for c in priority:
            if c in tied:
                return c
        return tied[0]
    return "general"

def count_loc(filepath: str, repo_root: Path) -> int:
    """Count non-blank, non-comment lines."""
    try:
        content = (repo_root / filepath).read_text(errors="replace")
        return sum(1 for line in content.split("\n") if line.strip() and not line.strip().startswith("//"))
    except Exception:
        return 0

def load_agent_categories(work_dir: Path) -> dict | None:
    """Load agent-proposed categories from .guidelines/categories.json."""
    cat_file = work_dir / "categories.json"
    if cat_file.exists():
        try:
            return json.loads(cat_file.read_text())
        except Exception:
            return None
    return None


def phase_categorize(repo_root: Path, work_dir: Path, agent: str, model: str, extensions_re: str | None = None):
    """Ask the agent to propose categories based on repo structure."""
    all_files = get_committed_files(repo_root, extensions_re=extensions_re)
    if not all_files:
        print("❌ No files found")
        return

    # Build directory tree with file counts
    dir_counts: dict[str, int] = {}
    for f in all_files:
        parts = f.split("/")
        for i in range(1, len(parts)):
            d = "/".join(parts[:i])
            dir_counts[d] = dir_counts.get(d, 0) + 1

    # Show top dirs only (skip deep nesting with few files)
    tree_lines = []
    for d in sorted(dir_counts.keys()):
        depth = d.count("/")
        if depth <= 4 or dir_counts[d] >= 3:
            tree_lines.append(f"  {d}/ ({dir_counts[d]} files)")

    dir_tree = "\n".join(tree_lines[:200])  # cap for prompt size

    framework = detect_framework(repo_root)
    suggested = FRAMEWORK_CATEGORIES.get(framework, DEFAULT_CATEGORIES)
    suggested_excludes = list(FRAMEWORK_EXCLUDES.get(framework, DEFAULT_EXCLUDES))

    # Sample filenames for context
    sample = all_files[:80] if len(all_files) > 80 else all_files
    sample_block = "\n".join(f"  {f}" for f in sample)

    prompt = (
        f"Analyze this {framework} project and propose categories for guideline extraction.\n\n"
        f"Directory structure:\n{dir_tree}\n\n"
        f"Sample files:\n{sample_block}\n\n"
        f"Suggested categories (directory name → category label):\n{json.dumps(suggested, indent=2)}\n\n"
        f"Suggested excludes:\n{json.dumps(suggested_excludes)}\n\n"
        f"Instructions:\n"
        f"- Analyze the actual structure. Use the suggestions as starting point but adapt to what you see.\n"
        f"- Add categories for directories not covered. Remove ones that don't exist in this project.\n"
        f"- For test_subcategories: map directory names or class name suffixes (lowercase, without Test/Tests/IT/Spec) "
        f"to category labels. Example: \"controller\" → \"controllers\" means *ControllerTest.java or tests in controller/ "
        f"dirs go to tests/controllers.\n"
        f"- Return ONLY a JSON object with this structure, no commentary:\n"
        f'{{"categories": {{"dirname": "label", ...}}, '
        f'"test_subcategories": {{"suffix_or_dirname": "label", ...}}, '
        f'"excludes": ["dir1", "dir2"]}}'
    )

    print(f"\n  🤖 Asking agent to propose categories for {framework} project...")
    raw = kiro(prompt, agent, model, repo_root)
    if not raw:
        print("  ❌ Agent categorization failed — using defaults")
        return

    content = parse_response(raw)
    # Extract JSON from response
    json_match = re.search(r'\{[\s\S]*\}', content)
    if not json_match:
        print("  ❌ No JSON in agent response — using defaults")
        return

    try:
        result = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON from agent: {e} — using defaults")
        return

    cats = result.get("categories", {})
    test_cats = result.get("test_subcategories", {})
    excludes = result.get("excludes", [])

    (work_dir / "categories.json").write_text(json.dumps(result, indent=2))

    print(f"  ✅ Agent proposed {len(cats)} categories, {len(test_cats)} test subcategories, {len(excludes)} excludes")
    for label in sorted(set(cats.values())):
        dirs = [k for k, v in cats.items() if v == label]
        print(f"    {label}: {', '.join(dirs)}")
    if test_cats:
        print(f"  Test subcategories:")
        for label in sorted(set(test_cats.values())):
            keys = [k for k, v in test_cats.items() if v == label]
            print(f"    tests/{label}: {', '.join(keys)}")


def scan(repo_root: Path, only: list[str] | None = None, dir_filter: str | None = None, extensions_re: str | None = None, extra_categories: dict | None = None) -> list[FileInfo]:
    """Scan repo and classify all committed files."""
    cfg = load_config(repo_root)
    framework = detect_framework(repo_root)
    work_dir = repo_root / ".guidelines"

    # Agent categories take priority, then framework defaults
    agent_cats = load_agent_categories(work_dir)
    if agent_cats:
        base_categories = agent_cats.get("categories", FRAMEWORK_CATEGORIES.get(framework, DEFAULT_CATEGORIES))
        base_excludes = set(agent_cats.get("excludes", FRAMEWORK_EXCLUDES.get(framework, DEFAULT_EXCLUDES)))
    else:
        base_categories = FRAMEWORK_CATEGORIES.get(framework, DEFAULT_CATEGORIES)
        base_excludes = FRAMEWORK_EXCLUDES.get(framework, DEFAULT_EXCLUDES)

    categories = {**base_categories, **cfg.get("categories", {}), **(extra_categories or {})}
    excludes = base_excludes | set(cfg.get("exclude", []))
    test_subcats = agent_cats.get("test_subcategories", {}) if agent_cats else {}

    all_files = get_committed_files(repo_root, extensions_re=extensions_re)
    if dir_filter:
        all_files = [f for f in all_files if f.startswith(dir_filter)]

    only_tests = only and "tests" in only
    results = []

    for filepath in all_files:
        is_test = is_test_file(filepath)

        # If --only tests, skip non-test files
        if only_tests and not is_test:
            if only and len(only) == 1:
                continue
        # If --only but NOT tests, skip test files
        if only and not only_tests and is_test:
            continue

        if is_test:
            try:
                content = (repo_root / filepath).read_text(errors="replace")
            except Exception:
                content = ""
            sub_cat = classify_test(filepath, content, test_subcats)
            loc = sum(1 for line in content.split("\n") if line.strip() and not line.strip().startswith("//"))
            results.append(FileInfo(path=filepath, category="tests", sub_category=sub_cat, loc=loc))
        else:
            cat = classify_file(filepath, categories, excludes)
            if cat is None:
                continue
            if only and cat not in only:
                continue
            loc = count_loc(filepath, repo_root)
            if loc < 5:
                results.append(FileInfo(path=filepath, category=cat, loc=loc, skip_reason="too_small"))
                continue
            results.append(FileInfo(path=filepath, category=cat, loc=loc))

    return results

# ── Progress ─────────────────────────────────────────────────────────────────

def load_progress(work_dir: Path) -> dict:
    pf = work_dir / ".progress.json"
    if pf.exists():
        return json.loads(pf.read_text())
    return {"extract": {"done": [], "failed": []}, "review": {"done": [], "failed": []}, "split": {"done": [], "failed": []}}

def save_progress(work_dir: Path, progress: dict):
    (work_dir / ".progress.json").write_text(json.dumps(progress, indent=2))

# ── Helpers ──────────────────────────────────────────────────────────────────

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def kiro(msg: str, agent: str, model: str, repo_root: Path) -> str | None:
    """Call kiro-cli, return cleaned stdout or None on failure."""
    try:
        result = subprocess.run(
            ["kiro-cli", "chat", "--no-interactive", "-a", "--model", model, "--agent", agent, msg],
            capture_output=True, text=True, timeout=TIMEOUT, cwd=repo_root
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if stderr:
                print(f"      [kiro-cli error] {stderr[:200]}")
            return None
        return re.sub(r'\x1b\[[0-9;]*m', '', result.stdout).strip()
    except subprocess.TimeoutExpired:
        print(f"      [kiro-cli timeout] {TIMEOUT}s exceeded")
        return None
    except Exception as e:
        print(f"      [kiro-cli exception] {e}")
        return None

def parse_response(raw: str, heading: str | None = None) -> str:
    """Extract LLM response from kiro-cli output."""
    lines = raw.split("\n")
    last_start = 0
    for i, line in enumerate(lines):
        if line.startswith("> "):
            last_start = i
    result = [line.lstrip("> ").rstrip("\x07") for line in lines[last_start:]]
    content = "\n".join(result).strip()
    if heading:
        idx = content.find(heading)
        if idx >= 0:
            content = content[idx:].strip()
    for marker in ["Want me to", "Shall I", "Let me know", "Would you like"]:
        idx = content.rfind(marker)
        if idx > 0:
            content = content[:idx].strip()
    return content


def get_categories_with_files(files: list[FileInfo]) -> list[tuple[str, list[FileInfo]]]:
    """Group files by effective category (tests use sub_category), sorted by count."""
    cats: dict[str, list[FileInfo]] = {}
    for f in files:
        if f.skip_reason:
            continue
        key = f"tests/{f.sub_category}" if f.category == "tests" and f.sub_category else f.category
        cats.setdefault(key, []).append(f)
    return sorted(cats.items(), key=lambda x: len(x[1]))

# ── Phase 1: Extract ─────────────────────────────────────────────────────────

def phase_extract(files: list[FileInfo], repo_root: Path, work_dir: Path,
                  agent: str, model: str, framework: str, workers: int, max_tasks: int | None):
    """Generate autobuild tasks and run extraction."""
    progress = load_progress(work_dir)
    cats = get_categories_with_files(files)

    # Load template
    tmpl_path = TEMPLATES_DIR / "extract.md"
    if not tmpl_path.exists():
        print(f"❌ Template not found: {tmpl_path}")
        return
    template = tmpl_path.read_text()

    tasks_dir = work_dir / "tasks"
    raw_dir = work_dir / "raw"
    ensure_dir(tasks_dir)
    ensure_dir(raw_dir)

    # Generate tasks for pending files
    task_count = 0
    for cat, cat_files in cats:
        cat_dir = raw_dir / cat.replace("/", os.sep)
        ensure_dir(cat_dir)
        for f in cat_files:
            if f.path in progress["extract"]["done"]:
                continue
            if max_tasks and task_count >= max_tasks:
                break

            safe_name = f.path.replace("/", "_").replace(".", "_")
            output_path = f".guidelines/raw/{cat}/{Path(f.path).name}.md"
            task_content = template.replace("{SOURCE_PATH}", f.path) \
                .replace("{OUTPUT_PATH}", output_path) \
                .replace("{CATEGORY}", cat) \
                .replace("{FRAMEWORK}", framework)

            task_file = tasks_dir / f"{task_count:03d}_{safe_name}.md"
            task_file.write_text(task_content)
            task_count += 1

    if task_count == 0:
        print("✅ All files already extracted")
        return

    # Generate autobuild.json
    ab_config = {
        "agent": agent,
        "model": model,
        "review": "none",
        "max_retries": MAX_RETRIES,
        "timeout": TIMEOUT,
        "parallel": {"max_workers": workers},
        "health": {"builtin": True, "checks": []}
    }
    (work_dir / "autobuild.json").write_text(json.dumps(ab_config, indent=2))

    print(f"📝 Generated {task_count} extraction tasks")
    print(f"🚀 Running autobuild...")

    # Run autobuild
    engine = os.path.expanduser("~/.kiro/tools/autobuild/engine.py")
    result = subprocess.run(
        [sys.executable, engine, str(tasks_dir)],
        cwd=repo_root
    )

    # Update progress from raw output files (not autobuild's progress — that's fragile)
    for cat, cat_files in cats:
        for f in cat_files:
            if f.path in progress["extract"]["done"]:
                continue
            raw_file = raw_dir / cat.replace("/", os.sep) / f"{Path(f.path).name}.md"
            if raw_file.exists() and raw_file.stat().st_size > 0:
                progress["extract"]["done"].append(f.path)
    save_progress(work_dir, progress)

# ── Phase 2: Review ──────────────────────────────────────────────────────────

def phase_review(repo_root: Path, work_dir: Path, agent: str, model: str):
    """Consolidate raw extractions per category."""
    progress = load_progress(work_dir)
    raw_dir = work_dir / "raw"
    reviewed_dir = work_dir / "reviewed"
    ensure_dir(reviewed_dir)

    if not raw_dir.exists():
        print("❌ No raw/ directory — run extract phase first")
        return

    for cat_path in sorted(raw_dir.rglob("*")):
        if not cat_path.is_dir():
            continue
        cat = str(cat_path.relative_to(raw_dir))
        if cat in progress["review"]["done"] or STOP:
            continue

        # Collect all raw bullets for this category
        raw_files = sorted(cat_path.glob("*.md"))
        if not raw_files:
            continue

        raw_content = ""
        for rf in raw_files:
            raw_content += rf.read_text() + "\n"

        if len(raw_content.strip()) < 20:
            progress["review"]["done"].append(cat)
            save_progress(work_dir, progress)
            continue

        msg = (
            f"Below are raw pattern bullets for '{cat}' extracted from source files.\n"
            f"Clean them up:\n"
            f"1. Remove exact duplicates\n"
            f"2. Merge near-duplicates (same idea, different wording) into the best version\n"
            f"3. Remove patterns too specific to one file (not generalizable)\n"
            f"4. Group related patterns under sub-headings (## Topic)\n"
            f"5. Keep bullet-point format (- rule)\n"
            f"6. Keep ONLY actionable, generalizable conventions\n\n"
            f"Output the full cleaned file starting with '# Guidelines — {cat}'. "
            f"No commentary, no explanations.\n\n"
            f"---RAW BULLETS---\n{raw_content}\n---END---"
        )
        raw = kiro(msg, agent, model, repo_root)
        if raw is None:
            print(f"  ❌ review/{cat} — kiro-cli failed")
            if cat not in progress["review"]["failed"]:
                progress["review"]["failed"].append(cat)
            save_progress(work_dir, progress)
            continue

        content = parse_response(raw, "# Guidelines")
        if not content or len(content) < 20:
            print(f"  ⚠️  review/{cat} — empty response")
            continue

        out_file = reviewed_dir / f"{cat.replace('/', '_')}.md"
        out_file.write_text(content + "\n")
        print(f"  ✅ review/{cat} — {len(content)} chars")
        progress["review"]["done"].append(cat)
        progress["review"]["failed"] = [c for c in progress["review"]["failed"] if c != cat]
        save_progress(work_dir, progress)

# ── Phase 3: Split (deterministic) ───────────────────────────────────────────

def _parse_reviewed(content: str) -> list[tuple[str, str]]:
    """Parse reviewed .md into [(section, bullet), ...]. Section is '' for top-level."""
    section = ""
    items = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## "):
            section = stripped[3:].strip()
        elif stripped.startswith("- "):
            items.append((section, stripped))
    return items

def _chunk_bullets(content: str, chunk_size: int = 15) -> list[str]:
    """Extract bullets from content and return as text chunks."""
    bullets = [l for l in content.splitlines() if l.strip().startswith("- ")]
    if not bullets:
        return []
    return ["\n".join(bullets[i:i + chunk_size]) for i in range(0, len(bullets), chunk_size)]


def phase_split(repo_root: Path, work_dir: Path, agent: str, model: str, to_skills: bool):
    """Copy reviewed files to output directory. Shared extraction happens in refine phase."""
    progress = load_progress(work_dir)
    reviewed_dir = work_dir / "reviewed"
    guidelines_dir = repo_root / "docs" / "guidelines"
    shared_dir = guidelines_dir / "shared"
    tests_dir = guidelines_dir / "tests"
    ensure_dir(guidelines_dir)
    ensure_dir(shared_dir)
    ensure_dir(tests_dir)

    if not reviewed_dir.exists():
        print("❌ No reviewed/ directory — run review phase first")
        return

    for reviewed_file in sorted(reviewed_dir.glob("*.md")):
        cat = reviewed_file.stem.replace("_", "/")
        is_test_cat = cat.startswith("tests/")
        cat_label = cat.split("/")[-1] if is_test_cat else cat
        content = reviewed_file.read_text()
        n = sum(1 for l in content.splitlines() if l.strip().startswith("- "))

        if is_test_cat:
            out = tests_dir / f"{cat_label}.md"
        else:
            out = guidelines_dir / f"{cat_label}.md"
        out.write_text(content)
        print(f"  ✅ {cat} — {n} bullets")

        if cat not in progress["split"]["done"]:
            progress["split"]["done"].append(cat)

    save_progress(work_dir, progress)

    if to_skills and tests_dir.exists():
        _copy_to_skills(tests_dir)

def _copy_to_skills(tests_dir: Path):
    """Copy testing guidelines to tuimm_testing-nuxt-* skills."""
    skill_map = {
        "components": "tuimm_testing-nuxt-component",
        "composables": "tuimm_testing-nuxt-composable",
        "stores": "tuimm_testing-nuxt-store",
        "utils": "tuimm_testing-nuxt-utility",
        "middleware": "tuimm_testing-nuxt-middleware",
        "services": "tuimm_testing-nuxt-api-layer",
        "plugins": "tuimm_testing-nuxt-plugin",
    }
    for test_file in tests_dir.glob("*.md"):
        skill_name = skill_map.get(test_file.stem)
        if skill_name:
            skill_dir = SKILLS_DIR / skill_name
            ensure_dir(skill_dir)
            content = test_file.read_text()
            skill_content = (
                f"# {skill_name}\n\n"
                f"Testing guidelines for Nuxt {test_file.stem}, "
                f"extracted from real repo patterns.\n\n"
                f"{content.split(chr(10), 2)[-1] if chr(10) in content else content}"
            )
            (skill_dir / "SKILL.md").write_text(skill_content)
            print(f"  📋 Copied to skill://{skill_name}")

# ── Phase 4: Refine ──────────────────────────────────────────────────────────

_SUMMARY_RE = re.compile(
    r'(?:^Done\b|Summary of changes|bullets? removed|Here.s what|I removed)',
    re.IGNORECASE | re.MULTILINE
)


def _validate_file_response(raw: str | None, heading: str, min_bullets: int = 1) -> str | None:
    """Validate an LLM response that should be a markdown file. Returns cleaned content or None."""
    if raw is None:
        return None
    content = parse_response(raw, heading)
    if not content or len(content) < 30:
        return None
    if _SUMMARY_RE.search(content):
        return None
    first_line = content.split("\n", 1)[0].strip()
    if not first_line.startswith("# "):
        return None
    # Trim if heading appears twice (LLM repeated the file)
    lines = content.split("\n")
    h_indices = [i for i, l in enumerate(lines) if l.startswith("# ")]
    if len(h_indices) > 1:
        content = "\n".join(lines[:h_indices[1]]).strip()
    # Trim trailing commentary (lines after last bullet/header/marker)
    last_content_idx = 0
    for i, line in enumerate(content.split("\n")):
        s = line.strip()
        if s.startswith("- ") or s.startswith("## ") or s.startswith("# ") or s.startswith("<!-- MOVED_TO_SHARED:"):
            last_content_idx = i
    content = "\n".join(content.split("\n")[:last_content_idx + 1]).strip()
    bullets = sum(1 for l in content.splitlines()
                  if l.strip().startswith("- ") or l.strip().startswith("<!-- MOVED_TO_SHARED:"))
    if bullets < min_bullets:
        return None
    return content


CONTENT_LOSS_THRESHOLD = 0.60


def phase_refine(repo_root: Path, work_dir: Path, agent: str, model: str):
    """Refine: extract shared patterns, clean per-type files, verify.

    Step 0: Global shared extraction (all files at once)
    Step 1: Chunk all per-type files into ~15 bullet groups
    Step 2: Pairwise chunk comparisons → validate/enrich shared
    Step 3: Build shared file from Step 0 + Step 2 candidates
    Step 4: Clean per-type files against shared (per-file content loss check)
    Step 5: Verify + fix
    Step 6: Final verify-only
    Step 7: Cleanup migration markers
    """
    guidelines_dir = repo_root / "docs" / "guidelines"
    tests_dir = guidelines_dir / "tests"
    shared_dir = guidelines_dir / "shared"
    refine_dir = work_dir / "refine"
    ensure_dir(refine_dir)
    ensure_dir(shared_dir)

    if not tests_dir.exists():
        print("❌ No docs/guidelines/tests/ — run split phase first")
        return

    # Load per-type files
    per_type: dict[str, str] = {}
    for f in sorted(tests_dir.glob("*.md")):
        per_type[f.stem] = f.read_text()

    per_type_names = sorted(per_type.keys())

    if len(per_type) <= 1:
        print(f"  ⏭️  Only {len(per_type)} test category — skipping cross-file refine")
        return

    # Backup before any changes
    backup_dir = refine_dir / "backup"
    ensure_dir(backup_dir)
    for name, content in per_type.items():
        (backup_dir / f"{name}.md").write_text(content)

    # ── Step 0: Global shared extraction ────────────────────────────────────

    print(f"\n  🌐 Step 0: global shared extraction (all files at once) [{model}]")

    all_files_block = ""
    for name in per_type_names:
        all_files_block += f"## {name}\n{per_type[name]}\n\n"

    global_msg = (
        f"You have testing guidelines for {len(per_type)} different file types in a Nuxt project.\n"
        f"Read ALL of them and extract patterns that are SHARED across multiple file types.\n\n"
        f"{all_files_block}"
        f"Rules:\n"
        f"- A pattern is shared if it appears (same advice, same context) in 3+ file types\n"
        f"- When file types CONTRADICT each other on the same topic, pick the majority convention "
        f"and note which file type is the outlier\n"
        f"- Merge near-duplicates into the best wording\n"
        f"- Group by topic with ## section headers\n"
        f"- Bullet format: - <rule>\n"
        f"- Start with '# Shared Testing Patterns'\n"
        f"- Return ONLY the complete markdown file, no commentary"
    )
    global_raw = kiro(global_msg, agent, model, repo_root)
    global_shared = _validate_file_response(global_raw, "# Shared", min_bullets=3)

    if global_shared is None:
        print("    ⚠️  Global extraction failed, retrying...")
        global_raw = kiro(global_msg, agent, model, repo_root)
        global_shared = _validate_file_response(global_raw, "# Shared", min_bullets=3)

    if global_shared:
        global_n = sum(1 for l in global_shared.splitlines() if l.strip().startswith("- "))
        print(f"    ✅ Global shared: {global_n} bullets")
        (refine_dir / "global_shared.md").write_text(global_shared + "\n")
    else:
        print("    ⚠️  Global extraction failed — falling back to pairwise only")
        global_shared = None

    if STOP:
        return

    # ── Step 1: Chunk all files ─────────────────────────────────────────────

    CHUNK_SIZE = 15
    chunks_by_cat: dict[str, list[str]] = {}
    for name, content in per_type.items():
        chunks = _chunk_bullets(content, CHUNK_SIZE)
        chunks_by_cat[name] = chunks if chunks else [content]

    total_chunks = sum(len(c) for c in chunks_by_cat.values())
    print(f"\n  📦 Chunked {len(per_type)} files into {total_chunks} chunks (size={CHUNK_SIZE})")

    # ── Step 2: Pairwise chunk comparisons ──────────────────────────────────

    # Build all cross-category chunk pairs
    chunk_pairs: list[tuple[str, int, str, str, int, str]] = []
    for a, b in combinations(per_type_names, 2):
        for ci, chunk_a in enumerate(chunks_by_cat[a]):
            for cj, chunk_b in enumerate(chunks_by_cat[b]):
                chunk_pairs.append((a, ci, chunk_a, b, cj, chunk_b))

    print(f"  🔍 Step 2: {len(chunk_pairs)} pairwise chunk comparisons [{model}]")

    def compare_chunks(a_name: str, a_idx: int, a_text: str,
                       b_name: str, b_idx: int, b_text: str) -> str | None:
        msg = (
            f"Compare these two sets of testing guidelines from different file types.\n"
            f"Find bullets expressing the EXACT SAME advice for the EXACT SAME context.\n\n"
            f"## {a_name} (chunk {a_idx + 1})\n{a_text}\n\n"
            f"## {b_name} (chunk {b_idx + 1})\n{b_text}\n\n"
            f"CRITICAL: using the same tool is NOT enough. Both the technique AND the "
            f"context/application must match.\n"
            f"'vi.fn() for mock HTTP clients' ≠ 'vi.fn() for store spies'\n\n"
            f"Format (one per line):\n"
            f"COMMON | <canonical bullet — best wording>\n"
            f"RESOLVED | <correct bullet> | was: <wrong version>\n\n"
            f"If no matches: NONE\n"
            f"No commentary."
        )
        return kiro(msg, agent, model, repo_root)

    all_commons: list[str] = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(compare_chunks, a, ci, ca, b, cj, cb): (a, ci, b, cj)
            for a, ci, ca, b, cj, cb in chunk_pairs
        }
        done_count = 0
        for future in as_completed(futures):
            if STOP:
                executor.shutdown(wait=False, cancel_futures=True)
                break
            a, ci, b, cj = futures[future]
            done_count += 1
            result = future.result()
            if result is None:
                continue
            cleaned = parse_response(result)

            if cleaned.strip() == "NONE" or len(cleaned.strip()) < 5:
                continue

            n_found = 0
            for line in cleaned.split("\n"):
                line = line.strip()
                if line.startswith("COMMON |") or line.startswith("RESOLVED |"):
                    bullet = line.split("|")[1].strip()
                    if not bullet.startswith("- "):
                        bullet = f"- {bullet}"
                    all_commons.append(bullet)
                    n_found += 1
            if n_found:
                print(f"    [{done_count}/{len(chunk_pairs)}] {a}[{ci}] vs {b}[{cj}] — {n_found} commons")

    if STOP:
        return

    # Exact dedup
    unique_commons = list(dict.fromkeys(all_commons))
    print(f"\n  🧹 {len(all_commons)} raw → {len(unique_commons)} after exact dedup")

    if not unique_commons:
        print("\n  ✅ No cross-file commons found — skipping shared extraction")
        _quality_gate(repo_root, work_dir)
        return

    (refine_dir / "raw_commons.md").write_text("\n".join(unique_commons) + "\n")

    # ── Step 3: Build shared file (start from global if available) ─────────

    MERGE_CHUNK = 20
    chunks = [unique_commons[i:i + MERGE_CHUNK] for i in range(0, len(unique_commons), MERGE_CHUNK)]
    print(f"\n  📋 Step 3: building shared from {len(unique_commons)} candidates in {len(chunks)} chunks [{model}]")

    current_shared = global_shared if global_shared else "# Shared Testing Patterns\n"
    if global_shared:
        print(f"    📌 Starting from global shared ({sum(1 for l in global_shared.splitlines() if l.strip().startswith('- '))} bullets)")
    

    for ci, chunk in enumerate(chunks):
        if STOP:
            break
        chunk_text = "\n".join(chunk)
        msg = (
            f"Merge these new bullets into the shared testing patterns file.\n\n"
            f"## Current shared file\n{current_shared}\n\n"
            f"## New bullets to integrate\n{chunk_text}\n\n"
            f"Rules:\n"
            f"- Duplicate of existing (same concept) → keep the better version\n"
            f"- Genuinely new → add to appropriate ## section\n"
            f"- Group by topic with ## section headers\n"
            f"- Bullet format: - <rule>\n"
            f"- Start with '# Shared Testing Patterns'\n"
            f"- Return ONLY the complete markdown file, no commentary"
        )
        merge_raw = kiro(msg, agent, model, repo_root)
        merged = _validate_file_response(merge_raw, "# Shared", min_bullets=3)

        if merged is None:
            merge_raw = kiro(msg, agent, model, repo_root)
            merged = _validate_file_response(merge_raw, "# Shared", min_bullets=3)

        if merged is None:
            print(f"    ⚠️  chunk {ci + 1}/{len(chunks)} — skipped")
            continue

        current_shared = merged
        n = sum(1 for l in merged.splitlines() if l.strip().startswith("- "))
        print(f"    ✅ chunk {ci + 1}/{len(chunks)} — shared now {n} bullets")

    shared_path = shared_dir / "testing.md"
    shared_path.write_text(current_shared + "\n")
    shared_n = sum(1 for l in current_shared.splitlines() if l.strip().startswith("- "))
    print(f"  ✅ shared/testing.md — {shared_n} bullets")
    (refine_dir / "shared_final.md").write_text(current_shared + "\n")

    if STOP:
        return

    # ── Step 4: Clean per-type files against shared ─────────────────────────

    print(f"\n  🔧 Step 4: cleaning {len(per_type_names)} files against shared [{model}]")

    def clean_file(name: str, content: str) -> str | None:
        msg = (
            f"Remove from this guidelines file ONLY bullets that are truly redundant "
            f"with the shared patterns file.\n\n"
            f"## Shared patterns (reference — do NOT modify)\n{current_shared}\n\n"
            f"## File to clean: {name}\n{content}\n\n"
            f"A bullet is redundant ONLY when shared contains a bullet giving "
            f"the SAME specific advice for the SAME situation. Both tool/technique AND "
            f"context must match.\n\n"
            f"Using the same tool is NOT enough:\n"
            f"- 'Use vi.fn() for factory/injection-based modules' is NOT redundant with "
            f"generic 'Use vi.fn()' — the factory/injection context is {name}-specific.\n\n"
            f"When in doubt, KEEP the bullet.\n\n"
            f"Rules:\n"
            f"- Truly redundant (same advice + same context in shared) → REMOVE\n"
            f"- Generic tool in {name}-specific context → KEEP\n"
            f"- Preserve ## section headers, remove empty sections\n"
            f"- Return the COMPLETE cleaned file\n"
            f"- First line: '# Guidelines — {name}'"
        )
        return kiro(msg, agent, model, repo_root)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(clean_file, n, per_type[n]): n for n in per_type_names}
        for future in as_completed(futures):
            if STOP:
                executor.shutdown(wait=False, cancel_futures=True)
                break
            name = futures[future]
            result = future.result()
            old_n = sum(1 for l in per_type[name].splitlines() if l.strip().startswith("- "))

            refined = _validate_file_response(result, "# ", min_bullets=1)
            if refined is None:
                result = clean_file(name, per_type[name])
                refined = _validate_file_response(result, "# ", min_bullets=1)
            if refined is None:
                print(f"    ⚠️  {name} — skipped after retry")
                continue

            new_n = sum(1 for l in refined.splitlines() if l.strip().startswith("- "))
            # Per-file content loss check
            if old_n > 0 and (1 - new_n / old_n) > CONTENT_LOSS_THRESHOLD:
                print(f"    ⚠️  {name}: {old_n} → {new_n} ({(1 - new_n / old_n) * 100:.0f}% loss) — keeping original")
                continue

            (tests_dir / f"{name}.md").write_text(refined + "\n")
            per_type[name] = refined
            print(f"    ✅ {name}: {old_n} → {new_n} bullets")

    if STOP:
        return

    # ── Step 5: Verify + Fix (max 2 iterations) ────────────────────────────
    prev_issue_keys: set[str] = set()

    for iteration in range(1, 3):
        if STOP:
            break
        print(f"\n  {'=' * 50}")
        print(f"  Verify+Fix iteration {iteration}/2")
        print(f"  {'=' * 50}")

        issues_a = _phase_verify(repo_root, work_dir, agent, model, iteration, suffix="a")
        if STOP:
            break
        issues_b = _phase_verify(repo_root, work_dir, agent, model, iteration, suffix="b")
        if STOP:
            break

        keys_a = {(i["file"], i["bullet"][:80]) for i in issues_a}
        keys_b = {(i["file"], i["bullet"][:80]) for i in issues_b}
        # Union: if either run flags it, act on it (prevents false negatives from model self-doubt)
        all_keys = keys_a | keys_b
        # Deduplicate: prefer issues_a version, add issues_b-only
        seen = set()
        issues = []
        for i in issues_a + issues_b:
            key = (i["file"], i["bullet"][:80])
            if key in all_keys and key not in seen:
                issues.append(i)
                seen.add(key)

        only_a = len(keys_a - keys_b)
        only_b = len(keys_b - keys_a)
        both = len(keys_a & keys_b)
        if only_a or only_b:
            print(f"  🎯 Union: {both} agreed + {only_a} only-A + {only_b} only-B → {len(issues)} total")

        if not issues:
            print(f"\n  ✅ PASS on iteration {iteration}")
            break

        current_keys = {(i["file"], i["bullet"][:80]) for i in issues}
        stuck = current_keys & prev_issue_keys
        if stuck:
            stuck_issues = [i for i in issues if (i["file"], i["bullet"][:80]) in stuck]
            fresh_issues = [i for i in issues if (i["file"], i["bullet"][:80]) not in stuck]
            print(f"    🔧 {len(stuck_issues)} stuck → mechanical removal")
            _mechanical_remove(repo_root, stuck_issues)
            if fresh_issues:
                _phase_fix(repo_root, work_dir, agent, model, fresh_issues, iteration)
        else:
            _phase_fix(repo_root, work_dir, agent, model, issues, iteration)

        prev_issue_keys = current_keys
    else:
        print(f"\n  ⚠️  2 iterations completed — check quality-report.md")

    if not STOP:
        # ── Step 6: Final verify-only (no fix, just report) ────────────────
        print(f"\n  {'=' * 50}")
        print(f"  Step 6: Final verify (report only)")
        print(f"  {'=' * 50}")
        final_issues = _phase_verify(repo_root, work_dir, agent, model, iteration=99, suffix="final")
        if final_issues:
            print(f"\n  ⚠️  {len(final_issues)} issues remain after all iterations")
        else:
            print(f"\n  ✅ Final verify: CLEAN")

    if not STOP:
        # ── Step 7: Cleanup migration markers ──────────────────────────────
        print(f"\n  🧹 Step 7: cleaning up migration markers")
        _cleanup_migration_markers(repo_root)

    _quality_gate(repo_root, work_dir)


def _mechanical_remove(repo_root: Path, issues: list[dict]):
    """Remove stuck bullets by exact text match — no LLM needed."""
    tests_dir = repo_root / "docs" / "guidelines" / "tests"
    by_file: dict[str, list[str]] = {}
    for i in issues:
        by_file.setdefault(i["file"], []).append(i["bullet"])

    for name, bullets in by_file.items():
        fpath = tests_dir / f"{name}.md"
        if not fpath.exists():
            continue
        lines = fpath.read_text().splitlines()
        removed = 0
        kept: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- ") and any(b in stripped for b in bullets):
                removed += 1
            else:
                kept.append(line)
        # Remove empty sections
        final: list[str] = []
        for idx, line in enumerate(kept):
            if line.strip().startswith("## "):
                next_content = next((l for l in kept[idx+1:] if l.strip()), None)
                if not next_content or next_content.strip().startswith("## ") or next_content.strip().startswith("# "):
                    continue
            final.append(line)
        fpath.write_text("\n".join(final) + "\n")
        if removed:
            print(f"      ✂️  {name}: removed {removed} stuck bullets mechanically")


def _cleanup_migration_markers(repo_root: Path):
    """Remove <!-- MOVED_TO_SHARED: ... --> markers and empty sections left behind."""
    tests_dir = repo_root / "docs" / "guidelines" / "tests"
    if not tests_dir.exists():
        return
    marker_re = re.compile(r'^\s*<!--\s*MOVED_TO_SHARED:.*?-->\s*$')
    for fpath in sorted(tests_dir.glob("*.md")):
        lines = fpath.read_text().splitlines()
        cleaned = [l for l in lines if not marker_re.match(l)]
        if len(cleaned) == len(lines):
            continue
        removed = len(lines) - len(cleaned)
        # Remove empty sections
        final: list[str] = []
        for idx, line in enumerate(cleaned):
            if line.strip().startswith("## "):
                rest = [l for l in cleaned[idx+1:] if l.strip()]
                next_content = rest[0] if rest else None
                if not next_content or next_content.strip().startswith("## ") or next_content.strip().startswith("# "):
                    continue
            final.append(line)
        fpath.write_text("\n".join(final) + "\n")
        print(f"    ✂️  {fpath.stem}: removed {removed} migration markers")


def _quality_gate(repo_root: Path, work_dir: Path):
    """Final quality check after all phases complete."""
    guidelines_dir = repo_root / "docs" / "guidelines"
    tests_dir = guidelines_dir / "tests"
    shared_path = guidelines_dir / "shared" / "testing.md"
    backup_dir = work_dir / "refine" / "backup"

    print(f"\n  {'='*50}")
    print(f"  Quality Gate")
    print(f"  {'='*50}")

    issues: list[str] = []

    # Check shared bounds
    test_files = sorted(tests_dir.glob("*.md"))
    if len(test_files) > 1:
        if shared_path.exists():
            shared_n = sum(1 for l in shared_path.read_text().splitlines() if l.strip().startswith("- "))
            if shared_n < 15:
                issues.append(f"shared too small: {shared_n} bullets (expected ≥15)")
            elif shared_n > 120:
                issues.append(f"shared too large: {shared_n} bullets (expected ≤120)")
        else:
            issues.append("shared/testing.md missing")
    else:
        shared_n = 0
        if shared_path.exists():
            shared_n = sum(1 for l in shared_path.read_text().splitlines() if l.strip().startswith("- "))

    # Check no file is empty + total content
    orig_total = 0
    new_total = 0
    for f in sorted(tests_dir.glob("*.md")):
        n = sum(1 for l in f.read_text().splitlines() if l.strip().startswith("- "))
        new_total += n
        if n == 0:
            issues.append(f"{f.stem} is empty")
    if shared_path.exists():
        new_total += shared_n

    if backup_dir.exists():
        for f in sorted(backup_dir.glob("*.md")):
            orig_total += sum(1 for l in f.read_text().splitlines() if l.strip().startswith("- "))

    if orig_total > 0 and new_total < orig_total * 0.50:
        issues.append(f"total content too low: {new_total} vs {orig_total} original ({new_total/orig_total*100:.0f}%)")

    if issues:
        print(f"\n  ❌ QUALITY GATE FAILED:")
        for i in issues:
            print(f"    - {i}")
        print(f"\n  Output may need human review.")
    else:
        print(f"\n  ✅ QUALITY GATE PASSED")
        print(f"    Total: {new_total} bullets (from {orig_total} original, {new_total/orig_total*100:.0f}% retained)")


def _phase_verify(repo_root: Path, work_dir: Path, agent: str, model: str,
                  iteration: int = 1, suffix: str = "") -> list[dict]:
    """Verify quality: check for remaining duplicates, contradictions, misplaced content.
    Returns list of issue dicts: {file, type, bullet, detail}. Empty = PASS."""
    guidelines_dir = repo_root / "docs" / "guidelines"
    tests_dir = guidelines_dir / "tests"
    shared_dir = guidelines_dir / "shared"
    refine_dir = work_dir / "refine"

    shared_path = shared_dir / "testing.md"
    if not shared_path.exists():
        return []
    shared_content = shared_path.read_text()

    cleaned: dict[str, str] = {}
    for f in sorted(tests_dir.glob("*.md")):
        cleaned[f.stem] = f.read_text()

    # Load backup for content loss detection
    backup_dir = refine_dir / "backup"
    originals: dict[str, int] = {}
    if backup_dir.exists():
        for f in sorted(backup_dir.glob("*.md")):
            if f.stem != "shared":
                originals[f.stem] = sum(1 for l in f.read_text().splitlines() if l.strip().startswith("- "))

    print(f"\n  🔍 Verify (iteration {iteration}) [{model}]")

    all_issues: list[dict] = []

    def verify_file(name: str, content: str) -> str | None:
        msg = (
            f"You are a quality auditor for testing guidelines.\n\n"
            f"## Shared patterns (reference)\n{shared_content}\n\n"
            f"## File: {name}\n{content}\n\n"
            f"Check for these problems ONLY:\n"
            f"1. REMAINING_DUPLICATE — a bullet in {name} whose SPECIFIC advice (same context, "
            f"same when-to-apply) is already covered by a bullet in shared. Using the same "
            f"tool (vi.fn, vi.spyOn, etc.) is NOT enough — the full guideline including its "
            f"context must be redundant.\n"
            f"2. CONTRADICTION — a bullet in {name} that gives OPPOSITE advice to a shared bullet "
            f"on the same topic.\n\n"
            f"DO NOT flag bullets as misplaced or generic. A bullet that uses a generic tool "
            f"(vi.fn, vi.mock, etc.) in a {name}-specific context BELONGS in {name}.\n\n"
            f"When in doubt, do NOT flag it.\n\n"
            f"STRICT OUTPUT FORMAT — output ONLY structured lines, one per issue. "
            f"Do NOT write reasoning, reconsiderations, or commentary. "
            f"Do NOT change your mind mid-response. "
            f"If no problems found, output EXACTLY: CLEAN\n\n"
            f"Format (one per line):\n"
            f"REMAINING_DUPLICATE | <full bullet text> | shared bullet: <the shared bullet it duplicates>\n"
            f"CONTRADICTION | <full bullet text> | conflicts with: <shared bullet text>\n\n"
            f"If no problems: CLEAN"
        )
        return kiro(msg, agent, model, repo_root)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(verify_file, n, c): n for n, c in cleaned.items()}
        for future in as_completed(futures):
            if STOP:
                break
            name = futures[future]
            result = future.result()
            if result is None:
                print(f"    ⚠️  {name} — verify failed")
                continue
            response = parse_response(result)
            tag = f"{iteration}{suffix}"
            (refine_dir / f"verify_{tag}_{name}.md").write_text(response)

            # Parse issues — if response has both issues and CLEAN, take the issues
            # (model detected something then talked itself out of it)
            file_issues = []
            for line in response.splitlines():
                line = line.strip()
                for issue_type in ("REMAINING_DUPLICATE", "CONTRADICTION"):
                    if line.startswith(issue_type):
                        parts = [p.strip() for p in line.split("|")]
                        file_issues.append({
                            "file": name,
                            "type": parts[0],
                            "bullet": parts[1] if len(parts) > 1 else "",
                            "detail": parts[2] if len(parts) > 2 else "",
                        })

            if file_issues:
                all_issues.extend(file_issues)
                print(f"    ⚠️  {name} — {len(file_issues)} issues")
            else:
                print(f"    ✅ {name} — clean")

    # Content loss check
    loss_warnings: list[str] = []
    for name, orig_count in originals.items():
        if name in cleaned:
            new_count = sum(1 for l in cleaned[name].splitlines() if l.strip().startswith("- "))
            pct = (1 - new_count / orig_count) * 100 if orig_count > 0 else 0
            if pct > 70:
                loss_warnings.append(f"{name}: {orig_count} → {new_count} ({pct:.0f}% loss)")

    # Write quality report
    report_lines = [f"# Refine Quality Report — Iteration {iteration}\n"]
    shared_bullets = sum(1 for l in shared_content.splitlines() if l.strip().startswith("- "))
    total_specific = sum(sum(1 for l in c.splitlines() if l.strip().startswith("- ")) for c in cleaned.values())
    report_lines.append(f"Total: {total_specific} specific + {shared_bullets} shared = {total_specific + shared_bullets}\n")

    if not all_issues and not loss_warnings:
        report_lines.append("## Result: PASS ✅\n")
    else:
        report_lines.append("## Result: ISSUES FOUND ⚠️\n")
        if all_issues:
            report_lines.append(f"### Issues ({len(all_issues)})\n")
            for i in all_issues:
                report_lines.append(f"- [{i['file']}] {i['type']} | {i['bullet']}" +
                                    (f" | {i['detail']}" if i['detail'] else ""))
        if loss_warnings:
            report_lines.append(f"\n### Content loss warnings\n")
            for w in loss_warnings:
                report_lines.append(f"- {w}")

    report_lines.append(f"\n### Per-file summary\n")
    for name in sorted(cleaned.keys()):
        new_n = sum(1 for l in cleaned[name].splitlines() if l.strip().startswith("- "))
        orig_n = originals.get(name, "?")
        report_lines.append(f"- {name}: {orig_n} → {new_n}")
    report_lines.append(f"- shared: {shared_bullets}")

    report = "\n".join(report_lines) + "\n"
    (refine_dir / f"quality-report-{iteration}.md").write_text(report)

    if all_issues:
        print(f"  ⚠️  {len(all_issues)} issues → passing to fix step")
    else:
        print(f"  ✅ PASS")

    return all_issues


def _phase_fix(repo_root: Path, work_dir: Path, agent: str, model: str,
               issues: list[dict], iteration: int):
    """Fix issues found by verify: remove remaining duplicates, move misplaced to shared."""
    guidelines_dir = repo_root / "docs" / "guidelines"
    tests_dir = guidelines_dir / "tests"
    shared_dir = guidelines_dir / "shared"
    shared_path = shared_dir / "testing.md"
    refine_dir = work_dir / "refine"

    shared_content = shared_path.read_text() if shared_path.exists() else ""

    # Group issues by file
    by_file: dict[str, list[dict]] = {}
    for issue in issues:
        by_file.setdefault(issue["file"], []).append(issue)

    # Collect MISPLACED bullets to add to shared (only contradictions that need correction)
    misplaced_bullets = [i["bullet"] for i in issues if i["type"] == "MISPLACED" and i["bullet"]]

    print(f"\n  🔧 Fix (iteration {iteration}): {len(issues)} issues across {len(by_file)} files [{model}]")

    # Fix per-type files (parallel)
    def fix_file(name: str, file_issues: list[dict]) -> str | None:
        content = (tests_dir / f"{name}.md").read_text()
        issues_text = "\n".join(
            f"- {i['type']}: {i['bullet']}" for i in file_issues
        )
        msg = (
            f"Fix these issues in the '{name}' guidelines file.\n\n"
            f"## Issues to fix\n{issues_text}\n\n"
            f"## Current file\n{content}\n\n"
            f"Rules:\n"
            f"- REMAINING_DUPLICATE: replace the bullet with a migration marker:\n"
            f"  `<!-- MOVED_TO_SHARED: original bullet text -->`\n"
            f"- CONTRADICTION: replace the bullet with a migration marker:\n"
            f"  `<!-- MOVED_TO_SHARED: original bullet text -->`\n"
            f"  Shared is the source of truth. If the category bullet has useful "
            f"context absent from shared, rewrite it as a COMPLEMENT (not contradiction) "
            f"and keep it as a normal bullet alongside the marker.\n"
            f"- Keep everything else EXACTLY as is\n"
            f"- Keep ## section headers even if only markers remain\n"
            f"- Return the COMPLETE file. First line: '# Guidelines — {name}'"
        )
        return kiro(msg, agent, model, repo_root)

    # Load backup for content loss check
    backup_dir = refine_dir / "backup"
    originals: dict[str, int] = {}
    if backup_dir.exists():
        for f in sorted(backup_dir.glob("*.md")):
            if f.stem != "shared":
                originals[f.stem] = sum(1 for l in f.read_text().splitlines() if l.strip().startswith("- "))

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fix_file, n, fi): n for n, fi in by_file.items()}
        for future in as_completed(futures):
            if STOP:
                break
            name = futures[future]
            result = future.result()

            fixed = _validate_file_response(result, "# ", min_bullets=1)
            if fixed is None:
                print(f"    🔄 {name} — invalid response, retrying...")
                result = fix_file(name, by_file[name])
                fixed = _validate_file_response(result, "# ", min_bullets=1)
            if fixed is None:
                print(f"    ⚠️  {name} — skipped after retry")
                continue

            old_n = sum(1 for l in (tests_dir / f"{name}.md").read_text().splitlines() if l.strip().startswith("- "))
            new_n = sum(1 for l in fixed.splitlines() if l.strip().startswith("- "))
            orig_n = originals.get(name, old_n)
            if orig_n > 0 and (1 - new_n / orig_n) > CONTENT_LOSS_THRESHOLD:
                print(f"    ⚠️  {name}: {orig_n} → {new_n} ({(1-new_n/orig_n)*100:.0f}% loss vs original) — keeping current")
                continue

            (tests_dir / f"{name}.md").write_text(fixed + "\n")
            print(f"    ✅ {name}: {old_n} → {new_n} bullets (fixed {len(by_file[name])} issues)")

    # Add MISPLACED bullets to shared
    if misplaced_bullets and not STOP:
        print(f"\n  📋 Adding {len(misplaced_bullets)} misplaced bullets to shared [{model}]")
        bullets_text = "\n".join(b if b.startswith("- ") else f"- {b}" for b in misplaced_bullets)
        merge_msg = (
            f"Add these bullets to the shared testing patterns file, "
            f"placing each in the correct section. Deduplicate against existing bullets.\n\n"
            f"## Bullets to add\n{bullets_text}\n\n"
            f"## Current shared file\n{shared_content}\n\n"
            f"Return the COMPLETE updated file. First line: '# Shared Testing Patterns'\n"
            f"No commentary."
        )
        merge_raw = kiro(merge_msg, agent, model, repo_root)
        if merge_raw:
            merged = parse_response(merge_raw, "# Shared")
            if merged and len(merged) > 50 and merged.split("\n", 1)[0].strip().startswith("# "):
                old_n = sum(1 for l in shared_content.splitlines() if l.strip().startswith("- "))
                new_n = sum(1 for l in merged.splitlines() if l.strip().startswith("- "))
                shared_path.write_text(merged + "\n")
                (refine_dir / f"shared_fix_{iteration}.md").write_text(merged + "\n")
                print(f"    ✅ shared: {old_n} → {new_n} bullets")
            else:
                print(f"    ⚠️  shared merge response invalid, skipped")
        else:
            print(f"    ❌ shared merge failed")

# ── Report ───────────────────────────────────────────────────────────────────

def report(files: list[FileInfo], work_dir: Path):
    """Show progress summary."""
    progress = load_progress(work_dir)
    cats = get_categories_with_files(files)

    total = sum(len(fs) for _, fs in cats)
    extracted = len(progress["extract"]["done"])
    reviewed = len(progress["review"]["done"])
    split_done = len(progress["split"]["done"])

    print(f"\n📊 Guidelines Generator Report")
    print(f"{'='*50}")
    print(f"  Files:    {total} classified")
    print(f"  Extract:  {extracted} done, {len(progress['extract']['failed'])} failed")
    print(f"  Review:   {reviewed}/{len(cats)} categories")
    print(f"  Split:    {split_done}/{len(cats)} categories")
    print(f"\n  Categories:")
    for cat, cat_files in cats:
        done = sum(1 for f in cat_files if f.path in progress["extract"]["done"])
        rev = "✅" if cat in progress["review"]["done"] else "⬜"
        spl = "✅" if cat in progress["split"]["done"] else "⬜"
        print(f"    {cat:30s}  {done:3d}/{len(cat_files):3d} extracted  review:{rev}  split:{spl}")

# ── Scan display ─────────────────────────────────────────────────────────────

def display_scan(files: list[FileInfo], framework: str):
    """Print classification table."""
    cats = get_categories_with_files(files)
    skipped = [f for f in files if f.skip_reason]

    print(f"\n🔍 Scan Results — {framework}")
    print(f"{'='*60}")
    print(f"  {'Category':<30s} {'Files':>6s} {'LOC':>8s}")
    print(f"  {'-'*30} {'-'*6} {'-'*8}")
    total_files, total_loc = 0, 0
    for cat, cat_files in cats:
        loc = sum(f.loc for f in cat_files)
        print(f"  {cat:<30s} {len(cat_files):>6d} {loc:>8d}")
        total_files += len(cat_files)
        total_loc += loc
    print(f"  {'-'*30} {'-'*6} {'-'*8}")
    print(f"  {'TOTAL':<30s} {total_files:>6d} {total_loc:>8d}")
    if skipped:
        print(f"  Skipped: {len(skipped)} files ({', '.join(set(f.skip_reason for f in skipped))})")

# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Extract guidelines from committed files")
    parser.add_argument("--scan", action="store_true", help="Classify files, show table")
    parser.add_argument("--phase", choices=["extract", "review", "split", "refine", "all"], help="Run phase(s)")
    parser.add_argument("--only", help="Filter categories (comma-separated)")
    parser.add_argument("--dir", help="Filter directory")
    parser.add_argument("--report", action="store_true", help="Show progress")
    parser.add_argument("--reset-phase", choices=["extract", "review", "split", "refine", "all"], help="Reset phase progress")
    parser.add_argument("--to-skills", action="store_true", help="Copy testing guidelines to skills")
    parser.add_argument("--agent", default=DEFAULT_AGENT, help=f"Agent (default: {DEFAULT_AGENT})")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model (default: {DEFAULT_MODEL})")
    parser.add_argument("--workers", type=int, default=3, help="Parallel workers for extract")
    parser.add_argument("--max-tasks", type=int, help="Limit extraction tasks")
    parser.add_argument("--extensions", help="Regex for file extensions to include (default: frontend). Example: '\\.java$' or '\\.(py|pyi)$'")
    parser.add_argument("--categories", help="JSON string or path to JSON file with extra categories. Example: '{\"controller\": \"controllers\"}' or './my-categories.json'")
    parser.add_argument("--output-dir", help="Output directory for guidelines (default: docs/guidelines)")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompts")
    parser.add_argument("--no-agent-categories", action="store_true", help="Skip agent categorization, use defaults")
    parser.add_argument("--recategorize", action="store_true", help="Force re-run agent categorization")
    args = parser.parse_args()

    repo_root = Path.cwd()
    work_dir = repo_root / ".guidelines"
    ensure_dir(work_dir)

    # Check we're in a git repo
    if not (repo_root / ".git").exists():
        print("❌ Not a git repository")
        sys.exit(1)

    # Parse --categories (JSON string or file path)
    extra_categories = None
    if args.categories:
        cat_input = args.categories.strip()
        if cat_input.startswith("{"):
            try:
                extra_categories = json.loads(cat_input)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in --categories: {e}")
                sys.exit(1)
        else:
            cat_path = Path(cat_input)
            if cat_path.exists():
                try:
                    extra_categories = json.loads(cat_path.read_text())
                    if "categories" in extra_categories:
                        extra_categories = extra_categories["categories"]
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"❌ Invalid JSON file {cat_input}: {e}")
                    sys.exit(1)
            else:
                print(f"❌ --categories file not found: {cat_input}")
                sys.exit(1)

    # Detect existing guidelines — ask before overwriting
    guidelines_dir = repo_root / "docs" / "guidelines"
    if args.output_dir:
        guidelines_dir = repo_root / args.output_dir
    has_existing = guidelines_dir.exists() and any(guidelines_dir.iterdir()) if guidelines_dir.exists() else False

    if has_existing and args.phase and not args.yes:
        print(f"\n⚠️  Existing guidelines found in {guidelines_dir.relative_to(repo_root)}/")
        print(f"   Files: {sum(1 for _ in guidelines_dir.rglob('*.md'))}")
        print()
        print("   [d] Delete and start fresh")
        print("   [k] Keep and continue (resume/overwrite)")
        print("   [o] Output to a different directory")
        print("   [q] Quit")
        print()
        choice = input("   Choice [d/k/o/q]: ").strip().lower()
        if choice == "d":
            import shutil
            shutil.rmtree(guidelines_dir)
            shutil.rmtree(work_dir, ignore_errors=True)
            ensure_dir(work_dir)
            print(f"   🗑️  Deleted {guidelines_dir.relative_to(repo_root)}/ and .guidelines/")
        elif choice == "o":
            new_dir = input("   New output directory: ").strip()
            if not new_dir:
                print("   ❌ No directory provided")
                sys.exit(1)
            guidelines_dir = repo_root / new_dir
            work_dir = repo_root / ".guidelines" / new_dir.replace("/", "_")
            ensure_dir(work_dir)
            print(f"   📁 Output → {guidelines_dir.relative_to(repo_root)}/")
        elif choice == "q":
            sys.exit(0)
        # 'k' = keep going, no action needed

    framework = detect_framework(repo_root)
    only = [x.strip() for x in args.only.split(",")] if args.only else None

    # Reset
    if args.reset_phase:
        progress = load_progress(work_dir)
        if args.reset_phase == "all":
            for phase in ("extract", "review", "split"):
                progress[phase] = {"done": [], "failed": []}
            # Also clean autobuild progress (stored at repo root)
            import shutil
            shutil.rmtree(repo_root / ".auto-build", ignore_errors=True)
            shutil.rmtree(work_dir / "raw", ignore_errors=True)
            shutil.rmtree(work_dir / "reviewed", ignore_errors=True)
            shutil.rmtree(work_dir / "tasks", ignore_errors=True)
            cat_file = work_dir / "categories.json"
            if cat_file.exists():
                cat_file.unlink()
                print("  🗑️  Removed agent categories (will re-categorize on next run)")
        elif args.reset_phase == "extract":
            progress["extract"] = {"done": [], "failed": []}
            import shutil
            shutil.rmtree(repo_root / ".auto-build", ignore_errors=True)
            shutil.rmtree(work_dir / "raw", ignore_errors=True)
            shutil.rmtree(work_dir / "tasks", ignore_errors=True)
        elif args.reset_phase == "refine":
            import shutil
            shutil.rmtree(work_dir / "refine", ignore_errors=True)
            # Restore from backup if exists
            backup = work_dir / "refine" / "backup"
            # No progress to reset — refine doesn't use progress tracking
        else:
            progress[args.reset_phase] = {"done": [], "failed": []}
        save_progress(work_dir, progress)
        print(f"🗑️  Reset phase '{args.reset_phase}'")
        sys.exit(0)

    # Agent categorization: run if no categories.json yet (unless --no-agent-categories)
    if not args.no_agent_categories and (args.recategorize or not load_agent_categories(work_dir)):
        if args.scan or args.phase or args.recategorize:
            phase_categorize(repo_root, work_dir, args.agent, args.model, extensions_re=args.extensions)

    # Scan
    files = scan(repo_root, only=only, dir_filter=args.dir, extensions_re=args.extensions, extra_categories=extra_categories)

    if args.scan:
        display_scan(files, framework)
        sys.exit(0)

    if args.report:
        report(files, work_dir)
        sys.exit(0)

    # Run phases
    if not args.phase:
        parser.print_help()
        sys.exit(1)

    phases = ["extract", "review", "split", "refine"] if args.phase == "all" else [args.phase]

    for phase in phases:
        if STOP:
            break
        print(f"\n{'#'*50}")
        print(f"# Phase: {phase}")
        print(f"{'#'*50}")

        if phase == "extract":
            phase_extract(files, repo_root, work_dir, args.agent, args.model, framework, args.workers, args.max_tasks)
        elif phase == "review":
            phase_review(repo_root, work_dir, args.agent, args.model)
        elif phase == "split":
            phase_split(repo_root, work_dir, args.agent, args.model, args.to_skills)
        elif phase == "refine":
            phase_refine(repo_root, work_dir, args.agent, args.model)

    if STOP:
        print(f"\n⏸️  Paused. Resume with same command.")
    else:
        print(f"\n🏁 Done.")

if __name__ == "__main__":
    main()
