"""
Messages for the :mod:`csa_header` library.
"""
INVALID_CHECK_BIT: str = (
    "CSA element #{i_tag} has an invalid check bit value: {check_bit}!\nValid values are {valid_values}"
)
READ_OVERREACH: str = "Invalid item length! Destination {destination} is beyond the maximal length ({max_length})!"
