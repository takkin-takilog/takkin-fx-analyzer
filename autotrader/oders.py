from bokeh.plotting import figure
from oandapyV20 import API
from retrying import retry
from datetime import datetime, timedelta
from autotrader.oanda_common import OandaEnv
from autotrader.bokeh_common import ToolType
import oandapyV20.endpoints.instruments as it
import pandas as pd
import autotrader.oanda_account as oa


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
    def fetch(self, inst, dt_):

        jpdt = dt_ - timedelta(hours=9)

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
        # date型を整形する
        pd.to_datetime(self.__changeDateTimeFmt(
            ic.response[label][self.__TIME]))
        cur_price = float(ic.response[label][self.__CUR_PRICE])
        bucket_width = float(ic.response[label][self.__BUCKET_WIDTH])
        idx_th = bucket_width * self.__CUT_TH
        dfpos = df[(df.index > cur_price - idx_th)
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
