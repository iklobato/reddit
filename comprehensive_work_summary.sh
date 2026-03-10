#!/bin/bash

###############################################################################
# comprehensive_work_summary.sh - Complete Work Summary
# 
# Comprehensive script that collects and displays:
# 1. All repositories from precisetargetlabs organization
# 2. All tasks from GitHub Projects where user is assigned
# 3. All user PRs from precisetargetlabs (GitHub)
# 4. All assigned tasks from precisetargetlabs (GitHub Issues)
# 5. All user MRs from Rivian (GitLab)
# 6. All assigned Jira cards from multiple Jira instances:
#    - Rivian Jira (JIRA_TOKEN_RIVIAN)
#    - Orlo Jira (JIRA_TOKEN_ORLO)
# 7. All assigned Shortcut cards
#
# Environment Variables Required:
#   - JIRA_TOKEN_RIVIAN: Jira API token for Rivian instance
#   - JIRA_TOKEN_ORLO: Jira API token for Orlo instance
#   - JIRA_INSTANCE_URL_ORLO: Orlo Jira instance URL
#   - JIRA_EMAIL_ORLO: Email for Orlo Jira authentication
#   - SHORTCUT_API_KEY: Shortcut API key (optional)
#
# Usage: ./comprehensive_work_summary.sh
###############################################################################

set -uo pipefail

###############################################################################
# Configuration
###############################################################################

readonly GITHUB_ORG="precisetargetlabs"
readonly GITHUB_ORG_SANCTUM="HelloSanctum"
readonly GITHUB_PROJECT_NUMBER=14
readonly GITHUB_REPOS=("almagest" "monarch" "python-libs" "pyxis")
readonly GITLAB_ORG="rivian"

# Jira Configuration - Multiple Instances
# Rivian Jira
readonly JIRA_TOKEN_RIVIAN="${JIRA_TOKEN_RIVIAN:-}"
readonly JIRA_INSTANCE_URL_RIVIAN="https://rivianautomotivellc.atlassian.net"
readonly JIRA_EMAIL_RIVIAN="henriquelobato@rivian.com"

# Orlo Jira
readonly JIRA_TOKEN_ORLO="${JIRA_TOKEN_ORLO:-}"
readonly JIRA_INSTANCE_URL_ORLO="${JIRA_INSTANCE_URL_ORLO:-}"
readonly JIRA_EMAIL_ORLO="${JIRA_EMAIL_ORLO:-}"

readonly SHORTCUT_API_KEY="${SHORTCUT_API_KEY:-a11ffad3-59f0-4cc5-9b30-b29fadd16fc3}"
readonly SHORTCUT_API_BASE="https://api.app.shortcut.com/api/v3"

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
readonly DIM=$'\033[2m'
readonly NC=$'\033[0m'

###############################################################################
# Utility Functions
###############################################################################

print_main_header() {
    echo -e "${BOLD}${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              COMPREHENSIVE WORK SUMMARY                       ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

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
    local width="${2:-75}"
    echo "$text" | fold -w "$width" -s | sed 's/^/      /'
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

print_count_summary() {
    local label="$1"
    local count="$2"
    local color="${3:-${CYAN}}"
    echo -e "  ${color}${label}:${NC} ${BOLD}${count}${NC}"
}

###############################################################################
# Repository Collection (for filtering)
###############################################################################

# Global variable to store repositories with work items
readonly REPOS_WITH_WORK_FILE=$(mktemp /tmp/repos_with_work_XXXXXX)
readonly TASKS_JSON_FILE=$(mktemp /tmp/tasks_json_XXXXXX)
trap "rm -f $REPOS_WITH_WORK_FILE $TASKS_JSON_FILE" EXIT INT TERM

# Initialize tasks JSON file
echo "[]" > "$TASKS_JSON_FILE"

add_repo_with_work() {
    local repo="$1"
    echo "$repo" >> "$REPOS_WITH_WORK_FILE"
}

add_task_to_json() {
    local task_json="$1"
    # Merge the new task into the existing JSON array
    local current_tasks
    current_tasks=$(cat "$TASKS_JSON_FILE" 2>/dev/null || echo "[]")
    echo "$current_tasks" | jq --argjson new_task "$task_json" '. + [$new_task]' > "$TASKS_JSON_FILE"
}

print_progress() {
    local message="$1"
    echo -e "${DIM}  ${message}...${NC}" >&2
}

display_comprehensive_tables() {
    local tasks_json
    tasks_json=$(cat "$TASKS_JSON_FILE" 2>/dev/null || echo "[]")
    
    local task_count
    task_count=$(echo "$tasks_json" | jq 'length // 0')
    
    if [[ "$task_count" -eq 0 ]]; then
        echo -e "  ${YELLOW}No tasks found${NC}"
        return
    fi
    
    print_section_header "Comprehensive Work Summary"
    
    # Filter and display PRs/MRs table
    local prs_mrs
    prs_mrs=$(echo "$tasks_json" | jq '[.[] | select(.type == "PR" or .type == "Pull Request" or .type == "MR" or .type == "Merge Request")]' 2>/dev/null || echo "[]")
    local prs_mrs_count
    prs_mrs_count=$(echo "$prs_mrs" | jq 'length // 0')
    
    if [[ "$prs_mrs_count" -gt 0 ]]; then
        echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BOLD}${CYAN}  Pull Requests / Merge Requests (${prs_mrs_count})${NC}"
        echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "$prs_mrs" | python3 "$(dirname "$0")/format_tables.py" prs_mrs 2>/dev/null || {
            echo -e "  ${YELLOW}Error displaying PRs/MRs table. Using fallback format.${NC}"
            echo "$prs_mrs" | jq -r '.[] | "\(.company) | \(.id) | \(.title) | \(.status)"' 2>/dev/null || echo "  No PRs/MRs found"
        }
        echo ""
    fi
    
    # Filter and display Issues table
    local issues
    issues=$(echo "$tasks_json" | jq '[.[] | select(.type == "Issue")]' 2>/dev/null || echo "[]")
    local issues_count
    issues_count=$(echo "$issues" | jq 'length // 0')
    
    if [[ "$issues_count" -gt 0 ]]; then
        echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BOLD}${CYAN}  Issues (${issues_count})${NC}"
        echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "$issues" | python3 "$(dirname "$0")/format_tables.py" comprehensive 2>/dev/null || {
            echo -e "  ${YELLOW}Error displaying Issues table. Using fallback format.${NC}"
            echo "$issues" | jq -r '.[] | "\(.company) | \(.source) | \(.type) | \(.id) | \(.title) | \(.status)"' 2>/dev/null || echo "  No Issues found"
        }
        echo ""
    fi
    
    # Filter and display Cards (Shortcut/Jira) table
    # Only include items from Shortcut or Jira sources (exclude GitHub Project cards)
    local cards
    cards=$(echo "$tasks_json" | jq '[.[] | select((.source == "Shortcut" or .source == "Jira") and (.type != "PR" and .type != "Pull Request" and .type != "Issue" and .type != "MR" and .type != "Merge Request"))]' 2>/dev/null || echo "[]")
    local cards_count
    cards_count=$(echo "$cards" | jq 'length // 0')
    
    if [[ "$cards_count" -gt 0 ]]; then
        echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BOLD}${CYAN}  Cards - Shortcut / Jira (${cards_count})${NC}"
        echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "$cards" | python3 "$(dirname "$0")/format_tables.py" comprehensive 2>/dev/null || {
            echo -e "  ${YELLOW}Error displaying Cards table. Using fallback format.${NC}"
            echo "$cards" | jq -r '.[] | "\(.company) | \(.source) | \(.type) | \(.id) | \(.title) | \(.status)"' 2>/dev/null || echo "  No Cards found"
        }
        echo ""
    fi
    
    # Show summary if no items in any category
    if [[ "$prs_mrs_count" -eq 0 ]] && [[ "$issues_count" -eq 0 ]] && [[ "$cards_count" -eq 0 ]]; then
        echo -e "  ${YELLOW}No tasks found in any category${NC}"
    fi
}

