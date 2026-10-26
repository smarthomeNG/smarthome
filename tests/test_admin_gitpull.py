"""
Tests for modules/admin/gitpull.py - the git logic behind shngadmin's "pull core / pull plugins /
pull all" buttons (PUT /api/server/pull_*). All tests run real git against throwaway repositories.
"""

from modules.admin.gitpull import check_repo, has_upstream, pull_all, pull_repo

from .git_fixtures import GitTestCase, RepoPair, commit_file, git


class TestHasUpstream(GitTestCase):
    def test_clone_tracking_a_remote_branch_has_upstream(self):
        pair = RepoPair(self.root, 'core')
        self.assertTrue(has_upstream(pair.clone))

    def test_repo_without_remote_has_no_upstream(self):
        pair = RepoPair(self.root, 'core')
        git(pair.clone, 'remote', 'remove', 'origin')
        self.assertFalse(has_upstream(pair.clone))

    def test_local_branch_without_tracking_has_no_upstream(self):
        pair = RepoPair(self.root, 'core')
        git(pair.clone, 'switch', '-q', '-c', 'feature')
        self.assertFalse(has_upstream(pair.clone))

    def test_detached_head_has_no_upstream(self):
        pair = RepoPair(self.root, 'core')
        git(pair.clone, 'checkout', '-q', '--detach')
        self.assertFalse(has_upstream(pair.clone))

    def test_missing_directory_has_no_upstream(self):
        self.assertFalse(has_upstream(self.root / 'nope'))


class TestCheckRepo(GitTestCase):
    def test_counts_the_upstream_commits_it_is_behind_without_touching_the_checkout(self):
        pair = RepoPair(self.root, 'core')
        pair.push_upstream_commit('f.txt', 'two\n')
        pair.push_upstream_commit('f.txt', 'three\n')
        head = git(pair.clone, 'rev-parse', 'HEAD')

        check = check_repo('core', pair.clone)

        self.assertEqual(check, {'repo': 'core', 'state': 'behind', 'behind': 2, 'ahead': 0, 'text': ''})
        self.assertEqual(git(pair.clone, 'rev-parse', 'HEAD'), head)
        self.assertEqual((pair.clone / 'f.txt').read_text(), 'one\n')

    def test_repo_in_sync_with_its_upstream_is_current(self):
        pair = RepoPair(self.root, 'core')

        check = check_repo('core', pair.clone)

        self.assertEqual(check, {'repo': 'core', 'state': 'current', 'behind': 0, 'ahead': 0, 'text': ''})

    def test_repo_with_only_local_commits_is_ahead(self):
        pair = RepoPair(self.root, 'core')
        commit_file(pair.clone, 'local.txt', 'local\n')

        check = check_repo('core', pair.clone)

        self.assertEqual((check['state'], check['ahead'], check['behind']), ('ahead', 1, 0))

    def test_repo_with_commits_on_both_sides_is_diverged(self):
        pair = RepoPair(self.root, 'core')
        pair.push_upstream_commit('f.txt', 'upstream\n')
        commit_file(pair.clone, 'f.txt', 'local\n')

        check = check_repo('core', pair.clone)

        self.assertEqual((check['state'], check['ahead'], check['behind']), ('diverged', 1, 1))
        self.assertTrue(check['text'])

    def test_local_change_in_the_way_of_the_pull_is_blocked(self):
        pair = RepoPair(self.root, 'core')
        pair.push_upstream_commit()
        (pair.clone / 'f.txt').write_text('local edit\n')

        check = check_repo('core', pair.clone)

        self.assertEqual((check['state'], check['behind']), ('blocked', 1))
        self.assertIn('f.txt', check['text'])

    def test_untracked_file_in_the_way_of_the_pull_is_blocked(self):
        pair = RepoPair(self.root, 'core')
        pair.push_upstream_commit('new.txt', 'upstream\n')
        (pair.clone / 'new.txt').write_text('mine\n')

        check = check_repo('core', pair.clone)

        self.assertEqual(check['state'], 'blocked')

    def test_local_change_in_an_untouched_file_leaves_the_repo_behind(self):
        pair = RepoPair(self.root, 'core')
        commit_file(pair.upstream, 'g.txt', 'g\n')
        git(pair.clone, 'pull', '-q')
        pair.push_upstream_commit()
        (pair.clone / 'g.txt').write_text('local edit\n')

        self.assertEqual(check_repo('core', pair.clone)['state'], 'behind')

    def test_branch_without_upstream_has_no_upstream(self):
        pair = RepoPair(self.root, 'core')
        git(pair.clone, 'switch', '-q', '-c', 'feature')

        check = check_repo('core', pair.clone)

        self.assertEqual((check['state'], check['behind'], check['ahead']), ('no_upstream', 0, 0))

    def test_unreachable_upstream_is_unknown(self):
        pair = RepoPair(self.root, 'core')
        git(pair.clone, 'remote', 'set-url', 'origin', str(self.root / 'gone'))

        check = check_repo('core', pair.clone)

        self.assertEqual(check['state'], 'unknown')
        self.assertTrue(check['text'])

    def test_timeout_is_unknown(self):
        pair = RepoPair(self.root, 'core')

        check = check_repo('core', pair.clone, timeout=0)

        self.assertEqual(check['state'], 'unknown')
        self.assertIn('timed out', check['text'])


