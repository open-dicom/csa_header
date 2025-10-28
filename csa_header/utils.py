"""
Utilities for the :mod:`csa_header` library.
"""

from __future__ import annotations

# DICOM VR code to Python type
VR_TO_TYPE: dict[str, type[float] | type[int]] = {
    "FL": float,  # float
    "FD": float,  # double
    "DS": float,  # decimal string
    "SS": int,  # signed short
    "US": int,  # unsigned short
    "SL": int,  # signed long
    "UL": int,  # unsigned long
    "IS": int,  # integer string
}

ENCODING: str = "latin-1"
NULL: bytes = b"\x00"


def strip_to_null(string: bytes) -> bytes | str:
    """
    Strip string to first null.

    Parameters
    ----------
    s : bytes

    Returns
    -------
    sdash : str
       s stripped to first occurrence of null (0)
    """
    zero_position = string.find(NULL)
    if zero_position == -1:
        return string
    return string[:zero_position].decode(ENCODING)


def decode_latin1(value: bytes | str) -> str:
    """
    Decode bytes to string using latin-1 encoding if necessary.

    Parameters
    ----------
    value : bytes | str
        Value to decode (if bytes) or return as-is (if already str)

    Returns
    -------
    str
        Decoded string value
    """
    return value if isinstance(value, str) else value.decode(ENCODING)
