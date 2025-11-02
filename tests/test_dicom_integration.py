"""Tests for DICOM integration via CsaHeader.from_dicom() method."""

from __future__ import annotations

from unittest import TestCase

import pydicom

from csa_header.header import CsaHeader
from tests.fixtures import (
    DWI_CSA_IMAGE_HEADER_INFO,
    E11_CSA_SERIES_HEADER_INFO,
    RSFMRI_CSA_SERIES_HEADER_INFO,
)


class FromDicomValidationTestCase(TestCase):
    """Tests for CsaHeader.from_dicom() parameter validation."""

    def test_invalid_csa_type_raises_valueerror(self):
        """Test that invalid csa_type parameter raises ValueError."""
        # Create a real DICOM dataset (Mock doesn't work well with 'in' operator)
        dcm = pydicom.Dataset()

        # Test with various truly invalid csa_type values
        invalid_types = ["invalid", "image_header", "series_header", "both", "data", "header"]
        for invalid_type in invalid_types:
            with self.subTest(csa_type=invalid_type):
                with self.assertRaises(ValueError) as cm:
                    CsaHeader.from_dicom(dcm, invalid_type)
                self.assertIn("Invalid csa_type", str(cm.exception))
                self.assertIn(invalid_type, str(cm.exception))

    def test_valid_csa_types_accepted(self):
        """Test that valid csa_type parameters are accepted."""
        # Create an empty DICOM dataset (no CSA headers)
        dcm = pydicom.Dataset()

        # These should not raise ValueError (they return None because tag is missing)
        valid_types = ["image", "series", "IMAGE", "SERIES", "Image", "Series"]
        for valid_type in valid_types:
            with self.subTest(csa_type=valid_type):
                result = CsaHeader.from_dicom(dcm, valid_type)
                # Should return None (tag not present), not raise ValueError
                self.assertIsNone(result)


class FromDicomMissingDataTestCase(TestCase):
    """Tests for CsaHeader.from_dicom() with missing CSA data."""

    def test_returns_none_when_tag_missing(self):
        """Test that None is returned when CSA tag is not present."""
        # Create an empty DICOM dataset without CSA tags
        dcm = pydicom.Dataset()

        # Test for both image and series types
        for csa_type in ["image", "series"]:
            with self.subTest(csa_type=csa_type):
                result = CsaHeader.from_dicom(dcm, csa_type)
                self.assertIsNone(result)

    def test_returns_none_when_value_is_none(self):
        """Test that None is returned when tag exists but value is None."""
        # Create a DICOM dataset with tag present but value is None
        dcm = pydicom.Dataset()
        dcm.add_new((0x0029, 0x1010), "OB", None)

        result = CsaHeader.from_dicom(dcm, "image")
        self.assertIsNone(result)

    def test_returns_none_for_empty_dataset(self):
        """Test that None is returned for completely empty DICOM dataset."""
        # Create an empty pydicom Dataset
        dcm = pydicom.Dataset()

        # Should return None for both types
        self.assertIsNone(CsaHeader.from_dicom(dcm, "image"))
        self.assertIsNone(CsaHeader.from_dicom(dcm, "series"))


