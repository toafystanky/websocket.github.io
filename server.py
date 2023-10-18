import asyncio
import websockets

PORT = 6969
print("Server listening on Port " + str(PORT))

connected = {}  # Dictionary to track connected clients and their IPs
banned_clients = set()  # Set to store banned client IPs
message_history = []

async def notify_clients(message):
    for client in connected.values():
        await client['websocket'].send(message)

async def echo(websocket, path):
    print("A client just connected")
    client_ip = websocket.remote_address[0]  # Get the client's IP

    # Check if the client's IP is in the banned set
    if client_ip in banned_clients:
        print(f"Client with IP {client_ip} tried to reconnect but is permanently banned.")
        await websocket.send("You are permanently banned.")
        await websocket.close()
        return

    # Check if the client IP is already connected
    if client_ip in connected:
        print(f"Client IP {client_ip} is already connected. Sending alert message.")
        await websocket.send("You are already connected elsewhere.")
        return

    client_id = len(connected) + 1  # Assign the client ID based on the number of connected clients

    connected[client_id] = {'websocket': websocket, 'ip': client_ip}

    try:
        await notify_clients(f"Client {client_id} has just connected")

        async for message in websocket:
            print(f"Received message from client {client_id}: {message}")
            message_history.append((client_id, message))
            for client in connected.values():
                if client['websocket'] != websocket:
                    await client['websocket'].send(f"Client {client_id}: {message}")

            if "rum" in message.lower():
                banned_clients.add(client_ip)
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