has_work_items() {
    local repo_name="$1"
    grep -q "^${repo_name}$" "$REPOS_WITH_WORK_FILE" 2>/dev/null || return 1
}

###############################################################################
# GitHub Repository Listing
###############################################################################

list_repositories_with_work() {
    command -v gh &> /dev/null || { echo -e "  ${YELLOW}gh CLI not found${NC}"; return 1; }
    
    print_subsection_header "Repositories with Work Items (${GITHUB_ORG} & ${GITHUB_ORG_SANCTUM})"
    
    # Get unique list of repos with work
    local work_repos_list
    if [[ ! -f "$REPOS_WITH_WORK_FILE" ]] || [[ ! -s "$REPOS_WITH_WORK_FILE" ]]; then
        echo -e "  ${YELLOW}No repositories with work items found${NC}"
        return
    fi
    
    work_repos_list=$(sort -u "$REPOS_WITH_WORK_FILE" 2>/dev/null | grep -v '^$' | grep -v '^null$' || echo "")
    
    if [[ -z "$work_repos_list" ]]; then
        echo -e "  ${YELLOW}No repositories with work items found${NC}"
        return
    fi
    
    local actual_count
    actual_count=$(echo "$work_repos_list" | wc -l | tr -d ' ')
    
    print_count_summary "Repositories with work" "$actual_count"
    echo ""
    
    local all_orgs=("${GITHUB_ORG}" "${GITHUB_ORG_SANCTUM}")
    
    # Fetch each repo individually, trying both organizations
    echo "$work_repos_list" | while IFS= read -r repo_name; do
        [[ -z "$repo_name" ]] && continue
        [[ "$repo_name" == "null" ]] && continue
        
        local repo_json name url private description updated found=false
        
        # Try each organization
        for org in "${all_orgs[@]}"; do
            repo_json=$(gh api "repos/${org}/${repo_name}" 2>/dev/null || echo "{}")
            
            if [[ "$repo_json" != "{}" ]] && ! echo "$repo_json" | jq -e '.message' >/dev/null 2>&1; then
                found=true
                break
            fi
        done
        
        if [[ "$found" != "true" ]]; then
            # Repo not found in any organization, skip
            continue
        fi
        
        name=$(echo "$repo_json" | jq -r '.name // ""')
        url=$(echo "$repo_json" | jq -r '.html_url // ""')
        private=$(echo "$repo_json" | jq -r '.private // "false"')
        description=$(echo "$repo_json" | jq -r '.description // ""')
        updated=$(echo "$repo_json" | jq -r '.updated_at // ""' | cut -d'T' -f1)
        
        # Skip if essential fields are null or empty
        if [[ -z "$name" ]] || [[ "$name" == "null" ]] || [[ -z "$url" ]] || [[ "$url" == "null" ]]; then
            continue
        fi
        
        local privacy_icon
        [[ "$private" == "true" ]] && privacy_icon="${RED}🔒${NC}" || privacy_icon="${GREEN}🌐${NC}"
        
        echo -e "  ${BOLD}${name}${NC} ${privacy_icon}"
        echo -e "    ${CYAN}URL:${NC} ${url}"
        
        if [[ -n "$updated" ]] && [[ "$updated" != "null" ]]; then
            echo -e "    ${CYAN}Updated:${NC} ${updated}"
        fi
        
        if [[ -n "$description" ]] && [[ "$description" != "null" ]] && [[ "$description" != "No description" ]]; then
            echo -e "    ${CYAN}Description:${NC} ${description}"
        fi
        echo ""
    done || true
}

