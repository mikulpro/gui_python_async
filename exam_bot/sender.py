# gui_control.py
import socket

def send_command(command):
    HOST = 'localhost'
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(command.encode('utf-8'))
        
        data = s.recv(1024)
        
    print(f"Received response: {data.decode('utf-8')}")

# When you want to send a command from your GUI
if __name__ == "__main__":
    send_command("Load cogs.basiccog")
