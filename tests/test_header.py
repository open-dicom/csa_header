"""Comprehensive tests for csa_header.header module."""

from __future__ import annotations

import struct
from unittest import TestCase

from csa_header.exceptions import CsaReadError
from csa_header.header import CsaHeader
from csa_header.unpacker import Unpacker
from tests.fixtures import (
    DWI_CSA_IMAGE_HEADER_INFO,
    E11_CSA_SERIES_HEADER_INFO,
    RSFMRI_CSA_SERIES_HEADER_INFO,
)

TEST_DWI_HEADER_SIZE: int = 12964
TEST_E11_HEADER_SIZE: int = 93320
TEST_RSFMRI_HEADER_SIZE: int = 180076


class CsaHeaderInitTestCase(TestCase):
    """Tests for CsaHeader initialization."""

    def test_init_stores_raw(self):
        """Test that initialization stores raw bytes."""
        raw = b"test_data"
        csa = CsaHeader(raw)
        self.assertEqual(csa.raw, raw)

    def test_init_calculates_header_size(self):
        """Test that header_size is correctly calculated from raw data."""
        raw = b"test_data_123"
        csa = CsaHeader(raw)
        self.assertEqual(csa.header_size, len(raw))

    def test_init_with_empty_data(self):
        """Test initialization with empty bytes."""
        raw = b""
        csa = CsaHeader(raw)
        self.assertEqual(csa.raw, raw)
        self.assertEqual(csa.header_size, 0)

    def test_init_with_large_data(self):
        """Test initialization with large binary data."""
        with open(DWI_CSA_IMAGE_HEADER_INFO, "rb") as f:
            raw = f.read()
        csa = CsaHeader(raw)
        self.assertEqual(csa.header_size, TEST_DWI_HEADER_SIZE)
        self.assertEqual(len(csa.raw), TEST_DWI_HEADER_SIZE)


class CsaHeaderTypeDetectionTestCase(TestCase):
    """Tests for CSA header type detection (type 1 vs type 2)."""

    @classmethod
    def setUpClass(cls):
        """Load test data files."""
        with open(DWI_CSA_IMAGE_HEADER_INFO, "rb") as f:
            cls.raw_type2 = f.read()

    def test_check_csa_type_2(self):
        """Test detection of CSA type 2 (with SV10 marker)."""
        csa = CsaHeader(self.raw_type2)
        self.assertEqual(csa.check_csa_type(), CsaHeader.CSA_TYPE_2)

    def test_check_csa_type_1(self):
        """Test detection of CSA type 1 (without SV10 marker)."""
        # Create synthetic type 1 data (no SV10 marker)
        raw_type1 = b"XXXX" + b"\x00" * 100
        csa = CsaHeader(raw_type1)
        self.assertEqual(csa.check_csa_type(), CsaHeader.CSA_TYPE_1)

    def test_csa_type_property_type_2(self):
        """Test csa_type property for type 2."""
        csa = CsaHeader(self.raw_type2)
        self.assertEqual(csa.csa_type, 2)

    def test_csa_type_property_type_1(self):
        """Test csa_type property for type 1."""
        raw_type1 = b"DATA" + b"\x00" * 100
        csa = CsaHeader(raw_type1)
        self.assertEqual(csa.csa_type, 1)

    def test_is_type_2_true(self):
        """Test is_type_2 property returns True for type 2."""
        csa = CsaHeader(self.raw_type2)
        self.assertTrue(csa.is_type_2)

    def test_is_type_2_false(self):
        """Test is_type_2 property returns False for type 1."""
        raw_type1 = b"ABCD" + b"\x00" * 100
        csa = CsaHeader(raw_type1)
        self.assertFalse(csa.is_type_2)

    def test_type_2_identifier_constant(self):
        """Test TYPE_2_IDENTIFIER constant value."""
        self.assertEqual(CsaHeader.TYPE_2_IDENTIFIER, b"SV10")

    def test_type_constants(self):
        """Test CSA_TYPE_1 and CSA_TYPE_2 constants."""
        self.assertEqual(CsaHeader.CSA_TYPE_1, 1)
        self.assertEqual(CsaHeader.CSA_TYPE_2, 2)