###############################################################################
# GitHub Project Tasks
###############################################################################

get_project_items() {
    local org="$1"
    local project_number="$2"
    local user_login="$3"
    
    local query
    read -r -d '' query <<EOF || true
query(\$org: String!, \$number: Int!) {
  organization(login: \$org) {
    projectV2(number: \$number) {
      title
      url
      items(first: 100) {
        nodes {
          id
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldTextValue {
                text
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldDateValue {
                date
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
            }
          }
          content {
            __typename
            ... on Issue {
              number
              title
              state
              url
              updatedAt
              repository {
                nameWithOwner
              }
              assignees(first: 20) {
                nodes {
                  login
                }
              }
              body
              labels(first: 10) {
                nodes {
                  name
                }
              }
            }
            ... on PullRequest {
              number
              title
              state
              url
              updatedAt
              repository {
                nameWithOwner
              }
              assignees(first: 20) {
                nodes {
                  login
                }
              }
              body
              isDraft
              reviewDecision
              additions
              deletions
            }
          }
        }
      }
    }
  }
}
EOF
    
    gh api graphql -f query="$query" -F org="$org" -F number="$project_number" 2>/dev/null || echo "{}"
}

list_project_tasks() {
    command -v gh &> /dev/null || return 1
    
    local user_login
    user_login=$(gh api user -q '.login' 2>/dev/null || echo "")
    [[ -z "$user_login" ]] && return 1
    
    print_progress "Collecting GitHub Project tasks"
    
    local response
    response=$(get_project_items "$GITHUB_ORG" "$GITHUB_PROJECT_NUMBER" "$user_login")
    
    local project_title
    project_title=$(echo "$response" | jq -r '.data.organization.projectV2.title // "Unknown"')
    
    if [[ "$project_title" == "null" ]] || [[ -z "$project_title" ]]; then
        return 1
    fi
    
    local assigned_items
    assigned_items=$(echo "$response" | jq -r --arg login "$user_login" '
      .data.organization.projectV2.items.nodes[]?
      | select(.content != null)
      | select([.content.assignees.nodes[]?.login] | any(. == $login))
      | @json
    ' 2>/dev/null)
    
    local count
    count=$(echo "$assigned_items" | grep -c '{' || echo "0")
    
    if [[ "$count" -eq 0 ]]; then
        return
    fi
    
    echo "$assigned_items" | while IFS= read -r item; do
        [[ -z "$item" ]] && continue
        
        local typename number title state url updated repo body
        local is_draft review_decision additions deletions labels
        
        typename=$(echo "$item" | jq -r '.content.__typename // ""')
        number=$(echo "$item" | jq -r '.content.number // ""')
        title=$(echo "$item" | jq -r '.content.title // ""')
        state=$(echo "$item" | jq -r '.content.state // ""')
        url=$(echo "$item" | jq -r '.content.url // ""')
        updated=$(echo "$item" | jq -r '.content.updatedAt // ""' | cut -d'T' -f1)
        repo=$(echo "$item" | jq -r '.content.repository.nameWithOwner // ""')
        body=$(echo "$item" | jq -r '.content.body // ""')
        
        [[ -z "$number" ]] && continue
        
        # Determine company based on repo
        local company="precisetargetlabs"
        if [[ "$repo" == *"HelloSanctum"* ]]; then
            company="sanctum"
        fi
        
        # Extract repo name and add to work items list
        if [[ -n "$repo" ]]; then
            local repo_name
            repo_name=$(echo "$repo" | cut -d'/' -f2)
            add_repo_with_work "$repo_name"
        fi
        
        local type_label
        case "$typename" in
            Issue) 
                type_label="Issue"
                labels=$(echo "$item" | jq -r '[.content.labels.nodes[]?.name] | join(", ") // "None"')
                ;;
            PullRequest)
                type_label="Pull Request"
                is_draft=$(echo "$item" | jq -r '.content.isDraft // false')
                review_decision=$(echo "$item" | jq -r '.content.reviewDecision // "PENDING"')
                additions=$(echo "$item" | jq -r '.content.additions // 0')
                deletions=$(echo "$item" | jq -r '.content.deletions // 0')
                ;;
            *)
                type_label="Card"
                ;;
        esac
        
        # Build ID
        local id="#${number}"
        
        # Build additional info
        local additional_info=""
        if [[ "$typename" == "Issue" ]]; then
            additional_info="Labels: ${labels}"
        elif [[ "$typename" == "PullRequest" ]]; then
            local review_info=""
            case "$review_decision" in
                APPROVED) review_info="Review: Approved" ;;
                CHANGES_REQUESTED) review_info="Review: Changes Requested" ;;
                REVIEW_REQUIRED) review_info="Review: Required" ;;
                *) review_info="Review: Pending" ;;
            esac
            local draft_info=""
            [[ "$is_draft" == "true" ]] && draft_info="Draft"
            additional_info="${draft_info:+${draft_info} | }${review_info} | Changes: +${additions}/-${deletions}"
        fi
        
        # Add to JSON for centralized tables
        local task_json
        task_json=$(jq -n \
            --arg company "$company" \
            --arg source "GitHub" \
            --arg type "$type_label" \
            --arg id "$id" \
            --arg title "$title" \
            --arg status "$state" \
            --arg repo "$repo" \
            --arg updated "$updated" \
            --arg url "$url" \
            --arg additional "$additional_info" \
            '{company: $company, source: $source, type: $type, id: $id, title: $title, status: $status, repo: $repo, updated: $updated, url: $url, additional: $additional}' 2>/dev/null)
        [[ -n "$task_json" ]] && add_task_to_json "$task_json"
    done
}

###############################################################################
# GitHub PRs and Issues
###############################################################################

