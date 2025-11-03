# 🔴 Redis Kurulum Rehberi

## Redis Nedir?

Redis, **hafızada (RAM) çalışan** çok hızlı bir veritabanı sistemidir. Bu projede **cache** (önbellek) ve **rate limiting** (istek sınırlama) için kullanılır.

## Redis Olmadan Çalışır mı?

✅ **EVET!** Redis olmadan da uygulama tamamen çalışır. Sadece:
- Cache özelliği devre dışı kalır (uygulama biraz daha yavaş olabilir ama sorun değil)
- Rate limiting devre dışı kalır (güvenlik için istenen ama zorunlu değil)

## Redis'i Ne Zaman Kurmalısınız?

Redis'i kurmanız **sadece şu durumlarda gerekir**:
- Yüksek trafik bekliyorsanız (cache performansı için)
- Rate limiting istiyorsanız (güvenlik için)
- Production ortamında çalıştırıyorsanız

**Geliştirme için Redis zorunlu değildir!**

---

## 🚀 Redis Kurulum Yöntemleri

### Yöntem 1: Docker ile (EN KOLAY) ⭐

Projede zaten `docker-compose.yml` var, sadece Redis'i başlatın:

```bash
# Sadece Redis'i başlat
docker-compose up -d redis

# Veya tüm servisleri başlat (MongoDB, Redis, Backend, Frontend)
docker-compose up -d
```

**Avantajlar:**
- Çok kolay kurulum
- Otomatik yönetim
- Diğer servislerle birlikte çalışır

---

### Yöntem 2: Windows için Memurai (Resmi Windows Portu)

1. **Memurai indirin:**
   - https://www.memurai.com/get-memurai
   - Ücretsiz geliştirme sürümü mevcut

2. **Kurulum:**
   - İndirilen `.exe` dosyasını çalıştırın
   - Kurulum sihirbazını takip edin
   - Varsayılan ayarlarla kurun (port 6379)

3. **Servis olarak çalıştır:**
   - Windows Services'te "Memurai" servisini başlatın
   - Veya otomatik başlatılacak şekilde ayarlayın

---

### Yöntem 3: WSL (Windows Subsystem for Linux)

Windows'ta Linux terminali kullanarak:

```bash
# WSL'de Ubuntu terminalini açın
wsl

# Redis'i yükleyin
sudo apt update
sudo apt install redis-server

# Redis'i başlatın
sudo service redis-server start

# Otomatik başlatma için
sudo systemctl enable redis-server
```

---

### Yöntem 4: Chocolatey ile

```bash
# Chocolatey yüklüyse
choco install redis-64

# Redis'i başlat
redis-server
```

---

## ✅ Redis Kurulumunu Test Etme

Redis kurulduktan sonra, backend'i yeniden başlatın. Terminal çıktısında şunu görmelisiniz:

```
✅ Redis connection established
```

Redis yoksa şunu görürsünüz (sorun değil):

```
⚠️ Redis connection failed: ... Cache will be disabled.
```

---

## 🔧 Backend .env Ayarları

Redis kurduktan sonra, `backend/.env` dosyasına şunu ekleyin:

```env
REDIS_URL=redis://localhost:6379
```

Veya Docker kullanıyorsanız:

```env
REDIS_URL=redis://redis:6379
```

---

## 📊 Redis Ne İşe Yarar Bu Projede?

### 1. Cache (Önbellek)
- Sık kullanılan API yanıtlarını hafızada tutar
- Veritabanına daha az sorgu atar
- **Performans artışı sağlar**

### 2. Rate Limiting
- Login endpoint'i: Dakikada maksimum 5 deneme
- Register endpoint'i: Saatte maksimum 3 kayıt
- API endpoint'leri: Dakikada maksimum 100 istek

Bu sayede:
- Brute force saldırılarını önler
- API'yi kötüye kullanımdan korur
- Sunucu kaynaklarını korur

---

## 💡 Öneri

**Geliştirme aşamasında:** Redis kurmanıza gerek yok, uygulama çalışır.

**Production'da:** Redis kurun, performans ve güvenlik için önemli.

---

## 🆘 Sorun Giderme

### Redis bağlantı hatası alıyorum

1. **Redis çalışıyor mu kontrol edin:**
   ```bash
   # Windows (Memurai)
   # Services'te "Memurai" servisinin çalıştığından emin olun
   
   # Docker
   docker ps | grep redis
   ```

2. **Port kontrolü:**
   - Redis varsayılan port: `6379`
   - Başka bir program bu portu kullanıyor olabilir

3. **Backend'i yeniden başlatın:**
   - Redis'i kurduktan sonra backend'i durdurup tekrar başlatın

---

## 📝 Özet

- ✅ Redis **opsiyonel**, uygulama onsuz da çalışır
- ✅ Cache ve rate limiting için kullanılır
- ✅ **Production'da önerilir**, geliştirmede gerekmez
- ✅ En kolay yöntem: **Docker** (`docker-compose up -d redis`)

Herhangi bir sorunuz varsa çekinmeyin! 🚀





