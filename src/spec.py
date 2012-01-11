#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
Spectrum class offers a python object for mass spectrometry data.
The spectrum object holds the basic information on the spectrum and offers
methods to interrogate properties of the spectrum.
Data, i.e. mass over charge (m/z) and intensity decoding is performed on demand
and can be accessed via their properties, e.g. :py:attr:`spec.Spectrum.peaks`.

The Spectrum class is used in the :py:class:`run.Run` class.
There each spectrum is accessible as a Spectrum object.

Theoretical spectra can also be created using the setter functions.
For example, m/z values, intensities, and peaks can be set by the
corresponding properties: :py:attr:`spec.Spectrum.mz`,
:py:attr:`spec.Spectrum.i`, :py:attr:`spec.Spectrum.peaks`.
"""
#
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

import sys
import math
import copy
import random
import re

from base64 import b64decode as b64dec
from struct import unpack as unpack
from collections import defaultdict as ddict
from operator import itemgetter as itemgetter
import zlib

PROTON = 1.00727646677
ISOTOPE_AVERAGE_DIFFERENCE = 1.002

class Spectrum(dict):
    def __init__(self, measuredPrecision = None , param=None):
        """
        .. function:: __init__( measuredPrecision = value* )

            Initializes a pymzml.spec.Spectrum class.

            :param measuredPrecision: in m/z, mandatory
            :type measuredPrecision: float


        """
        assert isinstance( measuredPrecision , float ), "Require measured precision as input parameter..."
        self.measuredPrecision = measuredPrecision          # this will also set and update internalPrecision
        self.clear()
        self._mz = []
        self._i = []
        #self._time = self._mz
        self.param = param
        self.ms = {}
        return

    def __add__(self,otherSpec):
        """
        Adds two pymzml spectra together.

        :param otherSpec: Spectrum object
        :type otherSpec: object

        Example:

        >>> import pymzml
        >>> s = pymzml.spec.Spectrum( measuredPrescision = 20e-6 )
        >>> file_to_read = "../mzML_example_files/xy.mzML.gz"
        >>> run = pymzml.run.Reader(file_to_read , MS1_Precision = 5e-6 , MSn_Precision = 20e-6)
        >>> for spec in run:
        ...     s += spec

        """
        assert isinstance(otherSpec,Spectrum) , "can only add two pymzML spectra together ..."
        tmp = self.deRef()
        if tmp._reprofiledPeaks == None:
            tmp._reprofiledPeaks = tmp._reprofile_Peaks()

        for mz,i in otherSpec.reprofiledPeaks:
            tmp._reprofiledPeaks[mz] += i

        # deleting original data since we have now a combination of specs
        tmp_reprofiledPeaks = tmp._reprofiledPeaks

        tmp.clear()

        tmp._reprofiledPeaks = tmp_reprofiledPeaks
        tmp['reprofiled'] = True
        return tmp

    def __sub__(self,otherSpec):
        """
        Subtracts two pymzml spectra.
        
        :param otherSpec: Spectrum object
        :type otherSpec: object
        
        """
        assert isinstance(otherSpec,Spectrum) , "can only subtract two pymzML spectra ..."
        tmp = self.deRef()
        
        if tmp._reprofiledPeaks == None:
            tmp._reprofiledPeaks = tmp._reprofile_Peaks()

        for mz,i in otherSpec.reprofiledPeaks:
            tmp._reprofiledPeaks[mz] -= i

        # deleting original data since we have now a combination of specs
        tmp_reprofiledPeaks = tmp._reprofiledPeaks

        tmp.clear()

        tmp._reprofiledPeaks = tmp_reprofiledPeaks
        tmp['reprofiled'] = True
        return tmp

    def __mul__(self, value):
        """
        Multiplies each intensity with a float, i.e. scales the spectrum.

        :param value: Value to multiply the spectrum
        :type value: float

        """
        assert isinstance(value, (int, float)), "require float or int of intensity values ..."
        tmp = self.deRef()
        if tmp._peaks != None:
            tmp.peaks  = [(mz, i * float(value)) for mz, i in tmp.peaks]
        if tmp._centroidedPeaks != None:
            tmp.centroidedPeaks = [(mz, i * float(value)) for mz, i in tmp.centroidedPeaks]
        if tmp._reprofiledPeaks != None:
            for mz in tmp._reprofiledPeaks.keys():
                tmp._reprofiledPeaks[mz] *= float(value)
        return tmp

    def __truediv__(self,value):
        """
        Divides each intensity by a float, i.e. scales the spectrum.

        :param value: Value to divide the spectrum
        :type value: float, int

        """
        assert isinstance( value , ( int , float ) ), "require float or int of intensity values ..."
        tmp = self.deRef()
        if tmp._peaks != None:
            tmp.peaks  = [ (mz,i/float(value)) for mz,i in tmp.peaks ]
        if tmp._centroidedPeaks != None:
            tmp.centroidedPeaks = [ (mz,i/float(value)) for mz,i in tmp.centroidedPeaks ]
        if tmp._reprofiledPeaks != None:
            for mz in tmp._reprofiledPeaks.keys():
                tmp._reprofiledPeaks[mz] /= float(value)
        return tmp

    def __div__(self,value):
        return self.__truediv__(value)

    def __del__(self):
        self.clear()
        del self
        return

    def clear(self, scope = 'all'):
        """
        Clears the current spectrum object which means that all variables are
        set to default or ``None``
        """
        if scope == 'all':
            for k in list(self.keys()):
                del self[k]

        self._mz = None
        self._i = None
        self._peaks = None
        self._centroidedPeaks = None
        self._reprofiledPeaks = None
        self._deconvolutedPeaks = None
        self._transformedMzWithError = None
        self._transformedPeaks = None
        self._transformed_deconvolutedPeaks  = None
        self._transformedMassWithError = None
        self._extremeValues = None
        self._tmzSet = None
        self._tmassSet = None
        self._centroidedPeaksSortedByI = None
        self._xmlTree = None
        self._iter = None
        self['BinaryArrayOrder'] = []
        self.ms = {}
        return

    def strip(self, scope = 'all'):
        """
        Reduces the size of the spectrum. Interesting if specs need to be added
        or stored.

        :param scope: accepts currently ["all"]
        :type scope: string

        "all" will remove the raw and profiled data and some internal lookup
        tables as well.
        """
        if scope == 'all':
            if self._peaks == None:
                # decode, just in case ...
                self.peaks
            self._tmzSet = None
            self._tmassSet = None
            self._transformedMzWithError = None
            self._transformedPeaks = None
            self._transformed_deconvolutedPeaks  = None
            self._transformedMassWithError = None
            if 'encodedData' in self.keys():
                del self['encodedData']
                del self['PY:0000000'] # this is the ID tag corresponding to 'encodedData'
        else:
            print("Dont understand strip request ", file = sys.stderr)


    @property
    def mz(self):
        """
        Returns the list of m/z values. If the m/z values are encoded, the
        function :py:func:`_decode()` is used to decode the encoded data.\n
        The mz property can also be setted, e.g. for theoretical data.
        However, it is recommended to use the peaks property to set mz and
        intesity tuples at same time.

        :rtype: list
        :return: Returns a list of mz from the actual analysed spectrum

        """
        if self._mz == None:
            self._decode()
        return self._mz

    @mz.setter
    def mz(self,mzList):
        assert type(mzList) == type([]), "require list of mz values ..."
        self._mz = mzList
        return

    @property
    def time(self):
        """
        Returns the list of m/z values. If the m/z values are encoded, the
        function :py:func:`_decode()` is used to decode the encoded data.\n
        The mz property can also be setted, e.g. for theoretical data.
        However, it is recommended to use the peaks property to set mz and
        intesity tuples at same time.

        :rtype: list
        :return: Returns a list of mz from the actual analysed spectrum

        """
        if self._mz == None:
            self._decode()
        return self._mz

    def extremeValues(self,key):
        """
        Find extreme values, minimal and maximum mz and intensity

        :param key: m/z : "mz" or  intensity : "i"
        :type key: string
        :rtype: tuple
        :return: tuple of minimal and maximum m/z or intensity

        """
        if key not in ['mz','i']:
            print("Dont understand extreme request ", file = sys.stderr)
        if self._extremeValues == None:
            self._extremeValues = {}
        try:
            if key == 'mz':
                self._extremeValues['mz'] = ( min([mz for mz, i in self.peaks]) , max([mz for mz, i in self.peaks]) )
            else:
                self._extremeValues['i']  = ( min([i for mz, i in self.peaks]) , max([i for mz, i in self.peaks]) )
        except ValueError:
            # emtpy spectrum
            self._extremeValues[key] = ()
        return self._extremeValues[key]

    @property
    def i(self):
        """
        Returns the list of the intensity values.
        If the intensity values are encoded, the function :py:func:`_decode()`
        is used to decode the encoded data.\n
        The i property can also be setted, e.g. for theoretical data.However, it
        is recommended to use the peaks property to set mz and intesity tuples
        at same time.

        :rtype: list
        :return: Returns a list of intensity values from the actual analysed
            spectrum.

        """
        if self._i == None:
            self._decode()
        return self._i

    @i.setter
    def i(self,intensityList):
        assert type(intensityList) == type([]), "require list of intensity values ..."
        self._i = intensityList
        return

    @property
    def peaks(self):
        """
        Returns the list of peaks of the spectrum as tuples (m/z, intensity).

        :rtype: list of tuples
        :return: Returns list of tuples (m/z, intensity)

        Example:

        >>> import pymzml
        >>> run = pymzml.run.Reader(spectra.mzMl.gz, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
        >>> for spectrum in run:
        ...     for mz, i in spectrum.peaks:
        ...         print(mz, i)

        .. note::

           The peaks property can also be setted, e.g. for theoretical data.
           It requires a list of mz/intensity tuples.

        """
        if 'reprofiled' in self.keys():
            self.peaks = self._centroid_peaks()
        elif self._peaks == None:
            if self._mz == None and 'encodedData' not in self.keys():
                self._peaks = []
            else:
                self._peaks = list(zip(self.mz , self.i))
        return self._peaks

    @property
    def profile(self):
        """
        Returns the list of peaks of the chromatogram as tuples (time, intensity).

        :rtype: list of tuples
        :return: Returns list of tuples (time, intensity)

        Example:

        >>> import pymzml
        >>> run = pymzml.run.Reader(spectra.mzMl.gz, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
        >>> for spectrum in run:
        ...     for time, i in spectrum.profile:
        ...         print(time, i)
        """
        if 'reprofiled' in self.keys():
            self.peaks = self._centroid_peaks()
        elif self._peaks == None:
            if self._mz == None and 'encodedData' not in self.keys():
                self._peaks = []
            else:
                self._peaks = list(zip(self.mz , self.i))
        return self._peaks


    @peaks.setter
    def peaks(self,mz_i_tuple_list):
        assert type(mz_i_tuple_list) == type([]), "require list of tuples (mz,intensity) ..."
        if len(mz_i_tuple_list) == 0:
            return
        self._mz, self._i = map(list,zip(*mz_i_tuple_list))
        self._peaks = mz_i_tuple_list
        return self

    @property
    def centroidedPeaks(self):
        """
        Returns the centroided version of a profile spectrum. Performs a Gauss
        fit to determine centroided mz and intensities, if the spectrum is in
        measured profile mode.
        Returns a list of tuples of fitted m/z-intesity values. If the spectrum
        peaks are already centroided, these peaks are returned.

        :rtype: list of tuples
        :return: Returns list of tuples (m/z, intensity)

        Example:

        >>> import pymzml
        >>> run = pymzml.run.Reader(spectra.mzMl.gz, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
        >>> for spectrum in run:
        ...     for mz, i in spectrum.centroidedPeaks:
        ...         print(mz, i)

        """
        if 'reprofiled' in self.keys():
            self.peaks = self._centroid_peaks()
            self._centroidedPeaks = self._peaks

        if self._centroidedPeaks == None: #or self._reprofiledPeaks != None:
            self._centroidedPeaks = self._centroid_peaks()
        return self._centroidedPeaks

    @centroidedPeaks.setter
    def centroidedPeaks(self,mz_i_tuple_list):
        assert type(mz_i_tuple_list) == type([]), "require list of tuples (mz,intensity) ..."
        self._centroidedPeaks = mz_i_tuple_list
        return

    def _centroid_peaks(self):
        """
        Perform a Gauss fit to centroid the peaks for the property
        :py:attr:`centroidedPeaks`
        """
        isProfile = False
        for k in self.keys():
            try:
                if 'profile' in k:
                    isProfile = True
                    break
            except:
                print(self.keys(), file = sys.stderr)
                exit(1)
        if isProfile:
            tmp = []
            if 'reprofiled' in self.keys():
                intensity_array = [ i for mz,i in self.reprofiledPeaks ]
                mz_array = [ mz for mz,i in self.reprofiledPeaks ]
                del self['reprofiled']
            else:
                intensity_array = self.i
                mz_array = self.mz
            for pos , i in enumerate(intensity_array[:-1]):
                if pos <= 1: continue
                if 0 < intensity_array[pos-1] < i > intensity_array[pos+1] > 0:
                    # local maximum ...
                    #if 827 <= mz_array[pos] <= 828:
                    #    print("::",i,"@",mz_array[pos])
                    #    print("Found maximum",i,"@",mz_array[pos],intensity_array[pos-1] ,'<' ,i ,"> ",intensity_array[pos+1] )
                    x1  = mz_array[pos-1]
                    y1  = intensity_array[pos-1]
                    x2  = mz_array[pos]
                    y2  = intensity_array[pos]
                    x3  = mz_array[pos+1]
                    y3  = intensity_array[pos+1]
                    
                    if x2-x1 > (x3-x2)*10 or (x2-x1)*10 < x3-x2:
                        # no gauss fit if distance between mz values is too large
                        continue
                    #print(x1,y1,x2,y2,x3,y3)
                    if y3 == y1:
                        # i.e. a reprofiledSpec
                        x1  = mz_array[pos-5]
                        y1  = intensity_array[pos-5]
                        x3  = mz_array[pos+7]
                        y3  = intensity_array[pos+7]
                    try:
                        doubleLog = math.log(y2/y1) / math.log(y3/y1)
                        mue = (doubleLog*( x1*x1 - x3*x3 ) - x1*x1 + x2*x2 ) / (2 * (x2-x1) - 2*doubleLog*(x3-x1))
                        cSquarred = ( x2*x2 - x1*x1 - 2*x2*mue + 2*x1*mue )/ ( 2* math.log(y1/y2 ))
                        A = y1 * math.exp( (x1-mue)*(x1-mue) / ( 2*cSquarred) )
                        
                        #if A > 1e20:
                            #print(mue, A, doubleLog, cSquarred)
                            #print(x1, "\t", y1)
                            #print(x2, "\t", y2)
                            #print(x3, "\t", y3)
                            #print()
                    except:
                        continue
                    tmp.append((mue,A))
            #for mue, A in tmp:
                #print(mue, "\t", A)
            return tmp
        else:
            return self.peaks

    @property
    def xmlTree(self):
        """
        xmlTree property returns an iterator over the original
        xmlTree structure the spectrum was initilized with.

        Example:

        >>> for element in spectrum.xmlTree:
        ...   print( element, element.tag, element.items() )

        please refer to the xml documentation of Python and cElementTree
        for more details.

        """
        return self._xmlTree.getiterator()

    @property
    def tmzSet(self):
        """
        Creates a set out of transformed m/z values (including all values in the defined imprecision).

        :rtype: set
        """
        if self._tmzSet == None:
            self._tmzSet = set()
            for mz, i in self.centroidedPeaks:
                self._tmzSet |= set(
                                    range(
                                            int(round((mz - (mz * self.measuredPrecision)) * self.internalPrecision)),
                                            int(round((mz + (mz * self.measuredPrecision)) * self.internalPrecision)) + 1)

                )
        return self._tmzSet

    @property
    def tmassSet(self):
        '''
        Creates a set out of transformed mass values (including all values in the defined imprecision).

        :rtype: set
        '''
        if self._tmassSet == None:
            self._tmassSet = set(self._transformed_mass_with_error.keys())
        return self._tmassSet

    def deRef( self ):
        """
        Strip some heavy data and return deepcopy of spectrum.

        Example:

        >>> run = pymzml.run.Reader(file_to_read, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
        >>> for spec in run:
        ...     tmp = spec.deRef()

        """
        self.strip()
        return copy.deepcopy(self)

    def reduce(self, mzRange = (None,None) ):
        """
        Works on peaks and reduces spectrum to a m/z range.

        Example:

        >>> run = pymzml.run.Reader(file_to_read, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
        >>> for spec in run:
        ...     spec.reduce( mzRange = (100,200) )

        """
        #NOTE Total ion current should be adjusted as well, I guess ;)
        assert type(mzRange) == type(()), "require tuple of (min,max) mz range to reduce spectrum"
        if mzRange != (None, None):
            tmp_peaks = [ (mz,i) for mz, i in self.peaks if mzRange[0] <= mz <= mzRange[1] ]
            self.clear(scope = 'not_all')
            self.peaks = tmp_peaks
        return self

    def removeNoise(self, mode = 'median', noiseLevel = None):
        """
        Function to remove noise from peaks, centroided peaks and reprofiled
        peaks.

        :param mode: define mode for removing noise. Default = "median"
            (other modes: "mean", "mad")
        :type mode: string
        :rtype: list of tuples
        :return: Returns a list with tuples of m/z-intensity pairs above the
            noise threshold

        mad < median < mean

        Threshold is calculated over the mad/median/mean of all intensity values.
        (mad = mean absolute deviation)

        Example:

        >>> import pymzml
        >>> run = pymzml.run.Reader(spectra.mzML.gz, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
        >>> for spectrum in run:
        ...     for mz, i in spectrum.removeNoise( mode = 'mean'):
        ...         print(mz, i)

        """
        if noiseLevel == None:
            noiseLevel = self.estimatedNoiseLevel(mode = mode)

        if self._peaks != None:
            self.peaks  = [ (mz,i) for mz,i in self.peaks  if i >= noiseLevel]

        if self._centroidedPeaks != None:
            self.centroidedPeaks = [ (mz,i) for mz,i in self.centroidedPeaks  if i >= noiseLevel]

        self._reprofiledPeaks = None
        return self

    def highestPeaks(self, n):
        """
        Function to retrieve the n-highest centroided peaks of the spectrum.

        :param n: Number of n-highest peaks
        :type n: int
        :rtype: list
        :return: list of centroided peaks (mz, intensity tuples)

        Example:

        >>> run = pymzml.run.Reader("../mzML_example_files/deconvolution.mzML.gz", MS1_Precision = 5e-6, MSn_Precision = 20e-6)
        >>> for spectrum in run:
        ...     if spectrum["ms level"] == 2:
        ...         if spectrum["id"] == 1770:
        ...             for mz,i in spectrum.highestPeaks(5):
        ...                print(mz,i)

        """
        if self._centroidedPeaksSortedByI == None:
            self._centroidedPeaksSortedByI = sorted(self.centroidedPeaks, key = itemgetter(1))
        return self._centroidedPeaksSortedByI[-n:]

    def estimatedNoiseLevel(self, mode = 'median'):
        """
        Calculates noise threshold for function :py:func:`removeNoise`
        """
        if self.centroidedPeaks == []:
            return 0

        if 'noiseLevelEstimate' not in self.keys():
            self['noiseLevelEstimate'] = {}
        if mode not in self['noiseLevelEstimate'].keys():
            if mode == 'median':
                self['noiseLevelEstimate']['median'] = self._median([ i for mz, i in self.centroidedPeaks])
            elif mode == 'mad':
                median = self.estimatedNoiseLevel(mode='median')
                self['noiseLevelEstimate']['mad'] = self._median(sorted([ abs(i - median) for mz,i in self.centroidedPeaks]))
            elif mode == 'mean':
                mean = sum([i for mz, i in self.centroidedPeaks]) / float(len(self.centroidedPeaks))
                self['noiseLevelEstimate']['mean'] = mean
                self['noiseLevelEstimate']['variance'] = sum([(i - mean) * (i - mean) for mz, i in self.centroidedPeaks]) / float(len(self.centroidedPeaks))
            else:
                print("dont understand noise level estimation method call", mode, file = sys.stderr)
        return self['noiseLevelEstimate'][mode]

    def _median(self, data):
        if len(data) == 0:
            return None
        data.sort()
        l = len(data)
        if not l % 2:
            median =   (data[int(math.floor(float(l)/float(2)))] + data[int(math.ceil(float(l)/float(2)))] ) / float(2.0)
        else:
            median =  data[int(l/2)]
        return median

    @property
    def reprofiledPeaks(self):
        """
        Returns the reprofiled version of a centroided spectrum.

        :rtype: list of reprofiled mz,i tuples
        :return: Reprofiled peaks as tuple list

        Example:

        >>> import pymzml
        >>> run = pymzml.run.Reader(spectra.mzMl.gz, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
        >>> for spectrum in run:
        ...     for mz, i in spectrum.reprofiledPeaks:
        ...         print(mz, i)

        """
        #NOTE self._reprofiledPeaks is a defaultdict(int) with k:mz, v:i
        if self._reprofiledPeaks == None:
            if self.mz != []:
                self._reprofiledPeaks = self._reprofile_Peaks()
            else:
                self._reprofiledPeaks = ddict(int)
        return sorted(self._reprofiledPeaks.items())

    def _reprofile_Peaks(self):
        """
        Performs reprofiling for property :py:func:`reprofiledPeaks`
        """
        tmp = ddict(int)
        for mz,i in self.centroidedPeaks:
            # Let's say the measured precision is 1 sigma of the signal width, i.e. 68.4%
            s = mz*self.measuredPrecision
            s2 = s*s
            floor  = mz - 3.0*s   # Gauss curve +- 3 sigma
            ceil = mz + 3.0*s
            ip = self.internalPrecision
            for _ in range( int(round(floor*ip)) , int(round(ceil*ip))+1 ):
                if _ % int(5) == 0 :
                    a = float(_)/float(ip)
                    y = i * math.exp( -1 * ((mz - a) * (mz - a))  / (2 * s2) )
                    tmp[ a ] += y
                    #print("a", a)
        self['reprofiled'] = True
        return tmp

    @property
    def measuredPrecision(self):
        """
        Sets the measured and internal precision

        :param value: measured precision (e.g. 5e-6)
        :type value: float
        """
        return self._measuredPrecision

    @measuredPrecision.setter
    def measuredPrecision(self, value):
        self._measuredPrecision = value
        self.internalPrecision = int(round(50000.0 / (value * 1e6)))
        return

    def _link(self, idTag=None, value = None, name = None):
        try:
            v = float(value)
        except:
            v = value
        if idTag not in self.keys():
            self[idTag] = v
        else:
            oldValue = self[idTag]
            self[idTag] = [oldValue]
            self[idTag].append(v)
        self[name] = self[idTag]
        return

    def _decode(self):
        """
        Decodes the base 64 encoded and packed strings from the data.

        :rtype: tuple
        :return: Returns the unpacked data as a tuple. Returns an empty list if
            there is no raw data or raises an exception if data could not be
            decoded.

        """
        if 'encodedData' in self.keys():
            compressionStated = True
            n_BinaryArrayOrder = len(self['BinaryArrayOrder'])
            if n_BinaryArrayOrder == 4:
                compressionStated = False

            #
            for pos in range(0, n_BinaryArrayOrder, int(n_BinaryArrayOrder/2)):
                if compressionStated:
                    arrayType, compression, encodingType  = [value for key, value in sorted([self['BinaryArrayOrder'][pos] , self['BinaryArrayOrder'][pos + 1], self['BinaryArrayOrder'][pos + 2]])]
                else:
                    arrayType, encodingType  = [value for key, value in sorted([self['BinaryArrayOrder'][pos] , self['BinaryArrayOrder'][pos + 1]])]
                    compression = 'no'

                if encodingType == '32-bit float':
                    floattype = 'f'
                elif encodingType == '64-bit float':
                    floattype = 'd'
                else:
                    floattype = None
                    print("New data encoding detected, please adjust parser", file = sys.stderr)

                unpackedData = []

                if self['encodedData'][int(pos*0.5)] == None:
                    pass
                elif len(self['encodedData'][int(pos*0.5)]) == 0:
                    pass
                elif len(self['encodedData'][int(pos*0.5)]) != 0:
                    decodedData  = b64dec(self['encodedData'][int(pos*0.5)].encode("utf-8"))
                    if compression == 'zlib':
                        decodedData = zlib.decompress(decodedData)
                    elif compression == 'no':
                        pass
                    else:
                        print("New data compression ({0}) detected, please adjust parser".format(compression), file = sys.stderr)
                        exit(1)
                    fmt = "{endian}{arraylength}{floattype}".format( endian = "<" , arraylength = self['defaultArrayLength'] , floattype = floattype )
                    try:
                        unpackedData = unpack( fmt , decodedData)
                    except: # NOTE raises struct.error, but cannot be checked for here
                        print("Couldn't extract data {0} fmt: {1}".format(arrayType, fmt), file = sys.stderr)
                        print(len(self['encodedData'][int(pos * 0.5)]), file = sys.stderr)
                        exit(1)

                if arrayType == 'mz' or arrayType == 'time':
                    self._mz = unpackedData
                elif arrayType == 'i':
                    self._i = unpackedData
                else:
                    print("Arraytype {0} not supported ...".format(arrayType), file = sys.stderr)
                    exit(1)
        return

    def hasPeak(self, mz2find):
        """
        Checks if a Spectrum has a certain peak.
        Needs a certain mz value as input and returns a list of peaks if a peak
        is found in the spectrum, otherwise ``[]`` is returned.
        Every peak is a tuple of m/z and intensity.

        :param mz2find: mz value which should be found
        :type mz2find: float
        :rtype: list
        :return: m/z and intensity as tuple in list

        Example:

        >>> import pymzml, get_example_file
        >>> example_file = get_example_file.open_example('deconvolution.mzML.gz')
        >>> run = pymzml.run.Reader(example_file, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
        >>> for spectrum in run:
        ...     if spectrum["ms level"] == 2:
        ...             peak_to_find = spectrum.hasPeak(1016.5404)
        ...             print(peak_to_find)
        [(1016.5404, 19141.735187697403)]

        """
        value = self.transformMZ(mz2find)
        return self._transformed_mz_with_error[value]

        # NOTE this can return a result if a peak is found within 20.08 ppm (for a 20 ppm spectrum) ...

    def hasDeconvolutedPeak(self, mass2find):
        """
        Checks if a deconvoluted spectrum contains a certain peak.
        Needs a mass value as input and returns a list of peaks if a peak
        is found in the spectrum. If the mass is not found ``[]`` is
        returned.
        Every peak is a tuple of m/z and intensity.

        :param mass2find: mass value which should be found
        :type mass2find: float
        :rtype: list
        :return: mass and intensity as tuple in list if mass is found,
            otherwise ``[]``

        Example:

        >>> import pymzml, get_example_file
        >>> example_file = get_example_file.open_example('deconvolution.mzML.gz')
        >>> run = pymzml.run.Reader(example_file, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
        >>> for spectrum in run:
        ...     if spectrum["ms level"] == 2:
        ...             peak_to_find = spectrum.hasDeconvolutedPeak(1044.5804)
        ...             print(peak_to_find)
        [(1044.5596, 3809.4356300564586)]

        """
        value = self.transformMZ(mass2find)
        return self._transformed_mass_with_error[value]

    @property
    def _transformed_mz_with_error(self):
        """
        Returns transformed m/z value with error

        :rtype: dictionary
        :return: Transformed m/z values in dictionary {m/z_with_error :
            [(m/z,intensity), ...], ...}

        """
        if self._transformedMzWithError == None:
            self._transformedMzWithError = ddict(list)
            for mz, i in self.centroidedPeaks:
                for t_mz_with_error in range(int(round((mz - (mz * self.measuredPrecision)) * self.internalPrecision)),
                                             int(round((mz + (mz * self.measuredPrecision)) * self.internalPrecision)) + 1):
                    self._transformedMzWithError[t_mz_with_error].append((mz, i))
        return self._transformedMzWithError

    @property
    def _transformed_mass_with_error(self):
        """
        Returns transformed mass value with error

        :rtype: dictionary
        :return: Transformed mass values in dictionary {mass_with_error:
            (mass,intensity), ...}

        """
        if self._transformedMassWithError == None:
            self._transformedMassWithError = ddict(list)
            for mass, i in self.deconvolutedPeaks:
                for t_mass_with_error in range(int(round((mass - (mass * self.measuredPrecision)) * self.internalPrecision)),
                                               int(round((mass + (mass * self.measuredPrecision)) * self.internalPrecision)) + 1):
                    self._transformedMassWithError[t_mass_with_error].append((mass, i))
        return self._transformedMassWithError

    @property
    def transformedPeaks(self):
        """
        m/z value is multiplied by the internal precision

        :rtype: list of tuples
        :return: Returns a list of peaks (tuples of mz and intensity). Float m/z
            values are adjusted by the internal precision to integers.

        """
        if self._transformedPeaks == None:
            self._transformedPeaks = [(self.transformMZ(mz), i) for mz, i in self.centroidedPeaks]
        return self._transformedPeaks

    @property
    def transformed_deconvolutedPeaks(self):
        """
        Deconvoluted mz value is multiplied by the internal precision

        :rtype: list of tuples
        :return: Returns a list of peaks (tuples of mz and intensity). Float m/z
            values are adjusted by the internal precision to integers.

        """
        if self._transformed_deconvolutedPeaks == None:
            self._transformed_deconvolutedPeaks = [(self.transformMZ(mass), i) for mass, i in self.deconvolutedPeaks]
        return self._transformed_deconvolutedPeaks

    def _mz2mass(self, mz, charge):
        """
        Calculate the uncharged mass for a given mz value

        :param mz: m/z value
        :type mz: float
        :param charge: charge
        :type charge: int
        :rtype: float
        :return: Returns mass of a given m/z value
        """
        return ((mz - PROTON) * charge)

    def _group(self, peaks):
        """
        Group mz (or mass) values according to the given ppm value. The mean
        value of grouped peaks is stored. When an intensity tuple is given, the
        corresponding intensity are summed up and stored.

        :rtype: list
        :return: list of peaks

        """
        mz_tuple, intensity_tuple = zip(*peaks)

        count_ungrouped = 0
        mz_list_grouped = []
        i = 0
        # iterate over all entries for grouping
        while i < len(mz_tuple):
            target =  self.ppm2abs(mz_tuple[i], self.measuredPrecision, 1, 1)
            j = i + 1
            while j < len(mz_tuple) and mz_tuple[j] <= target:
                j += 1
            j = j- 1
            if i == j:
                # no peaks have to be grouped, just add the current peak to the result and go in with the next peak
                mz_list_grouped.append(tuple([mz_tuple[i], intensity_tuple[i]]))
                i += 1
            else:
                # potential overlapping peaks are found.
                # check wether the mz value of the j index does not overlap with the next j+1 index
                k = j + 1
                group = True
                if k < len(mz_tuple):
                    target_new = self.ppm2abs(mz_tuple[j], self.measuredPrecision, 1, 1)
                    if target_new >= mz_tuple[k]:
                        group = False

                if group:
                    # group the peaks, calculate mean
                    mean = sum(mz_tuple[i:j+1])/len(mz_tuple[i:j+1])
                    intensity_sum = sum(intensity_tuple[i:j+1])
                    mz_list_grouped.append(tuple([mean, intensity_sum]))
                    i = j + 1
                else:
                    # peaks are ambigious, no grouping is applied --> every peak is stored
                    # this incident is counted.
                    count_ungrouped += j - i
                    # adding each element between i and j
                    for k in range(i, j + 1):
                        mz_list_grouped.append(tuple([mz_tuple[k], intensity_tuple[k]]))
                    i = j + 1

        if count_ungrouped:
            # if ungrouped entries occured, this is reported
            print('{0} elements could not be grouped due to an overlap.'.format(count_ungrouped), file = sys.stderr)
        return mz_list_grouped

    def _get_deisotopedMZ_for_chargeDeconvolution(self, ppmFactor = 4, minCharge = 1, maxCharge = 8, maxNextPeaks = 100):
        """
        Calculates the deisotoped m/z value as an input for the charge deconvolution

        :param ppmFactor: ppm factor
        :type ppmFactor: int
        :param minCharge: minimum charge considered
        :type minCharge: int
        :param maxCharge: maximum charge considered
        :type maxCharge: int
        :param maxNextPeaks: maximum length for isotope envelope
        :type maxNextPaks: int

        :rtype: list of tuples
        :return: Monoisotopic peak [(m/z, intensity_sum, charge, found),...]

        .. note::

           The argument *maxNextPeaks* is just to make sure that the isotope
           envelope doesnt get too long. This limit is not reached usually.

        """
        try:
            mz, intensities = zip(*self.centroidedPeaks)
        except ValueError:
            #empty spectrum
            exit()
            mz = []
            intensities = []

        monoisotopicPeaks = []
        length = len(mz)
        override = False
        for i in range(length):
            for charge in range(maxCharge, minCharge - 1, -1):
                # check absence of isotope envelope peaks before the current peak
                #print("Analyzing mz, charge:", mz[i], charge)
                found = False
                if i == 0:
                    # the current peak is the first peak, no preceding peak is available, so this is a monoisotopic candidate
                    pass
                else:
                    j = i - 1
                    target = mz[i] - ISOTOPE_AVERAGE_DIFFERENCE / charge
                    target_min = self.ppm2abs(target, self.measuredPrecision, -1, ppmFactor) # min and max should be calculated in one step (so that self.ppm() is not called twice)
                    target_max = self.ppm2abs(target, self.measuredPrecision, 1, ppmFactor)
                    while j >= 0 and mz[j] >= target_min:
                        if mz[j] <= target_max:
                            found = True
                            # Found preceeding peak, break goes to the next peak
                            break
                        j = j - 1

                # if a potential preceding peak for the current peak is found, jump to the next peak
                if found:
                    break
                ''' check presence of isotope envelope after the current peak'''
                found = 1
                intensity_sum = intensities[i]
                local_max = False
                for i_envelope in range(1, maxNextPeaks + 1):
                    k = i + 1
                    if (i + i_envelope) >= len(mz):
                        break
                    target = mz[i] + (ISOTOPE_AVERAGE_DIFFERENCE * i_envelope)/ charge
                    target_min = self.ppm2abs(target, self.measuredPrecision, -1, 1)
                    target_max = self.ppm2abs(target, self.measuredPrecision, 1, 1)
                    while k < length and mz[k] <= target_max:
                        if mz[k] >= target_min:
                            if intensities[k] < intensities[k-1]:
                                local_max = True
                            elif local_max and intensities[k] > intensities[k-1]:
                                # this would be a second local max, so this is no longer considered in the isotope envelope
                                break
                            found += 1
                            #print(mz[k])
                            intensity_sum += intensities[k]
                            # go to next k and reset the target
                            k += 1
                            if not k >= length:
                                target = mz[k] + ISOTOPE_AVERAGE_DIFFERENCE / charge
                                target_min = self.ppm2abs(target, self.measuredPrecision, -1, 1)
                                target_max = self.ppm2abs(target, self.measuredPrecision, 1, 1)
                        else:
                            k += 1
                    if found <= i_envelope:
                        break
                        # an isotope envelope is not supposed to have missing peaks

                if found > 1:
                    monoisotopicPeaks.append(tuple([mz[i], intensity_sum, charge, found]))
                    break
                    # as the first peak of the isotope envelope is added here, this is a monoisotopic peak.
                    # the charge derived from the isotope envelope is the highest charge which is possible.
        return monoisotopicPeaks

    @property
    def deconvolutedPeaks(self):
        """
        Calling :py:func:`spec.Spectrum.deconvolute_peaks` with standard
        parameters, which calculates uncharged masses and returns deconvoluted
        peaks.

        :rtype: list
        :return: list of deconvoluted peaks (mass (instead of m/z) / intensity tuples)

        """
        if self._deconvolutedPeaks == None:
            self._deconvolutedPeaks = self.deconvolute_peaks(ppmFactor = 4, minCharge = 1, maxCharge = 8, maxNextPeaks = 100)
        return self._deconvolutedPeaks

    def deconvolute_peaks(self, ppmFactor = 4, minCharge = 1, maxCharge = 8, maxNextPeaks = 100):
        """
        Calculating uncharged masses and returning deconvoluted peaks.

        The deconvolution of spectra is done by first identifying isotope envelopes and
        the charge state of this envelopes. The first peak of an isotope envelope is choosen
        as the monoisotopic peak for which the mass is calculated from the m/z ratio.
        Isotope envelopes are identified by searching the centroided spectrum for peaks
        which show no preceding isotope peak within a specified mass accuracy. To be
        sure, the measured mass accuracy is multiplied by a user adjustable factor
        (``ppmFactor``). When the current peak meets the criteria with no preceding peaks, the
        following peaks are analysed. The following peaks are considered to be part of
        the isotope envelope, as long as they fit within the measured precision and
        only one local maximum is present. The second local maximum is not considered
        as the starting point of a new isotope envelope as one cannot be sure were this
        isotope envelope starts. However, the last peak before the second local maximum
        is considered to be part of the isotope envelope from the first local maximum,
        as the intensity of this peak shouldn't have a big influence on the whole
        isotope envelope intensity.
        The charge range for detecting isotope envelopes can be specified (``minCharge``,
        ``maxCharge``). An isotope envelope always gets the highest possible charge.
        With the charge the mass can be calculated from the m/z value of the first peak
        of the isotope envelope. The intensity of the deconvoluted peak results from
        the sum of all isotope envelope peaks.
        In a last step, deconvoluted peaks are grouped together within the measured
        precision. This is necessary because isotope envelopes from the same fragment
        but with different charge states can leed to slightly different deconvoluted
        peaks.

        :param ppmFactor: ppm factor (imprecision factor)
        :type ppmFactor: int
        :param minCharge: minimum charge considered
        :type minCharge: int
        :param maxCharge: maximum charge considered
        :type maxCharge: int
        :param maxNextPeaks: maximum length for isotope envelope
        :type maxNextPaks: int

        :rtype: tuple (mass, intensity)
        :return: Deconvoluted peaks, mass (instead of m/z) and intensity are
            returned

        """
        if self.measuredPrecision > 50e-6:
            print("{0} ppm is too high for deconvolution. Please make sure to use spectra with < 50 ppm.".format(self.measuredPrecision * 1e6), file = sys.stderr)
            exit(1)

        # calculate monoisotopic m/z and charge
        interestingPeaks = self._get_deisotopedMZ_for_chargeDeconvolution(ppmFactor, minCharge, maxCharge, maxNextPeaks)

        # charge deconvolution
        result = []
        for mz, intensity, charge, n in interestingPeaks:
            mass = self._mz2mass(mz, charge)
            result.append(tuple([mass, intensity]))

        # sort the result corresponding to the mass (due to the mz to mass conversion, the values are no longer sorted)
        result = sorted(result)

        # check on empty result list
        if len(result) == 0:
            # no peaks could be identified for charge deconvolution.
            return []

        # group peaks
        return self._group(result)

    def ppm2abs(self, value, ppmValue, direction = 1, factor = 1):
        '''
        Returns the value plus (or minus, dependent on direction) the
        imprecession for this value.

        :param value: m/z value
        :type value: float
        :param ppmvalue: ppm value
        :type ppmvalue: int
        :param direction: plus or minus the considered m/z value. The argument
            *direction* should be 1 or -1
        :type direction: int
        :param factor: multiplication factor for the imprecision.The argument
            *factor* should be bigger than 0.
        :type factor: int
        :rtype: float
        :return: imprecision for a given value

        '''
        result = value + (value * (ppmValue * factor)) * direction
        return result

    def hasOverlappingPeak(self, mz):
        """
        Checks if a spetrum has more than one peak for a given m/z value and within the measured precision

        :param mz: m/z value which should be checked
        :type mz: float
        :return: Returns ``True`` if a nearby peak is detected, otherwise ``False``
        :rtype: bool
        """
        for minus_or_plus in [-1, 1]:
            target = self.ppm2abs(mz, self.measuredPrecision, minus_or_plus, 1)
            temp = self.hasPeak(self.ppm2abs(mz, self.measuredPrecision) )
            if temp and len(temp) > 1:
                return True
        return False

    def similarityTo(self,spec2):
        """
        Compares two spectra and returns cosine

        :param spec2: another pymzml spectrum that is compated to the current spectrum.
        :type spec2: pymzml.spec.Spectrum
        :return: value between 0 and 1, i.e. the cosine between the two spectra.
        :rtype: float

        .. note::
            Spectra data is transformed into an n-dimensional vector,
            whereas mz values are binned in bins of 10 m/z and the intensities are added up.
            Then the cosine is calculated between those two vectors.
            The more similar the specs are, the closer the value is to 1.

        """
        assert isinstance(spec2,Spectrum) , "Spectrum2 is not a pymzML spectrum"

        vector1 = ddict(int)
        vector2 = ddict(int)
        mzs = set()
        for mz, i in self.peaks:
            vector1[round(mz,1)] += i
            mzs.add(round(mz,1))
        for mz, i in spec2.peaks:
            vector2[round(mz,1)] += i
            mzs.add(round(mz,1))

        z = 0
        n_v1 = 0
        n_v2 = 0

        for mz in mzs:
            int1 = vector1[mz]
            int2 = vector2[mz]
            z += int1*int2
            n_v1 += int1*int1
            n_v2 += int2*int2
        try:
            cosine = z / (math.sqrt(n_v1) * math.sqrt(n_v2))
        except:
            cosine = 0.0
        return cosine


    def transformMZ(self, value):
        """
        pymzml uses an internal precision to different tasks. This precision depends on the
        measured prescision and is calculated when :py:func:`spec.Spectrum.measuredPrecision` is invoked.
        transformMZ can be used to transform mz values into the internal standard.

        :param value: mz value
        :type value: float
        :return: transformed value
        :rtype: float

        this value can be used to probe internal dictionaries, lists or sets, e.g. spectrum.tmzSet.

        Example:

        >>> import pymzml
        >>> mzValues_to_test = set()
        >>> run = pymzml.run.Reader( "test.mzML.gz" , MS1_Precision = 5e-6, MSn_Precision = 20e-6)
        >>>
        >>> for spectrum in run:
        ...     if spectrum["ms level"] == 2:
        ...             peak_to_find = spectrum.hasDeconvolutedPeak(1044.5804)
        ...             print(peak_to_find)
        [(1044.5596, 3809.4356300564586)]

        """
        return int(round(value * self.internalPrecision))

    def initFromTreeObject(self,treeObject):
        """
        treeObject.get('nativeID')
        print(treeObject)
        print(treeObject.items())
        for _ in treeObject.getiterator():
            print(_.tag,_.items())
        """
        self.clear()
        self._xmlTree = treeObject
        #
        if treeObject.tag.endswith('}chromatogram'):
            self['id'] = treeObject.get('id')
            self['ms level'] = None
        else:
            try:
                '''
                1.1.0  >> <spectrum id="spectrum=1019" index="8" defaultArrayLength="431">
                1.1.0  >> <spectrum id="scan=3" index="0" sourceFileRef="SF1" defaultArrayLength="92">
                1.0.0  >> <spectrum index="317" id="S318" nativeID="318" defaultArrayLength="34">
                0.99.1 >> <spectrum id="S20" scanNumber="20" msLevel="2">
                so far regex hold for this ...
                '''
                self['id'] = int(re.search( r'[0-9]*$',   treeObject.get('id')  ).group())
            except:
                self['id'] = None

        self['defaultArrayLength'] = int(treeObject.get('defaultArrayLength'))
        for element in treeObject.getiterator():
            accession = element.get('accession')
            self.ms[accession] = element
            if element.tag.endswith('cvParam'):
                if accession in self.param['accessions'].keys():
                    for mzmlTag in self.param['accessions'][accession]['valuesToExtract']:
                        try:
                            self._link(idTag = accession,
                                       value = element.get(mzmlTag),
                                       name  = self.param['accessions'][accession]['name']
                            )
                        except KeyError:
                            if mzmlTag == 'unitName':
                                continue
                                # this allows parsing of mzML files generated with ProteomeDiscoverer
                            else:
                                print("kind of 'unitName' issue again ... with {0}".format(mzmlTag))
                                exit()

                    if  self.param['accessions'][accession]['name'] == 'intensity array':
                        self['BinaryArrayOrder'].append(('arrayType', 'i'))

                    elif self.param['accessions'][accession]['name'] == 'm/z array':
                        self['BinaryArrayOrder'].append(('arrayType', 'mz'))

                    elif self.param['accessions'][accession]['name'] == 'time array':
                        self['BinaryArrayOrder'].append(('arrayType', 'time'))

                    elif self.param['accessions'][accession]['name'] == '32-bit float':
                        self['BinaryArrayOrder'].append(('encoding', '32-bit float'))

                    elif self.param['accessions'][accession]['name'] == '64-bit float':
                        self['BinaryArrayOrder'].append(('encoding', '64-bit float'))

                    elif self.param['accessions'][accession]['name'] == 'zlib compression':
                        self['BinaryArrayOrder'].append(('compression', 'zlib'))

                    elif self.param['accessions'][accession]['name'] == 'no compression':
                        self['BinaryArrayOrder'].append(('compression', 'no'))

            elif element.tag.endswith('precursorList'):
                self['precursors'] = []

            elif element.tag.endswith('selectedIon'):
                self['precursors'].append({'mz': None, 'charge': None})
                for subElement in element.getiterator():
                    if subElement.tag.endswith('cvParam'):
                        accession = subElement.get('accession')
                        if accession == 'MS:1000040':
                            self['precursors'][-1]['mz'] = subElement.get('value')
                        elif accession == 'MS:1000041':
                            self['precursors'][-1]['charge'] = subElement.get('value')
                        elif accession == 'MS:1000744':
                            self['precursors'][-1]['mz'] = subElement.get('value')
                        else:
                            pass

            elif element.tag.endswith('binary'):
                 self._link(    idTag = 'PY:0000000',
                                value = element.text,
                                name  = 'encodedData'
                    )

            elif element.tag.endswith('selectedIon'):
                if 'MS:1000040' in self.keys():
                    try:
                        self['precursors'][-1]['mz'] = float(self['MS:1000040'])
                    except KeyError:
                        pass
                if 'MS:1000744' in self.keys():
                    try:
                        self['precursors'][-1]['mz'] = float(self['MS:1000744'])
                    except KeyError:
                        pass

                try:
                    self['precursors'][-1]['charge'] = int(self['MS:1000041'])
                except KeyError:
                    pass
                else:
                    pass

        try:
            if self['ms level'] == 1:
                self.measuredPrecision = self.param['MS1_Precision']
            else:
                self.measuredPrecision = self.param['MSn_Precision']
        except KeyError:
            pass

        return


if __name__ == '__main__':
    print(__doc__)
