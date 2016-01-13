# encoding: utf-8
# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
import os
from setuptools import setup, find_packages

description = "Django API layer"
try:
    cur_dir = os.path.dirname(__file__)
    long_description = open(os.path.join(cur_dir, 'README.rst')).read()
except:
    long_description = description

setup(
    name = "django-wapiti",
    version = "0.0.3",
    packages = find_packages(),
    description = description,
    author = "Ecometrica",
    author_email = "info@ecometrica.ca",
    maintainer = "Éric St-Jean",
    maintainer_email = "esj@wwd.ca",
    url = "http://github.com/ecometrica/django-wapiti/",
    keywords = ["django", "api"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: Software Development :: Internationalization",
        "Framework :: Django",
        ],
    long_description = long_description,
)
