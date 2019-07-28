#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import os

import pymzml


def main():
    """
    This script shows how to plot multiple spectra in one plot and
    how to use label for the annotation of spectra.
    The first plot is an MS1 spectrum with the annotated precursor ion.
    The second plot is a zoom into the precursor isotope pattern.
    The third plot is an annotated fragmentation spectrum (MS2) of the
    peptide HLVDEPQNLIK from BSA.
    These examples also show the use of 'layout' to define the appearance
    of a plot.

    usage:

        ./plot_spectrum_with_annotation.py

    """

    # First we define some general layout attributes
    layout = {
        "xaxis": {
            "title": "<i>m/z</i>",
            "tickmode": "auto",
            "showticklabels": True,
            "ticklen": 5,
            "tickwidth": 1,
            "ticks": "outside",
            "showline": True,
            "showgrid": False,
        },
        "yaxis": {
            "color": "#000000",
            "tickmode": "auto",
            "showticklabels": True,
            "ticklen": 5,
            "tickwidth": 1,
            "ticks": "outside",
            "showline": True,
            "showgrid": False,
        },
    }

    # The example BSA file will be used
    example_file = os.path.join(
        os.path.dirname(__file__), os.pardir, "tests", "data", "BSA1.mzML.gz"
    )

    # Define different precisions for MS1 and MS2
    run = pymzml.run.Reader(example_file, MS_precisions={1: 5e-6, 2: 5e-4})
    p = pymzml.plot.Factory()
    plot_layout = {}

    # Now that everything is set up, we can plot the MS1 spectrum
    # Spectrum ID: 1574
    p.new_plot(title="MS1 Spectrum")
    ms1_spectrum = run[1574]

    # The measured peaks are added as first trace
    p.add(
        ms1_spectrum.peaks("centroided"),
        color=(0, 0, 0),
        opacity=1,
        style="sticks",
        name="raw data plot 1",
    )

    # The label for the precursor ion is added as a seperate trace.
    # Note that triangle.MS_precision is used here as a label.
    # By zooming in at this peak one can therefore check if the measured
    # peak fits into defined the mass accuracy range.
    precursor_mz_calc = 435.9102
    p.add(
        [(precursor_mz_calc, "max_intensity", "theoretical precursor")],
        color=(255, 0, 0),
        opacity=0.6,
        style="label.triangle.MS_precision",
        name="theoretical precursor plot 1",
    )

    # Define the layout for the first subplot.
    # The x- and y-axes of subplots are numbered, starting at 1.
    for axis in layout.keys():
        plot_layout["{0}1".format(axis)] = copy.copy(layout[axis])

    # Now we can add a second plot, the same way as above but as a zoom-in.
    # Therefore, we define a mz_range
    p.new_plot(title="MS1 Spectrum Zoom")
    p.add(
        ms1_spectrum.peaks("centroided"),
        color=(0, 0, 0),
        opacity=1,
        style="sticks",
        name="raw data plot 2",
        plot_num=1,
        mz_range=[435.7, 437],
    )

    p.add(
        [(precursor_mz_calc, "max_intensity", "theoretical precursor")],
        color=(255, 0, 0),
        opacity=0.3,
        plot_num=1,
        style="label.triangle.MS_precision",
        name="theoretical precursor plot 2",
    )

    # The mz_range can be included in the layout as well.
    # In contrast to mz_range in the add() function, which limits the included
    # datapoints, the layout range only defines the area that is depicted (i.e. the zoom)
    for axis in layout.keys():
        plot_layout["{0}2".format(axis)] = copy.copy(layout[axis])
    plot_layout["xaxis2"]["autorange"] = False
    plot_layout["xaxis2"]["range"] = [435.7, 437]

    # Now the third plot will be added, a fragmentation spectrum of HLVDEPQNLIK
    ms2_spectrum = run[3542]

    # The MS_precision for the plotting option label.triangle.MS_precision
    # needs to be defined
    p.new_plot(title="MS2 Spectrum Annotated: HLVDEPQNLIK", MS_precision=5e-4)
    p.add(
        ms2_spectrum.peaks("centroided"),
        color=(0, 0, 0),
        opacity=1,
        style="sticks",
        name="raw data plot 3",
        plot_num=2,
    )

    theoretical_b_ions = {
        "b<sub>2</sub><sup>+2</sup>": 126.0788,
        "b<sub>3</sub><sup>+2</sup>": 175.6130,
        "b<sub>4</sub><sup>+2</sup>": 233.1264,
        "b<sub>2</sub>": 251.1503,
        "b<sub>5</sub><sup>+2</sup>": 297.6477,
        "b<sub>6</sub><sup>+2</sup>": 346.1741,
        "b<sub>3</sub>": 350.2187,
        "b<sub>7</sub><sup>+2</sup>": 410.2034,
        "b<sub>4</sub>": 465.2456,
        "b<sub>8</sub><sup>+2</sup>": 467.2249,
        "b<sub>9</sub><sup>+2</sup>": 523.7669,
        "b<sub>10</sub><sup>+2</sup>": 580.3089,
        "b<sub>5</sub>": 594.2882,
        "b<sub>6</sub>": 691.341,
        "b<sub>7</sub>": 819.3995,
        "b<sub>8</sub>": 933.4425,
        "b<sub>9</sub>": 1046.5265,
        "b<sub>10</sub>": 1159.6106,
    }

    theoretical_y_ions = {
        "y<sub>1</sub><sup>+2</sup>": 74.0600,
        "y<sub>2</sub><sup>+2</sup>": 130.6021,
        "y<sub>1</sub>": 147.1128,
        "y<sub>3</sub><sup>+2</sup>": 187.1441,
        "y<sub>4</sub><sup>+2</sup>": 244.1656,
        "y<sub>2</sub>": 260.1969,
        "y<sub>5</sub><sup>+2</sup>": 308.1949,
        "y<sub>6</sub><sup>+2</sup>": 356.7212,
        "y<sub>3</sub>": 373.2809,
        "y<sub>7</sub><sup>+2</sup>": 421.2425,
        "y<sub>8</sub><sup>+2</sup>": 478.7560,
        "y<sub>4</sub>": 487.3239,
        "y<sub>9</sub><sup>+2</sup>": 528.2902,
        "y<sub>10</sub><sup>+2</sup>": 584.8322,
        "y<sub>5</sub>": 615.3824,
        "y<sub>6</sub>": 712.4352,
        "y<sub>7</sub>": 841.4778,
        "y<sub>8</sub>": 956.5047,
        "y<sub>9</sub>": 1055.5732,
        "y<sub>10</sub>": 1168.6572,
    }

    # Check which theoretical fragments are present in the spectrum
    # using the has_peak() function
    for ion_list in [theoretical_b_ions, theoretical_y_ions]:
        label_list = []
        for fragment in ion_list.keys():
            peak = ms2_spectrum.has_peak(ion_list[fragment])
            if len(peak) != 0:
                label_list.append((ion_list[fragment], peak[0][1], fragment))
        if ion_list == theoretical_b_ions:
            color = (0, 0, 255)
        else:
            color = (0, 255, 0)
        p.add(
            label_list,
            color=color,
            style="label.triangle.MS_precision",
            name="theoretical fragment ions plot 3",
        )

    for axis in layout.keys():
        plot_layout["{0}3".format(axis)] = copy.copy(layout[axis])

    # Save the plot in a file using the defined plot_layout
    filename = "example_plot_{0}_annotation.html".format(os.path.basename(example_file))
    p.save(filename=filename, layout=plot_layout)
    print("Plotted file: {0}".format(filename))


if __name__ == "__main__":
    main()
