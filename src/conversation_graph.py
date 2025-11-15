from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import asyncio
import time
from robot_state import RobotState, ActivityStatus, EmotionalState
from persona import RobotPersona
from config import Config

from typing import TypedDict

class ConversationState(TypedDict):
    """State structure for the conversation graph."""
    user_input: str
    robot_response: str
    context: str
    processing_time: float
    error: Optional[str]
    should_continue: bool

class ConversationGraph:
    """LangGraph-based conversation workflow for the robot assistant."""
    
    def __init__(self, robot_state: RobotState, persona: RobotPersona):
        self.robot_state = robot_state
        self.persona = persona
        # Initialize memory with proper configuration
        self.memory = MemorySaver()
        self.graph = self._build_graph()
        # Generate unique identifiers for this conversation session
        self.thread_id = f"spark_{int(time.time())}"
        self.checkpoint_ns = "robot_assistant"
        self.checkpoint_id = f"conv_{int(time.time())}"
        
    def _build_graph(self) -> StateGraph:
        """Build the conversation workflow graph."""
        workflow = StateGraph(ConversationState)
        
        # Add nodes - simplified flow
        workflow.add_node("process", self._process_node)
        workflow.add_node("respond", self._respond_node)
        workflow.add_node("speak", self._speak_node)
        
        # Define the flow - simple linear flow
        workflow.set_entry_point("process")
        workflow.add_edge("process", "respond")
        workflow.add_edge("respond", "speak")
        
        # Simple linear flow for now (can add conditional logic later)
        
        # Compile without checkpointer for now to avoid configuration issues
        return workflow.compile()
    
    async def _listen_node(self, state: dict) -> dict:
        """Listen for voice input."""
        try:
            self.robot_state.update_activity(ActivityStatus.LISTENING)
            self.robot_state.update_emotional_state(EmotionalState.NEUTRAL)
            
            print(f"[{self.persona.name}] Listening...")
            
            # Don't modify user_input, just pass it through
            should_continue = True
            
        except Exception as e:
            error = f"Error in listen node: {e}"
            self.robot_state.update_activity(ActivityStatus.ERROR)
            self.robot_state.mark_interaction_failure(str(e))
            return {
                **state,
                "error": error,
                "should_continue": False
            }
            
        return {
            **state,
            "should_continue": should_continue
        }
    
    async def _process_node(self, state: dict) -> dict:
        """Process user input and generate response."""
        try:
            start_time = time.time()
            self.robot_state.update_activity(ActivityStatus.THINKING)
            self.robot_state.update_emotional_state(EmotionalState.HELPFUL)
            
            print(f"[{self.persona.name}] Processing request...")
            
            user_input = state.get("user_input", "")
            robot_response = ""
            context = self.robot_state.current_context or ""
            processing_time = 0.0
            should_continue = True
            
            if user_input:
                # Check if we should use real API or fallback responses
                if self._should_use_real_api():
                    print(f"[{self.persona.name}] Using AI brain for response...")
                    robot_response, processing_time = await self._generate_real_response(user_input, context)
                    print(f"[{self.persona.name}] AI Response generated: '{robot_response}'")
                else:
                    # Use fallback responses
                    if "hello" in user_input.lower() or "hi" in user_input.lower():
                        robot_response = self.persona.get_response("greeting")
                    elif "how are you" in user_input.lower():
                        mood = self.persona.get_mood()
                        robot_response = f"I'm feeling quite {mood} today."
                    elif "help" in user_input.lower():
                        robot_response = self.persona.get_response("helpful")
                    elif "bye" in user_input.lower():
                        robot_response = self.persona.get_response("farewell")
                        should_continue = False
                    else:
                        robot_response = self._generate_contextual_response(user_input)
                    
                    processing_time = time.time() - start_time
                
                context = f"User asked about: {user_input[:50]}..."
                self.robot_state.set_context(context)
            else:
                    robot_response = self.persona.get_response("confused")
                
        except Exception as e:
            error = f"Error in process node: {e}"
            self.robot_state.update_activity(ActivityStatus.ERROR)
            self.robot_state.mark_interaction_failure(str(e))
            return {
                **state,
                "error": error,
                "should_continue": False
            }
            
        return {
            **state,
            "robot_response": robot_response,
            "context": context,
            "processing_time": processing_time,
            "should_continue": should_continue
        }
    
    async def _respond_node(self, state: dict) -> dict:
        """Prepare the response for output."""
        try:
            self.robot_state.update_activity(ActivityStatus.THINKING)
            
            # Debug: Check what we received
            print(f"[{self.persona.name}] Respond node - State keys: {list(state.keys())}")
            print(f"[{self.persona.name}] Respond node - robot_response: '{state.get('robot_response', 'NOT_FOUND')}'")
            
            print(f"[{self.persona.name}] Response ready: {state['robot_response']}")
            
        except Exception as e:
            state["error"] = f"Error in respond node: {e}"
            self.robot_state.update_activity(ActivityStatus.ERROR)
            self.robot_state.mark_interaction_failure(str(e))
            
        return state
    
    async def _speak_node(self, state: dict) -> dict:
        """Convert response to speech and play audio."""
        try:
            self.robot_state.update_activity(ActivityStatus.SPEAKING)
            
            # Debug: Check what we received
            print(f"[{self.persona.name}] Speak node - State keys: {list(state.keys())}")
            print(f"[{self.persona.name}] Speak node - robot_response: '{state.get('robot_response', 'NOT_FOUND')}'")
            
            print(f"[{self.persona.name}] Speaking: {state['robot_response']}")
            print(f"🤖 {state['robot_response']}")
            
            # ACTUALLY SPEAK THE RESPONSE!
            if state.get("robot_response"):
                print(f"[{self.persona.name}] Triggering voice output...")
                try:
                    # Get the voice handler from robot state and speak the response
                    if hasattr(self.robot_state, 'voice_handler') and self.robot_state.voice_handler:
                        print(f"[{self.persona.name}] Calling voice handler to speak...")
                        self.robot_state.voice_handler.speak_text(state["robot_response"])
                    else:
                        print(f"[{self.persona.name}] No voice handler available, using fallback...")
                        # Fallback: just wait a bit to simulate speech
                        import time
                        time.sleep(len(state["robot_response"]) * 0.05)
                except Exception as e:
                    print(f"[{self.persona.name}] Error in voice output: {e}")
                    # Fallback: just wait a bit to simulate speech
                    import time
                    time.sleep(len(state["robot_response"]) * 0.05)
            
            if state.get("user_input") and state.get("robot_response"):
                self.robot_state.add_conversation_entry(
                    state["user_input"],
                    state["robot_response"],
                    state.get("processing_time", 0.0),
                    state.get("context", "")
                )
                self.robot_state.mark_interaction_success()
                
                if "error" in state["user_input"].lower():
                    self.robot_state.update_emotional_state(EmotionalState.CONFUSED)
                elif "thank" in state["user_input"].lower():
                    self.robot_state.update_emotional_state(EmotionalState.HAPPY)
                else:
                    self.robot_state.update_emotional_state(EmotionalState.HELPFUL)
            
            # Clear the state for next iteration
            new_user_input = ""
            new_robot_response = ""
            new_context = ""
            new_processing_time = 0.0
            self.robot_state.update_activity(ActivityStatus.LISTENING)
            
        except Exception as e:
            error = f"Error in speak node: {e}"
            self.robot_state.update_activity(ActivityStatus.ERROR)
            self.robot_state.mark_interaction_failure(str(e))
            return {
                **state,
                "error": error,
                "should_continue": False
            }
            
        return {
            **state,
            "user_input": new_user_input,
            "robot_response": new_robot_response,
            "context": new_context,
            "processing_time": new_processing_time
        }
    
    async def _wait_node(self, state: dict) -> dict:
        """Wait state between interactions."""
        try:
            self.robot_state.update_activity(ActivityStatus.IDLE)
            
            if self.robot_state.is_paused:
                print(f"[{self.persona.name}] System paused. Press SPACE to resume.")
                while self.robot_state.is_paused:
                    await asyncio.sleep(0.1)
            
            await asyncio.sleep(0.5)
            
        except Exception as e:
            state["error"] = f"Error in wait node: {e}"
            self.robot_state.update_activity(ActivityStatus.ERROR)
            self.robot_state.mark_interaction_failure(str(e))
            
        return state
    
    async def _error_handler_node(self, state: dict) -> dict:
        """Handle errors in the conversation flow."""
        try:
            self.robot_state.update_activity(ActivityStatus.ERROR)
            self.robot_state.update_emotional_state(EmotionalState.CONFUSED)
            
            if state.get("error"):
                print(f"[{self.persona.name}] Error occurred: {state['error']}")
                error_response = f"I encountered an error: {state['error']}. Let me try to recover..."
                print(f"🤖 {error_response}")
                
                self.robot_state.add_conversation_entry(
                    "ERROR",
                    error_response,
                    0.0,
                    f"Error: {state['error']}"
                )
                
                state["error"] = None
                state["should_continue"] = True
                
        except Exception as e:
            print(f"[{self.persona.name}] Critical error in error handler: {e}")
            state["should_continue"] = False
            
        return state
    
    def _should_continue(self, state: dict) -> str:
        """Determine if the conversation should continue."""
        if not state.get("should_continue", True):
            return "end"
        return "continue"
    
    def _detect_wake_word(self, text: str) -> bool:
        """Detect if the wake word is present in the text."""
        if not text:
            return False
        
        wake_word = Config.WAKE_WORD.lower()
        return wake_word in text.lower()
    
    def _generate_contextual_response(self, user_input: str) -> str:
        """Generate a contextual response based on user input."""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["weather", "temperature"]):
            return "I'd check the weather for you, but my meteorological sensors are offline."
        
        elif any(word in input_lower for word in ["time", "clock"]):
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M")
            return f"The current time is {current_time}."
        
        elif any(word in input_lower for word in ["joke", "funny"]):
            return "Why did the robot go to the doctor? Because it had a virus!"
        
        else:
            return f"I'm not sure how to respond to '{user_input}'. Let's regroup and try again."
    
    async def _generate_real_response(self, user_input: str, context: str = "") -> tuple[str, float]:
        """Generate a response using OpenAI API."""
        try:
            import openai
            from config import Config
            
            print(f"[{self.persona.name}] _generate_real_response called with: '{user_input}'")
            
            # Check if OpenAI API key is configured
            if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "your_openai_api_key_here":
                print(f"[{self.persona.name}] No valid OpenAI API key found")
                return "I'd love to give you a smart response, but my AI brain isn't connected yet. Please check your OpenAI API key configuration.", 0.1
            
            print(f"[{self.persona.name}] OpenAI API key found, configuring client...")
            
            # Configure OpenAI client
            client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            
            # Build the prompt with persona and recent conversation
            system_prompt = self.persona.get_personality_prompt()
            history_snippet = ""
            if hasattr(self.robot_state, "get_recent_conversation"):
                history_snippet = self.robot_state.get_recent_conversation(max_turns=6)
            if not history_snippet:
                history_snippet = "No previous conversation. This is the first turn."
            
            user_prompt = (
                f"Recent conversation:\n{history_snippet}\n\n"
                f"Current user message: {user_input}\nContext: {context}\n\n"
                f"Respond as {self.persona.name}, following the mission described in the system message. "
                "Keep responses under 70 words, only discuss Open Droids/open source if the user asks, "
                "and do NOT prefix the response with your name or any speaker label."
            )
            
            print(f"[{self.persona.name}] Making OpenAI API call...")
            
            use_web = getattr(Config, "ENABLE_WEB_SEARCH", False)
            
            if use_web:
                response = client.responses.create(
                    model=Config.OPENAI_MODEL,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    tools=[{"type": "web_search", "name": "web"}],
                    tool_choice="auto",
                    temperature=0.8,
                    max_output_tokens=200,
                )
                ai_response = self._extract_response_text(response)
                token_usage = getattr(response, "usage", None)
                total_tokens = getattr(token_usage, "total_tokens", 0) if token_usage else 0
                processing_time = total_tokens / 1000 if total_tokens else 0.3
            else:
                response = client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=120,
                    temperature=0.8
                )
                ai_response = response.choices[0].message.content.strip()
                processing_time = response.usage.total_tokens / 1000  # Rough time estimate
            
            print(f"[{self.persona.name}] OpenAI API response received: '{ai_response}'")
            
            return ai_response, processing_time
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return f"I encountered an error with my AI brain: {str(e)[:50]}... Falling back to basic responses.", 0.1
    
    def _extract_response_text(self, response) -> str:
        """Normalize text output from the Responses API."""
        try:
            outputs = getattr(response, "output", None)
            if outputs:
                chunks: List[str] = []
                for item in outputs:
                    content_list = item.get("content") if isinstance(item, dict) else getattr(item, "content", [])
                    if not content_list:
                        continue
                    for content in content_list:
                        if isinstance(content, dict):
                            if content.get("type") == "output_text":
                                chunks.append(content.get("text", ""))
                        else:
                            if getattr(content, "type", "") == "output_text":
                                chunks.append(getattr(content, "text", ""))
                if chunks:
                    return " ".join(chunks).strip()
            if hasattr(response, "output_text") and response.output_text:
                return response.output_text.strip()
        except Exception as e:
            print(f"[{self.persona.name}] Warning: could not parse Responses output: {e}")
        return ""
    
    def _should_use_real_api(self) -> bool:
        """Check if we should use real API or mock responses."""
        from config import Config
        result = (Config.OPENAI_API_KEY and 
                Config.OPENAI_API_KEY != "your_openai_api_key_here" and
                not Config.DEV_MODE)  # DEV_MODE is already a boolean
        print(f"[{self.persona.name}] _should_use_real_api: {result}")
        print(f"[{self.persona.name}]   - OPENAI_API_KEY: {bool(Config.OPENAI_API_KEY)}")
        print(f"[{self.persona.name}]   - Not default: {Config.OPENAI_API_KEY != 'your_openai_api_key_here'}")
        print(f"[{self.persona.name}]   - DEV_MODE: {Config.DEV_MODE}")
        return result
    
    async def run_conversation(self, initial_input: str = None) -> None:
        """Run the conversation workflow."""
        try:
            # Create initial state dictionary directly
            state_dict = {
                "user_input": initial_input or "Hello, how are you today?",
                "robot_response": "",
                "context": "",
                "processing_time": 0.0,
                "error": None,
                "should_continue": True
            }
            
            print(f"[{self.persona.name}] Starting conversation workflow...")
            print(f"[{self.persona.name}] Initial state: {state_dict}")
            
            # Run the graph without checkpoint configuration for now
            async for event in self.graph.astream(state_dict):
                print(f"[{self.persona.name}] Graph event: {event}")
                if hasattr(event, 'node'):
                    print(f"[{self.persona.name}] Executing node: {event.node}")
                if hasattr(event, 'data'):
                    print(f"[{self.persona.name}] Node data: {event.data}")
                
        except Exception as e:
            print(f"[{self.persona.name}] Error running conversation: {e}")
            self.robot_state.update_activity(ActivityStatus.ERROR)
            self.robot_state.mark_interaction_failure(str(e))
    
    def stop_conversation(self):
        """Stop the conversation workflow."""
        self.robot_state.update_activity(ActivityStatus.IDLE)
        print(f"[{self.persona.name}] Conversation workflow stopped.")
