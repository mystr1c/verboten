export let maxRounds = 5;
export let currentRound = 0;
export let currentWord = null;


export function setCurrentWord(word) {
    currentWord = word
}

export function setCurrentRound(round) {
    currentRound = round
}

export function setMaxRounds(max) {
    maxRounds = max
}