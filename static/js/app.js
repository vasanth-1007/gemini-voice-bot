// Gemini Voice Bot - Web Application JavaScript

// Initialize Socket.IO
const socket = io();

// DOM Elements
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const docCount = document.getElementById('doc-count');
const imageStatus = document.getElementById('image-status');
const modelName = document.getElementById('model-name');

const loadSopsBtn = document.getElementById('load-sops-btn');
const rebuildIndexBtn = document.getElementById('rebuild-index-btn');
const refreshStatsBtn = document.getElementById('refresh-stats-btn');

const chatMessages = document.getElementById('chat-messages');
const questionInput = document.getElementById('question-input');
const sendBtn = document.getElementById('send-btn');
const clearChatBtn = document.getElementById('clear-chat-btn');

const audioUpload = document.getElementById('audio-upload');
const audioFilename = document.getElementById('audio-filename');

const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');

const exampleBtns = document.querySelectorAll('.example-btn');

// State
let isProcessing = false;

// Socket.IO Event Handlers
socket.on('connect', () => {
    console.log('Connected to server');
    updateStatus('connected', 'Connected');
    loadStats();
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    updateStatus('disconnected', 'Disconnected');
});

socket.on('status', (data) => {
    console.log('Status:', data);
    if (data.assistant_ready) {
        updateStatus('connected', 'Assistant Ready');
    }
});

socket.on('processing', (data) => {
    console.log('Processing:', data.message);
    showLoading(data.message);
});

socket.on('response', (data) => {
    console.log('Response received:', data);
    hideLoading();
    addMessage('bot', data.response, data.question);
    isProcessing = false;
});

socket.on('error', (data) => {
    console.error('Error:', data.message);
    hideLoading();
    showNotification('Error: ' + data.message, 'error');
    isProcessing = false;
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

// Load System Statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.error) {
            console.error('Error loading stats:', data.error);
            return;
        }
        
        // Update stats display
        const docCountValue = data.retrieval_stats?.document_count || 0;
        docCount.textContent = docCountValue;
        
        const imageEnabled = data.sop_stats?.image_extraction_enabled;
        imageStatus.textContent = imageEnabled ? 'Enabled ✓' : 'Disabled';
        
        const model = data.config?.model || 'Gemini AI';
        modelName.textContent = model.split('-')[0] + ' AI';
        
    } catch (error) {
        console.error('Error fetching stats:', error);
        showNotification('Failed to load statistics', 'error');
    }
}

// Load SOPs
async function loadSOPs(forceRebuild = false) {
    if (isProcessing) return;
    
    isProcessing = true;
    showLoading('Loading SOP documents...');
    
    try {
        const response = await fetch('/api/load-sops', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ force_rebuild: forceRebuild })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        hideLoading();
        showNotification(data.message, 'success');
        loadStats();
        
    } catch (error) {
        hideLoading();
        showNotification('Error: ' + error.message, 'error');
    } finally {
        isProcessing = false;
    }
}

// Ask Question
async function askQuestion(question) {
    if (!question.trim() || isProcessing) return;
    
    isProcessing = true;
    
    // Add user message
    addMessage('user', question);
    
    // Clear input
    questionInput.value = '';
    
    // Show loading
    showLoading('Processing your question...');
    
    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: question })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        hideLoading();
        addMessage('bot', data.response);
        
    } catch (error) {
        hideLoading();
        showNotification('Error: ' + error.message, 'error');
        addMessage('bot', 'Sorry, error aachu. Please try again.');
    } finally {
        isProcessing = false;
    }
}

// Upload and Process Audio
async function uploadAudio(file) {
    if (isProcessing) return;
    
    isProcessing = true;
    showLoading('Processing audio file...');
    
    try {
        const formData = new FormData();
        formData.append('audio', file);
        
        const response = await fetch('/api/upload-audio', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        hideLoading();
        
        // Add transcribed message
        if (data.transcribed) {
            addMessage('user', data.transcribed, null, '🎤 Voice');
        }
        
        // Add bot response
        addMessage('bot', data.response);
        
        showNotification('Audio processed successfully', 'success');
        
    } catch (error) {
        hideLoading();
        showNotification('Error: ' + error.message, 'error');
    } finally {
        isProcessing = false;
        audioUpload.value = '';
        audioFilename.textContent = '';
    }
}

// Add Message to Chat
function addMessage(type, text, question = null, label = null) {
    // Remove welcome message if exists
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const messageBubble = document.createElement('div');
    messageBubble.className = 'message-bubble';
    
    // Add label
    if (label || (type === 'user' && !label)) {
        const labelDiv = document.createElement('div');
        labelDiv.className = 'message-label';
        labelDiv.textContent = label || (type === 'user' ? 'You' : 'Bot');
        messageDiv.appendChild(labelDiv);
    }
    
    // Add question if provided (for bot responses)
    if (question && type === 'bot') {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'message-label';
        questionDiv.textContent = 'Question: ' + question;
        questionDiv.style.fontStyle = 'italic';
        questionDiv.style.marginBottom = '10px';
        messageDiv.appendChild(questionDiv);
    }
    
    messageBubble.textContent = text;
    messageDiv.appendChild(messageBubble);
    
    // Add timestamp
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString();
    messageDiv.appendChild(timeDiv);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Clear Chat
function clearChat() {
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <h3>Chat Cleared! 👋</h3>
            <p>Ask me anything about your SOPs.</p>
        </div>
    `;
}

// Show Loading Overlay
function showLoading(message = 'Processing...') {
    loadingText.textContent = message;
    loadingOverlay.style.display = 'flex';
}

// Hide Loading Overlay
function hideLoading() {
    loadingOverlay.style.display = 'none';
}

// Show Notification
function showNotification(message, type = 'info') {
    // Create notification element
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
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Event Listeners

// Send button
sendBtn.addEventListener('click', () => {
    const question = questionInput.value.trim();
    if (question) {
        askQuestion(question);
    }
});

// Enter key in input
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const question = questionInput.value.trim();
        if (question) {
            askQuestion(question);
        }
    }
});

// Load SOPs button
loadSopsBtn.addEventListener('click', () => {
    loadSOPs(false);
});

// Rebuild index button
rebuildIndexBtn.addEventListener('click', () => {
    if (confirm('This will rebuild the entire index. Continue?')) {
        loadSOPs(true);
    }
});

// Refresh stats button
refreshStatsBtn.addEventListener('click', () => {
    loadStats();
    showNotification('Statistics refreshed', 'info');
});

// Clear chat button
clearChatBtn.addEventListener('click', () => {
    if (confirm('Clear all chat messages?')) {
        clearChat();
    }
});

// Audio upload
audioUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        audioFilename.textContent = file.name;
        uploadAudio(file);
    }
});

// Example question buttons
exampleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const question = btn.getAttribute('data-question');
        questionInput.value = question;
        askQuestion(question);
    });
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize on page load
window.addEventListener('load', () => {
    console.log('Gemini Voice Bot Web Interface Loaded');
    loadStats();
});
