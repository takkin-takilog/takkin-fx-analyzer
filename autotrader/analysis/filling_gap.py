from bokeh.models.widgets import Toggle
from bokeh.layouts import layout
import autotrader.analyzer as ana
from autotrader.utils import DateTimeManager
from oandapyV20.exceptions import V20Error
import autotrader.oanda_common as oc
from datetime import datetime, timedelta


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

    def get_layout(self):
        """レイアウトを取得する[get layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        wdg = self.__btn_run

        self.__layout = layout(children=[[wdg]])
        return(self.__layout)

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
            self.__btn_run.button_type="primary"
        else:
            self.__btn_run.label = "解析実行"
            self.__btn_run.button_type="success"

        # 月曜のみを抽出する
        # Extract only Monday
        str_ = ana.datetime_str()
        end_ = ana.datetime_end() + timedelta(days=1)

        mondaylist = []
        for n in range((end_ - str_).days):
            day = str_ + timedelta(n)
            if day.weekday() == 0:
                mondaylist.append(day)

        if not mondaylist:
            print("リストは空です")
        else:
            dflist=[]
            for n in mondaylist:
                str_ = n + timedelta(hours=6)
                end_ = n + timedelta(hours=12)
                dtmstr = DateTimeManager(str_)
                dtmend = DateTimeManager(end_)
                print("開始：{}" .format(dtmstr.tokyo))
                print("終了：{}" .format(dtmend.tokyo))

                try:
                    df = oc.fetch_ohlc(ana._gran, ana._inst, dtmstr, dtmend)
                except V20Error as v20err:
                    print("-----V20Error: {}".format(v20err))
                except ConnectionError as cerr:
                    print("----- ConnectionError: {}".format(cerr))
                except Exception as err:
                    print("----- ExceptionError: {}".format(err))
                print(df)
                dflist.append(df)

            print("dflist:{}" .format(len(dflist)))

        print("Called cb_btn_run")
