#!/usr/bin/python

import argparse
import socket
import json
import time
from threading import Thread, Lock
from player import Player

class UdpServer(Thread):
    def __init__(self, udp_port, lock):
        super().__init__()
        self.udp_port = udp_port
        self.lock = lock
        self.players = {}
        self.is_running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", udp_port))

    def run(self):
        print(f"[UDP] Server listening on port {self.udp_port}")
        while self.is_running:
            try:
                data, addr = self.sock.recvfrom(1024)
                with self.lock:
                    for pid, player in self.players.items():
                        if player.addr != addr:
                            self.sock.sendto(data, player.addr)
            except Exception as e:
                if self.is_running:
                    print(f"[UDP] Error: {e}")

    def register_player(self, identifier, addr):
        with self.lock:
            self.players[identifier] = Player(identifier, addr)

    def send(self, identifier, message, sock):
        with self.lock:
            for pid, player in self.players.items():
                if pid != identifier:
                    sock.sendto(message.encode(), player.addr)

    def stop(self):
        self.is_running = False
        self.sock.close()
        print("[UDP] Server stopped")


class TcpServer(Thread):
    def __init__(self, tcp_port, udp_server, lock):
        super().__init__()
        self.tcp_port = tcp_port
        self.lock = lock
        self.udp_server = udp_server
        self.players = {}
        self.is_running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("", tcp_port))
        self.sock.listen(5)

    def run(self):
        print(f"[TCP] Server listening on port {self.tcp_port}")
        while self.is_running:
            try:
                conn, addr = self.sock.accept()
                Thread(target=self.handle_client, args=(conn, addr)).start()
            except Exception as e:
                if self.is_running:
                    print(f"[TCP] Accept error: {e}")

    def handle_client(self, conn, addr):
        try:
            data = conn.recv(1024).decode()
            message = json.loads(data)
            action = message.get("action")
            payload = message.get("payload")
            if action == "register":
                udp_port = int(payload)
                identifier = f"{addr[0]}:{udp_port}"
                player = Player(identifier, (addr[0], udp_port))
                with self.lock:
                    self.players[identifier] = player
                    self.udp_server.register_player(identifier, (addr[0], udp_port))
                response = json.dumps({"success": True, "identifier": identifier})
                conn.send(response.encode())
                print(f"[TCP] Registered player {identifier}")
            else:
                response = json.dumps({"success": False, "message": "Unknown action"})
                conn.send(response.encode())
        except Exception as e:
            print(f"[TCP] Client error: {e}")
        finally:
            conn.close()

    def stop(self):
        self.is_running = False
        self.sock.close()
        print("[TCP] Server stopped")


def main_loop(tcp_port, udp_port):
    lock = Lock()
    udp_server = UdpServer(udp_port, lock)
    tcp_server = TcpServer(tcp_port, udp_server, lock)

    udp_server.start()
    tcp_server.start()

    print("--------------------------------------")
    print(" Simple Game Server Started.")
    print(" Press Ctrl+C to stop.")
    print("--------------------------------------")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Main] Shutting down servers...")
        udp_server.stop()
        tcp_server.stop()
        udp_server.join()
        tcp_server.join()
        print("[Main] Servers stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Game Server")
    parser.add_argument("--tcp", type=int, default=12345, help="TCP port")
    parser.add_argument("--udp", type=int, default=54321, help="UDP port")
    args = parser.parse_args()
    main_loop(args.tcp, args.udp)
