from math import pi
from bokeh.layouts import Column, column
from bokeh.models import Range1d, RangeTool, ColumnDataSource
from bokeh.plotting import figure, output_file
from bokeh.models.glyphs import Segment, VBar
from oandapyV20 import API
from retrying import retry
import datetime
import oandapyV20.endpoints.instruments as inst
import pandas as pd
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

    def __init__(self, color_):
        self.__WIDE_SCALE = 0.5
        self.__COLOR = color_
        self.__src = ColumnDataSource(
            dict(xdt=[], yhi=[], ylo=[], yop=[], ycl=[])
        )
        self.__glyseg = Segment(x0="xdt", y0="ylo", x1="xdt", y1="yhi",
                                line_color=self.__COLOR,
                                line_width=1)
        self.__glvbar = VBar(x="xdt", top="yop", bottom="ycl",
                             fill_color=self.__COLOR,
                             line_width=0,
                             line_color=self.__COLOR)

    def set_data(self, df, gran):

        self.__src.data = dict(
            xdt=df.index.tolist(),
            ylo=df[_LOW].astype(float).values.tolist(),
            yhi=df[_HIGH].astype(float).values.tolist(),
            yop=df[_OPEN].astype(float).values.tolist(),
            ycl=df[_CLOSE].astype(float).values.tolist(),
        )
        self.__glvbar.width = self.__get_width(gran)

    def add_plot(self, plt):
        plt.add_glyph(self.__src, self.__glyseg)
        plt.add_glyph(self.__src, self.__glvbar)

    def __get_width(self, gran):

        _width = 1
        if gran is oc.OandaGrn.D:
            _width = 24 * 60 * 60 * 1000
        elif gran is oc.OandaGrn.H12:
            _width = 12 * 60 * 60 * 1000
        elif gran is oc.OandaGrn.H8:
            _width = 8 * 60 * 60 * 1000
        elif gran is oc.OandaGrn.H6:
            _width = 6 * 60 * 60 * 1000
        elif gran is oc.OandaGrn.H4:
            _width = 4 * 60 * 60 * 1000
        elif gran is oc.OandaGrn.H3:
            _width = 3 * 60 * 60 * 1000
        elif gran is oc.OandaGrn.H2:
            _width = 2 * 60 * 60 * 1000
        elif gran is oc.OandaGrn.H1:
            _width = 1 * 60 * 60 * 1000
        elif gran is oc.OandaGrn.M30:
            _width = 30 * 60 * 1000
        elif gran is oc.OandaGrn.M15:
            _width = 15 * 60 * 1000
        elif gran is oc.OandaGrn.M10:
            _width = 10 * 60 * 1000
        elif gran is oc.OandaGrn.M5:
            _width = 5 * 60 * 1000
        elif gran is oc.OandaGrn.M4:
            _width = 4 * 60 * 1000
        elif gran is oc.OandaGrn.M3:
            _width = 3 * 60 * 1000
        elif gran is oc.OandaGrn.M2:
            _width = 2 * 60 * 1000
        elif gran is oc.OandaGrn.M1:
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

        self.__glyinc = CandleGlyph(self.__CND_INC_COLOR)
        self.__glydec = CandleGlyph(self.__CND_DEC_COLOR)
        self.__glyequ = CandleGlyph(self.__CND_EQU_COLOR)

        self.__api = API(access_token=oa.ACCESS_TOKEN,
                         environment=oc.OandaEnv.PRACTICE)

        set_tools = bc.ToolType.gen_str(bc.ToolType.WHEEL_ZOOM,
                                        bc.ToolType.XBOX_ZOOM,
                                        bc.ToolType.RESET,
                                        bc.ToolType.SAVE)

        # Main chart figure
        self.__plt_main = figure(
            plot_height=400,
            x_axis_type=bc.AxisTyp.X_DATETIME,
            tools=set_tools,
            # x_range=[self.__mainst, self.__mained],
            background_fill_color=self.__BG_COLOR,
            title="Candlestick Chart"
        )
        self.__plt_main.xaxis.major_label_orientation = pi / 4
        self.__plt_main.grid.grid_line_alpha = 0.3

        # Range chart figure
        self.__plt_rang = figure(
            plot_height=100,
            plot_width=self.__plt_main.plot_width,
            # x_range=[self.__rngst, self.__rnged],
            y_range=self.__plt_main.y_range,
            x_axis_type=bc.AxisTyp.X_DATETIME,
            background_fill_color=self.__BG_COLOR,
            toolbar_location=None,
        )

        self.__plt_rang.xaxis.major_label_orientation = pi / 4
        self.__plt_rang.grid.grid_line_alpha = 0.3

    @retry(stop_max_attempt_number=5, wait_fixed=500)
    def fetch(self, gran, inst_, dt_from, dt_to):

        params_ = {
            # "alignmentTimezone": "Japan",
            "from": dt_from.strftime(self.__DT_FMT),
            "to": dt_to.strftime(self.__DT_FMT),
            "granularity": gran
        }

        # APIへ過去データをリクエスト
        ic = inst.InstrumentsCandles(instrument=inst_, params=params_)
        try:
            self.__api.request(ic)
        except Exception as err:
            raise err

        data = []
        for raw in ic.response[oc.OandaRsp.CNDL]:
            dt_ = oc.OandaGrn.convert_dtfmt(gran, raw[oc.OandaRsp.TIME],
                                            dt_ofs=datetime.timedelta(hours=9),
                                            fmt=self.__DT_FMT)
            data.append([dt_,
                         raw[oc.OandaRsp.VLM],
                         raw[oc.OandaRsp.MID][oc.OandaRsp.OPN],
                         raw[oc.OandaRsp.MID][oc.OandaRsp.HIG],
                         raw[oc.OandaRsp.MID][oc.OandaRsp.LOW],
                         raw[oc.OandaRsp.MID][oc.OandaRsp.CLS]])

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

        len_ = int(len(df) * self.__WIDE_SCALE)
        self.__mainst = df.index[-len_]
        self.__mained = oc.OandaGrn.offset(df.index[-1], gran)

        self.__rngst = df.index[0]
        self.__rnged = self.__mained
        print("mainst = {}" .format(self.__mainst))
        print("mained = {}" .format(self.__mained))
        print("rngst = {}" .format(self.__rngst))
        print("rnged = {}" .format(self.__rnged))

        self.__plt_main.x_range.start = self.__mainst
        self.__plt_main.x_range.end = self.__mained
        self.__plt_rang.x_range.start = self.__rngst
        self.__plt_rang.x_range.end = self.__rnged

    def get_widget(self):

        self.__glyinc.add_plot(self.__plt_main)
        self.__glydec.add_plot(self.__plt_main)
        self.__glyequ.add_plot(self.__plt_main)

        self.__glyinc.add_plot(self.__plt_rang)
        self.__glydec.add_plot(self.__plt_rang)
        self.__glyequ.add_plot(self.__plt_rang)

        # range_tool = RangeTool(x_range=self.__plt_main.x_range)
        range_tool = RangeTool()
        range_tool.x_range = Range1d(self.__mainst, self.__mained)

        self.__plt_rang.add_tools(range_tool)
        self.__plt_rang.toolbar.active_multi = range_tool

        return self.__plt_main, self.__plt_rang

    def __change_dt_fmt(self, granularity, dt):
        """"日付フォーマットの変換メソッド
        引数[Args]:
            granularity (str): 時間足[Candle stick granularity]
            dt (str): DT_FMT形式でフォーマットされた日付
        戻り値[Returns]:
            tf_dt (str): 変換後の日付
        """
        hour_ = 0
        minute_ = 0
        tdt = datetime.datetime.strptime(dt, self.__DT_FMT)
        if granularity is oc.OandaGrn.D:
            pass
        elif granularity is oc.OandaGrn.H12:
            hour_ = 12 * (tdt.hour // 12)
        elif granularity is oc.OandaGrn.H8:
            hour_ = 8 * (tdt.hour // 8)
        elif granularity is oc.OandaGrn.H6:
            hour_ = 6 * (tdt.hour // 6)
        elif granularity is oc.OandaGrn.H4:
            hour_ = 4 * (tdt.hour // 4)
        elif granularity is oc.OandaGrn.H3:
            hour_ = 3 * (tdt.hour // 3)
        elif granularity is oc.OandaGrn.H2:
            hour_ = 2 * (tdt.hour // 2)
        elif granularity is oc.OandaGrn.H1:
            hour_ = 1 * (tdt.hour // 1)
        elif granularity is oc.OandaGrn.M30:
            hour_ = tdt.hour
            minute_ = 30 * (tdt.minute // 30)
        elif granularity is oc.OandaGrn.M15:
            hour_ = tdt.hour
            minute_ = 15 * (tdt.minute // 15)
        elif granularity is oc.OandaGrn.M10:
            hour_ = tdt.hour
            minute_ = 10 * (tdt.minute // 10)
        elif granularity is oc.OandaGrn.M5:
            hour_ = tdt.hour
            minute_ = 5 * (tdt.minute // 5)
        elif granularity is oc.OandaGrn.M4:
            hour_ = tdt.hour
            minute_ = 4 * (tdt.minute // 4)
        elif granularity is oc.OandaGrn.M3:
            hour_ = tdt.hour
            minute_ = 3 * (tdt.minute // 3)
        elif granularity is oc.OandaGrn.M2:
            hour_ = tdt.hour
            minute_ = 2 * (tdt.minute // 2)
        elif granularity is oc.OandaGrn.M1:
            hour_ = tdt.hour
            minute_ = 1 * (tdt.minute // 1)

        tf_dt = datetime.datetime(tdt.year, tdt.month, tdt.day, hour_, minute_)

        return tf_dt
