from bokeh.models.widgets import Button, DataTable, TableColumn
from bokeh.models.widgets import DateFormatter, NumberFormatter
from bokeh.layouts import layout, widgetbox
import autotrader.analyzer as ana
from autotrader.utils import DateTimeManager
from datetime import datetime, timedelta
from autotrader.oanda_common import OandaGrn
import autotrader.utils as utl
from bokeh.models import ColumnDataSource
from autotrader.analysis.candlestick import CandleStickChartBase
from autotrader.analysis.candlestick import CandleStickData
from oandapyV20.exceptions import V20Error
import autotrader.analysis.candlestick as cs
import pandas as pd
from bokeh.models.glyphs import Line
from bokeh.models import CrosshairTool, HoverTool
from autotrader.analysis.candlestick import CandleGlyph


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

        # プロット設定
        self._fig.toolbar_location = "right"
        self._fig.add_tools(CrosshairTool(line_color="pink",
                                          line_alpha=1))

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


class GapFill(object):
    """ GapFill
            - 窓埋めクラス[Gap-fill class]
    """

    LBL_DATA = "Data"
    LBL_RESULT = "Result"
    LBL_DIR = "Direction"
    LBL_CLOSEPRI = "Close Price"
    LBL_OPENPRI = "Open Pric"
    LBL_GAPPRI = "Gap Price"
    LBL_FILLTIME = "Filled Time"

    def __init__(self):
        """"コンストラクタ[Constructor]
        引数[Args]:
            なし[None]
        """
        # Widget Button:解析実行[Run analysis]
        self.__btn_run = Button(label="解析実行",
                                button_type="success",
                                sizing_mode='fixed',
                                default_size=200)
        self.__btn_run.on_click(self.__cb_btn_run)

        # Widget DataTable:解析結果[Result of analysis]
        self.TBLLBL_DATE = "Date"
        self.TBLLBL_RSLT = "Result"
        self.TBLLBL_CLSPRI = "Close Price"
        self.TBLLBL_OPNPRI = "Open Price"
        self.TBLLBL_DIR = "Direction"
        self.TBLLBL_GAPPRI = "Gap Price"
        self.TBLLBL_FILLTIME = "Gap Filled Time"

        self.__src = ColumnDataSource({self.TBLLBL_DATE: [],
                                       self.TBLLBL_RSLT: [],
                                       self.TBLLBL_CLSPRI: [],
                                       self.TBLLBL_OPNPRI: [],
                                       self.TBLLBL_DIR: [],
                                       self.TBLLBL_GAPPRI: [],
                                       self.TBLLBL_FILLTIME: [],
                                       })

        cols = [
            TableColumn(field=self.TBLLBL_DATE, title="Date",
                        formatter=DateFormatter()),
            TableColumn(field=self.TBLLBL_RSLT, title="Result"),
            TableColumn(field=self.TBLLBL_CLSPRI, title="Open Price",
                        formatter=NumberFormatter(format="0[.]000")),
            TableColumn(field=self.TBLLBL_OPNPRI, title="Close Price",
                        formatter=NumberFormatter(format="0[.]000")),
            TableColumn(field=self.TBLLBL_DIR, title="Direction"),
            TableColumn(field=self.TBLLBL_GAPPRI, title="Gap Price",
                        formatter=NumberFormatter(format="0[.]00000")),
            TableColumn(field=self.TBLLBL_FILLTIME, title="Gap Filled Time",
                        formatter=DateFormatter(format="%R")),
        ]

        self.__tbl = DataTable(source=self.__src,
                               columns=cols,
                               fit_columns=True,
                               height=200)
        self.__src.selected.on_change('indices', self.__cb_dttbl)

        self.__csc = CandleStickChart()
        self.__csdlist = []

        cols = [GapFill.LBL_DATA,
                GapFill.LBL_RESULT,
                GapFill.LBL_DIR,
                GapFill.LBL_CLOSEPRI,
                GapFill.LBL_OPENPRI,
                GapFill.LBL_GAPPRI,
                GapFill.LBL_FILLTIME]
        self.__dfsmm = pd.DataFrame(columns=cols)

    def get_layout(self):
        """レイアウトを取得する[get layout]
        引数[Args]:
            None
        戻り値[Returns]:
            layout (layout) : レイアウト[layout]
        """
        btnrun = self.__btn_run
        tbl = self.__tbl
        fig = self.__csc.get_model()

        tblfig = widgetbox(children=[tbl, fig], sizing_mode='stretch_width')

        self.__layout = layout(children=[[btnrun], [tblfig]],
                               sizing_mode='stretch_width')
        return(self.__layout)

    def __judge_GapFill(self, df, monday):
        """窓埋め成功/失敗判定メソッド
           [judge method of GapFill success or fail]
        引数[Args]:
            df (pandas data frame) : ローソク足データ[candle stick data]
        戻り値[Returns]:
            jdg (boolean) : 判定結果
                            true: 窓埋め成功[Filling Gap success]
                            false: 窓埋め失敗[Filling Gap fail]
        """

        pre_df = df[df.index < (monday - timedelta(days=1))]
        close_pri = pre_df.at[pre_df.index[-1], cs.LBL_CLOSE]

        aft_df = df[df.index > (monday - timedelta(days=1))]
        open_pri = aft_df.at[aft_df.index[0], cs.LBL_OPEN]

        gap_pri = abs(close_pri - open_pri)
        if close_pri < open_pri:
            # 上に窓が開いた場合
            dir_ = "upper"
            ext_df = aft_df[aft_df[cs.LBL_LOW] <= close_pri]
        else:
            # 下に窓が開いた場合
            dir_ = "lower"
            ext_df = aft_df[aft_df[cs.LBL_HIGH] >= close_pri]

        if ext_df.empty:
            jdg_flg = False
            jdg_data = "-"
        else:
            jdg_flg = True
            jdg_data = ext_df.iloc[0]

        return close_pri, open_pri, dir_, gap_pri, jdg_flg, jdg_data

    def __cb_btn_run(self):
        """Widget Button(実行)コールバックメソッド
           [Callback method of Widget Button(Execute)]
        引数[Args]:
            なし[None]
        戻り値[Returns]:
            なし[None]
        """

        # 月曜のみを抽出する
        # Extract only Monday
        now = datetime.now() - timedelta(hours=9)
        str_ = ana.get_datetime_str()
        str_ = utl.limit_upper(str_, now)
        end_ = ana.get_datetime_end()
        end_ = utl.limit_upper(end_, now) + timedelta(days=1)

        mondaylist = []
        for n in range((end_ - str_).days):
            day = str_ + timedelta(n)
            if day.weekday() == 0:
                mondaylist.append(day)

        if not mondaylist:
            print("リストは空です")
        else:
            self.__csdlist = []
            rsllist = []
            self.__dfsmm = self.__dfsmm.drop(range(len(self.__dfsmm)))
            cnt = 0
            for n in mondaylist:
                str_ = n + timedelta(days=-3, hours=20)
                end_ = n + timedelta(days=1)
                dtmstr = DateTimeManager(str_)
                dtmend = DateTimeManager(end_)

                inst = ana.get_instrument()
                gran = OandaGrn.H1

                try:
                    csd = CandleStickData(gran, inst, dtmstr, dtmend)
                except V20Error as v20err:
                    print("-----V20Error: {}".format(v20err))
                except ConnectionError as cerr:
                    print("----- ConnectionError: {}".format(cerr))
                except Exception as excp:
                    print("----- Exception: {}".format(excp))

                # print(df)
                self.__csdlist.append(csd)

                # 窓埋め成功/失敗判定
                close_pri, open_pri, dir_, gap_pri, jdg_flg, jdg_data = self.__judge_GapFill(
                    csd.df, n)
                if jdg_flg is True:
                    rsl = True
                    rsllist.append("成功")
                else:
                    rsl = False
                    rsllist.append("失敗")

                if jdg_flg:
                    filltime = jdg_data.name
                else:
                    filltime = datetime(year=1985, month=12,
                                        day=31, hour=23, minute=59, second=59)
                print(filltime)

                record = pd.Series([n, rsl, dir_, close_pri, open_pri, gap_pri, filltime],
                                   index=self.__dfsmm.columns)
                self.__dfsmm = self.__dfsmm.append(record,  ignore_index=True)

                cnt = cnt + 1

            print("dflist:{}" .format(len(self.__csdlist)))

            self.__src.data = {
                self.TBLLBL_DATE: mondaylist,
                self.TBLLBL_RSLT: rsllist,
                self.TBLLBL_DIR: self.__dfsmm[GapFill.LBL_DIR].tolist(),
                self.TBLLBL_OPNPRI: self.__dfsmm[GapFill.LBL_OPENPRI].tolist(),
                self.TBLLBL_CLSPRI: self.__dfsmm[GapFill.LBL_CLOSEPRI].tolist(),
                self.TBLLBL_GAPPRI: self.__dfsmm[GapFill.LBL_GAPPRI].tolist(),
                self.TBLLBL_FILLTIME: self.__dfsmm[GapFill.LBL_FILLTIME].tolist(),
            }

        print("Called cb_btn_run")

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
        self.__csc.set_dataframe(self.__csdlist[idx], self.__dfsmm.iloc[idx])
