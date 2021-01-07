#!/usr/bin/env python
from distutils.core import setup

VERSION = '2.2.6'

setup(
    name='webexpy',
    version=VERSION,
    description='Python WebEx Api Wrapper',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    url='https://github.com/prior/webexpy',
    download_url='https://github.com/prior/webexpy/tarball/v%s'%VERSION,
    packages=['webex','webex.test'],
    install_requires=[ 'lxml==4.6.2', 'nose==1.1.2']
)
