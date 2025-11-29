"""
Airtable Scraper GUI Application

A comprehensive graphical interface for the Airtable Scraper project.
Provides all functionality of the command-line version with an intuitive GUI.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import sys
import os
from pathlib import Path
from datetime import datetime
import logging
try:
    from tkinter import font as tkFont
except ImportError:
    pass

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from modules.data_extractor import DataExtractor
from modules.airtable_uploader import AirtableUploader

class LogHandler(logging.Handler):
    """Custom logging handler that sends logs to a queue for GUI display"""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))

class AirtableScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Airtable Scraper Pro - Document Processing Suite")
        self.root.geometry("1000x650")  # More compact size
        self.root.minsize(900, 600)     # Smaller minimum size
        
        # Set application icon and styling
        try:
            # Try to set a nice color scheme
            self.root.configure(bg='#f0f0f0')
        except:
            pass
        
        # Initialize variables
        self.project_folder = tk.StringVar(value="BIOME")
        self.extract_only = tk.BooleanVar(value=False)
        self.enable_sync = tk.BooleanVar(value=True)
        
        # Data type variables
        self.sync_choices = tk.BooleanVar(value=True)
        self.sync_lenses = tk.BooleanVar(value=True)
        self.sync_sources = tk.BooleanVar(value=True)
        self.sync_metas = tk.BooleanVar(value=True)
        self.sync_patterns = tk.BooleanVar(value=True)
        self.sync_variations = tk.BooleanVar(value=True)
        
        # Processing state
        self.is_processing = False
        self.log_queue = queue.Queue()
        
        self.setup_ui()
        self.setup_logging()
        self.check_log_queue()
        
        # Test initial connection
        self.root.after(1000, self.test_airtable_connection_silent)
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Create main frame with minimal padding for more space
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for better responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(9, weight=1)  # Log area gets most space
        
        # Compact Professional Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 15), sticky=(tk.W, tk.E))
        header_frame.columnconfigure(1, weight=1)
        
        # Main title - Compact
        title_label = ttk.Label(header_frame, text="🔥 Airtable Scraper Pro", 
                               font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 3))
        
        # Subtitle - Compact
        subtitle_label = ttk.Label(header_frame, text="Document Processing & Data Sync", 
                                  font=("Segoe UI", 9), foreground="#666666")
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 5))
        
        # Status indicator
        self.connection_status = ttk.Label(header_frame, text="●", font=("Segoe UI", 12), foreground="orange")
        self.connection_status.grid(row=0, column=2, sticky=tk.E)
        self.create_tooltip(self.connection_status, "Connection Status: Not checked")
        
        # Project Folder Selection with enhanced styling
        folder_label = ttk.Label(main_frame, text="📁 Project Folder", 
                                font=("Segoe UI", 11, "bold"))
        folder_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 2))
        
        folder_desc = ttk.Label(main_frame, text="Select the folder containing your DOCX files to process", 
                               font=("Segoe UI", 9), foreground="#666666")
        folder_desc.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.project_folder, 
                                     font=("Segoe UI", 10), width=60)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="📂 Browse", 
                               command=self.browse_folder)
        browse_btn.grid(row=0, column=1)
        self.create_tooltip(browse_btn, "Browse for project folder containing DOCX files")
        
        # Operation Mode - Compact single row
        mode_frame = ttk.LabelFrame(main_frame, text="🎯 Operation Mode", padding="10")
        mode_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        mode_frame.columnconfigure(2, weight=1)
        
        sync_radio = ttk.Radiobutton(mode_frame, text="🔄 Extract & Sync", 
                                    variable=self.extract_only, value=False)
        sync_radio.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        self.create_tooltip(sync_radio, "Extract data from documents and upload to Airtable database")
        
        extract_radio = ttk.Radiobutton(mode_frame, text="📤 Extract Only", 
                                       variable=self.extract_only, value=True)
        extract_radio.grid(row=0, column=1, sticky=tk.W)
        self.create_tooltip(extract_radio, "Extract data without uploading (for testing or offline processing)")
        
        # Data Types Selection - Single row layout
        sync_frame = ttk.LabelFrame(main_frame, text="🗂️ Data Types", padding="10")
        sync_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        sync_frame.columnconfigure(5, weight=1)
        
        # Single row of checkboxes - make grid more compact
        choices_cb = ttk.Checkbutton(sync_frame, text="💭 Choices", variable=self.sync_choices)
        choices_cb.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.create_tooltip(choices_cb, "Pattern choice content and decisions")
        
        lenses_cb = ttk.Checkbutton(sync_frame, text="📖 Lenses", variable=self.sync_lenses)
        lenses_cb.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        self.create_tooltip(lenses_cb, "Conceptual frameworks and perspectives")
        
        sources_cb = ttk.Checkbutton(sync_frame, text="📚 Sources", variable=self.sync_sources)
        sources_cb.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.create_tooltip(sources_cb, "Reference materials and citations")
        
        metas_cb = ttk.Checkbutton(sync_frame, text="📋 Metas", variable=self.sync_metas)
        metas_cb.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        self.create_tooltip(metas_cb, "Document metadata and information")
        
        patterns_cb = ttk.Checkbutton(sync_frame, text="🎯 Patterns", variable=self.sync_patterns)
        patterns_cb.grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5,0))
        self.create_tooltip(patterns_cb, "Core structural patterns and frameworks")
        
        variations_cb = ttk.Checkbutton(sync_frame, text="🔄 Variations", variable=self.sync_variations)
        variations_cb.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(5,0))
        self.create_tooltip(variations_cb, "Pattern variations and implementations")
        
        # Selection buttons - More compact
        button_frame = ttk.Frame(sync_frame)
        button_frame.grid(row=1, column=0, columnspan=5, pady=(10, 0), sticky=tk.W)
        
        select_all_btn = ttk.Button(button_frame, text="✅ All", 
                                   command=self.select_all_types)
        select_all_btn.grid(row=0, column=0, padx=(0, 10))
        self.create_tooltip(select_all_btn, "Select all data types for processing")
        
        deselect_all_btn = ttk.Button(button_frame, text="❌ None", 
                                     command=self.deselect_all_types)
        deselect_all_btn.grid(row=0, column=1, padx=(0, 15))
        self.create_tooltip(deselect_all_btn, "Deselect all data types")
        
        # Add compact status info
        ttk.Label(button_frame, text="💡 Variations auto-include Patterns", 
                 font=("Segoe UI", 8), foreground="#0066cc").grid(row=0, column=2, padx=(10, 0))
        
        # Sync Options with enhanced design
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Advanced Options", padding="15")
        options_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        sync_checkbox = ttk.Checkbutton(options_frame, text="🔗 Enable relationship linking (--sync)", 
                                       variable=self.enable_sync)
        sync_checkbox.grid(row=0, column=0, sticky=tk.W)
        self.create_tooltip(sync_checkbox, "Connect related records in Airtable (sources to patterns, etc.)")
        
        # Action Buttons with better visibility
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=7, column=0, columnspan=3, pady=(0, 15))
        
        # Create a visible start button with better styling
        self.start_button = ttk.Button(action_frame, text="🚀 START PROCESSING", 
                                      command=self.start_processing,
                                      style="Start.TButton")
        self.start_button.grid(row=0, column=0, padx=(0, 15), pady=2)
        self.create_tooltip(self.start_button, "Begin data extraction and processing")
        
        self.stop_button = ttk.Button(action_frame, text="🛑 Stop", 
                                     command=self.stop_processing, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(0, 15))
        self.create_tooltip(self.stop_button, "Cancel current processing operation")
        
        # Add test connection button
        test_btn = ttk.Button(action_frame, text="🔧 Test Connection", 
                             command=self.test_airtable_connection)
        test_btn.grid(row=0, column=2)
        self.create_tooltip(test_btn, "Test Airtable connection and credentials")
        
        # Progress Bar with label
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to process", 
                                       font=("Segoe UI", 9), foreground="#666666")
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Scrollable Log Display - Optimized for screen space
        log_frame = ttk.LabelFrame(main_frame, text="📝 Log", padding="5")
        log_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
        # Compact log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        log_controls.columnconfigure(0, weight=1)
        
        ttk.Label(log_controls, text="Real-time processing info", 
                 font=("Segoe UI", 8), foreground="#666666").grid(row=0, column=0, sticky=tk.W)
        
        clear_log_btn = ttk.Button(log_controls, text="🗑️", command=self.clear_log, width=3)
        clear_log_btn.grid(row=0, column=1)
        self.create_tooltip(clear_log_btn, "Clear the log display")
        
        # Better contrast log display with proper scrolling and auto-sizing
        self.log_display = scrolledtext.ScrolledText(log_frame, height=10, width=85, 
                                                    font=("Consolas", 8), wrap=tk.WORD,
                                                    bg="#f8f8f8", fg="#333333",
                                                    insertbackground="#333333",
                                                    selectbackground="#0078d4",
                                                    selectforeground="white")
        self.log_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Enable automatic scrolling to bottom
        self.auto_scroll = True
        
        # Status Bar with enhanced styling
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, padx=(0, 5))
        self.status_var = tk.StringVar(value="Ready - Select folder and options to begin")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                font=("Segoe UI", 9), foreground="#0066cc")
        status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Add version info
        version_label = ttk.Label(status_frame, text="v2.0 Pro", 
                                 font=("Segoe UI", 8), foreground="#999999")
        version_label.grid(row=0, column=2, sticky=tk.E)
        
        # Menu Bar
        self.create_menu()
        
        # Initialize tooltips
        self.tooltips = []
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            tooltip.configure(bg='#ffffe0', relief='solid', borderwidth=1)
            label = tk.Label(tooltip, text=text, bg='#ffffe0', fg='#000000', 
                           font=("Segoe UI", 9), padx=5, pady=3)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
        
    def create_menu(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Project Folder...", command=self.browse_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Clear Log", command=self.clear_log)
        file_menu.add_command(label="Save Log...", command=self.save_log)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Settings Menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Configure Airtable...", command=self.configure_airtable)
        settings_menu.add_command(label="View Current Settings", command=self.show_settings)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Usage Guide", command=self.show_usage_guide)
        
    def setup_logging(self):
        """Setup logging to capture output from the scraper modules"""
        # Create a custom logger
        self.logger = logging.getLogger("AirtableScraperGUI")
        self.logger.setLevel(logging.DEBUG)  # Capture more detailed logs
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Also capture the root logger to get module logs
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Create our custom handler
        handler = LogHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', 
                                    datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Add handler to root logger to catch all module logs
        if not any(isinstance(h, LogHandler) for h in root_logger.handlers):
            root_logger.addHandler(handler)
        
    def check_log_queue(self):
        """Check for new log messages and display them with color coding"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                
                # Configure text tags for different log levels if not already done
                if not hasattr(self, '_tags_configured'):
                    self.log_display.tag_configure("INFO", foreground="#0066cc")
                    self.log_display.tag_configure("WARNING", foreground="#ff8c00")
                    self.log_display.tag_configure("ERROR", foreground="#dc3545")
                    self.log_display.tag_configure("SUCCESS", foreground="#28a745")
                    self._tags_configured = True
                
                # Determine tag based on message content
                tag = "INFO"  # default
                if "[WARNING]" in message or "Warning" in message:
                    tag = "WARNING"
                elif "[ERROR]" in message or "Error" in message or "Failed" in message:
                    tag = "ERROR"
                elif "✅" in message or "SUCCESS" in message or "Complete" in message:
                    tag = "SUCCESS"
                
                self.log_display.insert(tk.END, message + "\n", tag)
                if self.auto_scroll:
                    self.log_display.see(tk.END)
                    # Limit log size to prevent memory issues
                    lines = int(self.log_display.index('end-1c').split('.')[0])
                    if lines > 1000:
                        self.log_display.delete('1.0', '100.0')
        except queue.Empty:
            pass
        finally:
            # Schedule next check
            self.root.after(100, self.check_log_queue)
    
    def browse_folder(self):
        """Browse for project folder"""
        initial_dir = settings.SOURCE_DIR if settings.SOURCE_DIR.exists() else Path.home()
        folder = filedialog.askdirectory(
            title="Select Project Folder",
            initialdir=str(initial_dir)
        )
        if folder:
            # Convert to relative path if within SOURCE_DIR
            folder_path = Path(folder)
            try:
                relative_path = folder_path.relative_to(settings.SOURCE_DIR)
                self.project_folder.set(str(relative_path))
            except ValueError:
                # Not within SOURCE_DIR, use absolute path
                self.project_folder.set(folder)
    
    def select_all_types(self):
        """Select all data types"""
        self.sync_choices.set(True)
        self.sync_lenses.set(True)
        self.sync_sources.set(True)
        self.sync_metas.set(True)
        self.sync_patterns.set(True)
        self.sync_variations.set(True)
    
    def deselect_all_types(self):
        """Deselect all data types"""
        self.sync_choices.set(False)
        self.sync_lenses.set(False)
        self.sync_sources.set(False)
        self.sync_metas.set(False)
        self.sync_patterns.set(False)
        self.sync_variations.set(False)
    
    def test_airtable_connection(self):
        """Test Airtable connection and update status"""
        if not settings.AIRTABLE_CONFIG.get("api_token") or not settings.AIRTABLE_CONFIG.get("base_id"):
            self.connection_status.config(foreground="red", text="✗")
            self.create_tooltip(self.connection_status, "Connection Status: Not configured")
            messagebox.showwarning("Configuration Missing", 
                                 "Airtable credentials not configured.\n\nPlease go to Settings → Configure Airtable to set up your API token and Base ID.")
            return False
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {settings.AIRTABLE_CONFIG['api_token']}",
                "Content-Type": "application/json"
            }
            base_url = f"https://api.airtable.com/v0/{settings.AIRTABLE_CONFIG['base_id']}"
            
            # Test connection with a simple API call
            resp = requests.get(f"{base_url}/Sources?maxRecords=1", headers=headers, timeout=10)
            
            if resp.status_code == 200:
                self.connection_status.config(foreground="green", text="✓")
                self.create_tooltip(self.connection_status, "Connection Status: Connected successfully")
                messagebox.showinfo("Connection Success", "Successfully connected to Airtable!")
                return True
            else:
                self.connection_status.config(foreground="red", text="✗")
                self.create_tooltip(self.connection_status, f"Connection Status: Error {resp.status_code}")
                messagebox.showerror("Connection Failed", 
                                   f"Failed to connect to Airtable.\n\nStatus Code: {resp.status_code}\nResponse: {resp.text[:200]}...")
                return False
                
        except Exception as e:
            self.connection_status.config(foreground="red", text="✗")
            self.create_tooltip(self.connection_status, f"Connection Status: Error - {str(e)}")
            messagebox.showerror("Connection Error", f"Error testing connection:\n\n{str(e)}")
            return False
    
    def test_airtable_connection_silent(self):
        """Test connection silently on startup"""
        if not settings.AIRTABLE_CONFIG.get("api_token") or not settings.AIRTABLE_CONFIG.get("base_id"):
            self.connection_status.config(foreground="orange", text="●")
            self.create_tooltip(self.connection_status, "Connection Status: Not configured")
            return
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {settings.AIRTABLE_CONFIG['api_token']}",
                "Content-Type": "application/json"
            }
            base_url = f"https://api.airtable.com/v0/{settings.AIRTABLE_CONFIG['base_id']}"
            
            resp = requests.get(f"{base_url}/Sources?maxRecords=1", headers=headers, timeout=5)
            
            if resp.status_code == 200:
                self.connection_status.config(foreground="green", text="✓")
                self.create_tooltip(self.connection_status, "Connection Status: Connected and ready")
            else:
                self.connection_status.config(foreground="red", text="✗")
                self.create_tooltip(self.connection_status, f"Connection Status: Error {resp.status_code}")
        except:
            self.connection_status.config(foreground="orange", text="●")
            self.create_tooltip(self.connection_status, "Connection Status: Could not verify")
    
    def get_selected_sync_types(self):
        """Get list of selected sync types"""
        sync_types = []
        if self.sync_choices.get():
            sync_types.append('choices')
        if self.sync_lenses.get():
            sync_types.append('lenses')
        if self.sync_sources.get():
            sync_types.append('sources')
        if self.sync_metas.get():
            sync_types.append('metas')
        if self.sync_patterns.get():
            sync_types.append('patterns')
        if self.sync_variations.get():
            sync_types.append('variations')
        return sync_types
    
    def validate_inputs(self):
        """Validate user inputs before processing"""
        if not self.project_folder.get().strip():
            messagebox.showerror("Error", "Please specify a project folder.")
            return False
        
        sync_types = self.get_selected_sync_types()
        if not sync_types:
            messagebox.showerror("Error", "Please select at least one data type to process.")
            return False
        
        # Check if Airtable credentials are configured (if not extract-only)
        if not self.extract_only.get():
            if not settings.AIRTABLE_CONFIG.get("api_token") or not settings.AIRTABLE_CONFIG.get("base_id"):
                result = messagebox.askyesno(
                    "Airtable Configuration Missing",
                    "Airtable credentials are not configured. Do you want to proceed in extract-only mode?"
                )
                if result:
                    self.extract_only.set(True)
                else:
                    return False
        
        return True
    
    def start_processing(self):
        """Start the data processing in a separate thread"""
        if not self.validate_inputs():
            return
        
        self.is_processing = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress.start()
        self.status_var.set("Processing documents...")
        self.progress_label.config(text="Initializing processing pipeline...")
        self.clear_log()
        
        # Start processing in separate thread
        self.processing_thread = threading.Thread(target=self.run_processing, daemon=True)
        self.processing_thread.start()
    
    def stop_processing(self):
        """Stop the current processing"""
        self.is_processing = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress.stop()
        self.status_var.set("Processing cancelled by user")
        self.progress_label.config(text="Operation cancelled")
        self.logger.warning("Processing stopped by user")
    
    def run_processing(self):
        """Main processing function (runs in separate thread)"""
        try:
            sync_types = self.get_selected_sync_types()
            folder = self.project_folder.get()
            extract_only = self.extract_only.get()
            enable_linking = self.enable_sync.get()
            
            self.logger.info("="*50)
            self.logger.info("STARTING AIRTABLE SCRAPER PROJECT")
            self.logger.info("="*50)
            self.logger.info(f"Sync Types: {', '.join(sync_types)}")
            self.logger.info(f"Target Folder: {folder}")
            self.logger.info(f"Linking Mode: {'Enabled' if enable_linking else 'Disabled'}")
            
            if extract_only:
                self.logger.info("Mode: Extract only (no Airtable sync)")
            else:
                self.logger.info("Mode: Extract and sync to Airtable")
            
            # Auto-include patterns when variations are requested
            if 'variations' in sync_types and 'patterns' not in sync_types:
                sync_types.append('patterns')
                self.logger.info("Auto-including patterns (required for variation linking)")
            
            # Initialize modules
            extractor = DataExtractor(log_handler=self.logger)
            
            # Find project folders
            project_folders = self.find_project_folders(folder)
            
            if not project_folders:
                self.logger.warning(f"No valid project folders found in/at: {folder}")
                return
            
            self.logger.info(f"Found {len(project_folders)} project(s) to process: {[p.name for p in project_folders]}")
            
            # Process each project
            for project_path in project_folders:
                if not self.is_processing:
                    break
                
                self.logger.info("-" * 30)
                self.logger.info(f"Processing Project: {project_path.name}")
                
                extracted_data = extractor.process_folder(str(project_path), extract_types=sync_types)
                
                if not extracted_data or (not extracted_data.get("documents") and not extracted_data.get("metas")):
                    self.logger.warning(f"No data extracted for {project_path.name}. Skipping sync.")
                    continue
                
                # Upload to Airtable (unless extract-only mode)
                if not extract_only and self.is_processing:
                    self.logger.info(f"Initializing Airtable Sync for {project_path.name}...")
                    uploader = AirtableUploader(log_handler=self.logger)
                    
                    try:
                        # Always fetch patterns when syncing variations for proper linking
                        fetch_types = sync_types[:]
                        if 'variations' in sync_types and 'patterns' not in fetch_types:
                            fetch_types.append('patterns')
                            self.logger.info("Also fetching patterns for variation linking")
                        
                        # Read already uploaded data and sync selectively
                        uploader.fetch_existing_records(fetch_types)
                        uploader.sync_data(extracted_data, sync_types, enable_linking)
                        
                    except Exception as e:
                        self.logger.error(f"Upload failed for {project_path.name}: {str(e)}")
                        import traceback
                        self.logger.error(traceback.format_exc())
                else:
                    if extract_only:
                        self.logger.info(f"Skipping Airtable sync for {project_path.name} (extract-only mode)")
            
            if self.is_processing:
                self.logger.info("="*50)
                self.logger.info("PROJECT EXECUTION COMPLETE")
                self.logger.info("="*50)
                
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
        finally:
            # Update UI from main thread
            self.root.after(0, self.processing_complete)
    
    def processing_complete(self):
        """Called when processing is complete (runs in main thread)"""
        self.is_processing = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress.stop()
        self.status_var.set("Processing completed successfully")
        self.progress_label.config(text="Ready for next operation")
    
    def find_project_folders(self, start_path_str):
        """Find project folders to process (same logic as main.py)"""
        # Resolve path
        if os.path.isabs(start_path_str):
            start_path = Path(start_path_str)
        else:
            start_path = settings.SOURCE_DIR / start_path_str
            
        if not start_path.exists():
            self.logger.error(f"Path not found: {start_path}")
            return []

        projects = []
        
        def is_project(p):
            # Check for STEP 2 folder
            if (p / "STEP 2").exists() or (p / "Step 2").exists():
                return True
            # Check for docx files (excluding temp files)
            has_files = any(f for f in p.glob("*.docx") if not f.name.startswith("~$"))
            return has_files

        if is_project(start_path):
            projects.append(start_path)
        else:
            # Check subdirectories
            self.logger.info(f"Checking subdirectories of {start_path} for projects...")
            for child in start_path.iterdir():
                if child.is_dir() and is_project(child):
                    projects.append(child)
                    
        return projects
    
    def clear_log(self):
        """Clear the log display"""
        self.log_display.delete(1.0, tk.END)
    
    def save_log(self):
        """Save log contents to file"""
        log_content = self.log_display.get(1.0, tk.END)
        if not log_content.strip():
            messagebox.showwarning("Warning", "No log content to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Log File",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialname=f"airtable_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                messagebox.showinfo("Success", f"Log saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {str(e)}")
    
    def configure_airtable(self):
        """Open Airtable configuration dialog"""
        AirtableConfigDialog(self.root, self)
    
    def show_settings(self):
        """Show current settings"""
        settings_text = f"""Current Settings:

Source Directory: {settings.SOURCE_DIR}
Log Directory: {settings.LOG_DIR}
Data Directory: {settings.DATA_DIR}

Airtable Configuration:
- API Token: {'Configured' if settings.AIRTABLE_CONFIG.get('api_token') else 'Not configured'}
- Base ID: {'Configured' if settings.AIRTABLE_CONFIG.get('base_id') else 'Not configured'}

Tables:
- Lenses: {settings.AIRTABLE_CONFIG['tables']['lenses']}
- Sources: {settings.AIRTABLE_CONFIG['tables']['sources']}
- Metas: {settings.AIRTABLE_CONFIG['tables']['metas']}
- Patterns: {settings.AIRTABLE_CONFIG['tables']['patterns']}
- Variations: {settings.AIRTABLE_CONFIG['tables']['variations']}
"""
        SettingsDialog(self.root, "Current Settings", settings_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """🚀 Airtable Scraper Pro v2.0

Professional Document Processing & Data Synchronization Suite

✨ Key Features:
• Advanced DOCX document parsing and extraction
• Intelligent pattern and variation detection
• Smart project folder auto-detection
• Real-time Airtable synchronization
• Relationship linking and data integrity
• Professional user interface with tooltips
• Comprehensive error handling and recovery
• Background processing with progress tracking

🎯 Data Types Supported:
• Lenses - Conceptual frameworks and perspectives
• Sources - Reference materials and citations  
• Metas - Document metadata and information
• Patterns - Core structural patterns
• Variations - Pattern implementations and examples

🔧 Technical Specifications:
• Built with Python and tkinter
• Multi-threaded processing architecture
• Robust API error handling
• Field existence validation
• Automatic duplicate prevention

© 2025 - Developed for professional document workflow management
"""
        SettingsDialog(self.root, "About Airtable Scraper Pro", about_text)
    
    def show_usage_guide(self):
        """Show usage guide"""
        guide_text = """Usage Guide:

1. Project Folder Selection:
   - Enter folder name (relative to source directory) or absolute path
   - Use Browse button to select folder visually
   - Tool auto-detects project folders containing DOCX files or "STEP 2" folders

2. Operation Mode:
   - Extract and Sync: Process data and upload to Airtable (default)
   - Extract Only: Process data but skip Airtable upload

3. Data Types:
   - Select which data types to process
   - Variations automatically include Patterns for proper linking
   - Use Select/Deselect All for quick selection

4. Sync Options:
   - Enable relationship linking to connect related records in Airtable

5. Processing:
   - Click Start Processing to begin
   - Monitor progress in the log display
   - Use Stop button to cancel if needed

6. Configuration:
   - Configure Airtable credentials via Settings menu
   - Credentials stored in .env file in project root

Tips:
- Ensure DOCX files are properly formatted with expected patterns
- Check log output for detailed processing information
- Save logs for troubleshooting if needed
"""
        SettingsDialog(self.root, "Usage Guide", guide_text)


class AirtableConfigDialog:
    """Dialog for configuring Airtable credentials"""
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configure Airtable")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.api_token = tk.StringVar(value=settings.AIRTABLE_CONFIG.get("api_token", ""))
        self.base_id = tk.StringVar(value=settings.AIRTABLE_CONFIG.get("base_id", ""))
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Airtable Configuration", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # API Token
        ttk.Label(main_frame, text="API Token:").pack(anchor=tk.W)
        api_entry = ttk.Entry(main_frame, textvariable=self.api_token, width=60, show="*")
        api_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Base ID
        ttk.Label(main_frame, text="Base ID:").pack(anchor=tk.W)
        base_entry = ttk.Entry(main_frame, textvariable=self.base_id, width=60)
        base_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                               text="Get your API token from: https://airtable.com/developers/web/api/introduction\n"
                                    "Find your Base ID in the Airtable API documentation for your base.",
                               font=("Arial", 9), foreground="gray")
        instructions.pack(pady=20, fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Save", 
                  command=self.save_config).pack(side=tk.RIGHT)
    
    def save_config(self):
        """Save Airtable configuration to .env file"""
        api_token = self.api_token.get().strip()
        base_id = self.base_id.get().strip()
        
        if not api_token or not base_id:
            messagebox.showerror("Error", "Please enter both API token and Base ID.")
            return
        
        try:
            env_path = settings.BASE_DIR.parent / ".env"
            
            # Read existing .env content
            env_lines = []
            if env_path.exists():
                with open(env_path, 'r') as f:
                    env_lines = f.readlines()
            
            # Update or add the configuration
            updated_lines = []
            found_token = False
            found_base = False
            
            for line in env_lines:
                if line.startswith("AIRTABLE_API_TOKEN="):
                    updated_lines.append(f"AIRTABLE_API_TOKEN={api_token}\n")
                    found_token = True
                elif line.startswith("AIRTABLE_BASE_ID="):
                    updated_lines.append(f"AIRTABLE_BASE_ID={base_id}\n")
                    found_base = True
                else:
                    updated_lines.append(line)
            
            # Add new entries if not found
            if not found_token:
                updated_lines.append(f"AIRTABLE_API_TOKEN={api_token}\n")
            if not found_base:
                updated_lines.append(f"AIRTABLE_BASE_ID={base_id}\n")
            
            # Write back to .env file
            with open(env_path, 'w') as f:
                f.writelines(updated_lines)
            
            # Update settings in memory
            os.environ["AIRTABLE_API_TOKEN"] = api_token
            os.environ["AIRTABLE_BASE_ID"] = base_id
            settings.AIRTABLE_CONFIG["api_token"] = api_token
            settings.AIRTABLE_CONFIG["base_id"] = base_id
            
            messagebox.showinfo("Success", "Airtable configuration saved successfully!")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")


class SettingsDialog:
    """Simple dialog for displaying text information"""
    def __init__(self, parent, title, text):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Text display
        text_widget = scrolledtext.ScrolledText(self.dialog, wrap=tk.WORD, 
                                               font=("Arial", 10), padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(self.dialog, text="Close", 
                  command=self.dialog.destroy).pack(pady=(0, 10))


def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    
    # Set up professional ttk styling
    style = ttk.Style()
    
    # Try to use a modern theme
    available_themes = style.theme_names()
    if 'vista' in available_themes:
        style.theme_use('vista')
    elif 'winnative' in available_themes:
        style.theme_use('winnative')
    elif 'clam' in available_themes:
        style.theme_use('clam')
    
    # Configure custom professional styles for better visibility
    try:
        style.configure('Accent.TButton', 
                       font=('Segoe UI', 11, 'bold'),
                       foreground='white',
                       background='#0078d4',
                       relief='raised')
        
        style.configure('Start.TButton', 
                       font=('Segoe UI', 11, 'bold'),
                       foreground='black',
                       background='#28a745',
                       relief='raised',
                       borderwidth=2)
        
        # Map styles for different button states
        style.map('Start.TButton',
                 background=[('active', '#1e7e34'),
                            ('pressed', '#155724')])
    except Exception:
        # Fallback for platforms where advanced styling doesn't work
        pass
    
    # Configure labelframe styling
    style.configure('TLabelframe.Label', font=('Segoe UI', 9, 'bold'))
    style.configure('TLabelframe', padding=8)
    
    # Configure other elements for better readability
    style.configure('TLabel', font=('Segoe UI', 9))
    style.configure('TCheckbutton', font=('Segoe UI', 9))
    style.configure('TRadiobutton', font=('Segoe UI', 9))
    style.configure('TButton', font=('Segoe UI', 9))
    
    app = AirtableScraperGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.is_processing:
            result = messagebox.askyesno(
                "Confirm Exit", 
                "Processing is still running. Are you sure you want to exit?"
            )
            if not result:
                return
        root.quit()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()