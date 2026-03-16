import { showCorrectAnswer } from "../ui/render.js";
import { currentWord } from '../game/state.js'
import { stopGame } from '../game/engine.js'


let socket = null;
let currentChannel = null;
let messageIds = new Set();
let messageIdCounter = 0;

export async function connectToUserChannel() {
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
        stopGame();
        showCorrectAnswer(username);
    }
}