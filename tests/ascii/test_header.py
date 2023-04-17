from pathlib import Path
from unittest import TestCase

from csa_header.header import CsaAsciiHeader
from tests.fixtures import E11_CSA_SERIES_HEADER_INFO, RSFMRI_CSA_SERIES_HEADER_INFO


class CsaAsciiHeaderTestCase(TestCase):
    slice_array_size = 64
    CSA_FILE: Path = RSFMRI_CSA_SERIES_HEADER_INFO

    def setUp(self):
        with open(self.CSA_FILE, "rb") as f:
            self.series_header_info = f.read()
        self.ascii_header = CsaAsciiHeader(self.series_header_info)

    def test_init_prepares_cached_variables(self):
        fresh_header = CsaAsciiHeader(self.series_header_info)
        self.assertEqual(fresh_header._parsed, {})

    def test_parse_returns_dict(self):
        parsed = self.ascii_header.parse()
        self.assertIsInstance(parsed, dict)

    def test_parse_results_for_nested_dict_value(self):
        parsed = self.ascii_header.parse()
        value = parsed["sSliceArray"]["lSize"]
        self.assertEqual(self.slice_array_size, value)
        k_space_slice_resolution = 1
        value = parsed["sKSpace"]["dSliceResolution"]
        self.assertEqual(k_space_slice_resolution, value)

    def test_parse_results_for_nested_list_value(self):
        parsed = self.ascii_header.parse()
        value = parsed["sCoilSelectMeas"]["aRxCoilSelectData"]
        self.assertIsInstance(value, list)
        self.assertEqual(len(value), 2)

    def test_parsed_property(self):
        self.assertIsInstance(self.ascii_header.parsed, dict)
        self.assertIs(self.ascii_header.parsed, self.ascii_header.parsed)

    def test_n_slices_property(self):
        result = self.ascii_header.n_slices
        expected = self.ascii_header.parsed["sSliceArray"]["lSize"]
        self.assertEqual(result, expected)


class CsaAsciiHeaderVE11CTestCase(CsaAsciiHeaderTestCase):
    CSA_FILE: Path = E11_CSA_SERIES_HEADER_INFO
    slice_array_size = 3
