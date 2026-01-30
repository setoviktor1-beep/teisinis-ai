
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.scrapers.etar_scraper import ETARScraper
from prompts.legal_prompts import get_labor_complaint_prompt

load_dotenv()

class DocumentGenerator:
    """
    AI-powered legal document generator
    """
    
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            # For validation purposes allow running without key but fail on generation
            print("⚠️ WARNING: GEMINI_API_KEY not found")
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize scraper
        self.scraper = ETARScraper()
    
    def generate_labor_complaint(self, user_data):
        """
        Generate labor complaint document
        
        Args:
            user_data (dict): User's complaint details
            
        Returns:
            dict: Generated document data
        """
        print("="*70)
        print("📝 GENERATING LABOR COMPLAINT")
        print("="*70 + "\n")
        
        # Step 1: Fetch relevant legal articles
        print("STEP 1: Fetching relevant legal articles...\n")
        
        # Get Article 52 (remote work) - relevant for this complaint
        legal_articles = []
        
        # Try to fetch article 52
        article_52 = self.scraper.fetch_article(52)
        if article_52:
            legal_articles.append(article_52)
            legal_articles.append(article_52)
            # print(f"✅ Fetched: {article_52['title']}\n") # Can cause UnicodeEncodeError on Windows
        else:
            print("❌ Failed to fetch Article 52. Proceeding without specific legal context.\n")
        
        # Combine legal context
        legal_context = "\n\n".join([ # Combine legal context
            f"{art['title']}\n{art['content']}" 
            for art in legal_articles
        ])
        
        if not legal_context:
            legal_context = "Lietuvos Respublikos darbo kodeksas"
        
        # Step 2: Build prompt
        print("STEP 2: Building AI prompt...\n")
        
        prompt = get_labor_complaint_prompt(user_data, legal_context)
        
        print(f"✅ Prompt ready ({len(prompt)} characters)\n")
        
        # Step 3: Generate with Gemini
        print("STEP 3: Generating document with AI...\n")
        
        if not hasattr(self, 'model'):
             print("❌ Gemini model not initialized (missing API Key)")
             return None

        print("⏳ Calling Gemini API (this may take 10-30 seconds)...\n")
        
        try:
            response = self.model.generate_content(prompt)
            generated_text = response.text
            
            print(f"✅ Document generated ({len(generated_text)} characters)\n")
            
        except Exception as e:
            print(f"❌ Gemini API Error: {e}")
            return None
        
        # Step 4: Format and save
        print("STEP 4: Formatting result...\n")
        
        document = {
            'type': 'labor_complaint',
            'content': generated_text,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'user_data': user_data,
                'legal_articles_used': [art['article_number'] for art in legal_articles],
            }
        }
        
        # Save to file
        output_path = f"data/generated_complaint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved → {output_path}\n")
        
        # Display preview
        print("="*70)
        print("📄 GENERATED DOCUMENT PREVIEW:")
        print("="*70)
        # print(generated_text[:800]) # Can cause UnicodeEncodeError
        print("\n... (see full document in JSON file)")
        print("="*70)
        
        return document


# TEST CODE
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 DOCUMENT GENERATOR TEST")
    print("="*70 + "\n")
    
    # Sample user data
    test_data = {
        'employee_name': 'Jonas Jonaitis',
        'employer_name': 'UAB "Technologijos"',
        'workplace': 'Vilnius, Konstitucijos pr. 1',
        'violation_description': '''Darbdavys kategoriškai atsisako leisti man dirbti nuotoliniu būdu, 
nors mano darbo pareigos (programuotojo) yra visiškai atliekamos nuotoliu. 
Turiu visą reikiamą įrangą, interneto ryšį, o įmonėje naudojama nuotolinė darbo įranga.
Darbdavys nepateikia jokių objektyvių priežasčių, kodėl negaliu dirbti iš namų, 
tik nurodo, kad "taip nuspręsta vadovybėje".''',
        'violation_date': '2024-01-15'
    }
    
    # Initialize generator
    generator = DocumentGenerator()
    
    # Generate document
    result = generator.generate_labor_complaint(test_data)
    
    if result:
        print("\n" + "="*70)
        print("✅ DOCUMENT GENERATION TEST PASSED")
        print("="*70)
        print("\n🎉 SUCCESS! Check data/ folder for generated document.")
    else:
        print("\n" + "="*70)
        print("❌ DOCUMENT GENERATION TEST FAILED")
        print("="*70)
