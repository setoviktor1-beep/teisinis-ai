# 🏛️ Teisinis AI - Legal AI Assistant

Dirbtinio intelekto sistema, skirta Lietuvos teisinių dokumentų analizei ir konsultacijoms.

## 🚀 Funkcijos

- 📄 Automatinis teisinių dokumentų scraping iš e-seimas.lt
- 🤖 AI-powered teisinės konsultacijos naudojant Google Gemini
- 🔍 Pažangi paieška teisės aktuose
- 💬 Interaktyvus chat su teisiniu asistentu

## 🛠️ Technologijos

- **Backend**: FastAPI + Python 3.12
- **AI**: Google Gemini API
- **Web Scraping**: BeautifulSoup4
- **Database**: PostgreSQL (planuojama)
- **Payment**: Stripe Integration

## 📦 Instalacija

```bash
# Clone repository
git clone https://github.com/setovikor1-beep/teisinis-ai.git
cd teisinis-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env
# Edit .env with your API keys
```

## ⚙️ Konfigūracija

Sukurkite `.env` failą su šiais parametrais:

```env
GEMINI_API_KEY=your_gemini_api_key
STRIPE_SECRET_KEY=your_stripe_key
DATABASE_URL=postgresql://user:password@localhost/teisinis_ai
ENVIRONMENT=development
```

## 🚀 Paleidimas

```bash
# Activate virtual environment
venv\Scripts\activate

# Run FastAPI server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API bus pasiekiama: http://localhost:8000

## 📚 API Dokumentacija

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 Licencija

MIT License
