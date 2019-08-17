from bokeh.models.widgets import Toggle, DataTable, DateFormatter, TableColumn
from bokeh.layouts import layout, widgetbox, row
import autotrader.analyzer as ana
from autotrader.utils import DateTimeManager
from datetime import datetime, timedelta
from autotrader.oanda_common import OandaGrn
import autotrader.utils as utl
from bokeh.models import ColumnDataSource
from autotrader.analysis.candlestick import CandleStickChart, CandleStickData
from oandapyV20.exceptions import V20Error


class FillingGap(object):
    """ FillingGap
            - 窓埋めクラス[Filling gap class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        # Widget Toggle:解析実行[Run analysis]
        self.__btn_run = Toggle(label="解析実行",
                                active=False,
                                button_type="success")
        self.__btn_run.on_click(self.__cb_tglbtn_run)

        # Widget DataTable:解析結果[Result of analysis]
        self.TBLLBL_DATE = "Date"
        self.TBLLBL_RSLT = "Result"
        self.__src = ColumnDataSource({self.TBLLBL_DATE: [],
                                       self.TBLLBL_RSLT: []})

        cols = [
            TableColumn(field=self.TBLLBL_DATE, title="Date",
                        formatter=DateFormatter()),
            TableColumn(field=self.TBLLBL_RSLT, title="Result"),
        ]

        self.__tbl = DataTable(source=self.__src,
                               columns=cols,
                               width=400, height=280)
        self.__src.selected.on_change('indices', self.__cb_dttbl)

        self.__csc = CandleStickChart()
        self.__dflist = []

    def get_layout(self):
        """レイアウトを取得する[get layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        btnrun = self.__btn_run
        tbl = self.__tbl
        fig = self.__csc.get_model()

        tblfig = row(children=[tbl, fig])
        wdgbx1 = widgetbox(children=[btnrun, tblfig])

        self.__layout = layout(children=[[wdgbx1]])
        return(self.__layout)

    def __judge_fillingGap(self, df):
        """窓埋め成功/失敗判定メソッド
           [judge method of fillingGap success or fail]
        引数[Args]:
            df (pandas data frame) : ローソク足データ[candle stick data]
        戻り値[Returns]:
            jdg (boolean) : 判定結果
                            true: 窓埋め成功[Filling Gap success]
                            false: 窓埋め失敗[Filling Gap fail]
        """
        jdg = True
        return jdg

    def __cb_tglbtn_run(self, new):
        """Widget Toggle(実行)コールバックメソッド
           [Callback method of Widget Button(Execute)]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        print("new: {}" .format(new))
        if new is True:
            self.__btn_run.label = "キャンセル"
            self.__btn_run.button_type = "primary"
        else:
            self.__btn_run.label = "解析実行"
            self.__btn_run.button_type = "success"

        # 月曜のみを抽出する
        # Extract only Monday
        now = datetime.now()
        str_ = ana.get_datetime_str()
        str_ = utl.limit_upper(str_, now)
        end_ = ana.get_datetime_end()
        end_ = utl.limit_upper(end_, now) + timedelta(days=1)

        mondaylist = []
        for n in range((end_ - str_).days):
            day = str_ + timedelta(n)
            if day.weekday() == 0:
                mondaylist.append(day)

        if not mondaylist:
            print("リストは空です")
        else:
            rsllist = []
            cnt = 0
            for n in mondaylist:
                str_ = n + timedelta(days=-2, hours=0)
                end_ = n + timedelta(hours=12)
                dtmstr = DateTimeManager(str_)
                dtmend = DateTimeManager(end_)
                print("開始：{}" .format(dtmstr.tokyo))
                print("終了：{}" .format(dtmend.tokyo))

                inst = ana.get_instrument()
                gran = OandaGrn.H1

                try:
                    csd = CandleStickData(gran, inst, dtmstr, dtmend)
                except V20Error as v20err:
                    print("-----V20Error: {}".format(v20err))
                except ConnectionError as cerr:
                    print("----- ConnectionError: {}".format(cerr))
                except Exception as excp:
                    print("----- Exception: {}".format(excp))

                # print(df)
                self.__dflist.append(csd)

                # 窓埋め成功/失敗判定
                jdg = self.__judge_fillingGap(csd.df)
                if jdg is True:
                    rsllist.append("成功")
                else:
                    rsllist.append("失敗")
                cnt = cnt + 1

            print("dflist:{}" .format(len(self.__dflist)))

            self.__src.data = {
                self.TBLLBL_DATE: mondaylist,
                self.TBLLBL_RSLT: rsllist
            }

        print("Called cb_btn_run")

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
        self.__csc.set_dataframe(self.__dflist[new[0]])
