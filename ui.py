import tkinter
from queue import Queue, Empty


class ChatUI:

    def __init__(self, connect_callback, send_callback, private_send_callback, close_callback):

        # Ana pencere
        self.updates = Queue()
        self.app = tkinter.Tk()
        self.app.after(50, self.process_updates)
        self.app.title("Chat Application")

        # Pencere kapatılırken Client.py içindeki fonksiyonu çalıştır
        self.app.protocol("WM_DELETE_WINDOW", close_callback)

        # ------------------------------------------------
        # SERVER BAĞLANTI EKRANI
        # ------------------------------------------------

        self.connection_frame = tkinter.Frame(self.app)

        tkinter.Label(
            self.connection_frame,
            text="Kullanıcı Adı"
        ).pack()

        self.username_entry = tkinter.Entry(
            self.connection_frame
        )
        self.username_entry.pack()

        tkinter.Label(
            self.connection_frame,
            text="Server IP"
        ).pack()

        self.host_entry = tkinter.Entry(
            self.connection_frame
        )
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack()

        tkinter.Label(
            self.connection_frame,
            text="Port"
        ).pack()

        self.port_entry = tkinter.Entry(
            self.connection_frame
        )
        self.port_entry.insert(0, "19751")
        self.port_entry.pack()

        self.connect_button = tkinter.Button(
            self.connection_frame,
            text="Bağlan",
            command=connect_callback
        )
        self.connect_button.pack()

        self.connection_frame.pack()

        # ------------------------------------------------
        # CHAT EKRANI
        # ------------------------------------------------

        # Chat ekranını oluşturuyoruz fakat başlangıçta göstermiyoruz
        self.chat_frame = tkinter.Frame(self.app)

        # Mesaj listesinin bulunduğu frame
        self.message_frame = tkinter.Frame(
            self.chat_frame
        )

        # Kullanıcının yazdığı mesajı tutar
        self.my_message = tkinter.StringVar()
        self.my_message.set("")

        # Scrollbar
        self.scrollbar = tkinter.Scrollbar(
            self.message_frame
        )

        # Gelen mesajların gösterileceği liste
        self.message_list = tkinter.Listbox(
            self.message_frame,
            height=15,
            width=50,
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(
            side=tkinter.RIGHT,
            fill=tkinter.BOTH
        )

        self.message_list.pack(
            side=tkinter.LEFT,
            fill=tkinter.BOTH
        )

        self.message_frame.pack()

        tkinter.Label(self.chat_frame, text="Online kullanıcılar").pack()
        self.user_list = tkinter.Listbox(self.chat_frame, height=6, width=50)
        self.user_list.pack()

        # Mesaj yazma alanı

        self.private_user_entry = tkinter.Entry(
            self.chat_frame
        )
        self.private_user_entry.insert(0, "Hedef kullanıcı")
        self.private_user_entry.pack()

        self.entry_field = tkinter.Entry(
            self.chat_frame,
            textvariable=self.my_message
        )

        # Enter'a basıldığında mesaj gönder
        self.entry_field.bind(
            "<Return>",
            send_callback
        )

        self.entry_field.pack()

        # Gönder butonu
        self.send_button = tkinter.Button(
            self.chat_frame,
            text="Gönder",
            command=send_callback
        )
        self.send_button.pack()
        # Özel mesaj gönder butonu
        self.private_send_button = tkinter.Button(
            self.chat_frame,
            text="Özel Gönder",
            command=private_send_callback
        )
        self.private_send_button.pack()

    def show_chat(self):
        """
        Bağlantı ekranını gizler,
        chat ekranını gösterir.
        """
        self.connection_frame.pack_forget()
        self.chat_frame.pack()


    def get_connection_data(self):
        """
        Kullanıcının girdiği bağlantı bilgilerini döndürür.
        """

        username = self.username_entry.get()
        host = self.host_entry.get()
        port = int(self.port_entry.get())

        return username, host, port


    def get_message(self):
        """
        Mesaj kutusundaki mesajı döndürür.
        """
        return self.my_message.get()
    
    # özel mesaj için hedef kullanıcıyı döndürür
    def get_private_user(self):
        return self.private_user_entry.get()

    def clear_message(self):
        """
        Mesaj giriş kutusunu temizler.
        """
        self.my_message.set("")


    def set_message(self, message):
        """
        Mesaj kutusuna değer yazar.
        Örneğin {quit} göndermek için kullanılabilir.
        """
        self.my_message.set(message)


    def add_message(self, message):
        """
        Server'dan gelen mesajı chat ekranına ekler.
        """
        self.updates.put(("message", message))

    def update_users(self, users):
        self.updates.put(("users", list(users)))

    def process_updates(self):
        # Widget updates run on the Tkinter main thread.
        try:
            while True:
                kind, value = self.updates.get_nowait()
                if kind == "users":
                    self.user_list.delete(0, tkinter.END)
                    for username in value:
                        self.user_list.insert(tkinter.END, username)
                else:
                    self.message_list.insert(tkinter.END, value)
        except Empty:
            pass
        self.app.after(50, self.process_updates)


    def close(self):
        """
        GUI penceresini kapatır.
        """
        self.app.destroy()


    def run(self):
        """
        Tkinter event loop'unu başlatır.
        """
        self.app.mainloop()