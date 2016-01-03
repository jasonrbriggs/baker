import unittest
from setuptools import setup, Command

import sitebaker

class TestCommand(Command):
    user_options = [ ('test=', 't', 'specific test to run') ]

    def initialize_options(self):
        self.test = '*'

    def finalize_options(self):
        pass

    def run(self):
        suite = unittest.TestSuite()
        if self.test == '*':
            import test
            for tst in test.__all__:
                suite.addTests(unittest.TestLoader().loadTestsFromName('test.%s' % tst))
        else:
            suite = unittest.TestLoader().loadTestsFromName('test.%s' % self.test)
        unittest.TextTestRunner(verbosity=2).run(suite)

setup(
    name = 'SiteBaker',
    version = sitebaker.__version__,
    description = 'SiteBaker',
    license = 'Apache',
    url = 'http://todo',
    author = 'Jason R Briggs',
    author_email = 'jasonrbriggs@gmail.com',
    platforms = ['any'],
    packages = ['sitebaker', 'sitebaker.plugins'],
    install_requires = ['markdown2>=2.1.0', 'proton>=0.8.8', 'py-postgresql>=1.1.0', 'Pygments>=1.6rc1'],
    tests_require = ['mock'],
    test_suite = 'test',
    scripts = ['./baker'],
    cmdclass = {'test': TestCommand }
)
