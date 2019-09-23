from abc import ABCMeta, abstractmethod
import numpy as np
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.models.glyphs import Quad, Line, Image, Rect
from bokeh.plotting import figure
from bokeh.transform import transform
import autotrader.utils as utl
from autotrader.bokeh_common import ToolType


class HeatMap(object):

    IMAGE = "image"
    X = "x"
    Y = "y"
    DW = "dw"
    DH = "dh"

    def __init__(self, title):
        """"コンストラクタ[Constructor]
        引数[Args]:
            fig (figure) : フィギュアオブジェクト[figure object]
            color_ (str) : カラーコード[Color code(ex "#E73B3A")]
        """
        color_mapper = LinearColorMapper(palette="Plasma256", low=0, high=1)

        fig = figure(title=title,
                     tools='',
                     toolbar_location=None)
        fig.x_range.range_padding = 0
        fig.y_range.range_padding = 0

        src = ColumnDataSource({HeatMap.IMAGE: [],
                                HeatMap.X: [],
                                HeatMap.Y: [],
                                HeatMap.DW: [],
                                HeatMap.DH: []})

        glyph = Image(image=HeatMap.IMAGE,
                      x=HeatMap.X,
                      y=HeatMap.Y,
                      dw=HeatMap.DW,
                      dh=HeatMap.DH,
                      color_mapper=color_mapper)

        ren = fig.add_glyph(src, glyph)

        color_bar = ColorBar(color_mapper=color_mapper,
                             label_standoff=12,
                             border_line_color=None,
                             location=(0, 0))
        fig.add_layout(color_bar, 'right')

        self.__fig = fig
        self.__src = src
        self.__glyph = glyph
        self.__ren = ren
        self.__cm = color_mapper

    @property
    def fig(self):
        """モデルを取得する[get model]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            self._fig (object) : model object
        """
        return self.__fig

    def xaxis_label(self, xlabel):
        self.__fig.xaxis.axis_label = xlabel

    def yaxis_label(self, ylabel):
        self.__fig.yaxis.axis_label = ylabel

    def update(self, image, x, y, dw, dh):
        self.__src.data = {
            HeatMap.IMAGE: [image],
            HeatMap.X: [x],
            HeatMap.Y: [y],
            HeatMap.DW: [dw],
            HeatMap.DH: [dh]
        }
        self.__cm.low = image.min()
        self.__cm.high = image.max()

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        dict_ = {HeatMap.IMAGE: [],
                 HeatMap.X: [],
                 HeatMap.Y: [],
                 HeatMap.DW: [],
                 HeatMap.DH: []}
        self.__src.data = dict_


class HeatMap2(object):

    _X = "x"
    _Y = "y"
    _W = "width"
    _H = "height"
    _D = "depth"

    def __init__(self, title):
        """"コンストラクタ[Constructor]
        引数[Args]:
            fig (figure) : フィギュアオブジェクト[figure object]
            color_ (str) : カラーコード[Color code(ex "#E73B3A")]
        """
        mapper = LinearColorMapper(palette="Plasma256", low=0, high=1)
        tools_ = ToolType.gen_str(ToolType.HOVER)

        fig = figure(title=title,
                     tools=tools_,
                     toolbar_location=None)
        fig.x_range.range_padding = 0
        fig.y_range.range_padding = 0

        src = ColumnDataSource({HeatMap2._X: [],
                                HeatMap2._Y: [],
                                HeatMap2._W: [],
                                HeatMap2._H: [],
                                HeatMap2._D: []
                                })
        """
        glyph = Rect(x=HeatMap2.X,
                     y=HeatMap2.Y,
                     width=HeatMap2.W,
                     height=HeatMap2.H,
                     line_color=None,
                     hover_line_color="black",
                     fill_color=transform(HeatMap2.D, mapper)
                     )
        """

        fig.rect(x=HeatMap2._X,
                 y=HeatMap2._Y,
                 width=HeatMap2._W,
                 height=HeatMap2._H,
                 source=src,
                 line_color=None,
                 fill_color=transform(HeatMap2._D, mapper),
                 hover_line_color="black",
                 hover_color=transform(HeatMap2._D, mapper)
                 )


        #ren = fig.add_glyph(src, glyph)

        color_bar = ColorBar(color_mapper=mapper,
                             label_standoff=12,
                             border_line_color=None,
                             location=(0, 0))
        fig.add_layout(color_bar, 'right')

        self.__fig = fig
        self.__src = src
        #self.__glyph = glyph
        #self.__ren = ren
        self.__cm = mapper

    @property
    def fig(self):
        """モデルを取得する[get model]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            self._fig (object) : model object
        """
        return self.__fig

    def xaxis_label(self, xlabel):
        self.__fig.xaxis.axis_label = xlabel

    def yaxis_label(self, ylabel):
        self.__fig.yaxis.axis_label = ylabel

    def update(self, x, y, w, h, d):

        self.__src.data = {HeatMap2._X: x,
                           HeatMap2._Y: y,
                           HeatMap2._W: w,
                           HeatMap2._H: h,
                           HeatMap2._D: d
                           }
        self.__cm.low = d.min()
        self.__cm.high = d.max()

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        dict_ = {HeatMap2._X: [],
                 HeatMap2._Y: [],
                 HeatMap2._W: [],
                 HeatMap2._H: [],
                 HeatMap2._D: []
                 }
        self.__src.data = dict_


