# csa_header Examples

This directory contains examples demonstrating how to use csa_header in various scenarios.

## Getting Started

### Quick Start with Example Data

The easiest way to get started is using the built-in example data:

```bash
# Install with examples support
pip install csa_header[examples]

# Run the basic example
python basic_usage_example.py
```

This automatically downloads an anonymized example DICOM file from Zenodo (cached locally after first download).

## Examples

### Basic Usage (`basic_usage_example.py`)

Simple introduction to csa_header using built-in example data. Perfect for first-time users!

**Features:**
- Automatic download of example DICOM data (no need to find your own files)
- Basic CSA header parsing
- Accessing specific CSA tags
- Clear, beginner-friendly code

**Usage:**
```bash
python basic_usage_example.py
```

**Prerequisites:**
```bash
pip install csa_header[examples]
```

**Example output:**
```
BASIC CSA HEADER PARSING EXAMPLE
======================================================================

Available example files:
  - mprage_example_anon.dcm

Downloading example DICOM (cached after first download)...
✓ Example file cached at: /home/user/.cache/pooch/...

Parsing CSA headers...
Parsed 101 tags from image header
Parsed 79 tags from series header
```

### NiBabel Integration (`nibabel_integration.py`)

Comprehensive example showing how to integrate csa_header with NiBabel for neuroimaging workflows.

**Features:**
- Extract CSA headers from Siemens DICOM files
- Parse acquisition parameters (slice timing, b-values, etc.)
- Extract ASCCONV protocol parameters
- DWI-specific parameter extraction
- fMRI-specific parameter extraction
- Complete workflow combining pydicom, csa_header, and NiBabel

**Usage:**
```bash
python nibabel_integration.py path/to/siemens_dicom.dcm
```

**Prerequisites:**
```bash
pip install csa_header nibabel pydicom
```

**Example output:**
```
Analyzing: /path/to/scan.dcm
======================================================================
Manufacturer: SIEMENS
Model: Prisma
Sequence: ep2d_diff

======================================================================
CSA Header Information:
======================================================================
Series header contains 85 tags
Image header contains 42 tags

======================================================================
Acquisition Parameters:
======================================================================
b_value: 1000
gradient_direction: [0.707, 0.707, 0.0]
slice_times: [0.0, 0.5, 1.0, 1.5, ...] (length: 64)
```

## Use Cases

### Diffusion MRI (DWI/DTI)

Extract b-values, gradient directions, and diffusion scheme:

```python
from examples.nibabel_integration import extract_dwi_parameters

dwi_params = extract_dwi_parameters('dwi_scan.dcm')
print(f"B-value: {dwi_params['b_value']}")
print(f"Gradient: {dwi_params['gradient_direction']}")
```

### Functional MRI (fMRI)

Extract slice timing for slice timing correction:

```python
from examples.nibabel_integration import extract_fmri_parameters

fmri_params = extract_fmri_parameters('fmri_scan.dcm')
print(f"Slice times: {fmri_params['slice_times']}")
print(f"TR: {fmri_params['TR_ms']} ms")
```

### Protocol Parameters

Extract detailed scanner protocol:

```python
from examples.nibabel_integration import get_ascconv_protocol

protocol = get_ascconv_protocol('scan.dcm')
# Access nested protocol parameters
tr = protocol['alTR'][0]
te = protocol['alTE'][0]
```

## Integration Patterns

### With NiBabel

```python
import nibabel as nib
from csa_header import CsaHeader
import pydicom

# Load DICOM
dcm = pydicom.dcmread('scan.dcm')
nib_img = nib.load('scan.dcm')

# Extract CSA header
if (0x0029, 0x1010) in dcm:
    csa = CsaHeader(dcm[0x0029, 0x1010].value)
    csa_info = csa.read()

# Use both standard DICOM and CSA info
print(f"Shape: {nib_img.shape}")
print(f"Slice times from CSA: {csa_info.get('MosaicRefAcqTimes')}")
```

### With dcm2niix

Extract CSA information to complement dcm2niix conversions:

```python
# After running dcm2niix, extract additional CSA parameters
from examples.nibabel_integration import get_acquisition_parameters

params = get_acquisition_parameters('original.dcm')
# Use params to create BIDS-compatible JSON sidecar
```

### Batch Processing

Process multiple DICOM series:

```python
from pathlib import Path
from examples.nibabel_integration import extract_csa_from_dicom

dicom_dir = Path('/path/to/dicom/series')
for dcm_file in dicom_dir.glob('*.dcm'):
    try:
        csa_info = extract_csa_from_dicom(str(dcm_file))
        # Process CSA information
    except ValueError as e:
        print(f"Skipping {dcm_file}: {e}")
```

## Common CSA Header Tags

### Series Header Tags (0x0029, 0x1010)

- `MrPhoenixProtocol`: Complete scanner protocol (ASCCONV format)
- `MosaicRefAcqTimes`: Slice acquisition times (ms)
- `NumberOfImagesInMosaic`: Number of slices in mosaic image
- `PhaseEncodingDirectionPositive`: Phase encoding direction
- `SliceArray`: Slice positioning information

### Image Header Tags (0x0029, 0x1020)

- `B_value`: Diffusion b-value (s/mm²)
- `DiffusionGradientDirection`: Gradient direction vector
- `SlicePosition_PCS`: Slice position in patient coordinate system
- `ImaAbsTablePosition`: Absolute table position
- `ImaRelTablePosition`: Relative table position

## Tips and Best Practices

1. **Always check manufacturer**: Verify the DICOM is from Siemens before parsing CSA headers
   ```python
   if 'SIEMENS' not in dcm.Manufacturer.upper():
       raise ValueError("Not a Siemens file")
   ```

2. **Handle missing tags gracefully**: Not all Siemens files have all CSA tags
   ```python
   b_value = csa_info.get('B_value', None)
   if b_value is None:
       print("No b-value found (not a DWI scan)")
   ```

3. **Check CSA header type**: CSA headers come in Type 1 and Type 2 formats
   ```python
   csa = CsaHeader(data)
   print(f"CSA Type: {csa.csa_type}")
   ```

4. **Parse ASCCONV carefully**: The protocol dictionary is deeply nested
   ```python
   if 'sDiffusion' in protocol:
       if 'lDiffDirections' in protocol['sDiffusion']:
           n_dirs = protocol['sDiffusion']['lDiffDirections']
   ```

5. **Validate extracted values**: CSA headers can contain unexpected data
   ```python
   slice_times = csa_info.get('MosaicRefAcqTimes', [])
   if not isinstance(slice_times, list):
       slice_times = [slice_times]
   ```

## Contributing Examples

Have a useful integration pattern? Consider contributing!

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

Examples should:
- Be well-documented with docstrings
- Include error handling
- Show realistic use cases
- Be runnable with minimal setup
- Include example output

## Additional Resources

- [NiBabel Documentation](https://nipy.org/nibabel/)
- [PyDICOM Documentation](https://pydicom.github.io/)
- [DICOM Standard](https://www.dicomstandard.org/)
- [Siemens CSA Header Format](https://nipy.org/nibabel/dicom/siemens_csa.html)
