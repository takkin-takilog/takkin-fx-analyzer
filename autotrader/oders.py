from abc import ABCMeta
from bokeh.models import ColumnDataSource
from bokeh.models.glyphs import HBar, Line
from bokeh.plotting import figure
from oandapyV20 import API
from retrying import retry
from datetime import datetime
from autotrader.oanda_common import OandaEnv
from autotrader.bokeh_common import ToolType
import oandapyV20.endpoints.instruments as it
import pandas as pd
import autotrader.oanda_account as oa


class OpenBooksAbs(metaclass=ABCMeta):
    """ OpenBooksAbs - OpenBooks抽象クラス"""

    # Hbar Label
    YPR = "y"
    XCP = "x"

    # Line Label
    Y = "y"
    X = "x"

    def __init__(self, yrng):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__ORD_BOOK = "orderBook"

        self.__BG_COLOR = "#2E2E2E"
        self.__BAR_R_COLOR = "#00A4BD"
        self.__BAR_L_COLOR = "#FF8400"
        self.__CURPRI_COLOR = "#7DA900"

        self.__CUTTH = 50  # 現レートから上下何本残すか
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
                            title="Orders",
                            background_fill_color=self.__BG_COLOR)
        self.__plt.grid.grid_line_alpha = 0.3
        self.__plt.xaxis.axis_label = "Count Percent[%]"
        self.__plt.yaxis.axis_label = "Price"
        self.__plt.toolbar_location = None

        # 水平バー（順張り）
        self.__srchbarf = ColumnDataSource({self.YPR: [],
                                            self.XCP: []})
        self.__glyhbarf = HBar(y=self.YPR,
                               left=0,
                               right=self.XCP,
                               height=0.03,
                               fill_color=self.__BAR_R_COLOR)
        self.__plt.add_glyph(self.__srchbarf,
                             self.__glyhbarf)

        # 水平バー（逆張り）
        self.__srchbarc = ColumnDataSource({self.YPR: [],
                                            self.XCP: []})
        self.__glyhbarc = HBar(y=self.YPR,
                               left=self.XCP,
                               right=0,
                               height=0.03,
                               fill_color=self.__BAR_R_COLOR)
        self.__plt.add_glyph(self.__srchbarc, self.__glyhbarc)

        # 水平ライン
        self.__srcline = ColumnDataSource({self.X: [],
                                           self.Y: []})
        self.__glyline = Line(x=self.X,
                              y=self.Y,
                              line_color=self.__CURPRI_COLOR,
                              line_width=3)
        self.__plt.add_glyph(self.__srcline, self.__glyline)

    def get_params(self, dt_):

        params_ = {
            "time": dt_.gmt.strftime(self.__DT_FMT),
        }
        return params_

    def fetch(self, label, iob):

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
        dfhi = df[self.__LONG][(df.index > price)]
        dflo = df[self.__SHORT][(df.index < price)]
        df_follow = pd.concat([dfhi, -dflo])
        self.__srchbarf = {self.YPR: df.index,
                           self.XCP: df_follow}
        print("順張り側DataFrame") #TODO: ラベルの振り方
        print(df_follow)

        # 逆張り側DataFrame
        dfhi = df[self.__SHORT][(df.index > price)]
        dflo = df[self.__LONG][(df.index < price)]
        df_contrarian = pd.concat([-dfhi, dflo])
        self.__srchbarc = {self.YPR: df.index,
                           self.XCP: df_contrarian}

        # 現在価格ライン
        self.__srcline = {self.X: [-self.__X_AXIS_MAX, self.__X_AXIS_MAX],
                          self.Y: [price, price]}

    def update_yrange(self, yrng):
        self.__plt.y_range.update(start=yrng[0], end=yrng[1])

    @property
    def widget(self):
        """"ウィジェット取得[get widget]
        引数[Args]:
            None
        """
        return self.__plt


class OpenOrders(OpenBooksAbs):

    def __init__(self, yrng):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__LABEL = "orderBook"
        super().__init__(yrng)

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def fetch(self, inst, dt_):

        params_ = super().get_params(dt_)

        # APIへ過去データをリクエスト
        iob = it.InstrumentsOrderBook(instrument=inst,
                                      params=params_)
        super().fetch(self.__LABEL, iob)

    def update_yrange(self, yrng):
        super().update_yrange(yrng)

    @property
    def widget(self):
        return super().widget


class OpenPositions(OpenBooksAbs):

    def __init__(self, yrng):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__LABEL = "positionBook"
        super().__init__(yrng)

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def fetch(self, inst, dt_):

        params_ = super().get_params(dt_)

        # APIへ過去データをリクエスト
        iob = it.InstrumentsPositionBook(instrument=inst,
                                         params=params_)
        super().fetch(self.__LABEL, iob)

    def update_yrange(self, yrng):
        super().update_yrange(yrng)

    @property
    def widget(self):
        return super().widget


