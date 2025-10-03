# TV+ Sosyal İzleme – Ortak İzleme Odası

Bu proje, **TV+ içerikleri için arkadaşlarla aynı anda izleme deneyimini** simüle eden bir web/mini uygulamadır. Kullanıcılar bir oda kurabilir, içerik oylaması yapabilir, senkronize şekilde izleyebilir, sohbet edebilir, emoji tepkileri gönderebilir ve masrafları paylaşabilir.

## 🚀 Amaç

Ekipler, 6–8 saat içinde aşağıdaki özelliklere sahip bir prototip geliştirir:

* Oda oluşturma ve davet
* İçerik oylama
* Senkronize oynatma (host kontrolü)
* Sohbet & emoji tepkileri
* Masraf paylaşımı
* Hatırlatma bildirimi

## 🎬 Senaryo

Arkadaşlar, TV+’ta film/dizi/maç izlemek için bir **“oda”** kurar.

* Host, aday içerikleri seçer → grup oylama yapar.
* En çok oy alan içerik seçilir.
* Host play/pause yaptığında tüm kullanıcılar aynı anda senkron olur.
* Kullanıcılar sohbet eder ve emoji gönderir.
* Gece için yapılan harcamalar eşit/ağırlıklı olarak bölüşülür.
* Etkinlikten 1 saat önce hatırlatma gönderilir.

## ✅ MVP Özellikler

1. **Oda & Davet**

   * Oda oluşturma (başlık, tarih/saat)
   * Davet linki / QR (mock)
   * Roller: host, member

2. **İçerik Oylaması**

   * TV+ kataloğundan aday liste (mock)
   * Oy → en çok oy alan içerik seçilir

3. **Senkron Oynatma**

   * Host play/pause/seek kontrolü
   * Drift düzeltme: fark > 2 sn ise seek

4. **Sohbet & Emoji**

   * Metin mesajları, hızlı emojiler
   * Spam koruması (kullanıcı başına 2 sn limit)

5. **Masraf Paylaşımı (Split)**

   * Gider ekle (tutar, açıklama)
   * Eşit ya da ağırlıklı bölüşüm
   * Kişi bazlı net bakiye

6. **Hatırlatma**

   * Etkinlikten 1 saat önce oda özeti mock push

## ⭐ Ekstra (Opsiyonel)

* Geri sayım sayacı
* Mini anket (örn. altyazı mı dublaj mı?)
* Bağlantı kalitesi göstergesi (mock ping)
* Alt yazı dili senkronizasyonu

## 🏗️ Mimari

* **HTTP API + WebSocket (mock)**
* WebSocket kanalı: `/ws/rooms/{room_id}`
* Event tipleri: `play`, `pause`, `seek`, `chat`, `emoji`, `sync_ping`
* Senkron kuralı: host referans → client’lar apply

## 📡 Önerilen API Uçları

```http
POST /rooms
{ title, start_at, host_id } 
→ { room_id, invite_url }

POST /rooms/{id}/candidates
{ items:[{content_id}...] }

POST /rooms/{id}/vote
{ user_id, content_id }

GET /rooms/{id}/summary
→ { selected_content, votes, members, start_at }

POST /rooms/{id}/expenses
{ user_id, amount, note, weight? }

GET /rooms/{id}/balances
→ { totals, per_user }

POST /rooms/{id}/remind
→ { status: "ok" }
```

## 📊 Örnek Veri Setleri

* **users.csv** → `user_id,name,avatar`
* **catalog.csv** → `content_id,title,type,duration_min,tags`
* **rooms.csv** → `room_id,title,start_at,host_id`
* **candidates.csv** → `room_id,content_id`
* **votes.csv** → `room_id,content_id,user_id`
* **chat.csv** → `room_id,user_id,message,created_at`
* **emojis.csv** → `room_id,user_id,emoji,created_at`
* **expenses.csv** → `expense_id,room_id,user_id,amount,note,weight`

## 🎨 UI/UX Beklentisi

* Tek sayfa layout:

  * Sol → Video player (mock süre göstergesi)
  * Sağ → Oylama / Sohbet / Split sekmeleri
* “Senkronda değil misin?” butonu
* Üst bar: içerik adı + kalan süre sayacı

## 🏆 Puanlama

* Çalışabilirlik → 30
* Gerçek zamanlılık → 20
* Veri modeli doğruluğu → 20
* UI/UX → 20
* Bonus → 10

Kağan, istersen ben bunu daha **kısa ve pitch sunumu tarzında** da hazırlayabilirim (README yerine yatırımcıya/mentora sunum gibi). İstiyor musun?
