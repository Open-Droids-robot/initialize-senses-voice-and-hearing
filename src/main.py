#!/usr/bin/env python3
"""
Robot Assistant - Main Entry Point
A witty robot persona assistant with voice interaction capabilities.
"""

import asyncio
import signal
import sys
import os
from typing import Optional

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from persona import RobotPersona
from robot_state import RobotState
from conversation_graph import ConversationGraph
from voice_handler import VoiceHandler
from control import TerminalControl

class RobotAssistant:
    """Main robot assistant application."""
    
    def __init__(self):
        self.robot_state = None
        self.persona = None
        self.conversation_graph = None
        self.voice_handler = None
        self.terminal_control = None
        self.is_running = False
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def initialize(self):
        """Initialize all components of the robot assistant."""
        try:
            print("🤖 Bringing systems online...")
            
            # Validate configuration
            config_issues = Config.validate()
            if config_issues:
                print("⚠️  Configuration warnings:")
                for issue in config_issues:
                    print(f"   - {issue}")
                print()
            
            # Initialize components
            print("📝 Initializing robot persona...")
            self.persona = RobotPersona()
            print(f"🤖 {self.persona.get_system_prompt('initializing')}")
            
            print("💾 Initializing state management...")
            self.robot_state = RobotState(max_history=Config.MAX_CONVERSATION_HISTORY)
            
            print("🔄 Initializing conversation workflow...")
            self.conversation_graph = ConversationGraph(self.robot_state, self.persona)
            
            print("🎤 Initializing voice handler...")
            self.voice_handler = VoiceHandler()
            
            print("⌨️  Initializing terminal control...")
            self.terminal_control = TerminalControl(self.robot_state)
            
            # Set up callbacks
            self._setup_callbacks()
            
            print("✅ Initialization complete!")
            return True
            
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            return False
    
    def _setup_callbacks(self):
        """Set up callback functions between components."""
        try:
            # Voice handler callback for speech recognition
            self.voice_handler.set_callback(self._on_speech_recognized)
            
            # Set robot state reference in voice handler
            self.voice_handler.set_robot_state(self.robot_state)
            
            # Terminal control custom commands
            self.terminal_control.register_callback('t', self._test_conversation)
            self.terminal_control.register_callback('v', self._test_voice)
            
        except Exception as e:
            print(f"⚠️  Warning: Some callbacks could not be set up: {e}")
    
    def start(self):
        """Start the robot assistant."""
        if self.is_running:
            print("⚠️  Robot assistant is already running")
            return
        
        try:
            print(f"\n🚀 {self.persona.get_system_prompt('starting', 'Starting assistant...')}")
            print("=" * 50)
            
            # Start terminal control
            self.terminal_control.start()
            
            # Start voice handler
            self.voice_handler.start_listening()
            
            # Register voice handler pause/resume with robot state
            self.robot_state.register_voice_handler(self.voice_handler)
            
            # Mark as running
            self.is_running = True
            
            # Show welcome message
            self._show_welcome()
            
            # Start main event loop
            self._main_loop()
            
        except Exception as e:
            print(f"❌ Error starting robot assistant: {e}")
            self.cleanup()
    
    def _main_loop(self):
        """Main event loop for the robot assistant."""
        try:
            print("\n🔄 Entering main event loop...")
            print("Press 'h' for help, 'q' to quit")
            
            # Non-blocking event loop
            while self.is_running:
                try:
                    # Check global controls from external terminals
                    self.robot_state.check_global_controls()
                    
                    # Check if system is paused
                    if self.robot_state.is_paused:
                        # Wait for unpause with shorter intervals for responsiveness
                        import time
                        time.sleep(0.1)
                        continue
                    
                    # Process any pending voice input
                    if hasattr(self.voice_handler, 'audio_queue') and not self.voice_handler.audio_queue.empty():
                        try:
                            audio_data = self.voice_handler.audio_queue.get_nowait()
                            # Process audio data if needed
                        except:
                            pass
                    
                    # Check if global quit command was received
                    if self.robot_state.should_quit:
                        print("\n[Global Control] Quit command received, shutting down...")
                        break
                    
                    # Very short delay to allow terminal control to process input
                    import time
                    time.sleep(0.01)  # 10ms instead of 100ms for better responsiveness
                    
                except KeyboardInterrupt:
                    print("\n⚠️  Interrupt received, shutting down...")
                    break
                except Exception as e:
                    print(f"⚠️  Error in main loop: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            print(f"❌ Critical error in main loop: {e}")
        finally:
            self.cleanup()
    
    def _on_speech_recognized(self, text: str):
        """Callback for when speech is recognized."""
        try:
            print(f"\n🎤 Speech recognized: '{text}'")
            
            # Run conversation workflow
            asyncio.run(self.conversation_graph.run_conversation(text))
            
        except Exception as e:
            print(f"❌ Error processing speech: {e}")
            self.robot_state.mark_interaction_failure(f"Speech processing error: {e}")
    
    def _test_conversation(self):
        """Test the conversation workflow."""
        print("\n🧪 Testing conversation workflow...")
        
        test_inputs = [
            "Hello, how are you?",
            "What's the weather like?",
            "Tell me a joke",
            "What time is it?",
            "Goodbye"
        ]
        
        for test_input in test_inputs:
            print(f"\n--- Testing: '{test_input}' ---")
            try:
                asyncio.run(self.conversation_graph.run_conversation(test_input))
                import time
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test failed: {e}")
        
        print("\n✅ Conversation tests complete!")
    
    def _test_voice(self):
        """Test voice synthesis."""
        print("\n🔊 Testing voice synthesis...")
        
        test_texts = self.persona.get_voice_test_phrases()
        
        for text in test_texts:
            print(f"Speaking: {text}")
            self.voice_handler.speak_text(text)
            import time
            time.sleep(2)  # Wait for audio to finish
        
        print("✅ Voice tests complete!")
    
    def _show_welcome(self):
        """Show welcome message and initial status."""
        print(f"\n🤖 Welcome! I am {self.persona.name}")
        print(f"🎭 Current mood: {self.persona.get_mood()}")
        print(f"🔋 Battery level: {self.robot_state.battery_level:.1f}%")
        print(f"🎤 Wake word: '{Config.WAKE_WORD}'")
        print("\n💡 Try saying something or use the terminal controls!")
        print("   Press 'h' for help, 't' to test conversation, 'v' to test voice")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        print(f"\n⚠️  Signal {signum} received, shutting down gracefully...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up resources and shut down gracefully."""
        try:
            print("\n🧹 Cleaning up resources...")
            
            # Stop components
            if self.terminal_control:
                self.terminal_control.stop()
            
            if self.voice_handler:
                self.voice_handler.cleanup()
            
            if self.robot_state:
                self.robot_state.cleanup()
            
            self.is_running = False
            
            print(f"{self.persona.get_system_prompt('cleanup', 'Cleanup complete.')}")
            
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")
    
    def get_status(self) -> dict:
        """Get the current status of the robot assistant."""
        if not self.robot_state:
            return {"status": "not_initialized"}
        
        status = self.robot_state.get_stats()
        status.update({
            "is_running": self.is_running,
            "persona_name": self.persona.name if self.persona else None,
            "voice_handler_active": self.voice_handler.is_listening if self.voice_handler else False,
            "control_active": self.terminal_control.is_running if self.terminal_control else False
        })
        
        return status

def main():
    """Main entry point."""
    try:
        # Create and run robot assistant
        robot = RobotAssistant()
        
        if robot.initialize():
            robot.start()
        else:
            print("❌ Failed to initialize robot assistant")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
