import os
import re
from typing import Optional
from urllib.parse import urlparse

def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename."""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove control characters
    filename = "".join(char for char in filename if ord(char) >= 32)
    return filename.strip()

def get_extension_from_url(url: str) -> str:
    """Get file extension from URL or content type."""
    # Common video extensions
    VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.m4v', '.ts'}
    
    # Try to get extension from URL
    parsed_url = urlparse(url)
    path = parsed_url.path
    ext = os.path.splitext(path)[1].lower()
    
    # If valid video extension found, return it
    if ext in VIDEO_EXTENSIONS:
        return ext
    
    # Default to .mp4 if no valid extension found
    return '.mp4'

def ensure_unique_filename(base_path: str, filename: str) -> str:
    """Ensure filename is unique by adding number if necessary."""
    name, ext = os.path.splitext(filename)
    counter = 1
    final_path = os.path.join(base_path, filename)
    
    while os.path.exists(final_path):
        new_filename = f"{name}_{counter}{ext}"
        final_path = os.path.join(base_path, new_filename)
        counter += 1
        
    return final_path