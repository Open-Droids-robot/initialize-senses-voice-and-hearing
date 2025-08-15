#!/usr/bin/env python3
"""
Global Control Script for SPARK Robot Assistant
Allows controlling SPARK from any terminal using simple commands.
"""

import os
import sys
import time
import signal
from pathlib import Path

# Control file location
CONTROL_FILE = "data/spark_control.txt"
CONTROL_DIR = "data"

def ensure_control_dir():
    """Ensure the control directory exists."""
    Path(CONTROL_DIR).mkdir(exist_ok=True)

def send_command(command: str):
    """Send a command to SPARK via control file."""
    ensure_control_dir()
    
    try:
        with open(CONTROL_FILE, "w") as f:
            f.write(command)
            f.flush()
            os.fsync(f.fileno())  # Ensure it's written to disk
        
        print(f"✅ Command sent: {command}")
        return True
    except Exception as e:
        print(f"❌ Error sending command: {e}")
        return False

def check_status():
    """Check SPARK's current status."""
    ensure_control_dir()
    
    try:
        if os.path.exists(CONTROL_FILE):
            with open(CONTROL_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    print(f"📊 Current control command: {content}")
                else:
                    print("📊 No active control command")
        else:
            print("📊 No control file found - SPARK may not be running")
            
        # Check if SPARK is running
        import subprocess
        result = subprocess.run(['pgrep', '-f', 'python.*main.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("🟢 SPARK is running")
        else:
            print("🔴 SPARK is not running")
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")

def show_help():
    """Show help information."""
    print("🎮 SPARK Global Control Script")
    print("=" * 40)
    print("Usage: python control_spark.py <command>")
    print()
    print("Commands:")
    print("  pause     - Pause SPARK voice processing")
    print("  unpause   - Resume SPARK voice processing")
    print("  mute      - Mute SPARK audio output")
    print("  unmute    - Unmute SPARK audio output")
    print("  reset     - Reset SPARK conversation state")
    print("  quit      - Gracefully shut down SPARK")
    print("  status    - Check SPARK's current status")
    print("  help      - Show this help message")
    print()
    print("Examples:")
    print("  python control_spark.py pause")
    print("  python control_spark.py unpause")
    print("  python control_spark.py status")
    print()
    print("💡 You can control SPARK from ANY terminal using this script!")

def main():
    """Main control function."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    # Command mapping
    commands = {
        'pause': 'PAUSE',
        'unpause': 'UNPAUSE', 
        'resume': 'UNPAUSE',  # Alias
        'mute': 'MUTE',
        'unmute': 'UNMUTE',
        'reset': 'RESET',
        'quit': 'QUIT',
        'exit': 'QUIT',       # Alias
        'status': 'STATUS',
        'help': 'HELP'
    }
    
    if command in commands:
        if command == 'status':
            check_status()
        elif command == 'help':
            show_help()
        else:
            send_command(commands[command])
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python control_spark.py help' for available commands")

if __name__ == "__main__":
    main()
