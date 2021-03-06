from abc import ABCMeta
import pandas as pd
from retrying import retry
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.glyphs import HBar, Line
from bokeh.plotting import figure
import oandapyV20.endpoints.instruments as it
from oandapyV20 import API
import analyzer.oanda_account as oa
from analyzer.oanda_common import OandaEnv
from analyzer.bokeh_common import ToolType


class OpenBooksAbs(metaclass=ABCMeta):
    """ OpenBooksAbs - OpenBooks抽象クラス"""

    # Hbar Label
    YPR = "y"
    XCP = "x"

    # Line Label
    Y = "y"
    X = "x"

    def __init__(self, title_, yrng):
        """"コンストラクタ[Constructor]
        引数[Args]:
            title_ (str) : フィギュアタイトル[figure title]
            yrng (tuple) : Y軸の最小値、最大値 (min, max)
                           [Y range min and max]
        """
        self.__BG_COLOR = "#2E2E2E"
        self.__BAR_F_COLOR = "#00A4BD"
        self.__BAR_C_COLOR = "#FF8400"
        self.__CURPRI_COLOR = "#7DA900"

        self.__HEIGHT = 0.8
        self.__CUTTH = 300  # 現レートから上下何本残すか
        self.__X_AXIS_MAX = 2.5  # X軸レンジ

        self.__DT_FMT = "%Y-%m-%dT%H:%M:00Z"

        self.__POS_BOOK = "positionBook"
        self.__BUCKETS = "buckets"
        self.__PRICE = "price"
        self.__LONG = "longCountPercent"
        self.__SHORT = "shortCountPercent"

        self.__TIME = "time"
        self.__CUR_PRICE = "price"
        self.__BUCKET_WIDTH = "bucketWidth"

        self.__api = API(access_token=oa.ACCESS_TOKEN,
                         environment=OandaEnv.PRACTICE)

        tools_ = ToolType.gen_str(ToolType.XPAN,
                                  ToolType.WHEEL_ZOOM,
                                  ToolType.BOX_ZOOM,
                                  ToolType.RESET,
                                  ToolType.SAVE)

        self.__plt = figure(plot_height=400,
                            plot_width=200,
                            x_range=(-self.__X_AXIS_MAX, self.__X_AXIS_MAX),
                            y_range=yrng,
                            tools=tools_,
                            title=title_,
                            background_fill_color=self.__BG_COLOR)
        self.__plt.grid.grid_line_alpha = 0.3
        self.__plt.xaxis.axis_label = "Count Percent[%]"
        self.__plt.yaxis.axis_label = "Price"
        self.__plt.toolbar_location = None
        self.__plt.yaxis.visible = False  # y軸を非表示にする

        # 水平バー（順張り）
        self.__srchbarf = ColumnDataSource({self.YPR: [],
                                            self.XCP: []})
        self.__glyhbarf = HBar(y=self.YPR,
                               left=0,
                               right=self.XCP,
                               height=0.03,
                               fill_color=self.__BAR_F_COLOR,
                               line_alpha=0)
        renf = self.__plt.add_glyph(self.__srchbarf,
                                    self.__glyhbarf)

        # 水平バー（逆張り）
        self.__srchbarc = ColumnDataSource({self.YPR: [],
                                            self.XCP: []})
        self.__glyhbarc = HBar(y=self.YPR,
                               left=self.XCP,
                               right=0,
                               height=0.03,
                               fill_color=self.__BAR_C_COLOR,
                               line_alpha=0)
        renc = self.__plt.add_glyph(self.__srchbarc,
                                    self.__glyhbarc)

        # 水平ライン
        self.__srcline = ColumnDataSource({self.X: [],
                                           self.Y: []})
        self.__glyline = Line(x=self.X,
                              y=self.Y,
                              line_color=self.__CURPRI_COLOR,
                              line_width=1)
        self.__plt.add_glyph(self.__srcline, self.__glyline)

        # Tool
        hover = HoverTool()
        hover.tooltips = [("price", "@" + self.YPR),
                          ("percent", "@" + self.XCP + " %")]
        hover.renderers = [renf, renc]
        self.__plt.add_tools(hover)

    def get_params(self, dt_):
        """"OANDA-APIリクエストのためのパラメータを取得する[Constructor]
        引数[Args]:
            dt_ (DateTimeManager) : 日時[Date time]
        戻り値[Returns]:
            params_ (dict) : パラメータ[Parameter]
        """
        params_ = {
            "time": dt_.gmt.strftime(self.__DT_FMT),
        }
        return params_

    def fetch(self, label, iob):
        """"オープンオーダー＆ポジション情報を取得する
            [fetch open orders & positions]
        引数[Args]:
            label (str) : ラベル[label]
            iob (InstrumentsOrderBook) : iob
        戻り値[Returns]:
            なし[None]
        """
        self.__api.request(iob)

        self.__data = []
        for raw in iob.response[label][self.__BUCKETS]:
            self.__data.append([float(raw[self.__PRICE]),
                                float(raw[self.__LONG]),
                                float(raw[self.__SHORT])])

        # convert List to Pandas Data Frame
        df = pd.DataFrame(self.__data)
        df.columns = [self.__PRICE,
                      self.__LONG,
                      self.__SHORT]
        df = df.set_index(self.__PRICE).sort_index(ascending=False)

        # 現在価格をフェッチ[fetch current price]
        price = float(iob.response[label][self.__CUR_PRICE])

        # 価格間のレンジをフェッチ[fetch partition of the instrument's prices]
        width = float(iob.response[label][self.__BUCKET_WIDTH])

        # 範囲を絞る[narrow down price scope]
        idxth = width * self.__CUTTH
        df = df[(df.index > price - idxth)
                & (df.index < price + idxth)]

        # 順張り側DataFrame
        srhi = df[self.__LONG][(df.index > price)]
        srlo = df[self.__SHORT][(df.index < price)]
        df_fol = pd.concat([srhi, -srlo])
        self.__srchbarf.data = {self.YPR: df_fol.index.tolist(),
                                self.XCP: df_fol.tolist()}
        self.__glyhbarf.height = width * self.__HEIGHT

        # 逆張り側DataFrame
        srhi = df[self.__SHORT][(df.index > price)]
        srlo = df[self.__LONG][(df.index < price)]
        df_con = pd.concat([-srhi, srlo])
        self.__srchbarc.data = {self.YPR: df_con.index.tolist(),
                                self.XCP: df_con.tolist()}
        self.__glyhbarc.height = width * self.__HEIGHT

        # 現在価格ライン
        self.__srcline.data = {self.X: [-self.__X_AXIS_MAX, self.__X_AXIS_MAX],
                               self.Y: [price, price]}

    def update_yrange(self, yrng):
        """"ウィジェット取得[get widget]
        引数[Args]:
            yrng (tuple) : Y軸の最小値、最大値 (min, max)
                           [Y range min and max]
        戻り値[Returns]:
            なし[None]
        """
        self.__plt.y_range.update(start=yrng[0], end=yrng[1])

    @property
    def widget(self):
        """"ウィジェット取得[get widget]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            plt (figure) : フィギュアオブジェクト[figure object]
        """
        return self.__plt

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        self.__srchbarf.data = {self.YPR: [],
                                self.XCP: []}
        self.__srchbarc.data = {self.YPR: [],
                                self.XCP: []}
        self.__srcline.data = {self.X: [],
                               self.Y: []}


