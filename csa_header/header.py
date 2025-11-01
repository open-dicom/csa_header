"""Definition of the :class:`CsaHeader` class."""

from __future__ import annotations

from typing import Any

from csa_header.ascii import CsaAsciiHeader
from csa_header.exceptions import CsaReadError
from csa_header.messages import INVALID_CHECK_BIT, READ_OVERREACH, TOO_MANY_ITEMS
from csa_header.unpacker import Unpacker
from csa_header.utils import VR_TO_TYPE, decode_latin1, strip_to_null


class CsaHeader:
    """
    Represents a full CSA header data element, i.e. either
    (0029, 1010)/`"CSA Image Header Info"` or (0029, 1020)/`"CSA Series Header
    Info"`, and provides access to the header as a parsed dictionary.
    This implementation is heavily based on `dicom2nifti`_'s code
    (particularly `this module`_).

    .. _dicom2nifti:
       https://github.com/icometrix/dicom2nifti
    .. _this module:
       https://github.com/icometrix/dicom2nifti/blob/6722420a7673d36437e4358ce3cb2a7c77c91820/dicom2nifti/convert_siemens.py#L342
    """

    __slots__ = ("_csa_type", "_first_tag_n_items", "header_size", "raw")

    CSA_TYPE_1: int = 1
    CSA_TYPE_2: int = 2

    #: Byte alignment boundary for CSA item values.
    BYTE_ALIGNMENT: int = 4

    #: Used to determine whether the CSA header is of type 1 or 2.
    TYPE_2_IDENTIFIER: bytes = b"SV10"

    #: Endian format used to parse the CSA header information (little-endian).
    ENDIAN: str = "<"

    #: Format string used to unpack a single tag.
    TAG_FORMAT_STRING: str = "64si4s3i"

    #: Number of tags unpacking format characters (2 unsigned integers).
    PREFIX_FORMAT: str = "2I"

    #: Item value unpacking format characters (4 integers).
    ITEM_FORMAT: str = "4i"

    #: Valid values for the CSA element's check bit.
    VALID_CHECK_BIT_VALUES: frozenset[int] = frozenset({77, 205})

    #: ASCII header tag names.
    ASCII_HEADER_TAGS: frozenset[str] = frozenset({"MrPhoenixProtocol"})

    def __init__(self, raw: bytes):
        """
        Initialize a new `CsaHeader` instance.

        Parameters
        ----------
        raw : bytes
            Raw CSA header as read by *pydicom*
        """
        self.raw = raw
        self.header_size = len(self.raw)
        # Initialize CSA type 1 length fix
        self._first_tag_n_items: int | None = None
        # Cache CSA type at initialization - it never changes for an instance
        self._csa_type = self.check_csa_type()

    def skip_prefix(self, unpacker: Unpacker) -> None:
        """
        Skip the CSA type 2 header prefix.

        See Also
        --------
        * :attr:`TYPE_2_IDENTIFIER`

        Parameters
        ----------
        unpacker : Unpacker
            Stream-like header reader
        """
        if self.is_type_2:
            prefix_length = len(self.TYPE_2_IDENTIFIER)
            unpacker.pointer = prefix_length
            unpacker.read(prefix_length)

    def validate_check_bit(self, i_tag: int, value: int) -> None:
        """
        Validates a single CSA header tag's check-bit.

        See Also
        --------
        * :attr:`VALID_CHECK_BIT_VALUES`

        Parameters
        ----------
        i_tag : int
            Index of the parsed tag
        value : int
            Check-bit value

        Raises
        ------
        CsaReadError
            Invalid check-bit value
        """
        if value not in self.VALID_CHECK_BIT_VALUES:
            message = INVALID_CHECK_BIT.format(
                i_tag=i_tag,
                check_bit=value,
                valid_values=self.VALID_CHECK_BIT_VALUES,
            )
            raise CsaReadError(message)

    def _parse_csa1_item_length(self, unpacker: Unpacker, x0: int) -> tuple[int, bool]:
        """
        Calculate item length for CSA Type 1 headers.

        Parameters
        ----------
        unpacker : Unpacker
            Stream-like header reader
        x0 : int
            First value from ITEM_FORMAT unpacking

        Returns
        -------
        tuple[int, bool]
            Item length and whether to break parsing (invalid length)
        """
        # For CSA Type 1, _first_tag_n_items is set when parsing the first tag
        # It should never be None at this point, but we check for type safety
        if self._first_tag_n_items is None:
            return 0, True  # Invalid state, break parsing

        item_len = x0 - self._first_tag_n_items
        destination = unpacker.pointer + item_len
        negative_length = item_len < 0
        overreach = destination > self.header_size
        should_break = negative_length or overreach
        return item_len, should_break

    def _parse_csa2_item_length(self, unpacker: Unpacker, x1: int) -> int:
        """
        Calculate item length for CSA Type 2 headers.

        Parameters
        ----------
        unpacker : Unpacker
            Stream-like header reader
        x1 : int
            Second value from ITEM_FORMAT unpacking

        Returns
        -------
        int
            Item length

        Raises
        ------
        CsaReadError
            If reading would exceed header size
        """
        item_len = x1
        destination = unpacker.pointer + item_len
        if destination > self.header_size:
            message = READ_OVERREACH.format(
                destination=destination, max_length=self.header_size, pointer=unpacker.pointer
            )
            raise CsaReadError(message)
        return item_len

    def parse_items(self, unpacker: Unpacker, n_items: int, vr: str, vm: int) -> Any:
        """
        Parses a single header element's value.

        Parameters
        ----------
        unpacker : Unpacker
            Stream-like header reader
        n_items : int
            Number of items in this element's value as described in the header
            information
        vr : str
            Value representation
        vm : int
            Value multiplicity

        Returns
        -------
        Any
            CSA header element value

        Raises
        ------
        CsaReadError
            Invalid element value
        """
        n_values = vm or n_items
        converter = VR_TO_TYPE.get(vr)
        items: list[Any] = []
        # Cache frequently accessed attributes to avoid repeated lookups in loop
        csa_type = self.csa_type
        byte_alignment = self.BYTE_ALIGNMENT

        for i_item in range(n_items):
            x0, x1, _, _ = unpacker.unpack(self.ITEM_FORMAT)

            # Calculate item length based on CSA type
            if csa_type == 1:
                item_len, should_break = self._parse_csa1_item_length(unpacker, x0)
                if should_break:
                    if i_item < vm:
                        items.append("")
                    break
            else:  # CSA Type 2
                item_len = self._parse_csa2_item_length(unpacker, x1)

            if i_item >= n_values:
                if item_len != 0:
                    message = TOO_MANY_ITEMS.format(expected=n_values, vm=vm, i_item=i_item)
                    raise CsaReadError(message)
                continue

            item_raw = strip_to_null(unpacker.read(item_len))
            item_str = decode_latin1(item_raw)
            item: float | int | str

            if converter:
                # We may have fewer real items than are given in
                # n_items, but we don't know how many - assume that
                # we've reached the end when we hit an empty item
                if item_len == 0:
                    n_values = i_item
                    continue
                item = converter(item_str)
            else:
                item = item_str
            items.append(item)

            # Align to byte boundary
            remainder = item_len % byte_alignment
            if remainder != 0:
                unpacker.pointer += byte_alignment - remainder

        if items:
            return items if len(items) > 1 else items.pop()

    def parse_tag(self, unpacker: Unpacker, i_tag: int) -> dict[str, Any]:
        # 4th element (SyngoDT) seems to be a numeric representation of the
        # datatype, which is already provided as the VR.
        name_raw, vm, vr_raw, _, n_items, check_bit = unpacker.unpack(self.TAG_FORMAT_STRING)
        self.validate_check_bit(i_tag, check_bit)
        name_result = strip_to_null(name_raw)
        vr_result = strip_to_null(vr_raw)
        # strip_to_null returns str when null found, bytes otherwise - ensure we have str
        name = decode_latin1(name_result)
        vr = decode_latin1(vr_result)
        tag: dict[str, Any] = {
            "name": name,
            "VR": vr,
            "VM": vm,
        }
        # CSA1-specific length modifier
        if i_tag == 1:
            self._first_tag_n_items = n_items
        tag["value"] = self.parse_items(unpacker, n_items, vr, vm)
        if name in self.ASCII_HEADER_TAGS:
            tag["value"] = CsaAsciiHeader(tag["value"]).parse()
        return tag

    def read(self) -> dict[str, dict[str, Any]]:
        """
        Parse the CSA header and return tag information as a dictionary.

        Returns
        -------
        dict[str, dict[str, Any]]
            Dictionary mapping tag names to tag information. Keys are ordered
            by tag appearance in the CSA header (Python 3.7+ dict ordering
            guarantee). Each tag dictionary contains:

            - 'VR' : str
                Value Representation (DICOM standard)
            - 'VM' : int
                Value Multiplicity (DICOM standard)
            - 'value' : Any
                Parsed tag value (type depends on VR)

        Notes
        -----
        Tag ordering is preserved via Python's dict insertion order guarantee
        (Python 3.7+). To enumerate tags with explicit indices:

            >>> for idx, (name, tag) in enumerate(parsed.items(), 1):
            ...     print(f"Tag {idx}: {name}")
        """
        unpacker = Unpacker(self.raw, endian=self.ENDIAN)
        self.skip_prefix(unpacker)
        n_tags, _ = unpacker.unpack(self.PREFIX_FORMAT)
        result: dict[str, dict[str, Any]] = {}
        for i_tag in range(n_tags):
            tag = self.parse_tag(unpacker, i_tag)
            name = tag.pop("name")
            result[name] = tag
        return result

    def check_csa_type(self) -> int:
        """
        Checks whether the given CSA header is of type 1 or 2.

        See Also
        --------
        * :func:`csa_type`

        Returns
        -------
        int
            CSA header type (1 or 2)
        """
        is_type_2 = self.raw[:4] == self.TYPE_2_IDENTIFIER
        return self.CSA_TYPE_2 if is_type_2 else self.CSA_TYPE_1

    @property
    def csa_type(self) -> int:
        """
        Checks whether the given CSA header is of type 1 or 2.

        See Also
        --------
        * :func:`check_csa_type`

        Returns
        -------
        int
            CSA header type (1 or 2)
        """
        return self._csa_type

    @property
    def is_type_2(self) -> bool:
        """
        Returns whether this header if CSA type 2 or not (1).

        Returns
        -------
        bool
            CSA type 2 or not
        """
        return self._csa_type == self.CSA_TYPE_2
