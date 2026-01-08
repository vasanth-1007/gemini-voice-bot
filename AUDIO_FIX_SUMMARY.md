# Audio Format Fix - Solution Summary

## Problem Description

The Gemini Live API was receiving errors:

**Initial Error:**
```
Unsupported input type "<class 'bytes'>" or input content "b'\x1aE\xdf\xa3..."
Error: EBML header parsing failed
```

**Second Error (after initial fix):**
```
Unsupported input type "<class 'bytes'>" or input content "b'\xf5\xff\xc7\xff..."
```

**Third Error (after second fix):**
```
Error sending audio: sent 1000 (OK); then received 1000 (OK)
```
This was a WebSocket close error due to using the deprecated `send()` method.

**Fourth Error (after third fix):**
```
Error sending audio: sent 1000 (OK); then received 1000 (OK)
```
Still getting WebSocket close - the session configuration was missing `realtime_input_config`.

### Root Cause

1. **First issue**: Browser was sending WebM/Opus audio format (compressed container)
2. **Second issue**: Raw PCM bytes were being sent without proper structure
3. **Third issue**: Using deprecated `send()` method instead of `send_realtime_input()`
4. **Fourth issue**: Missing `realtime_input_config` in session configuration - session was not set up to accept audio input
5. **Gemini Live API expects**: 
   - Raw PCM audio (16-bit, mono, 16kHz)
   - Wrapped in `types.Blob` object
   - Sent via `send_realtime_input()` for real-time streaming with VAD
   - Session must be configured with `realtime_input_config` to enable audio input

## Solution Implemented

### Approach: Browser-side PCM Conversion

Instead of trying to convert WebM to PCM on the server (which required FFmpeg and had fragmentation issues), we now convert audio to PCM directly in the browser before sending.

### Changes Made

#### 1. Frontend (static/js/live_app.js)

**Removed**: `MediaRecorder` with WebM format  
**Added**: `ScriptProcessorNode` for real-time PCM conversion

```javascript
// Old approach (WebM chunks)
mediaRecorder = new MediaRecorder(mediaStream, {
    mimeType: 'audio/webm',
    audioBitsPerSecond: 16000
});

// New approach (Raw PCM)
audioProcessor = audioContext.createScriptProcessor(4096, 1, 1);
audioProcessor.onaudioprocess = (event) => {
    const inputData = event.inputBuffer.getChannelData(0);
    const int16Data = new Int16Array(inputData.length);
    for (let i = 0; i < inputData.length; i++) {
        const s = Math.max(-1, Math.min(1, inputData[i]));
        int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    // Send int16Data directly
};
```

**Benefits**:
- No fragmentation issues
- No server-side conversion needed
- No FFmpeg dependency
- More efficient bandwidth usage

#### 2. Backend (web_live_api.py)

**Removed**: 
- `pydub` import
- `convert_webm_to_pcm()` function
- FFmpeg dependency

**Simplified**:
```python
# Decode PCM from browser and send to live session
pcm_bytes = base64.b64decode(audio_base64)
asyncio.run(live_chat.send_audio_chunk(pcm_bytes))
```

#### 3. Live Session (src/gemini_live/live_session.py)

**Fixed**: Audio data format, API method, and session configuration

```python
# Session Configuration - MUST include realtime_input_config
config = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(...),
    # This is REQUIRED for audio input!
    realtime_input_config=types.RealtimeInputConfig()
)

# Audio Sending - Use proper API method
audio_blob = types.Blob(
    data=audio_data,
    mime_type=f'audio/pcm;rate={self.sample_rate}'
)
await self.session.send_realtime_input(audio=audio_blob)
```

**Key changes**:
- **Added `realtime_input_config`** to LiveConnectConfig - REQUIRED for audio input
- Use `send_realtime_input()` instead of deprecated `send()` method
- Create proper `Blob` object with audio data
- Include sample rate in mime_type: `audio/pcm;rate=16000`
- `send_realtime_input()` is optimized for real-time audio with Voice Activity Detection (VAD)

#### 4. Dependencies (requirements_live.txt)

**Removed**: `pydub>=0.25.1` (no longer needed)

## Technical Details

### Audio Format Specification
- **Sample Rate**: 16kHz (16,000 samples/second)
- **Bit Depth**: 16-bit signed integers
- **Channels**: Mono (1 channel)
- **Byte Order**: Little-endian
- **Chunk Size**: 4096 samples (~256ms at 16kHz)

### Data Flow

1. **Browser**: Microphone → AudioContext (16kHz) → ScriptProcessorNode
2. **ScriptProcessorNode**: Float32 PCM → Int16 PCM → Base64
3. **WebSocket**: Base64 string → Server
4. **Server**: Base64 → Raw bytes → Gemini Live API

## Testing

To test the fix:

1. Restart the web server:
   ```bash
   ./start_live_server.sh
   ```

2. Open the web interface in your browser

3. Click "Start Live Session" and grant microphone access

4. Speak into the microphone

5. Check the logs - you should see:
   ```
   Sent PCM audio chunk: 8192 bytes
   ```
   Without any conversion errors.

## Advantages of This Solution

1. **No External Dependencies**: No FFmpeg required
2. **Better Performance**: No server-side audio processing
3. **More Reliable**: No fragmentation or codec issues
4. **Simpler Architecture**: Less code, fewer failure points
5. **Cross-platform**: Works on all browsers with Web Audio API support

## Browser Compatibility

This solution uses the Web Audio API's `ScriptProcessorNode`, which is supported in:
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Most modern browsers

**Note**: `ScriptProcessorNode` is deprecated in favor of `AudioWorklet`, but still widely supported. Future enhancement could migrate to AudioWorklet for better performance.

## Troubleshooting

If you still see errors:

1. **Check browser console**: Look for JavaScript errors
2. **Check microphone permissions**: Ensure microphone access is granted
3. **Check sample rate**: AudioContext should be 16kHz
4. **Check network**: Ensure WebSocket connection is stable

## Files Modified

- `static/js/live_app.js` - Browser-side PCM conversion
- `web_live_api.py` - Simplified audio handling
- `requirements_live.txt` - Removed pydub dependency

## Files Removed

- `FFMPEG_INSTALLATION.md` - No longer needed (backed up)
