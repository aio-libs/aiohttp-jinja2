import codecs
import re
from pathlib import Path

from setuptools import setup


def _get_version():
    PATH_TO_INIT_PY = Path(__file__).parent / "aiohttp_jinja2" / "__init__.py"
    with codecs.open(PATH_TO_INIT_PY, "r", "latin1") as fp:
        try:
            for line in fp.readlines():
                if line:
                    line = line.strip()
                    version = re.findall(r'^__version__ = "([^"]+)"$', line, re.M)
                    if version:
                        return version[0]
        except IndexError:
            raise RuntimeError("Unable to determine version.")
    raise RuntimeError("Unable to find version.")


version = _get_version()


def read(f):
    return Path(__file__).with_name(f).read_text()


install_requires = [
    "aiohttp>=3.6.3",
    "jinja2>=3.0.0",
    'typing_extensions>=3.7.4; python_version<"3.8"',
]


setup(
    name="aiohttp-jinja2",
    version=version,
    description="jinja2 template renderer for aiohttp.web (http server for asyncio)",
    long_description="\n\n".join((read("README.rst"), read("CHANGES.rst"))),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Internet :: WWW/HTTP",
        "Framework :: AsyncIO",
        "Framework :: aiohttp",
    ],
    author="Andrew Svetlov",
    author_email="andrew.svetlov@gmail.com",
    url="https://github.com/aio-libs/aiohttp_jinja2/",
    license="Apache 2",
    packages=["aiohttp_jinja2"],
    python_requires=">=3.7",
    install_requires=install_requires,
    include_package_data=True,
)