class LineGraphAbs(metaclass=ABCMeta):
    """ LineGraphAbs
            - 線グラフ定義抽象クラス[Line graph definition abstract class]
    """

    X = "x"
    Y = "y"

    def __init__(self, title, color):
        """"コンストラクタ[Constructor]
        引数[Args]:
            fig (figure) : フィギュアオブジェクト[figure object]
            color_ (str) : カラーコード[Color code(ex "#E73B3A")]
        """
        self.__BG_COLOR = "#2E2E2E"  # Background color

        fig = figure(title=title,
                     plot_height=400,
                     plot_width=400,
                     tools='',
                     background_fill_color=self.__BG_COLOR)

        self._src = ColumnDataSource({LineGraphAbs.X: [],
                                      LineGraphAbs.Y: []})

        self.__glyph = Line(x=LineGraphAbs.X,
                            y=LineGraphAbs.Y,
                            line_color=color)
        fig.grid.grid_line_alpha = 0.3

        self._ren = fig.add_glyph(self._src, self.__glyph)

        self._fig = fig

    @property
    def render(self):
        """"フィギュアのGlyphRendererオブジェクトを取得する
            [get GlyphRenderer Object of Figure]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            GlyphRenderer Object
        """
        return self.__ren

    def xaxis_label(self, xlabel):
        self._fig.xaxis.axis_label = xlabel

    def yaxis_label(self, ylabel):
        self._fig.yaxis.axis_label = ylabel

    @property
    def fig(self):
        """モデルを取得する[get model]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            self._fig (object) : model object
        """
        return self._fig

    @abstractmethod
    def update(self):
        pass

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        dict_ = {LineGraphAbs.X: [],
                 LineGraphAbs.Y: []}
        self._src.data = dict_


class HistogramAbs(metaclass=ABCMeta):
    """ Histogram
            - ヒストグラム図形定義クラス[Histogram glyph definition class]
    """

    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

    def __init__(self, title, color):
        """"コンストラクタ[Constructor]
        引数[Args]:
            fig (figure) : フィギュアオブジェクト[figure object]
            color_ (str) : カラーコード[Color code(ex "#E73B3A")]
        """
        self.__BG_COLOR = "#2E2E2E"  # Background color

        fig = figure(title=title,
                     plot_height=400,
                     plot_width=400,
                     tools='',
                     background_fill_color=self.__BG_COLOR)

        self._src = ColumnDataSource({HistogramAbs.LEFT: [],
                                      HistogramAbs.RIGHT: [],
                                      HistogramAbs.TOP: [],
                                      HistogramAbs.BOTTOM: []})

        self.__glyph = Quad(left=HistogramAbs.LEFT,
                            right=HistogramAbs.RIGHT,
                            top=HistogramAbs.TOP,
                            bottom=HistogramAbs.BOTTOM,
                            fill_color=color,
                            line_width=0)
        fig.grid.grid_line_color = "white"
        fig.grid.grid_line_alpha = 0.3

        self.__ren = fig.add_glyph(self._src, self.__glyph)

        self._fig = fig

    @property
    def render(self):
        """"フィギュアのGlyphRendererオブジェクトを取得する
            [get GlyphRenderer Object of Figure]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            GlyphRenderer Object
        """
        return self.__ren

    def xaxis_label(self, xlabel):
        self._fig.xaxis.axis_label = xlabel

    def yaxis_label(self, ylabel):
        self._fig.yaxis.axis_label = ylabel

    @property
    def fig(self):
        """モデルを取得する[get model]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            self._fig (object) : model object
        """
        return self._fig

    @abstractmethod
    def update(self):
        pass

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        dict_ = {HistogramAbs.LEFT: [],
                 HistogramAbs.RIGHT: [],
                 HistogramAbs.TOP: [],
                 HistogramAbs.BOTTOM: []}
        self._src.data = dict_


