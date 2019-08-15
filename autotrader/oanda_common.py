import pandas.tseries.offsets as offsets
import datetime
import oandapyV20.endpoints.instruments as it
import pandas as pd
from retrying import retry
from oandapyV20 import API
from autotrader.oanda_account import ACCESS_TOKEN


class OandaEnv(object):
    """ OandaEnv
            - OANDA環境クラス[OANDA environment class]
    """

    PRACTICE = "practice"   # デモ口座[Demo account]
    LIVE = "live"   # 本講座[Live account]


class OandaGrn(object):
    """ OandaGrn
            - ローソク足の時間足クラス[Candle stick granularity class]
    """

    S5 = "S5"  # 5 seconds
    S10 = "S10"  # 10 seconds
    S15 = "S15"  # 15 seconds
    S30 = "S30"  # 30 seconds
    M1 = "M1"  # 1 minute
    M2 = "M2"  # 2 minutes
    M3 = "M3"  # 3 minutes
    M4 = "M4"  # 4 minutes
    M5 = "M5"  # 5 minutes
    M10 = "M10"  # 10 minutes
    M15 = "M15"  # 15 minutes
    M30 = "M30"  # 30 minutes
    H1 = "H1"  # 1 hour
    H2 = "H2"  # 2 hours
    H3 = "H3"  # 3 hours
    H4 = "H4"  # 4 hours
    H6 = "H6"  # 6 hours
    H8 = "H8"  # 8 hours
    H12 = "H12"  # 12 hours
    D = "D"  # 1 Day
    W = "W"  # 1 Week
    M = "M"  # 1 Month

    __OFS_MAG = 5

    @classmethod
    def offset(cls, dt, granularity):
        if granularity == cls.S5:
            return dt + offsets.Second(5 * cls.__OFS_MAG)
        elif granularity == cls.S10:
            return dt + offsets.Second(10 * cls.__OFS_MAG)
        elif granularity == cls.S15:
            return dt + offsets.Second(15 * cls.__OFS_MAG)
        elif granularity == cls.S30:
            return dt + offsets.Second(30 * cls.__OFS_MAG)
        elif granularity == cls.M1:
            return dt + offsets.Minute(1 * cls.__OFS_MAG)
        elif granularity == cls.M2:
            return dt + offsets.Minute(2 * cls.__OFS_MAG)
        elif granularity == cls.M3:
            return dt + offsets.Minute(3 * cls.__OFS_MAG)
        elif granularity == cls.M4:
            return dt + offsets.Minute(4 * cls.__OFS_MAG)
        elif granularity == cls.M5:
            return dt + offsets.Minute(5 * cls.__OFS_MAG)
        elif granularity == cls.M10:
            return dt + offsets.Minute(10 * cls.__OFS_MAG)
        elif granularity == cls.M15:
            return dt + offsets.Minute(15 * cls.__OFS_MAG)
        elif granularity == cls.M30:
            return dt + offsets.Minute(30 * cls.__OFS_MAG)
        elif granularity == cls.H1:
            return dt + offsets.Hour(1 * cls.__OFS_MAG)
        elif granularity == cls.H2:
            return dt + offsets.Hour(2 * cls.__OFS_MAG)
        elif granularity == cls.H3:
            return dt + offsets.Hour(3 * cls.__OFS_MAG)
        elif granularity == cls.H4:
            return dt + offsets.Hour(4 * cls.__OFS_MAG)
        elif granularity == cls.H6:
            return dt + offsets.Hour(6 * cls.__OFS_MAG)
        elif granularity == cls.H8:
            return dt + offsets.Hour(8 * cls.__OFS_MAG)
        elif granularity == cls.H12:
            return dt + offsets.Hour(12 * cls.__OFS_MAG)
        elif granularity == cls.D:
            return dt + offsets.Day(1 * cls.__OFS_MAG)
        elif granularity == cls.W:
            return dt + offsets.Week(1 * cls.__OFS_MAG)
        elif granularity == cls.M:
            return dt + offsets.MonthOffset(1 * cls.__OFS_MAG)

    @classmethod
    def convert_dtfmt(cls, granularity, dt, dt_ofs=datetime.timedelta(),
                      fmt="%Y-%m-%dT%H:%M:00.000000000Z"):
        """"日付フォーマットの変換メソッド
        引数[Args]:
            granularity (str): 時間足[Candle stick granularity]
            dt (str): DT_FMT形式でフォーマットされた日付
        戻り値[Returns]:
            tf_dt (str): 変換後の日付
        """
        hour_ = 0
        minute_ = 0
        tdt = datetime.datetime.strptime(dt, fmt) + dt_ofs
        if granularity == cls.D:
            pass
        elif granularity == cls.H12:
            hour_ = 12 * (tdt.hour // 12)
        elif granularity == cls.H8:
            hour_ = 8 * (tdt.hour // 8)
        elif granularity == cls.H6:
            hour_ = 6 * (tdt.hour // 6)
        elif granularity == cls.H4:
            hour_ = 4 * (tdt.hour // 4)
        elif granularity == cls.H3:
            hour_ = 3 * (tdt.hour // 3)
        elif granularity == cls.H2:
            hour_ = 2 * (tdt.hour // 2)
        elif granularity == cls.H1:
            hour_ = 1 * (tdt.hour // 1)
        elif granularity == cls.M30:
            hour_ = tdt.hour
            minute_ = 30 * (tdt.minute // 30)
        elif granularity == cls.M15:
            hour_ = tdt.hour
            minute_ = 15 * (tdt.minute // 15)
        elif granularity == cls.M10:
            hour_ = tdt.hour
            minute_ = 10 * (tdt.minute // 10)
        elif granularity == cls.M5:
            hour_ = tdt.hour
            minute_ = 5 * (tdt.minute // 5)
        elif granularity == cls.M4:
            hour_ = tdt.hour
            minute_ = 4 * (tdt.minute // 4)
        elif granularity == cls.M3:
            hour_ = tdt.hour
            minute_ = 3 * (tdt.minute // 3)
        elif granularity == cls.M2:
            hour_ = tdt.hour
            minute_ = 2 * (tdt.minute // 2)
        elif granularity == cls.M1:
            hour_ = tdt.hour
            minute_ = 1 * (tdt.minute // 1)

        tf_dt = datetime.datetime(tdt.year, tdt.month, tdt.day, hour_, minute_)

        return tf_dt


class OandaIns(object):
    """ OandaIns
        - 通貨ペアクラス[Instruments class]
    """

    USD_JPY = "USD_JPY"
    EUR_JPY = "EUR_JPY"
    EUR_USD = "EUR_USD"


class OandaRsp(object):
    """ OandaRspMsg
        - レスポンスメッセージクラス[Response message class]
    """

    CNDL = "candles"
    TIME = "time"
    VLM = "volume"
    MID = "mid"
    OPN = "o"
    HIG = "h"
    LOW = "l"
    CLS = "c"


# Pandas data label
LBL_TIME = "time"
LBL_VOLUME = "volume"
LBL_OPEN = "open"
LBL_HIGH = "high"
LBL_LOW = "low"
LBL_CLOSE = "close"


_api = API(access_token=ACCESS_TOKEN, environment=OandaEnv.PRACTICE)


@retry(stop_max_attempt_number=5, wait_fixed=500)
def fetch_ohlc(gran, inst, gmtstr, gmtend):
    """"ローソク足情報を取得する[fetch ohlc]
    引数[Args]:
        gran (str) : ローソク足の時間足[granularity of a candlestick]
        inst (str) : 通貨ペア[instrument]
        gmtstr (DateTimeManager) : 開始日時[from date]
        gmtend (DateTimeManager) : 終了日時[to date]
    戻り値[Returns]:
        yrng (tuple) : Y軸の最小値、最大値 (min, max)
                       [Y range min and max]
    """
    DT_FMT = "%Y-%m-%dT%H:%M:00.000000000Z"

    params_ = {
        # "alignmentTimezone": "Japan",
        "from": gmtstr.gmt.strftime(DT_FMT),
        "to": gmtend.gmt.strftime(DT_FMT),
        "granularity": gran
    }

    # APIへ過去データをリクエスト
    ic = it.InstrumentsCandles(instrument=inst, params=params_)
    try:
        global _api
        _api.request(ic)
    except Exception as err:
        raise err

    data = []
    for raw in ic.response[OandaRsp.CNDL]:
        dt_ = OandaGrn.convert_dtfmt(gran, raw[OandaRsp.TIME],
                                     dt_ofs=datetime.timedelta(hours=9),
                                     fmt=DT_FMT)
        data.append([dt_,
                     raw[OandaRsp.VLM],
                     float(raw[OandaRsp.MID][OandaRsp.OPN]),
                     float(raw[OandaRsp.MID][OandaRsp.HIG]),
                     float(raw[OandaRsp.MID][OandaRsp.LOW]),
                     float(raw[OandaRsp.MID][OandaRsp.CLS])
                     ])

    # convert List to pandas data frame
    df = pd.DataFrame(data)
    df.columns = [LBL_TIME,
                  LBL_VOLUME,
                  LBL_OPEN,
                  LBL_HIGH,
                  LBL_LOW,
                  LBL_CLOSE]
    df = df.set_index(LBL_TIME)
    # date型を整形する
    df.index = pd.to_datetime(df.index)

    return df
