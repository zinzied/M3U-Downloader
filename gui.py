import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Dict, List, Optional
from m3u_parser import M3UParser, M3UEntry
from async_downloader import DownloadManager
from file_utils import ensure_unique_filename
import threading

class M3UDownloaderGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("M3U Downloader")
        self.window.geometry("1000x700")
        
        self.download_manager = DownloadManager(max_concurrent=3)
        self.entries: List[M3UEntry] = []
        self.setup_gui()
        
    def setup_gui(self):
        # Style configuration
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        
        # Main container
        main_container = ttk.Frame(self.window, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_container, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.m3u_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        # M3U file selection
        ttk.Label(file_frame, text="M3U File:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(file_frame, textvariable=self.m3u_path, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_m3u).grid(row=0, column=2, padx=5)
        
        # Output directory selection
        ttk.Label(file_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_dir, width=60).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Download settings frame
        settings_frame = ttk.LabelFrame(main_container, text="Download Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(settings_frame, text="Concurrent Downloads:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.concurrent_var = tk.StringVar(value="3")
        concurrent_spinbox = ttk.Spinbox(settings_frame, from_=1, to=10, width=5, textvariable=self.concurrent_var)
        concurrent_spinbox.grid(row=0, column=1, padx=5)
        
        # Files list frame
        list_frame = ttk.LabelFrame(main_container, text="Files to Download", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        self.tree = ttk.Treeview(list_frame, columns=("Title", "URL", "Status", "Speed"), show="headings", selectmode="extended")
        self.tree.heading("Title", text="Title")
        self.tree.heading("URL", text="URL")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Speed", text="Speed")
        
        self.tree.column("Title", width=300)
        self.tree.column("URL", width=400)
        self.tree.column("Status", width=100)
        self.tree.column("Speed", width=100)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Grid layout for treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Load M3U", command=self.load_m3u).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Download Selected", command=self.download_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Download All", command=self.download_all).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_container, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
    def browse_m3u(self):
        filename = filedialog.askopenfilename(
            filetypes=[("M3U files", "*.m3u"), ("All files", "*.*")]
        )
        if filename:
            self.m3u_path.set(filename)
            
    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)
            
    def load_m3u(self):
        m3u_file = self.m3u_path.get()
        if not m3u_file:
            messagebox.showerror("Error", "Please select an M3U file first")
            return
            
        try:
            self.entries = M3UParser.parse(m3u_file)
            self.tree.delete(*self.tree.get_children())
            for entry in self.entries:
                self.tree.insert("", tk.END, values=(entry.title, entry.url, "Pending", ""))
            self.status_var.set(f"Loaded {len(self.entries)} items")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def download_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select items to download")
            return
        self._start_download(selected_items)
        
    def download_all(self):
        all_items = self.tree.get_children()
        if not all_items:
            messagebox.showinfo("Info", "No items to download")
            return
        self._start_download(all_items)
        
    def _start_download(self, items):
        output_dir = self.output_dir.get()
        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory")
            return
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Update concurrent downloads
        try:
            max_concurrent = int(self.concurrent_var.get())
            self.download_manager = DownloadManager(max_concurrent=max_concurrent)
        except ValueError:
            messagebox.showerror("Error", "Invalid concurrent downloads value")
            return
            
        downloads = []
        for item in items:
            values = self.tree.item(item)['values']
            url = values[1]
            filename = values[0]
            filepath = ensure_unique_filename(output_dir, filename)
            downloads.append((url, filepath))
            self.tree.set(item, "Status", "Queued")
            self.tree.set(item, "Speed", "")
            
        def update_progress(filename: str, progress: float, speed: Optional[float] = None):
            self.window.after(0, self._update_progress, filename, progress, speed)
            
        self.download_manager.start_downloads(downloads, update_progress)
        self.status_var.set("Downloading files...")
        
    def _format_speed(self, speed: float) -> str:
        """Format speed in bytes/second to human readable format."""
        if speed < 1024:
            return f"{speed:.1f} B/s"
        elif speed < 1024 * 1024:
            return f"{speed/1024:.1f} KB/s"
        else:
            return f"{speed/(1024*1024):.1f} MB/s"
        
    def _update_progress(self, filename: str, progress: float, speed: Optional[float] = None):
        for item in self.tree.get_children():
            if self.tree.item(item)['values'][0] == filename:
                status = "Complete" if progress >= 100 else f"{progress:.1f}%"
                self.tree.set(item, "Status", status)
                if speed is not None:
                    self.tree.set(item, "Speed", self._format_speed(speed))
                break
                
    def run(self):
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.window.mainloop()
        
    def _on_closing(self):
        self.download_manager.shutdown()
        self.window.destroy()