#!/usr/bin/env python3
"""autobuild — Task engine that executes markdown task files via kiro-cli agents.

Usage:
    autobuild tasks/                       # run all pending tasks
    autobuild tasks/ --bg                  # run in background
    autobuild tasks/ --status              # progress table
    autobuild tasks/ --dry-run             # show plan without executing
    autobuild tasks/ --retry               # re-run failed tasks
    autobuild tasks/ --from 10             # resume from task 10_*
    autobuild tasks/ --only 02             # run single task
    autobuild tasks/ --reset 01            # reset one task to pending
    autobuild tasks/ --reset-all           # reset everything
    autobuild tasks/ --report              # JSON summary
    autobuild tasks/ --makefile            # generate Makefile
"""

import argparse, ast, fnmatch, json, os, re, shutil, signal, subprocess, sys, threading, time
from dataclasses import dataclass, field
from pathlib import Path

# ── Dependencies ─────────────────────────────────────────────────────────────

sys.path.insert(0, os.path.expanduser("~/.kiro/tools/bg"))
sys.path.insert(0, os.path.expanduser("~/.kiro/tools/logd"))

from bg import setup_bg

_log = None
STOP = False


def _get_log():
    global _log
    if _log is None:
        try:
            from loglib import get_logger
            _log = get_logger("autobuild")
        except Exception:
            _log = False
    return _log if _log else None


def _sigint(sig, frame):
    global STOP
    STOP = True
    print("\n⚠ Stopping after current task...", file=sys.stderr)


# ── Task Model ───────────────────────────────────────────────────────────────

@dataclass
class Task:
    name: str           # e.g. "00_setup-db"
    path: Path          # full path to .md file
    content: str        # full markdown content (without frontmatter)
    prefix: str         # e.g. "00"
    agent: str = ""
    verify: str = ""
    gate: bool = False
    creates: list = field(default_factory=list)
    timeout: int = 600
    deps: list = field(default_factory=list)
    task_type: str = ""
    estimate: str = ""


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse optional YAML-like frontmatter from markdown. Returns (meta, body)."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = {}
    for line in parts[1].strip().splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, val = line.split(":", 1)  # split on FIRST colon only
        key, val = key.strip(), val.strip()
        if val.startswith("["):
            try:
                meta[key] = json.loads(val)
            except json.JSONDecodeError:
                meta[key] = val
        elif val.lower() in ("true", "false"):
            meta[key] = val.lower() == "true"
        elif val.isdigit():
            meta[key] = int(val)
        elif val.startswith('"') and val.endswith('"'):
            meta[key] = val[1:-1]
        else:
            meta[key] = val
    return meta, parts[2].strip()


def load_tasks(folder: Path, config: dict) -> list[Task]:
    """Load and parse task files from folder. Returns ordered list."""
    files = sorted(f for f in folder.glob("*.md") if f.name != "README.md")
    tasks = []
    prev_prefix = None

    for f in files:
        raw = f.read_text()
        meta, body = _parse_frontmatter(raw)
        match = re.match(r"^(\d+)", f.stem)
        prefix = match.group(1) if match else f.stem[:2]

        task = Task(
            name=f.stem,
            path=f,
            content=body,
            prefix=prefix,
            agent=meta.get("agent", ""),
            verify=meta.get("verify", ""),
            gate=meta.get("gate", False),
            creates=meta.get("creates", []),
            timeout=meta.get("timeout", config.get("timeout", 600)),
            deps=meta.get("deps", [prev_prefix] if prev_prefix else []),
            task_type=meta.get("type", ""),
            estimate=meta.get("estimate", ""),
        )
        tasks.append(task)
        prev_prefix = prefix

    # Resolve agents via priority chain
    agent_map = config.get("agent_map", {})
    default_agent = config.get("agent", "tuimm_default")

    for t in tasks:
        if not t.agent:
            t.agent = _resolve_agent(t, agent_map, default_agent)

    return tasks


