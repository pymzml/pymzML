# -*- coding: utf-8 -*-
# encoding: utf-8
"""
Plotting functions for pymzML.
The Factory object can hold several plots with several data traces each.
The data can be visualized as an interactive plotly plot or be exported as JSON.
"""

# pymzml
#
# Copyright (C) 2010-2016 M. Kösters, C. Fufezan, S. Schulze
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms fo the GNU General Public License as published by
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

import sys
import math
import warnings


# Fail gracefully if no plotly installed
try:
    import plotly.offline as plt
    import plotly.graph_objs as go
    from plotly import tools
except ImportError:
    warnings.warn("Plotly is required for plotting support.", ImportWarning)


from . import spec


class Factory(object):
    def __init__(self, filename=None):
        """
        Interface to visualize m/z or profile data using plotly (https://plot.ly/).

        Arguments:
            filename (str): Name for the output file. Default = "spectrum_plot.html"

        """
        self.filename = filename
        self.plots = []
        self.titles = []
        self.lookup = dict()
        self.y_max = []
        self.y_min = []
        self.x_max = []
        self.x_min = []
        self.offset = 1
        self.MS_precisions = []
        self.function_mapper = {
            "-__splineOffset__0": self.__return_neg_offset_0,
            "max_intensity": self.__return_max_y,
        }
        self.style_options = {"line.width": 1}  # default value

    def __return_max_y(self, i):
        """
        """
        return self.y_max[i]

    def __return_neg_offset_0(self, i):
        """
        """
        return 0.0 - (self.y_max[i] * (self.offset * 0.05))

    def new_plot(self, MS_precision="5e-6", title=None):
        """
        Add new plot to the plotting Factory.
        Every plot will be put into the x * 2 grid of one single figure.

        Keyword Arguments:
            title (str): an optional title that will be printed above the plot
            MS_precision (float): measuring MS_precision used in handler.
                Default 5e-6.

        Note:
            Old function newPlot() is still working. However, the new syntax
            should be used.

        """
        self.MS_precisions.append(MS_precision)
        self.plots.append([])
        self.titles.append(title)
        return

    def newPlot(self, MS_precision="5e-6", title=None):
        """Deprecated since version 1.2."""
        # Is this ok, pass the Factory.self to Spectrum class???
        # Id just make deprecation warning a function independent of any class
        # Also, this just looks wrong
        spec.Spectrum.deprecation_warning(
            self, function_name=sys._getframe().f_code.co_name
        )
        self.new_plot(MS_precision=MS_precision, title=title)

    def add(
        self,
        data,
        color=(0, 0, 0),
        style="sticks",
        mz_range=None,
        int_range=None,
        opacity=0.8,
        dash="solid",
        name=None,
        plot_num=-1,
        title=None,
    ):
        """
        Add data to the graph.

        Arguments:
            data (list): The data added to the graph. Must be list of  tuples with
                the following format. Note that i can be set to 'max_intensity' for
                setting the label position to the maximum intensity.
                    *   (mz,i) for all styles, except label,
                    *   (mz,i, string) for label.hoverinfo, .sticks and .triangle
                    *   (mz1, mz2, i, string) for label.linear and .spline

        Keyword Arguments:
            color (tuple): color encoded in RGB. Default = (0,0,0)
            style (str): plotting style. Default = "sticks".
                Currently supported styles are:
                    *   'lines':
                        Datapoints connected by lines
                    *   'points':
                        Datapoints without connection
                    *   'sticks':
                        Vertical line at given m/z (corresponds to centroided peaks)
                    *   'triangle' (MS_precision, micro, tiny, small, medium, big):
                        The top of the triangle corresponds to the given m/z, the width
                        corresponds to he given format, e.g. 'triangle.MS_precision'
                    *   'label.hoverinfo':
                        Label string appears as plotly hover info
                    *   'label.linear'   (top, medium or bottom)
                    *   'label.spline'   (top, medium or bottom)
                    *   'label.sticks'
                    *   'label.triangle' (small, medium or big)
            mz_range (list): Boundaries that should be added to the current
                plot
            int_range (list): Boundaries that should be added to the current
                plot
            opacity (float): opacity of the data points
            dash (str): type of line ('solid', 'dash', 'longdash', 'dot', 'dashdot', 'longdashdot')
            name (str): name of data in legend
            plot_num (int): Add data to plot[plot_num]
            title (str): an optional title that will be printed above the plot

        Note:
            The mz_range and int_range in the add() function sets the limits of datapoints
            added to the plot. This is in contrast to defining a range in the layout, which
            only defines the area that is depicted (i.e. the zoom) but still adds the datapoints to the plot
            (can be seen by zooming out).

        """
        if len(self.plots) == 0:
            self.new_plot(title=title)
        if mz_range is None:
            mz_range = [-float("Inf"), float("Inf")]
        if int_range is None:
            int_range = [-float("Inf"), float("Inf")]
        if len(self.x_max) < len(self.plots):
            self.x_max.append(mz_range[1])
            self.x_min.append(mz_range[0])
        if len(self.y_max) < len(self.plots):
            self.y_max.append(int_range[1])
            self.y_min.append(int_range[0])

        # Init variables
        filling = None
        mode = "lines"
        x_values = []
        y_values = []
        txt = []

        style = style.split(".")
        MS_precision = float(self.MS_precisions[plot_num])

        if len(style) == 3:
            pos = style[2]
            available_pos = [
                "MS_precision",
                "micro",
                "tiny",
                "small",
                "medium",
                "big",
                "top",
                "bottom",
            ]
            if pos not in available_pos:
                raise Exception(
                    "Position must one of the following: {0}".format(available_pos)
                )
        else:
            pos = None
        if style[0] == "label":
            mode = "text+lines"
            if len(data[0]) < 3:
                raise Exception(
                    """
                    Must have at least (mz, i, annotation) in data
                    when using labels
                    """
                )
            if style[1] == "hoverinfo":
                shape = "linear"
                mode = None
                filling = None
                for data_tuple in data:
                    x_values.append(data_tuple[0])
                    y_values.append(data_tuple[1])
                    txt.append(data_tuple[2])

            elif style[1] == "sticks":
                shape = "linear"
                filling = "tozeroy"
                for x in data:
                    y_pos = x[1]
                    x_values += x[0], x[0], x[0], None
                    y_values += 0.0, y_pos, 0.0, None
                    txt += None, x[2], None, None

            elif style[1] == "triangle":
                if not pos:
                    pos = "medium"
                triangle_pos_list = [
                    "MS_precision",
                    "micro",
                    "tiny",
                    "small",
                    "medium",
                    "big",
                ]
                if pos not in triangle_pos_list:
                    raise Exception("Position must be in {0}".format(triangle_pos_list))

                shape = "linear"
                filling = "tozeroy"
                for x in data:
                    x_max = self.x_max[plot_num]
                    y_max = x[1]
                    y_values += 0.0, y_max, 0.0, None
                    txt += None, x[2], None, None

                    if pos == "MS_precision":
                        x_values += (
                            x[0] - (x[0] * MS_precision),
                            x[0],
                            x[0] + (x[0] * MS_precision),
                            None,
                        )
                        continue
                    elif pos == "micro":
                        rel_width = 1 / float(10000)
                    elif pos == "tiny":
                        rel_width = 1 / float(2000)
                    elif pos == "small":
                        rel_width = 1 / float(200)
                    elif pos == "medium":
                        rel_width = 1 / float(100)
                    elif pos == "big":
                        rel_width = 1 / float(50)
                    x_values += (
                        x[0] - (x_max * rel_width),
                        x[0],
                        x[0] + (x_max * rel_width),
                        None,
                    )

            elif style[1] == "spline":
                mode = "lines+markers+text"
                shape = "spline"
                txt = []
                if not pos:
                    pos = "top"
                for x in data:
                    if x[2] == "max_intensity":
                        y_max = self.y_max[plot_num]
                    else:
                        y_max = x[1]
                    if pos == "top":
                        y_pos = y_max
                        offset = y_max + (y_max * 0.1)

                    elif pos == "medium":
                        print(
                            """'
                            {0}
                            is not working atm for
                            {1}
                            """.format(
                                pos, style
                            )
                        )
                        sys.exit(0)
                        y_pos = x[2] / 2
                        offset = "__splineOffset__"

                    elif pos == "bottom":
                        y_pos = 0.0
                        offset = "-__splineOffset__0"

                    x_values += x[0], (x[0] + x[1]) / 2, x[1], None
                    y_values += y_pos, str(offset), y_pos, None
                    txt += None, x[3], None, None

            elif style[1] == "linear":
                shape = "linear"
                if not pos:
                    pos = "bottom"
                for x in data:
                    if x[2] == "max_intensity":
                        y_max = self.y_max[plot_num]
                    else:
                        y_max = x[1]
                    if pos == "top":
                        y_pos = y_max
                        offset = y_max + (y_max * 0.1)
                    elif pos == "medium":
                        print(
                            """'
                            {0}
                            is not working atm for
                            {1}
                            """.format(
                                pos, style
                            )
                        )
                        sys.exit(0)
                        y_pos = x[2] / 2
                        offset = "+__splineOffset__"
                    elif pos == "bottom":
                        y_pos = 0.0
                        offset = "-__splineOffset__0"

                    x_values += x[0], (x[0] + x[1]) / 2, x[1], None
                    y_values += str(offset), str(offset), str(offset), None
                    txt += None, x[3], None, None

            # elif style[1] == 'lines':
            #         shape = 'linear'
            #         filling = 'tozeroy'
            #         for x in data:
            #             y_pos = 'self.y_max[i]'
            #             x_values += x[0], x[0], x[0], None
            #             y_values += .0, y_pos, .0, None
            #             txt     += None, x[2], None, None

            else:
                raise Exception(
                    """
                    Unknown label type
                    Currently supported are:
                    -> linear
                    -> spline
                    -> sticks
                    -> triangle
                    """
                )

        elif style[0] in ["sticks", "triangle", "lines", "points"]:
            x_vals = [
                mz
                for mz, i in data
                if mz_range[0] <= mz <= mz_range[1]
                and int_range[0] <= i <= int_range[1]
            ]
            y_vals = [
                i
                for mz, i in data
                if mz_range[0] <= mz <= mz_range[1]
                and int_range[0] <= i <= int_range[1]
            ]
            y_max = max(y_vals)
            y_min = min(y_vals)
            x_max = max(x_vals)
            x_min = min(x_vals)

            if self.x_max[plot_num] == float("Inf") or self.x_max[plot_num] < x_max:
                self.x_max[plot_num] = x_max
            if self.x_min[plot_num] == -float("Inf") or self.x_min[plot_num] > x_min:
                self.x_min[plot_num] = x_min
            if self.y_max[plot_num] == float("Inf") or self.y_max[plot_num] < y_max:
                self.y_max[plot_num] = y_max
            if self.y_min[plot_num] == -float("Inf") or self.y_min[plot_num] > y_min:
                self.y_min[plot_num] = y_min

            if style[0] == "sticks":
                shape = "linear"
                mode = "lines"
                filling = "tozeroy"
                for x in zip(x_vals, y_vals):
                    y_pos = x[1]
                    x_values += x[0], x[0], x[0], None
                    y_values += 0.0, y_pos, 0.0, None

            elif style[0] == "triangle":
                if len(style) == 2:
                    pos = style[1]
                else:
                    pos = "medium"
                triangle_pos_list = [
                    "MS_precision",
                    "micro",
                    "tiny",
                    "small",
                    "medium",
                    "big",
                ]
                if pos not in triangle_pos_list:
                    raise Exception("Position must be in {0}".format(triangle_pos_list))
                shape = "linear"
                filling = "tozeroy"
                for x in zip(x_vals, y_vals):
                    x_max = self.x_max[plot_num]
                    y_pos = x[1]
                    y_values += 0.0, y_pos, 0.0, None
                    if pos == "MS_precision":
                        x_values += (
                            x[0] - (x[0] * MS_precision),
                            x[0],
                            x[0] + (x[0] * MS_precision),
                            None,
                        )
                        continue
                    elif pos == "micro":
                        rel_width = 1 / float(10000)
                    elif pos == "tiny":
                        rel_width = 1 / float(2000)
                    elif pos == "small":
                        rel_width = 1 / float(200)
                    elif pos == "medium":
                        rel_width = 1 / float(100)
                    elif pos == "big":
                        rel_width = 1 / float(50)
                    x_values += (
                        x[0] - (x_max * rel_width),
                        x[0],
                        x[0] + (x_max * rel_width),
                        None,
                    )

            elif style[0] == "lines":
                mode = "lines"
                shape = "linear"
                for x in zip(x_vals, y_vals):
                    x_values.append(x[0])
                    y_values.append(x[1])

            elif style[0] == "points":
                mode = "markers"
                shape = "linear"
                x_values = x_vals
                y_values = y_vals

        else:
            raise Exception(
                """
                Invalid plotting style
                Currently supported are:
                -> lines
                -> points
                -> sticks
                -> triangle
                """
            )

        trace = go.Scatter(
            {
                "x": x_values,
                "y": y_values,
                "text": txt,
                "textfont": {"family": "Helvetica", "size": 10, "color": "#000000"},
                "textposition": "top center",
                "visible": True,
                "marker": {
                    "size": 10,
                    "color": "rgba" + str((color[0], color[1], color[2], opacity)),
                },
                "mode": mode,
                "name": name,
                "line": {
                    "color": "rgba" + str((color[0], color[1], color[2], opacity)),
                    "width": self.style_options["line.width"],
                    "shape": shape,
                    "dash": dash,
                },
                "fill": filling,
                "fillcolor": "rgba" + str((color[0], color[1], color[2], opacity)),
                "opacity": opacity,
            }
        )

        self.plots[plot_num].append(trace)
        return trace

    def info(self):
        """
        Prints summary about the plotting factory, i.e. how many plots and how
        many datasets per plot.
        """
        print(
            """
            Factory holds {0} unique plots
            """.format(
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

    def save(self, filename=None, mz_range=None, int_range=None, layout=None):
        """
        Saves all plots and their data points that have been added to the
        plotFactory.

        Keyword Arguments:
            filename (str): Name for the output file. Default = "spectrum_plot.html"
            mz_range (list): m/z range which should be considered [start, end].
                Default = None
            int_range (list): intensity range which should be considered [min, max].
                Default = None
            layout (dict): dictionary containing layout information in plotly style

        Note:
            mz_range and int_range defined here will be applied to all subplots in
            the current plot, i.e. ranges defined when adding a subplot will be
            overwritten. To avoid this, a list of lists can be given in the order
            corresponding to the subplots.
        """
        plot_number = len(self.plots)
        rows, cols = int(math.ceil(plot_number / float(2))), 2
        if plot_number % 2 == 0:
            my_figure = tools.make_subplots(
                rows=rows,
                cols=cols,
                vertical_spacing=0.6 / rows,
                subplot_titles=self.titles,
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
            print(int(math.floor((i / 2) + 1)), (i % 2) + 1)
            for j, trace in enumerate(plot):
                trace["y"] = [
                    self.function_mapper[x](i) if x in self.function_mapper else x
                    for x in trace["y"]
                ]
                my_figure.append_trace(trace, int(math.floor((i / 2) + 1)), (i % 2) + 1)

        for i in range(plot_number):
            xaxis_key = "xaxis{0}".format(i + 1)
            if mz_range:
                if mz_range[0] == list or mz_range[0] == tuple:
                    # if list and not list of lists, apply same for all
                    my_figure["layout"][xaxis_key].update(range=mz_range[i])
                    my_figure["layout"][xaxis_key]["autorange"] = False
                elif mz_range[0] == int or mz_range[0] == float:
                    my_figure["layout"][xaxis_key]["range"] = mz_range
                    my_figure["layout"][xaxis_key]["autorange"] = False
            yaxis_key = "yaxis{0}".format(i + 1)
            if int_range:
                if int_range[0] == list or int_range[0] == tuple:
                    # if list and not list of lists, apply same for all
                    my_figure["layout"][yaxis_key].update(range=int_range[i])
                    my_figure["layout"][yaxis_key]["autorange"] = False
                elif int_range[0] == int or int_range[0] == float:
                    my_figure["layout"][yaxis_key]["range"] = int_range
                    my_figure["layout"][yaxis_key]["autorange"] = False

            my_figure["layout"][xaxis_key].update(title="m/z ")
            my_figure["layout"][yaxis_key].update(title="Intensity")
            my_figure["layout"][xaxis_key].update(
                titlefont={"color": "#000000", "family": "Helvetica", "size": 18}
            )
            my_figure["layout"][yaxis_key].update(
                titlefont={"color": "#000000", "family": "Helvetica", "size": 18}
            )

        my_figure["layout"]["legend"].update(font={"size": 10, "color": "#FF0000"})
        if layout:
            my_figure["layout"].update(layout)
        if self.filename is None:
            _filename = "spectrum_plot.html"
        else:
            _filename = self.filename

        if filename is not None:
            # save fkt name definition overrules original filename
            _filename = filename

        plt.plot(my_figure, filename=_filename, auto_open=False)
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


if __name__ == "__main__":
    print(__doc__)
