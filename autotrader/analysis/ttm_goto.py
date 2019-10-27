import pandas as pd
import jpholiday
import datetime as dt
from bokeh.models import ColumnDataSource, CrosshairTool, HoverTool
from bokeh.models.widgets import Button
from bokeh.models.widgets import TableColumn, DataTable
from bokeh.models.widgets import DateFormatter
from bokeh.layouts import layout, widgetbox, row, column, gridplot
from oandapyV20.exceptions import V20Error
import autotrader.analyzer as ana
import autotrader.utils as utl
import autotrader.analysis.candlestick as cs
from autotrader.utils import DateTimeManager
from autotrader.oanda_common import OandaGrn, OandaIns
from autotrader.analysis.candlestick import CandleStickChartBase
from autotrader.analysis.candlestick import CandleStickData
from autotrader.analysis.candlestick import CandleGlyph


class CandleStickChart(CandleStickChartBase):
    """ CandleStickChart
            - ローソク足チャート定義クラス[Candle stick chart definition class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        # Hbar Label
        self.__Y = "y"
        self.__X = "x"
        self.__CLOSE_COLOR = "#FFEE55"
        self.__OPEN_COLOR = "#54FFEE"

        super().__init__()
        self._fig.title.text = "TTM Candlestick Chart ( 10 minutes )"

        # プロット設定
        self._fig.toolbar_location = "right"
        self._fig.add_tools(CrosshairTool(line_color="pink",
                                          line_alpha=0.5))

        hover = HoverTool()
        hover.formatters = {CandleGlyph.XDT: "datetime"}
        hover.tooltips = [(cs.LBL_TIME, "@" + CandleGlyph.XDT + "{%F %R}"),
                          (cs.LBL_HIGH, "@" + CandleGlyph.YHI),
                          (cs.LBL_OPEN, "@" + CandleGlyph.YOP),
                          (cs.LBL_CLOSE, "@" + CandleGlyph.YCL),
                          (cs.LBL_LOW, "@" + CandleGlyph.YLO)]
        hover.renderers = [self._glyinc.render,
                           self._glydec.render,
                           self._glyequ.render]
        self._fig.add_tools(hover)

    def set_dataframe(self, csd):

        super().set_dataframe(csd)


class TTMGoto(object):
    """ TTMGoto
            - 仲根(TTM)とゴトー日クラス[TTM and Goto day class]
    """

    LBL_WEEK = "week"
    LBL_GOTO = "goto-day"

    _WEEK_DICT = {0: "月", 1: "火", 2: "水", 3: "木",
                  4: "金", 5: "土", 6: "日"}
    _MLT_FIVE_LIST = [5, 10, 15, 20, 25, 30]

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        # Widget Button:解析実行[Run analysis]
        self.__btn_run = Button(label="解析実行",
                                button_type="success",
                                sizing_mode="fixed",
                                default_size=200)
        self.__btn_run.on_click(self.__cb_btn_run)

        cols = [TTMGoto.LBL_WEEK,
                TTMGoto.LBL_GOTO]
        self.__dfsmm = pd.DataFrame(columns=cols)

        # Widget DataTable:
        self.TBLLBL_DATE = "date"
        self.TBLLBL_WEEK = "week"
        self.TBLLBL_GOTO = "goto-day"

        # データテーブル初期化
        self.__src = ColumnDataSource({self.TBLLBL_DATE: [],
                                       self.TBLLBL_WEEK: [],
                                       self.TBLLBL_GOTO: []
                                       })

        cols = [
            TableColumn(field=self.TBLLBL_DATE, title="Date",
                        formatter=DateFormatter()),
            TableColumn(field=self.TBLLBL_WEEK, title="Week"),
            TableColumn(field=self.TBLLBL_GOTO, title="goto-day"),
        ]

        self.__tbl = DataTable(source=self.__src,
                               columns=cols,
                               fit_columns=True,
                               height=200)
        self.__src.selected.on_change("indices", self.__cb_dttbl)

        # ローソク足チャート初期化
        self.__csc = CandleStickChart()
        self.__csdlist = []

    def get_layout(self):
        """レイアウトを取得する[get layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        btnrun = self.__btn_run
        tbl = self.__tbl
        cscfig = self.__csc.fig

        tblfig = widgetbox(children=[tbl, cscfig], sizing_mode="stretch_width")

        layout_ = layout(children=[[btnrun], [tblfig]],
                         sizing_mode="stretch_width")
        return(layout_)

    def __cb_btn_run(self):
        """Widget Button(実行)コールバックメソッド
           [Callback method of Widget Button(Execute)]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        print("Called cb_btn_run")

        dfsmm = self.__dfsmm
        dfsmm.drop(index=dfsmm.index, inplace=True)
        self.__csdlist = []

        yesterday = dt.date.today() - dt.timedelta(days=1)
        str_ = ana.get_date_str()
        str_ = utl.limit_upper(str_, yesterday)
        end_ = ana.get_date_end()
        end_ = utl.limit_upper(end_, yesterday)

        print("Start:{}" .format(str_))
        print("End:  {}" .format(end_))

        nextdate = end_ + dt.timedelta(days=1)
        nextmonth = nextdate.month

        lastday_flg = False
        gotoday_flg = False

        for n in range((end_ - str_ + dt.timedelta(days=1)).days):
            date_ = end_ - dt.timedelta(n)
            weekdayno = date_.weekday()

            # 月末判定
            if not date_.month == nextmonth:
                lastday_flg = True

            # ゴトー日判定
            if date_.day in self._MLT_FIVE_LIST:
                gotoday_flg = True

            # 平日判定
            if (weekdayno < 5) and not jpholiday.is_holiday(date_):

                if lastday_flg or gotoday_flg:
                    target = "○"
                    lastday_flg = False
                    gotoday_flg = False
                else:
                    target = "×"

                # 出力
                record = pd.Series([self._WEEK_DICT[weekdayno],
                                    target],
                                   index=dfsmm.columns,
                                   name=date_)
                dfsmm = dfsmm.append(record)

            nextmonth = date_.month

        dfsmm.sort_index(inplace=True)

        if dfsmm.empty:
            print("リストは空です")
        else:

            inst_id = ana.get_instrument_id()
            inst = OandaIns.list[inst_id].oanda_name
            gran = OandaGrn.M10

            for date_ in dfsmm.index:
                str_ = dt.datetime.combine(date_, dt.time(0, 0))
                end_ = dt.datetime.combine(date_, dt.time(10, 0))
                dtmstr = DateTimeManager(str_)
                dtmend = DateTimeManager(end_)

                try:
                    csd = CandleStickData(gran, inst, dtmstr, dtmend)
                except V20Error as v20err:
                    print("-----V20Error: {}".format(v20err))
                except ConnectionError as cerr:
                    print("----- ConnectionError: {}".format(cerr))
                except Exception as excp:
                    print("----- Exception: {}".format(excp))

                self.__csdlist.append(csd)

        # 表示更新
        self.__src.data = {
            self.TBLLBL_DATE: dfsmm.index.tolist(),
            self.TBLLBL_WEEK: dfsmm[TTMGoto.LBL_WEEK].tolist(),
            self.TBLLBL_GOTO: dfsmm[TTMGoto.LBL_GOTO].tolist(),
        }

        self.__dfsmm = dfsmm

    def __cb_dttbl(self, attr, old, new):
        """Widget DataTableコールバックメソッド
           [Callback method of Widget DataTable]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        idx = new[0]
        self.__csc.set_dataframe(self.__csdlist[idx])
