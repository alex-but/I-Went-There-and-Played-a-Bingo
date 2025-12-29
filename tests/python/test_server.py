import unittest

import server


class ServerLogicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_challenges = [
            {"challenge": f"Challenge #{idx}", "difficulty": (idx % 10) + 1}
            for idx in range(30)
        ]

    def test_slugify_removes_non_alnum(self) -> None:
        self.assertEqual(server.slugify("Alice Smith!!"), "alice-smith")
        self.assertEqual(server.slugify("   123   "), "123")
        self.assertEqual(server.slugify(""), "player")

    def test_challenge_board_is_5x5(self) -> None:
        board = server.challenge_board(self.sample_challenges)
        self.assertEqual(len(board), 25)
        for row in range(1, 6):
            for col in range(1, 6):
                key = f"{row}x{col}"
                self.assertIn(key, board)
                cell = board[key]
                self.assertIn("challenge", cell)
                self.assertIn("difficulty", cell)
                self.assertFalse(cell.get("done"))


if __name__ == "__main__":
    unittest.main()
