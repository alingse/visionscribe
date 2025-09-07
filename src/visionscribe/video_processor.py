"""
Video processing module for VisionScribe.
"""

import cv2
import os
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image
import numpy as np
from tqdm import tqdm
import logging

from .models import Frame, VideoInfo, VideoConfig


class VideoProcessor:
    """Handles video frame extraction and processing."""
    
    def __init__(self, config: Optional[VideoConfig] = None):
        self.config = config or VideoConfig(
            fps=1,
            quality=95,
            max_frames=1000,
            skip_blurry=True,
            blur_threshold=100,
            format="jpg",
            cache_frames=True,
            temp_dir="./data/temp"
        )
        self.logger = logging.getLogger(__name__)
        
        # Create temp directory if it doesn't exist
        Path(self.config.temp_dir).mkdir(parents=True, exist_ok=True)
    
    def get_video_info(self, video_path: str) -> VideoInfo:
        """Get video metadata."""
        cap = cv2.VideoCapture(video_path)
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return VideoInfo(
            file_path=video_path,
            duration=duration,
            fps=fps,
            frame_count=frame_count,
            size=(0, 0),
            format="mp4"
        )
    
    def extract_frames(self, video_path: str, fps: Optional[int] = None) -> List[Frame]:
        """Extract frames from video at specified FPS."""
        if fps is None:
            fps = self.config.fps
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        video_info = self.get_video_info(video_path)
        frame_interval = int(video_info.fps / fps) if fps > 0 else 1
        
        frames = []
        frame_count = 0
        extracted_count = 0
        
        self.logger.info(f"Extracting frames from {video_path} at {fps} FPS...")
        
        pbar = tqdm(total=min(int(video_info.duration), self.config.max_frames), 
                   desc="Extracting frames")
        
        while cap.isOpened() and extracted_count < self.config.max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Extract frames at specified intervals
            if frame_count % frame_interval == 0:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process frame
                processed_frame = self._process_frame(frame_rgb)
                
                # Skip blurry frames if enabled
                if self.config.skip_blurry and self._is_blurry(processed_frame):
                    frame_count += 1
                    continue
                
                # Save frame
                frame_path = os.path.join(
                    self.config.temp_dir,
                    f"frame_{extracted_count:06d}.{self.config.format}"
                )
                
                # Save frame
                img = Image.fromarray(processed_frame)
                img.save(frame_path, quality=self.config.quality)
                
                # Create frame object
                frame_obj = Frame(
                    id=extracted_count,
                    image_path=frame_path,
                    timestamp=frame_count / video_info.fps,
                    size=img.size,
                    confidence=1.0
                )
                
                frames.append(frame_obj)
                extracted_count += 1
                
                pbar.update(1)
            
            frame_count += 1
        
        cap.release()
        pbar.close()
        
        self.logger.info(f"Extracted {len(frames)} frames from video")
        return frames
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process a single frame."""
        # Resize if needed
        if self.config.max_frames > 0:
            max_size = 1024
            h, w = frame.shape[:2]
            if max(h, w) > max_size:
                scale = max_size / max(h, w)
                new_size = (int(w * scale), int(h * scale))
                frame = cv2.resize(frame, new_size, interpolation=cv2.INTER_AREA)
        
        # Apply preprocessing
        if self.config.skip_blurry:
            # Apply slight denoising
            frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
        
        return frame
    
    def _is_blurry(self, frame: np.ndarray, threshold: Optional[float] = None) -> bool:
        """Check if frame is blurry using Laplacian variance."""
        if threshold is None:
            threshold = self.config.blur_threshold
        
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        return laplacian_var < threshold
    
    def deduplicate_frames(self, frames: List[Frame], threshold: float = 0.95) -> List[Frame]:
        """Remove duplicate frames using similarity comparison."""
        if not frames:
            return []
        
        unique_frames = [frames[0]]
        
        for i, frame in enumerate(frames[1:], 1):
            is_duplicate = False
            
            # Compare with unique frames
            for unique_frame in unique_frames:
                similarity = self._calculate_frame_similarity(frame, unique_frame)
                if similarity > threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_frames.append(frame)
        
        self.logger.info(f"Deduplicated {len(frames)} frames to {len(unique_frames)} unique frames")
        return unique_frames
    
    def _calculate_frame_similarity(self, frame1: Frame, frame2: Frame) -> float:
        """Calculate similarity between two frames using structural similarity."""
        try:
            img1 = cv2.imread(frame1.image_path)
            img2 = cv2.imread(frame2.image_path)
            
            if img1 is None or img2 is None:
                return 0.0
            
            # Resize to same size
            h1, w1 = img1.shape[:2]
            h2, w2 = img2.shape[:2]
            
            if h1 != h2 or w1 != w2:
                img2 = cv2.resize(img2, (w1, h1))
            
            # Calculate SSIM
            from skimage.metrics import structural_similarity as ssim
            similarity, _ = ssim(img1, img2, full=True, channel_axis=2)
            
            return float(similarity)
        
        except Exception as e:
            self.logger.warning(f"Error calculating frame similarity: {e}")
            return 0.0
    
    def filter_frames_by_quality(self, frames: List[Frame], min_confidence: float = 0.8) -> List[Frame]:
        """Filter frames by quality metrics."""
        filtered_frames = [f for f in frames if f.confidence >= min_confidence]
        
        if len(filtered_frames) < len(frames):
            self.logger.info(f"Filtered {len(frames) - len(filtered_frames)} low quality frames")
        
        return filtered_frames
    
    def clean_temp_files(self) -> None:
        """Clean up temporary files."""
        try:
            temp_dir = Path(self.config.temp_dir)
            if temp_dir.exists():
                for file in temp_dir.glob("frame_*"):
                    file.unlink()
                self.logger.info("Cleaned up temporary frame files")
        except Exception as e:
            self.logger.warning(f"Error cleaning temp files: {e}")