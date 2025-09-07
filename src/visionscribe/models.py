"""
Data models for VisionScribe project.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime


@dataclass
class Frame:
    """Represents a video frame."""
    id: int
    image_path: str
    timestamp: float
    text_content: str = ""
    confidence: float = 0.0
    size: tuple = (0, 0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "image_path": self.image_path,
            "timestamp": self.timestamp,
            "text_content": self.text_content,
            "confidence": self.confidence,
            "size": self.size
        }


@dataclass
class TextBlock:
    """Represents a block of text extracted from frames."""
    id: int
    text: str
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)
    source_frames: List[int]
    language: str = "en"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "source_frames": self.source_frames,
            "language": self.language
        }


@dataclass
class FileNode:
    """Represents a file in the project structure."""
    name: str
    path: str
    content: str
    file_type: str
    size: int
    confidence: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "content": self.content,
            "file_type": self.file_type,
            "size": self.size,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


@dataclass
class DirectoryNode:
    """Represents a directory in the project structure."""
    name: str
    path: str
    files: List[FileNode]
    subdirectories: List['DirectoryNode']
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "files": [f.to_dict() for f in self.files],
            "subdirectories": [d.to_dict() for d in self.subdirectories],
            "metadata": self.metadata
        }


@dataclass
class Project:
    """Represents a reconstructed project."""
    name: str
    root: DirectoryNode
    metadata: Dict[str, Any]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "root": self.root.to_dict(),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ProcessResult:
    """Result of video processing."""
    success: bool
    message: str
    project_data: Optional[Project]
    processing_time: float
    frame_count: int
    text_blocks: int
    file_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "project_data": self.project_data.to_dict() if self.project_data else None,
            "processing_time": self.processing_time,
            "frame_count": self.frame_count,
            "text_blocks": self.text_blocks,
            "file_count": self.file_count
        }


@dataclass
class VideoInfo:
    """Video metadata."""
    file_path: str
    duration: float
    fps: float
    frame_count: int
    size: tuple
    format: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "duration": self.duration,
            "fps": self.fps,
            "frame_count": self.frame_count,
            "size": self.size,
            "format": self.format
        }


@dataclass
class OCRConfig:
    """OCR configuration."""
    languages: List[str]
    confidence_threshold: float
    batch_size: int
    use_gpu: bool
    model_storage_dir: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "languages": self.languages,
            "confidence_threshold": self.confidence_threshold,
            "batch_size": self.batch_size,
            "use_gpu": self.use_gpu,
            "model_storage_dir": self.model_storage_dir
        }


@dataclass
class AIConfig:
    """AI model configuration."""
    provider: str  # "openai", "claude", "local"
    model: str
    api_key: Optional[str]
    temperature: float
    max_tokens: int
    timeout: int
    system_prompt: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "api_key": self.api_key,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "system_prompt": self.system_prompt
        }


@dataclass
class VideoConfig:
    """Video processing configuration."""
    fps: int
    quality: int
    max_frames: int
    skip_blurry: bool
    blur_threshold: float
    format: str
    cache_frames: bool
    temp_dir: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fps": self.fps,
            "quality": self.quality,
            "max_frames": self.max_frames,
            "skip_blurry": self.skip_blurry,
            "blur_threshold": self.blur_threshold,
            "format": self.format,
            "cache_frames": self.cache_frames,
            "temp_dir": self.temp_dir
        }