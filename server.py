from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread # birden fazla istemciyi aynı anda dinleyebilmek için

clients = {}# istemcilerin soketlerini tutmak için bir liste
addresses = {} # istemcilerin adreslerini tutmak için bir liste

# client taraıfnda hangi server ile yapılabir tarzı imput oluşturabililir gelişme amaçlı 
# kullanıc girişi veri tabanı send ile gönderilecek server alacak kullanıcı listesi oluşturulacak ve kullanıcılar listesi ile karşılaştırılacak
#gelen mesaj şu ise aç kullanıcadı varmı konrol et vs vs 
HEADER_SIZE = 10
HOST = '192.168.1.159' #localhost, ıp adresi
PORT = 19751 # port numarası 0–65535 arası olabilir



ADDR = (HOST, PORT) # adres tuple'ı
SERVER = socket(AF_INET, SOCK_STREAM) # soket oluşturma
SERVER.bind(ADDR) # soketi adrese bağlama   

def receive_connections():
# gelen mesajların kontrolünü yapar ve mesajları istemcilere iletir
    while True:
        client_socket, client_address = SERVER.accept() # istemciyi kabul et standart soket fonksiyonu
        print ("%s:%s has connected." % client_address) # istemcinin bağlandığını yazdır
        send_to_client(
            client_socket,
            "Welcome to the server!\nPlease enter your name:"
        )
         
        addresses[client_socket] = client_address # istemcinin adresini kaydet
        Thread(target = handle_client, args=(client_socket,)).start() # istemciyi dinlemeye başla

    

def handle_client(client_socket):
    # Client bağlantısı ile ilgili işlemleri yapar

    # Client'tan kullanıcı adını al
    name = receive_from_client(client_socket)

    # Bağlantı kullanıcı adı alınmadan kapandıysa çık
    if name is None:
        client_socket.close()
        return
    
    welcome_message = (
        "Welcome %s! "
        "If you ever want to quit, type {quit} to exit."
        % name
    )

    # Hoş geldin mesajını client'a gönder
    send_to_client(
        client_socket,
        welcome_message
    )

    # Client'ın kullanıcı adını kaydet
    clients[client_socket] = name

    # Diğer kullanıcılara yeni kişinin katıldığını bildir
    broadcast(
        "%s has joined the chat." % name
    )

    while True:

        # Client'tan yeni mesaj bekle
        message = receive_from_client(client_socket)

        # Bağlantı aniden kesildiyse döngüden çık
# Bağlantı aniden kesildiyse
        if message is None:

            # Client'ı kullanıcı listesinden sil
            if client_socket in clients:
                del clients[client_socket]

            # Client'ın adres bilgisini sil
            if client_socket in addresses:
                del addresses[client_socket]

            # Socket'i kapat
            client_socket.close()

            # Diğer kullanıcılara ayrıldığını bildir
            broadcast("%s has left the chat." % name)

            # Mesaj dinleme döngüsünden çık
            break
        # Kullanıcı çıkış komutu göndermediyse
        # mesajı diğer client'lara yayınla
        if message != "{quit}":
            broadcast(
                message,
                name + ": "
            )

        # Kullanıcı {quit} gönderdiyse
        else:

            # Client'a çıkış mesajını framing protokolüyle gönder
            send_to_client(
                client_socket,
                "{quit}"
            )

            # Socket bağlantısını kapat
            client_socket.close()

            # Client'ı kullanıcı listesinden sil
            if client_socket in clients:
                del clients[client_socket]

            # Client'ın adres bilgisini sil
            if client_socket in addresses:
                del addresses[client_socket]

            # Diğer kullanıcılara kişinin ayrıldığını bildir
            broadcast(
                "%s has left the chat." % name
            )

            break


def broadcast(message, person=""):
    # Mesajı bütün istemcilere gönder
    for client_socket in clients:

        full_message = person + message

        send_to_client(
            client_socket,
            full_message
        )

def receive_exactly(client_socket, byte_count):
    """
    Socket üzerinden tam olarak byte_count kadar veri okur.
    TCP veriyi parçalı verebildiği için recv() tek seferde
    istediğimiz tüm byte'ları döndürmeyebilir.
    """

    data = b""

    while len(data) < byte_count:

        # Eksik kalan byte sayısını hesapla
        remaining = byte_count - len(data)

        # Eksik kalan kadar veri oku
        chunk = client_socket.recv(remaining)

        # Boş veri geldiyse bağlantı kapanmıştır
        if not chunk:
            return None

        # Gelen parçayı biriktir
        data += chunk

    return data

def receive_from_client(client_socket):
    """
    Client'tan önce 10 byte header,
    sonra header'da belirtilen uzunluk kadar mesaj okur.
    """

    # Önce header'ı tam olarak oku
    header_bytes = receive_exactly(
        client_socket,
        HEADER_SIZE
    )

    # Bağlantı kapanmışsa
    if header_bytes is None:
        return None

    # Header'ı string'e çevir
    header = header_bytes.decode("utf-8")

    # Mesaj uzunluğunu al
    message_length = int(header)

    # Gerçek mesajı tam uzunluğu kadar oku
    message_bytes = receive_exactly(
        client_socket,
        message_length
    )

    if message_bytes is None:
        return None

    # Byte'ları tekrar string'e çevir
    return message_bytes.decode("utf-8")

def send_to_client(client_socket, message):
    """
    Mesajı header + message formatında client'a gönderir.
    """

    # String mesajı byte'a çevir
    message_bytes = message.encode("utf-8")

    # Mesajın byte uzunluğunu bul
    message_length = len(message_bytes)

    # 10 karakterlik header oluştur
    header = str(message_length).zfill(
        HEADER_SIZE
    )

    # Header'ı da byte'a çevir
    header_bytes = header.encode("utf-8")

    # Header ve mesajı birlikte gönder
    client_socket.sendall(
        header_bytes + message_bytes
    )



if __name__ == "__main__": # bu dosya çalıştırıldığında çalışacak kodlar
    SERVER.listen() # soketi dinlemeye başla
    print("Waiting for connection...") # bağlantı bekleniyor mesajı yazdır
    ACCEPT_THREAD = Thread(target=receive_connections) # gelen bağlantıları dinlemeye başla
    ACCEPT_THREAD.start() # thread'i başlat
    ACCEPT_THREAD.join() # thread'in bitmesini bekle
    SERVER.close() # soketi kapat