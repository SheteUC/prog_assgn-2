import socket
import threading
import json
from datetime import datetime

# Server Configuration
HOST = '0.0.0.0'
PORT = 12345

# Global Data Structures
clients = {}
groups = {f"Group{i}": {'members': {}, 'messages': []} for i in range(1, 6)}
public_messages = []

# Lock for thread safety
lock = threading.Lock()

# Add this constant at the top with other globals
GROUP_ACCESS_ERROR = "You are not a member of this group or group does not exist.\n"

def broadcast(message, exclude_client=None):
    with lock:
        for client in clients.values():
            if client != exclude_client:
                try:
                    client.sendall(message.encode())
                except (ConnectionError, socket.error) as e:
                    print(f"Connection error: {e}")

def handle_client(conn, addr):
    conn.sendall("Enter a unique username: ".encode())
    username = conn.recv(1024).decode().strip()
    with lock:
        clients[username] = conn
    conn.sendall(f"Welcome {username}!\n".encode())
    broadcast(f"{username} has joined the public board.\n", exclude_client=conn)

    # Send last two messages
    if public_messages:
        last_messages = public_messages[-2:]
        conn.sendall("Last two messages:\n".encode())
        for msg in last_messages:
            conn.sendall(f"{msg['id']}, {msg['sender']}, {msg['date']}, {msg['subject']}\n".encode())

    conn.sendall("Current users:\n".encode())
    for user in clients.keys():
        conn.sendall(f"- {user}\n".encode())

    try:
        while True:
            data = conn.recv(4096).decode()
            if not data:
                break
            response = process_command(data, username, conn)
            if response:
                conn.sendall(response.encode())
    except (ConnectionError, socket.error) as e:
        print(f"Connection error: {e}")
    finally:
        with lock:
            del clients[username]
        broadcast(f"{username} has left the public board.\n", exclude_client=conn)
        conn.close()

def process_command(data, username, conn):
    args = data.strip().split()
    if not args:
        return "Invalid command.\n"
        
    command_handlers = {
        '%post': handle_post,
        '%message': handle_message,
        '%users': handle_users,
        '%exit': handle_exit,
        '%groups': handle_groups,
        '%groupjoin': handle_group_join,
        '%grouppost': handle_group_post,
        '%groupmessage': handle_group_message,
        '%groupusers': handle_group_users,
        '%groupleave': handle_group_leave
    }
    
    command = args[0]
    handler = command_handlers.get(command)
    if not handler:
        return "Unknown command.\n"
    
    return handler(args, username, conn)

def handle_post(args, username, conn):
    subject = args[1]
    content = ' '.join(args[2:])
    message = {
        'id': len(public_messages) + 1,
        'sender': username,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'subject': subject,
        'content': content
    }
    with lock:
        public_messages.append(message)
    broadcast(f"New message posted by {username}: {subject}\n", exclude_client=None)
    return "Message posted.\n"

def handle_message(args, username, conn):
    msg_id = int(args[1]) - 1
    with lock:
        if 0 <= msg_id < len(public_messages):
            msg = public_messages[msg_id]
            return f"Message ID: {msg['id']}\nSender: {msg['sender']}\nDate: {msg['date']}\nSubject: {msg['subject']}\nContent: {msg['content']}\n"
        else:
            return "Message not found.\n"

def handle_users(args, username, conn):
    response = "Current users:\n"
    with lock:
        for user in clients.keys():
            response += f"- {user}\n"
    return response

def handle_exit(args, username, conn):
    conn.close()

def handle_groups(args, username, conn):
    response = "Available groups:\n"
    with lock:
        for idx, group in enumerate(groups.keys(), 1):
            response += f"{idx}. {group}\n"
    return response

def handle_group_join(args, username, conn):
    group_name = args[1]
    with lock:
        if group_name in groups:
            groups[group_name]['members'][username] = conn
            return f"Joined {group_name}.\n"
        else:
            return "Group not found.\n"

def handle_group_post(args, username, conn):
    group_name = args[1]
    subject = args[2]
    content = ' '.join(args[3:])
    with lock:
        if group_name in groups and username in groups[group_name]['members']:
            message = {
                'id': len(groups[group_name]['messages']) + 1,
                'sender': username,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'subject': subject,
                'content': content
            }
            groups[group_name]['messages'].append(message)
            # Notify group members
            for member_conn in groups[group_name]['members'].values():
                if member_conn != conn:
                    member_conn.sendall(f"New message in {group_name} by {username}: {subject}\n".encode())
            return "Group message posted.\n"
        else:
            return GROUP_ACCESS_ERROR

def handle_group_message(args, username, conn):
    group_name = args[1]
    msg_id = int(args[2]) - 1
    with lock:
        if group_name in groups and username in groups[group_name]['members']:
            if 0 <= msg_id < len(groups[group_name]['messages']):
                msg = groups[group_name]['messages'][msg_id]
                return f"Group: {group_name}\nMessage ID: {msg['id']}\nSender: {msg['sender']}\nDate: {msg['date']}\nSubject: {msg['subject']}\nContent: {msg['content']}\n"
            else:
                return "Message not found in group.\n"
        else:
            return GROUP_ACCESS_ERROR

def handle_group_users(args, username, conn):
    group_name = args[1]
    with lock:
        if group_name in groups and username in groups[group_name]['members']:
            response = f"Users in {group_name}:\n"
            for user in groups[group_name]['members'].keys():
                response += f"- {user}\n"
            return response
        else:
            return GROUP_ACCESS_ERROR

def handle_group_leave(args, username, conn):
    group_name = args[1]
    with lock:
        if group_name in groups and username in groups[group_name]['members']:
            del groups[group_name]['members'][username]
            return f"Left {group_name}.\n"
        else:
            return GROUP_ACCESS_ERROR

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server started on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    start_server()
