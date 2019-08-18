from bokeh.models import Range1d, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.models.glyphs import Segment, VBar
from oandapyV20 import API
from retrying import retry
import datetime
from autotrader.bokeh_common import GlyphVbarAbs, ToolType, AxisTyp
from autotrader.oanda_common import OandaEnv, OandaRsp, OandaGrn
import oandapyV20.endpoints.instruments as it
import pandas as pd
from autotrader.oanda_account import ACCESS_TOKEN
from oandapyV20.exceptions import V20Error


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

    def __init__(self, fig, color_):
        """"コンストラクタ[Constructor]
        引数[Args]:
            fig (figure) : フィギュアオブジェクト[figure object]
            color_ (str) : カラーコード[Color code(ex "#E73B3A")]
        """
        self.__WIDE_SCALE = 0.8
        self.__COLOR = color_

        super().__init__(self.__WIDE_SCALE)

        self.__src = ColumnDataSource({CandleGlyph.XDT: [],
                                       CandleGlyph.YHI: [],
                                       CandleGlyph.YLO: [],
                                       CandleGlyph.YOP: [],
                                       CandleGlyph.YCL: []})

        self.__glyseg = Segment(x0=CandleGlyph.XDT,
                                y0=CandleGlyph.YLO,
                                x1=CandleGlyph.XDT,
                                y1=CandleGlyph.YHI,
                                line_color="white",
                                line_width=2)
        self.__glvbar = VBar(x=CandleGlyph.XDT,
                             top=CandleGlyph.YOP,
                             bottom=CandleGlyph.YCL,
                             fill_color=self.__COLOR,
                             line_width=0,
                             line_color=self.__COLOR)

        self._fig = fig
        self.__ren = self._fig.add_glyph(self.__src, self.__glyseg)
        self._fig.add_glyph(self.__src, self.__glvbar)

    @property
    def render(self):
        """"メインフィギュアのGlyphRendererオブジェクトを取得する
            [get GlyphRenderer Object of Main Figure]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            GlyphRenderer Object
        """
        return self.__ren

    def update(self, df, gran):
        """"データを設定する[set glyph date]
        引数[Args]:
            df (pandas data frame) : pandasデータフレーム[pandas data frame]
            gran (str) : ローソク足の時間足[granularity of a candlestick]
        戻り値[Returns]:
            なし[None]
        """
        self.__src.data = {
            CandleGlyph.XDT: df.index.tolist(),
            CandleGlyph.YHI: df[LBL_HIGH].tolist(),
            CandleGlyph.YLO: df[LBL_LOW].tolist(),
            CandleGlyph.YOP: df[LBL_OPEN].tolist(),
            CandleGlyph.YCL: df[LBL_CLOSE].tolist()
        }

        self.__glvbar.width = self.get_width(gran)


