#!/usr/bin/env python3
"""
Table formatting helper for work summary script.
Uses tabulate to create beautiful, centralized tables with colors.
"""

import json
import sys
from tabulate import tabulate
from typing import List, Dict, Any

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

def colorize_company(company: str) -> str:
    """Colorize company names."""
    company_lower = company.lower()
    if 'precisetarget' in company_lower:
        return f"{Colors.CYAN}{company}{Colors.RESET}"
    elif 'rivian' in company_lower:
        return f"{Colors.MAGENTA}{company}{Colors.RESET}"
    elif 'sanctum' in company_lower:
        return f"{Colors.YELLOW}{company}{Colors.RESET}"
    return company

def colorize_status(status: str) -> str:
    """Colorize status values."""
    status_lower = status.lower()
    if 'open' in status_lower or 'opened' in status_lower:
        return f"{Colors.GREEN}{status}{Colors.RESET}"
    elif 'closed' in status_lower or 'done' in status_lower or 'cancelled' in status_lower:
        return f"{Colors.RED}{status}{Colors.RESET}"
    elif 'in progress' in status_lower or 'wip' in status_lower:
        return f"{Colors.YELLOW}{status}{Colors.RESET}"
    elif 'review' in status_lower or 'pending' in status_lower:
        return f"{Colors.BLUE}{status}{Colors.RESET}"
    return status

def colorize_type(task_type: str) -> str:
    """Colorize task types."""
    type_lower = task_type.lower()
    if 'pr' in type_lower or 'pull' in type_lower:
        return f"{Colors.GREEN}{task_type}{Colors.RESET}"
    elif 'mr' in type_lower or 'merge' in type_lower:
        return f"{Colors.MAGENTA}{task_type}{Colors.RESET}"
    elif 'issue' in type_lower:
        return f"{Colors.BLUE}{task_type}{Colors.RESET}"
    elif 'task' in type_lower or 'story' in type_lower:
        return f"{Colors.CYAN}{task_type}{Colors.RESET}"
    elif 'bug' in type_lower:
        return f"{Colors.RED}{task_type}{Colors.RESET}"
    return task_type

def colorize_source(source: str) -> str:
    """Colorize source names."""
    source_lower = source.lower()
    if 'github' in source_lower:
        return f"{Colors.BRIGHT_BLACK}{source}{Colors.RESET}"
    elif 'gitlab' in source_lower:
        return f"{Colors.MAGENTA}{source}{Colors.RESET}"
    elif 'jira' in source_lower:
        return f"{Colors.BLUE}{source}{Colors.RESET}"
    elif 'shortcut' in source_lower:
        return f"{Colors.YELLOW}{source}{Colors.RESET}"
    return source

