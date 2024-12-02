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
    '%exit',
    '%join',
}

sock = None

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(4096).decode()
            if data:
                print(data, end='')  # Avoid adding extra newlines
            else:
                print("Server closed the connection.")
                sock.close()
                break
        except Exception as e:
            print(f"Error receiving data: {e}")
            sock.close()
            break

def main():
    global sock
    while True:
        message = input()
        if message.strip() == '':
            continue
        args = message.strip().split()
        command = args[0]

        if command not in commands_list and command not in server_commands_list:
            print(f'{command} is not recognized as an internal command')
            continue

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
            continue  # Proceed to next input

        if sock is None:
            print("You need to connect first using %connect")
            continue

        if command == "%join":
            if len(args) != 2:
                print("Usage: %join [username]")
                continue
            try:
                sock.sendall(message.encode())
            except Exception as e:
                print(f"Error sending data: {e}")
                sock.close()
                break
            continue

        if command in server_commands_list:
            try:
                sock.sendall(message.encode())
                if command == '%exit':
                    print("Exiting.")
                    sock.close()
                    break
            except Exception as e:
                print(f"Error sending data: {e}")
                sock.close()
                break
        else:
            print(f"{command} is not a valid command.")

if __name__ == '__main__':
    main()
