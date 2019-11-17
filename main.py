import autotrader.tabs as tabs
import autotrader.select as sel
from bokeh.io import curdoc
from bokeh.io import show

if __name__ == "__main__":
    """eclipse実行用"""
    print("---------- Debug ----------")
    #show(tabs.get_rootmodel())
    show(sel.get_rootmodel())
else:
    """Bokehサーバー実行用"""
    document = curdoc()
    #document.add_root(tabs.get_rootmodel())
    document.add_root(sel.get_rootmodel())