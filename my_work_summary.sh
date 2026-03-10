#!/bin/bash

###############################################################################
# my_work_summary.sh - Comprehensive Work Summary
# 
# Collects and displays:
# - All user PRs from precisetargetlabs (GitHub)
# - All assigned tasks from precisetargetlabs (GitHub)
# - All user MRs from Rivian (GitLab)
# - All assigned Jira cards from Rivian Jira
#
# Usage: ./my_work_summary.sh
###############################################################################

set -euo pipefail

###############################################################################
# Configuration
###############################################################################

readonly JIRA_API_TOKEN="${JIRA_API_TOKEN:-}"
readonly JIRA_INSTANCE_URL="https://rivianautomotivellc.atlassian.net"
readonly JIRA_EMAIL="henriquelobato@rivian.com"
readonly GITHUB_ORG="precisetargetlabs"
readonly GITLAB_ORG="rivian"

###############################################################################
# Colors
###############################################################################

readonly RED=$'\033[0;31m'
readonly GREEN=$'\033[0;32m'
readonly YELLOW=$'\033[1;33m'
readonly BLUE=$'\033[0;34m'
readonly CYAN=$'\033[0;36m'
readonly MAGENTA=$'\033[0;35m'
readonly BOLD=$'\033[1m'
readonly NC=$'\033[0m'

###############################################################################
# Utility Functions
###############################################################################

print_section_header() {
    local title="$1"
    echo ""
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}  $title${NC}"
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_subsection_header() {
    local title="$1"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}  $title${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

format_status() {
    local status="$1"
    case "$(echo "$status" | tr '[:upper:]' '[:lower:]')" in
        *open*|*opened*|*inprogress*|*in\ progress*|*todo*|*to\ do*)
            echo -e "${GREEN}${status}${NC}"
            ;;
        *closed*|*done*|*resolved*|*completed*|*merged*)
            echo -e "${RED}${status}${NC}"
            ;;
        *review*|*testing*|*qa*|*pending*)
            echo -e "${YELLOW}${status}${NC}"
            ;;
        *)
            echo -e "${status}"
            ;;
    esac
}

wrap_text() {
    local text="$1"
    local width="${2:-80}"
    echo "$text" | fold -w "$width" -s | sed 's/^/    /'
}

extract_jira_description() {
    local desc_json="$1"
    [[ -z "$desc_json" ]] || [[ "$desc_json" == "null" ]] && echo "" && return
    
    echo "$desc_json" | jq -r '
        if type == "object" and .type == "doc" then
            def extract_text(node):
                if node.type == "text" then node.text // ""
                elif node.content then [node.content[] | extract_text(.)] | join("")
                else "" end;
            extract_text(.)
        elif type == "string" then .
        else tostring end
    ' 2>/dev/null || echo ""
}

###############################################################################
# GitHub Functions
###############################################################################

