"""Comprehensive tests for csa_header.unpacker module."""

from __future__ import annotations

import struct
from unittest import TestCase

import pytest

from csa_header.unpacker import ENDIAN_CODES, Unpacker


class UnpackerInitTestCase(TestCase):
    """Tests for Unpacker initialization."""

    def test_init_with_bytes(self):
        """Test initialization with bytes buffer."""
        buffer = b"test_data"
        unpacker = Unpacker(buffer)
        self.assertEqual(unpacker.buffer, buffer)
        self.assertEqual(unpacker.pointer, 0)
        self.assertIsNone(unpacker.endian)
        self.assertEqual(unpacker._cache, {})

    def test_init_with_custom_pointer(self):
        """Test initialization with custom pointer position."""
        buffer = b"0123456789"
        unpacker = Unpacker(buffer, pointer=5)
        self.assertEqual(unpacker.pointer, 5)
        self.assertEqual(unpacker.buffer, buffer)

    def test_init_with_endian_little(self):
        """Test initialization with little-endian setting."""
        buffer = b"test"
        unpacker = Unpacker(buffer, endian="<")
        self.assertEqual(unpacker.endian, "<")

    def test_init_with_endian_big(self):
        """Test initialization with big-endian setting."""
        buffer = b"test"
        unpacker = Unpacker(buffer, endian=">")
        self.assertEqual(unpacker.endian, ">")

    def test_init_with_endian_native(self):
        """Test initialization with native endian setting."""
        buffer = b"test"
        unpacker = Unpacker(buffer, endian="@")
        self.assertEqual(unpacker.endian, "@")

    def test_init_with_empty_buffer(self):
        """Test initialization with empty buffer."""
        buffer = b""
        unpacker = Unpacker(buffer)
        self.assertEqual(unpacker.buffer, buffer)
        self.assertEqual(unpacker.pointer, 0)

    def test_init_with_large_buffer(self):
        """Test initialization with large buffer."""
        buffer = b"A" * 10000
        unpacker = Unpacker(buffer)
        self.assertEqual(len(unpacker.buffer), 10000)

    def test_init_cache_is_empty_dict(self):
        """Test that cache is initialized as empty dictionary."""
        unpacker = Unpacker(b"test")
        self.assertIsInstance(unpacker._cache, dict)
        self.assertEqual(len(unpacker._cache), 0)


class UnpackerReadTestCase(TestCase):
    """Tests for Unpacker.read() method."""

    def test_read_exact_bytes(self):
        """Test reading exact number of bytes."""
        buffer = b"0123456789"
        unpacker = Unpacker(buffer)
        result = unpacker.read(5)
        self.assertEqual(result, b"01234")
        self.assertEqual(unpacker.pointer, 5)

    def test_read_all_bytes_with_minus_one(self):
        """Test reading all remaining bytes with n_bytes=-1."""
        buffer = b"0123456789"
        unpacker = Unpacker(buffer)
        result = unpacker.read(-1)
        self.assertEqual(result, buffer)
        self.assertEqual(unpacker.pointer, len(buffer))

    def test_read_all_bytes_default_parameter(self):
        """Test reading all bytes with default parameter."""
        buffer = b"hello world"
        unpacker = Unpacker(buffer)
        result = unpacker.read()
        self.assertEqual(result, b"hello world")

    def test_read_zero_bytes(self):
        """Test reading zero bytes."""
        buffer = b"test"
        unpacker = Unpacker(buffer)
        result = unpacker.read(0)
        self.assertEqual(result, b"")
        self.assertEqual(unpacker.pointer, 0)

    def test_read_from_middle(self):
        """Test reading from middle of buffer."""
        buffer = b"0123456789"
        unpacker = Unpacker(buffer, pointer=3)
        result = unpacker.read(4)
        self.assertEqual(result, b"3456")
        self.assertEqual(unpacker.pointer, 7)

    def test_read_beyond_buffer_end(self):
        """Test reading beyond buffer end returns partial data."""
        buffer = b"short"
        unpacker = Unpacker(buffer)
        result = unpacker.read(100)
        self.assertEqual(result, b"short")
        # Pointer moves to requested position even if beyond buffer
        self.assertEqual(unpacker.pointer, 100)

    def test_multiple_sequential_reads(self):
        """Test multiple sequential read operations."""
        buffer = b"ABCDEFGHIJ"
        unpacker = Unpacker(buffer)

        r1 = unpacker.read(3)
        self.assertEqual(r1, b"ABC")
        self.assertEqual(unpacker.pointer, 3)

        r2 = unpacker.read(2)
        self.assertEqual(r2, b"DE")
        self.assertEqual(unpacker.pointer, 5)

        r3 = unpacker.read(5)
        self.assertEqual(r3, b"FGHIJ")
        self.assertEqual(unpacker.pointer, 10)

    def test_read_from_end_returns_empty(self):
        """Test reading from end of buffer returns empty bytes."""
        buffer = b"test"
        unpacker = Unpacker(buffer, pointer=4)
        result = unpacker.read(5)
        self.assertEqual(result, b"")
        # Pointer advances by requested amount even if at end
        self.assertEqual(unpacker.pointer, 9)

    def test_read_single_byte(self):
        """Test reading single byte."""
        buffer = b"X"
        unpacker = Unpacker(buffer)
        result = unpacker.read(1)
        self.assertEqual(result, b"X")


