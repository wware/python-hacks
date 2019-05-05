#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='wware-hacks',
    version='0.0.1',
    description='My assorted python hacks',
    author='Will Ware',
    author_email='wware@alum.mit.edu',
    packages=find_packages(),
    install_requires=[
        'click==6.6',
        'coverage==4.1',
        'Flask==0.11.1',
        'funcsigs==1.0.2',
        'itsdangerous==0.24',
        'Jinja2==2.8',
        'MarkupSafe==0.23',
        'mock==3.0.4',
        'py==1.4.31',
        'pytest==2.9.1',
        'pytest-cov==2.2.1',
        'remote-pdb==1.2.0',
        'six==1.12.0',
        'Werkzeug==0.11.10',
        'zope.interface==4.1.3',
    ],
)
