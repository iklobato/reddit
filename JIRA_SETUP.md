# JIRA Configuration for Comprehensive Work Summary

This document explains how to configure multiple JIRA instances for the `comprehensive_work_summary.sh` script.

## Overview

The script now supports multiple JIRA instances to retrieve work items from different organizations:
- **Rivian JIRA**: Pre-configured for Rivian Automotive
- **Orlo JIRA**: Configurable for Orlo organization

The script collects:
- ✅ Issues **assigned** to you
- ✅ Issues you are **watching**
- ✅ Filters out Done/Closed issues

## Environment Variables

### Rivian JIRA (Pre-configured)

```bash
export JIRA_TOKEN_RIVIAN="your_rivian_jira_api_token"
```

The following are already configured in the script:
- Instance URL: `https://rivianautomotivellc.atlassian.net`
- Email: `henriquelobato@rivian.com`

### Orlo JIRA (Requires Configuration)

```bash
export JIRA_TOKEN_ORLO="your_orlo_jira_api_token"
export JIRA_INSTANCE_URL_ORLO="https://your-orlo-instance.atlassian.net"
export JIRA_EMAIL_ORLO="your.email@orlo.com"
```

## How to Get JIRA API Tokens

### Step 1: Log in to JIRA
Navigate to your JIRA instance and log in with your credentials.

### Step 2: Create API Token
1. Go to your account settings (usually by clicking your profile icon)
2. Navigate to **Security** → **API tokens**
3. Click **Create API token**
4. Give it a descriptive name (e.g., "Work Summary Script")
5. Copy the generated token immediately (you won't be able to see it again)

### Step 3: Set Environment Variables

#### Option 1: Temporary (Current Session Only)
```bash
export JIRA_TOKEN_RIVIAN="your_token_here"
export JIRA_TOKEN_ORLO="your_token_here"
export JIRA_INSTANCE_URL_ORLO="https://your-instance.atlassian.net"
export JIRA_EMAIL_ORLO="your.email@company.com"
```

#### Option 2: Permanent (Add to Shell Profile)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# JIRA Configuration
export JIRA_TOKEN_RIVIAN="your_rivian_token"
export JIRA_TOKEN_ORLO="your_orlo_token"
export JIRA_INSTANCE_URL_ORLO="https://your-orlo-instance.atlassian.net"
export JIRA_EMAIL_ORLO="your.email@orlo.com"
```

Then reload your shell:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

## Verification

To verify your configuration, run:

```bash
echo "Rivian Token: ${JIRA_TOKEN_RIVIAN:0:10}..."
echo "Orlo Token: ${JIRA_TOKEN_ORLO:0:10}..."
echo "Orlo URL: $JIRA_INSTANCE_URL_ORLO"
echo "Orlo Email: $JIRA_EMAIL_ORLO"
```

This will show the first 10 characters of your tokens (for security) and the full URL and email.

## Running the Script

Once configured, simply run:

```bash
./comprehensive_work_summary.sh
```

The script will automatically:
1. Collect issues from Rivian JIRA (if `JIRA_TOKEN_RIVIAN` is set)
2. Collect issues from Orlo JIRA (if all Orlo variables are set)
3. Display all issues in a unified table

## Troubleshooting

### No JIRA cards appearing
- Verify your API token is correct
- Check that the instance URL is correct (should end with `.atlassian.net`)
- Ensure your email matches the account used to generate the token
- Verify you have assigned issues in JIRA

### Authentication errors
- Regenerate your API token
- Ensure there are no extra spaces in your environment variables
- Check that your JIRA account has appropriate permissions

### Script skips JIRA collection
- The script will silently skip JIRA instances if tokens are not set
- Check that environment variables are exported (use `echo $JIRA_TOKEN_RIVIAN`)

## Security Best Practices

1. **Never commit tokens to git**: Add them to `.gitignore` or use environment variables
2. **Use separate tokens**: Create different tokens for different purposes
3. **Rotate regularly**: Regenerate tokens periodically
4. **Revoke unused tokens**: Remove old tokens from your JIRA account settings
5. **Use read-only permissions**: If possible, limit token permissions to read-only access

## Adding More JIRA Instances

To add additional JIRA instances, modify the script:

1. Add new configuration variables in the Configuration section:
```bash
readonly JIRA_TOKEN_NEWCOMPANY="${JIRA_TOKEN_NEWCOMPANY:-}"
readonly JIRA_INSTANCE_URL_NEWCOMPANY="https://newcompany.atlassian.net"
readonly JIRA_EMAIL_NEWCOMPANY="your.email@newcompany.com"
```

2. Add a new collection call in the `collect_jira_cards()` function:
```bash
if [[ -n "$JIRA_TOKEN_NEWCOMPANY" ]]; then
    print_progress "  - Collecting from NewCompany Jira"
    collect_jira_cards_from_instance "$JIRA_TOKEN_NEWCOMPANY" "$JIRA_INSTANCE_URL_NEWCOMPANY" "$JIRA_EMAIL_NEWCOMPANY" "newcompany" || true
fi
```

## Support

For issues or questions about JIRA configuration, please refer to:
- [Atlassian API Token Documentation](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
- [JIRA REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)
