const state = {
    players: [],
    boards: new Map(),
};

const boardsEl = document.getElementById('boards');
const statusEl = document.getElementById('status');
const selectEl = document.getElementById('playerSelect');
const refreshBtn = document.getElementById('refreshBoards');
const formEl = document.getElementById('startForm');
const nameInput = document.getElementById('playerName');

const statusClasses = {
    info: '--info',
    error: '--error',
};

function setStatus(message, tone = 'info') {
    statusEl.textContent = message;
    statusEl.dataset.tone = statusClasses[tone] || '--info';
}

async function refreshBoards(showMessage = true) {
    boardsEl.setAttribute('aria-busy', 'true');
    try {
        await fetchPlayers();
        if (showMessage) {
            setStatus('Boards refreshed');
        }
    } catch (error) {
        console.error(error);
        setStatus('Unable to refresh boards', 'error');
    } finally {
        boardsEl.setAttribute('aria-busy', 'false');
    }
}

async function fetchPlayers() {
    const response = await fetch('/api/players', { cache: 'no-store' });
    if (!response.ok) {
        throw new Error('Player list failed to load');
    }
    const data = await response.json();
    state.players = data.players || [];
    await Promise.all(
        state.players.map((player) =>
            fetchBoard(player).catch((error) => {
                console.error(error);
            })
        )
    );
    renderPlayerSelect();
    renderBoards();
}

async function fetchBoard(player) {
    const response = await fetch(player.file, { cache: 'no-store' });
    if (!response.ok) {
        throw new Error(`Board for ${player.name} is missing`);
    }
    const boardData = await response.json();
    state.boards.set(player.slug, boardData);
}

function renderPlayerSelect() {
    selectEl.innerHTML = '';
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = state.players.length ? 'Pick a player' : 'No players yet';
    selectEl.appendChild(placeholder);

    state.players.forEach((player) => {
        const option = document.createElement('option');
        option.value = player.slug;
        option.textContent = player.name;
        selectEl.appendChild(option);
    });
}

function renderBoards() {
    boardsEl.innerHTML = '';
    if (!state.players.length) {
        const empty = document.createElement('p');
        empty.textContent = 'No bingo boards yet. Start the game!';
        boardsEl.appendChild(empty);
        return;
    }

    state.players.forEach((player) => {
        const boardPayload = state.boards.get(player.slug);
        if (!boardPayload || !boardPayload.board) {
            return;
        }

        const card = document.createElement('article');
        card.className = 'board-card';
        card.id = `board-${player.slug}`;
        card.dataset.difficulty = `avg diff ${averageDifficulty(boardPayload.board)}/10`;

        const title = document.createElement('h2');
        title.textContent = player.name;
        card.appendChild(title);

        const helper = document.createElement('p');
        helper.textContent = 'Tap a tile to toggle done for anyone.';
        card.appendChild(helper);

        const grid = document.createElement('div');
        grid.className = 'challenge-grid';

        Object.entries(boardPayload.board)
            .sort(([a], [b]) => (a > b ? 1 : -1))
            .forEach(([cellKey, cellValue]) => {
            const cellButton = document.createElement('button');
            cellButton.type = 'button';
            cellButton.className = 'challenge-cell';
            cellButton.dataset.slug = player.slug;
            cellButton.dataset.cell = cellKey;
            cellButton.dataset.playerName = boardPayload.name;

            if (cellValue.done) {
                cellButton.classList.add('is-done');
            }

            const badge = document.createElement('strong');
            badge.textContent = `${cellKey} · diff ${cellValue.difficulty}`;
            const text = document.createElement('span');
            text.textContent = cellValue.challenge;
            const stateLabel = document.createElement('em');
            stateLabel.textContent = cellValue.done ? 'Done ✔' : 'Open';

            cellButton.appendChild(badge);
            cellButton.appendChild(text);
            cellButton.appendChild(stateLabel);
            cellButton.addEventListener('click', handleCellToggle);

                grid.appendChild(cellButton);
            });

        card.appendChild(grid);
        boardsEl.appendChild(card);
    });
}

function averageDifficulty(board) {
    const values = Object.values(board);
    const total = values.reduce((sum, cell) => sum + Number(cell.difficulty || 0), 0);
    return Math.round(total / values.length) || 0;
}

async function handleCellToggle(event) {
    const cell = event.currentTarget;
    const slug = cell.dataset.slug;
    const cellKey = cell.dataset.cell;
    const boardPayload = state.boards.get(slug);
    if (!boardPayload) {
        return;
    }

    const currentState = boardPayload.board[cellKey];
    const nextState = !currentState.done;
    const payload = { name: boardPayload.name };
    payload[cellKey] = { done: nextState };

    cell.disabled = true;
    try {
        const response = await fetch('/api/state', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            throw new Error('Update failed');
        }
        const data = await response.json();
        state.boards.set(slug, data.player);
        renderBoards();
        setStatus(`${boardPayload.name} toggled ${cellKey}`);
    } catch (error) {
        console.error(error);
        setStatus('Could not update cell', 'error');
    } finally {
        cell.disabled = false;
    }
}

formEl.addEventListener('submit', async (event) => {
    event.preventDefault();
    const name = nameInput.value.trim();
    if (!name) {
        setStatus('Enter your name first', 'error');
        return;
    }

    setStatus('Spinning your challenges...');
    try {
        const response = await fetch('/api/player', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name }),
        });
        if (!response.ok) {
            throw new Error('Failed to create player');
        }
        const data = await response.json();
        state.players = data.players || [];
        if (data.player) {
            state.boards.set(data.player.slug, data.player);
        }
        renderPlayerSelect();
        renderBoards();
        nameInput.value = '';
        setStatus('Board ready! Tap away.');
    } catch (error) {
        console.error(error);
        setStatus('Could not start the game', 'error');
    }
});

refreshBtn.addEventListener('click', () => refreshBoards());

selectEl.addEventListener('change', (event) => {
    const slug = event.target.value;
    if (!slug) {
        return;
    }
    const target = document.getElementById(`board-${slug}`);
    if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});

window.addEventListener('load', () => {
    refreshBoards(false).catch((error) => {
        console.error(error);
        setStatus('Server not ready yet', 'error');
    });
});
