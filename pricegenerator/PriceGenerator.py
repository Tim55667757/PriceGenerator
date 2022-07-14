# -*- coding: utf-8 -*-
# Author: Timur Gilmullin

"""
A simple price generator similar to real stock prices, but you can control the statistics of their distribution.
Use it to generate synthetic data to test your trading strategy.

This module generates chain of candlesticks with predefined statistical parameters, return pandas dataframe,
saving as .csv-file or .html-file with OHLCV-candlestick in every strings.

In additional you can view some statistical and probability parameters of generated or loaded prices.
"""

# Copyright (c) 2022 Gilmillin Timur Mansurovich
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import sys
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from argparse import ArgumentParser

from math import pi
from statistics import mode, pstdev, StatisticsError
from itertools import groupby
import pandas as pd
import pandas_ta as ta
import random
from bokeh.plotting import figure, save, output_file, ColumnDataSource
from bokeh.models import Legend, HoverTool, Range1d, NumeralTickFormatter
from bokeh.layouts import gridplot
import jinja2

import pricegenerator.UniLogger as uLog
import traceback as tb


# --- Common technical parameters:

uLogger = uLog.UniLogger
uLogger.level = 10  # debug level by default
uLogger.handlers[0].level = 20  # info level by default for STDOUT
# uLogger.handlers[1].level = 10  # debug level by default for log.txt

# Simple jinja2 template for rendering static html-page with not interactive Google Candlestick chart:
GOOGLE_TEMPLATE_J2 = """{# This template based on Jinja markup language: http://jinja.pocoo.org/docs/dev/templates/ #}
<!DOCTYPE html>
<html>

<head>
    <title>{{ title }}</title>
    <meta charset="utf-8">
    <script type="text/javascript" src="https://code.jquery.com/jquery-latest.min.js"></script>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">google.charts.load('current', {'packages': ['corechart']});</script>
    <style type="text/css">
    #preloader {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #FFFFFF;
        z-index: 99;
    }
    #status {
        width: 300px;
        height: 150px;
        position: absolute;
        left: 50%;
        top: 50%;
        background-image: url(https://raw.githubusercontent.com/niklausgerber/PreLoadMe/master/img/status.gif);
        background-repeat: no-repeat;
        background-position: left;
        margin: -100px 0 0 -100px;
        font-family: "Segoe UI", "Frutiger", "Frutiger Linotype", "Dejavu Sans", "Helvetica Neue", "Arial", sans-serif;
        font-size: 14px;
    }
    pre {
        font-family: "Lucida Console", sans-serif;
        font-size: 11px;
        padding: 0;
        border-width: 0 0 0 0;
    }
    table {
        font-family: "Segoe UI", "Frutiger", "Frutiger Linotype", "Dejavu Sans", "Helvetica Neue", "Arial", sans-serif;
        font-size: 12px;
        border-spacing: 0;
        text-align: left;
        background: white;
        width: 100%;
    }
    th {
        border-radius: 10px 10px 10px 10px;
        border-style: solid;
        border-width: 0 1px 1px 0;
        border-color: white;
        padding: 6px;
        vertical-align: middle;
        padding-left: 1em;
        background: #E6E6E6;
        height: 50px;
    }
    td {
        border-radius: 10px 10px 10px 10px;
        border-style: solid;
        border-width: 0 1px 1px 0;
        border-color: white;
        padding: 6px;
        vertical-align: top;
        padding-left: 1em;
        background: white;
    }
    </style>
    <script>
    function drawChartCandlesticks(candlesData) {
        var chartOptions = {
            legend: "none",
            titlePosition: "in",
            chartArea: {width: "100%", height: "100%"},
            fontSize: 11,
            candlestick: {
                fallingColor: {stroke: "#000000", strokeWidth: 1, fill: "#999999"},
                risingColor: {stroke: "#000000",  strokeWidth: 1, fill: "#FFFFFF"},
            },
            colors: ["#000000"],
            hAxis: {textPosition: "none"},
            vAxis: {textPosition: "in", textStyle: {fontSize: 12}},
        }
        if (typeof candlesData !== "undefined") {
            var data = google.visualization.arrayToDataTable(candlesData, true);
            var chart = new google.visualization.CandlestickChart(document.getElementById("candlestickChart"));
            chart.draw(data, chartOptions);
        }
    }
    </script>
</head>


<body onload="drawChartCandlesticks({{ candlesData }})">


<!-- Preloader -->
<script>
    $(window).on('load', function() {
        $('#status').fadeOut('slow');
        $('#preloader').fadeOut('slow');
    })
</script>
<div id="preloader">
    <div id="status">Wait...</div>
</div>


<!-- Chart part -->

<table id="chart">
    <tr>
        <th style="width: 75%;">
            <b>{{ title }}</b>
        </th>
        <th>
            <b>Info</b>
        </th>
    </tr>
    <tr>
        <td>
            <div id="candlestickChart" style="height: 800px; width: 100%;"></div>
        </td>
        <td>
            {% for line in info %}
                <pre>{{ line }}</pre>
            {% endfor %}
        </td>
    </tr>
</table>


<!-- Footer -->

<table>
    <tr>
        <th><b>Generated by <a href="https://github.com/Tim55667757/PriceGenerator">PriceGenerator</a></b></th>
    </tr>
</table>


</body>

</html>
"""


