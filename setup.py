#!/usr/bin/env python
from distutils.core import setup

setup(
    name='webexpy',
    version='2.1',
    description='Python WebEx Api Wrapper',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='https://github.com/prior/webexpy',
    download_url='https://github.com/prior/webexpy/tarball/v2.1',
    packages=['webex'],
    install_requires=[
        'lxml==2.3.1',
        'nose==1.1.2',
        'sanetime==3.2'],
    dependency_links = ['https://github.com/prior/sanetime/tarball/v3.2'],
)
