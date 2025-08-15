import speech_recognition as sr
import pygame
import pyaudio
import wave
import threading
import time
import queue
from typing import Optional, Callable, List, Dict
from config import Config

class VoiceHandler:
    """Handles voice input/output for the robot assistant."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.is_speaking = False
        self.audio_thread = None
        self.callback = None
        self.robot_state = None  # Reference to robot state for pause checking
        
        # Audio settings
        self.sample_rate = Config.SAMPLE_RATE
        self.chunk_size = Config.CHUNK_SIZE
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # Performance optimization attributes
        self._elevenlabs_client = None
        self._voice_id = None
        
        # Initialize audio components
        self._init_audio()
    
    def _init_audio(self):
        """Initialize audio components."""
        try:
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            
            # Try to find available audio devices
            input_devices = []
            for i in range(self.audio.get_device_count()):
                try:
                    info = self.audio.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:
                        input_devices.append((i, info['name']))
                        print(f"[Voice] Found input device {i}: {info['name']}")
                except:
                    pass
            
            if input_devices:
                # Use the first available input device
                device_index = input_devices[0][0]
                print(f"[Voice] Using input device: {input_devices[0][1]} (index {device_index})")
                self.microphone = sr.Microphone(device_index=device_index)
            else:
                # Fallback to default microphone
                print("[Voice] No specific input devices found, using default")
                self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Initialize pygame for audio playback
            pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=self.channels)
            
            print(f"[Voice] Audio initialized successfully with PulseAudio")
            
        except Exception as e:
            print(f"[Voice] Error initializing audio: {e}")
            print("[Voice] Running in text-only mode")
    
    def set_callback(self, callback: Callable[[str], None]):
        """Set callback function for when speech is recognized."""
        self.callback = callback
    
    def set_robot_state(self, robot_state):
        """Set reference to robot state for pause checking."""
        self.robot_state = robot_state
    
    def start_listening(self):
        """Start continuous listening for voice input."""
        if self.is_listening:
            return
        
        # Pre-warm ElevenLabs for faster responses
        self._pre_warm_elevenlabs()
        
        self.is_listening = True
        self.audio_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.audio_thread.start()
        print("[Voice] Started listening for voice input...")
    
    def stop_listening(self):
        """Stop listening for voice input."""
        self.is_listening = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1)
        print("[Voice] Stopped listening for voice input")
    
    def pause_listening(self):
        """Pause voice input temporarily."""
        self.is_listening = False
        print("[Voice] Voice input paused *click*")
    
    def resume_listening(self):
        """Resume voice input."""
        self.is_listening = True
        if not self.audio_thread or not self.audio_thread.is_alive():
            self.audio_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.audio_thread.start()
        print("[Voice] Voice input resumed *beep*")
    
    def _listen_loop(self):
        """Main listening loop for voice input."""
        while self.is_listening:
            try:
                # Check if system is paused
                if self.robot_state and self.robot_state.is_paused:
                    time.sleep(0.1)  # Wait while paused
                    continue
                
                if self.microphone:
                    # Use non-blocking audio capture
                    try:
                        with self.microphone as source:
                            # Very short timeout to prevent blocking
                            audio = self.recognizer.listen(source, timeout=0.05, phrase_time_limit=2)
                            if audio:
                                # Process the audio in a separate thread to avoid blocking
                                threading.Thread(target=self._process_audio, args=(audio,), daemon=True).start()
                    except sr.WaitTimeoutError:
                        # No speech detected, continue immediately
                        pass
                    except Exception as e:
                        # Log error but don't block
                        if "timeout" not in str(e).lower():
                            print(f"[Voice] Audio capture error: {e}")
                        
                else:
                    # Simulate voice input for testing (less frequent)
                    time.sleep(5)  # Reduced frequency
                    if self.callback and self.is_listening:
                        self.callback("Hello, how are you today?")
                        
            except Exception as e:
                print(f"[Voice] Error in listening loop: {e}")
                time.sleep(0.05)  # Very short error delay
    
    def _process_audio(self, audio):
        """Process captured audio and convert to text."""
        try:
            print("[Voice] Processing audio... *whirr*")
            
            # Convert speech to text
            text = self.recognizer.recognize_google(audio)
            
            if text:
                print(f"[Voice] Recognized: '{text}'")
                
                # For now, respond to all voice input (no wake word required)
                print("[Voice] Voice input received! *beep*")
                
                if self.callback:
                    print(f"[Voice] Sending '{text}' to conversation handler...")
                    self.callback(text)
                else:
                    print("[Voice] No callback registered")
            
        except sr.UnknownValueError:
            print("[Voice] Could not understand audio")
        except sr.RequestError as e:
            print(f"[Voice] Speech recognition service error: {e}")
        except Exception as e:
            print(f"[Voice] Error processing audio: {e}")
    
    def _detect_wake_word(self, text: str) -> bool:
        """Detect if the wake word is present in the text."""
        if not text:
            return False
        
        wake_word = Config.WAKE_WORD.lower()
        return wake_word in text.lower()
    
    def _extract_command(self, text: str) -> str:
        """Extract the command part after the wake word."""
        wake_word = Config.WAKE_WORD.lower()
        text_lower = text.lower()
        
        if wake_word in text_lower:
            # Find the position after the wake word
            wake_pos = text_lower.find(wake_word)
            command_start = wake_pos + len(wake_word)
            
            # Extract the command and clean it up
            command = text[command_start:].strip()
            
            # Remove common filler words
            filler_words = ["please", "can you", "would you", "could you"]
            for filler in filler_words:
                if command.lower().startswith(filler):
                    command = command[len(filler):].strip()
            
            return command if command else "Hello"
        
        return text
    
    def speak_text(self, text: str, voice_id: str = None):
        """Convert text to speech and play audio."""
        if self.is_speaking:
            return
        
        self.is_speaking = True
        
        try:
            print(f"[Voice] Speaking: {text}")
            
            # For now, simulate TTS (replace with ElevenLabs API)
            self._simulate_speech(text)
            
        except Exception as e:
            print(f"[Voice] Error in speech synthesis: {e}")
        finally:
            self.is_speaking = False
    
    def _simulate_speech(self, text: str):
        """Simulate speech output using pygame or ElevenLabs API."""
        try:
            print(f"[Voice] Processing speech: '{text}'")
            
            # Add safety timeout for entire speech process
            import time
            start_time = time.time()
            max_speech_time = 15.0  # Maximum 15 seconds for any speech operation
            
            # Check if we should use real ElevenLabs API
            if self._should_use_real_tts():
                self._generate_real_speech(text)
            else:
                self._generate_mock_speech(text)
            
            # Check if we exceeded maximum time
            if time.time() - start_time > max_speech_time:
                print("[Voice] Warning: Speech generation took longer than expected")
                
        except Exception as e:
            print(f"[Voice] Error in speech generation: {e}")
            # Fallback: just wait
            import time
            time.sleep(min(len(text) * 0.05, 2.0))
    
    def _should_use_real_tts(self) -> bool:
        """Check if we should use real ElevenLabs API or mock speech."""
        from config import Config
        result = (Config.ELEVENLABS_API_KEY and 
                Config.ELEVENLABS_API_KEY != "your_elevenlabs_api_key_here" and
                not Config.DEV_MODE)  # DEV_MODE is already a boolean
        print(f"[Voice] _should_use_real_tts: {result}")
        print(f"[Voice]   - ELEVENLABS_API_KEY: {bool(Config.ELEVENLABS_API_KEY)}")
        print(f"[Voice]   - Not default: {Config.ELEVENLABS_API_KEY != 'your_elevenlabs_api_key_here'}")
        print(f"[Voice]   - DEV_MODE: {Config.DEV_MODE}")
        return result
    
    def _generate_real_speech(self, text: str):
        """Generate speech using ElevenLabs API with optimized performance."""
        try:
            from elevenlabs import ElevenLabs
            from config import Config
            
            print(f"[Voice] Using ElevenLabs API for speech... *whirr*")
            print(f"[Voice] Text to convert: '{text}'")
            
            # Use pre-warmed client for faster response
            client = self._get_elevenlabs_client()
            voice_id = self._voice_id or Config.VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
            print(f"[Voice] Using pre-warmed ElevenLabs client with voice ID: {voice_id}")
            
            print(f"[Voice] Calling ElevenLabs API with optimized settings...")
            audio_stream = client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                output_format="mp3_44100_64",  # Lower bitrate for faster processing
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": 0.5,  # Lower stability for faster generation
                    "similarity_boost": 0.5  # Lower similarity for speed
                }
            )
            print(f"[Voice] ElevenLabs API call successful, audio stream received")
            
            # Optimized audio processing for speed
            import tempfile
            import os
            
            print(f"[Voice] Processing audio stream for fast playback...")
            # Convert generator to bytes more efficiently
            audio_bytes = b''.join(audio_stream)
            print(f"[Voice] Audio stream converted to bytes: {len(audio_bytes)} bytes")
            
            # Create temporary file with optimized settings
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file.flush()
                print(f"[Voice] Audio saved to temporary file: {temp_file.name}")
                
                # Fast audio loading and playback
                print(f"[Voice] Loading audio into pygame...")
                pygame.mixer.music.load(temp_file.name)
                print(f"[Voice] Starting audio playback immediately...")
                pygame.mixer.music.play()
                
                # Reduced timeout for faster response
                import time
                start_time = time.time()
                timeout = 8.0  # Reduced timeout for faster processing
                
                print(f"[Voice] Monitoring audio playback...")
                while pygame.mixer.music.get_busy() and (time.time() - start_time) < timeout:
                    time.sleep(0.05)  # Faster polling for responsiveness
                
                # Force stop if still playing
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    print("[Voice] Audio playback stopped (timeout)")
                
                print(f"[Voice] Audio playback completed successfully!")
                
                # Immediate cleanup for better performance
                try:
                    os.unlink(temp_file.name)
                    print(f"[Voice] Temporary file cleaned up")
                except Exception as e:
                    print(f"[Voice] Error cleaning up temp file: {e}")
            
            print(f"[Voice] Speech generated and played successfully! *beep*")
            
        except Exception as e:
            print(f"[Voice] ElevenLabs API error: {e}")
            print("[Voice] Falling back to mock speech...")
            self._generate_mock_speech(text)
    
    def _generate_mock_speech(self, text: str):
        """Generate mock speech using pygame."""
        try:
            print(f"[Voice] Using mock speech generation... *click*")
            
            # Generate a simple audio tone
            duration = len(text) * 0.1  # Rough estimate of speech duration
            
            # Create a simple beep sound
            sample_rate = 44100
            frequency = 440  # A4 note
            
            # Generate sine wave
            import numpy as np
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = np.sin(2 * np.pi * frequency * t)
            
            # Convert to 16-bit integer
            tone = (tone * 32767).astype(np.int16)
            
            # Save as temporary WAV file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                import wave
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(tone.tobytes())
                
                # Play the audio
                try:
                    pygame.mixer.music.load(temp_file.name)
                    pygame.mixer.music.play()
                    
                    # Wait for audio to finish with timeout
                    import time
                    start_time = time.time()
                    timeout = 5.0  # 5 second timeout for mock speech
                    
                    while pygame.mixer.music.get_busy() and (time.time() - start_time) < timeout:
                        time.sleep(0.1)
                    
                    # Force stop if still playing
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                        print("[Voice] Mock audio playback stopped (timeout)")
                        
                except Exception as e:
                    print(f"[Voice] Error playing audio: {e}")
                finally:
                    # Clean up temporary file
                    import os
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                        
        except Exception as e:
            print(f"[Voice] Error in mock speech: {e}")
            # Fallback: just wait
            import time
            time.sleep(min(len(text) * 0.05, 2.0))
    
    def play_audio_file(self, file_path: str):
        """Play an audio file."""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Wait for audio to finish with timeout
            start_time = time.time()
            timeout = 10.0  # 10 second timeout for audio files
            
            while pygame.mixer.music.get_busy() and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            # Force stop if still playing
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                print("[Voice] Audio file playback stopped (timeout)")
                
        except Exception as e:
            print(f"[Voice] Error playing audio file: {e}")
    
    def record_audio(self, duration: float = 5.0, filename: str = "recording.wav"):
        """Record audio for a specified duration."""
        try:
            if not self.microphone:
                print("[Voice] No microphone available for recording")
                return False
            
            print(f"[Voice] Recording for {duration} seconds...")
            
            with self.microphone as source:
                audio = self.recognizer.record(source, duration=duration)
            
            # Save the recording
            with open(filename, "wb") as f:
                f.write(audio.get_wav_data())
            
            print(f"[Voice] Recording saved to {filename}")
            return True
            
        except Exception as e:
            print(f"[Voice] Error recording audio: {e}")
            return False
    
    def get_available_microphones(self) -> List[Dict[str, any]]:
        """Get list of available microphones."""
        try:
            mic_list = []
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    mic_list.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': device_info['defaultSampleRate']
                    })
            return mic_list
        except Exception as e:
            print(f"[Voice] Error getting microphone list: {e}")
            return []
    
    def set_microphone(self, device_index: int):
        """Set the microphone device to use."""
        try:
            mic_list = self.get_available_microphones()
            if any(mic['index'] == device_index for mic in mic_list):
                self.microphone = sr.Microphone(device_index=device_index)
                print(f"[Voice] Microphone set to device {device_index}")
                return True
            else:
                print(f"[Voice] Invalid microphone device index: {device_index}")
                return False
        except Exception as e:
            print(f"[Voice] Error setting microphone: {e}")
            return False
    
    def cleanup(self):
        """Clean up audio resources."""
        try:
            self.stop_listening()
            
            if hasattr(self, 'audio'):
                self.audio.terminate()
            
            pygame.mixer.quit()
            
            print("[Voice] Audio resources cleaned up")
            
        except Exception as e:
            print(f"[Voice] Error during cleanup: {e}")
    
    def _pre_warm_elevenlabs(self):
        """Pre-warm ElevenLabs client for faster responses."""
        try:
            from elevenlabs import ElevenLabs
            from config import Config
            
            if Config.ELEVENLABS_API_KEY and Config.ELEVENLABS_API_KEY != "your_elevenlabs_api_key_here":
                print("[Voice] Pre-warming ElevenLabs client for faster responses...")
                self._elevenlabs_client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
                self._voice_id = Config.VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
                print(f"[Voice] ElevenLabs client pre-warmed with voice ID: {self._voice_id}")
            else:
                print("[Voice] ElevenLabs API key not configured, skipping pre-warm")
                
        except Exception as e:
            print(f"[Voice] Error pre-warming ElevenLabs: {e}")
    
    def _get_elevenlabs_client(self):
        """Get pre-warmed ElevenLabs client or create new one."""
        if self._elevenlabs_client:
            return self._elevenlabs_client
        
        # Fallback to creating new client
        from elevenlabs import ElevenLabs
        from config import Config
        return ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
