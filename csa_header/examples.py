"""Example data fetching using Pooch.

This module provides functions to download example DICOM files with Siemens CSA headers
for demonstration and testing purposes. The example data is hosted on Zenodo and
downloaded on first use, then cached locally.

Installation
------------
To use this module, install csa_header with the examples optional dependency::

    pip install csa_header[examples]

Usage
-----
>>> from csa_header.examples import fetch_example_dicom
>>> dicom_path = fetch_example_dicom('mprage_example_anon.dcm')
>>> import pydicom
>>> dcm = pydicom.dcmread(dicom_path)
>>> from csa_header import CsaHeader
>>> csa = CsaHeader(dcm.get((0x29, 0x1020)).value)
>>> result = csa.read()
"""

try:
    import pooch  # type: ignore[import-not-found]

    POOCH_AVAILABLE = True
except ImportError:  # pragma: no cover
    POOCH_AVAILABLE = False  # pragma: no cover


# Zenodo DOI and record information
ZENODO_DOI = "10.5281/zenodo.17482132"
ZENODO_RECORD_ID = "17482132"
# Note: Zenodo API requires /content suffix to download actual file content
ZENODO_BASE_URL = f"https://zenodo.org/api/records/{ZENODO_RECORD_ID}/files/{{fpath}}/content"

# File registry with SHA256 checksums
REGISTRY = {
    "mprage_example_anon.dcm": "sha256:831fa610f8853fbd7f5602e896824480af701dfc7286f9df30d1cc2302c2022e",
}

# Available example files
AVAILABLE_FILES = list(REGISTRY.keys())


def fetch_example_dicom(filename="mprage_example_anon.dcm"):
    """Fetch an example DICOM file with Siemens CSA headers.

    Downloads example DICOM files from Zenodo on first use and caches them locally
    for subsequent uses. All example files have been anonymized to remove Protected
    Health Information (PHI).

    Parameters
    ----------
    filename : str, optional
        Name of the example file to fetch. Default is 'mprage_example_anon.dcm'.
        Use `list_example_files()` to see all available files.

    Returns
    -------
    str
        Path to the downloaded and cached DICOM file.

    Raises
    ------
    ImportError
        If pooch is not installed. Install with: pip install csa_header[examples]
    ValueError
        If the specified filename is not available in the registry.

    Examples
    --------
    >>> from csa_header.examples import fetch_example_dicom
    >>> dicom_path = fetch_example_dicom()
    >>> print(dicom_path)
    /home/user/.cache/pooch/...mprage_example_anon.dcm

    >>> # Use with pydicom and csa_header
    >>> import pydicom
    >>> from csa_header import CsaHeader
    >>> dcm = pydicom.dcmread(dicom_path)
    >>> csa_bytes = dcm.get((0x29, 0x1020)).value
    >>> csa = CsaHeader(csa_bytes)
    >>> tags = csa.read()

    Notes
    -----
    The example data is hosted on Zenodo at https://doi.org/10.5281/zenodo.17482132
    and is licensed under CC0 (Public Domain).

    The MPRAGE example file contains:
    - Modality: MR (Magnetic Resonance)
    - Sequence: MPRAGE (Enhanced Contrast)
    - Image dimensions: 224 x 224
    - CSA Image Header: 11,196 bytes
    - CSA Series Header: 139,232 bytes
    """
    if not POOCH_AVAILABLE:  # pragma: no cover
        msg = (
            "Example data fetching requires the 'pooch' package. "
            "Install it with:\n\n"
            "    pip install csa_header[examples]\n\n"
            "or install pooch directly:\n\n"
            "    pip install pooch"
        )
        raise ImportError(msg)

    if filename not in REGISTRY:
        available = ", ".join(AVAILABLE_FILES)
        msg = (
            f"File '{filename}' not found in registry. "
            f"Available files: {available}. "
            f"Use list_example_files() to see all options."
        )
        raise ValueError(msg)

    # Create Pooch instance for fetching data
    # Zenodo API requires special URL handling - we provide full URLs
    fetcher = pooch.create(  # pragma: no cover
        path=pooch.os_cache("csa_header"),
        base_url="",  # Empty base_url since we provide full URLs
        registry={filename: REGISTRY[filename]},  # Include hash in registry
        urls={filename: f"https://zenodo.org/api/records/{ZENODO_RECORD_ID}/files/{filename}/content"},
    )

    # Fetch the file (downloads if not cached, validates checksum)
    return fetcher.fetch(filename)  # pragma: no cover


def list_example_files():
    """List all available example DICOM files.

    Returns
    -------
    list of str
        Names of all available example files.

    Examples
    --------
    >>> from csa_header.examples import list_example_files
    >>> files = list_example_files()
    >>> print(files)
    ['mprage_example_anon.dcm']
    """
    return AVAILABLE_FILES.copy()


def get_example_info(filename="mprage_example_anon.dcm"):
    """Get information about an example file.

    Parameters
    ----------
    filename : str, optional
        Name of the example file. Default is 'mprage_example_anon.dcm'.

    Returns
    -------
    dict
        Dictionary containing information about the file including:
        - name: filename
        - checksum: SHA256 checksum
        - url: Zenodo download URL
        - doi: Zenodo DOI

    Raises
    ------
    ValueError
        If the specified filename is not available.

    Examples
    --------
    >>> from csa_header.examples import get_example_info
    >>> info = get_example_info()
    >>> print(info['doi'])
    10.5281/zenodo.17482132
    """
    if filename not in REGISTRY:
        available = ", ".join(AVAILABLE_FILES)
        msg = f"File '{filename}' not found in registry. Available files: {available}"
        raise ValueError(msg)

    return {
        "name": filename,
        "checksum": REGISTRY[filename],
        "url": ZENODO_BASE_URL + filename,
        "doi": ZENODO_DOI,
    }


__all__ = [
    "AVAILABLE_FILES",
    "ZENODO_DOI",
    "fetch_example_dicom",
    "get_example_info",
    "list_example_files",
]
