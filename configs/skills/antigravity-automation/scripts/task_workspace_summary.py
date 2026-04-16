#!/usr/bin/env python3
"""task_workspace_summary.py

Workspace Summarizer

Creates a compact, evidence-first summary of a workspace for Antigravity/TUI.

- Uses AutomationAgentTask (Brain logging via automation_tasks/automation_steps)
- Safe by default: read-only probes (git status/log, filesystem listings)

Usage:
  python3 task_workspace_summary.py [--workspace PATH] [--projects-root PATH] [--max-files N] [--json]

Notes:
- Default workspace resolves to the repo root containing this skill (two levels up
  from this script: skills/antigravity-automation/scripts -> repo root).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from lib import AutomationAgentTask


def _run(cmd: List[str], cwd: Optional[Path] = None, timeout_s: int = 20) -> Dict[str, Any]:
    """Run a command and return structured output (never raises)."""
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        return {
            "cmd": cmd,
            "cwd": str(cwd) if cwd else None,
            "exit_code": p.returncode,
            "stdout": (p.stdout or "").strip(),
            "stderr": (p.stderr or "").strip(),
        }
    except Exception as e:
        return {
            "cmd": cmd,
            "cwd": str(cwd) if cwd else None,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"{type(e).__name__}: {e}",
        }


def _guess_default_workspace() -> Path:
    # .../skills/antigravity-automation/scripts/task_workspace_summary.py -> repo root
    return Path(__file__).resolve().parents[3]


def _summarize_git(task: AutomationAgentTask, workspace: Path) -> Dict[str, Any]:
    if not (workspace / ".git").exists():
        return {"enabled": False, "reason": "not a git repo"}

    status = task.step(
        "Git Status",
        _run,
        ["git", "status", "--porcelain=v1"],
        workspace,
        20,
    )
    head = task.step(
        "Git HEAD",
        _run,
        ["git", "rev-parse", "HEAD"],
        workspace,
        10,
    )
    branch = task.step(
        "Git Branch",
        _run,
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        workspace,
        10,
    )
    log = task.step(
        "Git Recent Commits",
        _run,
        ["git", "log", "-n", "5", "--pretty=format:%h %ad %s", "--date=short"],
        workspace,
        20,
    )

    changed = []
    if isinstance(status, dict) and status.get("exit_code") == 0:
        changed = [ln for ln in (status.get("stdout") or "").splitlines() if ln.strip()]

    return {
        "enabled": True,
        "branch": (branch.get("stdout") if isinstance(branch, dict) else "").strip(),
        "head": (head.get("stdout") if isinstance(head, dict) else "").strip(),
        "changed_files": changed,
        "recent_commits": (log.get("stdout") if isinstance(log, dict) else "").splitlines(),
    }


def _read_first_line(path: Path, max_bytes: int = 4096) -> str:
    try:
        with path.open("rb") as f:
            data = f.read(max_bytes)
        txt = data.decode("utf-8", errors="replace")
        for ln in txt.splitlines():
            if ln.strip():
                return ln.strip()
        return ""
    except Exception:
        return ""


def _summarize_project_dir(project_dir: Path) -> Dict[str, Any]:
    pkg = project_dir / "package.json"
    readme_md = project_dir / "README.md"
    readme_txt = project_dir / "README"

    out: Dict[str, Any] = {
        "name": project_dir.name,
        "path": str(project_dir),
        "has_package_json": pkg.exists(),
        "has_readme": readme_md.exists() or readme_txt.exists(),
    }

    if pkg.exists():
        try:
            obj = json.loads(pkg.read_text(encoding="utf-8", errors="replace"))
            out["package"] = {
                "name": obj.get("name"),
                "version": obj.get("version"),
                "private": obj.get("private"),
            }
        except Exception as e:
            out["package_error"] = f"{type(e).__name__}: {e}"

    rp = readme_md if readme_md.exists() else (readme_txt if readme_txt.exists() else None)
    if rp:
        out["readme_first_line"] = _read_first_line(rp)

    return out


def _summarize_fs(
    task: AutomationAgentTask,
    workspace: Path,
    max_files: int,
    projects_root: Optional[Path],
    max_projects: int = 50,
) -> Dict[str, Any]:
    # Keep it light: list top-level entries + recent file mtimes (excluding node_modules)
    top = task.step(
        "List Workspace Root",
        _run,
        ["bash", "-lc", "ls -la"],
        workspace,
        20,
    )

    projects = None
    project_names: List[str] = []
    project_summaries: Optional[List[Dict[str, Any]]] = None

    if projects_root:
        projects = task.step(
            "List Projects Root",
            _run,
            [
                "bash",
                "-lc",
                # directories only, one per line, stable order
                "ls -1d */ 2>/dev/null | sed 's:/$::' | sort",
            ],
            projects_root,
            20,
        )

        if isinstance(projects, dict) and (projects.get("stdout") or "").strip():
            project_names = [ln.strip() for ln in projects["stdout"].splitlines() if ln.strip()]

        def _summarize_all() -> List[Dict[str, Any]]:
            out: List[Dict[str, Any]] = []
            for name in project_names[:max_projects]:
                pdir = (projects_root / name).resolve()
                if pdir.is_dir():
                    out.append(_summarize_project_dir(pdir))
            return out

        project_summaries = task.step(
            "Summarize Projects",
            _summarize_all,
        )

    # Recent files (modified) - avoid node_modules and .git
    find_cmd = (
        "find . -type f "
        "-not -path './node_modules/*' "
        "-not -path './.git/*' "
        "-maxdepth 4 "
        "-print0 | xargs -0 stat -f '%m %N' | sort -nr | head -n "
        + str(max_files)
    )
    recent = task.step(
        "Recent Files",
        _run,
        ["bash", "-lc", find_cmd],
        workspace,
        40,
    )

    return {
        "root_listing": (top.get("stdout") if isinstance(top, dict) else ""),
        "projects_root": str(projects_root) if projects_root else None,
        "top_level_projects": project_names if projects_root else None,
        "project_summaries": project_summaries if projects_root else None,
        "recent_files": (recent.get("stdout") if isinstance(recent, dict) else "").splitlines(),
    }


def _summarize_system(task: AutomationAgentTask, workspace: Path) -> Dict[str, Any]:
    df = task.step(
        "Disk Space",
        _run,
        ["df", "-h", str(workspace)],
        None,
        10,
    )
    uname = task.step(
        "System Info",
        _run,
        ["uname", "-a"],
        None,
        10,
    )
    return {
        "disk": df,
        "uname": uname,
    }


def render_markdown(summary: Dict[str, Any]) -> str:
    ws = summary.get("workspace")
    ts = summary.get("ts")
    lines = [
        f"# Workspace Summary",
        f"- workspace: `{ws}`",
        f"- ts: {ts}",
        "",
    ]

    git = summary.get("git") or {}
    if git.get("enabled"):
        lines += [
            "## Git",
            f"- branch: `{git.get('branch','')}`",
            f"- head: `{git.get('head','')}`",
            f"- changed: {len(git.get('changed_files', []))}",
        ]
        for ln in (git.get("changed_files") or [])[:20]:
            lines.append(f"  - {ln}")
        lines.append("")
        lines.append("### Recent commits")
        for ln in (git.get("recent_commits") or [])[:5]:
            lines.append(f"- {ln}")
        lines.append("")
    else:
        lines += ["## Git", f"- disabled: {git.get('reason','unknown')}", ""]

    projects = summary.get("fs", {}).get("top_level_projects")
    proj_summaries = summary.get("fs", {}).get("project_summaries")

    if projects is not None:
        lines += ["## Projects (top-level)"]
        for p in projects[:50]:
            lines.append(f"- {p}")
        lines.append("")

    if isinstance(proj_summaries, list) and proj_summaries:
        lines += ["## Projects (summary)"]
        for p in proj_summaries[:30]:
            name = p.get("name")
            pkg = p.get("package") or {}
            pkg_name = pkg.get("name")
            pkg_ver = pkg.get("version")
            readme = p.get("readme_first_line") or ""
            bits = []
            if pkg_name:
                bits.append(f"npm: {pkg_name}{('@'+str(pkg_ver)) if pkg_ver else ''}")
            if readme:
                bits.append(readme)
            suffix = (" — " + " | ".join(bits)) if bits else ""
            lines.append(f"- {name}{suffix}")
        lines.append("")

    lines += ["## Recent files (mtime)"]
    for ln in (summary.get("fs", {}).get("recent_files") or [])[:20]:
        lines.append(f"- {ln}")
    lines.append("")

    lines += ["## Disk"]
    disk = summary.get("system", {}).get("disk")
    if isinstance(disk, dict) and disk.get("stdout"):
        lines.append("```")
        lines.append(disk.get("stdout"))
        lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=str, default=None)
    ap.add_argument(
        "--projects-root",
        type=str,
        default="/Users/danny/Desktop/nexus-projects/",
        help="Folder containing top-level project directories to list",
    )
    ap.add_argument("--max-files", type=int, default=30)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    workspace = Path(args.workspace).expanduser().resolve() if args.workspace else _guess_default_workspace()
    projects_root = Path(args.projects_root).expanduser().resolve() if args.projects_root else None
    if projects_root and not projects_root.exists():
        projects_root = None

    task = AutomationAgentTask(
        name="Workspace Summarizer",
        description=f"Summarize workspace state for {workspace}",
    )

    task.start()

    try:
        git = _summarize_git(task, workspace)
        fs = _summarize_fs(task, workspace, args.max_files, projects_root)
        system = _summarize_system(task, workspace)

        summary = {
            "workspace": str(workspace),
            "ts": int(time.time()),
            "git": git,
            "fs": fs,
            "system": system,
        }

        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(render_markdown(summary))

        task.finish(success=True, final_result=summary)
        return 0

    except Exception as e:
        err = {"error": str(e), "workspace": str(workspace), "ts": int(time.time())}
        print(f"WORKSPACE_SUMMARY_ERROR: {e}")
        task.finish(success=False, final_result=err)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