class FromDicomExtractionTestCase(TestCase):
    """Tests for CsaHeader.from_dicom() CSA header extraction."""

    def test_extracts_image_header(self):
        """Test extracting image CSA header from DICOM dataset."""
        # Load test CSA image header data
        with open(DWI_CSA_IMAGE_HEADER_INFO, "rb") as f:
            csa_bytes = f.read()

        # Create a mock DICOM dataset with image CSA header
        dcm = pydicom.Dataset()
        # Add the CSA Image Header Info tag (0x0029, 0x1010)
        dcm.add_new((0x0029, 0x1010), "OB", csa_bytes)

        # Extract using from_dicom()
        csa_header = CsaHeader.from_dicom(dcm, "image")

        # Verify we got a CsaHeader instance
        self.assertIsNotNone(csa_header)
        self.assertIsInstance(csa_header, CsaHeader)
        self.assertEqual(csa_header.raw, csa_bytes)

    def test_extracts_series_header(self):
        """Test extracting series CSA header from DICOM dataset."""
        # Load test CSA series header data
        with open(E11_CSA_SERIES_HEADER_INFO, "rb") as f:
            csa_bytes = f.read()

        # Create a mock DICOM dataset with series CSA header
        dcm = pydicom.Dataset()
        # Add the CSA Series Header Info tag (0x0029, 0x1020)
        dcm.add_new((0x0029, 0x1020), "OB", csa_bytes)

        # Extract using from_dicom()
        csa_header = CsaHeader.from_dicom(dcm, "series")

        # Verify we got a CsaHeader instance
        self.assertIsNotNone(csa_header)
        self.assertIsInstance(csa_header, CsaHeader)
        self.assertEqual(csa_header.raw, csa_bytes)

    def test_case_insensitive_csa_type(self):
        """Test that csa_type parameter is case-insensitive."""
        # Load test data
        with open(DWI_CSA_IMAGE_HEADER_INFO, "rb") as f:
            csa_bytes = f.read()

        dcm = pydicom.Dataset()
        dcm.add_new((0x0029, 0x1010), "OB", csa_bytes)

        # Test various case combinations
        for csa_type in ["image", "IMAGE", "Image", "ImAgE"]:
            with self.subTest(csa_type=csa_type):
                result = CsaHeader.from_dicom(dcm, csa_type)
                self.assertIsNotNone(result)
                self.assertEqual(result.raw, csa_bytes)


class FromDicomReadEquivalenceTestCase(TestCase):
    """Tests verifying from_dicom() produces same results as manual extraction."""

    def test_image_header_equivalence(self):
        """Test that from_dicom() for image header matches manual extraction."""
        # Load test data
        with open(DWI_CSA_IMAGE_HEADER_INFO, "rb") as f:
            csa_bytes = f.read()

        # Create DICOM dataset
        dcm = pydicom.Dataset()
        dcm.add_new((0x0029, 0x1010), "OB", csa_bytes)

        # Method 1: from_dicom()
        csa_from_dicom = CsaHeader.from_dicom(dcm, "image")
        self.assertIsNotNone(csa_from_dicom)
        result_from_dicom = csa_from_dicom.read()

        # Method 2: Manual extraction
        raw_csa = dcm[(0x0029, 0x1010)].value
        csa_manual = CsaHeader(raw_csa)
        result_manual = csa_manual.read()

        # Verify both methods produce identical results
        self.assertEqual(result_from_dicom.keys(), result_manual.keys())
        for key in result_from_dicom:
            self.assertEqual(
                result_from_dicom[key],
                result_manual[key],
                f"Mismatch for tag '{key}'",
            )

    def test_series_header_equivalence(self):
        """Test that from_dicom() for series header matches manual extraction."""
        # Load test data
        with open(RSFMRI_CSA_SERIES_HEADER_INFO, "rb") as f:
            csa_bytes = f.read()

        # Create DICOM dataset
        dcm = pydicom.Dataset()
        dcm.add_new((0x0029, 0x1020), "OB", csa_bytes)

        # Method 1: from_dicom()
        csa_from_dicom = CsaHeader.from_dicom(dcm, "series")
        self.assertIsNotNone(csa_from_dicom)
        result_from_dicom = csa_from_dicom.read()

        # Method 2: Manual extraction
        raw_csa = dcm[(0x0029, 0x1020)].value
        csa_manual = CsaHeader(raw_csa)
        result_manual = csa_manual.read()

        # Verify both methods produce identical results
        self.assertEqual(len(result_from_dicom), len(result_manual))
        self.assertEqual(result_from_dicom.keys(), result_manual.keys())


