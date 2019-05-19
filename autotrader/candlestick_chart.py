from math import pi
from bokeh.models import Range1d, RangeTool, ColumnDataSource
from bokeh.models import HoverTool, CrosshairTool
from bokeh.plotting import figure
from bokeh.models.glyphs import Segment, VBar
from oandapyV20 import API
from retrying import retry
import datetime as dt
import oandapyV20.endpoints.instruments as it
import pandas as pd
import numpy as np
import autotrader.bokeh_common as bc
import autotrader.oanda_common as oc
import autotrader.oanda_account as oa


# Pandas data label
_TIME = "time"
_VOLUME = "volume"
_OPEN = "open"
_HIGH = "high"
_LOW = "low"
_CLOSE = "close"


class CandleGlyph(object):
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
        self.__glvbar.width = self.__get_width(gran)

    def add_plot(self, plt):
        """"プロットを追加する[add plot]
        引数[Args]:
            plt (figure) : bokehのfigureクラス[class of bokeh's figure]
        戻り値[Returns]:
            None
        """
        plt.add_glyph(self.__src, self.__glyseg)
        plt.add_glyph(self.__src, self.__glvbar)

    def __get_width(self, gran):
        """"ローソク足の幅を取得する[get candlestick width]
        引数[Args]:
            gran (str) : ローソク足の時間足[granularity of a candlestick]
        戻り値[Returns]:
            _width (int) : ローソク足の幅[candlestick width]
        """
        _width = 1
        if gran == oc.OandaGrn.D:
            _width = 24 * 60 * 60 * 1000
        elif gran == oc.OandaGrn.H12:
            _width = 12 * 60 * 60 * 1000
        elif gran == oc.OandaGrn.H8:
            _width = 8 * 60 * 60 * 1000
        elif gran == oc.OandaGrn.H6:
            _width = 6 * 60 * 60 * 1000
        elif gran == oc.OandaGrn.H4:
            _width = 4 * 60 * 60 * 1000
        elif gran == oc.OandaGrn.H3:
            _width = 3 * 60 * 60 * 1000
        elif gran == oc.OandaGrn.H2:
            _width = 2 * 60 * 60 * 1000
        elif gran == oc.OandaGrn.H1:
            _width = 1 * 60 * 60 * 1000
        elif gran == oc.OandaGrn.M30:
            _width = 30 * 60 * 1000
        elif gran == oc.OandaGrn.M15:
            _width = 15 * 60 * 1000
        elif gran == oc.OandaGrn.M10:
            _width = 10 * 60 * 1000
        elif gran == oc.OandaGrn.M5:
            _width = 5 * 60 * 1000
        elif gran == oc.OandaGrn.M4:
            _width = 4 * 60 * 1000
        elif gran == oc.OandaGrn.M3:
            _width = 3 * 60 * 1000
        elif gran == oc.OandaGrn.M2:
            _width = 2 * 60 * 1000
        elif gran == oc.OandaGrn.M1:
            _width = 1 * 60 * 1000

        _width = _width * self.__WIDE_SCALE
        return _width


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

        self.__glyinc = CandleGlyph(self.__CND_INC_COLOR)
        self.__glydec = CandleGlyph(self.__CND_DEC_COLOR)
        self.__glyequ = CandleGlyph(self.__CND_EQU_COLOR)

        self.__api = API(access_token=oa.ACCESS_TOKEN,
                         environment=oc.OandaEnv.PRACTICE)

        tools_ = bc.ToolType.gen_str(bc.ToolType.WHEEL_ZOOM,
                                     bc.ToolType.XBOX_ZOOM,
                                     bc.ToolType.RESET,
                                     bc.ToolType.SAVE)

        # Main chart figure
        self.__plt_main = figure(
            plot_height=400,
            x_axis_type=bc.AxisTyp.X_DATETIME,
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
            x_axis_type=bc.AxisTyp.X_DATETIME,
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
        for raw in ic.response[oc.OandaRsp.CNDL]:
            dt_ = oc.OandaGrn.convert_dtfmt(gran, raw[oc.OandaRsp.TIME],
                                            dt_ofs=dt.timedelta(hours=9),
                                            fmt=self.__DT_FMT)
            data.append([dt_,
                         raw[oc.OandaRsp.VLM],
                         float(raw[oc.OandaRsp.MID][oc.OandaRsp.OPN]),
                         float(raw[oc.OandaRsp.MID][oc.OandaRsp.HIG]),
                         float(raw[oc.OandaRsp.MID][oc.OandaRsp.LOW]),
                         float(raw[oc.OandaRsp.MID][oc.OandaRsp.CLS])
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
            start=df.index[-len_], end=oc.OandaGrn.offset(df.index[-1], gran))

        self.__range_tool.x_range = self.__plt_main.x_range

        min_ = df[_LOW].min()
        max_ = df[_HIGH].max()
        mar = self.__YRANGE_MARGIN * (max_ - min_)
        str_ = min_ - mar
        end_ = max_ + mar
        self.__plt_main.y_range.update(start=str_, end=end_)
        yrng = (str_, end_)

        return yrng

    """
    def __add_orders_vline(self, gran, dt_from, dt_to):

        if gran == oc.OandaGrn.D:
            dlt = dt.datetime(day=1)
        elif gran == oc.OandaGrn.H12:
            dlt = dt.datetime(hour=12)
        elif gran == oc.OandaGrn.H8:
            dlt = dt.datetime(hour=8)
        elif gran == oc.OandaGrn.H6:
            dlt = dt.datetime(hour=6)
        elif gran == oc.OandaGrn.H4:
            dlt = dt.datetime(hour=4)
        elif gran == oc.OandaGrn.H3:
            dlt = dt.datetime(hour=3)
        elif gran == oc.OandaGrn.H2:
            dlt = dt.datetime(hour=2)
        elif gran == oc.OandaGrn.H1 or \
                gran == oc.OandaGrn.M30 or \
                gran == oc.OandaGrn.M15:
            dlt = dt.datetime(hour=1)
        elif gran == oc.OandaGrn.M10 or \
                gran == oc.OandaGrn.M5 or \
                gran == oc.OandaGrn.M4 or \
                gran == oc.OandaGrn.M3 or \
                gran == oc.OandaGrn.M2 or \
                gran == oc.OandaGrn.M1:
            dlt = dt.datetime(minute=20)
        else:
            dlt = dt.datetime(day=1)

        x = np.linspace(start=dt_from, stop=dt_to, dtype=)

        start = pd.Timestamp('2015-07-01')
        end = pd.Timestamp('2015-08-01')
        t = np.linspace(start.value, end.value, 100)
        t = pd.to_datetime(t)
    """

    def get_widget(self):
        """"ウィジェットを取得する[get widget]
        引数[Args]:
            None
        戻り値[Returns]:
            self.__plt_main (figure) : メインfigure[main figure]
            self.__plt_rang (figure) : レンジfigure[range figure]
        """
        return self.__plt_main, self.__plt_rang

    def __change_dt_fmt(self, gran, date_):
        """"日付フォーマットを変換する[change datetime format]
        引数[Args]:
            gran (str) : ローソク足の時間足[granularity of a candlestick]
            date_ (str) : DT_FMT形式でフォーマットされた日付
                         [datetime of formatted "DT_FMT" type]
        戻り値[Returns]:
            tf_dt (str) : 変換後の日付[changed datetime]
        """
        hour_ = 0
        minute_ = 0
        tdt = dt.datetime.strptime(date_, self.__DT_FMT)
        if gran == oc.OandaGrn.D:
            pass
        elif gran == oc.OandaGrn.H12:
            hour_ = 12 * (tdt.hour // 12)
        elif gran == oc.OandaGrn.H8:
            hour_ = 8 * (tdt.hour // 8)
        elif gran == oc.OandaGrn.H6:
            hour_ = 6 * (tdt.hour // 6)
        elif gran == oc.OandaGrn.H4:
            hour_ = 4 * (tdt.hour // 4)
        elif gran == oc.OandaGrn.H3:
            hour_ = 3 * (tdt.hour // 3)
        elif gran == oc.OandaGrn.H2:
            hour_ = 2 * (tdt.hour // 2)
        elif gran == oc.OandaGrn.H1:
            hour_ = 1 * (tdt.hour // 1)
        elif gran == oc.OandaGrn.M30:
            hour_ = tdt.hour
            minute_ = 30 * (tdt.minute // 30)
        elif gran == oc.OandaGrn.M15:
            hour_ = tdt.hour
            minute_ = 15 * (tdt.minute // 15)
        elif gran == oc.OandaGrn.M10:
            hour_ = tdt.hour
            minute_ = 10 * (tdt.minute // 10)
        elif gran == oc.OandaGrn.M5:
            hour_ = tdt.hour
            minute_ = 5 * (tdt.minute // 5)
        elif gran == oc.OandaGrn.M4:
            hour_ = tdt.hour
            minute_ = 4 * (tdt.minute // 4)
        elif gran == oc.OandaGrn.M3:
            hour_ = tdt.hour
            minute_ = 3 * (tdt.minute // 3)
        elif gran == oc.OandaGrn.M2:
            hour_ = tdt.hour
            minute_ = 2 * (tdt.minute // 2)
        elif gran == oc.OandaGrn.M1:
            hour_ = tdt.hour
            minute_ = 1 * (tdt.minute // 1)

        tf_dt = dt.datetime(tdt.year, tdt.month, tdt.day, hour_, minute_)

        return tf_dt