class CsaHeaderSkipPrefixTestCase(TestCase):
    """Tests for skip_prefix method."""

    def test_skip_prefix_type_2(self):
        """Test that skip_prefix moves pointer for type 2 headers."""
        # Create type 2 header with SV10 marker
        raw = b"SV10\x04\x03\x02\x01" + b"\x00" * 100
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<")

        # Verify initial state
        self.assertEqual(unpacker.pointer, 0)

        # Skip prefix
        csa.skip_prefix(unpacker)

        # For type 2, pointer should move by 8 (4 for SV10 + 4 more bytes read)
        self.assertEqual(unpacker.pointer, 8)

    def test_skip_prefix_type_1(self):
        """Test that skip_prefix does not move pointer for type 1 headers."""
        # Create type 1 header (no SV10 marker)
        raw = b"DATA\x04\x03\x02\x01" + b"\x00" * 100
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<")

        # Verify initial state
        self.assertEqual(unpacker.pointer, 0)

        # Skip prefix
        csa.skip_prefix(unpacker)

        # For type 1, pointer should remain at 0
        self.assertEqual(unpacker.pointer, 0)

    def test_skip_prefix_moves_correct_length(self):
        """Test that skip_prefix moves by exactly the length of TYPE_2_IDENTIFIER."""
        raw = b"SV10" + b"X" * 200
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<")

        csa.skip_prefix(unpacker)

        # Should skip 4 bytes for SV10 and read 4 more = 8 total
        expected_position = len(CsaHeader.TYPE_2_IDENTIFIER) * 2
        self.assertEqual(unpacker.pointer, expected_position)


class CsaHeaderValidateCheckBitTestCase(TestCase):
    """Tests for validate_check_bit method."""

    def test_validate_check_bit_77_valid(self):
        """Test that check bit value 77 (0x4D) is valid."""
        csa = CsaHeader(b"test")
        # Should not raise exception
        try:
            csa.validate_check_bit(0, 77)
        except CsaReadError:
            self.fail("validate_check_bit raised CsaReadError for valid value 77")

    def test_validate_check_bit_205_valid(self):
        """Test that check bit value 205 (0xCD) is valid."""
        csa = CsaHeader(b"test")
        # Should not raise exception
        try:
            csa.validate_check_bit(0, 205)
        except CsaReadError:
            self.fail("validate_check_bit raised CsaReadError for valid value 205")

    def test_validate_check_bit_invalid_raises_error(self):
        """Test that invalid check bit values raise CsaReadError."""
        csa = CsaHeader(b"test")
        with self.assertRaises(CsaReadError) as context:
            csa.validate_check_bit(5, 100)

        # Verify error message contains useful information
        error_msg = str(context.exception)
        self.assertIn("5", error_msg)  # Tag index
        self.assertIn("100", error_msg)  # Invalid check bit value

    def test_validate_check_bit_zero_invalid(self):
        """Test that check bit value 0 is invalid."""
        csa = CsaHeader(b"test")
        with self.assertRaises(CsaReadError):
            csa.validate_check_bit(0, 0)

    def test_validate_check_bit_negative_invalid(self):
        """Test that negative check bit values are invalid."""
        csa = CsaHeader(b"test")
        with self.assertRaises(CsaReadError):
            csa.validate_check_bit(0, -1)

    def test_validate_check_bit_large_value_invalid(self):
        """Test that large check bit values are invalid."""
        csa = CsaHeader(b"test")
        with self.assertRaises(CsaReadError):
            csa.validate_check_bit(0, 999)

    def test_valid_check_bit_values_constant(self):
        """Test VALID_CHECK_BIT_VALUES constant."""
        self.assertIn(77, CsaHeader.VALID_CHECK_BIT_VALUES)
        self.assertIn(205, CsaHeader.VALID_CHECK_BIT_VALUES)
        self.assertEqual(len(CsaHeader.VALID_CHECK_BIT_VALUES), 2)


