from math import pi
from bokeh.models import Range1d, RangeTool, ColumnDataSource
from bokeh.models import HoverTool, CrosshairTool
from bokeh.plotting import figure
from bokeh.models.glyphs import Segment, VBar
from oandapyV20 import API
from retrying import retry
from autotrader.bokeh_common import GlyphVbarAbs
from autotrader.oanda_common import OandaEnv, OandaRsp, OandaGrn
from autotrader.bokeh_common import ToolType, AxisTyp
from datetime import datetime, timedelta
import oandapyV20.endpoints.instruments as it
import pandas as pd
import autotrader.oanda_account as oa
from dask.array.tests.test_numpy_compat import dtype
from comtypes.npsupport import numpy


# Pandas data label
_TIME = "time"
_VOLUME = "volume"
_OPEN = "open"
_HIGH = "high"
_LOW = "low"
_CLOSE = "close"


class CandleGlyph(GlyphVbarAbs):
    """ CandleGlyph
            - ローソク図形定義クラス[Candle stick glyph definition class]
    """
    XDT = "xdt"
    YHI = "yhi"
    YLO = "ylo"
    YOP = "yop"
    YCL = "ycl"

    def __init__(self, color_):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__WIDE_SCALE = 0.5
        self.__COLOR = color_

        super().__init__(self.__WIDE_SCALE)

        self.__src = ColumnDataSource(
            dict(xdt=[], yhi=[], ylo=[], yop=[], ycl=[])
        )
        self.__glyseg = Segment(x0=self.XDT, y0=self.YLO, x1=self.XDT,
                                y1=self.YHI, line_color=self.__COLOR,
                                line_width=1)
        self.__glvbar = VBar(x=self.XDT, top=self.YOP, bottom=self.YCL,
                             fill_color=self.__COLOR, line_width=0,
                             line_color=self.__COLOR)

    def set_data(self, df, gran):
        """"データを設定する[set glyph date]
        引数[Args]:
            df (pandas data frame) : pandasデータフレーム[pandas data frame]
            gran (str) : ローソク足の時間足[granularity of a candlestick]
        戻り値[Returns]:
            None
        """
        self.__src.data = dict(
            xdt=df.index.tolist(),
            ylo=df[_LOW].tolist(),
            yhi=df[_HIGH].tolist(),
            yop=df[_OPEN].tolist(),
            ycl=df[_CLOSE].tolist(),
        )
        self.__glvbar.width = self.get_width(gran)

    def add_plot(self, plt):
        """"プロットを追加する[add plot]
        引数[Args]:
            plt (figure) : bokehのfigureクラス[class of bokeh's figure]
        戻り値[Returns]:
            None
        """
        plt.add_glyph(self.__src, self.__glyseg)
        plt.add_glyph(self.__src, self.__glvbar)


class OrdersVbarGlyph(GlyphVbarAbs):
    """ CandleGlyph
            - ローソク図形定義クラス[Candle stick glyph definition class]
    """
    XDT = "xdt"  # X軸(datetime)
    YTP = "ytp"  # Y軸 VbarのTop
    YBT = "ybt"  # Y軸 VbarのBottom

    def __init__(self, color_):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__WIDE_SCALE = 0.1
        self.__COLOR = color_

        super().__init__(self.__WIDE_SCALE)

        self.__src = ColumnDataSource(
            dict(xdt=[], ytp=[], ybt=[])
        )
        self.__glvbar = VBar(x=self.XDT, top=self.YTP, bottom=self.YBT,
                             fill_color=self.__COLOR, line_width=0,
                             line_color=self.__COLOR)

    def set_data(self, df, gran):
        """"データを設定する[set glyph date]
        引数[Args]:
            df (pandas data frame) : pandasデータフレーム[pandas data frame]
            gran (str) : ローソク足の時間足[granularity of a candlestick]
        戻り値[Returns]:
            None
        """
        self.__src.data = dict(
            xdt=df.index.tolist(),
            ytp=df[self.YTP].tolist(),
            ybt=df[self.YBT].tolist(),
        )
        self.__glvbar.width = self.get_width(gran)

    def add_plot(self, plt):
        """"プロットを追加する[add plot]
        引数[Args]:
            plt (figure) : bokehのfigureクラス[class of bokeh's figure]
        戻り値[Returns]:
            None
        """
        plt.add_glyph(self.__src, self.__glvbar)


