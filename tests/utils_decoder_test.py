#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Part of pymzml test cases
"""
# import sys
# import os
# # import PyNumpress
# import pymzml
# import pymzml.decoder as decoder
# import time
# import unittest
# import numpy as np
# # import PyNumpress as pnp
# import zlib
# from base64 import b64encode as b64enc
# import test_file_paths


# class DecoderTest(unittest.TestCase):

#     def assertPeaksIdentical(self, peaks1, peaks2, msg=None):
#         self.assertEqual(len(peaks1), len(peaks2))#, msg='List have different number of peaks!')
#         for x in range(len(peaks1)):
#             self.assertCountEqual(peaks1[x], peaks2[x], msg=msg)

#     def setUp(self):
#         self.paths = test_file_paths.paths
#         self.Decoder = pymzml.Decoder
#         self.Run  = pymzml.run.Reader(self.paths[2])

#     def test_decode_numpress(self):
#         arr = np.asarray([1,2,3], dtype=np.float64)
#         dec = pnp.MSNumpress([])
#         enc_np = dec.encode_linear(arr, dec.optimal_linear_fixed_point(arr))
#         enc_np_zlib = zlib.compress(enc_np)
#         enc_np_zlib_b64 = b64enc(enc_np_zlib)
#         comp = ['zlib', 'MS-Numpress linear prediction compression']
#         d_type, decoded = decoder._decode(enc_np_zlib_b64, comp, 3, '32-bit float', 'i')
#         self.assertCountEqual(arr, decoded)

#     def test_decode_numpress(self):
#         test_array = np.asarray([1,2,3], dtype=np.float64)
#         MSNumpress = PyNumpress.MSNumpress([])
#         nump_enc   = MSNumpress.encode_linear(test_array, MSNumpress.optimal_linear_fixed_point(test_array))
#         zlib_nump_enc = zlib.compress(nump_enc)
#         b64_zlib_nump_enc =b64enc( zlib_nump_enc )
#         d_type, arr = decoder._decode(b64_zlib_nump_enc, ['zlib', 'ms-np-slof'], 3, '64-bit float', 'i')
#         self.assertIsNotNone(len(arr))
#         self.assertIsInstance(arr, list)


#     def test_decode_32_bit_no_compression(self):
#         b64_array = 'cgDIQjgByEL+AchCxQLIQiGL7kIjjO5CJY3uQieO7kIpj+5CK5DuQi2R7kIvku5CMpPuQjeU7kI5le5CO5buQj2X7kK6QgJDTUMCQ+FDAkN0RAJDB0UCQ5pFAkMuRgJDwUYCQ1RHAkPoRwJDe0gCQw9JAkOiSQJDj/YGQyr3BkPF9wZDYfgGQ/z4BkOX+QZDM/oGQ876BkNp+wZDBfwGQ6L8BkM9/QZD2P0GQ3T+BkPmBRVDmgYVQ04HFUMCCBVDtggVQ2oJFUMfChVD0woVQ4cLFUM7DBVD8AwVQ6QNFUNYDhVDDA8VQ8EPFUN1EBVDKREVQ/UFFkOrBhZDYQcWQxcIFkPNCBZDgwkWQzkKFkPvChZDpQsWQ1sMFkMRDRZDxw0WQ34OFkM0DxZDw6gZQ4CpGUM9qhlD+aoZQ7arGUNzrBlDL60ZQ+ytGUOprhlDZq8ZQyKwGUPfsBlDnLEZQ0iiGkMGoxpDxaMaQ4OkGkNCpRpDAKYaQ7+mGkN9pxpDPKgaQ/+oGkO9qRpDfKoaQzqrGkO0o0dDy6RHQ+OlR0P6pkdDEahHQympR0NAqkdDWKtHQ2+sR0OHrUdDnq5HQ7avR0PNsEdDaT1RQ5U+UUPAP1FD7EBRQxhCUUNEQ1FDcERRQ5xFUUPHRlFD9EdRQyBJUUNLSlFDd0tRQ3p0bEPidWxDS3dsQ7N4bEMbemxDg3tsQ+t8bENTfmxDvH9sQySBbEONgmxD9YNsQ12FbEPGhmxDDn6EQ+R+hEO5f4RDj4CEQ2WBhEM6goRDEIOEQ+aDhEO7hIRDkYWEQ2eGhEM8h4RDEoiEQ5x6hUN0e4VDTHyFQyR9hUP9fYVD1X6FQ61/hUOFgIVDXYGFQzWChUMNg4VD5YOFQ72EhUOVhYVDlnaGQ3B3hkNLeIZDJXmGQwB6hkPaeoZDtHuGQ498hkNpfYZDRH6GQx5/hkP5f4ZD04CGQ66BhkOIgoZDY4OGQz2EhkMM9oZD6PaGQ8T3hkOf+IZDe/mGQ1f6hkMy+4ZDDvyGQ+r8hkPF/YZDof6GQ33/hkNYAIdDNAGHQxACh0PrAodDG9CIQ/vQiEPb0YhDu9KIQ5vTiEN71IhDXNWIQzzWiEMc14hD/NeIQ9zYiEO82YhDnNqIQ33biENvQYxDV0KMQ0BDjEMpRIxDEUWMQ/pFjEPjRoxDy0eMQ7RIjEOdSYxDhkqMQ25LjENXTIxDT3+MQzmAjEMigYxDC4KMQ/WCjEPeg4xDx4SMQ7CFjEOahoxDg4eMQ2yIjENWiYxDP4qMQyiLjEMSjIxD+4yMQ+WNjEMhAI1DCwGNQ/YBjUPgAo1DywONQ7UEjUOgBY1DigaNQ3UHjUNgCI1DSgmNQzUKjUMfC41DCgyNQ/UMjUP0fY1D4H6NQ8x/jUO3gI1Do4GNQ4+CjUN7g41DZ4SNQ1KFjUM+ho1DKoeNQxaIjUMCiY1D7YmNQ9mKjUO6eY5DqXqOQ5d7jkOFfI5Dc32OQ2F+jkNQf45DPoCOQyyBjkMago5DCYOOQ/eDjkPlhI5D1IWOQ8KGjkOwh45Dn4iOQ3n6jkNo+45DWPyOQ0f9jkM3/o5DJv+OQxYAj0MFAY9D9QGPQ+QCj0PUA49DwwSPQ7IFj0OiBo9DkQePQ4EIj0P7f5VD+4CVQ/uBlUP7gpVD+4OVQ/uElUP7hZVD+4aVQ/uHlUP7iJVD/ImVQ/yKlUP8i5VD/IyVQ/yNlUP8jpVD/I+VQ4AtmkOMLppDmC+aQ6UwmkOxMZpDvTKaQ8kzmkPVNJpD4jWaQ+42mkP6N5pDBjmaQxM6mkMfO5pDbF3DQ+pew0NpYMND52HDQw=='
#         d_type, arr = decoder._decode(b64_array, 'no compression', 343, '32-bit float', 'i')
#         self.assertIsNotNone(len(arr))
#         self.assertIsInstance(arr, np.ndarray)

#     def test_pool_decode_TIC(self):
#         """
#         """
#         spec  = self.Run["TIC"]
#         spec2 = self.Run["TIC"]
#         paramsMZ = spec._get_encoding_parameters('time array')
#         paramsMZ += ('time',)
#         paramsI = spec._get_encoding_parameters('intensity array')
#         paramsI += ('i',)

