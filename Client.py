from socket  import socket, AF_INET, SOCK_STREAM
from threading import Thread # birden fazla istemciyi aynı anda dinleyebilmek için
import tkinter # GUI kütüphanesi 

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


#application GUI
app = tkinter.Tk() # GUI oluştur
app.title("Chat uygulamam") # GUI başlığı


message_frame = tkinter.Frame(app) # mesaj çerçevesi oluştur
my_message = tkinter.StringVar() # mesaj değişkeni oluştur
my_message.set("chatinizi giriniz.") # mesaj değişkenine başlangıç mesajı ata
scrollbar = tkinter.Scrollbar(message_frame) # mesaj çerçevesine scrollbar ekle
message_list = tkinter.Listbox(message_frame, height=15, width=50, yscrollcommand=scrollbar.set) # mesaj listesi oluştur
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.BOTH) # scrollbar'ı sağ tarafa ekle
message_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH) # mesaj listesi'ni sola ekle
message_frame.pack() # mesaj çerçevesini GUI'ye ekle

entry_field = tkinter.Entry(app, textvariable=my_message) # mesaj giriş alanı oluştur
entry_field.bind("<Return>", send) # enter tuşuna basıldığında mesaj gönder
entry_field.pack() # mesaj giriş alanını GUI'ye ekle
send_button = tkinter.Button(app, text="Gönder", command=send) # mesaj gönder butonu oluştur
send_button.pack() # mesaj gönder butonunu GUI'ye ekle

HOST = '127.0.0.1' #localhost, ıp adresi
PORT = 19751 # port numarası 0–65535 arası olabilir

BUFFERSIZE = 1024 # buffer boyutu

ADDR = (HOST, PORT) # adres tuple'ı
client_socket = socket(AF_INET, SOCK_STREAM) # soket oluşturma
client_socket.connect(ADDR) # soketi adrese bağlama 

coming_message_thread = Thread(target=revieve_message) # gelen mesajları dinlemeye başla
coming_message_thread.start() # thread'i başlat

app.protocol("WM_DELETE_WINDOW", on_closing) # pencere kapatıldığında on_closing fonksiyonunu çağır

app.mainloop() # GUI'yi başlat
