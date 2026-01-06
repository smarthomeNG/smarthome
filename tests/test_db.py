
from . import common
import unittest
import sqlite3
import threading
import lib.db

class TestDbBase:

    def api(self, paramstyle='qmark'):
        return MockDbApi(paramstyle)

    def db(self, connect='', paramstyle='qmark', format_input='qmark'):
        return lib.db.Database('test', self.api(paramstyle=paramstyle), connect, format_input)


class TestDbTests(unittest.TestCase, TestDbBase):

    def test_paramstyle_supported(self):
        self.db(paramstyle='qmark')
        self.db(paramstyle='format')
        self.db(paramstyle='numeric')
        self.db(paramstyle='pyformat')

    def test_paramstyle_not_supported(self):
#        with self.assertRaisesRegex(Exception, 'driver format style .* not supported'):
#            self.db(paramstyle='wrongformat')
        test_db = self.db(paramstyle='wrongformat') # 'driver format style .* not supported'
        self.assertFalse(test_db.api_initialized)

    def test_connect(self):
        db = self.db(connect='host:server | user:username | password:secret')
        db.connect()
        args = db._dbapi.connect_kwargs
        self.assertTrue('host' in args)
        self.assertEqual('server', args['host'])
        self.assertTrue('user' in args)
        self.assertEqual('username', args['user'])
        self.assertTrue('password' in args)
        self.assertEqual('secret', args['password'])

    def test_connect_set_connected(self):
        db = self.db()
        self.assertFalse(db.connected())

        db.connect()
        self.assertTrue(db.connected())

    def test_close(self):
        db = self.db()
        db.connect()
        conn = db._conn
        db.close()
        self.assertTrue(conn.close_kwargs is not None)

    def test_close_set_connected(self):
        db = self.db()
        db.connect()
        db.close()
        self.assertFalse(db.connected())

    def test_lock(self):
        db = self.db()
        self.assertTrue(db.lock())

    def test_lock_already_locked(self):
        db = self.db()
        db.lock()
        self.assertFalse(db.lock(0))

    def test_release(self):
        db = self.db()
        db.lock()
        db.release()

    def test_release_not_locked(self):
        db = self.db()
        with self.assertRaisesRegex(Exception, 'release unlocked lock'):
	        db.release()

    def test_commit(self):
        db = self.db()
        db.connect()
        db.commit()
        self.assertTrue(db._conn.commit_kwargs is not None)

    def test_rollback(self):
        db = self.db()
        db.connect()
        db.rollback()
        self.assertTrue(db._conn.rollback_kwargs is not None)

    def test_cursor(self):
        db = self.db()
        db.connect()
        self.assertTrue(db.cursor() is not None)
        self.assertTrue(db._conn.cursor_kwargs is not None)

    def test_setup(self):
        db = self.db()
        db.connect()
        db.setup({
          1 : ['ROLLOUT 1', 'ROLLBACK 1'],
          2 : ['ROLLOUT 2', 'ROLLBACK 2']
        })

        # Statement 0: SELECT version - ignore
        # Statement 1: Rollout statment 1 - check:
        self.assertEqual("ROLLOUT 1", db._conn.cursor_return.execute_kwargs[1][0])
        # Statement 2: INSERT version - ignore
        # Statement 3: Rollout statment 2 - check:
        self.assertEqual("ROLLOUT 2", db._conn.cursor_return.execute_kwargs[3][0])
        # Statement 4: INSERT version - check
        self.assertEqual("INSERT INTO test_version", db._conn.cursor_return.execute_kwargs[4][0][0:24])
        self.assertEqual(2, db._conn.cursor_return.execute_kwargs[4][1][0])

    def test_execute_internal_cursor(self):
        db = self.db()
        db.connect()
        db.execute("select 1")
        self.assertEqual("select 1", db._conn.cursor_return.execute_kwargs[0][0])

    def test_execute_custom_cursor(self):
        db = self.db()
        db.connect()
        cur = db.cursor()
        db.execute("select 1", cur=cur)
        self.assertEqual("select 1", cur.execute_kwargs[0][0])

    def test_verify(self):
        db = self.db()
        db.connect()
        db.verify()
        self.assertEqual("SELECT 1", db._conn.cursor_return.execute_kwargs[0][0])

    def test_fetchone(self):
        db = self.db()
        db.connect()
        db.fetchone("SELECT 1")

    def test_fetchall(self):
        db = self.db()
        db.connect()
        db.fetchall("SELECT 1")


