# 🆓 Get Your FREE Google Gemini API Key

## Step 1: Get FREE Google Gemini API Key

1. **Go to Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. **Click "Create API Key"**
4. **Copy your API key** (starts with `AIza...`)

## Step 2: Configure Your System

1. **Open your `.env` file**:

   ```bash
   nano .env
   ```

2. **Replace the placeholder**:

   ```
   GOOGLE_API_KEY=AIza_your_actual_api_key_here
   ```

3. **Save the file**

## Step 3: Test the Google AI Integration

```bash
# Test the Google Gemini agent
python -c "
from src.agents.google_voicebot_agent import GoogleVoiceBotAgent
agent = GoogleVoiceBotAgent()
result = agent.analyze_call('demo', 'I need help with my EMI payment')
print(result)
"
```

## 🎯 FREE Tier Limits (Very Generous!)

- ✅ **15 requests per minute**
- ✅ **1 million tokens per month**
- ✅ **No credit card required**
- ✅ **No time limit**

## 🔄 How It Works

### With Google API Key:

- **Smart AI responses** using Google Gemini
- **Context-aware conversations**
- **Multi-language support**
- **Intent recognition**

### Without API Key (Fallback):

- **Rule-based responses** (still very functional)
- **Pattern matching**
- **Template responses**
- **Multilingual templates**

## 🚀 Integration

The system automatically detects if Google API is available:

1. **If configured**: Uses Google Gemini AI
2. **If not configured**: Falls back to rule-based responses

Both modes work perfectly for demos and presentations!

## 🎭 Voice Demo Features

Once configured, your Voice Demo will have:

- 🤖 **Real AI conversation**
- 🎤 **Speech recognition**
- 🔊 **Text-to-speech**
- 🌍 **Multi-language support**
- 📊 **Sentiment analysis**
- 🎯 **Intent detection**

This makes your EMI VoiceBot incredibly sophisticated while remaining completely FREE! 🎉
