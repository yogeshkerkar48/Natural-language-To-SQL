import urllib.request
import json
import bcrypt

def test_hashing():
    print("Testing bcrypt hashing...")
    try:
        pw = "12345678"
        hashed = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"Hashing successful: {hashed[:10]}...")
        if bcrypt.checkpw(pw.encode('utf-8'), hashed.encode('utf-8')):
            print("Verification successful.")
        else:
            print("Verification FAILED.")
    except Exception as e:
        print(f"Hashing error: {e}")

def test_api_register():
    print("\nTesting API Registration...")
    url = "http://localhost:8000/api/auth/register"
    data = {
        "email": "test_script@gmail.com",
        "password": "password123"
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Response Code: {response.getcode()}")
            print(f"Response: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_hashing()
    test_api_register()
