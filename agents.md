# LAN P2P JSON Sync — Tiny App Spec

## Goal
A minimal browser app that:
- Runs fully **peer-to-peer on LAN**
- Syncs a shared **JSON object** using **Yjs + WebRTC mesh**
- Stores data locally in **IndexedDB**
- Is delivered as static files (e.g., GitHub Pages)
- Can be tested using Python’s built-in HTTP server

## Core Rules
1. **No internet dependency** at runtime.
2. **No signaling/TURN/STUN servers** — WebRTC must connect directly over LAN.
3. **Data ownership is local-first** — each browser persists the latest Yjs document in IndexedDB.
4. **Shared state is a single JSON object** stored under Y.Map key `"data"`.
5. **Edits must replace the JSON atomically** using `ymap.set("data", newJSON)`.
6. **CRDT conflict resolution is automatic** via Yjs. Do not implement manual merge logic.
7. **Room name must be constant** across peers: `"lan-json-room"`.
8. **App bundle must be tiny** — prefer CDN ESM imports, no build step.
9. **UI must be minimal and stable** — render JSON in a `<pre>` block and provide a button to mutate it.
10. **Console logs are allowed** for debugging but must not break execution if absent.

## Data Schema (JSON)
The shared JSON object must follow this shape:

