from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import requests
from urllib.parse import quote
from zoneinfo import ZoneInfo
import re
import xml.etree.ElementTree as ET

# --- GÜVENLİK (SECURITY) İÇİN YENİ İMPORTLAR ---
from passlib.context import CryptContext
from jose import JWTError, jwt

# --- REDIS CACHE VE RATE LIMITİNG ---
from cache import init_redis, invalidate_cache
from rate_limit import limiter, rate_limit, LIMITS
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# --- GÜVENLİK AYARLARI ---
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default_karmaşık_bir_secret_key_ekleyin_mutlaka') 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 gün geçerli token
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

# --- ROOT DİZİN VE .ENV YÜKLEME ---
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
if not mongo_url:
    raise ValueError("MONGO_URL environment variable is required!")
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'royal_koltuk')]

# İletimerkezi SMS API Configuration
ILETIMERKEZI_API_KEY = os.environ.get('ILETIMERKEZI_API_KEY')
ILETIMERKEZI_HASH = os.environ.get('ILETIMERKEZI_HASH')
ILETIMERKEZI_SENDER = os.environ.get('ILETIMERKEZI_SENDER', 'FatihSenyuz')

# SMS Content Configuration
SUPPORT_PHONE = os.environ.get('SUPPORT_PHONE', '0545 595 3250')
FEEDBACK_URL = os.environ.get('FEEDBACK_URL', 'https://bit.ly/royalyorum')
COMPANY_SIGNATURE = os.environ.get('COMPANY_SIGNATURE', 'Royal Premium Care – Nevşehir')
SMS_ENABLED = os.environ.get('SMS_ENABLED', 'true').lower() in ('1', 'true', 'yes')

