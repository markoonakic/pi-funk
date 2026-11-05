#!/usr/bin/env python3
"""Native MCP + Code Mode check with a local model stub. Usage: check-mcp.py PI."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

pi = sys.argv[1]
with tempfile.TemporaryDirectory(prefix="pi-native-mcp-check-") as tmp:
    root = Path(tmp)
    agent, project, home = root / "agent", root / "project", root / "home"
    for directory in (agent, project / ".pi", home):
        directory.mkdir(parents=True)
    (agent / "settings.json").write_text(json.dumps({
        "packages": [], "defaultProjectTrust": "never", "defaultTools": ["+codemode"],
        "enableInstallTelemetry": False, "enableAnalytics": False,
    }))
    (agent / "mcp.json").write_text('{"mcpServers":{}}')
    (agent / "trust.json").write_text(json.dumps({str(project.resolve()): True}))
    (project / ".pi/mcp.json").write_text(json.dumps({"mcpServers": {
        "fixture": {"command": sys.executable, "args": [str(root / "server.py")],
                    "exposure": "codemode"},
    }}))
    (project / ".pi/extensions").mkdir()
    (project / ".pi/extensions/unapproved.ts").write_text('throw new Error("AMBIENT_EXTENSION_LOADED");')
    (root / "server.py").write_text('''import json, sys
for line in sys.stdin:
    request = json.loads(line)
    if "id" not in request:
        continue
    method = request["method"]
    if method == "initialize":
        result = {"protocolVersion": request["params"]["protocolVersion"],
                  "capabilities": {"tools": {}}, "serverInfo": {"name": "fixture", "version": "1"}}
    elif method == "tools/list":
        result = {"tools": [{"name": "echo", "description": "Return a fixture value.",
                  "inputSchema": {"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]},
                  "annotations": {"readOnlyHint": True, "destructiveHint": False}}]}
    elif method == "tools/call":
        result = {"content": [{"type": "text", "text": request["params"]["arguments"]["value"]}]}
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": result}), flush=True)
''')
    (root / "model.ts").write_text('''import { createAssistantMessageEventStream } from "@earendil-works/pi-ai";
export default function(pi) {
  let calls = 0;
  pi.registerProvider("native-mcp-fixture", {
    api: "native-mcp-fixture", baseUrl: "https://127.0.0.1:1", apiKey: "fixture-not-a-secret",
    models: [{id: "fixture", name: "Fixture", reasoning: false, input: ["text"],
              cost: {input: 0, output: 0, cacheRead: 0, cacheWrite: 0}, contextWindow: 128000, maxTokens: 1000}],
    streamSimple(model, context) {
      const stream = createAssistantMessageEventStream();
      const message = {role: "assistant", api: model.api, provider: model.provider, model: model.id,
        timestamp: Date.now(), content: [], stopReason: "pending",
        usage: {input: 0, output: 0, cacheRead: 0, cacheWrite: 0, totalTokens: 0,
                cost: {input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0}}};
      stream.push({type: "start", partial: message});
      if (calls++ === 0) {
        const tool = {type: "toolCall", id: "native-fixture-call", name: "codemode", arguments: {
          code: 'const matches = await searchTools("echo", {namespace: "mcp__fixture"}); if (!matches.some(x => x.name === "mcp__fixture__echo")) throw Error("MCP discovery failed"); if (ALL_TOOLS.some(x => ["mcp", "mcpScript"].includes(x.name))) throw Error("Legacy tool loaded"); const result = await tools.mcp__fixture__echo({value: "native-mcp-ok"}); if (result.isError) throw Error("MCP call failed"); text(result);'
        }};
        message.content.push(tool);
        stream.push({type: "toolcall_start", contentIndex: 0, partial: message});
        stream.push({type: "toolcall_end", contentIndex: 0, toolCall: tool, partial: message});
        message.stopReason = "toolUse";
      } else {
        const good = context.messages.some(x => x.role === "toolResult" && x.toolName === "codemode" && !x.isError && JSON.stringify(x.content).includes("native-mcp-ok"));
        message.content.push({type: "text", text: good ? "NATIVE_MCP_PASS" : "NATIVE_MCP_FAIL"});
        stream.push({type: "text_start", contentIndex: 0, partial: message});
        stream.push({type: "text_end", contentIndex: 0, content: message.content[0].text, partial: message});
        message.stopReason = "stop";
      }
      stream.push({type: "done", reason: message.stopReason, message});
      stream.end();
      return stream;
    },
  });
}
''')
    (root / "no-network.cjs").write_text('''globalThis.fetch = () => { throw new Error("NETWORK_FORBIDDEN"); };
for (const name of ["node:http", "node:https"]) {
  const transport = require(name);
  transport.request = transport.get = () => { throw new Error("NETWORK_FORBIDDEN"); };
}
''')
    env = {
        "PATH": os.environ["PATH"], "HOME": str(home), "XDG_CONFIG_HOME": str(home / ".config"),
        "PI_CODING_AGENT_DIR": str(agent), "PI_OFFLINE": "1", "PI_TELEMETRY": "0",
        "PI_SKIP_VERSION_CHECK": "1", "NPM_CONFIG_OFFLINE": "true",
        "NODE_OPTIONS": "--require=" + str(root / "no-network.cjs"),
    }
    flags = ["--mode", "json", "--print", "--no-session", "--no-extensions", "--no-skills",
             "--no-context-files", "--no-prompt-templates", "--no-themes",
             "--extension", "builtin:mcp", "--extension", "builtin:codemode",
             "--extension", str(root / "model.ts"), "--model", "native-mcp-fixture/fixture", "Check the fixture."]
    try:
        result = subprocess.run([pi, *flags], cwd=project, env=env, input="", capture_output=True, text=True, timeout=45)
    except subprocess.TimeoutExpired as error:
        raise AssertionError((error.stdout[-10000:] if error.stdout else b"", error.stderr[-3000:] if error.stderr else b"")) from error
    assert result.returncode == 0, (result.stdout[-5000:], result.stderr[-3000:])
    messages = [json.loads(line) for line in result.stdout.splitlines() if line.startswith("{")]
    completed = [x.get("message", {}) for x in messages if x.get("type") == "message_end"]
    assert any(x.get("role") == "assistant" and "NATIVE_MCP_PASS" in json.dumps(x.get("content")) for x in completed), result.stdout[-8000:]
    assert any(x.get("role") == "toolResult" and x.get("toolName") == "codemode" and not x.get("isError") for x in completed), completed
    assert not any(x.get("type") == "extension_error" for x in messages), messages
    assert "NETWORK_FORBIDDEN" not in result.stderr and "AMBIENT_EXTENSION_LOADED" not in result.stderr, result.stderr
    assert not (agent / "mcp-auth.json").exists()
    print("PASS: native MCP stdio connection, namespace discovery, real Code Mode tool call, saved trust, no legacy tools, no real credentials or external model/network, ambient extensions blocked")
