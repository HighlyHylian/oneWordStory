# client.py
import socket
import threading

SERVER_IP = input("Enter server IP: ").strip()
PORT = int(input("Enter port: ").strip())

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((SERVER_IP, PORT))
except Exception as e:
    print("Connection failed:", e)
    exit()


def receive():
    while True:
        try:
            message = client.recv(4096).decode()
            if not message:
                break

            # Print each server message as a new block
            print("\n" + message.strip())

        except:
            break


threading.Thread(target=receive, daemon=True).start()

while True:
    word = input("> ").strip()
    client.sendall(word.encode())