"""
Universal Legal Advisor Agent
Answers legal questions using RAG-powered semantic search
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Dict, Optional, List
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.rag.vector_store import LegalRAG

load_dotenv()


class LegalAdvisor:
    """
    AI-powered legal advisor that can answer questions about any Lithuanian law
    """
    
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            'gemini-1.5-pro',
            generation_config={
                'temperature': 0.1,  # Very deterministic for legal accuracy
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
        )
        
        # Initialize RAG system
        self.rag = LegalRAG()
        
        print("[OK] Legal Advisor initialized")
    
    def answer_legal_question(
        self, 
        question: str, 
        category: Optional[str] = None,
        top_k: int = 5
    ) -> Dict:
        """
        Answer a legal question using RAG + Gemini
        
        Args:
            question: User's legal question
            category: Optional legal category filter
            top_k: Number of relevant articles to retrieve
        
        Returns:
            {
                'answer': str,
                'sources': List[Dict],
                'confidence': str,
                'category': str
            }
        """
        print("="*70)
        print("⚖️ LEGAL ADVISOR - ANSWERING QUESTION")
        print("="*70)
        print(f"\n❓ Question: {question}\n")
        
        # Step 1: RAG Search - Find relevant articles
        print("STEP 1: Searching for relevant legal articles...\n")
        relevant_articles = self.rag.search_relevant_articles(
            query=question,
            top_k=top_k,
            category=category
        )
        
        if not relevant_articles:
            return {
                'answer': "Atsiprašau, nepavyko rasti relevantišk ų įstatymų straipsnių šiam klausimui. Galbūt duomenų bazė dar neturi reikiamų įstatymų.",
                'sources': [],
                'confidence': 'low',
                'category': category or 'unknown'
            }
        
        # Step 2: Build context from retrieved articles
        print("STEP 2: Building legal context...\n")
        context = self._build_context(relevant_articles)
        
        # Step 3: Generate answer with Gemini
        print("STEP 3: Generating AI-powered answer...\n")
        prompt = self._build_prompt(question, context, relevant_articles)
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text
        except Exception as e:
            print(f"❌ Gemini API Error: {e}")
            return {
                'answer': f"Klaida generuojant atsakymą: {str(e)}",
                'sources': relevant_articles,
                'confidence': 'error',
                'category': category or 'unknown'
            }
        
        # Step 4: Calculate confidence based on article relevance
        confidence = self._calculate_confidence(relevant_articles)
        
        print("="*70)
        print("✅ ANSWER GENERATED")
        print("="*70)
        
        return {
            'answer': answer,
            'sources': relevant_articles,
            'confidence': confidence,
            'category': category or self._detect_category(relevant_articles)
        }
    
    def _build_context(self, articles: List[Dict]) -> str:
        """Build formatted legal context from retrieved articles"""
        context_parts = []
        
        for i, article in enumerate(articles, 1):
            context_parts.append(
                f"[{i}] {article['law_title']}\n"
                f"    Straipsnis {article['article_number']}: {article['article_title']}\n"
                f"    {article['content']}\n"
            )
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str, articles: List[Dict]) -> str:
        """Build the prompt for Gemini"""
        return f"""Tu esi Lietuvos teisės ekspertas. Tavo užduotis - atsakyti į klausimą remiantis pateiktais įstatymų straipsniais.

SVARBU:
- Atsakyk TIKTAI remiantis pateiktais straipsniais
- Nurodyk konkrečius straipsnius, kuriais remiesi
- Jei straipsniai nepakankami atsakymui - pasakyk tai
- Atsakymas turi būti aiškus ir suprantamas ne teisininkui
- Naudok lietuvių kalbą

RELEVANTIŠKI ĮSTATYMŲ STRAIPSNIAI:
{context}

KLAUSIMAS:
{question}

ATSAKYMAS (su nuorodomis į straipsnius):"""
    
    def _calculate_confidence(self, articles: List[Dict]) -> str:
        """
        Calculate confidence level based on article relevance scores
        
        Returns: 'high', 'medium', or 'low'
        """
        if not articles:
            return 'low'
        
        # Check distance scores (lower is better in cosine distance)
        avg_distance = sum(a.get('distance', 1.0) for a in articles) / len(articles)
        
        if avg_distance < 0.3:
            return 'high'
        elif avg_distance < 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _detect_category(self, articles: List[Dict]) -> str:
        """Detect the most common category from retrieved articles"""
        if not articles:
            return 'unknown'
        
        categories = [a['metadata'].get('category', 'unknown') for a in articles]
        # Return most common category
        return max(set(categories), key=categories.count)
    
    def get_stats(self) -> Dict:
        """Get statistics about the knowledge base"""
        return self.rag.get_collection_stats()


# Test code
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 LEGAL ADVISOR TEST")
    print("="*70 + "\n")
    
    try:
        advisor = LegalAdvisor()
        
        # Note: This test will fail if RAG database is empty
        # First need to index some laws using the indexing script
        
        stats = advisor.get_stats()
        print(f"📊 Knowledge base stats: {stats}\n")
        
        if stats['total_articles'] > 0:
            # Test question
            result = advisor.answer_legal_question(
                question="Kaip galiu nutraukti darbo sutartį?",
                category=None
            )
            
            print("\n📋 RESULT:")
            print("-"*70)
            print(f"Answer: {result['answer'][:200]}...")
            print(f"Confidence: {result['confidence']}")
            print(f"Sources: {len(result['sources'])} articles")
            print("-"*70)
        else:
            print("⚠️ Knowledge base is empty. Please index laws first.")
        
        print("\n✅ LEGAL ADVISOR TEST COMPLETED")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
