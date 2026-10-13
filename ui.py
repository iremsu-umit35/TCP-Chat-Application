import tkinter
from queue import Queue, Empty


class ChatUI:

    def __init__(self, connect_callback, send_callback, private_send_callback, close_callback):

        # Ana pencere
        self.updates = Queue()
        self.app = tkinter.Tk()
        self.app.after(50, self.process_updates)
        self.app.title("Chat Application")
        self.app.geometry("760x520")
        self.app.minsize(700, 480)

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

        self.content_frame = tkinter.Frame(self.chat_frame)
        self.content_frame.pack(
            fill=tkinter.BOTH,
            expand=True,
            padx=15,
            pady=15
        )

        self.left_frame = tkinter.Frame(self.content_frame)
        self.left_frame.pack(
            side=tkinter.LEFT,
            fill=tkinter.BOTH,
            expand=True
        )

        self.right_frame = tkinter.Frame(self.content_frame)
        self.right_frame.pack(
            side=tkinter.RIGHT,
            fill=tkinter.Y,
            padx=(15, 0)
        )        

        # Mesaj listesinin bulunduğu frame
        self.message_frame = tkinter.Frame(
            self.left_frame
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
            height=20,
            width=65,
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(
            side=tkinter.RIGHT,
            fill=tkinter.BOTH
        )

        self.message_list.pack(
            side=tkinter.LEFT,
            fill=tkinter.BOTH,
            expand=True
        )

        self.message_frame.pack( fill=tkinter.BOTH, expand=True)

        tkinter.Label(
            self.right_frame,
            text="Online Kullanıcılar"
        ).pack(pady=(0, 5))
        self.user_list = tkinter.Listbox(
            self.right_frame,
            height=15,
            width=22
        )

        self.user_list.pack(
            fill=tkinter.Y,
            expand=True
        )
        self.user_list.bind(
          "<<ListboxSelect>>",
          self.on_user_select
        )
        # ------------------------------------------------
        # MESAJ GÖNDERME ALANI
        # ------------------------------------------------
        # hedef kullanıcıyı göstermek için bir frame
        self.target_frame = tkinter.Frame(
            self.chat_frame
        )

        self.target_frame.pack(
            fill=tkinter.X,
            padx=15,
            pady=(0, 5)
        )

        self.selected_user = tkinter.StringVar()
        self.selected_user.set("Hedef: seçilmedi")

        self.selected_user_label = tkinter.Label(
            self.target_frame,
            textvariable=self.selected_user,
            anchor="w"
        )

        self.selected_user_label.pack(
            fill=tkinter.X
        )

        self.input_frame = tkinter.Frame(
            self.chat_frame
        )

        self.input_frame.pack(
            fill=tkinter.X,
            padx=15,
            pady=(0, 15)
        )

        # Özel mesaj için hedef kullanıcı

        self.current_username = None # Kullanıcının kendi kullanıcı adını tutar


        # Mesaj yazma kutusu
        self.entry_field = tkinter.Entry(
            self.input_frame,
            textvariable=self.my_message
        )
        self.entry_field.insert(0, "Mesaj yaz...")

        self.entry_field.bind(
            "<FocusIn>",
            self.clear_placeholder
        )

        self.entry_field.bind(
            "<FocusOut>",
            self.add_placeholder
        )

        self.entry_field.pack(
            side=tkinter.LEFT,
            fill=tkinter.X,
            expand=True,
            padx=(0, 8)
        )

        # Enter'a basıldığında mesaj gönder
        self.entry_field.bind(
            "<Return>",
            send_callback
        )

        # Normal mesaj gönderme butonu
        self.send_button = tkinter.Button(
            self.input_frame,
            text="Gönder",
            command=send_callback
        )

        self.send_button.pack(
            side=tkinter.LEFT,
            padx=(0, 5)
        )

        # Özel mesaj gönderme butonu
        self.private_send_button = tkinter.Button(
            self.input_frame,
            text="Özel Gönder",
            command=private_send_callback
        )

        self.private_send_button.pack(
            side=tkinter.LEFT
        )

    def show_chat(self):
        """
        Bağlantı ekranını gizler,
        chat ekranını gösterir.
        """
        self.connection_frame.pack_forget()
        self.chat_frame.pack(
            fill=tkinter.BOTH,
            expand=True
        )


    def get_connection_data(self):
        """
        Kullanıcının girdiği bağlantı bilgilerini döndürür.
        """
        username = self.username_entry.get()
        host = self.host_entry.get()
        port = int(self.port_entry.get())

        self.current_username = username

        return username, host, port

    def clear_placeholder(self, event=None):
        if self.entry_field.get() == "Mesaj yaz...":
            self.entry_field.delete(0, tkinter.END)


    def add_placeholder(self, event=None):
        if not self.entry_field.get():
            self.entry_field.insert(0, "Mesaj yaz...")

    def get_message(self):
        """
        Mesaj kutusundaki mesajı döndürür.
        """
        message = self.my_message.get()

        if message == "Mesaj yaz...":
            return ""
        return message

    def on_user_select(self, event=None):
        selected = self.user_list.curselection()

        if selected:
            username = self.user_list.get(selected[0])

            username = username.replace(" (Sen)", "")

            if username == self.current_username:
                self.selected_user.set("Kendine mesaj gönderemezsin")
            else:
                self.selected_user.set(f"Hedef: {username}")


    # özel mesaj için hedef kullanıcıyı döndürür
    def get_private_user(self):
        target_user = self.selected_user.get()

        if target_user == "Hedef seçilmedi":
            return ""

        if target_user == "Kendine mesaj gönderemezsin":
            return ""

        return target_user.replace("Hedef: ", "")
        
    def clear_message(self):
        """
        Mesaj giriş kutusunu temizler.
        """
        self.my_message.set("")
        self.add_placeholder()


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
                        if username == self.current_username:
                            self.user_list.insert(
                                tkinter.END,
                                f"{username} (Sen)"
                            )
                        else:
                            self.user_list.insert(
                                tkinter.END,
                                username
                            )

                elif kind == "message":
                    self.message_list.insert(
                        tkinter.END,
                        value
                    )

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