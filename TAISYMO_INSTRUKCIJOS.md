# 🔧 TeisinisAI - Autentifikacijos Taisymo Instrukcijos

## 📋 Kas buvo pataisyta:

### 1. ✅ **main.py pataisymai**
- Google OAuth dabar naudoja aplinkos kintamuosius iš `.env` failo
- Pašalintas dublikuotas `access_token` kūrimas login endpoint

### 2. ✅ **Nauji įrankiai**
- `setup_db.py` - DB lentelių kūrimas
- `check_setup.py` - Visos konfigūracijos patikrinimas

---

## 🚀 Kaip paleisti:

### ŽINGSNIS 1: Patikrink konfigūraciją
```bash
cd C:\Users\setov\OneDrive\Documents\teisinis-ai
python check_setup.py
```

Šis skriptas patikrins:
- ✅ Ar .env failas turi visus reikalingus kintamuosius
- ✅ Ar įdiegti visi Python paketai
- ✅ Ar duomenų bazė veikia
- ✅ Ar Google OAuth credentials nustatyti

---

### ŽINGSNIS 2: Sukurk duomenų bazės lenteles
```bash
python setup_db.py
```

Tai sukurs `users` ir `documents` lenteles SQLite DB.

---

### ŽINGSNIS 3: Sukonfigūruok Google OAuth

**LABAI SVARBU:** Google Cloud Console reikia pridėti redirect URI!

1. Eik į: https://console.cloud.google.com/apis/credentials
2. Rask savo OAuth 2.0 Client ID
3. Spausk "EDIT" (redaguoti)
4. Dalyje "Authorized redirect URIs" pridėk:
   ```
   http://localhost:8000/api/v1/auth/google/callback
   ```
5. Spausk "SAVE"

**Pastaba:** Jei naudoji kitą portą (pvz. 8080), pakeisk URL atitinkamai.

---

### ŽINGSNIS 4: Paleisk serverį
```bash
uvicorn backend.main:app --reload
```

Arba:
```bash
python backend/main.py
```

---

## 🧪 Kaip testuoti:

### A) Testuok paprastą registraciją:
1. Atidaryk: http://localhost:8000/register.html
2. Įvesk el. paštą ir slaptažodį
3. Spausk "Registruotis"
4. Turėtum būti nukreiptas į `index.html`

### B) Testuok Google prisijungimą:
1. Atidaryk: http://localhost:8000/login.html
2. Spausk "Prisijungti su Google"
3. Pasirink Google paskyrą
4. Turėtum būti nukreiptas atgal su token

---

## 🔍 Galimos problemos ir sprendimai:

### ❌ Problema 1: "Google OAuth not configured"
**Sprendimas:** Patikrink, ar .env faile yra šios eilutės:
```env
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

**Pastaba:** Tikrus credentials gausi iš Google Cloud Console:
https://console.cloud.google.com/apis/credentials


### ❌ Problema 2: "redirect_uri_mismatch"
**Sprendimas:** Google Cloud Console turi būti pridėtas tikslus redirect URI. Žiūrėk ŽINGSNIS 3.

### ❌ Problema 3: Database table not found
**Sprendimas:** Paleisk `python setup_db.py` iš naujo.

### ❌ Problema 4: ModuleNotFoundError
**Sprendimas:** Įdiegk trūkstamus paketus:
```bash
pip install -r requirements.txt
```

### ❌ Problema 5: Port already in use
**Sprendimas:** Paleisk su kitu portu:
```bash
uvicorn backend.main:app --reload --port 8001
```
Tada atnaujink Google OAuth redirect URI į `http://localhost:8001/api/v1/auth/google/callback`

---

## 📝 Debugging patarimai:

### 1. Tikrink serverio konsoles išvestį
Serveris turėtų parodyti:
```
✅ Loaded Google Client ID: 59928... (Length: 72)
✅ Loaded Google Client Secret: GOCSP... (Length: 35)
✅ Agents initialized successfully
```


### 2. Tikrink browser console (F12)
Jei registracija/login neveikia, pažiūrėk į klaidas Console tab.

### 3. Tikrink network requests
Chrome DevTools → Network tab → tikrink ar `/api/v1/auth/register` grąžina 200 OK

---

## 🎯 Sekantys žingsniai po taisymo:

1. Ištestuok registraciją ✅
2. Ištestuok įprastą login ✅
3. Ištestuok Google OAuth login ✅
4. Ištestuok dokumentų generavimą (reikia būti prisijungusiam)

---

Jei vis dar neveikia, parašyk man konkrečią klaidos pranešimą ir aš padėsiu! 💪
