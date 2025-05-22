import json
import threading
import socket
import time


class Client:
    def __init__(self,
                 server_host,
                 server_port_tcp=12345,
                 server_port_udp=54321,
                 client_port_udp=0):  # 0 for dynamic UDP port allocation
        """
        Create a game server client
        """
        self.identifier = None
        self.server_host = server_host
        self.server_port_tcp = server_port_tcp
        self.server_port_udp = server_port_udp
        self.client_host = socket.gethostbyname(socket.gethostname())

        # UDP socket for communication
        self.client_udp = (self.client_host, client_port_udp)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind(self.client_udp)
        self.client_udp = self.udp_sock.getsockname()  # Update with actual port if it was 0

        self.server_message = []
        self.lock = threading.Lock()
        self.udp_thread = SocketThread(self.client_udp, self, self.lock)

    def register(self):
        """
        Register the client to server and get a unique identifier
        """
        message = json.dumps({
            "action": "register",
            "payload": self.client_udp[1]
        })

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.server_host, self.server_port_tcp))
            sock.send(message.encode())
            response = sock.recv(1024).decode()
            data = json.loads(response)
            if data["success"]:
                self.identifier = data["identifier"]
                print(f"[REGISTERED] Identifier: {self.identifier}")
            else:
                print(f"[ERROR] Registration failed: {data['message']}")
            sock.close()
        except Exception as e:
            print(f"[ERROR] TCP registration failed: {e}")

    def send(self, message):
        """
        Send data to all players
        """
        if not self.identifier:
            print("[SEND] Client not registered!")
            return

        msg = json.dumps({
            "identifier": self.identifier,
            "message": message
        })

        try:
            self.udp_sock.sendto(msg.encode(), (self.server_host, self.server_port_udp))
        except Exception as e:
            print(f"[ERROR] UDP send failed: {e}")

    def parse_data(self, data):
        """
        Parse response from server
        """
        try:
            msg = json.loads(data.decode())
            return msg
        except:
            return {"message": data.decode()}

    def get_messages(self):
        """
        Get received messages from server
        """
        messages = []
        self.lock.acquire()
        try:
            while self.server_message:
                data = self.server_message.pop(0)
                msg = self.parse_data(data)
                messages.append(msg)
        finally:
            self.lock.release()
        return messages

    def run(self):
        """
        Start client threads
        """
        self.udp_thread.start()

    def stop(self):
        """
        Stop the client
        """
        self.udp_thread.stop()
        self.udp_sock.close()
        print("[CLIENT] Stopped")


class SocketThread(threading.Thread):
    def __init__(self, addr, client, lock):
        """
        Client UDP connection
        """
        threading.Thread.__init__(self)
        self.client = client
        self.lock = lock
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(addr)
        self.is_running = True

    def run(self):
        """
        Get responses from server
        """
        while self.is_running:
            try:
                data, addr = self.sock.recvfrom(1024)
                with self.lock:
                    self.client.server_message.append(data)
            except:
                break

    def stop(self):
        """
        Stop thread
        """
        self.is_running = False
        self.sock.close()


if __name__ == "__main__":
    """
    Example with 4 clients
    """
    clients = []
    for i in range(4):
        print(f"\n[CLIENT {i}] Starting...")
        client = Client("127.0.0.1", 12345, 54321)
        client.register()
        client.run()
        clients.append(client)

    print("\n[ALL CLIENTS REGISTERED] Sending messages...")

    try:
        for i, client in enumerate(clients):
            msg = f"Hello from client {i}"
            client.send(msg)

        time.sleep(3)  # Wait for messages to be received

        for i, client in enumerate(clients):
            print(f"\n[CLIENT {i}] Messages received:")
            for msg in client.get_messages():
                print("  -", msg)
    finally:
        for client in clients:
            client.stop()
