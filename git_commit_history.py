#!/usr/bin/env python3
"""
Script to display git commit history grouped by project and day, filtered by git username.
Scans subdirectories for git repositories.
"""

import subprocess
import sys
import re
from datetime import datetime
from collections import defaultdict
from pathlib import Path


def get_git_username():
    """Get the git username from git config."""
    try:
        result = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def find_git_repositories(root_path):
    """Find all git repositories in the given directory and subdirectories.
    
    Returns a list of Path objects pointing to git repository roots.
    """
    git_repos = []
    root_path = Path(root_path)
    
    # Check if root itself is a git repo
    if (root_path / '.git').exists():
        git_repos.append(root_path)
    
    # Search subdirectories
    for path in root_path.rglob('.git'):
        if path.is_dir():
            repo_path = path.parent
            # Avoid duplicates and nested repos
            if repo_path not in git_repos:
                git_repos.append(repo_path)
    
    return sorted(git_repos)


def get_commits_by_author(author_name, repo_path, since_date=None):
    """Get all commits by the specified author from a repository.
    
    Args:
        author_name: Git author name to filter by
        repo_path: Path to git repository
        since_date: Date string for --since filter (e.g., "2025-12-01")
    """
    cmd = [
        'git', 'log',
        '--author', author_name,
        '--pretty=format:%H|%ad|%s|%b',
        '--date=format:%Y-%m-%d %H:%M:%S',
        '--reverse'
    ]
    
    if since_date:
        cmd.extend(['--since', since_date])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=repo_path
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        # If there are no commits, git log returns non-zero, but that's okay
        if e.returncode == 128:
            return ""
        # Silently skip repos with errors (might not be accessible, etc.)
        return ""


def parse_commits(git_output):
    """Parse git log output into structured commit data."""
    commits = []
    
    if not git_output.strip():
        return commits
    
    # Split by commit hash pattern (40 char hex string followed by |)
    commit_pattern = re.compile(r'^([a-f0-9]{40})\|')
    
    current_commit = None
    lines = git_output.strip().split('\n')
    
    for line in lines:
        # Check if this line starts a new commit
        match = commit_pattern.match(line)
        if match:
            # Save previous commit if exists
            if current_commit:
                commits.append(current_commit)
            
            # Start new commit
            parts = line.split('|', 3)
            if len(parts) >= 3:
                commit_hash = parts[0]
                date_str = parts[1]
                title = parts[2]
                body = parts[3] if len(parts) > 3 else ""
                
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    current_commit = {
                        'hash': commit_hash,
                        'date': date,
                        'date_str': date_str,
                        'title': title,
                        'body': body
                    }
                except ValueError:
                    current_commit = None
        elif current_commit:
            # This is a continuation of the body
            current_commit['body'] += '\n' + line
    
    # Don't forget the last commit
    if current_commit:
        commits.append(current_commit)
    
    # Clean up body whitespace
    for commit in commits:
        commit['body'] = commit['body'].strip()
    
    return commits


def group_commits_by_project_and_day(project_commits):
    """Group commits by project and then by day.
    
    Args:
        project_commits: Dict mapping project paths to lists of commits
    
    Returns:
        Dict mapping project paths to dicts mapping days to lists of commits
    """
    result = {}
    
    for project_path, commits in project_commits.items():
        day_groups = defaultdict(list)
        for commit in commits:
            day_key = commit['date'].strftime('%Y-%m-%d')
            day_groups[day_key].append(commit)
        
        # Sort commits within each day by time
        for day in day_groups:
            day_groups[day].sort(key=lambda x: x['date'])
        
        result[project_path] = dict(sorted(day_groups.items()))
    
    return result


def get_project_name(project_path, root_path):
    """Get project name as relative path."""
    try:
        rel_path = project_path.relative_to(root_path)
        if str(rel_path) == '.':
            return project_path.name
        return str(rel_path)
    except ValueError:
        return str(project_path)


def format_commit_line(commit, project_name):
    """Format a single commit as one line."""
    date_str = commit['date'].strftime('%Y-%m-%d')
    time_str = commit['date'].strftime('%H:%M:%S')
    short_hash = commit['hash'][:8]
    
    # Combine title and body, replacing newlines with spaces
    message = commit['title']
    if commit['body']:
        body_clean = ' '.join(line.strip() for line in commit['body'].split('\n') if line.strip())
        if body_clean:
            message = f"{message} {body_clean}"
    
    return f"{date_str} {time_str} {project_name} {short_hash} {message}"


def main():
    """Main function."""
    # Get current directory
    root_dir = Path.cwd()
    
    # Get git username
    username = get_git_username()
    if not username:
        print("Error: Could not determine git username. Please set it with 'git config user.name'", file=sys.stderr)
        sys.exit(1)
    
    # Calculate date range (first day of last month until today)
    today = datetime.now()
    
    # Calculate first day of last month
    if today.month == 1:
        # If current month is January, last month is December of previous year
        first_day_last_month = datetime(today.year - 1, 12, 1)
    else:
        first_day_last_month = datetime(today.year, today.month - 1, 1)
    
    # Format date for git log (YYYY-MM-DD format)
    since_date = first_day_last_month.strftime('%Y-%m-%d')
    
    # Find all git repositories
    git_repos = find_git_repositories(root_dir)
    
    if not git_repos:
        sys.exit(0)
    
    # Collect commits from all repositories
    project_commits = {}
    
    for repo_path in git_repos:
        git_output = get_commits_by_author(username, repo_path, since_date=since_date)
        if git_output:
            commits = parse_commits(git_output)
            if commits:
                project_commits[repo_path] = commits
    
    if not project_commits:
        sys.exit(0)
    
    # Group commits by project and day
    grouped_data = group_commits_by_project_and_day(project_commits)
    
    # Collect all commits grouped by day
    commits_by_day = defaultdict(list)
    for project_path, day_groups in grouped_data.items():
        project_name = get_project_name(project_path, root_dir)
        for day, day_commits in day_groups.items():
            for commit in day_commits:
                commits_by_day[day].append((commit, project_name))
    
    # Sort days chronologically
    sorted_days = sorted(commits_by_day.keys())
    
    # Display commits grouped by day
    for day in sorted_days:
        # Format day header
        try:
            date_obj = datetime.strptime(day, '%Y-%m-%d')
            day_header = date_obj.strftime('%Y-%m-%d %A')
        except ValueError:
            day_header = day
        
        print(day_header)
        
        # Sort commits within the day by time
        day_commits = sorted(commits_by_day[day], key=lambda x: x[0]['date'])
        
        # Display each commit on one line
        for commit, project_name in day_commits:
            print(format_commit_line(commit, project_name))
        
        # Empty line between days
        print()


if __name__ == '__main__':
    main()
