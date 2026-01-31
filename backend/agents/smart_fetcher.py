"""
Smart Legal Fetcher Agent
Intelligently fetches laws from e-TAR with caching
"""

import sys
import os
import re
from typing import Dict, Optional, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.cache.cache_manager import CacheManager
from backend.scrapers.etar_scraper import ETARScraper


class SmartLegalFetcher:
    """
    Intelligent agent that fetches laws from e-TAR with smart caching
    """

    # Known laws mapping (name -> TAIS ID)
    KNOWN_LAWS = {
        'darbo_kodeksas': 'TAIS.245495',
        'darbo kodeksas': 'TAIS.245495',
        'dk': 'TAIS.245495',
        # Add more as needed
    }

    def __init__(self):
        """Initialize Smart Legal Fetcher"""
        self.cache = CacheManager()
        self.scraper = ETARScraper()
        print("[OK] Smart Legal Fetcher initialized")

    def get_law(
        self,
        law_identifier: str,
        force_refresh: bool = False
    ) -> Optional[Dict]:
        """
        Get law by ID or name, with smart caching

        Args:
            law_identifier: TAIS ID or law name
            force_refresh: Force fetch from e-TAR

        Returns:
            Law data with full text
        """
        # Resolve law ID
        law_id = self._resolve_law_id(law_identifier)
        if not law_id:
            print(f"❌ Unknown law: {law_identifier}")
            return None

        # Check cache first (unless force refresh)
        if not force_refresh:
            cached = self.cache.get_law(law_id)
            if cached:
                print(f"✅ Cache HIT: {law_id}")
                return cached

        # Cache miss - fetch from e-TAR
        print(f"🔍 Cache MISS: Fetching {law_id} from e-TAR...")
        law_data = self.scraper.fetch_law_by_id(law_id)

        if not law_data:
            print(f"❌ Failed to fetch law from e-TAR: {law_id}")
            return None

        # Parse articles
        articles = self._parse_articles(law_data['full_text'])

        # Cache the law
        self.cache.cache_law(
            law_id=law_id,
            title=law_data['title'],
            full_text=law_data['full_text'],
            version=law_data.get('fetched_at', 'unknown'),
            metadata={'url': law_data.get('url')},
            ttl_hours=24
        )

        # Cache individual articles
        if articles:
            articles_to_cache = [
                {
                    'law_id': law_id,
                    'article_number': article['number'],
                    'article_title': article['title'],
                    'content': article['content']
                }
                for article in articles
            ]
            self.cache.cache_articles_batch(articles_to_cache)

        return law_data

    def get_article(
        self,
        law_identifier: str,
        article_number: str
    ) -> Optional[Dict]:
        """
        Get specific article with caching

        Args:
            law_identifier: TAIS ID or law name
            article_number: Article number

        Returns:
            Article data
        """
        law_id = self._resolve_law_id(law_identifier)
        if not law_id:
            return None

        # Try cache first
        cached = self.cache.get_article(law_id, article_number)
        if cached:
            print(f"✅ Article cache HIT: {law_id} - {article_number}")
            return cached

        # Not in cache - fetch full law
        law = self.get_law(law_id)
        if not law:
            return None

        # Try cache again (should be there now)
        return self.cache.get_article(law_id, article_number)

    def search_articles(
        self,
        query: str,
        law_identifier: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search for relevant articles

        Args:
            query: Search query
            law_identifier: Optional specific law to search in
            top_k: Number of results to return

        Returns:
            List of relevant articles
        """
        # If specific law, search in that law
        if law_identifier:
            law = self.get_law(law_identifier)
            if not law:
                return []

            articles = self._parse_articles(law['full_text'])
            # Simple relevance scoring
            scored = []
            for article in articles:
                score = self._calculate_relevance(query, article)
                if score > 0:
                    scored.append((score, article))

            scored.sort(reverse=True, key=lambda x: x[0])
            return [article for _, article in scored[:top_k]]

        # TODO: Search across all cached laws
        return []

    def _resolve_law_id(self, identifier: str) -> Optional[str]:
        """
        Resolve law name to TAIS ID

        Args:
            identifier: TAIS ID or law name

        Returns:
            TAIS ID or None
        """
        # If already TAIS ID
        if identifier.startswith('TAIS.'):
            return identifier

        # Try known laws
        identifier_lower = identifier.lower().strip()
        return self.KNOWN_LAWS.get(identifier_lower)

    def _parse_articles(self, full_text: str) -> List[Dict]:
        """
        Parse law text into articles

        Args:
            full_text: Full text of the law

        Returns:
            List of article dicts
        """
        articles = []

        # Pattern: "Straipsnis 123. Title\nContent"
        # More flexible pattern to handle various formats
        pattern = r'(?:^|\n)Straipsnis\s+(\d+(?:\.\d+)?)\.\s+([^\n]+)\n(.*?)(?=\n(?:Straipsnis\s+\d+|$))'

        matches = re.finditer(pattern, full_text, re.DOTALL | re.MULTILINE)

        for match in matches:
            articles.append({
                'number': match.group(1),
                'title': match.group(2).strip(),
                'content': match.group(3).strip()
            })

        if not articles:
            print(f"⚠️ No articles parsed from text (length: {len(full_text)})")

        return articles

    def _calculate_relevance(self, query: str, article: Dict) -> float:
        """
        Simple relevance scoring

        Args:
            query: Search query
            article: Article dict

        Returns:
            Relevance score (0-1)
        """
        query_lower = query.lower()
        text = f"{article['title']} {article['content']}".lower()

        # Count query word matches
        query_words = query_lower.split()
        matches = sum(1 for word in query_words if word in text)

        return matches / len(query_words) if query_words else 0

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return self.cache.get_stats()

    def invalidate_law(self, law_identifier: str):
        """Invalidate cached law"""
        law_id = self._resolve_law_id(law_identifier)
        if law_id:
            self.cache.invalidate_law(law_id)


# Test code
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 SMART LEGAL FETCHER TEST")
    print("="*70 + "\n")

    fetcher = SmartLegalFetcher()

    # Test fetching Darbo Kodeksas
    print("Test 1: Fetching Darbo Kodeksas...\n")
    law = fetcher.get_law("darbo_kodeksas")

    if law:
        print(f"✅ Fetched: {law['title']}")
        print(f"   Text length: {len(law['full_text'])} chars")

        # Test article retrieval
        print("\nTest 2: Getting specific article...\n")
        article = fetcher.get_article("darbo_kodeksas", "1")
        if article:
            print(f"✅ Article {article['article_number']}: {article['article_title']}")
            print(f"   Content preview: {article['content'][:100]}...")

        # Test cache hit
        print("\nTest 3: Testing cache (should be HIT)...\n")
        law2 = fetcher.get_law("darbo_kodeksas")
        print(f"✅ Second fetch successful (from cache)")

    # Get stats
    stats = fetcher.get_stats()
    print(f"\n📊 Cache Stats:")
    print(f"   Active laws: {stats['active_laws']}")
    print(f"   Total articles: {stats['total_articles']}")

    print("\n" + "="*70)
    print("✅ SMART LEGAL FETCHER TEST COMPLETE")
    print("="*70)
