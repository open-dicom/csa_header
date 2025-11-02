"""Fixtures for tests."""

from pathlib import Path

TEST_FILES_DIR: Path = Path(__file__).parent / "files"
DWI_CSA_IMAGE_HEADER_INFO: Path = TEST_FILES_DIR / "dwi_image_header_info"
RSFMRI_CSA_SERIES_HEADER_INFO: Path = TEST_FILES_DIR / "rsfmri_series_header_info"
E11_CSA_SERIES_HEADER_INFO: Path = TEST_FILES_DIR / "e11_series_header_info"

# XA Enhanced DICOM test files (syngo MR XA30, XA60)
XA_ENHANCED_DIR: Path = TEST_FILES_DIR / "xa_enhanced"
XA30_SAMPLE_DICOM: Path = XA_ENHANCED_DIR / "xa30_sample.dcm"
XA60_SAMPLE_DICOM: Path = XA_ENHANCED_DIR / "xa60_sample.dcm"
