"""Run: python3 -m unittest discover -s profiles/bb -p 'test_*.py'."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from launch import launch_args, select_native_mcp, select_shared_tools, select_gateway_models, tool_environment, typescript_path

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

    def test_core_executable_is_opaque_to_the_launcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # The upstream Nix package changes lib/ layout, not bin/pi.
            candidate = "/nix/store/candidate-pi-1.4.0/bin/pi"
            flags = ["--mode", "rpc", "--no-extensions"]
            self.assertEqual(launch_args(candidate, "unused-lens.js", flags, root, root),
                             [candidate, *flags, "--no-approve"])

    def test_native_mcp_trust_does_not_enable_lens_or_inherit_parent_trust(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "project"
            project.mkdir()
            (root / "trust.json").write_text(json.dumps({str(project.resolve()): True}))
            flags = ["--no-extensions", "--extension", "builtin:mcp"]
            self.assertEqual(launch_args("pi", "missing-lens.js", flags, root, project),
                             ["pi", *flags, "--approve"])
            self.assertEqual(launch_args("pi", "missing-lens.js", flags, root, project / "nested"),
                             ["pi", *flags, "--no-approve"])
            alias = root / "alias"
            alias.symlink_to(project, target_is_directory=True)
            self.assertIn("--approve", launch_args("pi", "missing-lens.js", flags, root, alias))
            (root / "trust.json").write_text(json.dumps({str(project.resolve()): False}))
            self.assertIn("--no-approve", launch_args("pi", "missing-lens.js", flags, root, project))
            for bad in ([], {"relative": True}, {str(project): "yes"}):
                (root / "trust.json").write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    launch_args("pi", "missing-lens.js", flags, root, project)

    def test_native_mcp_replaces_old_service_arguments_without_discovery(self):
        root = Path("/tmp/fixture/.pi/bb-agent")
        args = ["--no-extensions", "--extension", "builtin:codemode", "--extension",
                str(root / "npm/node_modules/pi-mcp-adapter/index.ts")]
        selected = select_native_mcp(args, root)
        self.assertEqual(selected, [*args[:-1], "builtin:mcp"])
        self.assertEqual(select_native_mcp(selected, root), selected)
        self.assertTrue(args[-1].endswith("pi-mcp-adapter/index.ts"))
        self.assertEqual(select_native_mcp(["--no-extensions"], root),
                         ["--no-extensions", "--extension", "builtin:mcp"])
        unrelated = ["--extension", "/other/pi-mcp-adapter/index.ts"]
        self.assertEqual(select_native_mcp(unrelated, root), [*unrelated, "--extension", "builtin:mcp"])

    def test_shared_tools_use_the_standalone_install_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agent_dir = root / ".pi/bb-agent"
            processes = root / ".pi/agent/npm/node_modules/@aliou/pi-processes/extensions/processes/index.ts"
            for entry in (processes,):
                entry.parent.mkdir(parents=True)
                entry.touch()
            flags = ["--no-extensions", "--extension", "router.ts"]

            selected = select_shared_tools(flags, agent_dir)
            self.assertEqual(selected, [*flags, "--extension", str(processes)])
            self.assertEqual(select_shared_tools(selected, agent_dir), selected)
            self.assertEqual(flags, ["--no-extensions", "--extension", "router.ts"])
            processes.unlink()
            with self.assertRaises(FileNotFoundError):
                select_shared_tools(flags, agent_dir)

    def test_web_access_uses_the_published_package_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shared = root / ".pi/agent/npm/node_modules"
            processes = shared / "@aliou/pi-processes/extensions/processes/index.ts"
            processes.parent.mkdir(parents=True)
            processes.touch()
            web = shared / "pi-web-access"
            args = ["--extension", str(web / "index.ts"), "--extension", "/other/index.ts"]
            selected = select_shared_tools(args, root / ".pi/bb-agent")
            self.assertEqual(selected[:4], ["--extension", str(web), "--extension", "/other/index.ts"])
            self.assertEqual(select_shared_tools(selected, root / ".pi/bb-agent"), selected)
            self.assertTrue(args[1].endswith("/index.ts"))

    def test_gateway_models_explicit_selection_is_idempotent(self):
        args = ["--no-extensions", "--extension", "other.ts"]
        selected = select_gateway_models(args)
        self.assertTrue(selected[-1].endswith("/extensions/cliproxy-models/index.ts"))
        self.assertEqual(selected[-2], "--extension")
        self.assertEqual(select_gateway_models(selected), selected)
        self.assertEqual(args, ["--no-extensions", "--extension", "other.ts"])

    def test_missing_shared_tool_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent_dir = Path(tmp) / ".pi/bb-agent"
            with self.assertRaises(FileNotFoundError):
                select_shared_tools([], agent_dir)

    def test_nix_typescript_wrapper_exposes_the_real_compiler_without_installing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wrapper = root / "store/typescript/bin/tsc"
            native = root / "store/typescript/lib/node_modules/typescript/bin/tsc"
            server = native.parent.parent / "lib/tsserver.js"
            profile = root / "profile/bin/tsc"
            for path in (wrapper, native, server, profile):
                path.parent.mkdir(parents=True, exist_ok=True)
            wrapper.write_text("#!/bin/sh\n")
            wrapper.chmod(0o755)
            profile.symlink_to(wrapper)
            selected = str(profile.parent)
            self.assertEqual(typescript_path(selected), selected)
            native.write_text("#!/bin/sh\n")
            native.chmod(0o755)
            self.assertEqual(typescript_path(selected), selected)
            server.touch()
            fixed = str(native.parent) + ":" + selected
            self.assertEqual(typescript_path(selected), fixed)
            self.assertEqual(typescript_path(fixed), fixed)
            self.assertEqual(typescript_path(str(root / "missing")), str(root / "missing"))

    def test_tool_state_isolation(self):
        root = Path("/tmp/fixture-bb-agent")
        env = tool_environment(root)
        self.assertNotIn("PI_MCP_CONFIG_MODE", env)
        self.assertNotIn("MCP_UI_VIEWER", env)
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

    def test_skill_copy_updates_only_owned_files_and_refuses_unsafe_paths(self):
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
            unrelated = target / "other-skill/SKILL.md"
            unrelated.parent.mkdir()
            unrelated.write_text("not owned")
            extra = target / "ponytail/local-note.md"
            extra.write_text("keep")
            owned = target / "ponytail/SKILL.md"
            owned.write_text("old copy")
            (source / "skills/ponytail/SKILL.md").write_text("new upstream skill")
            (source / "LICENSE").write_text("new upstream license")
            updated = sync_skills.sync(source, target)
            self.assertNotEqual(hashes, updated)
            self.assertEqual(owned.read_text(), "new upstream skill")
            self.assertEqual(unrelated.read_text(), "not owned")
            self.assertEqual(extra.read_text(), "keep")
            self.assertEqual(updated, sync_skills.sync(source, target))
            self.assertTrue(all((target / name / "LICENSE").read_text() == "new upstream license"
                                for name in sync_skills.NAMES))

            # Validate the complete batch before overwriting the first owned file.
            owned.write_text("unchanged on failure")
            bad = target / sync_skills.NAMES[-1] / "LICENSE"
            bad.unlink()
            for link_target in (source / "LICENSE", root / "missing"):
                bad.symlink_to(link_target)
                with self.assertRaises(ValueError):
                    sync_skills.sync(source, target)
                self.assertEqual(owned.read_text(), "unchanged on failure")
                bad.unlink()
            bad.mkdir()
            with self.assertRaises(ValueError):
                sync_skills.sync(source, target)
            self.assertEqual(owned.read_text(), "unchanged on failure")
            bad.rmdir()

            alias = root / "target-alias"
            alias.symlink_to(target, target_is_directory=True)
            with self.assertRaises(ValueError):
                sync_skills.sync(source, alias)
            blocked = root / "blocked"
            blocked.mkdir()
            (blocked / sync_skills.NAMES[-1]).write_text("not a directory")
            with self.assertRaises(ValueError):
                sync_skills.sync(source, blocked)
            self.assertFalse((blocked / "ponytail").exists())

            # Source symlinks must not turn the copier into an arbitrary-file copy.
            (source / "LICENSE").unlink()
            (source / "LICENSE").symlink_to(extra)
            with self.assertRaises(ValueError):
                sync_skills.sync(source, target)
            self.assertEqual(owned.read_text(), "unchanged on failure")


if __name__ == "__main__":
    unittest.main()
