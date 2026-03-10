# Upfluence Unified Scraper Tool

## Overview
A unified command-line tool for extracting influencer data from Upfluence/Wednesday platform. Consolidates 4 separate scripts into one organized tool with subcommands.

## Quick Start

```bash
# 1. Set authentication token
export UPFLUENCE_BEARER_TOKEN="your_token_here"

# 2. Run basic search (most common use)
python upfluence.py search --output influencers.csv --limit 100

# 3. Export full contact details
python upfluence.py export --output contacts.csv --workers 32
```

## Installation & Setup

### Prerequisites
- Python 3.7+
- `requests` library (`pip install requests`)
- `python-dotenv` library (`pip install python-dotenv`)

### Authentication
```bash
# Set token as environment variable
export UPFLUENCE_BEARER_TOKEN="your_upfluence_bearer_token"

# Or create a .env file
echo "UPFLUENCE_BEARER_TOKEN=your_token" > .env
```

## Commands Reference

### 1. `search` - Find and Extract Influencers
Searches for influencers matching filters, unlocks their details, and saves to CSV.

```bash
# Basic search with default filters
python upfluence.py search --output influencers.csv

# Search with custom keywords
python upfluence.py search --keywords "Fintech,Trading,APIs" --limit 50

# Append to existing file
python upfluence.py search --output existing.csv --limit 200

# Use different filter configuration
python upfluence.py search --filters custom_filters.json

# Override list ID
python upfluence.py search --list-id "123456"
```

**Options:**
- `-o, --output`: Output CSV file (default: timestamp_upfluence_influencers.csv)
- `-l, --limit`: Maximum influencers to process
- `--per-page`: Matches per API page (default: 100)
- `--keywords`: Comma-separated search keywords
- `--filters`: Custom filters JSON file (default: filters.json)
- `--list-id`: Override list ID from filters

### 2. `export` - Export Full Contact Details
Exports complete influencer information with all available fields.

```bash
# Full export with parallel processing
python upfluence.py export --output contacts.csv --workers 64

# Limited export for testing
python upfluence.py export --limit 10 --output test.csv

# Export with custom filters
python upfluence.py export --filters strict_filters.json
```

**Options:**
- `-o, --output`: Output CSV file (default: upfluence_contacts.csv)
- `-w, --workers`: Concurrent unlock workers (default: 64)
- `-l, --limit`: Limit to first N influencers
- `--per-page`: Matches per API page (default: 100)

### 3. `remove` - Manage Community List
Removes influencers from the community list (changes status to "rejected").

```bash
# Dry run to see what would be removed
python upfluence.py remove --dry-run

# Actually remove influencers
python upfluence.py remove

# Remove from specific CSV file
python upfluence.py remove --from-file entries.csv
```

**Options:**
- `--from-file`: CSV with list_entry_id,influencer_id columns
- `--dry-run`: List without removing
- `--filters`: Custom filters for list ID
- `--list-id`: Override list ID

### 4. `cleanup` - Delete List Entries
Permanently deletes list entries from Upfluence.

```bash
# Delete both selected and rejected entries
python upfluence.py cleanup --status selected,rejected

# Dry run to preview deletions
python upfluence.py cleanup --dry-run

# Delete only rejected entries
python upfluence.py cleanup --status rejected
```

**Options:**
- `--status`: Comma-separated statuses (default: selected,rejected)
- `--dry-run`: Preview without deleting
- `--filters`: Custom filters for list ID

## Filter Configuration

### filters.json Structure
The `filters.json` file contains all search parameters:

```json
{
  "list_id": "374837",
  "criterias": [
    {"value": "Fintech", "weight": 1, "field": "all", "type": "should"},
    {"value": "Trading", "weight": 1, "field": "all", "type": "should"}
  ],
  "filters": [
    {"value": {"from": 10000, "to": 500000}, "type": "range-int", "slug": "youtubeFollowers", "name": "youtube.followers"},
    {"value": ["en"], "type": "multi-string", "slug": "lg", "name": "influencer.lang"}
  ],
  "audience_filters": [],
  "social_media_matching_operator": "or",
  "should_save": true,
  "track_hits_results": 10000,
  "score_model": "default"
}
```

### Filter Types
- **range-int**: Numeric ranges (followers, views, etc.)
- **float**: Percentage filters with comparison operators
- **multi-string**: Multiple string values (languages, categories)
- **average-engagement**: Engagement rate filters

### Customizing Filters
1. **Modify existing filters.json**:
   ```bash
   # Change follower ranges
   # Adjust engagement thresholds
   # Add/remove keywords
   ```

2. **Create custom filter files**:
   ```bash
   cp filters.json strict_filters.json
   # Edit strict_filters.json
   python upfluence.py search --filters strict_filters.json
   ```

3. **Command-line overrides**:
   ```bash
   python upfluence.py search --keywords "New,Keywords,Here" --list-id "987654"
   ```

## Workflow Examples

### Complete Data Extraction Pipeline
```bash
# 1. Clear existing list entries
python upfluence.py cleanup

# 2. Search for new influencers
python upfluence.py search --output new_influencers.csv --limit 500

# 3. Export full details
python upfluence.py export --output full_contacts.csv --workers 32

# 4. Remove processed influencers from list
python upfluence.py remove
```

