# config.py - Contains hardcoded secrets
API_KEY = "sk-live-1234567890abcdef"
DB_PASSWORD = "admin123"
SECRET_KEY = "my-super-secret-key-2024"

def init_app():
    print(f"Connecting with API key: {API_KEY}")
    print(f"Database password: {DB_PASSWORD}")
