from setuptools import setup, find_packages
setup(
    name='GAE Toolkit',
    version='0.1',
    packages=find_packages('src'),
    install_requires=['decorator', 'PyHAML', 'Mako', 'WTForms'],

    author='David Rogers',
    author_email='david@ethos-development.com',
    description='A small toolkit for building GAE apps with my preferred tools.',
    ## TODO: license='???',
    url='http://github.com/al-the-x/ethos-gae-toolkit',
)
