from threading import Thread

from network import NetworkClient
from ui import ChatUI
from protocol import create_message

# TCP işlemlerini yapacak nesne
network_client = NetworkClient()


def listen_for_messages():
    """
    Server'dan gelen mesajları sürekli dinler.
    """

    while True:
        try:
            msg = network_client.receive_message()

            if not msg:
                break

            # Gelen mesajı UI katmanına gönder
            ui.add_message(msg)

        except OSError:
            break


def send(event=None):
    """
    Kullanıcının yazdığı mesajı server'a gönderir.
    """

    # Mesajı UI'dan al
    msg = ui.get_message()

    # Mesaj kutusunu temizle
    ui.clear_message()

    # Server'a gönder
    network_client.send_message(msg)

    # Çıkış mesajı gönderildiyse bağlantıyı kapat
    if msg == "{quit}":

        network_client.close()

        ui.close()


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

    # UI katmanından bağlantı bilgilerini al
    username, host, port = ui.get_connection_data()

    # Server'a TCP bağlantısı kur
    network_client.connect(
        host,
        port
    )

    # Kullanıcı adını server'a gönder
    network_client.send_message(
        create_message("LOGIN", username)
    )

    # Bağlantı ekranını gizleyip chat ekranını göster
    ui.show_chat()

    # Server'dan mesajları ayrı thread içerisinde dinle
    coming_message_thread = Thread(
        target=listen_for_messages,
        daemon=True
    )

    coming_message_thread.start()


# UI nesnesini oluştur
ui = ChatUI(
    connect_callback=connect_to_server,
    send_callback=send,
    close_callback=on_closing
)


# GUI'yi çalıştır
ui.run()