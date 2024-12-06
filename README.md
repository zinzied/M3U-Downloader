# M3U Downloader

A powerful, asynchronous M3U playlist downloader with a user-friendly GUI interface. This application allows you to efficiently download media files from M3U playlists with optimized performance and progress tracking.

## Features

- 🚀 **Asynchronous Downloads**: Utilizes Python's asyncio for efficient concurrent downloads
- 📊 **Smart Download Optimization**: Automatically adjusts chunk sizes based on download speeds
- 🎯 **Connection Pool Management**: Intelligent handling of concurrent connections
- 📱 **User-Friendly GUI**: Clean and intuitive interface built with tkinter
- 📝 **Progress Tracking**: Real-time progress and speed monitoring for each download
- 🔄 **Resume Support**: Supports download resumption for interrupted transfers
- 🎮 **Flexible Control**: Download selected items or entire playlists
- 🛠 **Customizable Settings**: Adjust concurrent download limits and output directories

## Architecture

The application is built with a modular architecture consisting of several key components:

- `AsyncDownloader`: Core download engine with async I/O operations
- `DownloadOptimizer`: Smart optimization of chunk sizes and download speeds
- `ConnectionPool`: Management of concurrent connections
- `M3UParser`: Parsing and processing of M3U playlist files
- `M3UDownloaderGUI`: User interface and download management

## Requirements

- Python 3.7+
- aiohttp
- aiofiles
- tkinter (usually comes with Python)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/m3u-downloader.git
cd m3u-downloader
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
   - Click "Browse" to select an M3U file
   - Choose an output directory for downloads
   - Set the number of concurrent downloads (default: 3)
   - Click "Load M3U" to parse the playlist
   - Select items to download or use "Download All"
   - Monitor progress in the main window

## Key Components

### AsyncDownloader
- Handles asynchronous file downloads
- Manages connection pools and timeouts
- Implements context manager for resource cleanup

### DownloadOptimizer
- Dynamically adjusts chunk sizes based on performance
- Maintains download speed history
- Optimizes bandwidth usage

### ConnectionPool
- Manages concurrent connections
- Prevents server overload
- Implements connection limiting and tracking

### M3UParser
- Parses M3U playlist files
- Extracts media URLs and metadata
- Handles various M3U format variations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python's asyncio for high-performance async I/O
- Uses aiohttp for efficient HTTP requests
- Implements best practices for concurrent downloads
