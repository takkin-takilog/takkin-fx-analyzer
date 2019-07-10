import pandas as pd
from bokeh.models.glyphs import Line
from bokeh.models import ColumnDataSource


class SimpleMovingAverage(object):
    """ SimpleMovingAverage
            - 単純移動平均線クラス[moving average class]
    """

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
        SMACOL_S = "SMA-S"
        df[SMACOL_S] = df[LBL_CLOSE].rolling(
            window=window_).mean()
        self.__srcs.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[SMACOL_S].tolist(),
        }

    def update_mid(self, df, window_):
        from autotrader.candlestick import LBL_CLOSE
        SMACOL_M = "SMA-M"
        df[SMACOL_M] = df[LBL_CLOSE].rolling(
            window=window_).mean()
        self.__srcm.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[SMACOL_M].tolist(),
        }

    def update_lon(self, df, window_):
        from autotrader.candlestick import LBL_CLOSE
        SMACOL_L = "SMA-L"
        df[SMACOL_L] = df[LBL_CLOSE].rolling(
            window=window_).mean()
        self.__srcl.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[SMACOL_L].tolist(),
        }

    def clear(self):
        dict_ = {self.__XDT: [],
                 self.__YPR: []}
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
