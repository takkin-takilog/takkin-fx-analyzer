from autotrader.oanda_common import OandaGrn, OandaIns
from bokeh.models.widgets import Select
from bokeh.layouts import gridplot, row, column, layout
from datetime import datetime, timedelta


class DateTimeWidget(object):
    """ DateTimeWidget
            - 日時Widgetクラス[DateTime widget class]
    """

    def __init__(self, srt_, gran, dt_=datetime.today()):
        """"コンストラクタ[Constructor]
        引数[Args]:
            srt_ (str) : 識別用文字列[identification character]
            gran (str) : ローソク足の時間足[Granularity of a candlestick]
            st (Datetime) : デフォルト表示日付[Default datetime]
        """
        defsize = 80

        # Year
        curryear = dt_.year
        pastyear = 2010
        yaerlist = list(range(pastyear, curryear + 1))
        yaerlist.reverse()
        yearlist = list(map(str, yaerlist))
        self.__slc_year = Select(title="年（" + srt_ + "）",
                                 value=yearlist[0],
                                 options=yearlist,
                                 default_size=defsize)

        # Month
        monthlist = list(range(1, 13))
        monthlist = list(map(str, monthlist))
        currmonth = dt_.month
        self.__slc_month = Select(title="月（" + srt_ + "）",
                                  value=str(currmonth),
                                  options=monthlist,
                                  default_size=defsize)

        # Day
        daylist = list(range(1, 32))
        daylist = list(map(str, daylist))
        currday = dt_.day
        self.__slc_day = Select(title="日（" + srt_ + "）",
                                value=str(currday),
                                options=daylist,
                                default_size=defsize)

        # Hour
        hourlist = list(range(0, 24))
        hourlist = list(map(str, hourlist))
        currhour = dt_.hour
        self.__slc_hour = Select(title="時（" + srt_ + "）",
                                 value=str(currhour),
                                 options=hourlist,
                                 default_size=defsize)

        # Minute
        minlist = list(range(0, 60))
        minlist = list(map(str, minlist))
        currmin = dt_.minute
        self.__slc_min = Select(title="分（" + srt_ + "）",
                                value=str(currmin),
                                options=minlist,
                                default_size=defsize)

        self.update_vsibledata(gran)

    def update_vsibledata(self, gran):

        year_ = int(self.__slc_year.value)
        month_ = int(self.__slc_month.value)
        day_ = int(self.__slc_day.value)
        hour_ = int(self.__slc_hour.value)
        min_ = int(self.__slc_min.value)

        if gran == OandaGrn.D:
            self.__slc_year.visible = True
            self.__slc_month.visible = True
            self.__slc_day.visible = True
            self.__slc_hour.visible = False
            self.__slc_min.visible = False
            dt = datetime(year=year_, month=month_, day=day_)
        elif (gran == OandaGrn.H12
              or gran == OandaGrn.H8
              or gran == OandaGrn.H6
              or gran == OandaGrn.H4
              or gran == OandaGrn.H3
              or gran == OandaGrn.H2
              or gran == OandaGrn.H1):
            self.__slc_year.visible = True
            self.__slc_month.visible = True
            self.__slc_day.visible = True
            self.__slc_hour.visible = True
            self.__slc_min.visible = False
            dt = datetime(year=year_, month=month_, day=day_, hour=hour_)
        elif (gran == OandaGrn.M30
              or gran == OandaGrn.M15
              or gran == OandaGrn.M10
              or gran == OandaGrn.M5
              or gran == OandaGrn.M4
              or gran == OandaGrn.M3
              or gran == OandaGrn.M2
              or gran == OandaGrn.M1):
            self.__slc_year.visible = True
            self.__slc_month.visible = True
            self.__slc_day.visible = True
            self.__slc_hour.visible = True
            self.__slc_min.visible = True
            dt = datetime(year=year_, month=month_,
                          day=day_, hour=hour_, minute=min_)
        else:
            self.__slc_year.visible = True
            self.__slc_month.visible = True
            self.__slc_day.visible = True
            self.__slc_hour.visible = True
            self.__slc_min.visible = True
            dt = datetime(year=year_, month=month_,
                          day=day_, hour=hour_, minute=min_)

        return dt

    def get_layout(self):
        slyear = self.__slc_year
        slmonth = self.__slc_month
        slday = self.__slc_day
        slhour = self.__slc_hour
        slmin = self.__slc_min

        layout = column(
            children=[slyear, slmonth, slday, slhour, slmin])
        return layout


