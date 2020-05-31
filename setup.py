# -*- coding: utf-8 -*-
import os
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, "gesture_app", "__version__.py"), "r") as f:
    exec(f.read(), about)

with open("README.md", "r") as f:
    readme = f.read()

requires = ["Click==7.0", "opencv-python==4.1.0.25", "tensorflow==2.0.0", "keyboard==0.13.5", "numpy==1.18.4"]


def setup_package():
    metadata = dict(
        name=about["__title__"],
        version=about["__version__"],
        description=about["__description__"],
        long_description=readme,
        long_description_content_type="text/markdown",
        url=about["__url__"],
        author=about["__author__"],
        author_email=about["__author_email__"],
        license=about["__license__"],
        packages=find_packages(exclude=("tests",)),
        install_requires=requires,
        entry_points={"console_scripts": ["gesture-app = gesture_app.cli:cli"]},
        classifiers=[
            # Trove classifiers
            # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
        ],
        include_package_data=True,
    )

    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup

    setup(**metadata)

if __name__ == "__main__":
    setup_package()