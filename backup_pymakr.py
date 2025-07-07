#!/usr/bin/env python3
"""
Script to find and backup Pymakr extension
"""

import os
import shutil
import json
from pathlib import Path

def find_pymakr_extension():
    """Find Pymakr extension directory"""
    
    # VS Code extensions path
    vscode_extensions = Path.home() / ".vscode" / "extensions"
    
    if not vscode_extensions.exists():
        print("❌ VS Code extensions directory not found!")
        return None
    
    # Find Pymakr extension
    pymakr_dirs = list(vscode_extensions.glob("pycom.pymakr*"))
    
    if not pymakr_dirs:
        print("❌ Pymakr extension not found!")
        return None
    
    # Get the latest version if multiple found
    pymakr_dir = sorted(pymakr_dirs)[-1]
    
    print(f"✅ Found Pymakr extension: {pymakr_dir}")
    
    # Check package.json for version info
    package_json = pymakr_dir / "package.json"
    if package_json.exists():
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                version = data.get('version', 'unknown')
                print(f"📦 Version: {version}")
        except Exception as e:
            print(f"⚠️ Could not read version: {e}")
    
    return pymakr_dir

def backup_pymakr(pymakr_dir, backup_path):
    """Backup Pymakr extension"""
    
    backup_dir = Path(backup_path) / "pymakr_backup"
    
    try:
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        
        shutil.copytree(pymakr_dir, backup_dir)
        print(f"✅ Backup completed: {backup_dir}")
        
        # Create installation instructions
        instructions = backup_dir / "INSTALLATION_INSTRUCTIONS.txt"
        with open(instructions, 'w', encoding='utf-8') as f:
            f.write("""
PYMAKR EXTENSION INSTALLATION INSTRUCTIONS
==========================================

1. Close VS Code completely

2. Find VS Code extensions directory on target machine:
   - Windows: C:\\Users\\[username]\\.vscode\\extensions\\
   - macOS: ~/.vscode/extensions/
   - Linux: ~/.vscode/extensions/

3. Copy the pymakr extension folder to extensions directory:
   - Copy entire folder: pycom.pymakr-[version]
   - Make sure folder permissions are correct

4. Restart VS Code

5. Check if Pymakr appears in Extensions list

Alternative Installation:
- Use VS Code marketplace: Ctrl+Shift+X → Search "Pymakr"
- Or download .vsix file from: https://marketplace.visualstudio.com/items?itemName=pycom.Pymakr

Troubleshooting:
- If extension doesn't load, try reinstalling from marketplace
- Check VS Code version compatibility
- Ensure Python is properly installed on target machine
""")
        
        print(f"📝 Installation instructions: {instructions}")
        return backup_dir
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def main():
    print("🔍 Searching for Pymakr extension...")
    
    pymakr_dir = find_pymakr_extension()
    if not pymakr_dir:
        return
    
    # Create backup on Desktop
    desktop = Path.home() / "Desktop"
    backup_path = desktop
    
    print(f"\n📁 Creating backup at: {backup_path}")
    backup_dir = backup_pymakr(pymakr_dir, backup_path)
    
    if backup_dir:
        print(f"\n🎉 Pymakr extension backup completed!")
        print(f"📂 Backup location: {backup_dir}")
        print(f"📋 Size: {sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    main()
