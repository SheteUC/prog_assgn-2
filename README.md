# Simple Bulletin Board Using Socket Programming

## How to Run

### Server

1. Open a terminal.
2. Navigate to the directory containing `server.py`.
3. Run the server:

   ```bash
   python3 server.py
   ```

4. In another terminal:
   1. Run the `client.py` if wanting to run on terminal:

      ```bash
      python3 client.py
      ```

   2. Run the `client_gui.py` if wanting to use the GUI:

      ```bash
      python client_gui.py
      ```

## Available Commands

- **%help**: Show this help message.
- **%join [username]**: Join the public board with a unique username.
- **%post [message]**: Post a message to the public board.
- **%message [message_id]**: Retrieve a message from the public board.
- **%users**: List users on the public board.
- **%groups**: List available groups.
- **%groupjoin [group_name]**: Join a private group.
- **%grouppost [group_name] [message]**: Post a message to a group.
- **%groupmessage [group_name] [message_id]**: Retrieve a message from a group.
- **%groupusers [group_name]**: List users in a group.
- **%groupleave [group_name]**: Leave a group.
- **%exit**: Exit the application.
```