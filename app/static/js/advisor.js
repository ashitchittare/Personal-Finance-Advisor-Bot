/**
 * AI Financial Advisor Chat Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    const sendBtn = document.getElementById('sendBtn');
    const quickChips = document.querySelectorAll('.quick-prompt-chip');

    if (!chatForm || !chatInput || !chatMessages) return;

    // Scroll chat to bottom on load
    scrollToBottom();

    // Quick prompt chips click listener
    quickChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const prompt = chip.getAttribute('data-prompt');
            if (prompt) {
                chatInput.value = prompt;
                sendMessage(prompt);
            }
        });
    });

    // Form submission
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (text) {
            sendMessage(text);
        }
    });

    function sendMessage(messageText) {
        // Clear input and disable button
        chatInput.value = '';
        chatInput.disabled = true;
        sendBtn.disabled = true;

        // 1. Append User Bubble
        appendMessage('user', messageText);
        scrollToBottom();

        // 2. Append Typing Indicator
        const typingId = appendTypingIndicator();
        scrollToBottom();

        // 3. Send API request
        fetch('/advisor/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: messageText })
        })
        .then(res => {
            if (!res.ok) throw new Error('Network error');
            return res.json();
        })
        .then(data => {
            removeTypingIndicator(typingId);
            if (data.assistant_message) {
                appendMessage('assistant', data.assistant_message.message);
            } else {
                appendMessage('assistant', 'Sorry, I could not generate a response. Please try again.');
            }
        })
        .catch(err => {
            console.error('AI chat error:', err);
            removeTypingIndicator(typingId);
            appendMessage('assistant', '⚠️ An error occurred while communicating with FinBot. Please try again later.');
        })
        .finally(() => {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
            scrollToBottom();
        });
    }

    function appendMessage(role, text) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${role}`;
        
        if (role === 'user') {
            bubble.textContent = text;
        } else {
            bubble.innerHTML = parseMarkdown(text);
        }

        chatMessages.appendChild(bubble);
    }

    function appendTypingIndicator() {
        const id = 'typing-' + Date.now();
        const bubble = document.createElement('div');
        bubble.id = id;
        bubble.className = 'chat-bubble assistant typing-bubble';
        bubble.innerHTML = `
            <div class="d-flex align-items-center gap-2">
                <span class="text-muted small">FinBot is analyzing your finances</span>
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(bubble);
        return id;
    }

    function removeTypingIndicator(id) {
        const elem = document.getElementById(id);
        if (elem) elem.remove();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Lightweight Markdown to HTML formatter for FinBot responses
    function parseMarkdown(md) {
        if (!md) return '';
        let html = md
            // Escape special chars
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            // Headers
            .replace(/^### (.*$)/gim, '<h5>$1</h5>')
            .replace(/^## (.*$)/gim, '<h4>$1</h4>')
            .replace(/^# (.*$)/gim, '<h3>$1</h3>')
            // Bold
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/gim, '<em>$1</em>')
            // Blockquotes
            .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
            // Unordered Lists
            .replace(/^\s*[\-\*]\s+(.*$)/gim, '<li>$1</li>')
            // Ordered Lists
            .replace(/^\s*(\d+)\.\s+(.*$)/gim, '<li>$2</li>')
            // Line breaks
            .replace(/\n\n+/g, '<br><br>')
            .replace(/\n/g, '<br>');

        return html;
    }
});
