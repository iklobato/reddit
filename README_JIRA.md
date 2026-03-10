# JIRA Integration for Comprehensive Work Summary

## 🎯 Overview

The `comprehensive_work_summary.sh` script now supports **multiple JIRA instances**, allowing you to retrieve and display work items from both **Orlo** and **Rivian** JIRA instances in a single unified view.

## 🚀 Quick Start (5 Minutes)

### Step 1: Get Your JIRA API Tokens

1. **Rivian JIRA**:
   - Go to https://rivianautomotivellc.atlassian.net
   - Click your profile → Settings → Security → API Tokens
   - Create new token, copy it

2. **Orlo JIRA**:
   - Go to your Orlo JIRA instance
   - Click your profile → Settings → Security → API Tokens
   - Create new token, copy it

### Step 2: Set Environment Variables

```bash
# Rivian JIRA
export JIRA_TOKEN_RIVIAN="your_rivian_token_here"

# Orlo JIRA
export JIRA_TOKEN_ORLO="your_orlo_token_here"
export JIRA_INSTANCE_URL_ORLO="https://your-orlo-instance.atlassian.net"
export JIRA_EMAIL_ORLO="your.email@orlo.com"
```

### Step 3: Test Your Setup

```bash
./test_jira_connections.sh
```

You should see:
```
✓ Rivian JIRA: Connected
✓ Orlo JIRA: Connected
```

### Step 4: Run the Main Script

```bash
./comprehensive_work_summary.sh
```

## 📋 What You Get

The script will display a unified table showing:

| Company | Source | Type | ID | Title | Status | Updated |
|---------|--------|------|----|----|--------|---------|
| rivian | Jira | Story | PROJ-123 | Implement feature X | In Progress | 2026-01-10 |
| orlo | Jira | Bug | ORLO-456 | Fix authentication | To Do | 2026-01-11 |
| ... | ... | ... | ... | ... | ... | ... |

## 📁 Files Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `JIRA_SETUP.md` | Detailed setup guide | First time setup |
| `test_jira_connections.sh` | Test connections | Troubleshooting |
| `.env.example` | Environment template | Configuration reference |
| `JIRA_MIGRATION_NOTES.md` | Technical details | Understanding implementation |
| `JIRA_ORGANIZATION_SUMMARY.md` | Complete overview | Project documentation |
| `JIRA_FILES_OVERVIEW.txt` | Visual guide | Quick reference |

## 🔧 Configuration Options

### Minimal Setup (Rivian Only)

```bash
export JIRA_TOKEN_RIVIAN="your_token"
```

The script will:
- ✅ Collect from Rivian JIRA
- ⊘ Skip Orlo JIRA (no token set)

### Full Setup (Both Instances)

```bash
export JIRA_TOKEN_RIVIAN="your_rivian_token"
export JIRA_TOKEN_ORLO="your_orlo_token"
export JIRA_INSTANCE_URL_ORLO="https://orlo.atlassian.net"
export JIRA_EMAIL_ORLO="your.email@orlo.com"
```

The script will:
- ✅ Collect from Rivian JIRA
- ✅ Collect from Orlo JIRA

### Permanent Setup

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# JIRA Configuration
export JIRA_TOKEN_RIVIAN="your_rivian_token"
export JIRA_TOKEN_ORLO="your_orlo_token"
export JIRA_INSTANCE_URL_ORLO="https://orlo.atlassian.net"
export JIRA_EMAIL_ORLO="your.email@orlo.com"
```

Then reload:
```bash
source ~/.zshrc
```

## 🧪 Testing

### Test JIRA Connections

```bash
./test_jira_connections.sh
```

This will:
- ✓ Verify tokens are set
- ✓ Test authentication
- ✓ Check API access
- ✓ Show sample issues
- ✓ Display connection summary

### Verify Environment Variables

```bash
echo "Rivian Token: ${JIRA_TOKEN_RIVIAN:0:10}..."
echo "Orlo Token: ${JIRA_TOKEN_ORLO:0:10}..."
echo "Orlo URL: $JIRA_INSTANCE_URL_ORLO"
echo "Orlo Email: $JIRA_EMAIL_ORLO"
```

## 🐛 Troubleshooting

### No JIRA Issues Appearing

**Problem**: Script runs but no JIRA issues show up

**Solutions**:
1. Check tokens are set: `echo $JIRA_TOKEN_RIVIAN`
2. Run test script: `./test_jira_connections.sh`
3. Verify you have assigned issues in JIRA
4. Check token permissions

### Authentication Errors

**Problem**: "Authentication failed" error

**Solutions**:
1. Verify email matches token account
2. Regenerate API token
3. Check instance URL is correct
4. Ensure no extra spaces in variables

### Script Skips JIRA

**Problem**: Script runs but silently skips JIRA collection

**Solutions**:
1. Verify tokens are **exported** (not just set)
2. Check you're in the same shell session
3. Add to shell profile for persistence

### Connection Timeout

**Problem**: Script hangs or times out

**Solutions**:
1. Check internet connection
2. Verify JIRA instance URL is accessible
3. Check firewall/VPN settings
4. Try with curl manually

## 🔒 Security Best Practices

1. **Never commit tokens**: Always use environment variables
2. **Use .env files**: Copy `.env.example` to `.env` (gitignored)
3. **Rotate regularly**: Regenerate tokens every 90 days
4. **Revoke unused**: Remove old tokens from JIRA settings
5. **Limit permissions**: Use read-only tokens when possible

## 🎨 Output Example

```
╔═══════════════════════════════════════════════════════════════╗
║              COMPREHENSIVE WORK SUMMARY                       ║
╚═══════════════════════════════════════════════════════════════╝

