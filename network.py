from socket import AF_INET, socket, SOCK_STREAM

 # soket ile ilgili işlemleri yapacak sınıf
class NetworkClient:

    def __init__(self):
        self.client_socket = None
        self.buffer_size = 1024

    def connect(self, host, port):
        self.client_socket = socket(AF_INET, SOCK_STREAM) # soket oluşturma
        self.client_socket.connect((host, port)) # server'a bağlanma

    def send_message(self, message):
        self.client_socket.send(bytes(message, "utf-8")) # mesajı server'a gönder

    def receive_message(self):
        return self.client_socket.recv(self.buffer_size).decode("utf-8") # server'dan gelen mesajı al ve decode et

    def close_connection(self):
        if self.client_socket:
            self.client_socket.close() # soketi kapat    