def _resolve_agent(task: Task, agent_map: dict, default: str) -> str:
    """Resolve agent for task via agent_map rules."""
    for rule in agent_map.get("rules", []):
        match = rule.get("match", {})
        if "type" in match and task.task_type == match["type"]:
            return rule["agent"]
        if "folder" in match and match["folder"] in str(task.path):
            return rule["agent"]
        if "pattern" in match and fnmatch.fnmatch(task.name, match["pattern"]):
            return rule["agent"]
    return agent_map.get("default", default)


def resolve_waves(tasks: list[Task]) -> list[list[Task]]:
    """Group tasks into parallel waves based on dependencies."""
    completed = set()
    remaining = list(tasks)
    waves = []

    while remaining:
        wave = [t for t in remaining if all(d in completed for d in t.deps)]
        if not wave:
            # Distinguish missing deps from circular deps
            all_prefixes = {t.prefix for t in tasks}
            for t in remaining:
                unknown = set(t.deps) - all_prefixes
                if unknown:
                    raise ValueError(f"Task {t.name} depends on unknown prefix(es): {', '.join(unknown)}")
            names = [t.name for t in remaining]
            raise ValueError(f"Circular dependency detected among: {', '.join(names)}")
        waves.append(wave)
        for t in wave:
            completed.add(t.prefix)
        remaining = [t for t in remaining if t.prefix not in completed]

    return waves


# ── Progress Tracking ────────────────────────────────────────────────────────

class Progress:
    """Thread-safe progress tracking with JSON persistence."""

    def __init__(self, build_dir: Path, run_uid: str):
        self._path = build_dir / "progress.json"
        self._tsv_path = build_dir / "results.tsv"
        self._lock = threading.Lock()
        self._data = {
            "run_uid": run_uid,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "finished_at": None,
            "current_task": None,
            "summary": {"total": 0, "passed": 0, "failed": 0, "pending": 0, "running": 0},
            "tasks": {},
        }
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text())
            except json.JSONDecodeError:
                pass

    def init_tasks(self, tasks: list[Task]):
        with self._lock:
            self._data["summary"]["total"] = len(tasks)
            for t in tasks:
                if t.name not in self._data["tasks"]:
                    self._data["tasks"][t.name] = {
                        "status": "pending", "attempts": 0,
                        "started_at": None, "finished_at": None,
                        "current_phase": None, "last_error": None, "todo_count": 0,
                    }
            self._recount()
            self._save()

    def get_task(self, name: str) -> dict:
        with self._lock:
            return self._data["tasks"].get(name, {})

    def set_task(self, name: str, **kwargs):
        with self._lock:
            if name in self._data["tasks"]:
                self._data["tasks"][name].update(kwargs)
            self._data["current_task"] = name
            self._recount()
            self._save()

    def finish(self):
        with self._lock:
            self._data["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            self._data["current_task"] = None
            self._recount()
            self._save()

    def write_tsv(self, name: str, status: str, attempts: int, duration: float, error: str, todos: int):
        with self._lock:
            header = not self._tsv_path.exists()
            with open(self._tsv_path, "a") as f:
                if header:
                    f.write("task\tstatus\tattempts\tduration\terror\ttodos\n")
                err = error.replace("\t", " ").replace("\n", " ")[:200] if error else ""
                f.write(f"{name}\t{status}\t{attempts}\t{duration:.1f}\t{err}\t{todos}\n")

    def _recount(self):
        s = {"total": len(self._data["tasks"]), "passed": 0, "failed": 0, "pending": 0, "running": 0}
        for t in self._data["tasks"].values():
            st = t.get("status", "pending")
            if st in s:
                s[st] += 1
        self._data["summary"] = s

    def _save(self):
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, indent=2))
        os.replace(str(tmp), str(self._path))  # atomic on POSIX

    @property
    def data(self):
        with self._lock:
            return dict(self._data)


# ── Health Checks ────────────────────────────────────────────────────────────

