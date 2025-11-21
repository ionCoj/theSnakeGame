""" import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever() """
import socket
import threading

PORT = 8000
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"
HEADER = 64
print(f"Server started at {SERVER}:{PORT}")
filesToSend = ['signup.html', 'styles.css', 'script.js', 'index.html', 'index.css']

myServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
myServer.bind(ADDRESS)
myServer.listen()

for file_name in filesToSend:
    with open(file_name, 'rb') as file:
        signup_page = file.read()
        while True:
            communication_socket, client_address = myServer.accept()
            with communication_socket:
                print(f"Connection established with {client_address}")
                request = communication_socket.recv(1024)
                communication_socket.send('HTTP/1.1 200 OK\nContent-Type: text/html\n\n'.encode())
                communication_socket.sendall(signup_page)

#def handle_client(communication_socket, client_address):





""" thread = threading.Thread(target=handle_client, args=(communication_socket, client_address))
    thread.start() """
    