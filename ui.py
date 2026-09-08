import tkinter


class ChatUI:

    def __init__(self, connect_callback, send_callback, close_callback):

        # Ana pencere
        self.app = tkinter.Tk()
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

        # Mesaj yazma alanı
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
        self.message_list.insert(
            tkinter.END,
            message
        )


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