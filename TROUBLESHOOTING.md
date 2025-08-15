# 🚨 Troubleshooting Guide

Common issues and solutions for SPARK Robot Assistant.

## 📦 Package Installation Issues

### SpeechRecognition Package Not Found

**Error**: `ERROR: No matching distribution found for speech_recognition>=3.10.0`

**Solution**: The package name is case-sensitive. Use:
```bash
pip install SpeechRecognition
```

### PyAudio Installation Fails

**Error**: `fatal error: 'portaudio.h' file not found`

**Solution**: Install system dependencies first:

**Ubuntu/Debian**:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**macOS**:
```bash
brew install portaudio
```

**Windows**: Download pre-compiled wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

### LangGraph Import Error

**Error**: `ModuleNotFoundError: No module named 'langgraph'`

**Solution**: Install with specific version:
```bash
pip install langgraph==0.6.5
```

## 🎤 Audio Issues

### No Microphone Detected

**Symptoms**: "No microphone available" or "Audio initialization failed"

**Solutions**:
1. Check microphone permissions
2. List available devices:
   ```bash
   python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
   ```
3. Set correct device index in `.env`:
   ```
   MICROPHONE_INDEX=1  # Try different numbers
   ```

### Audio Playback Not Working

**Symptoms**: No sound output or pygame errors

**Solutions**:
1. Check system volume
2. Verify audio drivers
3. Test with simple pygame:
   ```bash
   python -c "import pygame; pygame.mixer.init(); print('Audio OK')"
   ```

## 🐳 Docker Issues

### Audio Devices Not Accessible

**Error**: "No audio devices found" in container

**Solutions**:
1. Ensure audio devices are mounted:
   ```bash
   docker run --device /dev/snd:/dev/snd --privileged spark_robot
   ```
2. Check host audio system:
   ```bash
   aplay -l  # List audio devices
   ```

### Permission Denied

**Error**: "Permission denied" for audio devices

**Solution**: Run with proper permissions:
```bash
docker run --group-add audio --device /dev/snd:/dev/snd spark_robot
```

## 🐍 Python Environment Issues

### Import Errors

**Error**: `ModuleNotFoundError` for local modules

**Solutions**:
1. Ensure you're in the correct directory
2. Check Python path:
   ```bash
   python -c "import sys; print(sys.path)"
   ```
3. Run from project root:
   ```bash
   cd robot_assistant
   python src/main.py
   ```

### Virtual Environment Issues

**Error**: Packages not found despite installation

**Solutions**:
1. Activate virtual environment:
   ```bash
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
2. Verify installation:
   ```bash
   pip list | grep -E "(langgraph|openai|elevenlabs)"
   ```

## 🔧 Runtime Issues

### Conversation Graph Errors

**Error**: `StateGraph` or workflow errors

**Solutions**:
1. Check LangGraph version compatibility
2. Verify state structure matches expected format
3. Run with debug logging:
   ```
   LOG_LEVEL=DEBUG python src/main.py
   ```

### Memory Issues

**Error**: Out of memory or slow performance

**Solutions**:
1. Reduce conversation history size in `.env`:
   ```
   MAX_CONVERSATION_HISTORY=5
   ```
2. Monitor memory usage
3. Restart application periodically

### Keyboard Input Not Working

**Error**: Terminal controls not responding

**Solutions**:
1. Ensure terminal has focus
2. Check for conflicting keyboard shortcuts
3. Try different terminal emulator
4. Verify Python version compatibility

## 🚀 Alternative Installation Methods

### Minimal Installation

For systems with limited resources or package conflicts:

```bash
# Install only essential packages
pip install python-dotenv numpy langgraph openai elevenlabs

# Run in text-only mode (no audio)
export AUDIO_DISABLED=true
python src/main.py
```

### Manual Package Installation

If automatic installation fails:

```bash
# Install packages one by one
pip install python-dotenv
pip install numpy
pip install langgraph
pip install openai
pip install elevenlabs
pip install SpeechRecognition
pip install pygame
pip install pydub
pip install pyaudio
```

### System Package Manager

Some packages may be available through system package managers:

**Ubuntu/Debian**:
```bash
sudo apt-get install python3-speechrecognition python3-pygame python3-pyaudio
```

**macOS**:
```bash
brew install portaudio
```

## 📋 Diagnostic Commands

### System Information
```bash
# Python version
python --version

# Audio devices
aplay -l  # Linux
system_profiler SPAudioDataType  # macOS

# Package versions
pip list | grep -E "(langgraph|openai|elevenlabs|SpeechRecognition)"
```

### Test Individual Components
```bash
# Test speech recognition
python -c "import speech_recognition as sr; print('SR OK')"

# Test pygame
python -c "import pygame; pygame.init(); print('Pygame OK')"

# Test pyaudio
python -c "import pyaudio; print('PyAudio OK')"
```

## 🆘 Getting Help

If you're still experiencing issues:

1. **Check the logs**: Look for error messages in the terminal output
2. **Run tests**: Use `python test_installation.py` to identify specific problems
3. **Check dependencies**: Verify all required packages are installed
4. **System compatibility**: Ensure your system meets the requirements
5. **Create issue**: Include error messages, system info, and steps to reproduce

## 🔍 Common Workarounds

### Audio Not Working
- Run in text-only mode
- Use external audio devices
- Check system audio settings

### Package Conflicts
- Use virtual environment
- Install packages individually
- Try different package versions

### Performance Issues
- Reduce conversation history
- Disable non-essential features
- Monitor system resources

---

*"I'm not broken, I'm just experiencing a temporary malfunction... *beep*"* - SPARK 🤖
