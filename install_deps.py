#!/usr/bin/env python3
"""
Dependency installation script for SPARK Robot Assistant.
Handles common installation issues and provides fallbacks.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} successful")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} crashed: {e}")
        return False

def install_package(package, description=None):
    """Install a single package."""
    if description is None:
        description = f"Installing {package}"
    
    return run_command(f"pip install {package}", description)

def main():
    """Main installation process."""
    print("🤖 SPARK Robot Assistant - Dependency Installation")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Upgrade pip first
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Pip upgrade failed, continuing anyway...")
    
    # Core packages (essential)
    core_packages = [
        "python-dotenv",
        "numpy",
        "langgraph",
        "openai",
        "elevenlabs"
    ]
    
    print("\n📦 Installing core packages...")
    core_success = 0
    for package in core_packages:
        if install_package(package):
            core_success += 1
        else:
            print(f"⚠️  {package} failed, will try alternative...")
    
    # Audio packages (may fail on some systems)
    audio_packages = [
        ("SpeechRecognition", "speech recognition"),
        ("pygame", "audio playback"),
        ("pydub", "audio processing")
    ]
    
    # Check if pyaudio is available via system package
    print("\n🔍 Checking system audio packages...")
    audio_success = 0
    try:
        import pyaudio
        print("✅ PyAudio available via system package")
        audio_success += 1
    except ImportError:
        print("⚠️  PyAudio not found, trying pip installation...")
        if install_package("pyaudio", "Installing audio I/O"):
            audio_success += 1
        else:
            print("⚠️  PyAudio installation failed - audio input may not work")
    
    print("\n🎤 Installing audio packages...")
    for package, description in audio_packages:
        if install_package(package, f"Installing {description}"):
            audio_success += 1
        else:
            print(f"⚠️  {package} failed - audio features may not work")
    
    # Development packages (optional)
    dev_packages = [
        "pytest",
        "pytest-asyncio"
    ]
    
    print("\n🧪 Installing development packages...")
    dev_success = 0
    for package in dev_packages:
        if install_package(package):
            dev_success += 1
        else:
            print(f"⚠️  {package} failed - testing features may not work")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Installation Summary:")
    print(f"   Core packages: {core_success}/{len(core_packages)}")
    print(f"   Audio packages: {audio_success}/{len(audio_packages)}")
    print(f"   Dev packages: {dev_success}/{len(dev_packages)}")
    
    if core_success == len(core_packages):
        print("🎉 Core functionality ready!")
        if audio_success >= 2:
            print("🎤 Audio features should work")
        else:
            print("⚠️  Limited audio support - some features may not work")
        
        print("\n🚀 You can now run the robot assistant:")
        print("   python src/main.py")
        return True
    else:
        print("❌ Critical packages missing - assistant may not work properly")
        print("\n💡 Try installing manually:")
        print("   pip install python-dotenv numpy langgraph openai elevenlabs")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
