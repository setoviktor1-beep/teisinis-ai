import requests
from bs4 import BeautifulSoup
import datetime
import json
import os

class ESeimasAgent:
    """
    Agent for searching and tracking legal updates on e-seimas.lt
    """
    
    def __init__(self):
        self.base_url = "https://e-seimas.lrs.lt"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def search_new_legislation(self, keyword="Darbo kodeksas", days_back=7):
        """
        Search for recent legislation containing the keyword.
        
        Args:
            keyword (str): Search term.
            days_back (int): How many days back to look for registration date.
            
        Returns:
            list: List of found documents (dict).
        """
        print(f"🔍 [eSeimasAgent] Searching for '{keyword}' in the last {days_back} days...")
        
        # NOTE: e-seimas.lt search is complex and dynamic.
        # For the MVP/Prototype phase, we will simulate finding a recent amendment if one "exists" 
        # in our mock data, or return an empty list to avoid fragile scraping of search results page.
        # In a production version, this would need to reverse-engineer the exact search form POST request.
        
        results = []
        
        # MOCK LOGIC FOR DEMO PURPOSES
        # If searching for "Darbo kodeksas", simulate finding a recent draft
        if "Darbo kodeksas" in keyword:
             mock_date = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
             results.append({
                 'title': 'Lietuvos Respublikos darbo kodekso 52 straipsnio pakeitimo įstatymo projektas',
                 'reg_date': mock_date,
                 'reg_num': 'XIVP-1234',
                 'url': 'https://e-seimas.lrs.lt/portal/legalAct/lt/TAP/mock_id',
                 'type': 'Įstatymo projektas'
             })
             print(f"   ✅ Found simulated result: {results[0]['title']} ({mock_date})")
        
        print(f"📊 Found {len(results)} relevant documents.")
        return results

    def check_for_amendments(self, law_name="Darbo kodeksas"):
        """
        Check if there are any new amendments for a specific law.
        """
        return self.search_new_legislation(keyword=law_name)

if __name__ == "__main__":
    agent = ESeimasAgent()
    updates = agent.check_for_amendments()
    print(json.dumps(updates, indent=2, ensure_ascii=False))
