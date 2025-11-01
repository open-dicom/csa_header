"""Integration tests validating README examples execute correctly.

These tests ensure that code examples in README.md work as documented,
without cluttering the documentation with doctest directives. Each test
corresponds to a specific example section in the README.

This addresses issue #14: validating example usage without the overhead
of doctests.
"""

from __future__ import annotations

from unittest import TestCase

import pytest

try:
    import pydicom

    PYDICOM_AVAILABLE = True
except ImportError:
    PYDICOM_AVAILABLE = False


class TestQuickstartExample(TestCase):
    """Validate the README quickstart example (lines 96-113)."""

    @pytest.mark.skipif(not PYDICOM_AVAILABLE, reason="Requires pydicom")
    def test_quickstart_with_example_data(self):
        """Test the main quickstart example from README.

        This validates the code at README lines 96-113:
        - Using fetch_example_dicom()
        - Reading DICOM with pydicom
        - Extracting CSA Series Header (0x29, 0x1020)
        - Parsing with CsaHeader
        """
        # Import inside test to handle missing dependencies
        from csa_header import CsaHeader
        from csa_header.examples import POOCH_AVAILABLE, fetch_example_dicom

        if not POOCH_AVAILABLE:
            pytest.skip("Requires pooch for example data")

        # This mirrors the exact code in README quickstart
        dicom_path = fetch_example_dicom()
        dcm = pydicom.dcmread(dicom_path)

        # Parse CSA Series Header
        raw_csa = dcm[(0x29, 0x1020)].value
        parsed_csa = CsaHeader(raw_csa).read()

        # Validate structure and content (flexible assertions, not exact output)
        self.assertIsInstance(parsed_csa, dict)
        self.assertGreater(len(parsed_csa), 70, "Should have more than 70 CSA tags")
        self.assertIn("MrPhoenixProtocol", parsed_csa, "Should contain MrPhoenixProtocol")

    @pytest.mark.skipif(not PYDICOM_AVAILABLE, reason="Requires pydicom")
    def test_tag_count_reasonable(self):
        """Test that the parsed CSA has a reasonable number of tags.

        README shows len(parsed_csa) == 79, but this may vary slightly
        with different example files. We test for a reasonable range.
        """
        from csa_header import CsaHeader
        from csa_header.examples import POOCH_AVAILABLE, fetch_example_dicom

        if not POOCH_AVAILABLE:
            pytest.skip("Requires pooch for example data")

        dicom_path = fetch_example_dicom()
        dcm = pydicom.dcmread(dicom_path)
        raw_csa = dcm[(0x29, 0x1020)].value
        parsed_csa = CsaHeader(raw_csa).read()

        # Should have between 70-100 tags for a typical Siemens MPRAGE
        tag_count = len(parsed_csa)
        self.assertGreaterEqual(tag_count, 70)
        self.assertLessEqual(tag_count, 100)


class TestASCCONVProtocolExample(TestCase):
    """Validate the ASCCONV protocol extraction example (README lines 175-184)."""

    @pytest.mark.skipif(not PYDICOM_AVAILABLE, reason="Requires pydicom")
    def test_ascconv_protocol_extraction(self):
        """Test ASCCONV protocol extraction example from README.

        This validates the code at README lines 175-184:
        - Extracting MrPhoenixProtocol from parsed CSA
        - Accessing nested protocol parameters
        """
        from csa_header import CsaHeader
        from csa_header.examples import POOCH_AVAILABLE, fetch_example_dicom

        if not POOCH_AVAILABLE:
            pytest.skip("Requires pooch for example data")

        dicom_path = fetch_example_dicom()
        dcm = pydicom.dcmread(dicom_path)
        raw_csa = dcm[(0x29, 0x1020)].value
        parsed_csa = CsaHeader(raw_csa).read()

        # Test protocol extraction
        protocol = parsed_csa.get("MrPhoenixProtocol")
        self.assertIsNotNone(protocol, "MrPhoenixProtocol should exist")
        self.assertIn("value", protocol)

        # ASCCONV should be parsed as a dictionary
        ascconv = protocol["value"]
        self.assertIsInstance(ascconv, dict, "ASCCONV should be parsed as dict")

    @pytest.mark.skipif(not PYDICOM_AVAILABLE, reason="Requires pydicom")
    def test_ascconv_protocol_structure(self):
        """Test that ASCCONV protocol contains expected structure.

        The README example shows accessing alTR[0] and alTE[0].
        We test that the protocol has typical parameters.
        """
        from csa_header import CsaHeader
        from csa_header.examples import POOCH_AVAILABLE, fetch_example_dicom

        if not POOCH_AVAILABLE:
            pytest.skip("Requires pooch for example data")

        dicom_path = fetch_example_dicom()
        dcm = pydicom.dcmread(dicom_path)
        raw_csa = dcm[(0x29, 0x1020)].value
        parsed_csa = CsaHeader(raw_csa).read()

        protocol = parsed_csa.get("MrPhoenixProtocol")
        ascconv = protocol["value"]

        # ASCCONV should contain common protocol parameters
        # Note: specific parameters like alTR/alTE depend on the sequence type
        # We test for structural elements that should be present
        self.assertIsInstance(ascconv, dict)
        self.assertGreater(len(ascconv), 10, "ASCCONV should contain multiple parameters")

        # Check for presence of typical ASCCONV keys
        # ulVersion is a common protocol version identifier
        typical_keys = ["ulVersion", "tProtocolName", "sProtConsistencyInfo"]
        found_keys = [key for key in typical_keys if key in ascconv]
        self.assertGreater(
            len(found_keys),
            0,
            f"ASCCONV should contain at least one typical key: {typical_keys}",
        )


