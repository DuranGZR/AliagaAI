import os
import requests
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("COLLECTAPI_KEY")
headers = {
    "authorization": key,
    "content-type": "application/json"
}

print("=== 1. NOBETCI ECZANE (Aliaga) ===")
res1 = requests.get("https://api.collectapi.com/health/dutyPharmacy?ilce=Alia%C4%9Fa&il=%C4%B0zmir", headers=headers)
print(f"Status: {res1.status_code}")
print(res1.text)

print("\n=== 2. EKO/DOVIZ ===")
res3 = requests.get("https://api.collectapi.com/economy/allCurrency", headers=headers)
print(f"Status: {res3.status_code}")
print(res3.text)
