import pandas as pd
import jpholiday
from datetime import date, timedelta
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Button
from bokeh.models.widgets import TableColumn, DataTable
from bokeh.models.widgets import DateFormatter
from bokeh.layouts import layout
import autotrader.analyzer as ana
import autotrader.utils as utl


class TTMGoto(object):
    """ TTMGoto
            - 仲根(TTM)とゴトー日クラス[TTM and Goto day class]
    """

    LBL_DATE = "data"
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

        cols = [TTMGoto.LBL_DATE,
                TTMGoto.LBL_WEEK,
                TTMGoto.LBL_GOTO]
        self.__dfsmm = pd.DataFrame(columns=cols)

        # Widget DataTable:
        self.TBLLBL_DATE = "date"
        self.TBLLBL_WEEK = "week"
        self.TBLLBL_GOTO = "goto-day"

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

    def get_layout(self):
        """レイアウトを取得する[get layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        btnrun = self.__btn_run
        tbl = self.__tbl

        layout_ = layout(children=[[btnrun], [tbl]],
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
        dfsmm = dfsmm.drop(range(len(dfsmm)))

        yesterday = date.today() - timedelta(days=1)
        str_ = ana.get_date_str()
        str_ = utl.limit_upper(str_, yesterday)
        end_ = ana.get_date_end()
        end_ = utl.limit_upper(end_, yesterday)

        print("Start:{}" .format(str_))
        print("End:  {}" .format(end_))

        nextdate = end_ + timedelta(days=1)
        nextmonth = nextdate.month

        lastday_flg = False
        gotoday_flg = False

        for n in range((end_ - str_ + timedelta(days=1)).days):
            date_ = end_ - timedelta(n)
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
                record = pd.Series([date_,
                                    self._WEEK_DICT[weekdayno],
                                    target],
                                   index=dfsmm.columns)
                dfsmm = dfsmm.append(record,  ignore_index=True)

            nextmonth = date_.month

        dfsmm = dfsmm.sort_values(by=TTMGoto.LBL_DATE).reset_index(drop=True)

        self.__src.data = {
            self.TBLLBL_DATE: dfsmm[TTMGoto.LBL_DATE].tolist(),
            self.TBLLBL_WEEK: dfsmm[TTMGoto.LBL_WEEK].tolist(),
            self.TBLLBL_GOTO: dfsmm[TTMGoto.LBL_GOTO].tolist(),
        }

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
        print("Table Idx: {}" .format(idx))
