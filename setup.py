# -*- coding: utf-8 -*-
# Author: Timur Gilmullin

# Build with Travis CI


from setuptools import setup
import os

__version__ = "1.3"

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

    description="PriceGenerator is the platform for generating prices similar to real stock prices, but you can control the statistics of their distribution. Generates chain of candlesticks with predefined statistical parameters, return Pandas DataFrame or saving as .CSV-file with OHLCV-candlestick in every string. Use PriceGenerator to generate synthetic data to test your trading strategy.",

    long_description="See full documentation with examples: https://github.com/Tim55667757/PriceGenerator/blob/master/README.md\n\nTKSBrokerAPI module documentation: https://tim55667757.github.io/PriceGenerator/docs/pricegenerator/PriceGenerator.html\n\nПодробная документация на русском с примерами: https://github.com/Tim55667757/PriceGenerator/blob/master/README_RU.md\n\nДокументация на модуль PriceGenerator: https://tim55667757.github.io/PriceGenerator/docs/pricegenerator/PriceGenerator.html",

    license="Apache-2.0",

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
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],  # classifiers are from here: https://pypi.org/classifiers/

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
        "OHLCV",
        "generator",
    ],

    tests_require=[
        "pytest >= 6.2.2",
        "requests >= 2.25.1",  # Apache-2.0 license
        "pandas >= 1.5.2",
        "bokeh >= 3.0.3",  # BSD-3-Clause license
        "bkcharts >= 0.2",  # New BSD License
        "numpy >= 1.23.5",  # BSD-3-Clause license
        "matplotlib >= 3.3.4",  # PSF license
        "python-dateutil >= 2.8.1",  # Apache-2.0 license
        "jinja2 >= 2.11.3",  # BSD-3-Clause license
        "pandas_ta >= 0.2.45b0",  # MIT License
        "notebook >= 6.5.2",  # BSD License
    ],

    install_requires=[
        "requests >= 2.25.1",  # Apache-2.0 license
        "pandas >= 1.5.2",  # MIT License
        "bokeh >= 3.0.3",  # BSD-3-Clause license
        "bkcharts >= 0.2",  # New BSD License
        "numpy >= 1.23.5",  # BSD-3-Clause license
        "matplotlib >= 3.3.4",  # PSF license
        "python-dateutil >= 2.8.1",  # Apache-2.0 license
        "jinja2 >= 2.11.3",  # BSD-3-Clause license
        "pandas_ta >= 0.2.45b0",  # MIT License
        "notebook >= 6.5.2",  # BSD License
    ],

    packages=[
        "pricegenerator",
    ],

    package_data={
        "pricegenerator": [
            "*.j2",
        ],
    },

    include_package_data=True,

    zip_safe=True,
)
