#!/usr/bin/env python3
"""
SPARK Robot Assistant - Feature Demo Script
Showcases all available features and capabilities.
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

def demo_spark_features():
    """Demonstrate all SPARK features."""
    print("🤖 SPARK Robot Assistant - Feature Demo")
    print("=" * 60)
    
    try:
        # Initialize all components
        print("📝 Initializing SPARK...")
        persona = RobotPersona()
        robot_state = RobotState()
        conversation_graph = ConversationGraph(robot_state, persona)
        voice_handler = VoiceHandler()
        terminal_control = TerminalControl(robot_state)
        
        # Set up connections
        voice_handler.set_robot_state(robot_state)
        robot_state.register_voice_handler(voice_handler)
        
        print("✅ SPARK initialized successfully! *beep* *whirr*")
        
        # Demo 1: Show SPARK's personality
        print("\n🎭 Demo 1: SPARK's Personality")
        print("-" * 40)
        print(f"🤖 Name: {persona.name}")
        print(f"💭 Sarcasm Level: {persona.personality_traits['sarcasm_level']}")
        print(f"🎯 Quirks: {', '.join(persona.quirks[:3])}")
        print(f"😄 Current Mood: {robot_state.mood.current_mood}")
        
        # Demo 2: Show configuration
        print("\n⚙️  Demo 2: System Configuration")
        print("-" * 40)
        Config.print_config()
        
        # Demo 3: Test conversation workflow
        print("\n💬 Demo 3: Conversation Workflow")
        print("-" * 40)
        test_inputs = [
            "Hello, who are you?",
            "Tell me a tech joke",
            "What's your mood today?",
            "How's your battery?"
        ]
        
        for i, test_input in enumerate(test_inputs, 1):
            print(f"\n--- Test {i}: '{test_input}' ---")
            try:
                asyncio.run(conversation_graph.run_conversation(test_input))
                time.sleep(1)
            except Exception as e:
                print(f"❌ Test failed: {e}")
        
        # Demo 4: Show system status
        print("\n📊 Demo 4: System Status")
        print("-" * 40)
        stats = robot_state.get_stats()
        print(f"🕐 Uptime: {stats['uptime_formatted']}")
        print(f"🔋 Battery: {stats['battery_level']:.1f}%")
        print(f"💬 Total Interactions: {stats['total_interactions']}")
        print(f"✅ Success Rate: {stats['success_rate']:.1f}%")
        print(f"⚡ Avg Response Time: {stats['avg_response_time']:.3f}s")
        
        # Demo 5: Show conversation history
        print("\n📚 Demo 5: Recent Conversations")
        print("-" * 40)
        conversations = robot_state.get_recent_conversations(3)
        if conversations:
            for i, conv in enumerate(conversations, 1):
                timestamp = conv['timestamp'][:19]
                user_input = conv['user_input'][:40]
                if len(conv['user_input']) > 40:
                    user_input += "..."
                print(f"{i}. [{timestamp}] User: {user_input}")
        else:
            print("No conversations yet.")
        
        # Demo 6: Show available controls
        print("\n🎮 Demo 6: Available Terminal Controls")
        print("-" * 40)
        print("SPACE - Pause/Unpause voice processing")
        print("q     - Quit application")
        print("r     - Reset conversation state")
        print("s     - Show current status/stats")
        print("m     - Toggle mute mode")
        print("h     - Show help")
        print("c     - Show configuration")
        print("l     - List recent conversations")
        print("b     - Show battery status")
        print("e     - Show recent errors")
        print("t     - Test conversation workflow")
        print("v     - Test voice synthesis")
        
        # Demo 7: Interactive mode
        print("\n🎯 Demo 7: Interactive Mode")
        print("-" * 40)
        print("Starting terminal control for interactive testing...")
        print("Press SPACE to pause, 'h' for help, 'q' to quit")
        print("=" * 60)
        
        # Start terminal control
        terminal_control.start()
        
        # Interactive loop
        count = 0
        while True:
            try:
                # Show live status
                stats = robot_state.get_stats()
                status = "PAUSED" if stats['is_paused'] else "ACTIVE"
                voice_status = "VOICE ON" if voice_handler.is_listening else "VOICE OFF"
                print(f"\r[Live] {status} | {voice_status} | Battery: {stats['battery_level']:.1f}% | Count: {count}", end="")
                
                count += 1
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Demo interrupted by user")
                break
                
    except Exception as e:
        print(f"❌ Demo error: {e}")
    finally:
        if 'terminal_control' in locals():
            terminal_control.stop()
        if 'voice_handler' in locals():
            voice_handler.stop_listening()
        print("\n🎉 Feature demo completed!")
        print("SPARK is ready for action! 🤖✨")

if __name__ == "__main__":
    demo_spark_features()
