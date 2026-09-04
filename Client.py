from socket  import socket, AF_INET, SOCK_STREAM
from threading import Thread # birden fazla istemciyi aynı anda dinleyebilmek için
import tkinter # GUI kütüphanesi 

client_socket = None 
BUFFERSIZE = 1024 # buffer boyutu

def revieve_message():
    #daima gelen mesajları dinler ve GUI'ye ekler
    while True:
        try:
            msg = client_socket.recv(BUFFERSIZE).decode("utf-8") # server'dan gelen mesajı al
            message_list.insert(tkinter.END, msg) # mesajı GUI'ye ekle
        except OSError:  # muhtemelen pencere kapatıldı
            break



def send(event=None):  # enter tuşuna basıldığında mesaj gönder
    msg = my_message.get() # mesaj değişkenini al
    my_message.set("") # mesaj değişkenini temizle
    client_socket.send(bytes(msg, "utf-8")) # mesajı server'a gönder    

    if msg == "{quit}": # eğer mesaj {quit} ise
        client_socket.close() # soketi kapat
        app.quit() # GUI'yi kapat



def on_closing(event=None): #çıkış yaparken yapılacak işlemler
    my_message.set("{quit}") # mesaj değişkenine {quit} ata
    send() # mesajı gönder

# server'a bağlanmak için gerekli işlemleri yapar kullanıcıdan host ve port bilgilerini alır ve soket oluşturur
def connect_to_server(): 
    global client_socket

    username = username_entry.get()
    host = host_entry.get()  # host adresini al
    port = int(port_entry.get()) # port numarasını al

    client_socket = socket(AF_INET, SOCK_STREAM) # soket oluşturma
    client_socket.connect((host, port)) # server'a bağlanma
    client_socket.send(bytes(username, "utf-8"))
    connection_frame.pack_forget() #giriş çerçevesini gizle
    chat_frame.pack() # sohbet çerçevesini göster
    coming_message_thread = Thread( # gelen mesajları dinlemek için thread oluştur
        target=revieve_message,
        daemon=True
    )
    coming_message_thread.start() # thread'i başlat



#application GUI
app = tkinter.Tk() # GUI oluştur
app.title("Chat uygulamam") # GUI başlığı

connection_frame = tkinter.Frame(app) # bağlantı çerçevesi oluştur

tkinter.Label(
    connection_frame,
    text="Kullanıcı Adı"
).pack()

username_entry = tkinter.Entry(connection_frame)
username_entry.pack()

# bağlantı çerçevesine host etiketi ekle
host_label = tkinter.Label(  
    connection_frame,
    text="Server IP"
)
host_label.pack() # etiketi çerçeveye ekle ve görünmesini sağla

host_entry = tkinter.Entry(connection_frame)
host_entry.insert(0, "127.0.0.1")
host_entry.pack() # giriş alanını çerçeveye ekle ve görünmesini sağla

port_label = tkinter.Label(
    connection_frame,
    text="Port"
)
port_label.pack()

port_entry = tkinter.Entry(connection_frame)
port_entry.insert(0, "19751")
port_entry.pack()

connect_button = tkinter.Button(
    connection_frame,
    text="Bağlan",
    command=connect_to_server 
)
connect_button.pack()

connection_frame.pack()



chat_frame = tkinter.Frame(app)

message_frame = tkinter.Frame(chat_frame) 


my_message = tkinter.StringVar() # mesaj değişkeni oluştur
my_message.set("chatinizi giriniz.") # mesaj değişkenine başlangıç mesajı ata
scrollbar = tkinter.Scrollbar(message_frame) # mesaj çerçevesine scrollbar ekle
message_list = tkinter.Listbox(message_frame, height=15, width=50, yscrollcommand=scrollbar.set) # mesaj listesi oluştur
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.BOTH) # scrollbar'ı sağ tarafa ekle
message_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH) # mesaj listesi'ni sola ekle
message_frame.pack() # mesaj çerçevesini GUI'ye ekle

entry_field = tkinter.Entry(chat_frame, textvariable=my_message) # mesaj giriş alanı oluştur
entry_field.bind("<Return>", send) # enter tuşuna basıldığında mesaj gönder
entry_field.pack() # mesaj giriş alanını GUI'ye ekle
send_button = tkinter.Button(chat_frame, text="Gönder", command=send) # mesaj gönder butonu oluştur
send_button.pack() # mesaj gönder butonunu GUI'ye ekle







app.protocol("WM_DELETE_WINDOW", on_closing) # pencere kapatıldığında on_closing fonksiyonunu çağır

app.mainloop() # GUI'yi başlat