class TestAPIUsageExample(TestCase):
    """Validate general API usage patterns from README."""

    @pytest.mark.skipif(not PYDICOM_AVAILABLE, reason="Requires pydicom")
    def test_basic_csa_header_workflow(self):
        """Test the basic workflow: raw bytes -> CsaHeader -> parsed dict.

        This validates the core API usage pattern shown throughout README.
        """
        from csa_header import CsaHeader
        from csa_header.examples import POOCH_AVAILABLE, fetch_example_dicom

        if not POOCH_AVAILABLE:
            pytest.skip("Requires pooch for example data")

        # 1. Get DICOM file
        dicom_path = fetch_example_dicom()
        dcm = pydicom.dcmread(dicom_path)

        # 2. Extract raw CSA bytes
        raw_csa = dcm[(0x29, 0x1020)].value
        self.assertIsInstance(raw_csa, bytes)
        self.assertGreater(len(raw_csa), 0)

        # 3. Parse with CsaHeader
        csa = CsaHeader(raw_csa)
        self.assertIsInstance(csa, CsaHeader)

        # 4. Read parsed structure
        parsed = csa.read()
        self.assertIsInstance(parsed, dict)

        # 5. Verify each tag has expected structure
        for tag_name, tag_data in parsed.items():
            self.assertIsInstance(tag_name, str)
            self.assertIsInstance(tag_data, dict)
            self.assertIn("VR", tag_data)
            self.assertIn("VM", tag_data)
            self.assertIn("value", tag_data)

    @pytest.mark.skipif(not PYDICOM_AVAILABLE, reason="Requires pydicom")
    def test_both_csa_headers_can_be_parsed(self):
        """Test that both CSA Image and Series headers can be parsed.

        README shows examples with both (0x29, 0x1010) and (0x29, 0x1020).
        """
        from csa_header import CsaHeader
        from csa_header.examples import POOCH_AVAILABLE, fetch_example_dicom

        if not POOCH_AVAILABLE:
            pytest.skip("Requires pooch for example data")

        dicom_path = fetch_example_dicom()
        dcm = pydicom.dcmread(dicom_path)

        # Test CSA Series Header (0x29, 0x1020)
        if (0x29, 0x1020) in dcm:
            raw_series = dcm[(0x29, 0x1020)].value
            series_csa = CsaHeader(raw_series).read()
            self.assertIsInstance(series_csa, dict)
            self.assertGreater(len(series_csa), 0)

        # Test CSA Image Header (0x29, 0x1010) if present
        if (0x29, 0x1010) in dcm:
            raw_image = dcm[(0x29, 0x1010)].value
            image_csa = CsaHeader(raw_image).read()
            self.assertIsInstance(image_csa, dict)
            self.assertGreater(len(image_csa), 0)


class TestExampleDataIntegration(TestCase):
    """Test that the example data infrastructure works as documented."""

    def test_fetch_example_dicom_returns_valid_path(self):
        """Test that fetch_example_dicom() returns a valid file path."""
        from csa_header.examples import POOCH_AVAILABLE, fetch_example_dicom

        if not POOCH_AVAILABLE:
            pytest.skip("Requires pooch for example data")

        dicom_path = fetch_example_dicom()

        # Should return a string path
        self.assertIsInstance(dicom_path, str)

        # Path should exist
        from pathlib import Path

        self.assertTrue(Path(dicom_path).exists())
        self.assertTrue(Path(dicom_path).is_file())

    @pytest.mark.skipif(not PYDICOM_AVAILABLE, reason="Requires pydicom")
    def test_example_file_is_siemens_dicom(self):
        """Test that the example file is a valid Siemens DICOM."""
        from csa_header.examples import POOCH_AVAILABLE, fetch_example_dicom

        if not POOCH_AVAILABLE:
            pytest.skip("Requires pooch for example data")

        dicom_path = fetch_example_dicom()
        dcm = pydicom.dcmread(dicom_path)

        # Should be a Siemens file
        self.assertTrue(hasattr(dcm, "Manufacturer"))
        self.assertIn("SIEMENS", dcm.Manufacturer.upper())

        # Should have CSA headers
        has_csa = (0x29, 0x1010) in dcm or (0x29, 0x1020) in dcm
        self.assertTrue(has_csa, "Example file should contain CSA headers")

    def test_example_file_metadata_accessible(self):
        """Test that example file metadata is accessible without downloading."""
        from csa_header.examples import get_example_info

        # Should work without pooch installed
        info = get_example_info()

        self.assertIsInstance(info, dict)
        self.assertIn("name", info)
        self.assertIn("checksum", info)
        self.assertIn("url", info)
        self.assertIn("doi", info)

        # Verify it's the documented example
        self.assertEqual(info["doi"], "10.5281/zenodo.17482132")
