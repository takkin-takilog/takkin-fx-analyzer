from abc import ABCMeta, abstractmethod
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models import LinearColorMapper, ColorBar, HoverTool
from bokeh.models.glyphs import Quad, Line, Rect
from bokeh.plotting import figure
from bokeh.transform import transform


class HeatMap(object):

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
        self.__FIG_WIDTH = 300

        mapper = LinearColorMapper(palette="Plasma256", low=0, high=1)

        fig = figure(title=title,
                     plot_width=self.__FIG_WIDTH,
                     plot_height=self.__FIG_WIDTH,
                     tools="",
                     toolbar_location=None,
                     background_fill_color="black",
                     )
        fig.xgrid.visible = False
        fig.ygrid.visible = False

        fig.x_range = Range1d()
        fig.y_range = Range1d()

        src = ColumnDataSource({HeatMap._X: [],
                                HeatMap._Y: [],
                                HeatMap._W: [],
                                HeatMap._H: [],
                                HeatMap._D: []
                                })
        glyph = Rect(x=HeatMap._X,
                     y=HeatMap._Y,
                     width=HeatMap._W,
                     height=HeatMap._H,
                     line_color=None,
                     fill_color=transform(HeatMap._D, mapper),
                     )

        ren = fig.add_glyph(src, glyph)

        srcm = ColumnDataSource({HeatMap._X: [],
                                 HeatMap._Y: [],
                                 HeatMap._W: [],
                                 HeatMap._H: [],
                                 HeatMap._D: []
                                 })
        glyphm = Rect(x=HeatMap._X,
                      y=HeatMap._Y,
                      width=HeatMap._W,
                      height=HeatMap._H,
                      line_color="red",
                      line_width=2,
                      fill_color=transform(HeatMap._D, mapper),
                      )

        fig.add_glyph(srcm, glyphm)

        hover = HoverTool()
        hover.tooltips = [
            ("Loss cut Price Offset", "@" + HeatMap._X + "{0.00000}"),
            ("Thresh", "@" + HeatMap._Y + "{0.00000}"),
            ("Sum of pips", "@" + HeatMap._D + "{0.00000}")
        ]
        hover.renderers = [ren]
        fig.add_tools(hover)

        ren.hover_glyph = Rect(line_color="red",
                               line_width=2,
                               fill_color=transform(HeatMap._D, mapper))

        self._hline = HorLine(fig, "white", 2)

        color_bar = ColorBar(color_mapper=mapper,
                             label_standoff=12,
                             border_line_color=None,
                             location=(0, 0))
        fig.add_layout(color_bar, 'right')

        self._fig = fig
        self.__src = src
        self.__srcm = srcm
        self.__cb = color_bar
        self.__cm = mapper
        self._disp_y = 0
        self._upflg = False

    @property
    def fig(self):
        return self._fig

    def xaxis_label(self, xlabel):
        self._fig.xaxis.axis_label = xlabel

    def yaxis_label(self, ylabel):
        self._fig.yaxis.axis_label = ylabel

    def update(self, map3d, xlist, ylist, xstep, ystep):

        ofsx = xstep / 2
        ofsy = ystep / 2

        x = map3d[:, 0] + ofsx
        y = map3d[:, 1] + ofsy
        d = map3d[:, 2]
        w = [xstep * 0.9] * len(map3d)
        h = [ystep * 0.9] * len(map3d)

        self.__src.data = {HeatMap._X: x,
                           HeatMap._Y: y,
                           HeatMap._W: w,
                           HeatMap._H: h,
                           HeatMap._D: d
                           }

        maxidx = np.argmax(d)
        self.__srcm.data = {HeatMap._X: [x[maxidx]],
                            HeatMap._Y: [y[maxidx]],
                            HeatMap._W: [w[maxidx]],
                            HeatMap._H: [h[maxidx]],
                            HeatMap._D: [d[maxidx]]
                            }

        self.__cm.low = d.min()
        self.__cm.high = d.max()

        strx = min(x) - ofsx
        endx = max(x) + ofsx
        self._fig.x_range.update(start=strx, end=endx, bounds=(strx, endx))

        stry = min(y) - ofsy
        endy = max(y) + ofsy
        self._fig.y_range.update(start=stry, end=endy, bounds=(stry, endy))

        self._fig.width = int(len(xlist)) * 10 + 150
        self._fig.height = int(len(ylist)) * 10

        self._df_y = pd.Series(ylist + ofsy)
        self._xrng = [strx, endx]

        self._maxidx = maxidx
        self._upflg = True

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        dict_ = {HeatMap._X: [],
                 HeatMap._Y: [],
                 HeatMap._W: [],
                 HeatMap._H: [],
                 HeatMap._D: []
                 }
        self.__src.data = dict_
        self.__srcm.data = dict_
        self._upflg = False


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

        fig.x_range = Range1d()
        fig.y_range = Range1d()

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


class LineAbs(object):
    """ LineAbs
            - 直線定義抽象クラス[Line definition abstract class]
    """
    X = "x"  # Start point
    Y = "y"  # End point

    def __init__(self, plt, color, line_width=1):
        """"コンストラクタ[Constructor]
        引数[Args]:
            plt (figure) : フィギュアオブジェクト[figure object]
            color (str) : カラーコード[Color code(ex "#E73B3A")]
        """
        self.__COLOR = color

        self._src = ColumnDataSource({LineAbs.X: [],
                                      LineAbs.Y: []})
        self.__glv = Line(x=LineAbs.X,
                          y=LineAbs.Y,
                          line_color=self.__COLOR,
                          line_dash="dashed",
                          line_width=line_width,
                          line_alpha=1.0)

        plt.add_glyph(self._src, self.__glv)
        self.__plt = plt

    @abstractmethod
    def update(self):
        pass

    def clear(self):
        """"データをクリアする[clear glyph data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        dict_ = {LineAbs.X: [],
                 LineAbs.Y: []}
        self._src.data = dict_


class VerLine(LineAbs):
    """ VerLine
            - 直線定義抽象クラス[Vertical Line definition class]
    """

    def __init__(self, plt, color, line_width=1):
        super().__init__(plt, color, line_width)

    def update(self, x, y_str, y_end):
        """"データを更新する[update glyph data]
        引数[Args]:
            dict_ (dict) : 更新データ[update data]
        戻り値[Returns]:
            なし[None]
        """
        self._src.data = {
            VerLine.X: [x, x],
            VerLine.Y: [y_str, y_end]
        }


class HorLine(LineAbs):
    """ HorLine
            - 直線定義抽象クラス[Horizontal Line definition class]
    """

    def __init__(self, plt, color, line_width=1):
        super().__init__(plt, color, line_width)

    def update(self, x_rng, y):
        """"データを更新する[update glyph data]
        引数[Args]:
            dict_ (dict) : 更新データ[update data]
        戻り値[Returns]:
            なし[None]
        """
        self._src.data = {
            VerLine.X: x_rng,
            VerLine.Y: [y, y]
        }


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

    x = np.array([0, 1, 2,
                  0, 1, 2,
                  0, 1, 2])

    y = np.array([0, 0, 0,
                  1, 1, 1,
                  2, 2, 2])

    w = np.ones(len(x)) * 0.9
    h = np.ones(len(x)) * 0.9

    d = np.arange(len(x))

    hm.update(x, y, w, h, d)

    layout_ = layout(children=[[plt_vhist, plt_hhist],
                               [plt_vhis2, plt_hhis2],
                               [hm.fig]])

    show(layout_)
