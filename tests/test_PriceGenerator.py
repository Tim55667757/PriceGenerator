# -*- coding: utf-8 -*-

import pytest
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
import random

from pricegenerator import PriceGenerator as Gen


class TestFeatures:

    @pytest.fixture(scope='function', autouse=True)
    def init(self):
        Gen.uLogger.level = 50  # Disable debug logging while test, logger CRITICAL = 50
        Gen.uLogger.handlers[0].level = 50  # Disable debug logging for STDOUT

        self.model = Gen.PriceGenerator()  # init generator for the next tests

    def test_Generate(self):
        self.model.Generate()
        assert isinstance(self.model.prices, pd.DataFrame) is True, "Expected Pandas DataFrame when Generate()!"

    def test_GenerateWithSomeTrends(self):
        self.model.horizon = 30
        self.model.trendSplit = r"/\-"
        self.model.splitCount = [5, 10, 15]
        self.model.Generate()
        self.model.trendSplit = ""
        self.model.splitCount = []
        assert isinstance(self.model.prices, pd.DataFrame) is True, "Expected Pandas DataFrame when Generate()!"

    def test_LoadFromFile(self):
        self.model.LoadFromFile(os.path.join("tests", "AFLT_day.csv"))
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
        self.model.horizon = 30
        self.model.Generate()
        suffix = random.uniform(0, 1000000000)
        name = "test_render_bokeh{}.html".format(suffix)
        nameMD = "{}.md".format(name)
        self.model.RenderBokeh(fileName=name, viewInBrowser=False)
        assert os.path.exists(name), "Expected .html-file '{}' after saving but it is not exist!".format(name)
        assert os.path.exists(nameMD), "Expected markdown file '{}' after saving but it is not exist!".format(nameMD)

    def test_RenderBokehWithSomeTrends(self):
        self.model.horizon = 30
        self.model.trendSplit = r"\-/"
        self.model.splitCount = [5, 10, 15]
        self.model.Generate()
        suffix = random.uniform(0, 1000000000)
        name = "test_render_bokeh__{}.html".format(suffix)
        nameMD = "{}.md".format(name)
        self.model.RenderBokeh(fileName=name, viewInBrowser=False)
        self.model.trendSplit = ""
        self.model.splitCount = []
        assert os.path.exists(name), "Expected .html-file '{}' after saving but it is not exist!".format(name)
        assert os.path.exists(nameMD), "Expected markdown file '{}' after saving but it is not exist!".format(nameMD)

    def test_RenderGoogleDefault(self):
        self.model.horizon = 30
        self.model.Generate()
        suffix = random.uniform(0, 1000000000)
        name = "test_render_google{}.html".format(suffix)
        nameMD = "{}.md".format(name)
        self.model.RenderGoogle(fileName=name, viewInBrowser=False)
        assert os.path.exists(name), "Expected .html-file '{}' after saving but it is not exist!".format(name)
        assert os.path.exists(nameMD), "Expected markdown file '{}' after saving but it is not exist!".format(nameMD)

    def test_RenderGoogleDefaultWithSomeTrends(self):
        self.model.horizon = 30
        self.model.trendSplit = "/-\\"
        self.model.splitCount = [5, 10, 15]
        self.model.Generate()
        suffix = random.uniform(0, 1000000000)
        name = "test_render_google__{}.html".format(suffix)
        nameMD = "{}.md".format(name)
        self.model.RenderGoogle(fileName=name, viewInBrowser=False)
        self.model.trendSplit = ""
        self.model.splitCount = []
        assert os.path.exists(name), "Expected .html-file '{}' after saving but it is not exist!".format(name)
        assert os.path.exists(nameMD), "Expected markdown file '{}' after saving but it is not exist!".format(nameMD)

    def test_RenderGoogleFromFileTemplate(self):
        self.model.horizon = 30
        self.model.Generate()
        suffix = random.uniform(0, 1000000000)
        name = "test_render_google{}.html".format(suffix)
        nameMD = "{}.md".format(name)
        self.model.j2template = os.path.join("tests", "test_template.j2")
        self.model.RenderGoogle(fileName=name, viewInBrowser=False)
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

    def test_DetectTimeframe(self):
        testData = [
            timedelta(minutes=1),
            timedelta(minutes=5),
            timedelta(minutes=15),
            timedelta(minutes=30),
            timedelta(hours=1),
            timedelta(hours=4),
            timedelta(days=1),
            timedelta(days=5),
            timedelta(days=7),
            timedelta(days=30),
            timedelta(days=31),
        ]
        for test in testData:
            self.model.horizon = 5
            self.model.timeframe = test  # set test data as "timeframe" field
            self.model.Generate()
            self.model.DetectTimeframe()  # detect real generated timeframe and save to self.timeframe
            assert self.model.timeframe == test, "Expected timeframe = {}".format(test)

    def test_precision(self):
        testData = [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [-1, 2], [-2, 2], ["xxx", 2]]
        for test in testData:
            self.model.precision = test[0]  # set test[0] data as "precision" field in PriceGenerator() class
            assert test[1] == self.model.precision, "Expected precision = {} for test = {}".format(test[1], test[0])

    def test_zigZagDeviation(self):
        testData = [[0, 0], [1, 1], [0.5, 0.5], [-1, 0.03], [2, 1], [0.12345, 0.12345]]
        for test in testData:
            self.model.zigZagDeviation = test[0]  # set test[0] data as "zigZagDeviation" field in PriceGenerator() class
            assert test[1] == self.model.zigZagDeviation, "Expected zigZagDeviation = {} for test = {}".format(test[1], test[0])

    def test_ZigZagFilter(self):
        testData = [
            {
                "deviation": 0.03,
                "dates": pd.Series(data=[datetime(year=2021, month=2, day=28, hour=12), datetime(year=2021, month=2, day=28, hour=13)]),
                "closes": pd.Series(data=[100, 103]),
                "expected": pd.Series(data=[100, 103]),
            },
            {
                "deviation": 0.03,
                "dates": pd.Series(data=[datetime(year=2021, month=2, day=28, hour=12), datetime(year=2021, month=2, day=28, hour=13)]),
                "closes": pd.Series(data=[100, 105]),
                "expected": pd.Series(data=[100, 105]),
            },
            {
                "deviation": 0.03,
                "dates": pd.Series(data=[datetime(year=2021, month=2, day=28, hour=12), datetime(year=2021, month=2, day=28, hour=13)]),
                "closes": pd.Series(data=[100, 102]),
                "expected": pd.Series(data=[100]),
            },
            {
                "deviation": 0.03,
                "dates": pd.Series(data=[datetime(year=2021, month=2, day=28, hour=12), datetime(year=2021, month=2, day=28, hour=13), datetime(year=2021, month=2, day=28, hour=14)]),
                "closes": pd.Series(data=[100, 102, 103]),
                "expected": pd.Series(data=[100, 103]),
            },
            {
                "deviation": 0.05,
                "dates": pd.Series(data=[datetime(year=2021, month=2, day=28, hour=12), datetime(year=2021, month=2, day=28, hour=13), datetime(year=2021, month=2, day=28, hour=14)]),
                "closes": pd.Series(data=[100, 102, 103]),
                "expected": pd.Series(data=[100]),
            },
            {
                "deviation": 0.05,
                "dates": pd.Series(data=[datetime(year=2021, month=2, day=28, hour=12), datetime(year=2021, month=2, day=28, hour=13), datetime(year=2021, month=2, day=28, hour=14)]),
                "closes": pd.Series(data=[100, 103, 200]),
                "expected": pd.Series(data=[100, 200]),
            },
        ]
        for test in testData:
            actual = self.model.ZigZagFilter(datetimes=test["dates"], values=test["closes"], deviation=test["deviation"])
            assert isinstance(actual, dict), "Expected dictionary result!"
            assert "datetimes" in actual.keys(), "Expected 'datetimes' key in ZigZagFilter() is present in result!"
            assert "filtered" in actual.keys(), "Expected 'filtered' key in ZigZagFilter() is present in result!"
            assert list(test["expected"]) == list(actual["filtered"]), "Expected filtered data: {}\nInput parameters:\n- deviation: {}\n- dates: {}\n- closes: {}".format(test["expected"], test["deviation"], test["dates"], test["closes"])

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

    def test_maxOutlier(self):
        testData = [None, 0, 1, 10, 100]
        for test in testData:
            self.model.horizon = 10
            self.model.minClose = 10
            self.model.maxClose = 110
            self.model.maxCandleBody = 10
            self.model.initClose = 50
            self.model.maxOutlier = test  # set test data as "maxOutlier" field in PriceGenerator() class
            self.model.Generate()  # if maxOutlier == None then used (maxClose - minClose) / 10
            if test is None:
                correctOutliers = (self.model.maxClose - self.model.minClose) / 10
                assert self.model.maxOutlier == correctOutliers, "if maxOutlier == None then used (maxClose - minClose) / 10 = {} but {} given!".format(correctOutliers, self.model.maxOutlier)
            else:
                upperOutliers = []
                lowerOutliers = []
                for item in range(self.model.horizon):
                    upperOutliers.append(self.model.prices.high[item] - max(self.model.prices.open[item], self.model.prices.close[item]))
                    lowerOutliers.append(min(self.model.prices.open[item], self.model.prices.close[item]) - self.model.prices.low[item])
                maxHighOutliers = max(upperOutliers)
                maxLowOutliers = max(lowerOutliers)
                maxHalfBodies = max(list(abs(self.model.prices.open - self.model.prices.close) / 2))
                assert maxHighOutliers <= test + maxHalfBodies, "All candle 'tails' must be less than maxOutlier + maxHalfBodies = {} + {}, but there are some values more than maxOutlier!\nList of upper tails: {}".format(test, maxHalfBodies, upperOutliers)
                assert maxLowOutliers <= test + maxHalfBodies, "All candle 'tails' must be less than  maxOutlier + maxHalfBodies = {} + {}, but there are some values more than maxOutlier!\nList of lower tails: {}".format(test, maxHalfBodies, lowerOutliers)

    def test_maxCandleBody(self):
        testData = [None, 0, 1, 10, 100]
        for test in testData:
            self.model.horizon = 10
            self.model.minClose = 10
            self.model.maxClose = 110
            self.model.maxOutlier = 10
            self.model.initClose = 50
            self.model.maxCandleBody = test  # set test data as "maxCandleBody" field in PriceGenerator() class
            self.model.Generate()  # if maxOutlier == None then used (maxClose - minClose) / 10
            if test is None:
                correctMaxCandleBody = self.model.maxOutlier * 0.9
                assert self.model.maxCandleBody == correctMaxCandleBody, "if maxCandleBody == None then used maxOutlier * 90% = {} but {} given!".format(correctMaxCandleBody, self.model.maxCandleBody)
            else:
                bodies = list(abs(self.model.prices.open - self.model.prices.close))
                maxBody = max(bodies)
                assert maxBody <= test, "All candles bodies must be less than maxCandleBody = {}, but there are some values more than maxCandleBody!\nList of bodies: {}".format(test, bodies)

    def test_maxVolume(self):
        testData = [[-1, 0], [None, 0], [0, 0], [1, 1], [10, 10], [100, 100]]
        for test in testData:
            self.model.horizon = 10
            self.model.minClose = 10
            self.model.maxClose = 110
            self.model.maxOutlier = 10
            self.model.initClose = 50
            self.model.maxCandleBody = 20
            self.model.maxVolume = test[0]  # set test data as "maxVolume" field in PriceGenerator() class
            self.model.Generate()
            assert self.model.prices.volume.max() <= test[1], "All candles volumes must be less than maxVolume = {}, but there are some values more than maxVolume!\nList of volumes: {}".format(test[1], list(self.model.prices.volume))
