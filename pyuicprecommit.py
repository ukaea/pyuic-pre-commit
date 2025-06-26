"""The entry point for the pyuic-pre-commit pre-commit hook."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

UI_TO_PY_PATTERN = r"ui_{}.py"


@dataclass
class Args:
    """Command line options for the hook."""

    files: list[Path]
    exe_name: str
    pattern: str


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
        if not (target_file := target_file_path(ui_file, args.pattern)):
            return 1
        if not target_file.is_file():
            print(
                f"no Python file '{target_file}' found for ui file '{ui_file}'",
                file=sys.stderr,
            )
            exit_code = 1
            continue
        out = run_uic(uic_exe, ui_file)
        if out != target_file.read_text():
            print(
                f"Python file '{target_file}' out of date with '{ui_file}'",
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
    parser.add_argument(
        "--pattern",
        default=UI_TO_PY_PATTERN,
        type=lambda s: str(s).strip("\"'"),
        help=(
            r"the pattern used to match ui files to Python files. The '{}' is replaced "
            "with the name of the .ui file, without the extension. This can be a path "
            "relative to the ui file. For OS compatibility, prefer '/' as a path "
            f"separator [default: {UI_TO_PY_PATTERN}]"
        ),
    )
    return Args(**vars(parser.parse_args(argv)))


def find_uic_exe(cli_exe: str) -> Path | None:
    """Find the uic executable on the system path."""
    if exe := shutil.which(cli_exe):
        return Path(exe)
    return None


def target_file_path(ui_file: Path, pattern: str) -> Path | None:
    """
    Return the path to the target Python file.

    Return None and print an error message if the pattern is not valid.
    """
    try:
        formatted_pattern = pattern.format(ui_file.stem)
    except Exception as exc:
        print(f"invalid pattern '{pattern}': {exc}", file=sys.stderr)
        return None
    return Path(ui_file.parent / formatted_pattern).resolve().relative_to(Path.cwd())


def run_uic(uic_exe: Path, ui_file: Path) -> str:
    """Run uic on the given ui file, returning the output."""
    cmd = [str(uic_exe), str(ui_file)]
    return subprocess.check_output(cmd).decode()  # noqa: S603


if __name__ == "__main__":
    main_with_exit()
