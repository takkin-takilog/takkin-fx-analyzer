from bokeh.models.widgets import Button
from bokeh.layouts import layout


class FillingGap(object):
    """ FillingGap
            - 窓埋めクラス[Filling gap class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        # Widget Button:解析実行[Run analysis]
        self.__btn_run = Button(label="解析実行", button_type="success")
        self.__btn_run.on_click(self.__cb_btn_run)

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

    def __cb_btn_run(self):
        """Widget Button(実行)コールバックメソッド
           [Callback method of Widget Button(Execute)]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        print("Called cb_btn_run")
