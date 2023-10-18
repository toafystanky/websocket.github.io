import asyncio
import websockets

class ChatServer:
    def __init__(self):
        self.connected = set()
        self.banned_clients = set()
        self.message_history = []

    async def notify_clients(self, message):
        for conn in self.connected:
            await conn.send(message)

    async def on_connect(self, websocket, path):
        print("A client just connected")
        client_ip = websocket.remote_address[0]  # Get the client's IP

        # Check if the client's IP is in the banned set
        if client_ip in self.banned_clients:
            print(f"Client with IP {client_ip} tried to reconnect but is permanently banned.")
            await websocket.send("You are permanently banned.")
            await websocket.close()
            return

        # Check if the client IP is already connected
        for conn in self.connected:
            if conn.remote_address[0] == client_ip and conn != websocket:
                print(f"Client IP {client_ip} is already connected. Sending alert message.")
                await websocket.send("You are already connected elsewhere.")
                await websocket.close()
                return

        self.connected.add(websocket)
        client_id = len(self.connected)  # Assign the client ID based on the number of connected clients

        try:
            await self.notify_clients(f"Client {client_id} has just connected")

            async for message in websocket:
                print(f"Received message from client {client_id}: {message}")
                self.message_history.append((client_id, message))
                for conn in self.connected:
                    if conn != websocket:
                        await conn.send(f"Client {client_id}: {message}")

                if "rum" in message.lower():
                    self.banned_clients.add(client_ip)
                    await websocket.send("You are permanently banned.")
                    await websocket.close()
                    if websocket in self.connected:
                        self.connected.remove(websocket)

                    return

        except websockets.exceptions.ConnectionClosedError:
            pass

        finally:
            if websocket in self.connected:
                self.connected.remove(websocket)

def run_server():
    chat_server = ChatServer()
    start_server = websockets.serve(chat_server.on_connect, "0.0.0.0", 6969)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    run_server()
