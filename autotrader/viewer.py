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

    # 通貨ペア名定義[define currency pair(instrument)]
    INST_USDJPY = "USD-JPY"
    INST_EURJPY = "EUR-JPY"
    INST_EURUSD = "EUR-USD"

    # 時間足名定義[define time scale(granularity)]
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
            inst_def (str) : 通貨ペア[Instrument]
            gran_def (str) : ローソク足の時間足[Granularity of a candlestick]
        """
        # データ取得タイプ状態[State of data fetch type]
        self.__STS_DATARANGE_LATEST = 0  # 最新[Latest]
        self.__STS_DATARANGE_SELECT = 1  # 選択[Youser Select]

        # コンフィグファイル読み込み[read config file]
        cfg.read()

        # 辞書登録：通貨ペア[set dictionary:Instrument]
        self.__INST_DICT = {
            self.INST_USDJPY: OandaIns.USD_JPY,
            self.INST_EURJPY: OandaIns.EUR_JPY,
            self.INST_EURUSD: OandaIns.EUR_USD
        }

        # 辞書登録：時間足[set dictionary:Granularity]
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

        # モード種類リスト[List of Mode]
        self.__MODE_LIST = [
            "オープンオーダー ＆ ポジション",
            "テクニカル指標",
            "為替データ取得期間"
        ]

        # Widget Select:通貨ペア[Instrument]
        INST_OPT = [
            self.INST_USDJPY, self.INST_EURJPY, self.INST_EURUSD
        ]
        self.__slc_inst = Select(title="通貨ペア:",
                                 value=inst_def,
                                 options=INST_OPT,
                                 default_size=200)
        self.__slc_inst.on_change("value", self.__cb_slc_inst)

        # Widget Select:時間足[Granularity]
        GRAN_OPT = [
            self.GRAN_W, self.GRAN_D, self.GRAN_H12, self.GRAN_H8,
            self.GRAN_H6, self.GRAN_H4, self.GRAN_H2, self.GRAN_H1,
            self.GRAN_M30, self.GRAN_M15, self.GRAN_M10, self.GRAN_M5,
            self.GRAN_M1
        ]

        self.__slc_gran = Select(title="時間足:",
                                 value=gran_def,
                                 options=GRAN_OPT,
                                 default_size=200)
        self.__slc_gran.on_change("value", self.__cb_slc_gran)

        # Widget Select:ローソク足取得本数[Number of candle stick]
        CSNUM_OPT = [
            100, 200, 300, 400, 500, 600
        ]
        csnum_optstr = list(map(str, CSNUM_OPT))
        self.__slc_csnum = Select(title="取得本数:",
                                  value=str(CSNUM_OPT[2]),
                                  options=csnum_optstr,
                                  default_size=200)
        self.__slc_csnum.on_change("value", self.__cb_slc_csnum)
        self.__csnum = CSNUM_OPT[2]

        # Widget Select:表示モード[Display mode]
        self.__slc_mode = Select(title="表示モード:",
                                 value=self.__MODE_LIST[0],
                                 options=self.__MODE_LIST)
        self.__slc_mode.on_change("value", self.__cb_slc_mode)
        self.__mode = self.__MODE_LIST[0]

        # Widget Select:テクニカル指標[Technical index]
        self.__tech_dict = {"単純移動平均": self.__cb_func_sma,
                            "MACD": self.__cb_func_macd,
                            "ボリンジャーバンド": self.__cb_func_bb
                            }
        TECH_OPT = list(self.__tech_dict.keys())
        self.__slc_tech = Select(title="テクニカル指標",
                                 value=TECH_OPT[0],
                                 options=TECH_OPT,
                                 width=200)
        self.__slc_tech.on_change("value", self.__cb_slc_tech)

        # Widget Checkbox Group:テクニカル指標[Technical index]
        active_ = cfg.get_conf_act()
        self.__cbg_tech = CheckboxGroup(labels=TECH_OPT, active=active_)
        self.__cbg_tech.on_change("active", self.__cb_cbg_tech)
        self.__tech_act = active_

        # Widget Radio Group:データ取得タイプ[Data fetch type]
        self.__rg_ftchtyp = RadioGroup(labels=["最新", "日時指定"], active=0)
        self.__rg_ftchtyp.on_change("active", self.__cb_rg_ftchtyp)
        self.__sts_ftchtyp = self.__STS_DATARANGE_LATEST

        # Widget Select:データ取得タイプ(選択)[Data fetch type(Youser Select)]
        # ●Year
        curryear = datetime.today().year
        pastyear = 2010
        yaerlist = list(range(pastyear, curryear + 1))
        yaerlist.reverse()
        yearlist = list(map(str, yaerlist))
        self.__slc_datayear = Select(title="年",
                                     value=yearlist[0],
                                     options=yearlist)
        self.__slc_datayear.visible = False

        # ●Month
        monthlist = list(range(1, 13))
        monthlist = list(map(str, monthlist))
        currmonth = datetime.today().month
        self.__slc_datamonth = Select(title="月",
                                      value=str(currmonth),
                                      options=monthlist)
        self.__slc_datamonth.visible = False

        # ●Day
        daylist = list(range(1, 32))
        daylist = list(map(str, daylist))
        currday = datetime.today().day
        self.__slc_dataday = Select(title="日",
                                    value=str(currday),
                                    options=daylist)
        self.__slc_dataday.visible = False

        # ●Hour
        hourlist = list(range(0, 24))
        hourlist = list(map(str, hourlist))
        currhour = datetime.today().hour
        self.__slc_datahour = Select(title="時",
                                     value=str(currhour),
                                     options=hourlist)
        self.__slc_datahour.visible = False

        # ●Minute
        minlist = list(range(0, 60))
        minlist = list(map(str, minlist))
        currmin = datetime.today().minute
        self.__slc_datamin = Select(title="分",
                                    value=str(currmin),
                                    options=minlist)
        self.__slc_datamin.visible = False

        # Widget Button:実行[Execute]
        self.__btn_ftchtypexe = Button(label="実行", button_type="success")
        self.__btn_ftchtypexe.on_click(self.__cb_btn_ftchtypexe)

        # ---------- テクニカル指標[technical index] ----------
        # ●単純移動平均[Simple Moving Average]
        defshr = cfg.get_conf(cfg.ITEM_SMA_SHR)
        self.__sld_techsma_s = Slider(start=1, end=100, value=defshr,
                                      step=1, title="SMA S")
        self.__sld_techsma_s.on_change('value', self.__cb_sld_techsma_s)

        defmdl = cfg.get_conf(cfg.ITEM_SMA_MDL)
        self.__sld_techsma_m = Slider(start=1, end=100, value=defmdl,
                                      step=1, title="SMA M")
        self.__sld_techsma_m.on_change('value', self.__cb_sld_techsma_m)

        deflng = cfg.get_conf(cfg.ITEM_SMA_LNG)
        self.__sld_techsma_l = Slider(start=1, end=100, value=deflng,
                                      step=1, title="SMA L")
        self.__sld_techsma_l.on_change('value', self.__cb_sld_techsma_l)

        # ●MACD[Moving Average Convergence and Divergence]
        defshr = cfg.get_conf(cfg.ITEM_MACD_SHR)
        self.__sld_techmacd_shr = Slider(start=1, end=100, value=defshr,
                                         step=1, title="短期")
        self.__sld_techmacd_shr.on_change('value', self.__cb_sld_techmacd_shr)

        deflng = cfg.get_conf(cfg.ITEM_MACD_LNG)
        self.__sld_techmacd_lng = Slider(start=1, end=100, value=deflng,
                                         step=1, title="長期")
        self.__sld_techmacd_lng.on_change('value', self.__cb_sld_techmacd_lng)

        defsgn = cfg.get_conf(cfg.ITEM_MACD_SGN)
        self.__sld_techmacd_sgn = Slider(start=1, end=100, value=defsgn,
                                         step=1, title="シグナル")
        self.__sld_techmacd_sgn.on_change('value', self.__cb_sld_techmacd_sgn)

        # ●ボリンジャーバンド[Bollinger Bands]
        defprd = cfg.get_conf(cfg.ITEM_BB_PRD)
        self.__sld_techbb = Slider(start=1, end=100, value=defprd,
                                   step=1, title="期間")
        self.__sld_techbb.on_change('value', self.__cb_sld_techbb)

        # ---------- 初期設定[Initial Settings] ----------
        self.__inst = self.__INST_DICT[inst_def]
        self.__gran = self.__GRAN_DICT[gran_def]
        self.__set_ftchtyp()

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
        print("Called Destructor")

    def __get_latestrange(self, gran, num):
        """"最新のチャート取得の期間を取得する[get period of latest chart fetching]
        引数[Args]:
            gran (str) : ローソク足の時間足[granularity of a candlestick]
            num (int) : ローソクの表示本数[number of drawn candlestick]
        戻り値[Returns]:
            dtmstr (DateTimeManager) : 開始日時[start date]
            dtmend (DateTimeManager) : 終了日時[end date]
        """
        # 現在時刻を取得[fetch latest datetime]
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
        """"選択されたチャート取得の期間を取得する[get period of selected chart fetching]
        引数[Args]:
            gran (str) : ローソク足の時間足[granularity of a candlestick]
            num (int) : ローソクの表示本数[number of drawn candlestick]
        戻り値[Returns]:
            dtmstr (DateTimeManager) : 開始日時[start date]
            dtmend (DateTimeManager) : 終了日時[end date]
        """
        year_ = int(self.__slc_datayear.value)
        month_ = int(self.__slc_datamonth.value)
        day_ = int(self.__slc_dataday.value)
        hour_ = int(self.__slc_datahour.value)
        min_ = int(self.__slc_datamin.value)

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
        self.__update_chart()

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
        self.__set_ftchtyp()
        self.__update_chart()

        # データ取得タイプが「日時指定」の場合
        # [If Data fetch type is "Youser Select"]
        if self.__rg_ftchtyp.active == 1:
            self.__switch_visible()

    def __cb_slc_csnum(self, attr, old, new):
        """Widget Select(ローソク足取得本数)コールバックメソッド
           [Callback method of Widget Select(Number of candle sticks to fetch)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        self.__csnum = int(new)
        self.__set_ftchtyp()
        self.__update_chart()

    def __update_chart(self):
        """チャート更新[update charts]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
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

    def __cb_slc_mode(self, attr, old, new):
        """Widget Select(モード)コールバックメソッド
           [Callback method of Widget Select(Mode)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        if new == self.__MODE_LIST[0]:
            self.__switch_main_layout()
            self.__mode = self.__MODE_LIST[0]
        elif new == self.__MODE_LIST[1]:
            self.__switch_technical_sma()
            self.__mode = self.__MODE_LIST[1]
            self.__cs.clear_orders_vline()
            self.__opord.clear()
            self.__oppos.clear()
        elif new == self.__MODE_LIST[2]:
            self.__switch_ftchtyp_layout()
            self.__mode = self.__MODE_LIST[2]
            self.__cs.clear_orders_vline()
            self.__opord.clear()
            self.__oppos.clear()

    def __cb_slc_tech(self, attr, old, new):
        """Widget Select(テクニカル指標)コールバックメソッド
           [Callback method of Widget Select(Technical index)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        self.__tech_dict[new]()

    def __cb_chart_tap(self, event):
        """Event tap(チャート)コールバックメソッド
           [Callback method of tap event(Chart)]
        引数[Args]:
            event (str) : An event name on this object
        戻り値[Returns]:
            なし[None]
        """
        if self.__mode == self.__MODE_LIST[0]:
            dtmmin = self.__cs.orders_fetch_datetime
            self.__opord.fetch(self.__inst, dtmmin)
            self.__oppos.fetch(self.__inst, dtmmin)
            self.__cs.draw_orders_fix_vline()

    def __cb_chart_mousemove(self, event):
        """Event mouse move(チャート)コールバックメソッド
           [Callback method of mouse move event(Chart)]
        引数[Args]:
            event (str) : An event name on this object
        戻り値[Returns]:
            なし[None]
        """
        if self.__mode == self.__MODE_LIST[0]:
            date = datetime.fromtimestamp(
                int(event.x) / 1000) - timedelta(hours=9)
            self.__cs.draw_orders_cand_vline(date)

    def __cb_cbg_tech(self, attr, old, new):
        """Widget Check Box Group(テクニカル指標)コールバックメソッド
           [Callback method of Widget Check Box Group(Technical index)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        # 単純移動平均[Simple Moving Average]
        if not (0 in self.__tech_act) == (0 in new):
            if (0 in new):
                self.__cs.update_sma_shr(self.__sld_techsma_s.value)
                self.__cs.update_sma_mdl(self.__sld_techsma_m.value)
                self.__cs.update_sma_lng(self.__sld_techsma_l.value)
            else:
                self.__cs.clear_sma()

        # MACD[Moving Average Convergence and Divergence]
        if not (1 in self.__tech_act) == (1 in new):
            if (1 in new):
                self.__cs.update_macd_shr(self.__sld_techmacd_shr.value)
                self.__cs.update_macd_lng(self.__sld_techmacd_lng.value)
                self.__cs.update_macd_sgn(self.__sld_techmacd_sgn.value)
            else:
                self.__cs.clear_macd()
            self.__switch_visible_macd(1 in new)

        # ボリンジャーバンド[Bollinger Bands]
        if not (2 in self.__tech_act) == (2 in new):
            if (2 in new):
                self.__cs.update_bb(self.__sld_techbb.value)
            else:
                self.__cs.clear_bb()

        cfg.set_conf_act(new)
        cfg.write()
        self.__tech_act = new

    def __cb_rg_ftchtyp(self, attr, old, new):
        """Widget Radio Group(データ取得タイプ)コールバックメソッド
           [Callback method of Widget Radio Group(Fetch type)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        if new == 0:
            self.__slc_datayear.visible = False
            self.__slc_datamonth.visible = False
            self.__slc_dataday.visible = False
            self.__slc_datahour.visible = False
            self.__slc_datamin.visible = False
        elif new == 1:
            self.__switch_visible()

    def __cb_btn_ftchtypexe(self):
        """Widget Button(実行)コールバックメソッド
           [Callback method of Widget Button(Execute)]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        rg = self.__rg_ftchtyp.active
        if rg == 0:
            self.__sts_ftchtyp = self.__STS_DATARANGE_LATEST
        else:
            self.__sts_ftchtyp = self.__STS_DATARANGE_SELECT

        self.__set_ftchtyp()
        self.__update_chart()

    def __set_ftchtyp(self):
        """データ取得タイプを設定する[set data fetching type]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        if self.__sts_ftchtyp == self.__STS_DATARANGE_LATEST:
            str_, end_ = self.__get_latestrange(self.__gran, self.__csnum)
        else:
            str_, end_ = self.__get_selectrange(self.__gran, self.__csnum)

        self.__gmtstr = str_
        self.__gmtend = end_

    def __switch_visible(self):
        """表示可否を切り替える[switch visible]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        self.__slc_datayear.visible = True
        self.__slc_datamonth.visible = True
        self.__slc_dataday.visible = True

        if self.__gran == OandaGrn.D:
            self.__slc_datahour.visible = False
            self.__slc_datamin.visible = False
        elif (self.__gran == OandaGrn.H12
              or self.__gran == OandaGrn.H8
              or self.__gran == OandaGrn.H6
              or self.__gran == OandaGrn.H4
              or self.__gran == OandaGrn.H3
              or self.__gran == OandaGrn.H2
              or self.__gran == OandaGrn.H1):
            self.__slc_datahour.visible = True
            self.__slc_datamin.visible = False
        elif (self.__gran == OandaGrn.M30
              or self.__gran == OandaGrn.M15
              or self.__gran == OandaGrn.M10
              or self.__gran == OandaGrn.M5
              or self.__gran == OandaGrn.M4
              or self.__gran == OandaGrn.M3
              or self.__gran == OandaGrn.M2
              or self.__gran == OandaGrn.M1):
            self.__slc_datahour.visible = True
            self.__slc_datamin.visible = True
        else:
            self.__slc_datahour.visible = True
            self.__slc_datamin.visible = True

    def __cb_sld_techsma_s(self, attr, old, new):
        """Widget Slider(単純移動平均：短期)コールバックメソッド
           [Callback method of Widget Slider(SMA:short range)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        if cfg.get_conf(cfg.ITEM_SMA_ACT) == 1:
            self.__cs.update_sma_shr(new)
        cfg.set_conf(cfg.ITEM_SMA_SHR, new)
        cfg.write()

    def __cb_sld_techsma_m(self, attr, old, new):
        """Widget Slider(単純移動平均：中期)コールバックメソッド
           [Callback method of Widget Slider(SMA:middle range)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        if cfg.get_conf(cfg.ITEM_SMA_ACT) == 1:
            self.__cs.update_sma_mdl(new)
        cfg.set_conf(cfg.ITEM_SMA_MDL, new)
        cfg.write()

    def __cb_sld_techsma_l(self, attr, old, new):
        """Widget Slider(単純移動平均：長期)コールバックメソッド
           [Callback method of Widget Slider(SMA:long range)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        if cfg.get_conf(cfg.ITEM_SMA_ACT) == 1:
            self.__cs.update_sma_lng(new)
        cfg.set_conf(cfg.ITEM_SMA_LNG, new)
        cfg.write()

    def __cb_sld_techmacd_shr(self, attr, old, new):
        """Widget Slider(MACD：短期)コールバックメソッド
           [Callback method of Widget Slider(MACD:short range)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        if cfg.get_conf(cfg.ITEM_MACD_ACT) == 1:
            self.__cs.update_macd_shr(new)
        cfg.set_conf(cfg.ITEM_MACD_SHR, new)
        cfg.write()

    def __cb_sld_techmacd_lng(self, attr, old, new):
        """Widget Slider(MACD：長期)コールバックメソッド
           [Callback method of Widget Slider(MACD:long range)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        if cfg.get_conf(cfg.ITEM_MACD_ACT) == 1:
            self.__cs.update_macd_lng(new)
        cfg.set_conf(cfg.ITEM_MACD_LNG, new)
        cfg.write()

    def __cb_sld_techmacd_sgn(self, attr, old, new):
        """Widget Slider(MACD：シグナル)コールバックメソッド
           [Callback method of Widget Slider(SMA:signal)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        if cfg.get_conf(cfg.ITEM_MACD_ACT) == 1:
            self.__cs.update_macd_sgn(new)
        cfg.set_conf(cfg.ITEM_MACD_SGN, new)
        cfg.write()

    def __cb_sld_techbb(self, attr, old, new):
        """Widget Slider(ボリンジャーバンド)コールバックメソッド
           [Callback method of Widget Slider(Bollinger Bands)]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        if cfg.get_conf(cfg.ITEM_BB_ACT) == 1:
            self.__cs.update_bb(new)
        cfg.set_conf(cfg.ITEM_BB_PRD, new)
        cfg.write()

    def __get_chart_layout(self):
        """チャートレイアウトを取得する[get chart layout]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            chgp (GridBox) : GridBox
        """
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

    def get_overall_layout(self):
        """全体レイアウトを取得する[get overall layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        wslin = self.__slc_inst
        wslgr = self.__slc_gran
        wslcs = self.__slc_csnum
        wslmo = self.__slc_mode

        widsel1 = row(children=[wslin, wslgr, wslcs], width=300)
        widsel2 = row(children=[wslmo], width=1000)

        chgp = self.__get_chart_layout()
        wid = row(children=[widsel1, widsel2], sizing_mode='stretch_width')
        self.__layout = layout(
            children=[wid, chgp], sizing_mode='stretch_width')

        self.__cs.fig_main.on_event(events.Tap, self.__cb_chart_tap)
        self.__cs.fig_main.on_event(events.MouseMove,
                                    self.__cb_chart_mousemove)

        return(self.__layout)

    def __switch_main_layout(self):
        """メインレイアウトに切り替える[switch main layout]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        chgp = self.__get_chart_layout()
        self.__layout.children[1] = chgp

    def __switch_ftchtyp_layout(self):
        """為替データ取得期間レイアウトに切り替える[switch fetch type select layout]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        rg = self.__rg_ftchtyp
        slyear = self.__slc_datayear
        slmonth = self.__slc_datamonth
        slday = self.__slc_dataday
        slhour = self.__slc_datahour
        slmin = self.__slc_datamin
        buexe = self.__btn_ftchtypexe

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

    def __switch_technical_sma(self):
        """テクニカル指標レイアウト（単純移動平均）に切り替える
           [switch technical index(Simple Moving Average) layout]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        para = column(children=[self.__sld_techsma_l,
                                self.__sld_techsma_m,
                                self.__sld_techsma_s
                                ])
        self.__set_technical_layout(para)

    def __switch_technical_macd(self):
        """テクニカル指標レイアウト（MACD）に切り替える
           [switch technical index(MACD) layout]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        para = column(children=[self.__sld_techmacd_shr,
                                self.__sld_techmacd_lng,
                                self.__sld_techmacd_sgn
                                ])
        self.__set_technical_layout(para)

    def __switch_technical_bb(self):
        """テクニカル指標レイアウト（ボリンジャーバンド）に切り替える
           [switch technical index(Bollinger Bands) layout]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        para = column(children=[self.__sld_techbb])
        self.__set_technical_layout(para)

    def __set_technical_layout(self, para):
        """テクニカル指標レイアウトを設定する
           [set technical index layout]
        引数[Args]:
            para (column) : テクニカル指標設定パラメータ[tecnical index parameter]
        戻り値[Returns]:
            なし[None]
        """
        cbgt = self.__cbg_tech
        tech = self.__slc_tech

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

    def __switch_visible_macd(self, flg):
        """MACDチャートの可視状態を切り替える
           [switch visible of MACD chart]
        引数[Args]:
            flg (boolean) : 可視フラグ
                            true: visible
                            false: non-visible
        戻り値[Returns]:
            なし[None]
        """
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
        """コールバック関数：単純移動平均
           [Callback fuction of Simple Moving Average]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        self.__switch_technical_sma()

    def __cb_func_macd(self):
        """コールバック関数：MACD
           [Callback fuction of MACD]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        self.__switch_technical_macd()

    def __cb_func_bb(self):
        """コールバック関数：ボリンジャーバンド
           [Callback fuction of Bollinger Bands]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        self.__switch_technical_bb()