class DbQueryBaseTests(TestDbBase):

    format = None
    query = None
    args = (1, 'test')

    def execute(self, sql, args, format_input='qmark', paramstyle='pyformat'):
        db = self.db(paramstyle=paramstyle, format_input=format_input)
        db.connect()
        db.execute(sql, args)
        return db._conn.cursor_return.execute_kwargs[0]

    def test_execute_qmark(self):
        args = self.execute(self.query, self.args, self.format, 'qmark')
        self.assertEqual('SELECT * FROM TABLE WHERE ID = ? AND Name = ?', args[0])
        self.assertEqual([1, 'test'], args[1])

    def test_execute_format(self):
        args = self.execute(self.query, self.args, self.format, 'format')
        self.assertEqual('SELECT * FROM TABLE WHERE ID = %s AND Name = %s', args[0])
        self.assertEqual([1, 'test'], args[1])

    def test_execute_numeric(self):
        args = self.execute(self.query, self.args, self.format, 'numeric')
        self.assertEqual('SELECT * FROM TABLE WHERE ID = :1 AND Name = :2', args[0])
        self.assertEqual([1, 'test'], args[1])

    def test_execute_pyformat(self):
        args = self.execute(self.query, self.args, self.format, 'pyformat')
        self.assertEqual('SELECT * FROM TABLE WHERE ID = %(arg1)s AND Name = %(arg2)s', args[0])
        self.assertEqual({'arg1':1, 'arg2':'test'}, args[1])

    def test_execute_same_format_input_is_output(self):
        args = self.execute(self.query_formatter, self.args, self.format, self.format)
        self.assertEqual(self.query_formatter, args[0])

    def _assert_argument_reuse(self, args, output_format):
        if self.format == output_format:
          args_list = list(self.args)
          args_dict = self.args
        else:
          args_list = self.expect_args_argsreuse_list
          args_dict = self.expect_args_argsreuse_dict
        if type(args[1]) == list:
          self.assertEqual(args_list, args[1])
        else:
          self.assertEqual(args_dict, dict(args[1]))

    def test_execute_argument_reuse_qmark(self):
        args = self.execute(self.query_argsreuse, self.args, self.format, 'qmark')
        self._assert_argument_reuse(args, 'qmark')

    def test_execute_argument_reuse_format(self):
        args = self.execute(self.query_argsreuse, self.args, self.format, 'format')
        self._assert_argument_reuse(args, 'format')

    def test_execute_argument_reuse_numeric(self):
        args = self.execute(self.query_argsreuse, self.args, self.format, 'numeric')
        self._assert_argument_reuse(args, 'numeric')

    def test_execute_argument_reuse_named(self):
        args = self.execute(self.query_argsreuse, self.args, self.format, 'named')
        self._assert_argument_reuse(args, 'named')

    def test_execute_argument_reuse_pyformat(self):
        args = self.execute(self.query_argsreuse, self.args, self.format, 'pyformat')
        self._assert_argument_reuse(args, 'pyformat')


class TestDbQueryQmark(unittest.TestCase, DbQueryBaseTests):

    format = 'qmark'
    query = 'SELECT * FROM TABLE WHERE ID = ? AND Name = ?'
    query_formatter = 'SELECT * FROM TABLE WHERE ID = ? AND Name = ?'
    query_argsreuse = 'SELECT * FROM TABLE WHERE ID = ? AND Name = ?'
    expect_args_argsreuse_list = [1, 'test']
    expect_args_argsreuse_dict = {'arg1' : 1, 'arg2' : 'test'}


