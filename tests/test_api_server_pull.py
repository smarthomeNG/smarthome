"""
Tests for modules/admin/api_server.py's ServerController pull actions - the backend for shngadmin's
"pull core / pull plugins / pull all" buttons (PUT /api/server/pull_*). They run against real git
repositories: the core checkout with the plugins checkout nested in its plugins/ directory.
"""

import json

from . import common

common.register_shng_log_levels()

from modules.admin.api_server import ServerController

from .git_fixtures import GitTestCase, RepoPair, git


class _FakeSh:
    """Stands in for the SmartHome instance; its base directory is the core checkout under test."""

    def __init__(self, basedir):
        self.basedir = str(basedir)
        self.shng_status = {'code': 20, 'text': ''}

    def get_basedir(self):
        return self.basedir

    def get_config_dir(self, name):
        return common.BASE + '/' + name


class _FakeModule:
    def __init__(self, sh):
        self._sh = sh


class PullTestCase(GitTestCase):
    """A core checkout with a nested plugins checkout, both tracking their own upstream."""

    def setUp(self):
        super().setUp()
        self.core = RepoPair(self.root, 'core')
        self.plugins = RepoPair(self.root, 'plugins', clone=self.core.clone / 'plugins')
        self.controller = ServerController(_FakeModule(_FakeSh(self.core.clone)))

    def put(self, action):
        return json.loads(self.controller.update(action))


class TestPullCore(PullTestCase):
    def test_pulls_the_core_checkout(self):
        self.core.push_upstream_commit()

        response = self.put('pull_core')

        self.assertEqual(response['result'], 'ok')
        self.assertEqual([(r['repo'], r['status'], r['changed']) for r in response['repos']], [('core', 'ok', True)])
        self.assertEqual((self.core.clone / 'f.txt').read_text(), 'two\n')

    def test_leaves_the_plugins_checkout_alone(self):
        self.core.push_upstream_commit()
        self.plugins.push_upstream_commit()
        plugins_head = git(self.plugins.clone, 'rev-parse', 'HEAD')

        self.put('pull_core')

        self.assertEqual(git(self.plugins.clone, 'rev-parse', 'HEAD'), plugins_head)

    def test_branch_without_upstream_is_an_error(self):
        git(self.core.clone, 'switch', '-q', '-c', 'feature')

        response = self.put('pull_core')

        self.assertEqual(response['result'], 'error')
        self.assertEqual([(r['repo'], r['status']) for r in response['repos']], [('core', 'error')])


class TestPullPlugins(PullTestCase):
    def test_pulls_the_plugins_checkout_only(self):
        self.core.push_upstream_commit()
        self.plugins.push_upstream_commit()
        core_head = git(self.core.clone, 'rev-parse', 'HEAD')

        response = self.put('pull_plugins')

        self.assertEqual(response['result'], 'ok')
        self.assertEqual([(r['repo'], r['changed']) for r in response['repos']], [('plugins', True)])
        self.assertEqual((self.plugins.clone / 'f.txt').read_text(), 'two\n')
        self.assertEqual(git(self.core.clone, 'rev-parse', 'HEAD'), core_head)


class TestPullAll(PullTestCase):
    def test_pulls_core_and_plugins(self):
        self.core.push_upstream_commit()
        self.plugins.push_upstream_commit()

        response = self.put('pull_all')

        self.assertEqual(response['result'], 'ok')
        self.assertEqual([(r['repo'], r['changed']) for r in response['repos']], [('core', True), ('plugins', True)])

    def test_pulls_nothing_if_one_checkout_cannot_be_pulled(self):
        self.core.push_upstream_commit()
        self.plugins.push_upstream_commit()
        git(self.plugins.clone, 'switch', '-q', '-c', 'feature')
        core_head = git(self.core.clone, 'rev-parse', 'HEAD')

        response = self.put('pull_all')

        self.assertEqual(response['result'], 'error')
        self.assertEqual(
            [(r['repo'], r['status']) for r in response['repos']], [('core', 'skipped'), ('plugins', 'error')]
        )
        self.assertEqual(git(self.core.clone, 'rev-parse', 'HEAD'), core_head)


class TestPullBusy(PullTestCase):
    def test_second_pull_is_refused_while_one_is_running(self):
        self.core.push_upstream_commit()
        core_head = git(self.core.clone, 'rev-parse', 'HEAD')
        self.assertTrue(self.controller._pull_lock.acquire(blocking=False))
        self.addCleanup(self.controller._pull_lock.release)

        response = self.put('pull_core')

        self.assertEqual(response['result'], 'error')
        self.assertEqual(response['repos'], [])
        self.assertEqual(git(self.core.clone, 'rev-parse', 'HEAD'), core_head)


class TestPullAvailability(PullTestCase):
    def test_reports_per_checkout_whether_it_has_an_upstream(self):
        self.assertEqual(self.controller.pull_availability, {'core': True, 'plugins': True})
        git(self.plugins.clone, 'switch', '-q', '-c', 'feature')
        self.assertEqual(self.controller.pull_availability, {'core': True, 'plugins': False})

    def test_missing_plugins_checkout_is_not_available(self):
        controller = ServerController(_FakeModule(_FakeSh(self.root / 'elsewhere')))
        self.assertEqual(controller.pull_availability, {'core': False, 'plugins': False})


class TestPullStatus(PullTestCase):
    def get(self, action):
        return json.loads(self.controller.read(action))

    def test_reports_each_checkout_against_its_upstream(self):
        self.core.push_upstream_commit()

        response = self.get('pull_status')

        self.assertEqual(response['result'], 'ok')
        self.assertEqual(
            [(r['repo'], r['state'], r['behind']) for r in response['repos']],
            [('core', 'behind', 1), ('plugins', 'current', 0)],
        )

    def test_changes_nothing_in_the_checkouts(self):
        self.core.push_upstream_commit()
        core_head = git(self.core.clone, 'rev-parse', 'HEAD')

        self.get('pull_status')

        self.assertEqual(git(self.core.clone, 'rev-parse', 'HEAD'), core_head)

    def test_is_refused_while_a_pull_is_running(self):
        self.assertTrue(self.controller._pull_lock.acquire(blocking=False))
        self.addCleanup(self.controller._pull_lock.release)

        response = self.get('pull_status')

        self.assertEqual(response['result'], 'error')
        self.assertEqual(response['repos'], [])
