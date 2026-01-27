# Changelog

All notable changes to the ERCOT API Query Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-27

### Added
- Initial release of ERCOT API Query Tool
- Main query script (`ercot_query.py`) with comprehensive inline documentation
- Automatic authentication and token refresh (30-minute expiry handling)
- Bearer token management system
- Flexible JSON-based query configuration system
- Support for unlimited query parameters
- Automatic output directory creation
- Environment variable management using `.env` file
- Security features (`.gitignore` prevents credential commits)
- Three example query configurations:
  - Real-time system load
  - Settlement point prices
  - Wind power production
- Comprehensive documentation:
  - README.md (main documentation)
  - QUICKSTART.md (5-minute getting started guide)
  - TROUBLESHOOTING.md (common issues and solutions)
  - EXAMPLES.md (practical usage examples)
  - LICENSE (MIT License)
- Python dependencies management (requirements.txt)
- Command-line interface with argparse
- Verbose mode option
- Response validation and error handling
- File size reporting on save
- JSON response pretty-printing

### Features
- ✅ Automatic token refresh before expiry
- ✅ Flexible parameter support (reads all parameters from config)
- ✅ Secure credential storage
- ✅ Detailed logging and status messages
- ✅ Cross-platform compatibility (Linux, Mac, Windows)
- ✅ Virtual environment support
- ✅ Well-commented code for code-aware non-developers

---

## [Unreleased]

### Planned Features
- Add support for pagination for large datasets
- Add data validation before saving
- Add support for CSV output format
- Add query history tracking
- Add data visualization examples
- Add unit tests
- Add CI/CD pipeline
- Add Docker support
- Add configuration validation schema

---

## Version History

- **1.0.0** (2025-01-27): Initial release

---

## How to Update

When pulling updates from the repository:

```bash
# Pull latest changes
git pull origin main

# Update dependencies (if requirements.txt changed)
pip3 install -r requirements.txt --upgrade

# Review CHANGELOG.md for breaking changes
```

---

## Contributing

When contributing, please:
1. Update this CHANGELOG.md with your changes
2. Follow the format: [Version] - YYYY-MM-DD
3. Categorize changes: Added, Changed, Deprecated, Removed, Fixed, Security
4. Include example usage for new features
