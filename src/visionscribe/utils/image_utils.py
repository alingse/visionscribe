"""
Image utility functions for VisionScribe.
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Tuple, List, Optional
import logging


def is_blurry(image: np.ndarray, threshold: float = 100) -> bool:
    """Check if image is blurry using Laplacian variance."""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Calculate Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        return laplacian_var < threshold
    except Exception as e:
        logging.error(f"Error checking image blur: {e}")
        return True


def resize_image(image: np.ndarray, size: Optional[Tuple[int, int]] = None, 
                 maintain_aspect: bool = True, 
                 interpolation: int = cv2.INTER_AREA) -> np.ndarray:
    """Resize image with optional aspect ratio preservation."""
    try:
        if size is None:
            return image
        
        h, w = image.shape[:2]
        target_w, target_h = size
        
        if maintain_aspect:
            # Calculate scaling factor
            scale = min(target_w / w, target_h / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            # Resize image
            resized = cv2.resize(image, (new_w, new_h), interpolation=interpolation)
            
            # Create canvas with target size
            canvas = np.zeros((target_h, target_w, 3), dtype=image.dtype)
            
            # Center the image
            y_offset = (target_h - new_h) // 2
            x_offset = (target_w - new_w) // 2
            
            canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
            
            return canvas
        else:
            return cv2.resize(image, size, interpolation=interpolation)
    except Exception as e:
        logging.error(f"Error resizing image: {e}")
        return image


def enhance_image(image: np.ndarray, brightness: float = 1.0, 
                 contrast: float = 1.0, sharpness: float = 1.0) -> np.ndarray:
    """Enhance image with brightness, contrast, and sharpness."""
    try:
        # Convert to PIL for better enhancement
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Apply enhancements
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(contrast)
        
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(sharpness)
        
        # Convert back to OpenCV format
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        logging.error(f"Error enhancing image: {e}")
        return image


def denoise_image(image: np.ndarray, method: str = 'fastNlMeans') -> np.ndarray:
    """Denoise image using specified method."""
    try:
        if method == 'fastNlMeans':
            # Fast non-local means denoising
            return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        elif method == 'gaussian':
            # Gaussian blur
            return cv2.GaussianBlur(image, (5, 5), 0)
        elif method == 'median':
            # Median blur
            return cv2.medianBlur(image, 5)
        else:
            return image
    except Exception as e:
        logging.error(f"Error denoising image: {e}")
        return image


def threshold_image(image: np.ndarray, method: str = 'adaptive', 
                    block_size: int = 11, c: float = 2) -> np.ndarray:
    """Apply threshold to image."""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if method == 'adaptive':
            # Adaptive threshold
            return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, block_size, c)
        elif method == 'otsu':
            # Otsu's threshold
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return binary
        else:
            # Simple threshold
            _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
            return binary
    except Exception as e:
        logging.error(f"Error applying threshold: {e}")
        return gray


def crop_image(image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
    """Crop image using bounding box."""
    try:
        x1, y1, x2, y2 = bbox
        
        # Ensure coordinates are within image bounds
        h, w = image.shape[:2]
        x1 = max(0, min(x1, w))
        y1 = max(0, min(y1, h))
        x2 = max(0, min(x2, w))
        y2 = max(0, min(y2, h))
        
        return image[y1:y2, x1:x2]
    except Exception as e:
        logging.error(f"Error cropping image: {e}")
        return image


def rotate_image(image: np.ndarray, angle: float, 
                 center: Optional[Tuple[int, int]] = None) -> np.ndarray:
    """Rotate image by specified angle."""
    try:
        h, w = image.shape[:2]
        
        if center is None:
            center = (w // 2, h // 2)
        
        # Calculate rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Apply rotation
        rotated = cv2.warpAffine(image, rotation_matrix, (w, h))
        
        return rotated
    except Exception as e:
        logging.error(f"Error rotating image: {e}")
        return image


def flip_image(image: np.ndarray, direction: str = 'horizontal') -> np.ndarray:
    """Flip image horizontally or vertically."""
    try:
        if direction == 'horizontal':
            return cv2.flip(image, 1)
        elif direction == 'vertical':
            return cv2.flip(image, 0)
        elif direction == 'both':
            return cv2.flip(image, -1)
        else:
            return image
    except Exception as e:
        logging.error(f"Error flipping image: {e}")
        return image


def detect_edges(image: np.ndarray, method: str = 'canny', 
                 threshold1: int = 50, threshold2: int = 150) -> np.ndarray:
    """Detect edges in image."""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if method == 'canny':
            return cv2.Canny(gray, threshold1, threshold2)
        elif method == 'sobel':
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            return np.sqrt(sobelx**2 + sobely**2).astype(np.uint8)
        elif method == 'laplacian':
            return cv2.Laplacian(gray, cv2.CV_64F)
        else:
            return gray
    except Exception as e:
        logging.error(f"Error detecting edges: {e}")
        return gray


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalize image to 0-255 range."""
    try:
        # Convert to float32
        normalized = image.astype(np.float32)
        
        # Normalize to 0-255 range
        normalized = (normalized - normalized.min()) / (normalized.max() - normalized.min()) * 255
        
        return normalized.astype(np.uint8)
    except Exception as e:
        logging.error(f"Error normalizing image: {e}")
        return image


def get_image_info(image: np.ndarray) -> dict:
    """Get comprehensive image information."""
    try:
        return {
            'shape': image.shape,
            'dtype': str(image.dtype),
            'size': image.size,
            'height': image.shape[0],
            'width': image.shape[1],
            'channels': image.shape[2] if len(image.shape) > 2 else 1,
            'min_value': np.min(image),
            'max_value': np.max(image),
            'mean_value': np.mean(image),
            'std_value': np.std(image),
        }
    except Exception as e:
        logging.error(f"Error getting image info: {e}")
        return {}


def convert_color_space(image: np.ndarray, target_space: str) -> np.ndarray:
    """Convert image to different color space."""
    try:
        if target_space == 'rgb':
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif target_space == 'hsv':
            return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        elif target_space == 'lab':
            return cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        elif target_space == 'gray':
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif target_space == 'yuv':
            return cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        else:
            return image
    except Exception as e:
        logging.error(f"Error converting color space: {e}")
        return image