class TestPullRepo(GitTestCase):
    def test_fast_forwards_to_the_upstream_commit(self):
        pair = RepoPair(self.root, 'core')
        pair.push_upstream_commit()

        result = pull_repo('core', pair.clone)

        self.assertEqual(result['repo'], 'core')
        self.assertEqual(result['status'], 'ok')
        self.assertTrue(result['changed'])
        self.assertEqual((pair.clone / 'f.txt').read_text(), 'two\n')

    def test_up_to_date_repo_is_ok_but_unchanged(self):
        pair = RepoPair(self.root, 'core')

        result = pull_repo('core', pair.clone)

        self.assertEqual(result['status'], 'ok')
        self.assertFalse(result['changed'])

    def test_repo_without_upstream_is_an_error(self):
        pair = RepoPair(self.root, 'core')
        git(pair.clone, 'switch', '-q', '-c', 'feature')

        result = pull_repo('core', pair.clone)

        self.assertEqual(result['status'], 'error')
        self.assertFalse(result['changed'])
        self.assertTrue(result['text'])

    def test_diverged_branch_is_an_error_and_stays_as_it_was(self):
        pair = RepoPair(self.root, 'core')
        pair.push_upstream_commit('f.txt', 'upstream\n')
        commit_file(pair.clone, 'f.txt', 'local\n')
        head = git(pair.clone, 'rev-parse', 'HEAD')

        result = pull_repo('core', pair.clone)

        self.assertEqual(result['status'], 'error')
        self.assertFalse(result['changed'])
        self.assertEqual(git(pair.clone, 'rev-parse', 'HEAD'), head)
        self.assertEqual((pair.clone / 'f.txt').read_text(), 'local\n')

    def test_local_change_that_the_pull_would_overwrite_is_kept(self):
        pair = RepoPair(self.root, 'core')
        pair.push_upstream_commit()
        (pair.clone / 'f.txt').write_text('local edit\n')

        result = pull_repo('core', pair.clone)

        self.assertEqual(result['status'], 'error')
        self.assertFalse(result['changed'])
        self.assertEqual((pair.clone / 'f.txt').read_text(), 'local edit\n')

    def test_local_change_in_an_untouched_file_does_not_block_the_pull(self):
        pair = RepoPair(self.root, 'core')
        commit_file(pair.upstream, 'g.txt', 'g\n')
        git(pair.clone, 'pull', '-q')
        pair.push_upstream_commit()
        (pair.clone / 'g.txt').write_text('local edit\n')

        result = pull_repo('core', pair.clone)

        self.assertEqual(result['status'], 'ok')
        self.assertTrue(result['changed'])
        self.assertEqual((pair.clone / 'g.txt').read_text(), 'local edit\n')

    def test_timeout_is_an_error(self):
        pair = RepoPair(self.root, 'core')
        pair.push_upstream_commit()

        result = pull_repo('core', pair.clone, timeout=0)

        self.assertEqual(result['status'], 'error')
        self.assertIn('timed out', result['text'])