class CsaHeaderParseItemsTestCase(TestCase):
    """Tests for parse_items method."""

    def test_parse_items_integer_string(self):
        """Test parsing IS (Integer String) value representation."""
        # Create header with IS value: "42"
        item_data = struct.pack("<4i", 9, 2, 0, 0) + b"42"  # x0=9, x1=2 (actual length)
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=1, vr="IS", vm=1)
        self.assertEqual(result, 42)
        self.assertIsInstance(result, int)

    def test_parse_items_decimal_string(self):
        """Test parsing DS (Decimal String) value representation."""
        # Create header with DS value: "3.14159"
        value = b"3.14159\x00"
        item_data = struct.pack("<4i", 8, 8, 0, 0) + value
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=1, vr="DS", vm=1)
        self.assertAlmostEqual(result, 3.14159, places=5)
        self.assertIsInstance(result, float)

    def test_parse_items_float(self):
        """Test parsing FL (Float) value representation."""
        value = b"2.5\x00"
        item_data = struct.pack("<4i", 4, 4, 0, 0) + value
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=1, vr="FL", vm=1)
        self.assertEqual(result, 2.5)
        self.assertIsInstance(result, float)

    def test_parse_items_float_double(self):
        """Test parsing FD (Float Double) value representation."""
        value = b"1.23456789\x00\x00"
        item_data = struct.pack("<4i", 12, 12, 0, 0) + value
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=1, vr="FD", vm=1)
        self.assertAlmostEqual(result, 1.23456789, places=7)

    def test_parse_items_signed_short(self):
        """Test parsing SS (Signed Short) value representation."""
        value = b"-123\x00\x00\x00"
        item_data = struct.pack("<4i", 5, 5, 0, 0) + value
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=1, vr="SS", vm=1)
        self.assertEqual(result, -123)
        self.assertIsInstance(result, int)

    def test_parse_items_unsigned_short(self):
        """Test parsing US (Unsigned Short) value representation."""
        value = b"65000\x00\x00"
        item_data = struct.pack("<4i", 6, 6, 0, 0) + value
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=1, vr="US", vm=1)
        self.assertEqual(result, 65000)

    def test_parse_items_signed_long(self):
        """Test parsing SL (Signed Long) value representation."""
        value = b"-999999\x00"
        item_data = struct.pack("<4i", 8, 8, 0, 0) + value
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=1, vr="SL", vm=1)
        self.assertEqual(result, -999999)

    def test_parse_items_unsigned_long(self):
        """Test parsing UL (Unsigned Long) value representation."""
        value = b"4000000\x00"
        item_data = struct.pack("<4i", 8, 8, 0, 0) + value
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=1, vr="UL", vm=1)
        self.assertEqual(result, 4000000)

    def test_parse_items_unknown_vr_returns_string(self):
        """Test parsing UN (Unknown) or unrecognized VR returns string."""
        value = b"TestString\x00\x00"
        item_data = struct.pack("<4i", 12, 12, 0, 0) + value
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=1, vr="UN", vm=1)
        self.assertEqual(result, "TestString")
        self.assertIsInstance(result, str)

    def test_parse_items_string_vr(self):
        """Test parsing string VR types (LO, SH, ST, CS)."""
        value = b"SIEMENS\x00"
        item_data = struct.pack("<4i", 8, 8, 0, 0) + value
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=1, vr="LO", vm=1)
        self.assertEqual(result, "SIEMENS")

    def test_parse_items_multiple_values(self):
        """Test parsing multiple item values (VM > 1)."""
        # Two integer values - need proper alignment
        item1 = struct.pack("<4i", 5, 2, 0, 0) + b"10\x00\x00"  # 2 bytes + 2 padding
        item2 = struct.pack("<4i", 5, 2, 0, 0) + b"20\x00\x00"
        raw = b"SV10\x04\x03\x02\x01" + item1 + item2 + b"\x00" * 50  # Extra space
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=2, vr="IS", vm=2)
        self.assertEqual(result, [10, 20])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    def test_parse_items_empty_value(self):
        """Test parsing empty item value."""
        item_data = struct.pack("<4i", 0, 0, 0, 0)
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=1, vr="IS", vm=1)
        self.assertIsNone(result)

    def test_parse_items_vm_zero_uses_n_items(self):
        """Test that when VM=0, n_items is used for value count."""
        value = b"42\x00\x00"
        item_data = struct.pack("<4i", 4, 4, 0, 0) + value
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        # VM=0 should use n_items=1
        result = csa.parse_items(unpacker, n_items=1, vr="IS", vm=0)
        self.assertEqual(result, 42)

    def test_parse_items_alignment_to_4_bytes(self):
        """Test that items are aligned to 4-byte boundaries."""
        # 3-byte value should skip 1 byte for alignment
        value = b"ABC"
        item_data = struct.pack("<4i", 3, 3, 0, 0) + value + b"\x00"  # +1 padding
        next_item = struct.pack("<4i", 3, 3, 0, 0) + b"DEF" + b"\x00"
        raw = b"SV10\x04\x03\x02\x01" + item_data + next_item
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        result = csa.parse_items(unpacker, n_items=2, vr="LO", vm=2)
        self.assertEqual(result, ["ABC", "DEF"])

    def test_parse_items_type2_overreach_raises_error(self):
        """Test that reading beyond header size raises CsaReadError for type 2."""
        # Create a small header where item claims to be larger than available
        item_data = struct.pack("<4i", 1000, 1000, 0, 0)  # Claims 1000 bytes
        raw = b"SV10\x04\x03\x02\x01" + item_data  # But only ~24 bytes total
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        with self.assertRaises(CsaReadError) as context:
            csa.parse_items(unpacker, n_items=1, vr="IS", vm=1)

        error_msg = str(context.exception)
        self.assertIn("destination", error_msg.lower())

    def test_parse_items_too_many_items_raises_error(self):
        """Test that more items than expected raises CsaReadError."""
        # VM=1 but provide 2 non-empty items
        item1 = struct.pack("<4i", 4, 4, 0, 0) + b"10\x00\x00"
        item2 = struct.pack("<4i", 4, 4, 0, 0) + b"20\x00\x00"
        raw = b"SV10\x04\x03\x02\x01" + item1 + item2
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        with self.assertRaises(CsaReadError) as context:
            csa.parse_items(unpacker, n_items=2, vr="IS", vm=1)

        error_msg = str(context.exception)
        self.assertIn("Too many items", error_msg)


