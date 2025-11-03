# 🏆 Royal Koltuk Yıkama - Randevu ve Gelir Yönetim Sistemi

Modern web teknolojileri kullanılarak geliştirilmiş, profesyonel koltuk yıkama işletmeleri için tam kapsamlı randevu ve gelir takip sistemi.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![React](https://img.shields.io/badge/react-19.0-blue)
![MongoDB](https://img.shields.io/badge/mongodb-7.0-green)

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Teknoloji Stack](#-teknoloji-stack)
- [Hızlı Başlangıç](#-hızlı-başlangıç)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [Docker ile Çalıştırma](#-docker-ile-çalıştırma)
- [Geliştirme](#-geliştirme)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)

---

## ✨ Özellikler

### 🎯 Ana Özellikler

- ✅ **Randevu Yönetimi**: Oluştur, düzenle, sil, iptal et
- ✅ **Müşteri Takibi**: Detaylı müşteri geçmişi ve istatistikleri
- ✅ **Hizmet Yönetimi**: Hizmet türleri ve dinamik fiyatlandırma
- ✅ **Kasa ve Gelir**: Günlük, haftalık, aylık gelir takibi
- ✅ **Dashboard**: Görsel istatistikler ve özet bilgiler
- ✅ **SMS Bildirimleri**: Otomatik randevu bildirimleri (İletimerkezi)
- ✅ **Excel İçe Aktarma**: Toplu veri yükleme
- ✅ **Çalışma Saatleri**: Esnek çalışma saatleri yapılandırması
- ✅ **Güvenlik**: JWT authentication ve rate limiting
- ✅ **Dark Mode**: Koyu/açık tema desteği
- ✅ **Responsive**: Mobil ve desktop uyumlu

### 🚀 Gelişmiş Özellikler

- ⚡ **Redis Cache**: Performans optimizasyonu
- 🔒 **Rate Limiting**: API güvenliği
- 📊 **Real-time Updates**: Anlık güncellemeler
- 🌙 **Dark Mode**: Göz dostu tema
- 📱 **PWA Ready**: Progressive Web App desteği

---

## 🛠 Teknoloji Stack

### Backend
- **Framework**: FastAPI 0.110.1
- **Database**: MongoDB 7.0 (Motor async)
- **Authentication**: JWT + OAuth2
- **Cache**: Redis 7.0
- **Security**: bcrypt, slowapi
- **SMS**: İletimerkezi API

### Frontend
- **Framework**: React 19.0
- **Routing**: React Router DOM 7.5
- **Styling**: Tailwind CSS 3.4
- **UI Components**: Shadcn/UI + Radix UI
- **State Management**: Context API + Hooks
- **Charts**: Chart.js (isteğe bağlı)
- **Forms**: React Hook Form + Zod

### DevOps & Tools
- **Containerization**: Docker + Docker Compose
- **Build Tools**: CRACO
- **Code Quality**: ESLint, Black, Flake8
- **Testing**: Pytest, Vitest

---

## 🚀 Hızlı Başlangıç

### Docker ile Çalıştırma (Önerilen)

En kolay kurulum yöntemi:

```bash
# Projeyi klonla
git clone https://github.com/yourusername/royal-koltuk-yikama.git
cd royal-koltuk-yikama

# Environment dosyasını oluştur
cp .env.example .env
# .env dosyasını düzenle (API anahtarlarını ekle)

# Docker ile başlat
docker-compose up -d

# Backend: http://localhost:8001
# Frontend: http://localhost:3000
# MongoDB: localhost:27017
# Redis: localhost:6379
```

---

## 📦 Kurulum

### Gereksinimler

- Python 3.11+
- Node.js 18+
- MongoDB 7.0+
- Redis 7.0+ (opsiyonel ama önerilir)
- Yarn veya npm

### Backend Kurulumu

```bash
# Backend dizinine geç
cd backend

# Virtual environment oluştur
python -m venv venv

# Virtual environment'ı aktifleştir
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Dependencies yükle
pip install -r requirements.txt

# Environment variables ayarla
cp .env.example .env
# .env dosyasını düzenle

# Sunucuyu başlat
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Kurulumu

```bash
# Frontend dizinine geç
cd frontend

# Dependencies yükle
yarn install
# veya
npm install

# Environment variables ayarla
cp .env.example .env
# .env dosyasını düzenle

# Sunucuyu başlat
yarn start
# veya
npm start
```

### MongoDB Kurulumu

#### Yerel Kurulum

```bash
# macOS (Homebrew)
brew install mongodb-community
brew services start mongodb-community

# Ubuntu
sudo apt-get install mongodb
sudo systemctl start mongodb
```

#### Cloud Kurulum (MongoDB Atlas)

1. [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) hesabı oluştur
2. Cluster oluştur
3. Connection string'i al
4. `.env` dosyasına ekle:

```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/royal_koltuk
```

### Redis Kurulumu (Opsiyonel)

#### Yerel Kurulum

```bash
# macOS (Homebrew)
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis
```

#### Docker ile

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

---

## ⚙️ Konfigürasyon

### Backend Environment Variables

`backend/.env` dosyası:

```env
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=royal_koltuk

# Security
JWT_SECRET_KEY=your_super_secret_jwt_key_change_this

# SMS (İletimerkezi)
ILETIMERKEZI_API_KEY=your_api_key
ILETIMERKEZI_HASH=your_hash
ILETIMERKEZI_SENDER=FatihSenyuz

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Redis (Opsiyonel)
REDIS_URL=redis://localhost:6379

# Rate Limiting
RATE_LIMIT_ENABLED=true
```

### Frontend Environment Variables

`frontend/.env` dosyası:

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 📚 Kullanım

### İlk Kullanıcı Oluşturma

Backend'de kayıt olmak için:

```bash
curl -X POST http://localhost:8001/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password",
    "full_name": "Admin User"
  }'
```

### Giriş Yapma

```bash
curl -X POST http://localhost:8001/api/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password"
```

### API Kullanımı

1. Token al (`/api/token`)
2. Headers'a ekle: `Authorization: Bearer <token>`
3. API istekleri gönder

```bash
# Randevuları listele
curl -X GET http://localhost:8001/api/appointments \
  -H "Authorization: Bearer YOUR_TOKEN"

# Yeni randevu oluştur
curl -X POST http://localhost:8001/api/appointments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Ahmet Yılmaz",
    "phone": "05551234567",
    "address": "İstanbul",
    "service_id": "service_id_here",
    "appointment_date": "2025-01-28",
    "appointment_time": "10:00",
    "notes": "Not"
  }'
```

---

## 📖 API Dokümantasyonu

FastAPI otomatik olarak Swagger UI ve ReDoc sağlar:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI Schema**: http://localhost:8001/openapi.json

### Ana Endpoint'ler

| Endpoint | Method | Açıklama | Auth |
|----------|--------|----------|------|
| `/api/register` | POST | Kullanıcı kaydı | ❌ |
| `/api/token` | POST | Giriş yap | ❌ |
| `/api/services` | GET/POST | Hizmet yönetimi | ✅ |
| `/api/appointments` | GET/POST | Randevu yönetimi | ✅ |
| `/api/transactions` | GET | Kasa işlemleri | ✅ |
| `/api/stats/dashboard` | GET | Dashboard istatistikleri | ✅ |
| `/api/settings` | GET/PUT | Ayarlar | ✅ |

---

## 🐳 Docker ile Çalıştırma

### Tüm Servisleri Başlat

```bash
# Build ve start
docker-compose up -d

# Logları görüntüle
docker-compose logs -f

# Durdur
docker-compose down

# Volumes ile birlikte sil (VERİTABANI UYARISI!)
docker-compose down -v
```

### Tekil Servisleri Başlat

```bash
# Sadece backend
docker-compose up -d backend

# Sadece frontend
docker-compose up -d frontend

# Sadece MongoDB
docker-compose up -d mongodb
```

### Docker Compose Servisleri

- **backend**: FastAPI uygulaması (Port 8001)
- **frontend**: React uygulaması (Port 3000)
- **mongodb**: Veritabanı (Port 27017)
- **redis**: Cache (Port 6379)

---

## 🔧 Geliştirme

### Backend Geliştirme

```bash
cd backend

# Sanal ortamı aktifleştir
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Kod kalitesi
black server.py cache.py rate_limit.py
flake8 . --exclude venv
isort . --skip venv

# Test çalıştır
pytest tests/
```

### Frontend Geliştirme

```bash
cd frontend

# Development server
yarn start

# Production build
yarn build

# Test
yarn test

# Lint
yarn lint
```

### VSCode Tasks

VSCode tasks kullanımı için `.vscode/tasks.json` dosyası mevcuttur:

- **Start Backend**: Backend'i başlat
- **Start Frontend**: Frontend'i başlat
- **Start Both**: Her ikisini birden başlat

---

## 🧪 Test

### Backend Testleri

```bash
cd backend
pytest tests/ -v --cov=. --cov-report=html
```

### Frontend Testleri

```bash
cd frontend
yarn test --coverage
```

---

## 📊 Proje Yapısı

```
royal-koltuk-yikama/
├── backend/
│   ├── server.py              # Ana uygulama
│   ├── cache.py               # Redis cache helper
│   ├── rate_limit.py          # Rate limiting
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.js             # Ana komponent
│   │   ├── index.js           # Entry point
│   │   ├── api/
│   │   │   └── api.js         # API client
│   │   ├── context/
│   │   │   ├── AuthContext.js # Auth context
│   │   │   └── ThemeContext.js# Theme context
│   │   ├── components/
│   │   │   ├── Dashboard.js
│   │   │   ├── AppointmentForm.js
│   │   │   ├── ServiceManagement.js
│   │   │   ├── CashRegister.js
│   │   │   ├── Customers.js
│   │   │   ├── Settings.js
│   │   │   ├── ImportData.js
│   │   │   ├── LoginPage.js
│   │   │   └── ui/            # Shadcn UI components
│   │   └── lib/
│   │       └── utils.js
│   ├── package.json
│   └── .env
│
├── docker-compose.yml         # Docker configuration
├── Dockerfile.backend         # Backend Dockerfile
├── Dockerfile.frontend        # Frontend Dockerfile
├── .dockerignore
├── README.md
└── PROJE_ANALİZ_RAPORU.md    # Detaylı analiz raporu
```

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları takip edin:

1. Fork yap
2. Feature branch oluştur (`git checkout -b feature/amazing-feature`)
3. Commit yap (`git commit -m 'Add amazing feature'`)
4. Push yap (`git push origin feature/amazing-feature`)
5. Pull Request aç

### Kod Standartları

- Python: Black formatter + Flake8 linter
- JavaScript: ESLint + Prettier
- Commit mesajları: Conventional Commits
- Branch naming: `feature/`, `bugfix/`, `hotfix/`

---

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

---

## 👥 Ekip

- **Geliştirici**: [Your Name]
- **Email**: your.email@example.com
- **GitHub**: [@yourusername](https://github.com/yourusername)

---

## 🙏 Teşekkürler

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - UI kütüphanesi
- [Shadcn/UI](https://ui.shadcn.com/) - UI component library
- [MongoDB](https://www.mongodb.com/) - Veritabanı
- [İletimerkezi](https://www.iletimerkezi.com/) - SMS servisi

---

## 📞 Destek

Sorularınız için:
- 📧 Email: support@royalkoltuk.com
- 💬 Issues: [GitHub Issues](https://github.com/yourusername/royal-koltuk-yikama/issues)
- 📖 Dokümantasyon: [Wiki](https://github.com/yourusername/royal-koltuk-yikama/wiki)

---

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!**

![Stars](https://img.shields.io/github/stars/yourusername/royal-koltuk-yikama?style=social)