class TestPullAll(GitTestCase):
    def setUp(self):
        super().setUp()
        self.core = RepoPair(self.root, 'core')
        self.plugins = RepoPair(self.root, 'plugins')
        self.repos = [('core', self.core.clone), ('plugins', self.plugins.clone)]

    def test_pulls_core_then_plugins(self):
        self.core.push_upstream_commit()
        self.plugins.push_upstream_commit()

        results = pull_all(self.repos)

        self.assertEqual([r['repo'] for r in results], ['core', 'plugins'])
        self.assertEqual([r['status'] for r in results], ['ok', 'ok'])
        self.assertEqual([r['changed'] for r in results], [True, True])
        self.assertEqual((self.core.clone / 'f.txt').read_text(), 'two\n')
        self.assertEqual((self.plugins.clone / 'f.txt').read_text(), 'two\n')

    def test_repo_without_upstream_blocks_the_whole_pull(self):
        self.core.push_upstream_commit()
        self.plugins.push_upstream_commit()
        git(self.plugins.clone, 'switch', '-q', '-c', 'feature')
        core_head = git(self.core.clone, 'rev-parse', 'HEAD')

        results = pull_all(self.repos)

        self.assertEqual({r['repo']: r['status'] for r in results}, {'core': 'skipped', 'plugins': 'error'})
        self.assertFalse(any(r['changed'] for r in results))
        self.assertEqual(git(self.core.clone, 'rev-parse', 'HEAD'), core_head)

    def test_diverged_repo_blocks_the_whole_pull(self):
        self.core.push_upstream_commit()
        self.plugins.push_upstream_commit('f.txt', 'upstream\n')
        commit_file(self.plugins.clone, 'f.txt', 'local\n')
        core_head = git(self.core.clone, 'rev-parse', 'HEAD')

        results = pull_all(self.repos)

        self.assertEqual({r['repo']: r['status'] for r in results}, {'core': 'skipped', 'plugins': 'error'})
        self.assertEqual(git(self.core.clone, 'rev-parse', 'HEAD'), core_head)

    def test_repo_that_is_only_ahead_of_its_upstream_does_not_block_the_pull(self):
        self.core.push_upstream_commit()
        commit_file(self.plugins.clone, 'local.txt', 'local\n')
        plugins_head = git(self.plugins.clone, 'rev-parse', 'HEAD')

        results = pull_all(self.repos)

        self.assertEqual({r['repo']: r['status'] for r in results}, {'core': 'ok', 'plugins': 'ok'})
        self.assertEqual({r['repo']: r['changed'] for r in results}, {'core': True, 'plugins': False})
        self.assertEqual(git(self.plugins.clone, 'rev-parse', 'HEAD'), plugins_head)

    def test_local_change_that_the_pull_would_overwrite_blocks_the_whole_pull(self):
        self.core.push_upstream_commit()
        self.plugins.push_upstream_commit()
        (self.plugins.clone / 'f.txt').write_text('local edit\n')
        core_head = git(self.core.clone, 'rev-parse', 'HEAD')

        results = pull_all(self.repos)

        self.assertEqual({r['repo']: r['status'] for r in results}, {'core': 'skipped', 'plugins': 'error'})
        self.assertEqual(git(self.core.clone, 'rev-parse', 'HEAD'), core_head)
        self.assertEqual((self.plugins.clone / 'f.txt').read_text(), 'local edit\n')

    def test_untracked_file_that_the_pull_would_overwrite_blocks_the_whole_pull(self):
        self.core.push_upstream_commit()
        self.plugins.push_upstream_commit('new.txt', 'upstream\n')
        (self.plugins.clone / 'new.txt').write_text('mine\n')
        core_head = git(self.core.clone, 'rev-parse', 'HEAD')

        results = pull_all(self.repos)

        self.assertEqual({r['repo']: r['status'] for r in results}, {'core': 'skipped', 'plugins': 'error'})
        self.assertEqual(git(self.core.clone, 'rev-parse', 'HEAD'), core_head)
        self.assertEqual((self.plugins.clone / 'new.txt').read_text(), 'mine\n')

    def test_local_change_in_an_untouched_file_does_not_block_the_pull(self):
        commit_file(self.plugins.upstream, 'g.txt', 'g\n')
        git(self.plugins.clone, 'pull', '-q')
        self.core.push_upstream_commit()
        self.plugins.push_upstream_commit()
        (self.plugins.clone / 'g.txt').write_text('local edit\n')

        results = pull_all(self.repos)

        self.assertEqual([r['status'] for r in results], ['ok', 'ok'])
        self.assertEqual((self.plugins.clone / 'g.txt').read_text(), 'local edit\n')

    def test_failing_fetch_blocks_the_whole_pull(self):
        self.core.push_upstream_commit()
        self.plugins.push_upstream_commit()
        git(self.plugins.clone, 'remote', 'set-url', 'origin', str(self.root / 'gone'))
        core_head = git(self.core.clone, 'rev-parse', 'HEAD')

        results = pull_all(self.repos)

        self.assertEqual({r['repo']: r['status'] for r in results}, {'core': 'skipped', 'plugins': 'error'})
        self.assertEqual(git(self.core.clone, 'rev-parse', 'HEAD'), core_head)

    def test_timeout_blocks_the_whole_pull(self):
        self.core.push_upstream_commit()
        self.plugins.push_upstream_commit()
        core_head = git(self.core.clone, 'rev-parse', 'HEAD')

        results = pull_all(self.repos, timeout=0)

        self.assertTrue(all(r['status'] != 'ok' for r in results))
        self.assertTrue(any('timed out' in r['text'] for r in results))
        self.assertEqual(git(self.core.clone, 'rev-parse', 'HEAD'), core_head)


