from bokeh.models import Panel, Tabs
import autotrader.viewer as _viewer
import autotrader.analyzer as an
from bokeh.models.widgets import Slider, RadioGroup, Button
from bokeh.models.widgets import Select, CheckboxGroup
from bokeh.layouts import layout, widgetbox, row, gridplot, column
import autotrader.analyzer as an

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


# set each callback function
_SELECT_DICT = {
    "Candlestick chart": _vi.get_overall_layout(),
    "Analysis - Gap Fill": an.get_overall_layout(),
    "Analysis - TTM & Goto-Day": 2
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

_layout = layout(children=[_sel])
