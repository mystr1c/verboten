import { game_id, currentWord, leaderboard, addPoints } from "../game/state.js";

export function showUserInfo(user) {
    document.getElementById('userInfo').innerHTML = `
        <div class="user-info">
            <img src="${user.profile_image_url}" alt="${user.display_name}" class="user-avatar">
            <div class="user-name">${user.display_name}</div>
        </div>
    `;
    document.getElementById('userInfo').style.display = 'block';
}

export function showCorrectAnswer(username) {
    const modalOverlay = document.getElementById('modalOverlay');
    const modalText = document.getElementById('modalText');
    
    modalText.textContent = `${username} угадал слово!`;
    modalOverlay.style.display = 'flex';

    addPoints(username)

    fetch(`/api/leaderboard/${game_id}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'nickname': username})
    })
    updateWordStatus()
}

export function showGameOver() {
    const modalOverlay = document.getElementById('modalOverlay');
    const modalText = document.getElementById('modalText');
    
    modalText.textContent = 'Увы, время вышло!';
    modalOverlay.style.display = 'flex';

    updateWordStatus()
}

export function showEndGame() {
    const gameOverOverlay = document.getElementById('endGameScreen');
    gameOverOverlay.style.display = 'flex';
}

function updateWordStatus() {
    fetch(`/api/word/${game_id}/${currentWord}`, {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'status': 'finished'})
    })
}