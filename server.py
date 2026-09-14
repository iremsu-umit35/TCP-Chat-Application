import json
from threading import RLock, Lock
from time import monotonic, sleep
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread # birden fazla istemciyi aynı anda dinleyebilmek için
from protocol import (SEPARATOR, parse_message,
                      PRIVATE_MESSAGE, USER_LIST, PING, PONG, create_message)

clients = {}# istemcilerin soketlerini tutmak için bir liste
clients_lock = RLock()
send_locks = {}
last_pong = {}
user_list_lock = Lock()
PING_INTERVAL = 10
PONG_TIMEOUT = 30
addresses = {} # istemcilerin adreslerini tutmak için bir liste

# client taraıfnda hangi server ile yapılabir tarzı imput oluşturabililir gelişme amaçlı 
# kullanıc girişi veri tabanı send ile gönderilecek server alacak kullanıcı listesi oluşturulacak ve kullanıcılar listesi ile karşılaştırılacak
#gelen mesaj şu ise aç kullanıcadı varmı konrol et vs vs 
HEADER_SIZE = 10
HOST = '127.0.0.1' #localhost, ıp adresi
PORT = 19751 # port numarası 0–65535 arası olabilir



ADDR = (HOST, PORT) # adres tuple'ı
SERVER = socket(AF_INET, SOCK_STREAM) # soket oluşturma
SERVER.bind(ADDR) # soketi adrese bağlama   

def receive_connections():
# gelen mesajların kontrolünü yapar ve mesajları istemcilere iletir
    while True:
        client_socket, client_address = SERVER.accept() # istemciyi kabul et standart soket fonksiyonu
        print ("%s:%s has connected." % client_address) # istemcinin bağlandığını yazdır
        with clients_lock:
            addresses[client_socket] = client_address
            send_locks[client_socket] = Lock()
        Thread(target = handle_client, args=(client_socket,)).start() # istemciyi dinlemeye başla

    

def handle_client(client_socket):
    try:
        send_to_client(
            client_socket,
            "Welcome to the server!\nPlease enter your name:"
        )
        # Client bağlantısı ile ilgili işlemleri yapar

        # Client'tan kullanıcı adını al
        raw_message = receive_from_client(client_socket)
    
        # message_type, content = parse_message(message)

        if raw_message is None:
            client_socket.close()
            return

        # Bağlantı kullanıcı adı alınmadan kapandıysa çık
        message_type, content = parse_message(raw_message)

        if message_type != "LOGIN":
            client_socket.close()
            return

        name = content
        
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
        with clients_lock:
            clients[client_socket] = name
            last_pong[client_socket] = monotonic()
        broadcast_user_list()

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
                break

            with clients_lock:
                if client_socket not in last_pong:
                    break

            message_type, content = parse_message(message)
            if message_type == PONG:
                with clients_lock:
                    if client_socket in last_pong:
                        last_pong[client_socket] = monotonic()
            elif message_type == "MESSAGE":
                 broadcast(content, name + ": ")

            elif message_type == "PRIVATE_MESSAGE":
                parts = content.split(SEPARATOR, 1)
                if len(parts) == 2:
                    target_user = parts[0]
                    private_content = parts[1]

                    user_found = False

                    # Hedef kullanıcıyı bul
                    with clients_lock:
                        online_clients = list(clients.items())
                    for client, user_name in online_clients:
                        if user_name == target_user:
                            try:
                                send_to_client(
                                    client,
                                    f"[özel] {name}: {private_content}"
                                )
                            except OSError:
                                stop_client(client)
                                break

                            if client != client_socket:
                                send_to_client(
                                    client_socket,
                                    f"[özel -> {target_user}] {private_content}"
                                )
                            user_found = True
                            break

                    if not user_found:
                        send_to_client(
                            client_socket,
                            f"User '{target_user}' not found."
                        )

            elif message_type == "QUIT":
                send_to_client(client_socket, "{quit}")
                break
    except (OSError, ValueError):
        # EOF, reset and invalid frames all use the same cleanup.
        pass
    finally:
        remove_client(client_socket)


def stop_client(client_socket):
    # Do not wait for a send lock: shutdown must interrupt blocked socket I/O.
    with clients_lock:
        last_pong.pop(client_socket, None)
        try:
            client_socket.shutdown(2)
        except OSError:
            pass
        client_socket.close()


def remove_client(client_socket):
    with clients_lock:
        was_online = client_socket in clients
        name = clients.pop(client_socket, None)
        addresses.pop(client_socket, None)
        stop_client(client_socket)
        send_locks.pop(client_socket, None)
    if was_online:
        broadcast("%s has left the chat." % name)
        broadcast_user_list()


def send_heartbeats():
    while True:
        sleep(PING_INTERVAL)
        with clients_lock:
            online_clients = list(last_pong)
        for client_socket in online_clients:
            try:
                send_to_client(client_socket, create_message(PING))
            except OSError:
                stop_client(client_socket)


def check_heartbeat_timeouts():
    while True:
        sleep(1)
        with clients_lock:
            for client_socket, pong_time in list(last_pong.items()):
                if monotonic() - pong_time >= PONG_TIMEOUT:
                    # The handler performs cleanup and broadcasts outside this thread.
                    stop_client(client_socket)


def broadcast(message, person=""):
    with clients_lock:
        online_clients = list(clients)
    for client_socket in online_clients:
        try:
            send_to_client(client_socket, person + message)
        except OSError:
            stop_client(client_socket)


def broadcast_user_list():
    # Serialize snapshots so an older list cannot overwrite a newer one.
    with user_list_lock:
        with clients_lock:
            users = list(clients.values())
        broadcast(create_message(USER_LIST, json.dumps(users, ensure_ascii=False)))


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
    with clients_lock:
        send_lock = send_locks.get(client_socket)
    if send_lock is None:
        raise OSError("Client is disconnected")
    with send_lock:
        client_socket.sendall(
            header_bytes + message_bytes
        )




if __name__ == "__main__": # bu dosya çalıştırıldığında çalışacak kodlar
    SERVER.listen() # soketi dinlemeye başla
    Thread(target=send_heartbeats, daemon=True).start()
    Thread(target=check_heartbeat_timeouts, daemon=True).start()
    print("Waiting for connection...") # bağlantı bekleniyor mesajı yazdır
    ACCEPT_THREAD = Thread(target=receive_connections) # gelen bağlantıları dinlemeye başla
    ACCEPT_THREAD.start() # thread'i başlat
    ACCEPT_THREAD.join() # thread'in bitmesini bekle
    SERVER.close() # soketi kapat
