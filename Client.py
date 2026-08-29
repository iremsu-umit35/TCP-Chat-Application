from socket  import socket, AF_INET, SOCK_STREAM
from threading import Thread # birden fazla istemciyi aynı anda dinleyebilmek için
import tkinter # GUI kütüphanesi 

def send():
    pass


def revieve_message():
    pass


def on_closing(): #çıkış yaparken yapılacak işlemler
    pass


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
tkinter.mainloop() # GUI'yi başlat
