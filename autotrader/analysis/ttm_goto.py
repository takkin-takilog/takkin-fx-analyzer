from abc import ABCMeta
import itertools
import math
from math import pi
from retrying import retry
import numpy as np
import pandas as pd
import jpholiday
import datetime as dt
from bokeh import events
from bokeh.models import Circle, Legend, LegendItem
from bokeh.models import NumeralTickFormatter
from bokeh.models import ColumnDataSource, CrosshairTool, HoverTool
from bokeh.models import Panel, Tabs, Range1d, FactorRange, Span
from bokeh.models.widgets import Button, TextInput
from bokeh.models.widgets import TableColumn, DataTable
from bokeh.models.widgets import DateFormatter
from bokeh.models.glyphs import VBar, Line
from bokeh.palettes import Pastel1_9
from bokeh.plotting import figure
from bokeh.layouts import row, gridplot, column
from oandapyV20.exceptions import V20Error
import autotrader.utils as utl
import autotrader.analysis.candlestick as cs
from autotrader.utils import DateTimeManager
from autotrader.oanda_common import OandaGrn, OandaIns
from autotrader.analysis.candlestick import CandleStickChartBase
from autotrader.analysis.candlestick import CandleStickData
from autotrader.analysis.candlestick import CandleGlyph
from autotrader.technical import SimpleMovingAverage
from autotrader.analysis.base import AnalysisAbs, DateWidget

_TM0900 = dt.time(hour=9, minute=0)
_TM0955 = dt.time(hour=9, minute=55)
_TM1030 = dt.time(hour=10, minute=30)


def _retry_if_connection_error(exception):
    return isinstance(exception, ConnectionError)


class CorrPlot(object):
    """ CorrPlot
            - 相関図定義クラス[Correlation plot definition class]
    """

    X = "x"
    Y = "y"
    C = "color"
    D = "date"

    def __init__(self, title):
        """"コンストラクタ[Constructor]
        """
        BG_COLOR = "#2E2E2E"  # Background color

        fig = figure(title=title,
                     plot_width=400,
                     plot_height=400,
                     x_range=Range1d(),
                     y_range=Range1d(),
                     match_aspect=True,
                     tools='',
                     background_fill_color=BG_COLOR)
        fig.grid.grid_line_color = "white"
        fig.grid.grid_line_alpha = 0.3
        fig.xaxis.axis_label = "diff price (t-1)"
        fig.yaxis.axis_label = "diff price (t)"

        # ----- Vertical and Horizontal line -----
        vl = Span(location=0.0, dimension="height",
                  line_color="white", line_dash="solid", line_width=1)
        fig.add_layout(vl)
        hl = Span(location=0.0, dimension="width",
                  line_color="white", line_dash="solid", line_width=1)
        fig.add_layout(hl)

        # ---------- circle ----------
        src = ColumnDataSource({CorrPlot.X: [],
                                CorrPlot.Y: [],
                                CorrPlot.C: [],
                                CorrPlot.D: []
                                })
        glycir = Circle(x=CorrPlot.X, y=CorrPlot.Y, radius=0.005,
                        line_color=CorrPlot.C, line_alpha=1.0,
                        fill_color=CorrPlot.C, fill_alpha=0.5)
        ren_cir = fig.add_glyph(src, glycir)

        # ---------- legend ----------
        legends = Legend(items=[])
        fig.add_layout(legends)

        # ---------- hover ----------
        hover = HoverTool()
        hover.formatters = {CorrPlot.D: "datetime"}
        hover.tooltips = [("date", "@" + CorrPlot.D + "{%F}"),
                          ("x", "@" + CorrPlot.X + "{0.0000}"),
                          ("y", "@" + CorrPlot.Y + "{0.0000}"),
                          ]
        hover.renderers = [ren_cir]
        fig.add_tools(hover)

        self.__fig = fig
        self.__src = src
        self.__legends = legends
        self.__ren_cir = ren_cir
        self.__glycir = glycir

    def update(self, xlist, ylist, clist, dlist, maxval, yearsidx):

        dict_ = {
            CorrPlot.X: xlist,
            CorrPlot.Y: ylist,
            CorrPlot.C: clist,
            CorrPlot.D: dlist,
        }
        self.__src.data = dict_

        self.__fig.x_range.start = -maxval
        self.__fig.x_range.end = maxval
        self.__fig.y_range.start = -maxval
        self.__fig.y_range.end = maxval
        self.__glycir.radius = maxval / 80

        # set legend
        self.__legends.items = []
        for year, idx in yearsidx:
            item = LegendItem(label=str(year),
                              renderers=[self.__ren_cir],
                              index=idx)
            self.__legends.items.append(item)

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        dict_ = {
            CorrPlot.X: [],
            CorrPlot.Y: [],
            CorrPlot.C: [],
        }
        self.__src.data = dict_

        self.__legends.items = []

    @property
    def fig(self):
        """モデルを取得する[get model]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            self.__fig (object) : model object
        """
        return self.__fig


