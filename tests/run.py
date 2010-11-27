

import os
import doctest
import unittest

import liberet

settingsdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')

os.environ[liberet.LIBERET_SETTINGS_DIRECTORY] = settingsdir

suite = unittest.TestSuite()
loader = unittest.TestLoader()

#suite.addTest(loader.loadTestsFromModule(testcases))

for root, dirs, files in os.walk('.'):
    for f in files:
        if f.startswith('test_') and f.endswith('.rst'):
            suite.addTest(doctest.DocFileSuite(os.path.join(root, f)))

unittest.TextTestRunner(verbosity=1).run(suite)

