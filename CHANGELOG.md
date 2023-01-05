# PriceGenerator — Release notes

[![gift](https://badgen.net/badge/gift/donate/green)](https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=Donat%20(gift)%20for%20the%20authors%20of%20the%20PriceGenerator%20project&default-sum=999&button-text=13&payment-type-choice=on&successURL=https%3A%2F%2Ftim55667757.github.io%2FPriceGenerator%2F&quickpay=shop&account=410015019068268)

* 🇷🇺 [Релиз-ноты на русском (see release notes in russian here)](https://github.com/Tim55667757/PriceGenerator/blob/develop/CHANGELOG_RU.md)
* 📚 [Documentation for the PriceGenerator module and examples of working with CLI](https://tim55667757.github.io/PriceGenerator)
* 🎁 Support the project with a donation to our yoomoney-wallet: [410015019068268](https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=Donat%20(gift)%20for%20the%20authors%20of%20the%20PriceGenerator%20project&default-sum=999&button-text=13&payment-type-choice=on&successURL=https%3A%2F%2Ftim55667757.github.io%2FPriceGenerator%2F&quickpay=shop&account=410015019068268)


### [1.3.81 (2023-01-05)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.3.81) — released

##### New features

* Python version support was changed to 3.9.
* [#17](https://github.com/Tim55667757/PriceGenerator/issues/17) Into the `RenderBokeh()` method was added `layouts` parameter. You can add new Bokeh Chart-objects on the Main Chart with that parameter. Also, `darkTheme` parameter was added. If it `True`, then will be used dark theme, `False` (by default) mean light theme. Also, you can manipulate with chart and adding lines or markers to the main chart. Use `markers` and `lines` parameters for it. `markers` is a Pandas Dataframe with custom series, where additional markers will place on main series. `None` by default. One marker is a custom symbol, e.g. ×, ↓ or ↑ or anyone else. Marker data must contain at least two columns. There are `datetime` with date and time and some markers columns (`markersUpper`, `markersCenter` or `markersLower`). Length of marker dataframes must be equal to the length of main candle series. `lines` is a list with custom series, where additional chart-lines will place on main series. `None` by default. Line data must contain at least two columns. There are `datetime` with date and time and `custom_line_name` with y-coordinates. Length of the chart-line dataframes must be equal to the length of main candle series.
* [#10](https://github.com/Tim55667757/PriceGenerator/issues/10) Ability to specify directions with words or chars was added. Words may be next: `up`, `down`, `no` or chars: `u`, `d`, `n` for the `--split-trend` key, in addition to the existing ability to set up of the trend with symbols `/\-`. To separate words or chars use the hyphen symbol, e.g. `--split-trend=up-down-no-up`, `--split-trend=u-d-n-u` etc.
* [#13](https://github.com/Tim55667757/PriceGenerator/issues/13) [API-doc](https://tim55667757.github.io/PriceGenerator/docs/pricegenerator/PriceGenerator.html) on module `PriceGenerator` was added.

##### Improvements

* [#15](https://github.com/Tim55667757/PriceGenerator/issues/15) Statistic block view was improvement.
* [#16](https://github.com/Tim55667757/PriceGenerator/issues/16) Examples were added: [how to generate prices chain without candles](https://github.com/Tim55667757/PriceGenerator/issues/16#issuecomment-1287875048).

##### Bug fixes

* [#19](https://github.com/Tim55667757/PriceGenerator/issues/19) Bug fix with incorrect high and low values when trend is set.
* [#18](https://github.com/Tim55667757/PriceGenerator/issues/18) Bug fix with incorrect multiple tips on chart and incorrect width of visible area.
* [#11](https://github.com/Tim55667757/PriceGenerator/issues/11) Incorrect warnings were disabled.


### [1.2.58 (2021-12-09)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.2.58) — released

##### New features

* License changed from MIT to [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).
* [#8](https://github.com/Tim55667757/PriceGenerator/issues/8) Added ability to separate candlesticks by some trends. It was implemented two additional keys: `--split-trend` and `--split-count`. These keys affect the appearance of the trend and the number of candles in each trend.
  * The `--split-trend` key shows trends movements, e.g. `--split-trend=/\-` means that generated candles has uptrend at first part, next downtrend and then no trend.
  * The `--split-count` key set count of candles of difference periods, e.g. `--split-count 5 10 15` means that generated candles has 3 trends with 5, 10 and 15 candles in chain.


### [1.2.46 (2021-02-28)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.2.46) — released

##### New features

* Some moving averages were added to Bokeh chart with [`pandas_ta`](https://github.com/Tim55667757/pandas-ta) library:
  * Simple Moving Averages (5, 20, 50, 200),
  * Hull Moving Averages (5, 20),
  * Volume Weighted Moving Averages (5, 20),
  * Also, only "Max_close / Min_close / Trend line" is showing by default.
* Volatility indicators were implements:
  * Bollinger Bands,
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

* Not-detected timeframe when rendering from Pandas DataFrame without loading from file was fixed.


### [1.1.30 (2021-02-20)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.1.30) — released

##### New features

* A lot of keys were added for CLI: `--ticker`, `--timeframe`, `--start`, `--horizon`, `--max-close`, `--min-close`, `--init-close`, `--max-outlier`, `--max-body`, `--max-volume`, `--up-candles-prob`, `--outliers-prob`, `--trend-deviation`. That keys are overriding default parameters.
* Implements new method `RenderGoogle()` and a `--render-google` key that can draw not interactive [Google Candlestick Chart](https://developers.google.com/chart/interactive/docs/gallery/candlestickchart).

##### Improvements

* Extended examples were added. See examples in [`README.md`](https://github.com/Tim55667757/PriceGenerator/blob/master/README.md) (english) and [`README_RU.md`](https://github.com/Tim55667757/PriceGenerator/blob/master/README_RU.md) (russian).


### [1.0.19 (2021-02-05)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.0.19) — released

##### Retrospective

The first version of PriceGenerator library allows you to:
* save generated prices in csv-format (example: `./media/test.csv`);
* save the generated prices to a Pandas DataFrame variable for further use in automation scripts;
* automatically calculate some statistical and probabilistic characteristics of the generated prices and save them in Markdown format (example: `./media/index.html.md`);
* load the prices of real instruments according to the OHLCV-candlesticks model from the csv-file and carry out their statistical analysis;
  * draw a chart of generated or loaded real prices and save it in html-format (example: `./media/index.html`);
  * generate prices, a chart and some data on price behavior can be saved as a regular png-image (example: `./media/index.html.png`).

[![gift](https://badgen.net/badge/gift/donate/green)](https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=Donat%20(gift)%20for%20the%20authors%20of%20the%20PriceGenerator%20project&default-sum=999&button-text=13&payment-type-choice=on&successURL=https%3A%2F%2Ftim55667757.github.io%2FPriceGenerator%2F&quickpay=shop&account=410015019068268)
