#!/usr/bin/env python3
"""
Test SPARK's voice output functionality
"""

import sys
import os
sys.path.insert(0, 'src')

from voice_handler import VoiceHandler
from config import Config

def test_voice_output():
    """Test SPARK's voice output."""
    print("🎤 Testing SPARK's Voice Output")
    print("=" * 50)
    
    # Initialize voice handler
    print("📝 Initializing voice handler...")
    voice_handler = VoiceHandler()
    print("✅ Voice handler initialized!")
    
    # Test text
    test_text = "Hello! I am SPARK, your witty robot assistant. *beep* *whirr*"
    print(f"\n🎯 Testing voice output with: '{test_text}'")
    
    # Test speech generation
    print("\n🔊 Generating speech...")
    voice_handler._simulate_speech(test_text)
    
    print("\n✅ Voice output test completed!")

if __name__ == "__main__":
    test_voice_output()
