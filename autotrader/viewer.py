from bokeh.io import show
from bokeh.layouts import gridplot, row, column, layout
from bokeh.models.widgets import Select, CheckboxGroup
from bokeh import events
from datetime import datetime, timedelta
from oandapyV20.exceptions import V20Error
from autotrader.candlestick import CandleStick
from autotrader.oders import OpenOrders, OpenPositions
from autotrader.oanda_common import OandaGrn, OandaIns
from autotrader.utils import DateTimeManager
from bokeh.models.widgets import Slider, RadioGroup, Button
import autotrader.config as cfg


class Viewer(object):
    """ Viewer
            - ビュアークラス[Viewer class]
    """

    # 通貨ペア名定義
    INST_USDJPY = "USD-JPY"
    INST_EURJPY = "EUR-JPY"
    INST_EURUSD = "EUR-USD"

    # 時間足名定義
    GRAN_S5 = "５秒間足"
    GRAN_S10 = "１０秒間足"
    GRAN_S15 = "１５秒間足"
    GRAN_S30 = "３０秒間足"
    GRAN_M1 = "１分間足"
    GRAN_M2 = "２分間足"
    GRAN_M3 = "３分間足"
    GRAN_M4 = "４分間足"
    GRAN_M5 = "５分間足"
    GRAN_M10 = "１０分間足"
    GRAN_M15 = "１５分間足"
    GRAN_M30 = "３０分間足"
    GRAN_H1 = "１時間足"
    GRAN_H2 = "２時間足"
    GRAN_H3 = "３時間足"
    GRAN_H4 = "４時間足"
    GRAN_H6 = "６時間足"
    GRAN_H8 = "８時間足"
    GRAN_H12 = "１２時間足"
    GRAN_D = "日足"
    GRAN_W = "週足"

    def __init__(self, inst_def=INST_USDJPY, gran_def=GRAN_D):
        """"コンストラクタ[Constructor]
        引数[Args]:
            inst_def (str) : 通貨ペア[instrument]
            gran_def (str) : ローソク足の時間足[granularity of a candlestick]
        """
        self.__STS_DATARANGE_LATEST = 0
        self.__STS_DATARANGE_SELECT = 1

        # コンフィグファイル読み込み
        cfg.read()

        # 辞書登録：通貨ペア
        self.__INST_DICT = {
            self.INST_USDJPY: OandaIns.USD_JPY,
            self.INST_EURJPY: OandaIns.EUR_JPY,
            self.INST_EURUSD: OandaIns.EUR_USD
        }

        # 辞書登録：時間足
        self.__GRAN_DICT = {
            self.GRAN_S5: OandaGrn.S5,
            self.GRAN_S10: OandaGrn.S10,
            self.GRAN_S15: OandaGrn.S15,
            self.GRAN_S30: OandaGrn.S30,
            self.GRAN_M1: OandaGrn.M1,
            self.GRAN_M2: OandaGrn.M2,
            self.GRAN_M3: OandaGrn.M3,
            self.GRAN_M4: OandaGrn.M4,
            self.GRAN_M5: OandaGrn.M5,
            self.GRAN_M10: OandaGrn.M10,
            self.GRAN_M15: OandaGrn.M15,
            self.GRAN_M30: OandaGrn.M30,
            self.GRAN_H1: OandaGrn.H1,
            self.GRAN_H2: OandaGrn.H2,
            self.GRAN_H3: OandaGrn.H3,
            self.GRAN_H4: OandaGrn.H4,
            self.GRAN_H6: OandaGrn.H6,
            self.GRAN_H8: OandaGrn.H8,
            self.GRAN_H12: OandaGrn.H12,
            self.GRAN_D: OandaGrn.D,
            self.GRAN_W: OandaGrn.W
        }

        # モード種類リスト
        self.__MODE_LIST = [
            "オープンオーダー ＆ ポジション",
            "テクニカル指標",
            "為替データ取得期間"
        ]

        # Widgetセレクト（通貨ペア）
        INST_OPT = [
            self.INST_USDJPY, self.INST_EURJPY, self.INST_EURUSD
        ]
        self.__sl_inst = Select(title="通貨ペア:",
                                value=inst_def,
                                options=INST_OPT,
                                default_size=200)
        self.__sl_inst.on_change("value", self.__cb_sl_inst)

        # Widgetセレクト（期間）
        GRAN_OPT = [
            self.GRAN_W, self.GRAN_D, self.GRAN_H12, self.GRAN_H8,
            self.GRAN_H6, self.GRAN_H4, self.GRAN_H2, self.GRAN_H1,
            self.GRAN_M30, self.GRAN_M15, self.GRAN_M10, self.GRAN_M5,
            self.GRAN_M1
        ]

        self.__sl_gran = Select(title="期間:",
                                value=gran_def,
                                options=GRAN_OPT,
                                default_size=200)
        self.__sl_gran.on_change("value", self.__cb_sl_gran)

        # Widgetセレクト（ローソク足取得本数）
        CSNUM_OPT = [
            100, 200, 300, 400, 500, 600
        ]
        csnum_optstr = list(map(str, CSNUM_OPT))
        self.__sl_csnum = Select(title="取得本数:",
                                 value=str(CSNUM_OPT[2]),
                                 options=csnum_optstr,
                                 default_size=200)
        self.__sl_csnum.on_change("value", self.__cb_sl_csnum)
        self.__csnum = CSNUM_OPT[2]

        # Widgetセレクト（表示モード）
        self.__sl_mode = Select(title="表示モード:",
                                value=self.__MODE_LIST[0],
                                options=self.__MODE_LIST)
        self.__sl_mode.on_change("value", self.__cb_sl_mode)
        self.__mode = self.__MODE_LIST[0]

        # Widgetセレクト（テクニカル指標）
        self.__tech_dict = {"単純移動平均": self.__cb_func_sma,
                            "MACD": self.__cb_func_macd,
                            "ボリンジャーバンド": self.__cb_func_bb
                            }
        TECH_OPT = list(self.__tech_dict.keys())
        self.__sl_tech = Select(title="テクニカル指標",
                                value=TECH_OPT[0],
                                options=TECH_OPT,
                                width=200)
        self.__sl_tech.on_change("value", self.__cb_sl_tech)

        # Checkbox Group
        active_ = cfg.get_conf_act()
        self.__ckbxgr_tech = CheckboxGroup(labels=TECH_OPT, active=active_)
        self.__ckbxgr_tech.on_change("active", self.__cb_ckbxgr_tech)

        # ----- データ取得期間 ----
        self.__rg_datarang = RadioGroup(labels=["最新", "日時指定"], active=0)
        self.__rg_datarang.on_change("active", self.__cb_rg_datarang)
        self.__sts_datarang = self.__STS_DATARANGE_LATEST

        # Widgetセレクト（データ取得期間）
        # 1.Year
        curryear = datetime.today().year
        pastyear = 2010
        yaerlist = list(range(pastyear, curryear + 1))
        yaerlist.reverse()
        yearlist = list(map(str, yaerlist))
        self.__sl_datayear = Select(title="年",
                                    value=yearlist[0],
                                    options=yearlist)
        self.__sl_datayear.visible = False

        # 2.Month
        monthlist = list(range(1, 13))
        monthlist = list(map(str, monthlist))
        currmonth = datetime.today().month
        self.__sl_datamonth = Select(title="月",
                                     value=str(currmonth),
                                     options=monthlist)
        self.__sl_datamonth.visible = False

        # 3.Day
        daylist = list(range(1, 32))
        daylist = list(map(str, daylist))
        currday = datetime.today().day
        self.__sl_dataday = Select(title="日",
                                   value=str(currday),
                                   options=daylist)
        self.__sl_dataday.visible = False

        # 4.Hour
        hourlist = list(range(0, 24))
        hourlist = list(map(str, hourlist))
        currhour = datetime.today().hour
        self.__sl_datahour = Select(title="時",
                                    value=str(currhour),
                                    options=hourlist)
        self.__sl_datahour.visible = False

        # 5.Minute
        minlist = list(range(0, 60))
        minlist = list(map(str, minlist))
        currmin = datetime.today().minute
        self.__sl_datamin = Select(title="分",
                                   value=str(currmin),
                                   options=minlist)
        self.__sl_datamin.visible = False

        # 実行
        self.__bt_datarang = Button(label="実行", button_type="success")
        self.__bt_datarang.on_click(self.__cb_but_datarang)

        # ---------- テクニカル指標 ----------
        # ===== 単純移動平均 =====
        defsho = cfg.get_conf(cfg.ITEM_SMA_SHO)
        self.__sldtecsma_s = Slider(start=1, end=100, value=defsho,
                                    step=1, title="SMA S")
        self.__sldtecsma_s.on_change('value', self.__cb_sldtecsma_s)

        defmid = cfg.get_conf(cfg.ITEM_SMA_MID)
        self.__sldtecsma_m = Slider(start=1, end=100, value=defmid,
                                    step=1, title="SMA M")
        self.__sldtecsma_m.on_change('value', self.__cb_sldtecsma_m)

        deflon = cfg.get_conf(cfg.ITEM_SMA_LON)
        self.__sldtecsma_l = Slider(start=1, end=100, value=deflon,
                                    step=1, title="SMA L")
        self.__sldtecsma_l.on_change('value', self.__cb_sldtecsma_l)

        # ===== MACD =====
        defsho = cfg.get_conf(cfg.ITEM_MACD_SHO)
        self.__sldtecmacd_sh = Slider(start=1, end=100, value=defsho,
                                      step=1, title="短期")
        self.__sldtecmacd_sh.on_change('value', self.__cb_sldtecmacd_sh)

        deflon = cfg.get_conf(cfg.ITEM_MACD_LON)
        self.__sldtecmacd_lo = Slider(start=1, end=100, value=deflon,
                                      step=1, title="長期")
        self.__sldtecmacd_lo.on_change('value', self.__cb_sldtecmacd_lo)

        defsig = cfg.get_conf(cfg.ITEM_MACD_SIG)
        self.__sldtecmacd_si = Slider(start=1, end=100, value=defsig,
                                      step=1, title="シグナル")
        self.__sldtecmacd_si.on_change('value', self.__cb_sldtecmacd_si)

        # ===== ボリンジャーバンド =====
        defprd = cfg.get_conf(cfg.ITEM_BB_PRD)
        self.__sldtecbb = Slider(start=1, end=100, value=defprd,
                                 step=1, title="期間")
        self.__sldtecbb.on_change('value', self.__cb_sldtecbb)

        # ---------- 初期設定 ----------
        self.__inst = self.__INST_DICT[inst_def]
        self.__gran = self.__GRAN_DICT[gran_def]

        self.__set_datarang()

        self.__cs = CandleStick()
        try:
            yrng = self.__cs.fetch(self.__gran, self.__inst,
                                   self.__gmtstr, self.__gmtend)
        except V20Error as v20err:
            print("-----V20Error: {}".format(v20err))
        except ConnectionError as cerr:
            print("----- ConnectionError: {}".format(cerr))
        except Exception as err:
            print("----- ExceptionError: {}".format(err))

        self.__opord = OpenOrders(yrng)
        self.__oppos = OpenPositions(yrng)

    def __del__(self):
        """"デストラクタ[Destructor]
        """
        print("デストラクタ")

    def __get_latestrange(self, gran, num):
        """"チャートを描写する期間を取得する[get period of chart]
        引数[Args]:
            gran (str) : ローソク足の時間足[granularity of a candlestick]
            num (int) : ローソクの表示本数[number of drawn candlestick]
        戻り値[Returns]:
            dtmstr (DateTimeManager) : 開始日時[start date]
            dtmend (DateTimeManager) : 終了日時[end date]
        """
        # 現在時刻を取得
        now_ = datetime.now()
        to_ = datetime(now_.year, now_.month, now_.day,
                       now_.hour, now_.minute, now_.second)

        if gran == OandaGrn.D:
            from_ = to_ - timedelta(days=num)
        elif gran == OandaGrn.H12:
            from_ = to_ - timedelta(hours=num * 12)
        elif gran == OandaGrn.H8:
            from_ = to_ - timedelta(hours=num * 8)
        elif gran == OandaGrn.H6:
            from_ = to_ - timedelta(hours=num * 6)
        elif gran == OandaGrn.H4:
            from_ = to_ - timedelta(hours=num * 4)
        elif gran == OandaGrn.H3:
            from_ = to_ - timedelta(hours=num * 3)
        elif gran == OandaGrn.H2:
            from_ = to_ - timedelta(hours=num * 2)
        elif gran == OandaGrn.H1:
            from_ = to_ - timedelta(hours=num)
        elif gran == OandaGrn.M30:
            from_ = to_ - timedelta(minutes=num * 30)
        elif gran == OandaGrn.M15:
            from_ = to_ - timedelta(minutes=num * 15)
        elif gran == OandaGrn.M10:
            from_ = to_ - timedelta(minutes=num * 10)
        elif gran == OandaGrn.M5:
            from_ = to_ - timedelta(minutes=num * 5)
        elif gran == OandaGrn.M4:
            from_ = to_ - timedelta(minutes=num * 4)
        elif gran == OandaGrn.M3:
            from_ = to_ - timedelta(minutes=num * 3)
        elif gran == OandaGrn.M2:
            from_ = to_ - timedelta(minutes=num * 2)
        elif gran == OandaGrn.M1:
            from_ = to_ - timedelta(minutes=num)

        dtmstr = DateTimeManager(from_)
        dtmend = DateTimeManager(to_)

        return dtmstr, dtmend

    def __get_selectrange(self, gran, num):

        year_ = int(self.__sl_datayear.value)
        month_ = int(self.__sl_datamonth.value)
        day_ = int(self.__sl_dataday.value)
        hour_ = int(self.__sl_datahour.value)
        min_ = int(self.__sl_datamin.value)

        if self.__gran == OandaGrn.D:
            from_ = datetime(year=year_, month=month_, day=day_)
        elif (self.__gran == OandaGrn.H12
              or self.__gran == OandaGrn.H8
              or self.__gran == OandaGrn.H6
              or self.__gran == OandaGrn.H4
              or self.__gran == OandaGrn.H3
              or self.__gran == OandaGrn.H2
              or self.__gran == OandaGrn.H1):
            from_ = datetime(
                year=year_, month=month_, day=day_, hour=hour_)
        elif (self.__gran == OandaGrn.M30
              or self.__gran == OandaGrn.M15
              or self.__gran == OandaGrn.M10
              or self.__gran == OandaGrn.M5
              or self.__gran == OandaGrn.M4
              or self.__gran == OandaGrn.M3
              or self.__gran == OandaGrn.M2
              or self.__gran == OandaGrn.M1):
            from_ = datetime(year=year_, month=month_,
                             day=day_, hour=hour_, minute=min_)
        else:
            from_ = datetime(year=year_, month=month_,
                             day=day_, hour=hour_, minute=min_)

        if gran == OandaGrn.D:
            to_ = from_ + timedelta(days=num)
        elif gran == OandaGrn.H12:
            to_ = from_ + timedelta(hours=num * 12)
        elif gran == OandaGrn.H8:
            to_ = from_ + timedelta(hours=num * 8)
        elif gran == OandaGrn.H6:
            to_ = from_ + timedelta(hours=num * 6)
        elif gran == OandaGrn.H4:
            to_ = from_ + timedelta(hours=num * 4)
        elif gran == OandaGrn.H3:
            to_ = from_ + timedelta(hours=num * 3)
        elif gran == OandaGrn.H2:
            to_ = from_ + timedelta(hours=num * 2)
        elif gran == OandaGrn.H1:
            to_ = from_ + timedelta(hours=num)
        elif gran == OandaGrn.M30:
            to_ = from_ + timedelta(minutes=num * 30)
        elif gran == OandaGrn.M15:
            to_ = from_ + timedelta(minutes=num * 15)
        elif gran == OandaGrn.M10:
            to_ = from_ + timedelta(minutes=num * 10)
        elif gran == OandaGrn.M5:
            to_ = from_ + timedelta(minutes=num * 5)
        elif gran == OandaGrn.M4:
            to_ = from_ + timedelta(minutes=num * 4)
        elif gran == OandaGrn.M3:
            to_ = from_ + timedelta(minutes=num * 3)
        elif gran == OandaGrn.M2:
            to_ = from_ + timedelta(minutes=num * 2)
        elif gran == OandaGrn.M1:
            to_ = from_ + timedelta(minutes=num)

        now_ = datetime.now()
        if now_ < to_:
            to_ = datetime(now_.year, now_.month, now_.day,
                           now_.hour, now_.minute)

        dtmstr = DateTimeManager(from_)
        dtmend = DateTimeManager(to_)

        return dtmstr, dtmend

    def __cb_sl_inst(self, attr, old, new):
        """Widgetセレクト（通貨ペア）コールバックメソッド
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old value
            new (str) : New value
        戻り値[Returns]:
            None
        """
        self.__inst = self.__INST_DICT[new]
        self.__update_chart()

    def __cb_sl_gran(self, attr, old, new):
        """Widgetセレクト（期間）コールバックメソッド
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old value
            new (str) : New value
        戻り値[Returns]:
            なし[None]
        """
        self.__gran = self.__GRAN_DICT[new]
        self.__set_datarang()
        self.__update_chart()

        # 日時指定モードの場合
        if self.__rg_datarang.active == 1:
            self.__change_visible()

    def __cb_sl_csnum(self, attr, old, new):
        self.__csnum = int(new)
        self.__set_datarang()
        self.__update_chart()

    def __update_chart(self):

        try:
            yrng = self.__cs.fetch(self.__gran, self.__inst,
                                   self.__gmtstr, self.__gmtend)
        except V20Error as v20err:
            print("-----V20Error: {}".format(v20err))
        except ConnectionError as cerr:
            print("----- ConnectionError: {}".format(cerr))
        except Exception as err:
            print("----- ExceptionError: {}".format(err))

        self.__opord.clear()
        self.__opord.update_yrange(yrng)
        self.__oppos.clear()
        self.__oppos.update_yrange(yrng)

    def __cb_sl_mode(self, attr, old, new):
        """Widgetセレクト（モード）コールバックメソッド
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old value
            new (str) : New value
        戻り値[Returns]:
            なし[None]
        """
        if new == self.__MODE_LIST[0]:
            self.__set_layout_main()
            self.__mode = self.__MODE_LIST[0]
        elif new == self.__MODE_LIST[1]:
            self.__set_deflayout_tech()
            self.__mode = self.__MODE_LIST[1]
            self.__cs.clear_orders_vline()
            self.__opord.clear()
            self.__oppos.clear()
        elif new == self.__MODE_LIST[2]:
            self.__set_deflayout_datarang()
            self.__mode = self.__MODE_LIST[2]
            self.__cs.clear_orders_vline()
            self.__opord.clear()
            self.__oppos.clear()

    def __cb_sl_tech(self, attr, old, new):
        self.__tech_dict[new]()

    def __cb_chart_tap(self, event):
        # NOTE: read timestamp is Not mutches disp one.
        # fetch Open Order and Position
        if self.__mode == self.__MODE_LIST[0]:
            dtmmin = self.__cs.orders_fetch_datetime
            self.__opord.fetch(self.__inst, dtmmin)
            self.__oppos.fetch(self.__inst, dtmmin)
            self.__cs.draw_orders_fix_vline()

    def __cb_chart_mousemove(self, event):
        if self.__mode == self.__MODE_LIST[0]:
            date = datetime.fromtimestamp(
                int(event.x) / 1000) - timedelta(hours=9)
            self.__cs.draw_orders_cand_vline(date)

    def __cb_ckbxgr_tech(self, attr, old, new):
        if (0 in new):
            self.__cs.update_sma_sho(self.__sldtecsma_s.value)
            self.__cs.update_sma_mid(self.__sldtecsma_m.value)
            self.__cs.update_sma_lon(self.__sldtecsma_l.value)
        else:
            self.__cs.clear_sma()

        if (1 in new):
            self.__cs.update_macd_sho(self.__sldtecmacd_sh.value)
            self.__cs.update_macd_lon(self.__sldtecmacd_lo.value)
            self.__cs.update_macd_sig(self.__sldtecmacd_si.value)
        else:
            self.__cs.clear_macd()
        self.__switch_macdlay(1 in new)

        if (2 in new):
            self.__cs.update_bb(self.__sldtecbb.value)
        else:
            self.__cs.clear_bb()
        cfg.set_conf_act(new)
        cfg.write()

    def __cb_rg_datarang(self, attr, old, new):
        if new == 0:
            self.__sl_datayear.visible = False
            self.__sl_datamonth.visible = False
            self.__sl_dataday.visible = False
            self.__sl_datahour.visible = False
            self.__sl_datamin.visible = False
        elif new == 1:
            self.__change_visible()

    def __cb_but_datarang(self):
        rg = self.__rg_datarang.active
        if rg == 0:
            self.__sts_datarang = self.__STS_DATARANGE_LATEST
        else:
            self.__sts_datarang = self.__STS_DATARANGE_SELECT

        self.__set_datarang()
        self.__update_chart()

    def __set_datarang(self):
        if self.__sts_datarang == self.__STS_DATARANGE_LATEST:
            str_, end_ = self.__get_latestrange(self.__gran, self.__csnum)
        else:
            str_, end_ = self.__get_selectrange(self.__gran, self.__csnum)

        self.__gmtstr = str_
        self.__gmtend = end_

    def __change_visible(self):

        self.__sl_datayear.visible = True
        self.__sl_datamonth.visible = True
        self.__sl_dataday.visible = True

        if self.__gran == OandaGrn.D:
            self.__sl_datahour.visible = False
            self.__sl_datamin.visible = False
        elif (self.__gran == OandaGrn.H12
              or self.__gran == OandaGrn.H8
              or self.__gran == OandaGrn.H6
              or self.__gran == OandaGrn.H4
              or self.__gran == OandaGrn.H3
              or self.__gran == OandaGrn.H2
              or self.__gran == OandaGrn.H1):
            self.__sl_datahour.visible = True
            self.__sl_datamin.visible = False
        elif (self.__gran == OandaGrn.M30
              or self.__gran == OandaGrn.M15
              or self.__gran == OandaGrn.M10
              or self.__gran == OandaGrn.M5
              or self.__gran == OandaGrn.M4
              or self.__gran == OandaGrn.M3
              or self.__gran == OandaGrn.M2
              or self.__gran == OandaGrn.M1):
            self.__sl_datahour.visible = True
            self.__sl_datamin.visible = True
        else:
            self.__sl_datahour.visible = True
            self.__sl_datamin.visible = True

    def __cb_sldtecsma_s(self, attr, old, new):
        if cfg.get_conf(cfg.ITEM_SMA_ACT) == 1:
            self.__cs.update_sma_sho(new)
        cfg.set_conf(cfg.ITEM_SMA_SHO, new)
        cfg.write()

    def __cb_sldtecsma_m(self, attr, old, new):
        if cfg.get_conf(cfg.ITEM_SMA_ACT) == 1:
            self.__cs.update_sma_mid(new)
        cfg.set_conf(cfg.ITEM_SMA_MID, new)
        cfg.write()

    def __cb_sldtecsma_l(self, attr, old, new):
        if cfg.get_conf(cfg.ITEM_SMA_ACT) == 1:
            self.__cs.update_sma_lon(new)
        cfg.set_conf(cfg.ITEM_SMA_LON, new)
        cfg.write()

    def __cb_sldtecmacd_sh(self, attr, old, new):
        if cfg.get_conf(cfg.ITEM_MACD_ACT) == 1:
            self.__cs.update_macd_sho(new)
        cfg.set_conf(cfg.ITEM_MACD_SHO, new)
        cfg.write()

    def __cb_sldtecmacd_lo(self, attr, old, new):
        if cfg.get_conf(cfg.ITEM_MACD_ACT) == 1:
            self.__cs.update_macd_lon(new)
        cfg.set_conf(cfg.ITEM_MACD_LON, new)
        cfg.write()

    def __cb_sldtecmacd_si(self, attr, old, new):
        if cfg.get_conf(cfg.ITEM_MACD_ACT) == 1:
            self.__cs.update_macd_sig(new)
        cfg.set_conf(cfg.ITEM_MACD_SIG, new)
        cfg.write()

    def __cb_sldtecbb(self, attr, old, new):
        if cfg.get_conf(cfg.ITEM_BB_ACT) == 1:
            self.__cs.update_bb(new)
        cfg.set_conf(cfg.ITEM_BB_PRD, new)
        cfg.write()

    def __chart_layout(self):
        opord = self.__opord.widget
        oppos = self.__oppos.widget
        opbk = row(children=[opord, oppos], sizing_mode='fixed')

        chrt = self.__cs.fig_main
        rang = self.__cs.fig_range

        if cfg.get_conf(cfg.ITEM_MACD_ACT) == 1:
            macd = self.__cs.macd_plt
            chgp = gridplot(
                [
                    [None, rang],
                    [opbk, chrt],
                    [None, macd],
                ], sizing_mode='stretch_width', merge_tools=False)
        else:
            chgp = gridplot(
                [
                    [None, rang],
                    [opbk, chrt],
                ], sizing_mode='stretch_width', merge_tools=False)

        return chgp

    def get_layout(self):
        """レイアウトを取得する[get layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        wslin = self.__sl_inst
        wslgr = self.__sl_gran
        wslcs = self.__sl_csnum
        wslmo = self.__sl_mode

        widsel1 = row(children=[wslin, wslgr, wslcs], width=300)
        widsel2 = row(children=[wslmo], width=1000)

        chgp = self.__chart_layout()
        wid = row(children=[widsel1, widsel2], sizing_mode='stretch_width')
        self.__layout = layout(
            children=[wid, chgp], sizing_mode='stretch_width')

        self.__cs.fig_main.on_event(events.Tap, self.__cb_chart_tap)
        self.__cs.fig_main.on_event(
            events.MouseMove, self.__cb_chart_mousemove)

        return(self.__layout)

    def view(self):
        """描写する[view]
        引数[Args]:
            None
        戻り値[Returns]:
            None
        """
        show(self.get_layout())

    def __set_layout_main(self):
        chgp = self.__chart_layout()
        self.__layout.children[1] = chgp

    def __set_deflayout_tech(self):
        self.__set_techlay_sma()

    def __set_deflayout_datarang(self):

        rg = self.__rg_datarang
        slyear = self.__sl_datayear
        slmonth = self.__sl_datamonth
        slday = self.__sl_dataday
        slhour = self.__sl_datahour
        slmin = self.__sl_datamin
        buexe = self.__bt_datarang

        techpara = column(
            children=[rg, slyear, slmonth, slday, slhour, slmin, buexe],
            sizing_mode='fixed')

        chrt = self.__cs.fig_main
        rang = self.__cs.fig_range

        if cfg.get_conf(cfg.ITEM_MACD_ACT) == 1:
            macd = self.__cs.macd_plt
            chrtset = column(children=[rang, chrt, macd],
                             sizing_mode='stretch_width')
        else:
            chrtset = column(children=[rang, chrt],
                             sizing_mode='stretch_width')

        chartlay = row(children=[techpara, chrtset],
                       sizing_mode='stretch_width')

        self.__layout.children[1] = chartlay

    def __set_techlay_sma(self):
        para = column(children=[self.__sldtecsma_l,
                                self.__sldtecsma_m,
                                self.__sldtecsma_s
                                ])
        self.__switch_techlay(para)

    def __set_techlay_macd(self):
        para = column(children=[self.__sldtecmacd_sh,
                                self.__sldtecmacd_lo,
                                self.__sldtecmacd_si
                                ])
        self.__switch_techlay(para)

    def __set_techlay_bb(self):
        para = column(children=[self.__sldtecbb])
        self.__switch_techlay(para)

    def __switch_techlay(self, para):

        cbgt = self.__ckbxgr_tech
        tech = self.__sl_tech

        techpara = column(
            children=[cbgt, tech, para], sizing_mode='fixed')

        chrt = self.__cs.fig_main
        rang = self.__cs.fig_range

        if cfg.get_conf(cfg.ITEM_MACD_ACT) == 1:
            macd = self.__cs.macd_plt
            chrtset = column(children=[rang, chrt, macd],
                             sizing_mode='stretch_width')
        else:
            chrtset = column(children=[rang, chrt],
                             sizing_mode='stretch_width')

        chartlay = row(children=[techpara, chrtset],
                       sizing_mode='stretch_width')

        self.__layout.children[1] = chartlay

    def __switch_macdlay(self, flg):
        from bokeh.io import curdoc
        macdlay = self.__layout.children[1].children[1].children
        if flg:
            macd = self.__cs.macd_plt
            macdlay.append(macd)
        else:
            plotToRemove = curdoc().get_model_by_name('MACD')
            if plotToRemove:
                macdlay.remove(plotToRemove)

    def __cb_func_sma(self):
        self.__set_techlay_sma()

    def __cb_func_macd(self):
        self.__set_techlay_macd()

    def __cb_func_bb(self):
        self.__set_techlay_bb()