class PriceGenerator:
    """
    This class implements methods to generation of prices statistically similar to real ones.
    """

    def __init__(self):
        self.prices = None  # generated or loaded prices will be put into this Pandas variable

        self.csvHeaders = ["date", "time", "open", "high", "low", "close", "volume"]  # headers if .csv-file used
        self.dfHeaders = ["datetime", "open", "high", "low", "close", "volume"]  # dataframe headers
        self.sep = ","  # Separator in csv-file
        self.j2template = GOOGLE_TEMPLATE_J2  # full path to custom jinja2 html template (e.g. "google_template_example.j2") or template as a long multi-string variable
        self.j2model = None  # dictionary of variables for jinja2 template, if None then auto-generating for default google_template.j2

        self._precision = 2  # signs after comma
        self._deg10prec = 10 ** 2  # 10^precision is used for some formulas

        self.ticker = "TEST"  # some fake ticker name
        self.timeframe = timedelta(hours=1)  # time delta between two neighbour candles, 1 hour by default
        self.timeStart = datetime.now(tzlocal()).replace(microsecond=0, second=0, minute=0)
        self.horizon = None  # Candlesticks count (generating or in view), must be >= 5 for generator
        self.trendSplit = ""  # set difference periods, e.g. split="/\-" means that generated candles has up trend at first part, next down trend and then no trend
        self.splitCount = []  # set count of candles of difference periods, e.g. splitCount=[5, 10, 15] means that generated candles has 3 trends with 5, 10 and 15 candles in chain, with sum equal to horizon
        self.maxClose = random.uniform(70, 90)  # maximum of close prices must be >= self.minClose
        self.minClose = random.uniform(60, 70)  # minimum of close prices must be <= self.maxClose
        self.initClose = None  # if not None generator started 1st open price of chain from this price
        self.maxOutlier = None  # maximum of outlier size of candle tails, if None then used (maxClose - minClose) / 10
        self.maxCandleBody = None  # maximum of candle body sizes: abs(open - close), if None then used maxOutlier * 90%
        self._maxVolume = random.randint(0, 100000)  # maximum of trade volumes
        self._upCandlesProb = 0.5  # probability that next candle is up, 50% by default
        self._outliersProb = 0.03  # statistical outliers probability (price "tails"), 3% by default
        self._trendDeviation = 0.005  # relative deviation for trend detection, 0.005 mean ±0.5% by default. "NO trend" if (1st_close - last_close) / 1st_close <= self.trendDeviation

        self._chartTitle = ""  # chart title, auto-generated when loading or creating chain of candlesticks

        self._zigZagDeviation = 0.03  # relative deviation to detection points of Zig-Zag indicator, 0.03 mean 3% by default

        # some default statistics for calculation:
        self._stat = {
            "candles": 0,  # generated candlesticks count
            "precision": 2,  # generated candlesticks count
            "closeFirst": 0.,  # first close price
            "closeLast": 0.,  # last close price
            "closeMax": 0.,  # max close price
            "closeMix": 0.,  # min close price
            "diapason": 0.,  # diapason = closeMax - closeMin
            "trend": "NO trend",  # "UP trend" or "DOWN trend" with uses ±self.trendDeviation
            "trendDev": 0.005,
            "upCount": 0,  # count of up candles
            "downCount": 0,  # count of down candles
            "upCountChainMax": 0,  # max chain count of up candles
            "downCountChainMax": 0,  # max chain count of down candles
            "deltas": {
                "max": 0.,  # delta max = max(close_prices)
                "min": 0.,  # delta min = min(close_prices)
                "stDev": 0.,  # standard deviation
                "q99": 0.,  # 99 percentile
                "q95": 0.,  # 95 percentile
                "q80": 0.,  # 80 percentile
                "q50": 0.,  # 50 percentile
            },
            "cumSumVolumes": 0  # cumulative sum of volumes
        }

    @property
    def upCandlesProb(self):
        return self._upCandlesProb

    @upCandlesProb.setter
    def upCandlesProb(self, value):
        if value is None or value < 0:
            self._upCandlesProb = 0

        elif value > 1:
            self._upCandlesProb = 1

        else:
            self._upCandlesProb = value

    @property
    def outliersProb(self):
        return self._outliersProb

    @outliersProb.setter
    def outliersProb(self, value):
        if value is None or value < 0:
            self._outliersProb = 0

        elif value > 1:
            self._outliersProb = 1

        else:
            self._outliersProb = value

    @property
    def trendDeviation(self):
        return self._trendDeviation

    @trendDeviation.setter
    def trendDeviation(self, value):
        if value is None or value < 0:
            self._trendDeviation = 0

        elif value > 1:
            self._trendDeviation = 1

        else:
            self._trendDeviation = value

    @property
    def maxVolume(self):
        return self._maxVolume

    @maxVolume.setter
    def maxVolume(self, value):
        if value is None or value < 0:
            self._maxVolume = 0

        else:
            self._maxVolume = value

    @property
    def stat(self) -> dict:
        return self._stat

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, value):
        self._precision = 2  # default
        self._deg10prec = 100  # default

        if isinstance(value, int):
            if value >= 0:
                self._precision = value
                self._deg10prec = 10 ** value  # 10^precision

    @property
    def zigZagDeviation(self):
        return self._zigZagDeviation

    @zigZagDeviation.setter
    def zigZagDeviation(self, value):
        if value is None or value < 0:
            self._zigZagDeviation = 0.03  # by default

        elif value > 1:
            self._zigZagDeviation = 1

        else:
            self._zigZagDeviation = value

    @staticmethod
    def FormattedDelta(tDelta, fmt):
        """
        Return timedelta formatted as string, e.g. FormattedDelta(delta_obj, "{days} days {hours}:{minutes}:{seconds}")
        """
        d = {"days": tDelta.days}
        d["hours"], rem = divmod(tDelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)

        return fmt.format(**d)

    def DetectPrecision(self, examples):
        """
        Auto detect precision from example values. E.g. 0.123 => 3, 0.12345 => 5 and so on.
        This method set self.precision variable after detect precision.
        :param examples: numpy.ndarray with examples of float values.
        """
        uLogger.debug("Detecting precision of data values...")
        try:
            if self.precision != 0:
                self.precision = mode(list(map(lambda x: len(str(x).split('.')[-1]) if len(str(x).split('.')) > 1 else 0, examples)))

        except StatisticsError as e:
            uLogger.warning("Unable to unambiguously determine Mode() of the value of precision! Precision is set to 2 (default). StatisticsError: '{}'".format(e))
            self.precision = 2

        finally:
            uLogger.debug("Auto-detected precision: {}".format(self._precision))

    def DetectTimeframe(self) -> timedelta:
        """
        Auto-detect time delta between last two neighbour candles.
        :return: timedelta object to self.timeframe
        """
        self.timeframe = min(
            self.prices.iloc[-1].datetime - self.prices.iloc[-2].datetime,
            self.prices.iloc[-2].datetime - self.prices.iloc[-3].datetime
        )
        uLogger.debug("Auto-detected timeframe: {}".format(self.timeframe))

        return self.timeframe

    def LoadFromFile(self, fileName):
        """
        Load Pandas OHLCV model from csv-file.
        :param fileName: path to csv-file with OHLCV columns.
        :return: Pandas dataframe.
        """
        uLogger.info("Loading, parse and preparing input data from [{}]...".format(os.path.abspath(fileName)))

        self.prices = pd.read_csv(fileName, names=self.csvHeaders, engine="python", sep=self.sep, parse_dates={"datetime": ["date", "time"]})
        if self.horizon is None or self.horizon < 1 or self.horizon > len(self.prices):
            self.horizon = len(self.prices)  # use loaded file "as is" with all candles

        else:
            self.prices = self.prices.tail(self.horizon)  # remove old candles, leave only the "tail" ...
            self.prices.index = range(self.horizon)  # ... and reindex

        self.ticker = os.path.basename(fileName)

        self.DetectTimeframe()  # auto-detect time delta between last two neighbour candles

        uLogger.info("It was read {} rows".format(self.horizon))
        uLogger.info("Showing last 5 rows as pandas dataframe:")
        for line in pd.DataFrame.to_string(self.prices[self.dfHeaders][-5:], max_cols=20).split("\n"):
            uLogger.info(line)

        return self.prices

    def SaveToFile(self, fileName):
        """
        Save Pandas OHLCV model to csv-file.
        :param fileName: path to csv-file.
        """
        if self.prices is not None and not self.prices.empty:
            uLogger.info("Saving [{}] rows of pandas dataframe with columns: {}...".format(len(self.prices), self.csvHeaders))
            uLogger.debug("Delimeter: {}".format(self.sep))
            dataReplacedDateTime = self.prices.copy(deep=True)
            dataReplacedDateTime["date"] = [d.date() for d in dataReplacedDateTime["datetime"]]
            dataReplacedDateTime["time"] = [d.time() for d in dataReplacedDateTime["datetime"]]
            del dataReplacedDateTime["datetime"]
            dataReplacedDateTime = dataReplacedDateTime[self.csvHeaders]
            dataReplacedDateTime.to_csv(fileName, sep=self.sep, index=False, header=False)
            uLogger.info("Pandas dataframe saved to .csv-file [{}]".format(os.path.abspath(fileName)))

        else:
            raise Exception("Empty price data! Generate or load prices before saving!")

    @staticmethod
    def GetTrend(firstClose, lastClose, trendDeviation=0.005):
        """
        Get string with trend: "UP trend", "DOWN trend" or "NO trend".
        :param firstClose: close of first candle.
        :param lastClose: close of last candle.
        :param trendDeviation: relative deviation for trend detection, 0.005 mean ±0.5% by default.
        :return: string
        """
        if abs(firstClose - lastClose) / firstClose <= trendDeviation:
            trend = "NO trend"

        else:
            trend = "UP trend" if firstClose <= lastClose else "DOWN trend"

        return trend

    @staticmethod
    def ZigZagFilter(datetimes: pd.Series, values: pd.Series, deviation: float) -> dict:
        """
        This method filter input data as ZigZag indicator: when input value of candlestick price (e.g. close price)
        is difference with next values with define percent then this point is a point of ZigZag indicator.
        :param datetimes: input pandas Series with datetime values.
        :param values: input pandas Series or list, e.g. list of closes values of candlesticks.
        :param deviation: [0, 1] float number is a relative difference between i and i+1 values to set as ZigZag point.
        :return: dict with pandas Series filtered data: {"datetimes": filtered_datetimes, "filtered": filtered_values}
        """
        filteredPoints = [True]
        prev = values[0]
        for i in range(1, len(values)):
            difference = abs(values[i] - prev) / prev
            if difference >= deviation:
                filteredPoints.append(True)
                prev = values[i]

            else:
                filteredPoints.append(False)

        return {"datetimes": datetimes[filteredPoints], "filtered": values[filteredPoints]}

    def GetStatistics(self):
        """
        Calculates statistics of candles chain.
        :return: text in markdown with statistics.
        """
        uLogger.debug("Calculating column with deltas between high and low values...")
        self.prices["delta"] = list(map(
            lambda x, y: x - y,
            self.prices.high.values,
            self.prices.low.values
        ))

        uLogger.debug("Calculating column with average values...")
        self.prices["avg"] = list(map(
            lambda x, y: x - y / 2,
            self.prices.high.values,
            self.prices.delta.values
        ))

        uLogger.debug("Calculating some technical analysis indicators...")
        self.prices["sma5"] = ta.sma(close=self.prices.close, length=5, offset=None)
        self.prices["sma20"] = ta.sma(close=self.prices.close, length=20, offset=None)
        self.prices["sma50"] = ta.sma(close=self.prices.close, length=50, offset=None)
        self.prices["sma200"] = ta.sma(close=self.prices.close, length=200, offset=None)
        self.prices["hma5"] = ta.hma(close=self.prices.close, length=5, offset=None)
        self.prices["hma20"] = ta.hma(close=self.prices.close, length=20, offset=None)
        self.prices["vwma5"] = ta.vwma(close=self.prices.close, volume=self.prices.volume, length=5, offset=None)
        self.prices["vwma20"] = ta.vwma(close=self.prices.close, volume=self.prices.volume, length=20, offset=None)
        bbands = ta.bbands(close=self.prices.close, length=None, std=None, mamode=None, offset=None)
        bbands.columns = ["lower", "mid", "upper", "bandwidth", "percent"]
        psar = ta.psar(high=self.prices.high, low=self.prices.low, close=self.prices.close, af=0.02, max_af=0.2, offset=None)
        psar.columns = ["long", "short", "af", "reversal"]
        self.prices["hma13"] = ta.hma(close=self.prices.close, length=13, offset=8)  # alligator Jaw
        self.prices["hma8"] = ta.hma(close=self.prices.close, length=8, offset=5)  # alligator Teeth
        self.prices["hma5"] = ta.hma(close=self.prices.close, length=5, offset=3)  # alligator Lips
        zigzag = self.ZigZagFilter(datetimes=self.prices.datetime, values=self.prices.close, deviation=self.zigZagDeviation)  # ZigZag indicator

        self.DetectPrecision(self.prices.close.values)  # auto-detect precision

        self._chartTitle = "Instrument: {}, timeframe: {}, horizon length: {} (from {} to {})".format(
            self.ticker,
            self.FormattedDelta(
                self.timeframe, "{days} days {hours}h {minutes}m {seconds}s"
            ) if self.timeframe >= timedelta(days=1) else self.FormattedDelta(
                self.timeframe, "{hours}h {minutes}m {seconds}s"
            ),
            self.horizon,
            pd.to_datetime(self.prices.datetime.values[0]).strftime("%Y-%m-%d %H:%M:%S"),
            pd.to_datetime(self.prices.datetime.values[-1]).strftime("%Y-%m-%d %H:%M:%S"),
        )

        self._stat["candles"] = len(self.prices)
        self._stat["precision"] = self.precision
        self._stat["closeFirst"] = self.prices.close.values[0]
        self._stat["closeLast"] = self.prices.close.values[-1]
        self._stat["closeMax"] = pd.DataFrame.max(self.prices.close)
        self._stat["closeMin"] = pd.DataFrame.min(self.prices.close)
        self._stat["diapason"] = self._stat["closeMax"] - self._stat["closeMin"]
        self._stat["trend"] = self.GetTrend(firstClose=self._stat["closeFirst"], lastClose=self._stat["closeLast"], trendDeviation=self.trendDeviation)

        self.prices["up"] = self.prices.close >= self.prices.open  # True mean that is up candle, and False mean down
        upList = list(self.prices.up)
        upChainsLengths = [len(list(chain)) for value, chain in groupby(upList) if value is True]
        downChainsLengths = [len(list(chain)) for value, chain in groupby(upList) if value is False]

        self._stat["trendDev"] = self.trendDeviation
        self._stat["upCount"] = len(self.prices.up[self.prices.up == True])
        self._stat["downCount"] = len(self.prices.up[self.prices.up == False])
        self._stat["upCountChainMax"] = max(upChainsLengths) if upChainsLengths else 1
        self._stat["downCountChainMax"] = max(downChainsLengths) if downChainsLengths else 1
        self._stat["deltas"]["max"] = pd.DataFrame.max(self.prices.delta)
        self._stat["deltas"]["min"] = pd.DataFrame.min(self.prices.delta)
        self._stat["deltas"]["stDev"] = round(pstdev(self.prices.delta), self._precision)
        self._stat["deltas"]["q99"] = round(max(pd.DataFrame(self.prices.delta).quantile(q=0.99, interpolation='linear')), self._precision)
        self._stat["deltas"]["q95"] = round(max(pd.DataFrame(self.prices.delta).quantile(q=0.95, interpolation='linear')), self._precision)
        self._stat["deltas"]["q80"] = round(max(pd.DataFrame(self.prices.delta).quantile(q=0.80, interpolation='linear')), self._precision)
        self._stat["deltas"]["q50"] = round(max(pd.DataFrame(self.prices.delta).quantile(q=0.50, interpolation='linear')), self._precision)
        self._stat["cumSumVolumes"] = self.prices.volume.sum()

        self._stat["sma5"] = self.prices["sma5"]
        self._stat["sma20"] = self.prices["sma20"]
        self._stat["sma50"] = self.prices["sma50"]
        self._stat["sma200"] = self.prices["sma200"]
        self._stat["hma5"] = self.prices["hma5"]
        self._stat["hma20"] = self.prices["hma20"]
        self._stat["vwma5"] = self.prices["vwma5"]
        self._stat["vwma20"] = self.prices["vwma20"]
        self._stat["bbands"] = bbands
        self._stat["psar"] = psar
        self._stat["hma13"] = self.prices["hma13"]
        self._stat["hma8"] = self.prices["hma8"]
        self._stat["hma5"] = self.prices["hma5"]
        self._stat["zigzag3"] = zigzag

        summary = [
            "# Summary",
            "| Parameter                                    | Value",
            "|----------------------------------------------|---------------",
            "| Candles count:                               | {}".format(self.stat["candles"]),
            "| Timeframe:                                   | {}".format(self.timeframe),
            "| Precision (signs after comma):               | {}".format(self.stat["precision"]),
            "| Close first:                                 | {}".format(round(self.stat["closeFirst"], self.precision)),
            "| Close last:                                  | {}".format(round(self.stat["closeLast"], self.precision)),
            "| Close max:                                   | {}".format(round(self.stat["closeMax"], self.precision)),
            "| Close min:                                   | {}".format(round(self.stat["closeMin"], self.precision)),
            "| Diapason (between max and min close prices): | {}".format(round(self.stat["diapason"], self.precision)),
            "| Trend (between close first and close last:   | {}".format(self.stat["trend"]),
            "",
            "# Some statistics",
            "| Statistic                                    | Value",
            "|----------------------------------------------|---------------",
            "| Up candles count:                            | {} ({}%)".format(self.stat["upCount"], round(100 * self.stat["upCount"] / self.stat["candles"], self.precision)),
            "| Down candles count:                          | {} ({}%)".format(self.stat["downCount"], round(100 * self.stat["downCount"] / self.stat["candles"], self.precision)),
            "| Max of up / down candle chains:              | {} / {}".format(self.stat["upCountChainMax"], self.stat["downCountChainMax"]),
            "| Max delta (between High and Low prices):     | {}".format(round(self.stat["deltas"]["max"], self.precision)),
            "| Min delta (between High and Low prices):     | {}".format(round(self.stat["deltas"]["min"], self.precision)),
            "| Delta's std. dev.:                           | {}".format(round(self.stat["deltas"]["stDev"], self.precision)),
            "| - 99 percentile:                             | ≤ {}".format(round(self.stat["deltas"]["q99"], self.precision)),
            "| - 95 percentile:                             | ≤ {}".format(round(self.stat["deltas"]["q95"], self.precision)),
            "| - 80 percentile:                             | ≤ {}".format(round(self.stat["deltas"]["q80"], self.precision)),
            "| Cumulative sum of volumes:                   | {}".format(self.stat["cumSumVolumes"]),
        ]

        uLogger.info("Some statistical info:\n{}".format("\n".join(summary)))

        return summary

    def _GenNextCandle(self, lastClose):
        """
        Generator for creating 1 next candle based on global probability parameters.
        :param lastClose: value of last close price.
        :return: OHLCV-candle as dict.
        """
        candle = {
            "open": lastClose,
            "high": 0,
            "low": 0,
            "close": 0,
            "volume": random.randint(a=0, b=self.maxVolume)
        }

        if random.random() <= self.upCandlesProb:
            maxBody = min(self.maxClose, candle["open"] + self.maxCandleBody)
            candle["close"] = round(random.uniform(a=candle["open"], b=maxBody), self.precision)  # up candle

            if random.random() <= self.outliersProb:
                candle["high"] = round(random.uniform(a=candle["close"], b=candle["close"] + self.maxOutlier), self.precision)  # with outlier price "tails"
                candle["low"] = round(random.uniform(a=candle["open"] - self.maxOutlier, b=candle["open"]), self.precision)

            else:
                halfBody = (candle["close"] - candle["open"]) / 2
                candle["high"] = round(random.uniform(a=candle["close"], b=candle["close"] + halfBody), self.precision)  # without outlier price "tails"
                candle["low"] = round(random.uniform(a=candle["open"] - halfBody, b=candle["open"]), self.precision)

        else:
            minBody = max(self.minClose, candle["open"] - self.maxCandleBody)
            candle["close"] = round(random.uniform(a=minBody, b=candle["open"]), self.precision)  # down candle

            if random.random() <= self.outliersProb:
                candle["high"] = round(random.uniform(a=candle["open"], b=candle["open"] + self.maxOutlier), self.precision)  # with outlier price "tails"
                candle["low"] = round(random.uniform(a=candle["close"] - self.maxOutlier, b=candle["close"]), self.precision)

            else:
                halfBody = (candle["open"] - candle["close"]) / 2
                candle["high"] = round(random.uniform(a=candle["open"], b=candle["open"] + halfBody), self.precision)  # without outlier price "tails"
                candle["low"] = round(random.uniform(a=candle["close"] - halfBody, b=candle["close"]), self.precision)

        return candle

    def Generate(self):
        """
        Main method to generate prices.
        :return Pandas object with OHLCV-candlestick in every line and also saving it to the self.prices.
        """
        if self.horizon is None or self.horizon < 5:
            self.horizon = 5
            uLogger.warning("Horizon length less than 5! It is set to 5 by default.")

        if self.trendSplit is not None and self.splitCount is not None:
            if len(self.trendSplit) > self.horizon:
                uLogger.warning("Trend parts count ({}) must be less than horizon ({})! New trend: {}".format(len(self.trendSplit), self.horizon, self.trendSplit[0]))
                self.trendSplit = self.trendSplit[0]

            if sum(self.splitCount) != self.horizon or len(self.trendSplit) == 1:
                self.splitCount = [self.horizon]
                uLogger.warning("Set only one trend with length equal to horizon: {}".format(self.splitCount))

            if len(self.splitCount) != len(self.trendSplit):
                self.trendSplit = None
                self.splitCount = None
                uLogger.warning("See help to work with --split-trend and --split-count keys.")

        # maximum of candle sizes: (high - low), if None then used (maxClose - minClose) / 10
        if self.maxOutlier is None:
            self.maxOutlier = (self.maxClose - self.minClose) / 10

        # maximum of candle body sizes: abs(open - close), if None then used maxOutlier * 90%
        if self.maxCandleBody is None:
            self.maxCandleBody = 0.9 * self.maxOutlier

        # initClose is the last close price (left on chart or "before" 1st generated candle), 1st candle["open"] = initClose
        if self.initClose is None:
            self.initClose = round(random.uniform(a=self.minClose, b=self.maxClose), self.precision)

        uLogger.info("Generating prices...")
        uLogger.debug("- Ticker name: {}".format(self.ticker))
        uLogger.debug("- Precision: {}".format(self.precision))
        uLogger.debug("- Interval or timeframe (time delta between two neighbour candles): {}".format(self.timeframe))
        uLogger.debug("- Horizon length (candlesticks count): {}".format(self.horizon))
        if self.trendSplit is not None and self.trendSplit and self.splitCount is not None and self.splitCount:
            uLogger.debug("- Trend type: {}".format(self.trendSplit))
            uLogger.debug("- Candlesticks count in every mini-trend: {}".format(self.splitCount))

        uLogger.debug("- Start time: {}".format(self.timeStart.strftime("%Y-%m-%d %H:%M:%S")))
        uLogger.debug("  |-> end time: {}".format((self.timeStart + self.horizon * self.timeframe).strftime("%Y-%m-%d %H:%M:%S")))
        uLogger.debug("- Maximum of close prices: {}".format(round(self.maxClose, self.precision)))
        uLogger.debug("- Minimum of close prices: {}".format(round(self.minClose, self.precision)))
        uLogger.debug("- Maximum of candle body sizes: {}".format(round(self.maxCandleBody, self.precision)))
        uLogger.debug("- Maximum of candle tails outlier sizes: {}".format(round(self.maxOutlier, self.precision)))
        uLogger.debug("- Init close (1st open price in chain): {}".format(round(self.initClose, self.precision)))
        uLogger.debug("- Maximum of volume of one candle: {}".format(self.maxVolume))
        uLogger.debug("- Probability that next candle is up: {}%".format(self.upCandlesProb * 100))
        uLogger.debug("- Statistical outliers probability: {}%".format(self.outliersProb * 100))

        # prepare candles chain:
        if self.trendSplit is not None and self.trendSplit and self.splitCount is not None and self.splitCount:
            userProb = self.upCandlesProb
            userHorizon = self.horizon
            userInitC = self.initClose
            candles = []

            for trendNum in range(len(self.splitCount)):
                self.horizon = self.splitCount[trendNum]
                self.initClose = candles[-1]["close"] if trendNum > 0 else self.initClose

                # change probability of candles direction in next trend:
                if self.trendSplit[trendNum] == "/":
                    self.upCandlesProb = 0.51 if userProb <= 0.5 else userProb

                elif self.trendSplit[trendNum] == "\\":
                    self.upCandlesProb = 0.49 if userProb >= 0.5 else userProb

                else:
                    self.upCandlesProb = 0.5

                firstCandle = self._GenNextCandle(round(self.initClose, self.precision))  # first candle in next trend
                candles.append(firstCandle)

                for _ in range(1, self.horizon):
                    candles.append(self._GenNextCandle(candles[-1]["close"]))

                # change last candle in every trend:
                if self.trendSplit[trendNum] == "/":
                    if firstCandle["close"] > candles[-1]["close"]:
                        candles[-1]["close"] = round(random.uniform(a=firstCandle["close"], b=self.maxClose), self.precision)

                elif self.trendSplit[trendNum] == "\\":
                    if firstCandle["close"] < candles[-1]["close"]:
                        candles[-1]["close"] = round(random.uniform(a=self.minClose, b=firstCandle["close"]), self.precision)

                else:
                    if abs(firstCandle["close"] - candles[-1]["close"]) / firstCandle["close"] > self.trendDeviation:
                        candles[-1]["close"] = round(
                            random.uniform(
                                a=firstCandle["close"] - firstCandle["close"] * self.trendDeviation / 2,
                                b=firstCandle["close"] + firstCandle["close"] * self.trendDeviation / 2,
                            ),
                            self.precision,
                        )

            self.upCandlesProb = userProb
            self.horizon = userHorizon
            self.initClose = userInitC

        else:
            candles = [self._GenNextCandle(round(self.initClose, self.precision))]  # first candle in chain
            for _ in range(1, self.horizon):
                candles.append(self._GenNextCandle(candles[-1]["close"]))

        # prepare Dataframe from generated prices:
        indx = pd.date_range(
            start=self.timeStart,
            end=self.timeStart + (self.horizon - 1) * self.timeframe,
            freq=self.timeframe,
            tz=tzlocal(),
        )
        self.prices = pd.DataFrame(data=candles, columns=self.dfHeaders)
        self.prices.datetime = indx

        uLogger.info("Showing last 5 rows of Pandas generated dataframe object:")
        for line in pd.DataFrame.to_string(self.prices[self.dfHeaders][-5:], max_cols=20).split("\n"):
            uLogger.info(line)

        return self.prices

    def RenderBokeh(self, fileName="index.html", viewInBrowser=False):
        """
        Rendering prices from pandas dataframe to Bokeh chart of candlesticks and save to html-file.
        See: https://docs.bokeh.org/en/latest/docs/gallery/candlestick.html
        :param fileName: html-file path to save Bokeh chart.
        :param viewInBrowser: If True, then immediately opens html in browser after rendering.
        """
        if self.prices is not None and not self.prices.empty:
            uLogger.info("Rendering pandas dataframe as Bokeh chart...")

            self.DetectTimeframe()  # auto-detect time delta between last two neighbour candles
            infoBlock = self.GetStatistics()  # calculating some indicators

            uLogger.debug("Preparing Bokeh chart configuration...")
            uLogger.debug("Title: {}".format(self._chartTitle))

            # --- Preparing Main chart:
            chart = figure(
                title=self._chartTitle,
                x_axis_type="datetime",
                y_axis_label="Price",
                outline_line_width=2,
                outline_line_color="white",
                tools=["pan", "wheel_zoom", "box_zoom", "hover", "reset", "save"],
                toolbar_location="above",
                active_scroll="wheel_zoom",
                plot_width=1200,
                plot_height=540,
                sizing_mode="scale_width",
                background_fill_color="black",
                min_border_left=0,
                min_border_right=0,
                min_border_top=0,
                min_border_bottom=0,
            )
            chart.toolbar.logo = None  # remove bokeh logo and link to https://bokeh.org/
            chart.xaxis.major_label_orientation = pi / 6
            chart.grid.grid_line_dash = [6, 4]
            chart.grid.grid_line_alpha = 0.5
            chart.grid.minor_grid_line_dash = [6, 4]
            chart.grid.minor_grid_line_alpha = 0.5
            chart.xgrid.minor_grid_line_dash = [6, 4]
            chart.xgrid.minor_grid_line_alpha = 0.3
            chart.xgrid.minor_grid_line_color = "white"
            chart.ygrid.minor_grid_line_dash = [6, 4]
            chart.ygrid.minor_grid_line_alpha = 0.3
            chart.ygrid.minor_grid_line_color = "white"

            # Summary section and controls:
            legendNameMain = "Max close / Min close / Trend line"
            legendNameAvg = "Averages points (highs - deltas/2)"
            legendNameSMA = "Simple Moving Averages (SMA: 5, 20)"
            legendNameSMAlong = "Long Simple Moving Averages (SMA: 50, 200)"
            legendNameHMA = "Hull Moving Averages (HMA: 5, 20)"
            legendNameVWMA = "Volume Weighted Moving Averages (VWMA: 5, 20)"
            legendNameBBANDS = "Bollinger Bands (BBands)"
            legendNamePsar = "Parabolic Stop and Reverse (psar)"
            legendNameAlligator = "Alligator (based on HMA: 13, 8, 5)"
            legendNameZigZag = "Zig-Zag indicator (with {}% of difference)".format(self.zigZagDeviation * 100)
            summaryInfo = Legend(
                click_policy="hide",
                items=[(info, []) for info in infoBlock] + [("", []), ("Click to show/hide on chart:", [])],
                location="top_right",
                label_text_font_size="8pt",
                margin=0,
                padding=0,
                spacing=0,
                label_text_font="Lucida Console",
            )
            chart.add_layout(summaryInfo, 'right')

            # preparing data for candles:
            inc = self.prices.open <= self.prices.close
            dec = self.prices.open > self.prices.close
            candleWidth = 108000  # as for 5 minutes by default

            if self.timeframe <= timedelta(days=31):
                candleWidth = 864000000  # 12 * 60 * 60 * 25 * 800  # for 43200 minutes

            if self.timeframe <= timedelta(days=7):
                candleWidth = 216000000  # 12 * 60 * 60 * 25 * 200  # for 10080 minutes

            if self.timeframe <= timedelta(days=1):
                candleWidth = 32400000  # 12 * 60 * 60 * 25 * 30  # for 1440 minutes

            if self.timeframe <= timedelta(hours=4):
                candleWidth = 6480000  # 12 * 60 * 60 * 25 * 6  # for 240 minutes

            if self.timeframe <= timedelta(hours=1):
                candleWidth = 1620000  # 12 * 60 * 60 * 25 * 1.5  # for 60 minutes

            if self.timeframe <= timedelta(minutes=30):
                candleWidth = 648000  # 12 * 60 * 60 * 15  # for 30 minutes

            if self.timeframe <= timedelta(minutes=15):
                candleWidth = 345600  # 12 * 60 * 60 * 8  # for 15 minutes

            if self.timeframe <= timedelta(minutes=5):
                candleWidth = 108000  # 12 * 60 * 60 * 2.5  # for 5 minutes

            if self.timeframe <= timedelta(minutes=1):
                candleWidth = 21600  # 12 * 60 * 30   # for 1 minute

            disabledObjects = []  # bokeh objects to hide by default when page is loaded

            # preparing data for hover tooltips:
            source = {
                "candle": [x + 1 for x in range(-len(self.prices.close), 0, 1)],
                "datetime": self.prices.datetime,
                "open": self.prices.open,
                "high": self.prices.high,
                "low": self.prices.low,
                "close": self.prices.close,
                "volume": self.prices.volume,
            }
            hoverData = ColumnDataSource(data=source)
            hover = chart.select(dict(type=HoverTool))
            hover.names = ["candle"]
            hover.tooltips = [
                ("Candle", "@candle"),
                ("Date", "@datetime{%Y-%m-%d}"),
                ("Time", "@datetime{%H:%M:%S}"),
                ("Open", "@open{0.0000}"),
                ("High", "@high{0.0000}"),
                ("Low", "@low{0.0000}"),
                ("Close", "@close{0.0000}"),
                ("Volume", "@volume"),
            ]
            hover.formatters = {
                "@datetime": "datetime",
                "@open": "numeral",
                "@high": "numeral",
                "@low": "numeral",
                "@close": "numeral",
            }
            hover.point_policy = "snap_to_data"
            hover.line_policy = "nearest"
            hover.mode = "vline"

            # --- preparing body of candles:
            chart.segment(
                x0="datetime", y0="high", x1="datetime", y1="low",
                color="#20ff00", line_alpha=1, name="candle", source=hoverData,
            )
            chart.vbar(
                x=self.prices.datetime[inc], width=candleWidth, bottom=self.prices.open[inc], top=self.prices.close[inc],
                fill_color="black", line_color="#20ff00", line_width=1, fill_alpha=1, line_alpha=1,
            )
            chart.vbar(
                x=self.prices.datetime[dec], width=candleWidth, bottom=self.prices.open[dec], top=self.prices.close[dec],
                fill_color="white", line_color="#20ff00", line_width=1, fill_alpha=1, line_alpha=1,
            )

            # preparing candle's average points:
            disabledObjects.append(chart.circle(
                self.prices.datetime, self.prices.avg,
                size=3, color="red", alpha=1, legend_label=legendNameAvg,
            ))
            disabledObjects.append(chart.line(
                self.prices.datetime, self.prices.avg,
                line_width=1, line_color="red", line_alpha=1, legend_label=legendNameAvg,
            ))

            # preparing for highest close line:
            highestClose = round(max(self.prices.close.values), self._precision)
            chart.line(
                self.prices.datetime, highestClose,
                line_width=2, line_color="yellow", line_alpha=1, legend_label=legendNameMain,
            )
            chart.text(
                self.prices.datetime.values[-1], highestClose + 1 / self._deg10prec,
                text=[str(highestClose)], angle=0, text_color="yellow", text_font_size="8pt", legend_label=legendNameMain,
            )

            # preparing for lowest close line:
            lowestClose = round(min(self.prices.close.values), self._precision)
            chart.line(
                self.prices.datetime, lowestClose,
                line_width=2, line_color="yellow", line_alpha=1, legend_label=legendNameMain,
            )
            chart.text(
                self.prices.datetime.values[-1], lowestClose - 2 / self._deg10prec,
                text=[str(lowestClose)], angle=0, text_color="yellow", text_font_size="8pt", legend_label=legendNameMain,
            )

            # preparing lines for all trends:
            if self.trendSplit is not None and self.trendSplit and self.splitCount is not None and self.splitCount:
                left = 0
                for trendNum in range(len(self.splitCount)):
                    right = left + self.splitCount[trendNum] - 1
                    chart.line(
                        [self.prices.datetime.values[left], self.prices.datetime.values[right]],
                        [self.prices.close.values[left], self.prices.close.values[right]],
                        line_width=1, line_color="white", line_alpha=0.9, line_dash=[3, 3], legend_label=legendNameMain,
                    )
                    left += self.splitCount[trendNum]

            # preparing for main direction line:
            chart.line(
                [self.prices.datetime.values[0], self.prices.datetime.values[-1]],
                [self.prices.close.values[0], self.prices.close.values[-1]],
                line_width=1, line_color="white", line_alpha=1, line_dash=[6, 6], legend_label=legendNameMain,
            )

            # --- Preparing a lot of TA lines:

            # Simple Moving Averages (SMA) 5, 20
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["sma5"],
                line_width=2, line_color="yellow", line_alpha=1, legend_label=legendNameSMA,
            ))
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["sma20"],
                line_width=3, line_color="red", line_alpha=1, legend_label=legendNameSMA,
            ))

            # Long Simple Moving Averages (SMA) 50, 200
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["sma50"],
                line_width=2, line_color="#ffbf00", line_alpha=1, legend_label=legendNameSMAlong,
            ))
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["sma200"],
                line_width=3, line_color="#ff0040", line_alpha=1, legend_label=legendNameSMAlong,
            ))

            # Hull Moving Averages (HMA) 5, 20
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["hma5"],
                line_width=2, line_color="#00ffff", line_alpha=1, legend_label=legendNameHMA,
            ))
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["hma20"],
                line_width=3, line_color="#ff00ff", line_alpha=1, legend_label=legendNameHMA,
            ))

            # Volume Weighted Moving Averages (VWMA) 5, 20
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["vwma5"],
                line_width=2, line_color="blue", line_alpha=1, legend_label=legendNameVWMA,
            ))
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["vwma20"],
                line_width=3, line_color="#ff8000", line_alpha=1, legend_label=legendNameVWMA,
            ))

            # Bollinger Bands (BBands)
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["bbands"]["lower"],
                line_width=1, line_color="#66ffff", line_alpha=1, legend_label=legendNameBBANDS,
            ))
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["bbands"]["mid"],
                line_width=1, line_color="#66ffff", line_alpha=1, legend_label=legendNameBBANDS,
            ))
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["bbands"]["upper"],
                line_width=1, line_color="#66ffff", line_alpha=1, legend_label=legendNameBBANDS,
            ))

            # Parabolic Stop and Reverse (psar)
            disabledObjects.append(chart.circle(
                self.prices.datetime, self.stat["psar"]["long"],
                size=3, line_color="#00ffff", line_alpha=1, legend_label=legendNamePsar,
            ))
            disabledObjects.append(chart.circle(
                self.prices.datetime, self.stat["psar"]["short"],
                size=3, line_color="#ff00ff", line_alpha=1, legend_label=legendNamePsar,
            ))

            # Hull Moving Averages (HMA) 13, 8, 5 for the Alligator indicator (Jaw, Teeth, and Lips)
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["hma13"],
                line_width=2, line_color="#1a1aff", line_alpha=1, legend_label=legendNameAlligator,
            ))
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["hma8"],
                line_width=2, line_color="#ff1a1a", line_alpha=1, legend_label=legendNameAlligator,
            ))
            disabledObjects.append(chart.line(
                self.prices.datetime, self.stat["hma5"],
                line_width=2, line_color="#40ff00", line_alpha=1, legend_label=legendNameAlligator,
            ))

            # Zig-Zag indicator with self.zigZagDeviation of difference parameter
            disabledObjects.append(chart.line(
                self.stat["zigzag3"]["datetimes"], self.stat["zigzag3"]["filtered"],
                line_width=3, line_color="cyan", line_alpha=1, legend_label=legendNameZigZag,
            ))

            for item in disabledObjects:
                item.visible = False

            # --- Volume chart options:
            volumeChart = figure(
                x_axis_type="datetime",
                y_axis_label="Volume",
                outline_line_width=0,
                outline_line_color="white",
                plot_width=1200,
                plot_height=90,
                sizing_mode="scale_width",
                background_fill_color="black",
                tools=["pan", "wheel_zoom", "hover"],
                toolbar_location=None,
                active_scroll="wheel_zoom",
                min_border_left=0,
                min_border_right=0,
                min_border_top=0,
                min_border_bottom=0,
                x_range=chart.x_range,
                y_range=Range1d(0, max(self.prices.volume), bounds=(0, max(self.prices.volume))),
            )
            volumeChart.toolbar.logo = None  # remove bokeh logo and link to https://bokeh.org/
            volumeChart.xaxis.major_label_orientation = pi / 6
            volumeChart.xaxis.visible = False
            volumeChart.yaxis.formatter = NumeralTickFormatter(format="0a")
            volumeChart.grid.grid_line_dash = [6, 4]
            volumeChart.grid.grid_line_alpha = 0.5
            volumeChart.grid.minor_grid_line_dash = [6, 4]
            volumeChart.grid.minor_grid_line_alpha = 0.5
            volumeChart.xgrid.minor_grid_line_dash = [6, 4]
            volumeChart.xgrid.minor_grid_line_alpha = 0.3
            volumeChart.xgrid.minor_grid_line_color = "white"

            # preparing data for hover tooltips:
            volSource = {
                "candle": [x + 1 for x in range(-len(self.prices.close), 0, 1)],
                "datetime": self.prices.datetime,
                "volume": self.prices.volume,
                "zero": [0] * len(self.prices.volume),
            }
            volHoverData = ColumnDataSource(data=volSource)
            volHover = volumeChart.select(dict(type=HoverTool))
            volHover.names = ["volumes"]
            volHover.tooltips = [
                ("Candle", "@candle"),
                ("Date", "@datetime{%Y-%m-%d}"),
                ("Time", "@datetime{%H:%M:%S}"),
                ("Volume", "@volume"),
            ]
            volHover.formatters = {
                "@datetime": "datetime",
            }
            volHover.point_policy = "snap_to_data"
            volHover.line_policy = "nearest"
            volHover.mode = "vline"

            # preparing volume chart:
            volumeChart.segment(
                x0="datetime", y0="volume", x1="datetime", y1="zero",
                color="black", line_alpha=0, name="volumes", source=volHoverData,
            )
            volumeChart.vbar(
                x=self.prices.datetime[inc], width=candleWidth, bottom=0, top=self.prices.volume[inc],
                fill_color="black", line_color="#20ff00", line_width=1, fill_alpha=1, line_alpha=1,
            )
            volumeChart.vbar(
                x=self.prices.datetime[dec], width=candleWidth, bottom=0, top=self.prices.volume[dec],
                fill_color="white", line_color="#20ff00", line_width=1, fill_alpha=1, line_alpha=1,
            )

            # preparing html-file with forecast chart and statistics in markdown:
            output_file(fileName, title=self._chartTitle, mode="cdn")
            save(gridplot(
                    children=[[chart], [volumeChart]],
                    sizing_mode="stretch_both",
                    merge_tools=False,
            ))
            with open("{}.md".format(fileName), "w", encoding="UTF-8") as fH:
                fH.write("\n".join(infoBlock))

            if viewInBrowser:
                os.system(os.path.abspath(fileName))  # view forecast chart in default browser immediately

            uLogger.info("Pandas dataframe rendered as html-file [{}]".format(os.path.abspath(fileName)))

        else:
            raise Exception("Empty price data! Generate or load prices before show as Bokeh chart!")

    def RenderGoogle(self, fileName="index.html", viewInBrowser=False):
        """
        Rendering prices from pandas dataframe to not interactive Google Candlestick chart and save to html-file.
        See: https://developers.google.com/chart/interactive/docs/gallery/candlestickchart
        :param fileName: html-file path to save Google Candlestick chart.
        :param viewInBrowser: If True, then immediately opens html in browser after rendering.
        """
        if self.prices is not None and not self.prices.empty:
            uLogger.info("Rendering pandas dataframe as Google Candlestick chart...")

            self.DetectTimeframe()  # auto-detect time delta between last two neighbour candles
            infoBlock = self.GetStatistics()  # calculating some indicators

            if self.j2model is None or not self.j2model:
                uLogger.debug("Preparing Google Candlestick chart configuration...")
                self.j2model = {"info": infoBlock, "title": self._chartTitle}
                googleDates = [pd.to_datetime(date).strftime("%Y-%m-%d %H:%M:%S") for date in self.prices.datetime.values]
                data = zip(googleDates, self.prices.low, self.prices.open, self.prices.close, self.prices.high)
                self.j2model["candlesData"] = [list(x) for x in data]

            else:
                uLogger.debug("Using custom chart model")

            # --- Rendering and saving chart as html-file and markdown-file with statistics:
            if os.path.exists(self.j2template):
                renderedTemplate = jinja2.Template(open(self.j2template, "r", encoding="UTF-8").read())

            else:
                renderedTemplate = jinja2.Template(self.j2template)

            htmlMain = renderedTemplate.render(self.j2model)

            with open(fileName, "w", encoding="UTF-8") as fH:
                fH.write(htmlMain)
            with open("{}.md".format(fileName), "w", encoding="UTF-8") as fH:
                fH.write("\n".join(infoBlock))

            if viewInBrowser:
                os.system(os.path.abspath(fileName))  # view forecast chart in default browser immediately

            uLogger.info("Pandas dataframe rendered as html-file [{}]".format(os.path.abspath(fileName)))

        else:
            raise Exception("Empty price data! Generate or load prices before show as Google Candlestick chart!")


