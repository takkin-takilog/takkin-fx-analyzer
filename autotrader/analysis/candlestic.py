from bokeh.models import Range1d, RangeTool, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.models.glyphs import Segment, VBar, Line
from oandapyV20 import API
from retrying import retry
from datetime import datetime, timedelta
from autotrader.bokeh_common import GlyphVbarAbs, ToolType, AxisTyp
from autotrader.oanda_common import OandaEnv, OandaRsp, OandaGrn
from autotrader.utils import DateTimeManager
from autotrader.technical import SimpleMovingAverage, MACD, BollingerBands
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

    _XDT = "xdt"
    _YHI = "yhi"
    _YLO = "ylo"
    _YOP = "yop"
    _YCL = "ycl"

    def __init__(self, fig, color_):
        """"コンストラクタ[Constructor]
        引数[Args]:
            fig (figure) : フィギュアオブジェクト[figure object]
            color_ (str) : カラーコード[Color code(ex "#E73B3A")]
        """
        self.__WIDE_SCALE = 0.8
        self.__COLOR = color_

        super().__init__(self.__WIDE_SCALE)

        self.__src = ColumnDataSource({CandleGlyph._XDT: [],
                                       CandleGlyph._YHI: [],
                                       CandleGlyph._YLO: [],
                                       CandleGlyph._YOP: [],
                                       CandleGlyph._YCL: []})

        self.__glyseg = Segment(x0=CandleGlyph._XDT,
                                y0=CandleGlyph._YLO,
                                x1=CandleGlyph._XDT,
                                y1=CandleGlyph._YHI,
                                line_color="white",
                                line_width=2)
        self.__glvbar = VBar(x=CandleGlyph._XDT,
                             top=CandleGlyph._YOP,
                             bottom=CandleGlyph._YCL,
                             fill_color=self.__COLOR,
                             line_width=0,
                             line_color=self.__COLOR)

        self.__fig = fig
        self.__ren = self.__fig.add_glyph(self.__src, self.__glyseg)
        self.__fig.add_glyph(self.__src, self.__glvbar)

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
            self.XDT: df.index.tolist(),
            self.YHI: df[LBL_HIGH].tolist(),
            self.YLO: df[LBL_LOW].tolist(),
            self.YOP: df[LBL_OPEN].tolist(),
            self.YCL: df[LBL_CLOSE].tolist()
        }

        self.__glvbar.width = self.get_width(gran)
