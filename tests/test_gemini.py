import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini():
    """
    Test Gemini API connection
    """
    print("="*70)
    print("🧪 TESTING GEMINI API")
    print("="*70 + "\n")
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in .env")
        print("\n📝 Steps:")
        print("1. Get key from https://ai.google.dev/")
        print("2. Add to .env file: GEMINI_API_KEY=your_key")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-5:]}\n")
    
    try:
        # Discover supported model
        model_name = 'gemini-1.5-flash' # Default fallback
        print("🔍 Discovering available models...")
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
                    print(f"   Found: {m.name}")
                    model_name = m.name
                    break # Use the first one found
        except:
            print("   (Discovery failed, using default)")

        print(f"🔮 Using model: {model_name}")
        model = genai.GenerativeModel(model_name)
        
        # Test prompt
        print("⏳ Sending test prompt...\n")
        
        prompt = "Paaiškink trumpai (2-3 sakiniais) kas yra Darbo kodeksas Lietuvoje."
        
        response = model.generate_content(prompt)
        
        print("📝 GEMINI RESPONSE:")
        print("-"*70)
        print(response.text)
        print("-"*70)
        
        print("\n✅ Gemini API works!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        try:
            print("\n🔍 Listing available models:")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"   - {m.name}")
        except Exception as list_e:
            print(f"   (Could not list models: {list_e})")
        return False

if __name__ == "__main__":
    success = test_gemini()
    
    if success:
        print("\n" + "="*70)
        print("✅ GEMINI API TEST PASSED")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ GEMINI API TEST FAILED")
        print("="*70)
