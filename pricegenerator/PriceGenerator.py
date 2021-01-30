# -*- coding: utf-8 -*-
# Author: Timur Gilmullin


# Module: forex and stocks price generator.
# Generates chain of candlesticks with predefined statistical parameters, return pandas dataframe or saving as .csv-file with OHLCV-candlestick in every strings.
# In additional you can view some statistical parameters of generated or loaded prices.


import os
import sys
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from argparse import ArgumentParser

from math import pi
from statistics import mode, pstdev, StatisticsError
from itertools import groupby
import pandas as pd
import random
from bokeh.plotting import figure, show, save, output_file
from bokeh.models import Legend

import pricegenerator.UniLogger as uLog
import traceback as tb


# --- Common technical parameters:

uLogger = uLog.UniLogger
uLogger.level = 10  # debug level by default
uLogger.handlers[0].level = 20  # info level by default for STDOUT
# uLogger.handlers[1].level = 10  # debug level by default for log.txt


class PriceGenerator:
    """
    This class implements methods to generation of prices statistically similar to real ones.
    """

    def __init__(self):
        self.prices = None  # copy of generated or loaded prices will be put into this Pandas variable

        self.inputHeaders = ["date", "time", "open", "high", "low", "close", "volume"]  # headers if .csv-file used
        self.dfHeaders = ["datetime", "open", "high", "low", "close", "volume"]  # dataframe headers
        self.sep = ","  # Separator in csv-file

        self._precision = 2  # signs after comma
        self._deg10prec = 10 ** 2  # 10^precision is used for some formulas
        self.showCandlesCount = 124  # How many candlestick are shown on forecast chart window, 124 for the best view.

        self.ticker = "TEST"  # some fake ticker name
        self.timeframe = timedelta(hours=1)  # time delta between two neighbour candles, 1 hour by default
        self.timeStart = datetime.now(tzlocal()).replace(microsecond=0, second=0, minute=0)
        self.horizon = 100  # Generating candlesticks count, must be >= 5
        self.maxClose = random.uniform(70, 90)  # maximum of close prices must be >= self.minClose
        self.minClose = random.uniform(60, 70)  # minimum of close prices must be <= self.maxClose
        self.initClose = None  # if not None generator started 1st open price of chain from this price
        self.maxCandleBody = None  # maximum of candle body sizes: abs(open - close), if None then used maxOutlier * 90%
        self.maxOutlier = None  # maximum of outlier size of candle tails, if None then used (maxClose - minClose) / 10
        self.maxVolume = random.randint(0, 100000)  # maximum of trade volumes
        self.upCandlesProb = 0.5  # probability that next candle is up, 50% by default
        self.outliersProb = 0.03  # statistical outliers probability (price "tails"), 3% by default
        self.trendDeviation = 0.005  # relative deviation for trend detection, 0.005 mean ±0.5% by default. "NO trend" if (1st_close - last_close) / 1st_close <= self.trendDeviation

        self._chartTitle = ""  # chart title, auto-generated when loading or creating chain of candlesticks

        # some statistics for calculation:
        self._stat = {
            "candles": 0,  # generated candlesticks count
            "precision": self.precision,  # generated candlesticks count
            "closeFirst": 0.,  # first close price
            "closeLast": 0.,  # last close price
            "closeMax": 0.,  # max close price
            "closeMix": 0.,  # min close price
            "diapason": 0.,  # diapason = closeMax - closeMin
            "trend": "NO trend",  # "UP trend" or "DOWN trend" with uses ±self.trendDeviation
            "trendDev": self.trendDeviation,
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
    def stat(self):
        return self._stat

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, value):
        if value >= 0:
            self._precision = value
            self._deg10prec = 10 ** value  # 10^precision

        else:
            self._precision = -1  # auto-detect precision next when data-file load
            self._deg10prec = 1

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
            self.precision = mode(list(map(lambda x: len(str(x).split('.')[-1]) if len(str(x).split('.')) > 1 else 0, examples)))

        except StatisticsError as e:
            uLogger.warning("Unable to unambiguously determine Mode() of the value of precision! Precision is set to 2 (default). StatisticsError: '{}'".format(e))
            self.precision = 2

        finally:
            uLogger.debug("Auto-detected precision: {}".format(self._precision))

    def LoadFromFile(self, fileName):
        """
        Load Pandas OHLCV model from csv-file.
        :param fileName: path to csv-file with OHLCV columns.
        :return: Pandas dataframe.
        """
        uLogger.info("Loading, parse and preparing input data from [{}]...".format(os.path.abspath(fileName)))
        self.prices = pd.read_csv(fileName, names=self.inputHeaders, engine="python", sep=self.sep, parse_dates={"datetime": ["date", "time"]})

        self.horizon = len(self.prices)
        self.ticker = os.path.basename(fileName)

        # auto-detect time delta between last two neighbour candles:
        self.timeframe = min(
            self.prices.iloc[-1].datetime - self.prices.iloc[-2].datetime,
            self.prices.iloc[-2].datetime - self.prices.iloc[-3].datetime
        )
        uLogger.debug("Detected time delta: {}".format(self.timeframe))

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
            uLogger.info("Saving [{}] rows of pandas dataframe without headers...".format(len(self.prices)))
            self.prices.to_csv(fileName, sep=self.sep, index=False, header=False)
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
        self._stat["upCountChainMax"] = max(upChainsLengths)
        self._stat["downCountChainMax"] = max(downChainsLengths)
        self._stat["deltas"]["max"] = pd.DataFrame.max(self.prices.delta)
        self._stat["deltas"]["min"] = pd.DataFrame.min(self.prices.delta)
        self._stat["deltas"]["stDev"] = round(pstdev(self.prices.delta), self._precision)
        self._stat["deltas"]["q99"] = round(max(pd.DataFrame(self.prices.delta).quantile(q=0.99, interpolation='linear')), self._precision)
        self._stat["deltas"]["q95"] = round(max(pd.DataFrame(self.prices.delta).quantile(q=0.95, interpolation='linear')), self._precision)
        self._stat["deltas"]["q80"] = round(max(pd.DataFrame(self.prices.delta).quantile(q=0.80, interpolation='linear')), self._precision)
        self._stat["deltas"]["q50"] = round(max(pd.DataFrame(self.prices.delta).quantile(q=0.50, interpolation='linear')), self._precision)
        self._stat["cumSumVolumes"] = self.prices.volume.sum()

        uLogger.debug("self._stat = {}".format(self._stat))

        summary = [
            "## Summary",
            "",
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
            "| - Trend deviation parameter:                 | ±{}%".format(self.stat["trendDev"] * 100),
            "",
            "## Some statistics",
            "",
            "| Statistic                                    | Value",
            "|----------------------------------------------|---------------",
            "| Up candles count:                            | {} ({}%)".format(self.stat["upCount"], round(100 * self.stat["upCount"] / self.stat["candles"], self.precision)),
            "| Down candles count:                          | {} ({}%)".format(self.stat["downCount"], round(100 * self.stat["downCount"] / self.stat["candles"], self.precision)),
            "| Max of up candles chain:                     | {}".format(self.stat["upCountChainMax"]),
            "| Max of down candles chain:                   | {}".format(self.stat["downCountChainMax"]),
            "| Max delta (between High and Low prices):     | {}".format(round(self.stat["deltas"]["max"], self.precision)),
            "| Min delta (between High and Low prices):     | {}".format(round(self.stat["deltas"]["min"], self.precision)),
            "| Delta's std. dev.:                           | {}".format(round(self.stat["deltas"]["stDev"], self.precision)),
            "| - 99 percentile:                             | ≤ {}".format(round(self.stat["deltas"]["q99"], self.precision)),
            "| - 95 percentile:                             | ≤ {}".format(round(self.stat["deltas"]["q95"], self.precision)),
            "| - 80 percentile:                             | ≤ {}".format(round(self.stat["deltas"]["q80"], self.precision)),
            "| - 50 percentile:                             | ≤ {}".format(round(self.stat["deltas"]["q50"], self.precision)),
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
        uLogger.debug("- Interval or timeframe (time delta between two neighbour candles): {}".format(self.timeframe))
        uLogger.debug("- Horizon length (candlesticks count): {}".format(self.horizon))
        uLogger.debug("- Start time: {}".format(self.timeStart.strftime("%Y-%m-%d--%H-%M-%S")))
        uLogger.debug("  |-> end time: {}".format((self.timeStart + self.horizon * self.timeframe).strftime("%Y-%m-%d--%H-%M-%S")))
        uLogger.debug("- Maximum of close prices: {}".format(round(self.maxClose, self.precision)))
        uLogger.debug("- Minimum of close prices: {}".format(round(self.minClose, self.precision)))
        uLogger.debug("- Maximum of candle body sizes: {}".format(round(self.maxCandleBody, self.precision)))
        uLogger.debug("- Maximum of candle tails outlier sizes: {}".format(round(self.maxOutlier, self.precision)))
        uLogger.debug("- Init close (1st open price in chain): {}".format(round(self.initClose, self.precision)))
        uLogger.debug("- Maximum of volume of one candle: {}".format(self.maxVolume))
        uLogger.debug("- Probability that next candle is up: {}%".format(self.upCandlesProb * 100))
        uLogger.debug("- Statistical outliers probability: {}%".format(self.outliersProb * 100))

        # prepare candles chain:
        candles = [self._GenNextCandle(round(self.initClose, self.precision))]
        for i in range(1, self.horizon):
            candles.append(self._GenNextCandle(candles[i - 1]["close"]))

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
        :param fileName: html-file path to save Bokeh chart.
        :param viewInBrowser: If True, then opens html in browser after rendering.
        """
        if self.prices is not None and not self.prices.empty:
            uLogger.info("Rendering pandas dataframe as Bokeh chart...")

            infoBlock = self.GetStatistics()

            uLogger.debug("Preparing Bokeh chart configuration...")
            uLogger.debug("Title: {}".format(self._chartTitle))

            # chart options:
            chart = figure(
                x_axis_type="datetime",
                x_axis_label="Date and time",
                y_axis_label="Price",
                outline_line_width=3,
                outline_line_color="white",
                tools=["pan", "wheel_zoom", "box_zoom", "reset", "save"],
                plot_width=1200,
                plot_height=600,
                sizing_mode="scale_width",
                background_fill_color="black",
                title=self._chartTitle,
                toolbar_location="above",
                min_border_left=0,
                min_border_right=0,
                min_border_top=0,
                min_border_bottom=0,
            )
            chart.toolbar.logo = None  # remove bokeh logo and link to https://bokeh.org/

            # Summary section and controls:
            legendNameMain = "Max_close / Min_close / Trend line / Averages points"
            summaryInfo = Legend(
                click_policy="hide",
                items=[(info, []) for info in infoBlock] + [("", []), ("", []), (uLog.sepShort, []), ("Show/hide on chart:", [])],
                location="top_right",
                label_text_font_size="8pt",
                margin=0,
                padding=0,
                spacing=0,
                label_text_font="Lucida Console",
            )
            chart.add_layout(summaryInfo, 'right')

            # preparing grid:
            chart.xaxis.major_label_orientation = pi / 4
            minY = pd.DataFrame.min(self.prices.low)
            maxY = pd.DataFrame.max(self.prices.high)
            chart.yaxis.bounds = (minY - (maxY - minY) / 2, maxY + (maxY - minY) / 2)
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

            # preparing data for candles:
            inc = self.prices.open <= self.prices.close
            dec = self.prices.open > self.prices.close
            width = 108000  # as for 5 minutes by default

            if self.timeframe <= timedelta(days=31):
                width = 864000000  # 12 * 60 * 60 * 25 * 800  # for 43200 minutes

            if self.timeframe <= timedelta(days=7):
                width = 216000000  # 12 * 60 * 60 * 25 * 200  # for 10080 minutes

            if self.timeframe <= timedelta(days=1):
                width = 32400000  # 12 * 60 * 60 * 25 * 30  # for 1440 minutes

            if self.timeframe <= timedelta(hours=4):
                width = 6480000  # 12 * 60 * 60 * 25 * 6  # for 240 minutes

            if self.timeframe <= timedelta(hours=1):
                width = 1620000  # 12 * 60 * 60 * 25 * 1.5  # for 60 minutes

            if self.timeframe <= timedelta(minutes=30):
                width = 648000  # 12 * 60 * 60 * 15  # for 30 minutes

            if self.timeframe <= timedelta(minutes=15):
                width = 345600  # 12 * 60 * 60 * 8  # for 15 minutes

            if self.timeframe <= timedelta(minutes=5):
                width = 108000  # 12 * 60 * 60 * 2.5  # for 5 minutes

            if self.timeframe <= timedelta(minutes=1):
                width = 21600  # 12 * 60 * 30   # for 1 minute

            # --- preparing body of candles:
            candlesData = self.prices
            chart.segment(
                candlesData.datetime, candlesData.high, candlesData.datetime, candlesData.low,
                color="#20ff00", line_alpha=1,
            )
            chart.vbar(
                candlesData.datetime[inc], width, candlesData.open[inc], candlesData.close[inc],
                fill_color="black", line_color="#20ff00", line_width=1, fill_alpha=1, line_alpha=1,
            )
            chart.vbar(
                candlesData.datetime[dec], width, candlesData.open[dec], candlesData.close[dec],
                fill_color="white", line_color="#20ff00", line_width=1, fill_alpha=1, line_alpha=1,
            )

            # preparing candle's average points:
            chart.circle(
                self.prices.tail(self.horizon).datetime, self.prices.tail(self.horizon).avg,
                size=3, color="red", alpha=1, legend_label=legendNameMain,
            )
            chart.line(
                self.prices.tail(self.horizon).datetime, self.prices.tail(self.horizon).avg,
                line_width=1, line_color="red", line_alpha=1, legend_label=legendNameMain,
            )

            # preparing for highest close line:
            highestClose = round(max(self.prices.close.values), self._precision)
            chart.line(
                self.prices.tail(self.horizon + 1).datetime, highestClose,
                line_width=2, line_color="yellow", line_alpha=1, legend_label=legendNameMain,
            )
            chart.text(
                self.prices.datetime.values[-1], highestClose + 1 / self._deg10prec,
                text=[str(highestClose)], angle=0, text_color="yellow", text_font_size="8pt", legend_label=legendNameMain,
            )

            # preparing for lowest close line:
            lowestClose = round(min(self.prices.close.values), self._precision)
            chart.line(
                self.prices.tail(self.horizon + 1).datetime, lowestClose,
                line_width=2, line_color="yellow", line_alpha=1, legend_label=legendNameMain,
            )
            chart.text(
                self.prices.datetime.values[-1], lowestClose - 2 / self._deg10prec,
                text=[str(lowestClose)], angle=0, text_color="yellow", text_font_size="8pt", legend_label=legendNameMain,
            )

            # preparing for direction line:
            chart.line(
                [self.prices.datetime.values[0], self.prices.datetime.values[-1]],
                [self.prices.close.values[0], self.prices.close.values[-1]],
                line_width=1, line_color="white", line_alpha=1, line_dash=[6, 6], legend_label=legendNameMain,
            )

            # preparing html-file with forecast chart:
            output_file(fileName, title=self._chartTitle, mode="cdn")
            save(chart)
            with open("{}.md".format(fileName), "w", encoding="UTF-8") as fH:
                fH.write("\n".join(infoBlock))

            if viewInBrowser:
                show(chart)  # view forecast chart in browser immediately

            uLogger.info("Pandas dataframe rendered as html-file [{}]".format(os.path.abspath(fileName)))

        else:
            raise Exception("Empty price data! Generate or load prices before show as Bokeh chart!")


def ParseArgs():
    """
    Function get and parse command line keys.
    """
    parser = ArgumentParser()  # command-line string parser

    parser.description = "Forex and stocks price generator. Generates chain of candlesticks with predefined statistical parameters, return pandas dataframe or saving as .csv-file with OHLCV-candlestick in every strings. See examples: https://tim55667757.github.io/PriceGenerator"
    parser.usage = "python PriceGenerator.py [some options] [one or more commands]"

    # options:
    parser.add_argument("--sep", type=str, default=None, help="Option: separator in csv-file, if None then auto-detecting enable.")
    parser.add_argument("--debug-level", type=int, default=20, help="Option: showing STDOUT messages of minimal debug level, e.g., 10 = DEBUG, 20 = INFO, 30 = WARNING, 40 = ERROR, 50 = CRITICAL.")

    # commands:
    parser.add_argument("--load-from", type=str, help="Command: Load .cvs-file to Pandas dataframe. You can draw chart in additional with --show-to key.")
    parser.add_argument("--generate", action="store_true", help="Command: Generates chain of candlesticks with predefined statistical parameters and save stock history as pandas dataframe or .csv-file if --save-to key is defined. You can draw chart in additional with --show-to key.")
    parser.add_argument("--save-to", type=str, help="Command: Save generated or loaded dataframe to .csv-file. You can draw chart in additional with --show-to key.")
    parser.add_argument("--render-bokeh", type=str, help="Command: Show chain of candlesticks as interactive Bokeh chart. Before using this key you must define --load-from or --generate keys.")

    cmdArgs = parser.parse_args()
    return cmdArgs


def Main():
    """
    Main function to work from CLI, generate pandas dataframe, show charts and save to file|.
    """
    args = ParseArgs()  # get and parse command-line parameters
    exitCode = 0

    if args.debug_level:
        uLogger.level = 10  # always debug level by default
        uLogger.handlers[0].level = args.debug_level  # level for STDOUT
        # uLogger.handlers[1].level = 10  # always debug level for log.txt

    start = datetime.now()
    uLogger.debug(uLog.sepLine)
    uLogger.debug("PriceGenerator started: {}".format(start.strftime("%Y-%m-%d %H:%M:%S")))

    priceModel = PriceGenerator()

    try:
        # --- set options:

        if args.sep:
            priceModel.sep = args.sep  # separator in .csv-file

        # --- do one or more commands:

        if not args.load_from and not args.generate and not args.show and not args.save_to:
            raise Exception("At least one command must be selected! See: python PriceGenerator.py --help")

        if args.load_from:
            priceModel.LoadFromFile(fileName=args.load_from)

        if args.generate:
            priceModel.Generate()

        if args.save_to:
            priceModel.SaveToFile(fileName=args.save_to)

        if args.render_bokeh:
            priceModel.RenderBokeh(fileName=args.render_bokeh, viewInBrowser=True)

    except Exception as e:
        uLogger.error(e)
        exc = tb.format_exc().split("\n")
        for line in exc:
            if line:
                uLogger.debug(line)
        exitCode = 255

    finally:
        finish = datetime.now()

        if exitCode == 0:
            uLogger.debug("All PriceGenerator operations are finished success (summary code is 0).")

        else:
            uLogger.error("An errors occurred during the work! See full debug log with --debug-level 10. Summary code: {}".format(exitCode))

        uLogger.debug("PriceGenerator work duration: {}".format(finish - start))
        uLogger.debug("PriceGenerator work finished: {}".format(finish.strftime("%Y-%m-%d %H:%M:%S")))

        sys.exit(exitCode)


if __name__ == "__main__":
    Main()
