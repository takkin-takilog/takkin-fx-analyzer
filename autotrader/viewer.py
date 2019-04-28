from bokeh.io import show
from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.models import CustomJS, Div
from bokeh.models.widgets import Select
from bokeh import events
from datetime import datetime, timedelta
import autotrader.candlestick_chart as cdl
import autotrader.oanda_common as oc
from oandapyV20.exceptions import V20Error


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
        self.__DISP_NUM = 100

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
            self.GRAN_W, self.GRAN_D, self.GRAN_H12, self.GRAN_H8,
            self.GRAN_H6, self.GRAN_H4, self.GRAN_H2, self.GRAN_H1,
            self.GRAN_M30, self.GRAN_M15, self.GRAN_M10, self.GRAN_M5,
            self.GRAN_M1
        ]

        self.__widsel_gran = Select(title="期間:",
                                    value=gran_def,
                                    options=GRAN_OPS)
        self.__widsel_gran.on_change("value", self.__sel_gran_callback)

        self.__inst = self.__INST_DICT[inst_def]
        self.__gran = self.__GRAN_DICT[gran_def]

        to_, from_ = self.__get_gran(self.__gran, self.__DISP_NUM)
        self.__dt_to = to_
        self.__dt_from = from_

        self.__widcs = cdl.CandleStick()
        try:
            self.__widcs.fetch(self.__gran, self.__inst,
                               self.__dt_from, self.__dt_to)
        except V20Error as v20err:
            print("-----V20Error: {}".format(v20err))
        except ConnectionError as cerr:
            print("----- ConnectionError: {}".format(cerr))
        except Exception as err:
            print("----- ExceptionError: {}".format(err))

    def __get_gran(self, gran, num):

        # 標準時の現在時刻を取得
        now_ = datetime.now() - timedelta(hours=9)
        to_ = datetime(now_.year, now_.month, now_.day,
                       now_.hour, now_.minute, now_.second)

        if gran is oc.OandaGrn.D:
            from_ = to_ - timedelta(days=num)
        elif gran is oc.OandaGrn.H12:
            from_ = to_ - timedelta(hours=num * 12)
        elif gran is oc.OandaGrn.H8:
            from_ = to_ - timedelta(hours=num * 8)
        elif gran is oc.OandaGrn.H6:
            from_ = to_ - timedelta(hours=num * 6)
        elif gran is oc.OandaGrn.H4:
            from_ = to_ - timedelta(hours=num * 4)
        elif gran is oc.OandaGrn.H3:
            from_ = to_ - timedelta(hours=num * 3)
        elif gran is oc.OandaGrn.H2:
            from_ = to_ - timedelta(hours=num * 2)
        elif gran is oc.OandaGrn.H1:
            from_ = to_ - timedelta(hours=num)
        elif gran is oc.OandaGrn.M30:
            from_ = to_ - timedelta(minutes=num * 30)
        elif gran is oc.OandaGrn.M15:
            from_ = to_ - timedelta(minutes=num * 15)
        elif gran is oc.OandaGrn.M10:
            from_ = to_ - timedelta(minutes=num * 10)
        elif gran is oc.OandaGrn.M5:
            from_ = to_ - timedelta(minutes=num * 5)
        elif gran is oc.OandaGrn.M4:
            from_ = to_ - timedelta(minutes=num * 4)
        elif gran is oc.OandaGrn.M3:
            from_ = to_ - timedelta(minutes=num * 3)
        elif gran is oc.OandaGrn.M2:
            from_ = to_ - timedelta(minutes=num * 2)
        elif gran is oc.OandaGrn.M1:
            from_ = to_ - timedelta(minutes=num)

        return to_, from_

    def __sel_inst_callback(self, attr, old, new):
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
            self.__widcs.fetch(self.__gran, self.__inst,
                               self.__dt_from, self.__dt_to)
        except V20Error as v20err:
            print("-----V20Error: {}".format(v20err))
        except ConnectionError as cerr:
            print("----- ConnectionError: {}".format(cerr))
        except Exception as err:
            print("----- ExceptionError: {}".format(err))

    def __sel_gran_callback(self, attr, old, new):
        """Widgetセレクト（期間）コールバックメソッド
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old value
            new (str) : New value
        戻り値[Returns]:
            なし[None]
        """
        self.__gran = self.__GRAN_DICT[new]
        to_, from_ = self.__get_gran(self.__gran, self.__DISP_NUM)
        self.__dt_to = to_
        self.__dt_from = from_
        try:
            self.__widcs.fetch(self.__gran, self.__inst,
                               self.__dt_from, self.__dt_to)
        except V20Error as v20err:
            print("-----V20Error: {}".format(v20err))
        except ConnectionError as cerr:
            print("----- ConnectionError: {}".format(cerr))
        except Exception as err:
            print("----- ExceptionError: {}".format(err))

    def __callback_disp(self, div, attributes=[],
                        style='float:left;clear:left;font_size=10pt'):
        return CustomJS(args=dict(div=div), code="""
        var attrs = %s; var args = [];
        for (var i = 0; i<attrs.length; i++) {
            if (attrs[i] == "x") {
                var date = new Date(cb_obj[attrs[i]])
                args.push(attrs[i] + '=' + date.getFullYear() + "/" + date.getMonth() + "/" + date.getDate());
            }else{
                args.push(attrs[i] + '=' + Number(cb_obj[attrs[i]]).toFixed(2));
            }
        }
        var line = "<span style=%r><b>" + cb_obj.event_name + "</b>(" + args.join(", ") + ")</span>\\n";
        var text = div.text.concat(line);
        var lines = text.split("\\n")
        if (lines.length > 20)
            lines.shift();
        div.text = lines.join("\\n");
    """ % (attributes, style))

    def get_layout(self):
        w1 = self.__widsel_inst
        w2 = self.__widsel_gran

        wbox1 = row(children=[w1, w2])
        fig = self.__widcs.get_widget()

        point_events = [
            events.Tap, events.DoubleTap, events.Press,
            events.MouseMove, events.MouseEnter, events.MouseLeave
        ]
        point_attributes = ['x', 'y', 'sx', 'sy']  # Point events
        div = Div(width=400, height=fig.plot_height, height_policy="fixed")

        for event in point_events:
            fig.js_on_event(event, self.__callback_disp(
                div, attributes=point_attributes))

        layout = gridplot(
            [
                [wbox1],
                [fig, div],
            ],
            merge_tools=False)

        return(layout)

    def view(self):
        show(self.get_layout())