class Analyzer(object):
    """ Analyzer
            - 解析クラス[Analyzer class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        # 通貨ペア名定義[define currency pair(instrument)]
        self.__INST_USDJPY = "USD-JPY"
        self.__INST_EURJPY = "EUR-JPY"
        self.__INST_EURUSD = "EUR-USD"

        # 時間足名定義[define time scale(granularity)]
        self.__GRAN_S5 = "５秒間足"
        self.__GRAN_S10 = "１０秒間足"
        self.__GRAN_S15 = "１５秒間足"
        self.__GRAN_S30 = "３０秒間足"
        self.__GRAN_M1 = "１分間足"
        self.__GRAN_M2 = "２分間足"
        self.__GRAN_M3 = "３分間足"
        self.__GRAN_M4 = "４分間足"
        self.__GRAN_M5 = "５分間足"
        self.__GRAN_M10 = "１０分間足"
        self.__GRAN_M15 = "１５分間足"
        self.__GRAN_M30 = "３０分間足"
        self.__GRAN_H1 = "１時間足"
        self.__GRAN_H2 = "２時間足"
        self.__GRAN_H3 = "３時間足"
        self.__GRAN_H4 = "４時間足"
        self.__GRAN_H6 = "６時間足"
        self.__GRAN_H8 = "８時間足"
        self.__GRAN_H12 = "１２時間足"
        self.__GRAN_D = "日足"
        self.__GRAN_W = "週足"

        # 辞書登録：通貨ペア[set dictionary:Instrument]
        self.__INST_DICT = {
            self.__INST_USDJPY: OandaIns.USD_JPY,
            self.__INST_EURJPY: OandaIns.EUR_JPY,
            self.__INST_EURUSD: OandaIns.EUR_USD
        }

        # 辞書登録：時間足[set dictionary:Granularity]
        self.__GRAN_DICT = {
            self.__GRAN_S5: OandaGrn.S5,
            self.__GRAN_S10: OandaGrn.S10,
            self.__GRAN_S15: OandaGrn.S15,
            self.__GRAN_S30: OandaGrn.S30,
            self.__GRAN_M1: OandaGrn.M1,
            self.__GRAN_M2: OandaGrn.M2,
            self.__GRAN_M3: OandaGrn.M3,
            self.__GRAN_M4: OandaGrn.M4,
            self.__GRAN_M5: OandaGrn.M5,
            self.__GRAN_M10: OandaGrn.M10,
            self.__GRAN_M15: OandaGrn.M15,
            self.__GRAN_M30: OandaGrn.M30,
            self.__GRAN_H1: OandaGrn.H1,
            self.__GRAN_H2: OandaGrn.H2,
            self.__GRAN_H3: OandaGrn.H3,
            self.__GRAN_H4: OandaGrn.H4,
            self.__GRAN_H6: OandaGrn.H6,
            self.__GRAN_H8: OandaGrn.H8,
            self.__GRAN_H12: OandaGrn.H12,
            self.__GRAN_D: OandaGrn.D,
            self.__GRAN_W: OandaGrn.W
        }

        # Widget Select:通貨ペア[Instrument]
        INST_OPT = [
            self.__INST_USDJPY, self.__INST_EURJPY, self.__INST_EURUSD
        ]
        inst_def = self.__INST_USDJPY
        self.__slc_inst = Select(title="通貨ペア:",
                                 value=inst_def,
                                 options=INST_OPT,
                                 default_size=200)
        self.__slc_inst.on_change("value", self.__cb_slc_inst)

        # Widget Select:時間足[Granularity]
        GRAN_OPT = [
            self.__GRAN_W, self.__GRAN_D, self.__GRAN_H12, self.__GRAN_H8,
            self.__GRAN_H6, self.__GRAN_H4, self.__GRAN_H2, self.__GRAN_H1,
            self.__GRAN_M30, self.__GRAN_M15, self.__GRAN_M10, self.__GRAN_M5,
            self.__GRAN_M1
        ]
        gran_def = self.__GRAN_D
        self.__slc_gran = Select(title="時間足:",
                                 value=gran_def,
                                 options=GRAN_OPT,
                                 default_size=200)
        self.__slc_gran.on_change("value", self.__cb_slc_gran)

        # ---------- 初期設定[Initial Settings] ----------
        self.__inst = self.__INST_DICT[inst_def]
        self.__gran = self.__GRAN_DICT[gran_def]

        self.__dtwdg_str = DateTimeWidget("開始", self.__gran)
        self.__dtwdg_end = DateTimeWidget("終了", self.__gran)

    def get_overall_layout(self):
        """全体レイアウトを取得する[get overall layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        wslin = self.__slc_inst
        wslgr = self.__slc_gran

        dtwdg_str = self.__dtwdg_str.get_layout()
        dtwdg_end = self.__dtwdg_end.get_layout()

        wdg1 = column(children=[wslin, wslgr])
        wdg2 = row(children=[dtwdg_str, dtwdg_end])

        slclay = column(children=[wdg1, wdg2], sizing_mode="fixed")
        self.__layout = layout(children=[slclay], sizing_mode="stretch_width")
        return(self.__layout)

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
        self.__inst = self.__INST_DICT[new]

    def __cb_slc_gran(self, attr, old, new):
        """Widget Select(時間足)コールバックメソッド
           [Callback method of Widget Select(Granularity)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        self.__gran = self.__GRAN_DICT[new]
        self.__dtwdg_str.update_vsibledata(self.__gran)
        self.__dtwdg_end.update_vsibledata(self.__gran)