class HistogramTwoAbs(metaclass=ABCMeta):
    """ Histogram
            - ヒストグラム図形定義クラス[Histogram glyph definition class]
    """

    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

    def __init__(self, title, color1, color2):
        """"コンストラクタ[Constructor]
        引数[Args]:
            fig (figure) : フィギュアオブジェクト[figure object]
            color_ (str) : カラーコード[Color code(ex "#E73B3A")]
        """
        self.__BG_COLOR = "#2E2E2E"  # Background color

        fig = figure(title=title,
                     plot_height=400,
                     plot_width=400,
                     tools='',
                     background_fill_color=self.__BG_COLOR)

        self._src1 = ColumnDataSource({HistogramAbs.LEFT: [],
                                       HistogramAbs.RIGHT: [],
                                       HistogramAbs.TOP: [],
                                       HistogramAbs.BOTTOM: []})
        self.__glyph1 = Quad(left=HistogramAbs.LEFT,
                             right=HistogramAbs.RIGHT,
                             top=HistogramAbs.TOP,
                             bottom=HistogramAbs.BOTTOM,
                             fill_color=color1,
                             line_width=0)

        self._src2 = ColumnDataSource({HistogramAbs.LEFT: [],
                                       HistogramAbs.RIGHT: [],
                                       HistogramAbs.TOP: [],
                                       HistogramAbs.BOTTOM: []})

        self.__glyph2 = Quad(left=HistogramAbs.LEFT,
                             right=HistogramAbs.RIGHT,
                             top=HistogramAbs.TOP,
                             bottom=HistogramAbs.BOTTOM,
                             fill_color=color2,
                             line_width=0)

        fig.grid.grid_line_color = "white"
        fig.grid.grid_line_alpha = 0.3

        self.__ren1 = fig.add_glyph(self._src1, self.__glyph1)
        self.__ren2 = fig.add_glyph(self._src2, self.__glyph2)

        self._fig = fig

    @property
    def render1(self):
        """"フィギュアのGlyphRendererオブジェクトを取得する
            [get GlyphRenderer Object of Figure]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            GlyphRenderer Object
        """
        return self.__ren1

    @property
    def render2(self):
        """"フィギュアのGlyphRendererオブジェクトを取得する
            [get GlyphRenderer Object of Figure]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            GlyphRenderer Object
        """
        return self.__ren2

    def xaxis_label(self, xlabel):
        self._fig.xaxis.axis_label = xlabel

    def yaxis_label(self, ylabel):
        self._fig.yaxis.axis_label = ylabel

    @property
    def fig(self):
        """モデルを取得する[get model]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            self._fig (object) : model object
        """
        return self._fig

    @abstractmethod
    def update(self):
        pass

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        dict_ = {HistogramAbs.LEFT: [],
                 HistogramAbs.RIGHT: [],
                 HistogramAbs.TOP: [],
                 HistogramAbs.BOTTOM: []}
        self._src1.data = dict_
        self._src2.data = dict_


class VerticalHistogram(HistogramAbs):

    def __init__(self, title, color):
        super().__init__(title, color)

    def update(self, arry, bins, rng=None):
        """"データを設定する[set glyph date]
        引数[Args]:
            df (pandas data frame) : pandasデータフレーム[pandas data frame]
            gran (str) : ローソク足の時間足[granularity of a candlestick]
        戻り値[Returns]:
            なし[None]
        """
        hist, edges = np.histogram(arry, bins=bins, range=rng)
        self._src.data = {
            HistogramAbs.LEFT: edges[:-1],
            HistogramAbs.RIGHT: edges[1:],
            HistogramAbs.TOP: hist,
            HistogramAbs.BOTTOM: [0] * len(hist),
        }


class VerticalHistogramTwo(HistogramTwoAbs):

    def __init__(self, title, color1, color2):
        super().__init__(title, color1, color2)
        self._fig.y_range = Range1d()

    def update(self, arry1, arry2, bins, rng=None):
        """"データを設定する[set glyph date]
        引数[Args]:
            df (pandas data frame) : pandasデータフレーム[pandas data frame]
            gran (str) : ローソク足の時間足[granularity of a candlestick]
        戻り値[Returns]:
            なし[None]
        """
        hist1, edges1 = np.histogram(arry1, bins=bins, range=rng)
        hist2, edges2 = np.histogram(arry2, bins=bins, range=rng)

        if rng is None:
            end_ = max(hist1.max(), hist2.max())
            end_ += (end_ * 0.1)
            str_ = -end_
        else:
            str_ = rng[0]
            end_ = rng[1]

        hist2 = [n * (-1) for n in hist2]

        self._src1.data = {
            HistogramAbs.LEFT: edges1[:-1],
            HistogramAbs.RIGHT: edges1[1:],
            HistogramAbs.TOP: hist1,
            HistogramAbs.BOTTOM: [0] * len(hist1),
        }

        self._src2.data = {
            HistogramAbs.LEFT: edges2[:-1],
            HistogramAbs.RIGHT: edges2[1:],
            HistogramAbs.TOP: [0] * len(hist2),
            HistogramAbs.BOTTOM: hist2,
        }

        self._fig.y_range.update(start=str_, end=end_)


