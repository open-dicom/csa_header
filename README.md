# CSA Header

Parse CSA header information from Siemens MRI acquisitions with Python.

[![PyPI - Version](https://img.shields.io/pypi/v/csa_header.svg)](https://pypi.org/project/csa_header)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/csa_header.svg)](https://pypi.org/project/csa_header)
[![Tests](https://github.com/open-dicom/csa_header/actions/workflows/tests.yml/badge.svg)](https://github.com/open-dicom/csa_header/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/open-dicom/csa_header/branch/main/graph/badge.svg)](https://codecov.io/gh/open-dicom/csa_header)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/open-dicom/csa_header/main.svg)](https://results.pre-commit.ci/latest/github/open-dicom/csa_header/main)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17474448.svg)](https://doi.org/10.5281/zenodo.17474448)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

Some Siemens MRI scans may include CSA headers that provide valuable information about the acquisition and storage of the data. These headers are stored as [private data elements](https://dicom.nema.org/medical/dicom/current/output/html/part05.html#sect_7.8), usually looking something like:

```
(0029, 1010) CSA Image Header Type          OB: 'IMAGE NUM 4'
(0029, 1010) CSA Image Header Version       OB: '20100114'
(0029, 1010) CSA Image Header Info          OB: Array of 11560 bytes
(0029, 1020) CSA Series Header Type         OB: 'MR'
(0029, 1020) CSA Series Header Version      OB: '20100114'
(0029, 1020) CSA Series Header Info         OB: Array of 80248 bytes
```

The _CSA Image Header Info_ and _CSA Series Header Info_ elements contain encoded information which is crucial for the correct interpretation of the associated acquisition data.

> For a detailed explanation on the CSA encoding scheme, please see [this](https://nipy.org/nibabel/dicom/siemens_csa.html) excellent article from [NiBabel](https://github.com/nipy/nibabel)'s documentation site.

## Features

- **Fast and Lightweight**: Minimal dependencies (numpy, pydicom)
- **Comprehensive Parsing**: Supports both CSA header types (Type 1 and Type 2)
- **ASCCONV Support**: Automatic parsing of embedded ASCCONV protocol parameters
- **Type-Safe**: Complete type hints for all public APIs
- **Well-Tested**: 96% test coverage with 161 tests
- **Python 3.9+**: Modern Python with support through Python 3.13
- **NiBabel Compatible**: Integrates seamlessly with neuroimaging workflows

**Table of Contents**

- [Features](#features)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Advanced Usage](#advanced-usage)
  - [Extracting ASCCONV Protocol](#extracting-ascconv-protocol)
  - [Diffusion MRI (DWI) Parameters](#diffusion-mri-dwi-parameters)
  - [Functional MRI (fMRI) Parameters](#functional-mri-fmri-parameters)
- [Integration with NiBabel](#integration-with-nibabel)
- [Examples](#examples)
- [Tests](#tests)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)

## Installation

```console
pip install csa_header
```

### Optional Dependencies

For working with the provided [NiBabel integration examples](#integration-with-nibabel):

```console
pip install csa_header[examples]
```

For development (includes pre-commit hooks and IPython):

```console
pip install csa_header[dev]
```

## Quickstart

Use [`pydicom`](https://github.com/pydicom/pydicom) to read a DICOM header:

```python
>>> import pydicom
>>> dcm = pydicom.dcmread("/path/to/file.dcm")
```

Extract a data element containing a CSA header, e.g., for _CSA Series Header Info_:

```python
>>> data_element = dcm.get((0x29, 0x1020))
>>> data_element
(0029, 1020) [CSA Series Header Info]            OB: Array of 180076 elements
```

Read the raw byte array from the data element:

```python
>>> raw_csa = data_element.value
>>> raw_csa
b'SV10\x04\x03\x02\x01O\x00\x00\x00M\x00\x00\x00UsedPatientWeight\x00      <Visible> "true" \n      \n      <ParamStr\x01\x00\x00\x00IS\x00\x00\x06...'
```

Parse the contents of the CSA header with the `CsaHeader` class:

```python
>>> from csa_header import CsaHeader
>>> parsed_csa = CsaHeader(raw_csa).read()
>>> parsed_csa
{
    'NumberOfPrescans': {'index': 1, 'VR': 'IS', 'VM': 1, 'value': 0},
    'TransmitterCalibration': {'index': 2, 'VR': 'DS', 'VM': 1, 'value': 247.102},
    'PhaseGradientAmplitude': {'index': 3, 'VR': 'DS', 'VM': 1, 'value': 0.0},
    'ReadoutGradientAmplitude': {'index': 4, 'VR': 'DS', 'VM': 1, 'value': 0.0},
    'SelectionGradientAmplitude': {'index': 5, 'VR': 'DS', 'VM': 1, 'value': 0.0},
    'GradientDelayTime': {'index': 6,
    'VR': 'DS',
    'VM': 3,
    'value': [36.0, 35.0, 31.0]},
    'RfWatchdogMask': {'index': 7, 'VR': 'IS', 'VM': 1, 'value': 0},
    'RfPowerErrorIndicator': {'index': 8, 'VR': 'DS', 'VM': 1, 'value': None},
    'SarWholeBody': {'index': 9, 'VR': 'DS', 'VM': 3, 'value': None},
    'Sed': {'index': 10,
    'VR': 'DS',
    'VM': 3,
    'value': [1000000.0, 324.74800987, 324.74800832]}
    ...
}
```

## Advanced Usage

### Extracting ASCCONV Protocol

CSA headers often contain the complete scanner protocol in ASCCONV format under the `MrPhoenixProtocol` tag. This is automatically parsed into a nested dictionary:

```python
>>> parsed_csa = CsaHeader(raw_csa).read()
>>> protocol = parsed_csa.get('MrPhoenixProtocol')
>>> if protocol:
...     # Access protocol parameters
...     tr = protocol['alTR'][0]  # Repetition time
...     te = protocol['alTE'][0]  # Echo time
...     print(f"TR: {tr} ms, TE: {te} ms")
TR: 2000 ms, TE: 30 ms
```

### Diffusion MRI (DWI) Parameters

Extract diffusion-specific parameters for DTI/DWI analysis:

```python
>>> # From image header (0x0029, 0x1020)
>>> image_header = CsaHeader(dcm[0x0029, 0x1020].value).read()
>>> b_value = image_header.get('B_value')
>>> gradient = image_header.get('DiffusionGradientDirection')
>>> print(f"B-value: {b_value}, Gradient: {gradient}")
B-value: 1000, Gradient: [0.707, 0.707, 0.0]
```

### Functional MRI (fMRI) Parameters

Extract slice timing for slice timing correction:

```python
>>> # From series header (0x0029, 0x1010)
>>> series_header = CsaHeader(dcm[0x0029, 0x1010].value).read()
>>> slice_times = series_header.get('MosaicRefAcqTimes')
>>> n_slices = series_header.get('NumberOfImagesInMosaic')
>>> print(f"Slice times: {slice_times[:3]}... ({n_slices} slices)")
Slice times: [0.0, 52.5, 105.0]... (64 slices)
```

## Integration with NiBabel

`csa_header` works seamlessly with [NiBabel](https://nipy.org/nibabel/) for comprehensive neuroimaging workflows:

```python
import nibabel as nib
import pydicom
from csa_header import CsaHeader

# Load DICOM with both pydicom and NiBabel
dcm = pydicom.dcmread('scan.dcm')
nib_img = nib.load('scan.dcm')

# Extract CSA header information
if (0x0029, 0x1010) in dcm:
    csa = CsaHeader(dcm[0x0029, 0x1010].value)
    csa_info = csa.read()

    # Use NiBabel for image data
    data = nib_img.get_fdata()

    # Use CSA for metadata
    slice_times = csa_info.get('MosaicRefAcqTimes', [])

    print(f"Image shape: {data.shape}")
    print(f"Slice timing from CSA: {len(slice_times)} time points")
```

### Use Cases with NiBabel

- **Slice Timing Correction**: Extract `MosaicRefAcqTimes` for accurate fMRI preprocessing
- **Diffusion Imaging**: Get b-values and gradient directions for DTI analysis
- **Protocol Verification**: Confirm acquisition parameters match expected values
- **Quality Assurance**: Extract technical parameters for QA pipelines
- **BIDS Conversion**: Generate complete metadata for BIDS-compliant datasets

See [examples/nibabel_integration.py](examples/nibabel_integration.py) for complete integration examples.

## Examples

The [examples/](examples/) directory contains comprehensive usage examples:

- **[nibabel_integration.py](examples/nibabel_integration.py)**: Complete workflow combining csa_header with NiBabel
  - Extract DWI parameters (b-values, gradients)
  - Extract fMRI parameters (slice timing, TR/TE)
  - Parse ASCCONV protocol parameters
  - Batch processing multiple DICOM files

Run examples:
```bash
python examples/nibabel_integration.py path/to/siemens_dicom.dcm
```

## Tests

This package uses [`hatch`](https://hatch.pypa.io/) to manage development and packaging. To run the tests, simply run:

```
hatch run test
```

### Coverage

To run the tests with [`coverage`](https://coverage.readthedocs.io/), run:

```
hatch run cov
```

Or, to automatically generate an HTML report and open it in your default browser:

```hatch
hatch run cov-show
```

## Contributing

Contributions are welcome! This project is community-maintained and aims to be a reliable tool for the medical imaging community.

### How to Contribute

1. **Report Issues**: Found a bug or have a feature request? [Open an issue](https://github.com/open-dicom/csa_header/issues/new/choose)
2. **Submit Pull Requests**: See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines
3. **Improve Documentation**: Help make the docs better
4. **Share Examples**: Contribute integration examples or use cases

### Development Setup

```bash
# Clone the repository
git clone https://github.com/open-dicom/csa_header.git
cd csa_header

# Install hatch
pip install hatch

# Run tests
hatch run test:test

# Run linting
hatch run lint:all

# Install pre-commit hooks
hatch run pre-commit install
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for complete development guidelines including:
- Code style requirements
- Testing requirements (90%+ coverage)
- Commit message conventions
- Pull request process

## Citation

If you use `csa_header` in your research, please cite it using the following:

**BibTeX:**
```bibtex
@software{baratz_2025_csa_header,
  author       = {Baratz, Zvi and Brett, Matthew},
  title        = {csa_header: Parse CSA header information from Siemens MRI acquisitions},
  year         = 2025,
  publisher    = {Zenodo},
  version      = {v1.0.2},
  doi          = {10.5281/zenodo.17474448},
  url          = {https://doi.org/10.5281/zenodo.17474448}
}
```

**APA:**
```
Baratz, Z., & Brett, M. (2025). csa_header: Parse CSA header information from Siemens MRI acquisitions (v1.0.2). Zenodo. https://doi.org/10.5281/zenodo.17474448
```

For the specific version you're using, please check the [Zenodo record](https://doi.org/10.5281/zenodo.17474448) for the appropriate DOI and citation information.

Alternatively, you can use the [CITATION.cff](CITATION.cff) file in this repository, which is automatically recognized by GitHub and can be imported into reference managers.

## License

`csa_header` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
