from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request

app = FastAPI()

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

viewers = set()
last_frame = None

# Serve the HTML page
@app.get("/")
async def index():
    return FileResponse("frontend/index.html")

# WebSocket for viewers
@app.websocket("/ws")
async def websocket_viewer(websocket: WebSocket):
    global last_frame
    await websocket.accept()
    viewers.add(websocket)
    print("Viewer connected")

    # Send the last frame immediately
    if last_frame:
        await websocket.send_text(last_frame)

    try:
        while True:
            await websocket.receive_text()  # viewers send nothing
    except:
        viewers.remove(websocket)
        print("Viewer disconnected")

# WebSocket for Raspberry Pi to upload frames
@app.websocket("/upload")
async def websocket_upload(websocket: WebSocket):
    global last_frame
    await websocket.accept()
    print("Pi connected")

    try:
        while True:
            frame = await websocket.receive_text()  # base64 JPEG
            last_frame = frame

            dead = []
            for v in viewers:
                try:
                    await v.send_text(frame)
                except:
                    dead.append(v)
            for v in dead:
                viewers.remove(v)
    except:
        print("Pi disconnected")

@app.post("/control")
async def control_car(request: Request):
    data = await request.json()
    cmd = data.get("cmd")
    print(f"Command received: {cmd}")
    # Here you can forward cmd to ROS2, or handle accordingly
    return {"status": "ok", "cmd": cmd}