#!/bin/bash
# Exit on any error
set -e

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run environment setup first."
    exit 1
fi

echo "Cleaning previous builds..."
rm -rf build/ dist/

echo "Building application with PyInstaller..."
pyinstaller --name "LinuxDesktopApp" \
            --onefile \
            --windowed \
            --clean \
            --paths src \
            --add-data "src/assets:assets" \
            src/main.py

echo "Build complete! Executable is located at dist/LinuxDesktopApp"