collect_github_prs() {
    command -v gh &> /dev/null || return 1
    
    local user_login
    user_login=$(gh api user -q '.login' 2>/dev/null || echo "")
    [[ -z "$user_login" ]] && return 1
    
    print_progress "Collecting GitHub Pull Requests"
    
    # Collect PRs from all organizations
    local all_orgs=("${GITHUB_ORG}" "${GITHUB_ORG_SANCTUM}")
    local all_prs_json="[]"
    
    for org in "${all_orgs[@]}"; do
        local repos_to_check=()
        
        if [[ "$org" == "$GITHUB_ORG" ]]; then
            # For precisetargetlabs, only check specific repositories
            repos_to_check=("${GITHUB_REPOS[@]}")
        else
            # For other orgs (like HelloSanctum), get all repositories
            local repos_json
            repos_json=$(gh api "orgs/${org}/repos" --paginate 2>/dev/null || echo "[]")
            local all_repos
            all_repos=$(echo "$repos_json" | jq -s 'flatten')
            
            # Extract repo names
            while IFS= read -r repo_name; do
                [[ -n "$repo_name" ]] && repos_to_check+=("$repo_name")
            done < <(echo "$all_repos" | jq -r '.[] | .name')
        fi
        
        # Iterate over repositories and check for PRs
        for repo_name in "${repos_to_check[@]}"; do
            [[ -z "$repo_name" ]] && continue
            
            local repo_prs
            repo_prs=$(gh pr list --repo "${org}/${repo_name}" --author "$user_login" --state open --limit 100 \
                --json number,title,state,url,createdAt,updatedAt,additions,deletions,reviewDecision,isDraft,reviewRequests,reviews,headRefName,baseRefName,author,comments 2>/dev/null || echo "[]")
            
            local pr_count
            pr_count=$(echo "$repo_prs" | jq 'length // 0')
            
            if [[ "$pr_count" -gt 0 ]]; then
                echo "$repo_prs" | jq -r --arg repo "${org}/${repo_name}" '.[] | . + {repository: $repo} | @json'
            fi
        done | jq -s '.' > /tmp/all_prs_${org}.json 2>/dev/null || echo "[]" > /tmp/all_prs_${org}.json
    done
    
    # Merge all PRs from all organizations
    local prs_json
    prs_json=$(jq -s 'flatten' /tmp/all_prs_*.json 2>/dev/null || echo "[]")
    rm -f /tmp/all_prs_*.json
    
    local count
    count=$(echo "$prs_json" | jq 'length // 0')
    
    if [[ "$count" -eq 0 ]]; then
        return
    fi
    
    echo "$prs_json" | jq -r '.[] | @json' | while IFS= read -r pr; do
        local number title state repo url created updated additions deletions review_decision is_draft head_ref base_ref
        local author reviewers total_comments resolved_review_comments
        
        number=$(echo "$pr" | jq -r '.number')
        title=$(echo "$pr" | jq -r '.title')
        state=$(echo "$pr" | jq -r '.state')
        repo=$(echo "$pr" | jq -r '.repository // ""')
        url=$(echo "$pr" | jq -r '.url')
        created=$(echo "$pr" | jq -r '.createdAt // ""' | cut -d'T' -f1)
        updated=$(echo "$pr" | jq -r '.updatedAt' | cut -d'T' -f1)
        additions=$(echo "$pr" | jq -r '.additions // 0')
        deletions=$(echo "$pr" | jq -r '.deletions // 0')
        review_decision=$(echo "$pr" | jq -r '.reviewDecision // "PENDING"')
        is_draft=$(echo "$pr" | jq -r '.isDraft // false')
        head_ref=$(echo "$pr" | jq -r '.headRefName')
        base_ref=$(echo "$pr" | jq -r '.baseRefName')
        author=$(echo "$pr" | jq -r '.author.login // ""')
        reviewers=$(echo "$pr" | jq -r '[.reviewRequests[]?.login] | join(", ") // "None"')
        
        # Get comment counts
        # Comments is an array, so count its length
        total_comments=$(echo "$pr" | jq -r '[.comments[]?] | length // 0')
        # Count resolved review comments - reviews that have been submitted (not just requested)
        # This represents reviews that have been completed/addressed
        resolved_review_comments=$(echo "$pr" | jq -r '[.reviews[]? | select(.state != null and .state != "")] | length // 0')
        
        # Extract repo name and add to work items list
        local company="precisetargetlabs"
        if [[ "$repo" == *"HelloSanctum"* ]]; then
            company="sanctum"
        fi
        
        if [[ -n "$repo" ]]; then
            local repo_name
            repo_name=$(echo "$repo" | cut -d'/' -f2)
            add_repo_with_work "$repo_name"
        fi
        
        # Build additional info
        local review_status=""
        case "$review_decision" in
            APPROVED) review_status="Review: Approved" ;;
            CHANGES_REQUESTED) review_status="Review: Changes Requested" ;;
            REVIEW_REQUIRED) review_status="Review: Required" ;;
            *) review_status="Review: Pending" ;;
        esac
        
        local draft_info=""
        [[ "$is_draft" == "true" ]] && draft_info="Draft"
        
        local branch_info="Branch: ${head_ref}→${base_ref}"
        local changes_info="Changes: +${additions}/-${deletions}"
        
        local additional_info="${draft_info:+${draft_info} | }${review_status} | ${branch_info} | ${changes_info}"
        if [[ -n "$reviewers" ]] && [[ "$reviewers" != "None" ]]; then
            additional_info="${additional_info} | Reviewers: ${reviewers}"
        fi
        
        # Add to JSON for centralized tables
        local task_json
        task_json=$(jq -n \
            --arg company "$company" \
            --arg source "GitHub" \
            --arg type "PR" \
            --arg id "#${number}" \
            --arg title "$title" \
            --arg status "$state" \
            --arg repo "$repo" \
            --arg updated "$updated" \
            --arg url "$url" \
            --arg additional "$additional_info" \
            --arg total_comments "$total_comments" \
            --arg resolved_review_comments "$resolved_review_comments" \
            '{company: $company, source: $source, type: $type, id: $id, title: $title, status: $status, repo: $repo, updated: $updated, url: $url, additional: $additional, total_comments: $total_comments, resolved_review_comments: $resolved_review_comments}' 2>/dev/null)
        [[ -n "$task_json" ]] && add_task_to_json "$task_json"
    done
}

