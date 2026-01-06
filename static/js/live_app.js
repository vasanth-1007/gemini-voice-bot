// Gemini Live Voice Bot - Real-time Communication JavaScript

// Initialize Socket.IO
const socket = io();

// DOM Elements
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const liveStatusDot = document.getElementById('live-status-dot');
const liveStatusText = document.getElementById('live-status-text');

const startLiveBtn = document.getElementById('start-live-btn');
const stopLiveBtn = document.getElementById('stop-live-btn');
const toggleMicBtn = document.getElementById('toggle-mic-btn');
const micIcon = document.getElementById('mic-icon');
const micText = document.getElementById('mic-text');

const audioStatus = document.getElementById('audio-status');
const connectionStatus = document.getElementById('connection-status');
const sessionDuration = document.getElementById('session-duration');

const visualizerCanvas = document.getElementById('visualizer-canvas');
const transcript = document.getElementById('transcript');
const clearTranscriptBtn = document.getElementById('clear-transcript-btn');

const docCount = document.getElementById('doc-count');
const sessionCount = document.getElementById('session-count');

const loadSopsBtn = document.getElementById('load-sops-btn');
const refreshStatsBtn = document.getElementById('refresh-stats-btn');

const chatMessages = document.getElementById('chat-messages');
const questionInput = document.getElementById('question-input');
const sendBtn = document.getElementById('send-btn');
const clearChatBtn = document.getElementById('clear-chat-btn');

const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');

// State
let isLiveSessionActive = false;
let isMicMuted = false;
let mediaStream = null;
let audioContext = null;
let mediaRecorder = null;
let sessionStartTime = null;
let durationInterval = null;

// Audio visualization
let analyser = null;
let dataArray = null;
let canvasContext = null;

// Initialize
if (visualizerCanvas) {
    canvasContext = visualizerCanvas.getContext('2d');
}

// Socket.IO Event Handlers
socket.on('connect', () => {
    console.log('Connected to server');
    updateStatus('connected', 'Connected');
    loadStats();
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    updateStatus('disconnected', 'Disconnected');
    if (isLiveSessionActive) {
        stopLiveSession();
    }
});

socket.on('status', (data) => {
    console.log('Status:', data);
    if (data.live_api_enabled) {
        console.log('✅ Live API enabled');
    }
});

socket.on('live_session_started', (data) => {
    console.log('Live session started:', data);
    isLiveSessionActive = true;
    updateLiveStatus('active', 'Live Session Active');
    connectionStatus.textContent = 'Connection: Active';
    startSessionTimer();
    showNotification('Live voice session started!', 'success');
});

socket.on('live_audio_response', async (data) => {
    console.log('Received audio response');
    try {
        // Decode base64 audio
        const audioData = base64ToArrayBuffer(data.audio);
        
        // Play audio
        await playAudioResponse(audioData);
        
        addTranscriptEntry('bot', 'Audio Response', 'voice');
    } catch (error) {
        console.error('Error playing audio response:', error);
    }
});

socket.on('live_text_response', (data) => {
    console.log('Received text response:', data.text);
    addTranscriptEntry('bot', data.text, 'text');
});

socket.on('live_text_sent', (data) => {
    console.log('Text sent confirmed:', data.text);
    addTranscriptEntry('user', data.text, 'text');
});

socket.on('live_session_stopped', (data) => {
    console.log('Live session stopped:', data);
    isLiveSessionActive = false;
    updateLiveStatus('inactive', 'Not Connected');
    connectionStatus.textContent = 'Connection: Standby';
    stopSessionTimer();
    showNotification('Live voice session ended', 'info');
});

socket.on('live_error', (data) => {
    console.error('Live error:', data.error);
    showNotification('Error: ' + data.error, 'error');
    if (isLiveSessionActive) {
        stopLiveSession();
    }
});

socket.on('response', (data) => {
    hideLoading();
    addChatMessage('bot', data.response);
});

socket.on('error', (data) => {
    hideLoading();
    showNotification('Error: ' + data.message, 'error');
});

// Update Status Indicator
function updateStatus(status, text) {
    statusText.textContent = text;
    if (status === 'connected') {
        statusDot.classList.add('connected');
    } else {
        statusDot.classList.remove('connected');
    }
}

function updateLiveStatus(status, text) {
    liveStatusText.textContent = text;
    if (status === 'active') {
        liveStatusDot.classList.add('active');
        liveStatusDot.classList.remove('recording');
    } else if (status === 'recording') {
        liveStatusDot.classList.add('recording');
        liveStatusDot.classList.remove('active');
    } else {
        liveStatusDot.classList.remove('active', 'recording');
    }
}

