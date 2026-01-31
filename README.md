# Teisinis AI - AI-Powered Teisinis Asistentas 🤖⚖️

## 🎯 Apie Projektą

**Teisinis AI** - pilnavertis AI-powered teisinis asistentas, skirtas Lietuvos teisei. Sistema naudoja **Gemini 1.5 Pro**, **RAG** sistemą, ir **real-time e-TAR.lt** integraciją teikti tikslius, deterministiškus teisinius patarimus.

## ✨ Pagrindinės Funkcijos

- 🔍 **Legal Q&A** - Atsakymai į teisinius klausimus su AI
- 📄 **Contract Analysis** - Sutarčių analizė su rizikų identifikavimu
- 🔄 **Smart Caching** - Dinamiškas įstatymų fetching iš e-TAR (24h cache)
- 🚦 **Rate Limiting** - API apsauga (15 req/min)
- 🌡️ **Temperature 0.1** - Deterministiški, konsistenčiški atsakymai
- 🔐 **Google OAuth** - Saugus prisijungimas
- 📚 **Darbo Kodeksas** - Pilnai integruotas (~200 straipsnių)

## 🚀 Greitas Startas

### 1. Instaliacija

```bash
# Clone repository
git clone https://github.com/setoviktor1-beep/teisinis-ai-new.git
cd teisinis-ai

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigūracija

Sukurkite `.env` failą:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://user:password@localhost/teisinis_ai
```

### 3. Paleidimas

```bash
# Paleisti serverį
uvicorn backend.main:app --reload

# Atidaryti naršyklėje
# http://localhost:8000
```

## 📖 Naudojimas

### Web UI

**Legal Q&A**: `http://localhost:8000/qa_test.html`
```
1. Prisijunkite su Google
2. Užduokite klausimą: "Kaip veikia atostogos?"
3. Gaukite atsakymą su šaltiniais
```

**Contract Analyzer**: `http://localhost:8000/contract_analyzer.html`
```
1. Įklijuokite sutarties tekstą
2. Pasirinkite tipą (employment, real_estate, etc.)
3. Gaukite analizę su rizikomis ir rekomendacijomis
```

### API

**Legal Q&A**:
```bash
curl -X POST http://localhost:8000/api/v1/legal/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Ar galiu nutraukti darbo sutartį?",
    "category": "darbo_teisė"
  }'
```

**Contract Analysis**:
```bash
curl -X POST http://localhost:8000/api/v1/legal/analyze-contract \
  -H "Content-Type: application/json" \
  -d '{
    "contract_text": "DARBO SUTARTIS...",
    "contract_type": "employment"
  }'
```

## 🏗️ Architektūra

### System Flow

```
Vartotojas → FastAPI → Legal Advisor
                           ↓
                    Smart Fetcher
                    ↓         ↓
                Cache ←→ e-TAR.lt
                    ↓
              Gemini 1.5 Pro (temp=0.1)
                    ↓
                Atsakymas
```

### Tech Stack

**Backend**:
- FastAPI (Python 3.11+)
- Google Gemini 1.5 Pro
- ChromaDB (RAG)
- SQLite (Cache)
- PostgreSQL (Users)
- BeautifulSoup4 (Scraping)

**Frontend**:
- HTML5 + CSS3
- Vanilla JavaScript
- Google OAuth 2.0

**AI/ML**:
- Sentence Transformers
- RAG (Retrieval-Augmented Generation)
- Temperature 0.1 (deterministic)

## 📁 Projekto Struktūra

```
teisinis-ai/
├── backend/
│   ├── agents/              # AI agentai
│   │   ├── legal_advisor.py      # Q&A agentas
│   │   ├── document_analyzer.py  # Sutarčių analizė
│   │   ├── smart_fetcher.py      # e-TAR + cache
│   │   └── document_generator.py
│   ├── cache/               # Cache sistema
│   │   ├── cache_manager.py
│   │   └── schema.sql
│   ├── middleware/          # Middleware
│   │   └── rate_limiter.py
│   ├── rag/                 # RAG sistema
│   │   └── vector_store.py
│   ├── scrapers/            # Web scrapers
│   │   └── etar_scraper.py
│   └── main.py              # FastAPI app
├── frontend/                # Web UI
│   ├── index.html
│   ├── qa_test.html
│   ├── contract_analyzer.html
│   └── login.html
├── data/                    # Duomenų bazės
│   ├── legal_cache.db       # SQLite cache
│   └── chroma_db/           # ChromaDB
└── scripts/                 # Utility scripts
```

## 🔧 Phase 3.5: Smart Caching Sistema

### Problema
Įstatymai dažnai keičiasi. Statinis RAG greitai paseno.

### Sprendimas
**Hybrid Approach**: Real-time e-TAR + Smart Caching

**Funkcionalumas**:
- ✅ Automatinis cache check
- ✅ Real-time e-TAR fetching
- ✅ 24h TTL
- ✅ Batch article caching
- ✅ Law detection from questions
- ✅ RAG fallback

**Performance**:
- Cache HIT: <100ms
- Cache MISS: 2-5s (e-TAR fetch)
- Rate limit: 15 req/min

## 📊 Statistika

- **Indeksuota straipsnių**: ~200 (Darbo kodeksas)
- **Cache TTL**: 24 hours
- **API endpoints**: 15+
- **Agentai**: 4
- **Kodo eilučių**: ~5000+

## 🛣️ Roadmap

### ✅ Baigta (Phase 1-3.5)
- [x] RAG sistema
- [x] Legal Advisor
- [x] Document Analyzer
- [x] Smart Caching
- [x] Rate Limiting
- [x] Temperature 0.1
- [x] Google OAuth
- [x] Darbo kodeksas

### 🚧 Planuojama
- [ ] Background job (versijų tikrinimas)
- [ ] Frontend kategorijų sistema
- [ ] Civilinis kodeksas
- [ ] Mokesčių įstatymai
- [ ] Unit testai
- [ ] Docker deployment

## 🐛 Žinomos Problemos

- GitHub push protection (GH013) - reikia manual workaround
- Civilinis kodeksas - sudėtinga struktūra (6 knygos)

## 🤝 Prisidėjimas

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 Licencija

MIT License

## 🙏 Padėkos

- Google Gemini AI
- ChromaDB
- Sentence Transformers
- e-TAR.lt

---

**Sukurta su ❤️ Lietuvoje**

*Last updated: 2026-01-31 - Phase 3.5 Complete*
