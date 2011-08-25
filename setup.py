#!/usr/bin/env python
from distutils.core import setup

setup(
    name='pywebex',
    version='1.0',
    description='Python WebEx Api Wrapper',
    author='Michael Prior',
    author_email='prior@cracklabs.com',
    packages=['webex'],
    requires=[
'lxml==2.3',
'nose==1.1.2',
'pytz==2011h',
'unittest2==0.5.1',
'python-dateutil==1.5',
]

)
