# -*- coding: utf-8 -*-

import pytest
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
import random

from pricegenerator import PriceGenerator as pg


class TestPriceGenerator:

    @pytest.fixture(scope='function', autouse=True)
    def init(self):
        pg.uLogger.level = 50  # Disable debug logging while test, logger CRITICAL = 50
        pg.uLogger.handlers[0].level = 50  # Disable debug logging for STDOUT

        self.model = pg.PriceGenerator()  # init generator for the next tests

    def test_Generate(self):
        self.model.Generate()
        assert isinstance(self.model.prices, pd.DataFrame) is True, "Expected Pandas DataFrame when Generate()!"

    def test_LoadFromFile(self):
        self.model.LoadFromFile("AFLT_day.csv")
        assert isinstance(self.model.prices, pd.DataFrame) is True, "Expected Pandas DataFrame when LoadFromFile()!"
        assert self.model.horizon == 2775, "Expected 2775 string in test file 'AFLT_day.csv'! 'Horizon' field also must be equal to 2775!"
        assert self.model.ticker == "AFLT_day.csv", "Expected 'ticker' field is equal to 'AFLT_day.csv' after loading!"

    def test_SaveToFile(self):
        self.model.horizon = 5
        self.model.Generate()
        suffix = random.uniform(0, 1000000000)
        name = "test{}.csv".format(suffix)
        self.model.SaveToFile(name)
        assert os.path.exists(name), "Expected .csv-file '{}' after saving but it is not exist!".format(name)
        with open(name, "r") as fH:
            horizon = len(fH.readlines())
            assert horizon == 5, "Expected 5 lines in file '{}' but there is {}!".format(name, horizon)

    def test_RenderBokeh(self):
        self.model.horizon = 5
        self.model.Generate()
        suffix = random.uniform(0, 1000000000)
        name = "test_render_bokeh{}.html".format(suffix)
        nameMD = "{}.md".format(name)
        self.model.RenderBokeh(fileName=name, viewInBrowser=False)
        assert os.path.exists(name), "Expected .html-file '{}' after saving but it is not exist!".format(name)
        assert os.path.exists(nameMD), "Expected markdown file '{}' after saving but it is not exist!".format(nameMD)

    def test_PandasDFheaders(self):
        headers = ["datetime", "open", "high", "low", "close", "volume"]
        self.model.Generate()
        assert list(self.model.prices) == headers, "Expected headers: {}".format(headers)

    def test_DetectPrecision(self):
        testData = [
            [np.array([1, 2, 3], dtype=float), 1],  # precision can be 1
            [np.array([1., 2., 3.], dtype=float), 1],  # precision can be 1
            [np.array([1.1, 2.2, 3.3], dtype=float), 1],  # precision can be 1
            [np.array([1.11, 2.2, 3.3], dtype=float), 1],  # precision can be 1
            [np.array([1.11, 2.22, 3.3], dtype=float), 2],  # precision can be 2
            [np.array([1.11, 2.22, 3.33], dtype=float), 2],  # precision can be 2
            [np.array([1.11, 2.22, 3.3, 4.4], dtype=float), 2],  # precision can be 2 by default because mode() error
            [np.array([1.111, 2.22, 3.333, 4.444], dtype=float), 3],  # precision can be 3
            [np.array([1.111, 2.222, 3.3, 4.4], dtype=float), 2],  # precision can be 2 by default because mode() error
            [np.array([1.1111, 2.2222, 3.3333, 4.4], dtype=float), 4],  # precision can be 4
            [np.array([1.1111, 2., 3., 4.], dtype=float), 1],  # precision can be 1
            [np.array([1.1111, 2.2222, 3., 4.], dtype=float), 2],  # precision can be 2 by default because mode() error
            [np.array([1.1111, 2.2222, 3.1, 4.44], dtype=float), 4],  # precision can be 4
        ]
        for test in testData:
            self.model.DetectPrecision(test[0])
            assert self.model.precision == test[1], "Expected precision = {} for chain:\n{}".format(test[1], test[0])

    def test_precision(self):
        testData = [1, 2, 3, 4]
        for test in testData:
            self.model.precision = test  # set test data as "precision" field in PriceGenerator() class
            self.model.Generate()
            self.model.DetectPrecision(self.model.prices.close.values)  # re-calc and update "precision" field
            assert test == self.model.precision, "Expected precision = {} for chain:\n{}".format(test, self.model.prices.close.values)

    def test_timeframe(self):
        testData = [
            timedelta(seconds=1), timedelta(seconds=15), timedelta(seconds=30), timedelta(seconds=60),
            timedelta(minutes=1), timedelta(minutes=15), timedelta(minutes=30), timedelta(minutes=60),
            timedelta(hours=1), timedelta(hours=4), timedelta(hours=12), timedelta(hours=24),
            timedelta(days=1), timedelta(days=5), timedelta(days=7), timedelta(days=30), timedelta(days=31),
        ]
        for test in testData:
            self.model.timeframe = test  # set test data as "timeframe" field in PriceGenerator() class
            self.model.Generate()
            # auto-detect time delta between last two neighbour candles:
            timeframe = min(
                self.model.prices.iloc[-1].datetime - self.model.prices.iloc[-2].datetime,
                self.model.prices.iloc[-2].datetime - self.model.prices.iloc[-3].datetime
            )
            assert test == timeframe, "Expected timeframe between last two neighbour candles: {}".format(timeframe)

    def test_timeStart(self):
        testData = [
            datetime.now(tzlocal()),  # current time
            datetime.now(tzlocal()).replace(microsecond=0, second=0, minute=0),  # current time rounded to day start
            datetime.strptime("2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"),
            datetime.strptime("2021-02-03 04:05:06", "%Y-%m-%d %H:%M:%S"),
            datetime.strptime("2021-01-01 23:59:59", "%Y-%m-%d %H:%M:%S"),
            datetime.strptime("2021-01-01 00:00:01", "%Y-%m-%d %H:%M:%S"),
        ]
        for test in testData:
            self.model.timeStart = test  # set test data as "timeStart" field in PriceGenerator() class
            self.model.Generate()
            assert test.timestamp() == self.model.prices.datetime[0].timestamp(), "Expected datetime = {}".format(test)

    def test_horizon(self):
        testData = [[-1, 5], [0, 5], [1, 5], [4, 5], [5, 5], [6, 6], [10, 10], [99, 99], [333, 333]]
        for test in testData:
            self.model.horizon = test[0]  # set test data as "horizon" field in PriceGenerator() class
            self.model.Generate()  # horizon update during generating and must be >=5
            assert test[1] == self.model.horizon, "Expected class field 'horizon' = {} for requested horizon: {}".format(test[1], test[0])

    def test_minClose_maxClose(self):
        testData = [[0, 1], [1, 10], [100, 101]]
        for test in testData:
            self.model.minClose = test[0]  # set test data as "minClose" field in PriceGenerator() class
            self.model.maxClose = test[1]  # set test data as "maxClose" field in PriceGenerator() class
            self.model.initClose = None  # always re-calc start close value
            self.model.Generate()  # minClose <= all close prices <= maxClose
            assert (self.model.prices.close < test[0]).any() == False, "There are some values generated less than minClose: {}! All close values:\n{}".format(test[0], list(self.model.prices.close))
            assert (self.model.prices.close > test[1]).any() == False, "There are some values generated more than maxClose: {}! All close values:\n{}".format(test[1], list(self.model.prices.close))

    def test_initClose(self):
        testData = [None, 0, 1, 5., 9.9, 10]
        for test in testData:
            self.model.minClose = 0
            self.model.maxClose = 10
            self.model.initClose = test  # set test data as "initClose" field in PriceGenerator() class
            self.model.Generate()  # open price of first candle must be equal self.initClose or if None: minClose <= 1st open price <= maxClose
            assert self.model.minClose <= self.model.prices.open[0] <= self.model.maxClose, "minClose <= 1st open price <= maxClose, but 1st open price = {}".format(test)
            if test is not None:
                assert test == self.model.prices.open[0], "close price of first candle must be equal 'initClose' = {}, but 1st close price = {}".format(test, self.model.prices.close[0])
