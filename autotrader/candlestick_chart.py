from math import pi
from bokeh.layouts import column
from bokeh.models import RangeTool, ColumnDataSource
from bokeh.plotting import figure, output_file
from oandapyV20 import API
from bokeh.models.glyphs import Segment, VBar
import datetime
import oandapyV20.endpoints.instruments as inst
import pandas as pd
import autotrader.bokeh_common as bc
import autotrader.oanda_common as oc
import autotrader.oanda_account as oa


class CandleStick(object):
    """ CandleStick
            - ローソク足定義クラス[Candle stick definition class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            granularity (str): 時間足[Candle stick granularity]
        """
        # Pandas data label
        self.__TIME = "time"
        self.__VOLUME = "volume"
        self.__OPEN = "open"
        self.__HIGH = "high"
        self.__LOW = "low"
        self.__CLOSE = "close"

        self.__WIDE = 12 * 60 * 60 * 1000  # half day in ms
        self.__WIDE_SCALE = 0.2

        self.__CND_INC_COLOR = "#E73B3A"
        self.__CND_DEC_COLOR = "#03C103"
        self.__CND_EQU_COLOR = "#FFFF00"
        self.__BG_COLOR = "#2E2E2E"  # Background color
        self.__DT_FMT = "%Y-%m-%dT%H:%M:00.000000000Z"

        self.__incsrc = ColumnDataSource(
            dict(xdt=[], yhi=[], ylo=[], yop=[], ycl=[]))
        self.__decsrc = ColumnDataSource(
            dict(xdt=[], yhi=[], ylo=[], yop=[], ycl=[]))
        self.__equsrc = ColumnDataSource(
            dict(xdt=[], yhi=[], ylo=[], yop=[], ycl=[]))

        self.__api = API(access_token=oa.ACCESS_TOKEN,
                         environment=oc.OandaEnv.PRACTICE)

    def fetch(self, gran_, inst_, dt_from, dt_to):
        print("===== called fetch =====")

        params_ = {
            "alignmentTimezone": "Japan",
            "from": dt_from.strftime(self.__DT_FMT),
            "to": dt_to.strftime(self.__DT_FMT),
            "granularity": gran_
        }

        # APIへ過去データをリクエスト
        ic = inst.InstrumentsCandles(instrument=inst_, params=params_)
        self.__api.request(ic)

        data = []
        for raw in ic.response[oc.OandaRsp.CNDL]:
            data.append([self.__change_dt_fmt(gran_, raw[oc.OandaRsp.TIME]),
                         raw[oc.OandaRsp.VLM],
                         raw[oc.OandaRsp.MID][oc.OandaRsp.OPN],
                         raw[oc.OandaRsp.MID][oc.OandaRsp.HIG],
                         raw[oc.OandaRsp.MID][oc.OandaRsp.LOW],
                         raw[oc.OandaRsp.MID][oc.OandaRsp.CLS]])

        # convert List to pandas data frame
        df = pd.DataFrame(data)
        df.columns = [self.__TIME,
                      self.__VOLUME,
                      self.__OPEN,
                      self.__HIGH,
                      self.__LOW,
                      self.__CLOSE]
        df = df.set_index(self.__TIME)
        # date型を整形する
        df.index = pd.to_datetime(df.index)

        inc_df = df[self.__CLOSE] > df[self.__OPEN]
        dec_df = df[self.__OPEN] > df[self.__CLOSE]
        equ_df = df[self.__CLOSE] == df[self.__OPEN]

        self.__incsrc.data = self.__df2datsrc(df[inc_df])
        self.__decsrc.data = self.__df2datsrc(df[dec_df])
        self.__equsrc.data = self.__df2datsrc(df[equ_df])
        #self.__src.stream(new_)

    def __df2datsrc(self, df):
        new_ = dict(
            xdt=df.index.tolist(),
            ylo=df[self.__LOW].astype(float).values.tolist(),
            yhi=df[self.__HIGH].astype(float).values.tolist(),
            yop=df[self.__OPEN].astype(float).values.tolist(),
            ycl=df[self.__CLOSE].astype(float).values.tolist(),
        )
        return new_

    def get_widget(self, fig_width=1000):

        set_tools = bc.ToolType.gen_str(bc.ToolType.XPAN,
                                        bc.ToolType.WHEEL_ZOOM,
                                        bc.ToolType.BOX_ZOOM,
                                        bc.ToolType.RESET,
                                        bc.ToolType.SAVE)

        plt_main = figure(
            plot_height=400,
            plot_width=fig_width,
            x_axis_type=bc.AxisTyp.X_DATETIME,
            tools=set_tools,
            background_fill_color=self.__BG_COLOR,
            title="Candlestick example"
        )

        self.__add_candle(plt_main, self.__incsrc, self.__CND_INC_COLOR)
        self.__add_candle(plt_main, self.__decsrc, self.__CND_DEC_COLOR)
        self.__add_candle(plt_main, self.__equsrc, self.__CND_EQU_COLOR)

        plt_main.xaxis.major_label_orientation = pi / 4
        plt_main.grid.grid_line_alpha = 0.3
        return plt_main

    def __add_candle(self, plt, src, color):
        glyph = Segment(x0="xdt", y0="ylo", x1="xdt", y1="yhi",
                        line_color=color, line_width=1)
        plt.add_glyph(src, glyph)
        glyph = VBar(x="xdt", top="yop", bottom="ycl",
                     width=self.__WIDE, fill_color=color,
                     line_width=0, line_color=color)
        plt.add_glyph(src, glyph)

    def __change_dt_fmt(self, granularity, dt):
        """"日付フォーマットの変換メソッド
        引数:
            dt (str): DT_FMT形式でフォーマットされた日付
        戻り値:
            tf_dt (str): 変換後の日付
        """
        if granularity is oc.OandaGrn.D:
            tdt = datetime.datetime.strptime(dt, self.__DT_FMT)
            tf_dt = datetime.date(tdt.year, tdt.month, tdt.day)

        return tf_dt
