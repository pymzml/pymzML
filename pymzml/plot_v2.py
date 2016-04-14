# -*- coding: utf-8 -*-
# encoding: utf-8
"""
Plotting functions for pymzML
"""

# pymzml
#
# Copyright (C) 2010-2011 T. Bald, J. Barth, M. Kösters, A. Niehues, C. Fufezan
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
		self.maxVals        = [ ] # maxI for each plot
		self.lookup         = dict()
		self.linearAnnoPoints   = set()
		self.yMax = []
		self.xMax  = []
		self.offset = 1
		# self.functionMapper =  {
		# 						'+__splineOffset__1'				: self.__returnPosOffset,
		# 						'+__splineOffset__0'				: self.__returnPosOffset0,
		# 						'-__splineOffset__1'				: self.__returnNegOffset,
		# 						'-__splineOffset__0'				: self.__returnNegOffset0
		# 						}

	# def __returnMaxY(self, i):
	# 	return self.yMax[i]
	
	# def __returnPosOffset(self, i):
	# 	return self.yMax[i]+(self.yMax[i]*(self.offset*0.05))
	
	# def __returnNegOffset(self, i):
	# 	return self.yMax[i]-(self.yMax[i]*(self.offset*0.05))
	
	# def __returnBaseOffset(self, i):
	# 	return .0-(self.yMax[i]*(self.offset*0.05))

	# def __returnNegOffset0(self, i):
	# 	return .0-(self.yMax[i]*(self.offset*0.05))

	# def __returnPosOffset0(self, i):
	# 	pass
		
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

		self.plots.append( [] ) # create new plot
		self.lookup[header] = len(self.plots)-1 # TODO map header to index number
		self.precision = precision
		self.yMax.append(1) # initialize with 1
		self.xMax.append(1) # initialize with 1
		return
	
	def add(self,data, color=(0,0,0), style='sticks', mzRange = None, opacity=0.8, name=None, plotNum = -1):
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
			*   'triangle' (big, medium or small)
			*   'spline'   (top, medium or bottom)
			*   'linear'   (top, medium or bottom)
		"""
		if mzRange == None:
			mzRange = [-float('Inf'), float('Inf')]

		if len(self.plots) == 0:
			self.newPlot()

		filling = None

		style = style.split('.')
		ms_precision = self.precision # get from user? get from new Plot function?
		if style[0] == 'label':
			if style[1] == 'sticks':
				shape = 'linear'
				filling = 'tozeroy'
				xValues = list()
				yValues = list()
				txt     = list()
				for x in data:
					yPos = 'self.yMax[i]' #NOTE self.yMax[plotNum] = __Y__
					xValues += x[0]-(ms_precision), x[0], x[0]+(ms_precision), None # FIXME
					yValues += .0, yPos, .0, None
					txt     += None, x[3], None, None

			elif style[1] == 'triangle':
				shape = 'linear'
				filling = 'tozeroy'
				xValues = []
				yValues = []
				txt     = []
				if len(style) == 3:
					pos = style[1]

				else:
					pos = 'medium'
					relWidth = 1/float(100)

				for x in data:
					if pos == 'small':
						yPos   = yMax
						relWidth = 1/float(200)

					elif pos == 'medium':
						yPos   = .0
						relWidth = 1/float(100)

					elif pos == 'big':
						yPos = (x[2]/2)
						relWidth = 1/float(50)

					yMax = 'self.yMax[i]' #NOTE self.yMax[plotNum] = __Y__
					xMax = self.xMax[plotNum]
					xValues += x[0]-(xMax*relWidth), x[0], x[0]+(xMax*relWidth), None
					yValues += .0, yMax, .0, None
					txt += None, x[3], None, None
				pass

			elif style[1] == 'spline':
				shape = 'spline'
				xValues = []
				yValues = []
				txt     = []
				if len(style) == 3:
					pos = style[2]
				else:
					pos = 'top'
				xValues = []
				yValues = []
				txt     = []
				for x in data:
					yMax = 'self.yMax[i]' #NOTE self.yMax[plotNum] = __Y__
					if pos == 'top':
						yPos   = yMax
						offset = '+__splineOffset1__'

					elif pos == 'medium':
						print ('Not working atm')
						sys.exit(0)
						yPos = x[2]/2
						offset = '__splineOffset__'

					elif pos == 'bottom':
						yPos = .0
						offset = '-__splineOffset__0'

					xValues += x[0], (x[0]+x[1])/2, x[1], None
					yValues += yPos, str(offset), yPos, None
					txt += None, x[3], None, None

			elif style[1] == 'linear':
				shape = 'linear'
				if len(style) == 3:
					pos = style[2]
				else:
					pos = 'bottom'
				xValues = []
				yValues = []
				txt     = []
				txtOffset = 100
				for x in data:
					yMax = 'self.yMax[i]'#NOTE self.yMax[plotNum] = __Y__
					if pos == 'top':
						yPos   = yMax
						offset = '+__splineOffset1__'
					elif pos == 'medium':
						print ('Not working atm')
						sys.exit(0)
						yPos = x[2]/2
						offset = '+__splineOffset__'
					elif pos == 'bottom':
						yPos = .0
						offset = '-__splineOffset__0'

					if (int(round(x[0], 0)), int(yPos) ) in self.linearAnnoPoints:
						print ("increase offset")
						# self.offset += 1

					for point in range(int(round(x[0], 0)), int(round(x[1], 0)), 1):
						self.linearAnnoPoints.add((point,int(yPos)))

					xValues += x[0], (x[0]+x[1])/2, x[1], None
					yValues += str(offset), str(offset), str(offset), None
					txt     += None, x[3], None, None
			
			else:
				raise Exception("Unknown label type or position")
		
		else:
			xVals     = [mz for mz,i in data if mzRange[0] <= mz <= mzRange[1]]
			yVals     = [i  for mz,i in data if mzRange[0] <= mz <= mzRange[1]]
			yMax = max(yVals)
			xMax = max(xVals)
			print (yMax)

			if self.xMax[plotNum] < xMax:
				self.xMax[plotNum] = xMax
			if self.yMax[plotNum] < yMax: #NOTE self.yMax[plotNum] = __Y__
				self.yMax[plotNum] = yMax #NOTE self.yMax[plotNum] = __Y__


			if style[0] == 'sticks':
				shape = 'linear'
				filling = 'tozeroy'
				xValues = []
				yValues = []
				txt     = []
				for x in data:
					yPos   = x[1]
					xValues += x[0]-(ms_precision), x[0], x[0]+(ms_precision), None
					yValues += .0, yPos, .0, None

			elif style[0] == 'triangle':
				if len(style) == 2:
					pos = style[1]
				else:
					pos = 'medium'
				shape = 'linear'
				filling = 'tozeroy'
				xValues = []
				yValues = []
				txt     = []
				for x in data:
					if pos == 'small':
						relWidth = 1/float(200)

					elif pos == 'medium':
						relWidth = 1/float(100)

					elif pos == 'big':
						relWidth = 1/float(50)
					yPos = x[1]
					xValues += x[0]-(xMax*relWidth), x[0], x[0]+(xMax*relWidth), None
					yValues += .0, yPos, .0, None

		#In case one needs different Layouts, here is how a simple layout may look like			
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
										'fill'    : filling,
										'fillcolor' : 	{
														'color' : 'rgba'+str((color[0], color[1], color[2], opacity))
														},
																				'opacity' : opacity
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

		if plotNumber%2 == 0:
			myFigure = tools.make_subplots(rows=rows, cols=cols, vertical_spacing=0.6/rows)
		else:
			specs = [[{}, {}] for x in range(rows-1)]
			specs.append([{'colspan': 2}, None])
			myFigure = tools.make_subplots(rows=rows, cols=cols, vertical_spacing=0.6/rows, specs=specs)
		
		for i, plot in enumerate(self.plots):
			for j, trace in enumerate(plot):
				trace['y'] = [self.functionMapper[x](i) if x in self.functionMapper else x for x in trace['y']]
				# insert correct arguments, modulo to always have max 2 cols
				myFigure.append_trace(trace, int(math.ceil((i/2)+1)), (i%2)+1)

		for i in range(plotNumber):
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
		for i, plot in enumerate(self.plots):
			for j, trace in enumerate(plot):
				self.plots[i][j]['y'] = [self.functionMapper[x](i) if x in self.functionMapper else x for x in trace['y']]
		return json.dumps(self.plots, sort_keys=True,
			indent=4, separators=(',', ': '))

if __name__ == '__main__':
	print(__doc__)
	
	
	
	
	
	
	
	
	
	
	
	
