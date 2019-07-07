from math import pi
from bokeh.models import Range1d, RangeTool, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.models.glyphs import Segment, VBar, Line
from oandapyV20 import API
from retrying import retry
from datetime import datetime, timedelta
from autotrader.bokeh_common import GlyphVbarAbs
from autotrader.oanda_common import OandaEnv, OandaRsp, OandaGrn
from autotrader.bokeh_common import ToolType, AxisTyp
from autotrader.utils import DateTimeManager
from autotrader.technical import SimpleMovingAverage
import oandapyV20.endpoints.instruments as it
import pandas as pd
import numpy as np
import autotrader.config as cfg


# Pandas data label
LBL_TIME = "time"
LBL_VOLUME = "volume"
LBL_OPEN = "open"
LBL_HIGH = "high"
LBL_LOW = "low"
LBL_CLOSE = "close"


class CandleGlyph(GlyphVbarAbs):
    """ CandleGlyph
            - ローソク図形定義クラス[Candle stick glyph definition class]
    """
    XDT = "xdt"
    YHI = "yhi"
    YLO = "ylo"
    YOP = "yop"
    YCL = "ycl"

    def __init__(self, pltmain, pltrng, color_):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__WIDE_SCALE = 0.5
        self.__COLOR = color_

        super().__init__(self.__WIDE_SCALE)

        self.__src = ColumnDataSource({self.XDT: [], self.YHI: [],
                                       self.YLO: [], self.YOP: [],
                                       self.YCL: []})

        self.__glyseg = Segment(x0=self.XDT, y0=self.YLO, x1=self.XDT,
                                y1=self.YHI, line_color=self.__COLOR,
                                line_width=2)
        self.__glvbar = VBar(x=self.XDT, top=self.YOP, bottom=self.YCL,
                             fill_color=self.__COLOR, line_width=0,
                             line_color=self.__COLOR)

        self.__pltmain = pltmain
        self.__ren = self.__pltmain.add_glyph(self.__src, self.__glyseg)
        self.__pltmain.add_glyph(self.__src, self.__glvbar)

        self.__pltrng = pltrng
        self.__pltrng.add_glyph(self.__src, self.__glyseg)
        self.__pltrng.add_glyph(self.__src, self.__glvbar)

    @property
    def render(self):
        return self.__ren

    def update(self, df, gran):
        """"データを設定する[set glyph date]
        引数[Args]:
            df (pandas data frame) : pandasデータフレーム[pandas data frame]
            gran (str) : ローソク足の時間足[granularity of a candlestick]
        戻り値[Returns]:
            None
        """
        self.__src.data = {
            self.XDT: df.index.tolist(),
            self.YHI: df[LBL_HIGH].tolist(),
            self.YLO: df[LBL_LOW].tolist(),
            self.YOP: df[LBL_OPEN].tolist(),
            self.YCL: df[LBL_CLOSE].tolist()
        }

        self.__glvbar.width = self.get_width(gran)


class OrdersVLineGlyph(object):
    """ OrdersVLineGlyph
            - オーダー垂直線定義クラス[Orders vertical line glyph definition class]
    """
    XDT = "xdt"  # X軸(datetime)
    YPR = "ypr"  # Y軸(float)

    def __init__(self, plt, color_):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__WIDETH = 1
        self.__COLOR = color_

        self.__src = ColumnDataSource({self.XDT: [],
                                       self.YPR: []})
        self.__glvline = Line(x=self.XDT,
                              y=self.YPR,
                              line_color=self.__COLOR,
                              line_dash="dashed",
                              line_width=self.__WIDETH,
                              line_alpha=1.0)

        self.__plt = plt
        self.__plt.add_glyph(self.__src, self.__glvline)

    def update(self, dict_):
        """"データを更新する[update glyph date]
        引数[Args]:
            df (pandas data frame) : pandasデータフレーム[pandas data frame]
            gran (str) : ローソク足の時間足[granularity of a candlestick]
        戻り値[Returns]:
            None
        """
        self.__src.data = dict_

    def clear(self):
        dict_ = {self.XDT: [],
                 self.YPR: []}
        self.__src.data = dict_


