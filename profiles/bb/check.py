#!/usr/bin/env python3
"""No-auth launch check: python3 profiles/bb/check.py NIXOS_REPO PREPARED_RUNTIME.

PREPARED_RUNTIME contains packages/{account-router,codex-usage} and their locked
runtime dependencies. It is copied into disposable fixtures, never loaded live.
"""

import json
import os
import re
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

from launch import select_rpiv, tool_environment

profile = Path(__file__).resolve().parent
repo = Path(sys.argv[1]).resolve()
runtime = Path(sys.argv[2]).resolve()
assert (runtime / "packages/account-router/src/index.ts").is_file()
assert (runtime / "packages/codex-usage/extensions/codex-usage.ts").is_file()
settings = json.loads((profile / "settings.json").read_text())
assert settings == {
    "defaultProjectTrust": "never",
    "enableInstallTelemetry": False,
    "enableAnalytics": False,
    "defaultProvider": "openai-codex",
    "defaultModel": "gpt-6-astra",
    "defaultThinkingLevel": "high",
    "packages": [],
    "compaction": {"enabled": True, "reserveTokens": 100000},
}
# Evaluate only this module, not the dirty host/system configuration.
expression = f'''
let
  f = builtins.getFlake {json.dumps(str(repo))};
  pkgs = f.inputs.nixpkgs.legacyPackages.x86_64-linux;
  hm = f.inputs.home-manager.lib.homeManagerConfiguration {{
    inherit pkgs;
    modules = [ (builtins.toPath {json.dumps(str(repo / 'modules/home/bb.nix'))}) {{
      home.username = "bb-fixture";
      home.homeDirectory = "/home/bb-fixture";
      home.stateVersion = "26.05";
    }} ];
  }};
in hm.config
'''
result = subprocess.check_output([
    "nix", "eval", "--impure", "--json", "--no-update-lock-file", "--expr",
    f"({expression}).systemd.user.services.bb.Service",
], text=True)
service = json.loads(result)
env = dict(shlex.split(value)[0].split("=", 1) for value in service["Environment"])
flags = json.loads(env["BB_PI_BRIDGE_ARGS"])
assert flags[:7] == [
    "--no-extensions", "--no-skills", "--no-context-files",
    "--no-prompt-templates", "--no-themes", "--extension",
    "/home/bb-fixture/.pi/bb-agent/git/github.com/lmilojevicc/pi-zza/packages/account-router/src/index.ts",
]
extra_flags = flags[7:]
assert extra_flags == [part for entry in [
    ".pi/agent/npm/node_modules/pi-web-access/index.ts",
    ".pi/agent/npm/node_modules/pi-mcp-adapter/index.ts",
    ".pi/agent/npm/node_modules/@ff-labs/pi-fff/src/index.ts",
    ".pi/agent/git/github.com/lmilojevicc/pi-zza/packages/codex-native-compaction/extensions/codex-native-compaction.ts",
] for part in ["--extension", "/home/bb-fixture/" + entry]]
extra_flags = [value.replace("/home/bb-fixture/", str(Path.home()) + "/") for value in extra_flags]
flags = flags[:7]
assert env["PI_CODING_AGENT_DIR"] == "/home/bb-fixture/.pi/bb-agent"
assert env["PI_TELEMETRY"] == "0" and env["PI_SKIP_VERSION_CHECK"] == "1"
assert env["PI_OFFLINE"] == "1" and env["BB_TELEMETRY"] == "false"
assert set(service["UnsetEnvironment"]) == {
    "PI_ACCOUNT_ROUTER_AGENT_DIR", "PI_ACCOUNT_ROUTER_NAMESPACE",
}
assert service["UMask"] == "0077"
start = shlex.split(service["ExecStart"][0])
assert start[1:] == [
    "--data-dir=%h/.bb", "--server-bind-host=127.0.0.1",
    "--server-port=38886", "--host-daemon-port=38887",
]
# Realize just the launcher, not a system activation. check-lens.py separately
# exercises its Python trust selector; this regression retains the Router fixture.
subprocess.run([
    "nix", "build", "--impure", "--no-link", "--no-update-lock-file", "--expr",
    f'''let env = ({expression}).systemd.user.services.bb.Service.Environment;
    value = builtins.head (builtins.filter (x: builtins.match "BB_PI_BRIDGE_COMMAND=.*" x != null) env);
    in builtins.substring 21 (-1) value''',
], check=True)
launcher = Path(env["BB_PI_BRIDGE_COMMAND"])
match = re.search(r"(/nix/store/[^\s]+/bin/pi)\b", launcher.read_text())
assert match is not None
pi = Path(match.group(1))
assert str(pi).startswith("/nix/store/") and pi.is_file()
assert json.loads((pi.parent.parent / "lib/node_modules/pi-monorepo/package.json").read_text())["version"] == "0.85.1"
bb = Path(start[0]).parent.parent / "lib/bb-app/node_modules/bb-app"
host = (bb / "server/dist/builtin-plugins/provider-pi/dist/host.js").read_text()
# Extract the shipped bridge verbatim; changes to its packaging fail this receipt.
bridge = host.split("var BB_PI_EXTENSION_SOURCE = String.raw`", 1)[1].split("\n`;", 1)[0]
assert 'spawn(launch.command, [...launch.args, ...args.args]' in host
assert '"--extension",\n      this.options.extensionPath' in host
policy_path = profile / "AGENTS.md"
assert policy_path.is_symlink() and os.readlink(policy_path) == "../../agent/AGENTS.md"
policy = policy_path.read_text()
assert policy == (profile / "../../agent/AGENTS.md").read_text()
assert "You are the parent/orchestrator session." in policy
assert all(model in policy for model in [
    "antigravity/gemini-3.8-flash", "openai-codex/gpt-5.6-luna",
    "openai-codex/gpt-5.6-sol", "openai-codex/gpt-6-astra",
])
assert "Write all user-facing responses in ASD-STE100 Simplified Technical English." in policy

