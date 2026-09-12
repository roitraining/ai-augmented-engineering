#!/usr/bin/env python3
"""Lab loader for the AI-Augmented Engineering course repo.

    python lab.py start 2            # reset the workspace to the start of Lab 2
    python lab.py solution 2         # load the finished state of Lab 2
    python lab.py start 2 --copilot  # same, Copilot path (copilot-starters/)
    python lab.py status             # which lab state the workspace matches
    python lab.py list               # what each lab state contains

A lab state is a folder under lab-starters/ (or copilot-starters/). "start N"
removes every file any lab produces, then copies lab-starters/labN in.
"solution N" loads lab-starters/lab(N+1); the finished state of the last lab
is lab-starters/solution. Nothing outside those files is touched.

The script refuses to run if git shows uncommitted changes, so nobody loses
work by accident. Commit or stash first, or pass --force.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
# Students open the pipeline folder as their Cursor workspace when it exists;
# starters and instructor material live one level up, outside the agent's view.
ROOT = REPO / "sample_pipeline" if (REPO / "sample_pipeline").is_dir() else REPO
LAST_LAB = 4


def starters_dir(copilot: bool) -> Path:
    return REPO / ("copilot-starters" if copilot else "lab-starters")


def state_dir(name: str, copilot: bool) -> Path:
    d = starters_dir(copilot) / name
    if not d.is_dir():
        sys.exit(f"No such lab state: {d.relative_to(REPO)}")
    return d


def files_under(d: Path) -> list[Path]:
    return sorted(p.relative_to(d) for p in d.rglob("*") if p.is_file())


def owned_paths(copilot: bool) -> set[Path]:
    """Every file that any lab state ships. These are the files labs create
    or edit, so they are the only files start/solution may delete."""
    owned: set[Path] = set()
    for d in starters_dir(copilot).iterdir():
        if d.is_dir():
            owned.update(files_under(d))
    return owned


def git_dirty() -> bool:
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return bool(out.strip())


def load(state: str, copilot: bool, force: bool) -> None:
    src = state_dir(state, copilot)
    if git_dirty() and not force:
        sys.exit("You have uncommitted changes. Commit or stash them first "
                 "(git add -A && git commit -m 'checkpoint'), or re-run with --force.")
    removed = 0
    for rel in owned_paths(copilot):
        target = ROOT / rel
        if target.exists():
            target.unlink()
            removed += 1
    # drop directories a lab may have emptied (keeps .gitkeep-only folders tidy)
    for d in ("src", "tests", "docs", "audit", ".cursor/skills", ".cursor/rules", ".github"):
        p = ROOT / d
        if p.is_dir():
            for sub in sorted(p.rglob("*"), reverse=True):
                if sub.is_dir() and not any(sub.iterdir()):
                    sub.rmdir()
    copied = 0
    for rel in files_under(src):
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / rel, dst)
        copied += 1
    for cache in ROOT.rglob("__pycache__"):
        if "venv" not in cache.parts and ".venv" not in cache.parts:
            shutil.rmtree(cache, ignore_errors=True)
    print(f"Loaded {src.relative_to(REPO)} into {ROOT.name}/: removed {removed} file(s), copied {copied}.")
    print("Check with:  python lab.py status")


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def status(copilot: bool) -> None:
    states = [d for d in sorted(starters_dir(copilot).iterdir()) if d.is_dir()]
    owned = owned_paths(copilot)
    present = {rel for rel in owned if (ROOT / rel).exists()}
    print(f"Workspace: {ROOT}")
    for d in states:
        files = files_under(d)
        same = sum(1 for rel in files if (ROOT / rel).exists() and digest(ROOT / rel) == digest(d / rel))
        extra = len(present - set(files))
        mark = "  <- matches" if same == len(files) and extra == 0 else ""
        print(f"  {d.name:10s} {same}/{len(files)} files identical, {extra} extra lab file(s) present{mark}")
    if git_dirty():
        print("git: uncommitted changes present")


def list_states(copilot: bool) -> None:
    for d in sorted(starters_dir(copilot).iterdir()):
        if d.is_dir():
            print(f"{d.name}/")
            for rel in files_under(d):
                print(f"    {rel.as_posix()}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["start", "solution", "status", "list"])
    ap.add_argument("lab", nargs="?", type=int, help="lab number 1-4")
    ap.add_argument("--copilot", action="store_true", help="use copilot-starters/ instead of lab-starters/")
    ap.add_argument("--force", action="store_true", help="proceed even with uncommitted git changes")
    a = ap.parse_args()

    if a.command in ("start", "solution"):
        if a.lab is None or not 1 <= a.lab <= LAST_LAB:
            sys.exit(f"Give a lab number 1-{LAST_LAB}, e.g.  python lab.py {a.command} 2")
        if a.command == "start":
            load(f"lab{a.lab}", a.copilot, a.force)
        else:
            load("solution" if a.lab == LAST_LAB else f"lab{a.lab + 1}", a.copilot, a.force)
    elif a.command == "status":
        status(a.copilot)
    else:
        list_states(a.copilot)


if __name__ == "__main__":
    main()
