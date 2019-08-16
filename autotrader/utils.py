import datetime
import copy


class DateTimeManager(object):
    """ DateTimeManager
            - DateTime管理クラス[DateTime Manager class]
    """
    # タイムゾーン[Time zone]
    TZ_ASIATOKYO = 1    # Asia/Tokyo
    TZ_GMT = 2          # Greenwich Mean Time

    __TMDLT = datetime.timedelta(hours=9)

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
    if input_val < upper_val:
        ret = input_val
    else:
        ret = upper_val
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
        ret = input_val
    else:
        ret = lower_val
    return ret
