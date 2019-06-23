from autotrader.candlestick import LBL_CLOSE
import pandas as pd


class MovingAverage(object):
    """ MovingAverage
            - 単純移動平均線クラス[moving average class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__SMA1PRD = 5
        self.__SMA2PRD = 20
        self.__SMA3PRD = 75

        # 移動平均線
        self.__SMA1COL = "SMA-" + str(self.__SMA1PRD)
        self.__SMA2COL = "SMA-" + str(self.__SMA2PRD)
        self.__SMA3COL = "SMA-" + str(self.__SMA3PRD)

    def update(self, df):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        df[self.__SMA1COL] = df[LBL_CLOSE].rolling(
            window=self.__SMA1PRD).mean()
        df[self.__SMA2COL] = df[LBL_CLOSE].rolling(
            window=self.__SMA2PRD).mean()
        df[self.__SMA3COL] = df[LBL_CLOSE].rolling(
            window=self.__SMA3PRD).mean()


if __name__ == "__main__":

    dic_arr = {LBL_CLOSE: [110, 111, 112, 113,
                           114, 115, 116, 117, 118, 119, 120]}

    df = pd.DataFrame(dic_arr)

    print(df)
    ma = MovingAverage()
    ma.update(df)
    print(df)