# Create the main app without a prefix
app = FastAPI(
    title="Royal Koltuk Yıkama API",
    description="""
    ## 🏆 Royal Koltuk Yıkama API Dokümantasyonu
    
    Koltuk yıkama işletmeleri için tam kapsamlı randevu ve gelir yönetim sistemi API'si.
    
    ### Özellikler:
    
    * **📅 Randevu Yönetimi**: Oluştur, düzenle, sil, iptal et
    * **👥 Müşteri Takibi**: Müşteri geçmişi ve istatistikleri
    * **💼 Hizmet Yönetimi**: Hizmet türleri ve fiyatları
    * **💰 Kasa ve Gelir**: Gelir takibi ve raporlama
    * **📧 SMS Bildirimleri**: Otomatik SMS gönderimi
    * **📊 Dashboard İstatistikleri**: Günlük, haftalık, aylık istatistikler
    
    ### Kimlik Doğrulama:
    
    API'ye erişim için JWT token kullanılmaktadır. 
    
    1. `/api/token` endpoint'inden token alın
    2. Headers'a `Authorization: Bearer <token>` ekleyin
    3. Token süresi: 24 saat
    
    ### Rate Limiting:
    
    * Login: 5 istek/dakika
    * Register: 3 istek/saat
    * Genel API: 100 istek/dakika
    
    ### WebSocket Desteği:
    
    Real-time güncellemeler için WebSocket desteği yakında eklenecek.
    """,
    version="1.0.0",
    contact={
        "name": "Royal Koltuk Yıkama",
        "url": "https://royalkoltuk.com",
    },
    license_info={
        "name": "MIT License",
    },
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize Redis cache
init_redis()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# === YENİ GÜVENLİK YARDIMCI FONKSİYONLARI ===

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_from_db(username: str):
    user = await db.users.find_one({"username": username})
    if user:
        return UserInDB(**user)
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_from_db(username)
    if user is None:
        raise credentials_exception
    return user

# === GÜVENLİK YARDIMCI FONKSİYONLARI SONU ===


# SMS Helper Function (Değişiklik yok)
def send_sms(to_phone: str, message: str):
    try:
        if not SMS_ENABLED:
            logging.info("SMS sending is disabled via SMS_ENABLED env. Skipping.")
            return True

        clean_phone = re.sub(r'\D', '', to_phone)
        if clean_phone.startswith('90'): clean_phone = clean_phone[2:]
        if clean_phone.startswith('0'): clean_phone = clean_phone[1:]
        if not clean_phone.startswith('5') or len(clean_phone) != 10:
            logging.error(f"Invalid Turkish phone number format: {to_phone} -> {clean_phone}")
            return False
        
        # Sanitize and cap message length to avoid URL length or provider issues
        sanitized = re.sub(r"\s+", " ", message).strip()
        MAX_LEN = 480  # conservative multi-part SMS cap
        if len(sanitized) > MAX_LEN:
            sanitized = sanitized[:MAX_LEN]

        api_url = "https://api.iletimerkezi.com/v1/send-sms/get/"
        params = {
            'key': ILETIMERKEZI_API_KEY, 'hash': ILETIMERKEZI_HASH, 'text': sanitized,
            'receipents': clean_phone, 'sender': ILETIMERKEZI_SENDER,
            'iys': '1', 'iysList': 'BIREYSEL'
        }
        response = requests.get(api_url, params=params, timeout=10)
        
        try:
            root = ET.fromstring(response.text)
            status_code = root.find('.//status/code').text
            status_message = root.find('.//status/message').text
            
            if status_code == '200':
                logging.info(f"SMS sent successfully to {clean_phone}.")
                return True
            else:
                logging.error(f"SMS failed to {clean_phone}. Code: {status_code}, Message: {status_message}")
                return False
        except ET.ParseError as e:
            logging.error(f"Failed to parse İletimerkezi response (status={response.status_code}): {response.text} | Error: {str(e)}")
            return False
    except Exception as e:
        logging.error(f"Failed to send SMS to {to_phone}: {str(e)}")
        return False


# === VERİ MODELLERİ ===

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    
class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class Service(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ServiceCreate(BaseModel):
    name: str
    price: float

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

class Appointment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_name: str
    phone: str
    address: str
    service_id: str
    service_name: str
    service_price: float
    appointment_date: str
    appointment_time: str
    notes: str = ""
    status: str = "Bekliyor"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[str] = None

class AppointmentCreate(BaseModel):
    customer_name: str
    phone: str
    address: str
    service_id: str
    appointment_date: str
    appointment_time: str
    notes: str = ""

class AppointmentUpdate(BaseModel):
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    service_id: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class Transaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    appointment_id: str
    customer_name: str
    service_name: str
    amount: float
    date: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TransactionUpdate(BaseModel):
    amount: float

class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "app_settings"
    work_start_hour: int = 7
    work_end_hour: int = 3
    appointment_interval: int = 30

# === GÜVENLİK API ENDPOINT'LERİ ===

@api_router.post("/register", response_model=User)
@rate_limit(LIMITS['register'])
async def register_user(request: Request, user_in: UserCreate):
    existing_user = await get_user_from_db(user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already registered.",
        )
    
    hashed_password = get_password_hash(user_in.password)
    user_db = UserInDB(
        username=user_in.username,
        hashed_password=hashed_password,
        full_name=user_in.full_name
    )
    
    await db.users.insert_one(user_db.model_dump())
    
    return User(username=user_db.username, full_name=user_db.full_name)

@api_router.post("/token", response_model=Token)
@rate_limit(LIMITS['login'])
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_from_db(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# === KORUMALI API ENDPOINT'LERİ ===

# Services Routes
@api_router.post("/services", response_model=Service)
async def create_service(service: ServiceCreate, current_user: User = Depends(get_current_user)):
    service_obj = Service(**service.model_dump())
    doc = service_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.services.insert_one(doc)
    return service_obj

@api_router.get("/services", response_model=List[Service])
async def get_services(current_user: User = Depends(get_current_user)):
    services = await db.services.find({}, {"_id": 0}).to_list(1000)
    for service in services:
        if isinstance(service['created_at'], str):
            service['created_at'] = datetime.fromisoformat(service['created_at'])
    return services

@api_router.get("/services/{service_id}", response_model=Service)
async def get_service(service_id: str, current_user: User = Depends(get_current_user)):
    service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Hizmet bulunamadı")
    if isinstance(service['created_at'], str):
        service['created_at'] = datetime.fromisoformat(service['created_at'])
    return service

@api_router.put("/services/{service_id}", response_model=Service)
async def update_service(service_id: str, service_update: ServiceUpdate, current_user: User = Depends(get_current_user)):
    service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Hizmet bulunamadı")
    
    update_data = {k: v for k, v in service_update.model_dump().items() if v is not None}
    if update_data:
        await db.services.update_one({"id": service_id}, {"$set": update_data})
    
    updated_service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if isinstance(updated_service['created_at'], str):
        updated_service['created_at'] = datetime.fromisoformat(updated_service['created_at'])
    return updated_service

@api_router.delete("/services/{service_id}")
async def delete_service(service_id: str, current_user: User = Depends(get_current_user)):
    result = await db.services.delete_one({"id": service_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Hizmet bulunamadı")
    return {"message": "Hizmet silindi"}


# Appointments Routes
@api_router.post("/appointments", response_model=Appointment)
async def create_appointment(appointment: AppointmentCreate, current_user: User = Depends(get_current_user)):
    service = await db.services.find_one({"id": appointment.service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Hizmet bulunamadı")
    
    existing = await db.appointments.find_one({
        "appointment_date": appointment.appointment_date,
        "appointment_time": appointment.appointment_time,
        "status": {"$ne": "İptal"}
    })
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"{appointment.appointment_date} tarihinde {appointment.appointment_time} saatinde zaten bir randevu var. Lütfen başka bir saat seçin."
        )
    
    appointment_data = appointment.model_dump()
    appointment_data['service_name'] = service['name']
    appointment_data['service_price'] = service['price']
    
    try:
        turkey_tz = ZoneInfo("Europe/Istanbul")
        now = datetime.now(turkey_tz)
        dt_str = f"{appointment.appointment_date} {appointment.appointment_time}"
        naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        appointment_dt = naive_dt.replace(tzinfo=turkey_tz)
        completion_threshold = appointment_dt + timedelta(hours=1)
        
        if now >= completion_threshold:
            appointment_data['status'] = 'Tamamlandı'
            appointment_data['completed_at'] = datetime.now(timezone.utc).isoformat()
        else:
            appointment_data['status'] = 'Bekliyor'
            
    except (ValueError, TypeError) as e:
        logging.warning(f"Randevu durumu ayarlanırken tarih hatası: {e}")
        appointment_data['status'] = 'Bekliyor'
    
    appointment_obj = Appointment(**appointment_data)
    doc = appointment_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.appointments.insert_one(doc)
    
    if appointment_obj.status == 'Tamamlandı':
        transaction = Transaction(
            appointment_id=appointment_obj.id, customer_name=appointment_obj.customer_name,
            service_name=appointment_obj.service_name, amount=appointment_obj.service_price,
            date=appointment_obj.appointment_date
        )
        trans_doc = transaction.model_dump()
        trans_doc['created_at'] = trans_doc['created_at'].isoformat()
        await db.transactions.insert_one(trans_doc)

    # === SADECE YENİ RANDEVU SMS'İ (Oluşturma / Onay) ===
    sms_message = (
        f"Sayın {appointment.customer_name},\n\n"
        f"Royal Koltuk Yıkama hizmet randevunuz onaylanmıştır.\n\n"
        f"Tarih: {appointment.appointment_date}\n"
        f"Saat: {appointment.appointment_time}\n\n"
        f"Profesyonel ekibimiz belirtilen adreste zamanında hizmet verecektir.\n\n"
        f"Tüm işlemler hijyen ve müşteri memnuniyeti standartlarına uygun olarak yürütülecektir.\n\n"
        f"Bilgi veya değişiklik için: {SUPPORT_PHONE}\n\n"
        f"— {COMPANY_SIGNATURE}"
    )
    send_sms(appointment.phone, sms_message)
    
    return appointment_obj

@api_router.get("/appointments", response_model=List[Appointment])
async def get_appointments(
    date: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    query = {}
    if date: query['appointment_date'] = date
    if status: query['status'] = status
    if search:
        query['$or'] = [
            {'customer_name': {'$regex': search, '$options': 'i'}},
            {'phone': {'$regex': search, '$options': 'i'}}
        ]
    
    appointments_from_db = await db.appointments.find(query, {"_id": 0}).sort("appointment_date", -1).to_list(1000)
    
    try:
        turkey_tz = ZoneInfo("Europe/Istanbul")
        now = datetime.now(turkey_tz)
    except Exception:
        turkey_tz = timezone(timedelta(hours=3))
        now = datetime.now(turkey_tz)

    ids_to_update = [] 
    transactions_to_create = [] 

    for appt in appointments_from_db:
        if isinstance(appt.get('created_at'), str):
            appt['created_at'] = datetime.fromisoformat(appt['created_at'])

        if appt.get('status') == 'Bekliyor':
            try:
                dt_str = f"{appt['appointment_date']} {appt['appointment_time']}"
                naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                appointment_dt = naive_dt.replace(tzinfo=turkey_tz)
                completion_threshold = appointment_dt + timedelta(hours=1)
                
                if now >= completion_threshold:
                    appt['status'] = 'Tamamlandı'
                    completed_at_iso = datetime.now(timezone.utc).isoformat()
                    appt['completed_at'] = completed_at_iso
                    ids_to_update.append(appt['id'])
                    
                    transaction = Transaction(
                        appointment_id=appt['id'], customer_name=appt['customer_name'],
                        service_name=appt['service_name'], amount=appt['service_price'],
                        date=appt['appointment_date']
                    )
                    trans_doc = transaction.model_dump()
                    trans_doc['created_at'] = trans_doc['created_at'].isoformat()
                    transactions_to_create.append(trans_doc)
            
            except (ValueError, TypeError) as e:
                logging.warning(f"Randevu {appt['id']} için tarih ayrıştırılamadı: {e}")

    if ids_to_update:
        await db.appointments.update_many(
            {"id": {"$in": ids_to_update}},
            {"$set": {
                "status": "Tamamlandı",
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    
    if transactions_to_create:
        # Otomatik tamamlamada SMS göndermiyoruz (müşteriyi rahatsız etmemek için)
        # Sadece Kasa (Transaction) kaydı oluşturuyoruz
        await db.transactions.insert_many(transactions_to_create)
    
    return appointments_from_db

@api_router.get("/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str, current_user: User = Depends(get_current_user)):
    appointment = await db.appointments.find_one({"id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")
    if isinstance(appointment['created_at'], str):
        appointment['created_at'] = datetime.fromisoformat(appointment['created_at'])
    return appointment

# === === === === === === === === === === === ===
# === İŞTE DÜZELTİLMİŞ FONKSİYON (SMS'li) ===
# === === === === === === === === === === === ===
@api_router.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: str, appointment_update: AppointmentUpdate, current_user: User = Depends(get_current_user)):
    appointment = await db.appointments.find_one({"id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")
    
    update_data = {k: v for k, v in appointment_update.model_dump().items() if v is not None}
    
    # Check if date/time changed and if there's a conflict
    if 'appointment_date' in update_data or 'appointment_time' in update_data:
        check_date = update_data.get('appointment_date', appointment['appointment_date'])
        check_time = update_data.get('appointment_time', appointment['appointment_time'])
        
        existing = await db.appointments.find_one({
            "id": {"$ne": appointment_id},
            "appointment_date": check_date,
            "appointment_time": check_time,
            "status": {"$ne": "İptal"}
        })
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"{check_date} tarihinde {check_time} saatinde zaten bir randevu var. Lütfen başka bir saat seçin."
            )
    
    # If service_id changed, update service details
    if 'service_id' in update_data:
        service = await db.services.find_one({"id": update_data['service_id']}, {"_id": 0})
        if service:
            update_data['service_name'] = service['name']
            update_data['service_price'] = service['price']
    

    # === YENİ SMS ve İŞLEM (TRANSACTION) MANTIĞI ===
    
    new_status = update_data.get('status')
    old_status = appointment['status']
    
    # Durum "Tamamlandı" olarak değiştiyse
    if new_status == 'Tamamlandı' and old_status != 'Tamamlandı':
        update_data['completed_at'] = datetime.now(timezone.utc).isoformat()
        
        # İşlem (Kasa) oluştur
        transaction = Transaction(
            appointment_id=appointment_id,
            customer_name=appointment['customer_name'],
            service_name=appointment['service_name'],
            amount=appointment['service_price'],
            date=appointment['appointment_date']
        )
        trans_doc = transaction.model_dump()
        trans_doc['created_at'] = trans_doc['created_at'].isoformat()
        await db.transactions.insert_one(trans_doc)
        
        # Müşteriye SMS GÖNDER (Tamamlandı)
        try:
            sms_message = (
                f"Sayın {appointment['customer_name']},\n\n"
                f"Royal Koltuk Yıkama hizmetiniz başarıyla tamamlanmıştır.\n\n"
                f"Koltuk ve tekstil yüzeyleriniz yüksek ısıda buhar ve antibakteriyel ürünlerle profesyonel olarak temizlenmiştir.\n\n"
                f"Hizmet kalitemizi geliştirmek adına geri bildiriminiz bizim için değerlidir.\n\n"
                f"Görüş bildirmek için: {FEEDBACK_URL}\n\n"
                f"— {COMPANY_SIGNATURE}"
            )
            send_sms(appointment['phone'], sms_message)
        except Exception as e:
            logging.error(f"Tamamlandı SMS'i gönderilirken hata oluştu: {e}")

    # Durum "İptal" olarak değiştiyse
    elif new_status == 'İptal' and old_status != 'İptal':
        
        # Müşteriye SMS GÖNDER (İptal)
        try:
            sms_message = (
                f"Sayın {appointment['customer_name']},\n\n"
                f"Royal Koltuk Yıkama randevunuz talebiniz doğrultusunda iptal edilmiştir.\n\n"
                f"Yeni bir tarih planlamak veya bilgi almak için bizimle iletişime geçebilirsiniz.\n\n"
                f"Müşteri memnuniyetine verdiğimiz önem doğrultusunda her zaman hizmetinizdeyiz.\n\n"
                f"📞 İletişim: {SUPPORT_PHONE}\n\n"
                f"— {COMPANY_SIGNATURE}"
            )
            send_sms(appointment['phone'], sms_message)
        except Exception as e:
            logging.error(f"İptal SMS'i gönderilirken hata oluştu: {e}")
            
    # === YENİ SMS MANTIĞI SONU ===

    if update_data:
        await db.appointments.update_one({"id": appointment_id}, {"$set": update_data})
    
    updated_appointment = await db.appointments.find_one({"id": appointment_id}, {"_id": 0})
    if isinstance(updated_appointment['created_at'], str):
        updated_appointment['created_at'] = datetime.fromisoformat(updated_appointment['created_at'])
    return updated_appointment

@api_router.delete("/appointments/{appointment_id}")
async def delete_appointment(appointment_id: str, current_user: User = Depends(get_current_user)):
    result = await db.appointments.delete_one({"id": appointment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")
    return {"message": "Randevu silindi"}


# Transactions Routes
@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    query = {}
    if start_date and end_date:
        query['date'] = {'$gte': start_date, '$lte': end_date}
    elif start_date:
        query['date'] = {'$gte': start_date}
    elif end_date:
        query['date'] = {'$lte': end_date}
    
    transactions = await db.transactions.find(query, {"_id": 0}).sort("date", -1).to_list(1000)
    for transaction in transactions:
        if isinstance(transaction['created_at'], str):
            transaction['created_at'] = datetime.fromisoformat(transaction['created_at'])
    return transactions

@api_router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str, transaction_update: TransactionUpdate, current_user: User = Depends(get_current_user)):
    transaction = await db.transactions.find_one({"id": transaction_id}, {"_id": 0})
    if not transaction:
        raise HTTPException(status_code=404, detail="İşlem bulunamadı")
    
    await db.transactions.update_one(
        {"id": transaction_id},
        {"$set": {"amount": transaction_update.amount}}
    )
    
    updated_transaction = await db.transactions.find_one({"id": transaction_id}, {"_id": 0})
    if isinstance(updated_transaction['created_at'], str):
        updated_transaction['created_at'] = datetime.fromisoformat(updated_transaction['created_at'])
    return updated_transaction

@api_router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str, current_user: User = Depends(get_current_user)):
    result = await db.transactions.delete_one({"id": transaction_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="İşlem bulunamadı")
    return {"message": "İşlem silindi"}


# Dashboard Stats
@api_router.get("/stats/dashboard")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    turkey_tz = ZoneInfo("Europe/Istanbul")
    today = datetime.now(turkey_tz).date().isoformat()
    
    today_appointments = await db.appointments.count_documents({"appointment_date": today})
    today_completed = await db.appointments.count_documents({"appointment_date": today, "status": "Tamamlandı"})
    
    today_transactions = await db.transactions.find({"date": today}, {"_id": 0}).to_list(1000)
    today_income = sum(t['amount'] for t in today_transactions)
    
    week_start = (datetime.now(turkey_tz).date() - timedelta(days=7)).isoformat()
    week_transactions = await db.transactions.find({"date": {"$gte": week_start}}, {"_id": 0}).to_list(1000)
    week_income = sum(t['amount'] for t in week_transactions)
    
    month_start = datetime.now(turkey_tz).date().replace(day=1).isoformat()
    month_transactions = await db.transactions.find({"date": {"$gte": month_start}}, {"_id": 0}).to_list(1000)
    month_income = sum(t['amount'] for t in month_transactions)
    
    return {
        "today_appointments": today_appointments,
        "today_completed": today_completed,
        "today_income": today_income,
        "week_income": week_income,
        "month_income": month_income
    }


# Settings Routes
@api_router.get("/settings", response_model=Settings)
async def get_settings(current_user: User = Depends(get_current_user)):
    settings = await db.settings.find_one({"id": "app_settings"}, {"_id": 0})
    if not settings:
        default_settings = Settings()
        await db.settings.insert_one(default_settings.model_dump())
        return default_settings
    return Settings(**settings)

@api_router.put("/settings", response_model=Settings)
async def update_settings(settings: Settings, current_user: User = Depends(get_current_user)):
    await db.settings.update_one(
        {"id": "app_settings"},
        {"$set": settings.model_dump()},
        upsert=True
    )
    return settings


# Customer History
@api_router.get("/customers/{phone}/history")
async def get_customer_history(phone: str, current_user: User = Depends(get_current_user)):
    appointments = await db.appointments.find(
        {"phone": phone},
        {"_id": 0}
    ).sort("appointment_date", -1).to_list(1000)
    
    for appointment in appointments:
        if isinstance(appointment['created_at'], str):
            appointment['created_at'] = datetime.fromisoformat(appointment['created_at'])
    
    total_completed = len([a for a in appointments if a['status'] == 'Tamamlandı'])
    
    return {
        "phone": phone,
        "total_appointments": len(appointments),
        "completed_appointments": total_completed,
        "appointments": appointments
    }


# Include the router in the main app
app.include_router(api_router)

# CORS Middleware (Değişiklik yok)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging (Değişiklik yok)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()