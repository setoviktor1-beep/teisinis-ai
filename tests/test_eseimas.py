import sys
import os
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.eseimas_agent import ESeimasAgent
import json
import datetime

def test_eseimas_agent():
    print("="*70)
    print("🧪 TESTING E-SEIMAS AGENT")
    print("="*70 + "\n")
    
    agent = ESeimasAgent()
    
    # Test 1: Search for Darbo kodeksas (Expect simulated result)
    print("TEST 1: Search 'Darbo kodeksas'")
    results = agent.search_new_legislation("Darbo kodeksas")
    
    if len(results) > 0 and "52 straipsnio pakeitimo" in results[0]['title']:
        print("✅ PASSED: Found simulated amendment.")
    else:
        print(f"❌ FAILED: Expected results, got {len(results)}")
        
    # Test 2: Search for unrelated term (Expect empty)
    print("\nTEST 2: Search 'Kosmoso strategija'")
    results_empty = agent.search_new_legislation("Kosmoso strategija")
    
    if len(results_empty) == 0:
        print("✅ PASSED: Correctly returned no results for unrelated term.")
    else:
        print(f"❌ FAILED: Expected 0 results, got {len(results_empty)}")

if __name__ == "__main__":
    import sys
    import os
    # Add project root to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_eseimas_agent()
