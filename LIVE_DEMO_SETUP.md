# Live Call Demo Setup Guide

## Quick Start (Basic Mode)

The live call demo system works without any optional dependencies for basic demonstration:

```bash
cd /Users/rsaxena/Downloads/Manya-TVS-Project
python live_call_demo.py
```

This will start the system at `http://localhost:8002` with:

- ✅ WebSocket-based live call simulation
- ✅ Real-time UI updates
- ✅ Customer interaction flow
- ✅ Demo mode (no actual calls)

## Enhanced Mode (With Audio Features)

For full audio capabilities and real phone calls, install optional dependencies:

```bash
pip install -r requirements-audio-demo.txt
```

This enables:

- 🔊 Text-to-speech audio generation (gTTS)
- 🎵 Audio playback (pygame)
- 🎤 Speech recognition
- ☎️ Real phone calls (Twilio - requires account setup)

## Twilio Setup (Optional - for real calls)

1. Create a Twilio account at https://www.twilio.com
2. Get your Account SID and Auth Token
3. Purchase a phone number
4. Set environment variables:

```bash
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_PHONE_NUMBER="your_phone_number"
```

## Usage

1. Start the demo system:

```bash
python live_call_demo.py
```

2. Open browser to `http://localhost:8002`

3. The system provides:
   - Live call simulation interface
   - Real-time WebSocket updates
   - Customer management
   - Audio controls (if dependencies installed)
   - Twilio integration (if configured)

## Integration with Main UI

The live call demo integrates with the main UI system:

1. Start main UI: `python advanced_ui_server.py` (port 8001)
2. Start live demo: `python live_call_demo.py` (port 8002)
3. Access live demo via main UI at `/live-demo`

## Troubleshooting

- **Import warnings**: Expected for optional dependencies - system works without them
- **Audio not working**: Install `pip install gtts pygame`
- **Phone calls not working**: Set up Twilio credentials
- **WebSocket errors**: Check firewall/port 8002 availability

The system is designed to gracefully handle missing optional components.
