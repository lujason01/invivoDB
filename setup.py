#!/usr/bin/env python3
"""
InvivoDB Setup Script

This script sets up the InvivoDB environment by installing all required dependencies.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up InvivoDB Environment")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("\n⚠️  Some dependencies failed to install. You may need to install them manually.")
        print("   Try running: pip install -r requirements.txt")
    
    # Create directories if they don't exist
    directories = [
        "src/instance",
        "src/web/static/uploads",
        "logs"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed!")
    print("\nTo start the application:")
    print("   cd src/web")
    print("   python app.py")
    print("\nThen visit: http://localhost:5000")
    print("API Documentation: http://localhost:5000/api/v1/docs/")

if __name__ == "__main__":
    main()
