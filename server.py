import asyncio
import websockets

PORT = 6969
print("Server listening on Port " + str(PORT))

connected = {}  # Dictionary to track connected clients
banned_clients = set()  # Set to store banned client IDs
client_id_counter = 0
message_history = []

async def notify_clients(message):
    for client in connected.values():
        await client['websocket'].send(message)

async def echo(websocket, path):
    global client_id_counter
    client_id_counter += 1  # Increment client ID for each new connection
    client_id = client_id_counter

    connected[client_id] = {'websocket': websocket, 'ip': websocket.remote_address[0]}

    try:
        await notify_clients(f"Client {client_id} has just connected")

        async for message in websocket:
            print(f"Received message from client {client_id}: {message}")
            message_history.append((client_id, message))
            for client in connected.values():
                if client['websocket'] != websocket:
                    await client['websocket'].send(f"Client {client_id}: {message}")

            if "rum" in message.lower():
                banned_clients.add(client_id)
                await websocket.send("You are permanently banned.")
                if client_id in connected:
                    del connected[client_id]

                return

    except websockets.exceptions.ConnectionClosedError:
        pass

    finally:
        if client_id in connected:
            del connected[client_id]

start_server = websockets.serve(echo, "0.0.0.0", PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
