"""
Messages for the :mod:`csa_header` library.
"""

INVALID_CHECK_BIT: str = (
    "CSA element #{i_tag} has an invalid check bit value: {check_bit}!\n"
    "Valid values are {valid_values}\n"
    "This may indicate a corrupted or invalid CSA header."
)

READ_OVERREACH: str = (
    "Invalid item length! Destination {destination} is beyond the maximal length ({max_length}).\n"
    "This indicates a corrupted CSA header or parsing error at byte position {pointer}."
)

TOO_MANY_ITEMS: str = (
    "Too many items in CSA header element.\n"
    "Expected {expected} items (VM={vm}) but found more non-empty items at index {i_item}.\n"
    "This may indicate a malformed CSA header."
)
