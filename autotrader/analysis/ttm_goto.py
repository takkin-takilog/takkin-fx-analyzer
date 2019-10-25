import pandas as pd
from datetime import datetime, timedelta
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Button
from bokeh.models.widgets import TableColumn, DataTable
from bokeh.models.widgets import DateFormatter, NumberFormatter
from bokeh.layouts import layout, widgetbox
import autotrader.analyzer as ana
import autotrader.utils as utl


class TTMGoto(object):
    """ TTMGoto
            - 仲根(TTM)とゴトー日クラス[TTM and Goto day class]
    """

    LBL_DATE = "data"
    LBL_WEEK = "week"
    LBL_GOTO = "goto-day"

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

        # 月曜のみを抽出する
        # Extract only Monday
        now = datetime.now() - timedelta(hours=9)
        str_ = ana.get_datetime_str()
        str_ = utl.limit_upper(str_, now)
        end_ = ana.get_datetime_end()
        end_ = utl.limit_upper(end_, now)

        print("Start:{}" .format(str_))
        print("End:  {}" .format(end_))

        workdayslist = utl.extract_workdays(str_, end_)

        for wday in workdayslist:

            # 曜日判定
            if wday.weekday() == 0:
                week = "月"
            elif wday.weekday() == 1:
                week = "火"
            elif wday.weekday() == 2:
                week = "水"
            elif wday.weekday() == 3:
                week = "木"
            elif wday.weekday() == 4:
                week = "金"

            # ゴトー日判定
            #gotoflg = self.__judge_gotoday(wday)


            # 出力
            record = pd.Series([wday,
                                week,
                                "○"],
                               index=self.__dfsmm.columns)

            dfsmm = dfsmm.append(record,  ignore_index=True)

        self.__src.data = {
            self.TBLLBL_DATE: dfsmm[TTMGoto.LBL_DATE].tolist(),
            self.TBLLBL_WEEK: dfsmm[TTMGoto.LBL_WEEK].tolist(),
            self.TBLLBL_GOTO: dfsmm[TTMGoto.LBL_GOTO].tolist(),
        }
    """
    def __judge_gotoday(self, wday):

        gotolist = [5, 10, 15, 20, 25]

        if ((wday.day == 5) or ( (wday.weekday() == 4) or ( (wday.day == 3) or (wday.day == 4)))) or
            ((wday.day == 10) or ( (wday.weekday() == 4) or ( (wday.day == 9) or (wday.day == 8))))

        :
    """


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
