# Python TCP Chat

Python ile geliştirilmiş, TCP client-server mimarisini kullanan çok kullanıcılı bir mesajlaşma uygulamasıdır. Proje; socket programlama, TCP üzerinde mesaj sınırlandırma, eşzamanlı istemci yönetimi ve bağlantı kontrolü gibi temel ağ programlama konularını uygulamalı olarak göstermeyi amaçlar.

## Temel özellikler

- TCP client-server tabanlı çok kullanıcılı iletişim
- Her istemcinin ayrı bir thread ile işlendiği multi-client desteği
- Genel ve özel mesajlaşma
- Bağlantı ve ayrılmalarda güncellenen online kullanıcı listesi
- Özel mesaj hedefini online kullanıcı listesinden seçebilme
- Kullanıcının kendi hesabını listede `(Sen)` etiketiyle ayırt edebilmesi
- TCP byte akışında mesaj sınırlarını belirlemek için 10 byte header kullanan message framing
- `LOGIN`, `MESSAGE`, `PRIVATE_MESSAGE`, `USER_LIST`, `PING`, `PONG` ve `QUIT` türlerinden oluşan uygulama katmanı protokolü
- `PING`/`PONG` tabanlı heartbeat ve heartbeat timeout kontrolü
- Bağlantı beklenmedik şekilde kesildiğinde client tarafında otomatik yeniden bağlanma denemeleri
- Client ve server tarafında kilitlerle korunan thread-safe socket gönderimleri
- Client ve server tarafında dosyaya loglama
- Socket hataları, bağlantılar, kullanıcı giriş/çıkışları, heartbeat timeout'ları ve reconnect denemelerinin loglanması
- Tkinter tabanlı kullanıcı arayüzü

## Kullanılan teknolojiler

Proje Python 3 ile geliştirilmiştir. `socket`, `threading`, `queue`, `time`, `json`, `logging` ve Tkinter kullanılır. Harici bir Python paketi gerekmez; Python kurulumunda Tkinter desteğinin bulunması yeterlidir.

Wireshark uygulamayı çalıştırmak için zorunlu değildir. İstenirse aşağıdaki görüntüleme filtresiyle uygulamanın TCP trafiği incelenebilir:

```text
tcp.port == 19751
```

## İletişim yapısı

### TCP message framing

TCP veriyi mesajlar halinde değil, kesintisiz bir byte akışı olarak taşır. Bu nedenle her gönderimin başına, UTF-8 ile kodlanan mesaj gövdesinin byte uzunluğunu belirten sabit boyutlu 10 byte header eklenir. Alıcı önce header'ı, ardından belirtilen uzunluktaki gövdeyi tam olarak okur.

### Uygulama katmanı protokolü

Protokol mesajları `TÜR|içerik` biçimindedir.

| Mesaj türü | Amaç |
| --- | --- |
| `LOGIN` | Kullanıcı adını server'a iletir. |
| `MESSAGE` | Genel sohbet mesajı gönderir. |
| `PRIVATE_MESSAGE` | Seçilen kullanıcıya özel mesaj gönderir. |
| `USER_LIST` | Online kullanıcı listesini JSON olarak client'lara iletir. |
| `PING` | Server'ın bağlantının aktif olup olmadığını kontrol etmesini sağlar. |
| `PONG` | Client'ın heartbeat kontrolüne yanıt vermesini sağlar. |
| `QUIT` | Kullanıcının sohbetten ayrıldığını bildirir. |

Server'ın bazı sohbet ve bilgilendirme yanıtları aynı 10 byte framing yapısı içinde düz metin olarak gönderilir.

### Heartbeat ve bağlantı yönetimi

Server, bağlı client'lara 10 saniyede bir `PING` gönderir; client buna otomatik olarak `PONG` ile yanıt verir. Son `PONG` yanıtından itibaren 30 saniye içinde yeni bir yanıt alınmazsa server bağlantıyı zaman aşımına uğramış kabul ederek kapatır ve kullanıcı kaydını temizler.

Client bağlantının beklenmedik şekilde kapandığını algıladığında kayıtlı bağlantı bilgileriyle otomatik olarak yeniden bağlanmayı dener. Mevcut uygulamada en fazla 3 deneme yapılır ve denemeler arasında 3 saniye beklenir. Kullanıcının `QUIT` ile yaptığı normal çıkışta reconnect başlatılmaz.

## Logging

Server logları `server.log`, client logları ise `client.log` dosyasına yazılır. Bağlantıların kurulması ve kesilmesi, kullanıcı giriş/çıkışları, socket hataları, heartbeat timeout'ları ve reconnect denemeleri kayıt altına alınır.

## Çalıştırma

1. Proje klasöründe server'ı başlatın:

   ```bash
   python server.py
   ```

2. Ayrı bir terminalde client'ı başlatın. Birden fazla kullanıcı için komutu farklı terminallerde yeniden çalıştırın:

   ```bash
   python Client.py
   ```

3. Arayüzde kullanıcı adını girin ve bağlantıyı kurun. Varsayılan server adresi `127.0.0.1`, port numarası `19751`'dir. Server varsayılan ayarlarıyla yalnızca yerel bilgisayarı dinler.
4. Genel mesaj göndermek için mesaj kutusunu kullanın.
5. Özel mesaj göndermek için online kullanıcı listesinden hedef kullanıcıyı seçin, mesajınızı yazın ve özel gönderme butonunu kullanın. Kendi hesabınız listede `(Sen)` etiketiyle gösterilir. Özel mesajlar `/msg KullanıcıAdı Mesaj` biçimiyle de gönderilebilir.
6. Çıkmak için `{quit}` gönderin veya pencereyi kapatın.

## Öğrenilen network konuları

- TCP bağlantısının kurulması, veri aktarımı ve kapanması
- TCP'nin byte akışı yapısı ve parçalı verinin tam olarak okunması
- Mesaj sınırlarının header tabanlı framing ile belirlenmesi
- Uygulama katmanında mesaj türleri ve mesaj yönlendirme
- Thread kullanarak eşzamanlı istemci yönetimi
- Kilitlerle thread-safe socket gönderimi
- Heartbeat, timeout ve bağlantı temizliği
- Wireshark ile TCP trafiği ve uygulama mesajlarının incelenmesi

## Cisco Packet Tracer Labı

Cisco Packet Tracer çalışması, Python chat uygulamasından ayrı bir network laboratuvar çalışmasıdır. Python uygulamasına entegre değildir ve chat uygulamasını çalıştırmak için gerekli değildir.

Bu ayrı laboratuvar çalışmasında ele alınan konular:

- VLAN
- Trunk bağlantıları
- Router-on-a-stick
- Inter-VLAN routing
- DHCP
- ACL

## Gelecekte yapılabilecek geliştirmeler

- Kullanıcı doğrulama
- Benzersiz kullanıcı adı kontrolü
- Kullanıcı veritabanı
- TLS ile şifreli iletişim
- Mesaj geçmişi
- Sohbet odaları
- Dosya gönderimi
