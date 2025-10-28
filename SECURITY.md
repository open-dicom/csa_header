# Security Policy

## Supported Versions

We provide security updates for the following versions of csa_header:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

The csa_header team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by email to the project maintainer. You can find the maintainer contact information in the `pyproject.toml` file under the `[project]` section.

Please include the following information in your report:

- **Type of vulnerability** (e.g., buffer overflow, injection, authentication bypass)
- **Full paths of source file(s)** related to the vulnerability
- **Location of the affected source code** (tag/branch/commit or direct URL)
- **Step-by-step instructions to reproduce** the issue
- **Proof-of-concept or exploit code** (if possible)
- **Impact of the vulnerability** (what an attacker could achieve)
- **Suggested fix** (if you have one)

### Response Timeline

You can expect the following response timeline:

- **Initial Response**: Within 48 hours of your report
- **Status Update**: Within 7 days with either:
  - Confirmation of the issue and estimated fix timeline
  - Request for additional information
  - Explanation if the report is not accepted as a security issue
- **Fix Release**: Depending on severity:
  - **Critical**: Within 7 days
  - **High**: Within 14 days
  - **Medium**: Within 30 days
  - **Low**: Next scheduled release

### Security Update Process

When a security vulnerability is confirmed:

1. We will acknowledge receipt of your report
2. We will confirm the vulnerability and determine its severity
3. We will develop and test a fix
4. We will prepare a security advisory
5. We will release a patched version
6. We will publish the security advisory with credit to the reporter (if desired)

### Public Disclosure

We follow a **coordinated disclosure** process:

- Security issues will be disclosed publicly only after a fix is released
- We will credit reporters in the security advisory (unless anonymity is requested)
- We request that reporters allow us reasonable time to fix issues before public disclosure

### Security Best Practices for Users

When using csa_header:

1. **Always use the latest version** with security updates
2. **Validate input data** - csa_header parses binary CSA headers from DICOM files, which could potentially be malformed or malicious
3. **Handle exceptions** - wrap csa_header calls in appropriate error handling
4. **Sanitize outputs** - if displaying parsed CSA data to users, ensure proper sanitization
5. **Monitor dependencies** - keep numpy and pydicom up to date with their security patches

### Security Features

csa_header includes the following security-conscious features:

- **Bounds checking**: The Unpacker class validates buffer bounds to prevent overreach
- **Type validation**: Strict type checking with mypy in strict mode
- **Error handling**: Comprehensive exception handling for malformed data
- **No dynamic code execution**: The parser does not use `eval()` or similar functions (except for controlled AST parsing of ASCCONV protocol text)

## Acknowledgments

We thank all security researchers who help keep csa_header and its users safe.
