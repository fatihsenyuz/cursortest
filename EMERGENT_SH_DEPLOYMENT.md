# 🚀 Emergent.sh Deployment Rehberi

## ✅ Deployment Öncesi Kontrol Listesi

### 1. **Environment Variables (Kritik!)**

Backend için gerekli environment variables'ları Emergent.sh'de ayarlayın:

```env
# Database (MongoDB Atlas kullanın - production için)
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/royal_koltuk
DB_NAME=royal_koltuk

# Security (ÇOK ÖNEMLİ - Güçlü bir key kullanın!)
JWT_SECRET_KEY=your_super_secret_production_key_change_this_immediately

# SMS (İletimerkezi)
ILETIMERKEZI_API_KEY=your_api_key
ILETIMERKEZI_HASH=your_hash
ILETIMERKEZI_SENDER=FatihSenyuz
SUPPORT_PHONE=0545 595 3250
FEEDBACK_URL=https://bit.ly/royalyorum
COMPANY_SIGNATURE=Royal Premium Care – Nevşehir
SMS_ENABLED=true # SMS geçici olarak kapatmak için false yapın

# CORS (Frontend URL'inizi ekleyin)
CORS_ORIGINS=https://your-frontend-domain.emergent.sh,https://your-custom-domain.com

# Redis (Opsiyonel - Production'da önerilir)
REDIS_URL=redis://your-redis-host:6379

# Rate Limiting
RATE_LIMIT_ENABLED=true
```

Frontend için:
```env
REACT_APP_BACKEND_URL=https://your-backend-url.emergent.sh
# veya production backend URL'iniz
```

---

## 📋 Deployment Adımları

### Adım 1: MongoDB Atlas Kurulumu (Önerilir)

1. [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) hesabı oluşturun
2. Free tier cluster oluşturun
3. Database User oluşturun
4. Network Access'te IP adresinizi ekleyin (veya `0.0.0.0/0` - tüm IP'ler için)
5. Connection string'i alın:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/royal_koltuk
   ```

### Adım 2: Backend Deployment

1. **Emergent.sh'de backend servisini oluşturun:**
   - Python 3.11+ seçin
   - Port: `8001`
   - Build Command: (boş bırakabilirsiniz, Dockerfile kullanıyorsanız)
   - Start Command: `uvicorn server:app --host 0.0.0.0 --port 8001`

2. **Environment Variables ekleyin:**
   - Yukarıdaki tüm backend environment variables'ları ekleyin

3. **Build ayarları:**
   - Dockerfile kullanıyorsanız: `Dockerfile.backend` kullanın
   - Veya direkt Python environment: `requirements.txt` yüklenecek

### Adım 3: Frontend Deployment

1. **Emergent.sh'de frontend servisini oluşturun:**
   - Node.js 18+ seçin
   - Port: `3000`
   - Build Command: `yarn build` (production build)
   - Start Command: `yarn start` (veya `serve -s build` - statik dosya serve için)

2. **Environment Variables:**
   ```env
   REACT_APP_BACKEND_URL=https://your-backend-url.emergent.sh
   ```

3. **Build ayarları:**
   - `package.json` dosyanızda `build` script'i var
   - Production build otomatik oluşturulacak

### Adım 4: Redis (Opsiyonel)

1. **Emergent.sh Redis servisi ekleyin** (varsa)
2. Veya **Redis Cloud** gibi bir servis kullanın
3. Redis URL'ini backend environment variables'a ekleyin

---

## ⚠️ Kritik Dikkat Edilmesi Gerekenler

### 1. **CORS Ayarları**
Backend'deki `CORS_ORIGINS` environment variable'ına **tam frontend URL'inizi** ekleyin:
```env
CORS_ORIGINS=https://your-app.emergent.sh
```

### 2. **Frontend Backend URL**
Frontend'deki `REACT_APP_BACKEND_URL` environment variable'ına **tam backend URL'inizi** ekleyin:
```env
REACT_APP_BACKEND_URL=https://your-backend.emergent.sh
```

### 3. **JWT Secret Key**
**Kesinlikle değiştirin!** Production'da güçlü bir secret key kullanın:
```bash
# Güçlü bir key oluşturmak için (Linux/Mac)
openssl rand -hex 32

# Veya online: https://randomkeygen.com/
```

### 4. **MongoDB Bağlantısı**
- Production'da **MongoDB Atlas** kullanın (yerel MongoDB değil)
- Connection string'in doğru olduğundan emin olun
- IP whitelist'i ayarlayın

### 5. **Build ve Start Komutları**

Backend:
```bash
# Dockerfile kullanıyorsanız
# (Emergent.sh otomatik Dockerfile'ı kullanacak)

