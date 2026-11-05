#!/usr/bin/env python3
"""Credential-free target check: PI NPM_NODE_MODULES SUBAGENTS_DIR [EXTRA_ENTRY...].

Uses the real CLI, extension factories, public subagent tool and foreground/
background SDK lifecycles. Only the model is a deterministic local faux provider.
Package code is read-only; all settings, auth, sessions and artifacts are temporary.
Set PI_TEST_ARTIFACTS to retain evidence outside source; run before activation.
"""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile

pi, modules, subagents, *extras = sys.argv[1:]
modules, subagents = Path(modules).resolve(), Path(subagents).resolve()
out = Path(os.environ.get("PI_TEST_ARTIFACTS", tempfile.gettempdir()))
out.mkdir(parents=True, exist_ok=True)
root = Path(tempfile.mkdtemp(prefix="target-extension-check-", dir=out))
agent, home, project = root / "agent", root / "home", root / "project"
for p in (agent / "extensions/subagent", home, project / ".pi/agents"):
    p.mkdir(parents=True)
settings = {"packages": [], "defaultProvider": "qualification", "defaultModel": "local",
            "defaultProjectTrust": "never", "enableAnalytics": False, "enableInstallTelemetry": False,
            "compaction": {"enabled": False}, "retry": {"enabled": False}}