class ChartAbs(metaclass=ABCMeta):
    """ ChartAbs - Chart抽象クラス"""

    CHART_OFS = 0.5

    def __init__(self, title, plot_height):
        """"コンストラクタ[Constructor]
        """
        BG_COLOR = "#2E2E2E"  # Background color
        self._TIME_FMT = "%H:%M:%S"

        fig = figure(title=title,
                     plot_width=800,
                     x_range=FactorRange(),
                     y_range=Range1d(),
                     plot_height=plot_height,
                     tools='',
                     background_fill_color=BG_COLOR)
        fig.grid.grid_line_color = "white"
        fig.grid.grid_line_alpha = 0.3
        fig.xaxis.axis_label = "time"
        fig.yaxis.axis_label = "diff price"
        fig.xaxis.major_label_orientation = pi / 2

        # ----- Vertical line 9:00 -----
        ttmvl0900 = Span(location=0.0, dimension="height",
                         line_color="cyan", line_dash="solid", line_width=2)
        fig.add_layout(ttmvl0900)

        # ----- Vertical line 9:55 -----
        ttmvl0955 = Span(location=0.0, dimension="height",
                         line_color="pink", line_dash="solid", line_width=2)
        fig.add_layout(ttmvl0955)

        # ----- Vertical line 10:30 -----
        ttmvl1030 = Span(location=0.0, dimension="height",
                         line_color="yellow", line_dash="solid", line_width=2)
        fig.add_layout(ttmvl1030)

        # ----- Vertical line on Cursor -----
        vloncur = Span(location=0.0, dimension="height",
                       line_color="white", line_dash="dashed", line_width=1)
        fig.add_layout(vloncur)

        # ----- Vertical line on Select -----
        vlonsel = Span(location=0.0, dimension="height",
                       line_color="greenyellow", line_dash="dashed",
                       line_width=1)
        fig.add_layout(vlonsel)

        self._fig = fig
        self.__vloncur = vloncur
        self.__vlonsel = vlonsel
        self.__ttmvl0900 = ttmvl0900
        self.__ttmvl0955 = ttmvl0955
        self.__ttmvl1030 = ttmvl1030

    @property
    def fig(self):
        """モデルを取得する[get model]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            self.__fig (object) : model object
        """
        return self._fig

    def update(self, timelist):

        # ----- Vertical line 9:00 -----
        idx = timelist.index(_TM0900.strftime(self._TIME_FMT))
        self.__ttmvl0900.location = idx + DiffChart.CHART_OFS

        # ----- Vertical line 9:55 -----
        idx = timelist.index(_TM0955.strftime(self._TIME_FMT))
        self.__ttmvl0955.location = idx + DiffChart.CHART_OFS

        # ----- Vertical line 10:30 -----
        idx = timelist.index(_TM1030.strftime(self._TIME_FMT))
        self.__ttmvl1030.location = idx + DiffChart.CHART_OFS

    def update_vl_cursol(self, idx):

        self.__vloncur.location = idx + DiffChart.CHART_OFS

    def update_vl_select(self, idx):

        self.__vlonsel.location = idx + DiffChart.CHART_OFS


class DiffChart(ChartAbs):
    """ DiffChart
            - 差分チャート定義クラス[Difference chart definition class]
    """

    X_TIME = "x_time"
    Y_HI_AVE = "y_hi_ave"
    Y_LO_AVE = "y_lo_ave"
    Y_CL_AVE = "y_cl_ave"
    Y_HI_STD = "y_hi_std"
    Y_LO_STD = "y_lo_std"
    Y_CL_STD_HI = "y_cl_std_hi"
    Y_CL_STD_LO = "y_cl_std_lo"

    LBL_AVE_HI = "ave_high"
    LBL_AVE_LO = "ave_low"
    LBL_AVE_CL = "ave_close"
    LBL_STD_HI_OVE = "std_high_over"
    LBL_STD_LO_UND = "std_low_under"
    LBL_STD_CL_OVE = "std_close_over"
    LBL_STD_CL_UND = "std_close_under"

    def __init__(self, title):
        """"コンストラクタ[Constructor]
        引数[Args]:
            fig (figure) : フィギュアオブジェクト[figure object]
            color_ (str) : カラーコード[Color code(ex "#E73B3A")]
        """
        super().__init__(title, 400)

        fig = self._fig
        fig.xaxis.axis_label = "time"
        fig.yaxis.axis_label = "diff price"
        fig.xaxis.major_label_orientation = pi / 2

        dict_ = {DiffChart.X_TIME: [],
                 DiffChart.Y_HI_AVE: [],
                 DiffChart.Y_LO_AVE: [],
                 DiffChart.Y_CL_AVE: [],
                 DiffChart.Y_HI_STD: [],
                 DiffChart.Y_LO_STD: [],
                 DiffChart.Y_CL_STD_HI: [],
                 DiffChart.Y_CL_STD_LO: [],
                 }
        src = ColumnDataSource(dict_)

        # ----- Diff high price ave -----
        vbarhiave = VBar(x=DiffChart.X_TIME,
                         top=DiffChart.Y_HI_AVE,
                         width=0.9,
                         fill_color="green", line_color="white",
                         line_alpha=0.5, fill_alpha=0.5)
        fig.add_glyph(src, vbarhiave)

        # ----- Diff low price ave -----
        vbarloave = VBar(x=DiffChart.X_TIME,
                         top=DiffChart.Y_LO_AVE,
                         width=0.9,
                         fill_color="red", line_color="white",
                         line_alpha=0.5, fill_alpha=0.5)
        fig.add_glyph(src, vbarloave)

        # ----- Diff close price ave -----
        vbarclave = Line(x=DiffChart.X_TIME,
                         y=DiffChart.Y_CL_AVE,
                         line_color="cyan", line_width=2,
                         line_alpha=1.0)
        renclave = fig.add_glyph(src, vbarclave)

        # ----- Diff high price std -----
        vbarhistd = Line(x=DiffChart.X_TIME,
                         y=DiffChart.Y_HI_STD,
                         line_color="lawngreen", line_dash="solid",
                         line_width=1, line_alpha=1.0)
        fig.add_glyph(src, vbarhistd)

        # ----- Diff low price std -----
        vbarlostd = Line(x=DiffChart.X_TIME,
                         y=DiffChart.Y_LO_STD,
                         line_color="pink", line_dash="solid", line_width=1,
                         line_alpha=1.0)
        fig.add_glyph(src, vbarlostd)

        # ----- Diff close price std high -----
        vbarclstdhi = Line(x=DiffChart.X_TIME,
                           y=DiffChart.Y_CL_STD_HI,
                           line_color="cyan", line_dash="dotted", line_width=1,
                           line_alpha=1.0)
        fig.add_glyph(src, vbarclstdhi)

        # ----- Diff close price std low -----
        vbarclstdlo = Line(x=DiffChart.X_TIME,
                           y=DiffChart.Y_CL_STD_LO,
                           line_color="cyan", line_dash="dotted", line_width=1,
                           line_alpha=1.0)
        fig.add_glyph(src, vbarclstdlo)

        # ---------- hover ----------
        hover = HoverTool()
        hover.formatters = {DiffChart.X_TIME: "printf"}
        hover.tooltips = [
            ("Time", "@" + DiffChart.X_TIME),
            ("High(STD)", "@" + DiffChart.Y_HI_STD + "{0.0000}"),
            ("High(AVE)", "@" + DiffChart.Y_HI_AVE + "{0.0000}"),
            ("Close(STD)[HI]", "@" + DiffChart.Y_CL_STD_HI + "{0.0000}"),
            ("Close(AVE)", "@" + DiffChart.Y_CL_AVE + "{0.0000}"),
            ("Close(STD)[LO]", "@" + DiffChart.Y_CL_STD_LO + "{0.0000}"),
            ("Low(AVE)", "@" + DiffChart.Y_LO_AVE + "{0.0000}"),
            ("Low(STD)", "@" + DiffChart.Y_LO_STD + "{0.0000}")
        ]
        hover.renderers = [renclave]
        hover.mode = "vline"
        fig.add_tools(hover)

        self.__fig = fig
        self.__src = src

    def update(self, inst_id, df, y_str, y_end):

        timelist = [i.strftime(self._TIME_FMT) for i in df.index.tolist()]

        super().update(timelist)

        dict_ = {
            DiffChart.X_TIME: timelist,
            DiffChart.Y_HI_AVE: df[DiffChart.LBL_AVE_HI].tolist(),
            DiffChart.Y_LO_AVE: df[DiffChart.LBL_AVE_LO].tolist(),
            DiffChart.Y_CL_AVE: df[DiffChart.LBL_AVE_CL].tolist(),
            DiffChart.Y_HI_STD: df[DiffChart.LBL_STD_HI_OVE].tolist(),
            DiffChart.Y_LO_STD: df[DiffChart.LBL_STD_LO_UND].tolist(),
            DiffChart.Y_CL_STD_HI: df[DiffChart.LBL_STD_CL_OVE].tolist(),
            DiffChart.Y_CL_STD_LO: df[DiffChart.LBL_STD_CL_UND].tolist()
        }
        self.__src.data = dict_

        self.__fig.x_range.factors = timelist
        self.__fig.y_range.start = y_str
        self.__fig.y_range.end = y_end

        fmt = OandaIns.format(inst_id)
        self.__fig.yaxis.formatter = NumeralTickFormatter(format=fmt)

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        dict_ = {DiffChart.X_TIME: [],
                 DiffChart.Y_HI_AVE: [],
                 DiffChart.Y_LO_AVE: [],
                 DiffChart.Y_CL_AVE: [],
                 DiffChart.Y_HI_STD: [],
                 DiffChart.Y_LO_STD: [],
                 DiffChart.Y_CL_STD_HI: []
                 }
        self.__src.data = dict_


