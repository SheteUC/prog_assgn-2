import socket
import threading
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

GROUP_ACCESS_ERROR = "You are not a member of this group or the group does not exist.\n"

def broadcast(message, exclude_client=None):
    with lock:
        for client in clients.values():
            if client != exclude_client:
                try:
                    client.sendall(message.encode())
                except (ConnectionError, socket.error) as e:
                    print(f"Connection error during broadcast: {e}")

def format_message(msg):
    return (f"Message ID: {msg['id']}\n"
            f"Sender: {msg['sender']}\n"
            f"Date: {msg['date']}\n"
            f"Subject: {msg['subject']}\n"
            f"Content: {msg['content']}\n")

def handle_client(conn, addr):
    try:
        # Handle username
        while True:
            conn.sendall(USERNAME_PROMPT.encode())
            username = conn.recv(1024).decode().strip()
            with lock:
                if username in clients:
                    conn.sendall("Username already taken. Enter a different username.\n".encode())
                elif username == '':
                    conn.sendall("Username cannot be empty. Enter a different username.\n".encode())
                else:
                    clients[username] = conn
                    break

        conn.sendall(f"Welcome {username}! Type '%help' for a list of commands.\n".encode())
        broadcast(f"{username} has joined the public board.\n", exclude_client=conn)

        # Send last two messages
        with lock:
            if public_messages:
                last_messages = public_messages[-2:]
                conn.sendall("Last two messages on the public board:\n".encode())
                for msg in last_messages:
                    conn.sendall(format_message(msg).encode())
            else:
                conn.sendall("No messages on the public board yet.\n".encode())

            # Send list of current users
            conn.sendall("Current users on the public board:\n".encode())
            for user in clients.keys():
                conn.sendall(f"- {user}\n".encode())

        current_location = 'Public Board'

        while True:
            conn.sendall(f"\n[{current_location}]> ".encode())
            data = conn.recv(4096).decode()
            if not data:
                break
            response = process_command(data, username, conn)
            if response == "EXIT":
                break
            elif response:
                conn.sendall(response.encode())
    except (ConnectionError, socket.error) as e:
        print(f"Connection error with {addr}: {e}")
    finally:
        with lock:
            if username in clients:
                del clients[username]
            # Remove user from any groups they're part of
            for group in groups.values():
                group['members'].pop(username, None)
        broadcast(f"{username} has left the public board.\n", exclude_client=conn)
        conn.close()

def process_command(data, username, conn):
    args = data.strip().split()
    if not args:
        return "No command provided. Type '%help' for a list of commands.\n"
    command_handlers = {
        '%help': handle_help,
        '%post': handle_post,
        '%message': handle_message,
        '%users': handle_users,
        '%groups': handle_groups,
        '%groupjoin': handle_group_join,
        '%grouppost': handle_group_post,
        '%groupmessage': handle_group_message,
        '%groupusers': handle_group_users,
        '%groupleave': handle_group_leave,
        '%exit': handle_exit,
        '%join': handle_join
    }

    handler = command_handlers.get(args[0])
    if handler is None:
        return "Unknown command. Type '%help' for a list of commands.\n"

    try:
        return handler(args, username, conn)
    except Exception as e:
        print(f"Error processing command from {username}: {e}")
        return f"Error processing command: {e}\n"

#handles %help (works)
def handle_help(args, username, conn):
    help_text = """
Available Commands:
- %help: Show this help message.
- %post [subject] [content]: Post a message to the public board.
- %message [message_id]: Retrieve a message from the public board.
- %users: List users on the public board.
- %groups: List available groups.
- %groupjoin [group_name]: Join a private group.
- %grouppost [group_name] [subject] [content]: Post a message to a group.
- %groupmessage [group_name] [message_id]: Retrieve a message from a group.
- %groupusers [group_name]: List users in a group.
- %groupleave [group_name]: Leave a group.
- %exit: Exit the application.
"""
    return help_text

#handles %post (looks like it works)
def handle_post(args, username, conn):
    if len(args) < 3:
        return "Usage: %post [subject] [content]\n"
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
    broadcast(f"New public message posted by {username}: {subject}\n", exclude_client=None)
    return "Message posted to the public board.\n"

