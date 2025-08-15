#!/usr/bin/env python3
"""
Safe test script for SPARK Robot Assistant with timeout protection.
"""

import sys
import time
import threading
import signal
sys.path.insert(0, 'src')

from config import Config
from persona import RobotPersona
from robot_state import RobotState
from conversation_graph import ConversationGraph
from voice_handler import VoiceHandler
from control import TerminalControl

class SafeSPARKTest:
    """Safe test class with timeout protection."""
    
    def __init__(self):
        self.running = False
        self.voice_handler = None
        self.terminal_control = None
        
    def signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        print(f"\n⚠️  Signal {signum} received, shutting down safely...")
        self.shutdown()
        sys.exit(0)
    
    def shutdown(self):
        """Safely shutdown all components."""
        print("[Safe] Shutting down SPARK safely...")
        self.running = False
        
        if self.terminal_control:
            self.terminal_control.stop()
            print("[Safe] Terminal control stopped")
        
        if self.voice_handler:
            self.voice_handler.stop_listening()
            print("[Safe] Voice handler stopped")
        
        print("[Safe] Shutdown complete")
    
    def test_speech_callback(self, text: str):
        """Test callback for speech recognition with timeout protection."""
        try:
            print(f"\n🎤 Speech recognized: '{text}'")
            
            # Set a timeout for the entire conversation
            import asyncio
            import concurrent.futures
            
            # Run conversation with timeout
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.conversation_graph.run_conversation(text))
                try:
                    future.result(timeout=30)  # 30 second timeout
                    print("[Safe] Conversation completed successfully")
                except concurrent.futures.TimeoutError:
                    print("[Safe] Conversation timed out - stopping")
                    future.cancel()
                    
        except Exception as e:
            print(f"❌ Error processing speech: {e}")
            if self.robot_state:
                self.robot_state.mark_interaction_failure(f"Speech processing error: {e}")
    
    def run_safe_test(self):
        """Run the safe test with all protections."""
        print("🤖 Safe SPARK Robot Assistant Test")
        print("=" * 50)
        print("This test includes timeout protection and safe shutdown.")
        print("Press Ctrl+C to stop safely at any time.")
        print()
        
        try:
            # Set up signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # Initialize components
            print("📝 Initializing SPARK safely...")
            self.persona = RobotPersona()
            self.robot_state = RobotState()
            self.conversation_graph = ConversationGraph(self.robot_state, self.persona)
            self.voice_handler = VoiceHandler()
            self.terminal_control = TerminalControl(self.robot_state)
            
            # Set up connections
            self.voice_handler.set_robot_state(self.robot_state)
            self.robot_state.register_voice_handler(self.voice_handler)
            
            # Set up speech callback
            self.voice_handler.set_callback(self.test_speech_callback)
            
            print("✅ SPARK initialized successfully! *beep* *whirr*")
            
            # Start terminal control
            self.terminal_control.start()
            
            print("\n🎤 Starting voice handler with safety timeouts...")
            self.voice_handler.start_listening()
            
            print("\n🚀 SPARK is now listening safely!")
            print("🎯 Try saying: 'Hello SPARK' or 'What's your name?'")
            print("⌨️  Press SPACE to pause/unpause, 'q' to quit")
            print("⚠️  Press Ctrl+C to stop safely")
            print("=" * 60)
            
            # Main loop with safety checks
            self.running = True
            count = 0
            last_speech_check = time.time()
            
            while self.running:
                try:
                    # Show status
                    stats = self.robot_state.get_stats()
                    status = "PAUSED" if stats['is_paused'] else "ACTIVE"
                    voice_status = "VOICE ON" if self.voice_handler.is_listening else "VOICE OFF"
                    print(f"\r[Status] {status} | {voice_status} | Battery: {stats['battery_level']:.1f}% | Count: {count}", end="")
                    
                    count += 1
                    time.sleep(0.1)
                    
                    # Safety check: if no speech for 60 seconds, show reminder
                    if time.time() - last_speech_check > 60:
                        print(f"\n[Safe] No speech detected for 60s. Try saying something or press Ctrl+C to stop.")
                        last_speech_check = time.time()
                    
                    # Check if global quit command was received
                    if self.robot_state.should_quit:
                        print("\n[Global Control] Quit command received, shutting down...")
                        break
                        
                except KeyboardInterrupt:
                    print("\n\n⚠️  Interrupt received, shutting down safely...")
                    break
                except Exception as e:
                    print(f"\n❌ Error in main loop: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Critical error: {e}")
        finally:
            self.shutdown()
            print("\n✅ Safe test completed!")

def main():
    """Main function."""
    test = SafeSPARKTest()
    test.run_safe_test()

if __name__ == "__main__":
    main()
