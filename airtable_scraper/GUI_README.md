# Airtable Scraper GUI

A comprehensive graphical user interface for the Airtable Scraper project, providing an intuitive way to extract data from DOCX files and synchronize with Airtable.

## Features

### 🖥️ **User-Friendly Interface**
- Clean, modern GUI built with tkinter
- Real-time processing logs with syntax highlighting
- Progress indicators and status updates
- Responsive design that works on different screen sizes

### 📁 **Project Management**
- Browse and select project folders visually
- Auto-detection of project folders (containing DOCX files or "STEP 2" folders)
- Support for both relative and absolute paths
- Intelligent project structure recognition

### 🎯 **Selective Processing**
- Choose specific data types to process:
  - **Lenses**: Conceptual frameworks and perspectives
  - **Sources**: Reference materials and citations
  - **Metas**: Metadata and document information
  - **Patterns**: Core structural patterns
  - **Variations**: Pattern variations and implementations
- Select All/Deselect All for quick configuration
- Auto-inclusion of dependencies (e.g., patterns when processing variations)

### ⚙️ **Flexible Operation Modes**
- **Extract and Sync**: Full processing with Airtable upload (default)
- **Extract Only**: Process data without Airtable synchronization
- **Relationship Linking**: Optional connection of related records in Airtable

### 🔧 **Configuration Management**
- Built-in Airtable credentials configuration
- Automatic .env file management
- Settings validation and error handling
- View current configuration at any time

### 📊 **Comprehensive Logging**
- Real-time log display with scroll support
- Detailed processing information and error messages
- Save logs to file for troubleshooting
- Clear log functionality for fresh starts

## Quick Start

### Method 1: Double-click Launcher (Windows)
```bash
# Simply double-click launch_gui.bat
launch_gui.bat
```

### Method 2: Python Command
```bash
# Navigate to the airtable_scraper directory
cd E:\Work\shoaib\upwork\airtable_scraper

# Run the GUI application
python gui_app.py
```

### Method 3: Python Launcher
```bash
# Use the cross-platform launcher
python launch_gui.py
```

## Configuration

### First-Time Setup

1. **Launch the Application**: Use any of the methods above
2. **Configure Airtable** (if using sync mode):
   - Go to `Settings` → `Configure Airtable...`
   - Enter your Airtable API Token
   - Enter your Airtable Base ID
   - Click `Save`

3. **Select Project Folder**:
   - Enter folder name (relative to source directory) or use `Browse` button
   - Default source directory: `E:\Work\shoaib\upwork\new_extractions`

### Getting Airtable Credentials

1. **API Token**: 
   - Visit [Airtable Developers](https://airtable.com/developers/web/api/introduction)
   - Generate a personal access token
   - Ensure it has read/write permissions for your base

2. **Base ID**:
   - Open your Airtable base
   - Go to Help → API documentation
   - Find your Base ID in the URL or documentation

## Usage Guide

### Basic Workflow

1. **Select Project Folder**
   - Enter the folder name containing your DOCX files
   - Use relative paths (e.g., "BIOME", "BUSINESS") or absolute paths
   - Click `Browse` to select visually

2. **Choose Operation Mode**
   - **Extract and Sync**: Process and upload to Airtable (recommended)
   - **Extract Only**: Process without uploading (for testing/offline use)

3. **Select Data Types**
   - Check the data types you want to process
   - Use `Select All` for complete processing
   - Variations automatically include Patterns for proper linking

4. **Configure Sync Options**
   - Enable "relationship linking" to connect related records in Airtable
   - This creates proper relationships between patterns, variations, sources, etc.

5. **Start Processing**
   - Click `Start Processing` to begin
   - Monitor progress in the log display
   - Use `Stop` button if you need to cancel

### Advanced Features

#### Menu Options

- **File Menu**:
  - Open Project Folder: Quick folder selection
  - Clear Log: Clear the log display
  - Save Log: Export logs for troubleshooting

- **Settings Menu**:
  - Configure Airtable: Set up API credentials
  - View Current Settings: Check configuration

- **Help Menu**:
  - About: Application information
  - Usage Guide: Detailed usage instructions

#### Project Auto-Detection

The application automatically detects project folders by looking for:
- Folders containing `.docx` files (excluding temporary files starting with `~$`)
- Folders containing a "STEP 2" subfolder

If you specify a folder that contains multiple projects, it will process all of them sequentially.

## File Structure

```
airtable_scraper/
├── gui_app.py              # Main GUI application
├── launch_gui.bat          # Windows launcher
├── launch_gui.py           # Cross-platform launcher
├── main.py                 # Original command-line interface
├── config/
│   └── settings.py         # Configuration settings
├── modules/
│   ├── data_extractor.py   # Data extraction logic
│   └── airtable_uploader.py # Airtable synchronization
├── extraction_rules/       # Extraction rule engines
├── logs/                   # Processing logs
└── json_data/             # Extracted data files
```

## Troubleshooting

### Common Issues

1. **"Python is not installed"**
   - Install Python 3.7 or later
   - Ensure Python is added to your system PATH

2. **"Airtable credentials not configured"**
   - Use Settings → Configure Airtable to set up credentials
   - Check that your API token has the correct permissions

3. **"No valid project folders found"**
   - Verify the folder path exists
   - Ensure the folder contains .docx files or "STEP 2" subfolder
   - Try using the Browse button to select the folder

4. **Processing stops unexpectedly**
   - Check the log display for error messages
   - Save the log and review for detailed error information
   - Verify DOCX files are not corrupted or password-protected

### Getting Help

1. **Check the Log**: The log display shows detailed processing information and error messages
2. **Save Logs**: Use File → Save Log to export logs for analysis
3. **View Settings**: Use Settings → View Current Settings to verify configuration
4. **Usage Guide**: Access Help → Usage Guide for detailed instructions

## Technical Details

### Dependencies
- **tkinter**: GUI framework (included with Python)
- **threading**: Background processing
- **queue**: Thread-safe communication
- **pathlib**: Modern path handling
- All existing project dependencies (docx, requests, etc.)

### Performance
- Multi-threaded processing to keep GUI responsive
- Real-time log updates without blocking
- Efficient memory usage with streaming log display
- Progress indicators for long-running operations

### Compatibility
- Windows, macOS, Linux (tkinter is cross-platform)
- Python 3.7+
- Same document format requirements as the command-line version

## Command-Line Equivalent

The GUI provides the same functionality as running:

```bash
# GUI equivalent of:
python main.py --folder "BUSINESS" --sources --patterns --sync

# Is the same as:
# 1. Select folder: "BUSINESS"
# 2. Check: Sources, Patterns
# 3. Enable: relationship linking
# 4. Click: Start Processing
```

## Development Notes

The GUI application is designed to be:
- **User-friendly**: Intuitive interface for non-technical users
- **Comprehensive**: All command-line features available
- **Robust**: Proper error handling and validation
- **Maintainable**: Clean separation between GUI and business logic
- **Extensible**: Easy to add new features or modify existing ones

The original command-line interface (`main.py`) remains available and unchanged, providing both options for different use cases.