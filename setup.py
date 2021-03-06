from setuptools import setup, find_packages

setup(
    name='panomena-accounts',
    description='Panomena Accounts',
    version='0.0.5',
    author='',
    license='Proprietory',
    url='http://www.unomena.com/',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    dependency_links = [
        'http://github.com/unomena/panomena-general/tarball/master#egg=panomena-general',
        'http://github.com/unomena/panomena-mobile/tarball/master#egg=panomena-mobile',
    ],
    install_requires = [
        'Django',
        'panomena-general==0.0.3',
        'panomena-mobile==0.0.3',
    ],
)
