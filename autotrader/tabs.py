from bokeh.models import Panel, Tabs
import autotrader.viewer as _viewer
import autotrader.analyzer as _analyzer


# Tab1の設定
vi = _viewer.Viewer()
p1 = vi.get_overall_layout()
tab1 = Panel(child=p1, title="Main view")

# Tab2の設定
an = _analyzer.Analyzer()
p2 = an.get_overall_layout()
tab2 = Panel(child=p2, title="Analyzer")

# ルートモデル取得
tabs = Tabs(tabs=[tab1, tab2])


def get_rootmodel():
    """ルートモデルを取得する[get root model]
    引数[Args]:
        なし[None]
    戻り値[Returns]:
        tabs (object) : Root model object
    """
    return tabs