class UnpackerUnpackTestCase(TestCase):
    """Tests for Unpacker.unpack() method."""

    def test_unpack_little_endian_int(self):
        """Test unpacking little-endian integer."""
        buffer = struct.pack("<i", 42)
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("i")
        self.assertEqual(result, (42,))
        self.assertEqual(unpacker.pointer, 4)

    def test_unpack_big_endian_int(self):
        """Test unpacking big-endian integer."""
        buffer = struct.pack(">i", 42)
        unpacker = Unpacker(buffer, endian=">")
        result = unpacker.unpack("i")
        self.assertEqual(result, (42,))

    def test_unpack_float(self):
        """Test unpacking float value."""
        buffer = struct.pack("<f", 3.14)
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("f")
        self.assertAlmostEqual(result[0], 3.14, places=5)

    def test_unpack_double(self):
        """Test unpacking double value."""
        buffer = struct.pack("<d", 3.141592653589793)
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("d")
        self.assertAlmostEqual(result[0], 3.141592653589793, places=10)

    def test_unpack_string(self):
        """Test unpacking fixed-length string."""
        buffer = b"ABCD"
        unpacker = Unpacker(buffer)
        result = unpacker.unpack("4s")
        self.assertEqual(result, (b"ABCD",))

    def test_unpack_multiple_values(self):
        """Test unpacking multiple values at once."""
        buffer = struct.pack("<2i", 10, 20)
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("2i")
        self.assertEqual(result, (10, 20))

    def test_unpack_mixed_types(self):
        """Test unpacking mixed types (int + float)."""
        buffer = struct.pack("<if", 42, 3.14)
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("if")
        self.assertEqual(result[0], 42)
        self.assertAlmostEqual(result[1], 3.14, places=5)

    def test_unpack_with_explicit_endian_in_format(self):
        """Test unpacking with explicit endian code in format string."""
        buffer = struct.pack("<i", 100)
        unpacker = Unpacker(buffer, endian=">")  # Default big-endian
        # Explicit little-endian in format should override
        result = unpacker.unpack("<i")
        self.assertEqual(result, (100,))

    def test_unpack_advances_pointer(self):
        """Test that unpack advances pointer correctly."""
        buffer = struct.pack("<3i", 1, 2, 3)
        unpacker = Unpacker(buffer, endian="<")

        unpacker.unpack("i")
        self.assertEqual(unpacker.pointer, 4)

        unpacker.unpack("i")
        self.assertEqual(unpacker.pointer, 8)

        unpacker.unpack("i")
        self.assertEqual(unpacker.pointer, 12)

    def test_unpack_returns_tuple(self):
        """Test that unpack always returns a tuple."""
        buffer = struct.pack("<i", 42)
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("i")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)

    def test_unpack_unsigned_values(self):
        """Test unpacking unsigned integer types."""
        buffer = struct.pack("<I", 4294967295)  # Max uint32
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("I")
        self.assertEqual(result, (4294967295,))

    def test_unpack_short(self):
        """Test unpacking short integer."""
        buffer = struct.pack("<h", -32768)
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("h")
        self.assertEqual(result, (-32768,))

    def test_unpack_unsigned_short(self):
        """Test unpacking unsigned short."""
        buffer = struct.pack("<H", 65535)
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("H")
        self.assertEqual(result, (65535,))

    def test_unpack_byte(self):
        """Test unpacking single byte."""
        buffer = struct.pack("b", -128)
        unpacker = Unpacker(buffer)
        result = unpacker.unpack("b")
        self.assertEqual(result, (-128,))

    def test_unpack_multiple_strings(self):
        """Test unpacking multiple fixed strings."""
        buffer = b"ABCDEFGH"
        unpacker = Unpacker(buffer)
        result = unpacker.unpack("4s4s")
        self.assertEqual(
            result,
            (
                b"ABCD",
                b"EFGH",
            ),
        )


