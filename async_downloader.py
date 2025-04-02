import aiohttp
import aiofiles
import asyncio
from typing import Callable, Optional, Dict
import os
from concurrent.futures import ThreadPoolExecutor
from download_optimizer import DownloadOptimizer, ConnectionPool
import time
from iptv_auth import IPTVAuthenticator
from utils import format_speed

class AsyncDownloader:
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.optimizer = DownloadOptimizer()
        self.connection_pool = ConnectionPool(max_connections=max_concurrent * 2)
        self.session = None
        self.retry_count = 3  # Add retry count for failed requests
        self.authenticator = IPTVAuthenticator()
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=None, connect=60, sock_read=60)
        conn = aiohttp.TCPConnector(limit=self.max_concurrent * 2, force_close=True)  # Changed to force_close=True
        self.session = aiohttp.ClientSession(timeout=timeout, connector=conn)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.authenticator:
            await self.authenticator.close()
        if self.session:
            await self.session.close()

    async def _refresh_token(self, url: str) -> str:
        # Extract base URL and parameters
        from urllib.parse import urlparse, parse_qs, urlencode
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # If there's a play_token, try to refresh it
        if 'play_token' in params:
            # Construct token refresh URL - adjust this according to your server's API
            base_url = f"{parsed.scheme}://{parsed.netloc}/player_api.php"
            refresh_params = {
                'mac': params.get('mac', [''])[0],
                'type': params.get('type', [''])[0],
                'stream': params.get('stream', [''])[0],
                'refresh': '1'
            }
            
            async with self.session.get(f"{base_url}?{urlencode(refresh_params)}") as response:
                if response.status == 200:
                    data = await response.json()
                    if 'play_token' in data:
                        params['play_token'] = [data['play_token']]
                        # Reconstruct URL with new token
                        return parsed._replace(query=urlencode(params, doseq=True)).geturl()
        
        return url

    async def download_file(self, url: str, filepath: str, 
                          progress_callback: Optional[Callable[[str, float, Optional[str]], None]] = None) -> None:
        retries = 0
        while retries < self.retry_count:
            try:
                await self.connection_pool.acquire(url)
                
                # Authenticate and get fresh URL if needed
                if 'play_token' in url:
                    url = await self.authenticator.authenticate(url)
                
                headers = {
                    'User-Agent': 'VLC/3.0.16 LibVLC/3.0.16',
                    'Accept': '*/*',
                    'Connection': 'keep-alive'
                }
                
                async with self.session.get(url, headers=headers, allow_redirects=True) as response:
                    if response.status == 458:  # Token expired
                        if retries < self.retry_count - 1:
                            url = await self.authenticator.authenticate(url)
                            retries += 1
                            await asyncio.sleep(2)
                            continue
                    
                    if response.status not in (200, 206):
                        raise Exception(f"HTTP {response.status}: {response.reason}")
                    
                    # Rest of the download logic remains the same
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    start_time = time.time()
                    last_update = start_time
                    chunk_sizes = []  # For calculating average speed
                    
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    async with aiofiles.open(filepath, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                            downloaded += len(chunk)
                            chunk_sizes.append((time.time(), len(chunk)))
                            
                            # Calculate speed over last 2 seconds
                            current_time = time.time()
                            if current_time - last_update >= 0.5:
                                # Remove old chunks from calculation
                                chunk_sizes = [(t, s) for t, s in chunk_sizes 
                                             if current_time - t <= 2]
                                
                                if chunk_sizes:
                                    duration = current_time - chunk_sizes[0][0]
                                    if duration > 0:
                                        speed = sum(s for _, s in chunk_sizes) / duration
                                        speed_str = format_speed(speed)
                                        
                                        if progress_callback and total_size:
                                            progress = (downloaded / total_size) * 100
                                            progress_callback(
                                                os.path.basename(filepath),
                                                progress,
                                                speed_str
                                            )
                                
                                last_update = current_time
                    
                    # If we get here, download was successful
                    return
                    
            except Exception as e:
                print(f"Download error for {url}: {str(e)}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                if retries >= self.retry_count - 1:
                    raise
                retries += 1
                await asyncio.sleep(2)  # Wait before retry
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