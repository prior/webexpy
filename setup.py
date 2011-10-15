#!/usr/bin/env python
from distutils.core import setup

setup(
    name='pywebex',
    version='1.0.0',
    description='Python WebEx Api Wrapper',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='',
    packages=['webex'],
    install_requires=[
        'lxml',
        'nose',
        'unittest2',
        'sanetime==1.0.0'],
    dependency_links = [
        'http://github.com/prior/sanetime/tarball/v1.0.0#egg=sanetime-1.0.0']
)
