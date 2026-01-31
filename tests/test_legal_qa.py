"""
Test the Legal Advisor Q&A functionality
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.legal_advisor import LegalAdvisor


def test_legal_qa():
    """Test the legal Q&A system"""
    print("\n" + "="*70)
    print("🧪 TESTING LEGAL Q&A SYSTEM")
    print("="*70 + "\n")
    
    # Initialize advisor
    advisor = LegalAdvisor()
    
    # Check stats
    stats = advisor.get_stats()
    print("📊 Knowledge Base Stats:")
    print(f"   Total articles indexed: {stats['total_articles']}")
    print()
    
    if stats['total_articles'] == 0:
        print("❌ No articles in database. Please run index_laws.py first.")
        return
    
    # Test questions
    test_questions = [
        "Kaip galiu nutraukti darbo sutartį?",
        "Kokios yra mano teisės dėl atostogų?",
        "Ar galiu dirbti nuotoliniu būdu?",
        "Kas yra bandomasis laikotarpis?",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print("="*70)
        print(f"TEST {i}/{len(test_questions)}")
        print("="*70)
        print(f"\n❓ Klausimas: {question}\n")
        
        try:
            result = advisor.answer_legal_question(question, top_k=3)
            
            print(f"\n📊 Confidence: {result['confidence'].upper()}")
            print(f"📚 Sources found: {len(result['sources'])}")
            print("\n💡 Atsakymas:")
            print('-'*70)
            print(result['answer'][:500] + "..." if len(result['answer']) > 500 else result['answer'])
            print('-'*70)
            
            print("\n📖 Šaltiniai:")
            for j, source in enumerate(result['sources'][:3], 1):
                print(f"   {j}. {source['law_title']} - Str. {source['article_number']}")
                print(f"      {source['article_title'][:80]}...")
            
            print(f"\n✅ TEST {i} PASSED\n")
            
        except Exception as e:
            print(f"\n❌ TEST {i} FAILED: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    test_legal_qa()
