"""
NiBabel Integration Example
============================

This example demonstrates how to use csa_header with NiBabel to extract
CSA header information from Siemens MRI DICOM files and integrate it
with neuroimaging workflows.

Prerequisites
-------------
pip install csa_header nibabel pydicom

"""

import pydicom
from csa_header import CsaHeader

# Optional: NiBabel for advanced DICOM handling
try:
    import nibabel as nib
    NIBABEL_AVAILABLE = True
except ImportError:
    NIBABEL_AVAILABLE = False
    print("NiBabel not available. Install with: pip install nibabel")


def extract_csa_from_dicom(dicom_path):
    """
    Extract CSA header from a Siemens DICOM file.

    Parameters
    ----------
    dicom_path : str
        Path to Siemens DICOM file

    Returns
    -------
    dict
        Parsed CSA header information
    """
    # Load DICOM file
    dcm = pydicom.dcmread(dicom_path)

    # Check if it's a Siemens file with CSA headers
    if not hasattr(dcm, 'Manufacturer'):
        raise ValueError("No manufacturer information found")

    if 'SIEMENS' not in dcm.Manufacturer.upper():
        raise ValueError(f"Not a Siemens file (manufacturer: {dcm.Manufacturer})")

    # CSA headers are stored in private tags 0029,1010 and 0029,1020
    # Series Header (0x0029, 0x1010)
    series_header_info = None
    if (0x0029, 0x1010) in dcm:
        series_header_data = dcm[0x0029, 0x1010].value
        csa = CsaHeader(series_header_data)
        series_header_info = csa.read()
        print(f"Series header contains {len(series_header_info)} tags")

    # Image Header (0x0029, 0x1020)
    image_header_info = None
    if (0x0029, 0x1020) in dcm:
        image_header_data = dcm[0x0029, 0x1020].value
        csa = CsaHeader(image_header_data)
        image_header_info = csa.read()
        print(f"Image header contains {len(image_header_info)} tags")

    return {
        'series_header': series_header_info,
        'image_header': image_header_info
    }


def get_acquisition_parameters(dicom_path):
    """
    Extract common MRI acquisition parameters from CSA headers.

    Parameters
    ----------
    dicom_path : str
        Path to Siemens DICOM file

    Returns
    -------
    dict
        Common acquisition parameters
    """
    csa_headers = extract_csa_from_dicom(dicom_path)
    params = {}

    # Extract parameters from series header if available
    if csa_headers['series_header']:
        series = csa_headers['series_header']

        # Slice timing information (crucial for fMRI analysis)
        if 'MosaicRefAcqTimes' in series:
            params['slice_times'] = series['MosaicRefAcqTimes']

        # Number of echoes
        if 'NumberOfImagesInMosaic' in series:
            params['n_slices_mosaic'] = series['NumberOfImagesInMosaic']

        # Phase encoding direction
        if 'PhaseEncodingDirectionPositive' in series:
            params['phase_encoding_positive'] = series['PhaseEncodingDirectionPositive']

    # Extract parameters from image header if available
    if csa_headers['image_header']:
        image = csa_headers['image_header']

        # B-value for diffusion imaging
        if 'B_value' in image:
            params['b_value'] = image['B_value']

        # Diffusion gradient direction
        if 'DiffusionGradientDirection' in image:
            params['gradient_direction'] = image['DiffusionGradientDirection']

        # Slice position
        if 'SlicePosition_PCS' in image:
            params['slice_position'] = image['SlicePosition_PCS']

    return params


def get_ascconv_protocol(dicom_path):
    """
    Extract the ASCCONV protocol parameters from CSA header.

    The ASCCONV section contains detailed scanner protocol parameters
    in a structured format.

    Parameters
    ----------
    dicom_path : str
        Path to Siemens DICOM file

    Returns
    -------
    dict
        ASCCONV protocol dictionary
    """
    csa_headers = extract_csa_from_dicom(dicom_path)

    # ASCCONV is typically in the series header under MrPhoenixProtocol
    if csa_headers['series_header'] and 'MrPhoenixProtocol' in csa_headers['series_header']:
        protocol_text = csa_headers['series_header']['MrPhoenixProtocol']

        # The protocol is stored as a string in ASCCONV format
        # csa_header automatically parses it into a nested dictionary
        if isinstance(protocol_text, dict):
            return protocol_text

    return None


def extract_dwi_parameters(dicom_path):
    """
    Extract diffusion-weighted imaging (DWI) specific parameters.

    Parameters
    ----------
    dicom_path : str
        Path to Siemens DWI DICOM file

    Returns
    -------
    dict
        DWI-specific parameters
    """
    params = get_acquisition_parameters(dicom_path)
    protocol = get_ascconv_protocol(dicom_path)

    dwi_params = {}

    # B-value from CSA header
    if 'b_value' in params:
        dwi_params['b_value'] = params['b_value']

    # Gradient direction from CSA header
    if 'gradient_direction' in params:
        dwi_params['gradient_direction'] = params['gradient_direction']

    # Additional DWI parameters from protocol
    if protocol:
        # Number of diffusion directions
        if 'sDiffusion' in protocol and 'lDiffDirections' in protocol['sDiffusion']:
            dwi_params['n_directions'] = protocol['sDiffusion']['lDiffDirections']

        # Diffusion scheme
        if 'sDiffusion' in protocol and 'dsScheme' in protocol['sDiffusion']:
            dwi_params['diffusion_scheme'] = protocol['sDiffusion']['dsScheme']

    return dwi_params


