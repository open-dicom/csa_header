"""Tests for XA Enhanced DICOM support (Issue #31)."""

from __future__ import annotations

from unittest import TestCase

import pydicom

from csa_header.ascii import CsaAsciiHeader
from csa_header.header import CsaHeader
from tests.fixtures import XA30_SAMPLE_DICOM, XA60_SAMPLE_DICOM


class XAEnhancedDetectionTestCase(TestCase):
    """Tests for XA Enhanced DICOM format detection."""

    def setUp(self):
        """Load XA Enhanced DICOM test files."""
        self.xa30_dcm = pydicom.dcmread(XA30_SAMPLE_DICOM)
        self.xa60_dcm = pydicom.dcmread(XA60_SAMPLE_DICOM)

    def test_xa30_has_shared_functional_groups_sequence(self):
        """Test that XA30 DICOM has SharedFunctionalGroupsSequence."""
        self.assertIn("SharedFunctionalGroupsSequence", self.xa30_dcm)

    def test_xa60_has_shared_functional_groups_sequence(self):
        """Test that XA60 DICOM has SharedFunctionalGroupsSequence."""
        self.assertIn("SharedFunctionalGroupsSequence", self.xa60_dcm)

    def test_xa30_does_not_have_standard_csa_tags(self):
        """Test that XA30 DICOM does not have standard CSA tags."""
        self.assertNotIn((0x0029, 0x1010), self.xa30_dcm)
        self.assertNotIn((0x0029, 0x1020), self.xa30_dcm)

    def test_xa60_does_not_have_standard_csa_tags(self):
        """Test that XA60 DICOM does not have standard CSA tags."""
        self.assertNotIn((0x0029, 0x1010), self.xa60_dcm)
        self.assertNotIn((0x0029, 0x1020), self.xa60_dcm)

    def test_xa30_has_xprotocol_data(self):
        """Test that XA30 DICOM has XProtocol data in the expected location."""
        sds = self.xa30_dcm.SharedFunctionalGroupsSequence[0]
        self.assertIn((0x0021, 0x10FE), sds)

        mrprot_seq = sds[(0x0021, 0x10FE)]
        self.assertIsNotNone(mrprot_seq.value)
        self.assertGreater(len(mrprot_seq.value), 0)

        mrprot_item = mrprot_seq.value[0]
        self.assertIn((0x0021, 0x1019), mrprot_item)

        protocol_data = mrprot_item[(0x0021, 0x1019)].value
        self.assertIsNotNone(protocol_data)
        self.assertIsInstance(protocol_data, bytes)

    def test_xa60_has_xprotocol_data(self):
        """Test that XA60 DICOM has XProtocol data in the expected location."""
        sds = self.xa60_dcm.SharedFunctionalGroupsSequence[0]
        self.assertIn((0x0021, 0x10FE), sds)

        mrprot_seq = sds[(0x0021, 0x10FE)]
        mrprot_item = mrprot_seq.value[0]
        self.assertIn((0x0021, 0x1019), mrprot_item)

        protocol_data = mrprot_item[(0x0021, 0x1019)].value
        self.assertIsNotNone(protocol_data)


class XAEnhancedExtractionTestCase(TestCase):
    """Tests for XA Enhanced XProtocol data extraction."""

    def setUp(self):
        """Load XA Enhanced DICOM test files."""
        self.xa30_dcm = pydicom.dcmread(XA30_SAMPLE_DICOM)
        self.xa60_dcm = pydicom.dcmread(XA60_SAMPLE_DICOM)

    def test_extract_xa_enhanced_protocol_xa30(self):
        """Test extracting XProtocol from XA30 DICOM."""
        protocol = CsaHeader._extract_xa_enhanced_protocol(self.xa30_dcm)
        self.assertIsNotNone(protocol)
        self.assertIsInstance(protocol, bytes)
        self.assertGreater(len(protocol), 0)

        # Check that it starts with XProtocol marker
        self.assertTrue(protocol.startswith(b"<XProtocol>"))

    def test_extract_xa_enhanced_protocol_xa60(self):
        """Test extracting XProtocol from XA60 DICOM."""
        protocol = CsaHeader._extract_xa_enhanced_protocol(self.xa60_dcm)
        self.assertIsNotNone(protocol)
        self.assertIsInstance(protocol, bytes)
        self.assertGreater(len(protocol), 0)
        self.assertTrue(protocol.startswith(b"<XProtocol>"))

    def test_extract_xa_enhanced_protocol_returns_none_for_standard_dicom(self):
        """Test that extraction returns None for non-XA Enhanced DICOMs."""
        # Create a minimal DICOM dataset without SharedFunctionalGroupsSequence
        standard_dcm = pydicom.Dataset()
        result = CsaHeader._extract_xa_enhanced_protocol(standard_dcm)
        self.assertIsNone(result)


class XAEnhancedFromDicomTestCase(TestCase):
    """Tests for CsaHeader.from_dicom() with XA Enhanced DICOMs."""

    def setUp(self):
        """Load XA Enhanced DICOM test files."""
        self.xa30_dcm = pydicom.dcmread(XA30_SAMPLE_DICOM)
        self.xa60_dcm = pydicom.dcmread(XA60_SAMPLE_DICOM)

    def test_from_dicom_xa30_returns_csa_ascii_header(self):
        """Test that from_dicom returns CsaAsciiHeader for XA30 files."""
        result = CsaHeader.from_dicom(self.xa30_dcm, "image")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CsaAsciiHeader)

    def test_from_dicom_xa60_returns_csa_ascii_header(self):
        """Test that from_dicom returns CsaAsciiHeader for XA60 files."""
        result = CsaHeader.from_dicom(self.xa60_dcm, "image")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CsaAsciiHeader)

    def test_from_dicom_xa30_with_series_type(self):
        """Test from_dicom with 'series' type for XA30 (should still work)."""
        # XA Enhanced stores protocol in one place, type is ignored
        result = CsaHeader.from_dicom(self.xa30_dcm, "series")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CsaAsciiHeader)

    def test_from_dicom_xa60_with_series_type(self):
        """Test from_dicom with 'series' type for XA60 (should still work)."""
        result = CsaHeader.from_dicom(self.xa60_dcm, "series")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CsaAsciiHeader)


