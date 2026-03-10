#!/bin/bash

###############################################################################
# test_jira_connections.sh - Test JIRA API Connections
# 
# This script tests the JIRA API connections for both Rivian and Orlo
# instances to verify that tokens and configurations are correct.
#
# Usage: ./test_jira_connections.sh
###############################################################################

set -uo pipefail

# Colors
readonly GREEN=$'\033[0;32m'
readonly RED=$'\033[0;31m'
readonly YELLOW=$'\033[1;33m'
readonly CYAN=$'\033[0;36m'
readonly BOLD=$'\033[1m'
readonly NC=$'\033[0m'

# Configuration
readonly JIRA_TOKEN_RIVIAN="${JIRA_TOKEN_RIVIAN:-}"
readonly JIRA_INSTANCE_URL_RIVIAN="https://rivianautomotivellc.atlassian.net"
readonly JIRA_EMAIL_RIVIAN="henriquelobato@rivian.com"

readonly JIRA_TOKEN_ORLO="${JIRA_TOKEN_ORLO:-}"
readonly JIRA_INSTANCE_URL_ORLO="${JIRA_INSTANCE_URL_ORLO:-}"
readonly JIRA_EMAIL_ORLO="${JIRA_EMAIL_ORLO:-}"

print_header() {
    echo -e "${BOLD}${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           JIRA CONNECTION TEST                                ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

test_jira_connection() {
    local instance_name="$1"
    local jira_token="$2"
    local jira_instance_url="$3"
    local jira_email="$4"
    
    echo -e "${BOLD}${CYAN}Testing ${instance_name} JIRA...${NC}"
    echo ""
    
    # Check if token is set
    if [[ -z "$jira_token" ]]; then
        echo -e "  ${RED}✗ Token not set${NC}"
        echo -e "    Set ${YELLOW}JIRA_TOKEN_${instance_name^^}${NC} environment variable"
        echo ""
        return 1
    fi
    
    # Check if instance URL is set
    if [[ -z "$jira_instance_url" ]]; then
        echo -e "  ${RED}✗ Instance URL not set${NC}"
        echo -e "    Set ${YELLOW}JIRA_INSTANCE_URL_${instance_name^^}${NC} environment variable"
        echo ""
        return 1
    fi
    
    # Check if email is set
    if [[ -z "$jira_email" ]]; then
        echo -e "  ${RED}✗ Email not set${NC}"
        echo -e "    Set ${YELLOW}JIRA_EMAIL_${instance_name^^}${NC} environment variable"
        echo ""
        return 1
    fi
    
    echo -e "  ${CYAN}Token:${NC} ${jira_token:0:10}... (${#jira_token} chars)"
    echo -e "  ${CYAN}URL:${NC} ${jira_instance_url}"
    echo -e "  ${CYAN}Email:${NC} ${jira_email}"
    echo ""
    
    # Test connection
    local jira_base_url="${jira_instance_url%/}"
    local jira_api_url="${jira_base_url}/rest/api/3"
    
    local auth_string
    auth_string=$(echo -n "${jira_email}:${jira_token}" | base64)
    local auth_header="Authorization: Basic $auth_string"
    
    echo -e "  ${CYAN}Testing authentication...${NC}"
    local myself_response
    myself_response=$(curl -s -X GET \
        -H "$auth_header" \
        -H "Accept: application/json" \
        "${jira_api_url}/myself" 2>/dev/null || echo "{}")
    
    # Check for errors
    if echo "$myself_response" | jq -e '.errorMessages' >/dev/null 2>&1; then
        local error_msg
        error_msg=$(echo "$myself_response" | jq -r '.errorMessages[0] // "Unknown error"')
        echo -e "  ${RED}✗ Authentication failed${NC}"
        echo -e "    Error: ${error_msg}"
        echo ""
        return 1
    fi
    
    # Extract user info
    local display_name account_id email_address
    display_name=$(echo "$myself_response" | jq -r '.displayName // "Unknown"')
    account_id=$(echo "$myself_response" | jq -r '.accountId // "Unknown"')
    email_address=$(echo "$myself_response" | jq -r '.emailAddress // "Unknown"')
    
    if [[ "$display_name" == "Unknown" ]] || [[ -z "$display_name" ]]; then
        echo -e "  ${RED}✗ Could not retrieve user information${NC}"
        echo ""
        return 1
    fi
    
    echo -e "  ${GREEN}✓ Authentication successful${NC}"
    echo -e "    User: ${display_name}"
    echo -e "    Email: ${email_address}"
    echo -e "    Account ID: ${account_id}"
    echo ""
    
    # Test issue search
    echo -e "  ${CYAN}Testing issue search (assigned + watched)...${NC}"
    local jql_query="(assignee = currentUser() OR watcher = currentUser()) AND status != Done AND status != Closed ORDER BY updated DESC"
    local search_response
    search_response=$(curl -s -X POST \
        -H "$auth_header" \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d "{\"jql\":\"$jql_query\",\"maxResults\":10,\"fields\":[\"summary\",\"status\",\"project\",\"assignee\",\"watches\"]}" \
        "${jira_api_url}/search" 2>/dev/null || echo "{}")
    
    # Check for errors
    if echo "$search_response" | jq -e '.errorMessages' >/dev/null 2>&1; then
        local error_msg
        error_msg=$(echo "$search_response" | jq -r '.errorMessages[0] // "Unknown error"')
        echo -e "  ${YELLOW}⚠ Search failed (but authentication worked)${NC}"
        echo -e "    Error: ${error_msg}"
        echo ""
        return 0
    fi
    
    local issue_count
    issue_count=$(echo "$search_response" | jq -r '.total // 0')
    
    echo -e "  ${GREEN}✓ Issue search successful${NC}"
    echo -e "    Found ${BOLD}${issue_count}${NC} issues (assigned + watched)"
    
    # Show sample issues with more details
    if [[ "$issue_count" -gt 0 ]]; then
        echo ""
        echo -e "  ${CYAN}Sample issues:${NC}"
        echo "$search_response" | jq -r '.issues[:3][] | 
            "    - \(.key): \(.fields.summary)\n      Assignee: \(.fields.assignee.displayName // "Unassigned") | Watching: \(.fields.watches.isWatching // false) | Status: \(.fields.status.name)"' 2>/dev/null || echo "    (Could not display issues)"
    fi
    
    echo ""
    return 0
}

main() {
    print_header
    
    local rivian_result=0
    local orlo_result=0
    
    # Test Rivian JIRA
    test_jira_connection "RIVIAN" "$JIRA_TOKEN_RIVIAN" "$JIRA_INSTANCE_URL_RIVIAN" "$JIRA_EMAIL_RIVIAN"
    rivian_result=$?
    
    # Test Orlo JIRA
    if [[ -n "$JIRA_TOKEN_ORLO" ]] || [[ -n "$JIRA_INSTANCE_URL_ORLO" ]] || [[ -n "$JIRA_EMAIL_ORLO" ]]; then
        test_jira_connection "ORLO" "$JIRA_TOKEN_ORLO" "$JIRA_INSTANCE_URL_ORLO" "$JIRA_EMAIL_ORLO"
        orlo_result=$?
    else
        echo -e "${YELLOW}Orlo JIRA not configured (skipping)${NC}"
        echo -e "  To configure, set:"
        echo -e "    - ${CYAN}JIRA_TOKEN_ORLO${NC}"
        echo -e "    - ${CYAN}JIRA_INSTANCE_URL_ORLO${NC}"
        echo -e "    - ${CYAN}JIRA_EMAIL_ORLO${NC}"
        echo ""
    fi
    
    # Summary
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}  Summary${NC}"
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [[ $rivian_result -eq 0 ]]; then
        echo -e "  ${GREEN}✓ Rivian JIRA: Connected${NC}"
    else
        echo -e "  ${RED}✗ Rivian JIRA: Failed${NC}"
    fi
    
    if [[ -n "$JIRA_TOKEN_ORLO" ]]; then
        if [[ $orlo_result -eq 0 ]]; then
            echo -e "  ${GREEN}✓ Orlo JIRA: Connected${NC}"
        else
            echo -e "  ${RED}✗ Orlo JIRA: Failed${NC}"
        fi
    else
        echo -e "  ${YELLOW}⊘ Orlo JIRA: Not configured${NC}"
    fi
    
    echo ""
    
    if [[ $rivian_result -eq 0 ]] || [[ $orlo_result -eq 0 ]]; then
        echo -e "${GREEN}At least one JIRA connection is working!${NC}"
        echo -e "You can now run: ${CYAN}./comprehensive_work_summary.sh${NC}"
        return 0
    else
        echo -e "${RED}No JIRA connections are working.${NC}"
        echo -e "Please check your configuration and try again."
        echo -e "See ${CYAN}JIRA_SETUP.md${NC} for detailed instructions."
        return 1
    fi
}

main "$@"
