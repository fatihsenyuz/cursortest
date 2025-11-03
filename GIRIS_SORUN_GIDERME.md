# 🔐 Giriş Sorunu Giderme Kılavuzu

Eğer giriş yaparken "kullanıcı adı veya şifre kabul edilmedi" hatası alıyorsanız, aşağıdaki adımları takip edin.

## ✅ Adım 1: Backend'in Çalıştığından Emin Olun

Backend sunucusunun çalışıyor olduğundan emin olun:

```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Backend'in çalıştığını kontrol etmek için tarayıcınızda şu adresi açın:
- http://localhost:8001/docs (FastAPI Swagger dokümantasyonu)

## ✅ Adım 2: Veritabanında Kullanıcı Oluşturun

**ÖNEMLİ:** İlk kullanıcıyı oluşturmak için `create_user.py` scriptini kullanın:

### Yöntem 1: Python Script Kullanarak (Önerilen)

```bash
cd backend
python create_user.py
```

Script sizden şunları isteyecek:
- Kullanıcı adı (varsayılan: admin)
- Şifre
- Tam ad (opsiyonel)

### Yöntem 2: curl ile API'yi Kullanarak

```bash
curl -X POST http://localhost:8001/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "sifreniz",
    "full_name": "Admin User"
  }'
```

### Yöntem 3: MongoDB'ye Doğrudan Ekleme (Gelişmiş)

MongoDB shell veya MongoDB Compass kullanarak:

```javascript
use royal_koltuk

db.users.insertOne({
  username: "admin",
  hashed_password: "$2b$12$...", // bcrypt hash (create_user.py scriptini kullanın)
  full_name: "Admin User"
})
```

## ✅ Adım 3: Environment Variables Kontrolü

### Backend (.env dosyası - backend/.env)

`backend/.env` dosyasının mevcut olduğundan ve şu değişkenleri içerdiğinden emin olun:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=royal_koltuk
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env dosyası - frontend/.env)

`frontend/.env` dosyasının mevcut olduğundan ve şu değişkeni içerdiğinden emin olun:

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Not:** Frontend'i yeniden başlatmanız gerekebilir (`yarn start` veya `npm start`)

## ✅ Adım 4: MongoDB Bağlantısını Kontrol Edin

MongoDB'nin çalışıyor olduğundan emin olun:

```bash
# MongoDB'nin çalışıp çalışmadığını kontrol edin
# Windows'ta:
# MongoDB servisinin çalıştığından emin olun

# Linux/Mac:
sudo systemctl status mongod
# veya
brew services list | grep mongodb
```

## ✅ Adım 5: Tarayıcı Konsolunu Kontrol Edin

1. Tarayıcınızda F12 tuşuna basın (Developer Tools)
2. Console sekmesine gidin
3. Giriş yapmayı deneyin
4. Hangi hata mesajını aldığınızı not edin

Olası hata mesajları:
- **"Backend sunucusuna bağlanılamıyor"** → Backend çalışmıyor veya URL yanlış
- **"Kullanıcı adı veya parola hatalı"** → Kullanıcı yok veya şifre yanlış
- **"REACT_APP_BACKEND_URL environment variable tanımlı değil"** → Frontend .env dosyası eksik

## ✅ Adım 6: Mevcut Kullanıcıları Kontrol Edin

MongoDB'de mevcut kullanıcıları görmek için:

```bash
cd backend
python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ.get('DB_NAME', 'royal_koltuk')]

async def list_users():
    users = await db.users.find({}, {'username': 1, 'full_name': 1, '_id': 0}).to_list(100)
    print('Mevcut kullanıcılar:')
    for user in users:
        print(f\"  - {user.get('username')} ({user.get('full_name', 'İsim yok')})\")
    if not users:
        print('  (Kullanıcı bulunamadı)')
    client.close()

asyncio.run(list_users())
"
```

## 🔄 Kullanıcı Şifresini Sıfırlama

Mevcut bir kullanıcının şifresini değiştirmek için:

```bash
cd backend
python create_user.py
```

Kullanıcı adını girdikten sonra, script zaten var olan bir kullanıcı olduğunu algılayacak ve şifresini güncellemek isteyip istemediğinizi soracaktır.

## 📝 Notlar

- Şifreler bcrypt ile hash'lenir ve veritabanında düz metin olarak saklanmaz
- JWT token'lar 24 saat geçerlidir
- Rate limiting aktif: Login için dakikada 5 deneme hakkı vardır
- Tüm hatalar artık daha açıklayıcı mesajlarla gösterilecektir

## 🆘 Hala Sorun mu Var?

1. Backend loglarını kontrol edin (terminal'de hata mesajları var mı?)
2. MongoDB loglarını kontrol edin
3. Network tab'ında (F12 → Network) API isteklerini inceleyin
4. Backend'in çalıştığı portu kontrol edin (varsayılan: 8001)
5. Frontend'in çalıştığı portu kontrol edin (varsayılan: 3000)





