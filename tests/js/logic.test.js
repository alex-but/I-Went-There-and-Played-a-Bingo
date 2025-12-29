const path = require('node:path');
const test = require('node:test');
const assert = require('node:assert/strict');

const logicPath = path.join(__dirname, '../../public/logic.js');
const { averageDifficulty, buildTogglePayload } = require(logicPath);

test('averageDifficulty rounds the mean difficulty of a board', () => {
    const board = {
        '1x1': { difficulty: 1 },
        '1x2': { difficulty: 10 },
        '1x3': { difficulty: 5 },
    };
    const result = averageDifficulty(board);
    assert.equal(result, 5);
});

test('averageDifficulty tolerates missing or non numeric values', () => {
    const board = {
        '2x1': { difficulty: '4' },
        '2x2': {},
    };
    const result = averageDifficulty(board);
    assert.equal(result, 2);
});

test('buildTogglePayload shapes the POST body expected by the API', () => {
    const payload = buildTogglePayload('Alice', '3x3', true);
    assert.deepEqual(payload, {
        name: 'Alice',
        '3x3': { done: true },
    });
});

test('buildTogglePayload coerces done to boolean', () => {
    const payload = buildTogglePayload('Bob', '5x5', 0);
    assert.equal(payload['5x5'].done, false);
});

test('buildTogglePayload rejects missing params', () => {
    assert.throws(() => buildTogglePayload('', '1x1', true));
    assert.throws(() => buildTogglePayload('Alice', '', true));
});
