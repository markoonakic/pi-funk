#!/usr/bin/env python3
"""BB-only Pi launcher: explicit RPIV Todo and trusted Lens selection."""

import json
import os
from pathlib import Path
import sys


def launch_args(pi, lens, args, agent_dir, cwd):
    if any(arg in ("--approve", "--no-approve") for arg in args):
        raise ValueError("Project trust is selected by the BB launcher, not bridge arguments")
    path = agent_dir / "lens-projects.json"
    roots = json.loads(path.read_text()) if path.exists() else []
    if not isinstance(roots, list) or any(
        not isinstance(root, str) or not Path(root).expanduser().is_absolute()
        for root in roots
    ):
        raise ValueError("lens-projects.json must be an array of absolute directory paths")
    # Exact cwd matches: a sibling/worktree/nested project needs its own approval.
    approved = cwd.resolve() in {Path(root).expanduser().resolve() for root in roots}
    selected = [pi, *args, "--approve" if approved else "--no-approve"]
    if approved:
        if not Path(lens).is_file():
            raise FileNotFoundError(f"Selected Lens entry is missing: {lens}")
        selected += ["--extension", lens, "--no-autoformat", "--no-autofix", "--no-tests"]
    return selected


def select_rpiv(args, agent_dir):
    rpiv = agent_dir.parent / "agent/npm/node_modules/@juicesharp/rpiv-todo/index.ts"
    if not rpiv.is_file():
        raise FileNotFoundError(f"Selected RPIV Todo entry is missing: {rpiv}")
    selected = list(args)
    if str(rpiv) not in selected:
        selected += ["--extension", str(rpiv)]
    return selected


def tool_environment(agent_dir):
    return {
        "MCP_UI_VIEWER": "none",
        "FFF_FRECENCY_DB": str(agent_dir / "fff/frecency"),
        "FFF_HISTORY_DB": str(agent_dir / "fff/history"),
        # Replace Pi's built-in find/grep; Pi autocomplete is not BB's UI.
        "PI_FFF_MODE": "override",
    }


def main():
    pi, lens, *args = sys.argv[1:]
    agent_dir = Path(os.environ["PI_CODING_AGENT_DIR"]).expanduser().resolve()
    selected = launch_args(pi, lens, select_rpiv(args, agent_dir), agent_dir, Path.cwd())
    # These are profile-owned state/config paths, independent of standalone Lens.
    os.environ.update({
        "PI_LENS_HOME": str(agent_dir / "lens"),
        "PILENS_DATA_DIR": str(agent_dir / "lens/projects"),
        "PI_LENS_CONFIG_PATH": str(agent_dir / "lens/config.json"),
        "PI_LENS_DISABLE_LSP_INSTALL": "1",
        "PI_LENS_DISABLE_TOOL_INSTALL": "1",
        "PI_LENS_AUTO_INSTALL": "0",
    })
    os.environ.update(tool_environment(agent_dir))
    os.execv(pi, selected)


if __name__ == "__main__":
    main()
