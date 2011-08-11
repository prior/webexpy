from distutils.core import setup

setup(name='pywebex',
      version='0.1',
      description='Python wrapper for WebEx XML API',
      author='Victor Vu',
      author_email='vvu@hubspot.com',
      packages=['pywebex','pywebex.builders', 'pywebex.parsers'],
      package_data={'webex': ['schemas/*/*.xsd', 'schemas/*/*/*.xsd']})