class Orders(object):

    def __init__(self, yrng):
        """"コンストラクタ[Constructor]
        引数[Args]:
            None
        """
        self.__ORD_BOOK = "orderBook"

        self.__BG_COLOR = "#2E2E2E"
        self.__BAR_R_COLOR = "#00A4BD"
        self.__BAR_L_COLOR = "#FF8400"
        self.__CURPRI_COLOR = "#7DA900"

        self.__CUT_TH = 50  # 現レートから上下何本残すか
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

        # ---------- Orders ----------
        self.__pltodr = figure(
            plot_height=400,
            plot_width=200,
            x_range=(-self.__X_AXIS_MAX, self.__X_AXIS_MAX),
            y_range=yrng,
            tools=tools_,
            title="Orders",
            background_fill_color=self.__BG_COLOR
        )
        self.__pltodr.grid.grid_line_alpha = 0.3
        self.__pltodr.xaxis.axis_label = "Count Percent[%]"
        self.__pltodr.yaxis.axis_label = "Price"
        self.__pltodr.toolbar_location = None

        # ---------- Position ----------
        self.__pltpos = figure(
            plot_height=400,
            plot_width=200,
            x_range=(-self.__X_AXIS_MAX, self.__X_AXIS_MAX),
            y_range=yrng,
            tools=tools_,
            title="Position",
            background_fill_color=self.__BG_COLOR
        )
        self.__pltpos.grid.grid_line_alpha = 0.3
        self.__pltpos.xaxis.axis_label = "Count Percent[%]"
        self.__pltpos.yaxis.axis_label = "Price"
        self.__pltpos.toolbar_location = None

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def fetch(self, inst, dtmmin):

        jpdt = dtmmin.gmt

        params_ = {
            "time": jpdt.strftime(self.__DT_FMT),
        }

        # APIへ過去データをリクエスト
        ic_ord = it.InstrumentsOrderBook(instrument=inst,
                                         params=params_)
        self.__fetch(self.__ORD_BOOK, ic_ord, self.__pltodr)

        # APIへ過去データをリクエスト
        ic_pos = it.InstrumentsPositionBook(instrument=inst,
                                            params=params_)
        self.__fetch(self.__POS_BOOK, ic_pos, self.__pltpos)

    def __fetch(self, label, ic, plt):

        self.__api.request(ic)

        self.__data = []
        for raw in ic.response[label][self.__BUCKETS]:
            self.__data.append([float(raw[self.__PRICE]),
                                float(raw[self.__LONG]),
                                float(raw[self.__SHORT])])

        # convert List to pandas data frame
        df = pd.DataFrame(self.__data)
        df.columns = [self.__PRICE,
                      self.__LONG,
                      self.__SHORT]
        df = df.set_index(self.__PRICE).sort_index(ascending=False)
        """
        pd.to_datetime(self.__changeDateTimeFmt(
            ic.response[label][self.__TIME]))
        """
        cur_price = float(ic.response[label][self.__CUR_PRICE])
        bucket_width = float(ic.response[label][self.__BUCKET_WIDTH])
        idx_th = bucket_width * self.__CUT_TH
        dfpos = df[(df.index > cur_price - idx_th)
                   & (df.index < cur_price + idx_th)]
        df = df[(df.index > cur_price - idx_th)
                & (df.index < cur_price + idx_th)]
        df_up = dfpos[self.__LONG][(dfpos.index > cur_price)]
        df_lo = -dfpos[self.__SHORT][(dfpos.index < cur_price)]
        df_right = pd.concat([df_up, df_lo])

        df_up = -dfpos[self.__SHORT][(dfpos.index > cur_price)]
        df_lo = dfpos[self.__LONG][(dfpos.index < cur_price)]
        df_left = pd.concat([df_up, df_lo])

        plt.hbar(y=dfpos.index, height=0.03, left=df_right,
                 right=0, color=self.__BAR_R_COLOR)
        plt.hbar(y=dfpos.index, height=0.03, left=df_left,
                 right=0, color=self.__BAR_L_COLOR)
        plt.line(x=[-self.__X_AXIS_MAX, self.__X_AXIS_MAX],
                 y=[cur_price, cur_price],
                 color=self.__CURPRI_COLOR, line_width=3)

    def update_yrange(self, yrng):
        self.__pltodr.y_range.update(start=yrng[0], end=yrng[1])
        self.__pltpos.y_range.update(start=yrng[0], end=yrng[1])

    def get_widget(self):
        """"ウィジェット取得[get widget]
        引数[Args]:
            None
        """
        return self.__pltodr, self.__pltpos

    def __changeDateTimeFmt(self, dt):
        """"日付フォーマットの変換メソッド
        引数:
            dt (str): DT_FMT形式でフォーマットされた日付
        戻り値:
            tf_dt (str): 変換後の日付
        """
        tdt = datetime.strptime(dt, self.__DT_FMT)

        return tdt
