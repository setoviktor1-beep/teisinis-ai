"""
Script to index Civilinis kodeksas into RAG system
"""

import sys
import os
import re

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag.vector_store import LegalRAG
from backend.scrapers.etar_scraper import ETARScraper


def index_civilinis_kodeksas():
    """Fetch and index Civilinis kodeksas"""
    print("\n" + "="*70)
    print("📚 INDEXING CIVILINIS KODEKSAS")
    print("="*70 + "\n")
    
    rag = LegalRAG()
    scraper = ETARScraper()
    
    # Civilinis kodeksas TAIS ID
    tais_id = "TAIS.245495"
    
    # Check if we have cached data
    cache_file = 'data/tais_245495_text.txt'
    
    if not os.path.exists(cache_file):
        print("⏳ Fetching Civilinis kodeksas from e-TAR...")
        result = scraper.fetch_law_by_id(tais_id, "Civilinis kodeksas")
        
        if not result:
            print("❌ Failed to fetch Civilinis kodeksas")
            return False
    else:
        print("✅ Using cached Civilinis kodeksas data")
    
    # Load the full text
    with open(cache_file, 'r', encoding='utf-8') as f:
        full_text = f.read()
    
    print(f"📊 Text length: {len(full_text):,} characters")
    
    # Parse into articles
    # Civilinis kodeksas uses format: "1.1 straipsnis", "2.15 straipsnis", etc.
    article_pattern = re.compile(
        r'(\d+\.\d+)\s+straipsnis[.\s]+([^\n]+)',
        re.IGNORECASE
    )
    matches = list(article_pattern.finditer(full_text))
    
    print(f"📊 Found {len(matches)} article headers")
    
    articles = []
    for i, match in enumerate(matches):
        article_num = match.group(1)
        article_title = match.group(2).strip()
        
        # Extract content until next article
        start = match.end()
        if i < len(matches) - 1:
            end = matches[i + 1].start()
        else:
            end = min(start + 3000, len(full_text))
        
        content = full_text[start:end].strip()
        
        # Limit content length for embedding
        if len(content) > 2000:
            content = content[:2000] + "..."
        
        # Skip very short articles (likely parsing errors)
        if len(content) < 50:
            continue
        
        articles.append({
            'number': article_num,
            'title': article_title,
            'content': content
        })
    
    print(f"📊 Parsed {len(articles)} valid articles")
    
    if len(articles) < 10:
        print("⚠️ Too few articles parsed, might be a parsing issue")
        print("Trying alternative pattern...")
        
        # Alternative: just numbered articles
        article_pattern_alt = re.compile(
            r'(\d+)\s+straipsnis[.\s]+([^\n]+)',
            re.IGNORECASE
        )
        matches_alt = list(article_pattern_alt.finditer(full_text))
        
        if len(matches_alt) > len(matches):
            print(f"✅ Alternative pattern found {len(matches_alt)} articles")
            articles = []
            for i, match in enumerate(matches_alt[:500]):  # Limit to first 500
                article_num = match.group(1)
                article_title = match.group(2).strip()
                
                start = match.end()
                if i < len(matches_alt) - 1:
                    end = matches_alt[i + 1].start()
                else:
                    end = min(start + 3000, len(full_text))
                
                content = full_text[start:end].strip()
                
                if len(content) > 2000:
                    content = content[:2000] + "..."
                
                if len(content) >= 50:
                    articles.append({
                        'number': article_num,
                        'title': article_title,
                        'content': content
                    })
    
    print(f"📊 Final article count: {len(articles)}")
    
    # Create law data structure
    law_data = {
        'law_id': tais_id,
        'title': 'Lietuvos Respublikos civilinis kodeksas',
        'category': 'civilinė_teisė',
        'articles': articles
    }
    
    # Index into RAG
    print("\n⏳ Indexing into RAG system...")
    rag.index_law(law_data)
    
    # Show stats
    stats = rag.get_collection_stats()
    print(f"\n📈 Total articles in database: {stats['total_articles']}")
    
    print("\n" + "="*70)
    print("✅ CIVILINIS KODEKSAS INDEXED SUCCESSFULLY")
    print("="*70)
    
    return True


if __name__ == "__main__":
    print("\n🚀 CIVILINIS KODEKSAS INDEXER\n")
    
    success = index_civilinis_kodeksas()
    
    if success:
        print("\n✅ Indexing complete! Restart the server to use the new data.")
    else:
        print("\n❌ Indexing failed. Check errors above.")
