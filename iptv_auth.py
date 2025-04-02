import aiohttp
import json
from urllib.parse import urlparse, parse_qs, urlencode

class IPTVAuthenticator:
    def __init__(self):
        self.session = None
        
    async def authenticate(self, url: str) -> str:
        """Authenticate and get fresh token for IPTV stream"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Extract required parameters
        mac = params.get('mac', [''])[0]
        stream_id = params.get('stream', [''])[0]
        content_type = params.get('type', [''])[0]
        
        if not all([mac, stream_id, content_type]):
            return url
            
        # Construct authentication URL
        auth_url = f"{parsed.scheme}://{parsed.netloc}/player_api.php"
        auth_params = {
            'username': mac,
            'password': mac,
            'action': 'get_link',
            'stream_id': stream_id,
            'type': content_type
        }
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            # First authenticate
            async with self.session.post(f"{auth_url}?{urlencode(auth_params)}") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, dict) and 'token' in data:
                        # Update URL with new token
                        params['play_token'] = [data['token']]
                        return parsed._replace(query=urlencode(params, doseq=True)).geturl()
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            
        return url
        
    async def close(self):
        if self.session:
            await self.session.close()