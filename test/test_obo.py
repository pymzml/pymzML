import unittest

import pymzml.obo


class TestObo(unittest.TestCase):

    def test_normalize_version(self):
        normalize = pymzml.obo.oboTranslator._oboTranslator__normalize_version

        self.assertEqual(normalize(None), None)
        self.assertEqual(normalize('1.0.0'), '1.0.0')
        self.assertEqual(normalize('5.69.200-moop'), '5.69.200-moop')
        self.assertEqual(normalize('2340'), '2340.0.0')
        self.assertEqual(normalize('234.0'), '234.0.0')
        self.assertEqual(normalize('2.3.4.0'), '2.3.4.0')

    def test_valid_obo(self):
        # Test features of the OBO that differ for each version
        obos = {
            version: pymzml.obo.oboTranslator(version)
            for version in ('1.18.2', '2.0.0', '2.01.0')
        }

        # Changes from 1.18.2 to 2.0.0
        self.assertEqual(
            obos['1.18.2']['MS:0000000'],
            'Proteomics Standards Initiative Mass Spectrometry Ontology'
        )
        self.assertEqual(
            obos['2.0.0']['MS:0000000'],
            'Proteomics Standards Initiative Mass Spectrometry Vocabularies'
        )
        self.assertEqual(
            obos['2.0.0']['MS:0000000'],
            obos['2.01.0']['MS:0000000'],
        )

        # Changes from 2.0.0 to 2.01.0
        self.assertEqual(obos['1.18.2']['MS:1000854'], None)
        self.assertEqual(obos['2.0.0']['MS:1000854'], None)
        self.assertEqual(obos['2.01.0']['MS:1000854'], 'LTQ XL')

    def test_most_recent_obo(self):
        obo = pymzml.obo.oboTranslator()
        self.assertEqual(obo.version, None)

        # Changes only implemented in 3.78.0
        self.assertEqual(
            obo[obo['MS:1000130']]['is_a'],
            'MS:1000808 ! chromatogram attribute',
        )

    def test_invalid_obo(self):
        with self.assertRaises(Exception):
            obo = pymzml.obo.oboTranslator('1.1.1')
            parsing_on_demand = obo['MS:1002569']

    def test_getitem(self):
        obo = pymzml.obo.oboTranslator('3.78.0')
        data = {
            'id': 'MS:1002569',
            'name': 'ProteomeDiscoverer:Number of Spectra Processed At Once',
            'def': '"Number of spectra processed at once in a ProteomeDiscoverer search." [PSI:PI]',
            'xref': 'value-type:xsd\:int "The allowed value-type for this CV term."',
            'is_a': 'MS:1002101 ! ProteomeDiscoverer input parameter',
        }

        # Lookup by ID and get name
        self.assertEqual(obo[data['id']], data['name'])

        # Lookup by name and get a dict
        self.assertEqual(obo[data['name']], data)

        # Nested lookup
        self.assertEqual(obo[obo[data['id']]], data)

        # Lookup by definition and get a name
        self.assertEqual(obo[data['def']], data)



if __name__ == '__main__':
    unittest.main()
