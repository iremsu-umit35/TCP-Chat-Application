# Python TCP Chat

TCP socket programlama ve network iletişimini öğrenmek için geliştirilen, Tkinter arayüzlü çok kullanıcılı sohbet uygulaması.

## Temel özellikler

- TCP client-server iletişimi ve thread tabanlı multi-client desteği
- Genel (public) ve özel (private) mesajlaşma
- Bağlantı ve ayrılmalarda güncellenen online kullanıcı listesi
- 10 byte uzunluk header'ı ile TCP message framing
- Uygulama katmanı protokolü (application-layer protocol)
- Heartbeat: 10 saniyede bir PING, client'tan otomatik PONG yanıtı
- 30 saniye PONG alınmazsa bağlantının kapatılması ve kullanıcı kaydının temizlenmesi
- Kilitlerle korunan thread-safe socket gönderimleri
- Tkinter arayüzü; heartbeat mesajları sohbet alanında gösterilmez

## Kullanılan teknolojiler

Python 3, `socket`, `threading`, `queue`, `time`, `json` ve Tkinter. Harici Python paketi gerekmez; Python ortamında Tkinter bulunmalıdır. Network analizlerinde Wireshark kullanılmıştır; uygulamayı çalıştırmak için gerekli değildir.

## Protokol mesaj türleri

| Tür | Amaç |
| --- | --- |
| `LOGIN` | Kullanıcı adını server'a iletme |
| `MESSAGE` | Genel mesaj gönderme |
| `PRIVATE_MESSAGE` | Belirli kullanıcıya mesaj gönderme |
| `USER_LIST` | Online kullanıcı listesini JSON olarak iletme |
| `PING` | Server'ın bağlantı kontrolü |
| `PONG` | Client'ın heartbeat yanıtı |
| `QUIT` | Sohbetten çıkış |

Protokol mesajlarının gövdesi `TÜR|içerik` biçimindedir. Her gönderimin başında, UTF-8 gövdesinin byte uzunluğunu belirten 10 byte header bulunur. Server'ın sohbet ve bilgilendirme yanıtları aynı framing içinde düz metin olarak gönderilir.

## Çalıştırma

1. Proje klasöründe server'ı başlat:

   ```bash
   python server.py
   ```

2. Ayrı bir terminalde client'ı başlat. Birden fazla kullanıcı için bu komutu farklı terminallerde tekrarla:

   ```bash
   python Client.py
   ```

3. Arayüzde kullanıcı adını gir; IP `127.0.0.1`, port `19751` ile bağlan. Varsayılan server yalnızca yerel bilgisayarı dinler.
4. Genel mesaj için mesaj kutusunu kullan. Özel mesaj için `/msg Ayse Merhaba` yaz veya hedef kullanıcı alanını ve **Özel Gönder** butonunu kullan.
5. Çıkmak için `{quit}` gönder veya pencereyi kapat.

## Öğrenilen network konuları

- TCP bağlantısının kurulması, veri aktarımı ve kapanması
- TCP'nin byte akışı olması; parçalı veriyi okuma ve mesaj sınırlarını framing ile belirleme
- Uygulama katmanında mesaj türleri ve yönlendirme
- Eşzamanlı socket işlemleri, thread ve kilit kullanımı
- Heartbeat, timeout ve bağlantı temizliği
- Wireshark ile TCP trafiği ve uygulama mesajlarının analizi (`tcp.port == 19751`)

## Gelecekte yapılabilecek geliştirmeler

- Bağlantı kesilince otomatik yeniden bağlanma
- Kullanıcı doğrulama ve benzersiz kullanıcı adı kontrolü
- TLS ile şifreli iletişim
- Mesaj geçmişi ve sohbet odaları
