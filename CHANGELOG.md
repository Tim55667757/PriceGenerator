# PriceGenerator — Release notes

[![gift](https://badgen.net/badge/gift/donate/green)](https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=Donat%20(gift)%20for%20the%20authors%20of%20the%20PriceGenerator%20project&default-sum=999&button-text=13&payment-type-choice=on&successURL=https%3A%2F%2Ftim55667757.github.io%2FPriceGenerator%2F&quickpay=shop&account=410015019068268)

* 🇷🇺 [Релиз-ноты на русском (see release notes in russian here)](https://github.com/Tim55667757/PriceGenerator/blob/master/CHANGELOG_RU.md)
* 📚 [Documentation for the PriceGenerator module and examples of working with CLI](https://tim55667757.github.io/PriceGenerator)
* 🎁 Support the project with a donation to our yoomoney-wallet: [410015019068268](https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=Donat%20(gift)%20for%20the%20authors%20of%20the%20PriceGenerator%20project&default-sum=999&button-text=13&payment-type-choice=on&successURL=https%3A%2F%2Ftim55667757.github.io%2FPriceGenerator%2F&quickpay=shop&account=410015019068268)


### [1.2.58 (2021-12-09)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.2.58) — stable release

##### New features

* [#8](https://github.com/Tim55667757/PriceGenerator/issues/8) Added ability to separate candlesticks by some trends. It was implemented two additional keys: `--split-trend` and `--split-count`. These keys affect the appearance of the trend and the number of candles in each trend.
  * The `--split-trend` key shows trends movements, e.g. `--split-trend=/\-` means that generated candles has up trend at first part, next down trend and then no trend.
  * The `--split-count` key set count of candles of difference periods, e.g. `--split-count 5 10 15` means that generated candles has 3 trends with 5, 10 and 15 candles in chain.


### [1.2.46 (2021-02-28)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.2.46)

##### New features

* Some moving averages were added to Bokeh chart with [`pandas_ta`](https://github.com/Tim55667757/pandas-ta) library:
  * Simple Moving Averages (5, 20, 50, 200),
  * Hull Moving Averages (5, 20),
  * Volume Weighted Moving Averages (5, 20),
  * Also, only "Max_close / Min_close / Trend line" is showing by default.
* Volatility indicators were implements:
  * Bollinger Bands.
  * Parabolic Stop and Reverse,
  * Alligator (based on HMAs 13, 8, 5),
  * ZigZag with 3% deviation by default.
* Volume chart was added.
* Candle's tooltips were added on main and volume charts.

##### Improvements

* More tests and examples were added. Also, little refactor. All used libraries were updated.
* The key `--horizon` when loading from a file is used to specify loading of the last N = horizon candles.
* The `--precision` key is used to specify the signs after comma.

##### Bug fixes

* Bug fix with not detected timeframe when rendering from pandas dataframe without loading from file.


### [1.1.30 (2021-02-20)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.1.30)

##### New features

* A lot of keys were added for CLI: `--ticker`, `--timeframe`, `--start`, `--horizon`, `--max-close`, `--min-close`, `--init-close`, `--max-outlier`, `--max-body`, `--max-volume`, `--up-candles-prob`, `--outliers-prob`, `--trend-deviation`. That keys are overriding default parameters.
* Implements new method `RenderGoogle()` and a `--render-google` key that can be draw not interactive Google Candlestick chart.

##### Improvements

* Extended examples were added. See examples in `README.md` (english) and `README_RU.md` (russian).


### [1.0.19 (2021-02-05)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.0.19)

##### Retrospective

The first version of PriceGenerator library allows you to:
* save generated prices in csv-format (example: `./media/test.csv`);
* save the generated prices to a Pandas DataFrame variable for further use in automation scripts;
* automatically calculate some statistical and probabilistic characteristics of the generated prices and save them in markdown format (example: `./media/index.html.md`);
* load the prices of real instruments according to the OHLCV-candlesticks model from the csv-file and carry out their statistical analysis;
  * draw a chart of generated or loaded real prices and save it in html-format (example: `./media/index.html`);
  * generated prices, a chart and some data on price behavior can be saved as a regular png-image (example: `./media/index.html.png`).

[![gift](https://badgen.net/badge/gift/donate/green)](https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=Donat%20(gift)%20for%20the%20authors%20of%20the%20PriceGenerator%20project&default-sum=999&button-text=13&payment-type-choice=on&successURL=https%3A%2F%2Ftim55667757.github.io%2FPriceGenerator%2F&quickpay=shop&account=410015019068268)
