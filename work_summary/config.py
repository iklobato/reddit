"""
Configuration management for work summary.

Uses Pydantic Settings for configuration with support for:
- Environment variables
- Config files (YAML)
- Command-line arguments
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class JiraInstance(BaseSettings):
    """Configuration for a single Jira instance."""
    
    name: str
    url: str
    email: str
    token: str
    company: str = "unknown"
    
    model_config = SettingsConfigDict(
        env_prefix='',
        case_sensitive=False,
    )


class GitHubConfig(BaseSettings):
    """GitHub configuration."""
    
    organizations: List[str] = Field(default_factory=lambda: ["precisetargetlabs", "HelloSanctum"])
    repos: List[str] = Field(default_factory=lambda: ["almagest", "monarch", "python-libs", "pyxis"])
    project_number: Optional[int] = 14
    enabled: bool = True
    
    model_config = SettingsConfigDict(
        env_prefix='GITHUB_',
        case_sensitive=False,
    )


class GitLabConfig(BaseSettings):
    """GitLab configuration."""
    
    organizations: List[str] = Field(default_factory=lambda: ["rivian"])
    enabled: bool = True
    
    model_config = SettingsConfigDict(
        env_prefix='GITLAB_',
        case_sensitive=False,
    )


class JiraConfig(BaseSettings):
    """Jira configuration."""
    
    instances: List[Dict[str, Any]] = Field(default_factory=list)
    enabled: bool = True
    
    model_config = SettingsConfigDict(
        env_prefix='JIRA_',
        case_sensitive=False,
    )
    
    def get_instances(self) -> List[JiraInstance]:
        """Get list of Jira instances."""
        result = []
        
        # Add Rivian instance if configured
        rivian_token = os.getenv('JIRA_TOKEN_RIVIAN')
        if rivian_token:
            result.append(JiraInstance(
                name='rivian',
                url='https://rivianautomotivellc.atlassian.net',
                email=os.getenv('JIRA_EMAIL_RIVIAN', 'henriquelobato@rivian.com'),
                token=rivian_token,
                company='rivian'
            ))
        
        # Add Orlo instance if configured
        orlo_token = os.getenv('JIRA_TOKEN_ORLO')
        orlo_url = os.getenv('JIRA_INSTANCE_URL_ORLO')
        orlo_email = os.getenv('JIRA_EMAIL_ORLO')
        if orlo_token and orlo_url and orlo_email:
            result.append(JiraInstance(
                name='orlo',
                url=orlo_url,
                email=orlo_email,
                token=orlo_token,
                company='orlo'
            ))
        
        # Add instances from config
        for instance_data in self.instances:
            result.append(JiraInstance(**instance_data))
        
        return result


class ShortcutConfig(BaseSettings):
    """Shortcut configuration."""
    
    api_key: str = Field(default='')
    enabled: bool = True
    
    model_config = SettingsConfigDict(
        env_prefix='SHORTCUT_',
        case_sensitive=False,
    )
    
    @field_validator('api_key', mode='before')
    @classmethod
    def get_api_key(cls, v):
        """Get API key from environment."""
        if v:
            return v
        return os.getenv('SHORTCUT_API_KEY', 'a11ffad3-59f0-4cc5-9b30-b29fadd16fc3')


class OutputConfig(BaseSettings):
    """Output configuration."""
    
    format: str = "table"
    file: Optional[str] = None
    color_theme: str = "default"
    
    model_config = SettingsConfigDict(
        env_prefix='OUTPUT_',
        case_sensitive=False,
    )
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        """Validate output format."""
        valid_formats = ['table', 'json', 'csv']
        if v not in valid_formats:
            raise ValueError(f"Invalid format: {v}. Must be one of {valid_formats}")
        return v


class CacheConfig(BaseSettings):
    """Cache configuration."""
    
    enabled: bool = False
    ttl: int = 300  # 5 minutes
    directory: Optional[Path] = None
    
    model_config = SettingsConfigDict(
        env_prefix='CACHE_',
        case_sensitive=False,
    )


class AppConfig(BaseSettings):
    """Main application configuration."""
    
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    gitlab: GitLabConfig = Field(default_factory=GitLabConfig)
    jira: JiraConfig = Field(default_factory=JiraConfig)
    shortcut: ShortcutConfig = Field(default_factory=ShortcutConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    
    verbose: bool = False
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
    )
    
    @classmethod
    def from_yaml(cls, path: Path) -> 'AppConfig':
        """
        Load configuration from YAML file.
        
        Args:
            path: Path to YAML file
            
        Returns:
            AppConfig instance
        """
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Transform old config format if needed
        config_data = {}
        
        # Handle GitHub config
        if 'github' in data:
            config_data['github'] = data['github']
        
        # Handle GitLab config
        if 'gitlab' in data:
            config_data['gitlab'] = data['gitlab']
        
        # Handle Jira config
        if 'jira' in data:
            config_data['jira'] = data['jira']
        
        # Handle Shortcut config
        if 'shortcut' in data:
            config_data['shortcut'] = data['shortcut']
        
        # Handle output config
        if 'output' in data:
            config_data['output'] = data['output']
        
        # Handle cache config
        if 'cache' in data:
            config_data['cache'] = data['cache']
        
        return cls(**config_data)
    
    def to_yaml(self, path: Path) -> None:
        """
        Save configuration to YAML file.
        
        Args:
            path: Path to save YAML file
        """
        data = {
            'github': self.github.model_dump(),
            'gitlab': self.gitlab.model_dump(),
            'jira': self.jira.model_dump(),
            'shortcut': self.shortcut.model_dump(),
            'output': self.output.model_dump(),
            'cache': self.cache.model_dump(),
        }
        
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Load configuration from file or environment.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        AppConfig instance
    """
    if config_path and config_path.exists():
        return AppConfig.from_yaml(config_path)
    
    # Try default locations
    default_paths = [
        Path.cwd() / 'work_summary.yaml',
        Path.cwd() / 'work_summary.yml',
        Path.home() / '.config' / 'work_summary' / 'config.yaml',
        Path.home() / '.config' / 'work_summary' / 'config.yml',
    ]
    
    for path in default_paths:
        if path.exists():
            return AppConfig.from_yaml(path)
    
    # No config file found, use defaults and environment variables
    return AppConfig()
