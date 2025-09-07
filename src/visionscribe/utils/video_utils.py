"""
Video utility functions for VisionScribe.
"""

import cv2
import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import logging
from tqdm import tqdm


def get_video_info(video_path: str) -> Dict[str, Any]:
    """Get comprehensive video information."""
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {"error": "Cannot open video file"}
        
        # Get basic properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        # Get video dimensions
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Get file size
        file_size = os.path.getsize(video_path)
        
        # Get format
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = chr(fourcc & 0xFF) + chr((fourcc >> 8) & 0xFF) + \
                chr((fourcc >> 16) & 0xFF) + chr((fourcc >> 24) & 0xFF)
        
        cap.release()
        
        return {
            "file_path": video_path,
            "file_size": file_size,
            "duration": duration,
            "fps": fps,
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "codec": codec,
            "format": Path(video_path).suffix.lower(),
            "aspect_ratio": width / height if height > 0 else 0
        }
        
    except Exception as e:
        logging.error(f"Error getting video info: {e}")
        return {"error": str(e)}


def extract_frames_ffmpeg(video_path: str, output_dir: str, fps: int = 1) -> List[str]:
    """Extract frames from video using FFmpeg."""
    try:
        import subprocess
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Calculate frame extraction interval
        video_info = get_video_info(video_path)
        if "error" in video_info:
            return []
        
        frame_interval = int(video_info["fps"] / fps) if fps > 0 else 1
        
        # FFmpeg command
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"fps={fps}",
            "-q:v", "2",
            f"{output_dir}/frame_%06d.jpg"
        ]
        
        # Run ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logging.error(f"FFmpeg error: {result.stderr}")
            return []
        
        # Get extracted frames
        frame_files = list(Path(output_dir).glob("frame_*.jpg"))
        frame_files.sort()
        
        return [str(f) for f in frame_files]
        
    except Exception as e:
        logging.error(f"Error extracting frames with FFmpeg: {e}")
        return []


def calculate_video_metrics(video_path: str) -> Dict[str, Any]:
    """Calculate various video metrics."""
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {"error": "Cannot open video file"}
        
        metrics = {
            "brightness_changes": 0,
            "motion_level": 0,
            "scene_changes": 0,
            "blur_frames": 0,
            "total_frames": 0
        }
        
        prev_frame = None
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Calculate brightness
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = gray.mean()
            
            # Calculate motion
            if prev_frame is not None:
                motion = cv2.absdiff(prev_frame, gray).mean()
                metrics["motion_level"] += motion
                
                # Detect scene changes
                if motion > 30:
                    metrics["scene_changes"] += 1
            
            # Check blur
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 100:
                metrics["blur_frames"] += 1
            
            prev_frame = gray.copy()
        
        cap.release()
        
        # Calculate averages
        if frame_count > 0:
            metrics["motion_level"] /= frame_count
            metrics["brightness_changes"] = frame_count // 30  # Rough estimate
        
        metrics["total_frames"] = frame_count
        
        return metrics
        
    except Exception as e:
        logging.error(f"Error calculating video metrics: {e}")
        return {"error": str(e)}


def validate_video_file(video_path: str) -> bool:
    """Validate if video file is readable."""
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return False
        
        # Try to read first few frames
        for _ in range(10):
            ret, frame = cap.read()
            if not ret:
                cap.release()
                return False
        
        cap.release()
        return True
        
    except Exception as e:
        logging.error(f"Error validating video file: {e}")
        return False


def estimate_processing_time(video_path: str, fps: int = 1) -> Dict[str, float]:
    """Estimate processing time for video."""
    try:
        video_info = get_video_info(video_path)
        
        if "error" in video_info:
            return {"error": "Cannot get video info"}
        
        duration = video_info["duration"]
        frame_count = int(duration * fps)
        
        # Estimate processing times (rough estimates)
        frame_extraction_time = duration * 0.1  # 10% of duration
        ocr_processing_time = frame_count * 0.05  # 0.05s per frame
        ai_processing_time = duration * 0.3  # 30% of duration
        total_time = frame_extraction_time + ocr_processing_time + ai_processing_time
        
        return {
            "video_duration": duration,
            "estimated_frames": frame_count,
            "frame_extraction_time": frame_extraction_time,
            "ocr_processing_time": ocr_processing_time,
            "ai_processing_time": ai_processing_time,
            "total_estimated_time": total_time
        }
        
    except Exception as e:
        logging.error(f"Error estimating processing time: {e}")
        return {"error": str(e)}


def compress_video(input_path: str, output_path: str, quality: str = "medium") -> bool:
    """Compress video using FFmpeg."""
    try:
        import subprocess
        
        # Quality settings
        quality_settings = {
            "low": "-crf 28",
            "medium": "-crf 23",
            "high": "-crf 18"
        }
        
        # FFmpeg command
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-c:v", "libx264",
            quality_settings.get(quality, "-crf 23"),
            "-preset", "medium",
            "-c:a", "copy",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        logging.error(f"Error compressing video: {e}")
        return False


def extract_audio(video_path: str, output_path: str) -> bool:
    """Extract audio from video."""
    try:
        import subprocess
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",  # No video
            "-acodec", "pcm_s16le",  # PCM audio
            "-y",  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        logging.error(f"Error extracting audio: {e}")
        return False


def create_video_from_frames(frame_dir: str, output_path: str, fps: int = 1) -> bool:
    """Create video from extracted frames."""
    try:
        import subprocess
        
        # Get frame files
        frame_files = list(Path(frame_dir).glob("frame_*.jpg"))
        frame_files.sort()
        
        if not frame_files:
            return False
        
        # FFmpeg command
        cmd = [
            "ffmpeg",
            "-framerate", str(fps),
            "-i", f"{frame_dir}/frame_%06d.jpg",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-y",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        logging.error(f"Error creating video from frames: {e}")
        return False


def get_video_codec_info(video_path: str) -> Dict[str, Any]:
    """Get detailed codec information."""
    try:
        import subprocess
        
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        else:
            return {"error": "FFprobe failed"}
            
    except Exception as e:
        logging.error(f"Error getting codec info: {e}")
        return {"error": str(e)}