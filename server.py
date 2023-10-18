import asyncio
import websockets

PORT = 6969
print("Server listening on Port " + str(PORT))

class Message():
    def __init__(self, client_id, message):
        self.client_id = client_id
        self.message = message

    def __str__(self):
        return f"({self.client_id}, {self.message})"


banned_clients = set()
connected = {}
next_client_id = 1
messages = []


async def handle_client(websocket, path):
    global next_client_id
    client_id = next_client_id
    next_client_id += 1

    client_ip = websocket.remote_address[0]

    if client_ip in banned_clients:
        await websocket.send("You are banned from the server.")
        await websocket.close()
        return

    connected[client_id] = websocket

    try:
        async for message in websocket:
            print(f"Client {client_id} sent: {message}")
            messages.append(Message(client_id, message))

            for id, client in connected.items():
                if id != client_id:
                    await client.send(f"Client {client_id}: {message}")

            if "rum" in message.lower():
                banned_clients.add(client_ip)
                await websocket.send("You have been banned for using the word 'rum'.")
                await websocket.close()

    except websockets.exceptions.ConnectionClosedError:
        pass

    finally:
        del connected[client_id]
        print(f"Client {client_id} disconnected")


start_server = websockets.serve(handle_client, "0.0.0.0", PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
