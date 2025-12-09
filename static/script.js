document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatMessages = document.getElementById('chatMessages');
    const sendBtn = document.getElementById('sendBtn');
    const resetBtn = document.getElementById('resetBtn');

    // Suggestion Chips handler
    window.setInput = function(text) {
        userInput.value = text;
        userInput.focus();
        // Optional: auto-send
        // chatForm.dispatchEvent(new Event('submit'));
    }

    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        let innerHTML = '';
        if (!isUser) {
            innerHTML += `
                <div class="avatar">
                    <img src="https://res.cloudinary.com/dkeupjars/image/upload/v1765254047/agent/thay-tu-avatar-01_vju3dt.png" alt="Thầy Tư">
                </div>
            `;
        }

        // Parse for chart data
        const { text, chartData } = parseContent(content);

        innerHTML += `<div class="message-content">
                        ${formatMessage(text)}
                        ${chartData ? '<div class="chart-container" style="position: relative; height:300px; width:100%"><canvas id="chart-' + Date.now() + '"></canvas></div>' : ''}
                      </div>`;
        messageDiv.innerHTML = innerHTML;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        if (chartData) {
            const canvasId = messageDiv.querySelector('canvas').id;
            renderChart(canvasId, chartData);
        }
    }

    function parseContent(content) {
        // Regex to find JSON block: ```json { ... } ```
        const jsonBlockRegex = /```json\s*(\{[\s\S]*?"type"\s*:\s*"chart_data"[\s\S]*?\})\s*```/;
        const match = content.match(jsonBlockRegex);
        
        if (match) {
            try {
                const chartData = JSON.parse(match[1]);
                const cleanText = content.replace(jsonBlockRegex, '').trim();
                return { text: cleanText, chartData: chartData };
            } catch (e) {
                console.error("Error parsing chart JSON:", e);
                return { text: content, chartData: null };
            }
        }
        return { text: content, chartData: null };
    }

    function renderChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        const config = data.chart_config;
        
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: config.labels,
                datasets: [{
                    label: `Chỉ số năng lượng năm ${data.nam_sinh}`,
                    data: config.data,
                    backgroundColor: 'rgba(255, 215, 0, 0.2)',
                    borderColor: '#ffd700',
                    pointBackgroundColor: '#8b0000',
                    borderWidth: 2
                }]
            },
            options: {
                scales: {
                    r: {
                        angleLines: { color: 'rgba(245, 230, 211, 0.2)' },
                        grid: { color: 'rgba(245, 230, 211, 0.2)' },
                        pointLabels: { 
                            color: '#f5e6d3',
                            font: { size: 12 }
                        },
                        ticks: {
                            backdropColor: 'transparent',
                            color: 'rgba(245, 230, 211, 0.5)'
                        },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#f5e6d3' }
                    }
                },
                maintainAspectRatio: false
            }
        });
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
            <div class="avatar">
                <img src="https://res.cloudinary.com/dkeupjars/image/upload/v1765254047/agent/thay-tu-avatar-01_vju3dt.png" alt="Thầy Tư">
            </div>
            <div class="message-content">
                <i class="fas fa-pen-nib fa-spin-slow" style="font-size: 0.8rem; margin-right: 5px;"></i>
                Thầy đang bấm quẻ...
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
        if (userInput) userInput.disabled = isLoading;
        if (sendBtn) {
            sendBtn.disabled = isLoading;
            if (isLoading) {
                sendBtn.innerHTML = '<i class="fas fa-yin-yang fa-spin"></i>';
            } else {
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
            }
        }
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
            addMessage('Mạng mẽo cà chớn quá, con đợi xíu rồi hỏi lại nghen!', false);
            console.error('Error:', error);
        } finally {
            setLoading(false);
            userInput.focus();
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
            chatMessages.innerHTML = `
                <div class="message bot-message">
                    <div class="avatar">
                        <img src="https://res.cloudinary.com/dkeupjars/image/upload/v1765254047/agent/thay-tu-avatar-01_vju3dt.png" alt="Thầy Tư">
                    </div>
                    <div class="message-content">
                        Hello con! Thầy Tư đã quay lại nè.<br>
                        Con muốn coi quẻ mới hông? Cho Tui biết <strong>Năm Sinh</strong> với <strong>Giới Tính</strong> đi.
                    </div>
                </div>
            `;
            userInput.value = '';
            userInput.focus();
        } catch (error) {
            console.error('Reset error:', error);
        }
    });

    userInput.focus();
});
