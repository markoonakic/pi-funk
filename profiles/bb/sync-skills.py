#!/usr/bin/env python3
"""Copy upstream Ponytail skills for BB, without symlinks or edited skill forks.

Usage: python3 profiles/bb/sync-skills.py PONYTAIL_CHECKOUT BB_SKILLS_DIRECTORY
Existing differing files are refused; back them up before explicitly replacing.
"""

import hashlib
from pathlib import Path
import shutil
import sys

NAMES = ("ponytail", "ponytail-review", "ponytail-audit", "ponytail-debt", "ponytail-gain", "ponytail-help")


def sync(source, destination):
    copies = []
    for name in NAMES:
        for src, dst in [
            (source / "skills" / name / "SKILL.md", destination / name / "SKILL.md"),
            (source / "LICENSE", destination / name / "LICENSE"),
        ]:
            if src.is_symlink() or not src.is_file():
                raise ValueError(f"Expected original regular source file: {src}")
            if any(part.is_symlink() for part in [dst, *dst.parents]):
                raise ValueError(f"BB skill destination must not contain symlinks: {dst}")
            if dst.exists() and dst.read_bytes() != src.read_bytes():
                raise ValueError(f"Back up and remove differing destination before updating: {dst}")
            copies.append((src, dst))
    for src, dst in copies:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return {str(dst.relative_to(destination)): hashlib.sha256(dst.read_bytes()).hexdigest()
            for _, dst in copies}


if __name__ == "__main__":
    hashes = sync(Path(sys.argv[1]).expanduser().resolve(), Path(sys.argv[2]).expanduser().absolute())
    print(f"Copied/verified {len(NAMES)} original Ponytail skills and their MIT license ({len(hashes)} files)")
