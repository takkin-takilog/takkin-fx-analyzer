from bokeh.models.widgets import Button, Select
from bokeh.layouts import layout, row
import autotrader.viewer as _viewer
from autotrader.analysis.gapfill import GapFill
from autotrader.analysis.ttm_goto import TTMGoto


def _cb_btn_view(self):
    del _layout.children[1:]
    _layout.children.append(_SELECT_DICT[_slc_view.value])


def get_rootmodel():
    """ルートモデルを取得する[get root model]
    引数[Args]:
        なし[None]
    戻り値[Returns]:
        tabs (object) : Root model object
    """
    global _layout
    return _layout


_vi = _viewer.Viewer()
_gf = GapFill()
_ttm = TTMGoto()

# set each callback function
_SELECT_DICT = {
    "Candlestick chart": _vi.layout,
    "Analysis - Gap Fill": _gf.layout,
    "Analysis - TTM & Goto-Day": _ttm.layout
}


_keylist = list(_SELECT_DICT.keys())
_slc_view = Select(title="",
                   value=_keylist[0],
                   options=_keylist,
                   default_size=400)

_btn_view = Button(label="決定",
                   button_type="success",
                   sizing_mode="fixed",
                   default_size=200)

_btn_view.on_click(_cb_btn_view)

_sel = row(children=[_slc_view, _btn_view])

_layout = layout(children=[_sel], sizing_mode="stretch_width")


if __name__ == "__main__":
    from bokeh.io import show

    #lay = _vi.layout
    lay = _gf.layout
    #lay = _ttm.layout
    show(lay)
