"""
Cache Manager for Legal Documents
Manages SQLite cache for laws and articles
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json
import os


class CacheManager:
    """
    Manages SQLite cache for legal documents
    """

    def __init__(self, db_path: str = "data/legal_cache.db"):
        """
        Initialize cache manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_data_dir()
        self._init_db()
        print(f"[OK] Cache Manager initialized: {db_path}")

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _init_db(self):
        """Initialize database schema"""
        schema_path = os.path.join(
            os.path.dirname(__file__),
            'schema.sql'
        )

        if not os.path.exists(schema_path):
            print(f"⚠️ Schema file not found: {schema_path}")
            return

        conn = sqlite3.connect(self.db_path)
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()

    def get_law(self, law_id: str) -> Optional[Dict]:
        """
        Get cached law if fresh

        Args:
            law_id: TAIS ID of the law

        Returns:
            Law data if cached and fresh, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT title, full_text, version, fetched_at, metadata
            FROM law_cache
            WHERE law_id = ? AND expires_at > datetime('now')
        """, (law_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'law_id': law_id,
                'title': row[0],
                'full_text': row[1],
                'version': row[2],
                'fetched_at': row[3],
                'metadata': json.loads(row[4]) if row[4] else {}
            }
        return None

    def cache_law(
        self,
        law_id: str,
        title: str,
        full_text: str,
        version: str,
        metadata: Dict = None,
        ttl_hours: int = 24
    ):
        """
        Cache a law with TTL

        Args:
            law_id: TAIS ID
            title: Law title
            full_text: Full text of the law
            version: Version identifier
            metadata: Additional metadata
            ttl_hours: Time to live in hours
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        expires_at = datetime.now() + timedelta(hours=ttl_hours)

        cursor.execute("""
            INSERT OR REPLACE INTO law_cache
            (law_id, title, full_text, version, expires_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            law_id, title, full_text, version,
            expires_at.isoformat(),
            json.dumps(metadata or {})
        ))

        conn.commit()
        conn.close()
        print(f"✅ Cached law: {law_id} (expires in {ttl_hours}h)")

    def get_article(
        self,
        law_id: str,
        article_number: str
    ) -> Optional[Dict]:
        """
        Get specific article from cache

        Args:
            law_id: TAIS ID of the law
            article_number: Article number

        Returns:
            Article data if cached, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT article_title, content
            FROM article_cache
            WHERE law_id = ? AND article_number = ?
        """, (law_id, article_number))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'law_id': law_id,
                'article_number': article_number,
                'article_title': row[0],
                'content': row[1]
            }
        return None

    def cache_article(
        self,
        law_id: str,
        article_number: str,
        article_title: str,
        content: str
    ):
        """
        Cache individual article

        Args:
            law_id: TAIS ID
            article_number: Article number
            article_title: Article title
            content: Article content
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO article_cache
            (law_id, article_number, article_title, content)
            VALUES (?, ?, ?, ?)
        """, (law_id, article_number, article_title, content))

        conn.commit()
        conn.close()

    def cache_articles_batch(self, articles: List[Dict]):
        """
        Cache multiple articles at once

        Args:
            articles: List of article dicts with law_id, article_number, article_title, content
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for article in articles:
            cursor.execute("""
                INSERT OR REPLACE INTO article_cache
                (law_id, article_number, article_title, content)
                VALUES (?, ?, ?, ?)
            """, (
                article['law_id'],
                article['article_number'],
                article['article_title'],
                article['content']
            ))

        conn.commit()
        conn.close()
        print(f"✅ Cached {len(articles)} articles")

    def invalidate_law(self, law_id: str):
        """
        Invalidate cached law (force refresh on next request)

        Args:
            law_id: TAIS ID to invalidate
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE law_cache
            SET expires_at = datetime('now')
            WHERE law_id = ?
        """, (law_id,))

        conn.commit()
        conn.close()
        print(f"🔄 Invalidated cache: {law_id}")

    def get_stats(self) -> Dict:
        """
        Get cache statistics

        Returns:
            Dict with cache stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM law_cache
            WHERE expires_at > datetime('now')
        """)
        active_laws = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM law_cache")
        total_laws = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM article_cache")
        total_articles = cursor.fetchone()[0]

        conn.close()

        return {
            'active_laws': active_laws,
            'total_laws': total_laws,
            'total_articles': total_articles,
            'cache_hit_rate': 'N/A'  # TODO: Implement hit tracking
        }

    def clear_expired(self):
        """Remove expired entries from cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM law_cache
            WHERE expires_at <= datetime('now')
        """)

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted > 0:
            print(f"🧹 Cleared {deleted} expired laws from cache")

        return deleted


# Test code
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 CACHE MANAGER TEST")
    print("="*70 + "\n")

    cache = CacheManager()

    # Test caching
    print("Testing cache operations...\n")

    # Cache a law
    cache.cache_law(
        law_id="TAIS.245495",
        title="Darbo kodeksas",
        full_text="Test content...",
        version="2024-01-01",
        metadata={'url': 'https://e-tar.lt/...'},
        ttl_hours=1
    )

    # Retrieve it
    law = cache.get_law("TAIS.245495")
    print(f"\nRetrieved: {law['title'] if law else 'Not found'}")

    # Cache an article
    cache.cache_article(
        law_id="TAIS.245495",
        article_number="1",
        article_title="Bendrosios nuostatos",
        content="Šis kodeksas reglamentuoja..."
    )

    # Get stats
    stats = cache.get_stats()
    print(f"\n📊 Cache Stats:")
    print(f"   Active laws: {stats['active_laws']}")
    print(f"   Total articles: {stats['total_articles']}")

    print("\n" + "="*70)
    print("✅ CACHE MANAGER TEST COMPLETE")
    print("="*70)