### Targeted Search Campaign
```bash
# Search for fintech influencers
python upfluence.py search --keywords "Fintech,API,Developer" --limit 200

# Search for trading educators
python upfluence.py search --keywords "Trading,Education,Stocks" --limit 150

# Combine results
cat 2025*.csv > combined_influencers.csv
```

### Batch Processing
```bash
# Process in batches of 100
for i in {1..5}; do
  python upfluence.py search --output batch_${i}.csv --limit 100
  sleep 60  # Avoid rate limits
done
```

## Output Format

### CSV Columns
The tool exports all available influencer fields including:
- `id`: Unique influencer ID
- `name`: Full name
- `email`: Contact email (if available)
- `categories`: Influencer categories as JSON
- `location`: Geographic location as JSON
- Social media stats (followers, engagement, etc.)
- `processed_features`: Platform analysis data

### Data Types
- **Strings**: Names, emails, URLs
- **Numbers**: Followers, engagement rates
- **JSON**: Complex objects (location, categories, features)
- **Booleans**: Verified status, contact availability

### File Management
- Default filenames include timestamps: `20250310_153000_upfluence_influencers.csv`
- Can append to existing files (maintains headers)
- Automatic column ordering with `id` first

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   ```bash
   # Check token is set
   echo $UPFLUENCE_BEARER_TOKEN
   
   # Or use .env file
   cat .env
   ```

2. **API Rate Limits**:
   ```bash
   # Reduce workers
   python upfluence.py search --workers 1
   
   # Add delays between batches
   python upfluence.py search --limit 50 && sleep 30
   ```

3. **Pagination Limits**:
   - API limits offsets to 1000
   - Tool handles this automatically
   - Use `--per-page 100` for optimal results

4. **File Permission Issues**:
   ```bash
   # Specify writable output directory
   python upfluence.py search --output /path/to/writable/influencers.csv
   ```

### Error Messages
- `"UPFLUENCE_BEARER_TOKEN not set"`: Set environment variable
- `"402 Payment Required"`: Check Upfluence subscription
- `"404 Not Found"`: Invalid list ID or API endpoint
- `"400 Bad Request"`: Invalid filter parameters

## Performance Tips

### Optimizing Speed
```bash
# Use maximum workers (if not hitting rate limits)
python upfluence.py export --workers 64

# Increase per-page for fewer API calls
python upfluence.py search --per-page 100

# Process in parallel batches
python upfluence.py search --limit 1000 --output part1.csv &
python upfluence.py search --limit 1000 --output part2.csv &
```

### Managing API Limits
```bash
# Conservative settings for rate-limited accounts
python upfluence.py search --workers 1 --per-page 50

# Add delays between operations
python upfluence.py search --limit 100 && sleep 60

# Use dry runs for destructive operations
python upfluence.py remove --dry-run
```

## Advanced Usage

### Script Integration
```python
# Use as Python module
import subprocess
result = subprocess.run([
    "python", "upfluence.py", "search",
    "--output", "data.csv",
    "--limit", "50"
], capture_output=True, text=True)
```

### Scheduled Jobs (cron)
```bash
# Daily extraction at 2 AM
0 2 * * * cd /path/to/scripts && python upfluence.py search --output daily_$(date +\%Y\%m\%d).csv
```

### Data Processing Pipeline
```bash
# Extract
python upfluence.py export --output raw_data.csv

# Filter (example with jq)
cat raw_data.csv | csvjson | jq '[.[] | select(.followers > 10000)]' > filtered.json

# Analyze
python analyze_influencers.py filtered.json
```

## Migration from Old Scripts

### Equivalent Commands
| Old Script | New Command |
|------------|-------------|
| `upfluence_unlock_and_store.py` | `python upfluence.py search` |
| `upfluence_export_contacts.py` | `python upfluence.py export` |
| `upfluence_remove_community.py` | `python upfluence.py remove` |
| `upfluence_delete_list_entries.py` | `python upfluence.py cleanup` |

### Parameter Mapping
```bash
# Old: python upfluence_unlock_and_store.py -l 100 -o output.csv
# New: python upfluence.py search --limit 100 --output output.csv

# Old: python upfluence_export_contacts.py --workers 64 --output contacts.csv
# New: python upfluence.py export --workers 64 --output contacts.csv

# Old: python upfluence_remove_community.py --dry-run
# New: python upfluence.py remove --dry-run
```

## Support

### Getting Help
```bash
# Show all commands
python upfluence.py --help

# Command-specific help
python upfluence.py search --help
python upfluence.py export --help
```

### Debug Mode
For troubleshooting, add verbose logging to the script or check:
- API responses in console output
- CSV file headers and data
- Environment variable settings

### Common Questions
- **Q**: Can I use multiple filter files?
  **A**: Yes, use `--filters filename.json` for each command

- **Q**: How do I resume interrupted downloads?
  **A**: Use the same output file - tool will append new data

- **Q**: Can I filter by specific platforms only?
  **A**: Modify `filters.json` to include only desired platform filters

## License & Attribution
This tool consolidates functionality from multiple Upfluence scraping scripts. Use responsibly and in accordance with Upfluence's terms of service.

---
*Last updated: March 2025*