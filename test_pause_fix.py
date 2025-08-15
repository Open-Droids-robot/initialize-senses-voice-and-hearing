#!/usr/bin/env python3
"""
Test script to verify pause functionality with fixed voice handler.
"""

import sys
import time
import threading
sys.path.insert(0, 'src')

from config import Config
from persona import RobotPersona
from robot_state import RobotState
from conversation_graph import ConversationGraph
from voice_handler import VoiceHandler
from control import TerminalControl

def test_pause_with_voice():
    """Test pause functionality with voice handler."""
    print("🤖 Testing SPARK Robot Assistant with Fixed Voice Handler")
    print("=" * 60)
    
    try:
        # Initialize components
        print("📝 Initializing robot persona...")
        persona = RobotPersona()
        
        print("💾 Initializing state management...")
        robot_state = RobotState()
        
        print("🔄 Initializing conversation workflow...")
        conversation_graph = ConversationGraph(robot_state, persona)
        
        print("🎤 Initializing voice handler...")
        voice_handler = VoiceHandler()
        
        print("⌨️  Initializing terminal control...")
        terminal_control = TerminalControl(robot_state)
        
        # Set up connections
        voice_handler.set_robot_state(robot_state)
        robot_state.register_voice_handler(voice_handler)
        
        print("✅ Initialization complete! *beep* *whirr*")
        
        # Start components
        terminal_control.start()
        voice_handler.start_listening()
        
        print("\n🚀 SPARK Robot Assistant Ready!")
        print("Press SPACE to pause/unpause, 'h' for help, 'q' to quit")
        print("Voice handler is running but should not block SPACE key!")
        print("=" * 60)
        
        # Main loop
        count = 0
        while True:
            try:
                # Show status
                stats = robot_state.get_stats()
                status = "PAUSED" if stats['is_paused'] else "ACTIVE"
                voice_status = "VOICE ON" if voice_handler.is_listening else "VOICE OFF"
                print(f"\r[Status] {status} | {voice_status} | Battery: {stats['battery_level']:.1f}% | Count: {count}", end="")
                
                count += 1
                time.sleep(0.1)  # Responsive
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupt received, shutting down...")
                break
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'terminal_control' in locals():
            terminal_control.stop()
        if 'voice_handler' in locals():
            voice_handler.stop_listening()
        print("\n✅ Test completed!")

if __name__ == "__main__":
    test_pause_with_voice()
