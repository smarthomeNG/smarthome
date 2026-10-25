"""
Real git repositories for tests: an upstream with commits and clones tracking it.
"""

import os
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


def git(path: Path, *args: str) -> str:
    """Runs git in path and returns its stripped stdout; raises on a non-zero exit."""
    env = {
        **os.environ,
        'GIT_AUTHOR_NAME': 't',
        'GIT_AUTHOR_EMAIL': 't@t',
        'GIT_COMMITTER_NAME': 't',
        'GIT_COMMITTER_EMAIL': 't@t',
    }
    return subprocess.run(
        ['git', '-C', str(path), *args], capture_output=True, text=True, check=True, env=env
    ).stdout.strip()


def commit_file(path: Path, name: str, content: str) -> None:
    """Writes content to name in the repository at path and commits it."""
    (path / name).write_text(content)
    git(path, 'add', name)
    git(path, 'commit', '-qm', f'{name}: {content}')


class RepoPair:
    """An upstream repository and a clone of it tracking the upstream's main branch."""

    def __init__(self, root: Path, name: str, clone: Path | None = None):
        """
        :param root: directory for the upstream (and the clone, unless clone is given)
        :param name: repository name, used for the directory names
        :param clone: directory to clone into, defaults to root/name
        """
        self.upstream = root / f'{name}_upstream'
        self.clone = clone if clone is not None else root / name
        subprocess.run(['git', 'init', '-q', '-b', 'main', str(self.upstream)], check=True)
        commit_file(self.upstream, 'f.txt', 'one\n')
        subprocess.run(['git', 'clone', '-q', str(self.upstream), str(self.clone)], check=True)

    def push_upstream_commit(self, name: str = 'f.txt', content: str = 'two\n') -> None:
        """Adds a commit to the upstream that the clone does not have yet."""
        commit_file(self.upstream, name, content)


class GitTestCase(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
