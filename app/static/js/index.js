import { checkAuth } from './services/auth.js'
import { startCountdown, nextWord, restartGame } from './game/engine.js'

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('startButton').addEventListener('click', startCountdown)
    document.getElementById('nextWordButton').addEventListener('click', nextWord)
    document.getElementById('restartButton').addEventListener('click', restartGame)
    checkAuth();
    scaleApp();
})


function scaleApp() {
    const container = document.querySelector('.main-container');
    const padding = 20;
    const scaleX = (window.innerWidth - padding * 2) / 1280;
    const scaleY = (window.innerHeight - padding * 2) / 720;
    const scale = Math.min(scaleX, scaleY);
    container.style.transform = `translate(-50%, -50%) scale(${scale})`;
}

window.addEventListener('resize', scaleApp);
