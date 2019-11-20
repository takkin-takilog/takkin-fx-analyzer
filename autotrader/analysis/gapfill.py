from math import pi
import pandas as pd
import numpy as np
import datetime as dt
from bokeh import events
from bokeh.models import ColumnDataSource
from bokeh.models import CrosshairTool, HoverTool
from bokeh.models import Panel, Tabs
from bokeh.models import NumeralTickFormatter
from bokeh.models.widgets import Button, TextInput, DataTable, TableColumn
from bokeh.models.widgets import DateFormatter, NumberFormatter
from bokeh.models.glyphs import Line
from bokeh.layouts import widgetbox, row, column, gridplot
from oandapyV20.exceptions import V20Error
import autotrader.utils as utl
import autotrader.analysis.candlestick as cs
from autotrader.utils import DateTimeManager
from autotrader.oanda_common import OandaGrn, OandaIns
from autotrader.analysis.candlestick import CandleGlyph
from autotrader.analysis.candlestick import CandleStickChartBase
from autotrader.analysis.candlestick import CandleStickData
from autotrader.analysis.graph import HorizontalHistogram
from autotrader.analysis.graph import HorizontalHistogramTwo
from autotrader.analysis.graph import LineGraphAbs, HeatMap
from autotrader.analysis.base import AnalysisAbs, DateWidget


