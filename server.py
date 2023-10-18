import asyncio
import websockets

PORT = 6969
print("Server listening on Port " + str(PORT))

connected = set()
banned_clients = set()  # Set to store banned client IPs
message_history = []
connected_ips = set()  # Set to track connected IPs

async def notify_clients(message):
    for conn in connected:
        await conn.send(message)

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
    if client_ip in connected_ips:
        print(f"Client IP {client_ip} is already connected. Sending alert message.")
        await websocket.send("You are already connected elsewhere.")
        return

    connected.add(websocket)
    connected_ips.add(client_ip)
    client_id = len(connected)  # Assign the client ID based on the number of connected clients

    try:
        await notify_clients(f"Client {client_id} has just connected")

        async for message in websocket:
            print(f"Received message from client {client_id}: {message}")
            message_history.append((client_id, message))
            for client in connected:
                if client != websocket:
                    await client.send(f"Client {client_id}: {message}")

            if "rum" in message.lower():
                banned_clients.add(client_ip)
                await websocket.send("You are permanently banned.")
                if websocket in connected:
                    connected.remove(websocket)
                connected_ips.remove(client_ip)

                return

    except websockets.exceptions.ConnectionClosedError:
        pass

    finally:
        if websocket in connected:
            connected.remove(websocket)
        if client_ip in connected_ips:
            connected_ips.remove(client_ip)

start_server = websockets.serve(echo, "0.0.0.0", PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