def run_health_checks(config: dict) -> bool:
    """Run builtin + custom health checks. Returns True if all required pass."""
    health = config.get("health", {"builtin": True})
    ok = True

    if health.get("builtin", True):
        # kiro-cli in PATH
        if shutil.which("kiro-cli"):
            print("  ✓ kiro-cli found", file=sys.stderr)
        else:
            print("  ✗ kiro-cli not in PATH", file=sys.stderr)
            ok = False

        # logd running
        try:
            r = subprocess.run(
                [sys.executable, os.path.expanduser("~/.kiro/tools/logd/logd.py"), "status"],
                capture_output=True, text=True, timeout=5,
            )
            if "running" in r.stdout.lower():
                print("  ✓ logd running", file=sys.stderr)
            else:
                print("  ⚠ logd not running (logs will be lost)", file=sys.stderr)
        except Exception:
            print("  ⚠ logd check failed", file=sys.stderr)

        # Disk space
        try:
            st = os.statvfs(".")
            free_gb = (st.f_bavail * st.f_frsize) / (1024**3)
            if free_gb > 1:
                print(f"  ✓ disk space: {free_gb:.1f} GB free", file=sys.stderr)
            else:
                print(f"  ✗ low disk space: {free_gb:.1f} GB", file=sys.stderr)
                ok = False
        except Exception:
            pass

    for check in health.get("checks", []):
        name = check.get("name", "custom")
        cmd = check.get("cmd", "")
        required = check.get("required", False)
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
            if r.returncode == 0:
                print(f"  ✓ {name}", file=sys.stderr)
            else:
                sym = "✗" if required else "⚠"
                print(f"  {sym} {name} failed", file=sys.stderr)
                if required:
                    ok = False
        except Exception:
            print(f"  ⚠ {name} error", file=sys.stderr)
            if required:
                ok = False

    return ok


# ── Review Parsing ────────────────────────────────────────────────────────────

def _parse_review(output: str) -> tuple[bool, str]:
    """Parse PASS/FAIL from review output. Scans bottom-up for robustness."""
    for line in reversed(output.strip().splitlines()):
        line = line.strip().strip(">").strip("*").strip()
        upper = line.upper()
        if upper == "PASS" or upper == "PASS.":
            return True, ""
        if upper.startswith("FAIL:"):
            return False, line[5:].strip()
        if upper == "FAIL" or upper == "FAIL.":
            return False, "No reason given"
    return False, "Review response did not contain PASS or FAIL"


# ── Execution Engine ─────────────────────────────────────────────────────────

