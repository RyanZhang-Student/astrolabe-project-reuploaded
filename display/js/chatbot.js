document.addEventListener('DOMContentLoaded', () => {
    const chatOverlay = document.getElementById('chatbot-modal');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const consultBtn = document.getElementById('consult-btn');

    let chatHistory = []; // {role: 'user'|'assistant', content: '...'}
    let currentPersona = 'bot1';
    let currentAvatar = '☆';
    
    // Profile Selection Logic
    const profiles = document.querySelectorAll('.chat-profile');
    const profileDesc = document.getElementById('chat-profile-desc');
    const headerAvatar = document.getElementById('chat-current-avatar');
    const headerName = document.getElementById('chat-current-name');
    
    const getWelcomeHtml = () => {
        const t = window.translations[window.currentLanguage || 'en'];
        return `
        <div class="chat-welcome">
            <h4>${t.chat_welcome_title}</h4>
            <p>${t.chat_welcome_desc}</p>
            <div class="suggestions">
                <span class="suggestion-chip">${t.chat_sugg_1}</span>
                <span class="suggestion-chip">${t.chat_sugg_2}</span>
                <span class="suggestion-chip">${t.chat_sugg_3}</span>
                <span class="suggestion-chip">${t.chat_sugg_4}</span>
            </div>
        </div>
        `;
    };

    profiles.forEach(profile => {
        profile.addEventListener('click', () => {
            if (profile.dataset.persona === currentPersona) return;
            
            // Update active styling
            profiles.forEach(p => p.classList.remove('active'));
            profile.classList.add('active');
            
            // Update state
            currentPersona = profile.dataset.persona;
            currentAvatar = profile.dataset.avatar;
            const name = profile.dataset.name;
            const desc = profile.dataset.desc;
            
            // Update UI
            headerAvatar.textContent = currentAvatar;
            headerName.textContent = name;
            profileDesc.textContent = desc;
            
            // Clear chat history
            chatHistory = [];
            chatMessages.innerHTML = getWelcomeHtml();
            chatInput.placeholder = window.translations[window.currentLanguage || 'en'].chat_placeholder;
        });
    });

    // Open chatbot modal
    if (consultBtn) {
        consultBtn.addEventListener('click', () => {
            chatOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            chatInput.focus();
        });
    }

    // Close chatbot modal
    window.closeChatbot = function () {
        chatOverlay.classList.remove('active');
        document.body.style.overflow = 'auto';
    };

    // Close on overlay click
    if (chatOverlay) {
        chatOverlay.addEventListener('click', (e) => {
            if (e.target === chatOverlay) {
                window.closeChatbot();
            }
        });
    }

    // Send message
    async function sendMessage(text) {
        if (!text.trim()) return;

        const userName = window.currentAnalysisUserName;
        if (!userName) {
            alert('Please generate a chart first before consulting.');
            return;
        }

        // Add user message to UI
        appendMessage('user', text);
        chatHistory.push({ role: 'user', content: text });

        // Clear input
        chatInput.value = '';
        chatInput.style.height = 'auto';
        chatSendBtn.disabled = true;

        // Remove welcome message if present
        const welcome = chatMessages.querySelector('.chat-welcome');
        if (welcome) welcome.remove();

        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_name: userName,
                    message: text,
                    persona: currentPersona,
                    history: chatHistory.slice(0, -1), // exclude the message we just added
                    lang: window.currentLanguage || 'en'
                })
            });

            const result = await response.json();
            removeTypingIndicator();

            if (response.ok && result.status === 'success') {
                appendMessage('assistant', result.reply);
                chatHistory.push({ role: 'assistant', content: result.reply });
            } else if (response.status === 503 || (result && result.error === 'unavailable')) {
                // Service unavailable (429 rate limit / quota depleted)
                appendMessage('assistant', 'Your Consultant is temporarily unavailable. Please try again in a few minutes.');
                // Update header status to offline
                const statusEl = document.querySelector('.chat-advisor-status');
                if (statusEl) {
                    const t = window.translations[window.currentLanguage || 'en'];
                    statusEl.innerHTML = `<span class="status-dot offline"></span> ${t.chat_offline}`;
                }
            } else {
                appendMessage('assistant', 'Sorry, something went wrong. Please try again later.');
            }
        } catch (error) {
            console.error('Chatbot error:', error);
            removeTypingIndicator();
            appendMessage('assistant', 'Unable to reach your Consultant. Please check your connection and try again.');
        }

        chatSendBtn.disabled = false;
    }

    // Append message to chat UI
    function appendMessage(role, content) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${role}`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'msg-avatar';
        avatarDiv.textContent = role === 'assistant' ? currentAvatar : '✦';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'msg-bubble';

        // Parse basic markdown
        let html = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br/>');
        html = `<p>${html}</p>`;

        bubbleDiv.innerHTML = html;

        msgDiv.appendChild(avatarDiv);
        msgDiv.appendChild(bubbleDiv);
        chatMessages.appendChild(msgDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Typing indicator
    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.id = 'typing-indicator';

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'msg-avatar';
        avatarDiv.style.background = 'linear-gradient(135deg, var(--primary), #b39b6b)';
        avatarDiv.style.color = 'var(--bg-dark)';
        avatarDiv.textContent = currentAvatar;

        const dotsDiv = document.createElement('div');
        dotsDiv.className = 'typing-dots';
        dotsDiv.innerHTML = '<span></span><span></span><span></span>';

        indicator.appendChild(avatarDiv);
        indicator.appendChild(dotsDiv);
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }

    // Send button click
    if (chatSendBtn) {
        chatSendBtn.addEventListener('click', () => {
            sendMessage(chatInput.value);
        });
    }

    // Enter key to send (Shift+Enter for newline)
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage(chatInput.value);
            }
        });

        // Auto-resize textarea
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
        });
    }

    // Suggestion chips
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('suggestion-chip')) {
            const text = e.target.textContent;
            chatInput.value = text;
            sendMessage(text);
        }
    });
});
