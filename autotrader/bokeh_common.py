# ==============================================================================
# brief        Bokeh共通モジュール
#
# author       たっきん
# ==============================================================================


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