class CandleStick(object):
    """ CandleStick
            - ローソク足定義クラス[Candle stick definition class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        from autotrader.oanda_account import ACCESS_TOKEN
        self.__CND_INC_COLOR = "#E73B3A"
        self.__CND_DEC_COLOR = "#03C103"
        self.__CND_EQU_COLOR = "#FFFF00"
        self.__BG_COLOR = "#2E2E2E"  # Background color
        self.__DT_FMT = "%Y-%m-%dT%H:%M:00.000000000Z"
        self.__INIT_WIDE = 0.5
        self.__YRANGE_MARGIN = 0.1

        self.__ORDLINE_CND_COLOR = "yellow"
        self.__ORDLINE_FIX_COLOR = "cyan"

        # self.__CH_COLOR = "#FFFF00"  # Crosshair line color

        self.__yrng = [0, 0]  # [min, max]
        self.__api = API(access_token=ACCESS_TOKEN,
                         environment=OandaEnv.PRACTICE)

        tools_ = ToolType.gen_str(ToolType.WHEEL_ZOOM,
                                  ToolType.XBOX_ZOOM,
                                  ToolType.RESET,
                                  ToolType.SAVE)

        # Main chart figure
        self.__plt_main = figure(plot_height=400,
                                 x_axis_type=AxisTyp.X_DATETIME,
                                 tools=tools_,
                                 background_fill_color=self.__BG_COLOR,
                                 sizing_mode="stretch_width",
                                 title="Candlestick Chart")
        self.__plt_main.xaxis.major_label_orientation = pi / 4
        self.__plt_main.grid.grid_line_alpha = 0.3
        self.__plt_main.x_range = Range1d()
        self.__plt_main.y_range = Range1d()

        # Range chart figure
        self.__plt_rang = figure(plot_height=70,
                                 plot_width=self.__plt_main.plot_width,
                                 y_range=self.__plt_main.y_range,
                                 x_axis_type=AxisTyp.X_DATETIME,
                                 background_fill_color=self.__BG_COLOR,
                                 sizing_mode="stretch_width",
                                 toolbar_location=None)
        self.__plt_rang.yaxis.visible = False
        self.__plt_rang.ygrid.visible = False
        self.__plt_rang.xgrid.visible = False

        self.__range_tool = RangeTool()
        self.__plt_rang.add_tools(self.__range_tool)
        self.__plt_rang.toolbar.active_multi = self.__range_tool
        self.__plt_rang.xaxis.major_label_orientation = pi / 4
        self.__plt_rang.grid.grid_line_alpha = 0.3

        self.__idxmin = -1
        self.__idxmindt = -1

        # Open Orders & Positions vertical line
        self.__glyordcnd = OrdersVLineGlyph(self.__plt_main,
                                            self.__ORDLINE_CND_COLOR)
        self.__glyordfix = OrdersVLineGlyph(self.__plt_main,
                                            self.__ORDLINE_FIX_COLOR)

        # Candle stick figure
        self.__glyinc = CandleGlyph(self.__plt_main,
                                    self.__plt_rang,
                                    self.__CND_INC_COLOR)
        self.__glydec = CandleGlyph(self.__plt_main,
                                    self.__plt_rang,
                                    self.__CND_DEC_COLOR)
        self.__glyequ = CandleGlyph(self.__plt_main,
                                    self.__plt_rang,
                                    self.__CND_EQU_COLOR)

        hover = HoverTool()
        hover.formatters = {CandleGlyph.XDT: "datetime"}
        hover.tooltips = [(LBL_TIME, "@" + CandleGlyph.XDT + "{%F}"),
                          (LBL_HIGH, "@" + CandleGlyph.YHI),
                          (LBL_OPEN, "@" + CandleGlyph.YOP),
                          (LBL_CLOSE, "@" + CandleGlyph.YCL),
                          (LBL_LOW, "@" + CandleGlyph.YLO)]
        hover.renderers = [self.__glyinc.render,
                           self.__glydec.render,
                           self.__glyequ.render]
        self.__plt_main.add_tools(hover)

        self.__sma = SimpleMovingAverage(self.__plt_main)

    @retry(stop_max_attempt_number=5, wait_fixed=500)
    def fetch(self, gran, inst, gmtstr, gmtend):
        """"ローソク足情報を取得する[fetch candles]
        引数[Args]:
            gran (str) : ローソク足の時間足[granularity of a candlestick]
            inst (str) : 通貨ペア[instrument]
            gmtstr (DateTimeManager) : 開始日時[from date]
            gmtend (DateTimeManager) : 終了日時[to date]
        戻り値[Returns]:
            yrng (tuple) : Y軸の最小値、最大値 (min, max)
                           [Y range min and max]
        """
        params_ = {
            # "alignmentTimezone": "Japan",
            "from": gmtstr.gmt.strftime(self.__DT_FMT),
            "to": gmtend.gmt.strftime(self.__DT_FMT),
            "granularity": gran
        }

        # APIへ過去データをリクエスト
        ic = it.InstrumentsCandles(instrument=inst, params=params_)
        try:
            self.__api.request(ic)
        except Exception as err:
            raise err

        data = []
        for raw in ic.response[OandaRsp.CNDL]:
            dt_ = OandaGrn.convert_dtfmt(gran, raw[OandaRsp.TIME],
                                         dt_ofs=timedelta(hours=9),
                                         fmt=self.__DT_FMT)
            data.append([dt_,
                         raw[OandaRsp.VLM],
                         float(raw[OandaRsp.MID][OandaRsp.OPN]),
                         float(raw[OandaRsp.MID][OandaRsp.HIG]),
                         float(raw[OandaRsp.MID][OandaRsp.LOW]),
                         float(raw[OandaRsp.MID][OandaRsp.CLS])
                         ])

        # convert List to pandas data frame
        df = pd.DataFrame(data)
        df.columns = [LBL_TIME,
                      LBL_VOLUME,
                      LBL_OPEN,
                      LBL_HIGH,
                      LBL_LOW,
                      LBL_CLOSE]
        df = df.set_index(LBL_TIME)
        # date型を整形する
        df.index = pd.to_datetime(df.index)

        incflg = df[LBL_CLOSE] > df[LBL_OPEN]
        decflg = df[LBL_OPEN] > df[LBL_CLOSE]
        equflg = df[LBL_CLOSE] == df[LBL_OPEN]

        self.__glyinc.update(df[incflg], gran)
        self.__glydec.update(df[decflg], gran)
        self.__glyequ.update(df[equflg], gran)

        self.__glyordcnd.clear()
        self.__glyordfix.clear()

        len_ = int(len(df) * self.__INIT_WIDE)
        self.__plt_main.x_range.update(
            start=df.index[-len_], end=OandaGrn.offset(df.index[-1], gran))

        self.__range_tool.x_range = self.__plt_main.x_range

        min_ = df[LBL_LOW].min()
        max_ = df[LBL_HIGH].max()
        mar = self.__YRANGE_MARGIN * (max_ - min_)
        str_ = min_ - mar
        end_ = max_ + mar
        yrng = (str_, end_)
        self.__yrng = [str_, end_]

        self.__add_orders_vline(gran, gmtstr, gmtend)
        self.__plt_main.y_range.update(start=str_, end=end_)

        # 単純移動平均線
        if cfg.get_conf(cfg.ITEM_SMA) == 1:
            self.__sma.update_sho(df, cfg.get_conf(cfg.ITEM_SHO))
            self.__sma.update_mid(df, cfg.get_conf(cfg.ITEM_MID))
            self.__sma.update_lon(df, cfg.get_conf(cfg.ITEM_LON))

        self.__df = df

        return yrng

    def update_sma_sho(self, new):
        self.__sma.update_sho(self.__df, new)

    def update_sma_mid(self, new):
        self.__sma.update_mid(self.__df, new)

    def update_sma_lon(self, new):
        self.__sma.update_lon(self.__df, new)

    def clear_sma(self):
        self.__sma.clear()

    def __add_orders_vline(self, gran, gmtstr, gmtend):
        hour_ = gmtstr.tokyo.hour
        minute_ = gmtend.tokyo.minute
        if gran == OandaGrn.D:
            freq_ = pd.offsets.Day(1)
            hour_ = 0
            minute_ = 0
        elif gran == OandaGrn.H12:
            freq_ = pd.offsets.Hour(12)
            hour_ = (hour_ // 12) * 12
            minute_ = 0
        elif gran == OandaGrn.H8:
            freq_ = pd.offsets.Hour(8)
            hour_ = (hour_ // 8) * 8
            minute_ = 0
        elif gran == OandaGrn.H6:
            freq_ = pd.offsets.Hour(6)
            hour_ = (hour_ // 6) * 6
            minute_ = 0
        elif gran == OandaGrn.H4:
            freq_ = pd.offsets.Hour(4)
            hour_ = (hour_ // 4) * 4
            minute_ = 0
        elif gran == OandaGrn.H3:
            freq_ = pd.offsets.Hour(3)
            hour_ = (hour_ // 3) * 3
            minute_ = 0
        elif gran == OandaGrn.H2:
            freq_ = pd.offsets.Hour(2)
            hour_ = (hour_ // 2) * 2
            minute_ = 0
        elif gran == OandaGrn.H1 or \
                gran == OandaGrn.M30 or \
                gran == OandaGrn.M15:
            freq_ = pd.offsets.Hour(1)
            minute_ = 0
        elif gran == OandaGrn.M10 or \
                gran == OandaGrn.M5 or \
                gran == OandaGrn.M4 or \
                gran == OandaGrn.M3 or \
                gran == OandaGrn.M2 or \
                gran == OandaGrn.M1:
            freq_ = pd.offsets.Minute(20)
            minute_ = 20
        else:
            freq_ = pd.offsets.Minute(20)
            minute_ = 20

        dttky_ = gmtstr.tokyo
        str_ = datetime(dttky_.year,
                        dttky_.month,
                        dttky_.day,
                        hour_,
                        minute_)
        end_ = gmtend.tokyo

        dti = pd.date_range(start=str_, end=end_, freq=freq_)
        uti = dti.tz_localize('Asia/Tokyo').astype(np.int64) // 10**9

        self.__dtdf = pd.DataFrame({"timestamp": dti,
                                    "unixtime": uti})

    def draw_orders_cand_vline(self, point):
        idxmin = np.abs(self.__dtdf["unixtime"] - point.timestamp()).idxmin()

        if not self.__idxmin == idxmin:
            idxmindt = self.__dtdf["timestamp"][idxmin].to_pydatetime()
            dict_ = {OrdersVLineGlyph.XDT: [idxmindt, idxmindt],
                     OrdersVLineGlyph.YPR: self.__yrng}
            self.__glyordcnd.update(dict_)
            self.__idxmindt = idxmindt
            self.__idxmin = idxmin

    def draw_orders_fix_vline(self):

        idxmindt = self.__idxmindt
        dict_ = {OrdersVLineGlyph.XDT: [idxmindt, idxmindt],
                 OrdersVLineGlyph.YPR: self.__yrng}
        self.__glyordfix.update(dict_)

    def clear_orders_vline(self):
        self.__glyordcnd.clear()
        self.__glyordfix.clear()

    @property
    def orders_fetch_datetime(self):
        return DateTimeManager(self.__idxmindt)

    @property
    def fig_main(self):
        return self.__plt_main

    @property
    def fig_range(self):
        return self.__plt_rang