def format_company_summary_table(tasks: List[Dict[str, Any]]) -> str:
    """Create a summary table grouped by company."""
    if not tasks:
        return "No tasks found."
    
    # Group by company
    companies = {}
    for task in tasks:
        company = task.get('company', 'Unknown')
        if company not in companies:
            companies[company] = {
                'total': 0,
                'by_type': {},
                'by_status': {}
            }
        
        companies[company]['total'] += 1
        
        task_type = task.get('type', 'Unknown')
        companies[company]['by_type'][task_type] = companies[company]['by_type'].get(task_type, 0) + 1
        
        status = task.get('status', 'Unknown')
        companies[company]['by_status'][status] = companies[company]['by_status'].get(status, 0) + 1
    
    # Build table data with colors
    table_data = []
    for company, stats in sorted(companies.items()):
        # Colorize type summary
        type_parts = []
        for k, v in sorted(stats['by_type'].items()):
            type_parts.append(f"{colorize_type(k)}: {Colors.BOLD}{v}{Colors.RESET}")
        type_summary = ', '.join(type_parts) if type_parts else 'N/A'
        
        # Colorize status summary
        status_parts = []
        for k, v in sorted(stats['by_status'].items()):
            status_parts.append(f"{colorize_status(k)}: {Colors.BOLD}{v}{Colors.RESET}")
        status_summary = ', '.join(status_parts) if status_parts else 'N/A'
        
        table_data.append([
            colorize_company(company.title()),
            f"{Colors.BOLD}{Colors.CYAN}{stats['total']}{Colors.RESET}",
            type_summary,
            status_summary
        ])
    
    # Colorize headers
    headers = [
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Company{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Total Tasks{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}By Type{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}By Status{Colors.RESET}"
    ]
    return tabulate(table_data, headers=headers, tablefmt='simple_grid', stralign='left')

def format_detailed_tasks_table(tasks: List[Dict[str, Any]]) -> str:
    """Create a detailed table with all task information."""
    if not tasks:
        return "No tasks found."
    
    table_data = []
    for task in tasks:
        # Truncate long fields for table display
        title = task.get('title', 'N/A')
        if len(title) > 50:
            title = title[:47] + '...'
        
        repo = task.get('repo', 'N/A')
        if len(repo) > 25:
            repo = repo[:22] + '...'
        
        url = task.get('url', 'N/A')
        if len(url) > 40:
            url = url[:37] + '...'
        
        # Colorize ID
        task_id = task.get('id', 'N/A')
        if task_id.startswith('#'):
            task_id = f"{Colors.BRIGHT_GREEN}{task_id}{Colors.RESET}"
        elif task_id.startswith('!'):
            task_id = f"{Colors.BRIGHT_MAGENTA}{task_id}{Colors.RESET}"
        else:
            task_id = f"{Colors.BRIGHT_BLUE}{task_id}{Colors.RESET}"
        
        table_data.append([
            colorize_company(task.get('company', 'Unknown').title()),
            colorize_source(task.get('source', 'N/A')),
            colorize_type(task.get('type', 'N/A')),
            task_id,
            f"{Colors.WHITE}{title}{Colors.RESET}",
            colorize_status(task.get('status', 'N/A')),
            f"{Colors.DIM}{repo}{Colors.RESET}",
            f"{Colors.DIM}{task.get('updated', 'N/A')}{Colors.RESET}",
            f"{Colors.BRIGHT_BLACK}{url}{Colors.RESET}"
        ])
    
    # Colorize headers
    headers = [
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Company{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Source{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Type{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}ID{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Title{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Status{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Repository/Project{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Updated{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}URL{Colors.RESET}"
    ]
    return tabulate(table_data, headers=headers, tablefmt='simple_grid', stralign='left', maxcolwidths=[None, None, None, None, 50, None, 25, None, 40])

def parse_additional_info(additional: str) -> Dict[str, str]:
    """Parse additional info string into structured fields."""
    parsed = {
        'review': '',
        'branch': '',
        'changes': '',
        'labels': '',
        'comments': '',
        'priority': '',
        'estimate': '',
        'draft_wip': '',
        'merge': '',
        'approvals': '',
        'author': '',
        'reporter': '',
        'type_info': '',
        'assignee': '',
        'watching': ''
    }
    
    if not additional:
        return parsed
    
    # Split by pipe
    parts = [p.strip() for p in additional.split('|')]
    
    for part in parts:
        part_lower = part.lower()
        
        # Review status
        if 'review:' in part_lower:
            parsed['review'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Branch info
        elif 'branch:' in part_lower:
            parsed['branch'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Changes
        elif 'changes:' in part_lower or ('+' in part and '-' in part and ('lines' in part_lower or 'files' in part_lower)):
            parsed['changes'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Labels
        elif 'labels:' in part_lower:
            parsed['labels'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Comments
        elif 'comments:' in part_lower:
            parsed['comments'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Priority
        elif 'priority:' in part_lower:
            parsed['priority'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Estimate
        elif 'estimate:' in part_lower:
            parsed['estimate'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Draft/WIP
        elif part_lower in ['draft', 'wip'] or part_lower.startswith('draft') or part_lower.startswith('wip'):
            parsed['draft_wip'] = part
        # Merge status
        elif 'merge:' in part_lower:
            parsed['merge'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Approvals
        elif 'approved' in part_lower or 'pending' in part_lower or 'approvals' in part_lower:
            if 'approvals' in part_lower or 'approved' in part_lower:
                parsed['approvals'] = part
        # Author
        elif 'author:' in part_lower:
            parsed['author'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Reporter
        elif 'reporter:' in part_lower:
            parsed['reporter'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Type info
        elif 'type:' in part_lower:
            parsed['type_info'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Files changed (for MRs)
        elif 'files:' in part_lower:
            parsed['changes'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Assignee
        elif 'assignee:' in part_lower:
            parsed['assignee'] = part.split(':', 1)[1].strip() if ':' in part else part
        # Watching indicator
        elif '👁' in part or 'watching' in part_lower:
            parsed['watching'] = part
    
    return parsed

def truncate_text(text: str, max_len: int) -> str:
    """Return text as-is without truncation."""
    return text if text else ''

def format_prs_mrs_table(tasks: List[Dict[str, Any]]) -> str:
    """Create a table specifically for PRs/MRs with custom columns."""
    if not tasks:
        return "No tasks found."
    
    # First pass: parse all tasks and determine which columns have data
    all_parsed = []
    for task in tasks:
        additional = task.get('additional', '')
        parsed = parse_additional_info(additional)
        all_parsed.append((task, parsed))
    
    # Determine which optional columns to show (only if at least one task has data)
    has_draft_wip = any(p.get('draft_wip', '') for _, p in all_parsed)
    has_review = any(p.get('review', '') for _, p in all_parsed)
    has_branch = any(p.get('branch', '') for _, p in all_parsed)
    has_changes = any(p.get('changes', '') for _, p in all_parsed)
    has_merge = any(p.get('merge', '') for _, p in all_parsed)
    has_approvals = any(p.get('approvals', '') for _, p in all_parsed)
    
    # Build headers - exclude Source, Type, Repository
    headers = [
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Company{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}ID{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Title{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Status{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Updated{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Comments{Colors.RESET}",
    ]
    maxcolwidths = [None, None, None, None, None, None]
    
    # Add optional column headers
    if has_draft_wip:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Draft/WIP{Colors.RESET}")
        maxcolwidths.append(None)
    if has_review:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Review{Colors.RESET}")
        maxcolwidths.append(None)
    if has_branch:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Branch{Colors.RESET}")
        maxcolwidths.append(None)
    if has_changes:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Changes{Colors.RESET}")
        maxcolwidths.append(None)
    if has_merge:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Merge Status{Colors.RESET}")
        maxcolwidths.append(None)
    if has_approvals:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Approvals{Colors.RESET}")
        maxcolwidths.append(None)
    
    headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}URL{Colors.RESET}")
    maxcolwidths.append(None)
    
    # Build table data
    table_data = []
    for task, parsed in all_parsed:
        # Colorize ID
        task_id = task.get('id', 'N/A')
        if task_id.startswith('#'):
            task_id = f"{Colors.BRIGHT_GREEN}{task_id}{Colors.RESET}"
        elif task_id.startswith('!'):
            task_id = f"{Colors.BRIGHT_MAGENTA}{task_id}{Colors.RESET}"
        else:
            task_id = f"{Colors.BRIGHT_BLUE}{task_id}{Colors.RESET}"
        
        # Get comment counts
        total_comments = task.get('total_comments', '0')
        resolved_review_comments = task.get('resolved_review_comments', '0')
        # Ensure they're strings and not empty
        if not total_comments or total_comments == '':
            total_comments = '0'
        if not resolved_review_comments or resolved_review_comments == '':
            resolved_review_comments = '0'
        comments_display = f"{total_comments}/{resolved_review_comments}"
        
        row = [
            colorize_company(task.get('company', 'Unknown').title()),
            task_id,
            f"{Colors.WHITE}{task.get('title', 'N/A')}{Colors.RESET}",
            colorize_status(task.get('status', 'N/A')),
            f"{Colors.DIM}{task.get('updated', 'N/A')}{Colors.RESET}",
            comments_display,
        ]
        
        # Add optional columns
        if has_draft_wip:
            draft_wip = parsed.get('draft_wip', '')
            if draft_wip:
                draft_wip = f"{Colors.YELLOW}{draft_wip}{Colors.RESET}"
            row.append(draft_wip)
        
        if has_review:
            review = parsed.get('review', '')
            if review:
                review_lower = review.lower()
                if 'approved' in review_lower:
                    review = f"{Colors.GREEN}{review}{Colors.RESET}"
                elif 'changes requested' in review_lower or 'blocked' in review_lower:
                    review = f"{Colors.RED}{review}{Colors.RESET}"
                elif 'required' in review_lower or 'pending' in review_lower:
                    review = f"{Colors.YELLOW}{review}{Colors.RESET}"
            row.append(review)
        
        if has_branch:
            row.append(parsed.get('branch', ''))
        
        if has_changes:
            row.append(parsed.get('changes', ''))
        
        if has_merge:
            merge = parsed.get('merge', '')
            if merge:
                merge_lower = merge.lower()
                if 'ready' in merge_lower or 'can be merged' in merge_lower:
                    merge = f"{Colors.GREEN}{merge}{Colors.RESET}"
                elif 'blocked' in merge_lower or 'cannot' in merge_lower:
                    merge = f"{Colors.RED}{merge}{Colors.RESET}"
                elif 'checking' in merge_lower:
                    merge = f"{Colors.YELLOW}{merge}{Colors.RESET}"
            row.append(merge)
        
        if has_approvals:
            approvals = parsed.get('approvals', '')
            if approvals:
                approvals_lower = approvals.lower()
                if 'approved' in approvals_lower and 'pending' not in approvals_lower:
                    approvals = f"{Colors.GREEN}{approvals}{Colors.RESET}"
                elif 'pending' in approvals_lower:
                    approvals = f"{Colors.YELLOW}{approvals}{Colors.RESET}"
            row.append(approvals)
        
        # URL is always last
        url = task.get('url', 'N/A')
        row.append(f"{Colors.BRIGHT_BLACK}{url}{Colors.RESET}")
        
        table_data.append(row)
    
    return tabulate(table_data, headers=headers, tablefmt='simple_grid', stralign='left', maxcolwidths=maxcolwidths, disable_numparse=True)

def format_comprehensive_table(tasks: List[Dict[str, Any]]) -> str:
    """Create a comprehensive table with all task information including additional details as sub-columns."""
    if not tasks:
        return "No tasks found."
    
    # First pass: parse all tasks and determine which columns have data
    all_parsed = []
    for task in tasks:
        additional = task.get('additional', '')
        parsed = parse_additional_info(additional)
        all_parsed.append((task, parsed))
    
    # Determine which optional columns to show (only if at least one task has data)
    has_draft_wip = any(p.get('draft_wip', '') for _, p in all_parsed)
    has_review = any(p.get('review', '') for _, p in all_parsed)
    has_branch = any(p.get('branch', '') for _, p in all_parsed)
    has_changes = any(p.get('changes', '') for _, p in all_parsed)
    has_labels = any(p.get('labels', '') for _, p in all_parsed)
    has_comments = any(p.get('comments', '') or task.get('comment_count') for task, p in all_parsed)
    has_priority = any(p.get('priority', '') or task.get('priority') for task, p in all_parsed)
    has_estimate = any(p.get('estimate', '') for _, p in all_parsed)
    has_merge = any(p.get('merge', '') for _, p in all_parsed)
    has_approvals = any(p.get('approvals', '') for _, p in all_parsed)
    has_author = any(p.get('author', '') for _, p in all_parsed)
    has_reporter = any(p.get('reporter', '') or task.get('reporter') for task, p in all_parsed)
    has_type_info = any(p.get('type_info', '') for _, p in all_parsed)
    has_assignee = any(p.get('assignee', '') or task.get('assignee') for task, p in all_parsed)
    has_watching = any(p.get('watching', '') or task.get('is_watching') == 'true' for task, p in all_parsed)
    has_created = any(task.get('created') for task, _ in all_parsed)
    has_description = any(task.get('description') for task, _ in all_parsed)
    
    # Build headers and maxcolwidths first
    headers = [
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Company{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Source{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Type{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}ID{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Title{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Status{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Repository{Colors.RESET}",
    ]
    maxcolwidths = [None, None, None, None, None, None, None]
    
    # Add created date if available
    if has_created:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Created{Colors.RESET}")
        maxcolwidths.append(None)
    
    headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Updated{Colors.RESET}")
    maxcolwidths.append(None)
    
    # Add optional column headers
    if has_draft_wip:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Draft/WIP{Colors.RESET}")
        maxcolwidths.append(None)
    if has_review:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Review{Colors.RESET}")
        maxcolwidths.append(None)
    if has_branch:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Branch{Colors.RESET}")
        maxcolwidths.append(None)
    if has_changes:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Changes{Colors.RESET}")
        maxcolwidths.append(None)
    if has_labels:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Labels{Colors.RESET}")
        maxcolwidths.append(None)
    if has_comments:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Comments{Colors.RESET}")
        maxcolwidths.append(None)
    if has_priority:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Priority{Colors.RESET}")
        maxcolwidths.append(None)
    if has_estimate:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Estimate{Colors.RESET}")
        maxcolwidths.append(None)
    if has_merge:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Merge Status{Colors.RESET}")
        maxcolwidths.append(None)
    if has_approvals:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Approvals{Colors.RESET}")
        maxcolwidths.append(None)
    if has_assignee:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Assignee{Colors.RESET}")
        maxcolwidths.append(None)
    if has_watching:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Watching{Colors.RESET}")
        maxcolwidths.append(None)
    if has_author:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Author{Colors.RESET}")
        maxcolwidths.append(None)
    if has_reporter:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Reporter{Colors.RESET}")
        maxcolwidths.append(None)
    if has_type_info:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Type Info{Colors.RESET}")
        maxcolwidths.append(None)
    
    if has_description:
        headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Description{Colors.RESET}")
        maxcolwidths.append(60)  # Limit description width
    
    headers.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}URL{Colors.RESET}")
    maxcolwidths.append(None)
    
    # Build table data
    table_data = []
    for task, parsed in all_parsed:
        # Add watching indicator to title if present
        title = task.get('title', 'N/A')
        watching = parsed.get('watching', '')
        if watching and '👁' in watching:
            title = f"👁 {title}"
        
        row = [
            colorize_company(task.get('company', 'Unknown').title()),
            colorize_source(task.get('source', 'N/A')),
            colorize_type(task.get('type', 'N/A')),
            '',
            f"{Colors.WHITE}{title}{Colors.RESET}",
            colorize_status(task.get('status', 'N/A')),
            f"{Colors.DIM}{task.get('repo', 'N/A')}{Colors.RESET}",
        ]
        
        # Add created date if column exists
        if has_created:
            created_date = task.get('created', 'N/A')
            if created_date and created_date != 'N/A':
                row.append(f"{Colors.DIM}{created_date}{Colors.RESET}")
            else:
                row.append('')
        
        # Add updated date
        row.append(f"{Colors.DIM}{task.get('updated', 'N/A')}{Colors.RESET}")
        
        # Colorize ID
        task_id = task.get('id', 'N/A')
        if task_id.startswith('#'):
            row[3] = f"{Colors.BRIGHT_GREEN}{task_id}{Colors.RESET}"
        elif task_id.startswith('!'):
            row[3] = f"{Colors.BRIGHT_MAGENTA}{task_id}{Colors.RESET}"
        else:
            row[3] = f"{Colors.BRIGHT_BLUE}{task_id}{Colors.RESET}"
        
        # Add optional columns
        if has_draft_wip:
            draft_wip = parsed.get('draft_wip', '')
            if draft_wip:
                draft_wip = f"{Colors.YELLOW}{draft_wip}{Colors.RESET}"
            row.append(draft_wip)
        
        if has_review:
            review = parsed.get('review', '')
            if review:
                review_lower = review.lower()
                if 'approved' in review_lower:
                    review = f"{Colors.GREEN}{review}{Colors.RESET}"
                elif 'changes requested' in review_lower or 'blocked' in review_lower:
                    review = f"{Colors.RED}{review}{Colors.RESET}"
                elif 'required' in review_lower or 'pending' in review_lower:
                    review = f"{Colors.YELLOW}{review}{Colors.RESET}"
            row.append(review)
        
        if has_branch:
            row.append(parsed.get('branch', ''))
        
        if has_changes:
            row.append(parsed.get('changes', ''))
        
        if has_labels:
            row.append(parsed.get('labels', ''))
        
        if has_comments:
            # Use direct field if available, otherwise use parsed
            comment_val = task.get('comment_count', parsed.get('comments', ''))
            if comment_val and comment_val != '0':
                comment_val = f"{Colors.CYAN}{comment_val}{Colors.RESET}"
            row.append(comment_val)
        
        if has_priority:
            # Use direct field if available, otherwise use parsed
            priority_val = task.get('priority', parsed.get('priority', ''))
            if priority_val:
                priority_lower = str(priority_val).lower()
                if 'high' in priority_lower or 'critical' in priority_lower or 'blocker' in priority_lower:
                    priority_val = f"{Colors.RED}{priority_val}{Colors.RESET}"
                elif 'medium' in priority_lower:
                    priority_val = f"{Colors.YELLOW}{priority_val}{Colors.RESET}"
                elif 'low' in priority_lower:
                    priority_val = f"{Colors.GREEN}{priority_val}{Colors.RESET}"
            row.append(priority_val)
        
        if has_estimate:
            row.append(parsed.get('estimate', ''))
        
        if has_merge:
            merge = parsed.get('merge', '')
            if merge:
                merge_lower = merge.lower()
                if 'ready' in merge_lower or 'can be merged' in merge_lower:
                    merge = f"{Colors.GREEN}{merge}{Colors.RESET}"
                elif 'blocked' in merge_lower or 'cannot' in merge_lower:
                    merge = f"{Colors.RED}{merge}{Colors.RESET}"
                elif 'checking' in merge_lower:
                    merge = f"{Colors.YELLOW}{merge}{Colors.RESET}"
            row.append(merge)
        
        if has_approvals:
            approvals = parsed.get('approvals', '')
            if approvals:
                approvals_lower = approvals.lower()
                if 'approved' in approvals_lower and 'pending' not in approvals_lower:
                    approvals = f"{Colors.GREEN}{approvals}{Colors.RESET}"
                elif 'pending' in approvals_lower:
                    approvals = f"{Colors.YELLOW}{approvals}{Colors.RESET}"
            row.append(approvals)
        
        if has_assignee:
            # Use direct field if available, otherwise use parsed
            assignee = task.get('assignee', parsed.get('assignee', ''))
            if assignee and assignee not in ['', 'Unassigned', 'null']:
                assignee = f"{Colors.CYAN}{assignee}{Colors.RESET}"
            else:
                assignee = ''
            row.append(assignee)
        
        if has_watching:
            # Use direct field if available, otherwise use parsed
            is_watching = task.get('is_watching', 'false')
            watch_count = task.get('watch_count', '0')
            watching_text = parsed.get('watching', '')
            
            if is_watching == 'true' or watching_text:
                if not watching_text:
                    watching_text = f"👁 Watching"
                    if watch_count and watch_count != '0':
                        watching_text += f" ({watch_count})"
                watching_text = f"{Colors.YELLOW}{watching_text}{Colors.RESET}"
                row.append(watching_text)
            else:
                row.append('')
        
        if has_author:
            row.append(parsed.get('author', ''))
        
        if has_reporter:
            # Use direct field if available, otherwise use parsed
            reporter = task.get('reporter', parsed.get('reporter', ''))
            if reporter and reporter not in ['', 'Unknown', 'null']:
                reporter = f"{Colors.DIM}{reporter}{Colors.RESET}"
            else:
                reporter = ''
            row.append(reporter)
        
        if has_type_info:
            row.append(parsed.get('type_info', ''))
        
        if has_description:
            description = task.get('description', '')
            if description and description not in ['', 'null', 'N/A']:
                # Clean up description and truncate
                description = description.replace('\n', ' ').replace('\r', ' ').strip()
                if len(description) > 100:
                    description = description[:97] + '...'
                description = f"{Colors.DIM}{description}{Colors.RESET}"
            else:
                description = ''
            row.append(description)
        
        # URL is always last
        url = task.get('url', 'N/A')
        row.append(f"{Colors.BRIGHT_BLACK}{url}{Colors.RESET}")
        
        table_data.append(row)
    
    # Use None for maxcolwidths to disable wrapping, and disable text wrapping
    return tabulate(table_data, headers=headers, tablefmt='simple_grid', stralign='left', maxcolwidths=maxcolwidths, disable_numparse=True)

def main():
    """Main function to format tables from JSON input."""
    if len(sys.argv) < 2:
        print("Usage: format_tables.py <summary|detailed|comprehensive> [json_file]")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    # Read JSON from stdin or file
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'r') as f:
            tasks = json.load(f)
    else:
        tasks = json.load(sys.stdin)
    
    if mode == 'summary':
        print(format_company_summary_table(tasks))
    elif mode == 'detailed':
        print(format_detailed_tasks_table(tasks))
    elif mode == 'comprehensive':
        print(format_comprehensive_table(tasks))
    elif mode == 'prs_mrs':
        print(format_prs_mrs_table(tasks))
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)

if __name__ == '__main__':
    main()