def ParseArgs():
    """
    Function get and parse command line keys.
    """
    parser = ArgumentParser()  # command-line string parser

    parser.description = "Forex and stocks price generator. Generates chain of candlesticks with predefined statistical parameters, return pandas dataframe or saving as .csv-file with OHLCV-candlestick in every strings. See examples: https://tim55667757.github.io/PriceGenerator"
    parser.usage = "python PriceGenerator.py [some options] [one or more commands]"

    # options:
    parser.add_argument("--ticker", type=str, default="TEST", help="Option: some fake ticker name, 'TEST' by default.")
    parser.add_argument("--precision", type=int, default=2, help="Option: precision is count of digits after comma, 2 by default.")
    parser.add_argument("--timeframe", type=int, default=60, help="Option: time delta between two neighbour candles in minutes, 60 (1 hour) by default.")
    parser.add_argument("--start", type=str, help="Option: start time of 1st candle as string with format 'year-month-day hour:min', e.g. '2021-01-02 12:00'.")
    parser.add_argument("--horizon", type=int, help="Option: candlesticks count.")
    parser.add_argument("--split-trend", type=str, default="", help=r"Option: set difference periods, e.g. --split-trend=/\- means that generated candles has up trend at first part, next down trend and then no trend. Used with --split-count key.")
    parser.add_argument("--split-count", type=int, nargs="+", help="Option: set count of candles of difference periods, e.g. --split-count 5 10 15 means that generated candles has 3 trends with 5, 10 and 15 candles in chain, with sum equal to --horizon. Used with --split-count and --horizon keys.")
    parser.add_argument("--max-close", type=float, help="Option: maximum of all close prices.")
    parser.add_argument("--min-close", type=float, help="Option: minimum of all close prices.")
    parser.add_argument("--init-close", type=float, help="Option: generator started 1st open price of chain from this 'last' close price.")
    parser.add_argument("--max-outlier", type=float, help="Option: maximum of outlier size of candle tails, by default used (max-close - min-close) / 10.")
    parser.add_argument("--max-body", type=float, help="Option: maximum of candle body sizes: abs(open - close), by default used max-outlier * 0.9.")
    parser.add_argument("--max-volume", type=int, help="Option: maximum of trade volumes.")
    parser.add_argument("--up-candles-prob", type=float, default=0.5, help="Option: float number in [0; 1] is a probability that next candle is up, 0.5 by default.")
    parser.add_argument("--outliers-prob", type=float, default=0.03, help="Option: float number in [0; 1] is a statistical outliers probability (price 'tails'), 0.03 by default.")
    parser.add_argument("--trend-deviation", type=float, default=0.005, help="Option: relative deviation for trend detection, 0.005 mean ±0.005 by default. 'NO trend' if (1st_close - last_close) / 1st_close <= trend-deviation.")
    parser.add_argument("--zigzag", type=float, default=0.03, help="Option: relative deviation to detection points of ZigZag indicator, 0.03 by default.")
    parser.add_argument("--sep", type=str, default=None, help="Option: separator in csv-file, if None then auto-detecting enable.")
    parser.add_argument("--debug-level", type=int, default=20, help="Option: showing STDOUT messages of minimal debug level, e.g., 10 = DEBUG, 20 = INFO, 30 = WARNING, 40 = ERROR, 50 = CRITICAL.")

    # commands:
    parser.add_argument("--load-from", type=str, help="Command: Load .cvs-file to Pandas dataframe. You can draw chart in additional with --render-bokeh key.")
    parser.add_argument("--generate", action="store_true", help="Command: Generates chain of candlesticks with predefined statistical parameters and save stock history as pandas dataframe or .csv-file if --save-to key is defined. You can draw chart in additional with --render-bokeh key.")
    parser.add_argument("--save-to", type=str, help="Command: Save generated or loaded dataframe to .csv-file. You can draw chart in additional with --render-bokeh key.")
    parser.add_argument("--render-bokeh", type=str, help="Command: Show chain of candlesticks as interactive Bokeh chart. See: https://docs.bokeh.org/en/latest/docs/gallery/candlestick.html. Before using this key you must define --load-from or --generate keys.")
    parser.add_argument("--render-google", type=str, help="Command: Show chain of candlesticks as not interactive Google Candlestick chart. See: https://developers.google.com/chart/interactive/docs/gallery/candlestickchart. Before using this key you must define --load-from or --generate keys.")

    cmdArgs = parser.parse_args()
    return cmdArgs