collect_github_prs() {
    command -v gh &> /dev/null || return 1
    
    print_subsection_header "GitHub Pull Requests (precisetargetlabs)"
    
    local prs_json
    prs_json=$(gh search prs --author @me --org "$GITHUB_ORG" --state open --limit 100 \
        --json number,title,state,repository,url,updatedAt,additions,deletions,reviewDecision,isDraft,reviewRequests,reviews,author,headRefName,baseRefName 2>/dev/null || echo "[]")
    
    local count
    count=$(echo "$prs_json" | jq 'length')
    
    if [[ "$count" -eq 0 ]]; then
        echo -e "  ${YELLOW}No open PRs found${NC}"
        return
    fi
    
    echo "$prs_json" | jq -r '.[] | @json' | while IFS= read -r pr; do
        local number title state repo url updated additions deletions review_decision is_draft head_ref base_ref
        local author reviews review_requests
        
        number=$(echo "$pr" | jq -r '.number')
        title=$(echo "$pr" | jq -r '.title')
        state=$(echo "$pr" | jq -r '.state')
        repo=$(echo "$pr" | jq -r '.repository.nameWithOwner')
        url=$(echo "$pr" | jq -r '.url')
        updated=$(echo "$pr" | jq -r '.updatedAt' | cut -d'T' -f1)
        additions=$(echo "$pr" | jq -r '.additions // 0')
        deletions=$(echo "$pr" | jq -r '.deletions // 0')
        review_decision=$(echo "$pr" | jq -r '.reviewDecision // "PENDING"')
        is_draft=$(echo "$pr" | jq -r '.isDraft // false')
        head_ref=$(echo "$pr" | jq -r '.headRefName')
        base_ref=$(echo "$pr" | jq -r '.baseRefName')
        author=$(echo "$pr" | jq -r '.author.login')
        
        echo -e "  ${BOLD}${GREEN}PR #${number}${NC}: ${BOLD}${title}${NC}"
        echo -e "    ${CYAN}Repository:${NC} ${repo}"
        echo -e "    ${CYAN}Status:${NC} $(format_status "$state")"
        echo -e "    ${CYAN}Branch:${NC} ${head_ref} → ${base_ref}"
        echo -e "    ${CYAN}Changes:${NC} +${additions} / -${deletions} lines"
        echo -e "    ${CYAN}Updated:${NC} ${updated}"
        echo -e "    ${CYAN}URL:${NC} ${url}"
        
        if [[ "$is_draft" == "true" ]]; then
            echo -e "    ${YELLOW}⚠ Draft PR${NC}"
        fi
        
        # Review status
        local review_status
        case "$review_decision" in
            APPROVED) review_status="${GREEN}✓ Approved${NC}" ;;
            CHANGES_REQUESTED) review_status="${RED}✗ Changes Requested${NC}" ;;
            REVIEW_REQUIRED) review_status="${YELLOW}⏳ Review Required${NC}" ;;
            *) review_status="${YELLOW}⏳ Pending Review${NC}" ;;
        esac
        echo -e "    ${CYAN}Review Status:${NC} ${review_status}"
        
        # Review requests
        local reviewers
        reviewers=$(echo "$pr" | jq -r '[.reviewRequests[]?.login] | join(", ") // "None"')
        echo -e "    ${CYAN}Reviewers:${NC} ${reviewers}"
        
        # Reviews
        local review_count
        review_count=$(echo "$pr" | jq -r '[.reviews[]?] | length // 0')
        if [[ "$review_count" -gt 0 ]]; then
            echo -e "    ${CYAN}Reviews:${NC} ${review_count} review(s)"
            echo "$pr" | jq -r '.reviews[]? | "      - \(.author.login): \(.state) (\(.submittedAt // "N/A" | split("T")[0]))"' 2>/dev/null || true
        fi
        
        echo ""
    done
}

collect_github_issues() {
    command -v gh &> /dev/null || return 1
    
    print_subsection_header "GitHub Assigned Issues (precisetargetlabs)"
    
    local issues_json
    issues_json=$(gh search issues --assignee @me --org "$GITHUB_ORG" --state open --limit 100 \
        --json number,title,state,repository,url,updatedAt,body,labels,author,comments 2>/dev/null || echo "[]")
    
    local count
    count=$(echo "$issues_json" | jq 'length')
    
    if [[ "$count" -eq 0 ]]; then
        echo -e "  ${YELLOW}No assigned issues found${NC}"
        return
    fi
    
    echo "$issues_json" | jq -r '.[] | @json' | while IFS= read -r issue; do
        local number title state repo url updated body labels author comment_count
        
        number=$(echo "$issue" | jq -r '.number')
        title=$(echo "$issue" | jq -r '.title')
        state=$(echo "$issue" | jq -r '.state')
        repo=$(echo "$issue" | jq -r '.repository.nameWithOwner')
        url=$(echo "$issue" | jq -r '.url')
        updated=$(echo "$issue" | jq -r '.updatedAt' | cut -d'T' -f1)
        body=$(echo "$issue" | jq -r '.body // ""')
        labels=$(echo "$issue" | jq -r '[.labels[]?.name] | join(", ") // "None"')
        author=$(echo "$issue" | jq -r '.author.login')
        comment_count=$(echo "$issue" | jq -r '.comments.totalCount // 0')
        
        echo -e "  ${BOLD}${MAGENTA}Issue #${number}${NC}: ${BOLD}${title}${NC}"
        echo -e "    ${CYAN}Repository:${NC} ${repo}"
        echo -e "    ${CYAN}Status:${NC} $(format_status "$state")"
        echo -e "    ${CYAN}Author:${NC} ${author}"
        echo -e "    ${CYAN}Labels:${NC} ${labels}"
        echo -e "    ${CYAN}Comments:${NC} ${comment_count}"
        echo -e "    ${CYAN}Updated:${NC} ${updated}"
        echo -e "    ${CYAN}URL:${NC} ${url}"
        
        if [[ -n "$body" ]] && [[ "$body" != "null" ]] && [[ -n "$(echo "$body" | tr -d '[:space:]')" ]]; then
            echo -e "    ${CYAN}Description:${NC}"
            wrap_text "$body" 70
        fi
        
        echo ""
    done
}