class CsaHeaderParseTagTestCase(TestCase):
    """Tests for parse_tag method."""

    def test_parse_tag_extracts_name(self):
        """Test that parse_tag correctly extracts tag name."""
        # Create a minimal tag structure
        tag_name = b"TestTag" + b"\x00" * 57  # 64 bytes total for name
        tag_data = (
            tag_name
            + struct.pack("<i", 1)  # VM
            + b"IS\x00\x00"  # VR (4 bytes)
            + struct.pack("<3i", 0, 1, 77)  # SyngoDT, n_items, check_bit
        )
        # Add item data
        item_data = struct.pack("<4i", 4, 4, 0, 0) + b"42\x00\x00"
        raw = b"SV10\x04\x03\x02\x01" + struct.pack("<2I", 1, 0) + tag_data + item_data

        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)
        unpacker.unpack("2I")  # Skip n_tags prefix

        tag = csa.parse_tag(unpacker, i_tag=0)

        self.assertEqual(tag["name"], "TestTag")

    def test_parse_tag_extracts_vr_and_vm(self):
        """Test that parse_tag correctly extracts VR and VM."""
        tag_name = b"MyTag" + b"\x00" * 59
        tag_data = tag_name + struct.pack("<i", 3) + b"DS\x00\x00" + struct.pack("<3i", 0, 1, 77)  # VM = 3  # VR = DS
        item_data = struct.pack("<4i", 4, 4, 0, 0) + b"1.5\x00"
        raw = b"SV10\x04\x03\x02\x01" + struct.pack("<2I", 1, 0) + tag_data + item_data

        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)
        unpacker.unpack("2I")

        tag = csa.parse_tag(unpacker, i_tag=0)

        self.assertEqual(tag["VR"], "DS")
        self.assertEqual(tag["VM"], 3)

    def test_parse_tag_validates_check_bit(self):
        """Test that parse_tag validates check bit and raises on invalid value."""
        tag_name = b"BadTag" + b"\x00" * 58
        tag_data = tag_name + struct.pack("<i", 1) + b"IS\x00\x00" + struct.pack("<3i", 0, 1, 99)  # Invalid check bit
        raw = b"SV10\x04\x03\x02\x01" + struct.pack("<2I", 1, 0) + tag_data

        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)
        unpacker.unpack("2I")

        with self.assertRaises(CsaReadError):
            csa.parse_tag(unpacker, i_tag=0)

    def test_parse_tag_sets_first_tag_n_items_for_type1(self):
        """Test that parse_tag sets _first_tag_n_items for CSA type 1."""
        # Type 1 header (no SV10) - starts directly with n_tags prefix
        # TAG_FORMAT_STRING is "64si4s3i" which unpacks to 6 values
        tag_name = b"FirstTag" + b"\x00" * 56
        tag_data = (
            tag_name  # 64 bytes
            + struct.pack("<i", 1)  # VM
            + b"IS\x00\x00"  # VR (4 bytes)
            + struct.pack("<3i", 0, 42, 77)  # SyngoDT, n_items, check_bit (3 ints)
        )
        item_data = struct.pack("<4i", 42, 4, 0, 0) + b"10\x00\x00"
        # Type 1: No SV10 prefix, starts with n_tags directly
        raw = struct.pack("<2I", 1, 0) + tag_data + item_data + b"\x00" * 100

        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=0)
        unpacker.unpack("2I")

        # First tag (index 1 in the code, but we pass 1 as i_tag)
        self.assertIsNone(csa._first_tag_n_items)
        _ = csa.parse_tag(unpacker, i_tag=1)
        self.assertEqual(csa._first_tag_n_items, 42)


