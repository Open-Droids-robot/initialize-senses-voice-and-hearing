#!/usr/bin/env python3
"""
Test script to verify SPARK's API integration.
"""

import sys
import asyncio
sys.path.insert(0, 'src')

from config import Config
from persona import RobotPersona
from robot_state import RobotState
from conversation_graph import ConversationGraph

def test_api_configuration():
    """Test if API keys are properly configured."""
    print("🔑 Testing API Configuration")
    print("=" * 40)
    
    # Check OpenAI
    openai_key = Config.OPENAI_API_KEY
    if openai_key and openai_key != "your_openai_api_key_here":
        print(f"✅ OpenAI API Key: {openai_key[:10]}...")
        print(f"✅ OpenAI Model: {Config.OPENAI_MODEL}")
    else:
        print("❌ OpenAI API Key: Not configured")
        print("   Get one at: https://platform.openai.com/api-keys")
    
    # Check ElevenLabs
    elevenlabs_key = Config.ELEVENLABS_API_KEY
    if elevenlabs_key and elevenlabs_key != "your_elevenlabs_api_key_here":
        print(f"✅ ElevenLabs API Key: {elevenlabs_key[:10]}...")
        print(f"✅ Voice ID: {Config.VOICE_ID}")
    else:
        print("❌ ElevenLabs API Key: Not configured")
        print("   Get one at: https://elevenlabs.io/")
    
    # Check dev mode
    dev_mode = Config.DEV_MODE
    print(f"✅ Dev Mode: {dev_mode}")
    
    if dev_mode:
        print("⚠️  Note: Dev mode is enabled - using mock responses")
    else:
        print("🎯 Dev mode disabled - using real APIs")
    
    print()

def test_openai_integration():
    """Test OpenAI API integration."""
    print("🧠 Testing OpenAI Integration")
    print("=" * 40)
    
    try:
        # Check if openai module is available
        import openai
        print("✅ OpenAI module available")
        
        # Check if API key is configured
        if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "your_openai_api_key_here":
            print("❌ OpenAI API key not configured")
            return False
        
        # Test API connection
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Simple test call
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "user", "content": "Say 'Hello SPARK' in 5 words or less"}
            ],
            max_tokens=20
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI API test successful!")
        print(f"   Response: '{result}'")
        return True
        
    except ImportError:
        print("❌ OpenAI module not installed")
        print("   Install with: pip install openai")
        return False
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def test_elevenlabs_integration():
    """Test ElevenLabs API integration."""
    print("🎤 Testing ElevenLabs Integration")
    print("=" * 40)
    
    try:
        # Check if elevenlabs module is available
        from elevenlabs import ElevenLabs
        print("✅ ElevenLabs module available")
        
        # Check if API key is configured
        if not Config.ELEVENLABS_API_KEY or Config.ELEVENLABS_API_KEY == "your_elevenlabs_api_key_here":
            print("❌ ElevenLabs API key not configured")
            return False
        
        # Test API connection
        client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
        
        # Simple test call
        voice_id = Config.VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id,
            text="Hello, this is a test of the ElevenLabs API.",
            output_format="mp3_44100_128",
            model_id="eleven_multilingual_v2"
        )
        
        print(f"✅ ElevenLabs API test successful!")
        print(f"   Audio generated: Audio stream ready")
        print(f"   Voice ID: {voice_id}")
        return True
        
    except ImportError:
        print("❌ ElevenLabs module not installed")
        print("   Install with: pip install elevenlabs")
        return False
    except Exception as e:
        print(f"❌ ElevenLabs API test failed: {e}")
        return False

async def test_conversation_workflow():
    """Test the conversation workflow with real APIs."""
    print("🔄 Testing Conversation Workflow")
    print("=" * 40)
    
    try:
        # Initialize components
        persona = RobotPersona()
        robot_state = RobotState()
        conversation_graph = ConversationGraph(robot_state, persona)
        
        print("✅ Components initialized")
        
        # Test conversation
        test_input = "What is artificial intelligence?"
        print(f"🎯 Testing with: '{test_input}'")
        
        await conversation_graph.run_conversation(test_input)
        
        print("✅ Conversation workflow test completed")
        return True
        
    except Exception as e:
        print(f"❌ Conversation workflow test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 SPARK API Integration Test Suite")
    print("=" * 50)
    print("This will test your API configuration and integration.")
    print()
    
    # Test 1: Configuration
    test_api_configuration()
    
    # Test 2: OpenAI
    openai_success = test_openai_integration()
    
    # Test 3: ElevenLabs
    elevenlabs_success = test_elevenlabs_integration()
    
    # Test 4: Conversation workflow
    print("🔄 Testing conversation workflow...")
    conversation_success = asyncio.run(test_conversation_workflow())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"OpenAI Integration: {'✅ PASS' if openai_success else '❌ FAIL'}")
    print(f"ElevenLabs Integration: {'✅ PASS' if elevenlabs_success else '❌ FAIL'}")
    print(f"Conversation Workflow: {'✅ PASS' if conversation_success else '❌ FAIL'}")
    
    if openai_success and conversation_success:
        print("\n🎉 SPARK is ready with real AI intelligence!")
        print("   You can now have intelligent conversations!")
    else:
        print("\n⚠️  Some tests failed. Check the configuration:")
        print("   1. Verify your API keys in .env file")
        print("   2. Set DEV_MODE=false in .env file")
        print("   3. Install required packages: pip install openai elevenlabs")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
