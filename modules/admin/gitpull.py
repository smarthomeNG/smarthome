#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#########################################################################
#  This file is part of SmartHomeNG.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
Fast-forward-only git pulls of the core and plugins repositories, for the admin interface.

Pulling only replaces files on disk; the running core keeps executing what it has loaded
until it is restarted. Nothing here restarts it.
"""

import os
import subprocess
from pathlib import Path
from typing import Literal, TypedDict

PullTarget = Literal['core', 'plugins', 'all']
RepoStatus = Literal['ok', 'error', 'skipped']
RepoState = Literal['current', 'behind', 'ahead', 'diverged', 'blocked', 'no_upstream', 'unknown']


class RepoPullResult(TypedDict):
    """Outcome of pulling one repository."""

    repo: str
    status: RepoStatus
    text: str  # git's output, or the reason for an error or skip
    changed: bool  # True if HEAD moved, i.e. the files on disk differ from what the running core loaded
    before: str  # commit id HEAD pointed at before the pull, '' if it could not be determined
    files: list[str]  # paths that differ between before and the new HEAD, relative to the repository root


class RepoCheck(TypedDict):
    """How a repository stands against its upstream, as of a fresh fetch."""

    repo: str
    state: RepoState  # 'unknown' if the upstream could not be fetched
    behind: int  # upstream commits the checked-out branch does not have
    ahead: int  # commits the checked-out branch has that the upstream does not
    text: str  # why the state is 'blocked', 'diverged', 'no_upstream' or 'unknown', otherwise ''


def _git(path: Path, *args: str, timeout: float = 60) -> tuple[bool, str]:
    """
    Runs git in the repository at path and waits for it to finish.

    Credential prompts are disabled, so a remote that wants authentication fails instead of hanging. Output is
    never colored, whatever the git configuration says.

    :param path: repository directory
    :param args: git arguments
    :param timeout: seconds to wait before killing git
    :return: (True, output) on exit code 0, otherwise (False, git's error output or the failure reason)
    """
    argv = ['git', '-c', 'color.ui=never', '-C', str(path), *args]
    try:
        result = subprocess.run(
            argv, capture_output=True, text=True, timeout=timeout, env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
        )
    except FileNotFoundError:
        return False, "command 'git' not found"
    except subprocess.TimeoutExpired:
        return False, f"command '{' '.join(argv)}' timed out after {timeout} seconds"
    except OSError as e:
        return False, f"command '{' '.join(argv)}' failed: {e}"

    output = '\n'.join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return result.returncode == 0, output


def has_upstream(path: Path) -> bool:
    """
    Tells whether the checked-out branch of the repository at path tracks a remote branch.

    False for a missing repository, a detached HEAD and a branch without tracking information.
    """
    ok, _ = _git(path, 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}')
    return ok


def check_repo(name: str, path: Path, timeout: float = 60) -> RepoCheck:
    """
    Fetches the upstream of the checked-out branch of the repository at path and reports how the
    branch stands against it. Only remote-tracking refs change, never the working tree.

    'blocked' means the branch is behind, but a local change (tracked or untracked) is in the way
    of the fast-forward; git's complaint is in the text.

    :param name: label for the result ('core' or 'plugins')
    :param path: repository directory
    :param timeout: seconds to wait for each fetch before giving up
    """

    def result(state: RepoState, behind: int = 0, ahead: int = 0, text: str = '') -> RepoCheck:
        return {'repo': name, 'state': state, 'behind': behind, 'ahead': ahead, 'text': text}

    if not has_upstream(path):
        return result('no_upstream', text='the checked-out branch has no upstream')
    ok, text = _git(path, 'fetch', timeout=timeout)
    if not ok:
        return result('unknown', text=text)
    ok, text = _git(path, 'rev-list', '--left-right', '--count', 'HEAD...@{u}')
    if not ok:
        return result('unknown', text=text)
    ahead, behind = (int(n) for n in text.split())

    if ahead and behind:
        return result('diverged', behind, ahead, 'the checked-out branch has diverged from its upstream')
    if behind:
        # dry-run two-tree merge: fails like the real fast-forward would on local changes in its way
        ok, text = _git(path, 'read-tree', '-m', '-u', '-n', 'HEAD', '@{u}')
        return result('behind' if ok else 'blocked', behind, text='' if ok else text)
    return result('ahead' if ahead else 'current', ahead=ahead)


def _head(path: Path) -> str:
    """Returns the commit id HEAD points at, or '' if it cannot be determined."""
    ok, output = _git(path, 'rev-parse', 'HEAD')
    return output if ok else ''


def changed_files(path: Path, before: str, after: str = 'HEAD') -> list[str]:
    """Returns the paths that differ between two commits of the repository at path, or [] if git fails."""
    if not before:
        return []
    ok, output = _git(path, 'diff', '--name-only', '-z', before, after)
    return [name for name in output.split('\0') if name] if ok else []


def file_at(path: Path, rev: str, relpath: str) -> str | None:
    """Returns the content of relpath at commit rev of the repository at path, or None if it does not exist there."""
    ok, output = _git(path, 'show', f'{rev}:{relpath}')
    return output if ok else None


def _advance(name: str, path: Path, git_args: tuple[str, ...], timeout: float) -> RepoPullResult:
    """Runs the given git command, which is expected to move HEAD forward, and reports the outcome."""
    before = _head(path)
    ok, text = _git(path, *git_args, timeout=timeout)
    changed = ok and _head(path) != before
    return {
        'repo': name,
        'status': 'ok' if ok else 'error',
        'text': text,
        'changed': changed,
        'before': before,
        'files': changed_files(path, before) if changed else [],
    }


def pull_repo(name: str, path: Path, timeout: float = 60) -> RepoPullResult:
    """
    Fast-forwards the checked-out branch of the repository at path to its upstream (git pull --ff-only).

    Git refuses, and the working tree stays as it was, if the branch has diverged from its upstream
    or if local changes would be overwritten.

    :param name: label for the result ('core' or 'plugins')
    :param path: repository directory
    :param timeout: seconds to wait for git before giving up
    """
    return _advance(name, path, ('pull', '--ff-only'), timeout)


def _preflight(name: str, path: Path, timeout: float) -> str:
    """Returns why the repository at path cannot be fast-forwarded to its upstream, or '' if it can."""
    check = check_repo(name, path, timeout)
    return check['text'] if check['state'] in ('no_upstream', 'unknown', 'diverged', 'blocked') else ''


def pull_all(repos: list[tuple[str, Path]], timeout: float = 60) -> list[RepoPullResult]:
    """
    Fast-forwards several repositories, in the order given, or none of them.

    Every repository is checked first. If any cannot be pulled, nothing is touched: that repository
    is reported as an error and the others as skipped. This keeps core and plugins from ending up
    at different upstream states.

    :param repos: (label, directory) per repository
    :param timeout: seconds to wait for each git call before giving up
    """
    problems = {name: _preflight(name, path, timeout) for name, path in repos}
    if any(problems.values()):
        return [
            {
                'repo': name,
                'status': 'error' if problems[name] else 'skipped',
                'text': problems[name] or 'not pulled because another repository cannot be pulled',
                'changed': False,
                'before': '',
                'files': [],
            }
            for name, _ in repos
        ]
    return [_advance(name, path, ('merge', '--ff-only', '@{u}'), timeout) for name, path in repos]
