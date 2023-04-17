from unittest import TestCase

from csa_header.header import CsaHeader
from tests.fixtures import DWI_CSA_IMAGE_HEADER_INFO

TEST_DWI_HEADER_SIZE: int = 12964


class CsaHeaderTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DWI_CSA_IMAGE_HEADER_INFO, "rb") as f:
            cls.raw_csa = f.read()
        cls.csa = CsaHeader(cls.raw_csa)

    def test_init_stores_raw(self):
        self.assertEqual(self.csa.raw, self.raw_csa)

    def test_header_size(self):
        self.assertEqual(self.csa.header_size, TEST_DWI_HEADER_SIZE)

    def test_check_csa_type(self):
        value = self.csa.check_csa_type()
        expected = CsaHeader.CSA_TYPE_2
        self.assertEqual(value, expected)
