#!/usr/bin/env python
from distutils.core import setup

setup(
    name='pywebex',
    version='1.1.1',
    description='Python WebEx Api Wrapper',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='',
    packages=['webex'],
    install_requires=[
        'lxml',
        'nose',
        'unittest2',
        'sanetime==3.0.1'],
    dependency_links = [
        'http://github.com/prior/sanetime/tarball/v3.0.1#egg=sanetime-3.0.1']
)
