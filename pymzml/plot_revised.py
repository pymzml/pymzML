# -*- coding: utf-8 -*-
# encoding: utf-8
"""
Plotting functions for pymzML.
The Factory object can hold several plots with several data traces each.
The plot will be rendered as interactive plotly plots.
"""

# pymzml
#
# Copyright (C) 2010-2011 M. Kösters, C. Fufezan, S. Schulze
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import plotly.offline as plt
import plotly.graph_objs as go
from plotly import tools


class Factory(object):
    def __init__(self, filename="spectrum_plot.html"):
        """
        Class to plot pymzml.spec.Spectrum using plotly.

        Args:
            filename (str): Name for the output file. Default = "spectrum_plot.html"

        Example:

            >>> import pymzml, get_example_file
            >>> mzMLFile = 'profile-mass-spectrum.mzml'
            >>> example_file = get_example_file.open_example(mzMLFile)
            >>> run = pymzml.run.Run("../mzML_example_files/"+mzMLFile,
            ...     precisionMSn = 250e-6
            ... )
            >>> p = pymzml.plot.Factory()
            >>> for spec in run:
            >>>     p.new_plot()
            >>>     p.add(spec.peaks, color=(200,00,00), style='sticks')
            >>>     p.add(spec.centroided_peaks, color=(00,00,00), style='sticks')
            >>>     p.add(spec.reprofiled_peaks, color=(00,255,00), style='sticks')
            >>>     p.save(
            ...         filename="output/plotAspect.xhtml",
            ...         mz_range = (745.2,745.6)
            ...     )

        NOTE:
            This should go into example_script/plot_spectrum.py

        """
        self.filename = filename
        self.plots = []
        self.titles = []
        self.lookup = dict()
        self.y_max = []
        self.x_max = []
        self.offset = 1
        self.precisions = []
        self.styles = ["sticks", "triangle", "spline", "linear"]
        self.widths = ["small", "medium", "big"]
        self.style_parameters = {
            "sticks": {
                "mode": "lines+text",
                "shape": "linear",
                "filling": "tozeroy",
                "width": lambda n: self.precisions[n],
            },
            "triangle": {
                "mode": "lines+text",
                "shape": "linear",
                "filling": "tozeroy",
                "width": lambda n: self.scalings[n],
            },
            "lines": {"mode": "lines+text", "shape": "spline", "filling": None},
            "points": {"mode": "markers", "shape": "linear", "filling": None},
        }

    def new_plot(self, precision="5e-6", title=None):
        """
        Add new plot to the plotting Factory.

        Args:
            header (str): an optional title that will be printed above the plot
            mz_range (tuple): Boundaries of the new plot
            normalize (boolean): whether or not the individal data sets
                are normalized in the plot
            precision (float): measuring precision used in handler.
                Default 5e-6.
        """
        self.precisions.append(precision)
        self.plots.append([])
        return

    def add(
        self,
        data,
        color=(0, 0, 0),
        style="sticks",
        mz_range=None,
        opacity=0.8,
        name=None,
        plot_num=-1,
        title=None,
    ):
        """
        Add data to the graph.

        Arguments:
            data (list): The data added to the graph. Must be list of
                tuples, like (mz,i) or (mz1, mz2, i, string)
                style (str): plotting style. Default = "sticks".\n
                Currently supported styles are:\n
                    *   'sticks'\n
                    *   'triangle' (small, medium or big)\n
                    *   'spline'   (top, medium or bottom)\n
                    *   'linear'   (top, medium or bottom)\n
            color (tuple): color encoded in RGB. Default = (0,0,0)
            mz_range (tuple): Boundaries that should be added to the current
                plot
            opacity (float): opacity of the data points\n
            name (str): name of data in legend\n
            plot_num (int): Add data to plot[plot_num]\n

        """
        style_attribs = style.split(".")
        assert (
            len(style_attribs) == 3
        ), "Style must set datatype, plotting style and width:\n{0}".format(
            style_attribs
        )

        if len(self.plots) == 0:
            self.new_plot(title=title)

        precision = float(self.precisions[plot_num])

        if style_attribs[0] == "label":
            as_anno = True
        elif style_attribs[0] == "data":
            as_anno = False
        else:
            raise Exception("Style must be declare trace as data or annotation")

        # use numpy arrays
        x_values = []
        y_values = []
        txt_values = []

        if as_anno:
            for vars in data:
                mz, i = vars[0], vars[1]
                txt = vars[2]
                x_values.extend(
                    [
                        mz
                        - (
                            mz * precision
                        ),  # self.style_parameters[style_attribs[1]]['width'])(plot_num)
                        mz,
                        mz
                        + (
                            mz * precision
                        ),  # self.style_parameters[style_attribs[1]]['width'])(plot_num)
                        None,
                    ]
                )
                y_values.extend(
                    [
                        0,  # y pos for spline, offset for linear, also via dict grab
                        i,  # offset for linear
                        0,  # ypos for spline, offset for linear, also via dict grab
                        None,
                    ]
                )
                txt_values.extend([None, txt, None, None])
        else:
            for mz, i in data:
                x_values.extend(
                    [mz - (mz * precision), mz, mz + (mz * precision), None]
                )
                y_values.extend([0.0, i, 0.0, None])

        data = go.Scatter(
            {
                "x": x_values,
                "y": y_values,
                "text": txt_values,
                "textfont": {"family": "Helvetica", "size": 10, "color": "#000000"},
                "textposition": "top center",
                "visible": "True",
                "marker": {"size": 10},
                "mode": self.style_parameters[style_attribs[1]]["mode"],
                "name": name,
                "line": {
                    "color": "rgb" + str(color),
                    "width": 1,
                    "shape": self.style_parameters[style_attribs[1]]["shape"],
                },
                "fill": self.style_parameters[style_attribs[1]]["filling"],
                "fillcolor": {
                    "color": "rgba" + str((color[0], color[1], color[2], opacity))
                },
                "opacity": opacity,
            }
        )

        self.plots[plot_num].append(data)
        return

    def info(self):
        """
        Prints summary about the plotting factory, i.e.how many plots and how
        many datasets per plot.
        """
        print(
            """
        Factory holds {0} unique plots""".format(
                len(self.plots)
            )
        )
        for i, plot in enumerate(self.plots):
            print("\t\tPlot {0} holds {1} unique datasets".format(i, len(plot)))
            for j, dataset in enumerate(plot):
                print(
                    "\t\t\tDataset {0} holds {1} datapoints".format(
                        j, len(dataset["x"])
                    )
                )

        print()
        return

    def get_data(self):
        """
        Return data and layout in JSON format.

        Returns:
            plots (dict): JSON compatible python dict
        """
        for i, plot in enumerate(self.plots):
            for j, trace in enumerate(plot):
                self.plots[i][j]["y"] = [
                    self.function_mapper[x](i) if x in self.function_mapper else x
                    for x in trace["y"]
                ]
        return self.plots

    def save(self, filename=None, xLimits=None):
        """
        Saves all plots and their data points that have been added to the
        plotFactory.

        Args:
        filename (str): Name for the output file. Default = "spectrum_plot.html"
        mz_range (tuple): m/z range which should be considered [start, end].
            Default = None
        """
        plot_number = len(self.plots)

        rows, cols = int(math.ceil(plot_number / float(2))), 2

        if plot_number % 2 == 0:
            my_figure = tools.make_subplots(
                rows=rows, cols=cols, vertical_spacing=0.6 / rows
            )
        else:
            specs = [[{}, {}] for x in range(rows - 1)]
            specs.append([{"colspan": 2}, None])
            my_figure = tools.make_subplots(
                rows=rows,
                cols=cols,
                vertical_spacing=0.6 / rows,
                specs=specs,
                subplot_titles=self.titles,
            )

        for i, plot in enumerate(self.plots):
            for j, trace in enumerate(plot):
                my_figure.append_trace(trace, int(math.floor((i / 2) + 1)), (i % 2) + 1)

        for i in range(plot_number):
            if xLimits:
                my_figure["layout"]["xaxis" + str(i + 1)].update(range=xLimits[i])
            my_figure["layout"]["xaxis" + str(i + 1)].update(title="m/z ")
            my_figure["layout"]["yaxis" + str(i + 1)].update(title="Intensity")
            my_figure["layout"]["xaxis" + str(i + 1)].update(
                titlefont={"color": "#000000", "family": "Helvetica", "size": "18"}
            )
            my_figure["layout"]["yaxis" + str(i + 1)].update(
                titlefont={"color": "#000000", "family": "Helvetica", "size": "18"}
            )

        my_figure["layout"]["legend"].update(font={"size": 10, "color": "#FF0000"})

        if self.filename is None:
            _filename = "spectrum_plot.html"
        else:
            _filename = self.filename

        if filename is not None:
            # save fkt name definition overrules original filename
            _filename = filename

        plt.plot(my_figure, filename=_filename, auto_open=False)
        return


if __name__ == "__main__":
    data = [(1, 10), (2, 20)]
    anno = [(1, 10, "blub"), (2, 20, "bla")]
    Fac = Factory()

    print("'style='data.sticks.medium'")
    Fac.add(data, style="data.sticks.medium")
    print()
    print("style='data.triangle.small'")
    Fac.add(data, style="data.triangle.small")
    print()
    Fac.add(anno, style="label.sticks.medium")
    Fac.save(filename="tmp.html")
