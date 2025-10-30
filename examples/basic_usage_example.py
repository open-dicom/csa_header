"""
Basic Usage Example with Example Data
=======================================

This example demonstrates the basic usage of csa_header with the built-in
example DICOM data. This is the quickest way to get started with the library.

Prerequisites
-------------
pip install csa_header[examples]

This installs csa_header along with pooch for downloading example data.
"""

import pydicom

from csa_header import CsaHeader

# Import example data fetching (requires pooch)
try:
    from csa_header.examples import fetch_example_dicom, list_example_files

    EXAMPLES_AVAILABLE = True
except ImportError:
    EXAMPLES_AVAILABLE = False
    print("Example data fetching not available.")
    print("Install with: pip install csa_header[examples]")


def basic_csa_parsing():
    """
    Basic example: Parse CSA headers from example DICOM file.

    This demonstrates the simplest use case - loading a DICOM file
    and extracting CSA header information.
    """
    if not EXAMPLES_AVAILABLE:
        print("\nThis example requires the 'examples' optional dependency.")
        print("Install with: pip install csa_header[examples]")
        return

    print("=" * 70)
    print("BASIC CSA HEADER PARSING EXAMPLE")
    print("=" * 70)

    # List available example files
    print("\nAvailable example files:")
    for filename in list_example_files():
        print(f"  - {filename}")

    # Fetch example DICOM file
    print("\nDownloading example DICOM (cached after first download)...")
    dicom_path = fetch_example_dicom("mprage_example_anon.dcm")
    print(f"✓ Example file cached at: {dicom_path}")

    # Load DICOM file
    print("\nLoading DICOM file...")
    dcm = pydicom.dcmread(dicom_path)
    print(f"  Manufacturer: {dcm.Manufacturer}")
    print(f"  Modality: {dcm.Modality}")
    print(f"  Series Description: {dcm.SeriesDescription}")

    # Check for CSA headers
    print("\nChecking for CSA headers...")
    csa_image_tag = (0x0029, 0x1010)
    csa_series_tag = (0x0029, 0x1020)

    has_image = csa_image_tag in dcm
    has_series = csa_series_tag in dcm

    print(f"  CSA Image Header (0029,1010): {'✓ Found' if has_image else '✗ Not found'}")
    print(f"  CSA Series Header (0029,1020): {'✓ Found' if has_series else '✗ Not found'}")

    # Parse CSA Image Header
    if has_image:
        print("\n" + "=" * 70)
        print("PARSING CSA IMAGE HEADER")
        print("=" * 70)

        csa_image_data = dcm[csa_image_tag].value
        print(f"CSA Image Header size: {len(csa_image_data):,} bytes")

        csa = CsaHeader(csa_image_data)
        image_tags = csa.read()

        print(f"\nParsed {len(image_tags)} tags from image header")
        print("\nFirst 10 tags:")
        for i, (tag_name, tag_data) in enumerate(list(image_tags.items())[:10]):
            value = tag_data.get('value', 'N/A')
            if isinstance(value, list) and len(value) > 3:
                value = f"[{value[0]}, {value[1]}, ..., {value[-1]}] (len={len(value)})"
            print(f"  {i+1}. {tag_name}: {value}")

    # Parse CSA Series Header
    if has_series:
        print("\n" + "=" * 70)
        print("PARSING CSA SERIES HEADER")
        print("=" * 70)

        csa_series_data = dcm[csa_series_tag].value
        print(f"CSA Series Header size: {len(csa_series_data):,} bytes")

        csa = CsaHeader(csa_series_data)
        series_tags = csa.read()

        print(f"\nParsed {len(series_tags)} tags from series header")
        print("\nFirst 10 tags:")
        for i, (tag_name, tag_data) in enumerate(list(series_tags.items())[:10]):
            value = tag_data.get('value', 'N/A')
            if isinstance(value, list) and len(value) > 3:
                value = f"[{value[0]}, {value[1]}, ..., {value[-1]}] (len={len(value)})"
            print(f"  {i+1}. {tag_name}: {value}")


def inspect_specific_tags():
    """
    Example: Access specific CSA header tags.

    This demonstrates how to extract specific parameters of interest
    from the CSA headers.
    """
    if not EXAMPLES_AVAILABLE:
        return

    print("\n\n" + "=" * 70)
    print("ACCESSING SPECIFIC CSA TAGS")
    print("=" * 70)

    # Fetch and load example DICOM
    dicom_path = fetch_example_dicom()
    dcm = pydicom.dcmread(dicom_path)

    # Parse CSA Series Header
    if (0x0029, 0x1020) in dcm:
        csa = CsaHeader(dcm[(0x0029, 0x1020)].value)
        tags = csa.read()

        # Look for specific interesting tags
        interesting_tags = [
            'EchoTime',
            'RepetitionTime',
            'ImagingFrequency',
            'FlipAngle',
            'SequenceName',
            'ProtocolSliceNumber',
        ]

        print("\nSelected acquisition parameters:")
        for tag_name in interesting_tags:
            if tag_name in tags:
                value = tags[tag_name].get('value', 'N/A')
                vm = tags[tag_name].get('VM', 'N/A')
                print(f"  {tag_name} (VM={vm}): {value}")
            else:
                print(f"  {tag_name}: Not found")


def working_with_your_own_data():
    """
    Example: Use csa_header with your own DICOM files.

    This shows how to switch from example data to your own files.
    """
    print("\n\n" + "=" * 70)
    print("WORKING WITH YOUR OWN DATA")
    print("=" * 70)

    print("""
Once you're familiar with the library using example data, you can use
your own Siemens DICOM files:

    import pydicom
    from csa_header import CsaHeader

    # Load your own DICOM file
    dcm = pydicom.dcmread('path/to/your/siemens_scan.dcm')

    # Extract CSA Series Header (0x0029, 0x1020)
    if (0x0029, 0x1020) in dcm:
        csa_data = dcm[(0x0029, 0x1020)].value
        csa = CsaHeader(csa_data)
        tags = csa.read()
        print(f"Found {len(tags)} CSA tags")

    # Or extract CSA Image Header (0x0029, 0x1010)
    if (0x0029, 0x1010) in dcm:
        csa_data = dcm[(0x0029, 0x1010)].value
        csa = CsaHeader(csa_data)
        tags = csa.read()
        print(f"Found {len(tags)} CSA tags")

Note: CSA headers are only present in Siemens MRI DICOM files.
    """)


def main():
    """
    Main example function.

    Usage:
        python basic_usage_example.py
    """
    if not EXAMPLES_AVAILABLE:
        print("\n" + "=" * 70)
        print("ERROR: Example data fetching not available")
        print("=" * 70)
        print("\nTo run this example, install csa_header with examples support:")
        print("  pip install csa_header[examples]")
        print("\nThis will install csa_header along with pooch for downloading example data.")
        return

    try:
        # Run all example functions
        basic_csa_parsing()
        inspect_specific_tags()
        working_with_your_own_data()

        print("\n" + "=" * 70)
        print("EXAMPLES COMPLETE")
        print("=" * 70)
        print("\nFor more advanced examples, see:")
        print("  - nibabel_integration.py: Integration with NiBabel for neuroimaging workflows")
        print("  - README.md: Additional examples and use cases")

    except Exception as e:
        print(f"\nError running example: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
