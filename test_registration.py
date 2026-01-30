import requests

# Test registration
print("Testing registration...")
try:
    response = requests.post(
        'http://localhost:8000/api/v1/auth/register',
        json={'email': 'test@example.com', 'password': 'test1234'},  # noqa: S106
        timeout=5
    )

    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Response Text: {response.text[:500]}")  # First 500 chars

    if response.status_code == 200:
        print("✓ Registration successful!")
        data = response.json()
        print(f"Access Token: {data.get('access_token', 'N/A')[:20]}...")
    else:
        print("✗ Registration failed!")
        try:
            error = response.json()
            print(f"Error: {error}")
        except Exception as e: # Fixed bare except
            print(f"Could not parse error response: {e}")
except requests.exceptions.RequestException as e:
    print(f"❌ Connection failed: {e}")
