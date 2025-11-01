# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2025-11-01

### 🔥 Breaking Changes

#### Removed redundant 'index' field from parsed CSA tags

**What changed:**
- The `'index'` field has been removed from each tag dictionary returned by `CsaHeader.read()`
- Tags now contain only: `'VR'` (Value Representation), `'VM'` (Value Multiplicity), and `'value'`

**Why:**
- The `'index'` field was redundant with Python's guaranteed dict ordering (Python 3.7+)
- Since the minimum supported Python version is 3.9, dict insertion order is guaranteed by the language
- This simplifies the API and follows the DRY (Don't Repeat Yourself) principle
- Resolves issue #15

**Migration guide:**

Before (v1.x):
```python
parsed = CsaHeader(raw_csa).read()
for tag_name, tag_data in parsed.items():
    idx = tag_data['index']  # Direct access to index field
    print(f"Tag {idx}: {tag_name}")
```

After (v2.0):
```python
parsed = CsaHeader(raw_csa).read()
for idx, (tag_name, tag_data) in enumerate(parsed.items(), 1):
    print(f"Tag {idx}: {tag_name}")
```

**Note:** Tag ordering is preserved via Python's dict insertion order (guaranteed since Python 3.7). Tags appear in the same sequential order as they do in the CSA header.

### Added
- Comprehensive docstring for `CsaHeader.read()` method explaining dict ordering guarantees
- Migration examples in CHANGELOG showing how to enumerate tags if explicit indices are needed

### Changed
- Simplified tag structure from `{'index': int, 'VR': str, 'VM': int, 'value': Any}` to `{'VR': str, 'VM': int, 'value': Any}`
- Updated README examples to reflect new tag structure without 'index' field
- Updated test suite to verify tags no longer contain 'index' field

## [1.0.1] - 2025-10-28

### Fixed
- **Python 3.9 compatibility**: Added `from __future__ import annotations` to ensure compatibility with Python 3.9
- **Linting violations**: Resolved 11 ruff violations from pre-commit.ci
  - Removed unused imports (`Iterable`, `pytest`)
  - Fixed unused variable assignments (F841, B007)
  - Replaced inefficient list slicing with `next(iter())` (RUF015)
  - Replaced blind exception catching with specific exception types (B017)
- **Code style**: Auto-fixed quote style consistency (Q000) and `__slots__` sorting (RUF023)

### Changed
- **Performance**: Added `__slots__` to classes for memory efficiency and faster attribute access
- **Code quality**: Comprehensive refactoring to improve maintainability
  - Better error handling with specific exception types
  - More Pythonic iteration patterns
  - Cleaner variable naming conventions
- **Code of conduct**: Replaced Contributor Covenant v2.1 with a community-focused code of conduct inspired by the NIPY community standards
- **Examples**: Added per-file-ignores for `examples/**/*` to allow simpler, more readable code patterns

## [1.0.0] - 2025-10-28

### 🎉 First Stable Release

This is the first production-ready release of `csa_header`. The package has undergone a comprehensive modernization and now provides a robust, well-tested foundation for parsing Siemens CSA headers in medical imaging workflows.

### Added

#### Testing
- **Comprehensive test suite**: 161 tests covering all core functionality
- **96% test coverage**: All critical parsing code at 100% coverage
  - `header.py`: 25% → 100% (75 new tests)
  - `unpacker.py`: 23% → 100% (63 new tests)
  - `utils.py`: 40% → 100%
- **Real DICOM data tests**: Integration tests with actual CSA headers
- **All VR types tested**: IS, DS, FL, FD, SS, US, SL, UL, UN, string types
- **Error handling tests**: Comprehensive edge case and malformed data testing

#### Documentation
- **CONTRIBUTING.md**: Complete contributor guide with development setup, code style, testing requirements, and PR process
- **CODE_OF_CONDUCT.md**: Contributor Covenant v2.1 for community standards
- **GitHub issue templates**: Bug report, feature request, and question templates
- **Pull request template**: Comprehensive PR checklist for quality assurance
- **Enhanced README**: Advanced usage examples, NiBabel integration guide, feature highlights
- **Examples directory**: Complete NiBabel integration examples with runnable scripts

#### Community Infrastructure
- GitHub Actions CI/CD with Python 3.9-3.13 testing
- Pre-commit hooks with automatic code formatting and linting
- Codecov integration for coverage tracking
- Issue and PR templates for structured contributions

#### Type Safety
- **Complete type hints**: All public APIs now have comprehensive type annotations
- **Modern type syntax**: Uses Python 3.10+ union syntax (`X | Y`)
- **Zero mypy errors**: Full type checking compliance

#### Python Support
- **Python 3.12 support**: Added to test matrix
- **Python 3.13 support**: Added to test matrix
- **Dropped Python 3.7-3.8**: Minimum version is now Python 3.9

### Changed

#### Code Quality
- **Modernized type annotations**: Replaced `Union[X, Y]` with `X | Y`, `Optional[X]` with `X | None`
- **Improved code organization**: Better separation of concerns in test suite
- **Enhanced error messages**: More descriptive error reporting

#### Tooling
- **Updated pre-commit hooks**:
  - pre-commit-hooks: v4.4.0 → v6.0.0
  - black: 23.3.0 → 25.9.0 (moved to mirror repo)
  - ruff: v0.0.272 → v0.14.2 (moved to astral-sh org)
- **Modernized ruff configuration**: Migrated to new `[tool.ruff.lint]` structure
- **Fixed ruff command syntax**: Updated to `ruff check` from deprecated `ruff`
- **GitHub Actions updates**: checkout@v4, setup-python@v5, codecov@v4

#### Testing Infrastructure
- **Test organization**: Better structured test classes with clear naming
- **Fixture improvements**: More efficient test data loading
- **Coverage reporting**: Enhanced coverage reports with branch coverage

### Removed
- **Python 3.8 compatibility code**: Removed dead code branches for ast.Constant handling
- **Python 3.7-3.8 support**: No longer tested or officially supported
- **Deprecated imports**: Cleaned up unused `Union` and `Optional` imports

### Fixed
- **Type errors**: Resolved all 7 mypy errors in codebase
- **AST parsing**: Fixed subscript handling for Python 3.9+
- **Ruff deprecation warnings**: Updated configuration to eliminate warnings

### Security
- No known security issues
- All dependencies up to date
- Pre-commit hooks include security checks (detect-private-key)

## [0.0.1] - 2023-06-XX

### Initial Beta Release
- Basic CSA header parsing functionality
- Support for CSA Type 1 and Type 2 headers
- ASCCONV protocol parsing
- Integration with pydicom
- Initial test coverage (~59%)

---

## Release Notes

### 1.0.0 Migration Guide

#### No Breaking Changes
Version 1.0.0 maintains full backward compatibility with 0.0.1. All existing code will continue to work without modifications.

#### Recommended Updates

1. **Update Python version**: Minimum is now Python 3.9
   ```bash
   # Verify your Python version
   python --version  # Should be 3.9+
   ```

2. **Update type hints** (if you're using them):
   ```python
   # Old style
   from typing import Union, Optional
   def func(x: Optional[int]) -> Union[str, int]:
       pass

   # New style (Python 3.10+)
   def func(x: int | None) -> str | int:
       pass
   ```

3. **Leverage new examples**:
   ```bash
   # Check out the NiBabel integration example
   python examples/nibabel_integration.py your_dicom.dcm
   ```

### For Contributors

If you're contributing to the project, note the new requirements:
- **Test coverage**: Maintain 90%+ coverage for new code
- **Type hints**: All public APIs must have complete type annotations
- **Commit messages**: Follow Conventional Commits specification
- **Pre-commit hooks**: Must pass all checks before committing

See [CONTRIBUTING.md](CONTRIBUTING.md) for complete guidelines.

### Acknowledgments

This release represents a complete modernization of the package. Special thanks to:
- The NiBabel team for their excellent CSA header documentation
- The PyDICOM community for DICOM parsing infrastructure
- All contributors who filed issues and provided feedback

### What's Next (Future Releases)

Potential features for future releases:
- CSA header writing support (currently read-only)
- Support for additional Siemens private tags
- Performance optimizations for large batch processing
- Extended ASCCONV parameter documentation
- Additional integration examples (MONAI, SimpleITK, dcmstack)

---

[1.0.1]: https://github.com/open-dicom/csa_header/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/open-dicom/csa_header/compare/v0.0.1...v1.0.0
[0.0.1]: https://github.com/open-dicom/csa_header/releases/tag/v0.0.1
