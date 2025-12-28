import * as Y from "https://cdn.jsdelivr.net/npm/yjs/+esm";
import { WebrtcProvider } from "https://cdn.jsdelivr.net/npm/y-webrtc/+esm";
import { IndexeddbPersistence } from "https://cdn.jsdelivr.net/npm/y-indexeddb/+esm";

const ydoc = new Y.Doc();
new IndexeddbPersistence("lan-yjs-json-demo", ydoc);

const provider = new WebrtcProvider("lan-json-room", ydoc, {
  signaling: [],
  peerOpts: { config: { iceServers: [] } }
});

const ymap = ydoc.getMap("shared-json");
if (ymap.size === 0) {
  ymap.set("data", { counter: 0, updatedAt: Date.now() });
}

const view = document.getElementById("jsonView");
const peerBox = document.getElementById("peerInfo");

function render() {
  const data = ymap.get("data");
  view.textContent = JSON.stringify(data, null, 2);
}

ymap.observe(render);
render();

document.getElementById("updateBtn").onclick = () => {
  const data = ymap.get("data");
  ymap.set("data", {
    ...data,
    counter: data.counter + 1,
    updatedAt: Date.now()
  });
};

// Show connected peer count (just for fun)
provider.on("peers", (peers) => {
  peerBox.textContent = `Connected peers on LAN: ${peers.length}`;
});
