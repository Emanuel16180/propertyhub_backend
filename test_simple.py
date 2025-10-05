import requests

try:
    response = requests.get('http://bienestar.localhost:8000/admin/', timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ FUNCIONA!")
    else:
        print(f"⚠️ Respuesta: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

try:
    response = requests.get('http://localhost:8000/admin/', timeout=5)
    print(f"Localhost Status: {response.status_code}")
except Exception as e:
    print(f"❌ Localhost Error: {str(e)}")