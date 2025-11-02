# XA Enhanced DICOM Analysis - Issue #31

## Summary

XA Enhanced DICOM files (syngo MR XA30, XA60, etc.) store Siemens protocol data in a different format and location compared to standard Siemens DICOMs.

## Key Findings

### 1. Data Location Differences

**Standard Siemens DICOMs:**
- CSA Image Header: `(0x0029, 0x1010)`
- CSA Series Header: `(0x0029, 0x1020)`

**XA Enhanced DICOMs:**
- No CSA tags at `(0x0029, 0x1010)` or `(0x0029, 0x1020)`
- Protocol data stored in: `SharedFunctionalGroupsSequence[0][(0x0021, 0x10FE)][0][(0x0021, 0x1019)]`

### 2. Data Format Differences

**Standard Siemens DICOMs:**
- Binary CSA format (Type 1 or Type 2 with "SV10" signature)
- Contains structured binary data with check bits (77 or 205)
- Parsed by `CsaHeader` class

**XA Enhanced DICOMs:**
- **XProtocol format** (ASCII/XML-like text)
- Starts with `<XProtocol>` tag
- Contains ASCCONV-style parameters
- **Already parseable by `CsaAsciiHeader` class!**

### 3. Sample XProtocol Data Structure

```
<XProtocol>
{
  <Name> "PhoenixMetaProtocol"
  <ID> 1000002
  <Userversion> 2.0

  <ParamMap."">
  {
    <ParamLong."Count"> { ... }
    <ParamString."Protocol0"> { ... }
    ...
  }
}
```

## Test Data

Sample XA files downloaded and stored in:
- `tests/files/xa_enhanced/xa30_sample.dcm` (XA30 - Siemens MAGNETOM Prisma Fit)
- `tests/files/xa_enhanced/xa60_sample.dcm` (XA60 - Siemens MAGNETOM Terra.X)

Full test repositories cloned to:
- `tests/files/xa_enhanced/xa30_repo/` (https://github.com/neurolabusc/dcm_qa_xa30)
- `tests/files/xa_enhanced/xa60_repo/` (https://github.com/neurolabusc/dcm_qa_xa60)

## Solution Approach

The library already has the components needed to support XA Enhanced DICOMs:

1. **`CsaAsciiHeader`** class can successfully parse XProtocol data
2. Just need to update `CsaHeader.from_dicom()` to:
   - Detect XA Enhanced DICOMs (check for SharedFunctionalGroupsSequence)
   - Extract XProtocol data from the correct tag sequence
   - Return `CsaAsciiHeader` instance instead of `CsaHeader` instance

## Implementation Plan

1. Modify `CsaHeader.from_dicom()` method:
   - Add XA Enhanced DICOM detection
   - Extract XProtocol data from SharedFunctionalGroupsSequence
   - Return appropriate parser (CsaHeader for binary, CsaAsciiHeader for XProtocol)

2. Add comprehensive tests for XA Enhanced support

3. Update documentation to list XA Enhanced as supported format

## Example Usage (Post-Implementation)

```python
import pydicom
from csa_header import CsaHeader

# Load XA Enhanced DICOM
dcm = pydicom.dcmread('xa_enhanced.dcm')

# This will now work and return a CsaAsciiHeader instance
header = CsaHeader.from_dicom(dcm, 'image')  # or 'series'
parsed = header.parsed  # Access parsed protocol data

# Example: Get slice information
n_slices = header.parsed['sSliceArray']['lSize']
```

## Original Error

When trying to parse XProtocol data as binary CSA:
```
CsaReadError: CSA element #0 has an invalid check bit value: 1632648224!
Valid values are {205, 77}
```

This occurred because the ASCII characters `<XProtocol>` were being interpreted as binary integers.