class TestPullResultFiles(GitTestCase):
    def test_pull_repo_lists_the_changed_files(self):
        pair = RepoPair(self.root, 'core')
        old_head = git(pair.clone, 'rev-parse', 'HEAD')
        pair.push_upstream_commit('f.txt', 'two\n')
        (pair.upstream / 'sub').mkdir()
        pair.push_upstream_commit('sub/g.txt', 'new\n')

        result = pull_repo('core', pair.clone)

        self.assertEqual(sorted(result['files']), ['f.txt', 'sub/g.txt'])
        self.assertEqual(result['before'], old_head)

    def test_pull_all_lists_the_changed_files_per_repository(self):
        core = RepoPair(self.root, 'core')
        plugins = RepoPair(self.root, 'plugins')
        plugins.push_upstream_commit('g.txt', 'new\n')

        results = pull_all([('core', core.clone), ('plugins', plugins.clone)])

        self.assertEqual([(r['repo'], r['files']) for r in results], [('core', []), ('plugins', ['g.txt'])])

    def test_nothing_changed_lists_no_files(self):
        pair = RepoPair(self.root, 'core')
        self.assertEqual(pull_repo('core', pair.clone)['files'], [])


class TestPlainOutput(GitTestCase):
    def test_output_has_no_color_codes_even_if_git_is_configured_to_always_color(self):
        pair = RepoPair(self.root, 'core')
        git(pair.clone, 'config', 'color.ui', 'always')
        pair.push_upstream_commit('f.txt', 'two\n')

        result = pull_repo('core', pair.clone)

        self.assertIn('f.txt', result['text'])
        self.assertNotIn('\x1b', result['text'])
