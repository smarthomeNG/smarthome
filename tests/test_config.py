
import common
import unittest
import lib.config

class TestConfig(unittest.TestCase):

    def config(self, name):
        return lib.config.parse('resources/' + name + '.conf')

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

    def test_read_lists_spaces(self):
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

