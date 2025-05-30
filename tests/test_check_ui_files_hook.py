import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path

import git
import pytest
from pre_commit.main import main as pre_commit_main

from tests.try_repo import make_shadow_repo

DATA_DIR = Path(__file__).parent / "data"
ROOT_DIR = Path(__file__).parent.parent
HOOK_NAME = "check-ui-files"


@contextmanager
def working_directory(working_dir: Path):
    current_dir = Path.cwd()
    try:
        os.chdir(working_dir)
        yield
    finally:
        os.chdir(current_dir)


@pytest.fixture
def temp_repo():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield git.Repo.init(tmp_dir)


def test_install_succeeds(temp_repo: git.Repo):
    repo_dir = Path(temp_repo.git_dir).parent

    with working_directory(repo_dir):
        result = pre_commit_main(["try-repo", str(ROOT_DIR), HOOK_NAME])

    assert result == 0


def test_hook_errors_given_missing_py_file(temp_repo: git.Repo):
    repo_dir = Path(temp_repo.git_dir).parent
    shutil.copyfile(DATA_DIR / "window.ui", repo_dir / "window.ui")
    temp_repo.git.add(str(repo_dir / "window.ui"))

    with working_directory(repo_dir):
        result = pre_commit_main(["try-repo", str(ROOT_DIR), HOOK_NAME])

    assert result == 1


def test_hook_errors_given_py_file_out_of_date(temp_repo: git.Repo):
    repo_dir = Path(temp_repo.git_dir).parent
    shutil.copyfile(DATA_DIR / "window.ui", repo_dir / "window.ui")
    (repo_dir / "ui_window.py").write_text("Not right content")
    temp_repo.git.add(str(repo_dir / "window.ui"))

    with working_directory(repo_dir):
        result = pre_commit_main(["try-repo", str(ROOT_DIR), HOOK_NAME])

    assert result == 1


def test_hook_successful_given_py_file_present(temp_repo: git.Repo):
    repo_dir = Path(temp_repo.git_dir).parent
    shutil.copyfile(DATA_DIR / "window.ui", repo_dir / "window.ui")
    shutil.copyfile(DATA_DIR / "ui_window.py", repo_dir / "ui_window.py")
    temp_repo.git.add(str(repo_dir / "window.ui"))

    with working_directory(repo_dir):
        result = pre_commit_main(["try-repo", str(ROOT_DIR), HOOK_NAME])

    assert result == 0


def test_hook_finds_ui_file_using_non_default_pattern(
    temp_repo: git.Repo, tmp_path: Path
):
    repo_dir = Path(temp_repo.git_dir).parent
    (repo_dir / "ui").mkdir()
    shutil.copyfile(DATA_DIR / "window.ui", repo_dir / "ui" / "window.ui")
    shutil.copyfile(DATA_DIR / "ui_window.py", repo_dir / "window.py")
    temp_repo.git.add(str(repo_dir / "ui" / "window.ui"))

    with working_directory(repo_dir):
        ref = str(git.Repo(ROOT_DIR).head.ref)
        config_path = make_shadow_repo(
            tmp_path,
            ROOT_DIR,
            HOOK_NAME,
            ["--pattern", "../{}.py"],
            ref=ref,
        )
        result = pre_commit_main(["run", "--all-files", "--config", str(config_path)])

    assert result == 0
