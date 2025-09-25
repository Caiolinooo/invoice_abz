#!/usr/bin/env python3
"""
Script para fazer commit da versão 8.0 com fonte Calibri
"""

import subprocess
import os

def run_command(cmd, cwd=None):
    """Execute command and return result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            encoding='utf-8'
        )
        print(f"Command: {cmd}")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return result
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return None

def main():
    """Main function"""
    cwd = os.getcwd()
    print(f"Working directory: {cwd}")
    
    # Add all files
    print("\n=== Adding Files ===")
    run_command("git add .", cwd)
    
    # Commit with detailed message
    print("\n=== Committing V8.0 ===")
    commit_msg = """feat: Release v8.0.0 - Universal Calibri Font System

🔤 Typography Enhancement - Fonte Calibri Universal

Features:
- Universal Calibri font application across entire invoice
- Hierarchical typography with different Calibri sizes:
  * Title: Calibri 14pt Bold (A7)
  * Headers: Calibri 12pt Bold (C12, C13, C14)  
  * Table headers: Calibri 11pt Bold (line 16)
  * Content: Calibri 11pt (services, totals)
  * Corporate details: Calibri 10pt (lines 43-50)
- Maximum readability optimization for screen and print
- Professional corporate appearance consistency

Technical Implementation:
- Complete rewrite of _preserve_template_fonts() method
- Intelligent cell type detection for appropriate font sizing
- 100% Calibri compliance validation system
- Comprehensive test suite with test_calibri_fonts.py

Benefits:
- Superior readability with optimized digital/print font
- Visual consistency across entire invoice
- Professional Microsoft Office standard font
- Universal Windows compatibility

Documentation:
- Updated README with Typography section
- Enhanced CHANGELOG with v8.0.0 details
- Comprehensive font hierarchy documentation"""
    
    run_command(f'git commit -m "{commit_msg}"', cwd)
    
    # Check log
    print("\n=== Git Log ===")
    run_command("git log --oneline -3", cwd)

if __name__ == "__main__":
    main()
