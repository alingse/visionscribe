"""
VisionScribe - Video to Code / Video to Documentation Converter

A Python library for converting video content to code projects and documentation
using AI-powered analysis and OCR technology.
"""

__version__ = "0.1.0"
__author__ = "VisionScribe Team"
__email__ = "team@visionscribe.ai"

# Main components
from .video_processor import VideoProcessor
from .text_extractor import TextExtractor
from .text_deduplicator import TextDeduplicator
from .ai_reconstructor import AIReconstructor
from .output_generator import OutputGenerator
from .models import *

# Configuration - temporarily commented out
# from config.ocr_config import get_ocr_config, create_custom_config

# Utilities - temporarily commented out
# from utils.text_similarity import calculate_text_similarity
# from utils.file_utils import *
# from utils.image_utils import *
# from utils.video_utils import *
# from utils.text_utils import *

__all__ = [
    # Main components
    'VideoProcessor',
    'TextExtractor',
    'TextDeduplicator',
    'AIReconstructor',
    'OutputGenerator',
    
    # Models
    'Frame',
    'TextBlock',
    'FileNode',
    'DirectoryNode',
    'Project',
    'ProcessResult',
    'VideoInfo',
    'OCRConfig',
    'AIConfig',
    'VideoConfig',
    
    # Configuration
    'get_ocr_config',
    'create_custom_config',
    
    # Utilities
    'calculate_text_similarity',
    'clean_text',
    'is_blurry',
    'get_file_info',
    'extract_text_similarity',
    'extract_file_paths',
    'extract_urls',
    'extract_emails',
    'extract_keywords',
    'detect_programming_language',
]