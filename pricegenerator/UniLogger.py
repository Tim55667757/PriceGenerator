# -*- coding: utf-8 -*-
#
# Author: Timur Gilmullin

# This module initialize standard python logging system.


import sys
import logging.handlers


# initialize Main Parent Logger:
UniLogger = logging.getLogger("UniLogger")
formatString = "%(filename)-20sL:%(lineno)-5d%(levelname)-8s[%(asctime)s] %(message)s"
formatter = logging.Formatter(formatString)
sys.stderr = sys.stdout


def SetLevel(vLevel='ERROR'):
    """
    This procedure setting up UniLogger verbosity level.
    """
    UniLogger.level = logging.NOTSET

    if isinstance(vLevel, str):
        if vLevel == '5' or vLevel.upper() == 'CRITICAL':
            UniLogger.level = logging.CRITICAL

        elif vLevel == '4' or vLevel.upper() == 'ERROR':
            UniLogger.level = logging.ERROR

        elif vLevel == '3' or vLevel.upper() == 'WARNING':
            UniLogger.level = logging.WARNING

        elif vLevel == '2' or vLevel.upper() == 'INFO':
            UniLogger.level = logging.INFO

        elif vLevel == '1' or vLevel.upper() == 'DEBUG':
            UniLogger.level = logging.DEBUG


class LevelFilter(logging.Filter):
    """
    Class using to set up log level filtering.
    """

    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        return record.levelno >= self.level


def EnableLogger(logFile, parentHandler=UniLogger, useFormat=formatter):
    """
    Adding new file logger with rotation.
    """
    # logHandler = logging.FileHandler(logFile)
    maxSizeBytes = 50 * 1024 * 1024  # 5Mb log rotate by default
    logHandler = logging.handlers.RotatingFileHandler(logFile, encoding="UTF-8", maxBytes=maxSizeBytes, backupCount=4)
    logHandler.level = logging.DEBUG  # set up DEBUG verbosity level by default for file logging
    logHandler.addFilter(LevelFilter(logging.DEBUG))

    if useFormat:
        logHandler.setFormatter(useFormat)

    else:
        logHandler.setFormatter(formatter)

    parentHandler.addHandler(logHandler)

    return logHandler


def DisableLogger(handler, parentHandler=UniLogger):
    """
    Disable given file logger.
    """
    if handler:
        handler.flush()
        handler.close()

    if handler in parentHandler.handlers:
        parentHandler.removeHandler(handler)


# --- Main init:

SetLevel('DEBUG')  # set up DEBUG verbosity level by default for UniLogger

streamHandler = logging.StreamHandler()  # initialize STDOUT UniLogger
streamHandler.setFormatter(formatter)  # set formatter for STDOUT UniLogger
streamHandler.level = logging.INFO  # set up INFO verbosity level by default for STDOUT UniLogger
UniLogger.addHandler(streamHandler)  # adding STDOUT UniLogger handler to Parent UniLogger

# fileLogHandler = EnableLogger(logFile='log.txt', parentHandler=UniLogger, useFormat=formatter)  # add logging to file

sepWide = '-' * 120  # long-long log separator
sepLong = '-' * 80  # long log separator
sepShort = '-' * 40  # short log separator
sepLine = '=--=' * 20  # log part separator