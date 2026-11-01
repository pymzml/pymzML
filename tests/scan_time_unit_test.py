import unittest
import xml.etree.ElementTree as ElementTree

from pymzml.spec import Spectrum

NS = "http://psi.hupo.org/ms/mzml"


def make_spectrum(scan_start_time_attrs=None):
    if scan_start_time_attrs is None:
        cv = ""
    else:
        attrs = " ".join(f'{k}="{v}"' for k, v in scan_start_time_attrs.items())
        cv = f'<cvParam cvRef="MS" accession="MS:1000016" name="scan start time" {attrs}/>'
    xml = (
        f'<spectrum xmlns="{NS}" index="0" id="scan=1" defaultArrayLength="0">'
        f"<scanList count=\"1\"><scan>{cv}</scan></scanList></spectrum>"
    )
    return Spectrum(ElementTree.fromstring(xml))


class ScanTimeUnitTest(unittest.TestCase):
    def test_unit_name(self):
        spec = make_spectrum({"value": "90", "unitCvRef": "UO", "unitAccession": "UO:0000010", "unitName": "second"})
        self.assertEqual(spec.scan_time_in_minutes(), 1.5)

    def test_unit_accession_without_unit_name(self):
        # unitName is optional in the mzML schema
        spec = make_spectrum({"value": "90", "unitCvRef": "UO", "unitAccession": "UO:0000010"})
        self.assertEqual(spec.scan_time_in_minutes(), 1.5)
        spec = make_spectrum({"value": "1.5", "unitCvRef": "UO", "unitAccession": "UO:0000031"})
        self.assertEqual(spec.scan_time_in_minutes(), 1.5)

    def test_millisecond(self):
        spec = make_spectrum({"value": "90000", "unitAccession": "UO:0000028", "unitName": "millisecond"})
        self.assertEqual(spec.scan_time_in_minutes(), 1.5)

    def test_no_scan_start_time(self):
        spec = make_spectrum()
        self.assertIsNone(spec.scan_time_in_minutes())

    def test_unknown_unit_still_raises(self):
        spec = make_spectrum({"value": "90"})
        with self.assertRaises(Exception):
            spec.scan_time_in_minutes()


if __name__ == "__main__":
    unittest.main(verbosity=3)
