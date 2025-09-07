"""
Text deduplication module for VisionScribe.
"""

from typing import List, Dict, Any


class TextDeduplicator:
    """Handles text deduplication and clustering."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def deduplicate_texts(self, text_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate text blocks using simple method."""
        if not text_blocks:
            return []
        
        # Simple deduplication - keep unique texts
        seen_texts = set()
        unique_blocks = []
        
        for block in text_blocks:
            if block["text"] not in seen_texts:
                seen_texts.add(block["text"])
                unique_blocks.append(block)
        
        return unique_blocks