class CandleStick(object):
    """ CandleStick
            - ローソク足定義クラス[Candle stick definition class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__CND_INC_COLOR = "#E73B3A"
        self.__CND_DEC_COLOR = "#03C103"
        self.__CND_EQU_COLOR = "#FFFF00"
        self.__BG_COLOR = "#2E2E2E"  # Background color
        self.__DT_FMT = "%Y-%m-%dT%H:%M:00.000000000Z"
        self.__WIDE_SCALE = 0.2
        self.__YRANGE_MARGIN = 0.1

        self.__CH_COLOR = "#FFFF00"  # Crosshair line color

        self.__yrng = [0, 0]  # [min, max]
        self.__glyinc = CandleGlyph(self.__CND_INC_COLOR)
        self.__glydec = CandleGlyph(self.__CND_DEC_COLOR)
        self.__glyequ = CandleGlyph(self.__CND_EQU_COLOR)

        self.__glyord = OrdersVbarGlyph(self.__CND_EQU_COLOR)

        self.__api = API(access_token=oa.ACCESS_TOKEN,
                         environment=OandaEnv.PRACTICE)

        tools_ = ToolType.gen_str(ToolType.WHEEL_ZOOM,
                                  ToolType.XBOX_ZOOM,
                                  ToolType.RESET,
                                  ToolType.SAVE)

        # Main chart figure
        self.__plt_main = figure(
            plot_height=400,
            x_axis_type=AxisTyp.X_DATETIME,
            tools=tools_,
            background_fill_color=self.__BG_COLOR,
            title="Candlestick Chart"
        )
        self.__plt_main.xaxis.major_label_orientation = pi / 4
        self.__plt_main.grid.grid_line_alpha = 0.3
        self.__plt_main.x_range = Range1d()

        # Range chart figure
        self.__plt_rang = figure(
            plot_height=70,
            plot_width=self.__plt_main.plot_width,
            y_range=self.__plt_main.y_range,
            x_axis_type=AxisTyp.X_DATETIME,
            background_fill_color=self.__BG_COLOR,
            toolbar_location=None,
        )
        self.__plt_rang.yaxis.visible = False
        self.__plt_rang.ygrid.visible = False
        self.__plt_rang.xgrid.visible = False

        self.__range_tool = RangeTool()
        self.__plt_rang.add_tools(self.__range_tool)
        self.__plt_rang.toolbar.active_multi = self.__range_tool
        self.__plt_rang.xaxis.major_label_orientation = pi / 4
        self.__plt_rang.grid.grid_line_alpha = 0.3

        hover = HoverTool()
        hover.formatters = {CandleGlyph.XDT: "datetime"}
        hover.tooltips = [(_TIME, "@" + CandleGlyph.XDT + "{%F}"),
                          (_HIGH, "@" + CandleGlyph.YHI),
                          (_OPEN, "@" + CandleGlyph.YOP),
                          (_CLOSE, "@" + CandleGlyph.YCL),
                          (_LOW, "@" + CandleGlyph.YLO)]
        self.__plt_main.add_tools(hover)

        ch = CrosshairTool()
        ch.dimensions = "height"
        ch.line_color = self.__CH_COLOR
        ch.line_alpha = 0.7
        self.__plt_main.add_tools(ch)

    @retry(stop_max_attempt_number=5, wait_fixed=500)
    def fetch(self, gran, inst, dt_from, dt_to):
        """"ローソク足情報を取得する[fetch candles]
        引数[Args]:
            gran (str) : ローソク足の時間足[granularity of a candlestick]
            inst (str) : 通貨ペア[instrument]
            dt_from (datetime) : 開始日時[from date]
            dt_to (datetime) : 終了日時[to date]
        戻り値[Returns]:
            yrng (tuple) : Y軸の最小値、最大値 (min, max)
                           [Y range min and max]
        """
        params_ = {
            # "alignmentTimezone": "Japan",
            "from": dt_from.strftime(self.__DT_FMT),
            "to": dt_to.strftime(self.__DT_FMT),
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
        df.columns = [_TIME,
                      _VOLUME,
                      _OPEN,
                      _HIGH,
                      _LOW,
                      _CLOSE]
        df = df.set_index(_TIME)
        # date型を整形する
        df.index = pd.to_datetime(df.index)

        incflg = df[_CLOSE] > df[_OPEN]
        decflg = df[_OPEN] > df[_CLOSE]
        equflg = df[_CLOSE] == df[_OPEN]

        self.__glyinc.set_data(df[incflg], gran)
        self.__glydec.set_data(df[decflg], gran)
        self.__glyequ.set_data(df[equflg], gran)

        self.__glyinc.add_plot(self.__plt_main)
        self.__glydec.add_plot(self.__plt_main)
        self.__glyequ.add_plot(self.__plt_main)

        self.__glyinc.add_plot(self.__plt_rang)
        self.__glydec.add_plot(self.__plt_rang)
        self.__glyequ.add_plot(self.__plt_rang)

        len_ = int(len(df) * self.__WIDE_SCALE)
        self.__plt_main.x_range.update(
            start=df.index[-len_], end=OandaGrn.offset(df.index[-1], gran))

        self.__range_tool.x_range = self.__plt_main.x_range

        min_ = df[_LOW].min()
        max_ = df[_HIGH].max()
        mar = self.__YRANGE_MARGIN * (max_ - min_)
        str_ = min_ - mar
        end_ = max_ + mar
        self.__plt_main.y_range.update(start=str_, end=end_)
        yrng = (str_, end_)
        self.__yrng = [str_, end_]

        self.add_orders_vline(gran, dt_from, dt_to)

        return yrng

    def add_orders_vline(self, gran, dt_from, dt_to):

        hour_ = dt_from.hour
        minute_ = dt_from.minute
        if gran == OandaGrn.D:
            freq_ = pd.offsets.Day(1)
            hour_ = 0
            minute_ = 0
        elif gran == OandaGrn.H12:
            freq_ = pd.offsets.Hour(12)
            minute_ = 0
        elif gran == OandaGrn.H8:
            freq_ = pd.offsets.Hour(8)
            minute_ = 0
        elif gran == OandaGrn.H6:
            freq_ = pd.offsets.Hour(6)
            minute_ = 0
        elif gran == OandaGrn.H4:
            freq_ = pd.offsets.Hour(4)
            minute_ = 0
        elif gran == OandaGrn.H3:
            freq_ = pd.offsets.Hour(3)
            minute_ = 0
        elif gran == OandaGrn.H2:
            freq_ = pd.offsets.Hour(2)
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

        print("=================1")
        print(freq_)
        print("=================2")
        print(freq_/2)
        print("=================3")

        str_ = datetime(dt_from.year, dt_from.month,
                        dt_from.day, hour_, minute_)
        end_ = dt_to + timedelta(hours=9)
        """
        self.__dtlist = pd.date_range(
            start=str_, end=end_, freq=freq_).to_pydatetime()
        """
        dtlist = pd.date_range(start=str_, end=end_, freq=freq_).to_pydatetime()
        ofslist = dtlist + freq_/2
        #self.__dtdf = pd.DataFrame(dtlist).astype('int64') // 10**9

        self.__orddf = pd.DataFrame({'point': dtlist,
                                     'thresh': ofslist})
        print(self.__orddf)

        """
        data = {OrdersVbarGlyph.XDT: self.__dtlist,
                OrdersVbarGlyph.YBT: self.__yrng[0],
                OrdersVbarGlyph.YTP: self.__yrng[1],
                }
        df = pd.DataFrame(data)
        df = df.set_index(OrdersVbarGlyph.XDT)
        self.__glyord.set_data(df, gran)
        self.__glyord.add_plot(self.__plt_main)
        """

    def get_draw_vline(self, point_):
        print("--------------------1")
        print(point_)
        print("--------------------2")
        aaaa = self.__orddf["thresh"] > point_
        # aaaa = self.__orddf["point"]
        print(aaaa)

        #aaaa = self.__orddf.loc[self.__orddf["thresh"] > point_, 'point']
        #print(aaaa.astype('int64') // 10**9)
        print("--------------------3")


    def get_widget(self):
        """"ウィジェットを取得する[get widget]
        引数[Args]:
            None
        戻り値[Returns]:
            self.__plt_main (figure) : メインfigure[main figure]
            self.__plt_rang (figure) : レンジfigure[range figure]
        """
        return self.__plt_main, self.__plt_rang