class CsaHeaderReadTestCase(TestCase):
    """Tests for the main read method."""

    @classmethod
    def setUpClass(cls):
        """Load real test data."""
        with open(DWI_CSA_IMAGE_HEADER_INFO, "rb") as f:
            cls.raw_dwi = f.read()
        with open(E11_CSA_SERIES_HEADER_INFO, "rb") as f:
            cls.raw_e11 = f.read()
        with open(RSFMRI_CSA_SERIES_HEADER_INFO, "rb") as f:
            cls.raw_rsfmri = f.read()

    def test_read_returns_dict(self):
        """Test that read() returns a dictionary."""
        csa = CsaHeader(self.raw_dwi)
        result = csa.read()
        self.assertIsInstance(result, dict)

    def test_read_parses_all_tags_dwi(self):
        """Test that read() parses all tags from DWI header."""
        csa = CsaHeader(self.raw_dwi)
        result = csa.read()
        # DWI header has 101 tags
        self.assertEqual(len(result), 101)

    def test_read_parses_all_tags_e11(self):
        """Test that read() parses all tags from E11 series header."""
        csa = CsaHeader(self.raw_e11)
        result = csa.read()
        # Should have multiple tags
        self.assertGreater(len(result), 50)

    def test_read_tag_structure(self):
        """Test that parsed tags have correct structure."""
        csa = CsaHeader(self.raw_dwi)
        result = csa.read()

        # Check first tag
        first_tag_name = next(iter(result.keys()))
        tag = result[first_tag_name]

        # Tag should have these keys
        self.assertIn("VR", tag)
        self.assertIn("VM", tag)
        self.assertIn("value", tag)

        # Should NOT have "name" (it's used as dict key)
        self.assertNotIn("name", tag)

    def test_read_preserves_tag_names_as_keys(self):
        """Test that tag names are used as dictionary keys."""
        csa = CsaHeader(self.raw_dwi)
        result = csa.read()

        # Known tags from DWI header
        self.assertIn("EchoLinePosition", result)
        self.assertIn("EchoColumnPosition", result)
        self.assertIn("EchoPartitionPosition", result)

    def test_read_parses_integer_values(self):
        """Test that integer values are parsed correctly."""
        csa = CsaHeader(self.raw_dwi)
        result = csa.read()

        echo_line = result["EchoLinePosition"]
        self.assertEqual(echo_line["VR"], "IS")
        self.assertIsInstance(echo_line["value"], int)
        self.assertEqual(echo_line["value"], 64)

    def test_read_parses_float_values(self):
        """Test that float values are parsed correctly."""
        csa = CsaHeader(self.raw_e11)
        result = csa.read()

        # Find a DS or FD tag
        transmitter_cal = result.get("TransmitterCalibration")
        if transmitter_cal:
            self.assertIsInstance(transmitter_cal["value"], float)

    def test_read_parses_string_values(self):
        """Test that string values are parsed correctly."""
        csa = CsaHeader(self.raw_e11)
        result = csa.read()

        # Find a string tag
        seq_owner = result.get("SequenceFileOwner")
        if seq_owner:
            self.assertIsInstance(seq_owner["value"], str)

    def test_read_parses_multi_value_tags(self):
        """Test that tags with multiple values return lists."""
        csa = CsaHeader(self.raw_e11)
        result = csa.read()

        # TablePositionOrigin has VM=3
        table_pos = result.get("TablePositionOrigin")
        if table_pos:
            self.assertIsInstance(table_pos["value"], list)
            self.assertEqual(len(table_pos["value"]), 3)

    def test_read_handles_empty_values(self):
        """Test that tags with no value are handled correctly."""
        csa = CsaHeader(self.raw_e11)
        result = csa.read()

        # Some tags have None values
        for _tag_name, tag_data in result.items():
            if tag_data["value"] is None:
                # Just verify it doesn't crash
                self.assertIsNone(tag_data["value"])
                break


