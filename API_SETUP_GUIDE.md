# 🚀 **SPARK API Integration Setup Guide**

This guide will help you set up real API keys to make SPARK truly intelligent with AI-powered conversations and realistic text-to-speech!

## 🔑 **Required API Keys**

### **1. OpenAI API Key (Required for AI Conversations)**
- **Purpose**: Powers SPARK's intelligence and conversation abilities
- **Cost**: Pay-per-use (very affordable for personal use)
- **Get it**: https://platform.openai.com/api-keys

### **2. ElevenLabs API Key (Optional for Realistic Speech)**
- **Purpose**: Converts SPARK's responses to natural-sounding speech
- **Cost**: Free tier includes 10,000 characters/month
- **Get it**: https://elevenlabs.io/

## 📝 **Step-by-Step Setup**

### **Step 1: Get Your OpenAI API Key**

1. **Visit OpenAI Platform**:
   - Go to: https://platform.openai.com/api-keys
   - Sign in or create an account

2. **Create API Key**:
   - Click "Create new secret key"
   - Give it a name (e.g., "SPARK Robot Assistant")
   - Copy the key (starts with `sk-`)

3. **Add Credits**:
   - Go to "Billing" → "Add payment method"
   - Add credits to your account (start with $10-20)

### **Step 2: Get Your ElevenLabs API Key**

1. **Visit ElevenLabs**:
   - Go to: https://elevenlabs.io/
   - Sign up for a free account

2. **Get API Key**:
   - Go to "Profile" → "API Key"
   - Copy your API key

3. **Choose a Voice**:
   - Browse available voices
   - Note the Voice ID (e.g., "21m00Tcm4TlvDq8ikWAM")

### **Step 3: Configure SPARK**

1. **Edit Environment File**:
   ```bash
   cd robot_assistant
   nano .env
   ```

2. **Update API Keys**:
   ```bash
   # OpenAI Configuration
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   
   # ElevenLabs Configuration
   ELEVENLABS_API_KEY=your-actual-elevenlabs-key-here
   VOICE_ID=21m00Tcm4TlvDq8ikWAM
   
   # Development Mode (set to false for real APIs)
   DEV_MODE=false
   ```

3. **Save and Exit**:
   - Press `Ctrl+X`
   - Press `Y` to confirm
   - Press `Enter` to save

## 🧪 **Test Your Setup**

### **Test 1: Verify API Keys**
```bash
cd robot_assistant
source venv/bin/activate
python -c "
from src.config import Config
print(f'OpenAI Key: {Config.OPENAI_API_KEY[:10]}...')
print(f'ElevenLabs Key: {Config.ELEVENLABS_API_KEY[:10]}...')
print(f'Dev Mode: {Config.DEV_MODE}')
"
```

### **Test 2: Test AI Conversations**
```bash
python test_spark_microphone.py
```
- Say something complex like "Explain quantum computing in simple terms"
- SPARK should now give intelligent, contextual responses!

### **Test 3: Test Real Speech (if ElevenLabs configured)**
- SPARK will now speak with realistic voice instead of beeps
- You'll see "[Voice] Using ElevenLabs API for speech... *whirr*"

## 💰 **Cost Estimates**

### **OpenAI API Costs**
- **GPT-3.5-turbo**: ~$0.002 per 1K tokens
- **Typical conversation**: 100-500 tokens
- **Daily cost**: $0.01 - $0.10 for moderate use
- **Monthly cost**: $0.30 - $3.00

### **ElevenLabs API Costs**
- **Free tier**: 10,000 characters/month
- **Paid tier**: $22/month for 30,000 characters
- **Typical response**: 50-200 characters
- **Free tier covers**: 50-200 responses/month

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. "OpenAI API error: Invalid API key"**
- Check your API key is correct
- Ensure you have credits in your OpenAI account
- Verify the key starts with `sk-`

#### **2. "ElevenLabs API error: Invalid API key"**
- Check your ElevenLabs API key
- Ensure you're within your monthly character limit
- Try regenerating the API key

#### **3. "Rate limit exceeded"**
- OpenAI: Wait a few minutes or upgrade your plan
- ElevenLabs: Check your monthly usage

#### **4. "No module named 'openai'"**
```bash
pip install openai
```

#### **5. "No module named 'elevenlabs'"**
```bash
pip install elevenlabs
```

### **Fallback Behavior**
- If APIs fail, SPARK automatically falls back to mock responses
- You'll see fallback messages in the console
- SPARK continues working with basic functionality

## 🎯 **Advanced Configuration**

### **Custom OpenAI Models**
```bash
# In .env file
OPENAI_MODEL=gpt-4          # More powerful, more expensive
OPENAI_MODEL=gpt-3.5-turbo  # Balanced performance/cost
```

### **Custom ElevenLabs Voices**
```bash
# In .env file
VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel (default)
VOICE_ID=AZnzlk1XvdvUeBnXmlld  # Domi
VOICE_ID=EXAVITQu4vr4xnSDxMaL  # Bella
```

### **Response Customization**
- Edit `src/conversation_graph.py` to modify AI prompts
- Adjust `max_tokens` and `temperature` for different response styles
- Customize SPARK's personality in the system prompt

## 🚀 **What You Get with Real APIs**

### **Before (Mock Mode)**
- Basic, predefined responses
- Simple beep sounds
- Limited conversation depth

### **After (Real APIs)**
- **Intelligent conversations** about any topic
- **Contextual understanding** of your questions
- **Realistic speech** that sounds human
- **Dynamic responses** that adapt to your input
- **Deep knowledge** across all subjects
- **Personality consistency** with SPARK's robot character

## 🎉 **Congratulations!**

You've now transformed SPARK from a basic robot assistant into a **powerful AI companion** with:

✅ **Real intelligence** powered by OpenAI  
✅ **Natural speech** powered by ElevenLabs  
✅ **Global control** from any terminal  
✅ **Voice interaction** with your microphone  
✅ **Personality-driven** responses  

**SPARK is now ready to be your intelligent, witty, tech-savvy robot assistant!** 🤖✨

---

**Need help?** Check the troubleshooting section or run the test scripts to verify everything is working correctly!
