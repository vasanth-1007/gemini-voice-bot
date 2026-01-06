#!/usr/bin/env python3
"""
Gemini Voice Bot - Web Application with Live API
Real-time bidirectional voice communication
"""
import os
import sys
import json
import asyncio
import base64
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from loguru import logger
import tempfile
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from src.voice_assistant import GeminiVoiceAssistant
from src.gemini_live import LiveVoiceChat

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gemini-live-api-secret-change-me')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize config and voice assistant
config = Config()
voice_assistant = None
live_sessions = {}  # Store active live sessions per client

# Setup logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("web_live_api.log", rotation="10 MB", retention="7 days", level="INFO")


def initialize_assistant():
    """Initialize the voice assistant"""
    global voice_assistant
    try:
        logger.info("Initializing Gemini Voice Assistant...")
        voice_assistant = GeminiVoiceAssistant(config)
        logger.info("Voice Assistant initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing assistant: {e}")
        return False


# Initialize on startup
initialize_assistant()


@app.route('/')
def index():
    """Serve the live API web interface"""
    return render_template('live_index.html')


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'assistant_ready': voice_assistant is not None,
        'live_api_enabled': True,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    if not voice_assistant:
        return jsonify({'error': 'Assistant not initialized'}), 500
    
    try:
        stats = voice_assistant.get_system_stats()
        stats['live_api_enabled'] = True
        stats['active_sessions'] = len(live_sessions)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/load-sops', methods=['POST'])
def load_sops():
    """Load and index SOP documents"""
    if not voice_assistant:
        return jsonify({'error': 'Assistant not initialized'}), 500
    
    try:
        force_rebuild = request.json.get('force_rebuild', False)
        logger.info(f"Loading SOPs (force_rebuild={force_rebuild})...")
        
        stats = voice_assistant.load_and_index_sops(force_rebuild=force_rebuild)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'message': f"Indexed {stats['document_count']} document chunks"
        })
    except Exception as e:
        logger.error(f"Error loading SOPs: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Ask a text question (non-live mode)"""
    if not voice_assistant:
        return jsonify({'error': 'Assistant not initialized'}), 500
    
    try:
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        logger.info(f"Processing question: {question}")
        
        response = voice_assistant.process_text_query(question)
        
        return jsonify({
            'success': True,
            'question': question,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({'error': str(e)}), 500


# SocketIO Events for Live Voice Communication

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    logger.info(f"Client connected: {client_id}")
    emit('status', {
        'connected': True,
        'assistant_ready': voice_assistant is not None,
        'live_api_enabled': True
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    logger.info(f"Client disconnected: {client_id}")
    
    # Clean up live session if exists
    if client_id in live_sessions:
        asyncio.run(live_sessions[client_id].stop())
        del live_sessions[client_id]
        logger.info(f"Cleaned up live session for {client_id}")


@socketio.on('start_live_session')
def handle_start_live_session(data):
    """Start a new live voice session"""
    client_id = request.sid
    
    try:
        logger.info(f"Starting live session for {client_id}")
        
        # Get SOP context
        retrieval_result = None
        if voice_assistant:
            # Get recent context or all SOPs summary
            sop_context = "Available SOPs indexed and ready for questions."
        else:
            sop_context = None
        
        # Create live session
        live_chat = LiveVoiceChat(
            api_key=config.google_api_key,
            sop_context=sop_context,
            sample_rate=16000
        )
        
        # Set up callbacks
        async def on_audio(audio_data):
            # Send audio back to client
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            socketio.emit('live_audio_response', {
                'audio': audio_base64
            }, room=client_id)
        
        async def on_text(text):
            # Send text back to client
            socketio.emit('live_text_response', {
                'text': text
            }, room=client_id)
        
        async def on_error(error):
            # Send error to client
            socketio.emit('live_error', {
                'error': error
            }, room=client_id)
        
        live_chat.session.set_callbacks(
            on_audio=on_audio,
            on_text=on_text,
            on_error=on_error
        )
        
        # Start session asynchronously
        asyncio.run(live_chat.start())
        
        # Store session
        live_sessions[client_id] = live_chat
        
        emit('live_session_started', {
            'success': True,
            'message': 'Live voice session started'
        })
        
        logger.info(f"✅ Live session started for {client_id}")
        
    except Exception as e:
        logger.error(f"Error starting live session: {e}")
        emit('live_error', {
            'error': str(e)
        })


@socketio.on('send_live_audio')
def handle_send_live_audio(data):
    """Receive audio from client and send to Gemini Live API"""
    client_id = request.sid
    
    if client_id not in live_sessions:
        emit('live_error', {'error': 'No active live session'})
        return
    
    try:
        # Get audio data (now raw PCM from browser)
        audio_base64 = data.get('audio')
        if not audio_base64:
            return
        
        # Decode audio - already in PCM format (16-bit, mono, 16kHz)
        pcm_bytes = base64.b64decode(audio_base64)
        
        # Send PCM audio directly to live session
        live_chat = live_sessions[client_id]
        asyncio.run(live_chat.send_audio_chunk(pcm_bytes))
        
        logger.debug(f"Sent audio to live session: {len(pcm_bytes)} bytes PCM")
        
    except Exception as e:
        logger.error(f"Error sending live audio: {e}")
        emit('live_error', {'error': str(e)})


@socketio.on('send_live_text')
def handle_send_live_text(data):
    """Receive text from client and send to Gemini Live API"""
    client_id = request.sid
    
    if client_id not in live_sessions:
        emit('live_error', {'error': 'No active live session'})
        return
    
    try:
        text = data.get('text', '')
        if not text:
            return
        
        # Send to live session
        live_chat = live_sessions[client_id]
        asyncio.run(live_chat.send_text(text))
        
        logger.info(f"Sent text to live session: {text}")
        
        # Echo to client
        emit('live_text_sent', {
            'text': text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error sending live text: {e}")
        emit('live_error', {'error': str(e)})


@socketio.on('stop_live_session')
def handle_stop_live_session():
    """Stop the live voice session"""
    client_id = request.sid
    
    if client_id not in live_sessions:
        return
    
    try:
        logger.info(f"Stopping live session for {client_id}")
        
        # Stop session
        live_chat = live_sessions[client_id]
        asyncio.run(live_chat.stop())
        
        # Remove from sessions
        del live_sessions[client_id]
        
        emit('live_session_stopped', {
            'success': True,
            'message': 'Live voice session stopped'
        })
        
        logger.info(f"✅ Live session stopped for {client_id}")
        
    except Exception as e:
        logger.error(f"Error stopping live session: {e}")
        emit('live_error', {'error': str(e)})


@socketio.on('ask_question')
def handle_ask_question(data):
    """Handle regular text question (non-live)"""
    if not voice_assistant:
        emit('error', {'message': 'Assistant not initialized'})
        return
    
    try:
        question = data.get('question', '')
        logger.info(f"WebSocket question: {question}")
        
        emit('processing', {'message': 'Processing your question...'})
        
        response = voice_assistant.process_text_query(question)
        
        emit('response', {
            'question': question,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in WebSocket handler: {e}")
        emit('error', {'message': str(e)})


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    
    logger.info(f"Starting Gemini Live API Web Server on {host}:{port}")
    logger.info("Real-time voice communication enabled")
    
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
