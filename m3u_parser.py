from typing import List, Dict
from file_utils import sanitize_filename, get_extension_from_url

class M3UEntry:
    def __init__(self, title: str, url: str, filename: str):
        self.title = title
        self.url = url
        self.filename = filename

class M3UParser:
    @staticmethod
    def parse(file_path: str) -> List[M3UEntry]:
        entries = []
        current_title = None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#EXTINF:'):
                        parts = line.split(',', 1)
                        if len(parts) > 1:
                            current_title = parts[1]
                    elif line and not line.startswith('#'):
                        title = current_title or f"Video_{len(entries) + 1}"
                        filename = sanitize_filename(title) + get_extension_from_url(line)
                        entries.append(M3UEntry(title, line, filename))
                        current_title = None
                        
        except Exception as e:
            raise Exception(f"Failed to parse M3U file: {str(e)}")
            
        return entries