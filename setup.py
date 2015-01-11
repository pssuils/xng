#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
    name = "xng",
    version = "0.1",
    packages = find_packages(),
    scripts=['src/xng.py'],
    author = "Pilar Sopena Suils",
    author_email = "pssuils@gmail.com",
    description = "Generates a xng (svg) file from a folder of images",
    keywords = "xng",
    install_requires=[
            "PIL>=1.1.7",
            ],

)
