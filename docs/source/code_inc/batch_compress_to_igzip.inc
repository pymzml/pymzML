.. code-block:: python

	#!/usr/bin/env python3.4
	
	import sys
	import os
	from pymzml.utils.utils import index_gzip
	from pymzml.run import Reader
	
	
	def main(mzml_path):
	    """
	    Create and indexed gzip mzML file from a plain mzML.
	
	    Usage: python3 gzip_mzml.py <path/to/mzml> <path/to/output>
	    """
	    with open(mzml_path) as fin:
	        fin.seek(0,2)
	        max_offset_len = fin.tell()
	        max_spec_no    = Reader(mzml_path).get_spectrum_count() + 10
	
	    out_path = '{0}.gz'.format(mzml_path)
	    index_gzip(
	        mzml_path,
	        out_path,
	        max_idx = max_spec_no,
	        idx_len = len(str(max_offset_len))
	    )
	    print('Wrote file {0}'.format(out_path))
	
	if __name__ == '__main__':
	    if len(sys.argv) > 1:
	        main(
	            sys.argv[1],
	        )
	    else:
	        print(main.__doc__)
