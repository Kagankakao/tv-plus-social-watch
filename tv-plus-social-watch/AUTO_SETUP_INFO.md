# 🎬 Otomatik Kurulum - Hazır Oylama Sistemi

## ✅ Artık Her Şey Otomatik!

Artık uygulama başladığında **hiçbir script çalıştırmanıza gerek yok**. Her şey otomatik olarak hazır!

---

## 🚀 Nasıl Çalışıyor?

### 1. Sunucu Başlatıldığında (Startup)
```
python -m uvicorn main:app --reload
```

**Otomatik olarak:**
- ✅ `room_1` odası oluşturulur
- ✅ Varsayılan kullanıcılar eklenir (Ali, Ayşe, Mehmet, Moderatör)
- ✅ Oda başlangıç saati 1 saat sonraya ayarlanır

### 2. İlk Oylama Sayfası Açıldığında

Kullanıcı `/votes/room_1/candidates` endpoint'ine istek attığında:

**Otomatik olarak:**
- ✅ 3 film catalog'a eklenir:
  - Yıldızlararası (169 dk)
  - Fight Club (139 dk)
  - Star Wars (121 dk)
- ✅ Bu filmler room_1 için oylama adayı olarak eklenir
- ✅ Filmler anında kullanıcıya gösterilir

### 3. Uygulama Açıldığında

Kullanıcı `http://localhost:8000/app` adresini ziyaret ettiğinde:

**Otomatik olarak:**
- ✅ Geçici kullanıcı oluşturulur (localStorage'da saklanır)
- ✅ room_1'e katılır
- ✅ **Oylama sekmesinde 3 film hazır görünür** 🎉

---

## 📋 Otomatik Eklenen Veriler

### Kullanıcılar (room_1 için)
```
user_id    | name      | avatar
-----------|-----------|-------
user_1     | Ali       | 👨
user_2     | Ayşe      | 👩
user_3     | Mehmet    | 🧑
host_1     | Moderatör | 👑
```

### Oda (room_1)
```
room_id | title               | host_id | start_at
--------|---------------------|---------|----------
room_1  | Akşam Film Gecesi   | host_1  | +1 saat
```

### Filmler (Catalog)
```
content_id   | title           | type  | duration | tags
-------------|-----------------|-------|----------|----------------------
interstellar | Yıldızlararası  | movie | 169 min  | bilim-kurgu,dram,...
fight_club   | Fight Club      | movie | 139 min  | dram,gerilim,...
star_wars    | Star Wars       | movie | 121 min  | bilim-kurgu,...
```

### Oylama Adayları (Candidates)
```
room_id | content_id
--------|------------
room_1  | interstellar
room_1  | fight_club
room_1  | star_wars
```

---

## 🎯 Artık Yapmanız Gerekenler

### Sadece 2 Adım!

**1. Sunucuyu Başlatın**
```bash
cd tv-plus-social-watch
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Konsol Çıktısı:**
```
✅ Default room 'room_1' initialized with voting candidates
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**2. Tarayıcıyı Açın**
```
http://localhost:8000/app
```

**İşte bu kadar!** 🎉

---

## 🎬 Kullanıcı Deneyimi

### Kullanıcı Uygulamayı Açar

1. **Anasayfa yüklenir**
   - Otomatik geçici kullanıcı oluşturulur
   - room_1'e otomatik katılır

2. **"Oylama" sekmesine tıklar**
   - **3 film anında görünür!** ✅
   - Yıldızlararası (169 dk)
   - Fight Club (139 dk)
   - Star Wars (121 dk)

3. **Oy verebilir**
   - Herhangi bir filme "Oy Ver" butonuna tıklar
   - Oyu kaydedilir
   - Sayaç güncellenir: "1/1 kişi oy kullandı"

4. **2. kullanıcı katılınca**
   - Sayaç: "1/2 kişi oy kullandı" olur
   - Her iki kullanıcı oy verince kazanan film seçilir
   - Video oynatıcı açılır

---

## 🔧 Kod Değişiklikleri

### 1. `main.py` - Startup Event
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Otomatik room_1 oluştur
    await create_room("room_1", "Akşam Film Gecesi", start_time, "host_1")
    yield
```

### 2. `voting_service.py` - Auto-Add Candidates
```python
async def list_candidates(room_id: str):
    # Aday yoksa otomatik ekle
    if candidate_count == 0:
        # 3 filmi ekle
        for movie in default_movies:
            await cur.execute("INSERT INTO catalog ...")
        # Adayları ekle
        for candidate in default_candidates:
            await cur.execute("INSERT INTO candidates ...")
```

### 3. `room_service.py` - Auto-Add Users
```python
async def create_room(...):
    if room_id == 'room_1':
        # Varsayılan kullanıcıları ekle
        for user in default_users:
            await cur.execute("INSERT INTO users ...")
```

### 4. `app.js` - Auto-Create User & Room
```javascript
loadUserAndRoomData() {
    if (!storedUser) {
        // Otomatik kullanıcı oluştur
        this.userData = {...}
    }
    if (!storedRoom) {
        // Otomatik room_1 kullan
        this.roomData = {roomId: 'room_1', ...}
    }
}
```

---

## ✨ Avantajlar

### Eskiden (Manuel)
```bash
# 1. Veritabanını kontrol et
python check_candidates.py

# 2. Mock data ekle
python add_mock_data.py

# 3. Kullanıcı oluştur
# Login sayfasından kayıt ol

# 4. Oda oluştur
# Register sayfasından oda oluştur

# 5. Sonunda uygulamayı aç
http://localhost:8000/app
```

### Şimdi (Otomatik)
```bash
# 1. Sunucuyu başlat
python -m uvicorn main:app --reload

# 2. Uygulamayı aç - HER ŞEY HAZIR!
http://localhost:8000/app
```

---

## 🐛 Sorun Giderme

### Film listesi görünmüyorsa?

**Konsolu kontrol edin (F12 → Console):**
```
Loading candidates for room: room_1
Candidates loaded: {candidates: Array(3)}
```

**Network sekmesini kontrol edin (F12 → Network):**
```
GET /votes/room_1/candidates
Status: 200 OK
Response: {candidates: [...]}
```

### Sunucu başlarken hata alıyorsanız?

**Konsol çıktısına bakın:**
```
⚠️ Room initialization: [hata mesajı]
```

Veritabanı bağlantısını kontrol edin:
```bash
# .env dosyasını kontrol et
cat .env
```

---

## 🎉 Sonuç

Artık sistem tamamen otomatik! 

✅ **Sunucuyu başlatın**  
✅ **Tarayıcıyı açın**  
✅ **3 film hazır, oylama başlasın!** 🎬

Hiçbir manuel işlem gerekmez! 🚀
