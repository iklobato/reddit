# Work Summary

A modern Python tool for collecting and displaying work items from multiple sources.

## Features

- **Multiple Sources**: Collect work items from GitHub, GitLab, Jira, and Shortcut
- **Async Collection**: Fast parallel data collection using asyncio
- **Beautiful Output**: Rich terminal tables with colors
- **Multiple Formats**: Output as tables, JSON, JSON Lines, or CSV
- **Type Safe**: Full type hints with Pydantic models
- **Configurable**: YAML config files and environment variables
- **Caching**: Optional caching to reduce API calls
- **Extensible**: Easy to add new collectors and formatters

## Installation

```bash
# Install dependencies
uv pip install -e .

# Or install from pyproject.toml
uv sync
```

## Quick Start

```bash
# Collect from all sources and display as table
python -m work_summary

# Or use the installed command
work-summary

# Collect only from GitHub
work-summary collect-github

# Output as JSON
work-summary --format json

# Save to file
work-summary --output summary.json --format json

# Use custom config
work-summary --config ~/.config/work_summary/config.yaml
```

## Configuration

### Environment Variables

```bash
# GitHub
export GITHUB_TOKEN="your_github_token"

# GitLab
export GITLAB_TOKEN="your_gitlab_token"

# Jira (Rivian)
export JIRA_TOKEN_RIVIAN="your_jira_token"
export JIRA_EMAIL_RIVIAN="your_email@rivian.com"

# Jira (Orlo)
export JIRA_TOKEN_ORLO="your_jira_token"
export JIRA_INSTANCE_URL_ORLO="https://your-instance.atlassian.net"
export JIRA_EMAIL_ORLO="your_email@company.com"

# Shortcut
export SHORTCUT_API_KEY="your_shortcut_api_key"
```

### Configuration File

Create a `work_summary.yaml` file:

```yaml
github:
  organizations:
    - precisetargetlabs
    - HelloSanctum
  repos:
    - almagest
    - monarch
    - python-libs
    - pyxis
  project_number: 14
  enabled: true

gitlab:
  organizations:
    - rivian
  enabled: true

jira:
  enabled: true
  instances:
    - name: custom
      url: https://your-instance.atlassian.net
      email: your_email@company.com
      token: your_token
      company: your_company

shortcut:
  api_key: your_api_key
  enabled: true

output:
  format: table  # table, json, jsonl, csv
  color_theme: default  # default, dark, light, none

cache:
  enabled: false
  ttl: 300  # seconds
```

## Usage Examples

### Basic Usage

```bash
# Collect and display all work items
work-summary

# Verbose output
work-summary --verbose

# Debug mode
work-summary --debug
```

### Filtering by Source

```bash
# Only GitHub
work-summary collect-github

# Only GitLab
work-summary collect-gitlab

# Only Jira
work-summary collect-jira

# Only Shortcut
work-summary collect-shortcut
```

### Output Formats

```bash
# Table (default)
work-summary --format table

# Pretty JSON
work-summary --format json

# JSON Lines (one object per line)
work-summary --format jsonl

# CSV for spreadsheets
work-summary --format csv
```

### Advanced Options

```bash
# Disable colors
work-summary --no-color

# Enable caching
work-summary  # (configure in config file)

# Custom config file
work-summary --config ~/my-config.yaml

# Save output to file
work-summary --output summary.json --format json
```

## Architecture

### Project Structure

```
work_summary/
├── __init__.py           # Package initialization
├── __main__.py           # Entry point (python -m work_summary)
├── cli.py                # CLI interface using Click
├── config.py             # Configuration management
├── models.py             # Data models (Task, WorkSummary, etc.)
├── collectors/           # Data collectors
│   ├── __init__.py
│   ├── base.py          # Base collector class
│   ├── github.py        # GitHub collector
│   ├── gitlab.py        # GitLab collector
│   ├── jira.py          # Jira collector
│   └── shortcut.py      # Shortcut collector
├── formatters/           # Output formatters
│   ├── __init__.py
│   ├── base.py          # Base formatter class
│   ├── table.py         # Table formatter (rich)
│   ├── json.py          # JSON formatter
│   └── csv.py           # CSV formatter
├── utils/                # Utilities
│   ├── __init__.py
│   ├── colors.py        # ANSI color utilities
│   ├── http.py          # HTTP client utilities
│   └── cache.py         # Caching layer
└── tests/                # Tests
    └── __init__.py
```