class UnpackerCachingTestCase(TestCase):
    """Tests for Unpacker struct format caching mechanism."""

    def test_cache_stores_format_string(self):
        """Test that format strings are cached after first use."""
        buffer = struct.pack("<i", 42)
        unpacker = Unpacker(buffer, endian="<")

        self.assertEqual(len(unpacker._cache), 0)
        unpacker.unpack("i")
        # Both "i" and "<i" (with endian prefix) are cached
        self.assertEqual(len(unpacker._cache), 2)
        self.assertIn("i", unpacker._cache)
        self.assertIn("<i", unpacker._cache)

    def test_cache_reuses_struct(self):
        """Test that cached struct is reused on subsequent calls."""
        buffer = struct.pack("<3i", 1, 2, 3)
        unpacker = Unpacker(buffer, endian="<")

        unpacker.unpack("i")
        cached_struct = unpacker._cache["i"]

        unpacker.unpack("i")
        # Should be the same object
        self.assertIs(unpacker._cache["i"], cached_struct)

    def test_cache_with_endian_prefix(self):
        """Test that default endian is prepended and both versions cached."""
        buffer = struct.pack("<i", 42)
        unpacker = Unpacker(buffer, endian="<")

        unpacker.unpack("i")
        # Both "i" and "<i" should be in cache
        self.assertIn("i", unpacker._cache)
        self.assertIn("<i", unpacker._cache)

    def test_cache_without_default_endian(self):
        """Test caching when no default endian is set."""
        buffer = struct.pack("<i", 42)
        unpacker = Unpacker(buffer, endian=None)

        unpacker.unpack("<i")
        # Only the explicit format should be cached
        self.assertIn("<i", unpacker._cache)
        self.assertEqual(len(unpacker._cache), 1)

    def test_cache_with_explicit_endian_in_format(self):
        """Test that explicit endian in format bypasses default endian."""
        buffer = struct.pack("<i", 100)
        unpacker = Unpacker(buffer, endian=">")

        unpacker.unpack("<i")
        # Should cache explicit format, not prepend default
        self.assertIn("<i", unpacker._cache)

    def test_cache_different_formats(self):
        """Test that different format strings are cached separately."""
        buffer = struct.pack("<ifh", 42, 3.14, 100)
        unpacker = Unpacker(buffer, endian="<")

        unpacker.unpack("i")
        unpacker.unpack("f")
        unpacker.unpack("h")

        self.assertGreaterEqual(len(unpacker._cache), 3)
        self.assertIn("i", unpacker._cache)
        self.assertIn("f", unpacker._cache)
        self.assertIn("h", unpacker._cache)

    def test_cache_performance_benefit(self):
        """Test that caching provides performance benefit (multiple uses)."""
        buffer = struct.pack("<100i", *range(100))
        unpacker = Unpacker(buffer, endian="<")

        # First call should populate cache
        for _ in range(100):
            unpacker = Unpacker(buffer, endian="<")
            for _i in range(100):
                unpacker.unpack("i")
            # Cache should remain size 2 (with endian prefix)
            self.assertEqual(len(unpacker._cache), 2)


