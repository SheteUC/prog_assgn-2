import socket
import threading
import sys

# Client Configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 12345

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(4096).decode()
            if data:
                print(data)
            else:
                break
        except:
            break

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_HOST, SERVER_PORT))
    except:
        print("Unable to connect to the server.")
        sys.exit()

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    while True:
        message = input()
        if message.strip() == '':
            continue
        sock.sendall(message.encode())
        if message.strip() == '%exit':
            print("Exiting.")
            break

if __name__ == '__main__':
    main()