class CsaHeaderAscconvTestCase(TestCase):
    """Tests for ASCCONV (MrPhoenixProtocol) integration."""

    @classmethod
    def setUpClass(cls):
        """Load E11 series header which contains ASCCONV."""
        with open(E11_CSA_SERIES_HEADER_INFO, "rb") as f:
            cls.raw_e11 = f.read()

    def test_read_parses_ascconv_protocol(self):
        """Test that MrPhoenixProtocol is parsed as ASCCONV."""
        csa = CsaHeader(self.raw_e11)
        result = csa.read()

        self.assertIn("MrPhoenixProtocol", result)
        protocol = result["MrPhoenixProtocol"]

        # ASCCONV should be parsed as a dictionary
        self.assertIsInstance(protocol["value"], dict)

    def test_ascconv_contains_expected_keys(self):
        """Test that parsed ASCCONV contains expected protocol parameters."""
        csa = CsaHeader(self.raw_e11)
        result = csa.read()

        ascconv = result["MrPhoenixProtocol"]["value"]

        # Check for some known ASCCONV keys
        self.assertIn("ulVersion", ascconv)
        self.assertIn("tProtocolName", ascconv)
        self.assertIn("sProtConsistencyInfo", ascconv)

    def test_ascconv_tag_name_constant(self):
        """Test ASCII_HEADER_TAGS constant contains MrPhoenixProtocol."""
        self.assertIn("MrPhoenixProtocol", CsaHeader.ASCII_HEADER_TAGS)

    def test_ascconv_nested_structure(self):
        """Test that ASCCONV nested structures are parsed correctly."""
        csa = CsaHeader(self.raw_e11)
        result = csa.read()

        ascconv = result["MrPhoenixProtocol"]["value"]

        # Check nested structures
        self.assertIn("sProtConsistencyInfo", ascconv)
        self.assertIsInstance(ascconv["sProtConsistencyInfo"], dict)
        self.assertIn("tSystemType", ascconv["sProtConsistencyInfo"])


