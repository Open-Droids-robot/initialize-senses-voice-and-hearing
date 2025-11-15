import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration management for the robot assistant."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'mock_openai_key')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # ElevenLabs Configuration
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', 'mock_elevenlabs_key')
    VOICE_ID = os.getenv('VOICE_ID', 'mock_voice_id')
    
    # Audio Configuration
    MICROPHONE_INDEX = int(os.getenv('MICROPHONE_INDEX', '0'))
    SAMPLE_RATE = int(os.getenv('SAMPLE_RATE', '16000'))
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1024'))
    LISTEN_TIMEOUT = float(os.getenv('LISTEN_TIMEOUT', '1.0'))
    PHRASE_TIME_LIMIT = float(os.getenv('PHRASE_TIME_LIMIT', '10.0'))
    PAUSE_THRESHOLD = float(os.getenv('PAUSE_THRESHOLD', '0.5'))
    NON_SPEECH_DURATION = float(os.getenv('NON_SPEECH_DURATION', '0.3'))
    SPEAKER_COOLDOWN = float(os.getenv('SPEAKER_COOLDOWN', '0.8'))
    DYNAMIC_ENERGY = os.getenv('DYNAMIC_ENERGY', 'true').lower() == 'true'
    
    # Wake Word Configuration
    WAKE_WORD = os.getenv('WAKE_WORD', 'hey_spark').lower()
    
    # Audio Processing
    VAD_SENSITIVITY = float(os.getenv('VAD_SENSITIVITY', '0.5'))
    NOISE_REDUCTION = os.getenv('NOISE_REDUCTION', 'true').lower() == 'true'
    
    # Conversation Settings
    MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', '10'))
    RESPONSE_TIMEOUT = int(os.getenv('RESPONSE_TIMEOUT', '30'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'robot_assistant.log')
    
    # Development Mode
    DEV_MODE = os.getenv('DEV_MODE', 'true').lower() == 'true'
    ENABLE_WEB_SEARCH = os.getenv('ENABLE_WEB_SEARCH', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Validate configuration and return any issues."""
        issues = []
        
        if cls.OPENAI_API_KEY == 'mock_openai_key':
            issues.append("Using mock OpenAI API key - set OPENAI_API_KEY for real integration")
        
        if cls.ELEVENLABS_API_KEY == 'mock_elevenlabs_key':
            issues.append("Using mock ElevenLabs API key - set ELEVENLABS_API_KEY for real integration")
            
        return issues
    
    @classmethod
    def print_config(cls):
        """Print current configuration (hiding sensitive keys)."""
        print("=== Robot Assistant Configuration ===")
        print(f"OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"Voice ID: {cls.VOICE_ID}")
        print(f"Microphone Index: {cls.MICROPHONE_INDEX}")
        print(f"Sample Rate: {cls.SAMPLE_RATE}")
        print(f"Wake Word: {cls.WAKE_WORD}")
        print(f"VAD Sensitivity: {cls.VAD_SENSITIVITY}")
        print(f"Max Conversation History: {cls.MAX_CONVERSATION_HISTORY}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print("==================================")
