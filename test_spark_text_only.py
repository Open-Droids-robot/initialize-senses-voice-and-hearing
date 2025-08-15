#!/usr/bin/env python3
"""
Text-only test script for SPARK Robot Assistant.
Tests AI responses without voice complications.
"""

import sys
import asyncio
sys.path.insert(0, 'src')

from config import Config
from persona import RobotPersona
from robot_state import RobotState
from conversation_graph import ConversationGraph

async def test_text_conversation():
    """Test text conversation with SPARK."""
    print("🤖 SPARK Text-Only Conversation Test")
    print("=" * 50)
    print("This test verifies AI responses without voice complications.")
    print()
    
    try:
        # Initialize components
        print("📝 Initializing SPARK...")
        persona = RobotPersona()
        robot_state = RobotState()
        conversation_graph = ConversationGraph(robot_state, persona)
        
        print("✅ SPARK initialized successfully!")
        print()
        
        # Test questions
        test_questions = [
            "Hello SPARK, how are you today?",
            "What is artificial intelligence?",
            "Can you tell me a joke?",
            "What's your favorite color?",
            "Explain quantum computing in simple terms"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"🎯 Test {i}: {question}")
            print("-" * 40)
            
            try:
                await conversation_graph.run_conversation(question)
                print("✅ Response generated successfully")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print()
            await asyncio.sleep(1)  # Brief pause between questions
        
        print("🎉 All text conversation tests completed!")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")

def main():
    """Main function."""
    print("🚀 Starting SPARK Text-Only Test...")
    asyncio.run(test_text_conversation())

if __name__ == "__main__":
    main()