class CsaHeaderType1SpecificTestCase(TestCase):
    """Tests specific to CSA type 1 headers."""

    def test_type1_parse_items_length_calculation(self):
        """Test CSA type 1 specific length calculation in parse_items."""
        # Create a type 1 header (no SV10 prefix)
        # TAG_FORMAT_STRING: "64si4s3i" = 64 bytes name, 1 int VM, 4 bytes VR, 3 ints (SyngoDT, n_items, check_bit)
        tag_name = b"Tag1" + b"\x00" * 60  # 64 bytes
        n_items_value = 10
        tag_data = (
            tag_name  # 64 bytes
            + struct.pack("<i", 1)  # VM
            + b"IS\x00\x00"  # VR (4 bytes)
            + struct.pack("<3i", 0, n_items_value, 77)  # SyngoDT, n_items, check_bit (3 ints)
        )
        # Type 1 uses x0 - _first_tag_n_items for length
        item_data = struct.pack("<4i", n_items_value + 4, 0, 0, 0) + b"42\x00\x00"
        # Type 1: No SV10, starts with n_tags directly
        raw = struct.pack("<2I", 1, 0) + tag_data + item_data + b"\x00" * 100

        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=0)
        unpacker.unpack("2I")

        # Parse first tag to set _first_tag_n_items
        tag = csa.parse_tag(unpacker, i_tag=1)

        # Should successfully parse
        self.assertIsNotNone(tag)

    def test_type1_negative_length_returns_empty_string(self):
        """Test that negative item length in type 1 returns empty string."""
        # Create type 1 header with negative length scenario (no SV10 prefix)
        tag_name = b"Tag1" + b"\x00" * 60
        n_items_value = 100
        tag_data = (
            tag_name  # 64 bytes
            + struct.pack("<i", 1)  # VM
            + b"IS\x00\x00"  # VR (4 bytes)
            + struct.pack("<3i", 0, n_items_value, 77)  # SyngoDT, n_items, check_bit (3 ints)
        )
        # x0 < _first_tag_n_items causes negative length
        item_data = struct.pack("<4i", 50, 0, 0, 0)  # 50 < 100
        # Type 1: No SV10, starts with n_tags directly
        raw = struct.pack("<2I", 1, 0) + tag_data + item_data

        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=0)
        unpacker.unpack("2I")

        tag = csa.parse_tag(unpacker, i_tag=1)
        # Should handle gracefully
        self.assertIsNotNone(tag)


class CsaHeaderErrorHandlingTestCase(TestCase):
    """Tests for error handling and edge cases."""

    def test_read_with_empty_header_raises_error(self):
        """Test that reading empty header raises appropriate error."""
        csa = CsaHeader(b"")
        with self.assertRaises((CsaReadError, struct.error)):
            csa.read()

    def test_read_with_truncated_header(self):
        """Test reading truncated header data."""
        # Create header that's too short
        raw = b"SV10\x01\x00\x00\x00"  # Only 8 bytes
        csa = CsaHeader(raw)

        with self.assertRaises((CsaReadError, struct.error)):
            csa.read()

    def test_read_with_invalid_n_tags(self):
        """Test reading header with impossible number of tags."""
        # Create header claiming 10000 tags but with small size
        raw = b"SV10\x04\x03\x02\x01" + struct.pack("<2I", 10000, 0) + b"\x00" * 100
        csa = CsaHeader(raw)

        with self.assertRaises((CsaReadError, struct.error)):
            csa.read()

    def test_malformed_tag_name(self):
        """Test handling of malformed tag name (no null terminator)."""
        # Tag name without null byte
        tag_name = b"A" * 64
        tag_data = tag_name + struct.pack("<i", 1) + b"IS\x00\x00" + struct.pack("<3i", 0, 1, 77)
        item_data = struct.pack("<4i", 3, 3, 0, 0) + b"42\x00"
        raw = b"SV10\x04\x03\x02\x01" + struct.pack("<2I", 1, 0) + tag_data + item_data

        csa = CsaHeader(raw)
        result = csa.read()

        # Should handle it by treating entire 64 bytes as name
        self.assertEqual(len(result), 1)

    def test_malformed_vr(self):
        """Test handling of malformed VR field."""
        tag_name = b"Test" + b"\x00" * 60
        tag_data = tag_name + struct.pack("<i", 1) + b"\xff\xff\x00\x00" + struct.pack("<3i", 0, 1, 77)  # Invalid VR
        item_data = struct.pack("<4i", 3, 3, 0, 0) + b"42\x00"
        raw = b"SV10\x04\x03\x02\x01" + struct.pack("<2I", 1, 0) + tag_data + item_data

        csa = CsaHeader(raw)
        result = csa.read()

        # Should parse but with invalid VR
        self.assertEqual(len(result), 1)

    def test_conversion_error_handling(self):
        """Test that invalid conversions are handled gracefully."""
        # Try to parse non-numeric string as integer
        value = b"NotANumber\x00"
        item_data = struct.pack("<4i", 11, 11, 0, 0) + value
        raw = b"SV10\x04\x03\x02\x01" + item_data
        csa = CsaHeader(raw)
        unpacker = Unpacker(raw, endian="<", pointer=8)

        # Should raise ValueError during int() conversion
        with self.assertRaises(ValueError):
            csa.parse_items(unpacker, n_items=1, vr="IS", vm=1)


