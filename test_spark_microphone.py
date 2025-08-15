#!/usr/bin/env python3
"""
Test if SPARK can hear microphone input.
"""

import sys
import time
import asyncio
sys.path.insert(0, 'src')

from config import Config
from persona import RobotPersona
from robot_state import RobotState
from conversation_graph import ConversationGraph
from voice_handler import VoiceHandler
from control import TerminalControl

def test_spark_microphone():
    """Test SPARK with real microphone input."""
    print("🎤 Testing SPARK with Real Microphone Input")
    print("=" * 60)
    
    try:
        # Initialize components
        print("📝 Initializing SPARK...")
        persona = RobotPersona()
        robot_state = RobotState()
        conversation_graph = ConversationGraph(robot_state, persona)
        voice_handler = VoiceHandler()
        terminal_control = TerminalControl(robot_state)
        
        # Set up connections
        voice_handler.set_robot_state(robot_state)
        robot_state.register_voice_handler(voice_handler)
        
        # Set up speech callback
        def on_speech_recognized(text: str):
            """Callback for when speech is recognized."""
            try:
                print(f"\n🎤 Speech recognized: '{text}'")
                
                # Run conversation workflow
                asyncio.run(conversation_graph.run_conversation(text))
                
            except Exception as e:
                print(f"❌ Error processing speech: {e}")
                robot_state.mark_interaction_failure(f"Speech processing error: {e}")
        
        voice_handler.set_callback(on_speech_recognized)
        
        print("✅ SPARK initialized successfully! *beep* *whirr*")
        
        # Start terminal control
        terminal_control.start()
        
        print("\n🎤 Starting voice handler...")
        voice_handler.start_listening()
        
        print("\n🚀 SPARK is now listening for your voice!")
        print("🎯 Try saying: 'Hello SPARK' or 'What's your name?'")
        print("⌨️  Press SPACE to pause/unpause, 'q' to quit")
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
                time.sleep(0.1)
                
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
    test_spark_microphone()
