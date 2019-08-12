
import autotrader.viewer as _viewer
from bokeh.io import curdoc

if __name__ == "__main__":
    """eclipse実行用"""
    print("---------- Debug ----------")
    vi = _viewer.Viewer()
    vi.view()
else:
    """Bokehサーバー実行用"""
    document = curdoc()
    vi = _viewer.Viewer()
    document.add_root(vi.get_overall_layout())
