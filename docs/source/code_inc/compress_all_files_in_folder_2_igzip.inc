.. code-block:: python

	#!/usr/bin/env python3
	
	import sys
	import os
	from pymzml.utils.utils import index_gzip
	# from pymzml.run import Reader
	import pymzml
	import glob
	
	
	def main(folder):
	    """
	    Create an indexed gzip mzML file from a plain mzML of all files in folder
	
	    Usage: python3 gzip_mzml.py <folder>
	    """
	
	    for mzml_path in glob.glob(os.path.join(folder, '*.mzML')):
	        if os.path.exists('{0}.gz'.format(mzml_path)):
	            print('Skipping: {0}'.format(mzml_path))
	            continue
	        print('Processing file: {0}'.format(mzml_path))
	        with open(mzml_path) as fin:
	            fin.seek(0,2)
	            max_offset_len = fin.tell()
	            max_spec_no    = pymzml.run.Reader(mzml_path).get_spectrum_count() + 10
	        out_path = '{0}.gz'.format(mzml_path)
	        index_gzip(
	            mzml_path,
	            out_path,
	            max_idx = max_spec_no,
	            idx_len = len(str(max_offset_len))
	        )
	        print('Wrote file {0}'.format(out_path))
	
	if __name__ == '__main__':
	    main(sys.argv[1])
