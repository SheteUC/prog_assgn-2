import socket
import threading
import sys

# Client Configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 12345

commands_list = {
    "%connect",
}

server_commands_list = {
        '%help',
        '%post',
        '%message',
        '%users',
        '%groups',
        '%groupjoin',
        '%grouppost',
        '%groupmessage',
        '%groupusers',
        '%groupleave',       
        '%exit'
        "%join",
        "%post", #used inconjuction with [subject][message] to actually post
        "%users",
        "%message",
        "%leave",
}

sock = None

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
    global sock
    while True:
        message = input()
        args = message.strip().split()
        command = args[0]

        if message.strip() == '':
            continue

        if command not in commands_list and command not in server_commands_list:
            return f'{command} is not recognized as an interal command'
        
        if command == "%connect":
            if len(args) != 3:
                print("Usage: %connect [address] [port]")
                continue

            address = args[1]
            try:
                port = int(args[2])
            except ValueError:
                print("Invalid port number.")
                continue

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((address, port))
                print(f"Connected to {address}:{port}")
                threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
            except Exception as e:
                print(f"Unable to connect to the server: {e}")
                sys.exit()

        if command in server_commands_list:
            sock.sendall(message.encode())

        sock.sendall(message.encode())
        if message.strip() == '%exit':
            print("Exiting.")
            break

if __name__ == '__main__':
    main()
