export let maxRounds = 5;
export let currentRound = 0;
export let currentWord = null;
export let timer_limit = 30
export let game_id = null
export let leaderboard = {}


export function setCurrentWord(word) {
    currentWord = word
}

export function setCurrentRound(round) {
    currentRound = round
}

export function setMaxRounds(max) {
    maxRounds = max
}

export function setTimerLimit(limit) {
    timer_limit = limit
}

export function setGameId(id) {
    game_id = id
}

export function addPoints(username) {
    leaderboard[username] = (leaderboard[username] || 0) + 1
}

export function clearLeaderboard() {
    leaderboard = {}
}