#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
Plotting functions for pymzML
"""

# pymzml
#
# Copyright (C) 2010-2011 T. Bald, J. Barth, M. Specht, C. Fufezan
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

from __future__ import print_function
import math
import sys
import collections


class Factory(object):
    """
    Class to plot pymzml.spec.Spectrum as svg/xhtml.

    :param filename: Name for the output file. Default = "spectra.xhtml"
    :type filename: string

    Example:

    >>> import pymzml, get_example_file
    >>> mzMLFile = 'profile-mass-spectrum.mzml'
    >>> example_file = get_example_file.open_example(mzMLFile)
    >>> run = pymzml.run.Run("../mzML_example_files/"+mzMLFile, precisionMSn = 250e-6)
    >>> p = pymzml.plot.Factory()
    >>> for spec in run:
    >>>     p.newPlot()
    >>>     p.add(spec.peaks, color=(200,00,00), style='circles')
    >>>     p.add(spec.centroidedPeaks, color=(00,00,00), style='sticks')
    >>>     p.add(spec.reprofiledPeaks, color=(00,255,00), style='circles')
    >>>     p.save( filename="output/plotAspect.xhtml" , mzRange = [745.2,745.6] )

    """

    def __init__(self,filename = None):
        self.filename = filename if filename != None else "spectra.xhtml"
        self.plots = [  ]     # list of plots, where each plot hold a list of mz-i lists that should be plotted in the same plot
        self.styles = [  ]
        self.colors = [  ]
        self.header = [  ]
        self.labelPos = [  ]
        self.mzRanges = [  ]
        self.normalizations = []
        pass

    def newPlot(self, header = None , mzRange = [None,None] , normalize = False):
        """
        Add new plot to the plotFactory.

        :param header: an optional title that will be printed above the plot
        :type header: string
        :param mzRange: Boundaries of the new plot
        :type mzRange: tuple of minMZ,maxMZ
        :param normalize: whether or not the individal data sets are normalized in the plot
        :type boolean:


        """
        self.plots.append( [] )
        self.styles.append( [] )
        self.colors.append( [] )
        self.labelPos.append( set() )
        self.mzRanges.append( mzRange )
        self.normalizations.append( normalize )
        if header == None:
            self.header.append( '' )
        else:
            self.header.append( header )
        return

    def add(self,data, color=(00,00,00) , style = 'sticks', mzRange = [None,None] ):
        """
        Add data to the graph.

        :param data: The data added to the graph
        :type data: list of tuples (mz,i)
        :param color: color encoded in RGB. Default = (0,0,0)
        :type color: tuple (R,G,B)
        :param style: plotting style. Default = "circles".
        :type style: string
        :param mzRange: Boundaries that should be added to the current plot
        :type mzRange: tuple of minMZ,maxMZ

        Currently supported styles are:
            *   'emptycircles'
            *   'circles'
            *   'sticks'
            *   'squares'
            *   'area'
            *   'triangle'
            *   'label'

        NOTE: The data format for label style is [( mz1, 'label1' ), ( mz2, 'label2' ), ( mz3, 'label3' ) ].
        """
        if len(self.plots) == 0:
            self.newPlot()
        self.styles[-1].append(style)
        self.colors[-1].append(color)
        selective = True
        if mzRange == [None,None]:
            if self.mzRanges[-1] == [None,None]:
                selective = False
                self.plots[-1].append(data)
            else:
                mzRange = self.mzRanges[-1]
        else:
            self.mzRanges[-1] = mzRange
            # NOTE this allows us to define the mzRange in the call of the add function, otherwise it has to be in the call of the new function
            # NOTE Problem can be: mzRanges[-1] can be overwritten ... don't know what is best here
        if selective:
            self.plots[-1].append([(mz,i) for mz,i in data if mzRange[0] <= mz <=mzRange[1]])
        #print("Added {0} data points".format(len(self.plots[-1][-1])))
        return

    def info(self):
        """
        Returns summary about the plotting factory, i.e.how many plots and how many datasets per plot.
        """
        print("""
        Factory holds {0} unique plots""".format(len(self.plots)))
        for i,plot in enumerate(self.plots):
            print("                Plot {0} holds {1} unique datasets".format(i,len(plot)))
            for j,dataset in enumerate(plot):
                print("                  Dataset {0} holds {1} datapoints".format(j,len(dataset)))

        print()
        return

    def save(self, filename = None, mzRange = [None,None]):
        """
        Saves all plots and their data points that have been added to the plotFactory.

        :param filename: Name for the output file. Default = "spectra.xhtml"
        :type filename: string
        :param mzRange: m/z range which should be considered [start, end]. Default = [ ``None`` , ``None`` ]
        :type mzRange: list
        """
        if filename == None:
            filename = self.filename

        io = open("{0}".format(filename), 'w' )
        # NOTE: we need to check if file exists and/or if file can be written ...

        print("""<html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <title>pymzml spectrum visualisation</title>
        <style>
        </style>
        </head>
        <body style="position:relative; z-index:0; width:100%; height:100%;">

        """, file = io)
        for plotNumber,plot in enumerate(self.plots):
            w = 1000
            h = 700
            heada = self.header[plotNumber]
            resolved_mzRange = [ None, None ]

            if mzRange != [ None, None ]:
                resolved_mzRange = mzRange

            else:
                if self.mzRanges[plotNumber] == [None,None]:
                    # we have to determine ranges ...
                    for dataset in plot:
                        print("Determing mzRanges ...")
                        if len(dataset) == 0:
                            continue

                        if resolved_mzRange[0] == None:
                            resolved_mzRange[0] = min(dataset)[0]
                        else:
                            if resolved_mzRange[0] > min(dataset)[0]:
                                resolved_mzRange[0] = min(dataset)[0]

                        if resolved_mzRange[1] == None:
                            resolved_mzRange[1] = max(dataset)[0]
                        else:
                            if resolved_mzRange[1] < max(dataset)[0]:
                                resolved_mzRange[1] = max(dataset)[0]
                else:
                    # Ranges have been defined by newPlot()
                    # i.e we want to plot no matter what ...
                    resolved_mzRange = self.mzRanges[plotNumber]

            if resolved_mzRange == [None,None]:
                print("Skipping empty plot, plotNumber {0} , header :{1} ...".format(plotNumber,heada))
                continue

            i_max = 0
            i_min = 0
            for dataset in plot:
                for mz,i in dataset:
                    if resolved_mzRange[0] <= mz <= resolved_mzRange[1]:
                        try:
                            i = float(i)
                        except:
                            continue
                        if i >= i_max:
                            i_max = i
            if i_max == 0:
                i_max = 0.1
            if self.normalizations[plotNumber] == True:
                resolved_i_max = 1.05
            else:
                resolved_i_max = i_max * 1.05
            print("""
            <svg xmlns="http://www.w3.org/2000/svg" version="1.1"
            width="{w}" height="{h}"
            style="position:relative; top:0; left:0; z-index:-1;">
            """.format(w = w, h = h), file = io)
            PADDING = (300,50,100,50) # css style convention
            baseline = h-PADDING[2]

            # Drawing Frame ...
            for x1,y1,x2,y2 in [    (PADDING[3],PADDING[0],w-PADDING[1],PADDING[0]),
                                    (w-PADDING[1],PADDING[0],w-PADDING[1],h-PADDING[2]),
                                    (PADDING[3],h-PADDING[2],w-PADDING[1],h-PADDING[2]),
                                    (PADDING[3],PADDING[0],PADDING[3],h-PADDING[2]),
            ]:
                print("""<line x1="{0}" y1="{1}" x2="{2}" y2="{3}"
                style="stroke:rgb(00,00,00);stroke-width:1"/>""".format(x1,y1,x2,y2),file=io)

            if heada != '':
                heada_y = 30
                for subheada in heada.split("\n"):
                    print("""<text x="{x}" y="{y}" font-family="Courier" text-anchor="start" font-size="{fontsize}" fill="black" >{0}</text>
                        """.format(subheada, x = 0, y = heada_y, fontsize = 24), file = io)
                    heada_y += 30
            pixelpermz = float( w - PADDING[1] - PADDING[3] ) / float(resolved_mzRange[1]-resolved_mzRange[0]) # NOTE this returns ZeroDivisionError if the range to plot contains only one peak
            pixelper_i = float( h - PADDING[0] - PADDING[2] ) / float(resolved_i_max-i_min)
            delta = resolved_mzRange[1]-resolved_mzRange[0]
            sep = round(math.log(delta,10))
            factor = 10**(-1*(sep-1))

            # grid
            # Drawing ticks and x labels
            for _ in range(int(round(resolved_mzRange[0]*factor)),int(round(resolved_mzRange[1]*factor))+1 ):
                x = int(round(PADDING[3]  +   (float(_)/float(factor) - resolved_mzRange[0] ) * pixelpermz   ))
                y = baseline
                color = 77 #if _ % 10 == 0 else 125
                print("""<line x1="{0}" y1="{1}" x2="{0}" y2="{2}"
                style="stroke-dasharray: 9, 5;stroke:rgb({3},{3},{3});stroke-width:0.5"/>""".format(x,PADDING[0],baseline,color),file=io)
                print("""<line x1="{0}" y1="{1}" x2="{0}" y2="{2}"
                style="stroke:rgb(00,00,00);stroke-width:0.5;"/>""".format(x,baseline,baseline+10),file=io)
                print("""<text x="{x}" y="{y}" transform="rotate(90 {x},{y})" font-family="Courier" text-anchor="start" font-size="{fontsize}" fill="black" >{0:7.3f}</text>
                    """.format(float(_)/float(factor), x = x, y = y + 30, fontsize = 12), file = io)

            # Drawing data points .. labels first
            for datasetnumber,dataset in enumerate(plot):
                r,g,b = self.colors[plotNumber][datasetnumber]
                style = self.styles[plotNumber][datasetnumber]
                if style[:5] == 'label':
                    for pos,(mz,i) in enumerate(dataset):
                        if resolved_mzRange[0] <= mz <= resolved_mzRange[1]:
                            x = int(round(PADDING[3]  +   (mz - resolved_mzRange[0] ) * pixelpermz   ))
                            y = baseline
                            y2 = baseline - (resolved_i_max * pixelper_i)

                            x3 = round(x,-1)
                            if style.upper().endswith('X1'):
                                y3 = round(y+10)
                                sign = 1
                                stroke_width = 0.50
                            else:
                                y3 = round(y2)
                                sign = -1
                                stroke_width = 0.40
                            layers = 15
                            while (x3,y3) in self.labelPos[plotNumber]:
                                y3 = y3 + sign * 15
                                layers -= 1
                                if layers <= 0:
                                    break

                            print("""<line x1="{0}" y1="{1}" x2="{0}" y2="{2}"
                            style="stroke-opacity: 0.6;stroke:rgb({r},{g},{b});stroke-width:{o};" />""".format(x, y, y2, o=stroke_width, r=r,g=g,b=b),file=io)

                            self.labelPos[plotNumber].add((x3,y3))
                            self.labelPos[plotNumber].add((x3+10,y3 + sign * 15))

                            print("""<text x="{x}" y="{y}" transform="rotate({angle} {x},{y})" font-family="Courier" text-anchor="start" font-size="{fontsize}" style="fill:rgb({r},{g},{b});" >{0}</text>
                                """.format(i, x = x, y = y3, fontsize = 10, angle = sign * 45 , r = r, g = g, b = b), file = io)

                elif style[:5] == 'area':
                    if self.normalizations[plotNumber] == True:
                        maxI = max([ i for mz,i in dataset ])
                    else:
                        maxI = None

                    first = True
                    for pos,(mz,i) in enumerate(sorted(dataset)):
                        if resolved_mzRange[0] <= mz <= resolved_mzRange[1]:
                            x = int(round(PADDING[3]  +   (mz - resolved_mzRange[0] ) * pixelpermz   ))
                            if self.normalizations[plotNumber] == True:
                                y = baseline - ((float(i)/float(maxI)) * pixelper_i)
                            else:
                                y = baseline - (i * pixelper_i)

                            if first:
                                print('<path d="M{0} {2} L{0} {1}'.format(x,y,baseline), end=" ", file = io)
                                first = False
                            else:
                                print('L{0} {1}'.format(x,y ), end=" ", file = io)
                    if first == False:
                        # aka we have seen some points ;)
                        print(' L{0} {1} Z" style="fill:rgb({r},{g},{b}); fill-opacity:0.2; stroke:rgb({r},{g},{b}); stroke-width:1" />'.format(x,baseline,r=r,g=g,b=b), file = io)

                elif style[:8] == 'triangle':
                    if self.normalizations[plotNumber] == True:
                        maxI = max([ i for mz,i in dataset ])
                    else:
                        maxI = None

                    #first = True
                    for pos,(mz,i) in enumerate(sorted(dataset)):
                        if resolved_mzRange[0] <= mz <= resolved_mzRange[1]:
                            x = int(round(PADDING[3]  +   (mz - resolved_mzRange[0] ) * pixelpermz   ))
                            xl = int(round(PADDING[3]  +   (mz-0.15 - resolved_mzRange[0] ) * pixelpermz   ))
                            xr = int(round(PADDING[3]  +   (mz+0.15 - resolved_mzRange[0] ) * pixelpermz   ))
                            if self.normalizations[plotNumber] == True:
                                y = baseline - ((float(i)/float(maxI)) * pixelper_i)
                            else:
                                y = baseline - (i * pixelper_i)

                            print('<path d="M{0} {4} L{2} {3} L{1} {4} Z" style="fill:rgb({r},{g},{b}); fill-opacity:0.4"/>'.format(xl,xr,x,y,baseline,r=r,g=g,b=b), file = io)
                            #print('<line x1="{0}" y1="{1}" x2="{0}" y2="{2}" style="stroke:rgb({r},{g},{b});stroke-width:1"/>'.format(x,y,baseline,r=r,g=g,b=b), file = io)

            # Drawing data ...
            for datasetnumber,dataset in enumerate(plot):
                r,g,b = self.colors[plotNumber][datasetnumber]
                style = self.styles[plotNumber][datasetnumber]
                if style[:5] not in ['label', 'area', 'trian']:
                    if len(dataset) == 0:
                        continue
                    if self.normalizations[plotNumber] == True:
                        maxI = max([ i for mz,i in dataset ])
                    else:
                        maxI = None

                    for pos,(mz,i) in enumerate(dataset):
                        if resolved_mzRange[0] <= mz <= resolved_mzRange[1]:
                            x = int(round(PADDING[3]  +   (mz - resolved_mzRange[0] ) * pixelpermz   ))
                            if self.normalizations[plotNumber] == True:
                                y = baseline - ((float(i)/float(maxI)) * pixelper_i)
                            else:
                                y = baseline - (i * pixelper_i)

                            if style == 'circles':
                                print("""<circle cx="{x}" cy="{y}" r="2" style="fill:rgb({r},{g},{b});" />""".format( x = x, y = y , r = r, g = g, b = b),file=io)

                            elif style == 'emptycircles':
                                print("""<circle cx="{x}" cy="{y}" r="4" style="stroke:rgb({r},{g},{b}); stroke-width:2; fill:none" />""".format( x = x, y = y , r = r, g = g, b = b),file=io)

                            elif style == 'sticks':
                                print("""<line x1="{0}" y1="{1}" x2="{0}" y2="{2}"
                                style="stroke:rgb({r},{g},{b});stroke-width:0.5"/>""".format(x,y,baseline,r=r,g=g,b=b),file=io)

                            elif style == 'squares':
                                # this is experimental, the squares are not centred
                                print("""<rect x="{0}" y="{1}" width="4" height="4" style="fill:rgb({r},{g},{b});
                                fill-opacity:0.8;" />
                                """.format(x-2,y-2,r=r,g=g,b=b),file=io)

                            else:
                                print("Style {0} not support yet ...".format(style),file=sys.stderr)
                                exit(1)

            print("</svg>", file = io)
        print("""
        </body>
        </html>
        """, file = io)
        return

if __name__ == '__main__':
    print(__doc__)
