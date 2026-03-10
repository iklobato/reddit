#!/bin/bash

###############################################################################
# list_precisetarget_repos_and_tasks.sh
# 
# Lists:
# - All repositories from precisetargetlabs organization
# - All tasks from GitHub Projects where user is assigned
#
# Usage: ./list_precisetarget_repos_and_tasks.sh
###############################################################################

set -euo pipefail

###############################################################################
# Configuration
###############################################################################

readonly ORG="precisetargetlabs"
readonly PROJECT_NUMBER=14

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

###############################################################################
# Repository Listing
###############################################################################

list_all_repositories() {
    command -v gh &> /dev/null || { echo "gh CLI not found"; return 1; }
    
    print_subsection_header "All Repositories from ${ORG}"
    
    local repos_json
    repos_json=$(gh api "orgs/${ORG}/repos" --paginate 2>/dev/null || echo "[]")
    
    # Combine paginated results into single array
    local all_repos
    all_repos=$(echo "$repos_json" | jq -s 'flatten | sort_by(.name)')
    
    local count
    count=$(echo "$all_repos" | jq 'length')
    
    echo -e "  ${CYAN}Total repositories: ${BOLD}${count}${NC}"
    echo ""
    
    echo "$all_repos" | jq -r '.[] | @json' | while IFS= read -r repo; do
        local name url private description updated
        name=$(echo "$repo" | jq -r '.name')
        url=$(echo "$repo" | jq -r '.html_url')
        private=$(echo "$repo" | jq -r '.private')
        description=$(echo "$repo" | jq -r '.description // "No description"')
        updated=$(echo "$repo" | jq -r '.updated_at' | cut -d'T' -f1)
        
        local privacy_icon
        [[ "$private" == "true" ]] && privacy_icon="${RED}🔒${NC}" || privacy_icon="${GREEN}🌐${NC}"
        
        echo -e "  ${BOLD}${name}${NC} ${privacy_icon}"
        echo -e "    ${CYAN}URL:${NC} ${url}"
        echo -e "    ${CYAN}Updated:${NC} ${updated}"
        if [[ "$description" != "No description" ]] && [[ -n "$description" ]]; then
            echo -e "    ${CYAN}Description:${NC} ${description}"
        fi
        echo ""
    done
}

###############################################################################
# Project Tasks Listing
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
    command -v gh &> /dev/null || { echo "gh CLI not found"; return 1; }
    
    local user_login
    user_login=$(gh api user -q '.login' 2>/dev/null || echo "")
    [[ -z "$user_login" ]] && { echo "Could not get user login"; return 1; }
    
    print_subsection_header "GitHub Project #${PROJECT_NUMBER} - Assigned Tasks"
    
    local response
    response=$(get_project_items "$ORG" "$PROJECT_NUMBER" "$user_login")
    
    # Check if project exists
    local project_title
    project_title=$(echo "$response" | jq -r '.data.organization.projectV2.title // "Unknown"')
    
    if [[ "$project_title" == "null" ]] || [[ -z "$project_title" ]]; then
        echo -e "  ${YELLOW}Project #${PROJECT_NUMBER} not found or not accessible${NC}"
        return 1
    fi
    
    local project_url
    project_url=$(echo "$response" | jq -r '.data.organization.projectV2.url // ""')
    
    echo -e "  ${CYAN}Project:${NC} ${BOLD}${project_title}${NC}"
    echo -e "  ${CYAN}URL:${NC} ${project_url}"
    echo ""
    
    # Filter items where user is assigned
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
        echo -e "  ${YELLOW}No assigned tasks found in this project${NC}"
        return
    fi
    
    echo -e "  ${CYAN}Total assigned items: ${BOLD}${count}${NC}"
    echo ""
    
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
        
        local type_label icon
        case "$typename" in
            Issue) 
                type_label="Issue"
                icon="${MAGENTA}📋${NC}"
                labels=$(echo "$item" | jq -r '[.content.labels.nodes[]?.name] | join(", ") // "None"')
                ;;
            PullRequest)
                type_label="Pull Request"
                icon="${GREEN}🔀${NC}"
                is_draft=$(echo "$item" | jq -r '.content.isDraft // false')
                review_decision=$(echo "$item" | jq -r '.content.reviewDecision // "PENDING"')
                additions=$(echo "$item" | jq -r '.content.additions // 0')
                deletions=$(echo "$item" | jq -r '.content.deletions // 0')
                ;;
            *)
                type_label="Card"
                icon="${BLUE}📌${NC}"
                ;;
        esac
        
        echo -e "  ${icon} ${BOLD}${type_label} #${number}${NC}: ${BOLD}${title}${NC}"
        echo -e "    ${CYAN}Repository:${NC} ${repo}"
        echo -e "    ${CYAN}Status:${NC} ${state}"
        echo -e "    ${CYAN}Updated:${NC} ${updated}"
        echo -e "    ${CYAN}URL:${NC} ${url}"
        
        if [[ "$typename" == "Issue" ]]; then
            echo -e "    ${CYAN}Labels:${NC} ${labels}"
        elif [[ "$typename" == "PullRequest" ]]; then
            if [[ "$is_draft" == "true" ]]; then
                echo -e "    ${YELLOW}⚠ Draft PR${NC}"
            fi
            echo -e "    ${CYAN}Changes:${NC} +${additions} / -${deletions} lines"
            case "$review_decision" in
                APPROVED) echo -e "    ${CYAN}Review:${NC} ${GREEN}✓ Approved${NC}" ;;
                CHANGES_REQUESTED) echo -e "    ${CYAN}Review:${NC} ${RED}✗ Changes Requested${NC}" ;;
                REVIEW_REQUIRED) echo -e "    ${CYAN}Review:${NC} ${YELLOW}⏳ Review Required${NC}" ;;
                *) echo -e "    ${CYAN}Review:${NC} ${YELLOW}⏳ Pending${NC}" ;;
            esac
        fi
        
        # Get custom field values from project
        local field_values
        field_values=$(echo "$item" | jq -r '.fieldValues.nodes[]? | select(.field != null) | "\(.field.name): \(.text // .name // .date // "N/A")"' 2>/dev/null || echo "")
        if [[ -n "$field_values" ]]; then
            echo -e "    ${CYAN}Project Fields:${NC}"
            echo "$field_values" | while IFS= read -r field; do
                echo -e "      - ${field}"
            done
        fi
        
        if [[ -n "$body" ]] && [[ "$body" != "null" ]] && [[ -n "$(echo "$body" | tr -d '[:space:]')" ]]; then
            echo -e "    ${CYAN}Description:${NC}"
            echo "$body" | head -c 300 | sed 's/^/      /'
            [[ ${#body} -gt 300 ]] && echo -e "      ${YELLOW}... (truncated)${NC}"
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
    echo "║     Precisetargetlabs Repositories & Project Tasks           ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_section_header "Repositories"
    list_all_repositories
    
    print_section_header "GitHub Projects - Assigned Tasks"
    list_project_tasks
    
    echo ""
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}  Summary Complete${NC}"
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

main "$@"
