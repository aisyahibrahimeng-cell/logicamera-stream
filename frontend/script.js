const camFeed = document.getElementById("cam-feed");

// WebSocket for livestream
const ws = new WebSocket("wss://" + location.host + "/ws");
ws.onmessage = (event) => {
    camFeed.src = "data:image/jpeg;base64," + event.data;
};

// Send HTTP commands to Flask server
async function sendCommand(cmd) {
    try {
        const resp = await fetch("https://" + location.host + "/control", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ cmd })
        });
        if (resp.ok) {
            console.log("Command sent:", cmd);
        } else {
            console.error("Failed to send command");
        }
    } catch (err) {
        console.error("Error sending command:", err);
    }
}


// Button controls
document.getElementById("forward").addEventListener("click", () => sendCommand("forward"));
document.getElementById("backward").addEventListener("click", () => sendCommand("backward"));
document.getElementById("left").addEventListener("click", () => sendCommand("left"));
document.getElementById("right").addEventListener("click", () => sendCommand("right"));
document.getElementById("stop").addEventListener("click", () => sendCommand("stop"));
