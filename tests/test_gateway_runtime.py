"""Real Pi RPC checks with fake keys and a private cached catalog; no model calls.
Run: python3 -m unittest discover -s tests -p test_gateway_runtime.py
Requires the installed Pi CLI. Skips when it is unavailable.
"""
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading
import time
import unittest

ENTRY = Path(__file__).resolve().parents[1] / "extensions/cliproxy-models/index.ts"
PI = shutil.which("pi")


@unittest.skipUnless(PI, "Pi CLI is required for native runtime checks")
class GatewayRuntimeTest(unittest.TestCase):
    def test_native_providers_overrides_exclusions_refresh_and_no_secret_cache(self):
        repo = ENTRY.parents[2]
        terra_id = "gpt-6.1-terra"
        terra = json.loads((repo / "models.json").read_text())["providers"]["openai-codex"]["modelOverrides"][terra_id]
        self.assertEqual(terra, {
            "name": "GPT-6.1 Terra", "reasoning": True, "input": ["text", "image"],
            "thinkingLevelMap": {"off": "none", "minimal": "low", "low": "low",
                                 "medium": "medium", "high": "high", "xhigh": "xhigh", "max": "max"},
            "contextWindow": 1000000, "maxTokens": 128000,
        })
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = "https://127.0.0.1:1/v1"  # fetch rejects this unsafe port; no remote access
            config = {
                "providers": {
                    "cliproxy": {"baseUrl": base, "api": "openai-responses", "models": [
                        {"id": "meta/muse-spark-1.3-contributor", "name": "Old manual Muse entry"}
                    ]},
                    "openai-codex": {"baseUrl": base, "modelOverrides": {
                        "gpt-6-astra": {"contextWindow": 1000000, "maxTokens": 128000},
                        terra_id: terra,
                    }},
                }
            }
            (root / "models.json").write_text(json.dumps(config))
            (root / "settings.json").write_text(json.dumps({"packages": [], "defaultProvider": "openai-codex", "defaultModel": "gpt-6-astra"}))
            (root / "cliproxy-api-key").write_text("fake-gateway-key-for-test")
            catalog = {
                "baseUrl": base, "observedAt": int(time.time() * 1000),
                "data": [
                    {"id": "gpt-6-astra", "owned_by": "openai"},
                    {"id": terra_id, "owned_by": "openai"},
                    {"id": "gemini-3.8-flash-high", "owned_by": "antigravity"},
                    {"id": "go/glm-5.3-flash", "owned_by": "opencode-go"},
                    {"id": "z-ai/glm-5.3-flash", "owned_by": ""},
                    {"id": "meta/muse-spark-1.3-contributor", "owned_by": ""},
                    {"id": "go/muse-spark-1.3-contributor", "owned_by": "opencode-go"},
                    {"id": "gpt-image-2.5", "owned_by": "openai"},
                ],
            }
            cache = root / "cliproxy-model-catalog.json"
            cache.write_text(json.dumps(catalog))
            original_config = (root / "models.json").read_bytes()
            env = {"PATH": os.environ.get("PATH", ""), "HOME": directory,
                   "PI_CODING_AGENT_DIR": directory, "PI_OFFLINE": "1",
                   "PI_SKIP_VERSION_CHECK": "1", "PI_TELEMETRY": "0"}
            process = subprocess.Popen([
                PI, "--mode", "rpc", "--no-session", "--no-extensions", "--no-skills",
                "--no-context-files", "--no-prompt-templates", "--no-themes", "--no-approve",
                "-e", str(ENTRY),
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, env=env, cwd=directory)
            responses = queue.Queue()

            def collect():
                for line in process.stdout:
                    try:
                        responses.put(json.loads(line))
                    except ValueError:
                        pass

            thread = threading.Thread(target=collect, daemon=True)
            thread.start()

            def rpc(payload):
                process.stdin.write(json.dumps(payload) + "\n")
                process.stdin.flush()
                deadline = time.monotonic() + 45
                while time.monotonic() < deadline:
                    try:
                        response = responses.get(timeout=0.5)
                    except queue.Empty:
                        if process.poll() is not None:
                            self.fail("Pi exited before the test response: " + process.stderr.read()[:2000])
                        continue
                    if response.get("id") == payload["id"]:
                        self.assertTrue(response.get("success"), response)
                        return response
                self.fail("Pi RPC response timed out")

            try:
                result = rpc({"id": "models", "type": "get_available_models"})
                ids = {"openai-codex", "antigravity", "cliproxy-go", "cliproxy"}
                models = [m for m in result["data"]["models"] if m["provider"] in ids]
                self.assertEqual(len(models), 7)
                self.assertEqual(sum("muse-spark" in m["id"] for m in models), 2)
                indexed = {m["provider"]: m for m in models if "muse-spark" not in m["id"] and m["id"] != terra_id}
                for provider in ids:
                    self.assertNotIn(" · ", indexed[provider]["name"])
                    self.assertEqual(indexed[provider]["baseUrl"], base)
                self.assertEqual(indexed["cliproxy"]["name"], "GLM 5.3 Flash")
                self.assertEqual(indexed["antigravity"]["name"], "Gemini 3.8 Flash")
                self.assertNotEqual(indexed["cliproxy"]["id"], indexed["cliproxy-go"]["id"])
                self.assertEqual(indexed["openai-codex"]["contextWindow"], 1000000)
                self.assertEqual(indexed["openai-codex"]["maxTokens"], 128000)
                self.assertEqual(indexed["antigravity"]["contextWindow"], 1048576)
                self.assertEqual(indexed["cliproxy"]["thinkingLevelMap"]["medium"], "high")
                self.assertTrue(indexed["cliproxy-go"]["reasoning"])
                self.assertNotIn("fake-gateway-key-for-test", json.dumps(result))
                terra_model = next(m for m in models if m["provider"] == "openai-codex" and m["id"] == terra_id)
                self.assertEqual({key: terra_model[key] for key in terra}, terra)
                rpc({"id": "select-terra", "type": "set_model", "provider": "openai-codex", "modelId": terra_id})
                levels = list(terra["thinkingLevelMap"])
                available = rpc({"id": "terra-levels", "type": "get_available_thinking_levels"})
                self.assertEqual(available["data"]["levels"], levels)
                for level in levels:
                    rpc({"id": "set-" + level, "type": "set_thinking_level", "level": level})
                    state = rpc({"id": "state-" + level, "type": "get_state"})
                    self.assertEqual(state["data"]["thinkingLevel"], level)

                commands = rpc({"id": "commands", "type": "get_commands"})
                self.assertIn("gateway-models-refresh", json.dumps(commands))
                # Extension command only; it is handled before the agent/model loop.
                rpc({"id": "refresh", "type": "prompt", "message": "/gateway-models-refresh"})
                again = rpc({"id": "models-again", "type": "get_available_models"})
                after = [m for m in again["data"]["models"] if m["provider"] in ids]
                self.assertEqual(models, after)
                available = rpc({"id": "terra-levels-refreshed", "type": "get_available_thinking_levels"})
                self.assertEqual(available["data"]["levels"], levels)
                self.assertEqual(original_config, (root / "models.json").read_bytes())
                self.assertNotIn("fake-gateway-key-for-test", cache.read_text())
                if (root / "auth.json").exists():
                    self.assertEqual(json.loads((root / "auth.json").read_text()), {})
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                thread.join(timeout=2)
                process.stdin.close()
                process.stdout.close()
                process.stderr.close()


if __name__ == "__main__":
    unittest.main()
