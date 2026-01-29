def get_labor_complaint_prompt(user_data, legal_context):
    """
    Generate prompt for labor complaint document
    
    Args:
        user_data (dict): User's complaint details
        legal_context (str): Relevant legal articles
        
    Returns:
        str: Formatted prompt for Gemini
    """
    
    system_instruction = """Tu esi profesionalus Lietuvos teisės dokumentų specialistas.

Tavo užduotis: parašyti formalų, teisinį skundą Valstybinei darbo inspekcijai.

REIKALAVIMAI:
- Naudok formalų, oficialų stilių
- Cituok konkrečius Darbo kodekso straipsnius
- Struktūra: antraštė, faktai, teisiniai pagrindai, prašymas
- Lietuvių kalba, teisinė terminologija
- Be jokių papildomų komentarų - tik dokumentas
"""

    prompt = f"""{system_instruction}

TEISINIAI PAGRINDAI:
{legal_context}

FAKTINĖ SITUACIJA:
Darbuotojas: {user_data.get('employee_name', 'Jonas Jonaitis')}
Darbdavys: {user_data.get('employer_name', 'UAB "Pavyzdys"')}
Darbo vieta: {user_data.get('workplace', 'Vilnius')}

Pažeidimo aprašymas:
{user_data.get('violation_description', 'Darbdavys atsisako leisti dirbti nuotoliniu būdu, nors darbo pobūdis tai leidžia.')}

Data nuo kada trunka: {user_data.get('violation_date', '2024-01-15')}

SUGENERUOK:
Formalų skundą Valstybinei darbo inspekcijai, kuriame:
1. Nurodomas pareiškėjas ir atsakovas
2. Aprašomi faktai
3. Nurodomi pažeisti Darbo kodekso straipsniai
4. Pateikiamas prašymas (ištirti situaciją, imtis veiksmų)

Dokumentas turi būti paruoštas siuntimui - pilnas ir oficialus.
"""
    
    return prompt


def get_system_prompt():
    """
    Get general system prompt for legal AI
    """
    return """Tu esi AI asistentas, specializuojantis Lietuvos teisėje.

Tavo tikslas:
- Teikti tikslią teisinę informaciją
- Cituoti konkrečius teisės aktus
- Padėti formuoti dokumentus

SVARBU:
- Visada nurodyk šaltinius (Darbo kodeksas, straipsnio numeris)
- Jei nežinai - pasakyk
- Tai teisinė informacija, ne patarimai (disclaimer)
"""
