# ==============================================================================
# brief        Bokeh共通モジュール
#
# author       たっきん
# ==============================================================================
from abc import ABCMeta
from autotrader.oanda_common import OandaGrn


class AxisTyp(object):
    """ AxisTyp - BoKehパラメータ定義クラス。"""

    """ x軸タイプ """
    X_LINEAR = "linear"        # linear
    X_LOG = "log"              # log
    X_DATETIME = "datetime"    # 日付
    X_MERCATOR = "mercator"    # mercator

    """ y軸タイプ """
    Y_LINEAR = "linear"        # linear
    Y_LOG = "log"              # log
    Y_DATETIME = "datetime"    # 日付
    Y_MERCATOR = "mercator"    # mercator


class ToolType(object):
    """ ToolType - TOOLタイプ定義クラス。"""

    PAN = "pan"
    XPAN = "xpan"
    YPAN = "ypan"
    XWHEEL_PAN = "xwheel_pan"
    YWHEEL_PAN = "ywheel_pan"
    WHEEL_ZOOM = "wheel_zoom"
    XWHEEL_ZOOM = "xwheel_zoom"
    YWHEEL_ZOOM = "ywheel_zoom"
    ZOOM_IN = "zoom_in"
    XZOOM_IN = "xzoom_in"
    YZOOM_IN = "yzoom_in"
    ZOOM_OUT = "zoom_out"
    XZOOM_OUT = "xzoom_out"
    YZOOM_OUT = "yzoom_out"
    CLICK = "click"
    TAP = "tap"
    CROSSHAIR = "crosshair"
    BOX_SELECT = "box_select"
    XBOX_SELECT = "xbox_select"
    YBOX_SELECT = "ybox_select"
    POLY_SELECT = "poly_select"
    LASSO_SELECT = "lasso_select"
    BOX_ZOOM = "box_zoom"
    XBOX_ZOOM = "xbox_zoom"
    YBOX_ZOOM = "ybox_zoom"
    HOVER = "hover"
    SAVE = "save"
    PREVIEWSAVE = "previewsave"
    UNDO = "undo"
    REDO = "redo"
    RESET = "reset"
    HELP = "help"
    BOX_EDIT = "box_edit"
    POINT_DRAW = "point_draw"
    POLY_DRAW = "poly_draw"
    POLY_EDIT = "poly_edit"

    @classmethod
    def gen_str(cls, *args):
        """TOOLタイプ設定用文字列生成メソッド
        Args:
            *args (str): TOOLタイプ文字列（複数指定可）
        Returns:
            引数の文字列をカンマ区切りで生成する。
            <example>
                args:("aaa", "bbb", "ccc")
                Returns -> "aaa, bbb, ccc"
        """
        mystr = ""
        for arg in args:
            mystr = mystr + "," + arg
        return(mystr[1:])


class GlyphVbarAbs(metaclass=ABCMeta):
    """ GlyphVbarAbs - GlyphVbar抽象クラス"""

    def __init__(self, wide_scale):
        """"コンストラクタ[Constructor]
        引数[Args]:
            wide_scale (float) : Vbar幅の調整
        """
        self.__WIDE_SCALE = wide_scale

    def get_width(self, gran):
        """"Vbar幅を取得する[get Vbar width]
        引数[Args]:
            gran (str) : ローソク足の時間足[granularity of a candlestick]
        戻り値[Returns]:
            width (int) : Vbar幅[Vbar width]
        """
        if gran == OandaGrn.D:
            width = 24 * 60 * 60 * 1000
        elif gran == OandaGrn.H12:
            width = 12 * 60 * 60 * 1000
        elif gran == OandaGrn.H8:
            width = 8 * 60 * 60 * 1000
        elif gran == OandaGrn.H6:
            width = 6 * 60 * 60 * 1000
        elif gran == OandaGrn.H4:
            width = 4 * 60 * 60 * 1000
        elif gran == OandaGrn.H3:
            width = 3 * 60 * 60 * 1000
        elif gran == OandaGrn.H2:
            width = 2 * 60 * 60 * 1000
        elif gran == OandaGrn.H1:
            width = 1 * 60 * 60 * 1000
        elif gran == OandaGrn.M30:
            width = 30 * 60 * 1000
        elif gran == OandaGrn.M15:
            width = 15 * 60 * 1000
        elif gran == OandaGrn.M10:
            width = 10 * 60 * 1000
        elif gran == OandaGrn.M5:
            width = 5 * 60 * 1000
        elif gran == OandaGrn.M4:
            width = 4 * 60 * 1000
        elif gran == OandaGrn.M3:
            width = 3 * 60 * 1000
        elif gran == OandaGrn.M2:
            width = 2 * 60 * 1000
        elif gran == OandaGrn.M1:
            width = 1 * 60 * 1000
        else:
            width = 1

        width = width * self.__WIDE_SCALE
        return width
