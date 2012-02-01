#!/usr/bin/env python
from distutils.core import setup

setup(
    name='pywebex',
    version='1.5.1',
    description='Python WebEx Api Wrapper',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='https://github.com/prior/pywebex',
    download_url='https://github.com/prior/pywebex/tarball/v1.5.1',
    packages=['webex'],
    install_requires=[
        'lxml==2.3.1',
        'nose==1.1.2',
        'unittest2==0.5.1',
        'sanetime==3.0.4'],
    dependency_links = ['https://github.com/prior/sanetime/tarball/v3.0.4'],
)
