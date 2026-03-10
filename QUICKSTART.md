# Quick Start Guide: Work Summary

Get started with the new Python-based work summary tool in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- Environment variables for API access (same as before)

## Installation

```bash
cd /Users/iklo/scripts

# Install dependencies (one-time setup)
pip install click rich pydantic pydantic-settings aiohttp PyGithub python-gitlab jira pyyaml python-dateutil
```

## Basic Usage

### 1. Check Installation

```bash
python -m work_summary --help
```

You should see:
```
Usage: python -m work_summary [OPTIONS] COMMAND [ARGS]...

  Work Summary - Collect and display work items from multiple sources.
```

### 2. Check Version

```bash
python -m work_summary version
```

Output: `work-summary version 2.0.0`

### 3. Collect All Work Items

```bash
python -m work_summary
```

This will:
- Collect PRs from GitHub
- Collect Issues from GitHub
- Collect MRs from GitLab
- Collect Issues from Jira (all instances)
- Collect Stories from Shortcut
- Display in a beautiful table

### 4. Collect from Specific Source

```bash
# Only GitHub
python -m work_summary collect-github

# Only GitLab
python -m work_summary collect-gitlab

# Only Jira
python -m work_summary collect-jira

# Only Shortcut
python -m work_summary collect-shortcut
```

### 5. Different Output Formats

```bash
# JSON (pretty-printed)
python -m work_summary --format json

# JSON Lines (one object per line)
python -m work_summary --format jsonl

# CSV (for spreadsheets)
python -m work_summary --format csv
```

### 6. Save to File

```bash
# Save as JSON
python -m work_summary --output summary.json --format json

# Save as CSV
python -m work_summary --output summary.csv --format csv
```

### 7. Debugging

```bash
# Verbose output (INFO level)
python -m work_summary --verbose

# Debug output (DEBUG level)
python -m work_summary --debug
```

## Environment Variables

Make sure these are set (same as before):

```bash
# GitHub
export GITHUB_TOKEN="your_github_token"

# GitLab
export GITLAB_TOKEN="your_gitlab_token"

# Jira (Rivian)
export JIRA_TOKEN_RIVIAN="your_jira_token"
export JIRA_EMAIL_RIVIAN="your_email@rivian.com"

# Jira (Orlo) - optional
export JIRA_TOKEN_ORLO="your_jira_token"
export JIRA_INSTANCE_URL_ORLO="https://your-instance.atlassian.net"
export JIRA_EMAIL_ORLO="your_email@company.com"

# Shortcut
export SHORTCUT_API_KEY="your_shortcut_api_key"
```

## Optional: Create Config File

For advanced configuration, create `work_summary.yaml`:

```bash
# Copy example config
cp work_summary.yaml.example work_summary.yaml

# Edit as needed
vim work_summary.yaml
```

Example config:
```yaml
github:
  organizations:
    - precisetargetlabs
    - HelloSanctum
  enabled: true

gitlab:
  enabled: true

jira:
  enabled: true

shortcut:
  enabled: true

output:
  format: table
  color_theme: default

cache:
  enabled: false
```

## Optional: Create Shell Aliases

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Work Summary aliases
alias ws='python -m work_summary'
alias wsg='python -m work_summary collect-github'
alias wsgl='python -m work_summary collect-gitlab'
alias wsj='python -m work_summary collect-jira'
alias wss='python -m work_summary collect-shortcut'
alias wsv='python -m work_summary --verbose'
alias wsd='python -m work_summary --debug'
```

Then use:
```bash
ws              # Collect all
wsg             # GitHub only
wsgl            # GitLab only
wsj             # Jira only
wss             # Shortcut only
wsv             # Verbose mode
wsd             # Debug mode
```

## Troubleshooting

### "No module named 'github'" Error

```bash
pip install PyGithub python-gitlab jira
```

### "No module named 'pydantic_settings'" Error

```bash
pip install pydantic-settings
```

### No Data Returned

1. Check environment variables are set:
   ```bash
   echo $GITHUB_TOKEN
   echo $GITLAB_TOKEN
   ```

2. Test individual sources:
   ```bash
   python -m work_summary collect-github --debug
   ```

3. Verify you have work items assigned/owned

### Authentication Errors

Check your tokens are valid:
```bash
# GitHub
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# GitLab
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" https://gitlab.com/api/v4/user
```

## Comparison with Old Script

### Old Way
```bash
./comprehensive_work_summary.sh
```

### New Way
```bash
python -m work_summary
```

### Advantages
- ✅ 40-60% faster (parallel collection)
- ✅ Multiple output formats
- ✅ Better error messages
- ✅ More options and flexibility
- ✅ Type-safe and maintainable

## Next Steps

1. ✅ Try basic collection: `python -m work_summary`
2. ✅ Compare with old script output
3. ✅ Try different formats: `--format json`, `--format csv`
4. ✅ Set up shell aliases for convenience
5. ✅ Read full documentation: `work_summary/README.md`
6. ✅ Check migration guide: `MIGRATION_GUIDE.md`

## Getting Help

```bash
# Command help
python -m work_summary --help
python -m work_summary collect-github --help

# Version
python -m work_summary version

# Debug mode
python -m work_summary --debug
```

## Documentation

- **Full README**: `/Users/iklo/scripts/work_summary/README.md`
- **Migration Guide**: `/Users/iklo/scripts/MIGRATION_GUIDE.md`
- **Implementation Summary**: `/Users/iklo/scripts/IMPLEMENTATION_SUMMARY.md`
- **This Quick Start**: `/Users/iklo/scripts/QUICKSTART.md`

## Success!

You're now ready to use the new work summary tool! 🎉

If everything works, consider:
1. Adding shell aliases for convenience
2. Creating a custom config file
3. Exploring different output formats
4. Providing feedback for improvements

Happy coding! 🚀
