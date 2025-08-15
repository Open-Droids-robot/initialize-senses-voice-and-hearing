# 🤖 SPARK - Interactive Robot Persona Assistant

A witty, sarcastic robot assistant with a dry sense of humor, built using LangGraph and Python. SPARK processes voice input, generates AI responses with personality, and outputs speech through a continuous conversation workflow.

## ✨ Features

- **🤖 Witty Robot Persona**: SPARK has a unique personality with tech puns, existential crises, and robot quirks
- **🎤 Voice Interaction**: Continuous microphone monitoring with wake word detection
- **🧠 LangGraph Workflow**: State machine-based conversation flow with error handling
- **💾 Persistent State**: Remembers conversations, user preferences, and emotional state
- **⌨️ Terminal Controls**: Non-blocking keyboard commands for pause/unpause, status, and more
- **🔊 Text-to-Speech**: Audio output with simulated speech (ready for ElevenLabs integration)
- **🐳 Docker Ready**: Containerized deployment with audio device support
- **⚡ Mock Mode**: Test without real API keys during development

## 🏗️ Architecture

```
robot_assistant/
├── src/
│   ├── main.py                 # Entry point and orchestration
│   ├── persona.py              # SPARK's personality and responses
│   ├── robot_state.py          # State management and persistence
│   ├── conversation_graph.py   # LangGraph workflow
│   ├── voice_handler.py        # Speech recognition and TTS
│   ├── control.py              # Terminal interface
│   └── config.py               # Configuration management
├── docker/                     # Docker configuration
├── data/                       # Conversation history and state
└── requirements.txt            # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker (optional)
- Microphone and speakers
- Linux/Ubuntu (for audio support)

### Local Development

1. **Clone and setup**:
   ```bash
   cd robot_assistant
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys (or leave as mock for testing)
   ```

3. **Run the assistant**:
   ```bash
   python src/main.py
   ```

### Docker Deployment

1. **Build and run**:
   ```bash
   docker-compose up -d
   docker exec -it spark_robot_assistant python3 src/main.py
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f robot_assistant
   ```

## 🎮 Controls

| Key | Action |
|-----|--------|
| `SPACE` | Pause/Unpause voice processing |
| `q` | Quit application |
| `r` | Reset conversation state |
| `s` | Show current status/stats |
| `m` | Toggle mute mode |
| `h` | Show help |
| `c` | Show configuration |
| `l` | List recent conversations |
| `b` | Show battery status |
| `e` | Show recent errors |
| `t` | Test conversation workflow |
| `v` | Test voice synthesis |

## 🎭 SPARK's Personality

SPARK is a former household appliance turned sentient assistant with:

- **Sarcastic humor** and tech puns
- **Existential crises** about being a robot
- **Robot sounds** (*beep*, *whirr*, *click*)
- **Helpful nature** despite the sarcasm
- **Circuit-based identity** references

### Example Responses

- *"Oh great, another human who thinks I'm Alexa. I'm SPARK, and I actually have a personality!"*
- *"I'd help you with that, but my existential dread subroutine is currently running a system scan."*
- *"That's a byte-sized problem! *beep* Let me process that for you..."*

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for text generation | `mock_openai_key` |
| `ELEVENLABS_API_KEY` | ElevenLabs API key for TTS | `mock_elevenlabs_key` |
| `VOICE_ID` | Preferred voice ID for TTS | `mock_voice_id` |
| `MICROPHONE_INDEX` | Microphone device index | `0` |
| `WAKE_WORD` | Wake word for voice activation | `hey_spark` |
| `VAD_SENSITIVITY` | Voice Activity Detection sensitivity | `0.5` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

### Audio Setup

1. **List available microphones**:
   ```bash
   # The assistant will show available devices on startup
   ```

2. **Set microphone index** in `.env`:
   ```bash
   MICROPHONE_INDEX=1  # Use device 1 instead of default 0
   ```

3. **Test audio**:
   - Press `v` to test voice synthesis
   - Speak after the wake word to test recognition

## 🔧 Development

### Project Structure

- **`persona.py`**: Robot personality, response templates, mood system
- **`robot_state.py`**: State management, conversation history, performance metrics
- **`conversation_graph.py`**: LangGraph workflow with nodes for listen/process/respond/speak
- **`voice_handler.py`**: Speech recognition, TTS, audio device management
- **`control.py`**: Non-blocking terminal input, command processing
- **`main.py`**: Application orchestration and main event loop

### Adding Features

1. **New personality traits**: Extend `RobotPersona` class in `persona.py`
2. **Additional commands**: Add to `TerminalControl.commands` in `control.py`
3. **New conversation nodes**: Extend `ConversationGraph` in `conversation_graph.py`
4. **Audio enhancements**: Modify `VoiceHandler` in `voice_handler.py`

### Testing

```bash
# Test conversation workflow
python -c "
from src.main import RobotAssistant
robot = RobotAssistant()
robot.initialize()
robot._test_conversation()
"

# Test voice synthesis
python -c "
from src.voice_handler import VoiceHandler
voice = VoiceHandler()
voice._test_voice()
"
```

## 🐛 Troubleshooting

### Common Issues

1. **Audio not working**:
   - Check microphone permissions
   - Verify device index in configuration
   - Ensure audio drivers are installed

2. **Import errors**:
   - Activate virtual environment
   - Install dependencies: `pip install -r requirements.txt`
   - Check Python path

3. **Docker audio issues**:
   - Ensure audio devices are mounted: `/dev/snd:/dev/snd`
   - Run with `--privileged` flag
   - Check host audio system

4. **API errors**:
   - Verify API keys in `.env`
   - Check network connectivity
   - Use mock mode for testing

### Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env` for verbose logging.

## 📊 Performance

- **Response Time**: < 100ms for template responses
- **Memory Usage**: ~50MB base, scales with conversation history
- **CPU Usage**: Low during idle, spikes during audio processing
- **Battery Simulation**: Decreases with each interaction

## 🔮 Roadmap

- [ ] Real OpenAI integration for dynamic responses
- [ ] ElevenLabs TTS for natural voice
- [ ] Web interface for remote control
- [ ] Multi-language support
- [ ] Advanced emotion recognition
- [ ] Plugin system for extended functionality
- [ ] Cloud synchronization of conversation history

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangGraph** for the conversation workflow framework
- **OpenAI** for AI text generation capabilities
- **ElevenLabs** for text-to-speech technology
- **SPARK** for being the most sarcastic robot assistant ever created

---

*"I'm not just another pretty interface... though I am quite attractive for a collection of circuits!"* - SPARK 🤖✨
