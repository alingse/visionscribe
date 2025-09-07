"""
File utility functions for VisionScribe.
"""

import os
import shutil
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging


def create_directory_structure(structure: Dict[str, Any], base_path: str) -> None:
    """Create directory structure from dictionary."""
    base = Path(base_path)
    
    for name, content in structure.items():
        path = base / name
        
        if isinstance(content, dict):
            # Create directory and recurse
            path.mkdir(parents=True, exist_ok=True)
            create_directory_structure(content, str(path))
        else:
            # Create file with content
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)


def save_file_with_encoding(file_path: str, content: str, encoding: str = 'utf-8') -> None:
    """Save file with specified encoding."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)


def load_file_with_encoding(file_path: str, encoding: str = 'utf-8') -> str:
    """Load file with specified encoding."""
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


def get_file_extension(file_path: str) -> str:
    """Get file extension without dot."""
    return Path(file_path).suffix.lstrip('.')


def get_file_type(file_path: str) -> str:
    """Get file type based on extension."""
    extension = get_file_extension(file_path).lower()
    
    # Programming languages
    if extension in ['py', 'pyw']:
        return 'python'
    elif extension in ['js', 'mjs', 'cjs']:
        return 'javascript'
    elif extension in ['ts', 'tsx', 'd.ts']:
        return 'typescript'
    elif extension in ['java']:
        return 'java'
    elif extension in ['cpp', 'cc', 'cxx', 'c++']:
        return 'cpp'
    elif extension in ['c', 'h']:
        return 'c'
    elif extension in ['go']:
        return 'go'
    elif extension in ['rs']:
        return 'rust'
    elif extension in ['php']:
        return 'php'
    elif extension in ['rb', 'ruby']:
        return 'ruby'
    elif extension in ['swift']:
        return 'swift'
    elif extension in ['kt', 'java']:
        return 'kotlin'
    elif extension in ['scala']:
        return 'scala'
    elif extension in ['r']:
        return 'r'
    
    # Web technologies
    elif extension in ['html', 'htm']:
        return 'html'
    elif extension in ['css', 'scss', 'sass']:
        return 'css'
    elif extension in ['xml', 'xsl']:
        return 'xml'
    elif extension in ['json']:
        return 'json'
    elif extension in ['yaml', 'yml']:
        return 'yaml'
    elif extension in ['md', 'markdown']:
        return 'markdown'
    elif extension in ['txt']:
        return 'text'
    
    # Configuration files
    elif extension in ['ini', 'cfg', 'conf', 'config']:
        return 'config'
    elif extension in ['toml']:
        return 'toml'
    elif extension in ['env']:
        return 'env'
    
    # Data files
    elif extension in ['csv']:
        return 'csv'
    elif extension in ['sql']:
        return 'sql'
    elif extension in ['sh', 'bash', 'zsh']:
        return 'shell'
    
    # Unknown
    else:
        return 'unknown'


def estimate_file_size(content: str) -> int:
    """Estimate file size in bytes."""
    return len(content.encode('utf-8'))


def copy_file_with_backup(src: str, dst: str, backup_suffix: str = '.bak') -> None:
    """Copy file and create backup if destination exists."""
    src_path = Path(src)
    dst_path = Path(dst)
    
    if dst_path.exists():
        backup_path = dst_path.with_suffix(dst_path.suffix + backup_suffix)
        shutil.copy2(dst_path, backup_path)
    
    shutil.copy2(src_path, dst_path)


def safe_filename(filename: str) -> str:
    """Make filename safe for filesystem."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read JSON file safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {file_path}: {e}")
        raise
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        raise


def write_json_file(file_path: str, data: Dict[str, Any], indent: int = 2) -> None:
    """Write JSON file safely."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error writing {file_path}: {e}")
        raise


def read_yaml_file(file_path: str) -> Dict[str, Any]:
    """Read YAML file safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        logging.error(f"Invalid YAML in {file_path}: {e}")
        raise
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        raise


def write_yaml_file(file_path: str, data: Dict[str, Any]) -> None:
    """Write YAML file safely."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        logging.error(f"Error writing {file_path}: {e}")
        raise


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get comprehensive file information."""
    path = Path(file_path)
    
    if not path.exists():
        return {'error': 'File not found'}
    
    stat = path.stat()
    
    return {
        'name': path.name,
        'path': str(path.absolute()),
        'size': stat.st_size,
        'size_human': format_file_size(stat.st_size),
        'extension': path.suffix,
        'type': get_file_type(file_path),
        'modified': stat.st_mtime,
        'created': stat.st_ctime,
        'readable': os.access(path, os.R_OK),
        'writable': os.access(path, os.W_OK),
        'executable': os.access(path, os.X_OK),
    }


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def clean_directory(directory: str, pattern: str = '*') -> None:
    """Clean directory contents matching pattern."""
    dir_path = Path(directory)
    
    if not dir_path.exists():
        return
    
    for file_path in dir_path.glob(pattern):
        if file_path.is_file():
            file_path.unlink()
        elif file_path.is_dir():
            shutil.rmtree(file_path)


def ensure_directory_exists(directory: str) -> None:
    """Ensure directory exists, create if not."""
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_relative_file_path(file_path: str, base_path: str) -> str:
    """Get relative file path from base path."""
    return str(Path(file_path).relative_to(Path(base_path)))