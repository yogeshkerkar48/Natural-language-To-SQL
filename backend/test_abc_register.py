import urllib.request
import json
import urllib.error

def test_abc_register():
    print("Testing API Registration for abc@gmail.com...")
    url = "http://localhost:8000/api/auth/register"
    data = {
        "email": "abc@gmail.com",
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
    test_abc_register()
