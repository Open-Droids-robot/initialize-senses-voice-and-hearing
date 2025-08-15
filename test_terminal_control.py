#!/usr/bin/env python3
"""
Test script to check if terminal control is working properly.
"""

import sys
import time
import threading
import sys
sys.path.insert(0, 'src')
from control import TerminalControl
from robot_state import RobotState

def test_terminal_control():
    """Test terminal control functionality."""
    print("Testing terminal control...")
    
    # Create robot state and terminal control
    robot_state = RobotState()
    terminal_control = TerminalControl(robot_state)
    
    # Start terminal control
    terminal_control.start()
    
    print("Terminal control started!")
    print("Press SPACE to pause, 's' for status, 'h' for help, 'q' to quit")
    print("=" * 60)
    
    try:
        # Keep the main thread alive
        count = 0
        while True:
            # Show current status
            stats = robot_state.get_stats()
            status = "PAUSED" if stats['is_paused'] else "ACTIVE"
            print(f"\rStatus: {status} | Battery: {stats['battery_level']:.1f}% | Count: {count}", end="")
            
            count += 1
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        terminal_control.stop()
        print("Terminal control stopped")

if __name__ == "__main__":
    test_terminal_control()
