import aiohttp
import aiofiles
import asyncio
from typing import Callable, Optional, Dict
import os
from concurrent.futures import ThreadPoolExecutor
from download_optimizer import DownloadOptimizer, ConnectionPool
import time

class AsyncDownloader:
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.optimizer = DownloadOptimizer()
        self.connection_pool = ConnectionPool(max_connections=max_concurrent * 2)
        self.session = None
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=None, connect=60, sock_read=60)
        conn = aiohttp.TCPConnector(limit=self.max_concurrent * 2, force_close=False)
        self.session = aiohttp.ClientSession(timeout=timeout, connector=conn)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def download_file(self, url: str, filepath: str, 
                          progress_callback: Optional[Callable[[str, float, Optional[float]], None]] = None) -> None:
        try:
            await self.connection_pool.acquire(url)
            headers = {'Range': 'bytes=0-'}  # Support resume
            
            async with self.session.get(url, headers=headers) as response:
                if response.status not in (200, 206):
                    raise Exception(f"HTTP {response.status}: {response.reason}")
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                start_time = time.time()
                last_update = start_time
                
                async with aiofiles.open(filepath, 'wb') as f:
                    while True:
                        chunk_size = self.optimizer.get_optimal_chunk_size(url)
                        chunk = await response.content.read(chunk_size)
                        
                        if not chunk:
                            break
                            
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update download speed and progress every 0.5 seconds
                        current_time = time.time()
                        if current_time - last_update >= 0.5:
                            duration = current_time - last_update
                            self.optimizer.update_speed(url, len(chunk), duration)
                            speed = self.optimizer.get_download_speed(url)
                            
                            if progress_callback and total_size:
                                progress = (downloaded / total_size) * 100
                                progress_callback(
                                    os.path.basename(filepath),
                                    progress,
                                    speed
                                )
                            last_update = current_time
                            
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            raise Exception(f"Failed to download {url}: {str(e)}")
        finally:
            self.connection_pool.release(url)

class DownloadManager:
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        
    def start_downloads(self, downloads: list, progress_callback: Optional[Callable] = None):
        async def run_downloads():
            async with AsyncDownloader(self.max_concurrent) as downloader:
                tasks = []
                for url, filepath in downloads:
                    task = asyncio.create_task(
                        downloader.download_file(url, filepath, progress_callback)
                    )
                    tasks.append(task)
                await asyncio.gather(*tasks, return_exceptions=True)
                
        def run_async_downloads():
            asyncio.run(run_downloads())
            
        self.executor.submit(run_async_downloads)
        
    def shutdown(self):
        self.executor.shutdown(wait=False)