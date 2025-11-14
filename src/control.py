import threading
import time
import sys
import os
from typing import Optional, Callable
from robot_state import RobotState, ActivityStatus

class TerminalControl:
    """Terminal control interface for the robot assistant."""
    
    def __init__(self, robot_state: RobotState):
        self.robot_state = robot_state
        self.is_running = False
        self.control_thread = None
        self.callbacks = {}
        
        # Control commands
        self.commands = {
            ' ': self._toggle_pause,
            'q': self._quit_application,
            'r': self._reset_conversation,
            's': self._show_status,
            'm': self._toggle_mute,
            'h': self._show_help,
            'c': self._show_config,
            'l': self._list_conversations,
            'b': self._show_battery_status,
            'e': self._show_errors
        }
        
        # Status display
        self.status_interval = 5.0  # seconds
        self.last_status_update = 0
    
    def start(self):
        """Start the terminal control interface."""
        if self.is_running:
            return
        
        self.is_running = True
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_thread.start()
        
        print("=== Robot Assistant Terminal Control ===")
        print("Press 'h' for help, 'q' to quit")
        print("=====================================")
    
    def stop(self):
        """Stop the terminal control interface."""
        self.is_running = False
        if self.control_thread:
            self.control_thread.join(timeout=1)
        print("[Control] Terminal control stopped")
    
    def _control_loop(self):
        """Main control loop for handling keyboard input."""
        while self.is_running:
            try:
                # Check for input (non-blocking)
                if self._has_input():
                    key = self._get_input()
                    if key in self.commands:
                        self.commands[key]()
                    elif key.isprintable():
                        print(f"[Control] Unknown command: '{key}' (press 'h' for help)")
                
                # Auto-status update
                current_time = time.time()
                if current_time - self.last_status_update >= self.status_interval:
                    self._auto_status_update()
                    self.last_status_update = current_time
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"[Control] Error in control loop: {e}")
                time.sleep(1)
    
    def _has_input(self) -> bool:
        """Check if there's input available (non-blocking)."""
        try:
            import select
            return select.select([sys.stdin], [], [], 0)[0]
        except ImportError:
            # Windows compatibility
            import msvcrt
            return msvcrt.kbhit()
        except:
            return False
    
    def _get_input(self) -> str:
        """Get a single character input."""
        try:
            import sys
            import tty
            import termios
            
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
        except ImportError:
            # Windows compatibility
            import msvcrt
            return msvcrt.getch().decode('utf-8')
        except:
            return ''
    
    def _toggle_pause(self):
        """Toggle pause/unpause functionality."""
        is_paused = self.robot_state.toggle_pause()
        status = "PAUSED" if is_paused else "RESUMED"
        print(f"[Control] System {status}")
        
        # Update activity status
        if is_paused:
            self.robot_state.update_activity(ActivityStatus.PAUSED)
        else:
            self.robot_state.update_activity(ActivityStatus.IDLE)
    
    def _quit_application(self):
        """Quit the application."""
        print("[Control] Quitting application...")
        self.robot_state.cleanup()
        self.is_running = False
        
        # Exit the application
        os._exit(0)
    
    def _reset_conversation(self):
        """Reset conversation state."""
        print("[Control] Resetting conversation... *whirr*")
        self.robot_state.reset_conversation()
        print("[Control] Conversation reset complete")
    
    def _show_status(self):
        """Show current system status."""
        stats = self.robot_state.get_stats()
        
        print("\n=== SYSTEM STATUS ===")
        print(f"Uptime: {stats['uptime_formatted']}")
        print(f"Activity: {stats['current_activity']}")
        print(f"Emotional State: {stats['emotional_state']}")
        print(f"Current Mood: {stats['current_mood']}")
        print(f"Battery: {stats['battery_level']:.1f}%")
        print(f"Paused: {'Yes' if stats['is_paused'] else 'No'}")
        print(f"Muted: {'Yes' if stats['is_muted'] else 'No'}")
        print(f"Total Interactions: {stats['total_interactions']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print(f"Avg Response Time: {stats['avg_response_time']:.3f}s")
        print("===================\n")
    
    def _toggle_mute(self):
        """Toggle mute/unmute functionality."""
        is_muted = self.robot_state.toggle_mute()
        status = "MUTED" if is_muted else "UNMUTED"
        print(f"[Control] Audio {status}")
    
    def _show_help(self):
        """Show help information."""
        print("\n=== HELP ===")
        print("SPACE - Pause/Unpause voice processing")
        print("q     - Quit application")
        print("r     - Reset conversation state")
        print("s     - Show current status/stats")
        print("m     - Toggle mute mode")
        print("h     - Show this help")
        print("c     - Show configuration")
        print("l     - List recent conversations")
        print("b     - Show battery status")
        print("e     - Show recent errors")
        print("==========\n")
    
    def _show_config(self):
        """Show current configuration."""
        from config import Config
        
        print("\n=== CONFIGURATION ===")
        Config.print_config()
        print("====================\n")
    
    def _list_conversations(self):
        """List recent conversations."""
        conversations = self.robot_state.get_recent_conversations(5)
        
        if not conversations:
            print("[Control] No recent conversations found")
            return
        
        print("\n=== RECENT CONVERSATIONS ===")
        for i, conv in enumerate(conversations, 1):
            timestamp = conv['timestamp'][:19]  # Show only date and time
            user_input = conv['user_input'][:50]  # Truncate long inputs
            if len(conv['user_input']) > 50:
                user_input += "..."
            
            print(f"{i}. [{timestamp}] User: {user_input}")
            print(f"   Response: {conv['robot_response'][:60]}...")
            print(f"   Processing Time: {conv['processing_time']:.3f}s")
            print()
        print("==============================\n")
    
    def _show_battery_status(self):
        """Show detailed battery status."""
        stats = self.robot_state.get_stats()
        battery = stats['battery_level']
        
        print("\n=== BATTERY STATUS ===")
        print(f"Current Level: {battery:.1f}%")
        
        # Battery status indicators
        if battery > 80:
            print("Status: Fully charged")
        elif battery > 60:
            print("Status: Good charge *whirr*")
        elif battery > 40:
            print("Status: Moderate charge *click*")
        elif battery > 20:
            print("Status: Low charge")
        else:
            print("Status: Critical charge")
        
        # Estimated runtime (simulated)
        if battery > 0:
            runtime_hours = (battery / 100) * 24  # Assume 24 hours at 100%
            print(f"Estimated Runtime: {runtime_hours:.1f} hours")
        
        print("=====================\n")
    
    def _show_errors(self):
        """Show recent system errors."""
        stats = self.robot_state.get_stats()
        errors = stats['recent_errors']
        
        if not errors:
            print("[Control] No recent errors found")
            return
        
        print("\n=== RECENT ERRORS ===")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")
        print("====================\n")
    
    def _auto_status_update(self):
        """Automatic status update (called periodically)."""
        if not self.robot_state.is_paused:
            # Show minimal status
            stats = self.robot_state.get_stats()
            print(f"[Status] {stats['current_activity']} | Battery: {stats['battery_level']:.1f}% | Interactions: {stats['total_interactions']}")
    
    def register_callback(self, command: str, callback: Callable):
        """Register a custom callback for a command."""
        if command not in self.commands:
            self.commands[command] = callback
            print(f"[Control] Registered custom command: '{command}'")
        else:
            print(f"[Control] Command '{command}' already exists, cannot override")
    
    def get_control_status(self) -> dict:
        """Get the current control interface status."""
        return {
            "is_running": self.is_running,
            "available_commands": list(self.commands.keys()),
            "status_interval": self.status_interval,
            "last_status_update": self.last_status_update
        }
