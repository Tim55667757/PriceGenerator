# PriceGenerator — список релизных изменений

[![gift](https://badgen.net/badge/gift/donate/green)](https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=%D0%94%D0%BE%D0%BD%D0%B0%D1%82%20(%D0%BF%D0%BE%D0%B4%D0%B0%D1%80%D0%BE%D0%BA)%20%D0%B4%D0%BB%D1%8F%20%D0%B0%D0%B2%D1%82%D0%BE%D1%80%D0%BE%D0%B2%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0%20PriceGenerator&default-sum=999&button-text=13&payment-type-choice=on&successURL=https%3A%2F%2Ftim55667757.github.io%2FPriceGenerator%2F&quickpay=shop&account=410015019068268)

* 🇺🇸 [See release notes in english here (актуальные релиз-ноты на английском)](https://github.com/Tim55667757/TKSBrokerAPI/blob/develop/CHANGELOG.md)
* 📚 [Документация на модуль PriceGenerator и примеры работы в консоли](https://github.com/Tim55667757/TKSBrokerAPI/blob/master/README_RU.md)
* 🎁 Поддержать проект донатом на ЮМани-кошелёк: [410015019068268](https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=%D0%94%D0%BE%D0%BD%D0%B0%D1%82%20(%D0%BF%D0%BE%D0%B4%D0%B0%D1%80%D0%BE%D0%BA)%20%D0%B4%D0%BB%D1%8F%20%D0%B0%D0%B2%D1%82%D0%BE%D1%80%D0%BE%D0%B2%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0%20PriceGenerator&default-sum=999&button-text=13&payment-type-choice=on&successURL=https%3A%2F%2Ftim55667757.github.io%2FPriceGenerator%2F&quickpay=shop&account=410015019068268)


### [1.3.81 (2023-01-05)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.3.81) — опубликована

##### Новая функциональность

* Поддерживаемая версия Python изменена на 3.9.
* [#17](https://github.com/Tim55667757/PriceGenerator/issues/17) В метод `RenderBokeh()` добавлен параметр `layouts`, с помощью которого можно добавлять новые Chart-объекты Bokeh на основной график. Также добавлен параметр `darkTheme`, который регулирует выбор темы: если он равен `True`, то будет использоваться тёмная тема, если `False` (по умолчанию), то будет использоваться светлая тема. Также вы можете манипулировать графиком и добавлять новые линии или маркеры на основной график. Используйте для этого параметры `markers` и `lines`. Pandas DataFrame `markers` содержит ряды, которые показывают, какой маркер нанести для той или иной свечи. `None` по умолчанию. Маркер представляет собой некоторый символ, например, ×, ↓ или ↑ или какой-либо другой. Датафрейм с маркерами должен содержать, как минимум, два столбца. Это столбец `datetime`, с датой и временем, и один из столбцов или все сразу: `markersUpper`, `markersCenter` или `markersLower`, с маркерами, которые нужно поставить сверху, по центру или снизу свечи соответственно. Длины рядов с маркерами должны быть равны длине основного ряда со свечами. Лист `lines` содержит ряды с данными о точках новых линий, которые нужно разместить на основном свечном графике. `None` по умолчанию. Датафрейм с линиями должен содержать, как минимум, два столбца. Это `datetime`, с датой и временем, и произвольно названный столбец `custom_line_name`, с y-координатами точек линии. Длины рядов с точками линий должны быть равны длине основного ряда со свечами.
 [#10](https://github.com/Tim55667757/PriceGenerator/issues/10) Добавлена возможность указания направлений генерируемых трендов с помощью слов или букв. Слова могут быть следующими: `up`, `down` или `no`, а буквы могут быть такими: `u`, `d` или `n`. Эти слова и знаки могут использоваться вместе с ключом `--split-trend`, в дополнение к уже имеющейся возможности указывать тренд символами `/\-`. Для разделения слов и букв используется символ дефиса, например, `--split-trend=up-down-no-up` или `--split-trend=u-d-n-u`.
* [#13](https://github.com/Tim55667757/PriceGenerator/issues/13) Была разработана [API-документация](https://tim55667757.github.io/PriceGenerator/docs/pricegenerator/PriceGenerator.html) на модуль `PriceGenerator`.

##### Улучшения

* [#15](https://github.com/Tim55667757/PriceGenerator/issues/15) Отображение блока статистики было улучшено.
* [#16](https://github.com/Tim55667757/PriceGenerator/issues/16) Добавлены примеры: [как сгенерировать цепочку случайных цен без свечей](https://github.com/Tim55667757/PriceGenerator/issues/16#issuecomment-1287875048).

##### Баг-фиксы

* [#19](https://github.com/Tim55667757/PriceGenerator/issues/19) Исправлена ошибка с генерацией некорректных значений high и low свечей, в случае, если задан тренд.
* [#18](https://github.com/Tim55667757/PriceGenerator/issues/18) Исправлена ошибка с отображением многочисленных всплывающих подсказок на графике, а также ошибка с неверным определением ширины области графика.
* [#11](https://github.com/Tim55667757/PriceGenerator/issues/11) Некорректные предупреждения в логах отключены.


### [1.2.58 (2021-12-09)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.2.58) — опубликована

##### Новая функциональность

* Лицензия изменена с MIT на [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).
* [#8](https://github.com/Tim55667757/PriceGenerator/issues/8) Добавлена возможность разделять наборы свечей по трендам. Для этого добавлены два дополнительных ключа: `--split-trend` и `--split-count`. Эти ключи влияют на внешний вид тренда и количество свечей в каждом тренде.
   * Ключ `--split-trend` устанавливает направления в трендах, например, `--split-trend=/\-` означает, что сгенерированные свечи имеют восходящий тренд в первой части, затем нисходящий тренд, а затем тренд отсутствует.
   * Ключ --split-count устанавливает количество свечей разных периодов, например `--split-count 5 10 15` означает, что сгенерированные свечи имеют 3 тренда с 5, 10 и 15 свечами в цепочке.


### [1.2.46 (2021-02-28)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.2.46) — опубликована

##### Новая функциональность

* Были добавлены некоторые скользящие средние на график Bokeh с библиотекой [`pandas_ta`](https://github.com/Tim55667757/pandas-ta):
  * простые скользящие средние (5, 20, 50, 200),
  * скользящие средние корпуса (5, 20),
  * скользящие средние, взвешенные по объему (5, 20),
  * кроме того, по умолчанию на графике отображается только линии «Max_close / Min_close / Trend line».
* Были реализованы индикаторы волатильности:
  * Полосы Боллинджера.
  * Параболический стоп и реверс,
  * Аллигатор (на базе HMA 13, 8, 5),
  * ZigZag с отклонением 3% по умолчанию.
* Добавлен график объемов.
* Добавлены всплывающие подсказки к свечам на основных и объемных графиках.

##### Улучшения

* Добавлено больше тестов и примеров. Проведён небольшой рефакторинг. У используемых библиотек продвинуты версии.
* Ключ `--horizon` при загрузке из файла используется для указания количества свечей, загружаемых с конца (N = horizon).
* Ключ `--precision` используется для указания количества знаков после запятой.

##### Баг-фиксы

* Исправлена ошибка с не обновляемым значением таймфрейма, при рендеринге из Pandas DataFrame (без загрузки из файла происходило падение).


### [1.1.30 (2021-02-20)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.1.30) — опубликована

##### Новая функциональность

* Добавлено множество ключей для CLI: `--ticker`, `--timeframe`, `--start`, `--horizon`, `--max-close`, `--min-close`, `--init-close`, `--max-outlier`, `--max-body`, `--max-volume`, `--up-candles-prob`, `--outliers-prob`, `--тренд-отклонение`. Эти ключи переопределяют параметры по умолчанию.
* Реализован новый метод `RenderGoogle()` и ключ `--render-google`, которые позволяют создать статический график [Google Candlestick Chart](https://developers.google.com/chart/interactive/docs/gallery/candlestickchart).

##### Улучшения

* Добавлены новые примеры, ищите их в [`README.md`](https://github.com/Tim55667757/PriceGenerator/blob/master/README.md) (на английском) и [`README_RU.md`](https://github.com/Tim55667757/PriceGenerator/blob/master/README_RU.md) (на русском).


### [1.0.19 (2021-02-05)](https://github.com/Tim55667757/PriceGenerator/releases/tag/1.0.19) — опубликована

##### Ретроспектива

Первая версия библиотеки PriceGenerator позволяла:
* сохранять сгенерированные цены в формате csv (пример: `./media/test.csv`);
* сохранять сгенерированные цены в переменную Pandas DataFrame для дальнейшего использования в сценариях автоматизации;
* автоматически рассчитывать некоторые статистические и вероятностные характеристики сгенерированных цен и сохранять их в формате Markdown (пример: `./media/index.html.md`);
* загрузить цены реальных инструментов по модели OHLCV-свечей из csv-файла и провести их статистический анализ;
  * нарисовать график сгенерированных или загруженных реальных цен и сохранить его в формате html (пример: `./media/index.html`);
  * сгенерировать цены, построить график и сохранить его в виде обычного png-изображения (пример: `./media/index.html.png`).

[![gift](https://badgen.net/badge/gift/donate/green)](https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=%D0%94%D0%BE%D0%BD%D0%B0%D1%82%20(%D0%BF%D0%BE%D0%B4%D0%B0%D1%80%D0%BE%D0%BA)%20%D0%B4%D0%BB%D1%8F%20%D0%B0%D0%B2%D1%82%D0%BE%D1%80%D0%BE%D0%B2%20%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0%20PriceGenerator&default-sum=999&button-text=13&payment-type-choice=on&successURL=https%3A%2F%2Ftim55667757.github.io%2FPriceGenerator%2F&quickpay=shop&account=410015019068268)
