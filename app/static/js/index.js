import { checkAuth } from './services/auth.js'
import { startCountdown, nextWord, restartGame } from './game/engine.js'

checkAuth();

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('startButton').addEventListener('click', startCountdown)
    document.getElementById('nextWordButton').addEventListener('click', nextWord)
    document.getElementById('restartButton').addEventListener('click', restartGame)
})