#         s = time.time()
#         self.Decoder.pool_decode([paramsMZ, paramsI], spec._register)
#         t1 = time.time() - s
#         peaks1 = spec.profile


#         s = time.time()
#         peaks2 = list(zip(spec.time, spec.i))
#         t2 = time.time() - s
#         self.assertPeaksIdentical(peaks1, peaks2)

#         assert t1 < t2, 'parallel version is slower than normal version:\n' \
#                 'Parallel took {0:.5f} seconds\n' \
#                 'Normal took {1:.05f} seconds\n'.format(t1, t2)

#     def test_pool_decode_spec4000(self):
#         spec3 = self.Run[5]
#         spec4 = self.Run[5]
#         paramsMZ = spec3._get_encoding_parameters('m/z array')
#         paramsMZ += ('mz',)
#         paramsI = spec3._get_encoding_parameters('intensity array')
#         paramsI += ('i',)

#         s = time.time()
#         self.Decoder.pool_decode([paramsMZ, paramsI], spec3._register)
#         t1 = time.time() - s
#         peaks3 = spec3.peaks

#         s = time.time()
#         peaks4 = list(zip(spec4.mz, spec4.i))
#         t2 = time.time() - s
#         self.assertPeaksIdentical(peaks3, peaks4)

#         assert t1 < t2, 'parallel version is slower than normal version:\n' \
#                 'Parallel took {0:.5f} seconds\n' \
#                 'Normal took {1:.05f} seconds\n'.format(t1, t2)

#     def test_big_parallel_array(self):
#         arr = np.asarray([x for x in range(1000000)], dtype=np.float64)
#         dec = pnp.MSNumpress([])
#         enc_np = dec.encode_linear(arr, dec.optimal_linear_fixed_point(arr))
#         enc_np_zlib = zlib.compress(enc_np)
#         enc_np_zlib_b64 = b64enc(enc_np_zlib)
#         comp = ['zlib', 'MS-Numpress linear prediction compression']
#         params = [
#             (enc_np_zlib_b64, comp, 100000, '32-bit float', 'i'),
#             (enc_np_zlib_b64, comp, 100000, '32-bit float', 'mz')
#         ]
#         s = time.time()
#         self.Decoder.pool_decode(params, lambda x,y :print(x,y))
#         t1 = time.time() - s

#         s = time.time()
#         d_type, decoded = decoder._decode(*params[0])
#         d_type, decoded = decoder._decode(*params[1])
#         t2 = time.time() - s
#         print(t1, t2)
#         assert t1 < t2

if __name__ == "__main__":
    unittest.main(verbosity=3)