class Engine:
    """Task execution engine with review modes."""

    def __init__(self, tasks: list[Task], config: dict, progress: Progress, build_dir: Path,
                 cli_agent: str = "", cli_model: str = "", review: str = "", dry_run: bool = False):
        self.tasks = tasks
        self.config = config
        self.progress = progress
        self.build_dir = build_dir
        self.context_dir = build_dir / "context"
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.cli_agent = cli_agent
        self.cli_model = cli_model or config.get("model", "claude-sonnet-4.6")
        self.review_mode = review or config.get("review", "final")
        self.max_retries = config.get("max_retries", 3)
        self.dry_run = dry_run
        self.max_workers = config.get("parallel", {}).get("max_workers", 1)
        self._log = _get_log()

    def run(self, from_prefix: str = "", only_prefix: str = "", retry: bool = False):
        """Run all tasks (or subset)."""
        tasks = self._filter_tasks(from_prefix, only_prefix, retry)
        if not tasks:
            print("No tasks to run", file=sys.stderr)
            return

        if self.dry_run:
            self._print_plan(tasks)
            return

        print(f"\n{'='*60}", file=sys.stderr)
        print(f"autobuild — {len(tasks)} tasks, review={self.review_mode}, workers={self.max_workers}", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)

        waves = resolve_waves(tasks)
        for i, wave in enumerate(waves):
            if STOP:
                print("\n⚠ Stopped by user", file=sys.stderr)
                break
            print(f"── Wave {i+1}/{len(waves)}: {', '.join(t.name for t in wave)} ──", file=sys.stderr)
            if self.max_workers > 1 and len(wave) > 1:
                if not self._run_wave_parallel(wave):
                    print(f"\n✗ Gate task failed in parallel wave — pipeline stopped", file=sys.stderr)
                    self.progress.finish()
                    return
            else:
                for task in wave:
                    if STOP:
                        break
                    success = self._run_task(task)
                    if not success and task.gate:
                        print(f"\n✗ Gate task {task.name} failed — pipeline stopped", file=sys.stderr)
                        self.progress.finish()
                        return

        self.progress.finish()
        s = self.progress.data["summary"]
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"Done: {s['passed']} passed, {s['failed']} failed, {s['total']} total", file=sys.stderr)

    def _filter_tasks(self, from_prefix: str, only_prefix: str, retry: bool) -> list[Task]:
        tasks = self.tasks
        if only_prefix:
            tasks = [t for t in tasks if t.prefix == only_prefix]
        elif from_prefix:
            found = False
            filtered = []
            for t in tasks:
                if t.prefix == from_prefix:
                    found = True
                if found:
                    filtered.append(t)
            tasks = filtered
        if retry:
            tasks = [t for t in tasks if self.progress.get_task(t.name).get("status") == "failed"]
        return tasks

    def _print_plan(self, tasks: list[Task]):
        waves = resolve_waves(tasks)
        print(f"\nDry run — {len(tasks)} tasks in {len(waves)} waves:\n", file=sys.stderr)
        for i, wave in enumerate(waves):
            print(f"  Wave {i+1}:", file=sys.stderr)
            for t in wave:
                agent = self.cli_agent or t.agent
                deps = f" (deps: {', '.join(t.deps)})" if t.deps else ""
                gate = " [GATE]" if t.gate else ""
                print(f"    {t.name} → {agent}{deps}{gate}", file=sys.stderr)
        print(f"\n  Review: {self.review_mode}, Model: {self.cli_model}", file=sys.stderr)

    def _run_wave_parallel(self, wave: list[Task]) -> bool:
        """Run wave in parallel. Returns False if a gate task failed."""
        from kiro import run_wave
        results = run_wave(self._run_task, wave, max_workers=self.max_workers)
        for task, result in results:
            if isinstance(result, Exception):
                self._log_error(f"Task {task.name} exception: {result}")
                if task.gate:
                    return False
            elif result is False and task.gate:
                return False
        return True

    def _run_task(self, task: Task) -> bool:
        """Execute a single task. Returns True on success."""
        state = self.progress.get_task(task.name)
        if state.get("status") == "passed":
            print(f"  ✓ {task.name} (already passed)", file=sys.stderr)
            return True

        # Pre-verify: skip if task output already exists
        if self._pre_verify(task):
            print(f"  ✓ {task.name} (pre-verify passed — already done)", file=sys.stderr)
            self.progress.set_task(task.name, status="passed", attempts=0,
                                   finished_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
            self.progress.write_tsv(task.name, "passed", 0, 0.0, "", 0)
            return True

        start = time.time()
        self.progress.set_task(task.name, status="running",
                               started_at=time.strftime("%Y-%m-%dT%H:%M:%S"), attempts=0)
        self._log_info(f"starting {task.name}")

        task_ctx_dir = self.context_dir / task.name
        task_ctx_dir.mkdir(parents=True, exist_ok=True)

        agent_name = self.cli_agent or task.agent
        success = False
        last_error = ""
        plan = None  # Plan once, reuse across retries

        for attempt in range(1, self.max_retries + 1):
            if STOP:
                self.progress.set_task(task.name, status="pending")
                return False

            self.progress.set_task(task.name, attempts=attempt)
            print(f"  → {task.name} (attempt {attempt}/{self.max_retries})", file=sys.stderr)

            try:
                result, plan = self._execute_cycle(task, agent_name, task_ctx_dir, attempt, plan)
                if result:
                    success = True
                    break
                last_error = "Review failed"
            except Exception as e:
                last_error = str(e)
                self._log_error(f"{task.name} attempt {attempt} failed: {e}")
                (task_ctx_dir / f"error_{attempt}.md").write_text(
                    f"# Error — Attempt {attempt}\n\n```\n{last_error}\n```"
                )

        duration = time.time() - start
        todos = self._scan_todos(task)
        status = "passed" if success else "failed"

        self.progress.set_task(task.name, status=status,
                               finished_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
                               last_error=last_error if not success else None,
                               todo_count=todos)
        self.progress.write_tsv(task.name, status, attempt, duration, last_error if not success else "", todos)

        sym = "✓" if success else "✗"
        print(f"  {sym} {task.name} ({duration:.0f}s, {attempt} attempts)", file=sys.stderr)
        return success

    def _pre_verify(self, task: Task) -> bool:
        """Check if task is already done without running it."""
        if not task.verify and not task.creates:
            return False
        if task.verify:
            try:
                r = subprocess.run(task.verify, shell=True, capture_output=True, timeout=60, cwd=str(Path.cwd()))
                if r.returncode != 0:
                    return False
            except Exception:
                return False
        for f in task.creates:
            if not Path(f).exists():
                return False
        return True

    def _execute_cycle(self, task: Task, agent_name: str, ctx_dir: Path, attempt: int,
                       existing_plan: str | None) -> tuple[bool, str]:
        """Run plan → execute → verify → review cycle. Returns (success, plan)."""
        from kiro import AcpAgent

        agent = AcpAgent(agent_name, self.cli_model, cwd=str(Path.cwd()))
        try:
            dep_context = self._gather_dep_context(task)
            error_context = self._gather_error_context(ctx_dir, attempt)

            # PLAN (only on first attempt — reuse plan across retries)
            if existing_plan is None:
                self.progress.set_task(task.name, current_phase="plan")
                plan_prompt = self._build_plan_prompt(task, dep_context, "")
                plan = agent.prompt(plan_prompt, timeout=task.timeout)
                (ctx_dir / f"plan_{attempt}.md").write_text(plan)
            else:
                plan = existing_plan

            # EXECUTE
            self.progress.set_task(task.name, current_phase="execute")
            exec_prompt = f"Execute this plan. Make the actual code changes.\n\n## Plan\n\n{plan}\n\n## Original Task\n\n{task.content}"
            if error_context:
                exec_prompt += f"\n\n## Previous failed attempts (avoid these mistakes)\n\n{error_context}"
            output = agent.prompt(exec_prompt, timeout=task.timeout)
            (ctx_dir / f"exec_{attempt}.md").write_text(output)

            # VERIFY
            self.progress.set_task(task.name, current_phase="verify")
            verify_ok, verify_details = self._verify(task)

            if not verify_ok:
                err = self._build_error_file(task, attempt, verify_details)
                (ctx_dir / f"error_{attempt}.md").write_text(err)
                return False, plan

            if self.review_mode == "none":
                return True, plan

            # REVIEW (final mode)
            self.progress.set_task(task.name, current_phase="review")
            review_prompt = (
                f"Review the work you just did for this task. Check:\n"
                f"- Does it match the original requirements?\n"
                f"- Are there any bugs or missing pieces?\n"
                f"- Is the code quality acceptable?\n\n"
                f"Respond with EXACTLY one line: PASS or FAIL: <reason>\n\n"
                f"## Original Task\n\n{task.content}\n\n"
                f"## Your Output\n\n{output}"
            )
            review = agent.prompt(review_prompt, timeout=task.timeout)
            (ctx_dir / f"review_{attempt}.md").write_text(review)

            passed, reason = _parse_review(review)
            if not passed:
                err = self._build_error_file(task, attempt, {"review": reason})
                (ctx_dir / f"error_{attempt}.md").write_text(err)
            return passed, plan

        finally:
            agent.close()

    def _build_plan_prompt(self, task: Task, dep_context: str, error_context: str) -> str:
        parts = [
            f"Plan the implementation for this task. Describe what you'll do step by step.\n",
            f"## Task\n\n{task.content}",
        ]
        if dep_context:
            parts.append(f"\n## Context from completed dependencies\n\n{dep_context}")
        if error_context:
            parts.append(f"\n## Previous failed attempts (avoid these mistakes)\n\n{error_context}")
        return "\n".join(parts)

    def _gather_dep_context(self, task: Task) -> str:
        parts = []
        for dep in task.deps:
            for t in self.tasks:
                if t.prefix == dep:
                    ctx_dir = self.context_dir / t.name
                    for f in sorted(ctx_dir.glob("exec_*.md")):
                        parts.append(f"### {t.name}\n\n{f.read_text()[:2000]}")
                    break
        return "\n\n".join(parts)

    def _gather_error_context(self, ctx_dir: Path, attempt: int) -> str:
        parts = []
        for i in range(1, attempt):
            err = ctx_dir / f"error_{i}.md"
            if err.exists():
                parts.append(f"### Attempt {i}\n\n{err.read_text()[:2000]}")
        return "\n\n".join(parts)

    def _verify(self, task: Task) -> tuple[bool, dict]:
        """Run verify command + file checks + syntax checks. Returns (ok, details)."""
        details = {}
        ok = True
        cwd = str(Path.cwd())

        # Verify command
        if task.verify:
            try:
                r = subprocess.run(task.verify, shell=True, capture_output=True, text=True, timeout=60, cwd=cwd)
                if r.returncode != 0:
                    ok = False
                    details["verify_cmd"] = task.verify
                    details["verify_rc"] = r.returncode
                    details["verify_stdout"] = r.stdout[:1000]
                    details["verify_stderr"] = r.stderr[:1000]
            except subprocess.TimeoutExpired:
                ok = False
                details["verify_cmd"] = task.verify
                details["verify_rc"] = -1
                details["verify_stderr"] = "Timeout after 60s"

        # File existence checks
        file_checks = []
        for f in task.creates:
            p = Path(f)
            exists = p.exists()
            size = p.stat().st_size if exists else None
            file_checks.append({"file": f, "exists": exists, "size": size})
            if not exists:
                ok = False
        if file_checks:
            details["file_checks"] = file_checks

        # Syntax checks on created files
        syntax_checks = []
        for f in task.creates:
            p = Path(f)
            if not p.exists():
                continue
            if f.endswith(".py"):
                try:
                    ast.parse(p.read_text())
                    syntax_checks.append({"file": f, "valid": True})
                except SyntaxError as e:
                    syntax_checks.append({"file": f, "valid": False, "error": f"line {e.lineno}: {e.msg}"})
                    ok = False
            elif f.endswith(".json"):
                try:
                    json.loads(p.read_text())
                    syntax_checks.append({"file": f, "valid": True})
                except json.JSONDecodeError as e:
                    syntax_checks.append({"file": f, "valid": False, "error": f"line {e.lineno}: {e.msg}"})
                    ok = False
        if syntax_checks:
            details["syntax_checks"] = syntax_checks

        return ok, details

    def _build_error_file(self, task: Task, attempt: int, details: dict) -> str:
        """Build structured error markdown for retry context."""
        lines = [f"# Error — {task.name} — Attempt {attempt}", "",
                 f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%S')}", ""]

        if "verify_cmd" in details:
            lines += ["## Verify command failed", "",
                       f"```bash\n{details['verify_cmd']}\n```",
                       f"Exit code: {details.get('verify_rc', '?')}", ""]
            if details.get("verify_stdout", "").strip():
                lines += ["### stdout", f"```\n{details['verify_stdout'].strip()}\n```", ""]
            if details.get("verify_stderr", "").strip():
                lines += ["### stderr", f"```\n{details['verify_stderr'].strip()}\n```", ""]

        if "file_checks" in details:
            lines += ["## File checks", "| File | Status | Size |", "|------|--------|------|"]
            for fc in details["file_checks"]:
                status = "✓ exists" if fc["exists"] else "✗ MISSING"
                size = f"{fc['size']}B" if fc.get("size") else "—"
                lines.append(f"| {fc['file']} | {status} | {size} |")
            lines.append("")

        if "syntax_checks" in details:
            lines += ["## Syntax checks", "| File | Status | Error |", "|------|--------|-------|"]
            for sc in details["syntax_checks"]:
                status = "✓ valid" if sc["valid"] else "✗ INVALID"
                err = sc.get("error", "—") or "—"
                lines.append(f"| {sc['file']} | {status} | {err} |")
            lines.append("")

        if "review" in details:
            lines += ["## Review failed", "", details["review"], ""]

        return "\n".join(lines)

    def _scan_todos(self, task: Task) -> int:
        count = 0
        for f in task.creates:
            p = Path(f)
            if p.exists() and p.is_file():
                try:
                    content = p.read_text()
                    count += len(re.findall(r"TODO\(autobuild\)", content))
                except Exception:
                    pass
        return count

    def _log_info(self, msg, **data):
        log = _get_log()
        if log:
            log.info(msg, **data)

    def _log_error(self, msg, **data):
        log = _get_log()
        if log:
            log.error(msg, **data)


# ── CLI ──────────────────────────────────────────────────────────────────────

def _load_config(folder: Path) -> dict:
    """Load autobuild.json from project root or folder parent."""
    for d in [Path.cwd(), folder.parent, folder]:
        cfg = d / "autobuild.json"
        if cfg.exists():
            try:
                return json.loads(cfg.read_text())
            except json.JSONDecodeError:
                pass
    return {}


def _gen_uid() -> str:
    import random
    return f"{time.strftime('%Y%m%d-%H%M')}-{random.randint(0, 0xfff):03x}"


def _cmd_status(build_dir: Path):
    """Print progress table."""
    pf = build_dir / "progress.json"
    if not pf.exists():
        print("No progress file found", file=sys.stderr)
        return
    data = json.loads(pf.read_text())
    s = data.get("summary", {})
    print(f"\nRun: {data.get('run_uid', '?')}  Started: {data.get('started_at', '?')}", file=sys.stderr)
    fin = data.get("finished_at")
    if fin:
        print(f"Finished: {fin}", file=sys.stderr)
    print(f"Progress: {s.get('passed',0)}/{s.get('total',0)} passed, "
          f"{s.get('failed',0)} failed, {s.get('running',0)} running\n", file=sys.stderr)

    tasks = data.get("tasks", {})
    if tasks:
        print(f"{'Task':<35} {'Status':<10} {'Att':>3} {'Phase':<10} {'Error'}", file=sys.stderr)
        print("-" * 80, file=sys.stderr)
        for name, t in tasks.items():
            status = t.get("status", "?")
            sym = {"passed": "✓", "failed": "✗", "running": "→", "pending": "·"}.get(status, "?")
            err = (t.get("last_error") or "")[:40]
            phase = t.get("current_phase") or ""
            print(f"{sym} {name:<33} {status:<10} {t.get('attempts',0):>3} {phase:<10} {err}", file=sys.stderr)


def _cmd_report(build_dir: Path):
    """Print JSON report."""
    pf = build_dir / "progress.json"
    if not pf.exists():
        print("{}", file=sys.stderr)
        return
    print(pf.read_text())


def _cmd_reset(build_dir: Path, prefix: str):
    """Reset a task to pending."""
    pf = build_dir / "progress.json"
    if not pf.exists():
        return
    data = json.loads(pf.read_text())
    for name, t in data.get("tasks", {}).items():
        if name.startswith(prefix):
            t["status"] = "pending"
            t["attempts"] = 0
            t["last_error"] = None
            t["current_phase"] = None
            print(f"Reset {name}", file=sys.stderr)
    pf.write_text(json.dumps(data, indent=2))


def _cmd_reset_all(build_dir: Path):
    """Reset all tasks."""
    pf = build_dir / "progress.json"
    if pf.exists():
        pf.unlink()
    tsv = build_dir / "results.tsv"
    if tsv.exists():
        tsv.unlink()
    ctx = build_dir / "context"
    if ctx.exists():
        shutil.rmtree(ctx)
    print("Reset all progress", file=sys.stderr)


def _cmd_makefile(folder: str):
    """Generate Makefile with common commands."""
    content = f""".PHONY: run status stop tail retry report

run:
\tautobuild {folder} --bg
status:
\tautobuild {folder} --status
stop:
\tautobuild {folder} --stop
tail:
\tautobuild {folder} --tail
retry:
\tautobuild {folder} --retry --bg
report:
\tautobuild {folder} --report
"""
    Path("Makefile").write_text(content)
    print("Generated Makefile", file=sys.stderr)


def main():
    # bg integration — intercepts --bg/--tail/--stop (NOT --status, engine handles that)
    setup_bg(exclude={"--status"})

    signal.signal(signal.SIGINT, _sigint)

    p = argparse.ArgumentParser(description="autobuild — task engine for kiro-cli agents")
    p.add_argument("folder", help="Task folder path")
    p.add_argument("--from", dest="from_prefix", help="Resume from task prefix")
    p.add_argument("--only", dest="only_prefix", help="Run single task by prefix")
    p.add_argument("--retry", action="store_true", help="Re-run failed tasks only")
    p.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    p.add_argument("--status", action="store_true", help="Show progress table")
    p.add_argument("--report", action="store_true", help="Print JSON report")
    p.add_argument("--reset", help="Reset task to pending (by prefix)")
    p.add_argument("--reset-all", action="store_true", help="Reset all progress")
    p.add_argument("--makefile", action="store_true", help="Generate Makefile")
    p.add_argument("--agent", help="Override agent for all tasks")
    p.add_argument("--model", help="Override model")
    p.add_argument("--review", choices=["none", "final"], help="Review mode (extended/full coming soon)")
    p.add_argument("--workers", type=int, help="Parallel workers per wave")

    args = p.parse_args()
    folder = Path(args.folder)
    build_dir = Path.cwd() / ".auto-build"
    build_dir.mkdir(parents=True, exist_ok=True)

    # Non-execution commands
    if args.makefile:
        _cmd_makefile(args.folder)
        return
    if args.status:
        _cmd_status(build_dir)
        return
    if args.report:
        _cmd_report(build_dir)
        return
    if args.reset:
        _cmd_reset(build_dir, args.reset)
        return
    if args.reset_all:
        _cmd_reset_all(build_dir)
        return

    if not folder.is_dir():
        print(f"Error: {folder} is not a directory", file=sys.stderr)
        sys.exit(1)

    config = _load_config(folder)
    if args.workers:
        config.setdefault("parallel", {})["max_workers"] = args.workers

    tasks = load_tasks(folder, config)
    if not tasks:
        print("No task files found", file=sys.stderr)
        sys.exit(1)

    run_uid = _gen_uid()
    os.environ["LOGD_UID"] = run_uid

    # Instance lock — prevent two runs on same project
    lock_file = build_dir / ".lock"
    if lock_file.exists():
        try:
            lock_pid = int(lock_file.read_text().strip())
            try:
                os.kill(lock_pid, 0)
                print(f"Error: another autobuild is running (PID {lock_pid}). Use --stop first.", file=sys.stderr)
                sys.exit(1)
            except OSError:
                lock_file.unlink()  # stale lock
        except (ValueError, FileNotFoundError):
            pass
    try:
        fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
    except FileExistsError:
        # Race: another process created it between our check and open
        print("Error: another autobuild just started. Use --stop first.", file=sys.stderr)
        sys.exit(1)

    try:
        log = _get_log()
        if log:
            log.info(f"pipeline start", tasks=len(tasks), uid=run_uid)

        # Health checks
        if not args.dry_run:
            print("\nHealth checks:", file=sys.stderr)
            if not run_health_checks(config):
                print("\n✗ Health checks failed — aborting", file=sys.stderr)
                sys.exit(1)
            print("", file=sys.stderr)

        progress = Progress(build_dir, run_uid)
        progress.init_tasks(tasks)

        engine = Engine(
            tasks=tasks, config=config, progress=progress, build_dir=build_dir,
            cli_agent=args.agent or "", cli_model=args.model or "",
            review=args.review or "", dry_run=args.dry_run,
        )
        engine.run(
            from_prefix=args.from_prefix or "",
            only_prefix=args.only_prefix or "",
            retry=args.retry,
        )
    finally:
        lock_file.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
