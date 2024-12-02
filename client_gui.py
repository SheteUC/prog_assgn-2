import tkinter as tk
from tkinter import messagebox
import socket
import threading

SERVER_HOST = "127.0.0.1"  # Replace with the actual server IP
SERVER_PORT = 12345  # Replace with the actual server port
BUFFER_SIZE = 1024

class ClientGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bulletin Board Client")
        self.chat_area = tk.Text(self.root, height=20, width=50, state='disabled', wrap='word') #this will be the chat area
        self.chat_area.pack(pady=10)

        self.input_field = tk.Entry(self.root, width=40) #size of input field
        self.input_field.pack(pady=5)
        self.input_field.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message) #send button
        self.send_button.pack()

        self.exit_button = tk.Button(self.root, text="Exit", command=self.close_connection) #exit button
        self.exit_button.pack(pady=5)

        self.client_socket = None #here initialising client socket
        self.running = True

        self.setup_connection()
        self.listen_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.listen_thread.start()

    def setup_connection(self):
        """Set up the connection to the server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_HOST, SERVER_PORT))
            self.update_chat("Connected to the server.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the server:\n{e}")
            self.running = False

    def update_chat(self, message):
        """Update the chat area with a new message."""
        self.chat_area.config(state='normal')
        self.chat_area.insert('end', message + '\n')
        self.chat_area.config(state='disabled')
        self.chat_area.see('end')

    def send_message(self, event=None):
        """Send a message to the server."""
        message = self.input_field.get().strip()
        if message:
            try:
                self.client_socket.sendall(message.encode())
                self.update_chat(f"You: {message}")
                self.input_field.delete(0, 'end')
            except Exception as e:
                self.update_chat(f"Error: {e}")
        else:
            self.update_chat("Cannot send an empty message.")

    def receive_messages(self):
        """Receive messages from the server."""
        while self.running:
            try:
                message = self.client_socket.recv(BUFFER_SIZE).decode()
                if message:
                    self.update_chat(f"Server: {message}")
                else:
                    self.update_chat("Server disconnected.")
                    self.running = False
            except Exception as e:
                self.update_chat(f"Error receiving message: {e}")
                break

    def close_connection(self):
        """Close the connection and exit the application."""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception:
                pass
        self.root.quit()

    def run(self):
        """Run the Tkinter main loop."""
        self.root.protocol("WM_DELETE_WINDOW", self.close_connection)
        self.root.mainloop()


if __name__ == "__main__":
    client = ClientGUI()
    client.run()
