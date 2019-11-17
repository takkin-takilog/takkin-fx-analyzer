from abc import ABCMeta, abstractmethod
from datetime import timedelta, date
from bokeh.models.widgets import Select
from bokeh.layouts import row, column
from autotrader.oanda_common import OandaIns


class DateWidget(object):
    """ DateWidget
            - 日付Widgetクラス[Date widget class]
    """

    def __init__(self, str_, dt_=date.today() - timedelta(days=1)):
        """"コンストラクタ[Constructor]
        引数[Args]:
            str_ (str) : 識別用文字列[identification character]
            st (date) : デフォルト表示日付[Default date]
        """
        defsize = 80

        # Year
        curryear = dt_.year
        pastyear = 2010
        yaerlist = list(range(pastyear, curryear + 1))
        yaerlist.reverse()
        yearlist = list(map(str, yaerlist))
        self.__slc_year = Select(title="年（" + str_ + "）",
                                 value=yearlist[0],
                                 options=yearlist,
                                 default_size=defsize)

        # Month
        monthlist = list(range(1, 13))
        monthlist = list(map(str, monthlist))
        currmonth = dt_.month
        self.__slc_month = Select(title="月（" + str_ + "）",
                                  value=str(currmonth),
                                  options=monthlist,
                                  default_size=defsize)

        # Day
        daylist = list(range(1, 32))
        daylist = list(map(str, daylist))
        currday = dt_.day
        self.__slc_day = Select(title="日（" + str_ + "）",
                                value=str(currday),
                                options=daylist,
                                default_size=defsize)

    @property
    def date(self):
        year_ = int(self.__slc_year.value)
        month_ = int(self.__slc_month.value)
        day_ = int(self.__slc_day.value)
        return date(year_, month_, day_)

    @property
    def widget(self):
        slyear = self.__slc_year
        slmonth = self.__slc_month
        slday = self.__slc_day

        col = column(
            children=[slyear, slmonth, slday])
        return col


class AnalysisAbs(metaclass=ABCMeta):
    """ AnalysisAbs
            - 線グラフ定義抽象クラス[Line graph definition abstract class]
    """

    def __init__(self):

        # Widget Select:通貨ペア[Instrument]
        INST_OPT = OandaIns.get_dispname_list()
        slc_inst = Select(title="通貨ペア:",
                          value=INST_OPT[0],
                          options=INST_OPT,
                          default_size=180)
        slc_inst.on_change("value", self.__cb_slc_inst)

        self.__inst_id = OandaIns.get_id_from_dispname(OandaIns.EUR_USD)

        self._slc_inst = slc_inst

    @property
    @abstractmethod
    def layout(self):
        pass

    @property
    def instrument_id(self):
        """"通貨ペアIDを取得する[get currency pair ID(instrument ID)]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            _inst_id (int) : 通貨ペアID[instrument ID]
        """
        return self.__inst_id

    def __cb_slc_inst(self, attr, old, new):
        """Widget Select(通貨ペア)コールバックメソッド
           [Callback method of Widget Select(Instrument)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        self.__inst_id = OandaIns.get_id_from_dispname(new)