def extract_fmri_parameters(dicom_path):
    """
    Extract functional MRI specific parameters.

    Parameters
    ----------
    dicom_path : str
        Path to Siemens fMRI DICOM file

    Returns
    -------
    dict
        fMRI-specific parameters
    """
    params = get_acquisition_parameters(dicom_path)
    protocol = get_ascconv_protocol(dicom_path)

    fmri_params = {}

    # Slice timing (critical for slice timing correction)
    if 'slice_times' in params:
        fmri_params['slice_times'] = params['slice_times']

    # Mosaic information
    if 'n_slices_mosaic' in params:
        fmri_params['n_slices'] = params['n_slices_mosaic']

    # Phase encoding direction (needed for distortion correction)
    if 'phase_encoding_positive' in params:
        fmri_params['phase_encoding_positive'] = params['phase_encoding_positive']

    # Additional fMRI parameters from protocol
    if protocol:
        # TR (Repetition Time)
        if 'alTR' in protocol and len(protocol['alTR']) > 0:
            fmri_params['TR_ms'] = protocol['alTR'][0]

        # TE (Echo Time)
        if 'alTE' in protocol and len(protocol['alTE']) > 0:
            fmri_params['TE_ms'] = protocol['alTE'][0]

        # Flip angle
        if 'adFlipAngleDegree' in protocol and len(protocol['adFlipAngleDegree']) > 0:
            fmri_params['flip_angle'] = protocol['adFlipAngleDegree'][0]

    return fmri_params


def nibabel_workflow_example(dicom_path):
    """
    Complete workflow example combining csa_header and NiBabel.

    This demonstrates how to:
    1. Extract CSA header information
    2. Load DICOM with NiBabel
    3. Combine standard DICOM and CSA information

    Parameters
    ----------
    dicom_path : str
        Path to Siemens DICOM file
    """
    if not NIBABEL_AVAILABLE:
        print("This example requires NiBabel. Install with: pip install nibabel")
        return

    print(f"\nAnalyzing: {dicom_path}\n")
    print("=" * 70)

    # 1. Load with pydicom for CSA extraction
    dcm = pydicom.dcmread(dicom_path)
    print(f"Manufacturer: {dcm.Manufacturer}")
    print(f"Model: {dcm.ManufacturerModelName}")
    print(f"Sequence: {dcm.SeriesDescription if hasattr(dcm, 'SeriesDescription') else 'N/A'}")

    # 2. Extract CSA headers
    print("\n" + "=" * 70)
    print("CSA Header Information:")
    print("=" * 70)
    csa_info = extract_csa_from_dicom(dicom_path)

    if csa_info['series_header']:
        print(f"\nSeries header tags: {list(csa_info['series_header'].keys())[:10]}...")

    if csa_info['image_header']:
        print(f"Image header tags: {list(csa_info['image_header'].keys())[:10]}...")

    # 3. Extract acquisition parameters
    print("\n" + "=" * 70)
    print("Acquisition Parameters:")
    print("=" * 70)
    params = get_acquisition_parameters(dicom_path)
    for key, value in params.items():
        if isinstance(value, (list, tuple)) and len(value) > 5:
            print(f"{key}: [{value[0]}, {value[1]}, ..., {value[-1]}] (length: {len(value)})")
        else:
            print(f"{key}: {value}")

    # 4. Load with NiBabel (if it's a valid DICOM image)
    try:
        print("\n" + "=" * 70)
        print("NiBabel Image Information:")
        print("=" * 70)
        nib_img = nib.load(dicom_path)
        print(f"Shape: {nib_img.shape}")
        print(f"Data type: {nib_img.get_data_dtype()}")
        print(f"Affine:\n{nib_img.affine}")
    except Exception as e:
        print(f"Could not load with NiBabel: {e}")

    # 5. Protocol parameters
    print("\n" + "=" * 70)
    print("Protocol Parameters (ASCCONV):")
    print("=" * 70)
    protocol = get_ascconv_protocol(dicom_path)
    if protocol:
        # Print first few protocol parameters
        count = 0
        for key in list(protocol.keys())[:5]:
            print(f"{key}: {protocol[key]}")
            count += 1
        if len(protocol) > 5:
            print(f"... and {len(protocol) - 5} more parameters")
    else:
        print("No ASCCONV protocol found")


def main():
    """
    Main example function.

    Usage:
        python nibabel_integration.py path/to/siemens_dicom.dcm
    """
    import sys

    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage:")
        print("  python nibabel_integration.py <path_to_siemens_dicom>")
        print("\nExample:")
        print("  python nibabel_integration.py /path/to/MRI_scan.dcm")
        return

    dicom_path = sys.argv[1]

    try:
        nibabel_workflow_example(dicom_path)
    except FileNotFoundError:
        print(f"Error: File not found: {dicom_path}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
