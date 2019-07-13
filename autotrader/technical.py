from math import pi
import pandas as pd
from bokeh.models.glyphs import Line
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from autotrader.bokeh_common import AxisTyp


class SimpleMovingAverage(object):
    """ SimpleMovingAverage
            - 単純移動平均線クラス[moving average class]
    """
    LBL_SMA_S = "SMA-S"
    LBL_SMA_M = "SMA-M"
    LBL_SMA_L = "SMA-L"

    def __init__(self, plt):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__XDT = "xdt"
        self.__YPR = "ypr"

        self.__srcs = ColumnDataSource({self.__XDT: [],
                                        self.__YPR: []})
        self.__srcm = ColumnDataSource({self.__XDT: [],
                                        self.__YPR: []})
        self.__srcl = ColumnDataSource({self.__XDT: [],
                                        self.__YPR: []})

        glvline = Line(x=self.__XDT,
                       y=self.__YPR,
                       line_color="pink",
                       line_dash="solid",
                       line_width=1,
                       line_alpha=1.0)
        plt.add_glyph(self.__srcs, glvline)

        glvline = Line(x=self.__XDT,
                       y=self.__YPR,
                       line_color="yellow",
                       line_dash="solid",
                       line_width=1,
                       line_alpha=1.0)
        plt.add_glyph(self.__srcm, glvline)

        glvline = Line(x=self.__XDT,
                       y=self.__YPR,
                       line_color="orange",
                       line_dash="solid",
                       line_width=1,
                       line_alpha=1.0)
        plt.add_glyph(self.__srcl, glvline)

    def update_sho(self, df, window_):
        from autotrader.candlestick import LBL_CLOSE
        df[self.LBL_SMA_S] = df[LBL_CLOSE].rolling(window=window_).mean()
        self.__srcs.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_SMA_S].tolist(),
        }

    def update_mid(self, df, window_):
        from autotrader.candlestick import LBL_CLOSE
        df[self.LBL_SMA_M] = df[LBL_CLOSE].rolling(window=window_).mean()
        self.__srcm.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_SMA_M].tolist(),
        }

    def update_lon(self, df, window_):
        from autotrader.candlestick import LBL_CLOSE
        df[self.LBL_SMA_L] = df[LBL_CLOSE].rolling(window=window_).mean()
        self.__srcl.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_SMA_L].tolist(),
        }

    def clear(self):
        dict_ = {self.__XDT: [],
                 self.__YPR: []}
        self.__srcs.data = dict_
        self.__srcm.data = dict_
        self.__srcl.data = dict_


class MACD(object):
    """ MACD
            - MACDクラス[MACD class]
    """
    LBL_MACD = "MACD"
    LBL_SIGN = "SIGN"

    def __init__(self, plt_):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__XDT = "xdt"
        self.__YPR = "ypr"

        # Main chart figure
        self.__plt = figure(plot_height=300,
                            x_axis_type=AxisTyp.X_DATETIME,
                            x_range=plt_.x_range,
                            background_fill_color=plt_.background_fill_color,
                            sizing_mode=plt_.sizing_mode,
                            title="MACD")
        self.__plt.xaxis.major_label_orientation = pi / 4
        self.__plt.grid.grid_line_alpha = 0.3

        print("MACD Active")


