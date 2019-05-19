from math import pi
from bokeh.models import Range1d, RangeTool, ColumnDataSource
from bokeh.models import HoverTool, CrosshairTool
from bokeh.plotting import figure
from bokeh.models.glyphs import Segment, VBar
from oandapyV20 import API
from retrying import retry
from bokeh.io.showing import show
from autotrader.bokeh_common import GlyphVbarAbs
from autotrader.oanda_common import OandaEnv, OandaRsp, OandaGrn
from autotrader.bokeh_common import ToolType, AxisTyp
import datetime as dt
import oandapyV20.endpoints.instruments as it
import pandas as pd
import numpy as np
import autotrader.oanda_account as oa


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
        print(self.__glvbar.width)

    def add_plot(self, plt):
        """"プロットを追加する[add plot]
        引数[Args]:
            plt (figure) : bokehのfigureクラス[class of bokeh's figure]
        戻り値[Returns]:
            None
        """
        plt.add_glyph(self.__src, self.__glyseg)
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

        self.__glyinc = CandleGlyph(self.__CND_INC_COLOR)
        self.__glydec = CandleGlyph(self.__CND_DEC_COLOR)
        self.__glyequ = CandleGlyph(self.__CND_EQU_COLOR)

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
                                         dt_ofs=dt.timedelta(hours=9),
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

        return yrng

    def add_orders_vline(self, gran, dt_from, dt_to):

        if gran == OandaGrn.D:
            freq_ = pd.offsets.Day(1)
        elif gran == OandaGrn.H12:
            freq_ = pd.offsets.Hour(12)
        elif gran == OandaGrn.H8:
            freq_ = pd.offsets.Hour(8)
        elif gran == OandaGrn.H6:
            freq_ = pd.offsets.Hour(6)
        elif gran == OandaGrn.H4:
            freq_ = pd.offsets.Hour(4)
        elif gran == OandaGrn.H3:
            freq_ = pd.offsets.Hour(3)
        elif gran == OandaGrn.H2:
            freq_ = pd.offsets.Hour(2)
        elif gran == OandaGrn.H1 or \
                gran == OandaGrn.M30 or \
                gran == OandaGrn.M15:
            freq_ = pd.offsets.Hour(1)
        elif gran == OandaGrn.M10 or \
                gran == OandaGrn.M5 or \
                gran == OandaGrn.M4 or \
                gran == OandaGrn.M3 or \
                gran == OandaGrn.M2 or \
                gran == OandaGrn.M1:
            freq_ = pd.offsets.Minute(20)
        else:
            freq_ = pd.offsets.Minute(20)

        dtlist = pd.date_range(start=dt_from, end=dt_to, freq=freq_)
        print(dtlist)
        return dtlist

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
        if gran == OandaGrn.D:
            pass
        elif gran == OandaGrn.H12:
            hour_ = 12 * (tdt.hour // 12)
        elif gran == OandaGrn.H8:
            hour_ = 8 * (tdt.hour // 8)
        elif gran == OandaGrn.H6:
            hour_ = 6 * (tdt.hour // 6)
        elif gran == OandaGrn.H4:
            hour_ = 4 * (tdt.hour // 4)
        elif gran == OandaGrn.H3:
            hour_ = 3 * (tdt.hour // 3)
        elif gran == OandaGrn.H2:
            hour_ = 2 * (tdt.hour // 2)
        elif gran == OandaGrn.H1:
            hour_ = 1 * (tdt.hour // 1)
        elif gran == OandaGrn.M30:
            hour_ = tdt.hour
            minute_ = 30 * (tdt.minute // 30)
        elif gran == OandaGrn.M15:
            hour_ = tdt.hour
            minute_ = 15 * (tdt.minute // 15)
        elif gran == OandaGrn.M10:
            hour_ = tdt.hour
            minute_ = 10 * (tdt.minute // 10)
        elif gran == OandaGrn.M5:
            hour_ = tdt.hour
            minute_ = 5 * (tdt.minute // 5)
        elif gran == OandaGrn.M4:
            hour_ = tdt.hour
            minute_ = 4 * (tdt.minute // 4)
        elif gran == OandaGrn.M3:
            hour_ = tdt.hour
            minute_ = 3 * (tdt.minute // 3)
        elif gran == OandaGrn.M2:
            hour_ = tdt.hour
            minute_ = 2 * (tdt.minute // 2)
        elif gran == OandaGrn.M1:
            hour_ = tdt.hour
            minute_ = 1 * (tdt.minute // 1)

        tf_dt = dt.datetime(tdt.year, tdt.month, tdt.day, hour_, minute_)

        return tf_dt


if __name__ == "__main__":
    from bokeh.models.glyphs import Line
    from bokeh.models import Span
#    import holoviews as hv

    __BG_COLOR = "#2E2E2E"  # Background color

    cs = CandleStick()

    gran = OandaGrn.D
    dt_from = dt.datetime(year=2019, month=1, day=1,
                          hour=0, minute=0, second=0)
    dt_to = dt.datetime(year=2019, month=2, day=1, hour=12, minute=0, second=0)

    dtlist = cs.add_orders_vline(gran, dt_from, dt_to)

    plot = figure(
        plot_height=400,
        x_axis_type=AxisTyp.X_DATETIME,
        background_fill_color=__BG_COLOR,
        title="Candlestick Chart"
    )
    plot.xaxis.major_label_orientation = pi / 4
    plot.grid.grid_line_alpha = 0.3

    x = dtlist
    y = np.linspace(start=0, stop=dtlist.shape[0], num=dtlist.shape[0])

    src = ColumnDataSource(dict(x=x, y=y))
    print(src)

    gly = Line(x="x", y="y", line_color="#f46d43",
               line_width=6, line_alpha=0.6)

    plot.add_glyph(src, gly)

    vline = Span(location=(dtlist[0], dtlist[1]),
                 dimension='height', line_color='green',
                 line_dash='dashed', line_width=3)

    plot.add_layout(vline)

    show(plot)
