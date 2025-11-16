import threading
import time
import tempfile
import os
import numpy as np
import wave
import pyaudio
import pygame
import speech_recognition as sr

from typing import Optional, Callable, List, Dict
from config import Config


class VoiceHandlerV2:
    """
    Voice handler inspired by the reference chatbot pipeline:
    - Opens a raw PyAudio stream and performs RMS-based VAD
    - Keeps the mic hot until the user stops speaking
    - Blocks listening while playback runs to avoid echo
    """

    FRAME_MS = 30
    MIN_SPEECH_MS = 300
    END_SILENCE_MS = int(os.getenv('END_SILENCE_MS', '400'))  # Configurable silence duration before processing (ms)
    MAX_RECORDING_MS = 15000
    BASE_THRESHOLD = 120.0
    POST_PROCESSING_COOLDOWN_MS = 1000  # Cooldown after processing audio to prevent immediate re-triggering

    def __init__(self):
        self.callback: Optional[Callable[[str], None]] = None
        self.robot_state = None

        self.recognizer = sr.Recognizer()
        self.audio = pyaudio.PyAudio()
        self.stream = None

        self.sample_rate = Config.SAMPLE_RATE
        self.channels = 1
        self.format = pyaudio.paInt16

        self.is_listening = False
        self.listen_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        self._playback_active = False
        self._playback_end_time = 0.0
        self._last_processing_time = 0.0  # Track when we last processed audio
        self._last_callback_time = 0.0  # Track when we last called the callback

        self._elevenlabs_client = None
        self._voice_id = None

        self._init_stream()
        self._pre_warm_elevenlabs()

    # ------------------------------------------------------------------ setup
    def _init_stream(self):
        """Open a PyAudio input stream, trying several rate/channel combos."""
        device_candidates: List[Optional[int]] = []
        if Config.MICROPHONE_INDEX is not None:
            device_candidates.append(Config.MICROPHONE_INDEX)
        try:
            default_idx = int(self.audio.get_default_input_device_info().get("index", 0))
            if default_idx not in device_candidates:
                device_candidates.append(default_idx)
        except Exception:
            pass
        if not device_candidates:
            device_candidates.append(None)

        for device_index in device_candidates:
            info = None
            try:
                info = (
                    self.audio.get_device_info_by_index(device_index)
                    if device_index is not None
                    else self.audio.get_default_input_device_info()
                )
            except Exception:
                pass
            max_channels = int(info["maxInputChannels"]) if info else 1
            default_rate = int(info["defaultSampleRate"]) if info else Config.SAMPLE_RATE

            rate_options = list(dict.fromkeys([Config.SAMPLE_RATE, default_rate, 16000, 44100, 48000]))
            channel_options = [1]
            if max_channels >= 2:
                channel_options.append(2)

            for rate in rate_options:
                for ch in channel_options:
                    if ch > max_channels:
                        continue
                    try:
                        self.stream = self.audio.open(
                            format=self.format,
                            channels=ch,
                            rate=rate,
                            input=True,
                            frames_per_buffer=int(rate * self.FRAME_MS / 1000),
                            input_device_index=device_index,
                        )
                        self.sample_rate = rate
                        self.channels = ch
                        print(f"[VoiceV2] Mic stream opened at {rate}Hz/{ch}ch (device={device_index})")
                        break
                    except Exception as e:
                        print(f"[VoiceV2] Mic stream failed for {rate}Hz/{ch}ch: {e}")
                if self.stream:
                    break

        if not self.stream:
            raise RuntimeError("Unable to open microphone stream. Adjust MIC settings or hardware.")

        self._calibrate_noise_floor()

        try:
            pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=self.channels)
            print("[VoiceV2] Pygame mixer initialized")
        except Exception as e:
            print(f"[VoiceV2] Failed to initialize pygame mixer: {e}")

    def _calibrate_noise_floor(self):
        ambient = []
        frame_bytes = int(self.sample_rate * self.FRAME_MS / 1000) * self.channels * 2
        for _ in range(20):
            data = self.stream.read(frame_bytes, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            ambient.append(np.sqrt(np.mean(samples * samples)))
        self.noise_floor = float(np.median(ambient)) if ambient else 50.0
        print(f"[VoiceV2] Noise floor calibrated to {self.noise_floor:.1f}")

    # ------------------------------------------------------------------ public API
    def set_callback(self, callback: Callable[[str], None]):
        self.callback = callback

    def set_robot_state(self, robot_state):
        self.robot_state = robot_state

    def start_listening(self):
        if self.is_listening:
            return
        self.is_listening = True
        self._stop_event.clear()
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        print("[VoiceV2] Listening for voice input...")

    def stop_listening(self):
        self.is_listening = False
        self._stop_event.set()
        if self.listen_thread:
            self.listen_thread.join(timeout=1)
        print("[VoiceV2] Listening stopped")

    def speak_text(self, text: str):
        if self._playback_active or not text:
            return
        self._playback_active = True
        try:
            self._simulate_speech(text)
        finally:
            pygame.mixer.music.stop()
            self._playback_active = False
            self._playback_end_time = time.time() + max(Config.SPEAKER_COOLDOWN, len(text) * 0.05)

    # ------------------------------------------------------------------ capture loop
    def _listen_loop(self):
        frame_bytes = int(self.sample_rate * self.FRAME_MS / 1000) * self.channels * 2
        # Use a higher threshold multiplier to reduce false positives from background noise
        threshold = max(self.BASE_THRESHOLD, self.noise_floor * 2.5)

        while not self._stop_event.is_set():
            if self._should_block_listening():
                time.sleep(0.05)
                continue

            # Cooldown period after processing audio to prevent immediate re-triggering
            time_since_last_processing = (time.time() * 1000) - (self._last_processing_time * 1000)
            if time_since_last_processing < self.POST_PROCESSING_COOLDOWN_MS:
                time.sleep(0.05)
                continue

            try:
                chunk = self.stream.read(frame_bytes, exception_on_overflow=False)
            except Exception as e:
                print(f"[VoiceV2] Stream read error: {e}")
                time.sleep(0.1)
                continue

            samples = np.frombuffer(chunk, dtype=np.int16).astype(np.float32)
            rms = float(np.sqrt(np.mean(samples * samples)))

            if rms > threshold:
                buffer = bytearray(chunk)
                speech_ms = self.FRAME_MS
                silence_ms = 0
                total_ms = self.FRAME_MS

                while total_ms < self.MAX_RECORDING_MS and not self._stop_event.is_set():
                    if self._should_block_listening():
                        time.sleep(0.05)
                        continue
                    chunk = self.stream.read(frame_bytes, exception_on_overflow=False)
                    samples = np.frombuffer(chunk, dtype=np.int16).astype(np.float32)
                    rms = float(np.sqrt(np.mean(samples * samples)))
                    buffer.extend(chunk)
                    total_ms += self.FRAME_MS

                    if rms < threshold:
                        silence_ms += self.FRAME_MS
                    else:
                        silence_ms = 0
                        speech_ms += self.FRAME_MS

                    if silence_ms >= self.END_SILENCE_MS and speech_ms >= self.MIN_SPEECH_MS:
                        break

                if buffer:
                    audio_data = sr.AudioData(bytes(buffer), self.sample_rate, 2)
                    self._last_processing_time = time.time()  # Mark when we start processing
                    threading.Thread(
                        target=self._process_audio,
                        args=(audio_data,),
                        daemon=True
                    ).start()

    def _process_audio(self, audio: sr.AudioData):
        if self._should_block_listening():
            return
        
        # Debounce: Don't process if we just called the callback recently (within 1 second)
        current_time = time.time()
        if current_time - self._last_callback_time < 1.0:
            return
        
        try:
            text = self.recognizer.recognize_google(audio)
            if text and self.callback:
                print(f"[VoiceV2] Recognized: {text}")
                self._last_callback_time = current_time
                self.callback(text)
        except sr.UnknownValueError:
            print("[VoiceV2] Could not understand audio")
        except sr.RequestError as e:
            print(f"[VoiceV2] Speech service error: {e}")
        except Exception as e:
            print(f"[VoiceV2] Processing error: {e}")

    def _should_block_listening(self) -> bool:
        now = time.time()
        if self._playback_active or now < self._playback_end_time:
            return True
        if self.robot_state and getattr(self.robot_state, "is_paused", False):
            return True
        return False

    # ------------------------------------------------------------------ playback helpers
    def _simulate_speech(self, text: str):
        print(f"[VoiceV2] Speaking: {text}")
        start = time.time()
        try:
            if self._should_use_real_tts():
                self._generate_real_speech(text)
            else:
                self._generate_mock_speech(text)
        except Exception as e:
            print(f"[VoiceV2] Speech generation error: {e}")
            time.sleep(min(len(text) * 0.05, 2.0))
        finally:
            if time.time() - start > 15:
                print("[VoiceV2] Warning: speech generation exceeded timeout")

    def _should_use_real_tts(self) -> bool:
        return (
            Config.ELEVENLABS_API_KEY
            and Config.ELEVENLABS_API_KEY != "your_elevenlabs_api_key_here"
            and not Config.DEV_MODE
        )

    def _generate_real_speech(self, text: str):
        from elevenlabs import ElevenLabs

        client = self._get_elevenlabs_client()
        voice_id = self._voice_id or Config.VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            output_format="mp3_44100_64",
            model_id="eleven_multilingual_v2",
            voice_settings={"stability": 0.5, "similarity_boost": 0.5},
        )
        audio_bytes = b"".join(audio_stream)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp.write(audio_bytes)
            path = tmp.name
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
        finally:
            pygame.mixer.music.stop()
            try:
                os.unlink(path)
            except Exception:
                pass

    def _generate_mock_speech(self, text: str):
        duration = max(1.0, min(len(text) * 0.05, 5.0))
        sample_rate = 44100
        frequency = 440
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            with wave.open(tmp.name, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(tone.tobytes())
            path = tmp.name
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
        finally:
            pygame.mixer.music.stop()
            try:
                os.unlink(path)
            except Exception:
                pass

    # ------------------------------------------------------------------ utilities
    def cleanup(self):
        try:
            self.stop_listening()
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if hasattr(self, "audio"):
                self.audio.terminate()
            pygame.mixer.quit()
            print("[VoiceV2] Resources cleaned up")
        except Exception as e:
            print(f"[VoiceV2] Cleanup error: {e}")

    def _pre_warm_elevenlabs(self):
        try:
            from elevenlabs import ElevenLabs
            if Config.ELEVENLABS_API_KEY and Config.ELEVENLABS_API_KEY != "your_elevenlabs_api_key_here":
                print("[VoiceV2] Pre-warming ElevenLabs client...")
                self._elevenlabs_client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
                self._voice_id = Config.VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
        except Exception as e:
            print(f"[VoiceV2] ElevenLabs pre-warm failed: {e}")

    def _get_elevenlabs_client(self):
        if self._elevenlabs_client:
            return self._elevenlabs_client
        from elevenlabs import ElevenLabs
        return ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)

