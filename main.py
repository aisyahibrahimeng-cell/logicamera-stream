from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

control_clients = set()  
pi_clients = set()  

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
    except Exception as e:
        viewers.remove(websocket)
        print("Viewer disconnected:", e)

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

@app.websocket("/control-ws")
async def control_ws(websocket: WebSocket):
    await websocket.accept()
    control_clients.add(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            # Forward to Pi(s)
            for p in pi_clients.copy():
                try:
                    await p.send_text(msg)
                except:
                    pi_clients.remove(p)
    except:
        control_clients.remove(websocket)
        
@app.websocket("/pi-control")
async def pi_control_ws(websocket: WebSocket):
    await websocket.accept()
    pi_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  
    except:
        pi_clients.remove(websocket)

