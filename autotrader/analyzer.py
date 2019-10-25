from datetime import timedelta, date
from bokeh.models import Panel, Tabs
from bokeh.models.widgets import Select
from bokeh.layouts import row, column, layout, widgetbox
from autotrader.analysis.gapfill import GapFill
from autotrader.analysis.ttm_goto import TTMGoto
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

    def date(self):
        year_ = int(self.__slc_year.value)
        month_ = int(self.__slc_month.value)
        day_ = int(self.__slc_day.value)
        return date(year_, month_, day_)

    def get_layout(self):
        slyear = self.__slc_year
        slmonth = self.__slc_month
        slday = self.__slc_day

        layout = column(
            children=[slyear, slmonth, slday])
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
    wdgbx1 = widgetbox(children=[wslin, dtwdg], sizing_mode="fixed")

    # ========== Tab1：窓埋め ==========
    gapfill = _angf.get_layout()
    tab1 = Panel(child=gapfill, title="窓埋め")

    # ========== Tab2：仲値＆ゴトー日 ==========
    ttmgoto = _antg.get_layout()
    tab2 = Panel(child=ttmgoto, title="仲値＆ゴトー日")

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


def get_date_str():
    """解析開始日時を取得する[get start date]
    引数[Args]:
        None
    戻り値[Returns]:
        layout (layout) : レイアウト[layout]
    """
    global _dtwdg_str
    return _dtwdg_str.date()


def get_date_end():
    """解析終了日時を取得する[get end date]
    引数[Args]:
        None
    戻り値[Returns]:
        layout (layout) : レイアウト[layout]
    """
    global _dtwdg_end
    return _dtwdg_end.date()


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


# Widget Select:通貨ペア[Instrument]
INST_OPT = OandaIns.get_dispname_list()
_slc_inst = Select(title="通貨ペア:",
                         value=INST_OPT[0],
                         options=INST_OPT,
                         default_size=180)
_slc_inst.on_change("value", _cb_slc_inst)


# ---------- 初期設定[Initial Settings] ----------
_inst_id = 0

_dtwdg_str = DateWidget("開始", date.today() - timedelta(days=30))
_dtwdg_end = DateWidget("終了",)

# 窓埋め解析
_angf = GapFill()

# 仲値(TTM)とゴトー日
_antg = TTMGoto()