class HeatMapSim(HeatMap):

    def __init__(self, title):
        super().__init__(title)

        # simulation graph
        self.__lgs = LineGraphSim(title="Profit Graph",
                                  color="yellow")
        self.__lgs.xaxis_label("Loss Cut Price Offset")
        self.__lgs.yaxis_label("Sum of Price")

        self._fig.on_event(events.MouseMove, self.__cb_mousemove)
        self._fig.xaxis.major_label_orientation = pi / 4

        self.__x_min = 0
        self.__y_min = 0

    @property
    def linegraph_fig(self):
        return self.__lgs.fig

    def update(self, map3d, xlist, ylist, htmap, xstep, ystep, inst_id):
        super().update(map3d, xlist, ylist, xstep, ystep, inst_id)

        MARGIN = 0.1

        d = map3d[:, 2]

        x_leng = (max(xlist) - min(xlist)) * MARGIN
        x_range = (min(xlist) - x_leng, max(xlist) + x_leng)

        z_leng = (max(d) - min(d)) * MARGIN
        z_range = (min(d) - z_leng, max(d) + z_leng)
        self.__lgs.update_range(x_range, z_range)

        x_max = map3d[:, 0][self._maxidx]
        y_max = map3d[:, 1][self._maxidx]

        self.__xlist = xlist
        self.__ylist = ylist
        self.__ystep = ystep
        self.__htmap = htmap

        self.__x_max = x_max
        self.__y_max = y_max

    @property
    def max_coordinate(self):
        return (self.__x_max, self.__y_max)

    def __cb_mousemove(self, event):

        if self._upflg:
            df_y = self._df_y
            xrng = self._xrng
            xlist = self.__xlist
            ylist = self.__ylist
            htmap = self.__htmap
            ystep = self.__ystep

            idxmin = np.abs(df_y - event.y).idxmin()
            y = df_y[idxmin]
            self._hline.update(xrng, y)
            self.__lgs.update(xlist, htmap[idxmin])

            str_ = round(ylist[idxmin], OandaIns.min_unit_max())
            end_ = round(str_ + ystep, OandaIns.min_unit_max())
            th_pos = " (Gap Price Thresh: " + \
                str(str_) + " - " + str(end_) + ")"
            self.__lgs.update_title(th_pos)

    def clear(self):
        """"データをクリアする[clear data]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        super().clear()
        self.__lgs.clear()


class LineGraphSim(LineGraphAbs):

    def __init__(self, title, color):
        super().__init__(title, color)

        self.__TITLE = title

        self._fig.add_tools(CrosshairTool(line_color="pink",
                                          line_alpha=0.5,
                                          dimensions="height"))

        hover = HoverTool()
        hover.tooltips = [("loss cut", "@" + LineGraphSim.X + "{0.00000}"),
                          ("profit", "@" + LineGraphSim.Y + "{0.00000}")]
        hover.renderers = [self._ren]
        hover.mode = "vline"
        self._fig.add_tools(hover)

        self._fig.xaxis.formatter = NumeralTickFormatter(format="0[.]00000")
        self._fig.yaxis.formatter = NumeralTickFormatter(format="0[.]00000")

        self._fig.xaxis.major_label_orientation = pi / 4

    def update(self, xlist, zlist):
        self._src.data = {
            LineGraphSim.X: xlist,
            LineGraphSim.Y: zlist,
        }

    def update_range(self, x_range, z_range):

        str_ = x_range[0]
        end_ = x_range[1]
        self._fig.x_range.update(start=str_, end=end_)

        str_ = z_range[0]
        end_ = z_range[1]
        self._fig.y_range.update(start=str_, end=end_)

    def update_title(self, th_pos):
        self._fig.title.text = self.__TITLE + th_pos


class CandleStickChart(CandleStickChartBase):
    """ CandleStickChart
            - ローソク足チャート定義クラス[Candle stick chart definition class]
    """

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        # Hbar Label
        self.__Y = "y"
        self.__X = "x"
        self.__CLOSE_COLOR = "#FFEE55"
        self.__OPEN_COLOR = "#54FFEE"

        super().__init__()
        self._fig.title.text = "Gap-Fill Candlestick Chart ( 1 hour )"

        # プロット設定
        self._fig.toolbar_location = "right"
        self._fig.add_tools(CrosshairTool(line_color="pink",
                                          line_alpha=0.5))

        hover = HoverTool()
        hover.formatters = {CandleGlyph.XDT: "datetime"}
        hover.tooltips = [(cs.LBL_TIME, "@" + CandleGlyph.XDT + "{%F %R}"),
                          (cs.LBL_HIGH, "@" + CandleGlyph.YHI),
                          (cs.LBL_OPEN, "@" + CandleGlyph.YOP),
                          (cs.LBL_CLOSE, "@" + CandleGlyph.YCL),
                          (cs.LBL_LOW, "@" + CandleGlyph.YLO)]
        hover.renderers = [self._glyinc.render,
                           self._glydec.render,
                           self._glyequ.render]
        self._fig.add_tools(hover)

        # 水平ライン(Close)
        self.__srcline_cl = ColumnDataSource({self.__X: [],
                                              self.__Y: []})
        self.__glyline_cl = Line(x=self.__X,
                                 y=self.__Y,
                                 line_dash="dotted",
                                 line_color=self.__CLOSE_COLOR,
                                 line_width=1)
        self._fig.add_glyph(self.__srcline_cl, self.__glyline_cl)

        # 水平ライン(Open)
        self.__srcline_op = ColumnDataSource({self.__X: [],
                                              self.__Y: []})
        self.__glyline_op = Line(x=self.__X,
                                 y=self.__Y,
                                 line_dash="dotted",
                                 line_color=self.__OPEN_COLOR,
                                 line_width=1)
        self._fig.add_glyph(self.__srcline_op, self.__glyline_op)

    def set_dataframe(self, csd, sr):

        super().set_dataframe(csd)
        xscal = self._fig.x_range

        clspri = sr[GapFill.LBL_CLOSEPRI]
        self.__srcline_cl.data = {self.__X: [xscal.start, xscal.end],
                                  self.__Y: [clspri, clspri]}

        opnpri = sr[GapFill.LBL_OPENPRI]
        self.__srcline_op.data = {self.__X: [xscal.start, xscal.end],
                                  self.__Y: [opnpri, opnpri]}


class GapFill(AnalysisAbs):
    """ GapFill
            - 窓埋めクラス[Gap-Fill class]
    """

    LBL_RESULT = "Result"
    LBL_DIR = "Direction"
    LBL_CLOSEPRI = "Close Price"
    LBL_OPENPRI = "Open Price"
    LBL_SPREAD = "Spread"
    LBL_GAPPRI = "Gap Price"
    LBL_FILLTIME = "Filled Time"
    LBL_MAXOPNRNG = "Max Open Range"
    LBL_VALID = "Valid Trade"

    RSL_FAIL = 0
    RSL_SUCCESS = 1

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        super().__init__()

        self.__BG_COLOR = "#2E2E2E"  # Background color
        self.__HIST_DIV = 50

        diffdate = dt.date.today() - dt.timedelta(days=30)
        self.__dtwdg_str = DateWidget("開始", diffdate)
        self.__dtwdg_end = DateWidget("終了",)

        # Widget Button:解析実行[Run analysis]
        self.__btn_run = Button(label="解析実行",
                                button_type="success",
                                sizing_mode="fixed",
                                default_size=200)
        self.__btn_run.on_click(self.__cb_btn_run)

        # Widget DataTable:解析結果[Result of analysis]
        self.TBLLBL_DATE = "Date"
        self.TBLLBL_RSLT = "Result"
        self.TBLLBL_CLSPRI = "Close Price"
        self.TBLLBL_OPNPRI = "Open Price"
        self.TBLLBL_DIR = "Direction"
        self.TBLLBL_SPREAD = "Spread"
        self.TBLLBL_GAPPRI = "Gap Price"
        self.TBLLBL_FILLTIME = "Gap-Fill Time"
        self.TBLLBL_MAXOPNRNG = "Max open range"

        self.__src = ColumnDataSource({self.TBLLBL_DATE: [],
                                       self.TBLLBL_RSLT: [],
                                       self.TBLLBL_CLSPRI: [],
                                       self.TBLLBL_OPNPRI: [],
                                       self.TBLLBL_DIR: [],
                                       self.TBLLBL_SPREAD: [],
                                       self.TBLLBL_GAPPRI: [],
                                       self.TBLLBL_FILLTIME: [],
                                       self.TBLLBL_MAXOPNRNG: [],
                                       })

        cols = [
            TableColumn(field=self.TBLLBL_DATE, title="Date",
                        formatter=DateFormatter()),
            TableColumn(field=self.TBLLBL_CLSPRI, title="Close Price",
                        formatter=NumberFormatter(format="0[.]000")),
            TableColumn(field=self.TBLLBL_OPNPRI, title="Open Price",
                        formatter=NumberFormatter(format="0[.]000")),
            TableColumn(field=self.TBLLBL_DIR, title="Direction"),
            TableColumn(field=self.TBLLBL_SPREAD, title="Spread"),
            TableColumn(field=self.TBLLBL_GAPPRI, title="Gap Price",
                        formatter=NumberFormatter(format="0[.]00000")),
            TableColumn(field=self.TBLLBL_RSLT, title="Result"),
            TableColumn(field=self.TBLLBL_FILLTIME, title="Fill-Gap Time",
                        formatter=DateFormatter(format="%R")),
            TableColumn(field=self.TBLLBL_MAXOPNRNG, title="Max Open Range",
                        formatter=NumberFormatter(format="0[.]00000")),
        ]

        self.__tbl = DataTable(source=self.__src,
                               columns=cols,
                               fit_columns=True,
                               height=200)
        self.__src.selected.on_change("indices", self.__cb_dttbl)

        self.__csc1 = CandleStickChart()
        self.__csdlist1 = []

        cols = [GapFill.LBL_RESULT,
                GapFill.LBL_DIR,
                GapFill.LBL_CLOSEPRI,
                GapFill.LBL_OPENPRI,
                GapFill.LBL_SPREAD,
                GapFill.LBL_GAPPRI,
                GapFill.LBL_FILLTIME,
                GapFill.LBL_MAXOPNRNG,
                GapFill.LBL_VALID]
        self.__dfsmm = pd.DataFrame(columns=cols)

        # ---------- Gap-Price histogram ----------
        hist = self.__generate_gapprice_hist("Gap-Price histogram (All data)")
        self.__hist_gap_all = hist

        hist = self.__generate_gapprice_hist(
            "Gap-Price histogram (Only valid data)")
        self.__hist_gap_vld = hist

        # ---------- Max open range histogram ----------
        hist = self.__generate_maxopenrange_hist(
            "Max open range histogram (All data)")
        self.__maxopn_hist_all = hist

        hist = self.__generate_maxopenrange_hist(
            "Max open range histogram (Only valid data)")
        self.__maxopn_hist_vld = hist

        # ---------- Income simulation ----------
        self.__btn_simrun = Button(label="シミュレーション実行",
                                   button_type="success",
                                   sizing_mode="fixed",
                                   default_size=200)
        self.__btn_simrun.on_click(self.__cb_btn_simrun)

        self.__txtin_losscut = TextInput(value="", title="最適ロスカット幅:",
                                         width=200)

        self.__txtin_gapprith = TextInput(value="", title="最適Gap Price閾値:",
                                          width=200)

        self.__hm = HeatMapSim("Profit Heatmap")

        self.__hm.xaxis_label("Loss Cut Price Offset")
        self.__hm.yaxis_label("Gap Price Thresh")

    @property
    def layout(self):
        """レイアウトを取得する[get layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        dtwdg_str = self.__dtwdg_str.widget
        dtwdg_end = self.__dtwdg_end.widget
        dtwdg = row(children=[dtwdg_str, dtwdg_end])
        wslin = self._slc_inst

        wdgbx1 = column(children=[wslin, dtwdg], sizing_mode="fixed")

        btnrun = self.__btn_run
        tbl = self.__tbl
        fig = self.__csc1.fig

        tblfig = column(children=[tbl, fig], sizing_mode="stretch_width")

        tabs = self.__create_result_tabs()

        wdgbx2 = column(children=[btnrun, tblfig, tabs],
                        sizing_mode="stretch_width")

        layout_ = row(children=[wdgbx1, wdgbx2],
                      sizing_mode="stretch_width")

        return(layout_)

    def __generate_gapprice_hist(self, title_):

        hist = HorizontalHistogramTwo(title=title_,
                                      color1="lime",
                                      color2="red")
        hist.xaxis_label("回数")
        hist.yaxis_label("Gap Price")

        # renderer1
        hover = HoverTool()
        hover.tooltips = [("回数", "@" + HorizontalHistogramTwo.RIGHT),
                          ("範囲", "@" + HorizontalHistogramTwo.BOTTOM
                           + "{(0.000)} - " + "@" + HorizontalHistogramTwo.TOP
                           + "{(0.000)}")]
        hover.renderers = [hist.render1]
        hist.fig.add_tools(hover)

        # renderer2
        hover = HoverTool()
        hover.tooltips = [("回数", "@" + HorizontalHistogramTwo.LEFT),
                          ("範囲", "@" + HorizontalHistogramTwo.BOTTOM
                           + "{(0.000)} - " + "@" + HorizontalHistogramTwo.TOP
                           + "{(0.000)}")]
        hover.renderers = [hist.render2]
        hist.fig.add_tools(hover)

        return hist

    def __generate_maxopenrange_hist(self, title_):

        hist = HorizontalHistogram(title=title_, color="lime")
        hist.xaxis_label("回数")
        hist.yaxis_label("Max Open Range")

        hover = HoverTool()
        hover.tooltips = [("回数", "@" + HorizontalHistogram.RIGHT),
                          ("範囲", "@" + HorizontalHistogram.BOTTOM
                           + "{(0.000)} - " + "@" + HorizontalHistogram.TOP
                           + "{(0.000)}")]
        hover.renderers = [hist.render]
        hist.fig.add_tools(hover)

        return hist

    def __create_result_tabs(self):

        # Tab1の設定
        txtin_succ = TextInput(value="",
                               title="Success count (All data):",
                               width=200)
        txtin_fail = TextInput(value="",
                               title="Failure count (All data):",
                               width=200)
        txtin_all_wdgbx = widgetbox(children=[txtin_succ,
                                              txtin_fail])
        self.__txtin_succ_all = txtin_succ
        self.__txtin_fail_all = txtin_fail

        txtin_succ = TextInput(value="",
                               title="Success count (Only valid data):",
                               width=200)
        txtin_fail = TextInput(value="",
                               title="Failure count (Only valid data):",
                               width=200)
        txtin_vld_wdgbx = widgetbox(children=[txtin_succ,
                                              txtin_fail])
        self.__txtin_succ_vld = txtin_succ
        self.__txtin_fail_vld = txtin_fail

        # Tab2の設定
        hist_gap_all = self.__hist_gap_all.fig
        hist_gap_vld = self.__hist_gap_vld.fig
        hist_max_all = self.__maxopn_hist_all.fig
        hist_max_vld = self.__maxopn_hist_vld.fig
        hist = gridplot(children=[[txtin_all_wdgbx, txtin_vld_wdgbx],
                                  [hist_gap_all, hist_gap_vld],
                                  [hist_max_all, hist_max_vld]])
        tab2 = Panel(child=hist, title="Summary")

        # Tab3の設定
        simrun = self.__btn_simrun
        hm = self.__hm.fig
        line = self.__hm.linegraph_fig

        lsct = self.__txtin_losscut
        gpth = self.__txtin_gapprith

        wgr1 = row(children=[lsct, gpth])
        wgr2 = row(children=[hm, line])

        wid3 = column(children=[simrun,
                                wgr1,
                                wgr2])

        tab3 = Panel(child=wid3, title="Income Simulation")

        # タブ生成
        tabs = Tabs(tabs=[tab2, tab3])

        return tabs

    def __update_summary(self, df):

        str_succ, str_fail = self.__make_summary(df)
        self.__txtin_succ_all.value = str_succ
        self.__txtin_fail_all.value = str_fail

        dfvld = df[df[GapFill.LBL_VALID] == utl.TRUE]
        str_succ, str_fail = self.__make_summary(dfvld)
        self.__txtin_succ_vld.value = str_succ
        self.__txtin_fail_vld.value = str_fail

    def __make_summary(self, df):

        if df.empty:
            length = 0
            succ_cnt = 0
            fail_cnt = 0
        else:
            length = len(df)
            succdf = df[df[GapFill.LBL_RESULT] == GapFill.RSL_SUCCESS]
            faildf = df[df[GapFill.LBL_RESULT] == GapFill.RSL_FAIL]
            succ_cnt = len(succdf)
            fail_cnt = len(faildf)

        str_succ = "  {} / {}" .format(succ_cnt, length)
        str_fail = "  {} / {}" .format(fail_cnt, length)

        return str_succ, str_fail

    def __update_hist(self, df, minunit):

        dfvld = df[df[GapFill.LBL_VALID] == utl.TRUE]

        # ========== Gap prie hist ==========
        # Gap prie hist all
        sulist, faillist, bins, rng = self.__update_hist_gapprice(df, minunit)
        self.__hist_gap_all.update(sulist, faillist, bins, rng)

        # Gap prie hist valid
        sulist, faillist, bins, rng = self.__update_hist_gapprice(
            dfvld, minunit)
        self.__hist_gap_vld.update(sulist, faillist, bins, rng)

        # ========== Max open hist ==========
        # Max open hist all
        sulist, bins, rng = self.__update_hist_maxopen(df, minunit)
        self.__maxopn_hist_all.update(sulist, bins, rng)

        # Max open hist valid
        sulist, bins, rng = self.__update_hist_maxopen(dfvld, minunit)
        self.__maxopn_hist_vld.update(sulist, bins, rng)

    def __update_hist_gapprice(self, df, minunit):

        succflg = (df[GapFill.LBL_RESULT] == GapFill.RSL_SUCCESS)
        failflg = (df[GapFill.LBL_RESULT] == GapFill.RSL_FAIL)
        succdf = df[succflg]
        faildf = df[failflg]

        succgappri = succdf[GapFill.LBL_GAPPRI].tolist()
        failgappri = faildf[GapFill.LBL_GAPPRI].tolist()

        if not succgappri:
            maxsu = 0
        else:
            maxsu = max(succgappri)

        if not failgappri:
            minsu = 0
        else:
            minsu = max(failgappri)
        max_ = max([maxsu, minsu])

        shiftl = 3
        tmp = shiftl - minunit

        maxrng = pow(10, tmp)
        ofs = pow(10, tmp - 2) * 5  # 切り上げ
        max_ = round(max_ + ofs, 1 - tmp)
        if max_ < maxrng:
            max_ = maxrng

        bins = int(max_ * pow(10, -tmp) * self.__HIST_DIV)
        rng = (0, max_)

        return succgappri, failgappri, bins, rng

    def __update_hist_maxopen(self, df, minunit):

        succflg = (df[GapFill.LBL_RESULT] == GapFill.RSL_SUCCESS)
        succdf = df[succflg]

        succgappri = succdf[GapFill.LBL_MAXOPNRNG].tolist()

        if not succgappri:
            max_ = 0
        else:
            max_ = max(succgappri)

        shiftl = 3
        tmp = shiftl - minunit

        maxrng = pow(10, tmp)
        ofs = pow(10, tmp - 2) * 5  # 切り上げ
        max_ = round(max_ + ofs, 1 - tmp)
        if max_ < maxrng:
            max_ = maxrng

        bins = int(max_ * pow(10, -tmp) * self.__HIST_DIV)
        rng = (0, max_)

        return succgappri, bins, rng

    def ___check_candlestickdata(self, df, monday):
        # 終値
        pre_df = df[df.index < (monday - dt.timedelta(days=1))]

        # 始値
        aft_df = df[df.index > (monday - dt.timedelta(days=1))]

        if pre_df.empty or aft_df.empty:
            flg = False
        else:
            flg = True

        return flg

    def __judge_gapfill(self, df, monday, gran, inst_id):
        """窓埋め成功/失敗判定メソッド
           [judge method of Gap-Fill success or fail]
        引数[Args]:
            df (pandas data frame) : ローソク足データ[candle stick data]
        戻り値[Returns]:
            jdg (boolean) : 判定結果
                            true: 窓埋め成功[Filling Gap success]
                            false: 窓埋め失敗[Filling Gap fail]
        """
        # 終値
        pre_df = df[df.index < (monday - dt.timedelta(days=1))]
        close_pri = pre_df.at[pre_df.index[-1], cs.LBL_CLOSE]

        # 始値
        aft_df = df[df.index > (monday - dt.timedelta(days=1))]
        open_pri = aft_df.at[aft_df.index[0], cs.LBL_OPEN]

        # スプレッド
        open_time = aft_df.index[0]
        spread = CandleStickData.get_spread(gran, inst_id, open_time)

        # 窓の幅
        gap_pri = abs(close_pri - open_pri)

        # 窓の方向
        if close_pri < open_pri:
            # 上に窓が開いた場合
            flgdir_up = True
            dir_ = "up"
            ext_df = aft_df[aft_df[cs.LBL_LOW] <= close_pri]
        else:
            # 下に窓が開いた場合
            flgdir_up = False
            dir_ = "down"
            ext_df = aft_df[aft_df[cs.LBL_HIGH] >= close_pri]

        # 窓埋め成功/失敗の判定結果
        # 窓埋め成功時の時刻
        if ext_df.empty:
            jdg_flg = False
            rst = GapFill.RSL_FAIL
            filltime = dt.datetime(year=1985, month=12, day=31)
        else:
            jdg_flg = True
            rst = GapFill.RSL_SUCCESS
            filltime = ext_df.iloc[0].name

        # 窓埋め前の最大開き幅
        ext2_df = aft_df[aft_df.index <= filltime]
        if ext2_df.empty:
            maxopngap = 0.0
        else:
            if flgdir_up is True:
                maxopnpri = ext2_df[cs.LBL_HIGH].max()
            else:
                maxopnpri = ext2_df[cs.LBL_LOW].min()
            maxopngap = abs(maxopnpri - open_pri)

        # 有効トレード判定結果
        vldflg = (spread / 2) < gap_pri

        # 出力
        record = pd.Series([rst,
                            dir_,
                            close_pri,
                            open_pri,
                            spread,
                            gap_pri,
                            filltime,
                            maxopngap,
                            vldflg],
                           index=self.__dfsmm.columns,
                           name=monday)

        return jdg_flg, record

    def __cb_btn_run(self):
        """Widget Button(実行)コールバックメソッド
           [Callback method of Widget Button(Execute)]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        self.__txtin_losscut.value = ""
        self.__txtin_gapprith.value = ""
        self.__hm.clear()
        self.__hm.clear()

        # 月曜のみを抽出する
        # Extract only Monday
        yesterday = dt.date.today() - dt.timedelta(days=1)
        str_ = self.__dtwdg_str.date
        str_ = utl.limit_upper(str_, yesterday)
        end_ = self.__dtwdg_end.date
        end_ = utl.limit_upper(end_, yesterday)

        mondaylist = []
        for n in range((end_ - str_).days):
            day = str_ + dt.timedelta(n)
            if day.weekday() == 0:
                dtmo = dt.datetime.combine(day, dt.time())
                mondaylist.append(dtmo)

        if not mondaylist:
            print("リストは空です")
        else:
            dfsmm = self.__dfsmm
            self.__csdlist1 = []
            validmondaylist = []
            rsllist = []
            dfsmm.drop(index=dfsmm.index, inplace=True)
            cnt = 0
            for monday in mondaylist:
                str_ = monday + dt.timedelta(days=-3, hours=20)
                end_ = monday + dt.timedelta(days=1)
                dtmstr = DateTimeManager(str_)
                dtmend = DateTimeManager(end_)

                inst_id = self.instrument_id
                inst = OandaIns.list[inst_id].oanda_name
                gran = OandaGrn.H1

                try:
                    csd = CandleStickData(gran, inst, dtmstr, dtmend)
                except V20Error as v20err:
                    print("-----V20Error: {}".format(v20err))
                except ConnectionError as cerr:
                    print("----- ConnectionError: {}".format(cerr))
                except Exception as excp:
                    print("----- Exception: {}".format(excp))

                # 解析可能データ判定
                okflg = self.___check_candlestickdata(csd.df, monday)

                if okflg is True:

                    # 窓埋め成功/失敗判定
                    jdg_flg, record = self.__judge_gapfill(csd.df,
                                                           monday,
                                                           gran,
                                                           inst_id)
                    if jdg_flg is True:
                        rsllist.append("成功")
                    else:
                        rsllist.append("失敗")

                    validmondaylist.append(monday)
                    self.__csdlist1.append(csd)
                    dfsmm = dfsmm.append(record)

                cnt = cnt + 1
                print("Fill-Gap Analyzing...  ( {} / {} )"
                      .format(cnt, len(mondaylist)))

            self.__src.data = {
                self.TBLLBL_DATE: validmondaylist,
                self.TBLLBL_RSLT: rsllist,
                self.TBLLBL_DIR: dfsmm[GapFill.LBL_DIR].tolist(),
                self.TBLLBL_CLSPRI: dfsmm[GapFill.LBL_CLOSEPRI].tolist(),
                self.TBLLBL_OPNPRI: dfsmm[GapFill.LBL_OPENPRI].tolist(),
                self.TBLLBL_SPREAD: dfsmm[GapFill.LBL_SPREAD].tolist(),
                self.TBLLBL_GAPPRI: dfsmm[GapFill.LBL_GAPPRI].tolist(),
                self.TBLLBL_FILLTIME: dfsmm[GapFill.LBL_FILLTIME].tolist(),
                self.TBLLBL_MAXOPNRNG: dfsmm[GapFill.LBL_MAXOPNRNG].tolist(),
            }

            self.__update_summary(dfsmm)
            minunit = OandaIns.list[inst_id].min_unit

            self.__update_hist(dfsmm, minunit)

            self.__dfsmm = dfsmm

    def __cb_dttbl(self, attr, old, new):
        """Widget DataTableコールバックメソッド
           [Callback method of Widget DataTable]
        引数[Args]:
            attr (str) : An attribute name on this object
            old (str) : Old strings
            new (str) : New strings
        戻り値[Returns]:
            なし[None]
        """
        idx = new[0]
        self.__csc1.set_dataframe(self.__csdlist1[idx], self.__dfsmm.iloc[idx])

    def __cb_btn_simrun(self):
        """Widget Button(シミュレーション実行)コールバックメソッド
           [Callback method of Widget Button(Execute simulation)]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """
        THIN_COE = 10   # 間引き係数
        MARGIN_COE = 1.3  # マージン係数
        MIN_DISP_AMP = 10  # 最低表示倍率係数

        if self.__dfsmm.empty:
            print("空です")
        else:
            inst_id = self.instrument_id
            minunit = OandaIns.list[inst_id].min_unit

            dfmst = self.__dfsmm[[GapFill.LBL_RESULT,
                                  GapFill.LBL_SPREAD,
                                  GapFill.LBL_GAPPRI,
                                  GapFill.LBL_MAXOPNRNG,
                                  GapFill.LBL_VALID]].copy()

            dfmst[GapFill.LBL_SPREAD] = dfmst[GapFill.LBL_SPREAD] / 2

            # 以下の条件を満たす場合トレードしないため、データフレームから除去する。
            # ・スプレッド < Gap Price
            df = dfmst[dfmst[GapFill.LBL_VALID] == utl.TRUE].copy()

            if not df.empty:
                minstep = OandaIns.normalize(inst_id, pow(0.1, minunit))

                maxgp = df[GapFill.LBL_GAPPRI].max()
                mingp = df[GapFill.LBL_GAPPRI].min()
                ystep = minstep * THIN_COE
                if maxgp < ystep:
                    end = ystep * MIN_DISP_AMP
                else:
                    end = maxgp * MARGIN_COE
                ylist = np.arange(0, end, ystep)
                ylist = np.array([i for i in ylist if mingp < i])

                df_flg1 = df[GapFill.LBL_RESULT] == GapFill.RSL_SUCCESS

                maxop = df[df_flg1][GapFill.LBL_MAXOPNRNG].max()
                xstep = minstep * THIN_COE
                if maxop < xstep:
                    end = xstep * MIN_DISP_AMP
                else:
                    end = maxop * MARGIN_COE

                xstep = ystep
                xlist = np.arange(0, end, xstep)

                htmap, map3d = self.__make_map(df, xlist, ylist)

                self.__hm.update(map3d, xlist, ylist, htmap,
                                 xstep, ystep, inst_id)

                x_max = self.__hm.max_coordinate[0]
                y_max = self.__hm.max_coordinate[1]
                x_max_str = x_max - xstep
                y_max_str = y_max - ystep
                x_max_end = x_max + xstep
                y_max_end = y_max + ystep

                x_max_str = utl.limit_lower(x_max_str, xlist[0])
                y_max_str = utl.limit_lower(y_max_str, ylist[0])
                x_max_end = utl.limit_upper(x_max_end, xlist[-1])
                y_max_end = utl.limit_upper(y_max_end, ylist[-1])

                xmaxlist = np.arange(x_max_str, x_max_end, minstep)
                ymaxlist = np.arange(y_max_str, y_max_end, minstep)
                htmap, map3d = self.__make_map(df, xmaxlist, ymaxlist)

                x = map3d[:, 0]
                y = map3d[:, 1]
                d = map3d[:, 2]
                maxidx = np.argmax(d)

                losscut = OandaIns.normalize(inst_id, x[maxidx])
                gapprith = OandaIns.normalize(inst_id, y[maxidx])
                self.__txtin_losscut.value = str(losscut)
                self.__txtin_gapprith.value = str(gapprith)

    def __make_map(self, df_, xlist, ylist):

        zlist_map = []
        map3d = np.empty((0, 3))
        cnt = 0

        for th in ylist:
            # 閾値未満
            df = df_[df_[GapFill.LBL_GAPPRI] < th].copy()
            df_flg1 = df[GapFill.LBL_RESULT] == GapFill.RSL_SUCCESS

            zlist = []
            for losscut in xlist:
                df_flg2 = losscut > df[GapFill.LBL_MAXOPNRNG]
                # 合計利益を計算
                dfpro = df[df_flg1 == df_flg2]
                profitsum = (dfpro[GapFill.LBL_GAPPRI] -
                             dfpro[GapFill.LBL_SPREAD]).sum()
                # 合計損失を計算
                lossdf = df[df_flg1 != df_flg2]
                losssum = (losscut + lossdf[GapFill.LBL_SPREAD]).sum()
                # 合計損益を計算
                prolossum = profitsum - losssum
                zlist.append(prolossum)

                nda = np.array([losscut, th, prolossum])
                map3d = np.vstack((map3d, nda))

            zlist_map.append(zlist)

            cnt = cnt + 1
            print("Sim: {}/{}" .format(cnt, len(ylist)))

        return zlist_map, map3d
