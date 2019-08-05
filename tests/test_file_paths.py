import os

DATA_FOLDER = os.path.join(
    *[
        os.path.dirname(__file__),
        # 'tests',
        "data",
    ]
)

DATA_FILES = [
    "example.mzML",
    "example.mzML.gz",
    "example.mzML.idx.gz",
    "mini.chrom.mzML",
    "mini.chrom.mzML.gz",
    "mini.chrom.mzML.idx.gz",
    "mini_numpress.chrom.mzML",
    "mini_numpress.chrom.mzML.gz",
    "mini_numpress.chrom.mzML.idx.gz",
    "BSA1.mzML.gz",
    "example_invalid_obo_version.mzML",
    "example_no_obo_version.mzML",
]

paths = [os.path.join(DATA_FOLDER, file) for file in DATA_FILES]
