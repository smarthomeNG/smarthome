#
# created by cstrassburg on January 31st, 2017
#
# actually probably not working at all, better develop a solution
# working with pytest
#
import unittest
import glob
import  os
import sys

# assuming that __file__ is '/usr/local/smarthome/tests/run_tests.py'
# BASE will then be '/usr/local/smarthome'
BASE = '/'.join(os.path.realpath(__file__).split('/')[:-2])
sys.path.insert(0, BASE)
print("__file__="+os.path.realpath(__file__))
print("BASE="+BASE)
print("Current working directory="+os.getcwd())

def create_testsuite(searchname):
    testfiles = glob.glob(searchname, recursive=True)
    tests = [stri[:-3] for stri in testfiles]
    suites = [unittest.defaultTestLoader.loadTestsFromName(name) for name in tests]
    testSuite = unittest.TestSuite(suites)
    return testSuite

testSuite = create_testsuite("**/test_*.py")
testSuite = unittest.defaultTestLoader.discover(BASE+"/plugins/","test_*.py")

text_runner = unittest.TextTestRunner().run(testSuite)
