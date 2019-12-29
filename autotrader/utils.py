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
    import pandas as pd

    str_ = datetime.date(2019, 7, 1)
    end_ = datetime.date(2019, 10, 3)

    weekdict = {0:"月", 1:"火", 2:"水", 3:"木",
                4:"金", 5:"土", 6:"日"}
    mltfivelist = [5, 10, 15, 20, 25, 30]

    nextdate = end_ + timedelta(days=1)
    nextmonth = nextdate.month

    lastday_flg = False
    gotoday_flg = False
    workdayslist = []

    for n in range((end_ - str_ + timedelta(days=1)).days):
        date_ = end_ - timedelta(n)
        weekdayno = date_.weekday()
        we = weekdict[weekdayno]

        # 月末判定
        if not date_.month == nextmonth:
            lastday_flg = True

        # ゴトー日判定
        if date_.day in mltfivelist:
            gotoday_flg = True

        # 平日判定
        if (weekdayno < 5) and not jpholiday.is_holiday(date_):

            if lastday_flg or gotoday_flg:
                target = "○"
                lastday_flg = False
                gotoday_flg = False
            else:
                target = "×"

            print("{}:{}:{}"  .format(date_, we, target))

        nextmonth = date_.month

        print(date_)

    df = pd.DataFrame(columns=['A', 'B'])

    re = pd.Series([10, 20], index=df.columns, name = "aaa")
    df = df.append(re)
    re = pd.Series([11, 21], index=df.columns, name = "bbb")
    df = df.append(re)

    print(df)

    print(df.index)

    df.drop(index=df.index, inplace=True)
    print("aaaaaa")
    print(df)