def Main():
    """
    Main function to work from CLI, generate pandas dataframe, show charts and save to file.
    """
    args = ParseArgs()  # get and parse command-line parameters
    exitCode = 0

    if args.debug_level:
        uLogger.level = 10  # always debug level by default
        uLogger.handlers[0].level = args.debug_level  # level for STDOUT
        # uLogger.handlers[1].level = 10  # always debug level for log.txt

    start = datetime.now(tzlocal())
    uLogger.debug(uLog.sepLine)
    uLogger.debug("PriceGenerator started: {}".format(start.strftime("%Y-%m-%d %H:%M:%S")))

    priceModel = PriceGenerator()

    try:
        # --- set options:

        if args.sep:
            priceModel.sep = args.sep  # separator in .csv-file

        if args.ticker:
            priceModel.ticker = args.ticker  # some fake ticker name, "TEST" by default

        if int(args.precision) >= 0:
            priceModel.precision = args.precision  # precision is count of digits after comma, 2 by default

        if args.timeframe:
            priceModel.timeframe = timedelta(minutes=args.timeframe)  # time delta between two neighbour candles in minutes, 60 (1 hour) by default

        if args.start:
            priceModel.timeStart = pd.to_datetime(args.start, format="%Y-%m-%d %H:%M")

        if args.horizon:
            priceModel.horizon = args.horizon  # generating candlesticks count

        if args.split_trend:
            priceModel.trendSplit = args.split_trend  # difference periods

        if args.split_count:
            priceModel.splitCount = args.split_count  # candles in every periods

        if args.min_close:
            priceModel.minClose = args.min_close  # minimum of all close prices

        if args.init_close:
            priceModel.initClose = args.init_close  # generator started 1st open price of chain from this "last" close price

        if args.max_outlier:
            priceModel.maxOutlier = args.max_outlier  # maximum of outlier size of candle tails, by default used (max-close - min-close) / 10

        if args.max_body:
            priceModel.maxCandleBody = args.max_body  # maximum of candle body sizes: abs(open - close), by default used max-outlier * 90%

        if args.max_volume:
            priceModel.maxVolume = args.max_volume  # maximum of trade volumes

        if args.up_candles_prob:
            priceModel.upCandlesProb = args.up_candles_prob  # float number in [0; 1] is a probability that next candle is up, 0.5 = 50% by default

        if args.outliers_prob:
            priceModel.outliersProb = args.outliers_prob  # float number in [0; 1] is a statistical outliers probability (price "tails"), 0.03 = 3% by default

        if args.trend_deviation:
            priceModel.trendDeviation = args.trend_deviation  # relative deviation for trend detection, 0.005 mean ±0.5% by default. "NO trend" if (1st_close - last_close) / 1st_close <= trend-deviation

        if args.zigzag:
            priceModel.zigZagDeviation = args.zigzag  # relative deviation to detection points of ZigZag indicator, 0.03 by default

        # --- do one or more commands:

        if not args.load_from and not args.generate and not args.save_to and not args.render_bokeh:
            raise Exception("At least one command must be selected! See: python PriceGenerator.py --help")

        if args.load_from:
            priceModel.LoadFromFile(fileName=args.load_from)

        if args.generate:
            priceModel.Generate()

        if args.save_to:
            priceModel.SaveToFile(fileName=args.save_to)

        if args.render_bokeh:
            priceModel.RenderBokeh(fileName=args.render_bokeh, viewInBrowser=True)

        if args.render_google:
            priceModel.RenderGoogle(fileName=args.render_google, viewInBrowser=True)

    except Exception as e:
        uLogger.error(e)
        exc = tb.format_exc().split("\n")
        for line in exc:
            if line:
                uLogger.debug(line)
        exitCode = 255

    finally:
        finish = datetime.now(tzlocal())

        if exitCode == 0:
            uLogger.debug("All PriceGenerator operations are finished success (summary code is 0).")

        else:
            uLogger.error("An errors occurred during the work! See full debug log with --debug-level 10. Summary code: {}".format(exitCode))

        uLogger.debug("PriceGenerator work duration: {}".format(finish - start))
        uLogger.debug("PriceGenerator work finished: {}".format(finish.strftime("%Y-%m-%d %H:%M:%S")))

        sys.exit(exitCode)


if __name__ == "__main__":
    Main()
