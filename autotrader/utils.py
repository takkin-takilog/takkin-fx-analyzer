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
