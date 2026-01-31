"""
Document Analyzer Agent
Analyzes legal documents (contracts, agreements) and identifies risks
"""

import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from typing import Dict, List
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import LegalRAG

load_dotenv()


class DocumentAnalyzer:
    """
    AI-powered document analyzer for legal contracts
    """
    
    # Contract type to legal category mapping
    CATEGORY_MAP = {
        "employment": "darbo_teisė",
        "real_estate": "nekilnojamasis_turtas",
        "family": "šeimos_teisė",
        "tax": "mokesčių_teisė",
        "general": None
    }
    
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            'gemini-1.5-pro',
            generation_config={
                'temperature': 0.1,  # Consistent contract analysis
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 3072,
            }
        )
        
        # Initialize RAG system
        self.rag = LegalRAG()
        
        print("[OK] Document Analyzer initialized")
    
    def analyze_contract(
        self,
        contract_text: str,
        contract_type: str = "general",
        language: str = "lt"
    ) -> Dict:
        """
        Analyze a contract and identify risks, missing clauses, and provide recommendations
        
        Args:
            contract_text: Full text of the contract
            contract_type: Type of contract (employment, real_estate, family, tax, general)
            language: Language of the contract (default: lt)
        
        Returns:
            {
                'summary': str,
                'contract_type': str,
                'risks': List[Dict],
                'missing_clauses': List[str],
                'recommendations': List[str],
                'relevant_laws': List[Dict],
                'confidence': str
            }
        """
        print("="*70)
        print("📄 DOCUMENT ANALYZER - ANALYZING CONTRACT")
        print("="*70)
        print(f"\nContract type: {contract_type}")
        print(f"Text length: {len(contract_text)} characters\n")
        
        # Step 1: Extract key clauses
        print("STEP 1: Extracting key clauses...")
        clauses = self._extract_clauses(contract_text)
        
        # Step 2: Find relevant laws using RAG
        print("\nSTEP 2: Finding relevant laws...")
        relevant_laws = self._find_relevant_laws(
            contract_text,
            contract_type
        )
        
        # Step 3: Analyze with AI
        print("\nSTEP 3: Analyzing with AI...")
        analysis = self._analyze_with_ai(
            contract_text,
            clauses,
            relevant_laws,
            contract_type
        )
        
        # Step 4: Calculate confidence
        confidence = self._calculate_confidence(relevant_laws, analysis)
        
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE")
        print("="*70)
        
        return {
            **analysis,
            'contract_type': contract_type,
            'relevant_laws': relevant_laws[:5],  # Top 5 most relevant
            'confidence': confidence
        }
    
    def _extract_clauses(self, contract_text: str) -> Dict:
        """Extract key clauses from contract using AI"""
        prompt = f"""Išanalizuok šią sutartį ir ištrauk pagrindines sąlygas.

SUTARTIS:
{contract_text[:3000]}

Grąžink TIKTAI JSON formatą (be jokio kito teksto):
{{
    "parties": ["Šalis 1", "Šalis 2"],
    "subject": "Sutarties dalykas",
    "price": "Kaina (jei nurodyta)",
    "duration": "Trukmė/terminas",
    "termination": "Nutraukimo sąlygos",
    "liability": "Atsakomybė"
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            text = response.text.strip()
            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            clauses = json.loads(text)
            print(f"   Extracted {len(clauses)} key clauses")
            return clauses
        except Exception as e:
            print(f"   ⚠️ Could not extract clauses: {e}")
            return {}
    
    def _find_relevant_laws(
        self,
        contract_text: str,
        contract_type: str
    ) -> List[Dict]:
        """Find relevant laws using RAG system"""
        category = self.CATEGORY_MAP.get(contract_type, None)
        
        # Use first 500 chars as query (usually contains main subject)
        query = contract_text[:500]
        
        try:
            results = self.rag.search_relevant_articles(
                query=query,
                top_k=10,
                category=category
            )
            print(f"   Found {len(results)} relevant articles")
            return results
        except Exception as e:
            print(f"   ⚠️ Could not find relevant laws: {e}")
            return []
    
    def _analyze_with_ai(
        self,
        contract_text: str,
        clauses: Dict,
        relevant_laws: List[Dict],
        contract_type: str
    ) -> Dict:
        """Perform deep analysis with AI"""
        # Build context from relevant laws
        law_context = "\n\n".join([
            f"[{i+1}] {law['law_title']}, Straipsnis {law['article_number']}: {law['article_title']}\n{law['content'][:300]}..."
            for i, law in enumerate(relevant_laws[:5])
        ]) if relevant_laws else "Nėra relevantiškų įstatymų duomenų bazėje."
        
        prompt = f"""Tu esi Lietuvos teisės ekspertas, specializuojantis sutarčių analizėje.

