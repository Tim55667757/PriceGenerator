# -*- coding: utf-8 -*-
# Author: Timur Gilmullin


# Module: forex and stocks price generator.
# Generates chain of candlesticks with predefined statistical parameters, return pandas dataframe or saving as .csv-file with OHLCV-candlestick in every strings.


import os
import sys
from datetime import datetime
import pandas as pd
from argparse import ArgumentParser

import pricegenerator.UniLogger as uLog
import traceback as tb


# --- Common technical parameters:

uLogger = uLog.UniLogger
uLogger.level = 10  # debug level by default
uLogger.handlers[0].level = 20  # info level by default for STDOUT
uLogger.handlers[1].level = 10  # debug level by default for log.txt


class PriceGenerator:
    """
    This class implements methods to generation of prices statistically similar to real ones.
    """

    def __init__(self):
        self.prices = None  # copy of generated or loaded prices will be put into this Pandas variable

        self.inputHeaders = ["date", "time", "open", "high", "low", "close", "volume"]  # headers if .csv-file used
        self.dfHeaders = ["datetime", "open", "high", "low", "close", "volume"]  # dataframe headers
        self.sep = None  # Separator in csv-file, if None then auto-detecting enable

        self.horizon = 1000  # Generating candlesticks count, must be >= 1
        self.showCandlesCount = 124  # How many candlestick are shown on forecast chart window, 124 for the best view.

    @staticmethod
    def FormattedDelta(tDelta, fmt):
        """
        Return timedelta formatted as string, e.g. FormattedDelta(delta_obj, "{days} days {hours}:{minutes}:{seconds}")
        """
        d = {"days": tDelta.days}
        d["hours"], rem = divmod(tDelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)

        return fmt.format(**d)

    def LoadFromFile(self, fileName):
        """
        Load Pandas OHLCV model from csv-file.
        :param fileName: path to csv-file with OHLCV columns.
        :return: Pandas dataframe.
        """
        uLogger.debug("Loading, parse and preparing input data from [{}]...".format(os.path.abspath(fileName)))
        self.prices = pd.read_csv(fileName, names=self.inputHeaders, engine="python", sep=self.sep, parse_dates={"datetime": ["date", "time"]})

        uLogger.debug("It was read {} rows".format(len(self.prices)))
        uLogger.debug("Showing last 5 rows as pandas dataframe:")
        for line in pd.DataFrame.to_string(self.prices[self.dfHeaders][-5:], max_cols=20).split("\n"):
            uLogger.debug(line)

        return self.prices


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
    parser.add_argument("--load-from", type=str, help="Command: Load .cvs-file to Pandas dataframe. You can draw chart in additional with --show key.")
    parser.add_argument("--generate", action="store_true", help="Command: Generates chain of candlesticks with predefined statistical parameters and save stock history as pandas dataframe or .csv-file if --output key is defined.")
    parser.add_argument("--show", action="store_true", help="Command: Show chain of candlesticks as interactive Bokeh chart.")
    parser.add_argument("--save-to", type=str, help="Command: Save generated dataframe to .csv-file. In additional you can use --show key.")

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
        uLogger.handlers[1].level = 10  # always debug level for log.txt

    start = datetime.now()
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
            priceModel.LoadFromFile(args.load_from)

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
