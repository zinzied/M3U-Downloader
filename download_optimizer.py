import time
from typing import Dict, Optional
import asyncio

class DownloadOptimizer:
    def __init__(self):
        self.speed_history: Dict[str, list] = {}
        self.chunk_sizes: Dict[str, int] = {}
        self.last_download_time: Dict[str, float] = {}
        self.min_chunk_size = float('inf')  # Unlimited
        self.max_chunk_size = float('inf')  # Unlimited
        
    def get_optimal_chunk_size(self, url: str) -> int:
        """Get optimal chunk size based on download history."""
        return self.chunk_sizes.get(url, self.min_chunk_size)
        
    def update_speed(self, url: str, bytes_downloaded: int, duration: float) -> None:
        """Update download speed statistics."""
        if duration > 0:
            speed = bytes_downloaded / duration  # bytes per second
            if url not in self.speed_history:
                self.speed_history[url] = []
            self.speed_history[url].append(speed)
            
            # Keep only last 5 measurements
            if len(self.speed_history[url]) > 5:
                self.speed_history[url].pop(0)
                
            # Adjust chunk size based on speed
            avg_speed = sum(self.speed_history[url]) / len(self.speed_history[url])
            new_chunk_size = min(
                max(int(avg_speed / 2), self.min_chunk_size),
                self.max_chunk_size
            )
            self.chunk_sizes[url] = new_chunk_size
            
    def get_download_speed(self, url: str) -> Optional[float]:
        """Get current download speed in bytes per second."""
        if url in self.speed_history and self.speed_history[url]:
            return sum(self.speed_history[url]) / len(self.speed_history[url])
        return None

class ConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.semaphore = asyncio.Semaphore(max_connections)
        self.active_connections: Dict[str, int] = {}
        
    async def acquire(self, url: str):
        """Acquire a connection from the pool."""
        await self.semaphore.acquire()
        self.active_connections[url] = self.active_connections.get(url, 0) + 1
        
    def release(self, url: str):
        """Release a connection back to the pool."""
        if url in self.active_connections:
            self.active_connections[url] -= 1
            if self.active_connections[url] <= 0:
                del self.active_connections[url]
        self.semaphore.release()
        
    def get_active_connections(self, url: str) -> int:
        """Get number of active connections for a URL."""
        return self.active_connections.get(url, 0)