SUTARTIS ({contract_type}):
{contract_text[:4000]}

RELEVANTIŠKI ĮSTATYMAI:
{law_context}

UŽDUOTIS:
1. Identifikuok galimas RIZIKAS (kas gali būti problema)
2. Nurodyk TRŪKSTAMAS SĄLYGAS (ko trūksta sutartyje)
3. Pateik REKOMENDACIJAS (kaip patobulinti)
4. Parašyk trumpą SANTRAUKĄ

SVARBU:
- Būk konkretus ir aiškus
- Nurodyk konkrečius straipsnius, jei remiesi įstatymais
- Įvertink rizikos lygį: high/medium/low
- Grąžink TIKTAI JSON formatą (be markdown)

JSON FORMATAS:
{{
    "summary": "Trumpa sutarties santrauka (2-3 sakiniai)",
    "risks": [
        {{
            "risk": "Rizikos aprašymas",
            "severity": "high/medium/low",
            "explanation": "Kodėl tai rizika",
            "relevant_article": "Straipsnis (jei yra)"
        }}
    ],
    "missing_clauses": [
        "Trūkstama sąlyga 1",
        "Trūkstama sąlyga 2"
    ],
    "recommendations": [
        "Rekomendacija 1",
        "Rekomendacija 2"
    ]
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Remove markdown code blocks
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            analysis = json.loads(text)
            print(f"   Identified {len(analysis.get('risks', []))} risks")
            print(f"   Found {len(analysis.get('missing_clauses', []))} missing clauses")
            return analysis
        except Exception as e:
            print(f"   ⚠️ Analysis error: {e}")
            return {
                'summary': "Klaida analizuojant sutartį",
                'risks': [],
                'missing_clauses': [],
                'recommendations': []
            }
    
    def _calculate_confidence(
        self,
        relevant_laws: List[Dict],
        analysis: Dict
    ) -> str:
        """Calculate confidence level of the analysis"""
        # Based on:
        # 1. Number of relevant laws found
        # 2. Quality of analysis (number of risks/recommendations)
        
        laws_score = min(len(relevant_laws) / 5, 1.0)  # 0-1
        analysis_score = min(
            (len(analysis.get('risks', [])) + len(analysis.get('recommendations', []))) / 5,
            1.0
        )
        
        total_score = (laws_score + analysis_score) / 2
        
        if total_score > 0.7:
            return 'high'
        elif total_score > 0.4:
            return 'medium'
        else:
            return 'low'


# Test code
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 DOCUMENT ANALYZER TEST")
    print("="*70 + "\n")
    
    analyzer = DocumentAnalyzer()
    
    # Test contract
    test_contract = """
    DARBO SUTARTIS
    
    Sudaryta 2026-01-30, Vilniuje
    
    Tarp:
    1. UAB "Pavyzdinė Įmonė" (Darbdavys)
    2. Jonas Jonaitis (Darbuotojas)
    
    1. SUTARTIES DALYKAS
    Darbuotojas įsipareigoja dirbti Programuotojo pareigose.
    
    2. DARBO UŽMOKESTIS
    Darbuotojui mokamas 2000 EUR/mėn. atlyginimas.
    
    3. DARBO LAIKAS
    Darbuotojas dirba 40 val./savaitę.
    
    4. KITOS SĄLYGOS
    Sutartis galioja nuo 2026-02-01.
    """
    
    result = analyzer.analyze_contract(
        contract_text=test_contract,
        contract_type="employment"
    )
    
    print("\n📊 ANALYSIS RESULTS:")
    print("-"*70)
    print(f"\nSummary: {result['summary']}")
    print(f"\nConfidence: {result['confidence']}")
    print(f"\nRisks ({len(result['risks'])}):")
    for risk in result['risks']:
        print(f"  - [{risk['severity'].upper()}] {risk['risk']}")
    print(f"\nMissing Clauses ({len(result['missing_clauses'])}):")
    for clause in result['missing_clauses']:
        print(f"  - {clause}")
    print(f"\nRecommendations ({len(result['recommendations'])}):")
    for rec in result['recommendations']:
        print(f"  - {rec}")
    print(f"\nRelevant Laws: {len(result['relevant_laws'])}")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)
