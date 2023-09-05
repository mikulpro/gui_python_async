# communication with bot
import socket

def send_command(command):
    HOST = 'localhost'
    PORT = 65432
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(command.encode('utf-8'))
            
            data = s.recv(1024)
            return data.decode('utf-8')
        #print(f"Received response: {data.decode('utf-8')}")
    except:
        return "fail"
    
# When you want to send a command from your GUI
if __name__ == "__main__":
    send_command("Load cogs.basiccog")