###############################################################################
# GitLab Functions
###############################################################################

collect_gitlab_mrs() {
    command -v glab &> /dev/null || return 1
    
    print_subsection_header "GitLab Merge Requests (Rivian)"
    
    local user_info user_id
    user_info=$(glab api user 2>/dev/null || echo "{}")
    user_id=$(echo "$user_info" | jq -r '.id // empty' 2>/dev/null)
    
    [[ -z "$user_id" ]] || [[ "$user_id" == "null" ]] && echo -e "  ${YELLOW}Could not get user ID${NC}" && return 1
    
    local mrs_json
    mrs_json=$(glab api "merge_requests?author_id=${user_id}&state=opened&per_page=100" 2>/dev/null || echo "[]")
    
    # Validate JSON
    if ! echo "$mrs_json" | jq empty 2>/dev/null; then
        echo -e "  ${YELLOW}Invalid response from GitLab API${NC}"
        return 1
    fi
    
    # Filter for Rivian projects
    local rivian_mrs
    rivian_mrs=$(echo "$mrs_json" | jq -r '[.[] | select(.project != null and .project.path_with_namespace != null and (.project.path_with_namespace | ascii_downcase | contains("rivian")))]' 2>/dev/null || echo "[]")
    
    local count
    count=$(echo "$rivian_mrs" | jq 'length')
    
    if [[ "$count" -eq 0 ]]; then
        echo -e "  ${YELLOW}No open MRs found${NC}"
        return
    fi
    
    echo "$rivian_mrs" | jq -r '.[] | @json' | while IFS= read -r mr; do
        local iid title state project url updated description source_branch target_branch
        local changes_count approvals_required approvals_left
        
        iid=$(echo "$mr" | jq -r '.iid')
        title=$(echo "$mr" | jq -r '.title')
        state=$(echo "$mr" | jq -r '.state')
        project=$(echo "$mr" | jq -r '.project.path_with_namespace')
        url=$(echo "$mr" | jq -r '.web_url')
        updated=$(echo "$mr" | jq -r '.updated_at' | cut -d'T' -f1)
        description=$(echo "$mr" | jq -r '.description // ""')
        source_branch=$(echo "$mr" | jq -r '.source_branch // "N/A"')
        target_branch=$(echo "$mr" | jq -r '.target_branch // "N/A"')
        changes_count=$(echo "$mr" | jq -r '.changes_count // 0')
        approvals_required=$(echo "$mr" | jq -r '.approvals_required // 0')
        approvals_left=$(echo "$mr" | jq -r '.approvals_left // 0')
        
        echo -e "  ${BOLD}${MAGENTA}MR !${iid}${NC}: ${BOLD}${title}${NC}"
        echo -e "    ${CYAN}Project:${NC} ${project}"
        echo -e "    ${CYAN}Status:${NC} $(format_status "$state")"
        echo -e "    ${CYAN}Branch:${NC} ${source_branch} → ${target_branch}"
        echo -e "    ${CYAN}Changes:${NC} ${changes_count} files changed"
        echo -e "    ${CYAN}Updated:${NC} ${updated}"
        echo -e "    ${CYAN}URL:${NC} ${url}"
        
        # Approval status
        if [[ "$approvals_required" -gt 0 ]]; then
            if [[ "$approvals_left" -eq 0 ]]; then
                echo -e "    ${CYAN}Approvals:${NC} ${GREEN}✓ Approved (${approvals_required}/${approvals_required})${NC}"
            else
                echo -e "    ${CYAN}Approvals:${NC} ${YELLOW}⏳ Pending (${approvals_left} more required)${NC}"
            fi
        else
            echo -e "    ${CYAN}Approvals:${NC} Not required"
        fi
        
        # Get detailed MR info for lines changed
        local mr_detail
        mr_detail=$(glab mr view "$iid" --repo "$project" --json additions,deletions,work_in_progress,merge_status 2>/dev/null || echo "{}")
        
        if [[ -n "$mr_detail" ]] && [[ "$mr_detail" != "{}" ]]; then
            local additions deletions wip merge_status
            additions=$(echo "$mr_detail" | jq -r '.additions // 0')
            deletions=$(echo "$mr_detail" | jq -r '.deletions // 0')
            wip=$(echo "$mr_detail" | jq -r '.work_in_progress // false')
            merge_status=$(echo "$mr_detail" | jq -r '.merge_status // "unknown"')
            
            if [[ "$additions" != "0" ]] || [[ "$deletions" != "0" ]]; then
                echo -e "    ${CYAN}Lines:${NC} +${additions} / -${deletions}"
            fi
            
            if [[ "$wip" == "true" ]]; then
                echo -e "    ${YELLOW}⚠ Work in Progress${NC}"
            fi
            
            case "$merge_status" in
                can_be_merged) echo -e "    ${GREEN}✓ Can be merged${NC}" ;;
                cannot_be_merged) echo -e "    ${RED}✗ Cannot be merged${NC}" ;;
                checking) echo -e "    ${YELLOW}⏳ Checking mergeability${NC}" ;;
            esac
        fi
        
        if [[ -n "$description" ]] && [[ "$description" != "null" ]] && [[ -n "$(echo "$description" | tr -d '[:space:]')" ]]; then
            echo -e "    ${CYAN}Description:${NC}"
            # Remove markdown formatting for cleaner display
            local clean_desc
            clean_desc=$(echo "$description" | sed 's/#\{1,6\} //g' | sed 's/\*\*//g' | sed 's/\*//g')
            wrap_text "$clean_desc" 70
        fi
        
        echo ""
    done
}

