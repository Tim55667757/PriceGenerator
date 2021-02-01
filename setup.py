# -*- coding: utf-8 -*-
# Author: Timur Gilmullin

# Build with Travis CI


from setuptools import setup
import os

__version__ = "1.0"

devStatus = "4 - Beta"

if "TRAVIS_BUILD_NUMBER" in os.environ and "TRAVIS_BRANCH" in os.environ:
    print("This is TRAVIS-CI build")
    print("TRAVIS_BUILD_NUMBER = {}".format(os.environ["TRAVIS_BUILD_NUMBER"]))
    print("TRAVIS_BRANCH = {}".format(os.environ["TRAVIS_BRANCH"]))

    __version__ += ".{}{}".format(
        "" if "release" in os.environ["TRAVIS_BRANCH"] or os.environ["TRAVIS_BRANCH"] == "master" else "dev",
        os.environ["TRAVIS_BUILD_NUMBER"],
    )

    devStatus = "5 - Production/Stable" if "release" in os.environ["TRAVIS_BRANCH"] or os.environ["TRAVIS_BRANCH"] == "master" else devStatus

else:
    print("This is local build")
    __version__ += ".dev0"  # set version as major.minor.localbuild if local build: python setup.py install

print("PriceGenerator build version = {}".format(__version__))

setup(
    name="pricegenerator",

    version=__version__,

    description="Forex and stocks price generator. Generates chain of candlesticks with predefined statistical parameters, return pandas dataframe or saving as .csv-file with OHLCV-candlestick in every strings.",

    long_description="GitHub Pages: https://tim55667757.github.io/PriceGenerator",

    license="MIT",

    author="Timur Gilmullin",

    author_email="tim55667757@gmail.com",

    url="https://github.com/Tim55667757/PriceGenerator/",

    download_url="https://github.com/Tim55667757/PriceGenerator.git",

    entry_points={"console_scripts": ["pricegenerator = pricegenerator.PriceGenerator:Main"]},

    classifiers=[
        "Development Status :: {}".format(devStatus),
        "Environment :: Console",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],

    keywords=[
        "history",
        "csv",
        "stock",
        "forex",
        "prices",
        "candlesticks",
        "parser",
        "generator",
        "statistics",
        "testing",
        "testdata",
    ],

    packages=[
        "pricegenerator",
    ],

    tests_require=[
        "pytest",
        "requests",
        "pandas",
    ],

    install_requires=[
        "requests",
        "pandas",
    ],

    package_data={
        "": [
            "./pricegenerator/*.py",
            "./media/*",
            "./tests/*",

            "LICENSE",
            "README.md",
            "README_RU.md",
        ],
    },

    zip_safe=True,
)