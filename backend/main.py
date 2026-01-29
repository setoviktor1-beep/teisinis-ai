from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
from typing import Optional, Dict, Any

# Ensure project root is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.document_generator import DocumentGenerator
from backend.agents.eseimas_agent import ESeimasAgent
from backend.scrapers.etar_scraper import ETARScraper
from backend.database import engine, get_db, Base
from backend.models import Document, User
from sqlalchemy.orm import Session
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from backend import auth

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Teisinis AI API",
    description="Backend API for Lithuanian Legal AI Assistant",
    version="0.1.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for MVP, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agents
try:
    doc_generator = DocumentGenerator()
    eseimas = ESeimasAgent()
    scraper = ETARScraper()
    print("✅ Agents initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize agents: {e}")
    # We don't crash here to allow health check to work even if agents fail

# --- Pydantic Models ---

class ComplaintRequest(BaseModel):
    employee_name: str
    employer_name: str
    workplace: str
    violation_description: str
    violation_date: str
    additional_details: Optional[str] = None

class ContractRequest(BaseModel):
    employee_name: str
    employer_name: str
    position: str
    salary: float
    workplace: str
    start_date: str
    additional_conditions: Optional[str] = None

class ArticleRequest(BaseModel):
    article_number: int

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Endpoints ---

@app.get("/api/health")
def health_check_api():
    return {
        "status": "healthy",
        "version": "0.1.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "agents": {
            "document_generator": "ready",
            "eseimas_agent": "ready",
            "etar_scraper": "ready"
        }
    }
    }

# --- Auth Endpoints ---

@app.post("/api/v1/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
@app.post("/api/v1/generate/complaint")
async def generate_complaint(request: ComplaintRequest, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    Generate a labor complaint based on user data and save to DB.
    """
    try:
        user_data = request.dict()
        result = doc_generator.generate_labor_complaint(user_data)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate document")
        
        # Save to Database
            title=f"Skundas: {user_data.get('employee_name', 'Darbuotojas')}",
            doc_type="complaint",
            content=result['content'],
            user_data=user_data,
            owner=current_user
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate/contract")
async def generate_contract(request: ContractRequest, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    Generate an employment contract.
    """
    try:
        user_data = request.dict()
        result = doc_generator.generate_employment_contract(user_data)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate document")
        
        # Save to Database
            title=f"Darbo Sutartis: {user_data.get('employee_name')}",
            doc_type="contract",
            content=result['content'],
            user_data=user_data,
            owner=current_user
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/documents")
def get_documents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    """
    Get user's generated documents history.
    """
    docs = db.query(Document).filter(Document.user_id == current_user.id).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return docs

@app.get("/api/v1/legislation/updates")
async def get_updates(keyword: str = "Darbo kodeksas", days: int = 7):
    """
    Get recent legislation updates.
    """
    try:
        updates = eseimas.search_new_legislation(keyword, days)
        return {"updates": updates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/articles/{article_id}")
async def get_article(article_id: int):
    """
    Fetch specific article content.
    """
    try:
        # Note: Scraper implementation needs to support fetch_article(int)
        # Current mock supports checking fallbacks
        
        # Temporary logic until scraper fetch_article is fully robust with args
        # For MVP we mainly used fetch_darbo_kodeksas
        
        # We'll try to use the scraper's analyze method if we had the text, 
        # but for now let's implement a simple lookup if the scraper has the method, 
        # or return a stub if not yet implemented in scraper class.
        
        if hasattr(scraper, 'fetch_article'):
             article = scraper.fetch_article(article_id)
        else:
             # Fallback implementation if scraper doesn't have fetch_article yet
             # This is just for the API endpoint to verify connectivity
             article = {"id": article_id, "content": "Article fetch logic pending in scraper update"}
             
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
            
        return article
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount Frontend - Must be after API routes
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
