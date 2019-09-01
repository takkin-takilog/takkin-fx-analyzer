from abc import ABCMeta, abstractmethod
import numpy as np
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.glyphs import Quad
from bokeh.plotting import figure


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

        if rng is None:
            end_ = max(hist1.max(), hist2.max())
            end_ += (end_ * 0.1)
            str_ = -end_
        else:
            str_ = rng[0]
            end_ = rng[1]

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

    layout_ = layout(children=[[plt_vhist, plt_hhist],
                               [plt_vhis2, plt_hhis2]])

    show(layout_)
