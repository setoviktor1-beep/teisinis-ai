import sys
import os
from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.document_generator import DocumentGenerator

def debug_generation():
    print("="*70)
    print("🛠️ DEBUGGING DOCUMENT GENERATION")
    print("="*70 + "\n")
    
    load_dotenv()
    
    try:
        generator = DocumentGenerator()
        print("✅ DocumentGenerator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize generator: {e}")
        return

    test_data = {
        'employee_name': 'Jonas Jonaitis',
        'employer_name': 'UAB "Testas"',
        'workplace': 'Vilnius',
        'violation_description': 'Nesumokėtas atlyginimas už 2 mėnesius.',
        'violation_date': '2024-01-30'
    }
    
    print("\n⏳ Calling generate_labor_complaint...")
    result = generator.generate_labor_complaint(test_data)
    
    if result:
        print("\n✅ SUCCESS: Document generated")
        print(f"Content length: {len(result['content'])}")
    else:
        print("\n❌ FAILED: generate_labor_complaint returned None")

if __name__ == "__main__":
    debug_generation()
