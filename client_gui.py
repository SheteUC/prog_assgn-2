import tkinter as tk
from tkinter import scrolledtext
import socket
import threading


class ClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Bulletin Board Client")
        self.master.geometry("600x400")

        # Username and connection setup
        self.username = None
        self.client_socket = None
        self.server_address = ("127.0.0.1", 12345)

        # GUI Layout
        self.chat_display = scrolledtext.ScrolledText(self.master, state="disabled", wrap="word", height=20, width=70)
        self.chat_display.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.input_field = tk.Entry(self.master, width=55)
        self.input_field.grid(row=1, column=0, padx=10, pady=10)
        self.input_field.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.master, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        # Prompt user for username at the start
        self.prompt_username()

    def prompt_username(self):
        """Prompt the user to enter a username."""
        self.username_window = tk.Toplevel(self.master)
        self.username_window.title("Set Username")
        self.username_window.geometry("300x100")
        self.username_window.resizable(False, False)

        tk.Label(self.username_window, text="Enter Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.username_window)
        self.username_entry.pack(pady=5)
        self.username_entry.bind("<Return>", self.set_username)

        tk.Button(self.username_window, text="Submit", command=self.set_username).pack(pady=5)

    def set_username(self, event=None):
        """Set the username entered by the user."""
        username = self.username_entry.get().strip()
        if username:
            self.username = username
            self.username_window.destroy()
            self.connect_to_server()
        else:
            self.update_chat("Username cannot be empty!")

    def connect_to_server(self):
        """Connect to the server and send the initial username."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(self.server_address)
            self.client_socket.sendall(self.username.encode())
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.update_chat(f"Connected to the server as {self.username}.")
        except Exception as e:
            self.update_chat(f"Error connecting to the server: {e}")

    def send_message(self, event=None):
        """Send a message to the server."""
        if not self.username:
            self.update_chat("Please set a username before sending messages.")
            return

        message = self.input_field.get().strip()
        if message.startswith("%join"):
            # Special handling for %join command
            parts = message.split()
            if len(parts) == 2 and parts[1] == self.username:
                self.update_chat("You are already part of the public board.")
                return
            elif len(parts) == 1:
                self.update_chat("Usage: %join [username]")
                return

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
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    self.update_chat(message)
            except Exception as e:
                self.update_chat(f"Error receiving message: {e}")
                break

    def update_chat(self, message):
        """Update the chat display with a new message."""
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", message + "\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")


if __name__ == "__main__":
    root = tk.Tk()
    gui = ClientGUI(root)
    root.mainloop()
