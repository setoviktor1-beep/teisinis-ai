"""
Script to index laws into the RAG vector database
Run this to populate the knowledge base
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag.vector_store import LegalRAG
from backend.scrapers.etar_scraper import ETARScraper


def index_darbo_kodeksas():
    """Index Darbo kodeksas from existing data"""
    print("\n" + "="*70)
    print("📚 INDEXING DARBO KODEKSAS")
    print("="*70 + "\n")
    
    rag = LegalRAG()
    scraper = ETARScraper()
    
    # Check if we have cached data
    if not os.path.exists('data/darbo_kodeksas_text.txt'):
        print("⏳ Fetching Darbo kodeksas from e-TAR...")
        scraper.fetch_darbo_kodeksas()
    
    # Load the full text
    with open('data/darbo_kodeksas_text.txt', 'r', encoding='utf-8') as f:
        full_text = f.read()
    
    # Parse into articles
    import re
    article_pattern = re.compile(r'(\d+)\s+straipsnis[.\s]+([^\n]+)', re.IGNORECASE)
    matches = list(article_pattern.finditer(full_text))
    
    articles = []
    for i, match in enumerate(matches):
        article_num = match.group(1)
        article_title = match.group(2).strip()
        
        # Extract content until next article
        start = match.end()
        if i < len(matches) - 1:
            end = matches[i + 1].start()
        else:
            end = start + 2000  # Last article
        
        content = full_text[start:end].strip()
        
        # Limit content length
        if len(content) > 2000:
            content = content[:2000] + "..."
        
        articles.append({
            'number': article_num,
            'title': article_title,
            'content': content
        })
    
    print(f"📊 Parsed {len(articles)} articles")
    
    # Create law data structure
    law_data = {
        'law_id': 'TAIS.dad7f3307a7011e6b969d7ae07280e89',
        'title': 'Lietuvos Respublikos darbo kodeksas',
        'category': 'darbo_teisė',
        'articles': articles
    }
    
    # Index into RAG
    rag.index_law(law_data)
    
    # Show stats
    stats = rag.get_collection_stats()
    print(f"\n📈 Total articles in database: {stats['total_articles']}")
    
    print("\n" + "="*70)
    print("✅ DARBO KODEKSAS INDEXED SUCCESSFULLY")
    print("="*70)


def index_civilinis_kodeksas():
    """Index Civilinis kodeksas (placeholder for future implementation)"""
    print("\n⚠️ Civilinis kodeksas indexing not yet implemented")
    print("   Will be added in Phase 2")


if __name__ == "__main__":
    print("\n🚀 LEGAL KNOWLEDGE BASE INDEXER\n")
    
    # Index Darbo kodeksas
    index_darbo_kodeksas()
    
    # Future: index other codes
    # index_civilinis_kodeksas()
    # index_baudziamasis_kodeksas()
    
    print("\n✅ All indexing complete!")
