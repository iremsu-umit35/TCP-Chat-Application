from socket import AF_INET, socket, SOCK_STREAM

 # soket ile ilgili işlemleri yapacak sınıf
class NetworkClient:

    def __init__(self):
        self.client_socket = None
        self.buffer_size = 10
        self.header_size = 10

    def connect(self, host, port):
        self.client_socket = socket(AF_INET, SOCK_STREAM) # soket oluşturma
        self.client_socket.connect((host, port)) # server'a bağlanma

    def send_message(self, message):
        #mesajı byte dizisine çevir ve server'a gönder
        message_bytes = message.encode("utf-8")

        #mesajon kaç byte olduğunu belirle
        message_length = len(message_bytes)

        #mesajın uzunluğunu server'a gönder
        header = str(message_length).zfill(self.header_size)

        # headerı bytea çevir
        header_bytes = header.encode("utf-8")

        #önce headerı gönder, sonra mesajı gönder
        self.client_socket.sendall(header_bytes + message_bytes)
        #sendall ile tüm mesajı gönderiyoruz, çünkü send() ile gönderilen mesajın tamamı gitmeyebilir

    def receive_message(self):

        # Önce sabit boyutlu header'ı oku
        header_bytes = self.receive_exactly(
            self.header_size
        )

        # Bağlantı kapandıysa
        if header_bytes is None:
            return None

        # Header byte'larını string'e çevir
        header = header_bytes.decode("utf-8")

        # Header içindeki mesaj uzunluğunu integer'a çevir
        message_length = int(header)

        # Mesaj gövdesini tam belirtilen uzunlukta oku
        message_bytes = self.receive_exactly(
            message_length
        )

        # Bağlantı mesaj okunurken kapanmış olabilir
        if message_bytes is None:
            return None

        # Byte dizisini tekrar Python string'ine çevir
        return message_bytes.decode("utf-8")

    def close(self):
        if self.client_socket:
            try:
                self.client_socket.shutdown(2)
            except OSError:
                pass

            self.client_socket.close()
            self.client_socket = None

    def receive_exactly(self, byte_count):

        # Toplanan veriyi burada tutacağız
        data = b""

        # İstenen byte sayısına ulaşana kadar okumaya devam et
        while len(data) < byte_count:

            # Eksik kalan byte sayısını hesapla
            remaining = byte_count - len(data)

            # Sadece eksik kalan kadar veri istemeye çalış
            chunk = self.client_socket.recv(remaining)

            # recv boş veri döndürürse bağlantı kapanmıştır
            if not chunk:
                return None

            # Gelen parçayı mevcut veriye ekle
            data += chunk

        return data

