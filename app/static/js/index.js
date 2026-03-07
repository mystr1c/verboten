let socket = null;
let currentChannel = null;
let currentWord = null;
let messageIds = new Set();
let messageIdCounter = 0;
let gameTimer = null;
let maxRounds = 5;
let currentRound = 0;

async function checkAuth() {
    try {
        const response = await fetch('/api/user');
        const data = await response.json();
        
        if (response.status !== 200) {
            window.location.href = '/login';
            return;
        }
        
        showUserInfo(data.data.user);
        connectToUserChannel();
    } catch (error) {
        console.error(error);
        window.location.href = '/login';
    }
}

function showUserInfo(user) {
    document.getElementById('userInfo').innerHTML = `
        <div class="user-info">
            <img src="${user.profile_image_url}" alt="${user.display_name}" class="user-avatar">
            <div class="user-name">${user.display_name}</div>
            <button class="logout-button" onclick="logout()">Выйти</button>
        </div>
    `;
    document.getElementById('userInfo').style.display = 'block';
}

function logout() {
    window.location.href = '/logout';
}

function startCountdown() {
    const wordsInput = document.getElementById('words-per-round');
    maxRounds = parseInt(wordsInput.value) || 5;
    currentRound = 0;

    const countdownOverlay = document.getElementById('countdownOverlay');
    const countdownNumber = document.getElementById('countdownNumber');
    let count = 3;

    countdownOverlay.style.display = 'flex';
    countdownNumber.textContent = count;

    const countdownInterval = setInterval(() => {
        count--;
        if (count > 0) {
            countdownNumber.textContent = count;
            countdownNumber.style.animation = 'none';
            countdownNumber.offsetHeight;
            countdownNumber.style.animation = 'countdownPulse 1s ease-in-out';
        } else {
            clearInterval(countdownInterval);
            countdownOverlay.style.display = 'none';
            document.getElementById('setup-screen').style.display = 'none';
            document.getElementById('active-game').style.display = 'block';
            displayRandomWord();
        }
    }, 1000);
}

checkAuth();

async function displayRandomWord() {
    currentRound++;

    if (currentRound > maxRounds) {
        showGameOverScreen();
        return;
    }

    document.getElementById('roundCounter').textContent = `Раунд ${currentRound} из ${maxRounds}`;
    document.getElementById('correctAnswer').style.display = 'none';
    currentWord = null;

    const chatMessages = document.getElementById('chatMessages');
    Array.from(chatMessages.children).forEach(msg => {
        msg.classList.remove('winner-message');
    });

    try {
        const response = await fetch('/api/word');
        if (!response.ok) throw new Error('Failed to load word');
        
        const data = await response.json();
        currentWord = data.data.word;
        
        const forbiddenHtml = data.data.forbidden.map(word => 
            `<span class="forbidden-word">${word}</span>`
        ).join('');
        
        clearTimeout(gameTimer);
        
        document.getElementById('content').innerHTML = `
            <div class="word-display">
                <div class="main-word">${currentWord}</div>
                <div class="forbidden-label">🚫 ЗАПРЕЩЕННЫЕ СЛОВА:</div>
                <div class="forbidden-words">
                    ${forbiddenHtml}
                </div>
                <div class="timer-container">
                    <div class="timer-line" id="timerLine"></div>
                </div>
            </div>
        `;
        
        const timerLine = document.getElementById('timerLine');
        let remainingTime = 30;
        
        gameTimer = setInterval(() => {
            remainingTime -= 0.1;
            const percentage = (remainingTime / 30) * 100;
            timerLine.style.width = percentage + '%';
            
            if (remainingTime <= 0) {
                clearInterval(gameTimer);
                showGameOver();
            }
        }, 100);
        
    } catch (error) {
        document.getElementById('content').innerHTML = `
            <div class="loading" style="color: red;">Ошибка загрузки</div>
        `;
    }
}

async function connectToUserChannel() {
    try {
        const response = await fetch('/api/channel');
        if (response.status !== 200) return;
        
        const data = await response.json();
        const channel = data.data.channel.toLowerCase();
        
        if (currentChannel === channel && socket && socket.connected) return;
        
        if (socket) socket.disconnect();
        
        socket = io({
            reconnection: true,
            reconnectionDelay: 3000,
            reconnectionAttempts: 5,
            transports: ['polling']
        });
        
        currentChannel = channel;
        document.getElementById('chatMessages').innerHTML = '';
        messageIds.clear();
        messageIdCounter = 0;

        socket.off('connect');
        socket.off('chat_message');
        socket.off('reconnect');

        socket.on('connect', function() {
            socket.emit('connect_chat', { channel: currentChannel });
        });

        socket.on('chat_message', function(data) {
            const msgId = `${data.message.username}-${data.message.text}-${messageIdCounter++}`;
            if (!messageIds.has(msgId)) {
                messageIds.add(msgId);
                addChatMessage(data.message.username, data.message.text);
            }
        });

        socket.on('reconnect', function() {
            socket.emit('connect_chat', { channel: currentChannel });
        });
    } catch (error) {
        console.error('Connection error:', error);
    }
}

function addChatMessage(username, text) {
    const chatMessages = document.getElementById('chatMessages');
    
    while (chatMessages.children.length >= 10) {
        chatMessages.removeChild(chatMessages.firstChild);
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message';
    
    if (currentWord && text.toLowerCase() === currentWord.toLowerCase()) {
        messageDiv.classList.add('winner-message');
    }
    
    messageDiv.innerHTML = `
        <span class="chat-username">${username}</span>
        <span class="chat-text">${text}</span>
    `;
    chatMessages.appendChild(messageDiv);
    
    if (currentWord && text.toLowerCase() === currentWord.toLowerCase()) {
        clearTimeout(gameTimer);
        showCorrectAnswer(username);
    }
}

function showCorrectAnswer(username) {
    const modalOverlay = document.getElementById('modalOverlay');
    const modalText = document.getElementById('modalText');
    
    modalText.textContent = `${username} угадал слово!`;
    modalOverlay.style.display = 'flex';
}

function showGameOver() {
    const modalOverlay = document.getElementById('modalOverlay');
    const modalText = document.getElementById('modalText');
    
    modalText.textContent = 'Увы, время вышло!';
    modalOverlay.style.display = 'flex';
}

function nextWord() {
    const modalOverlay = document.getElementById('modalOverlay');
    modalOverlay.style.display = 'none';
    document.getElementById('correctAnswer').style.display = 'none';
    displayRandomWord();
}

function showGameOverScreen() {
    const gameOverOverlay = document.getElementById('gameOverOverlay');
    gameOverOverlay.style.display = 'flex';
}

function restartGame() {
    const gameOverOverlay = document.getElementById('gameOverOverlay');
    gameOverOverlay.style.display = 'none';
    
    currentRound = 0;
    document.getElementById('active-game').style.display = 'none';
    document.getElementById('setup-screen').style.display = 'block';
    document.getElementById('correctAnswer').style.display = 'none';
    
    const chatMessages = document.getElementById('chatMessages');
    Array.from(chatMessages.children).forEach(msg => {
        msg.classList.remove('winner-message');
    });
}