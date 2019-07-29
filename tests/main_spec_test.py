import sys
import os
sys.path.append(os.path.abspath("."))
import pymzml.run as run
from pymzml.spec import Spectrum, Chromatogram
import random
import statistics as stat
import unittest
import test_file_paths
from pprint import pprint

try:
    import numpy as np

    numpy_installed = True
except:
    numpy_installed = False


class SpectrumTest(unittest.TestCase):
    """
    """

    def assertPeaksIdentical(
        self, peaks1, peaks2, mult=1, msg=None, measured_precision=5e-6
    ):
        self.assertEqual(
            len(peaks1), len(peaks2), msg="List have different number of peaks!"
        )
        for x in range(len(peaks1)):
            self.assertAlmostEqual(
                peaks1[x][0], peaks2[x][0], msg=msg, delta=measured_precision
            )
            self.assertAlmostEqual(
                peaks1[x][1] * mult, peaks2[x][1], msg=msg, delta=5e-4
            )

    def setUp(self):
        """
        """
        self.paths = test_file_paths.paths
        path = self.paths[2]
        self.Run = run.Reader(path)
        self.spec = self.Run[6]

    def test_init(self):
        """
        """
        self.assertEqual(self.spec.measured_precision, 5e-6)
        self.assertEqual(self.spec.ns, "{http://psi.hupo.org/ms/mzml}")
        self.assertIsNotNone(self.spec.element)

    def test_mz(self):
        """
        """
        mz = self.spec.mz
        self.spec.mz = [1, 2, 3]
        self.assertCountEqual(self.spec.mz, [1, 2, 3])
        Run64 = run.Reader(self.paths[0])
        spec64 = Run64[2]
        mz64 = spec64.mz

    def test_i(self):
        """
        """
        i = self.spec.i
        self.spec.i = [1, 2, 3]
        self.assertCountEqual(self.spec.i, [1, 2, 3])

    def test_decode_to_numpy(self):
        """
        """
        if numpy_installed:
            test_array = [100.00087, 100.00238, 100.00389, 100.00541, 119.27174]
            b64_array = "cgDIQjgByEL+AchCxQLIQiGL7kIjjO5CJY3uQieO7kIpj+5CK5DuQi2R7kIvku5CMpPuQjeU7kI5le5CO5buQj2X7kK6QgJDTUMCQ+FDAkN0RAJDB0UCQ5pFAkMuRgJDwUYCQ1RHAkPoRwJDe0gCQw9JAkOiSQJDj/YGQyr3BkPF9wZDYfgGQ/z4BkOX+QZDM/oGQ876BkNp+wZDBfwGQ6L8BkM9/QZD2P0GQ3T+BkPmBRVDmgYVQ04HFUMCCBVDtggVQ2oJFUMfChVD0woVQ4cLFUM7DBVD8AwVQ6QNFUNYDhVDDA8VQ8EPFUN1EBVDKREVQ/UFFkOrBhZDYQcWQxcIFkPNCBZDgwkWQzkKFkPvChZDpQsWQ1sMFkMRDRZDxw0WQ34OFkM0DxZDw6gZQ4CpGUM9qhlD+aoZQ7arGUNzrBlDL60ZQ+ytGUOprhlDZq8ZQyKwGUPfsBlDnLEZQ0iiGkMGoxpDxaMaQ4OkGkNCpRpDAKYaQ7+mGkN9pxpDPKgaQ/+oGkO9qRpDfKoaQzqrGkO0o0dDy6RHQ+OlR0P6pkdDEahHQympR0NAqkdDWKtHQ2+sR0OHrUdDnq5HQ7avR0PNsEdDaT1RQ5U+UUPAP1FD7EBRQxhCUUNEQ1FDcERRQ5xFUUPHRlFD9EdRQyBJUUNLSlFDd0tRQ3p0bEPidWxDS3dsQ7N4bEMbemxDg3tsQ+t8bENTfmxDvH9sQySBbEONgmxD9YNsQ12FbEPGhmxDDn6EQ+R+hEO5f4RDj4CEQ2WBhEM6goRDEIOEQ+aDhEO7hIRDkYWEQ2eGhEM8h4RDEoiEQ5x6hUN0e4VDTHyFQyR9hUP9fYVD1X6FQ61/hUOFgIVDXYGFQzWChUMNg4VD5YOFQ72EhUOVhYVDlnaGQ3B3hkNLeIZDJXmGQwB6hkPaeoZDtHuGQ498hkNpfYZDRH6GQx5/hkP5f4ZD04CGQ66BhkOIgoZDY4OGQz2EhkMM9oZD6PaGQ8T3hkOf+IZDe/mGQ1f6hkMy+4ZDDvyGQ+r8hkPF/YZDof6GQ33/hkNYAIdDNAGHQxACh0PrAodDG9CIQ/vQiEPb0YhDu9KIQ5vTiEN71IhDXNWIQzzWiEMc14hD/NeIQ9zYiEO82YhDnNqIQ33biENvQYxDV0KMQ0BDjEMpRIxDEUWMQ/pFjEPjRoxDy0eMQ7RIjEOdSYxDhkqMQ25LjENXTIxDT3+MQzmAjEMigYxDC4KMQ/WCjEPeg4xDx4SMQ7CFjEOahoxDg4eMQ2yIjENWiYxDP4qMQyiLjEMSjIxD+4yMQ+WNjEMhAI1DCwGNQ/YBjUPgAo1DywONQ7UEjUOgBY1DigaNQ3UHjUNgCI1DSgmNQzUKjUMfC41DCgyNQ/UMjUP0fY1D4H6NQ8x/jUO3gI1Do4GNQ4+CjUN7g41DZ4SNQ1KFjUM+ho1DKoeNQxaIjUMCiY1D7YmNQ9mKjUO6eY5DqXqOQ5d7jkOFfI5Dc32OQ2F+jkNQf45DPoCOQyyBjkMago5DCYOOQ/eDjkPlhI5D1IWOQ8KGjkOwh45Dn4iOQ3n6jkNo+45DWPyOQ0f9jkM3/o5DJv+OQxYAj0MFAY9D9QGPQ+QCj0PUA49DwwSPQ7IFj0OiBo9DkQePQ4EIj0P7f5VD+4CVQ/uBlUP7gpVD+4OVQ/uElUP7hZVD+4aVQ/uHlUP7iJVD/ImVQ/yKlUP8i5VD/IyVQ/yNlUP8jpVD/I+VQ4AtmkOMLppDmC+aQ6UwmkOxMZpDvTKaQ8kzmkPVNJpD4jWaQ+42mkP6N5pDBjmaQxM6mkMfO5pDbF3DQ+pew0NpYMND52HDQw=="

            out_array = self.spec._decode_to_numpy(
                b64_array, 4292, "32-bit float", "no compression"
            )
            val1 = round(float(test_array[1]), 3)
            val2 = round(float(out_array[1]), 3)
            self.assertEqual(val1, val2)

    def test_decode_to_tuple(self):
        """
        """
        test_array = "123"
        b64_array = "cgDIQjgByEL+AchCxQLIQiGL7kIjjO5CJY3uQieO7kIpj+5CK5DuQi2R7kIvku5CMpPuQjeU7kI5le5CO5buQj2X7kK6QgJDTUMCQ+FDAkN0RAJDB0UCQ5pFAkMuRgJDwUYCQ1RHAkPoRwJDe0gCQw9JAkOiSQJDj/YGQyr3BkPF9wZDYfgGQ/z4BkOX+QZDM/oGQ876BkNp+wZDBfwGQ6L8BkM9/QZD2P0GQ3T+BkPmBRVDmgYVQ04HFUMCCBVDtggVQ2oJFUMfChVD0woVQ4cLFUM7DBVD8AwVQ6QNFUNYDhVDDA8VQ8EPFUN1EBVDKREVQ/UFFkOrBhZDYQcWQxcIFkPNCBZDgwkWQzkKFkPvChZDpQsWQ1sMFkMRDRZDxw0WQ34OFkM0DxZDw6gZQ4CpGUM9qhlD+aoZQ7arGUNzrBlDL60ZQ+ytGUOprhlDZq8ZQyKwGUPfsBlDnLEZQ0iiGkMGoxpDxaMaQ4OkGkNCpRpDAKYaQ7+mGkN9pxpDPKgaQ/+oGkO9qRpDfKoaQzqrGkO0o0dDy6RHQ+OlR0P6pkdDEahHQympR0NAqkdDWKtHQ2+sR0OHrUdDnq5HQ7avR0PNsEdDaT1RQ5U+UUPAP1FD7EBRQxhCUUNEQ1FDcERRQ5xFUUPHRlFD9EdRQyBJUUNLSlFDd0tRQ3p0bEPidWxDS3dsQ7N4bEMbemxDg3tsQ+t8bENTfmxDvH9sQySBbEONgmxD9YNsQ12FbEPGhmxDDn6EQ+R+hEO5f4RDj4CEQ2WBhEM6goRDEIOEQ+aDhEO7hIRDkYWEQ2eGhEM8h4RDEoiEQ5x6hUN0e4VDTHyFQyR9hUP9fYVD1X6FQ61/hUOFgIVDXYGFQzWChUMNg4VD5YOFQ72EhUOVhYVDlnaGQ3B3hkNLeIZDJXmGQwB6hkPaeoZDtHuGQ498hkNpfYZDRH6GQx5/hkP5f4ZD04CGQ66BhkOIgoZDY4OGQz2EhkMM9oZD6PaGQ8T3hkOf+IZDe/mGQ1f6hkMy+4ZDDvyGQ+r8hkPF/YZDof6GQ33/hkNYAIdDNAGHQxACh0PrAodDG9CIQ/vQiEPb0YhDu9KIQ5vTiEN71IhDXNWIQzzWiEMc14hD/NeIQ9zYiEO82YhDnNqIQ33biENvQYxDV0KMQ0BDjEMpRIxDEUWMQ/pFjEPjRoxDy0eMQ7RIjEOdSYxDhkqMQ25LjENXTIxDT3+MQzmAjEMigYxDC4KMQ/WCjEPeg4xDx4SMQ7CFjEOahoxDg4eMQ2yIjENWiYxDP4qMQyiLjEMSjIxD+4yMQ+WNjEMhAI1DCwGNQ/YBjUPgAo1DywONQ7UEjUOgBY1DigaNQ3UHjUNgCI1DSgmNQzUKjUMfC41DCgyNQ/UMjUP0fY1D4H6NQ8x/jUO3gI1Do4GNQ4+CjUN7g41DZ4SNQ1KFjUM+ho1DKoeNQxaIjUMCiY1D7YmNQ9mKjUO6eY5DqXqOQ5d7jkOFfI5Dc32OQ2F+jkNQf45DPoCOQyyBjkMago5DCYOOQ/eDjkPlhI5D1IWOQ8KGjkOwh45Dn4iOQ3n6jkNo+45DWPyOQ0f9jkM3/o5DJv+OQxYAj0MFAY9D9QGPQ+QCj0PUA49DwwSPQ7IFj0OiBo9DkQePQ4EIj0P7f5VD+4CVQ/uBlUP7gpVD+4OVQ/uElUP7hZVD+4aVQ/uHlUP7iJVD/ImVQ/yKlUP8i5VD/IyVQ/yNlUP8jpVD/I+VQ4AtmkOMLppDmC+aQ6UwmkOxMZpDvTKaQ8kzmkPVNJpD4jWaQ+42mkP6N5pDBjmaQxM6mkMfO5pDbF3DQ+pew0NpYMND52HDQw=="
        out_array = self.spec._decode_to_tuple(
            b64_array, 343, "32-bit float", "no compression"
        )
        # self.assertEqual(out_array, test_array)

    def test_reprofile_peaks(self):
        """
        """
        r_peaks = self.spec.peaks("reprofiled")
        self.assertIsNotNone(r_peaks)
        # self.assertEqual(r_peaks, [(1, 10),(2, 20),(3, 30),(4, 40)])

    def test_centroid_peaks(self):
        """
        """
        self.spec.set_peaks([(1, 10), (2, 20), (3, 30), (4, 40)], "centroided")
        c_peaks = self.spec.peaks("centroided")
        self.assertPeaksIdentical(c_peaks, [(1, 10), (2, 20), (3, 30), (4, 40)])

    def test_centroid_peaks_for_real(self):
        """
        """
        new_peaks = [
            (99.999, 0.1),
            (99.9995, 1),
            (100.0000, 10),
            (100.0005, 1),
            (100.001, 0.1),
        ]
        self.spec.set_peaks(new_peaks, "raw")
        self.spec.measured_precision = 1e-5
        peaks = self.spec.peaks("centroided")
        self.assertPeaksIdentical(peaks, new_peaks)

    def test_median(self):
        array = [1, 4, 6, 7, 2, 5, 7, 23.324, 5.0, -4.4, 0]
        res = self.spec._median(array)
        res_correct = stat.median(array)
        self.assertEqual(res_correct, res)

    def test_add(self):
        """
        """
        spec = self.Run[6]
        p1 = spec.peaks("reprofiled")
        spec += spec
        p2 = spec.peaks("reprofiled")
        self.assertPeaksIdentical(
            p1, p2, mult=2
        )  # , msg='List 1 : {0}\nList 2:{1}'.format(p1, p2))

    def test_sub(self):
        spec = self.Run[6]
        p1 = spec.peaks("reprofiled")
        spec -= spec
        p2 = spec.peaks("reprofiled")

        self.assertPeaksIdentical(
            p1, p2, mult=0
        )  # , msg='List 1 : {0}\nList 2:{1}'.format(p1, p2))

    def test_mult(self):
        """
        """
        new_peaks = [(1, 10), (2, 20)]
        self.spec.set_peaks(new_peaks, "raw")
        self.spec * 2
        self.assertCountEqual(self.spec.peaks("raw")[0], (1, 20))
        self.assertCountEqual(self.spec.peaks("raw")[1], (2, 40))

    def test_div(self):
        """
        """
        new_peaks = [(1, 10), (2, 20)]
        self.spec.set_peaks(new_peaks, "raw")
        self.spec / 2
        self.assertCountEqual(self.spec.peaks("raw")[0], (1, 5))
        self.assertCountEqual(self.spec.peaks("raw")[1], (2, 10))

    def test_add_specs_to_empty_spec(self):
        spec1 = Spectrum()
        spec2 = Spectrum()
        spec2.set_peaks([(100, 200)], 'raw')
        spec1 += spec2
        centroided_mz = spec1.peaks('centroided')[:,0]
        centroided_i  = spec1.peaks('centroided')[:,1]
        assert np.allclose(
            centroided_mz,
            [100],
            rtol=5e-6
        )
        assert np.allclose(
            centroided_i,
            [200],
            atol=0.002
        )

    def test_add_tow_custom_specs(self):
        spec1 = Spectrum()
        spec2 = Spectrum()
        spec1.set_peaks([(100, 200)], 'raw')
        spec2.set_peaks([(100, 200), (200, 300)], 'raw')
        spec1 += spec2
        centroided_mz = spec1.peaks('centroided')[:,0]
        centroided_i  = spec1.peaks('centroided')[:,1]
        assert np.allclose(
            centroided_mz,
            [100, 200],
            rtol=5e-6
        )
        assert np.allclose(
            centroided_i,
            [400, 300],
            atol=0.002
        )

    def test_average_spectra(self):
        spec0 = Spectrum()
        spec1 = Spectrum()
        spec2 = Spectrum()

        spec1.set_peaks(np.array([(100, 200)]), 'centroided')
        spec2.set_peaks(np.array([(100, 200), (200, 300)]), 'centroided')

        spec0 += (spec1 / spec1.peaks('centroided')[:,1].sum())
        spec0 += (spec2 / spec2.peaks('centroided')[:,1].sum())

        centroided_peaks = spec0.peaks('centroided')
        assert np.allclose(
            centroided_peaks[:,0],
            [100, 200]
        )
        assert np.allclose(
            centroided_peaks[:,1],
            [1.4, 0.6],
            atol=0.0001
        )


    def test_reduce(self):
        """
        """
        new_peaks = [(50, 100), (102, 300), (400, 20), (401, 207)]
        # self.spec.peaks = new_peaks
        self.spec.set_peaks(new_peaks, "raw")
        peaks = self.spec.peaks("raw")
        self.spec.reduce(mz_range=(100, 400))
        self.assertPeaksIdentical(self.spec.peaks("raw"), [(102, 300), (400, 20)])

    def test_highest_peaks(self):
        """
        """
        h_peaks = self.spec.highest_peaks(3)
        high_i = [i for mz, i in h_peaks]
        self.assertEqual(
            sorted([i for mz, i in self.spec.peaks("centroided")])[-3:], high_i
        )

    def test_extreme_values(self):
        """
        """
        new_peaks = [(1, 10000), (10000, 1), (500, 600), (600, 500)]
        self.spec.set_peaks(new_peaks, "raw")
        extreme_vals_i = self.spec.extreme_values("i")
        extreme_vals_mz = self.spec.extreme_values("mz")
        self.assertEqual(extreme_vals_mz, (1, 10000))
        self.assertEqual(extreme_vals_i, (1, 10000))

    def test_has_peak(self):
        """
        """
        i = self.spec.peaks("centroided")[1][0]
        hits = self.spec.has_peak(i)
        hits2 = self.spec.has_peak(i + 5e-6)
        self.assertAlmostEqual(hits[0][0], i)
        self.assertIsNotNone(hits2[0][0], i)

    def test_transform_mz(self):
        """
        """
        mz = 213.33333333333333
        tMZ = self.spec.transform_mz(mz)
        self.assertEqual(tMZ, int(round(mz * self.spec.internal_precision)))

    def test_has_overlapping_peak(self):
        """
        """
        overlaps = []
        mzs = self.spec.mz
        for mz in mzs:
            overlaps.append(self.spec.has_overlapping_peak(mz))
        self.assertTrue(any(overlaps))

    def test_similarity_to(self):
        """
        """
        cos = self.spec.similarity_to(self.spec)
        self.assertEqual(round(cos), 1)

        # cos in this part to high, is other cos right though???
        spec2 = self.spec
        spec2.set_peaks([(1, 2), (3, 4)], "raw")
        cos = self.spec.similarity_to(spec2)
        self.assertLess(cos, 1)

    def test_peaks_are_set(self):
        spec = self.spec
        spec.set_peaks([(1000, 10)], "raw")
        self.assertEqual(spec.mz, [1000])
        self.assertEqual(spec.i, [10])
        self.assertPeaksIdentical(spec.peaks("raw"), [(1000, 10)])

    def test_spec_has_peak_within_precision(self):
        """
        """
        pass

    def test_getitem_index_gzip(self):
        idx_gzip = self.paths[2]
        run_idx_gzip = run.Reader(idx_gzip)
        randInt = 6
        spec = run_idx_gzip[randInt]
        self.assertIsInstance(spec, Spectrum)
        self.assertEqual(spec.ID, randInt)
        self.assertIsInstance(run_idx_gzip["TIC"], Chromatogram)

    def test_getitem_standard_gzip_1(self):
        gzip = self.paths[1]
        run_gzip = run.Reader(gzip)
        self.assertIsInstance(run_gzip[1], Spectrum)

    def test_getitem_standard_gzip_tic(self):
        gzip = self.paths[1]
        run_gzip = run.Reader(gzip)
        self.assertIsInstance(run_gzip["TIC"], Chromatogram)

    def test_getitem_standard_mzml_random(self):
        mzml = self.paths[0]
        RunMzml = run.Reader(mzml)
        randInt = 4
        self.assertIsInstance(RunMzml[randInt], Spectrum)
        self.assertIsInstance(RunMzml["TIC"], Chromatogram)

    def test_getitem_2_times_standard_mzml(self):
        mzml = self.paths[0]
        RunMzml = run.Reader(mzml)
        randInt = 10
        spec1 = RunMzml[randInt]
        self.assertIn(spec1.ID, RunMzml.info["offset_dict"])
        spec2 = RunMzml[randInt]
        self.assertIsInstance(RunMzml[randInt], Spectrum)
        self.assertEqual(spec1.ID, spec2.ID)

    def test_getitems_end_standard_mzml(self):
        mzml = self.paths[0]
        RunMzml = run.Reader(mzml)
        spec = RunMzml[11]
        self.assertEqual(spec.ID, 11)

    def test_getitem_index_mzml(self):
        idx_mzml = self.paths[1]
        run_idx_mzml = run.Reader(idx_mzml)
        randInt = 1
        spec = run_idx_mzml[randInt]
        self.assertIsInstance(spec, Spectrum)
        self.assertEqual(spec.ID, randInt)
        self.assertIsInstance(run_idx_mzml["TIC"], Chromatogram)

    def test_getitem_index_mzml_last(self):
        idx_mzml = self.paths[0]
        run_idx_mzml = run.Reader(idx_mzml)
        spec = run_idx_mzml[11]
        self.assertIsInstance(spec, Spectrum)
        self.assertEqual(spec.ID, 11)

    def test_getitem_index_mzml_double(self):
        idx_mzml = self.paths[0]
        run_idx_mzml = run.Reader(idx_mzml)
        self.assertIsInstance(run_idx_mzml[4], Spectrum)
        self.assertIn(4, run_idx_mzml.info["offset_dict"])
        self.assertIsInstance(run_idx_mzml[4], Spectrum)

    def test_get_search_spec_with_string(self):
        mzml = self.paths[0]
        Reader = run.Reader(mzml)
        string = "scan=2"
        self.assertIsInstance(Reader[string], Spectrum)

    def test_get_element_by_name(self):
        search_name = "scan window lower limit"
        ele = self.spec.get_element_by_name(search_name)
        self.assertEqual(ele.get("name"), search_name)

    def test_get_element_by_path(self):
        elements = self.spec.get_element_by_path(hooks=["scanList", "cvParam"])
        self.assertIsInstance(elements, list)
        for ele in elements:
            self.assertIn("cvParam", ele.tag)
        elements = self.spec.get_element_by_path(
            ["scanList", "scan", "scanWindowList", "scanWindow", "cvParam"]
        )
        self.assertIsInstance(elements, list)
        for ele in elements:
            self.assertIn("cvParam", ele.tag)

    def test_peaks(self):
        peaks = self.spec.peaks("raw")
        self.assertPeaksIdentical(
            peaks[:5],
            [
                [7.00487061e01, 6.13473730e03],
                [7.00657654e01, 4.08554297e04],
                [7.10610352e01, 2.26755859e04],
                [7.20450134e01, 6.51679375e04],
                [7.20813980e01, 3.49662469e05],
            ],
        )

    def test_remove_noise_mean_spec_6(self):
        spec = self.Run[6]
        spec.remove_noise("mean")
        self.assertPeaksIdentical(
            spec.peaks("centroided")[:5],
            [
                [7.20813980e01, 3.49662469e05],
                [7.40606766e01, 1.18710039e05],
                [7.40970306e01, 1.35170670e07],
                [7.51003647e01, 6.28674688e05],
                [8.40448761e01, 1.36323156e05],
            ],
        )

    def test_remove_noise_median_spec_6(self):
        spec = self.Run[6]
        spec.remove_noise("median")
        self.assertPeaksIdentical(
            spec.peaks("centroided")[:5],
            [
                [7.00657654e01, 4.08554297e04],
                [7.10610352e01, 2.26755859e04],
                [7.20450134e01, 6.51679375e04],
                [7.20813980e01, 3.49662469e05],
                [7.30847321e01, 2.11254648e04],
            ],
        )

    def test_remove_noise_mad_spec_6(self):
        spec = self.Run[6]
        p1 = spec.peaks("centroided")
        spec.remove_noise("mad")
        p2 = spec.peaks("centroided")
        self.assertPeaksIdentical(
            p2[:5],
            [
                [7.00657654e01, 4.08554297e04],
                [7.10610352e01, 2.26755859e04],
                [7.20450134e01, 6.51679375e04],
                [7.20813980e01, 3.49662469e05],
                [7.30847321e01, 2.11254648e04],
            ],
        )

    def test_transformed_mz_with_error(self):
        tmz = self.spec.transformed_mz_with_error
        self.assertIsInstance(tmz, dict)
        self.assertIsNotNone(len(tmz))

    def test_transformed_peaks(self):
        spec = self.Run[6]
        tpeaks = spec.transformed_peaks
        self.assertIsInstance(tpeaks, list)
        self.assertIsNotNone(len(tpeaks))
        known_tPeaks = [
            (700487, 6134.7373046875),
            (700658, 40855.4296875),
            (710610, 22675.5859375),
            (720450, 65167.9375),
            (720814, 349662.46875),
        ]
        self.assertPeaksIdentical(tpeaks[:5], known_tPeaks)

    def test_t_mz_set(self):
        spec = self.Run[6]
        tmzs = spec.t_mz_set
        self.assertIsInstance(tmzs, set)
        self.assertEqual(len(tmzs), 23081)

    # def test_precursosr(self):
    #     ms2_spec = self.Run[3]
    #     prec =ms2_spec.precursors
    #     self.assertIsNotNone(len(prec))
    #     self.assertIsInstance(prec, list)
    #     self.assertEqual(prec, ['199'])

    def test_TIC(self):
        tic = self.spec.TIC
        self.assertIsNotNone(tic)
        self.assertIsInstance(tic, float)
        self.assertEqual(tic, 9.6721256e07)

    def test_scan_time(self):
        scan_time, unit = self.spec.scan_time
        self.assertIsNotNone(scan_time)
        self.assertIsInstance(scan_time, float)
        self.assertEqual(scan_time, 0.023756566)


if __name__ == "__main__":
    unittest.main(verbosity=3)
