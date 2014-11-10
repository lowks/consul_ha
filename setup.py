from setuptools import setup, find_packages
from codecs import open
from os import path
from os import environ

here = path.abspath(path.dirname(__file__))

setup(
    name='consul_ha',
    version='0.1.%s' % environ.get("CIRCLE_BUILD_NUM"),
    url='https://github.com/mongohq/consul-ha',
    author='Chris Winslett',
    author_email='chris@compose.io',
    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        ],

    keywords='consul high availablity',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=[],

    # List additional groups of dependencies here (e.g. development dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    extras_require = {
            'dev': ['check-manifest'],
            'test': [],
            },
)
