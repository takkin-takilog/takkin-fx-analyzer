import pandas.tseries.offsets as offsets
import datetime as dt


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
    def offset_min_unit(cls, dt, granularity):
        ofs = 0
        if granularity == cls.S5:
            ofs = offsets.Second(5)
        elif granularity == cls.S10:
            ofs = offsets.Second(10)
        elif granularity == cls.S15:
            ofs = offsets.Second(15)
        elif granularity == cls.S30:
            ofs = offsets.Second(30)
        elif granularity == cls.M1:
            ofs = offsets.Minute(1)
        elif granularity == cls.M2:
            ofs = offsets.Minute(2)
        elif granularity == cls.M3:
            ofs = offsets.Minute(3)
        elif granularity == cls.M4:
            ofs = offsets.Minute(4)
        elif granularity == cls.M5:
            ofs = offsets.Minute(5)
        elif granularity == cls.M10:
            ofs = offsets.Minute(10)
        elif granularity == cls.M15:
            ofs = offsets.Minute(15)
        elif granularity == cls.M30:
            ofs = offsets.Minute(30)
        elif granularity == cls.H1:
            ofs = offsets.Hour(1)
        elif granularity == cls.H2:
            ofs = offsets.Hour(2)
        elif granularity == cls.H3:
            ofs = offsets.Hour(3)
        elif granularity == cls.H4:
            ofs = offsets.Hour(4)
        elif granularity == cls.H6:
            ofs = offsets.Hour(6)
        elif granularity == cls.H8:
            ofs = offsets.Hour(8)
        elif granularity == cls.H12:
            ofs = offsets.Hour(12)
        elif granularity == cls.D:
            ofs = offsets.Day(1)
        elif granularity == cls.W:
            ofs = offsets.Week(1)
        elif granularity == cls.M:
            ofs = offsets.MonthOffset(1)

        return dt + ofs

    @classmethod
    def convert_dtfmt(cls, granularity, dt_, dt_ofs=dt.timedelta(),
                      fmt="%Y-%m-%dT%H:%M:00.000000000Z"):
        """"日付フォーマットの変換メソッド
        引数[Args]:
            granularity (str): 時間足[Candle stick granularity]
            dt_ (str): DT_FMT形式でフォーマットされた日付
        戻り値[Returns]:
            tf_dt (str): 変換後の日付
        """
        hour_ = 0
        minute_ = 0
        tdt = dt.datetime.strptime(dt_, fmt) + dt_ofs
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

        tf_dt = dt.datetime(tdt.year, tdt.month, tdt.day, hour_, minute_)

        return tf_dt


class InsInfo(object):

    def __init__(self, disp_name, oanda_name, minunit):
        self.__disp_name = disp_name
        self.__oanda_name = oanda_name
        self.__minunit = minunit

    @property
    def disp_name(self):
        return self.__disp_name

    @property
    def oanda_name(self):
        return self.__oanda_name

    @property
    def min_unit(self):
        return self.__minunit


class OandaIns(object):
    """ OandaIns
        - 通貨ペアクラス[Instruments class]
    """

    USD_JPY = "USD_JPY"
    EUR_JPY = "EUR_JPY"
    EUR_USD = "EUR_USD"

    list = [InsInfo("USD-JPY", "USD_JPY", 3),
            InsInfo("EUR-JPY", "EUR_JPY", 3),
            InsInfo("EUR-USD", "EUR_USD", 5)
            ]

    @classmethod
    def get_id_from_dispname(cls, disp_name):

        for id_, obj in enumerate(cls.list):
            if disp_name == obj.disp_name:
                break
        return id_

    @classmethod
    def get_dispname_list(cls):

        namelist = []
        for obj in cls.list:
            namelist.append(obj.disp_name)
        return namelist

    @classmethod
    def normalize(cls, inst_id, value):
        minunit = cls.list[inst_id].min_unit
        return round(value, minunit)

    @classmethod
    def format(cls, inst_id):
        minunit = cls.list[inst_id].min_unit
        base = "0."
        fmt = base.ljust(minunit + 2, "0")
        return fmt

    @classmethod
    def min_unit_max(cls):

        minunitlist = []
        for obj in cls.list:
            minunitlist.append(obj.min_unit)
        return max(minunitlist)


class OandaRsp(object):
    """ OandaRspMsg
        - レスポンスメッセージクラス[Response message class]
    """

    CNDL = "candles"
    TIME = "time"
    VLM = "volume"
    MID = "mid"
    BID = "bid"
    ASK = "ask"
    OPN = "o"
    HIG = "h"
    LOW = "l"
    CLS = "c"
