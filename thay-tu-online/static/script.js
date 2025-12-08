document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatMessages = document.getElementById('chatMessages');
    const sendBtn = document.getElementById('sendBtn');
    const resetBtn = document.getElementById('resetBtn');
    const btnText = sendBtn.querySelector('.btn-text');
    const btnLoading = sendBtn.querySelector('.btn-loading');

    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = formatMessage(content);
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function formatMessage(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message bot-message';
        indicator.id = 'typingIndicator';
        indicator.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    function setLoading(isLoading) {
        sendBtn.disabled = isLoading;
        userInput.disabled = isLoading;
        btnText.classList.toggle('d-none', isLoading);
        btnLoading.classList.toggle('d-none', !isLoading);
    }

    async function sendMessage(message) {
        addMessage(message, true);
        setLoading(true);
        showTypingIndicator();

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            hideTypingIndicator();

            if (response.ok) {
                addMessage(data.response, false);
            } else {
                addMessage(data.error || 'Có lỗi xảy ra, vui lòng thử lại!', false);
            }
        } catch (error) {
            hideTypingIndicator();
            addMessage('Không thể kết nối với server. Vui lòng thử lại!', false);
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    }

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        if (message) {
            sendMessage(message);
            userInput.value = '';
        }
    });

    resetBtn.addEventListener('click', async function() {
        try {
            await fetch('/reset', { method: 'POST' });
            chatMessages.innerHTML = '';
            addMessage(
                'Chào bạn! Thầy Tư đây. Cho thầy biết <strong>năm sinh</strong> và <strong>giới tính</strong> của bạn, thầy sẽ luận giải tử vi cho bạn nghe nhé!<br><br>Ví dụ: "Em sinh năm 1995, nữ" hoặc "2k1 nam"',
                false
            );
        } catch (error) {
            console.error('Reset error:', error);
        }
    });

    userInput.focus();
});