class BollingerBands(object):
    """ BollingerBands
            - ボリンジャーバンドクラス[bollinger bands class]
    """
    LBL_BB_BASE = "BB-Base"
    LBL_BB_SIG1U = "BB-Sig*1-up"
    LBL_BB_SIG1D = "BB-Sig*1-dw"
    LBL_BB_SIG2U = "BB-Sig*2-up"
    LBL_BB_SIG2D = "BB-Sig*2-dw"
    LBL_BB_SIG3U = "BB-Sig*3-up"
    LBL_BB_SIG3D = "BB-Sig*3-dw"

    def __init__(self, plt):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__XDT = "xdt"
        self.__YPR = "ypr"

        self.__srcbs = ColumnDataSource({self.__XDT: [],
                                         self.__YPR: []})
        self.__srcu1 = ColumnDataSource({self.__XDT: [],
                                         self.__YPR: []})
        self.__srcu2 = ColumnDataSource({self.__XDT: [],
                                         self.__YPR: []})
        self.__srcu3 = ColumnDataSource({self.__XDT: [],
                                         self.__YPR: []})
        self.__srcd1 = ColumnDataSource({self.__XDT: [],
                                         self.__YPR: []})
        self.__srcd2 = ColumnDataSource({self.__XDT: [],
                                         self.__YPR: []})
        self.__srcd3 = ColumnDataSource({self.__XDT: [],
                                         self.__YPR: []})

        glvline = Line(x=self.__XDT,
                       y=self.__YPR,
                       line_color="blue",
                       line_dash="dotted",
                       line_width=1,
                       line_alpha=1.0)
        plt.add_glyph(self.__srcbs, glvline)

        glvline = Line(x=self.__XDT,
                       y=self.__YPR,
                       line_color="deepskyblue",
                       line_dash="dotted",
                       line_width=1,
                       line_alpha=1.0)
        plt.add_glyph(self.__srcu1, glvline)
        plt.add_glyph(self.__srcd1, glvline)

        glvline = Line(x=self.__XDT,
                       y=self.__YPR,
                       line_color="aqua",
                       line_dash="dotted",
                       line_width=1,
                       line_alpha=1.0)
        plt.add_glyph(self.__srcu2, glvline)
        plt.add_glyph(self.__srcd2, glvline)

        glvline = Line(x=self.__XDT,
                       y=self.__YPR,
                       line_color="aquamarine",
                       line_dash="dotted",
                       line_width=1,
                       line_alpha=1.0)
        plt.add_glyph(self.__srcu3, glvline)
        plt.add_glyph(self.__srcd3, glvline)

    def update(self, df, window_):
        from autotrader.candlestick import LBL_CLOSE
        df[self.LBL_BB_BASE] = df[LBL_CLOSE].rolling(window=window_).mean()
        self.__srcbs.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_BB_BASE].tolist(),
        }

        base = df[self.LBL_BB_BASE]
        sigma = df[LBL_CLOSE].rolling(window=window_).std(ddof=0)

        df[self.LBL_BB_SIG1U] = base + sigma
        df[self.LBL_BB_SIG1D] = base - sigma
        df[self.LBL_BB_SIG2U] = base + sigma * 2
        df[self.LBL_BB_SIG2D] = base - sigma * 2
        df[self.LBL_BB_SIG3U] = base + sigma * 3
        df[self.LBL_BB_SIG3D] = base - sigma * 3

        self.__srcu1.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_BB_SIG1U].tolist(),
        }
        self.__srcd1.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_BB_SIG1D].tolist(),
        }
        self.__srcu2.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_BB_SIG2U].tolist(),
        }
        self.__srcd2.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_BB_SIG2D].tolist(),
        }
        self.__srcu3.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_BB_SIG3U].tolist(),
        }
        self.__srcd3.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_BB_SIG3D].tolist(),
        }

    def clear(self):
        dict_ = {self.__XDT: [],
                 self.__YPR: []}
        self.__srcbs.data = dict_
        self.__srcu1.data = dict_
        self.__srcd1.data = dict_
        self.__srcu2.data = dict_
        self.__srcd2.data = dict_
        self.__srcu3.data = dict_
        self.__srcd3.data = dict_


if __name__ == "__main__":
    from autotrader.candlestick import LBL_CLOSE
    dic_arr = {LBL_CLOSE: [110, 111, 112, 113,
                           114, 115, 116, 117, 118, 119, 120]}

    df = pd.DataFrame(dic_arr)

    print(df)
    sma = SimpleMovingAverage()
    sma.update(df)
    print(df)
