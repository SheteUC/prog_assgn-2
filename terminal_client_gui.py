import tkinter as tk
from tkinter import messagebox
import socket
import threading

#this will give it a green-black terminal look
retro_font = ("Courier", 12, "bold")
bg_color = "#000000"  #black bbg
fg_color = "#00FF00"  #green text
button_color = "#444444"  #dark grey buttons
button_fg = "#000000"  #black button text

client_socket = None

#connect to the server and then check the username
def connect_to_server(username):
    try:
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 12345))  #update with your server IP/Port
        client_socket.sendall(username.encode('utf-8'))
        
        #waiting for server response
        response = client_socket.recv(1024).decode('utf-8')
        if "Username already taken" in response:
            client_socket.close()
            messagebox.showerror("Username Error", "Username already taken. Please try a different username.")
            return False
        
        #if successful connection
        threading.Thread(target=listen_for_messages, daemon=True).start()
        append_text(response)  #displaying a welcome text
        username_input_frame.pack_forget()  
        chat_frame.pack(fill=tk.BOTH, expand=True)  #show chat interface
        message_input.focus() 
        return True
    except Exception as e:
        messagebox.showerror("Connection Error", str(e))
        return False

#to send a msg
def send_message():
    message = message_input.get()
    if message.strip():
        client_socket.sendall(message.encode('utf-8'))
        message_input.delete(0, tk.END)
    else:
        append_text("Cannot send an empty message.")

#to listen for incoming msgs
def listen_for_messages():
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                append_text(message)
            else:
                break
    except Exception as e:
        append_text("Disconnected from server.")
    finally:
        client_socket.close()

def append_text(message):
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, message + "\n")
    chat_log.config(state=tk.DISABLED)
    chat_log.see(tk.END)

#disconnecting from the server
def disconnect():
    try:
        if client_socket:
            client_socket.close()
    except:
        pass
    root.destroy()

#main tkinter gui box
root = tk.Tk()
root.title("Client Terminal")
root.geometry("600x600")
root.config(bg=bg_color)

#input frame for the username
username_input_frame = tk.Frame(root, bg=bg_color)

username_label = tk.Label(username_input_frame, text="Enter Username:", font=retro_font, bg=bg_color, fg=fg_color)
username_label.pack(pady=10)

username_entry = tk.Entry(username_input_frame, font=retro_font, bg=button_color, fg=fg_color)
username_entry.pack(pady=5)
username_entry.focus()

def on_connect():
    username = username_entry.get().strip()
    if username:
        if connect_to_server(username):
            append_text(f"Connected as {username}.")
    else:
        messagebox.showwarning("Input Error", "Please enter a username.")

connect_button = tk.Button(username_input_frame, text="Connect", font=retro_font, bg=button_color, fg=button_fg, command=on_connect)
connect_button.pack(pady=10)

username_input_frame.pack(fill=tk.BOTH, expand=True)

#frame for the terminal chat
chat_frame = tk.Frame(root, bg=bg_color)

chat_log = tk.Text(chat_frame, font=retro_font, bg=bg_color, fg=fg_color, state=tk.DISABLED, wrap=tk.WORD)
chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

message_input = tk.Entry(chat_frame, font=retro_font, bg=button_color, fg=fg_color)
message_input.pack(padx=10, pady=5, fill=tk.X)
message_input.bind("<Return>", lambda event: send_message())  # Press Enter to send a message

send_button = tk.Button(chat_frame, text="Send", font=retro_font, bg=button_color, fg=button_fg, command=send_message)
send_button.pack(pady=5)

exit_button = tk.Button(chat_frame, text="Exit", font=retro_font, bg=button_color, fg=button_fg, command=disconnect)
exit_button.pack(pady=5)

root.protocol("WM_DELETE_WINDOW", disconnect)
root.mainloop()
