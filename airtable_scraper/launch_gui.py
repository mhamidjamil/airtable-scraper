#!/usr/bin/env python3
"""
Simple launcher for the Airtable Scraper GUI
"""

import sys
import subprocess
from pathlib import Path

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.resolve()
    gui_script = script_dir / "gui_app.py"
    
    if not gui_script.exists():
        print(f"ERROR: GUI script not found at {gui_script}")
        return 1
    
    try:
        # Launch the GUI application
        subprocess.run([sys.executable, str(gui_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to launch GUI application: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
        return 0

if __name__ == "__main__":
    sys.exit(main())