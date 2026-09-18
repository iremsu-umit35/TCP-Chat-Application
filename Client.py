import json
from threading import Thread
from time import sleep # reconnect için sleep fonksiyonu
from network import NetworkClient
from ui import ChatUI
from protocol import (
    SEPARATOR,
    USER_LIST,
    PING,
    PONG,
    parse_message,
    create_message,
    LOGIN,
    MESSAGE,
    QUIT,
    PRIVATE_MESSAGE)

DISCONNECTED = "DISCONNECTED"
CONNECTING = "CONNECTING"
CONNECTED = "CONNECTED"
RECONNECTING = "RECONNECTING"

connection_state = DISCONNECTED

should_reconnect = True
saved_username = None
saved_host = None
saved_port = None
# TCP işlemlerini yapacak nesne
network_client = NetworkClient()


def listen_for_messages():
    """
    Server'dan gelen mesajları sürekli dinler.
    """
    global connection_state, should_reconnect
    while True:
        try:
            msg = network_client.receive_message()

            if not msg:
                connection_state = DISCONNECTED
                break

            message_type, content = parse_message(msg)

            if message_type == PING:
                network_client.send_message(
                    create_message(PONG)
                )

            elif message_type == PONG:
                continue

            elif message_type == USER_LIST:
                ui.update_users(
                    json.loads(content)
                )

            else:
                ui.add_message(msg)

        except OSError:
            connection_state = DISCONNECTED
            break

    ui.update_users([])

    if should_reconnect:
        if reconnect_to_server():
            listen_for_messages()
            return
    
def send(event=None):
    """
    Kullanıcının yazdığı mesajı server'a gönderir.
    """
    global should_reconnect

    # Mesajı UI'dan al
    msg = ui.get_message()

    # Mesaj kutusunu temizle
    ui.clear_message()

    # Server'a gönder
    
    if msg == "{quit}":
        should_reconnect = False

        network_client.send_message(
            create_message(QUIT)
        )
    elif msg.startswith("/msg "):
        # Özel mesaj gönderme formatı: /msg alici_adi mesaj
        parts = msg.split(" ", 2)

        if len(parts) == 3:
            target_user = parts[1]
            private_content = parts[2]
            private_message = f"{target_user}{SEPARATOR}{private_content}"

            network_client.send_message(
                create_message(PRIVATE_MESSAGE, private_message)
            )    
    else:
        network_client.send_message(
            create_message(MESSAGE, msg)
        )

    # Çıkış mesajı gönderildiyse bağlantıyı kapat
    if msg == "{quit}":
        network_client.close()
        ui.close()



# özel mesaj gönderme fonksiyonu
def send_private_message():
    target_user = ui.get_private_user()
    message = ui.get_message()

    if not target_user or not message:
        return

    private_content = f"{target_user}|{message}"

    network_client.send_message(
        create_message(PRIVATE_MESSAGE, private_content)
    )

    ui.clear_message()

def on_closing(event=None):
    """
    Kullanıcı pencereyi kapattığında
    server'a çıkış mesajı gönderir.
    """

    if network_client.client_socket:

        ui.set_message("{quit}")

        send()

    else:

        ui.close()




def connect_to_server():

    """
    UI'dan server bilgilerini alır
    ve TCP bağlantısını oluşturur.
    """
    global connection_state
    global saved_username, saved_host, saved_port

    connection_state = CONNECTING

    # UI katmanından bağlantı bilgilerini al
    username, host, port = ui.get_connection_data()

    saved_username = username
    saved_host = host
    saved_port = port
    try:
        # Server'a TCP bağlantısı kur
        network_client.connect(
            host,
            port
        )

        connection_state = CONNECTED

        # Kullanıcı adını server'a gönder
        network_client.send_message(
            create_message(LOGIN, username)
        )

        # Bağlantı ekranını gizleyip chat ekranını göster
        ui.show_chat()

        # Server'dan mesajları ayrı thread içerisinde dinle
        coming_message_thread = Thread(
            target=listen_for_messages,
            daemon=True
        )

        coming_message_thread.start()

    except OSError:
        connection_state = DISCONNECTED
        print("Server'a bağlanılamadı.")

# UI nesnesini oluştur
ui = ChatUI(
    connect_callback=connect_to_server,
    send_callback=send,
    private_send_callback=send_private_message,
    close_callback=on_closing
)

def reconnect_to_server():
    """ Server'a yeniden bağlanmayı dener. 3 deneme + 3 saniye bekleme"""

    global connection_state

    connection_state = RECONNECTING

    max_attempts = 3
    retry_delay = 3

    for attempt in range(1, max_attempts + 1):
        try:
            print(
                f"Yeniden bağlanılıyor... "
                f"Deneme {attempt}/{max_attempts}"
            )

            network_client.connect(
                saved_host,
                saved_port
            )

            network_client.send_message(
                create_message(LOGIN, saved_username)
            )

            connection_state = CONNECTED

            print("Server'a yeniden bağlanıldı.")
            return True

        except OSError:
            print("Bağlantı denemesi başarısız.")

            if attempt < max_attempts:
                sleep(retry_delay)

    connection_state = DISCONNECTED
    print("Server'a yeniden bağlanılamadı.")

    return False

# GUI'yi çalıştır
ui.run()
