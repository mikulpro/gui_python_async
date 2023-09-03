# gui_control.py
import socket

def start_server():
    HOST = 'localhost'
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        print('Listening for incoming connections...')
        
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                
                command = data.decode('utf-8')
                print(f"Received command: {command}")
                
                # Process command and prepare a response
                response = "Command received"
                
                conn.sendall(response.encode('utf-8'))

if __name__ == "__main__":
    start_server()
