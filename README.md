# CSA Header

Parse CSA header information from Siemens MRI acquisitions with Python.

[![PyPI - Version](https://img.shields.io/pypi/v/csa_header.svg)](https://pypi.org/project/csa_header)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/csa_header.svg)](https://pypi.org/project/csa_header)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/open-dicom/csa_header/main.svg)](https://results.pre-commit.ci/latest/github/open-dicom/csa_header/main)

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

**Table of Contents**

- [Installation](#installation)
- [Quickstart](#quickstart)
- [Tests](#tests)
- [License](#license)

## Installation

```console
pip install csa_header
```

## Quickstart

Use [`pydicom`](https://github.com/pydicom/pydicom) to read a DICOM header:

```python
>>> import pydicom
>>> dcm = pydicom.dcmread("/path/to/file.dcm")
```

Extract a data element containing a CSA header, e.g., for _CSA Series Header Info_:

```python
>>> date_element = dcm.get((0x29, 0x1020))
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

## License

`csa_header` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
