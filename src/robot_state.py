import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class ActivityStatus(Enum):
    """Robot activity status enumeration."""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    PAUSED = "paused"
    ERROR = "error"

class EmotionalState(Enum):
    """Robot emotional state enumeration."""
    HAPPY = "happy"
    CONFUSED = "confused"
    SARCASTIC = "sarcastic"
    EXISTENTIAL = "existential_crisis"
    HELPFUL = "helpful"
    NEUTRAL = "neutral"

@dataclass
class ConversationEntry:
    """Single conversation entry with metadata."""
    timestamp: str
    user_input: str
    robot_response: str
    emotional_state: str
    processing_time: float
    context: Optional[str] = None

@dataclass
class RobotMood:
    """Robot mood tracking."""
    current_mood: str
    energy_level: float  # 0.0 to 1.0
    sarcasm_level: float  # 0.0 to 1.0
    last_mood_change: str
    mood_duration: float  # seconds

class RobotState:
    """Persistent state management for the robot assistant."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversation_history: List[ConversationEntry] = []
        self.current_activity = ActivityStatus.IDLE
        self.emotional_state = EmotionalState.NEUTRAL
        self.mood = RobotMood(
            current_mood="Circuit-optimized",
            energy_level=0.8,
            sarcasm_level=0.8,
            last_mood_change=datetime.now().isoformat(),
            mood_duration=0.0
        )
        
        # System state
        self.is_paused = False
        self.is_muted = False
        self.battery_level = 100.0  # Simulated battery
        self.start_time = time.time()
        self.total_interactions = 0
        self.successful_interactions = 0
        self.failed_interactions = 0
        
        # Voice handler reference
        self.voice_handler = None
        
        # Global control file monitoring
        self.control_file = "data/spark_control.txt"
        self.last_control_check = 0
        self.control_check_interval = 0.5  # Check every 500ms
        self.should_quit = False
        
        # Performance metrics
        self.avg_response_time = 0.0
        self.total_processing_time = 0.0
        
        # Context tracking
        self.current_context = ""
        self.user_preferences: Dict[str, Any] = {}
        self.system_errors: List[str] = []
        
        # Load existing state if available
        self.load_state()
    
    def update_activity(self, status: ActivityStatus):
        """Update the current activity status."""
        self.current_activity = status
        self._log_state_change(f"Activity changed to: {status.value}")
    
    def update_emotional_state(self, state: EmotionalState):
        """Update the emotional state."""
        self.emotional_state = state
        self._log_state_change(f"Emotional state changed to: {state.value}")
    
    def update_mood(self, mood: str, energy: float = None, sarcasm: float = None):
        """Update the robot's mood."""
        old_mood = self.mood.current_mood
        self.mood.current_mood = mood
        
        if energy is not None:
            self.mood.energy_level = max(0.0, min(1.0, energy))
        
        if sarcasm is not None:
            self.mood.sarcasm_level = max(0.0, min(1.0, sarcasm))
        
        # Calculate mood duration
        now = datetime.now()
        last_change = datetime.fromisoformat(self.mood.last_mood_change)
        self.mood.mood_duration = (now - last_change).total_seconds()
        
        if old_mood != mood:
            self.mood.last_mood_change = now.isoformat()
            self._log_state_change(f"Mood changed from {old_mood} to {mood}")
    
    def add_conversation_entry(self, user_input: str, robot_response: str, 
                             processing_time: float, context: str = None):
        """Add a new conversation entry to history."""
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            robot_response=robot_response,
            emotional_state=self.emotional_state.value,
            processing_time=processing_time,
            context=context
        )
        
        self.conversation_history.append(entry)
        self.total_interactions += 1
        
        # Update performance metrics
        self.total_processing_time += processing_time
        self.avg_response_time = self.total_processing_time / self.total_interactions
        
        # Maintain history size limit
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
        
        # Update battery (simulated drain)
        self.battery_level = max(0.0, self.battery_level - 0.1)
        
        self._log_state_change(f"Added conversation entry. Total: {self.total_interactions}")
    
    def mark_interaction_success(self):
        """Mark the last interaction as successful."""
        self.successful_interactions += 1
    
    def mark_interaction_failure(self, error: str):
        """Mark the last interaction as failed."""
        self.failed_interactions += 1
        self.system_errors.append(f"{datetime.now().isoformat()}: {error}")
        
        # Keep only recent errors
        if len(self.system_errors) > 20:
            self.system_errors.pop(0)
    
    def set_context(self, context: str):
        """Set the current conversation context."""
        self.current_context = context
    
    def add_user_preference(self, key: str, value: Any):
        """Add or update a user preference."""
        self.user_preferences[key] = value
    
    def get_user_preference(self, key: str, default: Any = None):
        """Get a user preference."""
        return self.user_preferences.get(key, default)
    
    def get_recent_conversation(self, max_turns: int = 5) -> str:
        """Return formatted recent conversation turns for context."""
        if not self.conversation_history:
            return ""
        turns = self.conversation_history[-max_turns:]
        lines: List[str] = []
        for entry in turns:
            lines.append(f"User: {entry.user_input}")
            lines.append(f"Assistant: {entry.robot_response}")
        return "\n".join(lines)
    
    def register_voice_handler(self, voice_handler):
        """Register the voice handler for pause/resume coordination."""
        self.voice_handler = voice_handler
        self._log_state_change("Voice handler registered")
    
    def check_global_controls(self):
        """Check for global control commands from external terminals."""
        import os
        import time
        
        current_time = time.time()
        if current_time - self.last_control_check < self.control_check_interval:
            return
        
        self.last_control_check = current_time
        
        try:
            if os.path.exists(self.control_file):
                with open(self.control_file, "r") as f:
                    command = f.read().strip().upper()
                
                if command:
                    # Clear the control file
                    with open(self.control_file, "w") as f:
                        f.write("")
                    
                    # Process the command
                    self._process_global_command(command)
                    
        except Exception as e:
            self._log_state_change(f"Error reading global controls: {e}")
    
    def _process_global_command(self, command: str):
        """Process a global control command."""
        print(f"[Global Control] Received command: {command}")
        
        if command == "PAUSE":
            if not self.is_paused:
                self.toggle_pause()
                print("[Global Control] SPARK paused from external terminal")
        
        elif command == "UNPAUSE":
            if self.is_paused:
                self.toggle_pause()
                print("[Global Control] SPARK unpaused from external terminal")
        
        elif command == "MUTE":
            if not self.is_muted:
                self.toggle_mute()
                print("[Global Control] SPARK muted from external terminal")
        
        elif command == "UNMUTE":
            if self.is_muted:
                self.toggle_mute()
                print("[Global Control] SPARK unmuted from external terminal")
        
        elif command == "RESET":
            self.reset_conversation()
            print("[Global Control] SPARK conversation reset from external terminal")
        
        elif command == "QUIT":
            print("[Global Control] Quit command received from external terminal")
            # Signal to main application to quit
            self._log_state_change("Quit command received from global control")
            # Set a flag that the main application can check
            self.should_quit = True
    
    def toggle_pause(self):
        """Toggle the paused state."""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.update_activity(ActivityStatus.PAUSED)
            # Pause voice input when system is paused
            if self.voice_handler:
                self.voice_handler.pause_listening()
        else:
            self.update_activity(ActivityStatus.IDLE)
            # Resume voice input when system is unpaused
            if self.voice_handler:
                self.voice_handler.resume_listening()
        
        self._log_state_change(f"Pause toggled: {self.is_paused}")
        return self.is_paused
    
    def toggle_mute(self):
        """Toggle the muted state."""
        self.is_muted = not self.is_muted
        self._log_state_change(f"Mute toggled: {self.is_muted}")
        return self.is_muted
    
    def reset_conversation(self):
        """Reset conversation history and context."""
        self.conversation_history.clear()
        self.current_context = ""
        self.total_interactions = 0
        self.successful_interactions = 0
        self.failed_interactions = 0
        self.total_processing_time = 0.0
        self.avg_response_time = 0.0
        
        self._log_state_change("Conversation reset")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics and state."""
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "total_interactions": self.total_interactions,
            "successful_interactions": self.successful_interactions,
            "failed_interactions": self.failed_interactions,
            "success_rate": (self.successful_interactions / max(1, self.total_interactions)) * 100,
            "avg_response_time": self.avg_response_time,
            "battery_level": self.battery_level,
            "current_activity": self.current_activity.value,
            "emotional_state": self.emotional_state.value,
            "current_mood": self.mood.current_mood,
            "is_paused": self.is_paused,
            "is_muted": self.is_muted,
            "conversation_history_size": len(self.conversation_history),
            "recent_errors": self.system_errors[-5:] if self.system_errors else []
        }
    
    def get_recent_conversations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation entries."""
        recent = self.conversation_history[-limit:] if self.conversation_history else []
        return [asdict(entry) for entry in recent]
    
    def save_state(self):
        """Save current state to file."""
        try:
            state_data = {
                "conversation_history": [asdict(entry) for entry in self.conversation_history],
                "user_preferences": self.user_preferences,
                "total_interactions": self.total_interactions,
                "successful_interactions": self.successful_interactions,
                "failed_interactions": self.failed_interactions,
                "total_processing_time": self.total_processing_time,
                "avg_response_time": self.avg_response_time,
                "last_saved": datetime.now().isoformat()
            }
            
            with open("data/robot_state.json", "w") as f:
                json.dump(state_data, f, indent=2)
                
        except Exception as e:
            self._log_state_change(f"Failed to save state: {e}")
    
    def load_state(self):
        """Load state from file if available."""
        try:
            with open("data/robot_state.json", "r") as f:
                state_data = json.load(f)
                
            # Restore conversation history
            if "conversation_history" in state_data:
                self.conversation_history = [
                    ConversationEntry(**entry) for entry in state_data["conversation_history"]
                ]
            
            # Restore other data
            self.user_preferences = state_data.get("user_preferences", {})
            self.total_interactions = state_data.get("total_interactions", 0)
            self.successful_interactions = state_data.get("successful_interactions", 0)
            self.failed_interactions = state_data.get("failed_interactions", 0)
            self.total_processing_time = state_data.get("total_processing_time", 0.0)
            self.avg_response_time = state_data.get("avg_response_time", 0.0)
            
            self._log_state_change("State loaded from file")
            
        except FileNotFoundError:
            self._log_state_change("No existing state file found, starting fresh")
        except Exception as e:
            self._log_state_change(f"Failed to load state: {e}")
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def _log_state_change(self, message: str):
        """Log a state change (placeholder for future logging implementation)."""
        # This could be expanded to use proper logging
        pass
    
    def cleanup(self):
        """Cleanup and save state before shutdown."""
        self.save_state()
        self._log_state_change("State saved during cleanup")