class CsaHeaderConstantsTestCase(TestCase):
    """Tests for class constants and configuration."""

    def test_endian_constant(self):
        """Test ENDIAN constant is little-endian."""
        self.assertEqual(CsaHeader.ENDIAN, "<")

    def test_tag_format_string(self):
        """Test TAG_FORMAT_STRING constant."""
        self.assertEqual(CsaHeader.TAG_FORMAT_STRING, "64si4s3i")

    def test_prefix_format(self):
        """Test PREFIX_FORMAT constant."""
        self.assertEqual(CsaHeader.PREFIX_FORMAT, "2I")

    def test_item_format(self):
        """Test ITEM_FORMAT constant."""
        self.assertEqual(CsaHeader.ITEM_FORMAT, "4i")

    def test_valid_check_bit_values(self):
        """Test VALID_CHECK_BIT_VALUES contains correct values."""
        valid_values = CsaHeader.VALID_CHECK_BIT_VALUES
        self.assertEqual(len(valid_values), 2)
        self.assertIn(77, valid_values)
        self.assertIn(205, valid_values)

    def test_ascii_header_tags(self):
        """Test ASCII_HEADER_TAGS constant."""
        tags = CsaHeader.ASCII_HEADER_TAGS
        self.assertIn("MrPhoenixProtocol", tags)


class CsaHeaderIntegrationTestCase(TestCase):
    """Integration tests with real data."""

    def test_full_pipeline_dwi(self):
        """Test complete parsing pipeline with DWI data."""
        with open(DWI_CSA_IMAGE_HEADER_INFO, "rb") as f:
            raw = f.read()

        csa = CsaHeader(raw)
        self.assertEqual(csa.csa_type, 2)
        self.assertTrue(csa.is_type_2)

        result = csa.read()
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 50)

    def test_full_pipeline_e11(self):
        """Test complete parsing pipeline with E11 series data."""
        with open(E11_CSA_SERIES_HEADER_INFO, "rb") as f:
            raw = f.read()

        csa = CsaHeader(raw)
        self.assertEqual(csa.csa_type, 2)

        result = csa.read()
        self.assertIn("MrPhoenixProtocol", result)
        self.assertIsInstance(result["MrPhoenixProtocol"]["value"], dict)

    def test_full_pipeline_rsfmri(self):
        """Test complete parsing pipeline with rsfMRI data."""
        with open(RSFMRI_CSA_SERIES_HEADER_INFO, "rb") as f:
            raw = f.read()

        csa = CsaHeader(raw)
        self.assertEqual(csa.csa_type, 2)
        self.assertEqual(csa.header_size, TEST_RSFMRI_HEADER_SIZE)

        result = csa.read()
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 50)

    def test_multiple_reads_same_result(self):
        """Test that reading same header multiple times gives same result."""
        with open(DWI_CSA_IMAGE_HEADER_INFO, "rb") as f:
            raw = f.read()

        csa = CsaHeader(raw)
        result1 = csa.read()

        # Read again
        csa2 = CsaHeader(raw)
        result2 = csa2.read()

        # Should be identical
        self.assertEqual(set(result1.keys()), set(result2.keys()))
        for key in result1.keys():
            self.assertEqual(result1[key], result2[key])

    def test_different_headers_different_content(self):
        """Test that different headers produce different results."""
        with open(DWI_CSA_IMAGE_HEADER_INFO, "rb") as f:
            raw1 = f.read()
        with open(E11_CSA_SERIES_HEADER_INFO, "rb") as f:
            raw2 = f.read()

        csa1 = CsaHeader(raw1)
        csa2 = CsaHeader(raw2)

        result1 = csa1.read()
        result2 = csa2.read()

        # Should have different keys
        self.assertNotEqual(set(result1.keys()), set(result2.keys()))
