import urllib.request
import urllib.error
import json

def test_url(url, description):
    print(f"\n=== {description} ===")
    print(f"URL: {url}")
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            content = response.read().decode('utf-8')
            print(f"Status: {response.getcode()}")
            print(f"Content: {content}")
            return True
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Probar tenant público
    test_url("http://127.0.0.1:8000/test-public/", "Tenant público")
    
    # Probar tenant específico con IP 
    test_url("http://127.0.0.1:8000/test/", "Tenant específico con IP")
    
    # NOTE: No podemos probar dominios .localhost desde Python sin configuración adicional
    print("\n=== NOTA ===")
    print("Los dominios .localhost solo funcionan en navegadores")
    print("El middleware de django-tenants necesita el header Host correcto")