collect_github_issues() {
    command -v gh &> /dev/null || return 1
    
    print_progress "Collecting GitHub Issues"
    
    local issues_json
    issues_json=$(gh search issues --assignee @me --org "$GITHUB_ORG" --state open --limit 100 \
        --json number,title,state,repository,url,updatedAt,body,labels,author,comments 2>/dev/null || echo "[]")
    
    local count
    count=$(echo "$issues_json" | jq 'length')
    
    if [[ "$count" -eq 0 ]]; then
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
        
        # Extract repo name and add to work items list
        local company="precisetargetlabs"
        if [[ -n "$repo" ]]; then
            local repo_name
            repo_name=$(echo "$repo" | cut -d'/' -f2)
            add_repo_with_work "$repo_name"
        fi
        
        # Build additional info
        local additional_info="Labels: ${labels}"
        if [[ "$comment_count" -gt 0 ]]; then
            additional_info="${additional_info} | Comments: ${comment_count}"
        fi
        additional_info="${additional_info} | Author: ${author}"
        
        # Add to JSON for centralized tables
        local task_json
        task_json=$(jq -n \
            --arg company "$company" \
            --arg source "GitHub" \
            --arg type "Issue" \
            --arg id "#${number}" \
            --arg title "$title" \
            --arg status "$state" \
            --arg repo "$repo" \
            --arg updated "$updated" \
            --arg url "$url" \
            --arg additional "$additional_info" \
            '{company: $company, source: $source, type: $type, id: $id, title: $title, status: $status, repo: $repo, updated: $updated, url: $url, additional: $additional}' 2>/dev/null)
        [[ -n "$task_json" ]] && add_task_to_json "$task_json"
    done
}

###############################################################################
# GitLab MRs
###############################################################################

