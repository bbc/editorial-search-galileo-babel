import os
from setuptools import setup, find_packages

setup(
    name='EditorialSearch - Galileo Babel',
    version='1.0.0',
    description='Editorial Search - Galileo Babel', 
    url='https://github.com/bbc/editorial-search-galileo-babel', 
    # For a list of valid classifiers, see
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=['troposphere', 'awacs','cosmosTroposphere', 'boto3'],
    tests_require=['pytest'],
    test_suite="tests",
    use_2to3=True,
    entry_points = {
        'console_scripts': ['galileobabel=babel.devenvironment:main'],
    },
    keywords='aws',
)