class OpenOrders(OpenBooksAbs):

    def __init__(self, yrng):
        """"コンストラクタ[Constructor]
        引数[Args]:
            yrng (tuple) : Y軸の最小値、最大値 (min, max)
                           [Y range min and max]
        """
        self.__LABEL = "orderBook"
        self.__TITLE = "Orders"
        super().__init__(self.__TITLE, yrng)

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def fetch(self, inst, dt_):
        """"オープンオーダー情報を取得する[fetch open orders]
        引数[Args]:
            inst (str) : 通貨ペア[instrument]
            dt_ (DateTimeManager) : 日付[date time]
        戻り値[Returns]:
            なし[None]
        """
        params_ = super().get_params(dt_)

        iob = it.InstrumentsOrderBook(instrument=inst,
                                      params=params_)
        super().fetch(self.__LABEL, iob)

    def update_yrange(self, yrng):
        """"Y軸範囲を更新する[update Y axis range]
        引数[Args]:
            yrng (tuple) : Y軸の最小値、最大値 (min, max)
                           [Y range min and max]
        戻り値[Returns]:
            なし[None]
        """
        super().update_yrange(yrng)

    @property
    def widget(self):
        """"ウィジェットを取得する[get widget]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        return super().widget


class OpenPositions(OpenBooksAbs):

    def __init__(self, yrng):
        """"コンストラクタ[Constructor]
        引数[Args]:
            yrng (tuple) : Y軸の最小値、最大値 (min, max)
                           [Y range min and max]
        """
        self.__LABEL = "positionBook"
        self.__TITLE = "Positions"
        super().__init__(self.__TITLE, yrng)

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def fetch(self, inst, dt_):
        """"オープンポジション情報を取得する[fetch openpositions]
        引数[Args]:
            inst (str) : 通貨ペア[instrument]
            dt_ (DateTimeManager) : 日付[date time]
        戻り値[Returns]:
            なし[None]
        """
        params_ = super().get_params(dt_)

        iob = it.InstrumentsPositionBook(instrument=inst,
                                         params=params_)
        super().fetch(self.__LABEL, iob)

    def update_yrange(self, yrng):
        """"Y軸範囲を更新する[update Y axis range]
        引数[Args]:
            yrng (tuple) : Y軸の最小値、最大値 (min, max)
                           [Y range min and max]
        戻り値[Returns]:
            なし[None]
        """
        super().update_yrange(yrng)

    @property
    def widget(self):
        """"ウィジェットを取得する[get widget]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        return super().widget
