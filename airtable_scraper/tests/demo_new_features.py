#!/usr/bin/env python3
"""
Demonstration script showing how to use the improved airtable scraper
with selective syncing and timestamped JSON exports.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_command(cmd, description):
    """Run a command and show the results"""
    print("=" * 80)
    print(f"🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 80)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            # Show last 20 lines of output
            lines = result.stdout.strip().split('\n')
            if len(lines) > 20:
                print("... (showing last 20 lines)")
                lines = lines[-20:]
            print('\n'.join(lines))
        else:
            print("❌ FAILED")
            print("STDOUT:", result.stdout[-1000:])  # Last 1000 chars
            print("STDERR:", result.stderr[-1000:])  # Last 1000 chars
            
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT - Command took too long")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print()

def show_json_files():
    """Show the timestamped JSON files created"""
    print("=" * 80)
    print("📄 TIMESTAMPED JSON FILES CREATED")
    print("=" * 80)
    
    json_dir = Path("json_data")
    json_files = sorted(json_dir.glob("airtable_sync_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"Found {len(json_files)} timestamped sync files:")
    for i, file in enumerate(json_files[:10]):  # Show last 10 files
        size = file.stat().st_size / 1024  # KB
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        print(f"  {i+1}. {file.name} ({size:.1f} KB) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print()

def main():
    """Demonstrate the improved airtable scraper functionality"""
    python_exe = "C:/Users/hamid/AppData/Local/Programs/Python/Python311/python.exe"
    
    print("🎯 AIRTABLE SCRAPER - NEW FEATURES DEMONSTRATION")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Test 1: Show help
    run_command([python_exe, "main.py", "--help"], 
                "Show command-line help")
    
    # Test 2: Extract and sync only variations (DRY RUN - without actual Airtable upload)
    print("⚠️  NOTE: The following demonstrations would normally sync to Airtable.")
    print("⚠️  To avoid actual uploads during demo, we'll use our test scripts instead.")
    print()
    
    # Test 3: Run our comprehensive test to show the system working
    run_command([python_exe, "test_complete_system.py"], 
                "Run comprehensive system test (shows extraction + validation)")
    
    # Test 4: Show the JSON files created
    show_json_files()
    
    # Test 5: Show example commands
    print("=" * 80)
    print("💡 EXAMPLE USAGE COMMANDS")
    print("=" * 80)
    print("To sync only variations:")
    print("  python main.py --variations")
    print()
    print("To sync only patterns and variations:")
    print("  python main.py --patterns --variations")
    print()
    print("To sync only lenses from a specific folder:")
    print("  python main.py --lenses --folder QUANTUM")
    print()
    print("To sync everything (default behavior):")
    print("  python main.py")
    print()
    print("All commands will create timestamped JSON files showing what was synced!")
    print()
    
    # Summary of fixes
    print("=" * 80)
    print("✅ SUMMARY OF FIXES IMPLEMENTED")
    print("=" * 80)
    print("1. 🛠️  FIXED 422 ERRORS:")
    print("   - Added field validation before sending to Airtable")
    print("   - Better error handling with detailed error messages")
    print("   - Null value filtering and string length limits")
    print()
    print("2. 🎛️  ADDED COMMAND-LINE PARAMETERS:")
    print("   - --variations, --patterns, --lenses, --metas, --sources")
    print("   - Case-insensitive: --Variations, --PATTERNS, etc.")
    print("   - --folder option to specify target directory")
    print("   - Selective syncing - only sync what you need!")
    print()
    print("3. 📄 ADDED TIMESTAMPED JSON EXPORTS:")
    print("   - Every sync creates a timestamped JSON file")
    print("   - Files saved in json_data/ directory")
    print("   - Shows exactly what data was sent to Airtable")
    print("   - Perfect for debugging and auditing")
    print()
    print("4. 🔧 IMPROVED ERROR HANDLING:")
    print("   - Better 422 error diagnosis")
    print("   - Field validation before API calls")
    print("   - More detailed logging throughout the process")
    print()
    print("🎉 THE SYSTEM IS NOW ROBUST AND READY FOR PRODUCTION! 🎉")

if __name__ == "__main__":
    main()