#handles %message
def handle_message(args, username, conn):
    if len(args) != 2:
        return "Usage: %message [message_id]\n"
    try:
        msg_id = int(args[1]) - 1
    except ValueError:
        return "Message ID must be a number.\n"
    with lock:
        if 0 <= msg_id < len(public_messages):
            msg = public_messages[msg_id]
            return format_message(msg)
        else:
            return "Message not found on the public board.\n"

#handles %users (works)
def handle_users(args, username, conn):
    response = "Current users on the public board:\n"
    with lock:
        for user in clients.keys():
            response += f"- {user}\n"
    return response

#handles %groups (works)
def handle_groups(args, username, conn):
    response = "Available groups:\n"
    with lock:
        for idx, group in enumerate(groups.keys(), 1):
            response += f"{idx}. {group}\n"
    return response

#handles %groupjoin (works)
def handle_group_join(args, username, conn):
    if len(args) != 2:
        return "Usage: %groupjoin [group_name]\n"
    group_name = args[1]
    with lock:
        if group_name in groups:
            groups[group_name]['members'][username] = conn
            return f"Joined {group_name}. You are now in Group: {group_name}\n"
        else:
            return "Group not found.\n"

#handles %grouppost (works)
def handle_group_post(args, username, conn):
    if len(args) < 4:
        return "Usage: %grouppost [group_name] [subject] [content]\n"
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
            for member_name, member_conn in groups[group_name]['members'].items():
                if member_conn != conn:
                    try:
                        member_conn.sendall(f"New message in {group_name} by {username}: {subject}\n".encode())
                    except (ConnectionError, socket.error) as e:
                        print(f"Connection error during group broadcast: {e}")
            return f"Message posted to {group_name}.\n"
        else:
            return GROUP_ACCESS_ERROR

#handles %groupmessage (works)
def handle_group_message(args, username, conn):
    if len(args) != 3:
        return "Usage: %groupmessage [group_name] [message_id]\n"
    group_name = args[1]
    try:
        msg_id = int(args[2]) - 1
    except ValueError:
        return "Message ID must be a number.\n"
    with lock:
        if group_name in groups and username in groups[group_name]['members']:
            if 0 <= msg_id < len(groups[group_name]['messages']):
                msg = groups[group_name]['messages'][msg_id]
                return format_message(msg)
            else:
                return "Message not found in the group.\n"
        else:
            return GROUP_ACCESS_ERROR

#handles %groupusers (works)
def handle_group_users(args, username, conn):
    if len(args) != 2:
        return "Usage: %groupusers [group_name]\n"
    group_name = args[1]
    with lock:
        if group_name in groups and username in groups[group_name]['members']:
            response = f"Users in {group_name}:\n"
            for user in groups[group_name]['members'].keys():
                response += f"- {user}\n"
            return response
        else:
            return GROUP_ACCESS_ERROR
 
#handles %groupleave (sorta works)
def handle_group_leave(args, username, conn):
    if len(args) != 2:
        return "Usage: %groupleave [group_name]\n"
    group_name = args[1]
    with lock:
        if group_name in groups and username in groups[group_name]['members']:
            del groups[group_name]['members'][username]
            return f"Left {group_name}. You are now back on the Public Board.\n"
        else:
            return GROUP_ACCESS_ERROR

#handles %join (this does not work yet)
def handle_join(args, username, conn):
    with lock:
        if username in clients:
            return f'{username} is already in public board'
        
        clients[username] = conn
        broadcast(f'{username} has joined the public board: ', exclude_client=conn)
        
        # Send the last two public messages to the new user
        response = "Last two messages on the public board:\n"
        if public_messages:
            last_messages = public_messages[-2:]
            for msg in last_messages:
                response += format_message(msg)
        else:
            response += "No messages on the public board yet.\n"
        
        # Send the list of current users
        response += "Current users on the public board:\n"
        for user in clients.keys():
            response += f"- {user}\n"
        
    return response

def handle_exit(args, username, conn):
    return "EXIT"

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