class XAEnhancedParsingTestCase(TestCase):
    """Tests for parsing XA Enhanced XProtocol data."""

    def setUp(self):
        """Load and extract XA Enhanced headers."""
        self.xa30_dcm = pydicom.dcmread(XA30_SAMPLE_DICOM)
        self.xa60_dcm = pydicom.dcmread(XA60_SAMPLE_DICOM)

        self.xa30_header = CsaHeader.from_dicom(self.xa30_dcm, "image")
        self.xa60_header = CsaHeader.from_dicom(self.xa60_dcm, "image")

    def test_xa30_parsing_succeeds(self):
        """Test that XA30 XProtocol data can be parsed."""
        self.assertIsNotNone(self.xa30_header)
        parsed = self.xa30_header.parsed
        self.assertIsInstance(parsed, dict)
        self.assertGreater(len(parsed), 0)

    def test_xa60_parsing_succeeds(self):
        """Test that XA60 XProtocol data can be parsed."""
        self.assertIsNotNone(self.xa60_header)
        parsed = self.xa60_header.parsed
        self.assertIsInstance(parsed, dict)
        self.assertGreater(len(parsed), 0)

    def test_xa30_parsed_contains_expected_keys(self):
        """Test that XA30 parsed data contains expected protocol keys."""
        parsed = self.xa30_header.parsed

        # Check for common protocol parameters
        self.assertIn("sSliceArray", parsed)
        self.assertIsInstance(parsed["sSliceArray"], dict)
        self.assertIn("lSize", parsed["sSliceArray"])

    def test_xa60_parsed_contains_expected_keys(self):
        """Test that XA60 parsed data contains expected protocol keys."""
        parsed = self.xa60_header.parsed
        self.assertIn("sSliceArray", parsed)
        self.assertIsInstance(parsed["sSliceArray"], dict)

    def test_xa30_slice_array_data(self):
        """Test accessing specific XA30 protocol data."""
        parsed = self.xa30_header.parsed
        slice_array = parsed["sSliceArray"]

        # Check that we can access nested data
        self.assertIn("lSize", slice_array)
        self.assertIsInstance(slice_array["lSize"], (int, float))
        self.assertGreaterEqual(slice_array["lSize"], 1)

    def test_xa60_slice_array_data(self):
        """Test accessing specific XA60 protocol data."""
        parsed = self.xa60_header.parsed
        slice_array = parsed["sSliceArray"]

        self.assertIn("lSize", slice_array)
        self.assertIsInstance(slice_array["lSize"], (int, float))


class XAEnhancedIssue31RegressionTestCase(TestCase):
    """Regression tests for Issue #31."""

    def setUp(self):
        """Set up test data matching Issue #31 example."""
        self.dcm = pydicom.dcmread(XA30_SAMPLE_DICOM)

    def test_issue_31_example_code_does_not_raise(self):
        """
        Test that the example code from Issue #31 now works.

        Original error:
        CsaReadError: CSA element #0 has an invalid check bit value: 1632648224!
        """
        # This is the approach from Issue #31
        sds = self.dcm.SharedFunctionalGroupsSequence[0]
        mrprot = sds[(0x0021, 0x10FE)][0][(0x0021, 0x1019)]

        # Using CsaHeader directly on the value should fail (it's XProtocol, not CSA)
        # But using from_dicom should work
        header = CsaHeader.from_dicom(self.dcm, "image")
        self.assertIsNotNone(header)

        # Should return CsaAsciiHeader which can parse XProtocol
        self.assertIsInstance(header, CsaAsciiHeader)

        # Should be able to parse without error
        parsed = header.parsed
        self.assertIsInstance(parsed, dict)
        self.assertGreater(len(parsed), 0)

    def test_issue_31_direct_xprotocol_parsing(self):
        """Test that we can parse XProtocol data directly with CsaAsciiHeader."""
        sds = self.dcm.SharedFunctionalGroupsSequence[0]
        xprotocol_data = sds[(0x0021, 0x10FE)][0][(0x0021, 0x1019)].value

        # This should work now
        header = CsaAsciiHeader(xprotocol_data)
        parsed = header.parsed

        self.assertIsInstance(parsed, dict)
        self.assertGreater(len(parsed), 0)
        self.assertIn("sSliceArray", parsed)


class XAEnhancedBackwardCompatibilityTestCase(TestCase):
    """Tests to ensure XA Enhanced support doesn't break existing functionality."""

    def test_from_dicom_still_validates_csa_type(self):
        """Test that invalid csa_type still raises ValueError."""
        dcm = pydicom.dcmread(XA30_SAMPLE_DICOM)

        with self.assertRaises(ValueError) as cm:
            CsaHeader.from_dicom(dcm, "invalid_type")

        self.assertIn("Invalid csa_type", str(cm.exception))

    def test_from_dicom_returns_none_for_empty_dicom(self):
        """Test that from_dicom returns None for DICOM without CSA or XProtocol."""
        empty_dcm = pydicom.Dataset()
        result = CsaHeader.from_dicom(empty_dcm, "image")
        self.assertIsNone(result)
