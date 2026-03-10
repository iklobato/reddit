# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-12

### Added

- Complete rewrite in Python from bash script
- Modern CLI using Click framework
- Async data collection with asyncio
- Type-safe data models using Pydantic
- Configuration management with Pydantic Settings
- Multiple output formats: table, JSON, JSON Lines, CSV
- Rich terminal tables with colors
- HTTP client with retry logic and rate limiting
- Optional file-based caching
- Comprehensive error handling
- Logging support with multiple levels
- Support for multiple Jira instances
- GitHub collector using PyGithub
- GitLab collector using python-gitlab
- Jira collector using jira library
- Shortcut collector using REST API
- Modular architecture for easy extension
- Full test coverage structure
- Documentation and examples

### Changed

- Replaced bash script with Python package
- Replaced CLI tools (gh, glab) with Python libraries
- Improved performance with parallel API calls
- Better error messages and debugging
- Simplified configuration format (YAML)

### Removed

- Bash script `comprehensive_work_summary.sh`
- Python helper `format_tables.py`
- Dependency on `gh` CLI tool
- Dependency on `glab` CLI tool
- Dependency on `jq` for JSON parsing

### Migration Guide

#### From v1.x (Bash Script)

1. **Environment Variables**: Same as before, no changes needed
2. **Configuration**: Create `work_summary.yaml` (optional, can use env vars)
3. **Command**: Use `work-summary` instead of `./comprehensive_work_summary.sh`
4. **Output**: Similar format but with improved colors and layout

#### Example Migration

Before (v1.x):
```bash
./comprehensive_work_summary.sh
```

After (v2.0):
```bash
work-summary
# or
python -m work_summary
```

## [1.0.0] - 2025-XX-XX

### Initial Release

- Bash script for collecting work items
- Support for GitHub, GitLab, Jira, Shortcut
- Python helper for table formatting
- Basic configuration via environment variables
