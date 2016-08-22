
import common
import unittest
import lib.config

class TestConfig(unittest.TestCase):


    # Tests for .conf files ----------------------------------------------------

    def config(self, name):
        return lib.config.parse('resources/config_' + name + '.conf')

    def test_confread_sections(self):
        conf = self.config('sections')
        self.assertIsInstance(conf, dict)
        self.assertTrue('section1' in conf)
        self.assertTrue('section2' in conf)

    def test_confread_keyvalues(self):
        conf = self.config('keyvalues')
        self.assertIsInstance(conf['section'], dict)
        self.assertTrue('key1' in conf['section'])
        self.assertTrue('key2' in conf['section'])
        self.assertEqual(conf['section']['key1'], 'value1')
        self.assertEqual(conf['section']['key2'], 'value2')

    def test_confread_keyvalues_quotes(self):
        conf = self.config('keyvalues')
        self.assertIsInstance(conf['section'], dict)
        self.assertTrue('key1_quotes' in conf['section'])
        self.assertTrue('key2_quotes' in conf['section'])
        self.assertEqual(conf['section']['key1_quotes'], 'value1')
        self.assertEqual(conf['section']['key2_quotes'], 'value2')

    def test_confread_lists(self):
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

    def test_confread_lists_quotes(self):
        conf = self.config('lists')
        self.assertIsInstance(conf['section']['list_quotes'], list)
        self.assertTrue('value1' in conf['section']['list_quotes'])
        self.assertTrue('value2' in conf['section']['list_quotes'])
        self.assertTrue('value3' in conf['section']['list_quotes'])

    def test_confread_lists_quotes_spaces(self):
        conf = self.config('lists')
        self.assertIsInstance(conf['section']['list_quotes_spaces'], list)
        self.assertTrue('value1' in conf['section']['list_quotes_spaces'])
        self.assertTrue('value2' in conf['section']['list_quotes_spaces'])
        self.assertTrue('value3' in conf['section']['list_quotes_spaces'])

    def test_confread_multiline(self):
        conf = self.config('keyvalues')
        self.assertEqual(conf['section']['key_multiline'], 'line1line2')
        self.assertEqual(conf['section']['key_multiline_space'], 'line1 line2')
        self.assertEqual(conf['section']['key_multiline_quotes'], 'line1line2')
    

    # Tests for .yaml files ----------------------------------------------------
    
    def configyaml(self, name):
        return lib.config.parse('resources/config_' + name + '.yaml')

    def test_yamlread_sections(self):
        conf = self.configyaml('sections')
        self.assertIsInstance(conf, dict)
        self.assertTrue('section1' in conf)
        self.assertTrue('section2' in conf)

    def test_yamlread_keyvalues(self):
        conf = self.configyaml('keyvalues')
        self.assertIsInstance(conf['section'], dict)
        self.assertTrue('key1' in conf['section'])
        self.assertTrue('key2' in conf['section'])
        self.assertEqual(conf['section']['key1'], 'value1')
        self.assertEqual(conf['section']['key2'], 'value2')

    def test_yamlread_keyvalues_quotes(self):
        conf = self.configyaml('keyvalues')
        self.assertIsInstance(conf['section'], dict)
        self.assertTrue('key1_quotes' in conf['section'])
        self.assertTrue('key2_quotes' in conf['section'])
        self.assertEqual(conf['section']['key1_quotes'], 'value1')
        self.assertEqual(conf['section']['key2_quotes'], 'value2')

    def test_yamlread_lists(self):
        conf = self.configyaml('lists')
        self.assertIsInstance(conf['section']['list'], list)
        self.assertTrue('value1' in conf['section']['list'])
        self.assertTrue('value2' in conf['section']['list'])
        self.assertTrue('value3' in conf['section']['list'])

    def test_yamlread_lists_spaces(self):
        conf = self.configyaml('lists')
        self.assertIsInstance(conf['section']['list_spaces'], list)
        self.assertTrue('value1' in conf['section']['list_spaces'])
        self.assertTrue('value2' in conf['section']['list_spaces'])
        self.assertTrue('value3' in conf['section']['list_spaces'])

    def test_yamlread_lists_quotes(self):
        conf = self.configyaml('lists')
        self.assertIsInstance(conf['section']['list_quotes'], list)
        self.assertTrue('value1' in conf['section']['list_quotes'])
        self.assertTrue('value2' in conf['section']['list_quotes'])
        self.assertTrue('value3' in conf['section']['list_quotes'])

    def test_yamlread_lists_quotes_spaces(self):
        conf = self.configyaml('lists')
        self.assertIsInstance(conf['section']['list_quotes_spaces'], list)
        self.assertTrue('value1' in conf['section']['list_quotes_spaces'])
        self.assertTrue('value2' in conf['section']['list_quotes_spaces'])
        self.assertTrue('value3' in conf['section']['list_quotes_spaces'])

    def test_yamlread_multiline(self):
        conf = self.configyaml('keyvalues')
        self.assertEqual(conf['section']['key_multiline'], 'line1line2')
#       Trailing spaces on a line are not supported by yaml
#        self.assertEqual(conf['section']['key_multiline_space'], 'line1 line2')
        self.assertEqual(conf['section']['key_multiline_quotes'], 'line1line2')

    
if __name__ == '__main__':
    unittest.main(verbosity=2)
