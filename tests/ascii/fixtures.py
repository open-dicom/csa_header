"""Comparison values to test ascconv parsing."""

from tests.fixtures import TEST_FILES_DIR

RAW_ELEMENTS = """
GRADSPEC.asGPAData[0].sEddyCompensationY.aflTimeConstant[1]\t = \t0.917683601379
TXSPEC.asNucleusInfo[0].CompProtectionValues.MaxOfflineTxAmpl\t = \t534.113952637
SliceArray.asSlice[2].sNormal.dSag\t = \t-0.01623302609
PtabAbsStartPosZValid\t = \t0x1
"""

PARSED_ELEMENTS = {
    "GRADSPEC": {"asGPAData": [{"sEddyCompensationY": {"aflTimeConstant": [None, 0.917683601379]}}]},
    "TXSPEC": {"asNucleusInfo": [{"CompProtectionValues": {"MaxOfflineTxAmpl": 534.113952637}}]},
    "SliceArray": {"asSlice": [None, None, {"sNormal": {"dSag": -0.01623302609}}]},
    "PtabAbsStartPosZValid": 1,
}
TEST_ASCCONV_FILE = TEST_FILES_DIR / "ascconv_sample.txt"
