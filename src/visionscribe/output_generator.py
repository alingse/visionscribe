"""
Output generation module for VisionScribe.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .models import Project, DirectoryNode, FileNode


class OutputGenerator:
    """Handles generation of code and documentation from project data."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    def generate_codebase(self, project_data: Project, output_dir: str) -> None:
        """Generate code files from project data."""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate directory structure
            self._create_directory_structure(project_data.root, output_path)
            
            self.logger.info(f"Codebase generated at {output_dir}")
            
        except Exception as e:
            self.logger.error(f"Error generating codebase: {e}")
            raise
    
    def generate_documentation(self, project_data: Project, output_file: str) -> None:
        """Generate documentation from project data."""
        try:
            doc_content = self._generate_markdown_documentation(project_data)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            self.logger.info(f"Documentation generated at {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error generating documentation: {e}")
            raise
    
    def _create_directory_structure(self, directory: DirectoryNode, base_path: Path) -> None:
        """Create directory structure and files."""
        current_path = base_path / directory.name
        
        # Create subdirectories
        for subdirectory in directory.subdirectories:
            sub_dir_path = current_path / subdirectory.name
            sub_dir_path.mkdir(exist_ok=True)
            self._create_directory_structure(subdirectory, sub_dir_path)
        
        # Create files
        for file_node in directory.files:
            file_path = current_path / file_node.name
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_node.content)
    
    def _generate_markdown_documentation(self, project_data: Project) -> str:
        """Generate markdown documentation."""
        doc_lines = []
        doc_lines.append(f"# {project_data.name}")
        doc_lines.append("")
        doc_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc_lines.append("")
        
        # Add project structure
        doc_lines.append("## Project Structure")
        doc_lines.append("")
        doc_lines.append("````")
        doc_lines.append(self._format_directory_tree(project_data.root))
        doc_lines.append("````")
        doc_lines.append("")
        
        # Add file contents
        doc_lines.append("## File Contents")
        doc_lines.append("")
        doc_lines.append(self._format_file_contents(project_data.root))
        
        return "\n".join(doc_lines)
    
    def _format_directory_tree(self, directory: DirectoryNode, indent: str = "") -> str:
        """Format directory tree as string."""
        tree_lines = []
        
        for i, file_node in enumerate(directory.files):
            if i == len(directory.files) - 1 and len(directory.subdirectories) == 0:
                tree_lines.append(f"{indent}└── {file_node.name}")
            else:
                tree_lines.append(f"{indent}├── {file_node.name}")
        
        for i, subdirectory in enumerate(directory.subdirectories):
            if i == len(directory.subdirectories) - 1:
                tree_lines.append(f"{indent}└── {subdirectory.name}/")
                subtree = self._format_directory_tree(subdirectory, indent + "    ")
                tree_lines.append(subtree)
            else:
                tree_lines.append(f"{indent}├── {subdirectory.name}/")
                subtree = self._format_directory_tree(subdirectory, indent + "│   ")
                tree_lines.append(subtree)
        
        return "\n".join(tree_lines)
    
    def _format_file_contents(self, directory: DirectoryNode) -> str:
        """Format file contents as markdown."""
        content_lines = []
        
        for file_node in directory.files:
            content_lines.append(f"### {file_node.name}")
            content_lines.append("")
            content_lines.append("```")
            content_lines.append(file_node.content)
            content_lines.append("```")
            content_lines.append("")
        
        for subdirectory in directory.subdirectories:
            content_lines.append(f"### {subdirectory.name}/")
            content_lines.append("")
            content_lines.extend(self._format_file_contents(subdirectory).split("\n"))
        
        return "\n".join(content_lines)