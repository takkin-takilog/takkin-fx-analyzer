import copy
import jpholiday
from datetime import timedelta
import numpy as np

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


def extract_workdays(str_date, end_date):
    """"平日のみを抽出する[extract workdays]
    引数[Args]:
        str_date : 開始日[start date]
        end_date : 終了日[end date]
    戻り値[Returns]:
        workdays list
    """
    workdays = []
    print("-----------------")
    for n in range((end_date - str_date + timedelta(days=1)).days):
        date_ = str_date + timedelta(n)
        if (date_.weekday() < 5) and not jpholiday.is_holiday(date_):
            workdays.append(date_)

    return workdays


if __name__ == "__main__":
    import datetime

    str_ = datetime.date(2019, 10, 1)
    end_ = datetime.date(2019, 10, 26)

    print(type(str_))

    workdayslist = extract_workdays(str_, end_)

    for wday in workdayslist:

        is_ = jpholiday.is_holiday(wday)

        # 曜日判定
        if wday.weekday() == 0:
            week = "月"
        elif wday.weekday() == 1:
            week = "火"
        elif wday.weekday() == 2:
            week = "水"
        elif wday.weekday() == 3:
            week = "木"
        elif wday.weekday() == 4:
            week = "金"

        print("{}: week:{}, Goto:{}" .format(wday, week, is_))