(agent / "settings.json").write_text(json.dumps(settings))
(agent / "mcp.json").write_text('{"mcpServers":{}}')
(agent / "web-search.json").write_text('{"workflow":"none","allowBrowserCookies":false}')
(agent / "extensions/subagent/config.json").write_text('{"toolActivation":"eager"}')
(agent / "auth.json").write_text('{}')
(root / "no-network.cjs").write_text('''
globalThis.fetch = () => { throw new Error("NETWORK_FORBIDDEN"); };
for (const name of ["node:http", "node:https"]) {
  const transport = require(name);
  transport.request = transport.get = () => { throw new Error("NETWORK_FORBIDDEN"); };
}
''')
provider = root / "provider.ts"
provider.write_text('''import fs from "node:fs";
import { fauxProvider, fauxAssistantMessage } from "@earendil-works/pi-ai";
import { getPackageDir, SessionManager } from "@earendil-works/pi-coding-agent";
const log = (data) => fs.appendFileSync(process.env.PI_TEST_LIFECYCLE, JSON.stringify({ ...data, pid:process.pid, node:process.version, packageDir:getPackageDir() }) + "\\n");
export default function(pi) {
  const faux = fauxProvider({provider:"qualification", models:[{id:"local"}], tokensPerSecond:100000});
  faux.setResponses([async (context) => {
    const text = JSON.stringify(context.messages);
    const label = text.includes("BACKGROUND_MARKER") ? "BACKGROUND_MARKER" : text.includes("FOREGROUND_MARKER") ? "FOREGROUND_MARKER" : "CUSTOM_MARKER";
    log({event:"request", label});
    return fauxAssistantMessage("QUALIFICATION_OK " + label);
  }]);
  pi.registerProvider(faux.provider);
  pi.on("session_start", (_event, ctx) => log({event:"start", sessionId:ctx.sessionManager.getSessionId(), sdkIdentity:ctx.sessionManager instanceof SessionManager}));
  pi.on("session_shutdown", (_event, ctx) => log({event:"shutdown", sessionId:ctx.sessionManager.getSessionId(), calls:faux.state.callCount}));
}
''')
(project / ".pi/agents/qualification.md").write_text(f'''---
name: qualification
description: Credential-free deterministic runtime qualification
model: qualification/local
tools:
extensions:
  - {provider}
---
Return the deterministic fixture response.
''')
harness = root / "harness.ts"
harness.write_text('import subagents from ' + json.dumps(str(subagents / "index.ts")) + ';\n'
    + 'import goal from ' + json.dumps(str(modules / "pi-codex-goal/extensions/index.ts")) + ';\n' + '''
import assert from "node:assert/strict";
import fs from "node:fs";
const dir = process.env.PI_TEST_RESULT_DIR;
const write = (name,data) => fs.writeFileSync(dir + "/" + name + ".json", JSON.stringify(data,null,2));
function until(file, predicate) {
  return new Promise(resolve => {
    const check = () => { if (fs.existsSync(file) && predicate(JSON.parse(fs.readFileSync(file,"utf8")))) { fs.unwatchFile(file, check); resolve(); } };
    fs.watchFile(file,{interval:25},check); check();
  });
}
export default async function(pi) {
  const tools = new Map();
  let delivered;
  const notification = new Promise(resolve => { delivered = resolve; });
  // Record public registration only. Runtime/tool/session/runner code is unmodified.
  const host = new Proxy(pi,{ get(target,key) {
    if (key === "registerTool") return definition => { tools.set(definition.name,definition); return target.registerTool(definition); };
    if (key === "sendMessage") return (message,options) => {
      // A completion must be observed, but must not start a second parent model loop.
      if (message.customType === "subagent-notify") { delivered(message); return target.sendMessage(message,{...options,triggerTurn:false}); }
      return target.sendMessage(message,options);
    };
    return Reflect.get(target,key);
  }});
  await subagents(host);
  await goal(host);
  pi.on("session_start",()=>{
    const names=pi.getAllTools().map(x=>x.name); write("registered-tools",names);
    for(const name of JSON.parse(process.env.PI_TEST_EXPECT_TOOLS)) assert.ok(names.includes(name),"Missing actual tool: "+name);
  });
  pi.on("before_agent_start", event => {
    if (event.messageType === "custom") write("custom-start",{messageType:event.messageType,hasPrompt:Object.hasOwn(event,"prompt")});
  });
  pi.on("agent_settled",()=>{ if(fs.existsSync(dir+"/custom-start.json")) write("custom-settled",{settled:true}); });
  pi.registerCommand("qualify-goal",{handler:async(_,ctx)=>{
    const call=(name,args)=>tools.get(name).execute("qualification-"+name,args,AbortSignal.timeout(30000),undefined,ctx);
    write("goal-created",await call("create_goal",{objective:"Credential-free custom-message check"}));
    write("goal-blocked",await call("update_goal",{status:"blocked",reason:"Deterministic fixture stops automatic continuation"}));
    pi.sendMessage({customType:"qualification-start",content:"CUSTOM_MARKER",display:false},{triggerTurn:true});
  }});
  pi.registerCommand("qualify-subagents",{handler:async(_,ctx)=>{
    const tool=tools.get("subagent"); assert.ok(tool,"real subagent tool registered");
    const common={agent:"qualification",model:"qualification/local",output:false,options:{context:"fresh",acceptance:false,timeoutMs:45000}};
    const foreground=await tool.execute("qualification-foreground",{...common,task:"FOREGROUND_MARKER",async:false},AbortSignal.timeout(65000),undefined,ctx);
    write("foreground",foreground);
    assert.notEqual(foreground.isError,true,JSON.stringify(foreground));
    assert.match(JSON.stringify(foreground),/QUALIFICATION_OK FOREGROUND_MARKER/);
    const launch=await tool.execute("qualification-background",{...common,task:"BACKGROUND_MARKER",async:true},AbortSignal.timeout(65000),undefined,ctx);
    write("background-launch",launch); assert.notEqual(launch.isError,true,JSON.stringify(launch));
    const completed=await notification;
    write("background-notification",completed);
    assert.match(JSON.stringify(completed),/QUALIFICATION_OK BACKGROUND_MARKER/);
    const terminalPath=launch.details.asyncDir+"/process-terminal.json";
    await until(terminalPath,x=>x.state==="observed");
    const terminal=JSON.parse(fs.readFileSync(terminalPath,"utf8")); write("background-terminal",terminal);
    assert.ok(terminal.instances.some(x=>x.kind==="runner" && x.exitCode===0),JSON.stringify(terminal));
    const status=JSON.parse(fs.readFileSync(launch.details.asyncDir+"/status.json","utf8")); write("background-status",status);
    assert.equal(status.state,"complete");
    assert.throws(()=>process.kill(status.pid,0),{code:"ESRCH"});
    write("subagents-passed",{foreground:true,background:true,notification:true,runnerClosed:true});
    pi.sendMessage({customType:"qualification-pass",content:"TARGET_EXTENSIONS_PASS",display:true});
    ctx.shutdown();
  }});
}
''')
flags = ["--mode", "rpc", "--no-session", "--no-extensions", "--no-skills", "--no-context-files",
         "--no-prompt-templates", "--no-themes", "--approve", "-e", str(provider), "-e", str(harness)]
for entry in extras:
    flags += ["-e", entry]
expected_tools = ["subagent", "create_goal", "get_goal", "update_goal"]
if any("pi-lens" in entry for entry in extras):
    flags += ["--no-autoformat", "--no-autofix", "--no-tests"]
    expected_tools += ["lens_diagnostics", "lsp_navigation"]
if any("pi-web-access" in entry for entry in extras):
    expected_tools += ["web_search", "fetch_content", "source_check", "get_search_content"]
if any("pi-processes" in entry for entry in extras):
    expected_tools += ["process"]
if "builtin:codemode" in extras:
    expected_tools += ["codemode"]
