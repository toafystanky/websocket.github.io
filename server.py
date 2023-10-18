import asyncio
import websockets

PORT = 6969
print("Server listening on Port " + str(PORT))

connected = set()
banned_clients = set()  # Set to store banned client IPs
message_history = []

async def notify_clients(message):
    for conn in connected:
        await conn.send(message)

async def echo(websocket, path):
    print("A client just connected")
    client_ip = websocket.remote_address[0]  # Get the client's IP

    if client_ip in banned_clients:
        print(f"Client with IP {client_ip} tried to reconnect but is permanently banned.")
        await websocket.send("You are permanently banned.")
        await websocket.close()
        return

    connected.add(websocket)
    client_id = len(connected)  # Assign the client ID based on the number of connected clients

    try:
        await notify_clients(f"Client {client_id} has just connected")

        async for message in websocket:
            print(f"Received message from client {client_id}: {message}")
            message_history.append((client_id, message))

            if "rum" in message.lower():
                banned_clients.add(client_ip)
                await websocket.send("You are permanently banned.")
                await websocket.close()
                if websocket in connected:
                    connected.remove(websocket)
                return



    except websockets.exceptions.ConnectionClosedError:
        pass

    finally:
        if websocket in connected:
            connected.remove(websocket)

start_server = websockets.serve(echo, "0.0.0.0", PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
