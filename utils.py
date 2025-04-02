import os
from urllib.parse import urlparse, unquote
import re

def get_extension_from_url(url: str) -> str:
    """Extract file extension from URL or default to .mp4"""
    parsed = urlparse(unquote(url))
    path = parsed.path
    
    # Common video extensions
    VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.avi', '.mov', '.m4v', '.ts']
    
    # Try to find extension in the URL path
    ext = os.path.splitext(path)[1].lower()
    if ext in VIDEO_EXTENSIONS:
        return ext
        
    # Check if extension is in query parameters
    if '.mp4' in url.lower():
        return '.mp4'
    if '.mkv' in url.lower():
        return '.mkv'
    if '.ts' in url.lower():
        return '.ts'
        
    # Default to .mp4 if no extension found
    return '.mp4'

def format_speed(speed_bytes: float) -> str:
    """Format download speed in human readable format"""
    if speed_bytes < 1024:
        return f"{speed_bytes:.1f} B/s"
    elif speed_bytes < 1024*1024:
        return f"{speed_bytes/1024:.1f} KB/s"
    else:
        return f"{speed_bytes/(1024*1024):.1f} MB/s"

def format_status(progress: float) -> str:
    """Format download status"""
    if progress >= 100:
        return "✅ Finished"
    else:
        return f"{progress:.1f}%"