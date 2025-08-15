#!/usr/bin/env python3
"""
Test script to check microphone access and audio devices.
"""

import sys
import os
sys.path.insert(0, 'src')

def test_audio_devices():
    """Test available audio devices."""
    print("🎤 Testing Audio Devices")
    print("=" * 40)
    
    # Test 1: Check system audio devices
    print("\n1️⃣  System Audio Devices:")
    print("-" * 20)
    
    try:
        import subprocess
        result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Recording devices found:")
            print(result.stdout)
        else:
            print("❌ No recording devices found")
            print("Error:", result.stderr)
    except FileNotFoundError:
        print("❌ 'arecord' command not found. Install alsa-utils:")
        print("   sudo apt install alsa-utils")
    
    # Test 2: Check playback devices
    print("\n2️⃣  Playback Devices:")
    print("-" * 20)
    
    try:
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Playback devices found:")
            print(result.stdout)
        else:
            print("❌ No playback devices found")
            print("Error:", result.stderr)
    except FileNotFoundError:
        print("❌ 'aplay' command not found")
    
    # Test 3: Check Python audio libraries
    print("\n3️⃣  Python Audio Libraries:")
    print("-" * 20)
    
    try:
        import pyaudio
        print("✅ PyAudio available")
        
        # List available devices
        p = pyaudio.PyAudio()
        print(f"📊 Total devices: {p.get_device_count()}")
        
        for i in range(p.get_device_count()):
            try:
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    print(f"🎤 Input Device {i}: {info['name']}")
                if info['maxOutputChannels'] > 0:
                    print(f"🔊 Output Device {i}: {info['name']}")
            except:
                pass
        p.terminate()
        
    except ImportError:
        print("❌ PyAudio not available")
        print("   Install: pip install pyaudio")
    except Exception as e:
        print(f"❌ PyAudio error: {e}")
    
    # Test 4: Check speech recognition
    print("\n4️⃣  Speech Recognition:")
    print("-" * 20)
    
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition available")
        
        # List available microphones
        print("📱 Available microphones:")
        for i, mic in enumerate(sr.Microphone.list_microphone_names()):
            print(f"   {i}: {mic}")
            
    except ImportError:
        print("❌ SpeechRecognition not available")
        print("   Install: pip install SpeechRecognition")
    except Exception as e:
        print(f"❌ SpeechRecognition error: {e}")
    
    # Test 5: Check user permissions
    print("\n5️⃣  User Permissions:")
    print("-" * 20)
    
    try:
        result = subprocess.run(['groups'], capture_output=True, text=True)
        if result.returncode == 0:
            groups = result.stdout.strip().split()
            if 'audio' in groups:
                print("✅ User is in 'audio' group")
            else:
                print("❌ User NOT in 'audio' group")
                print("   Add user to audio group:")
                print("   sudo usermod -a -G audio $USER")
                print("   (Then log out and back in)")
        else:
            print("❌ Could not check user groups")
    except Exception as e:
        print(f"❌ Permission check error: {e}")
    
    # Test 6: Test recording capability
    print("\n6️⃣  Test Recording:")
    print("-" * 20)
    
    try:
        import pyaudio
        import wave
        
        # Try to record a short audio sample
        print("🎤 Attempting to record 3 seconds...")
        print("   Speak into your microphone now!")
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 3
        
        p = pyaudio.PyAudio()
        
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        print("   Recording...")
        frames = []
        
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("   Recording complete!")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save the recorded audio
        with wave.open("test_recording.wav", 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        print("✅ Recording saved as 'test_recording.wav'")
        print("   File size:", os.path.getsize("test_recording.wav"), "bytes")
        
    except Exception as e:
        print(f"❌ Recording test failed: {e}")
        print("   This means microphone input won't work yet")

def main():
    """Main test function."""
    print("🎤 SPARK Microphone Test Suite")
    print("=" * 50)
    print("This will test your audio setup for microphone input.")
    print()
    
    test_audio_devices()
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. If you see ❌ errors above, fix them first")
    print("2. Make sure your microphone is connected and working")
    print("3. Run this test again to verify everything works")
    print("4. Then SPARK will be able to hear you!")
    print("=" * 50)

if __name__ == "__main__":
    main()
