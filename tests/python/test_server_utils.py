import random
import sys
from pathlib import Path
import unittest

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import server  # noqa: E402


class ServerUtilsTest(unittest.TestCase):
    def setUp(self):
        random.seed(0)

    def test_slugify_basic(self):
        self.assertEqual(server.slugify('Player One'), 'player-one')
        self.assertEqual(server.slugify('PLAYER__TWO'), 'player-two')

    def test_slugify_empty_defaults_to_player(self):
        self.assertEqual(server.slugify(''), 'player')
        self.assertEqual(server.slugify('   '), 'player')

    def test_challenge_board_builds_25_cells(self):
        challenges = [
            {'challenge': f'task {idx}', 'difficulty': (idx % 10) + 1}
            for idx in range(30)
        ]
        board = server.challenge_board(challenges)
        self.assertEqual(len(board), 25)
        for coord, cell in board.items():
            self.assertRegex(coord, r'^[1-5]x[1-5]$')
            self.assertIn('challenge', cell)
            self.assertIn('difficulty', cell)
            self.assertIn('done', cell)
            self.assertIs(cell['done'], False)


if __name__ == '__main__':
    unittest.main()