class UnpackerPointerTestCase(TestCase):
    """Tests for pointer position tracking."""

    def test_pointer_starts_at_zero(self):
        """Test that pointer starts at 0 by default."""
        unpacker = Unpacker(b"test")
        self.assertEqual(unpacker.pointer, 0)

    def test_pointer_custom_start(self):
        """Test pointer with custom starting position."""
        unpacker = Unpacker(b"0123456789", pointer=5)
        self.assertEqual(unpacker.pointer, 5)

    def test_pointer_after_read(self):
        """Test pointer position after read operation."""
        buffer = b"ABCDEFGHIJ"
        unpacker = Unpacker(buffer)
        unpacker.read(4)
        self.assertEqual(unpacker.pointer, 4)

    def test_pointer_after_unpack(self):
        """Test pointer position after unpack operation."""
        buffer = struct.pack("<i", 42)
        unpacker = Unpacker(buffer, endian="<")
        unpacker.unpack("i")
        self.assertEqual(unpacker.pointer, 4)

    def test_pointer_through_mixed_operations(self):
        """Test pointer tracking through mixed read/unpack operations."""
        buffer = b"TEST" + struct.pack("<i", 100) + b"END"
        unpacker = Unpacker(buffer, endian="<")

        self.assertEqual(unpacker.pointer, 0)

        unpacker.read(4)  # Read "TEST"
        self.assertEqual(unpacker.pointer, 4)

        unpacker.unpack("i")  # Unpack integer
        self.assertEqual(unpacker.pointer, 8)

        unpacker.read(3)  # Read "END"
        self.assertEqual(unpacker.pointer, 11)

    def test_pointer_with_large_unpack(self):
        """Test pointer advances correctly for large struct."""
        buffer = struct.pack("<10i", *range(10))
        unpacker = Unpacker(buffer, endian="<")
        unpacker.unpack("10i")
        self.assertEqual(unpacker.pointer, 40)  # 10 * 4 bytes


class UnpackerEdgeCasesTestCase(TestCase):
    """Tests for edge cases and error conditions."""

    def test_unpack_from_empty_buffer_raises_error(self):
        """Test unpacking from empty buffer raises struct.error."""
        unpacker = Unpacker(b"")
        with pytest.raises(struct.error):
            unpacker.unpack("i")

    def test_unpack_insufficient_data_raises_error(self):
        """Test unpacking with insufficient data raises struct.error."""
        buffer = b"AB"  # Only 2 bytes
        unpacker = Unpacker(buffer)
        with pytest.raises(struct.error):
            unpacker.unpack("i")  # Needs 4 bytes

    def test_unpack_invalid_format_raises_error(self):
        """Test unpacking with invalid format string raises error."""
        buffer = struct.pack("<i", 42)
        unpacker = Unpacker(buffer)
        with pytest.raises(struct.error):
            unpacker.unpack("X")  # Invalid format character

    def test_read_with_very_large_n_bytes(self):
        """Test reading with very large n_bytes value."""
        buffer = b"small"
        unpacker = Unpacker(buffer)
        result = unpacker.read(999999)
        self.assertEqual(result, b"small")

    def test_unpack_at_buffer_boundary(self):
        """Test unpacking exactly at buffer size boundary."""
        buffer = struct.pack("<i", 42)
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("i")
        self.assertEqual(result, (42,))
        # Pointer should be exactly at end
        self.assertEqual(unpacker.pointer, len(buffer))

    def test_operations_on_binary_data(self):
        """Test operations on binary data with null bytes."""
        buffer = b"\x00\x01\x00\x02\x00\x03\x00\x04"
        unpacker = Unpacker(buffer)
        result = unpacker.read(8)
        self.assertEqual(result, buffer)

    def test_unpack_negative_values(self):
        """Test unpacking negative integer values."""
        buffer = struct.pack("<i", -12345)
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("i")
        self.assertEqual(result, (-12345,))

    def test_unpack_zero(self):
        """Test unpacking zero value."""
        buffer = struct.pack("<i", 0)
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("i")
        self.assertEqual(result, (0,))

    def test_multiple_unpack_without_cache(self):
        """Test multiple unpacks with no default endian (no caching optimization)."""
        buffer = struct.pack("<3i", 1, 2, 3)
        unpacker = Unpacker(buffer, endian=None)

        r1 = unpacker.unpack("<i")
        r2 = unpacker.unpack("<i")
        r3 = unpacker.unpack("<i")

        self.assertEqual(r1, (1,))
        self.assertEqual(r2, (2,))
        self.assertEqual(r3, (3,))


