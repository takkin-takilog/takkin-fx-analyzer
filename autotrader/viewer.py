from bokeh.io import show
from bokeh.layouts import gridplot
from bokeh.models.widgets import Select, TextInput
import datetime
import autotrader.candlestick_chart as cdl
import autotrader.oanda_common as oc


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
        """"コンストラクタ
        Args:
            None
        """

        self.__dt_from = datetime.datetime(
            year=2018, month=1, day=1, hour=0, minute=0, second=0)
        self.__dt_to = datetime.datetime(
            year=2019, month=2, day=1, hour=12, minute=0, second=0)

        # 辞書登録：通貨ペア
        self.__INST_DICT = {
            self.INST_USDJPY: oc.OandaIns.USD_JPY,
            self.INST_EURJPY: oc.OandaIns.EUR_JPY,
            self.INST_EURUSD: oc.OandaIns.EUR_USD
        }

        # 辞書登録：時間足
        self.__GRAN_DICT = {
            self.GRAN_S5: oc.OandaGrn.S5,
            self.GRAN_S10: oc.OandaGrn.S10,
            self.GRAN_S15: oc.OandaGrn.S15,
            self.GRAN_S30: oc.OandaGrn.S30,
            self.GRAN_M1: oc.OandaGrn.M1,
            self.GRAN_M2: oc.OandaGrn.M2,
            self.GRAN_M3: oc.OandaGrn.M3,
            self.GRAN_M4: oc.OandaGrn.M4,
            self.GRAN_M5: oc.OandaGrn.M5,
            self.GRAN_M10: oc.OandaGrn.M10,
            self.GRAN_M15: oc.OandaGrn.M15,
            self.GRAN_M30: oc.OandaGrn.M30,
            self.GRAN_H1: oc.OandaGrn.H1,
            self.GRAN_H2: oc.OandaGrn.H2,
            self.GRAN_H3: oc.OandaGrn.H3,
            self.GRAN_H4: oc.OandaGrn.H4,
            self.GRAN_H6: oc.OandaGrn.H6,
            self.GRAN_H8: oc.OandaGrn.H8,
            self.GRAN_H12: oc.OandaGrn.H12,
            self.GRAN_D: oc.OandaGrn.D,
            self.GRAN_W: oc.OandaGrn.W
        }

        self.__debug_text_inst = TextInput(value=inst_def, title="debug text:")
        self.__debug_text_gran = TextInput(value=gran_def, title="debug text:")

        # Widgetセレクト（通貨ペア）
        INST_OPS = [
            self.INST_USDJPY, self.INST_EURJPY, self.INST_EURUSD
        ]
        self.__widsel_inst = Select(title="通貨ペア:",
                                    value=inst_def,
                                    options=INST_OPS)
        self.__widsel_inst.on_change("value", self.__sel_inst_callback)

        # Widgetセレクト（期間）
        GRAN_OPS = [
            self.GRAN_S5, self.GRAN_S10, self.GRAN_S15, self.GRAN_S30,
            self.GRAN_M1, self.GRAN_M2, self.GRAN_M3, self.GRAN_M4,
            self.GRAN_M5, self.GRAN_M10, self.GRAN_M15, self.GRAN_M30,
            self.GRAN_H1, self.GRAN_H2, self.GRAN_H3, self.GRAN_H4,
            self.GRAN_H6, self.GRAN_H8, self.GRAN_H12, self.GRAN_D,
            self.GRAN_W
        ]
        self.__widsel_gran = Select(title="期間:",
                                    value=gran_def,
                                    options=GRAN_OPS)
        self.__widsel_gran.on_change("value", self.__sel_gran_callback)

        self.__widcs = cdl.CandleStick()

    def __sel_inst_callback(self, attr, old, new):
        """Widgetセレクト（通貨ペア）コールバックメソッド
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old value
            new (str) : New value
        戻り値[Returns]:
            None
        """
        self.__debug_text_inst.value = new

    def __sel_gran_callback(self, attr, old, new):
        """Widgetセレクト（期間）コールバックメソッド
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old value
            new (str) : New value
        戻り値[Returns]:
            なし[None]
        """
        self.__debug_text_gran.value = new

    def get_layout(self):
        granularity = self.__GRAN_DICT[self.__widsel_gran.value]
        instrument = self.__INST_DICT[self.__widsel_inst.value]
        self.__widcs.fetch(granularity, instrument, self.__dt_from,
                           self.__dt_to)
        layout = gridplot(
            [
                [self.__widsel_inst, self.__widsel_gran],
                [self.__debug_text_inst, self.__debug_text_gran],
                [None, self.__widcs.get_widget(fig_width=1000)],
            ],
            merge_tools=False)
        return(layout)

    def view(self):
        show(self.get_layout())
