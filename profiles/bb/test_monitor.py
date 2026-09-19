"""Credential-free/offline checks: python3 -m unittest discover -s profiles/bb."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("monitor", Path(__file__).with_name("monitor-updates.py"))
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


class MonitorTest(unittest.TestCase):
    def test_shared_policy_contract(self):
        root = Path(__file__).resolve().parents[2]
        policy_path = root / "profiles/bb/AGENTS.md"
        self.assertTrue(policy_path.is_symlink())
        self.assertEqual(os.readlink(policy_path), "../../agent/AGENTS.md")
        policy = (root / "agent/AGENTS.md").read_text()
        self.assertIn("You are the parent/orchestrator session.", policy)
        for model in [
            "antigravity/gemini-3.8-flash", "openai-codex/gpt-5.6-luna",
            "openai-codex/gpt-5.6-sol", "openai-codex/gpt-6-astra",
        ]:
            self.assertIn(model, policy)
        self.assertIn("ASD-STE100 Simplified Technical English", policy)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        private = self.home / ".bb/pi-update-monitor"
        private.mkdir(mode=0o700, parents=True)
        self.state_dir = private / "state"
        self.config = {"workspace": str(self.home / "workspace"), "packages": [],
                       "ponytail_source": str(self.home / "source"), "bb_skills": str(self.home / "skills")}
        home = patch.object(monitor.Path, "home", return_value=self.home)
        home.start()
        self.addCleanup(home.stop)

    def npm_item(self, root):
        (root / "package.json").write_text('{"name":"fixture","version":"1.2.3"}')
        return {"name": "Fixture", "kind": "npm", "source": "fixture", "path": str(root),
                "owner": "shared", "qualified": "1.2.2"}

    def test_npm_holds_and_metadata_without_package_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            item = self.npm_item(root)
            before = (root / "package.json").read_bytes()
            metadata = {"name": "fixture", "version": "1.2.4", "dist": {"integrity": "sha512-test"}}
            with patch.object(monitor, "fetch_json", return_value=metadata) as fetch, patch.object(monitor, "run") as run:
                cache = {}
                result = monitor.inspect(item, cache)
                monitor.inspect(item, cache)
                self.assertEqual(fetch.call_count, 1)
                run.assert_not_called()
            self.assertEqual(result["status"], "candidate-differs")
            self.assertEqual(len(result["holds"]), 3)
            self.assertEqual((root / "package.json").read_bytes(), before)
            with patch.object(monitor, "fetch_json", return_value={**metadata, "version": "1.1.0"}):
                self.assertEqual(monitor.inspect(item, {})["status"], "upstream-behind")
            with patch.object(monitor, "fetch_json", return_value={**metadata, "name": "wrong"}):
                self.assertEqual(monitor.inspect(item, {})["status"], "check-failed")
            with patch.object(monitor, "fetch_json", side_effect=OSError("secret-path")):
                result = monitor.inspect(item, {})
                self.assertEqual(result["status"], "check-failed")
                self.assertNotIn("secret-path", json.dumps(result))

    def test_dirty_git_is_held_and_never_fetched_or_reconciled(self):
        item = {"name": "Git", "kind": "git", "source": "owner/repo", "owner": "bb", "path": "/fixture"}
        with patch.object(monitor, "run", side_effect=["a" * 40, " M overlay.ts"]) as run, patch.object(
            monitor, "fetch_json", return_value={"sha": "b" * 40}
        ):
            result = monitor.inspect(item, {})
        self.assertEqual(result["dirty_entries"], 1)
        self.assertTrue(any("local changes" in hold for hold in result["holds"]))
        commands = [call.args[0] for call in run.call_args_list]
        self.assertEqual(commands[0][-2:], ["rev-parse", "HEAD"])
        self.assertEqual(commands[1][-3:], ["status", "--porcelain", "--untracked-files=normal"])

    def test_host_selection_copy_and_local_source_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = {"hostname": "fixture", "workspace": str(root), "selection_hash": "wrong",
                      "guard_files": [{"name": "Launcher", "path": str(root / "missing"), "sha256": "none"}],
                      "packages": [], "ponytail_source": str(root), "bb_skills": str(root / "copies")}
            with patch.object(monitor.socket, "gethostname", return_value="wrong"):
                with self.assertRaises(ValueError):
                    monitor.collect(config)
            with patch.object(monitor.socket, "gethostname", return_value="fixture"), patch.object(
                monitor, "service_selection", return_value={}
            ):
                result = monitor.collect(config)
            self.assertEqual(len(result["warnings"]), 14)
            self.assertNotIn(tmp, json.dumps(result))

    def report(self, day="2026-01-01", candidate="2.0.0"):
        return {"checked_at": day + "T09:00:00+00:00", "packages": [
            {"name": "Fixture", "kind": "npm", "source": "fixture", "status": "candidate-differs", "current": "1.0.0", "candidate": candidate}
        ], "warnings": []}

    def test_review_cache_daily_cap_and_ambiguous_dispatch(self):
        with patch.object(monitor, "notify", return_value="thr_fixture") as notify, patch("builtins.print"):
            monitor.execute(self.config, self.report(), self.state_dir)
            monitor.execute(self.config, self.report(), self.state_dir)
            monitor.execute(self.config, self.report(candidate="2.1.0"), self.state_dir)
            self.assertEqual(notify.call_count, 1)
            monitor.execute(self.config, self.report(day="2026-01-02", candidate="2.1.0"), self.state_dir)
            self.assertEqual(notify.call_count, 2)
        with patch.object(monitor, "notify", side_effect=TimeoutError) as notify, patch("builtins.print"):
            monitor.execute(self.config, self.report(day="2026-01-03", candidate="3.0.0"), self.state_dir)
            monitor.execute(self.config, self.report(day="2026-01-04", candidate="3.0.0"), self.state_dir)
            self.assertEqual(notify.call_count, 1)
        state = json.loads((self.state_dir / "state.json").read_text())
        self.assertIn("dispatch-uncertain:TimeoutError", state["reviews"].values())

    def test_new_package_and_reordering_do_not_repeat_old_review(self):
        with patch.object(monitor, "notify", return_value="thr_fixture") as notify, patch("builtins.print"):
            monitor.execute(self.config, self.report(), self.state_dir)
            report = self.report(day="2026-01-02")
            report["packages"].append({**report["packages"][0], "source": "another-package"})
            report["packages"].reverse()
            monitor.execute(self.config, report, self.state_dir)
            snapshot = json.loads(notify.call_args.args[1].read_text())
            self.assertEqual([row["source"] for row in snapshot["packages"]], ["another-package"])
            report["packages"].reverse()
            monitor.execute(self.config, report, self.state_dir)
            self.assertEqual(notify.call_count, 2)

    def test_review_snapshot_keeps_all_consumers_of_one_candidate(self):
        report = self.report()
        report["packages"].append({**report["packages"][0], "name": "Second consumer", "owner": "shared"})
        with patch.object(monitor, "notify", return_value="thr_fixture") as notify, patch("builtins.print"):
            monitor.execute(self.config, report, self.state_dir)
        snapshot = json.loads(notify.call_args.args[1].read_text())
        self.assertEqual([row["name"] for row in snapshot["packages"]], ["Fixture", "Second consumer"])
        self.assertEqual(len(snapshot["packages"]), 2)

    def test_private_output_and_symlink_guards(self):
        with self.assertRaises(ValueError):
            monitor.validate_state_dir(self.config, self.home / "package")
        with self.assertRaises(ValueError):
            monitor.validate_state_dir({**self.config, "workspace": str(self.home)}, self.state_dir)
        monitor.validate_state_dir(self.config, self.state_dir)
        package = self.home / "package.json"
        package.write_text("untouched")
        (self.state_dir / "latest.tmp").symlink_to(package)
        monitor.save(self.state_dir / "latest.json", {"test": True})
        self.assertEqual(package.read_text(), "untouched")
        (self.state_dir / "linked.json").symlink_to(package)
        with self.assertRaises(ValueError):
            monitor.save(self.state_dir / "linked.json", {})
        (self.state_dir / "state.json").symlink_to(package)
        with self.assertRaises(ValueError):
            monitor.execute(self.config, self.report(), self.state_dir)
        self.assertEqual(package.read_text(), "untouched")

    def test_no_candidate_never_starts_agent(self):
        with patch.object(monitor, "notify") as notify, patch("builtins.print"):
            report = self.report()
            report["packages"][0]["status"] = "current"
            monitor.execute(self.config, report, self.state_dir)
            notify.assert_not_called()

    def test_notification_uses_explicit_scope_and_read_only_prompt(self):
        config = {"bb_cli": "/fixture/bb", "project_id": "proj_fixture", "environment_id": "env_fixture",
                  "review_model": "provider/model"}
        with patch.object(monitor, "run", return_value='{"id":"thr_fixture"}') as run:
            self.assertEqual(monitor.notify(config, Path("/private/report.json")), "thr_fixture")
        args = run.call_args.args[0]
        self.assertEqual(args[:3], ["/fixture/bb", "thread", "spawn"])
        self.assertIn("proj_fixture", args)
        self.assertIn("env_fixture", args)
        prompt = args[args.index("--prompt") + 1]
        self.assertIn("No installs, updates", prompt)
        self.assertIn("openai-codex/gpt-6-astra model at low reasoning", prompt)
        self.assertIn("at most one Flash worker (antigravity/gemini-3.8-flash) at low reasoning", prompt)
        self.assertIn("do not retry or switch providers", prompt)
        self.assertIn("one new review root thread per day", prompt)


if __name__ == "__main__":
    unittest.main()
