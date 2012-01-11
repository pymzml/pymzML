#!/usr/bin/env python

"""

Check for presence of example files and download them.
Just call the function open_example()

For using the correct output directory just state get_example_file.OUTPUT_DIR

"""
from __future__ import print_function
import sys
import os.path
import hashlib
                                                                                                                                                                                        
SHA256_DICT = {'deconvolution.mzML.gz':                 ('19399e4f87d8937cf7be32bab7fd8889700e119cbc2ede215270cbfc9913b394', 'http://www.uni-muenster.de/hippler/pymzml/example_mzML_files/'),
               'dta_example.mzML':                      ('2cd7207d5106ee5fb3ab7867961a6c1ad02f0ef72da19532e7ebb41c8d010b1a', 'http://dev.thep.lu.se/fp6-prodac/export/80/trunk/mzML/'),
               'neutral_loss_example_1.1.0.mzML':       ('5911fa5d91a435aedd7be5a2ea09272f437d44f350948179a96146705a177a16', 'http://dev.thep.lu.se/fp6-prodac/export/80/trunk/mzML/scans/'),
               'precursor_spectrum_example_1.1.0.mzML': ('783187ec7eb2ee2713aecd9f6032508caad3439afa0b4a20232480b33472c17b', 'http://dev.thep.lu.se/fp6-prodac/export/80/trunk/mzML/scans/'),
               'profile-mass-spectrum.mzml':            ('2e952de2a25db421f3e30d8c659acc6c3f5e862e4d0fd32ec24c7c606c9a62fd', 'http://www.uni-muenster.de/hippler/pymzml/example_mzML_files/'),
               'small-1.0.0.mzml':                      ('9e15d6d2eba26932e4d5c61f92df7771da0bbb8589b7237d05bd915017dbf82f', 'http://www.uni-muenster.de/hippler/pymzml/example_mzML_files/'),
               'BSA1.mzML':                             ('d4bde93c77ec9e948cc62f4c022b8d54591073fd1170e264b69a79dc8d259830', 'http://open-ms.svn.sourceforge.net/viewvc/open-ms/OpenMS/share/OpenMS/examples/BSA/'),
               'proteomeDiscoverer.mzML.gz':            ('7fdd45bfcb6d82b2a75abd63fdc0d8cc1f14c1bd717ba2f3d4eec87ec201f3be', 'http://www.uni-muenster.de/hippler/pymzml/example_mzML_files/'),
               '32-bit.mzML.gz':                        ('199d2611c9894f2a07fb734fbe4db2226cd2a43e806d4e9662b66b979f7df264', 'http://www.uni-muenster.de/hippler/pymzml/example_mzML_files/'),
               '32-bit-compressed.mzML.gz':             ('30fdde9ebf3bb145a60ea589f466cb0db8b3b2c451646156db3e56ffe1bf0e59', 'http://www.uni-muenster.de/hippler/pymzml/example_mzML_files/'),
               '64-bit.mzML.gz':                        ('0d56a2295096e7499a8a90509661d22d4a6a097ad58f3c03310804c9698113aa', 'http://www.uni-muenster.de/hippler/pymzml/example_mzML_files/'),
               'small.pwiz.1.1.mzML':                   ('87ddde776c9933857edb22f404116f23e85ca8bddadc84d10308eb8853a58768', 'http://proteowizard.sourceforge.net/example_data/'),
               'MRM_example_1.1.0.mzML':                ('8140d77921be6fe49e73d71536b211ad39ae48f0272d4a465da2dd202185bdd9', 'http://dev.thep.lu.se/fp6-prodac/export/80/trunk/mzML/scans/'),
               'emptyScan.mzML.gz':                     ('4d82ea02c1f938e8fbe97b907371aad0eceee074bbee37f7513374a1bb7c3f3b', 'http://www.uni-muenster.de/hippler/pymzml/example_mzML_files/')
                }

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'mzML_example_files')
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), 'output')
try:
    os.makedirs(EXAMPLE_DIR)
except OSError:
    pass
try:
    os.makedirs(OUTPUT_DIR)
except OSError:
    pass


def open_example(filename):
    """
    filename = filename of a file in the example directory
    If the file "filename" is not present in the example directory, the file is downloaded.
    Path with filename is returned.
    """
    try:
        SHA256_DICT[filename]
    except KeyError:
        print('File "{0}" not available.'.format(filename), file = sys.stderr)
        exit(1)
    
    filename_with_path = os.path.join(EXAMPLE_DIR, filename)
    # check file presence
    checked_file = check_file(filename_with_path, filename)
    if checked_file:
        return filename_with_path
    
    # file is not present or corrupt
    server_url = SHA256_DICT[filename][1]
    url = server_url + filename
    if download(filename_with_path, url):
        checked_file = check_file(filename_with_path, filename)
        if checked_file:
            return filename_with_path
        else:
            os.remove(filename_with_path)
            print("Downloaded file is corrupt. Please try again.", file = sys.stderr)
            exit(1)        

        exit(1)

def check_file(filename_with_path, filename):
    # check file presence
    if os.path.isfile(filename_with_path):
        # file exists, check SHA224 sum
        file = open(filename_with_path, 'rb')
        if check_sha256(file, filename):
            return True

def check_sha256(file, filename):
    sha256_sum = SHA256_DICT[filename][0]
    gz = False
    if filename.split(".")[-1] == "gz":
        gz = True
    
    if hashlib.sha256(file.read()).hexdigest() == sha256_sum:
        return True
    else:
        return False
        
def calc_sha256(file):
    gz = False
    if file.split(".")[-1] == "gz":
        gz = True
    sha256 = hashlib.sha256()
    file = open(file, 'rb')
    return hashlib.sha256(file.read()).hexdigest()

def download(filename_with_path, url):
    """
    filename_with_path = path and filename, where to save downloaded file
    url = url to download
    Path with filename is returned.
    """
    
    download = None
    if sys.version_info[0] < 3:
        from urllib2 import Request, urlopen, URLError, HTTPError
    else:
        from urllib.request import Request, urlopen, URLError, HTTPError
    
    print("Downloading file ...", end="\r", file = sys.stderr)
    req = Request(url)
    print("Downloading file completed.", file = sys.stderr)        
    try:
        response = urlopen(req)
        with open(filename_with_path, 'wb') as f:
            f.write(response.read())
        return filename_with_path
    except HTTPError:
        print('HTTP Error: The server could not fulfill the request. Possibly, the file is not found on the server.', file = sys.stderr)
        exit(1)
    except URLError:
        print ('URL Error: Server not available. Please check your internet connection.', file = sys.stderr)
        exit(1)

if __name__ == '__main__':
    print(__doc__)
