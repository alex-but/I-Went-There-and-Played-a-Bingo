### I went there and played a bingo

This is a super simple web app that allows a group of players to play challenge bingo.

* The admin adds a csv file with at least 25 challenges (more is fine) and their difficulty from 1 to 10
* A user enters his name in a tiny web UI home page with something like "Start this game NOW!!!". No registration whatsoever
* A backend (python) will randomize the challenges in a json named with as `player_name.json` and that has for each challenge:
```json
{
    "1x1": {
        "challenge": "...",
        "done": false
    }
}
```
where the key is the position in the 5x5 BINGO matrix
* All players matrixes are visible to all other players
* A player can click on any box from any player to set a challenge DONE or UNDONE
* Done squares are different color
* For frontend we only use HTML5, JS and CSS, served statically by the python server.
* Python server can:
    * serve all files (including player jsons) (GET)
    * add a new player (POST, `{"name": "player1"}`)
    * set "done" (POST, `{"name": "player1", "1x1": {"done": true}}`)
* everytime a user will refresh the page, they have to enter player name.
* There is a dropdown at the top with the registered players
* The app is mobile only
* No registering, no auth. Everything is accessible by everyone
* Not possible to delete users.

Make me the simplest implementation of this app. Use only built in python tools (http.server)

No build, one python script to run, no parameters, hardcoded port 5566.

---

### Getting started

1. Make sure you have Python 3.11+ available.
2. Optionally edit [data/challenges.csv](data/challenges.csv) with 25 or more rows of challenges (the server samples a random 25 for every player).
3. Run the server: `python server.py`
4. Open http://localhost:5566 on your phone (same network) and enter your name with the **Start this game NOW!!!** button.

The server stores a JSON file per player under [players/](players) and serves them verbatim so everyone can see each board. Click or tap any square to toggle its `done` status for any player.

### Running tests

All tests live under [tests/](tests).

* Python backend logic: `python -m unittest discover tests/python`
* Front-end helpers (Node test runner): `node --test tests/js`

### Tests

* Python helpers: `python -m unittest discover tests/python`
* Frontend logic: `node --test tests/js`