# Veya direkt Python
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001
```

Frontend:
```bash
yarn install
yarn build
# Statik dosya serve için:
npx serve -s build -l 3000
# Veya:
yarn start
```

---

## 🔄 Güncelleme İşlemi (Sizin Durumunuz)

Mevcut deployment'ı güncellemek için:

1. **Kodları Emergent.sh'e push edin**
   - Git repository'nizi güncelleyin
   - Emergent.sh otomatik olarak yeni commit'leri algılayacak

2. **Environment Variables kontrolü**
   - Eski environment variables'larınızı kontrol edin
   - Gerekirse yeni değişkenler ekleyin

3. **Redeploy**
   - Emergent.sh dashboard'undan "Redeploy" butonuna tıklayın
   - Veya yeni commit otomatik deploy tetikleyecek

---

## ✅ Deployment Sonrası Kontrol

1. **Backend sağlık kontrolü:**
   ```
   https://your-backend.emergent.sh/docs
   ```
   Swagger UI açılıyorsa backend çalışıyor demektir.

2. **Frontend kontrolü:**
   ```
   https://your-frontend.emergent.sh
   ```
   Sayfa açılıyorsa frontend çalışıyor demektir.

3. **API bağlantısı:**
   - Frontend'den backend'e bağlantı çalışıyor mu?
   - Browser console'da hata var mı?
   - Network tab'ında API istekleri başarılı mı?

4. **İlk kullanıcı oluşturma:**
   ```bash
   curl -X POST https://your-backend.emergent.sh/api/register \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "password": "your_secure_password",
       "full_name": "Admin User"
     }'
   ```

---

## 🐛 Olası Sorunlar ve Çözümleri

### Sorun 1: CORS Hatası
**Belirtiler:** Browser console'da CORS hatası  
**Çözüm:** Backend'deki `CORS_ORIGINS` environment variable'ına frontend URL'inizi ekleyin

### Sorun 2: Backend'e Bağlanılamıyor
**Belirtiler:** Network tab'ında connection refused  
**Çözüm:** 
- Frontend'deki `REACT_APP_BACKEND_URL` doğru mu kontrol edin
- Backend'in çalıştığından emin olun
- Port ayarlarını kontrol edin

### Sorun 3: MongoDB Bağlantı Hatası
**Belirtiler:** Backend loglarında MongoDB connection error  
**Çözüm:**
- MongoDB Atlas'te IP whitelist kontrolü
- Connection string'in doğru olduğundan emin olun
- Database user'ın doğru izinleri olduğundan emin olun

### Sorun 4: Redis Bağlantı Hatası
**Belirtiler:** Backend loglarında Redis connection failed  
**Çözüm:** 
- Redis opsiyonel, uygulama çalışmaya devam eder
- Sadece cache devre dışı kalır
- Production'da Redis kurmanızı öneririz

### Sorun 5: Build Hataları
**Belirtiler:** Deployment sırasında build hatası  
**Çözüm:**
- Node.js ve Python versiyonlarını kontrol edin
- `requirements.txt` ve `package.json` dosyalarını kontrol edin
- Build loglarını inceleyin

---

## 📝 Production Checklist

Deployment öncesi kontrol listesi:

- [ ] MongoDB Atlas kuruldu ve connection string alındı
- [ ] JWT_SECRET_KEY güçlü bir değerle değiştirildi
- [ ] CORS_ORIGINS production frontend URL'ini içeriyor
- [ ] REACT_APP_BACKEND_URL production backend URL'ini içeriyor
- [ ] İletimerkezi API bilgileri doğru
- [ ] Redis URL'i ayarlandı (opsiyonel ama önerilir)
- [ ] Backend build başarılı
- [ ] Frontend build başarılı
- [ ] İlk kullanıcı oluşturuldu
- [ ] Test girişi yapıldı
- [ ] SMS gönderimi test edildi (opsiyonel)

---

## 🎯 Özet

### Emergent.sh'de Deploy İçin Gerekenler:

1. **Backend:**
   - Python 3.11+ environment
   - Environment variables ayarlanmalı
   - Port: 8001
   - Start command: `uvicorn server:app --host 0.0.0.0 --port 8001`

2. **Frontend:**
   - Node.js 18+ environment
   - Environment variables ayarlanmalı
   - Port: 3000
   - Build command: `yarn build`
   - Start command: `yarn start` veya `serve -s build`

3. **Database:**
   - MongoDB Atlas (cloud) kullanın
   - Connection string'i backend environment variables'a ekleyin

4. **Redis:**
   - Opsiyonel ama production'da önerilir
   - Redis URL'i backend environment variables'a ekleyin

---

## 💡 İpuçları

1. **Environment Variables:** Emergent.sh dashboard'undan environment variables'ları kolayca yönetebilirsiniz

2. **Logs:** Deployment sırasında logları takip edin, hataları erken yakalayın

3. **Rollback:** Sorun olursa önceki deployment'a geri dönebilirsiniz

4. **Monitoring:** Production'da monitoring ekleyin (error tracking, performance monitoring)

---

**Başarılar! 🚀**

Sorularınız varsa çekinmeyin!