### Key Components

#### Models

- `Task`: Base model for all work items
- `PullRequest`: GitHub/GitLab PRs/MRs
- `Issue`: GitHub Issues
- `JiraCard`: Jira tickets
- `ShortcutStory`: Shortcut stories
- `WorkSummary`: Container for all tasks

#### Collectors

- `BaseCollector`: Abstract base with common functionality
- `GitHubCollector`: Collects PRs, Issues, and Project items
- `GitLabCollector`: Collects Merge Requests
- `JiraCollector`: Collects issues from multiple instances
- `ShortcutCollector`: Collects stories

#### Formatters

- `BaseFormatter`: Abstract base for formatters
- `TableFormatter`: Rich terminal tables with colors
- `JSONFormatter`: Pretty-printed JSON
- `JSONLinesFormatter`: JSON Lines format
- `CSVFormatter`: CSV for spreadsheets

## Development

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=work_summary
```

### Code Quality

```bash
# Format code
black work_summary/

# Lint
ruff check work_summary/

# Type checking
mypy work_summary/
```

## Migration from Bash Script

The new Python version replaces `comprehensive_work_summary.sh` and `format_tables.py`.

### Key Improvements

1. **70% Less Code**: ~600 lines vs 1,967 lines
2. **Type Safety**: Full type hints with Pydantic
3. **Async**: Parallel API calls for better performance
4. **Modular**: Easy to extend and test
5. **Better Errors**: Clear, actionable error messages
6. **Multiple Formats**: JSON, CSV, and more

### Breaking Changes

- Configuration format changed (YAML instead of bash variables)
- Output format slightly different (using rich tables)
- No longer uses `gh` and `glab` CLI tools (uses Python libraries)

### Migration Steps

1. Set environment variables (same as before)
2. Create `work_summary.yaml` config file (optional)
3. Run `work-summary` instead of `./comprehensive_work_summary.sh`

## Troubleshooting

### Authentication Issues

```bash
# Check tokens are set
echo $GITHUB_TOKEN
echo $GITLAB_TOKEN
echo $JIRA_TOKEN_RIVIAN

# Test GitHub auth
work-summary collect-github --debug

# Test GitLab auth
work-summary collect-gitlab --debug
```

### No Data Returned

- Check that you have work items assigned/owned
- Verify organization/repo names in config
- Use `--debug` flag to see API calls
- Check API rate limits

### Performance Issues

- Enable caching: set `cache.enabled: true` in config
- Reduce number of repos/orgs in config
- Use source-specific commands (e.g., `collect-github`)

## API Documentation

### Programmatic Usage

```python
import asyncio
from work_summary.config import AppConfig
from work_summary.collectors import GitHubCollector
from work_summary.formatters import TableFormatter
from work_summary.models import WorkSummary

async def main():
    # Load config
    config = AppConfig()
    
    # Create collector
    collector = GitHubCollector(config=config.github)
    await collector.start()
    
    # Collect tasks
    tasks = await collector.collect()
    
    # Create summary
    summary = WorkSummary(tasks=tasks)
    
    # Format output
    formatter = TableFormatter()
    output = formatter.format(summary)
    print(output)
    
    # Cleanup
    await collector.close()

asyncio.run(main())
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run code quality checks
6. Submit a pull request

## License

MIT License - see LICENSE file for details

## Authors

- Henrique Lobato

## Acknowledgments

- Original bash script: `comprehensive_work_summary.sh`
- Original Python helper: `format_tables.py`
