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
    created_by: Optional[str] = None  # Will be set by the endpoint
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
    min_quantity: int = 0  # Alert quando sotto questa quantità
    max_quantity: Optional[int] = None
    expiry_date: Optional[datetime] = None
    supplier: Optional[str] = None
    cost_per_unit: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

class InventoryUpdate(BaseModel):
    quantity_change: int  # +/- per aumentare/diminuire
    reason: str
    location: Optional[str] = None

class UserManagement(BaseModel):
    username: str
    email: str
    password: Optional[str] = None
    role: str
    full_name: str
    active: bool = True

class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    full_name: Optional[str] = None
    active: Optional[bool] = None
    new_password: Optional[str] = None

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

class ReportRequest(BaseModel):
    report_type: str  # events, logs, statistics, inventory, resources
    format: str = "pdf"  # pdf, excel, csv
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    event_type: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    operator: Optional[str] = None
    status: Optional[str] = None

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

# Report generation functions
def generate_events_pdf(events_data, filters):
    """Generate PDF report for emergency events"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Build content
    content = []
    
    # Title
    title = Paragraph("REPORT EVENTI DI EMERGENZA", title_style)
    content.append(title)
    content.append(Spacer(1, 12))
    
    # Report info
    report_info = f"""
    <b>Data generazione:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
    <b>Periodo:</b> {filters.get('start_date', 'Non specificato')} - {filters.get('end_date', 'Non specificato')}<br/>
    <b>Filtri applicati:</b> Tipo: {filters.get('event_type', 'Tutti')}, Gravità: {filters.get('severity', 'Tutte')}<br/>
    <b>Totale eventi:</b> {len(events_data)}
    """
    content.append(Paragraph(report_info, styles['Normal']))
    content.append(Spacer(1, 20))
    
    if events_data:
        # Create table data
        table_data = [['Titolo', 'Tipo', 'Gravità', 'Status', 'Data', 'Operatore']]
        
        for event in events_data:
            # Handle datetime conversion safely
            created_at = event.get('created_at', '')
            if isinstance(created_at, str) and created_at:
                try:
                    # Remove timezone info and parse
                    clean_date = created_at.replace('Z', '').replace('+00:00', '')
                    if 'T' in clean_date:
                        date_obj = datetime.fromisoformat(clean_date)
                    else:
                        date_obj = datetime.strptime(clean_date, '%Y-%m-%d %H:%M:%S')
                    formatted_date = date_obj.strftime('%d/%m/%Y')
                except (ValueError, TypeError):
                    formatted_date = 'N/A'
            elif isinstance(created_at, datetime):
                formatted_date = created_at.strftime('%d/%m/%Y')
            else:
                formatted_date = 'N/A'
            
            table_data.append([
                event.get('title', '')[:30],
                event.get('event_type', ''),
                event.get('severity', ''),
                event.get('status', ''),
                formatted_date,
                event.get('created_by', '')
            ])
        
        # Create table
        table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(table)
    else:
        content.append(Paragraph("Nessun evento trovato per i filtri specificati.", styles['Normal']))
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer

def generate_logs_pdf(logs_data, filters):
    """Generate PDF report for operational logs"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    content = []
    
    # Title
    title = Paragraph("REPORT LOG OPERATIVI", title_style)
    content.append(title)
    content.append(Spacer(1, 12))
    
    # Report info
    report_info = f"""
    <b>Data generazione:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
    <b>Periodo:</b> {filters.get('start_date', 'Non specificato')} - {filters.get('end_date', 'Non specificato')}<br/>
    <b>Filtri applicati:</b> Priorità: {filters.get('priority', 'Tutte')}, Operatore: {filters.get('operator', 'Tutti')}<br/>
    <b>Totale log:</b> {len(logs_data)}
    """
    content.append(Paragraph(report_info, styles['Normal']))
    content.append(Spacer(1, 20))
    
    if logs_data:
        # Create table data
        table_data = [['Azione', 'Priorità', 'Operatore', 'Data', 'Dettagli']]
        
        for log in logs_data:
            # Handle datetime conversion safely
            timestamp = log.get('timestamp', '')
            if isinstance(timestamp, str) and timestamp:
                try:
                    # Remove timezone info and parse
                    clean_date = timestamp.replace('Z', '').replace('+00:00', '')
                    if 'T' in clean_date:
                        date_obj = datetime.fromisoformat(clean_date)
                    else:
                        date_obj = datetime.strptime(clean_date, '%Y-%m-%d %H:%M:%S')
                    formatted_date = date_obj.strftime('%d/%m/%Y %H:%M')
                except (ValueError, TypeError):
                    formatted_date = 'N/A'
            elif isinstance(timestamp, datetime):
                formatted_date = timestamp.strftime('%d/%m/%Y %H:%M')
            else:
                formatted_date = 'N/A'
            
            table_data.append([
                log.get('action', '')[:25],
                log.get('priority', ''),
                log.get('operator', ''),
                formatted_date,
                log.get('details', '')[:40] + '...' if len(log.get('details', '')) > 40 else log.get('details', '')
            ])
        
        table = Table(table_data, colWidths=[1.5*inch, 0.8*inch, 1*inch, 1.2*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(table)
    else:
        content.append(Paragraph("Nessun log trovato per i filtri specificati.", styles['Normal']))
    
    doc.build(content)
    buffer.seek(0)
    return buffer

def generate_statistics_pdf(stats_data):
    """Generate PDF report for statistics"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    content = []
    
    # Title
    title = Paragraph("REPORT STATISTICHE GENERALI", title_style)
    content.append(title)
    content.append(Spacer(1, 12))
    
    # Report info
    report_info = f"""
    <b>Data generazione:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
    <b>Sistema:</b> Gestione Emergenze<br/>
    """
    content.append(Paragraph(report_info, styles['Normal']))
    content.append(Spacer(1, 20))
    
    # Statistics table
    stats_table_data = [
        ['Categoria', 'Valore'],
        ['Eventi Totali', str(stats_data.get('total_events', 0))],
        ['Eventi Aperti', str(stats_data.get('open_events', 0))],
        ['Eventi Critici', str(stats_data.get('critical_events', 0))],
        ['Log Operativi', str(stats_data.get('total_logs', 0))],
        ['Articoli Inventario', str(stats_data.get('inventory_items', 0))],
        ['Risorse Formate', str(stats_data.get('trained_resources', 0))]
    ]
    
    stats_table = Table(stats_table_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(stats_table)
    
    doc.build(content)
    buffer.seek(0)
    return buffer

def generate_excel_report(data, report_type, filters):
    """Generate Excel report"""
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        if report_type == 'events':
            # Convert events data to DataFrame
            if data:
                df = pd.DataFrame(data)
                # Convert datetime columns
                if 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y %H:%M')
                if 'updated_at' in df.columns:
                    df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')
                
                df.to_excel(writer, sheet_name='Eventi Emergenza', index=False)
            else:
                # Create empty DataFrame with headers if no data
                empty_df = pd.DataFrame(columns=['title', 'event_type', 'severity', 'status', 'created_at', 'created_by'])
                empty_df.to_excel(writer, sheet_name='Eventi Emergenza', index=False)
            
        elif report_type == 'logs':
            # Convert logs data to DataFrame
            if data:
                df = pd.DataFrame(data)
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%d/%m/%Y %H:%M')
                
                df.to_excel(writer, sheet_name='Log Operativi', index=False)
            else:
                # Create empty DataFrame with headers if no data
                empty_df = pd.DataFrame(columns=['action', 'priority', 'operator', 'timestamp', 'details'])
                empty_df.to_excel(writer, sheet_name='Log Operativi', index=False)
        
        elif report_type == 'statistics':
            # Create statistics sheet
            stats_df = pd.DataFrame.from_dict(data, orient='index', columns=['Valore'])
            stats_df.index.name = 'Categoria'
            stats_df.to_excel(writer, sheet_name='Statistiche')
    
    buffer.seek(0)
    return buffer

def filter_data_by_date(data, start_date, end_date, date_field='created_at'):
    """Filter data by date range"""
    if not start_date and not end_date:
        return data
    
    filtered_data = []
    for item in data:
        item_date_str = item.get(date_field)
        if not item_date_str:
            continue
            
        try:
            # Handle different datetime formats
            if isinstance(item_date_str, str):
                # Remove timezone info if present and parse
                clean_date_str = item_date_str.replace('Z', '').replace('+00:00', '')
                if 'T' in clean_date_str:
                    item_date = datetime.fromisoformat(clean_date_str)
                else:
                    item_date = datetime.strptime(clean_date_str, '%Y-%m-%d %H:%M:%S')
            elif isinstance(item_date_str, datetime):
                item_date = item_date_str
            else:
                continue
            
            if start_date:
                start_datetime = datetime.fromisoformat(start_date + 'T00:00:00')
                if item_date < start_datetime:
                    continue
                    
            if end_date:
                end_datetime = datetime.fromisoformat(end_date + 'T23:59:59')
                if item_date > end_datetime:
                    continue
                    
            filtered_data.append(item)
        except (ValueError, TypeError) as e:
            # Skip items with invalid dates
            print(f"Skipping item with invalid date: {item_date_str}, error: {e}")
            continue
    
    return filtered_data

# Initialize admin user and database
@app.on_event("startup")
async def startup_event():
    """Initialize database and create admin user on first startup"""
    print("\n🚀 === AVVIO SISTEMA GESTIONE EMERGENZE ===")
    
    try:
        # Test database connection
        print("📊 Connessione al database MongoDB...")
        db.command('ping')
        print("✅ Connessione MongoDB stabilita con successo")
        
        # Initialize collections with indexes for better performance
        print("🗂️ Inizializzazione collezioni database...")
        
        # Create indexes for better performance
        try:
            # Events collection indexes
            db.events.create_index([("created_at", -1)])
            db.events.create_index([("status", 1)])
            db.events.create_index([("severity", 1)])
            db.events.create_index([("event_type", 1)])
            db.events.create_index([("latitude", 1), ("longitude", 1)])
            
            # Users collection indexes
            db.users.create_index([("username", 1)], unique=True)
            db.users.create_index([("email", 1)], unique=True)
            db.users.create_index([("role", 1)])
            
            # Inventory collection indexes
            db.inventory.create_index([("name", 1)])
            db.inventory.create_index([("category", 1)])
            db.inventory.create_index([("location", 1)])
            db.inventory.create_index([("expiry_date", 1)])
            
            # Logs collection indexes
            db.logs.create_index([("timestamp", -1)])
            db.logs.create_index([("operator", 1)])
            db.logs.create_index([("priority", 1)])
            
            # Resources collection indexes
            db.resources.create_index([("full_name", 1)])
            db.resources.create_index([("role", 1)])
            db.resources.create_index([("availability", 1)])
            
            print("✅ Indici database creati con successo")
        except Exception as e:
            print(f"⚠️ Avviso indici database: {str(e)}")
        
        # Check and create admin user
        print("👤 Verifica utente amministratore...")
        admin_user = db.users.find_one({"username": "admin"})
        
        if not admin_user:
            print("🔧 Creazione utente amministratore...")
            admin_data = {
                "username": "admin",
                "email": "admin@emergency.local",
                "password": hash_password("admin123"),
                "role": "admin",
                "full_name": "Amministratore Sistema",
                "active": True,
                "created_at": datetime.now(),
                "created_by": "system"
            }
            db.users.insert_one(admin_data)
            print("✅ Utente amministratore creato con successo!")
            print("   📧 Username: admin")
            print("   🔑 Password: admin123")
            print("   🔐 Ruolo: Amministratore")
        else:
            print("✅ Utente amministratore già esistente")
        
        # Check if this is a fresh installation
        total_users = db.users.count_documents({})
        total_events = db.events.count_documents({})
        total_inventory = db.inventory.count_documents({})
        
        is_fresh_install = total_users <= 1 and total_events == 0 and total_inventory == 0
        
        if is_fresh_install:
            print("\n🆕 Prima installazione rilevata - Inizializzazione dati di esempio...")
            
            # Create sample users for testing
            print("👥 Creazione utenti di esempio...")
            sample_users = [
                {
                    "username": "coordinatore1",
                    "email": "coordinatore@emergency.local",
                    "password": hash_password("coord123"),
                    "role": "coordinator",
                    "full_name": "Mario Rossi",
                    "active": True,
                    "created_at": datetime.now(),
                    "created_by": "system"
                },
                {
                    "username": "operatore1",
                    "email": "operatore@emergency.local", 
                    "password": hash_password("oper123"),
                    "role": "operator",
                    "full_name": "Giulia Bianchi",
                    "active": True,
                    "created_at": datetime.now(),
                    "created_by": "system"
                },
                {
                    "username": "magazziniere1",
                    "email": "magazzino@emergency.local",
                    "password": hash_password("magaz123"),
                    "role": "warehouse",
                    "full_name": "Luca Verdi",
                    "active": True,
                    "created_at": datetime.now(),
                    "created_by": "system"
                }
            ]
            
            for user_data in sample_users:
                try:
                    existing = db.users.find_one({"username": user_data["username"]})
                    if not existing:
                        db.users.insert_one(user_data)
                        print(f"   ✅ Utente {user_data['username']} ({user_data['role']}) creato")
                except Exception as e:
                    print(f"   ⚠️ Errore creazione utente {user_data['username']}: {str(e)}")
            
            # Create sample inventory items
            print("📦 Creazione articoli inventario di esempio...")
            sample_inventory = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Kit Pronto Soccorso Completo",
                    "category": "medicinali",
                    "quantity": 25,
                    "unit": "pz",
                    "location": "Magazzino Centrale - Scaffale A1",
                    "min_quantity": 5,
                    "max_quantity": 50,
                    "expiry_date": datetime(2025, 12, 31),
                    "supplier": "MedSupply Italia",
                    "cost_per_unit": 45.50,
                    "notes": "Kit completi per emergenze mediche",
                    "created_at": datetime.now(),
                    "last_updated_by": "system"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Estintore Portatile CO2",
                    "category": "attrezzature",
                    "quantity": 15,
                    "unit": "pz",
                    "location": "Magazzino Sicurezza - Zona B",
                    "min_quantity": 3,
                    "max_quantity": 30,
                    "supplier": "SafeEquip Srl",
                    "cost_per_unit": 85.00,
                    "notes": "Estintori portatili per interventi rapidi",
                    "created_at": datetime.now(),
                    "last_updated_by": "system"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Coperte Termiche Emergency",
                    "category": "vestiario",
                    "quantity": 100,
                    "unit": "pz",
                    "location": "Magazzino Forniture - Scaffale C3",
                    "min_quantity": 20,
                    "max_quantity": 200,
                    "supplier": "Emergency Supplies",
                    "cost_per_unit": 3.50,
                    "notes": "Coperte termiche per evacuazioni",
                    "created_at": datetime.now(),
                    "last_updated_by": "system"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Radio Portatile VHF",
                    "category": "comunicazione",
                    "quantity": 8,
                    "unit": "pz",
                    "location": "Magazzino Comunicazioni",
                    "min_quantity": 2,
                    "max_quantity": 15,
                    "supplier": "RadioTech",
                    "cost_per_unit": 120.00,
                    "notes": "Radio per comunicazioni di emergenza",
                    "created_at": datetime.now(),
                    "last_updated_by": "system"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Acqua Potabile (Bottiglie 1.5L)",
                    "category": "alimentari",
                    "quantity": 200,
                    "unit": "pz",
                    "location": "Deposito Alimentari",
                    "min_quantity": 50,
                    "max_quantity": 500,
                    "expiry_date": datetime(2025, 8, 15),
                    "supplier": "AcquaPura Srl",
                    "cost_per_unit": 0.80,
                    "notes": "Scorte acqua per emergenze",
                    "created_at": datetime.now(),
                    "last_updated_by": "system"
                }
            ]
            
            for item in sample_inventory:
                try:
                    db.inventory.insert_one(item)
                    print(f"   ✅ Articolo '{item['name']}' aggiunto all'inventario")
                except Exception as e:
                    print(f"   ⚠️ Errore creazione articolo: {str(e)}")
            
            # Create sample trained resources
            print("👷 Creazione risorse formate di esempio...")
            sample_resources = [
                {
                    "id": str(uuid.uuid4()),
                    "full_name": "Dr. Anna Medicina",
                    "role": "Medico di Emergenza",
                    "specializations": ["Pronto Soccorso", "Traumatologia", "Rianimazione"],
                    "contact_phone": "+39 338 1234567",
                    "contact_email": "a.medicina@ospedale.it",
                    "availability": "disponibile",
                    "location": "Ospedale Centrale",
                    "created_at": datetime.now()
                },
                {
                    "id": str(uuid.uuid4()),
                    "full_name": "Cap. Marco Protezione",
                    "role": "Comandante Protezione Civile",
                    "specializations": ["Coordinamento Emergenze", "Evacuazioni", "Logistica"],
                    "contact_phone": "+39 347 9876543",
                    "contact_email": "m.protezione@protciv.it",
                    "availability": "disponibile",
                    "location": "Centro Operativo",
                    "created_at": datetime.now()
                },
                {
                    "id": str(uuid.uuid4()),
                    "full_name": "Ing. Sara Strutture",
                    "role": "Ingegnere Strutturale",
                    "specializations": ["Valutazione Danni", "Sicurezza Edifici", "Verifiche Strutturali"],
                    "contact_phone": "+39 349 5551234",
                    "contact_email": "s.strutture@studio.it",
                    "availability": "disponibile",
                    "location": "Studio Tecnico",
                    "created_at": datetime.now()
                }
            ]
            
            for resource in sample_resources:
                try:
                    db.resources.insert_one(resource)
                    print(f"   ✅ Risorsa '{resource['full_name']}' aggiunta")
                except Exception as e:
                    print(f"   ⚠️ Errore creazione risorsa: {str(e)}")
            
            # Create initial operational log
            initial_log = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(),
                "operator": "system",
                "action": "Inizializzazione Sistema",
                "details": "Sistema di gestione emergenze inizializzato con successo. Database configurato, utenti creati, inventario e risorse di esempio aggiunti.",
                "priority": "normale"
            }
            db.logs.insert_one(initial_log)
            print("✅ Log inizializzazione sistema creato")
            
            print("\n🎉 Inizializzazione completata con successo!")
            print("\n📋 CREDENZIALI DI ACCESSO:")
            print("   🔐 Amministratore: admin / admin123")
            print("   🎯 Coordinatore: coordinatore1 / coord123")
            print("   ⚙️ Operatore: operatore1 / oper123")
            print("   📦 Magazziniere: magazziniere1 / magaz123")
            
        else:
            print("✅ Sistema già configurato - Saltando inizializzazione dati esempio")
        
        # Final system status
        print(f"\n📊 STATO SISTEMA:")
        print(f"   👥 Utenti registrati: {db.users.count_documents({})}")
        print(f"   🚨 Eventi di emergenza: {db.events.count_documents({})}")
        print(f"   📦 Articoli inventario: {db.inventory.count_documents({})}")
        print(f"   👷 Risorse formate: {db.resources.count_documents({})}")
        print(f"   📝 Log operativi: {db.logs.count_documents({})}")
        
        print("\n✅ === SISTEMA GESTIONE EMERGENZE PRONTO ===")
        print("🌐 Accedi all'interfaccia web per iniziare!")
        
    except Exception as e:
        print(f"❌ Errore durante l'inizializzazione: {str(e)}")
        print("⚠️ Il sistema potrebbe non funzionare correttamente")
        raise e

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

@app.get("/api/events/map")
async def get_map_events(
    status: Optional[str] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get events with coordinates for map display"""
    # Build query for events with coordinates
    query = {
        "latitude": {"$exists": True, "$ne": None},
        "longitude": {"$exists": True, "$ne": None}
    }
    
    # Apply filters
    if status:
        if status == "active":
            query["status"] = {"$in": ["aperto", "in_corso"]}
        else:
            query["status"] = status
    else:
        # Default to active events only
        query["status"] = {"$in": ["aperto", "in_corso"]}
    
    if event_type:
        query["event_type"] = event_type
    
    if severity:
        query["severity"] = severity
    
    events = list(db.events.find(query, {"_id": 0}).sort("created_at", -1))
    
    # Format events for map display
    map_events = []
    for event in events:
        if event.get('latitude') is not None and event.get('longitude') is not None:
            map_events.append({
                "id": event["id"],
                "title": event["title"],
                "description": event["description"],
                "event_type": event["event_type"],
                "severity": event["severity"],
                "status": event["status"],
                "latitude": float(event["latitude"]),
                "longitude": float(event["longitude"]),
                "address": event.get("address", ""),
                "created_at": event["created_at"],
                "created_by": event["created_by"],
                "notes": event.get("notes", "")
            })
    
    return {
        "events": map_events,
        "total": len(map_events),
        "filters_applied": {
            "status": status or "active",
            "event_type": event_type,
            "severity": severity
        }
    }

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
    item_data["last_updated_by"] = current_user["username"]
    result = db.inventory.insert_one(item_data)
    return {"message": "Articolo creato con successo", "item_id": item.id}

@app.get("/api/inventory")
async def get_inventory(
    category: Optional[str] = None,
    location: Optional[str] = None,
    low_stock: Optional[bool] = None,
    expiring_soon: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    
    if category:
        query["category"] = category
    if location:
        query["location"] = location
    if low_stock:
        # Items below minimum quantity
        query["$expr"] = {"$lt": ["$quantity", "$min_quantity"]}
    
    items = list(db.inventory.find(query, {"_id": 0}).sort("name", 1))
    
    # Filter expiring items if requested
    if expiring_soon:
        today = datetime.now()
        thirty_days = today + timedelta(days=30)
        items = [item for item in items if item.get('expiry_date') and 
                datetime.fromisoformat(item['expiry_date'].replace('Z', '')) <= thirty_days]
    
    return items

@app.get("/api/inventory/{item_id}")
async def get_inventory_item(item_id: str, current_user: dict = Depends(get_current_user)):
    item = db.inventory.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    return item

@app.put("/api/inventory/{item_id}")
async def update_inventory_item(item_id: str, item: InventoryItem, current_user: dict = Depends(get_current_user)):
    # Check permissions
    if current_user["role"] not in ["admin", "coordinator", "warehouse"]:
        raise HTTPException(status_code=403, detail="Permessi insufficienti")
    
    item_data = item.dict()
    item_data["updated_at"] = datetime.now()
    item_data["last_updated_by"] = current_user["username"]
    
    result = db.inventory.update_one({"id": item_id}, {"$set": item_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    
    return {"message": "Articolo aggiornato con successo"}

@app.delete("/api/inventory/{item_id}")
async def delete_inventory_item(item_id: str, current_user: dict = Depends(get_current_user)):
    # Check permissions
    if current_user["role"] not in ["admin", "coordinator"]:
        raise HTTPException(status_code=403, detail="Permessi insufficienti")
    
    result = db.inventory.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    
    return {"message": "Articolo eliminato con successo"}

@app.post("/api/inventory/{item_id}/update-quantity")
async def update_inventory_quantity(item_id: str, update: InventoryUpdate, current_user: dict = Depends(get_current_user)):
    # Check permissions
    if current_user["role"] not in ["admin", "coordinator", "warehouse"]:
        raise HTTPException(status_code=403, detail="Permessi insufficienti")
    
    # Get current item
    item = db.inventory.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    
    # Calculate new quantity
    new_quantity = item["quantity"] + update.quantity_change
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="La quantità non può essere negativa")
    
    # Update item
    update_data = {
        "quantity": new_quantity,
        "updated_at": datetime.now(),
        "last_updated_by": current_user["username"]
    }
    
    if update.location:
        update_data["location"] = update.location
    
    db.inventory.update_one({"id": item_id}, {"$set": update_data})
    
    # Log the change
    log_data = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(),
        "operator": current_user["username"],
        "action": f"Aggiornamento inventario: {item['name']}",
        "details": f"{update.reason}. Quantità: {item['quantity']} → {new_quantity} ({'+' if update.quantity_change > 0 else ''}{update.quantity_change})",
        "priority": "normale"
    }
    db.logs.insert_one(log_data)
    
    return {"message": "Quantità aggiornata con successo", "new_quantity": new_quantity}

@app.get("/api/inventory/categories")
async def get_inventory_categories(current_user: dict = Depends(get_current_user)):
    categories = db.inventory.distinct("category")
    return {"categories": categories}

@app.get("/api/inventory/locations")
async def get_inventory_locations(current_user: dict = Depends(get_current_user)):
    locations = db.inventory.distinct("location")
    return {"locations": locations}

@app.get("/api/inventory/alerts")
async def get_inventory_alerts(current_user: dict = Depends(get_current_user)):
    # Get low stock items
    low_stock_items = list(db.inventory.find({
        "$expr": {"$lt": ["$quantity", "$min_quantity"]}
    }, {"_id": 0}))
    
    # Get expiring items (next 30 days)
    today = datetime.now()
    thirty_days_from_now = today + timedelta(days=30)
    
    expiring_items = []
    all_items = list(db.inventory.find({"expiry_date": {"$exists": True, "$ne": None}}, {"_id": 0}))
    
    for item in all_items:
        expiry_date = item.get('expiry_date')
        if expiry_date:
            if isinstance(expiry_date, str):
                try:
                    expiry_date = datetime.fromisoformat(expiry_date.replace('Z', ''))
                except:
                    continue
            
            if expiry_date <= thirty_days_from_now:
                expiring_items.append(item)
    
    return {
        "low_stock_items": low_stock_items,
        "expiring_items": expiring_items,
        "total_alerts": len(low_stock_items) + len(expiring_items)
    }

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
    
    # Inventory alerts
    low_stock_count = db.inventory.count_documents({
        "$expr": {"$lt": ["$quantity", "$min_quantity"]}
    })
    
    # Count expiring items (next 30 days)
    today = datetime.now()
    thirty_days_from_now = today + timedelta(days=30)
    expiring_count = 0
    
    try:
        all_items_with_expiry = list(db.inventory.find({"expiry_date": {"$exists": True, "$ne": None}}, {"expiry_date": 1}))
        for item in all_items_with_expiry:
            expiry_date = item.get('expiry_date')
            if expiry_date:
                if isinstance(expiry_date, str):
                    try:
                        expiry_date = datetime.fromisoformat(expiry_date.replace('Z', ''))
                    except:
                        continue
                
                if expiry_date <= thirty_days_from_now:
                    expiring_count += 1
    except:
        expiring_count = 0
    
    return {
        "total_events": total_events,
        "open_events": open_events,
        "critical_events": critical_events,
        "inventory_items": inventory_items,
        "trained_resources": trained_resources,
        "total_logs": total_logs,
        "inventory_alerts": {
            "low_stock": low_stock_count,
            "expiring_soon": expiring_count,
            "total": low_stock_count + expiring_count
        }
    }

@app.get("/api/health")
async def health_check():
    return {"status": "OK", "service": "Emergency Management System"}

# Report endpoints
@app.post("/api/reports/generate")
async def generate_report(report_request: ReportRequest, current_user: dict = Depends(get_current_user)):
    """Generate and download reports in various formats"""
    try:
        # Prepare filters
        filters = {
            'start_date': report_request.start_date,
            'end_date': report_request.end_date,
            'event_type': report_request.event_type,
            'severity': report_request.severity,
            'priority': report_request.priority,
            'operator': report_request.operator,
            'status': report_request.status
        }
        
        # Get data based on report type
        if report_request.report_type == 'events':
            # Get events data
            query = {}
            if report_request.event_type:
                query['event_type'] = report_request.event_type
            if report_request.severity:
                query['severity'] = report_request.severity
            if report_request.status:
                query['status'] = report_request.status
                
            events_data = list(db.events.find(query, {"_id": 0}).sort("created_at", -1))
            
            # Filter by date
            if report_request.start_date or report_request.end_date:
                events_data = filter_data_by_date(events_data, report_request.start_date, report_request.end_date)
            
            # Generate report
            if report_request.format == 'pdf':
                buffer = generate_events_pdf(events_data, filters)
                filename = f"report_eventi_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                media_type = 'application/pdf'
            elif report_request.format == 'excel':
                buffer = generate_excel_report(events_data, 'events', filters)
                filename = f"report_eventi_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                raise HTTPException(status_code=400, detail="Formato non supportato")
        
        elif report_request.report_type == 'logs':
            # Get logs data
            query = {}
            if report_request.priority:
                query['priority'] = report_request.priority
            if report_request.operator:
                query['operator'] = report_request.operator
                
            logs_data = list(db.logs.find(query, {"_id": 0}).sort("timestamp", -1))
            
            # Filter by date
            if report_request.start_date or report_request.end_date:
                logs_data = filter_data_by_date(logs_data, report_request.start_date, report_request.end_date, 'timestamp')
            
            # Generate report
            if report_request.format == 'pdf':
                buffer = generate_logs_pdf(logs_data, filters)
                filename = f"report_log_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                media_type = 'application/pdf'
            elif report_request.format == 'excel':
                buffer = generate_excel_report(logs_data, 'logs', filters)
                filename = f"report_log_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                raise HTTPException(status_code=400, detail="Formato non supportato")
        
        elif report_request.report_type == 'statistics':
            # Get statistics data
            total_events = db.events.count_documents({})
            open_events = db.events.count_documents({"status": "aperto"})
            critical_events = db.events.count_documents({"severity": "critica"})
            inventory_items = db.inventory.count_documents({})
            trained_resources = db.resources.count_documents({})
            total_logs = db.logs.count_documents({})
            
            stats_data = {
                "total_events": total_events,
                "open_events": open_events,
                "critical_events": critical_events,
                "inventory_items": inventory_items,
                "trained_resources": trained_resources,
                "total_logs": total_logs
            }
            
            # Generate report
            if report_request.format == 'pdf':
                buffer = generate_statistics_pdf(stats_data)
                filename = f"report_statistiche_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                media_type = 'application/pdf'
            elif report_request.format == 'excel':
                buffer = generate_excel_report(stats_data, 'statistics', filters)
                filename = f"report_statistiche_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                raise HTTPException(status_code=400, detail="Formato non supportato")
        
        else:
            raise HTTPException(status_code=400, detail="Tipo di report non supportato")
        
        # Return file as streaming response
        return StreamingResponse(
            io.BytesIO(buffer.read()),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la generazione del report: {str(e)}")

@app.get("/api/reports/templates")
async def get_report_templates(current_user: dict = Depends(get_current_user)):
    """Get available report templates and options"""
    templates = {
        "events": {
            "name": "Report Eventi di Emergenza",
            "description": "Report dettagliato di tutti gli eventi di emergenza",
            "filters": ["start_date", "end_date", "event_type", "severity", "status"],
            "formats": ["pdf", "excel"]
        },
        "logs": {
            "name": "Report Log Operativi", 
            "description": "Report delle attività operative registrate",
            "filters": ["start_date", "end_date", "priority", "operator"],
            "formats": ["pdf", "excel"]
        },
        "statistics": {
            "name": "Report Statistiche Generali",
            "description": "Riepilogo statistico del sistema",
            "filters": [],
            "formats": ["pdf", "excel"]
        }
    }
    
    # Get available filter options
    filter_options = {
        "event_types": ["incendio", "alluvione", "terremoto", "incidente_stradale", "emergenza_medica", "blackout", "altro"],
        "severities": ["bassa", "media", "alta", "critica"],
        "priorities": ["bassa", "normale", "alta"],
        "statuses": ["aperto", "in_corso", "risolto", "chiuso"],
        "operators": list(set([log.get('operator') for log in db.logs.find({}, {"operator": 1, "_id": 0}) if log.get('operator')]))
    }
    
    return {
        "templates": templates,
        "filter_options": filter_options
    }

# User Management endpoints (Admin only)
@app.get("/api/admin/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo gli amministratori possono accedere a questa funzione")
    
    users = list(db.users.find({}, {"_id": 0, "password": 0}).sort("username", 1))
    return users

@app.post("/api/admin/users")
async def create_user_admin(user: UserManagement, current_user: dict = Depends(get_current_user)):
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo gli amministratori possono creare utenti")
    
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
        "password": hash_password(user.password or "default123"),
        "role": user.role,
        "full_name": user.full_name,
        "active": user.active,
        "created_at": datetime.now(),
        "created_by": current_user["username"]
    }
    
    db.users.insert_one(user_data)
    return {"message": "Utente creato con successo"}

@app.put("/api/admin/users/{username}")
async def update_user_admin(username: str, user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo gli amministratori possono modificare utenti")
    
    # Cannot modify own account through this endpoint
    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="Non puoi modificare il tuo account tramite questa funzione")
    
    # Check if user exists
    existing_user = db.users.find_one({"username": username})
    if not existing_user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    # Prepare update data
    update_data = {"updated_at": datetime.now(), "updated_by": current_user["username"]}
    
    if user_update.email is not None:
        # Check if email already exists for another user
        email_check = db.users.find_one({"email": user_update.email, "username": {"$ne": username}})
        if email_check:
            raise HTTPException(status_code=400, detail="Email già utilizzata da un altro utente")
        update_data["email"] = user_update.email
    
    if user_update.role is not None:
        if user_update.role not in USER_ROLES:
            raise HTTPException(status_code=400, detail="Ruolo non valido")
        update_data["role"] = user_update.role
    
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    
    if user_update.active is not None:
        update_data["active"] = user_update.active
    
    if user_update.new_password is not None:
        update_data["password"] = hash_password(user_update.new_password)
    
    # Update user
    result = db.users.update_one({"username": username}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    return {"message": "Utente aggiornato con successo"}

@app.delete("/api/admin/users/{username}")
async def delete_user_admin(username: str, current_user: dict = Depends(get_current_user)):
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo gli amministratori possono eliminare utenti")
    
    # Cannot delete own account
    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="Non puoi eliminare il tuo account")
    
    # Cannot delete admin users (safety measure)
    user_to_delete = db.users.find_one({"username": username})
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    if user_to_delete["role"] == "admin":
        raise HTTPException(status_code=400, detail="Non è possibile eliminare account amministratore")
    
    result = db.users.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    return {"message": "Utente eliminato con successo"}

@app.post("/api/admin/users/{username}/reset-password")
async def reset_user_password(username: str, current_user: dict = Depends(get_current_user)):
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo gli amministratori possono resettare password")
    
    # Check if user exists
    if not db.users.find_one({"username": username}):
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    # Reset password to default
    new_password = "reset123"
    hashed_password = hash_password(new_password)
    
    db.users.update_one(
        {"username": username},
        {"$set": {
            "password": hashed_password,
            "password_reset_at": datetime.now(),
            "password_reset_by": current_user["username"]
        }}
    )
    
    return {"message": f"Password resettata con successo. Nuova password: {new_password}"}

@app.get("/api/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo gli amministratori possono accedere a queste statistiche")
    
    # User statistics
    total_users = db.users.count_documents({})
    active_users = db.users.count_documents({"active": True})
    users_by_role = {}
    for role in USER_ROLES.keys():
        users_by_role[role] = db.users.count_documents({"role": role})
    
    # System statistics
    total_events = db.events.count_documents({})
    total_logs = db.logs.count_documents({})
    total_inventory = db.inventory.count_documents({})
    
    # Recent activity (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_events = db.events.count_documents({"created_at": {"$gte": seven_days_ago.isoformat()}})
    recent_logs = db.logs.count_documents({"timestamp": {"$gte": seven_days_ago.isoformat()}})
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users,
            "by_role": users_by_role
        },
        "system": {
            "total_events": total_events,
            "total_logs": total_logs,
            "total_inventory": total_inventory
        },
        "recent_activity": {
            "events_last_7_days": recent_events,
            "logs_last_7_days": recent_logs
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)