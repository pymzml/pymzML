# -*- coding: utf-8 -*-
# encoding: utf-8
"""
Plotting functions for pymzML
"""

# pymzml
#
# Copyright (C) 2010-2011 T. Bald, J. Barth, A. Niehues, M. Kösters, C. Fufezan
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
import plotly.offline as plt
import plotly.graph_objs as go # or use python dicts???
from plotly import tools
import json
import pprint


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
    def __init__(self, filename = None):
        self.filename       = filename if filename != None else "spectra.xhtml" # why not spectra.xml no default in function # can be removed
        self.normalizations = [ ] # rather or not normalize data : True or False
        self.plots          = [ ] # List of Lists, whereas each inner list can have different Dataobjects (traces)
        self.layoutObjs     = [ ] # more than one Object required?
        self.maxI           = [ ] # maxI for each plot
        self.maxMZ			= [ ] # maxMZ for each plot
        self.linearOffset   = [ ]

    def newPlot(self, header = None , mzRange = None , normalize = False, precision='5e-6'):
        """
        Add new plot to the plotFactory.

        :param header: an optional title that will be printed above the plot
        :type header: string
        :param mzRange: Boundaries of the new plot
        :type mzRange: tuple of minMZ,maxMZ
        :param normalize: whether or not the individal data sets are normalized in the plot
        :type boolean:
        :param precision: measuring precision used in handler. Default 5e-6.
        :type precision: float
        """
        if mzRange == None:
            mzRange = [-float('inf'), float('Inf')]

        self.plots.append( [] )
        # necessary?
        self.layoutObjs.append({'xaxis'       : { 
                                                    'title'     : 'm/z',
                                                    'titlefont' : { 'color' : '#000000',
                                                                    'family': 'Helvetica',
                                                                    'size'  : '18'
                                                                  }
                                                },
                                'yaxis'       : {
                                                    'title'     : 'Intensity',
                                                    'titlefont' : { 'color' : '#000000',
                                                                    'family': 'Helvetica',
                                                                    'size'  : '18'
                                                                  }
                                                },
                                'title'       : header,
                                'legend'      : { 'font' : { 'size' :10,
                                                            'color' : '#FF0000'
                                                            }
                                                }

                            } )
        return
    
    def add(self,data, color=(0,0,0), style='sticks', mzRange = None, opacity = 0.8, name=None, plotNum = -1):
        """
        Add data to the graph.

        :param data: The data added to the graph
        :type data: list of tuples (mz,i) or (mz1, mz2, i, string)
        :param color: color encoded in RGB. Default = (0,0,0)
        :type color: tuple (R,G,B)
        :param style: plotting style. Default = "sticks".
        :type style: string
        :param mzRange: Boundaries that should be added to the current plot
        :type mzRange: tuple of minMZ,maxMZ
        :param opacity: opacity of the data points
        :type opacity: float
        :param name: name of data in legend
        :type name: string
        :param plotType: Plot type, must be either 'Scatter' or 'Bar'. Default = 'Bar'
        :type plotType: string
        :param plotNum: Add data to plot[plotNum]
        :type plotNum: integer

        Currently supported styles are:
            *   'sticks'
            *   'triangle'
            *   'spline'
            *   'linear'
        """

        if mzRange == None:
            mzRange = [-float('Inf'), float('Inf')]

        #  check if data is (mz, i) or (mz1, mz2, i, string)

        # if  len(data[0]) == 2: # normal data array with (mz, i)
        #     if len(self.plots) == 0:
        #         self.newPlot()
        #     xVals     = [mz for mz,i in data if mzRange[0] <= mz <= mzRange[1]]
        #     yVals     = [i  for mz,i in data if mzRange[0] <= mz <= mzRange[1]]
        #     if plotType == 'Bar':
        #         myData = go.Bar({
        #                 'x'           : xVals,
        #                 'y'           : yVals,
        #                 'text'        : name,
        #                 'hoverinfo'   : 'x+y',
        #                 'name'        : name,
        #                 'opacity'     : opacity,
        #                 'marker'      : {
        #                                 'color' : 'rgb'+str(color)
        #                                 }
        #                 })
        #     elif plotType == 'Scatter':
        #         myData = go.Scatter({
        #                 'x'           : xVals,
        #                 'y'           : yVals,
        #                 'text'        : 'annotation',
        #                 'hoverinfo'   : 'x+y',
        #                 'name'        : name,
        #                 'opacity'     : opacity,
        #                 'mode'        : 'markers',
        #                 'marker'      : {
        #                                 'color' : 'rgb'+str(color),
        #                                 'symbol': 'circle'
        #                                 }
        #                 })
        #     else:
        #         raise Exception("Unsupported plot type.\n Please use 'Scatter' or 'Bar'.")
        if len(self.plots) == 0:
        	self.newPlot()

        if len(data[0]) == 2:
        	xVals     = [mz for mz,i in data if mzRange[0] <= mz <= mzRange[1]]
        	yVals     = [i  for mz,i in data if mzRange[0] <= mz <= mzRange[1]]
	        yMax = max(yVals)
	        xMax = max(xVals) # what if not data and just anno?
	        print(xVals, yVals)

        self.maxI.append(yMax) 
        self.maxMZ.append(xMax)

        filling = None
        yMax = self.maxI[-1] # use yMax from most recent created plot
        xMax = self.maxMZ[-1] # use xMax from most recent created plot
        
        if style == 'sticks':  # stick width dependent on ms_precision!! works on 4 tuple array as data and anno
            shape = 'linear'
            ms_precision = float('1e-5') # get from user? get from new Plot function?
            try:
                pos   = style.split('.')[1]
            except:
                pos = 'medium'
            filling = 'tozeroy'
            xValues = []
            yValues = []
            txt     = []
            for x in data:
                yPos   = yMax
                xValues += x[0]-(ms_precision), x[0], x[0]+(ms_precision), None
                yValues += 0, yMax, 0, None
                try:
                	txt += None, x[3], None, None
                except:
                	pass

        elif style.split('.')[0] == 'triangle': # works on 4 tuple array as 
            shape = 'linear'
            try:
                pos   = style.split('.')[1]
            except:
                pos = 'medium'
            filling = 'tozeroy'
            xValues = []
            yValues = []
            txt     = []
            for x in data:
                if pos == 'small':
                    yPos   = yMax
                    relWidth = 1/float(200)

                elif pos == 'medium':
                    yPos   = 0
                    relWidth = 1/float(100)

                elif pos == 'big':
                    yPos = (x[2]/2)
                    relWidth = 1/float(50)

                print (data)
                if len(data[0]) == 4:
                	yPos = x[3]
                else:
                	yPos = x[1]
                xValues += x[0]-(xMax*relWidth), x[0], x[0]+(xMax*relWidth), None
                yValues += 0, yMax, 0, None
                try:
                	txt += None, x[3], None, None
                except:
                	pass

        elif style.split('.')[0] == 'spline': # works on 4 tuple only for anno (requires 2 x coordinates)
            shape = style.split('.')[0]
            try:
                pos   = style.split('.')[1]
            except:
                pos = 'top'

            xValues = []
            yValues = []
            txt     = []
            for x in data:
                if pos == 'top':
                    yPos   = yMax
                    offset = yMax*0.05

                elif pos == 'bottom':
                    yPos   = 0
                    offset = -(yMax*0.05)

                elif pos == 'mid':
                    yPos = (x[2]/2)
                    offset = yMax*0.05
                
                xValues += x[0], (x[0]+x[1])/2, x[1], None
                yValues += yPos, yPos+offset, yPos, None
                txt += None, x[3], None, None

        elif style.split('.')[0] == 'linear': # increase offset if new anno is in x range of another anno # works on 4 tuple only for anno (requires 2 x coordinates)
            shape = style.split('.')[0]
            try:
                pos   = style.split('.')[1]
            except:
                pos = 'top'

            xValues = []
            yValues = []
            txt     = []
            txtOffset = 100
            for x in data:
                if pos == 'top':
                    yPos   = yMax
                    offset = yMax*0.1

                elif pos == 'bottom':
                    yPos   = 0
                    offset = -(yMax*0.1)
                    print ('offset: ', yMax, -(yMax*0.1))

                elif pos == 'mid':
                    yPos = (x[2]+x[1])/2
                    offset = 0 
                    
                xValues += x[0], (x[0]+x[1])/2, x[1], None  
                yValues += yPos+offset, yPos+offset, yPos+offset, None  
                txt += None, x[3], None, None

        else:
            raise Exception('Unknown style./n Please use spline.top, spline.bottom, spline.mid, sticks, triangle or linear!')

        annotation_trace = go.Scatter({
                                        'x'       : xValues,
                                        'y'       : yValues,
                                        'text'    : txt,
                                        'textfont'  : {
                                                      'family' : 'Helvetica',
                                                      'size' : 10,
                                                      'color' : '#000000'
                                                    },
                                        'visible' : 'True',
                                        'marker'  : {'size' : 10},
                                        'mode'    : 'text+lines',
                                        'name'    : name,
                                        'line'    : {
                                                     'color' : 'rgb'+str(color),
                                                     'width' : 1,
                                                     'shape' : shape
                                                    },
                                        'fill'    : filling
                                        })

    	self.plots[plotNum].append(annotation_trace)
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
                print("                  Dataset {0} holds {1} datapoints".format(j,len(dataset['x'])))

        print()
        return

    def save(self, filename = "spectra.xhtml", mzRange = None):
        """
        Saves all plots and their data points that have been added to the plotFactory.

        :param filename: Name for the output file. Default = "spectra.xhtml"
        :type filename: string
        :param mzRange: m/z range which should be considered [start, end]. Default = None
        :type mzRange: list
        """
        # Save as Plotly html in given range, also enable to create pure SVGs???
        if mzRange == None: # accept all values
            mzRange = [-float('inf'), float('Inf')]

        plotNumber = len(self.plots)
        rows, cols = int(math.ceil(plotNumber/float(2))), 2
        print (rows, cols)
        if plotNumber%2 == 0:
            myFigure = tools.make_subplots(rows=rows, cols=cols, vertical_spacing=0.6/rows)
        else:
            specs = [[{}, {}] for x in range(rows-1)]
            specs.append([{'colspan': 2}, None])
            myFigure = tools.make_subplots(rows=rows, cols=cols, vertical_spacing=0.6/rows, specs=specs)
            
        for i, plot in enumerate(self.plots):
            for j, trace in enumerate(plot):
                myFigure.append_trace(trace, int(math.ceil((i/2)+1)), (i%2)+1)# insert correct arguments, modulo to always have max 2 cols

        
        for i in range(plotNumber):
            print('xaxis'+str(i+1))
            myFigure['layout']['xaxis'+str(i+1)].update(title='m/z ')
            myFigure['layout']['yaxis'+str(i+1)].update(title='Intensity')
            myFigure['layout']['xaxis'+str(i+1)].update(titlefont = { 'color' : '#000000',
                                                                'family': 'Helvetica',
                                                                'size'  : '18'
                                                              })
            myFigure['layout']['yaxis'+str(i+1)].update(titlefont = { 'color' : '#000000',
                                                                'family': 'Helvetica',
                                                                'size'  : '18'
                                                              })
        myFigure['layout']['legend'].update(font={ 'size' :10,
                                                        'color' : '#FF0000'
                                                        })
        plt.plot(myFigure, filename='test1')
        return

    def get_json(self):
        """
        return data and layout in JSON format
        """
        return json.dumps([self.plots, self.layoutObjs[-1]])

if __name__ == '__main__':
    print(__doc__)
    
    
    
    
    
    
    
    
    
    
    
    