###############################################################################
# Jira Functions
###############################################################################

collect_jira_cards() {
    [[ -z "$JIRA_API_TOKEN" ]] && echo -e "  ${YELLOW}JIRA_API_TOKEN not set${NC}" && return 1
    
    print_subsection_header "Jira Assigned Cards (Rivian)"
    
    local jira_base_url="${JIRA_INSTANCE_URL%/}"
    local jira_api_url="${jira_base_url}/rest/api/3"
    local jira_search_url="${jira_api_url}/search"
    
    # Create auth header
    local auth_string
    auth_string=$(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)
    local auth_header="Authorization: Basic $auth_string"
    
    # Search for assigned issues
    local jql_query="assignee = currentUser() AND status != Done AND status != Closed ORDER BY updated DESC"
    local search_response
    search_response=$(curl -s -X POST \
        -H "$auth_header" \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d "{\"jql\":\"$jql_query\",\"maxResults\":100,\"fields\":[\"summary\",\"status\",\"project\",\"updated\",\"description\",\"comment\",\"priority\",\"issuetype\",\"assignee\",\"reporter\",\"created\"]}" \
        "${jira_search_url}" 2>/dev/null || echo "{}")
    
    # Handle API migration
    if echo "$search_response" | jq -e '.errorMessages' >/dev/null 2>&1; then
        local error_msg
        error_msg=$(echo "$search_response" | jq -r '.errorMessages[0] // ""')
        if echo "$error_msg" | grep -q "migrate to.*search/jql"; then
            jira_search_url="${jira_api_url}/search/jql"
            search_response=$(curl -s -X POST \
                -H "$auth_header" \
                -H "Accept: application/json" \
                -H "Content-Type: application/json" \
                -d "{\"jql\":\"$jql_query\",\"maxResults\":100,\"fields\":[\"summary\",\"status\",\"project\",\"updated\",\"description\",\"comment\",\"priority\",\"issuetype\"]}" \
                "${jira_search_url}" 2>/dev/null || echo "{}")
        fi
    fi
    
    [[ -z "$search_response" ]] && echo -e "  ${YELLOW}No response from Jira${NC}" && return 1
    echo "$search_response" | jq -e '.errorMessages' >/dev/null 2>&1 && echo -e "  ${RED}Error: $(echo "$search_response" | jq -r '.errorMessages[0] // "Unknown error"')${NC}" && return 1
    
    local count
    count=$(echo "$search_response" | jq -r '.issues | length // 0')
    
    if [[ "$count" -eq 0 ]]; then
        echo -e "  ${YELLOW}No assigned cards found${NC}"
        return
    fi
    
    echo "$search_response" | jq -r '.issues[] | @json' | while IFS= read -r issue; do
        local key title status project updated description priority issue_type
        local assignee reporter created comments
        
        key=$(echo "$issue" | jq -r '.key')
        title=$(echo "$issue" | jq -r '.fields.summary')
        status=$(echo "$issue" | jq -r '.fields.status.name')
        project=$(echo "$issue" | jq -r '.fields.project.name')
        updated=$(echo "$issue" | jq -r '.fields.updated' | cut -d'T' -f1)
        description=$(echo "$issue" | jq -c '.fields.description // null' 2>/dev/null || echo "null")
        priority=$(echo "$issue" | jq -r '.fields.priority.name // "None"')
        issue_type=$(echo "$issue" | jq -r '.fields.issuetype.name // "Task"')
        assignee=$(echo "$issue" | jq -r '.fields.assignee.displayName // "Unassigned"')
        reporter=$(echo "$issue" | jq -r '.fields.reporter.displayName // "Unknown"')
        created=$(echo "$issue" | jq -r '.fields.created // ""' | cut -d'T' -f1)
        [[ "$created" == "null" ]] && created="N/A"
        comments=$(echo "$issue" | jq -c '.fields.comment.comments // []' 2>/dev/null || echo "[]")
        
        local url="${jira_base_url}/browse/${key}"
        local description_text
        description_text=$(extract_jira_description "$description")
        
        echo -e "  ${BOLD}${BLUE}${key}${NC}: ${BOLD}${title}${NC}"
        echo -e "    ${CYAN}Type:${NC} ${issue_type}"
        echo -e "    ${CYAN}Project:${NC} ${project}"
        echo -e "    ${CYAN}Status:${NC} $(format_status "$status")"
        echo -e "    ${CYAN}Priority:${NC} ${priority}"
        echo -e "    ${CYAN}Assignee:${NC} ${assignee}"
        echo -e "    ${CYAN}Reporter:${NC} ${reporter}"
        echo -e "    ${CYAN}Created:${NC} ${created}"
        echo -e "    ${CYAN}Updated:${NC} ${updated}"
        echo -e "    ${CYAN}URL:${NC} ${url}"
        
        if [[ -n "$description_text" ]] && [[ -n "$(echo "$description_text" | tr -d '[:space:]')" ]]; then
            echo -e "    ${CYAN}Description:${NC}"
            wrap_text "$description_text" 70
        fi
        
        # Comments
        local comment_count
        comment_count=$(echo "$comments" | jq -r 'length // 0')
        if [[ "$comment_count" -gt 0 ]]; then
            echo -e "    ${CYAN}Comments (${comment_count}):${NC}"
            echo "$comments" | jq -r '.[] | "      [\(.author.displayName) - \(.updated // .created | split("T")[0])]: \(.body // "" | gsub("\n"; " "))"' 2>/dev/null | while IFS= read -r comment; do
                wrap_text "$comment" 65
            done
        else
            echo -e "    ${CYAN}Comments:${NC} None"
        fi
        
        echo ""
    done
}

###############################################################################
# Main Function
###############################################################################

main() {
    echo -e "${BOLD}${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                  MY WORK SUMMARY                              ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_section_header "GitHub - Precisetargetlabs"
    collect_github_prs
    collect_github_issues
    
    print_section_header "GitLab - Rivian"
    collect_gitlab_mrs
    
    print_section_header "Jira - Rivian"
    collect_jira_cards
    
    echo ""
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}  Summary Complete${NC}"
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

main "$@"
