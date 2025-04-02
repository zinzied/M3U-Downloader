# M3U Downloader

A powerful, asynchronous M3U playlist downloader with a user-friendly GUI interface. Specially designed for downloading VOD content and series from IPTV M3U playlists with support for authentication and token management.

## Features

- 🚀 **Asynchronous Downloads**: Utilizes Python's asyncio for efficient concurrent downloads
- 🎬 **VOD Support**: Download movies and series with proper file extensions
- 🔐 **IPTV Authentication**: Handles token-based authentication and auto-refresh
- 📊 **Real-time Progress**: Live download speed and progress tracking
- 🎯 **Connection Pool Management**: Intelligent handling of concurrent connections
- 📱 **User-Friendly GUI**: Clean and intuitive interface built with tkinter
- 🔄 **Auto-Retry**: Automatic retry on failed downloads or expired tokens
- 🛠 **Customizable Settings**: Adjust concurrent download limits and output directories

## Requirements

- Python 3.7+
- aiohttp
- aiofiles
- tkinter (usually comes with Python)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/zinzied/m3u-Downloader.git
cd m3u-Downloader
```

2. Install dependencies:
```bash
pip install aiohttp aiofiles
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Using the GUI:
   - Load your M3U file containing VOD/Series links
   - Select output directory for downloads
   - Set concurrent downloads (recommended: 2-3)
   - Select items to download
   - Monitor real-time progress and speed

## Key Components

### AsyncDownloader
- Handles asynchronous file downloads
- Manages IPTV authentication and token refresh
- Preserves original file extensions
- Real-time speed calculation and progress updates

### IPTVAuthenticator
- Handles token-based authentication
- Automatic token refresh on expiration
- Supports various IPTV provider APIs

### DownloadManager
- Manages concurrent downloads
- Smart retry mechanism
- Progress tracking and speed monitoring

### GUI Interface
- Clean and intuitive design
- Real-time download speeds
- Progress tracking per file
- File extension preservation

## Supported Features

- ✅ VOD/Movie downloads
- ✅ Series/Episode downloads
- ✅ Token-based authentication
- ✅ Auto token refresh
- ✅ Real-time speed display
- ✅ Progress tracking
- ✅ Original file extensions
- ✅ Multiple concurrent downloads

## Troubleshooting

Common issues and solutions:

- **458 Error**: Token expired - the app will automatically retry with a new token
- **Download Stuck**: Check internet connection and server availability
- **Wrong Extension**: File extensions are preserved from source URL

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python's asyncio for high-performance async I/O
- Uses aiohttp for efficient HTTP requests
- Implements best practices for IPTV content downloading