class TestDbQueryFormat(unittest.TestCase, DbQueryBaseTests):

    format = 'format'
    query = 'SELECT * FROM TABLE WHERE ID = %s AND Name = %s'
    query_formatter = 'SELECT * FROM TABLE WHERE ID = %d AND Name = %s'
    query_argsreuse = 'SELECT * FROM TABLE WHERE ID = %s AND Name = %s'
    expect_args_argsreuse_list = [1, 'test']
    expect_args_argsreuse_dict = {'arg1' : 1, 'arg2' : 'test'}


class TestDbQueryNumeric(unittest.TestCase, DbQueryBaseTests):

    format = 'numeric'
    query = 'SELECT * FROM TABLE WHERE ID = :1 AND Name = :2'
    query_formatter = 'SELECT * FROM TABLE WHERE ID = :1 AND Name = :2'
    query_argsreuse = 'SELECT * FROM TABLE WHERE ID = :2 AND Name = :2'
    expect_args_argsreuse_list = ['test', 'test']
    expect_args_argsreuse_dict = {'arg2' : 'test'}


class TestDbQueryNamed(unittest.TestCase, DbQueryBaseTests):

    format = 'named'
    args = {'arg1' : 1, 'arg2' : 'test'}
    query = 'SELECT * FROM TABLE WHERE ID = :arg1 AND Name = :arg2'
    query_formatter = 'SELECT * FROM TABLE WHERE ID = :arg1 AND Name = :arg2'
    query_argsreuse = 'SELECT * FROM TABLE WHERE ID = :arg2 AND Name = :arg2'
    expect_args_argsreuse_list = ['test', 'test']
    expect_args_argsreuse_dict = {'arg2' : 'test'}


class TestDbQueryPyformat(unittest.TestCase, DbQueryBaseTests):

    format = 'pyformat'
    args = {'arg1' : 1, 'arg2' : 'test'}
    query = 'SELECT * FROM TABLE WHERE ID = %(arg1)s AND Name = %(arg2)s'
    query_formatter = 'SELECT * FROM TABLE WHERE ID = %(arg1)d AND Name = %(arg2)s'
    query_argsreuse = 'SELECT * FROM TABLE WHERE ID = %(arg2)d AND Name = %(arg2)s'
    expect_args_argsreuse_list = ['test', 'test']
    expect_args_argsreuse_dict = {'arg2' : 'test'}

    def test_execute_format_always_uses_strings(self):
        """Converting pyformat to format should always use %s
		See also: https://github.com/smarthomeNG/smarthome/pull/131/commits/bcaa491f91251e2129fa40958bad09cc623d9732
        """
        args = self.execute('SELECT * FROM TABLE WHERE ID = %(arg1)d AND Name = %(arg2)s', self.args, self.format, 'format')
        self.assertEqual('SELECT * FROM TABLE WHERE ID = %s AND Name = %s', args[0])


class MockDbApi():

    def __init__(self, paramstyle):
        self.paramstyle = paramstyle
        self.connected_kwargs = None

    def connect(self, **kwargs):
        self.connect_kwargs = kwargs if kwargs is not None else True
        return MockDbApiConnection()


class MockDbApiConnection():

    def __init__(self):
        self.close_kwargs = None
        self.commit_kwargs = None
        self.rollback_kwargs = None
        self.cursor_kwargs = None
        self.cursor_return = None

    def close(self, **kwargs):
        self.close_kwargs = kwargs if kwargs is not None else True

    def commit(self, **kwargs):
        self.commit_kwargs = kwargs if kwargs is not None else True

    def rollback(self, **kwargs):
        self.rollback_kwargs = kwargs if kwargs is not None else True

    def cursor(self, **kwargs):
        self.cursor_kwargs = kwargs if kwargs is not None else True
        self.cursor_return = MockDbApiCursor()
        return self.cursor_return


class MockDbApiCursor():

    def __init__(self):
        self.execute_kwargs = []
        self.close_kwargs = None

    def execute(self, *kwargs):
        self.execute_kwargs.append(kwargs if kwargs is not None else True)
        return {}

    def close(self, **kwargs):
        self.close_kwargs = kwargs if kwargs is not None else True

    def fetchone(self, **kwargs):
        return [0]

    def fetchall(self, **kwargs):
        return [[0]]


if __name__ == '__main__':
    unittest.main(verbosity=2)

