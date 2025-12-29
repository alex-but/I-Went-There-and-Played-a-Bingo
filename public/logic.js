(function attachLogic(globalScope) {
    function averageDifficulty(board) {
        if (!board) {
            return 0;
        }
        const entries = Object.values(board);
        if (!entries.length) {
            return 0;
        }
        const total = entries.reduce((sum, cell) => {
            const difficulty = Number(cell && cell.difficulty ? cell.difficulty : 0);
            return sum + (Number.isFinite(difficulty) ? difficulty : 0);
        }, 0);
        return Math.round(total / entries.length) || 0;
    }

    function buildTogglePayload(playerName, cellKey, doneState) {
        if (!playerName) {
            throw new Error('playerName is required');
        }
        if (!cellKey) {
            throw new Error('cellKey is required');
        }
        return {
            name: playerName,
            [cellKey]: {
                done: Boolean(doneState),
            },
        };
    }

    const api = { averageDifficulty, buildTogglePayload };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    } else {
        globalScope.BingoLogic = api;
    }
})(typeof window !== 'undefined' ? window : globalThis);
