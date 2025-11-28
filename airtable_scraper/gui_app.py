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
        self.root.title("Airtable Scraper - GUI Interface")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize variables
        self.project_folder = tk.StringVar(value="BIOME")
        self.extract_only = tk.BooleanVar(value=False)
        self.enable_sync = tk.BooleanVar(value=True)
        
        # Data type variables
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
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Airtable Scraper", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Project Folder Selection
        ttk.Label(main_frame, text="Project Folder:", 
                 font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.project_folder, 
                                     font=("Arial", 10))
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(folder_frame, text="Browse", 
                  command=self.browse_folder).grid(row=0, column=1)
        
        # Operation Mode
        mode_frame = ttk.LabelFrame(main_frame, text="Operation Mode", padding="5")
        mode_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        mode_frame.columnconfigure(0, weight=1)
        
        ttk.Radiobutton(mode_frame, text="Extract and Sync to Airtable (Default)", 
                       variable=self.extract_only, value=False).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(mode_frame, text="Extract Only (Skip Airtable Sync)", 
                       variable=self.extract_only, value=True).grid(row=1, column=0, sticky=tk.W)
        
        # Data Types Selection
        sync_frame = ttk.LabelFrame(main_frame, text="Data Types to Process", padding="5")
        sync_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Create two columns for checkboxes
        left_col = ttk.Frame(sync_frame)
        left_col.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 20))
        right_col = ttk.Frame(sync_frame)
        right_col.grid(row=0, column=1, sticky=(tk.W, tk.N))
        
        ttk.Checkbutton(left_col, text="Lenses", 
                       variable=self.sync_lenses).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(left_col, text="Sources", 
                       variable=self.sync_sources).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(left_col, text="Metas", 
                       variable=self.sync_metas).grid(row=2, column=0, sticky=tk.W)
        
        ttk.Checkbutton(right_col, text="Patterns", 
                       variable=self.sync_patterns).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(right_col, text="Variations", 
                       variable=self.sync_variations).grid(row=1, column=0, sticky=tk.W)
        
        # Selection buttons
        button_frame = ttk.Frame(sync_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Select All", 
                  command=self.select_all_types).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Deselect All", 
                  command=self.deselect_all_types).grid(row=0, column=1, padx=(5, 0))
        
        # Sync Options
        options_frame = ttk.LabelFrame(main_frame, text="Sync Options", padding="5")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Checkbutton(options_frame, text="Enable relationship linking (--sync)", 
                       variable=self.enable_sync).grid(row=0, column=0, sticky=tk.W)
        
        # Action Buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(action_frame, text="Start Processing", 
                                      command=self.start_processing, 
                                      style="Accent.TButton")
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(action_frame, text="Stop", 
                                     command=self.stop_processing, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(10, 0))
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(60, 0))
        
        # Log Display
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_display = scrolledtext.ScrolledText(log_frame, height=15, width=80, 
                                                    font=("Consolas", 9))
        self.log_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Menu Bar
        self.create_menu()
        
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
        self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create our custom handler
        handler = LogHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', 
                                    datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def check_log_queue(self):
        """Check for new log messages and display them"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_display.insert(tk.END, message + "\n")
                self.log_display.see(tk.END)
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
        self.sync_lenses.set(True)
        self.sync_sources.set(True)
        self.sync_metas.set(True)
        self.sync_patterns.set(True)
        self.sync_variations.set(True)
    
    def deselect_all_types(self):
        """Deselect all data types"""
        self.sync_lenses.set(False)
        self.sync_sources.set(False)
        self.sync_metas.set(False)
        self.sync_patterns.set(False)
        self.sync_variations.set(False)
    
    def get_selected_sync_types(self):
        """Get list of selected sync types"""
        sync_types = []
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
        self.status_var.set("Processing...")
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
        self.status_var.set("Stopped")
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
        self.status_var.set("Complete")
    
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
        about_text = """Airtable Scraper GUI v1.0

A comprehensive tool for extracting data from DOCX files and syncing to Airtable.

Features:
- Extract patterns, variations, sources, lenses, and metas from DOCX files
- Intelligent project folder detection
- Selective data type processing
- Airtable synchronization with relationship linking
- Extract-only mode for offline processing
- Comprehensive logging and error handling

Developed for processing structured documents and managing data workflows.
"""
        SettingsDialog(self.root, "About Airtable Scraper", about_text)
    
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
    
    # Set up ttk style
    style = ttk.Style()
    
    # Try to use a modern theme if available
    available_themes = style.theme_names()
    if 'winnative' in available_themes:
        style.theme_use('winnative')
    elif 'clam' in available_themes:
        style.theme_use('clam')
    
    # Configure custom styles
    style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
    
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