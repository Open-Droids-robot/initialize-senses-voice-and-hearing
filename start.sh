#!/bin/bash

# SPARK Robot Assistant Startup Script
# This script sets up the environment and starts the robot assistant

echo "🤖 Starting SPARK Robot Assistant..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    echo "❌ Error: Please run this script from the robot_assistant directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: src/main.py"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8+ required, found Python $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
python install_deps.py

if [ $? -ne 0 ]; then
    echo "❌ Dependency installation failed"
    echo "💡 Try running manually: python install_deps.py"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Created .env file from env.example"
        echo "💡 Edit .env to add your API keys (optional for testing)"
    else
        echo "⚠️  No env.example found, creating basic .env"
        cat > .env << EOF
# Robot Assistant Environment Configuration
OPENAI_API_KEY=mock_openai_key
ELEVENLABS_API_KEY=mock_elevenlabs_key
VOICE_ID=mock_voice_id
MICROPHONE_INDEX=0
WAKE_WORD=hey_spark
LOG_LEVEL=INFO
EOF
    fi
fi

# Run installation test
echo "🧪 Running installation test..."
python test_installation.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! Starting SPARK..."
    echo "======================================"
    echo "💡 Press 'h' for help, 'q' to quit"
    echo ""
    
    # Start the robot assistant
    python src/main.py
else
    echo "❌ Installation test failed. Please fix the issues above."
    exit 1
fi
