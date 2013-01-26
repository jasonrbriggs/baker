from setuptools import setup

import sitebaker

setup(
    name = 'SiteBaker',
    version = sitebaker.__version__,
    description = 'SiteBaker',
    license = 'Apache',
    url = 'http://todo',
    author = 'Jason R Briggs',
    author_email =  'jasonrbriggs@gmail.com',
    platforms = ['any'],
    packages = ['sitebaker', 'sitebaker.plugins' ],
    install_requires = ['markdown2>=2.1.0', 'proton>=0.7.2', 'py-postgresql>=1.1.0', 'Pygments>=1.6rc1'],
    tests_require = [ 'mock' ],
    test_suite = 'tests',
    scripts = [ './baker' ]
)
