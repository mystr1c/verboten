import { showEndGame, showGameOver } from '../ui/render.js'
import { maxRounds, currentRound, currentWord, setCurrentRound, setCurrentWord, setMaxRounds } from './state.js'

let gameTimer = null;

async function displayRandomWord() {
    setCurrentRound(currentRound + 1)

    if (currentRound > maxRounds) {
        showEndGame();
        return;
    }

    document.getElementById('roundCounter').textContent = `Раунд ${currentRound} из ${maxRounds}`;
    document.getElementById('correctAnswer').style.display = 'none';
    setCurrentWord(null);

    const chatMessages = document.getElementById('chatMessages');
    Array.from(chatMessages.children).forEach(msg => {
        msg.classList.remove('winner-message');
    });

    try {
        const response = await fetch('/api/word');
        if (!response.ok) throw new Error('Failed to load word');
        
        const data = await response.json();
        setCurrentWord(data.data.word);
        
        const forbiddenHtml = data.data.forbidden.map(word => 
            `<span class="forbidden-word">${word}</span>`
        ).join('');
        
        stopGame();
        
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
                stopGame();
                showGameOver();
            }
        }, 100);
        
    } catch (error) {
        document.getElementById('content').innerHTML = `
            <div class="error" style="color: red;">Ошибка загрузки</div>
        `;
    }
}

export function nextWord() {
    const modalOverlay = document.getElementById('modalOverlay');
    modalOverlay.style.display = 'none';
    document.getElementById('correctAnswer').style.display = 'none';
    displayRandomWord();
}

export function restartGame() {
    const endGameScreen = document.getElementById('endGameScreen');
    endGameScreen.style.display = 'none';
    
    setCurrentRound(0);
    document.getElementById('activeGame').style.display = 'none';
    document.getElementById('setupScreen').style.display = 'block';
    document.getElementById('correctAnswer').style.display = 'none';
    
    const chatMessages = document.getElementById('chatMessages');
    Array.from(chatMessages.children).forEach(msg => {
        msg.classList.remove('winner-message');
    });
}

export function startCountdown() {
    const wordsInput = document.getElementById('wordsPerGame');
    setMaxRounds(parseInt(wordsInput.value) || 5);
    setCurrentRound(0);

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
            document.getElementById('setupScreen').style.display = 'none';
            document.getElementById('activeGame').style.display = 'block';
            displayRandomWord();
        }
    }, 1000);
}

export function stopGame() {
    clearInterval(gameTimer)
}