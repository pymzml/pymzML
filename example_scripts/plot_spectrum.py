#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pymzml


def main():
    """
    This function shows how to plot a simple spectrum. It can be directly
    plotted via this script or using the python console.

    usage:

        ./plot_spectrum.py

    """

    example_file = os.path.join(
        os.path.dirname(__file__), os.pardir, "tests", "data", "example.mzML"
    )
    run = pymzml.run.Reader(example_file)
    p = pymzml.plot.Factory()
    for spec in run:
        p.new_plot()
        p.add(spec.peaks("centroided"), color=(0, 0, 0), style="sticks", name="peaks")
        filename = "example_plot_{0}_{1}.html".format(
            os.path.basename(example_file), spec.ID
        )
        p.save(filename=filename)
        print("Plotted file: {0}".format(filename))
        break


if __name__ == "__main__":
    main()
