from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import httpx
import json

app = FastAPI()

API_URL = "http://localhost:3000/updateVestraFindLexi"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()

            try:
                data = json.loads(message)
                document = data.get("document")
                lexi = data.get("lexi")

                if not document or not lexi:
                    await websocket.send_json({ "status": 400, "nexa": None })
                    continue

                async with httpx.AsyncClient() as client:
                    response = await client.post(API_URL, json={
                        "document": document,
                        "lexi": lexi
                    })

                if response.status_code == 200:
                    result = response.json()
                    nexa = result.get("nexa")
                    if nexa:
                        await websocket.send_json({ "status": 200, "nexa": nexa })
                    else:
                        await websocket.send_json({ "status": 400, "nexa": None })
                else:
                    await websocket.send_json({ "status": 400, "nexa": None })

            except json.JSONDecodeError:
                await websocket.send_json({ "status": 400, "nexa": None })
            except Exception as e:
                print("Server error:", e)
                await websocket.send_json({ "status": 400, "nexa": None })

    except WebSocketDisconnect:
        print("Client disconnected")
