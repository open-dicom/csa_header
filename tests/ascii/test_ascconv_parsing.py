from unittest import TestCase

from csa_header.ascii.ascconv import parse_ascconv, parse_ascconv_text
from tests.ascii.fixtures import PARSED_ELEMENTS, RAW_ELEMENTS
from tests.fixtures import RSFMRI_CSA_SERIES_HEADER_INFO


class CsaParsingTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RSFMRI_CSA_SERIES_HEADER_INFO, "rb") as f:
            cls.series_header_info = f.read()
        cls.csa_data, cls.first_line_info = parse_ascconv(cls.series_header_info.decode("ISO-8859-1"), delimiter='""')

    def test_key_and_value_ordered(self):
        first_key = "ulVersion"
        first_value = 51130001
        found_keys = list(self.csa_data)
        self.assertEqual(found_keys[0], first_key)
        self.assertEqual(self.csa_data[found_keys[0]], first_value)

    def test_nested_value(self):
        self.assertEqual(
            self.csa_data["sGRADSPEC"]["asGPAData"][0]["sEddyCompensationY"]["aflTimeConstant"][1],
            0.917683601379,
        )

    def test_parse_fragment(self):
        out = parse_ascconv_text(RAW_ELEMENTS)
        self.assertEqual(out, PARSED_ELEMENTS)
