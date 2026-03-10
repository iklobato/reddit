# JIRA Token Organization - Migration Notes

## Summary of Changes

The `comprehensive_work_summary.sh` script has been updated to support multiple JIRA instances, allowing you to retrieve work items from both Orlo and Rivian JIRA instances simultaneously.

## What Changed

### 1. Configuration Variables (Lines 22-35)

**Before:**
```bash
readonly JIRA_API_TOKEN="${JIRA_API_TOKEN:-}"
readonly JIRA_INSTANCE_URL="https://rivianautomotivellc.atlassian.net"
readonly JIRA_EMAIL="henriquelobato@rivian.com"
```

**After:**
```bash
# Rivian Jira
readonly JIRA_TOKEN_RIVIAN="${JIRA_TOKEN_RIVIAN:-}"
readonly JIRA_INSTANCE_URL_RIVIAN="https://rivianautomotivellc.atlassian.net"
readonly JIRA_EMAIL_RIVIAN="henriquelobato@rivian.com"

# Orlo Jira
readonly JIRA_TOKEN_ORLO="${JIRA_TOKEN_ORLO:-}"
readonly JIRA_INSTANCE_URL_ORLO="${JIRA_INSTANCE_URL_ORLO:-}"
readonly JIRA_EMAIL_ORLO="${JIRA_EMAIL_ORLO:-}"
```

### 2. Function Refactoring (Lines 1037-1182)

**Before:**
- Single `collect_jira_cards()` function hardcoded for Rivian

**After:**
- `collect_jira_cards_from_instance()`: Generic function that accepts parameters for any JIRA instance
- `collect_jira_cards()`: Wrapper function that calls the generic function for each configured instance

### 3. New Files Created

1. **JIRA_SETUP.md**: Comprehensive guide on how to configure JIRA tokens
2. **.env.example**: Template for environment variables
3. **test_jira_connections.sh**: Utility script to test JIRA connections
4. **JIRA_MIGRATION_NOTES.md**: This file

### 4. Updated .gitignore

Added entries to prevent committing sensitive files:
```
.env
.env.local
*.token
*_token.txt
```

## How to Use

### Quick Start

1. **Set up Rivian JIRA** (if not already done):
   ```bash
   export JIRA_TOKEN_RIVIAN="your_rivian_token"
   ```

2. **Set up Orlo JIRA**:
   ```bash
   export JIRA_TOKEN_ORLO="your_orlo_token"
   export JIRA_INSTANCE_URL_ORLO="https://orlo-instance.atlassian.net"
   export JIRA_EMAIL_ORLO="your.email@orlo.com"
   ```

3. **Test connections**:
   ```bash
   ./test_jira_connections.sh
   ```

4. **Run the main script**:
   ```bash
   ./comprehensive_work_summary.sh
   ```

### Using .env File

1. Copy the example:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual tokens

3. Load the environment:
   ```bash
   source .env
   ```

4. Run the script:
   ```bash
   ./comprehensive_work_summary.sh
   ```

## Backward Compatibility

The script is fully backward compatible:
- If only `JIRA_TOKEN_RIVIAN` is set, it will only collect from Rivian
- If only `JIRA_TOKEN_ORLO` is set (with URL and email), it will only collect from Orlo
- If both are set, it will collect from both instances
- If neither is set, JIRA collection is skipped silently

## Testing

Use the new test script to verify your configuration:

```bash
./test_jira_connections.sh
```

This will:
- Check if tokens are set
- Test authentication
- Verify API access
- Show sample issues
- Provide a summary of connection status

## Benefits

1. **Multi-organization support**: Retrieve work items from multiple JIRA instances
2. **Better organization**: Clear separation between different JIRA configurations
3. **Easier maintenance**: Generic function can be reused for additional instances
4. **Security**: Environment variables prevent hardcoding credentials
5. **Testing**: Dedicated test script for troubleshooting

## Adding More JIRA Instances

To add a third JIRA instance (e.g., for another company):

1. Add configuration variables:
   ```bash
   readonly JIRA_TOKEN_COMPANY3="${JIRA_TOKEN_COMPANY3:-}"
   readonly JIRA_INSTANCE_URL_COMPANY3="https://company3.atlassian.net"
   readonly JIRA_EMAIL_COMPANY3="your.email@company3.com"
   ```

2. Add collection call in `collect_jira_cards()`:
   ```bash
   if [[ -n "$JIRA_TOKEN_COMPANY3" ]] && [[ -n "$JIRA_INSTANCE_URL_COMPANY3" ]] && [[ -n "$JIRA_EMAIL_COMPANY3" ]]; then
       print_progress "  - Collecting from Company3 Jira"
       collect_jira_cards_from_instance "$JIRA_TOKEN_COMPANY3" "$JIRA_INSTANCE_URL_COMPANY3" "$JIRA_EMAIL_COMPANY3" "company3" || true
   fi
   ```

3. Update test script similarly

## Troubleshooting

### No issues appearing from Orlo JIRA

1. Verify all three Orlo variables are set:
   ```bash
   echo "Token: ${JIRA_TOKEN_ORLO:0:10}..."
   echo "URL: $JIRA_INSTANCE_URL_ORLO"
   echo "Email: $JIRA_EMAIL_ORLO"
   ```

2. Run the test script:
   ```bash
   ./test_jira_connections.sh
   ```

3. Check that you have assigned issues in Orlo JIRA

### Authentication errors

- Verify the email matches the account that created the token
- Regenerate the API token if needed
- Check the instance URL is correct (should end with `.atlassian.net`)

### Script runs but skips JIRA

- The script silently skips JIRA if tokens are not set
- Check that environment variables are exported (not just set)
- Verify you're running the script in the same shell where you set the variables

## Security Reminders

1. **Never commit tokens**: Always use environment variables or `.env` files (which are gitignored)
2. **Rotate tokens**: Periodically regenerate your API tokens
3. **Limit permissions**: Use read-only tokens when possible
4. **Revoke unused tokens**: Clean up old tokens from your JIRA account

## Next Steps

1. Set up your Orlo JIRA credentials
2. Run the test script to verify connections
3. Run the main script to see unified work summary
4. Add to your shell profile for permanent configuration

For detailed instructions, see **JIRA_SETUP.md**.
