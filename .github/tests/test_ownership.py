"""Unsigned, synthetic actual-source ownership tests; never builds the project."""

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(os.environ.get("OWNERSHIP_SOURCE_ROOT", ROOT)).resolve()
SDK = {
    "4DPluginAPI.c": "29788ed041effaf67269ccd93f971e8aee2ce5f8",
    "4DPluginAPI.h": "1854e9db452592498ad9047d8e1ffa46df75b795",
    "4DPluginAPI.def": "996ecc4ab11ad165de9192eba2e7478db141c757",
    "EntryPoints.h": "730f2f77ff2713fb2fe4b7d6562baeedf5f664cb",
    "Flags.h": "10a83185333dac06a62dda61b9f9428243d1e2ee",
    "PrivateTypes.h": "77053dc0c0a3718d2d3b6f158371a6af78c6ae66",
    "PublicTypes.h": "2bb392e73e9c556c274fe0a75b3a6b83e310b77c",
}


@unittest.skipUnless(sys.platform == "darwin", "macOS synthetic host")
class OwnershipTests(unittest.TestCase):
    leaf_runs = 0
    leaf_passes = 0

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="proxy-ownership-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.binary = Path(cls.temp.name) / "ownership"
        api = SOURCE / "4D Plugin API"
        for name, expected in SDK.items():
            contents = (api / name).read_bytes()
            blob = hashlib.sha1(f"blob {len(contents)}\0".encode() + contents).hexdigest()
            if blob != expected:
                raise AssertionError(f"Re-audit changed SDK: {name}: {blob}")
        result = subprocess.run([
            "clang++", "-std=c++14", "-x", "objective-c++",
            "-include", str(ROOT / ".github/tests/ownership_platform.h"),
            "-I", str(api), "-I", str(api / "Classes"), "-I", str(SOURCE),
            "-I", str(SOURCE / "include"),
            "-fsanitize=address,undefined", "-fno-sanitize=alignment",
            "-fno-omit-frame-pointer", "-g",
            "-Wno-deprecated-declarations", "-Wno-return-type-c-linkage",
            "-Wno-ignored-attributes", "-Wno-writable-strings",
            str(api / "4DPluginAPI.c"),
            *map(str, sorted((api / "Classes").glob("*.cpp"))),
            str(SOURCE / "4DPlugin.cpp"),
            str(ROOT / ".github/tests/ownership_host.mm"),
            "-framework", "Cocoa", "-framework", "Carbon", "-o", str(cls.binary),
        ], capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        imports = subprocess.check_output(["nm", "-u", str(cls.binary)], text=True)
        linked = {line.split()[-1] for line in imports.splitlines() if line.split()}
        forbidden = {
            "_getaddrinfo", "_freeaddrinfo", "_socket", "_sendto", "_recvfrom",
            "_select", "_gethostbyname", "_connect", "_send", "_recv",
            "_system", "_popen", "_execve", "_posix_spawn",
            "_px_proxy_factory_new", "_px_proxy_factory_free",
            "_px_proxy_factory_get_proxies", "_px_proxy_factory_free_proxies",
            "_OBJC_CLASS_$_NSURL", "_OBJC_CLASS_$_NSImage",
            "_OBJC_CLASS_$_NSFileManager", "_OBJC_CLASS_$_NSWorkspace",
            "_CFURLCreateWithFileSystemPath", "_CFURLCopyFileSystemPath",
        }
        forbidden_prefixes = ("_SC", "_CFNetwork", "_SCDynamic", "_JS", "_DNS")
        unsafe = forbidden & linked | {
            name for name in linked if name.startswith(forbidden_prefixes)
        }
        if unsafe:
            raise AssertionError(f"Real platform boundary linked: {unsafe}")

    @classmethod
    def tearDownClass(cls):
        print(f"LEAF runs={cls.leaf_runs} passed={cls.leaf_passes} "
              f"failed={cls.leaf_runs - cls.leaf_passes}", file=sys.stderr)

    def run_case(self, case, text="", empty="allocated", *args):
        type(self).leaf_runs += 1
        result = subprocess.run(
            [str(self.binary), case, text, empty, *map(str, args)],
            env={**os.environ, "ASAN_OPTIONS": "detect_leaks=0",
                 "UBSAN_OPTIONS": "halt_on_error=1"},
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            type(self).leaf_passes += 1
        self.assertEqual(result.returncode, 0, f"{case}: {result.stdout}{result.stderr}")
        self.assertIn("strings=0 pictures=0 handles=0 objects=n/a collections=n/a", result.stdout)

    def test_picture_paths_and_formats_exact_text(self):
        for case in ("path", "copy"):
            for text in ("ASCII", "\u65e5", "\U0001f600", ""):
                for empty in ("allocated", "null"):
                    with self.subTest(case=case, text=text, empty=empty):
                        self.run_case(case, text, empty)

    def test_picture_owner_handoffs(self):
        for case in ("bytes", "gray", "size", "thumbnail"):
            with self.subTest(case=case):
                self.run_case(case)

    def test_array_transfers_replacement_copy_shrink_clear_rejection(self):
        for empty in ("allocated", "null"):
            with self.subTest(empty=empty):
                self.run_case("arrays", "", empty)

    def test_scalar_content_setter_lifetime(self):
        for text in ("ASCII", "\u65e5", "\U0001f600", ""):
            for empty in ("allocated", "null"):
                with self.subTest(text=text, empty=empty):
                    self.run_case("scalar", text, empty)

    def test_failures_before_adoption_or_cleanup(self):
        for case in ("path", "copy", "gray", "size", "thumbnail"):
            for failure in ("handle", "command"):
                with self.subTest(case=case, failure=failure):
                    self.run_case(f"{case}:{failure}")
        for case in ("copy:conversion", "bytes:creation", "path:creation", "thumbnail:creation"):
            with self.subTest(case=case):
                self.run_case(case)

    def test_sdk_failure_predicates_not_oom_safety(self):
        self.run_case("sdk-failures")

    def test_successful_command_return_owners(self):
        for case in ("path", "copy", "gray", "size", "thumbnail"):
            for kind in range(3):
                with self.subTest(case=case, kind=kind):
                    self.run_case("command-returns", "ASCII", "allocated", kind, case)

    def test_pointer_owned_lookup_and_failure(self):
        for case in ("pointer", "pointer-failure"):
            with self.subTest(case=case):
                self.run_case(case, "ASCII")

    def test_actual_dispatcher_offline(self):
        for mode in range(6):
            for empty in ("allocated", "null"):
                with self.subTest(mode=mode, empty=empty):
                    self.run_case("dispatch", "https://synthetic.invalid/path", empty, mode)


if __name__ == "__main__":
    unittest.main()
