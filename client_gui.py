import tkinter as tk
import socket
def send_command():
    command = command_entry.get() 
    if command:
        display_message(f"Sending command: {command}")
        try:
            client_socket.sendall(command.encode())
            response = client_socket.recv(1024).decode()
            display_message(f"Server response: {response}")
        except Exception as e:
            display_message(f"Error: {e}")
def display_message(message):
    response_text.config(state=tk.NORMAL)  
    response_text.insert(tk.END, message + '\n')  
    response_text.config(state=tk.DISABLED)  
def connect_to_server():
    try:
        client_socket.connect(('localhost', 12345))
        display_message("Connected to the server.")
    except Exception as e:
        display_message(f"Connection error: {e}")
root = tk.Tk()
root.title("Bulletin Board Client")
response_text = tk.Text(root, height=15, width=50, wrap=tk.WORD) #lil simple box or sm
response_text.grid(row=0, column=0, padx=10, pady=10)
response_text.config(state=tk.DISABLED) 
command_entry = tk.Entry(root, width=50)
command_entry.grid(row=1, column=0, padx=10, pady=10)
send_button = tk.Button(root, text="Send Command", command=send_command)
send_button.grid(row=2, column=0, padx=10, pady=10)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect_to_server()
root.mainloop()
