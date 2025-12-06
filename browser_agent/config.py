"""
Configuration module for Browser Agent.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try to load from parent directory
    parent_env = Path(__file__).parent.parent / '.env'
    if parent_env.exists():
        load_dotenv(parent_env)

# Check for ds_api.txt and load API key if .env doesn't have it
ds_api_path = Path(__file__).parent / 'ds_api.txt'
if ds_api_path.exists() and not os.getenv('DEEPSEEK_API_KEY'):
    try:
        with open(ds_api_path, 'r', encoding='utf-8') as f:
            api_key = f.read().strip()
            # Remove any JSON metadata that might be appended
            if '{' in api_key:
                api_key = api_key.split('{')[0].strip()
            if api_key:
                os.environ['DEEPSEEK_API_KEY'] = api_key
                print(f"✓ Loaded API key from {ds_api_path.name}")
    except Exception as e:
        print(f"⚠️  Warning: Could not read API key from {ds_api_path.name}: {e}")

class Config:
    """Configuration class for Browser Agent."""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    PARENT_ROOT = PROJECT_ROOT.parent
    
    # DeepSeek API Configuration
    DEEPSEEK_API_KEY: str = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_BASE_URL: str = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    
    # Browser Configuration
    CHROME_USER_DATA_DIR: Path = Path(os.getenv('CHROME_USER_DATA_DIR', './chrome_user_data'))
    CHROME_EXECUTABLE_PATH: Optional[str] = os.getenv('CHROME_EXECUTABLE_PATH')
    BROWSER_HEADLESS: bool = os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true'
    BROWSER_WIDTH: int = int(os.getenv('BROWSER_WIDTH', '1440'))
    BROWSER_HEIGHT: int = int(os.getenv('BROWSER_HEIGHT', '900'))
    
    # Downloads Configuration
    DOWNLOADS_DIR: Path = Path(os.getenv('DOWNLOADS_DIR', './downloads'))
    BROWSER_HEIGHT: int = int(os.getenv('BROWSER_HEIGHT', '800'))
    
    # Xiaohongshu Configuration
    XHS_EXPLORE_URL: str = os.getenv('XHS_EXPLORE_URL', 'https://www.xiaohongshu.com/explore')
    
    # Search Settings
    DEFAULT_SEARCH_QUERY: str = os.getenv('DEFAULT_SEARCH_QUERY', 'AI Agent')
    MAX_SEARCH_RESULTS: int = int(os.getenv('MAX_SEARCH_RESULTS', '15'))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: Optional[Path] = None
    log_file_str = os.getenv('LOG_FILE')
    if log_file_str:
        LOG_FILE = Path(log_file_str)
    
    # MCP Server Configuration
    MCP_SERVER_HOST: str = os.getenv('MCP_SERVER_HOST', '127.0.0.1')
    MCP_SERVER_PORT: int = int(os.getenv('MCP_SERVER_PORT', '8000'))
    
    # Development Settings
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    TEST_MODE: bool = os.getenv('TEST_MODE', 'false').lower() == 'true'
    
    @classmethod
    def get_chrome_user_data_dir(cls) -> Path:
        """Get absolute path to Chrome user data directory."""
        path = cls.CHROME_USER_DATA_DIR
        if not path.is_absolute():
            # If relative path, make it relative to project root
            path = cls.PROJECT_ROOT / path
        return path.resolve()
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration."""
        errors = []
        
        # Check DeepSeek API key
        if not cls.DEEPSEEK_API_KEY:
            errors.append("DEEPSEEK_API_KEY is not set. Get one from: https://platform.deepseek.com/api_keys")
        
        # Check Chrome user data directory
        chrome_dir = cls.get_chrome_user_data_dir()
        if not chrome_dir.parent.exists():
            errors.append(f"Parent directory for Chrome user data does not exist: {chrome_dir.parent}")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def print_summary(cls):
        """Print configuration summary."""
        print("=" * 60)
        print("Browser Agent Configuration")
        print("=" * 60)
        print(f"Project Root: {cls.PROJECT_ROOT}")
        print(f"Chrome User Data: {cls.get_chrome_user_data_dir()}")
        print(f"DeepSeek API: {cls.DEEPSEEK_BASE_URL}")
        print(f"Browser Headless: {cls.BROWSER_HEADLESS}")
        print(f"XHS Explore URL: {cls.XHS_EXPLORE_URL}")
        print(f"MCP Server: {cls.MCP_SERVER_HOST}:{cls.MCP_SERVER_PORT}")
        print(f"Debug Mode: {cls.DEBUG}")
        print("=" * 60)

# Create global config instance
settings = Config()

if __name__ == "__main__":
    # Test configuration
    settings.print_summary()
    if settings.validate():
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration has errors")