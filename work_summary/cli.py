"""
Command-line interface for work summary.

Provides a modern CLI using Click framework.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from work_summary.config import load_config, AppConfig
from work_summary.models import WorkSummary
from work_summary.collectors import (
    GitHubCollector,
    GitLabCollector,
    JiraCollector,
    ShortcutCollector,
)
from work_summary.formatters import (
    TableFormatter,
    JSONFormatter,
    JSONLinesFormatter,
    CSVFormatter,
)
from work_summary.utils.colors import ColorManager, set_color_manager
from work_summary.utils.cache import FileCache, set_cache
from work_summary.utils.http import HTTPClient


# Configure logging
def setup_logging(verbose: bool = False, debug: bool = False):
    """Setup logging configuration."""
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


@click.group(invoke_without_command=True)
@click.option('--config', type=click.Path(exists=True, path_type=Path), help='Config file path')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'jsonl', 'csv']), default='table', help='Output format')
@click.option('--output', type=click.Path(path_type=Path), help='Output file (default: stdout)')
@click.option('--no-cache', is_flag=True, help='Disable caching')
@click.option('--no-color', is_flag=True, help='Disable colored output')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--debug', is_flag=True, help='Debug output')
@click.pass_context
def cli(ctx, config, output_format, output, no_cache, no_color, verbose, debug):
    """
    Work Summary - Collect and display work items from multiple sources.
    
    Collects work items from GitHub, GitLab, Jira, and Shortcut.
    """
    # Setup logging
    setup_logging(verbose, debug)
    
    # Load configuration
    try:
        app_config = load_config(config)
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)
    
    # Override config with CLI options
    if output_format:
        app_config.output.format = output_format
    if output:
        app_config.output.file = str(output)
    if no_cache:
        app_config.cache.enabled = False
    if no_color:
        app_config.output.color_theme = "none"
    if verbose:
        app_config.verbose = True
    if debug:
        app_config.debug = True
    
    # Store config in context
    ctx.obj = app_config
    
    # If no subcommand, run collect
    if ctx.invoked_subcommand is None:
        ctx.invoke(collect)


@cli.command()
@click.pass_obj
def collect(config: AppConfig):
    """Collect work items from all sources."""
    asyncio.run(collect_all(config))


@cli.command()
@click.pass_obj
def collect_github(config: AppConfig):
    """Collect only from GitHub."""
    config.gitlab.enabled = False
    config.jira.enabled = False
    config.shortcut.enabled = False
    asyncio.run(collect_all(config))


@cli.command()
@click.pass_obj
def collect_gitlab(config: AppConfig):
    """Collect only from GitLab."""
    config.github.enabled = False
    config.jira.enabled = False
    config.shortcut.enabled = False
    asyncio.run(collect_all(config))


@cli.command()
@click.pass_obj
def collect_jira(config: AppConfig):
    """Collect only from Jira."""
    config.github.enabled = False
    config.gitlab.enabled = False
    config.shortcut.enabled = False
    asyncio.run(collect_all(config))


@cli.command()
@click.pass_obj
def collect_shortcut(config: AppConfig):
    """Collect only from Shortcut."""
    config.github.enabled = False
    config.gitlab.enabled = False
    config.jira.enabled = False
    asyncio.run(collect_all(config))


async def collect_all(config: AppConfig):
    """
    Collect work items from all enabled sources.
    
    Args:
        config: Application configuration
    """
    # Setup color manager
    color_enabled = config.output.color_theme != "none"
    color_manager = ColorManager(enabled=color_enabled)
    set_color_manager(color_manager)
    
    # Setup cache
    cache = None
    if config.cache.enabled:
        cache = FileCache(
            cache_dir=config.cache.directory,
            default_ttl=config.cache.ttl
        )
        set_cache(cache)
    
    # Create HTTP client
    http_client = HTTPClient()
    await http_client.start()
    
    try:
        # Create collectors
        collectors = []
        
        if config.github.enabled:
            collectors.append(GitHubCollector(
                config=config.github,
                http_client=http_client,
                cache=cache,
            ))
        
        if config.gitlab.enabled:
            collectors.append(GitLabCollector(
                config=config.gitlab,
                http_client=http_client,
                cache=cache,
            ))
        
        if config.jira.enabled:
            collectors.append(JiraCollector(
                config=config.jira,
                http_client=http_client,
                cache=cache,
            ))
        
        if config.shortcut.enabled:
            collectors.append(ShortcutCollector(
                config=config.shortcut,
                http_client=http_client,
                cache=cache,
            ))
        
        # Start all collectors
        for collector in collectors:
            await collector.start()
        
        # Collect from all sources in parallel
        click.echo(color_manager.dim("Collecting work items from all sources..."))
        
        results = await asyncio.gather(
            *[collector.collect() for collector in collectors],
            return_exceptions=True
        )
        
        # Aggregate tasks
        summary = WorkSummary()
        for result in results:
            if isinstance(result, Exception):
                logging.error(f"Collection failed: {result}")
            elif isinstance(result, list):
                for task in result:
                    summary.add_task(task)
        
        # Close collectors
        for collector in collectors:
            await collector.close()
        
        # Format output
        formatter = get_formatter(config.output.format, color_manager)
        output_text = formatter.format(summary)
        
        # Write output
        if config.output.file:
            output_path = Path(config.output.file)
            output_path.write_text(output_text)
            click.echo(f"Output written to {output_path}")
        else:
            click.echo(output_text)
    
    finally:
        await http_client.close()


def get_formatter(format_name: str, color_manager: ColorManager):
    """
    Get formatter instance by name.
    
    Args:
        format_name: Format name (table, json, jsonl, csv)
        color_manager: Color manager instance
        
    Returns:
        Formatter instance
    """
    if format_name == 'table':
        return TableFormatter(color_manager=color_manager)
    elif format_name == 'json':
        return JSONFormatter(pretty=True)
    elif format_name == 'jsonl':
        return JSONLinesFormatter()
    elif format_name == 'csv':
        return CSVFormatter()
    else:
        raise ValueError(f"Unknown format: {format_name}")


@cli.command()
@click.argument('config_path', type=click.Path(path_type=Path))
@click.pass_obj
def init_config(config: AppConfig, config_path: Path):
    """Initialize a new configuration file."""
    try:
        config.to_yaml(config_path)
        click.echo(f"Configuration file created: {config_path}")
    except Exception as e:
        click.echo(f"Error creating configuration file: {e}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    from work_summary import __version__
    click.echo(f"work-summary version {__version__}")


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()
