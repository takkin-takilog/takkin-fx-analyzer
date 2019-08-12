from math import pi
import pandas as pd
from bokeh.models.glyphs import Line
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from autotrader.bokeh_common import AxisTyp
import autotrader.config as cfg


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
            plt (figure) : フィギュアオブジェクト[figure object]
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

    def update_shr(self, df, window_):
        """"短期データを更新する[update short range data]
        引数[Args]:
            df (pandas data frame) : ローソク足データ[pandas data frame]
            window_ (int) : 短期パラメータ[short range parameter]
        戻り値[Returns]:
            なし[None]
        """
        from autotrader.candlestick import LBL_CLOSE
        df[self.LBL_SMA_S] = df[LBL_CLOSE].rolling(window=window_).mean()
        self.__srcs.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_SMA_S].tolist(),
        }

    def update_mdl(self, df, window_):
        """"中期データを更新する[update middle range data]
        引数[Args]:
            df (pandas data frame) : ローソク足データ[pandas data frame]
            window_ (int) : 中期パラメータ[middle range parameter]
        戻り値[Returns]:
            なし[None]
        """
        from autotrader.candlestick import LBL_CLOSE
        df[self.LBL_SMA_M] = df[LBL_CLOSE].rolling(window=window_).mean()
        self.__srcm.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_SMA_M].tolist(),
        }

    def update_lng(self, df, window_):
        """"長期データを更新する[update long range data]
        引数[Args]:
            df (pandas data frame) : ローソク足データ[pandas data frame]
            window_ (int) : 長期パラメータ[long range parameter]
        戻り値[Returns]:
            なし[None]
        """
        from autotrader.candlestick import LBL_CLOSE
        df[self.LBL_SMA_L] = df[LBL_CLOSE].rolling(window=window_).mean()
        self.__srcl.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_SMA_L].tolist(),
        }

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
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

    def __init__(self, plt):
        """"コンストラクタ[Constructor]
        引数[Args]:
            plt (figure) : フィギュアオブジェクト[figure object]
        """
        self.__XDT = "xdt"
        self.__YPR = "ypr"

        # Main chart figure
        self.__plt = figure(name='MACD',
                            plot_height=200,
                            x_axis_type=AxisTyp.X_DATETIME,
                            x_range=plt.x_range,
                            background_fill_color=plt.background_fill_color,
                            sizing_mode=plt.sizing_mode,
                            title="MACD")
        self.__plt.xaxis.major_label_orientation = pi / 4
        self.__plt.grid.grid_line_alpha = 0.3
        self.__plt.toolbar_location = None

        self.__srcm = ColumnDataSource({self.__XDT: [],
                                        self.__YPR: []})
        self.__srcs = ColumnDataSource({self.__XDT: [],
                                        self.__YPR: []})

        glvline = Line(x=self.__XDT,
                       y=self.__YPR,
                       line_color="red",
                       line_dash="solid",
                       line_width=1,
                       line_alpha=1.0)
        self.__plt.add_glyph(self.__srcm, glvline)

        glvline = Line(x=self.__XDT,
                       y=self.__YPR,
                       line_color="cyan",
                       line_dash="solid",
                       line_width=1,
                       line_alpha=1.0)
        self.__plt.add_glyph(self.__srcs, glvline)

    @property
    def plt(self):
        """"フィギュアオブジェクトを取得する[get figure object]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            plt (figure) : フィギュアオブジェクト[figure object]
        """
        return self.__plt

    def update_shr(self, df, window_):
        """"短期データを更新する[update short range data]
        引数[Args]:
            df (pandas data frame) : ローソク足データ[pandas data frame]
            window_ (int) : 短期パラメータ[short range parameter]
        戻り値[Returns]:
            なし[None]
        """
        from autotrader.config import ITEM_MACD_LON, ITEM_MACD_SIG
        lon = cfg.get_conf(ITEM_MACD_LON)
        sig = cfg.get_conf(ITEM_MACD_SIG)
        self.__calcMACD(df, window_, lon, sig)
        self.__srcm.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_MACD].tolist(),
        }
        self.__srcs.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_SIGN].tolist(),
        }

    def update_lng(self, df, window_):
        """"長期データを更新する[update long range data]
        引数[Args]:
            df (pandas data frame) : ローソク足データ[pandas data frame]
            window_ (int) : 長期パラメータ[long range parameter]
        戻り値[Returns]:
            なし[None]
        """
        from autotrader.config import ITEM_MACD_SHO, ITEM_MACD_SIG
        sho = cfg.get_conf(ITEM_MACD_SHO)
        sig = cfg.get_conf(ITEM_MACD_SIG)
        self.__calcMACD(df, sho, window_, sig)
        self.__srcm.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_MACD].tolist(),
        }
        self.__srcs.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_SIGN].tolist(),
        }

    def update_sgn(self, df, window_):
        """"シグナルデータを更新する[update signal data]
        引数[Args]:
            df (pandas data frame) : ローソク足データ[pandas data frame]
            window_ (int) : シグナルパラメータ[signal parameter]
        戻り値[Returns]:
            なし[None]
        """
        from autotrader.config import ITEM_MACD_SHO, ITEM_MACD_LON
        sho = cfg.get_conf(ITEM_MACD_SHO)
        lon = cfg.get_conf(ITEM_MACD_LON)
        self.__calcMACD(df, sho, lon, window_)
        self.__srcm.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_MACD].tolist(),
        }
        self.__srcs.data = {
            self.__XDT: df.index.tolist(),
            self.__YPR: df[self.LBL_SIGN].tolist(),
        }

    def __calcMACD(self, df, shr, lng, sgn):
        """"MACDを計算する[calculate MACD]
        引数[Args]:
            df (pandas data frame) : ローソク足データ[pandas data frame]
            shr (int) : 短期パラメータ[short range parameter]
            lng (int) : 長期パラメータ[long range parameter]
            sgn (int) : シグナルパラメータ[signal parameter]
        戻り値[Returns]:
            なし[None]
        """
        from autotrader.candlestick import LBL_CLOSE
        ema_s = df[LBL_CLOSE].ewm(span=shr).mean()
        ema_l = df[LBL_CLOSE].ewm(span=lng).mean()
        df[self.LBL_MACD] = (ema_s - ema_l)
        df[self.LBL_SIGN] = df[self.LBL_MACD].ewm(span=sgn).mean()

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        dict_ = {self.__XDT: [],
                 self.__YPR: []}
        self.__srcm.data = dict_
        self.__srcs.data = dict_


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
            plt (figure) : フィギュアオブジェクト[figure object]
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
        """"データを更新する[update data]
        引数[Args]:
            df (pandas data frame) : ローソク足データ[pandas data frame]
            window_ (int) : パラメータ[parameter]
        戻り値[Returns]:
            なし[None]
        """
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
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
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
