from math import pi
import pandas as pd
import jpholiday
import datetime as dt
from bokeh.models import ColumnDataSource, CrosshairTool, HoverTool
from bokeh.models import Panel, Tabs
from bokeh.models.widgets import Button, TextInput
from bokeh.models.widgets import TableColumn, DataTable
from bokeh.models.widgets import DateFormatter
from bokeh.models.glyphs import VBar, Line
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox, row, gridplot
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


class DiffChart(object):
    """ DiffChart
            - 差分チャート定義クラス[Difference chart definition class]
    """

    X_TIME = "x_time"
    Y_PRHI = "y_pri_hi"
    Y_PRLO = "y_pri_lo"
    Y_PRCL = "y_pri_cl"

    LBL_MEAN_HI = "mean_high"
    LBL_MEAN_LO = "mean_low"
    LBL_MEAN_CL = "mean_close"
    LBL_STD_HI = "std_high"
    LBL_STD_LO = "std_low"
    LBL_STD_CL = "std_close"

    def __init__(self, title):
        """"コンストラクタ[Constructor]
        引数[Args]:
            fig (figure) : フィギュアオブジェクト[figure object]
            color_ (str) : カラーコード[Color code(ex "#E73B3A")]
        """
        BG_COLOR = "#2E2E2E"  # Background color

        fig = figure(title=title,
                     x_range=[],
                     plot_height=400,
                     plot_width=1500,
                     tools='',
                     background_fill_color=BG_COLOR)
        fig.xaxis.axis_label = "time"
        fig.yaxis.axis_label = "diff price"
        fig.xaxis.major_label_orientation = pi / 2

        dict_ = {DiffChart.X_TIME: [],
                 DiffChart.Y_PRHI: [],
                 DiffChart.Y_PRLO: [],
                 DiffChart.Y_PRCL: []}
        src = ColumnDataSource(dict_)

        # ----- Diff high price -----
        vbarhi = VBar(x=DiffChart.X_TIME,
                      top=DiffChart.Y_PRHI,
                      width=0.9,
                      fill_color="green", line_color="white",
                      line_alpha=0.5, fill_alpha=0.5)
        renhi = fig.add_glyph(src, vbarhi)

        # ----- Diff high price -----
        vbarlo = VBar(x=DiffChart.X_TIME,
                      top=DiffChart.Y_PRLO,
                      width=0.9,
                      fill_color="red", line_color="white",
                      line_alpha=0.5, fill_alpha=0.5)
        renlo = fig.add_glyph(src, vbarlo)

        # ----- Diff close price -----
        vbarcl = Line(x=DiffChart.X_TIME,
                      y=DiffChart.Y_PRCL,
                      line_color="cyan", line_width=2,
                      line_alpha=1.0)
        rencl = fig.add_glyph(src, vbarcl)

        fig.grid.grid_line_color = "white"
        fig.grid.grid_line_alpha = 0.3

        self.__fig = fig
        self.__src = src
        self.__renhi = renhi
        self.__renlo = renlo
        self.__rencl = rencl

    @property
    def render_hi(self):
        """"フィギュアのGlyphRendererオブジェクトを取得する
            [get GlyphRenderer Object of Figure]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            GlyphRenderer Object
        """
        return self.__renhi

    @property
    def render_lo(self):
        """"フィギュアのGlyphRendererオブジェクトを取得する
            [get GlyphRenderer Object of Figure]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            GlyphRenderer Object
        """
        return self.__renlo

    @property
    def render_cl(self):
        """"フィギュアのGlyphRendererオブジェクトを取得する
            [get GlyphRenderer Object of Figure]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            GlyphRenderer Object
        """
        return self.__rencl

    @property
    def fig(self):
        """モデルを取得する[get model]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            self.__fig (object) : model object
        """
        return self.__fig

    def update(self, df):
        timelist = [i.strftime("%H:%M:%S") for i in df.index.tolist()]

        dict_ = {DiffChart.X_TIME: timelist,
                 DiffChart.Y_PRHI: df[DiffChart.LBL_MEAN_HI].tolist(),
                 DiffChart.Y_PRLO: df[DiffChart.LBL_MEAN_LO].tolist(),
                 DiffChart.Y_PRCL: df[DiffChart.LBL_MEAN_CL].tolist(), }
        self.__src.data = dict_

        self.__fig.x_range.factors = timelist

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        dict_ = {DiffChart.X_TIME: [],
                 DiffChart.Y_PRHI: [],
                 DiffChart.Y_PRLO: [],
                 DiffChart.Y_PRCL: []}
        self.__src.data = dict_


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

        self.__vl1 = VerLine(self._fig, "pink", line_width=1)
        self.__vl2 = VerLine(self._fig, "yellow", line_width=1)

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

        self.__vl1 = VerLine(self._fig, "pink", line_width=1)

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

    LBL_DATE = "date"
    LBL_WEEK = "week"
    LBL_GOTO = "goto-day"
    LBL_DIFL = "diff-low-price"
    LBL_DIFH = "diff-high-price"

    FALSE = 0
    TRUE = 1

    _WEEK_DICT = {0: "月", 1: "火", 2: "水", 3: "木",
                  4: "金"}
    _GOTO_DICT = {FALSE: "×", TRUE: "○"}
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

        # 集計結果
        diffchrlist = []
        for i in TTMGoto._WEEK_DICT.keys():
            for j in TTMGoto._GOTO_DICT.keys():
                week = TTMGoto._WEEK_DICT[i]
                goto = TTMGoto._GOTO_DICT[j]
                str_ = "Diff chart [" + week + "]:[" + goto + "]"
                diffchrlist.append(DiffChart(str_))
        self.__diffchrlist = diffchrlist

        # Mean list: 0:High, 1:Low, 2:Close
        self.__meanlist = []
        self.__stdlist = []

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
                           sizing_mode="fixed")

        tabs = self.__create_result_tabs()

        layout_ = layout(children=[[btnrun], [tblfig], [tabs]],
                         sizing_mode="fixed")
        return(layout_)

    def __create_result_tabs(self):

        # Tab1の設定

        plotlist = []
        for i in TTMGoto._WEEK_DICT.keys():
            for j in TTMGoto._GOTO_DICT.keys():
                week = TTMGoto._WEEK_DICT[i]
                goto = TTMGoto._GOTO_DICT[j]
                plot = self.__diffchrlist[i * len(TTMGoto._GOTO_DICT) + j]
                obj = [TextInput(value=week, width=50),
                       TextInput(value=goto, width=50),
                       plot.fig]
                plotlist.append(obj)

        gridview = gridplot(plotlist)

        tab1 = Panel(child=gridview, title="Summary")

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
        dfsmm = self.__dfsmm
        dfsmm.drop(index=dfsmm.index, inplace=True)

        cols = [TTMGoto.LBL_WEEK,
                TTMGoto.LBL_GOTO]
        dfgoto = pd.DataFrame(columns=cols)

        self.__csdlist_5m = []
        self.__csdlist_1h = []

        self.__meanlist = []
        self.__stdlist = []

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
                    target = TTMGoto.TRUE
                    lastday_flg = False
                    gotoday_flg = False
                else:
                    target = TTMGoto.FALSE

                # 出力
                record = pd.Series([weekdayno,
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

            for date_, srrow in dfgoto.iterrows():
                # *************** 5分足チャート ***************
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
                    df5m = csd5m.df[strdttm:enddttm]
                except KeyError:
                    print("-----[Caution] Invalid Date found:[{}]"
                          .format(str(date_)))
                    continue

                minidx = df5m[cs.LBL_LOW].idxmin()
                minpri = df5m[cs.LBL_LOW].min()
                maxpri = df5m[:minidx][cs.LBL_HIGH].max()

                self.__csdlist_5m.append(csd5m)

                print("Open Price: {} " .format(openpri))
                print("Low Price: {} " .format(minpri))
                print("High Price: {} " .format(maxpri))

                # *************** 1時間足チャート ***************
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

                self.__csdlist_1h.append(csd1h)

                # *************** 5分足統計データ ***************
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

                df = csd5m.df

                # 集計
                idxnew = [s.time() for s in df.index]
                idxdict = dict(zip(df.index, idxnew))
                df.rename(index=idxdict, inplace=True)

                tmp = df[cs.LBL_HIGH] - df[cs.LBL_OPEN]
                srhi = pd.Series(tmp, name=date_)
                tmp = df[cs.LBL_LOW] - df[cs.LBL_OPEN]
                srlo = pd.Series(tmp, name=date_)
                tmp = df[cs.LBL_CLOSE] - df[cs.LBL_OPEN]
                srcl = pd.Series(tmp, name=date_)

                srdt = pd.Series(date_, index=[TTMGoto.LBL_DATE])

                dfhi = dfhi.append(
                    pd.concat([srdt, srrow, srhi]), ignore_index=True)
                dflo = dflo.append(
                    pd.concat([srdt, srrow, srlo]), ignore_index=True)
                dfcl = dfcl.append(
                    pd.concat([srdt, srrow, srcl]), ignore_index=True)

                # *************** 出力 ***************
                inst_id = ana.get_instrument_id()
                unit = OandaIns.list[inst_id].min_unit

                record = pd.Series([self._WEEK_DICT[srrow[TTMGoto.LBL_WEEK]],
                                    self._GOTO_DICT[srrow[TTMGoto.LBL_GOTO]],
                                    round(openpri - minpri, unit),
                                    round(maxpri - openpri, unit)],
                                   index=dfsmm.columns,
                                   name=date_)
                dfsmm = dfsmm.append(record)

            idx = [TTMGoto.LBL_DATE, TTMGoto.LBL_WEEK, TTMGoto.LBL_GOTO]
            level_ = [TTMGoto.LBL_WEEK, TTMGoto.LBL_GOTO]
            print("------ dfhi ------")
            print(dfhi)
            dftmp = dfhi.set_index(idx)
            dftmp.sort_index(axis=1, inplace=True)
            hiave = dftmp.mean(level=level_)
            histd = dftmp.std(ddof=0, level=level_)
            print(dftmp)
            print("＜平均＞")
            print(hiave)
            print("＜標準偏差＞")
            print(histd)

            print("------ dflo ------")
            print(dflo)
            dftmp = dflo.set_index(idx)
            dftmp.sort_index(axis=1, inplace=True)
            loave = dftmp.mean(level=level_)
            lostd = dftmp.std(ddof=0, level=level_)
            print(dftmp)
            print("＜平均＞")
            print(loave)
            print("＜標準偏差＞")
            print(lostd)

            print("------ dfcl ------")
            print(dfcl)
            dftmp = dfcl.set_index(idx)
            dftmp.sort_index(axis=1, inplace=True)
            clave = dftmp.mean(level=level_)
            clstd = dftmp.std(ddof=0, level=level_)
            print(dftmp)
            print("＜平均＞")
            print(clave)
            print("＜標準偏差＞")
            print(clstd)

            for i in TTMGoto._WEEK_DICT.keys():
                for j in TTMGoto._GOTO_DICT.keys():
                    try:
                        srhi = hiave.loc[(i, j), :]
                        srhi.name = DiffChart.LBL_MEAN_HI
                        srlo = loave.loc[(i, j), :]
                        srlo.name = DiffChart.LBL_MEAN_LO
                        srcl = clave.loc[(i, j), :]
                        srcl.name = DiffChart.LBL_MEAN_CL
                    except KeyError as e:
                        print("{} are not exist!" .format(e))
                        col = [srhi.name, srlo.name, srcl.name]
                        dfsumm = pd.DataFrame(index=hiave.T.index,
                                              columns=col)
                    else:
                        dfsumm = pd.concat([srhi, srlo, srcl], axis=1)
                    finally:
                        self.__meanlist.append(dfsumm)

                    diffchr = self.__diffchrlist[i * len(TTMGoto._GOTO_DICT) + j]
                    diffchr.update(dfsumm)

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


if __name__ == "__main__":
    from bokeh.io import show

    dc = DiffChart("Diff chart")

    dc.update()

    show(dc.fig)