collect_gitlab_mrs() {
    command -v glab &> /dev/null || return 1
    
    print_progress "Collecting GitLab Merge Requests"
    
    local user_info username
    user_info=$(glab api user 2>/dev/null || echo "{}")
    username=$(echo "$user_info" | jq -r '.username // empty' 2>/dev/null)
    
    [[ -z "$username" ]] || [[ "$username" == "null" ]] && return 1
    
    # Get all MRs for the user
    local mrs_json
    mrs_json=$(glab api "merge_requests?author_username=${username}&state=opened&per_page=100" 2>/dev/null || echo "[]")
    
    if ! echo "$mrs_json" | jq empty 2>/dev/null; then
        return 1
    fi
    
    # Filter for Rivian MRs by checking web_url
    local rivian_mrs
    rivian_mrs=$(echo "$mrs_json" | jq -r '[.[] | select(.web_url != null and (.web_url | ascii_downcase | contains("rivian")))]' 2>/dev/null || echo "[]")
    
    local count
    count=$(echo "$rivian_mrs" | jq 'length // 0')
    
    if [[ "$count" -eq 0 ]]; then
        return
    fi
    
    echo "$rivian_mrs" | jq -r '.[] | @json' | while IFS= read -r mr; do
        local iid project_id url
        iid=$(echo "$mr" | jq -r '.iid')
        project_id=$(echo "$mr" | jq -r '.project_id // .target_project_id // empty')
        url=$(echo "$mr" | jq -r '.web_url')
        
        [[ -z "$project_id" ]] || [[ "$project_id" == "null" ]] && continue
        
        # Fetch full MR details including project info
        local mr_full project_path
        mr_full=$(glab api "projects/${project_id}/merge_requests/${iid}" 2>/dev/null || echo "{}")
        project_path=$(glab api "projects/${project_id}" 2>/dev/null | jq -r '.path_with_namespace // ""' 2>/dev/null)
        
        # If project_path is still empty, extract from web_url
        if [[ -z "$project_path" ]] && [[ -n "$url" ]]; then
            # Extract from URL like: https://gitlab.com/rivian/dc/core-services/oms/order-management-monorepo/-/merge_requests/356
            project_path=$(echo "$url" | sed -E 's|https://[^/]+/([^/]+/[^/]+/[^/]+/[^/]+/[^/]+)/-.*|\1|' 2>/dev/null || echo "")
        fi
        
        local title state updated description source_branch target_branch
        local changes_count approvals_required approvals_left work_in_progress merge_status
        local additions deletions
        
        title=$(echo "$mr_full" | jq -r '.title // ""')
        state=$(echo "$mr_full" | jq -r '.state // "opened"')
        updated=$(echo "$mr_full" | jq -r '.updated_at // ""' | cut -d'T' -f1)
        description=$(echo "$mr_full" | jq -r '.description // ""')
        source_branch=$(echo "$mr_full" | jq -r '.source_branch // "N/A"')
        target_branch=$(echo "$mr_full" | jq -r '.target_branch // "N/A"')
        changes_count=$(echo "$mr_full" | jq -r '.changes_count // "0"')
        approvals_required=$(echo "$mr_full" | jq -r '.approvals_before_merge // 0')
        approvals_left=$(echo "$mr_full" | jq -r '.approvals_left // 0')
        work_in_progress=$(echo "$mr_full" | jq -r '.work_in_progress // false')
        merge_status=$(echo "$mr_full" | jq -r '.merge_status // "unknown"')
        
        # Try to get additions/deletions from changes endpoint
        local changes_json diff_text
        changes_json=$(glab api "projects/${project_id}/merge_requests/${iid}/changes" 2>/dev/null || echo "{}")
        diff_text=$(echo "$changes_json" | jq -r '.changes[]?.diff // ""' 2>/dev/null || echo "")
        
        additions=0
        deletions=0
        
        if [[ -n "$diff_text" ]] && [[ "$diff_text" != "null" ]] && [[ -n "$(echo "$diff_text" | tr -d '[:space:]')" ]]; then
            # Count additions and deletions from diff, ensuring numeric values
            local add_count del_count header_count
            add_count=$(echo "$diff_text" | grep -c '^+' 2>/dev/null | tr -d '\n\r' || echo "0")
            del_count=$(echo "$diff_text" | grep -c '^-' 2>/dev/null | tr -d '\n\r' || echo "0")
            
            # Ensure they're numeric
            add_count=$((add_count + 0))
            del_count=$((del_count + 0))
            
            # Subtract diff headers (+++ and ---)
            header_count=$(echo "$diff_text" | grep -c '^+++' 2>/dev/null | tr -d '\n\r' || echo "0")
            header_count=$((header_count + 0))
            additions=$((add_count - header_count))
            [[ $additions -lt 0 ]] && additions=0
            
            header_count=$(echo "$diff_text" | grep -c '^---' 2>/dev/null | tr -d '\n\r' || echo "0")
            header_count=$((header_count + 0))
            deletions=$((del_count - header_count))
            [[ $deletions -lt 0 ]] && deletions=0
        fi
        
        # Extract repo name from project path and add to work items list
        local company="rivian"
        if [[ -n "$project_path" ]]; then
            local repo_name
            repo_name=$(echo "$project_path" | rev | cut -d'/' -f1 | rev)
            add_repo_with_work "$repo_name"
        fi
        
        # Build additional info
        local wip_info=""
        [[ "$work_in_progress" == "true" ]] && wip_info="WIP"
        
        local merge_info=""
        case "$merge_status" in
            can_be_merged) merge_info="Merge: Ready" ;;
            cannot_be_merged) merge_info="Merge: Blocked" ;;
            checking) merge_info="Merge: Checking" ;;
            *) merge_info="Merge: ${merge_status}" ;;
        esac
        
        local approval_info=""
        if [[ "$approvals_required" -gt 0 ]]; then
            if [[ "$approvals_left" -eq 0 ]]; then
                approval_info="Approved (${approvals_required}/${approvals_required})"
            else
                approval_info="Pending (${approvals_left} more)"
            fi
        else
            approval_info="Not required"
        fi
        
        local branch_info="Branch: ${source_branch}→${target_branch}"
        local changes_info="Files: ${changes_count}"
        if [[ "$additions" != "0" ]] || [[ "$deletions" != "0" ]]; then
            changes_info="${changes_info} | Lines: +${additions}/-${deletions}"
        fi
        
        local additional_info="${wip_info:+${wip_info} | }${merge_info} | ${approval_info} | ${branch_info} | ${changes_info}"
        
        # Get comment counts for MR
        local total_comments resolved_review_comments
        # Get notes (comments) for the MR
        local notes_json
        notes_json=$(glab api "projects/${project_id}/merge_requests/${iid}/notes" 2>/dev/null || echo "[]")
        total_comments=$(echo "$notes_json" | jq -r 'length // 0' 2>/dev/null || echo "0")
        # Count resolved comments (notes with resolved_at not null)
        resolved_review_comments=$(echo "$notes_json" | jq -r '[.[] | select(.resolved_at != null)] | length // 0' 2>/dev/null || echo "0")
        
        # Add to JSON for centralized tables
        local task_json
        task_json=$(jq -n \
            --arg company "$company" \
            --arg source "GitLab" \
            --arg type "MR" \
            --arg id "!${iid}" \
            --arg title "$title" \
            --arg status "$state" \
            --arg repo "$project_path" \
            --arg updated "$updated" \
            --arg url "$url" \
            --arg additional "$additional_info" \
            --arg total_comments "$total_comments" \
            --arg resolved_review_comments "$resolved_review_comments" \
            '{company: $company, source: $source, type: $type, id: $id, title: $title, status: $status, repo: $repo, updated: $updated, url: $url, additional: $additional, total_comments: $total_comments, resolved_review_comments: $resolved_review_comments}' 2>/dev/null)
        [[ -n "$task_json" ]] && add_task_to_json "$task_json"
    done
}

###############################################################################
# Shortcut Cards (Sanctum)
###############################################################################

