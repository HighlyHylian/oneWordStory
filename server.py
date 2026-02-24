# server.py
import socket
import threading

HOST = "0.0.0.0"
PORT = 5000

clients = {}           # conn -> username
turn_order = []        # list of usernames in order
current_turn = 0
story = []
lock = threading.Lock()


def broadcast(message):
    # Send a message to all connected clients.
    for conn in list(clients.keys()):
        try:
            conn.sendall((message + "\n").encode())
        except:
            pass


def broadcast_story():
    # Send the story with separators to all clients.
    broadcast("\n--- STORY UPDATE ---")
    broadcast(" ".join(story) if story else "[Empty Story]")
    broadcast("--------------------")


def send_turn_info():
    if turn_order:
        current_player = turn_order[current_turn]
        broadcast(f"Current Turn: {current_player}")


def handle_client(conn, addr):
    global current_turn, story

    try:
        conn.sendall(b"Enter username: ")
        username = conn.recv(1024).decode().strip()

        with lock:
            clients[conn] = username
            turn_order.append(username)
            broadcast(f"{username} joined the game.")
            broadcast_story()
            send_turn_info()

        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                break

            command = data.upper()

            with lock:
                if username != turn_order[current_turn]:
                    conn.sendall(b"Not your turn.\n")
                    continue

                if command == "DELETE":
                    if story:
                        story.pop()
                        
                    broadcast_story()

                    # Rotate turn
                    current_turn = (current_turn + 1) % len(turn_order)
                    send_turn_info()

                    continue

                elif command == "RESET":
                    story = []
                    broadcast("\n[Story Reset]")
                    send_turn_info()
                    continue

                else:
                    if " " in data:
                        conn.sendall(b"One word only.\n")
                        continue

                    story.append(data)
                    broadcast_story()

                    # Rotate turn
                    current_turn = (current_turn + 1) % len(turn_order)
                    send_turn_info()

    except:
        pass

    with lock:
        username = clients.get(conn)
        if username:
            turn_order.remove(username)
            del clients[conn]
            broadcast(f"{username} left the game.")
            broadcast_story()
            if turn_order:
                current_turn %= len(turn_order)
                send_turn_info()

    conn.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Server started on port {PORT}...")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()