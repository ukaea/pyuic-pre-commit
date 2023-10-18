"""The entry point for the pyuic-pre-commit pre-commit hook."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Args:
    """Command line options for the hook."""

    files: list[Path]
    exe_name: str


def main_with_exit():
    """Run the pre-commit checks and exit on the returned error code."""
    sys.exit(main(sys.argv[1:]))


def main(argv: list[str]) -> int:
    """Run the pre-commit checks."""
    args = parse_args(argv)
    if not (uic_exe := find_uic_exe(args.exe_name)):
        print("cannot find uic executable, ensure it's on your path", file=sys.stderr)
        return 1

    exit_code = 0
    for ui_file in args.files:
        target_file = Path(ui_file.parent / f"ui_{ui_file.stem}.py")
        if not target_file.is_file():
            print(f"no Python file found for ui file '{ui_file}'", file=sys.stderr)
            exit_code = 1
            continue
        out = run_uic(uic_exe, ui_file)
        if out != target_file.read_text():
            print(
                f"Python file '{target_file}' out of data with '{ui_file}'",
                file=sys.stderr,
            )
            exit_code = 1
    return exit_code


def parse_args(argv: list[str]) -> Args:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="the files to apply the check to",
    )
    parser.add_argument(
        "--exe-name",
        default="pyside6-uic",
        type=str,
        help="the name of the uic executable to use",
    )
    return Args(**vars(parser.parse_args(argv)))


def find_uic_exe(cli_exe: str) -> Path | None:
    """Find the uic executable on the system path."""
    if exe := shutil.which(cli_exe):
        return Path(exe)
    return None


def run_uic(uic_exe: Path, ui_file: Path) -> str:
    """Run uic on the given ui file, returning the output."""
    cmd = [str(uic_exe), str(ui_file)]
    return subprocess.check_output(cmd).decode()  # noqa: S603


if __name__ == "__main__":
    main_with_exit()
