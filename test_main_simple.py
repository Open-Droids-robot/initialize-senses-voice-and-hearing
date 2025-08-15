#!/usr/bin/env python3
"""
Simplified test of main application without voice input.
"""

import sys
import time
import asyncio
sys.path.insert(0, 'src')

from config import Config
from persona import RobotPersona
from robot_state import RobotState
from conversation_graph import ConversationGraph
from control import TerminalControl

def test_main_simple():
    """Test main application without voice handler."""
    print("🤖 Testing SPARK Robot Assistant (Simplified)")
    print("=" * 50)
    
    try:
        # Initialize components
        print("📝 Initializing robot persona...")
        persona = RobotPersona()
        
        print("💾 Initializing state management...")
        robot_state = RobotState()
        
        print("🔄 Initializing conversation workflow...")
        conversation_graph = ConversationGraph(robot_state, persona)
        
        print("⌨️  Initializing terminal control...")
        terminal_control = TerminalControl(robot_state)
        
        print("✅ Initialization complete! *beep* *whirr*")
        
        # Start terminal control
        terminal_control.start()
        
        print("\n🚀 SPARK Robot Assistant Ready!")
        print("Press SPACE to pause/unpause, 'h' for help, 'q' to quit")
        print("=" * 50)
        
        # Simple main loop
        count = 0
        while True:
            try:
                # Show status
                stats = robot_state.get_stats()
                status = "PAUSED" if stats['is_paused'] else "ACTIVE"
                print(f"\r[Status] {status} | Battery: {stats['battery_level']:.1f}% | Count: {count}", end="")
                
                count += 1
                time.sleep(0.1)  # Very responsive
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupt received, shutting down...")
                break
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'terminal_control' in locals():
            terminal_control.stop()
        print("\n✅ Test completed!")

if __name__ == "__main__":
    test_main_simple()