class CandleStickChartBase(object):
    """ CandleStickChartBase
            - ローソク足チャート定義基準クラス[Candle stick chart definition base class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        self.__CND_INC_COLOR = "#E73B3A"
        self.__CND_DEC_COLOR = "#03C103"
        self.__CND_EQU_COLOR = "#FFFF00"
        self.__BG_COLOR = "#2E2E2E"  # Background color
        self.__DT_FMT = "%Y-%m-%dT%H:%M:00.000000000Z"
        self.__YRANGE_MARGIN = 0.1

        tools_ = ToolType.gen_str(ToolType.WHEEL_ZOOM,
                                  ToolType.XBOX_ZOOM,
                                  ToolType.RESET,
                                  ToolType.SAVE)

        # Main chart figure
        self._fig = figure(plot_height=400,
                           x_axis_type=AxisTyp.X_DATETIME,
                           tools=tools_,
                           background_fill_color=self.__BG_COLOR,
                           sizing_mode="stretch_width",
                           title="Candlestick Chart")
        self._fig.xaxis.axis_label = "Date Time"
        self._fig.grid.grid_line_alpha = 0.3
        self._fig.x_range = Range1d()
        self._fig.y_range = Range1d()
        self._fig.toolbar_location = None

        # Candle stick figure
        self.__glyinc = CandleGlyph(self._fig,
                                    self.__CND_INC_COLOR)
        self.__glydec = CandleGlyph(self._fig,
                                    self.__CND_DEC_COLOR)
        self.__glyequ = CandleGlyph(self._fig,
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
        self._fig.add_tools(hover)

    def set_dataframe(self, csd):
        """"ローソク足情報を取得する[fetch candles]
        引数[Args]:
            csd (object) : CandleStickDataオブジェクト[CandleStickData objecrt]
        戻り値[Returns]:
            yrng (tuple) : Y軸の最小値、最大値 (min, max)
                           [Y range min and max]
        """
        df = csd.df
        gran = csd.granularity

        incflg = df[LBL_CLOSE] > df[LBL_OPEN]
        decflg = df[LBL_OPEN] > df[LBL_CLOSE]
        equflg = df[LBL_CLOSE] == df[LBL_OPEN]

        self.__glyinc.update(df[incflg], gran)
        self.__glydec.update(df[decflg], gran)
        self.__glyequ.update(df[equflg], gran)

        # update x axis ange
        min_ = df.index[0]
        max_ = df.index[-1]
        str_ = min_
        end_ = max_
        self._fig.x_range.update(start=str_, end=end_)

        # update y axis ange
        min_ = df[LBL_LOW].min()
        max_ = df[LBL_HIGH].max()
        mar = self.__YRANGE_MARGIN * (max_ - min_)
        str_ = min_ - mar
        end_ = max_ + mar
        self._fig.y_range.update(start=str_, end=end_)

    def get_model(self):
        """モデルを取得する[get model]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            self._fig (object) : model object
        """
        return self._fig


class CandleStickData(object):

    _api = API(access_token=ACCESS_TOKEN, environment=OandaEnv.PRACTICE)

    def __init__(self, gran, inst, dtmstr, dtmend):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        df = self.__fetch_ohlc(gran, inst, dtmstr, dtmend)

        self.__df = df
        self.__gran = gran

    @retry(stop_max_attempt_number=5, wait_fixed=500)
    def __fetch_ohlc(self, gran, inst, gmtstr, gmtend):
        """"ローソク足情報を取得する[fetch ohlc]
        引数[Args]:
            gran (str) : ローソク足の時間足[granularity of a candlestick]
            inst (str) : 通貨ペア[instrument]
            gmtstr (DateTimeManager) : 開始日時[from date]
            gmtend (DateTimeManager) : 終了日時[to date]
        戻り値[Returns]:
            yrng (tuple) : Y軸の最小値、最大値 (min, max)
                           [Y range min and max]
        """
        DT_FMT = "%Y-%m-%dT%H:%M:00.000000000Z"

        params_ = {
            # "alignmentTimezone": "Japan",
            "from": gmtstr.gmt.strftime(DT_FMT),
            "to": gmtend.gmt.strftime(DT_FMT),
            "granularity": gran
        }

        # APIへ過去データをリクエスト
        ic = it.InstrumentsCandles(instrument=inst, params=params_)
        try:
            CandleStickData._api.request(ic)
        except V20Error as v20err:
            raise v20err
        except ConnectionError as cerr:
            raise cerr
        except Exception as err:
            raise err

        data = []
        for raw in ic.response[OandaRsp.CNDL]:
            dt_ = OandaGrn.convert_dtfmt(gran, raw[OandaRsp.TIME],
                                         dt_ofs=datetime.timedelta(hours=9),
                                         fmt=DT_FMT)
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

        return df

    @property
    def df(self):
        """ローソク足の時間足を取得する[get overall layout]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            self.__df (object) : ローソク足のデータフレーム[Data frame of a candlestick]
        """
        return self.__df

    @property
    def granularity(self):
        """ローソク足の時間足を取得する[get overall layout]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            self.__gran (str) : ローソク足の時間足[Granularity of a candlestick]
        """
        return self.__gran