class FromDicomBothHeadersTestCase(TestCase):
    """Tests for DICOM datasets containing both image and series headers."""

    def test_extract_both_headers_independently(self):
        """Test extracting both image and series headers from same dataset."""
        # Load both test data files
        with open(DWI_CSA_IMAGE_HEADER_INFO, "rb") as f:
            image_bytes = f.read()
        with open(E11_CSA_SERIES_HEADER_INFO, "rb") as f:
            series_bytes = f.read()

        # Create DICOM dataset with both headers
        dcm = pydicom.Dataset()
        dcm.add_new((0x0029, 0x1010), "OB", image_bytes)
        dcm.add_new((0x0029, 0x1020), "OB", series_bytes)

        # Extract image header
        csa_image = CsaHeader.from_dicom(dcm, "image")
        self.assertIsNotNone(csa_image)
        self.assertEqual(csa_image.raw, image_bytes)

        # Extract series header
        csa_series = CsaHeader.from_dicom(dcm, "series")
        self.assertIsNotNone(csa_series)
        self.assertEqual(csa_series.raw, series_bytes)

        # Verify they're different
        self.assertNotEqual(csa_image.raw, csa_series.raw)

        # Verify both can be parsed
        image_dict = csa_image.read()
        series_dict = csa_series.read()
        self.assertIsInstance(image_dict, dict)
        self.assertIsInstance(series_dict, dict)
        self.assertGreater(len(image_dict), 0)
        self.assertGreater(len(series_dict), 0)


class CsaTagsConstantTestCase(TestCase):
    """Tests for CSA_TAGS class constant."""

    def test_csa_tags_contains_image(self):
        """Test that CSA_TAGS contains 'image' mapping."""
        self.assertIn("image", CsaHeader.CSA_TAGS)
        self.assertEqual(CsaHeader.CSA_TAGS["image"], (0x0029, 0x1010))

    def test_csa_tags_contains_series(self):
        """Test that CSA_TAGS contains 'series' mapping."""
        self.assertIn("series", CsaHeader.CSA_TAGS)
        self.assertEqual(CsaHeader.CSA_TAGS["series"], (0x0029, 0x1020))

    def test_csa_tags_only_has_two_entries(self):
        """Test that CSA_TAGS contains exactly two entries."""
        self.assertEqual(len(CsaHeader.CSA_TAGS), 2)

    def test_csa_tags_is_dict(self):
        """Test that CSA_TAGS is a dictionary."""
        self.assertIsInstance(CsaHeader.CSA_TAGS, dict)


class ExtractCsaBytesTestCase(TestCase):
    """Tests for _extract_csa_bytes() static method."""

    def test_extracts_bytes_when_present(self):
        """Test that _extract_csa_bytes extracts bytes when tag is present."""
        with open(DWI_CSA_IMAGE_HEADER_INFO, "rb") as f:
            expected_bytes = f.read()

        dcm = pydicom.Dataset()
        dcm.add_new((0x0029, 0x1010), "OB", expected_bytes)

        result = CsaHeader._extract_csa_bytes(dcm, "image")
        self.assertEqual(result, expected_bytes)

    def test_returns_none_when_tag_missing(self):
        """Test that _extract_csa_bytes returns None when tag is missing."""
        dcm = pydicom.Dataset()

        result = CsaHeader._extract_csa_bytes(dcm, "image")
        self.assertIsNone(result)

    def test_returns_none_when_value_is_none(self):
        """Test that _extract_csa_bytes returns None when value is None."""
        dcm = pydicom.Dataset()
        dcm.add_new((0x0029, 0x1010), "OB", None)

        result = CsaHeader._extract_csa_bytes(dcm, "image")
        self.assertIsNone(result)

    def test_converts_to_bytes(self):
        """Test that _extract_csa_bytes returns bytes type."""
        test_data = b"test_csa_data"
        dcm = pydicom.Dataset()
        dcm.add_new((0x0029, 0x1010), "OB", test_data)

        result = CsaHeader._extract_csa_bytes(dcm, "image")
        self.assertIsInstance(result, bytes)
