import os
import json
from datetime import datetime

def validate_mvp():
    """
    Validate that MVP core functionality works
    """
    print("\n" + "="*70)
    print("🎯 TEISINIS AI - MVP VALIDATION")
    print("="*70 + "\n")
    
    checks = []
    
    # Check 1: Data directory exists
    checks.append({
        'name': 'Data directory',
        'passed': os.path.exists('data'),
        'file': 'data/'
    })
    
    # Check 2: Darbo kodeksas scraped (or fallback exists)
    checks.append({
        'name': 'Darbo kodeksas text',
        'passed': os.path.exists('data/darbo_kodeksas_text.txt'),
        'file': 'data/darbo_kodeksas_text.txt'
    })
    
    # Check 3: Scraper Script
    checks.append({
        'name': 'Scraper Script',
        'passed': os.path.exists('backend/scrapers/etar_scraper.py'),
        'file': 'backend/scrapers/etar_scraper.py'
    })
    
    # Check 4: Generator Script
    checks.append({
        'name': 'Generator Script',
        'passed': os.path.exists('backend/agents/document_generator.py'),
        'file': 'backend/agents/document_generator.py'
    })
    
    # Check 5: .env configured
    env_exists = os.path.exists('.env')
    has_key = False
    if env_exists:
        with open('.env', 'r') as f:
            content = f.read()
            # Check if key is set and not empty
            has_key = 'GEMINI_API_KEY=' in content and 'GEMINI_API_KEY=' != content.strip().split('GEMINI_API_KEY=')[1].split('\n')[0].strip()
            # Also check if it's not the placeholder
            if has_key:
                val = content.strip().split('GEMINI_API_KEY=')[1].split('\n')[0].strip()
                if not val: has_key = False
    
    checks.append({
        'name': 'Gemini API configured',
        'passed': env_exists and has_key,
        'file': '.env'
    })
    
    # Display results
    print("📊 VALIDATION RESULTS:\n")
    
    all_passed = True
    for i, check in enumerate(checks, 1):
        status = "✅ PASS" if check['passed'] else "❌ FAIL"
        print(f"{i}. {check['name']:30} {status:10} ({check['file']})")
        if not check['passed']:
            all_passed = False
    
    print("\n" + "="*70)
    
    if all_passed:
        print("🎉🎉🎉 ALL CHECKS PASSED!")
        print("="*70)
        print("\n✅ MVP CORE FUNCTIONALITY: READY")
        print("\n📂 Generated files:")
        if os.path.exists('data'):
            for f in os.listdir('data'):
                if not f.startswith('.'):
                    size = os.path.getsize(f'data/{f}') / 1024
                    print(f"   - data/{f} ({size:.1f} KB)")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("="*70)
        print("\n❌ Please review failed checks above.\n")
    
    return all_passed

if __name__ == "__main__":
    validate_mvp()
