#!/usr/bin/env python3
"""
Gemini Voice Bot - Web Application
Flask-based web interface for interacting with the voice bot
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from loguru import logger
import tempfile
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from src.voice_assistant import GeminiVoiceAssistant

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gemini-voice-bot-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for external access
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize config and voice assistant
config = Config()
voice_assistant = None

# Setup logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("web_app.log", rotation="10 MB", retention="7 days", level="INFO")


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
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'assistant_ready': voice_assistant is not None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    if not voice_assistant:
        return jsonify({'error': 'Assistant not initialized'}), 500
    
    try:
        stats = voice_assistant.get_system_stats()
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
    """Ask a text question"""
    if not voice_assistant:
        return jsonify({'error': 'Assistant not initialized'}), 500
    
    try:
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        logger.info(f"Processing question: {question}")
        
        # Process the query
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


@app.route('/api/upload-audio', methods=['POST'])
def upload_audio():
    """Upload and process audio file"""
    if not voice_assistant:
        return jsonify({'error': 'Assistant not initialized'}), 500
    
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            tmp_path = Path(tmp_file.name)
        
        logger.info(f"Processing audio file: {audio_file.filename}")
        
        # Process voice query
        transcribed, response = voice_assistant.process_voice_query(tmp_path)
        
        # Clean up
        tmp_path.unlink()
        
        return jsonify({
            'success': True,
            'transcribed': transcribed,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rebuild-index', methods=['POST'])
def rebuild_index():
    """Force rebuild of the document index"""
    if not voice_assistant:
        return jsonify({'error': 'Assistant not initialized'}), 500
    
    try:
        logger.info("Rebuilding document index...")
        stats = voice_assistant.load_and_index_sops(force_rebuild=True)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'message': 'Index rebuilt successfully'
        })
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}")
        return jsonify({'error': str(e)}), 500


# SocketIO events for real-time interaction
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('status', {
        'connected': True,
        'assistant_ready': voice_assistant is not None
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('ask_question')
def handle_ask_question(data):
    """Handle real-time question via WebSocket"""
    if not voice_assistant:
        emit('error', {'message': 'Assistant not initialized'})
        return
    
    try:
        question = data.get('question', '')
        logger.info(f"WebSocket question: {question}")
        
        # Emit processing status
        emit('processing', {'message': 'Processing your question...'})
        
        # Process query
        response = voice_assistant.process_text_query(question)
        
        # Emit response
        emit('response', {
            'question': question,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in WebSocket handler: {e}")
        emit('error', {'message': str(e)})


if __name__ == '__main__':
    # Get host and port from environment or use defaults
    host = os.getenv('HOST', '0.0.0.0')  # 0.0.0.0 allows external access
    port = int(os.getenv('PORT', '5000'))
    
    logger.info(f"Starting Gemini Voice Bot Web Server on {host}:{port}")
    logger.info("Access from external IP will be available")
    
    # Run with SocketIO
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
