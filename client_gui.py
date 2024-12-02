import tkinter as tk
from tkinter import messagebox
import socket
import threading

SERVER_HOST = "127.0.0.1"  # Replace with the actual server IP
SERVER_PORT = 12345        # Replace with the actual server port
BUFFER_SIZE = 4096

class ClientGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bulletin Board Client")
        self.root.geometry("500x600")
        self.root.configure(bg="#f0f0f0")

        # Fonts and Colors
        self.font = ("Helvetica", 12)
        self.bg_color = "#f0f0f0"
        self.text_color = "#333333"
        self.button_color = "#4CAF50"
        self.button_text_color = "#ffffff"

        # Menu Bar (Optional)
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.close_connection)

        # Chat Area Frame
        chat_frame = tk.Frame(self.root, bg=self.bg_color)
        chat_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Chat Area with Scrollbar
        self.chat_area = tk.Text(chat_frame, state='disabled', wrap='word', font=self.font, bg="#ffffff", fg=self.text_color)
        self.chat_area.pack(side='left', fill='both', expand=True)

        scrollbar = tk.Scrollbar(chat_frame, command=self.chat_area.yview)
        scrollbar.pack(side='right', fill='y')
        self.chat_area['yscrollcommand'] = scrollbar.set

        # Input Area Frame
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill='x', padx=10, pady=5)

        self.input_field = tk.Entry(input_frame, width=40, font=self.font)
        self.input_field.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.input_field.bind("<Return>", self.send_message)

        self.send_button = tk.Button(input_frame, text="Send", command=self.send_message,
                                     bg=self.button_color, fg=self.button_text_color, font=self.font)
        self.send_button.pack(side='left')

        # Status Bar Frame
        status_frame = tk.Frame(self.root, bg=self.bg_color)
        status_frame.pack(fill='x', padx=10, pady=5)

        self.exit_button = tk.Button(status_frame, text="Exit", command=self.close_connection,
                                     bg="#f44336", fg=self.button_text_color, font=self.font)
        self.exit_button.pack(side='right')

        # Client Socket
        self.client_socket = None
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
            self.prompt_username()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the server:\n{e}")
            self.running = False
            self.root.destroy()

    def prompt_username(self):
        """Prompt the user to enter a username."""
        self.username_window = tk.Toplevel(self.root)
        self.username_window.title("Enter Username")
        self.username_window.geometry("300x100")
        self.username_window.resizable(False, False)

        tk.Label(self.username_window, text="Enter a unique username:", font=self.font).pack(pady=10)
        self.username_entry = tk.Entry(self.username_window, font=self.font)
        self.username_entry.pack()
        self.username_entry.bind("<Return>", self.submit_username)

        submit_button = tk.Button(self.username_window, text="Join", command=self.submit_username,
                                  bg=self.button_color, fg=self.button_text_color, font=self.font)
        submit_button.pack(pady=5)

    def submit_username(self, event=None):
        """Send the username to the server."""
        username = self.username_entry.get().strip()
        if username:
            join_command = f"%join {username}"
            try:
                self.client_socket.sendall(join_command.encode())
                self.username_window.destroy()
            except Exception as e:
                self.update_chat(f"Error: {e}")
                self.username_window.destroy()
        else:
            messagebox.showwarning("Invalid Username", "Username cannot be empty.")

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
            messagebox.showwarning("Empty Message", "Cannot send an empty message.")

    def receive_messages(self):
        """Receive messages from the server."""
        while self.running:
            try:
                message = self.client_socket.recv(BUFFER_SIZE).decode()
                if message:
                    self.update_chat(message)
                else:
                    self.update_chat("Server disconnected.")
                    self.running = False
            except Exception as e:
                if self.running:
                    self.update_chat(f"Error receiving message: {e}")
                break

    def close_connection(self):
        """Close the connection and exit the application."""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.sendall("%exit".encode())
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