Collecting work items from all sources...
  Collecting GitHub Project tasks...
  Collecting GitHub Pull Requests...
  Collecting GitHub Issues...
  Collecting GitLab Merge Requests...
  Collecting Jira Cards from all instances...
    - Collecting from Rivian Jira...
    - Collecting from Orlo Jira...
  Collecting Shortcut Cards...

═══════════════════════════════════════════════════════════════
  Cards - Shortcut / Jira
═══════════════════════════════════════════════════════════════

┌─────────┬────────┬───────┬──────────┬─────────────────────┬──────────────┐
│ Company │ Source │ Type  │ ID       │ Title               │ Status       │
├─────────┼────────┼───────┼──────────┼─────────────────────┼──────────────┤
│ rivian  │ Jira   │ Story │ PROJ-123 │ Implement feature X │ In Progress  │
│ orlo    │ Jira   │ Bug   │ ORLO-456 │ Fix authentication  │ To Do        │
│ ...     │ ...    │ ...   │ ...      │ ...                 │ ...          │
└─────────┴────────┴───────┴──────────┴─────────────────────┴──────────────┘
```

## 🔄 Adding More JIRA Instances

Want to add a third JIRA instance? Here's how:

1. **Add configuration** in `comprehensive_work_summary.sh`:
   ```bash
   readonly JIRA_TOKEN_COMPANY3="${JIRA_TOKEN_COMPANY3:-}"
   readonly JIRA_INSTANCE_URL_COMPANY3="https://company3.atlassian.net"
   readonly JIRA_EMAIL_COMPANY3="your.email@company3.com"
   ```

2. **Add collection call** in `collect_jira_cards()`:
   ```bash
   if [[ -n "$JIRA_TOKEN_COMPANY3" ]]; then
       print_progress "  - Collecting from Company3 Jira"
       collect_jira_cards_from_instance "$JIRA_TOKEN_COMPANY3" \
           "$JIRA_INSTANCE_URL_COMPANY3" "$JIRA_EMAIL_COMPANY3" "company3" || true
   fi
   ```

3. **Update test script** similarly

## 📚 Additional Resources

- **Atlassian API Docs**: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **API Token Management**: https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
- **JQL Reference**: https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/

## 💡 Tips

1. **Use descriptive token names**: "Work Summary Script - 2026" helps identify tokens later
2. **Set expiration reminders**: Add calendar reminder to rotate tokens
3. **Test after changes**: Always run test script after updating configuration
4. **Keep tokens separate**: Use different tokens for different purposes
5. **Document your setup**: Note which tokens are used where

## ✅ Checklist

Before running the script, ensure:

- [ ] JIRA API tokens generated
- [ ] Environment variables set
- [ ] Test script passes
- [ ] Tokens added to shell profile (for permanent use)
- [ ] .env file created (if using that method)
- [ ] Tokens not committed to git

## 🆘 Getting Help

1. **Setup Issues**: Read `JIRA_SETUP.md`
2. **Connection Problems**: Run `./test_jira_connections.sh`
3. **Technical Details**: Read `JIRA_MIGRATION_NOTES.md`
4. **Quick Reference**: See `JIRA_FILES_OVERVIEW.txt`

## 📊 Status

✅ **Implementation Complete**  
✅ **Documentation Complete**  
✅ **Testing Utility Available**  
✅ **Ready for Production Use**

---

**Last Updated**: January 12, 2026  
**Version**: 2.0 (Multi-instance support)
