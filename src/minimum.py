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

MIN_REQ = [
#
#!NOTE!   exact names will be extracted of current OBO File, comments are just an orientation
#         pymzML comes with a little script (queryOBO.py) to query the obo file
#
#         $ ./example_scripts/queryOBO.py "scan time"
#         MS:1000016
#         scan time
#         "The time taken for an acquisition by scanning analyzers." [PSI:MS]
#         Is a: MS:1000503 ! scan attribute
#
('MS:1000016',['value']				), #"scan time" NOTE: that scan time comes with a unit                           
('MS:1000040',['value']             ), #"m/z"                                       
('MS:1000041',['value']             ), #"charge state"                              
('MS:1000127',['name']              ), #"centroid spectrum"                         
('MS:1000128',['name']              ), #"profile spectrum"                          
('MS:1000133',['name']              ), #"collision-induced dissociation"            
('MS:1000285',['value']             ), #"total ion current"                         
('MS:1000422',['name']              ), #"high-energy collision-induced dissociation"
('MS:1000511',['value']             ), #"ms level"                                  
('MS:1000512',['value']             ), #"filter string"                             
('MS:1000514',['name']              ), #"m/z array"                                 
('MS:1000515',['name']              ), #"intensity array"    
('MS:1000595',['name']              ), #"time array" 
('MS:1000521',['name']              ), #"32-bit float"                              
('MS:1000523',['name']              ), #"64-bit float"
('MS:1000574',['name']              ), #"zlib compression"
('MS:1000576',['name']              ), #"no compression"
('MS:1000744',['value']             ), # legacy precursor mz value ...
('MS:1000235',['name']              ), # total ion current chromatogram
]
