import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
import os
from typing import Dict, List, Optional
from m3u_parser import M3UParser, M3UEntry
from async_downloader import DownloadManager
from file_utils import ensure_unique_filename
import threading

class M3UDownloaderGUI:
    def __init__(self):
        self.window = ThemedTk(theme="equilux")  # Modern dark theme
        self.window.title("M3U Downloader")
        self.window.geometry("1200x800")
        
        # Configure colors
        self.colors = {
            'bg': '#2e2e2e',
            'fg': '#ffffff',
            'accent': '#007acc',
            'hover': '#1e90ff'
        }
        
        self.window.configure(bg=self.colors['bg'])
        self.download_manager = DownloadManager(max_concurrent=3)
        self.entries: List[M3UEntry] = []
        self.setup_gui()
        
    def setup_gui(self):
        # Style configuration
        style = ttk.Style()
        style.configure("Custom.TButton",
            padding=10,
            font=('Segoe UI', 10),
            background=self.colors['accent']
        )
        
        style.configure("Custom.TEntry",
            fieldbackground=self.colors['bg'],
            foreground=self.colors['fg']
        )
        
        style.configure("Custom.Treeview",
            background=self.colors['bg'],
            foreground=self.colors['fg'],
            fieldbackground=self.colors['bg'],
            rowheight=30
        )
        
        style.configure("Custom.TLabelframe",
            background=self.colors['bg'],
            foreground=self.colors['fg']
        )
        
        # Main container
        main_container = ttk.Frame(self.window, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # File selection frame with gradient effect
        file_frame = ttk.LabelFrame(main_container, text="File Selection", padding="15", style="Custom.TLabelframe")
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.m3u_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        # M3U file selection with modern layout
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_select_frame, text="M3U File:", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=5)
        ttk.Entry(file_select_frame, textvariable=self.m3u_path, width=70, style="Custom.TEntry").pack(side=tk.LEFT, padx=5)
        ttk.Button(file_select_frame, text="Browse", command=self.browse_m3u, style="Custom.TButton").pack(side=tk.LEFT, padx=5)
        
        # Output directory selection with modern layout
        output_select_frame = ttk.Frame(file_frame)
        output_select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_select_frame, text="Output Directory:", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=5)
        ttk.Entry(output_select_frame, textvariable=self.output_dir, width=70, style="Custom.TEntry").pack(side=tk.LEFT, padx=5)
        ttk.Button(output_select_frame, text="Browse", command=self.browse_output, style="Custom.TButton").pack(side=tk.LEFT, padx=5)
        
        # Download settings frame
        settings_frame = ttk.LabelFrame(main_container, text="Download Settings", padding="15", style="Custom.TLabelframe")
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(settings_frame, text="Concurrent Downloads:", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=5)
        self.concurrent_var = tk.StringVar(value="3")
        concurrent_spinbox = ttk.Spinbox(settings_frame, from_=1, to=10, width=5, textvariable=self.concurrent_var)
        concurrent_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Files list frame with modern styling
        list_frame = ttk.LabelFrame(main_container, text="Files to Download", padding="15", style="Custom.TLabelframe")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create modern treeview
        self.tree = ttk.Treeview(list_frame, columns=("Title", "URL", "Status", "Speed"), 
                                show="headings", selectmode="extended", style="Custom.Treeview")
        
        # Configure modern column headers
        for col in ("Title", "URL", "Status", "Speed"):
            self.tree.heading(col, text=col, anchor=tk.W)
            
        self.tree.column("Title", width=350)
        self.tree.column("URL", width=450)
        self.tree.column("Status", width=100)
        self.tree.column("Speed", width=100)
        
        # Modern scrollbars
        y_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Control buttons with modern styling
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=15)
        
        for text, command in [
            ("Load M3U", self.load_m3u),
            ("Download Selected", self.download_selected),
            ("Download All", self.download_all)
        ]:
            btn = ttk.Button(button_frame, text=text, command=command, style="Custom.TButton")
            btn.pack(side=tk.LEFT, padx=5)
        
        # Modern status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            main_container,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=('Segoe UI', 9),
            padding=5
        )
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
            filename = f"{values[0]}{self._get_extension_from_url(url)}"  # Add proper extension
            filepath = ensure_unique_filename(output_dir, filename)
            downloads.append((url, filepath))
            self.tree.set(item, "Status", "Queued")
            self.tree.set(item, "Speed", "")
            
        def update_progress(filename: str, progress: float, speed: Optional[float] = None):
            try:
                self.window.after(0, self._update_progress, filename, progress, speed)
            except Exception as e:
                print(f"Progress update error: {str(e)}")
            
        def error_callback(filename: str, error: str):
            self.window.after(0, lambda: self.tree.set(
                [item for item in self.tree.get_children() 
                 if self.tree.item(item)['values'][0] == filename][0],
                "Status", f"Error: {error}"
            ))

        try:
            self.download_manager.start_downloads(downloads, progress_callback=update_progress)
            self.status_var.set("Downloading files...")
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to start downloads: {str(e)}")
        
    def _get_extension_from_url(self, url: str) -> str:
        """Extract the file extension from a URL."""
        parsed_url = os.path.splitext(url)
        return parsed_url[1] if parsed_url[1] else ".unknown"

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
        self.window.destroy