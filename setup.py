import codecs
import os
import re

from setuptools import setup

with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'aiohttp_jinja2', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'$", fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()

install_requires = ['aiohttp>=0.20', 'jinja2>=2.7']
tests_require = install_requires + [
    'flake8==3.4.1',
    'coverage==4.4.1',
    'sphinx==1.6.3',
    'alabaster>=0.6.2',
    'aiohttp==2.2.5',
    'pytest==3.2.2',
    'pytest-cov==2.5.1',
    'yarl==0.12.0',
    'multidict==3.1.3',
    'pytest-aiohttp==0.1.3',
]


setup(name='aiohttp-jinja2',
      version=version,
      description=("jinja2 template renderer for aiohttp.web "
                   "(http server for asyncio)"),
      long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: AsyncIO',
      ],
      author='Andrew Svetlov',
      author_email='andrew.svetlov@gmail.com',
      url='https://github.com/aio-libs/aiohttp_jinja2/',
      license='Apache 2',
      packages=['aiohttp_jinja2'],
      install_requires=install_requires,
      extras_require={
          'tests': tests_require,
      },
      tests_require=tests_require,
      include_package_data=True)