env = {"PATH": str(Path(pi).parent) + ":" + os.environ["PATH"], "HOME":str(home),
       "XDG_CONFIG_HOME":str(home/".config"), "PI_CODING_AGENT_DIR":str(agent),
       "PI_TELEMETRY":"0", "PI_SKIP_VERSION_CHECK":"1", "PI_OFFLINE":"1", "NPM_CONFIG_OFFLINE":"true",
       "NODE_OPTIONS":"--require="+str(root/"no-network.cjs"), "JITI_FS_CACHE":"false",
       "PI_TEST_LIFECYCLE":str(root/"lifecycle.jsonl"), "PI_TEST_RESULT_DIR":str(root),
       "PI_TEST_EXPECT_TOOLS":json.dumps(expected_tools),
       "PI_FFF_MODE":"override", "FFF_FRECENCY_DB":str(agent/"fff/frecency"), "FFF_HISTORY_DB":str(agent/"fff/history"),
       "PI_LENS_HOME":str(agent/"lens"), "PILENS_DATA_DIR":str(agent/"lens/projects"),
       "PI_LENS_CONFIG_PATH":str(agent/"lens/config.json"), "PI_LENS_DISABLE_LSP_INSTALL":"1",
       "PI_LENS_DISABLE_TOOL_INSTALL":"1", "PI_LENS_AUTO_INSTALL":"0"}
print("ARTIFACTS",root,flush=True)
import queue
import threading
records = queue.Queue()
with (root/"stderr.log").open("w+") as stderr, (root/"stdout.jsonl").open("w") as stdout:
    process = subprocess.Popen([pi,*flags],cwd=project,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,text=True,start_new_session=True)
    def read_events():
        for line in process.stdout:
            stdout.write(line); stdout.flush()
            if line.startswith("{"):
                records.put(json.loads(line))
        records.put({"type":"fixture-eof"})
    thread=threading.Thread(target=read_events,daemon=True); thread.start()
    def send(command):
        process.stdin.write(json.dumps(command)+"\n"); process.stdin.flush()
    def wait(predicate, timeout=120):
        import time
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            event=records.get(timeout=max(.1,deadline-time.monotonic()))
            assert event.get("type") != "extension_error",event
            assert event.get("type") != "fixture-eof",("Unexpected Pi exit",process.poll())
            if event.get("type")=="response":
                assert event.get("success"),event
            if predicate(event): return event
        raise TimeoutError("Fixture did not finish")
    try:
        # Uncached extension compilation needs its own startup budget; later calls keep 120s.
        send({"id":"state","type":"get_state"}); wait(lambda x:x.get("id")=="state", timeout=300)
        send({"id":"goal","type":"prompt","message":"/qualify-goal"})
        wait(lambda x:x.get("type")=="agent_settled")
        assert json.loads((root/"custom-start.json").read_text())=={"messageType":"custom","hasPrompt":False}
        assert json.loads((root/"custom-settled.json").read_text())["settled"]
        send({"id":"children","type":"prompt","message":"/qualify-subagents"})
        wait(lambda x:x.get("type")=="message_end" and x.get("message",{}).get("customType")=="qualification-pass")
        process.stdin.close(); process.wait(timeout=15); thread.join(timeout=2)
        assert process.returncode==0,process.returncode
        lifecycle=[json.loads(line) for line in (root/"lifecycle.jsonl").read_text().splitlines()]
        assert all(x["node"].startswith("v24.") for x in lifecycle),lifecycle
        assert all(str(Path(pi).parents[1]) in x["packageDir"] for x in lifecycle),lifecycle
        assert all(x.get("sdkIdentity",True) for x in lifecycle),lifecycle
        assert {x.get("label") for x in lifecycle if x["event"]=="request"}=={"CUSTOM_MARKER","FOREGROUND_MARKER","BACKGROUND_MARKER"},lifecycle
        assert len({x["pid"] for x in lifecycle})==2,lifecycle
        started = {x["sessionId"] for x in lifecycle if x["event"] == "start"}
        stopped = {x["sessionId"] for x in lifecycle if x["event"] == "shutdown" and x["calls"] == 1}
        assert len(started) == 3 and started == stopped, lifecycle
        assert json.loads((agent/"auth.json").read_text())=={}
        stderr.seek(0); errors=stderr.read()
        assert "NETWORK_FORBIDDEN" not in errors,errors
        assert "Failed to load extension" not in errors,errors
        print("PASS: actual target Goal custom-message run; real foreground/background Subagents; shared candidate SDK and Node24 identity; notification and observed runner exit; no network or credentials")
    finally:
        try: os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError: pass
        process.wait()
        thread.join(timeout=2)
        if not process.stdin.closed: process.stdin.close()
        process.stdout.close()
