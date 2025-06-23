#!/usr/bin/env python3
"""
AI Agent Deployment Strategies - Directory Setup Script (Python)
This script creates the complete directory structure for the repository
Cross-platform compatible (Windows, macOS, Linux)
"""

import os
import sys
from pathlib import Path

def create_directory_structure():
    """Create the complete directory structure for AI Agent Deployment Strategies"""
    
    print("🚀 Creating AI Agent Deployment Strategies directory structure...")
    
    # Define the project structure
    project_name = "ai-agent-deployment-strategies"
    
    directories = [
        # GitHub directories
        ".github/workflows",
        ".github/ISSUE_TEMPLATE",
        
        # Documentation
        "docs",
        
        # Source code
        "src/assessment",
        "src/deployment", 
        "src/scaling",
        "src/monitoring",
        "src/security",
        "src/optimization",
        "src/utils",
        
        # Configuration
        "config/docker",
        "config/kubernetes",
        "config/ci-cd",
        "config/monitoring", 
        "config/environments",
        
        # Scripts
        "scripts",
        
        # Examples
        "examples/basic_deployment",
        "examples/advanced_deployment",
        "examples/monitoring_setup/dashboards",
        
        # Tests
        "tests/unit",
        "tests/integration", 
        "tests/performance",
        
        # Infrastructure as Code
        "terraform/aws",
        "terraform/gcp",
        "terraform/azure",
        
        # Tools
        "tools/migration",
        "tools/debugging",
        "tools/utilities"
    ]
    
    # Files to create
    initial_files = [
        "README.md",
        "LICENSE", 
        "requirements.txt",
        "setup.py",
        ".gitignore"
    ]
    
    # Python package __init__.py files
    python_packages = [
        "src/__init__.py",
        "src/assessment/__init__.py",
        "src/deployment/__init__.py",
        "src/scaling/__init__.py", 
        "src/monitoring/__init__.py",
        "src/security/__init__.py",
        "src/optimization/__init__.py",
        "src/utils/__init__.py",
        "tests/__init__.py"
    ]
    
    try:
        # Create main project directory
        project_path = Path(project_name)
        project_path.mkdir(exist_ok=True)
        os.chdir(project_path)
        
        print("📁 Creating directories...")
        # Create all directories
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"   ✓ {directory}")
        
        print("\n📄 Creating initial files...")
        # Create initial files
        for file_path in initial_files:
            Path(file_path).touch()
            print(f"   ✓ {file_path}")
        
        print("\n🐍 Creating Python package files...")
        # Create Python package files
        for package_file in python_packages:
            Path(package_file).touch()
            print(f"   ✓ {package_file}")
        
        print("\n✅ Directory structure created successfully!")
        print(f"\n📁 Project created at: {os.getcwd()}")
        
        # Display structure
        print("\n📋 Directory structure:")
        display_tree(Path("."), max_depth=3)
        
        print("\n🎉 Ready to start developing your AI Agent Deployment Strategies!")
        print("\nNext steps:")
        print("1. Initialize git repository: git init")
        print("2. Add your code files to the appropriate directories") 
        print("3. Update README.md with your project details")
        print("4. Create your first commit: git add . && git commit -m 'Initial project structure'")
        
    except Exception as e:
        print(f"❌ Error creating directory structure: {e}")
        sys.exit(1)

def display_tree(path, max_depth=3, current_depth=0, prefix=""):
    """Display directory tree structure"""
    if current_depth > max_depth:
        return
        
    items = sorted(path.iterdir())
    dirs = [item for item in items if item.is_dir() and not item.name.startswith('.git')]
    files = [item for item in items if item.is_file()]
    
    # Display directories first
    for i, directory in enumerate(dirs):
        is_last = (i == len(dirs) - 1) and len(files) == 0
        print(f"{prefix}{'└── ' if is_last else '├── '}{directory.name}/")
        
        next_prefix = prefix + ("    " if is_last else "│   ")
        display_tree(directory, max_depth, current_depth + 1, next_prefix)
    
    # Display files
    for i, file in enumerate(files[:5]):  # Show first 5 files only
        is_last = i == len(files) - 1
        print(f"{prefix}{'└── ' if is_last else '├── '}{file.name}")
    
    if len(files) > 5:
        print(f"{prefix}└── ... and {len(files) - 5} more files")

if __name__ == "__main__":
    create_directory_structure()