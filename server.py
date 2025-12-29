#!/usr/bin/env python3
"""Minimal challenge bingo server powered by http.server."""

from __future__ import annotations

import csv
import json
import random
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from typing import Dict, List
from urllib.parse import urlparse

BASE_DIR = Path(__file__).parent.resolve()
PUBLIC_DIR = BASE_DIR / "public"
DATA_DIR = BASE_DIR / "data"
PLAYERS_DIR = BASE_DIR / "players"
CHALLENGES_FILE = DATA_DIR / "challenges.csv"
PORT = 5566
BOARD_DIMENSION = 5
BOARD_SIZE = BOARD_DIMENSION * BOARD_DIMENSION

Challenge = Dict[str, object]
Board = Dict[str, Dict[str, object]]


def ensure_directories() -> None:
    """Create runtime directories if they are missing."""
    for path in (PUBLIC_DIR, DATA_DIR, PLAYERS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_challenges() -> List[Challenge]:
    """Load challenges from CSV and validate we have at least 25 entries."""
    if not CHALLENGES_FILE.exists():
        raise FileNotFoundError(
            f"Missing challenge list: {CHALLENGES_FILE}. Add 25 rows before starting the server."
        )

    challenges: List[Challenge] = []
    with CHALLENGES_FILE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            text = (row.get("challenge") or row.get("Challenge") or "").strip()
            difficulty_raw = (row.get("difficulty") or row.get("Difficulty") or "").strip()
            if not text:
                continue
            try:
                difficulty = int(difficulty_raw)
            except ValueError:
                continue
            difficulty = max(1, min(10, difficulty))
            challenges.append({"challenge": text, "difficulty": difficulty})

    if len(challenges) < 25:
        raise ValueError(
            f"Need at least {BOARD_SIZE} challenges to fill the bingo board. "
            f"Found {len(challenges)} entries in {CHALLENGES_FILE}."
        )
    return challenges


def slugify(name: str) -> str:
    """Convert a player supplied name into a filesystem-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "player"


def challenge_board(challenges: List[Challenge]) -> Board:
    """Return a randomized 5x5 board for a player."""
    picks = random.sample(challenges, BOARD_SIZE)
    board: Board = {}
    idx = 0
    for row in range(BOARD_DIMENSION):
        for col in range(BOARD_DIMENSION):
            cell_key = f"{row + 1}x{col + 1}"
            payload = picks[idx]
            board[cell_key] = {
                "challenge": payload["challenge"],
                "difficulty": payload["difficulty"],
                "done": False,
            }
            idx += 1
    return board


def player_file(slug: str) -> Path:
    return (PLAYERS_DIR / f"{slug}.json").resolve()


def list_players() -> List[Dict[str, str]]:
    players: List[Dict[str, str]] = []
    for file_path in sorted(PLAYERS_DIR.glob("*.json")):
        try:
            with file_path.open(encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            continue
        players.append(
            {
                "name": data.get("name", file_path.stem),
                "slug": file_path.stem,
                "file": f"/players/{file_path.name}",
            }
        )
    return players


CHALLENGES = []


class BingoHandler(SimpleHTTPRequestHandler):
    """Serve static assets alongside a tiny JSON API."""

    server_version = "BingoHTTP/0.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    # Routing helpers -----------------------------------------------------
    def _json_body(self) -> Dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON payload") from exc

    def _send_json(self, payload: Dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _bad_request(self, message: str) -> None:
        self._send_json({"error": message}, status=400)

    # API endpoints -------------------------------------------------------
    def do_POST(self) -> None:
        if self.path == "/api/player":
            self._handle_create_player()
            return
        if self.path == "/api/state":
            self._handle_toggle_state()
            return
        self.send_error(404, "Unknown endpoint")

    def do_GET(self) -> None:
        if self.path == "/api/players":
            self._send_json({"players": list_players()})
            return
        if self.path in ("/", ""):
            self.path = "/index.html"
        super().do_GET()

    def translate_path(self, path: str) -> str:
        parsed = urlparse(path)
        request_path = PurePosixPath(parsed.path)
        if len(request_path.parts) >= 2 and request_path.parts[:2] == ("/", "players"):
            rel_parts = request_path.parts[2:]
            rel = PurePosixPath(*rel_parts) if rel_parts else PurePosixPath(".")
            target = (PLAYERS_DIR / rel).resolve()
            if str(target).startswith(str(PLAYERS_DIR)):
                return str(target)
            return str(PLAYERS_DIR)
        return super().translate_path(path)

    # Internal helpers ----------------------------------------------------
    def _handle_create_player(self) -> None:
        try:
            payload = self._json_body()
        except ValueError as exc:
            self._bad_request(str(exc))
            return

        raw_name = str(payload.get("name", "")).strip()
        if not raw_name:
            self._bad_request("Missing player name")
            return

        slug = slugify(raw_name)
        file_path = player_file(slug)
        if file_path.exists():
            with file_path.open(encoding="utf-8") as handle:
                player_data = json.load(handle)
        else:
            board = challenge_board(CHALLENGES)
            player_data = {"name": raw_name, "slug": slug, "board": board}
            with file_path.open("w", encoding="utf-8") as handle:
                json.dump(player_data, handle, indent=2)

        self._send_json({"player": player_data, "players": list_players()}, status=201)

    def _handle_toggle_state(self) -> None:
        try:
            payload = self._json_body()
        except ValueError as exc:
            self._bad_request(str(exc))
            return

        raw_name = str(payload.get("name", "")).strip()
        if not raw_name:
            self._bad_request("Missing player name")
            return

        slug = slugify(raw_name)
        file_path = player_file(slug)
        if not file_path.exists():
            self.send_error(404, "Player not found")
            return

        cell_key = payload.get("cell")
        if not cell_key:
            dynamic_keys = [key for key in payload.keys() if key != "name"]
            cell_key = dynamic_keys[0] if dynamic_keys else None
        if not isinstance(cell_key, str):
            self._bad_request("Missing cell coordinate")
            return

        update_payload = payload.get("cell" if "cell" in payload else cell_key)
        if not isinstance(update_payload, dict):
            self._bad_request("Missing done flag")
            return

        if "done" not in update_payload:
            self._bad_request("Missing done flag")
            return

        done_state = bool(update_payload["done"])

        with file_path.open(encoding="utf-8") as handle:
            player_data = json.load(handle)

        board = player_data.get("board", {})
        if cell_key not in board:
            self._bad_request("Unknown cell coordinate")
            return

        board[cell_key]["done"] = done_state

        with file_path.open("w", encoding="utf-8") as handle:
            json.dump(player_data, handle, indent=2)

        self._send_json({"player": player_data})


def main() -> None:
    ensure_directories()
    global CHALLENGES
    CHALLENGES = load_challenges()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), BingoHandler)
    print(f"Challenge bingo running on http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
