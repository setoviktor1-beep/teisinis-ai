import google.generativeai as genai
import os
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

def test_gemini():
    """
    Test Gemini API connection with explicit debugging
    """
    print("="*70)
    print("🧪 TESTING GEMINI API (DEBUG MODE)")
    print("="*70 + "\n")
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in .env")
        return False
    
    # Masked key for verification
    masked_key = f"{api_key[:5]}...{api_key[-5:]}" if len(api_key) > 10 else "***"
    print(f"🔑 Using API Key: {masked_key}")
    
    try:
        # Explicit configuration
        print("⚙️  Configuring genai...")
        genai.configure(api_key=api_key)
        
        # models to try
        models_to_try = ['gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-pro']
        
        success = False
        
        for model_name in models_to_try:
            print(f"\n🔮 Trying model: {model_name}...")
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello, can you confirm you are working?")
                
                print("📝 RESPONSE RECEIVED:")
                print("-" * 30)
                print(response.text.strip())
                print("-" * 30)
                print(f"✅ SUCCESS with {model_name}!")
                success = True
                break
            except Exception as e:
                print(f"   ❌ Failed with {model_name}: {str(e)}")
        
        if success:
             return True
             
        # If all failed, try listing
        print("\n🔍 Listing available models (Auth Check):")
        for m in genai.list_models():
             if 'generateContent' in m.supported_generation_methods:
                 print(f"   - {m.name}")
                 
        return False

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        # traceback.print_exc()
        return False

if __name__ == "__main__":
    test_gemini()