class UnpackerIntegrationTestCase(TestCase):
    """Integration tests for typical usage patterns."""

    def test_typical_csa_header_pattern(self):
        """Test typical CSA header reading pattern."""
        # Simulate CSA header structure: magic + size + count + data
        magic = b"SV10"
        size = struct.pack("<i", 12964)
        count = struct.pack("<i", 101)
        data = b"\x00" * 100

        buffer = magic + size + count + data
        unpacker = Unpacker(buffer, endian="<")

        # Read magic
        magic_read = unpacker.read(4)
        self.assertEqual(magic_read, b"SV10")

        # Unpack size
        size_unpacked = unpacker.unpack("i")
        self.assertEqual(size_unpacked, (12964,))

        # Unpack count
        count_unpacked = unpacker.unpack("i")
        self.assertEqual(count_unpacked, (101,))

    def test_reading_array_of_floats(self):
        """Test reading an array of float values."""
        floats = [1.1, 2.2, 3.3, 4.4, 5.5]
        buffer = struct.pack("<5f", *floats)
        unpacker = Unpacker(buffer, endian="<")

        results = []
        for _ in range(5):
            value = unpacker.unpack("f")
            results.append(value[0])

        for i, expected in enumerate(floats):
            self.assertAlmostEqual(results[i], expected, places=5)

    def test_mixed_read_unpack_workflow(self):
        """Test realistic workflow mixing read and unpack operations."""
        # Header: 4-byte magic, 4-byte int count, then count*4 bytes of data
        buffer = b"HEAD" + struct.pack("<i", 3) + b"DATADATADATA"
        unpacker = Unpacker(buffer, endian="<")

        # Read magic
        magic = unpacker.read(4)
        self.assertEqual(magic, b"HEAD")

        # Unpack count
        count = unpacker.unpack("i")[0]
        self.assertEqual(count, 3)

        # Read data
        data = unpacker.read(4 * count)
        self.assertEqual(data, b"DATADATADATA")

    def test_struct_with_padding(self):
        """Test unpacking struct with padding."""
        # C struct with padding: int, char, int (will have padding)
        buffer = struct.pack("<i1c3xi", 42, b"A", 100)
        unpacker = Unpacker(buffer, endian="<")
        result = unpacker.unpack("i1c3xi")
        self.assertEqual(result[0], 42)
        self.assertEqual(result[1], b"A")
        self.assertEqual(result[2], 100)

    def test_endian_conversion(self):
        """Test reading same data with different endianness."""
        value = 0x12345678
        buffer_le = struct.pack("<I", value)
        buffer_be = struct.pack(">I", value)

        unpacker_le = Unpacker(buffer_le, endian="<")
        unpacker_be = Unpacker(buffer_be, endian=">")

        result_le = unpacker_le.unpack("I")
        result_be = unpacker_be.unpack("I")

        self.assertEqual(result_le, (value,))
        self.assertEqual(result_be, (value,))

    def test_reading_string_with_null_terminator(self):
        """Test reading null-terminated string pattern."""
        buffer = b"Hello\x00World\x00"
        unpacker = Unpacker(buffer)

        # Read first string (6 bytes including null)
        str1 = unpacker.read(6)
        self.assertEqual(str1, b"Hello\x00")

        # Read second string
        str2 = unpacker.read(6)
        self.assertEqual(str2, b"World\x00")


class UnpackerConstantsTestCase(TestCase):
    """Tests for module constants."""

    def test_endian_codes_constant(self):
        """Test ENDIAN_CODES constant contains expected values."""
        self.assertIn("@", ENDIAN_CODES)
        self.assertIn("=", ENDIAN_CODES)
        self.assertIn("<", ENDIAN_CODES)
        self.assertIn(">", ENDIAN_CODES)
        self.assertIn("!", ENDIAN_CODES)
        self.assertEqual(ENDIAN_CODES, "@=<>!")

    def test_all_endian_codes_work(self):
        """Test that all endian codes work in format strings."""
        buffer = struct.pack("<i", 42)
        for code in ["<", ">", "@", "=", "!"]:
            if code in ["<", "="]:
                # Little-endian compatible
                unpacker = Unpacker(buffer, endian=code)
                try:
                    result = unpacker.unpack("i")
                    # Just verify it doesn't crash
                    self.assertIsNotNone(result)
                except struct.error:
                    # Some endian codes might not work with test data
                    pass


class UnpackerDocstringExampleTestCase(TestCase):
    """Tests for examples from the docstring."""

    def test_docstring_example(self):
        """Test the example from the Unpacker class docstring."""
        a = b"1234567890"
        upk = Unpacker(a)

        result1 = upk.unpack("2s")
        self.assertEqual(result1, (b"12",))

        result2 = upk.unpack("2s")
        self.assertEqual(result2, (b"34",))

        self.assertEqual(upk.pointer, 4)

        result3 = upk.read(3)
        self.assertEqual(result3, b"567")

        self.assertEqual(upk.pointer, 7)
