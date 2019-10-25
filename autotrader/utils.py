import copy
import jpholiday
from datetime import timedelta
import numpy as np
from astropy.wcs.docstrings import delta

TRUE = 1
FALSE = 0


class DateTimeManager(object):
    """ DateTimeManager
            - DateTime管理クラス[DateTime Manager class]
    """
    # タイムゾーン[Time zone]
    TZ_ASIATOKYO = 1    # Asia/Tokyo
    TZ_GMT = 2          # Greenwich Mean Time

    __TMDLT = timedelta(hours=9)

    def __init__(self, dt_, tz_=TZ_ASIATOKYO):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        if tz_ == self.TZ_ASIATOKYO:
            self.__dttky = copy.deepcopy(dt_)
            self.__dtgmt = self.__dttky - self.__TMDLT
        else:  # tz_ == TZ_GMT
            self.__dtgmt = copy.deepcopy(dt_)
            self.__dttky = self.__dtgmt + self.__TMDLT

    @property
    def tokyo(self):
        return self.__dttky

    @property
    def gmt(self):
        return self.__dtgmt


def limit_upper(input_val, upper_val):
    """"入力値に上限を設定する[limit upper value]
    引数[Args]:
        input_val : 入力値[input value]
        upper_val : 上限値[upper value]
    戻り値[Returns]:
        [limited value]
    """
    if upper_val < input_val:
        ret = upper_val
    else:
        ret = input_val
    return ret


def limit_lower(input_val, lower_val):
    """"入力値に下限を設定する[limit lower value]
    引数[Args]:
        input_val : 入力値[input value]
        upper_val : 下限値[lower value]
    戻り値[Returns]:
        [limited value]
    """
    if input_val < lower_val:
        ret = lower_val
    else:
        ret = input_val
    return ret


def normalzie(x, amin=0, amax=1):
    """"正規化する[normalzie]
    引数[Args]:
        x : 入力値[input value]
        amin : 正規化下限値[normalzie lower value]
        amax : 正規化上限値[normalzie upper value]
    戻り値[Returns]:
        [normalzied value]
    """
    xmax = x.max()
    xmin = x.min()
    if xmin == xmax:
        return np.ones_like(x)
    return (amax - amin) * (x - xmin) / (xmax - xmin) + amin


def extract_workdays(startday, endday):
    """"平日のみを抽出する[extract workdays]
    引数[Args]:
        startday : 開始日[start day]
        endday : 終了日[end day]
    戻り値[Returns]:
        workdays list
    """
    workdays = []
    print("-----------------")
    for n in range((endday - startday + timedelta(days=1)).days):
        day_ = startday + timedelta(n)
        if (day_.weekday() < 5) or jpholiday.is_holiday(day_.day):
            workdays.append(day_)

    return workdays

if __name__ == "__main__":
    import datetime
    end_ = datetime.datetime.now()
    str_ = end_ - timedelta(days=30)

    extract_workdays(str_, end_)


