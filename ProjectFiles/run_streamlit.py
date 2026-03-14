#!/usr/bin/env python3
"""
Streamlit runner for EducatorAI
Simple script to launch the Streamlit application
"""

import subprocess
import sys
import os

def check_streamlit():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_streamlit():
    """Install Streamlit if not present"""
    print("Installing Streamlit...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    print("Streamlit installed successfully!")

def run_streamlit():
    """Run the Streamlit application"""
    if not check_streamlit():
        install_streamlit()
    
    print("Starting EducatorAI Streamlit application...")
    print("Open your browser to: http://localhost:8501")
    
    # Run Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])

if __name__ == "__main__":
    run_streamlit()