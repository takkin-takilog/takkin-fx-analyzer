from bokeh.io import show
from bokeh.layouts import gridplot, row
from bokeh.models import CustomJS, Div
from bokeh.models.widgets import Select, TextInput
from bokeh import events
from datetime import datetime, timedelta
from oandapyV20.exceptions import V20Error
import autotrader.candlestick_chart as cd
import autotrader.oders as od
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
        """"コンストラクタ[Constructor]
        引数[Args]:
            inst_def (str) : 通貨ペア[instrument]
            gran_def (str) : ローソク足の時間足[granularity of a candlestick]
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

        self.__text_input = TextInput(value="default", title="Label:")

        self.__inst = self.__INST_DICT[inst_def]
        self.__gran = self.__GRAN_DICT[gran_def]

        from_, to_ = self.__get_period(self.__gran, self.__DISP_NUM)
        self.__dt_to = to_
        self.__dt_from = from_

        self.__wicdl = cd.CandleStick()
        self.__widord = od.Orders()
        try:
            self.__wicdl.fetch(self.__gran, self.__inst,
                               self.__dt_from, self.__dt_to)
        except V20Error as v20err:
            print("-----V20Error: {}".format(v20err))
        except ConnectionError as cerr:
            print("----- ConnectionError: {}".format(cerr))
        except Exception as err:
            print("----- ExceptionError: {}".format(err))

    def __get_period(self, gran, num):
        """"チャートを描写する期間を取得する[get period of chart]
        引数[Args]:
            gran (str) : ローソク足の時間足[granularity of a candlestick]
            num (int) : ローソクの表示本数[number of drawn candlestick]
        戻り値[Returns]:
            from_ (datetime) : 開始日時[from date]
            to_ (datetime) : 終了日時[to date]
        """
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

        return from_, to_

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
            self.__wicdl.fetch(self.__gran, self.__inst,
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
        from_, to_ = self.__get_period(self.__gran, self.__DISP_NUM)
        self.__dt_to = to_
        self.__dt_from = from_
        try:
            self.__wicdl.fetch(self.__gran, self.__inst,
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
                args.push(attrs[i] + '=' + date.getFullYear() + "/" + date.getMonth() + "/" + date.getDate() + " " + date.getHours() + ":" + date.getMinutes());
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

    def __callback_tap(self, event):
        # NOTE: read timestamp is Not mutches disp one.

        print("--------update")
        yrng = self.__wicdl.get_widget_yrng()
        print(yrng)
        self.__widord.update_yrange(yrng)
        print("--------end")

        date = datetime.fromtimestamp(int(event.x) / 1000)
        str_ = str(date) + ":" + str(event.y)
        self.__text_input.value = "Tap: " + str_

        """
        order, posi = self.__widord.get_widget()
        chart, rang = self.__wicdl.get_widget()
        order.y_range.start = chart.y_range.start
        order.y_range.end = chart.y_range.end
        posi.y_range.start = chart.y_range.start
        posi.y_range.end = chart.y_range.end
        """

        #yrng = self.__wicdl.get_widget_yrng()
        #print(yrng)

        # fetch Open Order and Position
        dt_ = datetime(year=2017, month=2, day=1,
                       hour=12, minute=0, second=0)
        self.__widord.fetch(self.__inst, dt_)

    def __callback_press(self, event):
        date = datetime.fromtimestamp(int(event.x) / 1000)
        str_ = str(date) + ":" + str(event.y)
        self.__text_input.value = "Press: " + str_

    def get_layout(self):
        """レイアウトを取得する[get layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        w1 = self.__widsel_inst
        w2 = self.__widsel_gran

        wbox1 = row(children=[w1, w2])
        chart, rang = self.__wicdl.get_widget()
        order, posi = self.__widord.get_widget()

        point_events = [
            events.Tap, events.DoubleTap, events.Press,
            events.MouseMove, events.MouseEnter, events.MouseLeave
        ]
        point_attributes = ['x', 'y', 'sx', 'sy']  # Point events
        div = Div(width=400, height=400, height_policy="fixed")

        for event in point_events:
            chart.js_on_event(event, self.__callback_disp(
                div, attributes=point_attributes))

        chart.on_event(events.Tap, self.__callback_tap)
        chart.on_event(events.Press, self.__callback_press)

        chartlay = gridplot(
            [
                [order, posi, chart, div],
                [None, None, rang],
            ],
            merge_tools=False)

        layout = gridplot(
            [
                [wbox1],
                [chartlay],
                [self.__text_input]
            ],
            merge_tools=False)

        return(layout)

    def view(self):
        """描写する[view]
        引数[Args]:
            None
        戻り値[Returns]:
            None
        """
        show(self.get_layout())
