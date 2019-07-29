#!/usr/bin/env python3.4
# encoding: utf-8
"""
Plot a test spectrum for different plotting styles
"""
import pymzml
import os
import sys
import test_file_paths
from pymzml.plot import Factory
import unittest


class PlotTest(unittest.TestCase):
    """
    """

    def setUp(self):
        self.paths = test_file_paths.paths
        self.path = self.paths[2]
        self.Run = pymzml.run.Reader(self.path)
        self.spec = self.Run[6]

        self.layout = {
            "font": {"family": "Arial", "size": 20, "color": "#000000"},
            "autosize": False,
            "width": 1700,
            "height": 700,
            "margin": {"l": 100, "r": 80, "t": 100, "b": 60},
            # 'separatethousands' : False,
            # 'autoexpand':True,
            "xaxis1": {
                "type": "linear",
                "color": "#000000",
                "title": "<i>m/z</i>",
                "titlefont": {"family": "Arial", "size": 24, "color": "#000000"},
                "tickmode": "auto",
                "nticks": 0,
                "tickprefix": "",
                "ticksuffix": "",
                "showticklabels": True,
                "tickfont": {"family": "Arial", "size": 20, "color": "rgb(0, 0, 0)"},
                # "tickangle": "auto",
                "tickformat": "",
                "showexponent": "all",
                "exponentformat": "B",
                "ticklen": 5,
                "tickwidth": 1,
                "tickcolor": "#000000",
                "ticks": "outside",
                "showline": True,
                "mirror": False,
                "showgrid": False,
                "zerolinecolor": "rgb(0, 0, 0)",
                "zerolinewidth": 1,
                "zeroline": False,
                "anchor": "y",
                "side": "bottom",
                "tick0": 0,
                "dtick": 100,
            },
            "yaxis1": {
                "type": "linear",
                "color": "#000000",
                "title": "Intensity",
                "titlefont": {"family": "Arial", "size": 24, "color": "#000000"},
                "nticks": 0,
                "tickprefix": "",
                "ticksuffix": "",
                "showticklabels": True,
                "tickfont": {"family": "Arial", "size": 20, "color": "rgb(0, 0, 0)"},
                # "tickangle": "auto",
                "tickformat": "",
                "showexponent": "all",
                "exponentformat": "B",
                # 'separatethousands' : True,
                "ticklen": 5,
                "tickwidth": 1,
                "tickcolor": "#000000",
                "ticks": "outside",
                "showline": True,
                "mirror": False,
                "showgrid": False,
                "zerolinecolor": "rgb(0, 0, 0)",
                "zerolinewidth": 1,
                "zeroline": False,
                "anchor": "x",
                "side": "left",
                "tick0": 0,
                "dtick": 20000000,
            },
            "legend": {
                "bgcolor": "#fff",
                "bordercolor": "#444",
                "borderwidth": 0,
                "font": {"family": "Arial", "size": 20, "color": "#000000"},
                "orientation": "v",
                "traceorder": "normal",
                "x": 1.02,
                "xanchor": "left",
                "y": 1,
                "yanchor": "auto",
            },
        }
        self.test_styles = [
            ("lines", (200, 200, 200), "solid", 0.8, None, None),
            ("sticks", (200, 0, 0), "solid", 0.8, None, (200, 300)),
            ("points", (0, 0, 200), "solid", 0.8, None, None),
            ("label.sticks", (0, 0, 200), "dot", 0.8, None, None),
            ("triangle.big", (200, 0, 200), "solid", 0.8, None, None),
            ("triangle.small", (200, 0, 0), "solid", 0.8, None, None),
            ("label.triangle.MS_precision", (0, 200, 0), "dash", 0.8, None, None),
            ("label.spline", (0, 200, 0), "dash", 0.3, None, None),
            ("label.triangle.small", (0, 200, 0), "solid", 0.8, None, None),
            ("label.linear.bottom", (0, 200, 100), "solid", 0.8, self.layout, None),
        ]
        self.pf = Factory()
        self.file_name = os.path.join(os.path.dirname(self.path), "test_plot.html")

    def test_new_plot(self):
        self.pf.new_plot(MS_precision="100e-6", title="test")
        self.assertEqual(self.pf.MS_precisions[0], "100e-6")
        self.assertEqual(self.pf.titles[0], "test")
        self.pf.new_plot()
        self.assertEqual(len(self.pf.plots), 2)
        self.assertEqual(self.pf.MS_precisions[1], "5e-6")
        self.assertEqual(self.pf.titles[1], None)
        self.pf = Factory()

    def test_add_plots(self):
        for plotnumber, plot in enumerate(self.test_styles):
            self.pf.new_plot()
            style, color, dash, opacity, layout, mz_range = plot
            split_style = style.split(".")
            if split_style[0] == "label":
                self.pf.add(
                    self.spec.highest_peaks(100),
                    color=(200, 200, 200),
                    style="lines",
                    name="datapoints",
                    title="test spec plot",
                    plot_num=plotnumber,
                    mz_range=mz_range,
                )
                label_list = []
                for peak in self.spec.highest_peaks(100):
                    label_list.append((peak[0], 100, "spline_top", "label"))
                self.pf.add(
                    label_list,
                    color=color,
                    style=style,
                    name="Label",
                    opacity=opacity,
                    dash=dash,
                    title="test spec plot",
                    plot_num=plotnumber,
                    mz_range=mz_range,
                )
                self.assertEqual(len(self.pf.plots[plotnumber]), 2)
            else:
                peak_list = self.spec.highest_peaks(100)
                self.pf.add(
                    peak_list,
                    color=color,
                    style=style,
                    name="Label",
                    opacity=opacity,
                    dash=dash,
                    title="test spec plot",
                    plot_num=plotnumber,
                    mz_range=mz_range,
                )

            self.assertEqual(
                self.pf.plots[plotnumber][-1]["line"]["color"],
                "rgba({0}, {1}, {2}, {3})".format(
                    color[0], color[1], color[2], opacity
                ),
            )
            self.assertEqual(self.pf.plots[plotnumber][-1]["line"]["dash"], dash)
            if "label" in style:
                if "spline" in style:
                    mode = "lines+markers+text"
                else:
                    mode = "text+lines"
            elif style == "points":
                mode = "markers"
            else:
                mode = "lines"
            self.assertEqual(self.pf.plots[plotnumber][-1]["mode"], mode)
            if mz_range is not None:
                self.assertLessEqual(self.pf.x_max[plotnumber], mz_range[1])
        self.assertEqual(len(self.pf.plots), len(self.test_styles))

    def test_save_plot(self):
        self.pf.add(
            self.spec.highest_peaks(100),
            color=(200, 200, 200),
            style="sticks",
            name="datapoints",
        )
        self.pf.save(filename=self.file_name, layout=self.layout)
        self.assertTrue(os.path.exists(self.file_name))

    def tearDown(self):
        if os.path.exists(self.file_name):
            os.remove(self.file_name)


if __name__ == "__main__":
    unittest.main(verbosity=3)
