#!/usr/bin/env python3
"""No-model RPC Lens check. Usage: check-lens.py PI LENS_ENTRY SERVER_BIN_PATHS.

Uses the real Lens factory through a recording adapter, real RPC context and
preinstalled LSP. All auth, project files, settings and Lens state are disposable.
"""
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

profile = Path(__file__).resolve().parent
pi, lens, servers, *extensions = sys.argv[1:]
with tempfile.TemporaryDirectory(prefix="bb-lens-check-") as tmp:
    root = Path(tmp)
    agent, cwd, home = root / "agent", root / "project", root / "home"
    for directory in (agent, cwd / ".pi", home):
        directory.mkdir(parents=True)
    (agent / "settings.json").write_text((profile / "settings.json").read_text())
    (agent / "web-search.json").write_text('{"workflow":"none","allowBrowserCookies":false}')
    (agent / "mcp.json").write_text('{"mcpServers":{}}')
    (agent / "lens-projects.json").write_text(json.dumps([str(cwd)]))
    (cwd / "tsconfig.json").write_text('{"compilerOptions":{"strict":true,"noEmit":true},"include":["*.ts"]}')
    (cwd / "example.ts").write_text('export function add(a: number, b: number) { return a + b; }\nexport const result: number = "wrong";\nadd(1, 2);\n')
    original = (cwd / "example.ts").read_bytes()
    (cwd / ".pi/extensions").mkdir()
    (cwd / ".pi/extensions/unapproved.ts").write_text('throw new Error("AMBIENT_EXTENSION_LOADED");')
    (cwd / ".pi/AGENTS.md").write_text("AMBIENT_CONTEXT")
    (root / "no-network.cjs").write_text('''
globalThis.fetch = () => { throw new Error("NETWORK_FORBIDDEN"); };
for (const name of ["node:http", "node:https"]) {
  const transport = require(name);
  transport.request = transport.get = () => { throw new Error("NETWORK_FORBIDDEN"); };
}
''')
    # Intercept only registration to invoke exact vendor definitions with the real
    # Pi command context. No mocks for diagnostics/navigation or trust behavior.
    (root / "record-lens.ts").write_text(f'import lens from {json.dumps(str(Path(lens).resolve()))};\n' + '''
export default async function(pi) {
  const tools = new Map();
  const proxy = new Proxy(pi, { get(target, name) {
    if (name === "registerTool") return tool => { tools.set(tool.name, tool); target.registerTool(tool); };
    return target[name];
  }});
  await lens(proxy);
  pi.registerCommand("probe-lens", { handler: async (_, ctx) => {
    const call = (name, args) => tools.get(name).execute("fixture-" + name, args, AbortSignal.timeout(25000), undefined, ctx);
    const before = pi.getActiveTools();
    const diagnostics = await call("lsp_diagnostics", {path:"example.ts", serverScope:"primary", waitMs:15000});
    await call("pi_lens_activate_tools", {tools:["lsp_navigation"]});
    const navigation = await call("lsp_navigation", {operation:"definition", path:"example.ts", line:3, symbol:"add"});
    const all = await call("lens_diagnostics", {mode:"all"});
    pi.sendMessage({customType:"lens-fixture", display:true, content:JSON.stringify({
      trusted:ctx.isProjectTrusted(), mode:ctx.mode, before, after:pi.getActiveTools(),
      prompt:ctx.getSystemPrompt(), skills:ctx.getSystemPromptOptions().skills,
      diagnostics, navigation, all,
      state:[process.env.PI_LENS_HOME, process.env.PILENS_DATA_DIR, process.env.PI_LENS_CONFIG_PATH]
    })});
    ctx.shutdown();
  }});
}
''')
    skill = root / "skills/ponytail"
    skill.mkdir(parents=True)
    source_skill = Path.home() / ".bb/skills/ponytail/SKILL.md"
    (skill / "SKILL.md").write_bytes(source_skill.read_bytes())
    env = {
        "PATH": servers + ":" + os.environ["PATH"], "HOME": str(home),
        "XDG_CONFIG_HOME": str(home / ".config"), "PI_CODING_AGENT_DIR": str(agent),
        "PI_OFFLINE": "1", "PI_TELEMETRY": "0", "PI_SKIP_VERSION_CHECK": "1",
        "NPM_CONFIG_OFFLINE": "true",
        "NODE_OPTIONS": "--require=" + str(root / "no-network.cjs"),
    }
    flags = ["--mode", "rpc", "--no-session", "--no-extensions", "--no-skills",
             "--no-context-files", "--no-prompt-templates", "--no-themes", "--skill", str(skill)]
    for extension in extensions:
        flags += ["--extension", extension]
    with (root / "stderr.log").open("w+") as stderr:
        process = subprocess.Popen([sys.executable, str(profile / "launch.py"), pi,
                                    str(root / "record-lens.ts"), *flags], cwd=cwd, env=env,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
                                   text=True, start_new_session=True)
        assert process.stdin is not None and process.stdout is not None

        def stop_fixture():
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

        timer = threading.Timer(85, stop_fixture)
        timer.start()
        try:
            process.stdin.write('{"type":"prompt","message":"/probe-lens"}\n')
            process.stdin.flush()  # Keep RPC stdin open until ctx.shutdown().
            output = process.stdout.read()
            process.wait(timeout=5)
        finally:
            timer.cancel()
            stop_fixture()  # Also reap fixture-only LSP children if Pi failed.
            process.wait()
            process.stdin.close()
            process.stdout.close()
        stderr.seek(0)
        result = subprocess.CompletedProcess(process.args, process.returncode, output, stderr.read())
    messages = [json.loads(line) for line in result.stdout.split("\n") if line.startswith("{")]
    fixture = next((m["message"] for m in messages if m.get("type") == "message_end"
                    and m.get("message", {}).get("customType") == "lens-fixture"), None)
    assert fixture is not None, (result.returncode, result.stdout[-8000:], result.stderr[-4000:])
    data = json.loads(fixture["content"])
    assert data["trusted"] and data["mode"] == "rpc"
    assert "lens_diagnostics" in data["before"] and "lsp_diagnostics" in data["before"]
    assert "lsp_navigation" not in data["before"] and "lsp_navigation" in data["after"]
    assert {"read", "write", "edit", "bash"}.issubset(data["after"])
    if extensions:
        assert {"web_search", "source_check", "fetch_content", "get_search_content", "mcp", "mcpScript", "find", "grep"}.issubset(data["after"])
    assert "AMBIENT_CONTEXT" not in data["prompt"]
    assert "ponytail" in data["prompt"]
    assert [s["name"] for s in data["skills"]].count("ponytail") == 1
    assert all(s["name"] == "ponytail" or "pi-lens" in s["filePath"] for s in data["skills"]), data["skills"]
    assert all(path.startswith(str(agent / "lens")) for path in data["state"])
    assert any(str(d.get("code")) == "2322" for d in data["diagnostics"]["details"]["diagnostics"]), data["diagnostics"]
    assert data["navigation"]["details"].get("resultCount", 0) > 0, data["navigation"]
    assert data["all"]["details"].get("mode") == "all", data["all"]
    assert (cwd / "example.ts").read_bytes() == original
    assert not any(m.get("type") == "extension_error" for m in messages)
    assert "NETWORK_FORBIDDEN" not in result.stderr and "AMBIENT_EXTENSION_LOADED" not in result.stderr
    assert json.loads((agent / "auth.json").read_text()) == {}
    print("PASS: real Pi RPC + Lens tools; TS2322 diagnostic; definition navigation; lazy activation preserves built-ins; explicit Ponytail skill; isolated state; no model/auth/network or source edits")
