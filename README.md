# Teisinis AI - README

## 🎯 Apie Projektą

**Teisinis AI** - pilnavertis AI-powered teisinis asistentas, galintis atsakyti į bet kokius klausimus apie Lietuvos įstatymus naudojant RAG (Retrieval-Augmented Generation) sistemą ir semantinę paiešką.

## ✨ Pagrindinės Funkcijos

- 🔍 **Semantinė Paieška** - randa relevantiškiausius straipsnius pagal prasmę, ne žodžius
- 🤖 **AI Q&A** - atsakinėja į klausimus naudojant Gemini AI
- 📚 **Automatinis Citavimas** - visada nurodo šaltinius
- ⚖️ **Darbo Kodeksas** - pilnai indeksuotas (~200 straipsnių)
- 🌐 **API & Web UI** - prieinama per API arba naršyklę

## 🚀 Greitas Startas

### 1. Instaliacija

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/teisinis-ai.git
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
```

### 3. Indeksavimas

```bash
# Indeksuoti Darbo kodeksą (vienkartinė operacija)
python scripts/index_laws.py
```

### 4. Paleidimas

```bash
# Paleisti serverį
uvicorn backend.main:app --reload

# Atidaryti naršyklėje
# http://localhost:8000/qa_test.html
```

## 📖 Naudojimas

### Web UI

1. Eikite į `http://localhost:8000/qa_test.html`
2. Prisijunkite su Google
3. Užduokite klausimą, pvz: "Kaip veikia atostogos?"
4. Gaukite atsakymą su nuorodomis į straipsnius

### API

```bash
curl -X POST http://localhost:8000/api/v1/legal/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Ar galiu nutraukti darbo sutartį?",
    "top_k": 5
  }'
```

### Python

```python
from backend.agents.legal_advisor import LegalAdvisor

advisor = LegalAdvisor()
result = advisor.answer_legal_question(
    question="Kaip veikia atostogų sistema?",
    category="darbo_teisė",
    top_k=5
)

print(result['answer'])
print(f"Confidence: {result['confidence']}")
print(f"Sources: {len(result['sources'])}")
```

## 🏗️ Architektūra

```
Vartotojas → FastAPI → Legal Advisor → RAG System → ChromaDB
                                    ↓
                              Gemini 1.5 Pro
```

## 📁 Projekto Struktūra

```
teisinis-ai/
├── backend/
│   ├── agents/          # AI agentai
│   ├── rag/            # RAG sistema
│   ├── scrapers/       # Web scrapers
│   └── main.py         # FastAPI app
├── frontend/           # Web UI
├── scripts/            # Utility scripts
├── tests/              # Tests
└── data/               # Duomenų bazė
```

## 🔧 Technologijos

- **Backend**: FastAPI, Python 3.10+
- **AI**: Google Gemini 1.5 Pro
- **RAG**: ChromaDB, Sentence Transformers
- **Scraping**: BeautifulSoup, Requests
- **Auth**: Google OAuth 2.0

## 📊 Statistika

- **Indeksuota straipsnių**: ~200 (Darbo kodeksas)
- **Embedding modelis**: paraphrase-multilingual-mpnet-base-v2
- **Vektorių dimensija**: 768
- **Vidutinis atsakymo laikas**: 3-5s

## 🛣️ Roadmap

### Fazė 1: Pagrindas ✅
- [x] RAG sistema
- [x] Legal Advisor agentas
- [x] API endpoints
- [x] Darbo kodeksas

### Fazė 2: Plėtra
- [ ] Civilinis kodeksas
- [ ] Baudžiamasis kodeksas
- [ ] Administracinių nusižengimų kodeksas

### Fazė 3: Funkcionalumas
- [ ] Sutarčių analizė
- [ ] Teismų praktika
- [ ] Multi-language support

## 🐛 Žinomos Problemos

- Civilinis kodeksas turi sudėtingą struktūrą (6 knygos) - reikia custom parser
- GitHub push blocker (GH013) - reikia manual fix

## 🤝 Prisidėjimas

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 Licencija

MIT License - žiūrėkite LICENSE failą

## 📞 Kontaktai

- **Issues**: GitHub Issues
- **Email**: your.email@example.com

## 🙏 Padėkos

- Google Gemini AI
- ChromaDB
- Sentence Transformers
- e-TAR.lt

---

**Sukurta su ❤️ Lietuvoje**
