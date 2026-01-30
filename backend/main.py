import os
import sys
import traceback
from datetime import timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

load_dotenv()

# Ensure project root is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Local imports (must be after sys.path hack)
from backend import auth  # noqa: E402
from backend.agents.document_generator import DocumentGenerator  # noqa: E402
from backend.agents.eseimas_agent import ESeimasAgent  # noqa: E402
from backend.database import Base, engine, get_db  # noqa: E402
from backend.models import Document, User  # noqa: E402
from backend.scrapers.etar_scraper import ETARScraper  # noqa: E402

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

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"🔥 UNHANDLED EXCEPTION: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

# SessionMiddleware (Required for OAuth)
if not os.getenv("SECRET_KEY"):
    raise RuntimeError("SECRET_KEY must be set in .env file")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
    same_site="lax",
    https_only=False
)

# OAuth Configuration
oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    client_kwargs={
        'scope': 'openid email profile',
        'token_endpoint_auth_method': 'client_secret_post'
    }
)

# DEBUG: Print loaded config (masked)
print(f"[OK] Loaded Google Client ID: {os.getenv('GOOGLE_CLIENT_ID')[:10]}... (Length: {len(os.getenv('GOOGLE_CLIENT_ID') or '')})")
print(f"[OK] Loaded Google Client Secret: {os.getenv('GOOGLE_CLIENT_SECRET')[:5]}... (Length: {len(os.getenv('GOOGLE_CLIENT_SECRET') or '')})")

# Initialize Agents
try:
    doc_generator = DocumentGenerator()
    eseimas = ESeimasAgent()
    scraper = ETARScraper()
    print("[OK] Agents initialized successfully")
except Exception as e:
    print(f"[ERROR] Failed to initialize agents: {e}")
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

# --- Auth Endpoints ---

@app.post("/api/v1/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):  # noqa: B008
    try:
        # Validate email format (basic check)
        if not user.email or '@' not in user.email:
            raise HTTPException(status_code=400, detail="Invalid email format")

        # Validate password length
        if not user.password or len(user.password) < 4:
            raise HTTPException(status_code=400, detail="Password must be at least 4 characters")

        # Bcrypt limit is 72 bytes, warn if password is too long
        password_bytes = user.password.encode('utf-8')
        if len(password_bytes) > 72:
            raise HTTPException(status_code=400, detail="Password is too long (maximum 72 bytes). Please use a shorter password.")

        # Check if user already exists
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        hashed_password = auth.get_password_hash(user.password)
        db_user = User(email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Generate access token
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}") from e

@app.post("/api/v1/auth/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):  # noqa: B008
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

@app.get("/api/v1/auth/google")
async def login_google(request: Request):
    if not os.getenv('GOOGLE_CLIENT_ID') or not os.getenv('GOOGLE_CLIENT_SECRET'):
         raise HTTPException(status_code=500, detail="Google OAuth not configured (missing env vars)")

    # Use fixed Redirect URI from env to prevent state mismatch
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    if not redirect_uri:
        # Fallback for safety, but printing warning
        print("[WARNING] GOOGLE_REDIRECT_URI not set, using request.base_url (might cause state mismatch)")
        base_url = str(request.base_url).rstrip('/')
        redirect_uri = f"{base_url}/api/v1/auth/google/callback"

    print(f"[DEBUG] Google Login Init. Redirect URI: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/api/v1/auth/google/callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):  # noqa: B008
    try:
        token = await oauth.google.authorize_access_token(request)
        print(f"[DEBUG] Token received. Access Token present: {bool(token)}")

        # Fetch user info from Google using the token directly (more robust)
        user_info = await oauth.google.userinfo(token=token)
        print(f"[DEBUG] User info received: {user_info.get('email')}")

        email = user_info.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Google account has no email")

        # Check if user exists
        db_user = db.query(User).filter(User.email == email).first()
        if not db_user:
            # Create new user
            db_user = User(email=email, hashed_password=None) # No password for Google users
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        # Generate JWT
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )

        # Redirect to frontend with token
        return RedirectResponse(url=f"/index.html?token={access_token}")

    except Exception as e:
        error_msg = str(e)
        print(f"OAuth error: {error_msg}")
        traceback.print_exc()

        # Provide more helpful error messages
        if "invalid_client" in error_msg.lower():
            detail = "Google OAuth invalid_client error. Please verify:\n1. Client ID in .env matches Google Console exactly\n2. Client Secret in .env matches Google Console exactly\n3. Redirect URI in Google Console: http://localhost:8000/api/v1/auth/google/callback\n4. JavaScript origins in Google Console: http://localhost:8000\n\nNote: Changes in Google Console may take a few minutes to propagate."
        elif "redirect_uri_mismatch" in error_msg.lower():
            detail = "Redirect URI mismatch. In Google Console, add exactly: http://localhost:8000/api/v1/auth/google/callback"
        elif "mismatching_state" in error_msg.lower():
             detail = "OAuth State Mismatch. This usually happens if:\n1. You are mixing 'localhost' and '127.0.0.1'. Use 'http://localhost:8000' consistently.\n2. Session cookies are blocked or cleared. Try incognito mode.\n3. The server restarted during the login process."
        else:
            detail = f"OAuth failed: {error_msg}"

        return JSONResponse(
            status_code=500,
            content={"error": "Google OAuth failed", "detail": detail}
        )
@app.post("/api/v1/generate/complaint")
async def generate_complaint(request: ComplaintRequest, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):  # noqa: B008
    """
    Generate a labor complaint based on user data and save to DB.
    """
    try:
        user_data = request.dict()
        result = doc_generator.generate_labor_complaint(user_data)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate document")
        
        # Save to Database
        db_doc = Document(
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
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/api/v1/generate/contract")
async def generate_contract(request: ContractRequest, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):  # noqa: B008
    """
    Generate an employment contract.
    """
    try:
        user_data = request.dict()
        result = doc_generator.generate_employment_contract(user_data)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate document")
        
        # Save to Database
        db_doc = Document(
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
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/api/v1/documents")
def get_documents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):  # noqa: B008
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
        raise HTTPException(status_code=500, detail=str(e)) from e

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
        raise HTTPException(status_code=500, detail=str(e)) from e

# Mount Frontend - Must be after API routes
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