class SumChart(ChartAbs):
    """ SumChart
            - 累積和チャート定義クラス[Difference chart definition class]
    """

    X_TIME = "x_time"
    Y_PRI_SUM = "y_pri_sum"

    LBL_SUM = "sum"

    def __init__(self, title):
        """"コンストラクタ[Constructor]
        引数[Args]:
            fig (figure) : フィギュアオブジェクト[figure object]
            color_ (str) : カラーコード[Color code(ex "#E73B3A")]
        """
        super().__init__(title, 300)

        fig = self._fig
        fig.xaxis.axis_label = "time"
        fig.yaxis.axis_label = "Cumulative-Sum price"
        fig.xaxis.major_label_orientation = pi / 2

        dict_ = {SumChart.X_TIME: [],
                 SumChart.Y_PRI_SUM: [],
                 }
        src = ColumnDataSource(dict_)

        # ----- Horizontal line -----
        zeroline = Span(location=0.0, dimension="width", line_color="deeppink",
                        line_dash="solid", line_width=1)
        fig.add_layout(zeroline)

        # ----- Diff high price ave -----
        vbarsum = Line(x=SumChart.X_TIME,
                       y=SumChart.Y_PRI_SUM,
                       line_color="lawngreen", line_dash="solid",
                       line_width=2, line_alpha=1.0)
        rensum = fig.add_glyph(src, vbarsum)

        # ---------- hover ----------
        hover = HoverTool()
        hover.formatters = {SumChart.X_TIME: "printf"}
        hover.tooltips = [
            ("Time", "@" + SumChart.X_TIME),
            ("Price", "@" + SumChart.Y_PRI_SUM + "{0.0000}"),
        ]
        hover.renderers = [rensum]
        hover.mode = "vline"
        fig.add_tools(hover)

        self.__fig = fig
        self.__src = src

    def update(self, inst_id, df, y_str, y_end):

        timelist = [i.strftime(self._TIME_FMT) for i in df.index.tolist()]

        super().update(timelist)

        dict_ = {
            SumChart.X_TIME: timelist,
            SumChart.Y_PRI_SUM: df[SumChart.LBL_SUM].tolist(),
        }
        self.__src.data = dict_

        self.__fig.x_range.factors = timelist
        self.__fig.y_range.start = y_str
        self.__fig.y_range.end = y_end

        fmt = OandaIns.format(inst_id)
        self.__fig.yaxis.formatter = NumeralTickFormatter(format=fmt)

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        dict_ = {SumChart.X_TIME: [],
                 SumChart.Y_PRI_SUM: [],
                 }
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
        self._fig.width = 600
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

    def clear(self):
        super().clear()