with tempfile.TemporaryDirectory(prefix="bb-router-check-") as temp:
    root = Path(temp)
    home, agent, cwd = root / "home", root / "agent", root / "workspace"
    for directory in [home, agent, cwd / ".pi"]:
        directory.mkdir(parents=True)
    (agent / "settings.json").write_text(json.dumps(settings))
    prepared = root / "runtime"
    shutil.copytree(runtime, prepared, symlinks=True)
    flags[-1] = str(prepared / "packages/account-router/src/index.ts")
    # A throwing network sentinel also applies to the child Pi process.
    (root / "no-network.cjs").write_text('''
globalThis.fetch = () => { throw new Error("NETWORK_FORBIDDEN"); };
for (const name of ["node:http", "node:https"]) {
  const transport = require(name);
  transport.request = transport.get = () => { throw new Error("NETWORK_FORBIDDEN"); };
}
''')
    # Ambient resources fail loudly if selected. Project trust must stay denied.
    for directory in [agent, cwd / ".pi", home / ".pi/agent"]:
        (directory / "extensions").mkdir(parents=True)
        (directory / "extensions/unapproved.ts").write_text(
            'throw new Error("AMBIENT_EXTENSION_LOADED"); export default () => {};'
        )
        (directory / "skills/unapproved").mkdir(parents=True)
        (directory / "skills/unapproved/SKILL.md").write_text(
            "---\nname: unapproved\ndescription: fixture\n---\nAMBIENT_SKILL\n"
        )
        (directory / "AGENTS.md").write_text("AMBIENT_CONTEXT")
        (directory / "prompts").mkdir()
        (directory / "prompts/unapproved.md").write_text("AMBIENT_PROMPT")
    (cwd / ".pi/settings.json").write_text('{"defaultProvider":"unapproved"}')
    (cwd / ".pi/SYSTEM.md").write_text("UNTRUSTED_SYSTEM_PROMPT")
    (cwd / ".pi/APPEND_SYSTEM.md").write_text("UNTRUSTED_APPEND_PROMPT")
    (root / "bridge.ts").write_text(bridge)
    (root / "policy.md").write_text(policy)
    (root / "tools.json").write_text(json.dumps([{
        "name": "bb_fixture", "description": "Fixture BB tool",
        "inputSchema": {"type": "object", "properties": {}},
    }]))
    # An explicit test-only command observes the prompt and tools without a model.
    # Capture hook registration while running the actual compaction factory.
    (root / "compaction.ts").write_text('import compaction from ' + json.dumps(extra_flags[-1]) + ';\n' + '''
export default function(pi) {
  globalThis.bbCompactionHooks = [];
  compaction(new Proxy(pi, { get(target, key) {
    if (key === "on") return (event, handler) => { globalThis.bbCompactionHooks.push(event); return target.on(event, handler); };
    return target[key];
  }}));
}
''')
    (root / "inspect.ts").write_text('''
export default function (pi) {
  pi.registerCommand("inspect-fixture", { handler: async (_, ctx) => {
    const options = ctx.getSystemPromptOptions();
    pi.sendMessage({ customType: "fixture", display: false, content: JSON.stringify({
      node: process.versions.node, tools: pi.getActiveTools(), context: options.contextFiles,
      skills: options.skills, prompt: ctx.getSystemPrompt(), trusted: ctx.isProjectTrusted(),
      compactionHooks: globalThis.bbCompactionHooks ?? []
    }) });
  } });
}
''')
    # Use a fresh allowlisted environment: no provider credentials, inherited Pi
    # profile, cloud configuration, or user Node preload hooks enter the probe.
    probe_env = {
        "PATH": os.environ["PATH"], "HOME": str(home),
        "XDG_CONFIG_HOME": str(home / ".config"),
        "PI_CODING_AGENT_DIR": str(agent), "PI_OFFLINE": "1", "PI_TELEMETRY": "0",
        "PI_SKIP_VERSION_CHECK": "1", "PI_BB_TOOLS_FILE": str(root / "tools.json"),
        "NODE_OPTIONS": "--require=" + str(root / "no-network.cjs"),
    }
    probe_env.update(tool_environment(agent))
    (agent / "web-search.json").write_text('{"workflow":"none","allowBrowserCookies":false}')
    (agent / "mcp.json").write_text('{"mcpServers":{}}')
    runner = r'''
const { spawn } = require("node:child_process");
const assert = require("node:assert/strict");
const [pi, root, cwd, flagsJSON, withUsage] = process.argv.slice(1);
assert.equal(process.versions.node.split(".")[0], "22");
const flags = JSON.parse(flagsJSON);
const child = spawn(pi, [...flags, "--mode", "rpc", "--no-session",
  "--session-dir", root + "/sessions", "--extension", root + "/bridge.ts",
  "--extension", root + "/inspect.ts", "--append-system-prompt", root + "/policy.md"],
  { cwd, stdio: ["pipe", "pipe", "pipe", "pipe", "pipe"] });
process.on("exit", () => child.kill("SIGKILL"));
let stderr = "", ready = false, inspected = false, bash = false, commands = false;
const timer = setTimeout(() => { child.kill("SIGKILL"); process.exitCode = 1; }, 20000);
child.stderr.on("data", chunk => { stderr += chunk; });
function lines(stream, handle) {
  let pending = "";
  stream.setEncoding("utf8");
  stream.on("data", chunk => {
    pending += chunk;
    let index;
    while ((index = pending.indexOf("\n")) !== -1) {
      const line = pending.slice(0, index); pending = pending.slice(index + 1);
      if (line.trim()) handle(JSON.parse(line));
    }
  });
}
function send(value) { child.stdin.write(JSON.stringify(value) + "\n"); }
function finish() { if (ready && inspected && bash && commands) child.kill("SIGTERM"); }
lines(child.stdio[3], event => {
  if (event.kind === "ready") { ready = true; finish(); }
});
lines(child.stdout, event => {
  assert.notEqual(event.type, "extension_error");
  if (event.type === "message_end" && event.message.customType === "fixture") {
    const data = JSON.parse(event.message.content);
    // Native Pi remains Nix-managed; its wrapper selects Node 24, not BB's Node 22.
    assert.equal(data.node, "24.19.0");
    const expectedTools = ["bash", "bb_fixture", "edit", "read", "write"];
    if (withUsage === "tools") {
      expectedTools.push("web_search", "source_check", "fetch_content", "get_search_content", "mcp", "mcpScript", "find", "grep", "todo");
      assert.ok(data.compactionHooks.includes("session_before_compact"));
      assert.ok(data.compactionHooks.includes("before_provider_request"));
    }
    assert.deepEqual([...data.tools].sort(), expectedTools.sort());
    assert.equal(data.trusted, false);
    assert.equal((data.context ?? []).length, 0);
    assert.equal((data.skills ?? []).length, 0);
    assert.ok(data.prompt.includes("You are the parent/orchestrator session."));
    assert.ok(data.prompt.includes("openai-codex/gpt-6-astra"));
    assert.ok(data.prompt.includes("Simplified Technical English"));
    assert.ok(!data.prompt.includes("AMBIENT_") && !data.prompt.includes("UNTRUSTED_"));
    inspected = true; finish();
  }
  if (event.type === "response") {
    assert.equal(event.success, true);
    if (event.command === "get_commands") {
      // Pi 0.85.1 always includes its hidden built-in llama.cpp command.
      const expected = ["account-router", "inspect-fixture", "llama"];
      if (withUsage === "yes") expected.push("usage", "codex-usage");
      const names = event.data.commands.map(command => command.name);
      assert.equal(new Set(names).size, names.length);
      if (withUsage === "tools") {
        for (const name of [...expected, "mcp", "fff-health", "curator", "todos"]) assert.ok(names.includes(name));
      } else assert.deepEqual(names.sort(), expected.sort());
      commands = true; finish();
    }
    if (event.command === "bash") {
      assert.equal(event.data.output.trim(), "bare-profile-ok");
      assert.equal(event.data.exitCode, 0); bash = true; finish();
    }
  }
});
child.on("exit", () => {
  clearTimeout(timer);
  assert.ok(ready && inspected && bash && commands, "RPC probe incomplete: " + stderr);
  assert.ok(!stderr.includes("AMBIENT_EXTENSION_LOADED"));
  assert.ok(!stderr.includes("NETWORK_FORBIDDEN"));
  console.log("PASS: Router" + (withUsage === "yes" ? "+Usage" : withUsage === "tools" ? "+Web/MCP/FFF/RPIV Todo/compaction" : "") + ", BB bridge ready, built-ins + BB tool, policy delivered, ambient resources excluded");
});
send({type:"get_commands"});
send({type:"prompt", message:"/inspect-fixture"});
send({type:"bash", command:"printf bare-profile-ok"});
'''
    for mode in ["no", "yes", "tools"]:
        selected = [*flags, "--no-approve"]
        if mode == "tools":
            selected += [*extra_flags[:-1], str(root / "compaction.ts")]
            selected = select_rpiv(selected, Path.home() / ".pi/bb-agent")
        if mode == "yes":
            selected += ["--extension", str(prepared / "packages/codex-usage/extensions/codex-usage.ts")]
        subprocess.run([
            "node", "-e", runner, str(pi), str(root), str(cwd), json.dumps(selected),
            mode,
        ], env=probe_env, check=True, timeout=30)
        assert json.loads((agent / "auth.json").read_text()) == {}

print("PASS: explicit Router service selection, Router+Usage, Web/MCP/FFF/compaction, launcher-selected RPIV Todo, isolated no-auth RPC")
print("Pi:", pi.parent.parent.name, "native Node: 24.19.0; BB/fixture Node: 22.23.2; BB:", json.loads((bb / "package.json").read_text())["version"])
