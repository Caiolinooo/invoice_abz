#!/usr/bin/env python3
"""
Script para configurar git e fazer commits
"""

import subprocess
import os
import sys

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
    
    # Check git version
    print("\n=== Checking Git ===")
    run_command("git --version", cwd)
    
    # Check git status
    print("\n=== Git Status ===")
    run_command("git status", cwd)
    
    # Check if we have staged files
    print("\n=== Staged Files ===")
    run_command("git diff --cached --name-only", cwd)
    
    # Add all files
    print("\n=== Adding Files ===")
    run_command("git add -A", cwd)
    
    # Check staged files again
    print("\n=== Staged Files After Add ===")
    run_command("git diff --cached --name-only", cwd)
    
    # Try to commit
    print("\n=== Committing ===")
    commit_msg = """feat: Release v2.0.0 - Template-Based Invoice System

🎉 Major Release - Complete Template-Based Invoice System

Features:
- Template-based invoice generation using Template_Invoice_Geral.xlsx
- Call-off integration in header (C14) and service descriptions  
- Standardized filename generation with employee names
- Professional layout with preserved formatting and borders
- Single-page optimization for A4 printing

Technical Implementation:
- Complete template copying preserving images and formatting
- Robust merged cell handling for complex Excel structures
- Service table with 4 groups of merged cells
- Comprehensive error handling and validation

Documentation:
- Complete README with installation and usage guide
- Detailed CHANGELOG with version history
- Roadmap for future versions"""
    
    run_command(f'git commit -m "{commit_msg}"', cwd)
    
    # Check log
    print("\n=== Git Log ===")
    run_command("git log --oneline -5", cwd)
    
    # Set up remote
    print("\n=== Setting up Remote ===")
    run_command("git remote add origin https://github.com/Caiolinooo/invoice_abz.git", cwd)
    
    # Check remotes
    print("\n=== Remotes ===")
    run_command("git remote -v", cwd)

if __name__ == "__main__":
    main()
