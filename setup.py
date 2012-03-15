#!/usr/bin/env python
from distutils.core import setup

setup(
    name='webexpy',
    version='2.0.4',
    description='Python WebEx Api Wrapper',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='https://github.com/prior/webexpy',
    download_url='https://github.com/prior/webexpy/tarball/v2.0.4',
    packages=['webex'],
    install_requires=[
        'lxml==2.3.1',
        'nose==1.1.2',
        'unittest2==0.5.1',
        'sanetime==3.1.2'],
    dependency_links = ['https://github.com/prior/sanetime/tarball/v3.1.2'],
)
