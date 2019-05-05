#!/usr/bin/env python

from distutils.core import setup

setup(
    name='rdb',
    version='1.0',
    description='Remote debugger with extra stuff',
    author='Will Ware',
    author_email='wware@alum.mit.edu',
    packages=['rdb'],
    install_requires=['remote-pdb', 'Flask'],
)
