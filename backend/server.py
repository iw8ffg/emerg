from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
import hashlib
import os
from pymongo import MongoClient
import uuid
from bson import ObjectId
import pandas as pd
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import json

app = FastAPI(title="Emergency Management System API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client['emergency_management']

# JWT Configuration
SECRET_KEY = "emergency_management_secret_key_2025"
ALGORITHM = "HS256"

# Security
security = HTTPBearer()

# User roles
USER_ROLES = {
    "admin": "Amministratore",
    "coordinator": "Coordinatore Emergenze", 
    "operator": "Operatore Sala Operativa",
    "warehouse": "Addetto Magazzino",
    "viewer": "Visualizzatore"
}

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "viewer"
    full_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class EmergencyEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    event_type: str  # incendio, alluvione, terremoto, etc.
    severity: str  # bassa, media, alta, critica
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    status: str = "aperto"  # aperto, in_corso, risolto, chiuso
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str
    updated_at: Optional[datetime] = None
    resources_needed: Optional[List[str]] = []
    notes: Optional[str] = None

class InventoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    quantity: int
    unit: str
    location: str
    expiry_date: Optional[datetime] = None
    supplier: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class OperationalLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    operator: Optional[str] = None
    action: str
    details: str
    event_id: Optional[str] = None
    priority: str = "normale"  # bassa, normale, alta

class TrainedResource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    role: str
    specializations: List[str]
    contact_phone: str
    contact_email: str
    availability: str = "disponibile"  # disponibile, occupato, non_disponibile
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token non valido")
        
        user = db.users.find_one({"username": username})
        if user is None:
            raise HTTPException(status_code=401, detail="Utente non trovato")
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token non valido")

# Initialize admin user
@app.on_event("startup")
async def startup_event():
    # Create admin user if not exists
    admin_user = db.users.find_one({"username": "admin"})
    if not admin_user:
        admin_data = {
            "username": "admin",
            "email": "admin@emergency.local",
            "password": hash_password("admin123"),
            "role": "admin",
            "full_name": "Amministratore Sistema",
            "created_at": datetime.now()
        }
        db.users.insert_one(admin_data)
        print("Admin user created: admin/admin123")

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user: UserCreate):
    # Check if user exists
    if db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username già esistente")
    
    if db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email già registrata")
    
    # Validate role
    if user.role not in USER_ROLES:
        raise HTTPException(status_code=400, detail="Ruolo non valido")
    
    # Create user
    user_data = {
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),
        "role": user.role,
        "full_name": user.full_name,
        "created_at": datetime.now()
    }
    
    db.users.insert_one(user_data)
    return {"message": "Utente registrato con successo"}

@app.post("/api/auth/login")
async def login(user: UserLogin):
    db_user = db.users.find_one({"username": user.username})
    
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": db_user["username"],
            "role": db_user["role"],
            "full_name": db_user["full_name"]
        }
    }

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "role": current_user["role"],
        "full_name": current_user["full_name"],
        "email": current_user["email"]
    }

# Emergency Events endpoints
@app.post("/api/events")
async def create_emergency_event(event: EmergencyEvent, current_user: dict = Depends(get_current_user)):
    # Check permissions
    if current_user["role"] not in ["admin", "coordinator", "operator"]:
        raise HTTPException(status_code=403, detail="Permessi insufficienti")
    
    event_data = event.dict()
    event_data["created_by"] = current_user["username"]
    
    result = db.events.insert_one(event_data)
    return {"message": "Evento creato con successo", "event_id": event.id}

@app.get("/api/events")
async def get_emergency_events(current_user: dict = Depends(get_current_user)):
    events = list(db.events.find({}, {"_id": 0}).sort("created_at", -1))
    return events

@app.get("/api/events/{event_id}")
async def get_emergency_event(event_id: str, current_user: dict = Depends(get_current_user)):
    event = db.events.find_one({"id": event_id}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return event

@app.put("/api/events/{event_id}")
async def update_emergency_event(event_id: str, event: EmergencyEvent, current_user: dict = Depends(get_current_user)):
    # Check permissions
    if current_user["role"] not in ["admin", "coordinator", "operator"]:
        raise HTTPException(status_code=403, detail="Permessi insufficienti")
    
    event_data = event.dict()
    event_data["updated_at"] = datetime.now()
    
    result = db.events.update_one({"id": event_id}, {"$set": event_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    
    return {"message": "Evento aggiornato con successo"}

# Inventory endpoints
@app.post("/api/inventory")
async def create_inventory_item(item: InventoryItem, current_user: dict = Depends(get_current_user)):
    # Check permissions
    if current_user["role"] not in ["admin", "coordinator", "warehouse"]:
        raise HTTPException(status_code=403, detail="Permessi insufficienti")
    
    item_data = item.dict()
    result = db.inventory.insert_one(item_data)
    return {"message": "Articolo creato con successo", "item_id": item.id}

@app.get("/api/inventory")
async def get_inventory(current_user: dict = Depends(get_current_user)):
    items = list(db.inventory.find({}, {"_id": 0}).sort("name", 1))
    return items

# Operational Log endpoints
@app.post("/api/logs")
async def create_operational_log(log: OperationalLog, current_user: dict = Depends(get_current_user)):
    # Check permissions
    if current_user["role"] not in ["admin", "coordinator", "operator"]:
        raise HTTPException(status_code=403, detail="Permessi insufficienti")
    
    log_data = log.dict()
    log_data["operator"] = current_user["username"]
    
    result = db.logs.insert_one(log_data)
    return {"message": "Log creato con successo", "log_id": log.id}

@app.get("/api/logs")
async def get_operational_logs(current_user: dict = Depends(get_current_user)):
    logs = list(db.logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(100))
    return logs

# Trained Resources endpoints
@app.post("/api/resources")
async def create_trained_resource(resource: TrainedResource, current_user: dict = Depends(get_current_user)):
    # Check permissions
    if current_user["role"] not in ["admin", "coordinator"]:
        raise HTTPException(status_code=403, detail="Permessi insufficienti")
    
    resource_data = resource.dict()
    result = db.resources.insert_one(resource_data)
    return {"message": "Risorsa creata con successo", "resource_id": resource.id}

@app.get("/api/resources")
async def get_trained_resources(current_user: dict = Depends(get_current_user)):
    resources = list(db.resources.find({}, {"_id": 0}).sort("full_name", 1))
    return resources

# Dashboard stats endpoint
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    total_events = db.events.count_documents({})
    open_events = db.events.count_documents({"status": "aperto"})
    critical_events = db.events.count_documents({"severity": "critica"})
    inventory_items = db.inventory.count_documents({})
    trained_resources = db.resources.count_documents({})
    total_logs = db.logs.count_documents({})
    
    return {
        "total_events": total_events,
        "open_events": open_events,
        "critical_events": critical_events,
        "inventory_items": inventory_items,
        "trained_resources": trained_resources,
        "total_logs": total_logs
    }

@app.get("/api/health")
async def health_check():
    return {"status": "OK", "service": "Emergency Management System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)