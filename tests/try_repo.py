"""
Functions to aid in testing the pre-commit hook.

The logic is largely copied from the pre-commit repo:
https://github.com/pre-commit/pre-commit/blob/d2b61d0ef/pre_commit/commands/try_repo.py.
The original logic is modified to allow us to set arguments in the
config when running the hook in tests.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from pre_commit import constants, git, output
from pre_commit.util import cmd_output_b
from pre_commit.xargs import xargs
from pre_commit.yaml import yaml_dump

logger = logging.getLogger(__name__)


def make_shadow_repo(
    repo_copy_dir: Path,
    repo: Path,
    hook: str,
    config_args: list[str],
    ref: str,
) -> Path:
    """
    Make a copy of a hook repository that can be used to test that hook.

    In order to test a hook repository, you need another Git repository
    to run the hook from. The pre-commit config in the Git repository
    must contain a path to the local hook repository you want to test
    and the revision of that repository that should be used. This poses
    a problem when you are testing a hook repository that has
    uncommitted changes.

    To work around this, if there are uncommitted changes to the hook
    repository we clone it into a temporary directory, commit any
    unstaged changes, and use the new HEAD commit to run tests against.
    This is very similar to how 'pre-commit try-repo' works, in fact
    much of that code is used here.

    We could use 'pre-commit try-repo' directly, however it does not
    allow us to customise the pre-commit config used to test the hook
    repository. So we re-implement most of 'try-repo' here, but allow
    use of custom config options.

    Parameters
    ----------
    repo_copy_dir:
        The directory in which to make the fake hook repository. This
        will copy all files from ``repo``, create a git repo, and commit
        any unstaged changes. In tests, this will generally be a
        temporary directory.
    repo:
        The path to the hook repository. Usually **this** repository.
    hook:
        The name of the hook to test.
    config_args:
        The arguments to pass to the hook.
    ref:
        The Git revision of the hook repository to checkout in the copy.

    Returns
    -------
    :
        The path to the config file to be used when running the hook.

    """
    repo_str, ref = _repo_ref(repo_copy_dir, str(repo), ref)

    hooks = [{"id": hook, "args": config_args}]
    config = {"repos": [{"repo": repo_str, "rev": ref, "hooks": hooks}]}
    config_s = yaml_dump(config)
    config_filename = repo_copy_dir / constants.CONFIG_FILE
    config_filename.write_text(config_s)

    output.write_line("=" * 79)
    output.write_line("Using config:")
    output.write_line("=" * 79)
    output.write(config_s)
    output.write_line("=" * 79)

    return config_filename


def _repo_ref(tmpdir: Path, repo: str, ref: str) -> tuple[str, str]:
    if not git.has_diff("HEAD", repo=repo):
        return repo, ref

    ref = git.head_rev(repo)
    logger.warning("Creating temporary repo with uncommitted changes...")

    shadow = str(tmpdir / "shadow-repo")
    cmd_output_b("git", "clone", str(repo), shadow)
    cmd_output_b("git", "checkout", ref, "-b", "_pc_tmp", cwd=shadow)

    idx = git.git_path("index", repo=shadow)
    objs = git.git_path("objects", repo=shadow)
    env = dict(os.environ, GIT_INDEX_FILE=idx, GIT_OBJECT_DIRECTORY=objs)

    staged_files = git.get_staged_files(cwd=repo)
    if staged_files:
        xargs(("git", "add", "--"), staged_files, cwd=repo, env=env)

    cmd_output_b("git", "add", "-u", cwd=repo, env=env)
    git.commit(repo=shadow)

    return shadow, git.head_rev(shadow)
