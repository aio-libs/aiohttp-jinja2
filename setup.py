import os
import re
import codecs

from setuptools import setup

with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'aiohttp_jinja2', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'$", fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()

install_requires = [
    'aiohttp>=0.20',
    'jinja2>=2.7',
]
tests_require = install_requires + [
    'pytest>=3.0.7',
    'flake8==3.3.0',
    'coverage==4.3.4',
    'sphinx==1.5.3',
    'alabaster>=0.6.2',
    'pytest-cov==2.4.0',
    'yarl==0.10.0',
    'multidict==2.1.4',
    'pytest-aiohttp==0.1.3',
]


setup(
    name='aiohttp-jinja2',
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
        'Topic :: Internet :: WWW/HTTP'],
    author='Andrew Svetlov',
    author_email='andrew.svetlov@gmail.com',
    url='https://github.com/aio-libs/aiohttp_jinja2/',
    license='Apache 2',
    packages=['aiohttp_jinja2'],
    install_requires=install_requires,
    extras_require={
        'test': tests_require,
    },
    include_package_data=True
)
