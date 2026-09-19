"""Run: python3 -m unittest discover -s profiles/bb -p 'test_*.py'."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from launch import launch_args, select_rpiv, tool_environment

spec = importlib.util.spec_from_file_location("sync_skills", Path(__file__).with_name("sync-skills.py"))
assert spec is not None and spec.loader is not None
sync_skills = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_skills)


class LaunchTest(unittest.TestCase):
    def test_exact_trust_and_explicit_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lens = root / "lens.js"
            lens.touch()
            project = root / "project"
            project.mkdir()
            flags = ["--no-extensions", "--no-skills", "--extension", "router.ts"]
            self.assertEqual(launch_args("pi", str(lens), flags, root, project), ["pi", *flags, "--no-approve"])
            (root / "lens-projects.json").write_text(json.dumps([str(project)]))
            result = launch_args("pi", str(lens), flags, root, project)
            self.assertEqual(result, ["pi", *flags, "--approve", "--extension", str(lens), "--no-autoformat", "--no-autofix", "--no-tests"])
            for other in (project / "nested", root / "project-other"):
                self.assertNotIn("--approve", launch_args("pi", str(lens), flags, root, other))
            alias = root / "alias"
            alias.symlink_to(project, target_is_directory=True)
            self.assertIn("--approve", launch_args("pi", str(lens), flags, root, alias))
            with self.assertRaises(ValueError):
                launch_args("pi", str(lens), ["--approve"], root, project)
            lens.unlink()
            with self.assertRaises(FileNotFoundError):
                launch_args("pi", str(lens), flags, root, project)

    def test_rpiv_uses_the_standalone_install_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agent_dir = root / ".pi/bb-agent"
            rpiv = root / ".pi/agent/npm/node_modules/@juicesharp/rpiv-todo/index.ts"
            rpiv.parent.mkdir(parents=True)
            rpiv.touch()
            flags = ["--no-extensions", "--extension", "router.ts"]

            selected = select_rpiv(flags, agent_dir)
            self.assertEqual(selected, [*flags, "--extension", str(rpiv)])
            self.assertEqual(select_rpiv(selected, agent_dir), selected)
            self.assertEqual(flags, ["--no-extensions", "--extension", "router.ts"])

    def test_missing_rpiv_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent_dir = Path(tmp) / ".pi/bb-agent"
            with self.assertRaises(FileNotFoundError):
                select_rpiv([], agent_dir)

    def test_tool_state_isolation(self):
        root = Path("/tmp/fixture-bb-agent")
        env = tool_environment(root)
        self.assertNotIn("PI_MCP_CONFIG_MODE", env)
        self.assertEqual(env["MCP_UI_VIEWER"], "none")
        self.assertEqual(env["PI_FFF_MODE"], "override")
        self.assertEqual(env["FFF_FRECENCY_DB"], str(root / "fff/frecency"))
        self.assertEqual(env["FFF_HISTORY_DB"], str(root / "fff/history"))

    def test_bad_allowlist_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for value in ({}, ["relative"], [3]):
                (root / "lens-projects.json").write_text(json.dumps(value))
                with self.assertRaises(ValueError):
                    launch_args("pi", "lens", [], root, root)

    def test_skill_copy_and_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, target = root / "source", root / "target"
            source.mkdir()
            (source / "LICENSE").write_text("MIT fixture")
            for name in sync_skills.NAMES:
                folder = source / "skills" / name
                folder.mkdir(parents=True)
                (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: test\n---\nOriginal")
            hashes = sync_skills.sync(source, target)
            self.assertEqual(len(hashes), 12)
            self.assertEqual(hashes, sync_skills.sync(source, target))
            self.assertFalse(any(p.is_symlink() for p in target.rglob("*")))
            (target / "ponytail/SKILL.md").write_text("human edit")
            with self.assertRaises(ValueError):
                sync_skills.sync(source, target)
            (target / "ponytail/SKILL.md").unlink()
            (target / "ponytail/SKILL.md").symlink_to(source / "skills/ponytail/SKILL.md")
            with self.assertRaises(ValueError):
                sync_skills.sync(source, target)


if __name__ == "__main__":
    unittest.main()
