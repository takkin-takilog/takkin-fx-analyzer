import pandas as pd
from bokeh.models.glyphs import Line
from bokeh.models import ColumnDataSource


class SimpleMovingAverage(object):
    """ SimpleMovingAverage
            - 単純移動平均線クラス[moving average class]
    """
    SMACOL_S = "SMA-S"
    SMACOL_M = "SMA-M"
    SMACOL_L = "SMA-L"

    XDT = "xdt"
    YPR = "ypr"

    def __init__(self, plt):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        print("SimpleMovingAverage")
        """
        self.__plt = plt
        self.__plt.line(df.index, df[self.SMACOL_S], line_width=2,
                        line_color="pink", legend=self.SMACOL_S)
        """

        self.__srcs = ColumnDataSource({self.XDT: [],
                                        self.YPR: []})
        self.__srcm = ColumnDataSource({self.XDT: [],
                                        self.YPR: []})
        self.__srcl = ColumnDataSource({self.XDT: [],
                                        self.YPR: []})

        glvline = Line(x=self.XDT,
                       y=self.YPR,
                       line_color="pink",
                       line_dash="solid",
                       line_width=1,
                       line_alpha=1.0)
        plt.add_glyph(self.__srcs, glvline)

        glvline = Line(x=self.XDT,
                       y=self.YPR,
                       line_color="yellow",
                       line_dash="solid",
                       line_width=1,
                       line_alpha=1.0)
        plt.add_glyph(self.__srcm, glvline)

        glvline = Line(x=self.XDT,
                       y=self.YPR,
                       line_color="orange",
                       line_dash="solid",
                       line_width=1,
                       line_alpha=1.0)
        plt.add_glyph(self.__srcl, glvline)

    def update_sho(self, df, window_):
        from autotrader.candlestick import LBL_CLOSE
        df[self.SMACOL_S] = df[LBL_CLOSE].rolling(
            window=window_).mean()
        self.__srcs.data = {
            self.XDT: df.index.tolist(),
            self.YPR: df[self.SMACOL_S].tolist(),
        }

    def update_mid(self, df, window_):
        from autotrader.candlestick import LBL_CLOSE
        df[self.SMACOL_M] = df[LBL_CLOSE].rolling(
            window=window_).mean()
        self.__srcm.data = {
            self.XDT: df.index.tolist(),
            self.YPR: df[self.SMACOL_M].tolist(),
        }

    def update_lon(self, df, window_):
        from autotrader.candlestick import LBL_CLOSE
        df[self.SMACOL_L] = df[LBL_CLOSE].rolling(
            window=window_).mean()
        self.__srcl.data = {
            self.XDT: df.index.tolist(),
            self.YPR: df[self.SMACOL_L].tolist(),
        }

    def clear(self):
        dict_ = {self.XDT: [],
                 self.YPR: []}
        self.__srcs.data = dict_
        self.__srcm.data = dict_
        self.__srcl.data = dict_


if __name__ == "__main__":
    from autotrader.candlestick import LBL_CLOSE
    dic_arr = {LBL_CLOSE: [110, 111, 112, 113,
                           114, 115, 116, 117, 118, 119, 120]}

    df = pd.DataFrame(dic_arr)

    print(df)
    sma = SimpleMovingAverage()
    sma.update(df)
    print(df)
