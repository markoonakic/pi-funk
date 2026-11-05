#!/usr/bin/env python3
"""BB-only Pi launcher: explicit shared tools and trusted Lens selection."""

import json
import os
from pathlib import Path
import shutil
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
    lens_approved = cwd.resolve() in {Path(root).expanduser().resolve() for root in roots}
    trust_path = agent_dir / "trust.json"
    trust = json.loads(trust_path.read_text()) if trust_path.exists() else {}
    if not isinstance(trust, dict) or any(
        not isinstance(path, str) or not Path(path).is_absolute() or not isinstance(value, bool)
        for path, value in trust.items()
    ):
        raise ValueError("trust.json must map absolute directory paths to booleans")
    # Native MCP uses the saved Pi trust store, without enabling Lens or inheriting parent trust.
    approved = lens_approved or trust.get(str(cwd.resolve())) is True
    selected = [pi, *args, "--approve" if approved else "--no-approve"]
    if lens_approved:
        if not Path(lens).is_file():
            raise FileNotFoundError(f"Selected Lens entry is missing: {lens}")
        selected += ["--extension", lens, "--no-autoformat", "--no-autofix", "--no-tests"]
    return selected


def select_native_mcp(args, agent_dir):
    """Keep new runtimes native even while an older BB daemon retains its launch arguments."""
    legacy = {str(root / "npm/node_modules/pi-mcp-adapter/index.ts")
              for root in (agent_dir, agent_dir.parent / "agent")}
    selected = []
    index = 0
    while index < len(args):
        if (args[index] in ("--extension", "-e") and index + 1 < len(args)
                and args[index + 1] in legacy):
            index += 2
            continue
        selected.append(args[index])
        index += 1
    if not any(selected[index - 1] in ("--extension", "-e") and selected[index] == "builtin:mcp"
               for index in range(1, len(selected))):
        selected += ["--extension", "builtin:mcp"]
    return selected


def select_shared_tools(args, agent_dir):
    shared = agent_dir.parent / "agent/npm/node_modules"
    # Let Pi use the package manifest: Web Access moved its entry from index.ts to dist/.
    web = shared / "pi-web-access"
    selected = [str(web) if arg == str(web / "index.ts") else arg for arg in args]
    for relative in (
            # The core provides process tools; terminal log/dock overlays are not BB UI.
        "@aliou/pi-processes/extensions/processes/index.ts",
    ):
        entry = shared / relative
        if not entry.is_file():
            raise FileNotFoundError(f"Selected shared tool entry is missing: {entry}")
        if str(entry) not in selected:
            selected += ["--extension", str(entry)]
    return selected


def select_gateway_models(args):
    entry = Path(__file__).resolve().parents[2] / "extensions/cliproxy-models/index.ts"
    if not entry.is_file():
        raise FileNotFoundError("Gateway model discovery extension is missing")
    selected = list(args)
    if str(entry) not in selected:
        selected += ["--extension", str(entry)]
    return selected


def typescript_path(path):
    """Let Lens locate tsserver.js beside Nix's real tsc, not its bin wrapper."""
    tsc = shutil.which("tsc", path=path)
    if tsc:
        native = Path(tsc).resolve().parent.parent / "lib/node_modules/typescript/bin"
        if (native / "tsc").is_file() and (native.parent / "lib/tsserver.js").is_file():
            return str(native) + os.pathsep + path
    return path


def tool_environment(agent_dir):
    return {
        "FFF_FRECENCY_DB": str(agent_dir / "fff/frecency"),
        "FFF_HISTORY_DB": str(agent_dir / "fff/history"),
        # Replace Pi's built-in find/grep; Pi autocomplete is not BB's UI.
        "PI_FFF_MODE": "override",
    }


def main():
    pi, lens, *args = sys.argv[1:]
    agent_dir = Path(os.environ["PI_CODING_AGENT_DIR"]).expanduser().resolve()
    args = select_native_mcp(args, agent_dir)
    selected = launch_args(pi, lens, select_gateway_models(select_shared_tools(args, agent_dir)), agent_dir, Path.cwd())
    # These are profile-owned state/config paths, independent of standalone Lens.
    os.environ.update({
        "PI_LENS_HOME": str(agent_dir / "lens"),
        "PILENS_DATA_DIR": str(agent_dir / "lens/projects"),
        "PI_LENS_CONFIG_PATH": str(agent_dir / "lens/config.json"),
        "PI_LENS_DISABLE_LSP_INSTALL": "1",
        "PI_LENS_DISABLE_TOOL_INSTALL": "1",
        "PI_LENS_AUTO_INSTALL": "0",
    })
    os.environ.pop("PI_MCP_ADAPTER_OAUTH_FILE_KEY", None)
    os.environ.update(tool_environment(agent_dir))
    os.environ["PATH"] = typescript_path(os.environ.get("PATH", ""))
    os.execv(pi, selected)


if __name__ == "__main__":
    main()
