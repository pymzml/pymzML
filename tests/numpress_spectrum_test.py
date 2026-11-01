import os
import tempfile
import unittest
from unittest import mock

import numpy as np

import pymzml.decoder
import pymzml.run as run
from pymzml.ms_numpress import MSNumpress

MZ = [100.0123, 150.5, 200.25, 333.3333, 499.9999]
INTENSITY = [10.0, 2000.0, 35.0, 100000.0, 7.0]

# base64 payloads made with pynumpress from MZ (linear) and INTENSITY (pic, slof),
# plain and zlib-compressed after numpress
LINEAR = "QWs3SEAAAABdbw9Vzf//f6Thb1BfT/1kAqIAnBA="
LINEAR_ZLIB = "eJxzzDb3cGBgYIjN5w89+/9//ZKH+QHx/n9TmBYxzBEAAJ8QC4k="
PIC = "elDXYyMKaBdw"
PIC_ZLIB = "eJyrCrierMyVIV4AABGzAyE="
SLOF = "QLY8AAAAAABRNQOprU/8/zwu"
SLOF_ZLIB = "eJxz2GbDAAKBpswr1/r/+W+jBwArUgXG"

TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<mzML xmlns="http://psi.hupo.org/ms/mzml" version="1.1.0">
  <cvList count="2">
    <cv id="MS" fullName="PSI-MS" URI="https://raw.githubusercontent.com/HUPO-PSI/psi-ms-CV/master/psi-ms.obo" version="4.1.0"/>
    <cv id="UO" fullName="Unit Ontology" URI="http://ontologies.berkeleybop.org/uo.obo"/>
  </cvList>
  <run id="r">
    <spectrumList count="1">
      <spectrum index="0" id="scan=1" defaultArrayLength="5">
        <cvParam cvRef="MS" accession="MS:1000511" name="ms level" value="1"/>
        <binaryDataArrayList count="2">
          <binaryDataArray encodedLength="{mz_len}">
            <cvParam cvRef="MS" accession="MS:1000523" name="64-bit float"/>
            <cvParam cvRef="MS" accession="{mz_acc}" name="{mz_name}"/>
            <cvParam cvRef="MS" accession="MS:1000514" name="m/z array" unitCvRef="MS" unitAccession="MS:1000040" unitName="m/z"/>
            <binary>{mz}</binary>
          </binaryDataArray>
          <binaryDataArray encodedLength="{i_len}">
            <cvParam cvRef="MS" accession="MS:1000523" name="64-bit float"/>
            <cvParam cvRef="MS" accession="{i_acc}" name="{i_name}"/>
            <cvParam cvRef="MS" accession="MS:1000515" name="intensity array" unitCvRef="MS" unitAccession="MS:1000131" unitName="number of detector counts"/>
            <binary>{i}</binary>
          </binaryDataArray>
        </binaryDataArrayList>
      </spectrum>
    </spectrumList>
  </run>
</mzML>
"""

CASES = {
    "linear and pic": (
        ("MS:1002312", "MS-Numpress linear prediction compression", LINEAR),
        ("MS:1002313", "MS-Numpress positive integer compression", PIC),
        1e-6,
    ),
    "linear and slof": (
        ("MS:1002312", "MS-Numpress linear prediction compression", LINEAR),
        ("MS:1002314", "MS-Numpress short logged float compression", SLOF),
        1e-3,
    ),
    "linear and pic followed by zlib": (
        ("MS:1002746", "MS-Numpress linear prediction compression followed by zlib compression", LINEAR_ZLIB),
        ("MS:1002747", "MS-Numpress positive integer compression followed by zlib compression", PIC_ZLIB),
        1e-6,
    ),
    "linear and slof followed by zlib": (
        ("MS:1002746", "MS-Numpress linear prediction compression followed by zlib compression", LINEAR_ZLIB),
        ("MS:1002748", "MS-Numpress short logged float compression followed by zlib compression", SLOF_ZLIB),
        1e-3,
    ),
}


class NumpressSpectrumTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _write(self, name, mz_param, i_param):
        path = os.path.join(self.tmpdir.name, name.replace(" ", "_") + ".mzML")
        with open(path, "w") as fh:
            fh.write(
                TEMPLATE.format(
                    mz_acc=mz_param[0], mz_name=mz_param[1], mz=mz_param[2], mz_len=len(mz_param[2]),
                    i_acc=i_param[0], i_name=i_param[1], i=i_param[2], i_len=len(i_param[2]),
                )
            )
        return path

    def _check(self):
        for name, (mz_param, i_param, rtol) in CASES.items():
            with self.subTest(name):
                spec = next(iter(run.Reader(self._write(name, mz_param, i_param))))
                np.testing.assert_allclose(spec.mz, MZ, rtol=1e-6)
                np.testing.assert_allclose(spec.i, INTENSITY, rtol=rtol)

    def test_numpress_spectra(self):
        self._check()

    def test_numpress_spectra_python_fallback(self):
        with mock.patch.object(pymzml.decoder, "MSDecoder", MSNumpress()):
            self._check()


if __name__ == "__main__":
    unittest.main(verbosity=3)
