import subprocess
import time
import requests

def test():
    print("Starting server...")
    proc = subprocess.Popen(["uvicorn", "app.main:app", "--port", "8080"])
    time.sleep(3)
    
    try:
        print("\n--- Test 1: Register ---")
        res = requests.post("http://localhost:8080/v1/register", json={
            "username": "admin1",
            "email": "admin1@test.com",
            "password": "SecurePassword123",
            "full_name": "Admin User",
            "role": "admin"
        })
        print(res.status_code, res.text)
        
        print("\n--- Test 2: Login ---")
        res = requests.post("http://localhost:8080/v1/login", json={
            "username": "admin1",
            "password": "SecurePassword123"
        })
        print(res.status_code, res.text)
        token = res.json().get("access_token") if res.status_code == 200 else None
        
        if token:
            print("\n--- Test 3: Protected Route (/me) ---")
            res = requests.get("http://localhost:8080/v1/me", headers={"Authorization": f"Bearer {token}"})
            print(res.status_code, res.text)
            
            print("\n--- Test 4: Rate Limiting ---")
            for i in range(6):
                res = requests.post("http://localhost:8080/v1/login", json={"username": "test", "password": "abc"})
            print("Rate Limit (6th request):", res.status_code, res.text)
            
            print("\n--- Test 5: Audit Log Admin Endpoint ---")
            res = requests.get("http://localhost:8080/v1/audit-logs", headers={"Authorization": f"Bearer {token}"})
            print(res.status_code, res.text[:300] + "...")
            
    finally:
        print("Terminating server...")
        proc.terminate()

if __name__ == "__main__":
    test()