class CandleStickChart5M(CandleStickChartAbs):
    """ CandleStickChart
            - ローソク足チャート定義クラス[Candle stick chart definition class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        self.__TM0900 = dt.time(9, 0)
        self.__TM0954 = dt.time(9, 54)
        self.__TM1030 = dt.time(10, 30)

        super().__init__()
        self._fig.title.text = "TTM Candlestick Chart ( 5 minutes )"

        # Vertical Line (9:55)
        vl0900 = Span(location=0.0, dimension="height",
                      line_color="cyan", line_dash="dashed", line_width=1)
        self._fig.add_layout(vl0900)

        # Vertical Line (9:54)
        vl0954 = Span(location=0.0, dimension="height",
                      line_color="pink", line_dash="dashed", line_width=1)
        self._fig.add_layout(vl0954)

        # Vertical Line (10:30)
        vl1030 = Span(location=0.0, dimension="height",
                      line_color="yellow", line_dash="dashed", line_width=1)
        self._fig.add_layout(vl1030)

        self.__vl0900 = vl0900
        self.__vl0954 = vl0954
        self.__vl1030 = vl1030

    def set_dataframe(self, date_, csd):
        super().set_dataframe(csd)

        dat_ = dt.date(date_.year, date_.month, date_.day)

        x_dttm = dt.datetime.combine(dat_, self.__TM0900)
        self.__vl0900.location = x_dttm

        x_dttm = dt.datetime.combine(dat_, self.__TM0954)
        self.__vl0954.location = x_dttm

        x_dttm = dt.datetime.combine(dat_, self.__TM1030)
        self.__vl1030.location = x_dttm

    def clear(self):
        super().clear()

        self.__vl0900.location = 0
        self.__vl0954.location = 0
        self.__vl1030.location = 0


class CandleStickChart1H(CandleStickChartAbs):
    """ CandleStickChart
            - ローソク足チャート定義クラス[Candle stick chart definition class]
    """
    XDT = "xdt"  # X軸(datetime)
    YPR = "ypr"  # Y軸(float)

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        self.__TM0954 = dt.time(9, 54)

        super().__init__()
        self._fig.title.text = "TTM Candlestick Chart ( 1 hour )"

        # ---------- Vertical Line (9:54) ----------
        vl0954 = Span(location=0.0, dimension="height",
                      line_color="pink", line_dash="dashed", line_width=1)
        self._fig.add_layout(vl0954)

        # ---------- 移動平均線 ----------
        self.__sma = SimpleMovingAverage(self._fig)

        # ---------- slope line ----------
        src = ColumnDataSource({self.XDT: [],
                                self.YPR: []})
        glvline = Line(x=self.XDT,
                       y=self.YPR,
                       line_color="cyan",
                       line_dash="solid",
                       line_width=3.0,
                       line_alpha=1.0)
        self._fig.add_glyph(src, glvline)

        self.__vl0954 = vl0954
        self.__src = src

    def calc_sma(self, csd, window_):
        self.__sma.calc_sma_mdl(csd.df, window_)

    def set_dataframe(self, date_, csd, l2p):
        super().set_dataframe(csd)

        dat_ = dt.date(date_.year, date_.month, date_.day)

        x_dttm = dt.datetime.combine(dat_, self.__TM0954)
        self.__vl0954.location = x_dttm

        self.__sma.draw_mdl(csd.df)

        if len(l2p) == 0:
            self.__src.data = {self.XDT: [],
                               self.YPR: []}
        else:
            self.__src.data = {self.XDT: l2p[0],
                               self.YPR: l2p[1]}

    def clear(self):
        super().clear()

        self.__sma.clear()

        self.__src.data = {self.XDT: [],
                           self.YPR: []}


class TTMGoto(AnalysisAbs):
    """ TTMGoto
            - 仲根(TTM)とゴトー日クラス[TTM and Goto day class]
    """

    LBL_DATE = "date"
    LBL_WEEK = "week"
    LBL_GOTO = "goto-day"
    LBL_OHLC = "ohlc"
    LBL_TREND_SL = "trend-slope"
    LBL_DIF0900H = "diff-0900-high-price"
    LBL_DIF0955L = "diff-0955-low-price"
    LBL_DIF0900H = "diff-0900-high-price"
    LBL_DIF0955L = "diff-0955-low-price"
    LBL_DIF0950OC = "diff-cs0900oc"
    LBL_DIF0955OC = "diff-cs0955oc"
    LBL_TREND_2P = "trend-2p"

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
        super().__init__()

        diffdate = dt.date.today() - dt.timedelta(days=30)
        self.__dtwdg_str = DateWidget("開始", diffdate)
        self.__dtwdg_end = DateWidget("終了",)

        # Widget Button:解析実行[Run analysis]
        self.__btn_run = Button(label="解析実行",
                                button_type="success",
                                sizing_mode="fixed",
                                default_size=200)
        self.__btn_run.on_click(self.__cb_btn_run)

        cols = [TTMGoto.LBL_WEEK,
                TTMGoto.LBL_GOTO,
                TTMGoto.LBL_TREND_SL,
                TTMGoto.LBL_DIF0900H,
                TTMGoto.LBL_DIF0955L,
                TTMGoto.LBL_DIF0950OC,
                TTMGoto.LBL_DIF0955OC,
                TTMGoto.LBL_TREND_2P
                ]
        self.__dfsmm = pd.DataFrame(columns=cols)

        self.__dfall = pd.DataFrame()

        # Widget DataTable:
        self.TBLLBL_DATE = "date"
        self.TBLLBL_WEEK = "week"
        self.TBLLBL_GOTO = "goto-day"
        self.TBLLBL_TREND_SL = "trend slope"
        self.TBLLBL_DIF0900H = "diff-0900-high-price"
        self.TBLLBL_DIF0955L = "diff-0955-low-price"
        self.TBLLBL_CS0950OC = "cs-0950oc"
        self.TBLLBL_CS0955OC = "cs-0955oc"

        # データテーブル初期化
        self.__src = ColumnDataSource({self.TBLLBL_DATE: [],
                                       self.TBLLBL_WEEK: [],
                                       self.TBLLBL_GOTO: [],
                                       self.TBLLBL_TREND_SL: [],
                                       self.TBLLBL_DIF0900H: [],
                                       self.TBLLBL_DIF0955L: [],
                                       self.TBLLBL_CS0950OC: [],
                                       self.TBLLBL_CS0955OC: [],
                                       })

        cols = [
            TableColumn(field=self.TBLLBL_DATE, title="Date",
                        formatter=DateFormatter()),
            TableColumn(field=self.TBLLBL_WEEK, title="Week"),
            TableColumn(field=self.TBLLBL_GOTO, title="Goto Day"),
            TableColumn(field=self.TBLLBL_TREND_SL, title="Trend slope"),
            TableColumn(field=self.TBLLBL_DIF0900H,
                        title="Diff Price (9:00 - 9:55)"),
            TableColumn(field=self.TBLLBL_DIF0955L,
                        title="Diff Price (9:55 - 10:30)"),
            TableColumn(field=self.TBLLBL_CS0950OC,
                        title="Diff CS (9:50 - 9:55)"),
            TableColumn(field=self.TBLLBL_CS0955OC,
                        title="Diff CS (9:55 - 10:00)"),
        ]

        self.__tbl = DataTable(source=self.__src,
                               columns=cols,
                               fit_columns=True,
                               height=200,
                               width=1200)
        self.__src.selected.on_change("indices", self.__cb_dttbl)

        # ローソク足チャート初期化
        self.__csc5m = CandleStickChart5M()
        self.__csdlist_5m = []

        self.__csc1h = CandleStickChart1H()
        self.__csdlist_1h = []

        # 集計結果
        diffchrlist = []
        diffsumlist = []
        corrpltlist = []
        sampcntlist = []

        week_keys = TTMGoto._WEEK_DICT.keys()
        goto_keys = TTMGoto._GOTO_DICT.keys()
        for i, j in itertools.product(week_keys, goto_keys):
            week = TTMGoto._WEEK_DICT[i]
            goto = TTMGoto._GOTO_DICT[j]

            # ---------- Diff-chart ----------
            str_ = "Diff-chart Week[" + week + "]:Goto[" + goto + "]"
            diffchr = DiffChart(str_)
            diffchrlist.append(diffchr)

            # ---------- Cumulative Sum-chart ----------
            str_ = "Cumulative Sum-chart Week[" + week + "]:Goto[" + goto + "]"
            sumchr = SumChart(str_)
            diffsumlist.append(sumchr)

            # ---------- Correlation Plot ----------
            str_ = "Correlation plot Week[" + week + "]:Goto[" + goto + "]"
            corrplt = CorrPlot(str_)
            corrpltlist.append(corrplt)

            # ---------- Text ----------
            txtin_cnt = TextInput(value="", title="サンプル数:",
                                  width=100, sizing_mode="fixed")
            sampcntlist.append(txtin_cnt)

            diffchr.fig.on_event(events.MouseMove, self.__cb_chart_mousemove)
            sumchr.fig.on_event(events.MouseMove, self.__cb_chart_mousemove)

            diffchr.fig.on_event(events.Tap, self.__cb_chart_tap)
            sumchr.fig.on_event(events.Tap, self.__cb_chart_tap)

        self.__diffchrlist = diffchrlist
        self.__diffsumlist = diffsumlist
        self.__corrpltlist = corrpltlist
        self.__sampcntlist = sampcntlist
        self.__timelist = []

    @property
    def layout(self):
        """レイアウトを取得する[get layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        dtwdg_str = self.__dtwdg_str.widget
        dtwdg_end = self.__dtwdg_end.widget
        dtwdg = row(children=[dtwdg_str, dtwdg_end])
        wslin = self._slc_inst

        wdgbx1 = column(children=[wslin, dtwdg], sizing_mode="fixed")

        btnrun = self.__btn_run
        tbl = self.__tbl
        cscfig5m = self.__csc5m.fig
        cscfig1h = self.__csc1h.fig

        cscfigs = row(children=[cscfig5m, cscfig1h])

        tblfig = column(children=[tbl, cscfigs])

        tabs = self.__create_result_tabs()

        wdgbx2 = column(children=[btnrun, tblfig, tabs])

        layout_ = row(children=[wdgbx1, wdgbx2])

        return(layout_)

    def __create_result_tabs(self):

        # Tab1の設定

        plotlist = []

        week_keys = TTMGoto._WEEK_DICT.keys()
        goto_keys = TTMGoto._GOTO_DICT.keys()
        for i, j in itertools.product(week_keys, goto_keys):
            pos = i * len(TTMGoto._GOTO_DICT) + j
            sampcnt = self.__sampcntlist[pos]
            diffplot = self.__diffchrlist[pos]
            sumplot = self.__diffsumlist[pos]
            txtin = column(children=[sampcnt],
                           sizing_mode="fixed")
            plotfig = column(children=[diffplot.fig, sumplot.fig],
                             sizing_mode="fixed")
            corrfig = self.__corrpltlist[pos].fig
            plotlist.append([txtin, plotfig, corrfig])

        gridview = gridplot(children=plotlist, sizing_mode="fixed")

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
        for corrplt in self.__corrpltlist:
            corrplt.clear()

        dfsmm = self.__dfsmm
        dfsmm.drop(index=dfsmm.index, inplace=True)

        self.__csdlist_5m = []
        self.__csdlist_1h = []

        yesterday = dt.date.today() - dt.timedelta(days=1)
        str_ = self.__dtwdg_str.date
        str_ = utl.limit_upper(str_, yesterday)
        end_ = self.__dtwdg_end.date
        end_ = utl.limit_upper(end_, yesterday)

        # search Goto-Days
        dfgoto = self.__search_goto_day(str_, end_)

        if dfgoto.empty:
            print("リストは空です")
        else:

            df = pd.DataFrame()
            inst_id = self.instrument_id

            cnt = 0
            for date_, srrow in dfgoto.iterrows():

                try:
                    # *************** 1時間足チャート ***************
                    str_dt = dt.datetime.combine(
                        date_, dt.time(0, 0)) - dt.timedelta(days=5)
                    end_dt = dt.datetime.combine(date_, dt.time(15, 0))
                    gran = OandaGrn.H1

                    csd1h = self.__fetch_candlestick(inst_id, gran,
                                                     str_dt, end_dt)

                    # *************** 5分足チャート ***************
                    str_dt = dt.datetime.combine(date_, dt.time(8, 30))
                    end_dt = dt.datetime.combine(date_, dt.time(12, 0))
                    gran = OandaGrn.M5

                    csd5m = self.__fetch_candlestick(inst_id, gran,
                                                     str_dt, end_dt)

                except ValueError:
                    print("-----[Caution] Invalid Date found:[{}]"
                          .format(str(date_)))
                    cnt += 1
                    continue

                # 移動平均線
                self.__csc1h.calc_sma(csd1h, 20)
                sma_sr = csd1h.df[SimpleMovingAverage.LBL_SMA_M]

                # 線形近似
                slope, l2p = self.__calc_linear_slope(date_, sma_sr)

                try:
                    # ---------- Extraction 9:00～9:55 chart ----------
                    d900 = self.__extract_from_900_to_955(date_, csd5m,
                                                          inst_id)

                    # ---------- Extraction 9:55～10:30 chart ----------
                    d955 = self.__extract_from_955_to_1030(date_, csd5m,
                                                           inst_id)

                    tm = dt.time(hour=9, minute=50)
                    cs950 = self.__extract_diff_candlestick(
                        tm, date_, csd5m, inst_id)

                    tm = dt.time(hour=9, minute=55)
                    cs955 = self.__extract_diff_candlestick(
                        tm, date_, csd5m, inst_id)

                except KeyError:
                    print("-----[Caution] Can't extract data Due to Invalid \
                            Date:[{}]".format(str(date_)))
                    continue

                # ---------- output ----------
                self.__csdlist_1h.append(csd1h)
                self.__csdlist_5m.append(csd5m)

                # *************** 出力 ***************
                record = pd.Series([srrow[TTMGoto.LBL_WEEK],
                                    srrow[TTMGoto.LBL_GOTO],
                                    slope,
                                    d900,
                                    d955,
                                    cs950,
                                    cs955,
                                    l2p],
                                   index=self.__dfsmm.columns,
                                   name=date_)
                dfsmm = dfsmm.append(record)

                # make OHCL data-frame
                df = self.__append_ohcl_df(df, csd5m, date_, srrow)

                cnt += 1
                print("{} / {}" .format(cnt, len(dfgoto)))

            idx = [TTMGoto.LBL_OHLC, TTMGoto.LBL_DATE,
                   TTMGoto.LBL_WEEK, TTMGoto.LBL_GOTO]
            level_ = [TTMGoto.LBL_OHLC, TTMGoto.LBL_WEEK, TTMGoto.LBL_GOTO]

            df = df.set_index(idx)
            df.sort_index(axis=1, inplace=True)

            # ---------- calculate mean ----------
            dfave = df.mean(level=level_)
            # ---------- calculate standard deviation ----------
            dfstd = df.std(ddof=0, level=level_)

            self.__timelist = dfave.columns.tolist()

            # ---------- calculate parameter ----------
            dfhi = df.loc[cs.LBL_HIGH, :]
            tmp = [TTMGoto.LBL_WEEK, TTMGoto.LBL_GOTO]
            dfcnt = dfhi.groupby(level=tmp).size()
            dfparam = dfcnt.sum()

            # ---------- calculate Cumulative sum ----------
            dfavecl = dfave.loc[cs.LBL_CLOSE, :]
            dfaveclave = dfavecl.mean(
                level=[TTMGoto.LBL_WEEK, TTMGoto.LBL_GOTO])
            clavesum = dfaveclave.cumsum(axis=1)

            margin = 1.2
            y_diff_max = dfave.max().max() * margin
            y_diff_min = dfave.min().min() * margin
            y_sum_max = clavesum.max().max() * margin
            y_sum_min = clavesum.min().min() * margin

            week_keys = TTMGoto._WEEK_DICT.keys()
            goto_keys = TTMGoto._GOTO_DICT.keys()
            for i, j in itertools.product(week_keys, goto_keys):

                try:
                    cnt = dfcnt[i, j]
                    dfdiff = self.__generate_statistics_df(i, j, dfave, dfstd)
                    dfsum = self.__generate_sum_df(i, j, clavesum)
                except KeyError as e:
                    print("{} are not exist!" .format(e))
                    cnt = 0

                    col = [DiffChart.LBL_AVE_HI, DiffChart.LBL_AVE_LO,
                           DiffChart.LBL_AVE_CL, DiffChart.LBL_STD_HI_OVE,
                           DiffChart.LBL_STD_LO_UND, DiffChart.LBL_STD_CL_OVE,
                           DiffChart.LBL_STD_CL_UND]
                    idx = dfave.loc[cs.LBL_HIGH, :].T.index
                    dfdiff = pd.DataFrame(index=idx, columns=col)
                    col = [SumChart.LBL_SUM]
                    idx = clavesum.T.index
                    dfsum = pd.DataFrame(index=idx, columns=col)

                pos = i * len(TTMGoto._GOTO_DICT) + j
                diffchr = self.__diffchrlist[pos]
                diffchr.update(inst_id, dfdiff, y_diff_min, y_diff_max)

                diffsum = self.__diffsumlist[pos]
                diffsum.update(inst_id, dfsum, y_sum_min, y_sum_max)

                sampcnt = self.__sampcntlist[pos]
                sampcnt.value = str(cnt) + " / " + str(dfparam)

                self.__dfall = df

        # 表示更新
        srweek = dfsmm[TTMGoto.LBL_WEEK].replace(self._WEEK_DICT)
        srgoto = dfsmm[TTMGoto.LBL_GOTO].replace(self._GOTO_DICT)
        self.__src.data = {
            self.TBLLBL_DATE: dfsmm.index.tolist(),
            self.TBLLBL_WEEK: srweek.tolist(),
            self.TBLLBL_GOTO: srgoto.tolist(),
            self.TBLLBL_TREND_SL: dfsmm[TTMGoto.LBL_TREND_SL].tolist(),
            self.TBLLBL_DIF0900H: dfsmm[TTMGoto.LBL_DIF0900H].tolist(),
            self.TBLLBL_DIF0955L: dfsmm[TTMGoto.LBL_DIF0955L].tolist(),
            self.TBLLBL_CS0950OC: dfsmm[TTMGoto.LBL_DIF0950OC].tolist(),
            self.TBLLBL_CS0955OC: dfsmm[TTMGoto.LBL_DIF0955OC].tolist(),
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
        self.__csc5m.set_dataframe(
            self.__dfsmm.index[idx], self.__csdlist_5m[idx])
        self.__csc1h.set_dataframe(
            self.__dfsmm.index[idx], self.__csdlist_1h[idx],
            self.__dfsmm[TTMGoto.LBL_TREND_2P][idx])

    def __calc_linear_slope(self, date_, sr):

        strtm = dt.time(hour=0, minute=0)
        strdttm = str(dt.datetime.combine(date_, strtm))
        endtm = dt.time(hour=10, minute=0)
        enddttm = str(dt.datetime.combine(date_, endtm))

        slope = 0.0
        l2p = np.empty(0)
        try:
            dfsma = sr[strdttm:enddttm]
        except KeyError:
            print("-----[Caution] Invalid Date found:[{}]"
                  .format(str(date_)))
            return slope, l2p

        lenmax = endtm.hour - strtm.hour - 1
        if lenmax < len(dfsma):
            y = dfsma.values
            x = list(range(len(dfsma)))
            linear = np.polyfit(x, y, 1)
            slope = linear[0]
            func = np.poly1d(linear)
            y2p = func([x[0], x[-1]])
            x2p = [dfsma.index[0].to_pydatetime(),
                   dfsma.index[-1].to_pydatetime()]

            l2p = np.array([x2p, y2p])

        return slope, l2p

    def __search_goto_day(self, str_, end_):

        cols = [TTMGoto.LBL_WEEK,
                TTMGoto.LBL_GOTO]
        dfgoto = pd.DataFrame(columns=cols)

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

        return dfgoto

    @retry(stop_max_attempt_number=5,
           wait_fixed=500,
           retry_on_exception=_retry_if_connection_error)
    def __fetch_candlestick(self, inst_id, gran, str_dt, end_dt):

        inst = OandaIns.list[inst_id].oanda_name
        dtmstr = DateTimeManager(str_dt)
        dtmend = DateTimeManager(end_dt)

        try:
            csd = CandleStickData(gran, inst, dtmstr, dtmend)
        except V20Error as v20err:
            print("-----V20Error: {}".format(v20err))
            raise v20err
        except ConnectionError as cerr:
            print("----- ConnectionError: {}".format(cerr))
            raise cerr
        except Exception as excp:
            print("----- Exception: {}".format(excp))
            raise excp

        return csd

    def __extract_from_900_to_955(self, date_, csd5m, inst_id):

        strtm = dt.time(hour=9, minute=0)
        strdttm = str(dt.datetime.combine(date_, strtm))
        endtm = dt.time(hour=9, minute=50)
        enddttm = str(dt.datetime.combine(date_, endtm))

        openpri = csd5m.df.loc[strdttm, cs.LBL_OPEN]
        closepri = csd5m.df.loc[enddttm, cs.LBL_CLOSE]

        diff0900h = OandaIns.normalize(inst_id, closepri - openpri)

        return diff0900h

    def __extract_from_955_to_1030(self, date_, csd5m, inst_id):

        strtm = dt.time(hour=9, minute=55)
        strdttm = str(dt.datetime.combine(date_, strtm))
        endtm = dt.time(hour=10, minute=25)
        enddttm = str(dt.datetime.combine(date_, endtm))

        openpri = csd5m.df.loc[strdttm, cs.LBL_OPEN]
        df5m = csd5m.df[strdttm:enddttm]

        minpri = df5m[cs.LBL_LOW].min()
        diff0955l = OandaIns.normalize(inst_id, minpri - openpri)

        return diff0955l

    def __extract_diff_candlestick(self, tm, date_, csd5m, inst_id):

        dttm = str(dt.datetime.combine(date_, tm))

        openpri = csd5m.df.loc[dttm, cs.LBL_OPEN]
        closepri = csd5m.df.loc[dttm, cs.LBL_CLOSE]

        cslen = OandaIns.normalize(inst_id, closepri - openpri)

        return cslen

    def __append_ohcl_df(self, df, csd, date_, srrow):

        # 集計
        idxnew = [s.time() for s in csd.df.index]
        idxdict = dict(zip(csd.df.index, idxnew))
        dftmp = csd.df.rename(index=idxdict)

        tmp = dftmp[cs.LBL_HIGH] - dftmp[cs.LBL_OPEN]
        srhi = pd.Series(tmp, name=date_)
        tmp = dftmp[cs.LBL_LOW] - dftmp[cs.LBL_OPEN]
        srlo = pd.Series(tmp, name=date_)
        tmp = dftmp[cs.LBL_CLOSE] - dftmp[cs.LBL_OPEN]
        srcl = pd.Series(tmp, name=date_)

        srdt = pd.Series(date_, index=[TTMGoto.LBL_DATE])

        ochl = pd.Series(cs.LBL_HIGH, index=[TTMGoto.LBL_OHLC])
        df1 = pd.concat([srdt, srrow, srhi, ochl])
        ochl = pd.Series(cs.LBL_LOW, index=[TTMGoto.LBL_OHLC])
        df2 = pd.concat([srdt, srrow, srlo, ochl])
        ochl = pd.Series(cs.LBL_CLOSE, index=[TTMGoto.LBL_OHLC])
        df3 = pd.concat([srdt, srrow, srcl, ochl])

        df = df.append(df1, ignore_index=True)
        df = df.append(df2, ignore_index=True)
        df = df.append(df3, ignore_index=True)

        return df

    def __generate_statistics_df(self, week_no, goto_no, dfave, dfstd):

        sravehi = dfave.loc[cs.LBL_HIGH, :].loc[(week_no, goto_no), :]
        sravehi.name = DiffChart.LBL_AVE_HI
        sravelo = dfave.loc[cs.LBL_LOW, :].loc[(week_no, goto_no), :]
        sravelo.name = DiffChart.LBL_AVE_LO
        sravecl = dfave.loc[cs.LBL_CLOSE, :].loc[(week_no, goto_no), :]
        sravecl.name = DiffChart.LBL_AVE_CL

        dfstd_hi = dfstd.loc[cs.LBL_HIGH, :]
        srstdhi_ove = sravehi + dfstd_hi.loc[(week_no, goto_no), :]
        srstdhi_ove.name = DiffChart.LBL_STD_HI_OVE

        dfstd_lo = dfstd.loc[cs.LBL_LOW, :]
        srstdlo_und = sravelo - dfstd_lo.loc[(week_no, goto_no), :]
        srstdlo_und.name = DiffChart.LBL_STD_LO_UND

        dfstd_cl = dfstd.loc[cs.LBL_CLOSE, :]
        srstdcl_ove = sravecl + dfstd_cl.loc[(week_no, goto_no), :]
        srstdcl_ove.name = DiffChart.LBL_STD_CL_OVE
        srstdcl_und = sravecl - dfstd_cl.loc[(week_no, goto_no), :]
        srstdcl_und.name = DiffChart.LBL_STD_CL_UND

        dfdiff = pd.concat([sravehi, sravelo, sravecl, srstdhi_ove,
                            srstdlo_und, srstdcl_ove, srstdcl_und],
                           axis=1)
        return dfdiff

    def __generate_sum_df(self, week_no, goto_no, clavesum):

        sraveclsum = clavesum.loc[(week_no, goto_no), :]
        sraveclsum.name = SumChart.LBL_SUM
        dfsum = pd.concat([sraveclsum], axis=1)

        return dfsum

    def __cb_chart_mousemove(self, event):
        """Event mouse move(チャート)コールバックメソッド
           [Callback method of mouse move event(Chart)]
        引数[Args]:
            event (str) : An event name on this object
        戻り値[Returns]:
            なし[None]
        """
        if event.x is not None:
            idx = math.floor(event.x + DiffChart.CHART_OFS)

            for diffchr in self.__diffchrlist:
                diffchr.update_vl_cursol(idx)

            for diffsum in self.__diffsumlist:
                diffsum.update_vl_cursol(idx)

    def __cb_chart_tap(self, event):
        """Event tap(チャート)コールバックメソッド
           [Callback method of tap event(Chart)]
        引数[Args]:
            event (str) : An event name on this object
        戻り値[Returns]:
            なし[None]
        """
        if event.x is not None:

            LBL_YEAR = "year"
            LBL_COLOR = "color"
            MARGINE = 1.2

            idx = math.floor(event.x + DiffChart.CHART_OFS)

            for diffchr in self.__diffchrlist:
                diffchr.update_vl_select(idx)

            for diffsum in self.__diffsumlist:
                diffsum.update_vl_select(idx)

            if idx == 0:
                idx_pre = 0
            else:
                idx_pre = idx - 1

            col_tm = self.__timelist[idx]
            col_tmpre = self.__timelist[idx_pre]

            dfcl = self.__dfall.loc[cs.LBL_CLOSE, :]
            df = dfcl[[col_tmpre, col_tm]]
            df = df.reset_index(TTMGoto.LBL_DATE)
            idxnew = [s.year for s in df[TTMGoto.LBL_DATE]]
            df[LBL_YEAR] = idxnew

            # Year重複削除
            years = list(set(idxnew))

            colvals = []
            for x in range(len(years)):
                colvals.append(Pastel1_9[x])
            d = dict(zip(years, colvals))
            collist = [d[s] for s in idxnew]
            df[LBL_COLOR] = collist
            dftmp = df[[col_tmpre, col_tm]]

            max_ = dftmp.max().max()
            min_ = dftmp.min().min()
            maxval = max([math.fabs(max_), math.fabs(min_)]) * MARGINE

            df = df.sort_index()
            week_keys = TTMGoto._WEEK_DICT.keys()
            goto_keys = TTMGoto._GOTO_DICT.keys()
            for i, j in itertools.product(week_keys, goto_keys):

                try:
                    df1 = df.loc[(i, j), :]
                except KeyError as e:
                    print("{} are not exist!" .format(e))
                    continue

                xlist = df1[col_tmpre].tolist()
                ylist = df1[col_tm].tolist()
                clist = df1[LBL_COLOR].tolist()
                dlist = df1[TTMGoto.LBL_DATE].tolist()
                yearlist = df1[LBL_YEAR].tolist()

                pos = i * len(TTMGoto._GOTO_DICT) + j
                corrplt = self.__corrpltlist[pos]

                yearsidx = [(y, yearlist.index(y)) for y in set(yearlist)]
                corrplt.update(xlist, ylist, clist, dlist, maxval, yearsidx)
