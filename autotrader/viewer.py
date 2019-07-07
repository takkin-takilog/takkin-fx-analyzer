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
from bokeh.models.widgets import Slider, Button
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
        self.__DISP_NUM = 300

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
            "テクニカル指標"
        ]

        # Widgetセレクト（通貨ペア）
        INST_OPT = [
            self.INST_USDJPY, self.INST_EURJPY, self.INST_EURUSD
        ]
        self.__wse_inst = Select(title="通貨ペア:",
                                 value=inst_def,
                                 options=INST_OPT)
        self.__wse_inst.on_change("value", self.__cb_wse_inst)

        # Widgetセレクト（期間）
        GRAN_OPT = [
            self.GRAN_W, self.GRAN_D, self.GRAN_H12, self.GRAN_H8,
            self.GRAN_H6, self.GRAN_H4, self.GRAN_H2, self.GRAN_H1,
            self.GRAN_M30, self.GRAN_M15, self.GRAN_M10, self.GRAN_M5,
            self.GRAN_M1
        ]

        self.__wse_gran = Select(title="期間:",
                                 value=gran_def,
                                 options=GRAN_OPT)
        self.__wse_gran.on_change("value", self.__cb_wse_gran)

        # Widgetセレクト（表示モード）
        self.__wse_mode = Select(title="表示モード:",
                                 value=self.__MODE_LIST[0],
                                 options=self.__MODE_LIST)
        self.__wse_mode.on_change("value", self.__cb_wse_mode)
        self.__mode = self.__MODE_LIST[0]

        # Widgetセレクト（テクニカル指標）
        TECH_OPT = [
            "単純移動平均",
            "MACD",
            "ボリンジャーバンド",
        ]
        self.__wse_tech = Select(title="テクニカル指標",
                                 value=TECH_OPT[0],
                                 options=TECH_OPT,
                                 width=200)
        self.__wse_tech.on_change("value", self.__cb_wse_tech)

        # Checkbox Group
        self.__ckbxgr_tech = CheckboxGroup(labels=TECH_OPT, active=[0, 1])

        # ----------テクニカル指標----------
        # 単純移動平均
        defsho = cfg.get_conf(cfg.SEC_SMA, cfg.ITEM_SHO)
        self.__sldtecma_s = Slider(start=1, end=100, value=defsho,
                                   step=1, title="SMA S")
        self.__sldtecma_s.on_change('value', self.__cb_sldtecma_s)

        defmid = cfg.get_conf(cfg.SEC_SMA, cfg.ITEM_MID)
        self.__sldtecma_m = Slider(start=1, end=100, value=defmid,
                                   step=1, title="SMA M")
        self.__sldtecma_m.on_change('value', self.__cb_sldtecma_m)

        deflon = cfg.get_conf(cfg.SEC_SMA, cfg.ITEM_LON)
        self.__sldtecma_l = Slider(start=1, end=100, value=deflon,
                                   step=1, title="SMA L")
        self.__sldtecma_l.on_change('value', self.__cb_sldtecma_l)

        self.__btntecma_ok = Button(label="OK", button_type="success")
        self.__btntecma_cncl = Button(label="cancel", button_type="default")

        # 初期設定
        self.__inst = self.__INST_DICT[inst_def]
        self.__gran = self.__GRAN_DICT[gran_def]

        gmtstr_, gmtend_ = self.__get_period(self.__gran, self.__DISP_NUM)
        self.__gmtstr = gmtstr_
        self.__gmtend = gmtend_

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

    def __get_period(self, gran, num):
        """"チャートを描写する期間を取得する[get period of chart]
        引数[Args]:
            gran (str) : ローソク足の時間足[granularity of a candlestick]
            num (int) : ローソクの表示本数[number of drawn candlestick]
        戻り値[Returns]:
            dtmstr (DateTimeManager) : 開始日時[start date]
            dtmend (DateTimeManager) : 終了日時[end date]
        """
        # 現在時刻を取得
        dtm = DateTimeManager(datetime.now())
        now_ = dtm.tokyo
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

    def __cb_wse_inst(self, attr, old, new):
        """Widgetセレクト（通貨ペア）コールバックメソッド
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old value
            new (str) : New value
        戻り値[Returns]:
            None
        """
        self.__inst = self.__INST_DICT[new]
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

    def __cb_wse_gran(self, attr, old, new):
        """Widgetセレクト（期間）コールバックメソッド
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old value
            new (str) : New value
        戻り値[Returns]:
            なし[None]
        """
        self.__gran = self.__GRAN_DICT[new]
        gmtstr_, gmtend_ = self.__get_period(self.__gran, self.__DISP_NUM)
        self.__gmtstr = gmtstr_
        self.__gmtend = gmtend_
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

    def __cb_wse_mode(self, attr, old, new):
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
            self.__set_layout_tech()
            self.__mode = self.__MODE_LIST[1]
            self.__cs.clear_orders_vline()
            self.__opord.clear()
            self.__oppos.clear()

    def __cb_wse_tech(self, attr, old, new):
        pass

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

    def __cb_sldtecma_s(self, attr, old, new):
        cfg.set_conf(cfg.SEC_SMA, cfg.ITEM_SHO, new)
        cfg.write()

    def __cb_sldtecma_m(self, attr, old, new):
        cfg.set_conf(cfg.SEC_SMA, cfg.ITEM_MID, new)
        cfg.write()

    def __cb_sldtecma_l(self, attr, old, new):
        cfg.set_conf(cfg.SEC_SMA, cfg.ITEM_LON, new)
        cfg.write()

    def __chart_layout(self):
        opord = self.__opord.widget
        oppos = self.__oppos.widget
        opbk = row(children=[opord, oppos], sizing_mode='fixed')

        chrt = self.__cs.fig_main
        rang = self.__cs.fig_range
        chgp = gridplot(
            [
                [opbk, chrt],
                [None, rang],
            ], sizing_mode='stretch_width', merge_tools=False)

        return chgp

    def get_layout(self):
        """レイアウトを取得する[get layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        w1 = self.__wse_inst
        w2 = self.__wse_gran
        w3 = self.__wse_mode

        widsel1 = row(children=[w1, w2], width=300)
        widsel2 = row(children=[w3], width=1000)

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

    def __set_layout_tech(self):

        chrt = self.__cs.fig_main
        rang = self.__cs.fig_range

        chrtset = column(children=[chrt, rang], sizing_mode='stretch_width')

        cbgt = self.__ckbxgr_tech
        tech = self.__wse_tech
        para = column(children=[self.__sldtecma_l,
                                self.__sldtecma_m,
                                self.__sldtecma_s
                                ])
        btn = row(children=[self.__btntecma_cncl,
                            self.__btntecma_ok
                            ], width=200)
        techpara = column(
            children=[cbgt, tech, para, btn], sizing_mode='fixed')

        chartlay = row(children=[techpara, chrtset],
                       sizing_mode='stretch_width')

        self.__layout.children[1] = chartlay
