#!/usr/bin/env python3
"""
Quick audio test script for SPARK Robot Assistant.
Tests if audio packages are working correctly.
"""

import sys

def test_imports():
    """Test if audio packages can be imported."""
    print("🧪 Testing audio package imports...")
    
    # Test PyAudio
    try:
        import pyaudio
        print("✅ PyAudio imported successfully")
        
        # Test PyAudio initialization
        try:
            audio = pyaudio.PyAudio()
            device_count = audio.get_device_count()
            print(f"   Audio devices found: {device_count}")
            
            # List input devices
            input_devices = []
            for i in range(device_count):
                try:
                    device_info = audio.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        input_devices.append({
                            'index': i,
                            'name': device_info['name'],
                            'channels': device_info['maxInputChannels']
                        })
                except:
                    continue
            
            print(f"   Input devices: {len(input_devices)}")
            for device in input_devices[:3]:  # Show first 3
                print(f"     {device['index']}: {device['name']} ({device['channels']} channels)")
            
            audio.terminate()
            
        except Exception as e:
            print(f"   ⚠️  PyAudio initialization failed: {e}")
            
    except ImportError as e:
        print(f"❌ PyAudio import failed: {e}")
        return False
    
    # Test SpeechRecognition
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition imported successfully")
        
        # Test microphone listing
        try:
            mic_list = sr.Microphone.list_microphone_names()
            print(f"   Microphones found: {len(mic_list)}")
            for i, name in enumerate(mic_list[:3]):  # Show first 3
                print(f"     {i}: {name}")
        except Exception as e:
            print(f"   ⚠️  Microphone listing failed: {e}")
            
    except ImportError as e:
        print(f"❌ SpeechRecognition import failed: {e}")
        return False
    
    # Test Pygame
    try:
        import pygame
        print("✅ Pygame imported successfully")
        
        # Test pygame initialization
        try:
            pygame.mixer.init()
            print("   Pygame mixer initialized successfully")
            pygame.mixer.quit()
        except Exception as e:
            print(f"   ⚠️  Pygame mixer initialization failed: {e}")
            
    except ImportError as e:
        print(f"❌ Pygame import failed: {e}")
        return False
    
    # Test Pydub
    try:
        import pydub
        print("✅ Pydub imported successfully")
    except ImportError as e:
        print(f"❌ Pydub import failed: {e}")
        return False
    
    return True

def test_audio_devices():
    """Test if audio devices are accessible."""
    print("\n🔍 Testing audio device access...")
    
    try:
        import pyaudio
        
        audio = pyaudio.PyAudio()
        
        # Test default input device
        try:
            default_input = audio.get_default_input_device_info()
            print(f"✅ Default input device: {default_input['name']}")
        except Exception as e:
            print(f"⚠️  No default input device: {e}")
        
        # Test default output device
        try:
            default_output = audio.get_default_output_device_info()
            print(f"✅ Default output device: {default_output['name']}")
        except Exception as e:
            print(f"⚠️  No default output device: {e}")
        
        audio.terminate()
        
    except Exception as e:
        print(f"❌ Audio device test failed: {e}")
        return False
    
    return True

def test_simple_audio():
    """Test basic audio functionality."""
    print("\n🎵 Testing basic audio functionality...")
    
    try:
        import pygame
        import numpy as np
        
        # Initialize pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        
        # Generate a simple beep sound
        sample_rate = 44100
        duration = 0.5
        frequency = 440  # A4 note
        
        # Generate sine wave
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(2 * np.pi * frequency * t)
        
        # Convert to 16-bit integer
        tone = (tone * 32767).astype(np.int16)
        
        # Save as temporary WAV file
        import tempfile
        import wave
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(tone.tobytes())
            
            # Try to play the audio
            try:
                pygame.mixer.music.load(temp_file.name)
                pygame.mixer.music.play()
                
                # Wait for audio to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                print("✅ Audio playback test successful")
                
            except Exception as e:
                print(f"⚠️  Audio playback failed: {e}")
            finally:
                # Clean up temporary file
                import os
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
        
        pygame.mixer.quit()
        
    except Exception as e:
        print(f"❌ Audio functionality test failed: {e}")
        return False
    
    return True

def main():
    """Run all audio tests."""
    print("🎤 SPARK Robot Assistant - Audio Test")
    print("=" * 40)
    
    tests = [
        ("Package Imports", test_imports),
        ("Device Access", test_audio_devices),
        ("Audio Functionality", test_simple_audio)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Audio Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All audio tests passed! Audio features should work correctly.")
    elif passed >= 2:
        print("⚠️  Most audio tests passed. Some features may have limited functionality.")
    else:
        print("❌ Many audio tests failed. Audio features may not work properly.")
        print("💡 Check the troubleshooting guide for solutions.")
    
    return passed >= 2  # Consider it working if at least 2 tests pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
