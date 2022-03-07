#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup  # type: ignore

VERSION = '0.0.1'
DESCRIPTION = ""
LONG_DESCRIPTION = """
"""

setup(
    name="PyServiceUtil",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords=('PyServiceUtil', 'etcd3'),
    author="mutalisk999",
    author_email="",
    url="https://github.com/mutalisk999/py-service-util",
    license="MIT License",
    platforms=['any'],
    test_suite="",
    zip_safe=True,
    install_requires=[],
    packages=['PyServiceUtil']
)