// Load System Statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.error) {
            console.error('Error loading stats:', data.error);
            return;
        }
        
        const docCountValue = data.retrieval_stats?.document_count || 0;
        docCount.textContent = docCountValue;
        
        const activeSessions = data.active_sessions || 0;
        sessionCount.textContent = activeSessions;
        
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// Start Live Session
async function startLiveSession() {
    try {
        console.log('Requesting microphone access...');
        audioStatus.textContent = 'Microphone: Requesting...';
        
        // Request microphone access
        mediaStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                sampleRate: 16000,
                echoCancellation: true,
                noiseSuppression: true
            }
        });
        
        console.log('✅ Microphone access granted');
        audioStatus.textContent = 'Microphone: Active';
        
        // Set up audio context and analyser
        audioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: 16000
        });
        
        const source = audioContext.createMediaStreamSource(mediaStream);
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);
        
        source.connect(analyser);
        
        // Start visualization
        visualizeAudio();
        
        // Set up audio processor for streaming raw PCM
        setupAudioProcessor(source);
        
        // Notify server to start live session
        showLoading('Starting live session...');
        socket.emit('start_live_session', {});
        
        // Update UI
        startLiveBtn.style.display = 'none';
        stopLiveBtn.style.display = 'inline-flex';
        toggleMicBtn.style.display = 'inline-flex';
        
        hideLoading();
        
    } catch (error) {
        console.error('Error starting live session:', error);
        audioStatus.textContent = 'Microphone: Error';
        showNotification('Could not access microphone: ' + error.message, 'error');
        hideLoading();
    }
}

// Setup Audio Processor for streaming raw PCM audio
let audioProcessor = null;

function setupAudioProcessor(source) {
    try {
        // Create a script processor node (4096 buffer size for ~256ms chunks at 16kHz)
        audioProcessor = audioContext.createScriptProcessor(4096, 1, 1);
        
        audioProcessor.onaudioprocess = (event) => {
            if (!isLiveSessionActive || isMicMuted) {
                return;
            }
            
            // Get the audio data (Float32Array, values between -1 and 1)
            const inputData = event.inputBuffer.getChannelData(0);
            
            // Convert Float32 PCM to Int16 PCM (what Gemini expects)
            const int16Data = new Int16Array(inputData.length);
            for (let i = 0; i < inputData.length; i++) {
                // Clamp to [-1, 1] and convert to 16-bit integer
                const s = Math.max(-1, Math.min(1, inputData[i]));
                int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
            }
            
            // Convert to base64
            const base64Audio = arrayBufferToBase64(int16Data.buffer);
            
            // Send to server
            socket.emit('send_live_audio', {
                audio: base64Audio
            });
            
            console.log('Sent PCM audio chunk:', int16Data.length * 2, 'bytes');
        };
        
        // Connect: source -> processor -> destination (speaker, muted)
        source.connect(audioProcessor);
        audioProcessor.connect(audioContext.destination);
        
        updateLiveStatus('recording', 'Recording...');
        
    } catch (error) {
        console.error('Error setting up audio processor:', error);
        showNotification('Error setting up audio processing', 'error');
    }
}

// Stop Live Session
function stopLiveSession() {
    console.log('Stopping live session...');
    
    // Disconnect audio processor
    if (audioProcessor) {
        audioProcessor.disconnect();
        audioProcessor = null;
    }
    
    // Stop media stream
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }
    
    // Close audio context
    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }
    
    // Notify server
    socket.emit('stop_live_session');
    
    // Reset UI
    startLiveBtn.style.display = 'inline-flex';
    stopLiveBtn.style.display = 'none';
    toggleMicBtn.style.display = 'none';
    
    audioStatus.textContent = 'Microphone: Ready';
    connectionStatus.textContent = 'Connection: Standby';
    
    updateLiveStatus('inactive', 'Not Connected');
    
    // Clear visualization
    if (canvasContext) {
        canvasContext.clearRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);
    }
}

// Toggle Microphone Mute
function toggleMicrophone() {
    isMicMuted = !isMicMuted;
    
    if (isMicMuted) {
        micIcon.textContent = '🔇';
        micText.textContent = 'Unmute';
        audioStatus.textContent = 'Microphone: Muted';
        updateLiveStatus('active', 'Muted');
    } else {
        micIcon.textContent = '🎤';
        micText.textContent = 'Mute';
        audioStatus.textContent = 'Microphone: Active';
        updateLiveStatus('recording', 'Recording...');
    }
    
    // Mute/unmute the audio tracks
    if (mediaStream) {
        mediaStream.getAudioTracks().forEach(track => {
            track.enabled = !isMicMuted;
        });
    }
}

