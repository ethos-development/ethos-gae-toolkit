from setuptools import setup, find_packages
import os.path

def read(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)

    try:
        return open(filepath).read()

    except IOError:
        return None


setup(
    name='ethos Toolkit for Google App Engine',
    version='0.1',
    packages=find_packages('src'), package_dir={'': 'src'},
    install_requires=['PyHAML', 'Mako', 'WTForms'],

    author='David Rogers',
    author_email='david@ethos-development.com',
    ## TODO: license='???',
    url='http://github.com/al-the-x/ethos-gae-toolkit',
    description='A small toolkit for building GAE apps with my preferred tools.',
    long_description=read('README.markdown'),
)
