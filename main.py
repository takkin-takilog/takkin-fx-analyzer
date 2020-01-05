import analyzer.switch_func as sf
from bokeh.io import curdoc
from bokeh.io import show

if __name__ == "__main__":
    """eclipse実行用"""
    print("---------- Debug ----------")
    show(sf.get_rootmodel())
else:
    """Bokehサーバー実行用"""
    document = curdoc()
    document.add_root(sf.get_rootmodel())