// Audio Visualization
function visualizeAudio() {
    if (!analyser || !canvasContext || !isLiveSessionActive) return;
    
    requestAnimationFrame(visualizeAudio);
    
    analyser.getByteFrequencyData(dataArray);
    
    const width = visualizerCanvas.width;
    const height = visualizerCanvas.height;
    
    canvasContext.fillStyle = 'rgb(26, 26, 26)';
    canvasContext.fillRect(0, 0, width, height);
    
    const barWidth = (width / dataArray.length) * 2.5;
    let barHeight;
    let x = 0;
    
    for (let i = 0; i < dataArray.length; i++) {
        barHeight = (dataArray[i] / 255) * height;
        
        const gradient = canvasContext.createLinearGradient(0, height - barHeight, 0, height);
        gradient.addColorStop(0, '#4285f4');
        gradient.addColorStop(1, '#34a853');
        
        canvasContext.fillStyle = gradient;
        canvasContext.fillRect(x, height - barHeight, barWidth, barHeight);
        
        x += barWidth + 1;
    }
}

// Session Timer
function startSessionTimer() {
    sessionStartTime = Date.now();
    durationInterval = setInterval(updateSessionDuration, 1000);
}

function stopSessionTimer() {
    if (durationInterval) {
        clearInterval(durationInterval);
        durationInterval = null;
    }
    sessionStartTime = null;
    sessionDuration.textContent = 'Duration: 0:00';
}

function updateSessionDuration() {
    if (!sessionStartTime) return;
    
    const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    
    sessionDuration.textContent = `Duration: ${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// Transcript Functions
function addTranscriptEntry(type, text, mode = 'voice') {
    // Remove welcome message if exists
    const welcomeMsg = transcript.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const entry = document.createElement('div');
    entry.className = `transcript-entry ${type}`;
    
    const label = document.createElement('div');
    label.className = 'transcript-label';
    label.textContent = type === 'user' ? '🗣️ You' : '🤖 Bot';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'transcript-text';
    textDiv.textContent = text;
    
    const time = document.createElement('div');
    time.className = 'transcript-time';
    time.textContent = new Date().toLocaleTimeString();
    
    entry.appendChild(label);
    entry.appendChild(textDiv);
    entry.appendChild(time);
    
    transcript.appendChild(entry);
    transcript.scrollTop = transcript.scrollHeight;
}

function clearTranscript() {
    transcript.innerHTML = `
        <div class="welcome-message">
            <h3>Transcript Cleared</h3>
            <p>Start speaking to see your conversation here.</p>
        </div>
    `;
}

// Chat Functions (Text fallback)
function addChatMessage(type, text) {
    chatMessages.querySelector('.info-message')?.remove();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble';
    messageBubble.textContent = text;
    
    messageDiv.appendChild(messageBubble);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function askQuestion(question) {
    if (!question.trim()) return;
    
    addChatMessage('user', question);
    questionInput.value = '';
    
    showLoading('Processing...');
    
    socket.emit('ask_question', { question: question });
}

// Utility Functions
function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

function base64ToArrayBuffer(base64) {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}

async function playAudioResponse(arrayBuffer) {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.start(0);
}

function showLoading(message = 'Processing...') {
    loadingText.textContent = message;
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#00c851' : type === 'error' ? '#ea4335' : '#4285f4'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        z-index: 1001;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Event Listeners
startLiveBtn.addEventListener('click', startLiveSession);
stopLiveBtn.addEventListener('click', stopLiveSession);
toggleMicBtn.addEventListener('click', toggleMicrophone);

clearTranscriptBtn.addEventListener('click', () => {
    if (confirm('Clear conversation transcript?')) {
        clearTranscript();
    }
});

loadSopsBtn.addEventListener('click', async () => {
    showLoading('Loading SOPs...');
    try {
        const response = await fetch('/api/load-sops', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ force_rebuild: false })
        });
        const data = await response.json();
        hideLoading();
        showNotification(data.message, 'success');
        loadStats();
    } catch (error) {
        hideLoading();
        showNotification('Error loading SOPs', 'error');
    }
});

refreshStatsBtn.addEventListener('click', () => {
    loadStats();
    showNotification('Statistics refreshed', 'info');
});

sendBtn.addEventListener('click', () => {
    const question = questionInput.value.trim();
    if (question) askQuestion(question);
});

questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const question = questionInput.value.trim();
        if (question) askQuestion(question);
    }
});

clearChatBtn.addEventListener('click', () => {
    if (confirm('Clear chat messages?')) {
        chatMessages.innerHTML = '<div class="info-message">Chat cleared</div>';
    }
});

// Initialize on page load
window.addEventListener('load', () => {
    console.log('Gemini Live Voice Bot Interface Loaded');
    loadStats();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (isLiveSessionActive) {
        stopLiveSession();
    }
});