collect_shortcut_cards() {
    [[ -z "$SHORTCUT_API_KEY" ]] && return 1
    
    print_progress "Collecting Shortcut Cards"
    
    local member_response member_id
    member_response=$(curl -s -X GET \
        -H "Shortcut-Token: $SHORTCUT_API_KEY" \
        "${SHORTCUT_API_BASE}/member" 2>/dev/null || echo "{}")
    
    if echo "$member_response" | jq -e '.error' >/dev/null 2>&1; then
        return 1
    fi
    
    member_id=$(echo "$member_response" | jq -r '.id // empty' 2>/dev/null)
    mention_name=$(echo "$member_response" | jq -r '.mention_name // empty' 2>/dev/null)
    
    [[ -z "$member_id" ]] || [[ "$member_id" == "null" ]] && return 1
    [[ -z "$mention_name" ]] || [[ "$mention_name" == "null" ]] && return 1
    
    # Use mention_name in query (works better than member ID)
    local stories_response
    stories_response=$(curl -s -X GET \
        -H "Shortcut-Token: $SHORTCUT_API_KEY" \
        "${SHORTCUT_API_BASE}/search/stories?query=owner:${mention_name}&page_size=100" 2>/dev/null || echo "{}")
    
    # If query with mention_name fails or returns 0, try alternative method
    local total_count
    total_count=$(echo "$stories_response" | jq -r '.total // 0' 2>/dev/null || echo "0")
    
    if echo "$stories_response" | jq -e '.error' >/dev/null 2>&1 || [[ "$total_count" == "0" ]]; then
        # Fallback: get all open stories and filter by owner_ids
        stories_response=$(curl -s -X GET \
            -H "Shortcut-Token: $SHORTCUT_API_KEY" \
            "${SHORTCUT_API_BASE}/search/stories?query=is:open%20is:story&page_size=100" 2>/dev/null || echo "{}")
        
        # Filter by owner_ids containing member_id
        if ! echo "$stories_response" | jq -e '.error' >/dev/null 2>&1; then
            local filtered_data
            filtered_data=$(echo "$stories_response" | jq -r --arg member_id "$member_id" '[.data[]? | select(.owner_ids != null and (.owner_ids | length > 0) and (.owner_ids[] == $member_id))]' 2>/dev/null || echo "[]")
            stories_response=$(echo "{\"data\": $filtered_data, \"total\": $(echo "$filtered_data" | jq 'length')}" 2>/dev/null || echo "{}")
        fi
    fi
    
    # Check for errors
    if echo "$stories_response" | jq -e '.error' >/dev/null 2>&1; then
        return 1
    fi
    
    # Extract stories array and filter out completed/archived stories
    local active_stories
    if echo "$stories_response" | jq -e '.data' >/dev/null 2>&1; then
        # Filter: exclude Done/Completed states and archived stories
        # Note: workflow_state_name can be null for open stories
        active_stories=$(echo "$stories_response" | jq -r '[.data[]? | select((.workflow_state_name == null or (.workflow_state_name != "Done" and .workflow_state_name != "Completed")) and (.archived == false or .archived == null))]' 2>/dev/null || echo "[]")
    else
        active_stories="[]"
    fi
    
    # Ensure active_stories is valid JSON
    if ! echo "$active_stories" | jq empty 2>/dev/null; then
        active_stories="[]"
    fi
    
    local count
    count=$(echo "$active_stories" | jq 'length // 0' 2>/dev/null || echo "0")
    
    if [[ "$count" -eq 0 ]]; then
        return
    fi
    
    echo "$active_stories" | jq -r '.[] | @json' | while IFS= read -r story; do
        local id name state project updated url description story_type estimate
        local labels owner
        
        id=$(echo "$story" | jq -r '.id // ""')
        name=$(echo "$story" | jq -r '.name // ""')
        state=$(echo "$story" | jq -r '.workflow_state_name // .workflow_state.name // "Open"')
        project=$(echo "$story" | jq -r '.project.name // .group.name // "Unknown"')
        updated=$(echo "$story" | jq -r '.updated_at // ""' | cut -d'T' -f1)
        url=$(echo "$story" | jq -r '.app_url // ""')
        description=$(echo "$story" | jq -r '.description // ""')
        story_type=$(echo "$story" | jq -r '.story_type // "Story"')
        estimate=$(echo "$story" | jq -r '.estimate // 0')
        labels=$(echo "$story" | jq -r '[.labels[]?.name] | join(", ") // "None"' 2>/dev/null || echo "None")
        owner=$(echo "$story" | jq -r '.owner_ids[0] // ""' 2>/dev/null || echo "")
        
        # Extract repo name from project and add to work items list
        if [[ -n "$project" ]] && [[ "$project" != "Unknown" ]]; then
            local repo_name
            repo_name=$(echo "$project" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')
            add_repo_with_work "$repo_name"
        fi
        
        # Build additional info
        local additional_info="Type: ${story_type}"
        if [[ "$estimate" != "0" ]] && [[ "$estimate" != "null" ]]; then
            additional_info="${additional_info} | Estimate: ${estimate} pts"
        fi
        if [[ "$labels" != "None" ]] && [[ -n "$labels" ]]; then
            additional_info="${additional_info} | Labels: ${labels}"
        fi
        
        # Add to JSON for centralized tables
        local company="sanctum"
        local task_json
        task_json=$(jq -n \
            --arg company "$company" \
            --arg source "Shortcut" \
            --arg type "$story_type" \
            --arg id "#${id}" \
            --arg title "$name" \
            --arg status "$state" \
            --arg repo "$project" \
            --arg updated "$updated" \
            --arg url "$url" \
            --arg additional "$additional_info" \
            '{company: $company, source: $source, type: $type, id: $id, title: $title, status: $status, repo: $repo, updated: $updated, url: $url, additional: $additional}' 2>/dev/null)
        [[ -n "$task_json" ]] && add_task_to_json "$task_json"
    done
}


###############################################################################
# Jira Cards
###############################################################################

collect_jira_cards_from_instance() {
    local jira_token="$1"
    local jira_instance_url="$2"
    local jira_email="$3"
    local company_name="$4"
    
    [[ -z "$jira_token" ]] && return 1
    [[ -z "$jira_instance_url" ]] && return 1
    [[ -z "$jira_email" ]] && return 1
    
    local jira_base_url="${jira_instance_url%/}"
    local jira_api_url="${jira_base_url}/rest/api/3"
    local jira_search_url="${jira_api_url}/search"
    
    local auth_string
    auth_string=$(echo -n "${jira_email}:${jira_token}" | base64)
    local auth_header="Authorization: Basic $auth_string"
    
    # Updated JQL query to include both assigned AND watched issues
    local jql_query="(assignee = currentUser() OR watcher = currentUser()) AND status != Done AND status != Closed ORDER BY updated DESC"
    local search_response
    search_response=$(curl -s -X POST \
        -H "$auth_header" \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d "{\"jql\":\"$jql_query\",\"maxResults\":100,\"fields\":[\"summary\",\"status\",\"project\",\"updated\",\"description\",\"comment\",\"priority\",\"issuetype\",\"assignee\",\"reporter\",\"created\",\"watches\"]}" \
        "${jira_search_url}" 2>/dev/null || echo "{}")
    
    if echo "$search_response" | jq -e '.errorMessages' >/dev/null 2>&1; then
        local error_msg
        error_msg=$(echo "$search_response" | jq -r '.errorMessages[0] // ""')
        if echo "$error_msg" | grep -q "migrate to.*search/jql"; then
            jira_search_url="${jira_api_url}/search/jql"
            search_response=$(curl -s -X POST \
                -H "$auth_header" \
                -H "Accept: application/json" \
                -H "Content-Type: application/json" \
                -d "{\"jql\":\"$jql_query\",\"maxResults\":100,\"fields\":[\"summary\",\"status\",\"project\",\"updated\",\"description\",\"comment\",\"priority\",\"issuetype\",\"watches\"]}" \
                "${jira_search_url}" 2>/dev/null || echo "{}")
        fi
    fi
    
    [[ -z "$search_response" ]] && return 1
    echo "$search_response" | jq -e '.errorMessages' >/dev/null 2>&1 && return 1
    
    local count
    count=$(echo "$search_response" | jq -r '.issues | length // 0')
    
    if [[ "$count" -eq 0 ]]; then
        return
    fi
    
    echo "$search_response" | jq -r '.issues[] | @json' | while IFS= read -r issue; do
        local key title status project updated description priority issue_type
        local assignee reporter created comments watch_count is_watching
        
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
        local comment_count
        comment_count=$(echo "$comments" | jq -r 'length // 0' 2>/dev/null || echo "0")
        
        # Get watch information
        watch_count=$(echo "$issue" | jq -r '.fields.watches.watchCount // 0' 2>/dev/null || echo "0")
        is_watching=$(echo "$issue" | jq -r '.fields.watches.isWatching // false' 2>/dev/null || echo "false")
        
        local url="${jira_base_url}/browse/${key}"
        local description_text
        description_text=$(extract_jira_description "$description")
        
        # Build additional info
        local additional_info="Type: ${issue_type} | Priority: ${priority}"
        
        # Add assignee info
        if [[ "$assignee" != "Unassigned" ]]; then
            additional_info="${additional_info} | Assignee: ${assignee}"
        fi
        
        # Add watching indicator
        if [[ "$is_watching" == "true" ]]; then
            additional_info="${additional_info} | 👁 Watching"
            if [[ "$watch_count" -gt 0 ]]; then
                additional_info="${additional_info} (${watch_count})"
            fi
        fi
        
        if [[ "$comment_count" -gt 0 ]]; then
            additional_info="${additional_info} | Comments: ${comment_count}"
        fi
        additional_info="${additional_info} | Reporter: ${reporter}"
        
        # Add to JSON for centralized tables
        local task_json
        task_json=$(jq -n \
            --arg company "$company_name" \
            --arg source "Jira" \
            --arg type "$issue_type" \
            --arg id "$key" \
            --arg title "$title" \
            --arg status "$status" \
            --arg repo "$project" \
            --arg updated "$updated" \
            --arg created "$created" \
            --arg url "$url" \
            --arg additional "$additional_info" \
            --arg priority "$priority" \
            --arg assignee "$assignee" \
            --arg reporter "$reporter" \
            --arg comment_count "$comment_count" \
            --arg watch_count "$watch_count" \
            --arg is_watching "$is_watching" \
            --arg description "$description_text" \
            '{company: $company, source: $source, type: $type, id: $id, title: $title, status: $status, repo: $repo, updated: $updated, created: $created, url: $url, additional: $additional, priority: $priority, assignee: $assignee, reporter: $reporter, comment_count: $comment_count, watch_count: $watch_count, is_watching: $is_watching, description: $description}' 2>/dev/null)
        [[ -n "$task_json" ]] && add_task_to_json "$task_json"
    done
}

collect_jira_cards() {
    print_progress "Collecting Jira Cards from all instances"
    
    # Collect from Rivian Jira
    if [[ -n "$JIRA_TOKEN_RIVIAN" ]]; then
        print_progress "  - Collecting from Rivian Jira"
        collect_jira_cards_from_instance "$JIRA_TOKEN_RIVIAN" "$JIRA_INSTANCE_URL_RIVIAN" "$JIRA_EMAIL_RIVIAN" "rivian" || true
    fi
    
    # Collect from Orlo Jira
    if [[ -n "$JIRA_TOKEN_ORLO" ]] && [[ -n "$JIRA_INSTANCE_URL_ORLO" ]] && [[ -n "$JIRA_EMAIL_ORLO" ]]; then
        print_progress "  - Collecting from Orlo Jira"
        collect_jira_cards_from_instance "$JIRA_TOKEN_ORLO" "$JIRA_INSTANCE_URL_ORLO" "$JIRA_EMAIL_ORLO" "orlo" || true
    fi
}

###############################################################################
# Main Function
###############################################################################

main() {
    print_main_header
    
    # Initialize repos with work file
    > "$REPOS_WITH_WORK_FILE"
    
    # Collect all work items silently
    echo -e "${DIM}Collecting work items from all sources...${NC}"
    echo ""
    
    list_project_tasks || true
    collect_github_prs || true
    collect_github_issues || true
    collect_gitlab_mrs || true
    collect_jira_cards || true
    collect_shortcut_cards || true
    
    # Display comprehensive tables
    display_comprehensive_tables
    
    echo ""
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}  Summary Complete${NC}"
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

main "$@"
