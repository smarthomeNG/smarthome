import unittest
import pathlib
from . import common
import lib.config

verbose = True

class ConfigBaseTests:
    fmt = None

    @classmethod
    def setUpClass(cls):
        if cls is ConfigBaseTests:
            raise unittest.SkipTest("Skip BaseTest tests, it's a base class")
        super(ConfigBaseTests, cls).setUpClass()

    def config(self, name):
        to_parse = str(pathlib.Path(common.BASE) / 'tests/resources/config_{}.{}'.format(name, self.fmt))
        return lib.config.parse(to_parse)

    def test_read_ignores_starting_digits(self):
        conf = self.config('digits')
        self.assertEqual(1, len(conf['digits']))
        self.assertFalse('123' in conf['digits']['item'])

    def test_read_ignores_set(self):
        conf = self.config('reserved')
        self.assertEqual(1, len(conf['reserved']))
        self.assertEqual('test', conf['reserved']['item']['set'])

    def test_read_ignores_keyword(self):
        conf = self.config('keyword')
        self.assertEqual(1, len(conf['keyword']))
        self.assertEqual('test', conf['keyword']['item']['global'])

    def test_read_ignores_invalidchars(self):
        conf = self.config('invalidchars')
        self.assertEqual(1, len(conf['invalidchars']))
        self.assertFalse('invalid.dot' in conf['invalidchars']['item'])

    def test_read_sections(self):
        conf = self.config('sections')
        self.assertIsInstance(conf, dict)
        self.assertTrue('section1' in conf)
        self.assertTrue('section2' in conf)

    def test_read_keyvalues(self):
        conf = self.config('keyvalues')
        self.assertIsInstance(conf['section'], dict)
        self.assertTrue('key1' in conf['section'])
        self.assertTrue('key2' in conf['section'])
        self.assertEqual(conf['section']['key1'], 'value1')
        self.assertEqual(conf['section']['key2'], 'value2')

    def test_read_keyvalues_quotes(self):
        conf = self.config('keyvalues')
        self.assertIsInstance(conf['section'], dict)
        self.assertTrue('key1_quotes' in conf['section'])
        self.assertTrue('key2_quotes' in conf['section'])
        self.assertEqual(conf['section']['key1_quotes'], 'value1')
        self.assertEqual(conf['section']['key2_quotes'], 'value2')

    def test_read_lists(self):
        conf = self.config('lists')
        self.assertIsInstance(conf['section']['list'], list)
        self.assertTrue('value1' in conf['section']['list'])
        self.assertTrue('value2' in conf['section']['list'])
        self.assertTrue('value3' in conf['section']['list'])

    def test_confread_lists_spaces(self):
        conf = self.config('lists')
        self.assertIsInstance(conf['section']['list_spaces'], list)
        self.assertTrue('value1' in conf['section']['list_spaces'])
        self.assertTrue('value2' in conf['section']['list_spaces'])
        self.assertTrue('value3' in conf['section']['list_spaces'])

    def test_read_lists_quotes(self):
        conf = self.config('lists')
        self.assertIsInstance(conf['section']['list_quotes'], list)
        self.assertTrue('value1' in conf['section']['list_quotes'])
        self.assertTrue('value2' in conf['section']['list_quotes'])
        self.assertTrue('value3' in conf['section']['list_quotes'])

    def test_read_lists_quotes_spaces(self):
        conf = self.config('lists')
        self.assertIsInstance(conf['section']['list_quotes_spaces'], list)
        self.assertTrue('value1' in conf['section']['list_quotes_spaces'])
        self.assertTrue('value2' in conf['section']['list_quotes_spaces'])
        self.assertTrue('value3' in conf['section']['list_quotes_spaces'])

    def test_read_structure(self):
        conf = self.config('structure')
        self.assertTrue('child1' in conf['parent1'])
        self.assertTrue('child2' in conf['parent1'])
        self.assertTrue('child1' in conf['parent2'])
        self.assertTrue('child2' in conf['parent2'])

    def test_read_structure(self):
        conf = self.config('structure')
        self.assertTrue('attr1' in conf['parent1'])
        self.assertEqual('value1', conf['parent1']['attr1'])
        self.assertTrue('child1' in conf['parent1'])
        self.assertTrue('attr2' in conf['parent1']['child1'])
        self.assertEqual('value2', conf['parent1']['child1']['attr2'])
        self.assertTrue('child2' in conf['parent1'])
        self.assertTrue('attr3' in conf['parent1']['child2'])
        self.assertEqual('value3', conf['parent1']['child2']['attr3'])
        self.assertTrue('attr4' in conf['parent2'])
        self.assertEqual('value4', conf['parent2']['attr4'])
        self.assertTrue('child1' in conf['parent2'])
        self.assertTrue('attr5' in conf['parent2']['child1'])
        self.assertEqual('value5', conf['parent2']['child1']['attr5'])
        self.assertTrue('child2' in conf['parent2'])
        self.assertTrue('attr6' in conf['parent2']['child2'])
        self.assertEqual('value6', conf['parent2']['child2']['attr6'])


class TestConfigConf( unittest.TestCase,ConfigBaseTests):

    fmt = 'conf'

    def test_confread_ignores_empty_name(self):
        if verbose == True:
            print()
            print('=== TestConfigConf:')
        conf = self.config('empty')
        self.assertEqual(0, len(conf['empty']))

    def test_confread_multiline(self):
        conf = self.config('keyvalues')
        self.assertEqual(conf['section']['key_multiline'], 'line1line2')
        self.assertEqual(conf['section']['key_multiline_space'], 'line1 line2')
        self.assertEqual(conf['section']['key_multiline_quotes'], 'line1line2')
    

class TestConfigYaml(unittest.TestCase,ConfigBaseTests):

    fmt = 'yaml'

    def test_yamlread_multiline(self):
        if verbose == True:
            print()
            print('=== TestConfigYaml:')
        conf = self.config('keyvalues')
        self.assertEqual(conf['section']['key_multiline'], 'line1line2')
        self.assertEqual(conf['section']['key_multiline_quotes'], 'line1line2')


if __name__ == '__main__':
    unittest.main(verbosity=2)
