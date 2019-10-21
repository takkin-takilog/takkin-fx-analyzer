from datetime import datetime, timedelta
from bokeh.models.widgets import Select
from bokeh.layouts import row, column, layout, widgetbox
from autotrader.analysis.gapfill import GapFill
from autotrader.oanda_common import OandaGrn, OandaIns


class DateTimeWidget(object):
    """ DateTimeWidget
            - 日時Widgetクラス[DateTime widget class]
    """

    def __init__(self, str_, gran, dt_=datetime.today()):
        """"コンストラクタ[Constructor]
        引数[Args]:
            str_ (str) : 識別用文字列[identification character]
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

        # Hour
        hourlist = list(range(0, 24))
        hourlist = list(map(str, hourlist))
        currhour = dt_.hour
        self.__slc_hour = Select(title="時（" + str_ + "）",
                                 value=str(currhour),
                                 options=hourlist,
                                 default_size=defsize)

        # Minute
        minlist = list(range(0, 60))
        minlist = list(map(str, minlist))
        currmin = dt_.minute
        self.__slc_min = Select(title="分（" + str_ + "）",
                                value=str(currmin),
                                options=minlist,
                                default_size=defsize)

        self.update_vsibledata(gran)

    def update_vsibledata(self, gran):

        if gran == OandaGrn.D:
            self.__slc_year.visible = True
            self.__slc_month.visible = True
            self.__slc_day.visible = True
            self.__slc_hour.visible = False
            self.__slc_min.visible = False
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
        else:
            self.__slc_year.visible = True
            self.__slc_month.visible = True
            self.__slc_day.visible = True
            self.__slc_hour.visible = True
            self.__slc_min.visible = True

        self.__gran = gran

    @property
    def datetime(self):
        year_ = int(self.__slc_year.value)
        month_ = int(self.__slc_month.value)
        day_ = int(self.__slc_day.value)
        hour_ = int(self.__slc_hour.value)
        min_ = int(self.__slc_min.value)

        if self.__gran == OandaGrn.D:
            dt = datetime(year=year_, month=month_, day=day_)
        elif (self.__gran == OandaGrn.H12
              or self.__gran == OandaGrn.H8
              or self.__gran == OandaGrn.H6
              or self.__gran == OandaGrn.H4
              or self.__gran == OandaGrn.H3
              or self.__gran == OandaGrn.H2
              or self.__gran == OandaGrn.H1):
            dt = datetime(year=year_, month=month_, day=day_, hour=hour_)
        elif (self.__gran == OandaGrn.M30
              or self.__gran == OandaGrn.M15
              or self.__gran == OandaGrn.M10
              or self.__gran == OandaGrn.M5
              or self.__gran == OandaGrn.M4
              or self.__gran == OandaGrn.M3
              or self.__gran == OandaGrn.M2
              or self.__gran == OandaGrn.M1):
            dt = datetime(year=year_, month=month_,
                          day=day_, hour=hour_, minute=min_)
        else:
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


def get_overall_layout():
    """全体レイアウトを取得する[get overall layout]
    引数[Args]:
        None
    戻り値[Returns]:
        layout (layout) : レイアウト[layout]
    """
    dtwdg_str = _dtwdg_str.get_layout()
    dtwdg_end = _dtwdg_end.get_layout()
    dtwdg = row(children=[dtwdg_str, dtwdg_end])
    wslin = _slc_inst
    wslgr = _slc_gran
    wdgbx1 = widgetbox(children=[wslin, wslgr, dtwdg], sizing_mode="fixed")

    from bokeh.models import Panel, Tabs
    from bokeh.plotting import figure

    layfg = _anafg.get_layout()

    tab1 = Panel(child=layfg, title="窓埋め")

    p2 = figure(plot_width=300, plot_height=300,
                sizing_mode="stretch_width")
    p2.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5],
            line_width=3, color="navy", alpha=0.5)
    tab2 = Panel(child=p2, title="サンプル")

    tabs = Tabs(tabs=[tab1, tab2], sizing_mode="stretch_width")

    _layout = layout(children=[[wdgbx1, tabs]],
                     sizing_mode="stretch_width")
    return(_layout)


def get_instrument_id():
    """"通貨ペアIDを取得する[get currency pair ID(instrument ID)]
    引数[Args]:
        なし[None]
    戻り値[Returns]:
        _inst_id (int) : 通貨ペアID[instrument ID]
    """
    global _inst_id
    return _inst_id


def get_granularity():
    """"時間足を取得する[get granularity of a candlestick]
    引数[Args]:
        なし[None]
    戻り値[Returns]:
        _gran (str) : ローソク足の時間足[granularity of a candlestick]
    """
    global _gran
    return _gran


def get_datetime_str():
    """解析開始日時を取得する[get start datetime]
    引数[Args]:
        None
    戻り値[Returns]:
        layout (layout) : レイアウト[layout]
    """
    global _dtwdg_str
    return _dtwdg_str.datetime


def get_datetime_end():
    """解析終了日時を取得する[get end datetime]
    引数[Args]:
        None
    戻り値[Returns]:
        layout (layout) : レイアウト[layout]
    """
    global _dtwdg_end
    return _dtwdg_end.datetime


def _cb_slc_inst(attr, old, new):
    """Widget Select(通貨ペア)コールバックメソッド
       [Callback method of Widget Select(Instrument)]
    引数[Args]:
        attr (str) : An attribute name on this object
        old (str) : Old strings
        new (str) : New strings
    戻り値[Returns]:
        なし[None]
    """
    global _inst_id
    _inst_id = OandaIns.get_id_from_dispname(new)


def _cb_slc_gran(attr, old, new):
    """Widget Select(時間足)コールバックメソッド
       [Callback method of Widget Select(Granularity)]
    引数[Args]:
        attr (str) : An attribute name on this object
        old (str) : Old strings
        new (str) : New strings
    戻り値[Returns]:
        なし[None]
    """
    global _gran
    print("gran: {}" .format(_gran))
    _gran = _GRAN_DICT[new]
    _dtwdg_str.update_vsibledata(_gran)
    _dtwdg_end.update_vsibledata(_gran)


# 時間足名定義[define time scale(granularity)]
_GRAN_S5 = "５秒間足"
_GRAN_S10 = "１０秒間足"
_GRAN_S15 = "１５秒間足"
_GRAN_S30 = "３０秒間足"
_GRAN_M1 = "１分間足"
_GRAN_M2 = "２分間足"
_GRAN_M3 = "３分間足"
_GRAN_M4 = "４分間足"
_GRAN_M5 = "５分間足"
_GRAN_M10 = "１０分間足"
_GRAN_M15 = "１５分間足"
_GRAN_M30 = "３０分間足"
_GRAN_H1 = "１時間足"
_GRAN_H2 = "２時間足"
_GRAN_H3 = "３時間足"
_GRAN_H4 = "４時間足"
_GRAN_H6 = "６時間足"
_GRAN_H8 = "８時間足"
_GRAN_H12 = "１２時間足"
_GRAN_D = "日足"
_GRAN_W = "週足"

# 辞書登録：時間足[set dictionary:Granularity]
_GRAN_DICT = {
    _GRAN_S5: OandaGrn.S5,
    _GRAN_S10: OandaGrn.S10,
    _GRAN_S15: OandaGrn.S15,
    _GRAN_S30: OandaGrn.S30,
    _GRAN_M1: OandaGrn.M1,
    _GRAN_M2: OandaGrn.M2,
    _GRAN_M3: OandaGrn.M3,
    _GRAN_M4: OandaGrn.M4,
    _GRAN_M5: OandaGrn.M5,
    _GRAN_M10: OandaGrn.M10,
    _GRAN_M15: OandaGrn.M15,
    _GRAN_M30: OandaGrn.M30,
    _GRAN_H1: OandaGrn.H1,
    _GRAN_H2: OandaGrn.H2,
    _GRAN_H3: OandaGrn.H3,
    _GRAN_H4: OandaGrn.H4,
    _GRAN_H6: OandaGrn.H6,
    _GRAN_H8: OandaGrn.H8,
    _GRAN_H12: OandaGrn.H12,
    _GRAN_D: OandaGrn.D,
    _GRAN_W: OandaGrn.W
}

# Widget Select:通貨ペア[Instrument]
INST_OPT = OandaIns.get_dispname_list()
_slc_inst = Select(title="通貨ペア:",
                         value=INST_OPT[0],
                         options=INST_OPT,
                         default_size=180)
_slc_inst.on_change("value", _cb_slc_inst)

# Widget Select:時間足[Granularity]
_GRAN_OPT = [
    _GRAN_W, _GRAN_D, _GRAN_H12, _GRAN_H8,
    _GRAN_H6, _GRAN_H4, _GRAN_H2, _GRAN_H1,
    _GRAN_M30, _GRAN_M15, _GRAN_M10, _GRAN_M5,
    _GRAN_M1
]
_gran_def = _GRAN_D
_slc_gran = Select(title="時間足:",
                         value=_gran_def,
                         options=_GRAN_OPT,
                         default_size=180)
_slc_gran.on_change("value", _cb_slc_gran)

# ---------- 初期設定[Initial Settings] ----------
_inst_id = 0
_gran = _GRAN_DICT[_gran_def]

_dtwdg_str = DateTimeWidget("開始", _gran,
                            datetime.today() - timedelta(days=30))
_dtwdg_end = DateTimeWidget("終了", _gran)

# 窓埋め解析
_anafg = GapFill()
