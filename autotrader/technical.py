from autotrader import candlestick as cs
import pandas as pd


class SimpleMovingAverage(object):
    """ SimpleMovingAverage
            - 単純移動平均線クラス[moving average class]
    """
    SMACOL_S = "SMA-S"
    SMACOL_M = "SMA-M"
    SMACOL_L = "SMA-L"

    SMADEF_S = 5
    SMADEF_M = 20
    SMADEF_L = 75

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        pass

    def update_mas(self, df, window_):
        df[self.SMACOL_S] = df[cs.LBL_CLOSE].rolling(
            window=window_).mean()

    def update_mam(self, df, window_):
        df[self.SMACOL_S] = df[cs.LBL_CLOSE].rolling(
            window=window_).mean()

    def update_mal(self, df, window_):
        df[self.SMACOL_S] = df[cs.LBL_CLOSE].rolling(
            window=window_).mean()


if __name__ == "__main__":

    dic_arr = {cs.LBL_CLOSE: [110, 111, 112, 113,
                              114, 115, 116, 117, 118, 119, 120]}

    df = pd.DataFrame(dic_arr)

    print(df)
    sma = SimpleMovingAverage()
    sma.update(df)
    print(df)
