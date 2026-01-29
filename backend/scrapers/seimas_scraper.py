"""
E-Seimas.lt web scraper
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SeimasScraper:
    def __init__(self):
        self.base_url = "https://e-seimas.lrs.lt"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0'
        })
    
    async def scrape_documents(self, document_type: str = "all", limit: int = 10) -> List[Dict]:
        """Scrape legal documents"""
        try:
            url = f"{self.base_url}/portal/legalAct/lt/TAK"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            documents = []
            
            doc_items = soup.select('.document-item')[:limit]
            
            for item in doc_items:
                try:
                    title = item.select_one('.title')
                    link = item.select_one('a')
                    
                    if title and link:
                        documents.append({
                            'title': title.get_text(strip=True),
                            'url': self.base_url + link.get('href', '')
                        })
                except Exception as e:
                    continue
            
            return documents
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
