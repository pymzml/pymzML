#!/usr/bin/env python3

import sys
import os
from pymzml.utils.utils import index_gzip
import pymzml
import glob
import multiprocessing


def main(folder, num_cpus=1):
    """
    Creates indexed gzip mzML files from all mzMLs files in the given folder
    using a given number of threads.

    Usage:
        python multi_threading_file_compression.py <folder> <threads>

    Note:
        If the number of threads is larger than the number of actual possible
        threads, all possible threads will be used.

    """
    max_cpus = multiprocessing.cpu_count()
    if int(num_cpus) > max_cpus:
        num_cpus = max_cpus
    else:
        num_cpus = int(num_cpus)
    mzml_job_list = []
    for mzml_path in glob.glob(os.path.join(folder, "*.mzML")):
        out_path = "{0}.gz".format(mzml_path)
        if os.path.exists(out_path):
            print("Skipping: {0}".format(mzml_path))
            continue
        mzml_job_list.append((mzml_path, out_path))
    print(
        "Compressing {0} mzML files using {1} threads".format(
            len(mzml_job_list), num_cpus
        )
    )
    mp_pool = multiprocessing.Pool(num_cpus)
    results = mp_pool.starmap(compress_file, mzml_job_list)
    mp_pool.close()
    print("Done")
    return


def compress_file(file_path, out_path):
    print("Working on file {0}".format(file_path))
    with open(file_path) as fin:
        fin.seek(0, 2)
        max_offset_len = fin.tell()
        max_spec_no = pymzml.run.Reader(file_path).get_spectrum_count() + 10

    index_gzip(
        file_path, out_path, max_idx=max_spec_no, idx_len=len(str(max_offset_len))
    )
    print("Wrote file {0}".format(out_path))
    return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(main.__doc__)
        exit()
    else:
        main(*sys.argv[1:])