class HorizontalHistogram(HistogramAbs):

    def __init__(self, title, color):
        super().__init__(title, color)

    def update(self, arry, bins, rng=None):
        """"データを設定する[set glyph date]
        引数[Args]:
            df (pandas data frame) : pandasデータフレーム[pandas data frame]
            gran (str) : ローソク足の時間足[granularity of a candlestick]
        戻り値[Returns]:
            なし[None]
        """
        hist, edges = np.histogram(arry, bins=bins, range=rng)
        self._src.data = {
            HistogramAbs.LEFT: [0] * len(hist),
            HistogramAbs.RIGHT: hist,
            HistogramAbs.TOP: edges[1:],
            HistogramAbs.BOTTOM: edges[:-1],
        }


class HorizontalHistogramTwo(HistogramTwoAbs):

    def __init__(self, title, color1, color2):
        super().__init__(title, color1, color2)
        self._fig.x_range = Range1d()

    def update(self, arry1, arry2, bins, rng=None):
        """"データを設定する[set glyph date]
        引数[Args]:
            df (pandas data frame) : pandasデータフレーム[pandas data frame]
            gran (str) : ローソク足の時間足[granularity of a candlestick]
        戻り値[Returns]:
            なし[None]
        """
        hist1, edges1 = np.histogram(arry1, bins=bins, range=rng)
        hist2, edges2 = np.histogram(arry2, bins=bins, range=rng)

        end_ = max(hist1.max(), hist2.max())
        end_ += (end_ * 0.1)
        str_ = -end_

        hist2 = [n * (-1) for n in hist2]

        self._src1.data = {
            HistogramAbs.LEFT: [0] * len(hist1),
            HistogramAbs.RIGHT: hist1,
            HistogramAbs.TOP: edges1[1:],
            HistogramAbs.BOTTOM: edges1[:-1],
        }

        self._src2.data = {
            HistogramAbs.LEFT: hist2,
            HistogramAbs.RIGHT: [0] * len(hist2),
            HistogramAbs.TOP: edges2[1:],
            HistogramAbs.BOTTOM: edges2[:-1],
        }

        self._fig.x_range.update(start=str_, end=end_)


def normal2d(X, Y, sigx=1.0, sigy=1.0, mux=0.0, muy=0.0):
    z = (X - mux)**2 / sigx**2 + (Y - muy)**2 / sigy**2
    return np.exp(-z / 2) / (2 * np.pi * sigx * sigy)


if __name__ == "__main__":
    from bokeh.io import show
    from bokeh.layouts import layout

    vhist = VerticalHistogram(title="Vertical", color="pink")
    hhist = HorizontalHistogram(title="Horizontal", color="yellow")
    vhis2 = VerticalHistogramTwo(
        title="VerticalTwo", color1="red", color2="blue")
    hhis2 = HorizontalHistogramTwo(
        title="HorizontalTwo", color1="red", color2="blue")

    c = np.random.randint(10, size=500)
    d = np.random.randint(10, size=500)
    vhist.update(c, bins=10, rng=None)
    hhist.update(c, bins=10, rng=None)
    vhis2.update(c, d, bins=10, rng=None)
    hhis2.update(c, d, bins=10, rng=None)

    plt_vhist = vhist.fig
    plt_hhist = hhist.fig
    plt_vhis2 = vhis2.fig
    plt_hhis2 = hhis2.fig
    hhis2.xaxis_label("回数")
    hhis2.yaxis_label("Price")

    # ============ HeatMap ================
    hm = HeatMap("Title Sample")

    X1, Y1 = np.mgrid[0:10:2, 1:10:2]
    print(X1)
    image = utl.normalzie(X1, amin=0.03, amax=0.86)

    print(image)
    print(image.min())
    print(image.max())

    x = 0
    y = 0
    dw = 0.64
    dh = 0.75

    hm.update(image, x, y, dw, dh)
    hm.xaxis_label("X軸")
    hm.yaxis_label("Y軸")

    # ============ HeatMap ================
    hm2 = HeatMap2("Title Sample")

    x = np.array([0, 1, 2,
                  0, 1, 2,
                  0, 1, 2])

    y = np.array([0, 0, 0,
                  1, 1, 1,
                  2, 2, 2])

    w = np.ones(len(x)) * 0.9
    h = np.ones(len(x)) * 0.9

    d = np.arange(len(x))


    print(d)

    hm2.update(x, y, w, h, d)




    layout_ = layout(children=[[plt_vhist, plt_hhist],
                               [plt_vhis2, plt_hhis2],
                               [hm.fig, hm2.fig]])

    show(layout_)
