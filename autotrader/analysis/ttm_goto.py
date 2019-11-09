import pandas as pd
import jpholiday
import datetime as dt
from bokeh.models import ColumnDataSource, CrosshairTool, HoverTool
from bokeh.models import Panel, Tabs
from bokeh.models.widgets import Button, TextInput
from bokeh.models.widgets import TableColumn, DataTable
from bokeh.models.widgets import DateFormatter
from bokeh.layouts import layout, widgetbox, row
from oandapyV20.exceptions import V20Error
import autotrader.analyzer as ana
import autotrader.utils as utl
import autotrader.analysis.candlestick as cs
from autotrader.utils import DateTimeManager
from autotrader.oanda_common import OandaGrn, OandaIns
from autotrader.analysis.candlestick import CandleStickChartBase
from autotrader.analysis.candlestick import CandleStickData
from autotrader.analysis.candlestick import CandleGlyph
from autotrader.analysis.graph import VerLine
from autotrader.technical import SimpleMovingAverage


class CandleStickChartAbs(CandleStickChartBase):
    """ CandleStickChart
            - ローソク足チャート定義クラス[Candle stick chart definition class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        # Hbar Label
        self.__Y = "y"
        self.__X = "x"
        self.__CLOSE_COLOR = "#FFEE55"
        self.__OPEN_COLOR = "#54FFEE"

        super().__init__()

        # プロット設定
        self._fig.toolbar_location = "right"
        self._fig.add_tools(CrosshairTool(line_color="pink",
                                          line_alpha=0.5))

        hover = HoverTool()
        hover.formatters = {CandleGlyph.XDT: "datetime"}
        hover.tooltips = [(cs.LBL_TIME, "@" + CandleGlyph.XDT + "{%F %R}"),
                          (cs.LBL_HIGH, "@" + CandleGlyph.YHI),
                          (cs.LBL_OPEN, "@" + CandleGlyph.YOP),
                          (cs.LBL_CLOSE, "@" + CandleGlyph.YCL),
                          (cs.LBL_LOW, "@" + CandleGlyph.YLO)]
        hover.renderers = [self._glyinc.render,
                           self._glydec.render,
                           self._glyequ.render]
        self._fig.add_tools(hover)

    def set_dataframe(self, csd):
        super().set_dataframe(csd)


class CandleStickChart5M(CandleStickChartAbs):
    """ CandleStickChart
            - ローソク足チャート定義クラス[Candle stick chart definition class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        self.__TM0954 = dt.time(9, 54)
        self.__TM1030 = dt.time(10, 30)

        super().__init__()
        self._fig.title.text = "TTM Candlestick Chart ( 5 minutes )"

        self.__vl1 = VerLine(self._fig, "pink", line_width=2)
        self.__vl2 = VerLine(self._fig, "yellow", line_width=2)

        self.__sma = SimpleMovingAverage(self._fig)

    def set_dataframe(self, date_, csd):
        super().set_dataframe(csd)

        dat_ = dt.date(date_.year, date_.month, date_.day)
        y_pri = self._fig.y_range
        x_dttm = dt.datetime.combine(dat_, self.__TM0954)
        self.__vl1.update(x_dttm, y_pri.start, y_pri.end)
        x_dttm = dt.datetime.combine(dat_, self.__TM1030)
        self.__vl2.update(x_dttm, y_pri.start, y_pri.end)

        self.__sma.update_shr(csd.df, 5)
        self.__sma.update_mdl(csd.df, 20)
        self.__sma.update_lng(csd.df, 75)


class CandleStickChart1H(CandleStickChartAbs):
    """ CandleStickChart
            - ローソク足チャート定義クラス[Candle stick chart definition class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        self.__TM0954 = dt.time(9, 54)

        super().__init__()
        self._fig.title.text = "TTM Candlestick Chart ( 1 hour )"

        self.__vl1 = VerLine(self._fig, "pink", line_width=2)

    def set_dataframe(self, date_, csd):
        super().set_dataframe(csd)

        dat_ = dt.date(date_.year, date_.month, date_.day)
        y_pri = self._fig.y_range
        x_dttm = dt.datetime.combine(dat_, self.__TM0954)
        self.__vl1.update(x_dttm, y_pri.start, y_pri.end)


class TTMGoto(object):
    """ TTMGoto
            - 仲根(TTM)とゴトー日クラス[TTM and Goto day class]
    """

    LBL_WEEK = "week"
    LBL_GOTO = "goto-day"
    LBL_DIFL = "diff-low-price"
    LBL_DIFH = "diff-high-price"

    _WEEK_DICT = {0: "月", 1: "火", 2: "水", 3: "木",
                  4: "金", 5: "土", 6: "日"}
    _MLT_FIVE_LIST = [5, 10, 15, 20, 25, 30]

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        # Widget Button:解析実行[Run analysis]
        self.__btn_run = Button(label="解析実行",
                                button_type="success",
                                sizing_mode="fixed",
                                default_size=200)
        self.__btn_run.on_click(self.__cb_btn_run)

        cols = [TTMGoto.LBL_WEEK,
                TTMGoto.LBL_GOTO,
                TTMGoto.LBL_DIFL,
                TTMGoto.LBL_DIFH]
        self.__dfsmm = pd.DataFrame(columns=cols)

        # Widget DataTable:
        self.TBLLBL_DATE = "date"
        self.TBLLBL_WEEK = "week"
        self.TBLLBL_GOTO = "goto-day"
        self.TBLLBL_DIFL = "diff-low-price"
        self.TBLLBL_DIFH = "diff-high-price"

        # データテーブル初期化
        self.__src = ColumnDataSource({self.TBLLBL_DATE: [],
                                       self.TBLLBL_WEEK: [],
                                       self.TBLLBL_GOTO: [],
                                       self.TBLLBL_DIFL: [],
                                       self.TBLLBL_DIFH: [],
                                       })

        cols = [
            TableColumn(field=self.TBLLBL_DATE, title="Date",
                        formatter=DateFormatter()),
            TableColumn(field=self.TBLLBL_WEEK, title="Week"),
            TableColumn(field=self.TBLLBL_GOTO, title="Goto Day"),
            TableColumn(field=self.TBLLBL_DIFL, title="Diff Low Price"),
            TableColumn(field=self.TBLLBL_DIFH, title="Diff High Price"),
        ]

        self.__tbl = DataTable(source=self.__src,
                               columns=cols,
                               fit_columns=True,
                               height=200)
        self.__src.selected.on_change("indices", self.__cb_dttbl)

        # ローソク足チャート初期化
        self.__csc1 = CandleStickChart5M()
        self.__csdlist_5m = []

        self.__csc2 = CandleStickChart1H()
        self.__csdlist_1h = []

    def get_layout(self):
        """レイアウトを取得する[get layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        btnrun = self.__btn_run
        tbl = self.__tbl
        cscfig1 = self.__csc1.fig
        cscfig2 = self.__csc2.fig

        cscfigs = row(children=[cscfig1, cscfig2], sizing_mode="stretch_width")

        tblfig = widgetbox(children=[tbl, cscfigs],
                           sizing_mode="stretch_width")

        tabs = self.__create_result_tabs()

        layout_ = layout(children=[[btnrun], [tblfig], [tabs]],
                         sizing_mode="stretch_width")
        return(layout_)

    def __create_result_tabs(self):

        # Tab1の設定
        txtin = TextInput(value="",
                          title="Sample",
                          width=200)

        tab1 = Panel(child=txtin, title="Summary")

        # タブ生成
        tabs = Tabs(tabs=[tab1])

        return tabs

    def __cb_btn_run(self):
        """Widget Button(実行)コールバックメソッド
           [Callback method of Widget Button(Execute)]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        print("Called cb_btn_run")
        LBL_DIF_HI = "diff-high"
        LBL_DIF_LO = "diff-low"
        LBL_DIF_CL = "diff-close"

        dfsmm = self.__dfsmm
        dfsmm.drop(index=dfsmm.index, inplace=True)

        cols = [TTMGoto.LBL_WEEK,
                TTMGoto.LBL_GOTO]
        dfgoto = pd.DataFrame(columns=cols)

        self.__csdlist_5m = []
        self.__csdlist_1h = []

        yesterday = dt.date.today() - dt.timedelta(days=1)
        str_ = ana.get_date_str()
        str_ = utl.limit_upper(str_, yesterday)
        end_ = ana.get_date_end()
        end_ = utl.limit_upper(end_, yesterday)

        print("Start:{}" .format(str_))
        print("End:  {}" .format(end_))

        nextdate = end_ + dt.timedelta(days=1)
        nextmonth = nextdate.month

        lastday_flg = False
        gotoday_flg = False

        for n in range((end_ - str_ + dt.timedelta(days=1)).days):
            date_ = end_ - dt.timedelta(n)
            weekdayno = date_.weekday()

            # 月末判定
            if not date_.month == nextmonth:
                lastday_flg = True

            # ゴトー日判定
            if date_.day in self._MLT_FIVE_LIST:
                gotoday_flg = True

            # 平日判定
            if (weekdayno < 5) and not jpholiday.is_holiday(date_):

                if lastday_flg or gotoday_flg:
                    target = "○"
                    lastday_flg = False
                    gotoday_flg = False
                else:
                    target = "×"

                # 出力
                record = pd.Series([self._WEEK_DICT[weekdayno],
                                    target],
                                   index=dfgoto.columns,
                                   name=date_)
                dfgoto = dfgoto.append(record)

            nextmonth = date_.month

        dfgoto.sort_index(inplace=True)

        if dfgoto.empty:
            print("リストは空です")
        else:

            inst_id = ana.get_instrument_id()
            inst = OandaIns.list[inst_id].oanda_name
            dfhi = pd.DataFrame()
            dflo = pd.DataFrame()
            dfcl = pd.DataFrame()

            for date_, row_ in dfgoto.iterrows():
                # チャート1
                str_ = dt.datetime.combine(date_, dt.time(0, 0))
                end_ = dt.datetime.combine(date_, dt.time(12, 0))
                dtmstr = DateTimeManager(str_)
                dtmend = DateTimeManager(end_)
                gran = OandaGrn.M5

                try:
                    csd5m = CandleStickData(gran, inst, dtmstr, dtmend)
                except V20Error as v20err:
                    print("-----V20Error: {}".format(v20err))
                    continue
                except ConnectionError as cerr:
                    print("----- ConnectionError: {}".format(cerr))
                    continue
                except Exception as excp:
                    print("----- Exception: {}".format(excp))
                    continue

                # 始値 - 最安値
                strtm = dt.time(hour=9, minute=55)
                strdttm = str(dt.datetime.combine(date_, strtm))
                endtm = dt.time(hour=10, minute=25)
                enddttm = str(dt.datetime.combine(date_, endtm))

                try:
                    # 始値
                    openpri = csd5m.df.loc[strdttm, cs.LBL_OPEN]
                    df5m = csd5m.df[strdttm:enddttm].copy()
                except KeyError:
                    print("-----[Caution] Invalid Date found:[{}]"
                          .format(str(date_)))
                    continue

                minidx = df5m[cs.LBL_LOW].idxmin()
                minpri = df5m[cs.LBL_LOW].min()
                maxpri = df5m[:minidx][cs.LBL_HIGH].max()

                print("Open Price: {} " .format(openpri))
                print("Low Price: {} " .format(minpri))
                print("High Price: {} " .format(maxpri))

                # 最高値 - 始値
                idxnew = [s.time() for s in df5m.index]
                idxdict = dict(zip(df5m.index, idxnew))
                df5m.rename(index=idxdict, inplace=True)

                tmp = df5m[cs.LBL_HIGH] - df5m[cs.LBL_OPEN]
                srhi = pd.Series(tmp, name=date_)
                tmp = df5m[cs.LBL_LOW] - df5m[cs.LBL_OPEN]
                srlo = pd.Series(tmp, name=date_)
                tmp = df5m[cs.LBL_CLOSE] - df5m[cs.LBL_OPEN]
                srcl = pd.Series(tmp, name=date_)

                dfhi = dfhi.append(srhi)
                dflo = dflo.append(srlo)
                dfcl = dfcl.append(srcl)

                # チャート2
                str_ = dt.datetime.combine(
                    date_, dt.time(0, 0)) - dt.timedelta(days=5)
                end_ = dt.datetime.combine(date_, dt.time(15, 0))
                dtmstr = DateTimeManager(str_)
                dtmend = DateTimeManager(end_)
                gran = OandaGrn.H1

                try:
                    csd1h = CandleStickData(gran, inst, dtmstr, dtmend)
                except V20Error as v20err:
                    print("-----V20Error: {}".format(v20err))
                    continue
                except ConnectionError as cerr:
                    print("----- ConnectionError: {}".format(cerr))
                    continue
                except Exception as excp:
                    print("----- Exception: {}".format(excp))
                    continue

                self.__csdlist_5m.append(csd5m)
                self.__csdlist_1h.append(csd1h)

                # 出力
                inst_id = ana.get_instrument_id()
                unit = OandaIns.list[inst_id].min_unit

                record = pd.Series([row_[TTMGoto.LBL_WEEK],
                                    row_[TTMGoto.LBL_GOTO],
                                    round(openpri - minpri, unit),
                                    round(maxpri - openpri, unit)],
                                   index=dfsmm.columns,
                                   name=date_)
                dfsmm = dfsmm.append(record)

            print("------ dfhi ------")
            dftmp = dfhi.T.sort_index()
            print(dftmp)
            print("------ dflo ------")
            dftmp = dflo.T.sort_index()
            print(dftmp)
            print("------ dfcl ------")
            dftmp = dfcl.T.sort_index()
            print(dftmp)

        # 表示更新
        self.__src.data = {
            self.TBLLBL_DATE: dfsmm.index.tolist(),
            self.TBLLBL_WEEK: dfsmm[TTMGoto.LBL_WEEK].tolist(),
            self.TBLLBL_GOTO: dfsmm[TTMGoto.LBL_GOTO].tolist(),
            self.TBLLBL_DIFL: dfsmm[TTMGoto.LBL_DIFL].tolist(),
            self.TBLLBL_DIFH: dfsmm[TTMGoto.LBL_DIFH].tolist(),
        }

        self.__dfsmm = dfsmm

    def __cb_dttbl(self, attr, old, new):
        """Widget DataTableコールバックメソッド
           [Callback method of Widget DataTable]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        idx = new[0]
        self.__csc1.set_dataframe(
            self.__dfsmm.index[idx], self.__csdlist_5m[idx])
        self.__csc2.set_dataframe(
            self.__dfsmm.index[idx], self.__csdlist_1h[idx])
