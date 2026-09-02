from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread # birden fazla istemciyi aynı anda dinleyebilmek için

clients = {}# istemcilerin soketlerini tutmak için bir liste
addresses = {} # istemcilerin adreslerini tutmak için bir liste

# client taraıfnda hangi server ile yapılabir tarzı imput oluşturabililir gelişme amaçlı 
# kullanıc girişi veri tabanı send ile gönderilecek server alacak kullanıcı listesi oluşturulacak ve kullanıcılar listesi ile karşılaştırılacak
#gelen mesaj şu ise aç kullanıcadı varmı konrol et vs vs 

HOST = '127.0.0.1' #localhost, ıp adresi
PORT = 19751 # port numarası 0–65535 arası olabilir
BUFFeR_SIZE = 1024 # buffer boyutu

ADDR = (HOST, PORT) # adres tuple'ı
SERVER = socket(AF_INET, SOCK_STREAM) # soket oluşturma
SERVER.bind(ADDR) # soketi adrese bağlama   

def recieve_message():
# gelen mesajların kontrolünü yapar ve mesajları istemcilere iletir
    while True:
        client_socket, client_address = SERVER.accept() # istemciyi kabul et standart soket fonksiyonu
        print ("%s:%s has connected." % client_address) # istemcinin bağlandığını yazdır
        client_socket.send(
                    bytes(
                        "Welcome to the server!\nPlease enter your name:",
                        "utf-8"
                    )
                )   
         
        addresses[client_socket] = client_address # istemcinin adresini kaydet
        Thread(target = handle_client, args=(client_socket,)).start() # istemciyi dinlemeye başla

    

def handle_client(client_socket):
    #client bağlantısı ile ilgili işlemleri yapar
    name = client_socket.recv(BUFFeR_SIZE).decode("utf-8") # istemciden isim bilgisini al
    welcome_message = (
        "Welcome %s! "
        "If you ever want to quit, type {quit} to exit."
        % name
    )

    client_socket.send(bytes(welcome_message, "utf-8")) # istemciye hoşgeldin mesajı gönder
    clients[client_socket] = name # istemcinin ismini kaydet
    broadcast("%s has joined the chat." % name) # istemcinin sohbete katıldığını yayınla
   

    while True:

        message = client_socket.recv(BUFFeR_SIZE).decode("utf-8") # istemciden mesaj al
        if message != "{quit}":
            broadcast(message, name + ": ") # mesajı yayınla

        else:

            client_socket.send(bytes("{quit}", "utf-8")) # istemciye çıkış mesajı gönder
            client_socket.close() # istemcinin soketini kapat
            del clients[client_socket] # istemciyi listeden sil
            if client_socket in addresses:
                del addresses[client_socket] # istemcinin adresini listeden sil

            
            broadcast("%s has left the chat." % name)
            # istemcinin ayrıldığını yayınla
            break
      


def broadcast(message, person=""):
    # Mesajı bütün istemcilere gönder
    for client_socket in clients:

        full_message = person + message

        client_socket.send(
            bytes(full_message, "utf-8")
        )


if __name__ == "__main__": # bu dosya çalıştırıldığında çalışacak kodlar
    SERVER.listen() # soketi dinlemeye başla
    print("Waiting for connection...") # bağlantı bekleniyor mesajı yazdır
    ACCEPT_THREAD = Thread(target=recieve_message) # gelen mesajları dinlemeye başla
    ACCEPT_THREAD.start() # thread'i başlat
    ACCEPT_THREAD.join() # thread'in bitmesini bekle
    SERVER.close() # soketi kapat