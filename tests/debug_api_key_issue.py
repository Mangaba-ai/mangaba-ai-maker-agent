import os
import requests
import json
from dotenv import load_dotenv

def debug_api_key_issue():
    print("🔍 DEBUG: INVESTIGAÇÃO DO PROBLEMA DA CHAVE API")
    print("="*60)
    
    # Carregar .env
    load_dotenv()
    
    # Verificar chave do .env
    env_key = os.environ.get("GEMINI_API_KEY")
    print(f"🔑 Chave do .env: {env_key[:10] if env_key else 'NENHUMA'}...{env_key[-4:] if env_key else ''}")
    
    # Verificar se há variáveis de ambiente do sistema
    import subprocess
    try:
        result = subprocess.run(['powershell', '-Command', 'Get-ChildItem Env:GEMINI_API_KEY'], 
                              capture_output=True, text=True, shell=True)
        if result.stdout.strip():
            print(f"⚠️ Variável de ambiente do sistema encontrada: {result.stdout.strip()}")
        else:
            print("✅ Nenhuma variável de ambiente do sistema conflitante")
    except Exception as e:
        print(f"❓ Não foi possível verificar variáveis de ambiente do sistema: {e}")
    
    # Testar a chave diretamente
    if env_key:
        print("\n🧪 Testando chave do .env diretamente...")
        test_result = test_api_key_direct(env_key)
        print(f"📊 Resultado: {'✅ FUNCIONOU' if test_result else '❌ FALHOU'}")
    
    # Verificar se o app.py está carregando corretamente
    print("\n🔍 Simulando carregamento do app.py...")
    
    # Recarregar .env como o app.py faz
    load_dotenv(override=True)  # Force reload
    
    app_key = os.environ.get("GEMINI_API_KEY")
    print(f"🔑 Chave após reload: {app_key[:10] if app_key else 'NENHUMA'}...{app_key[-4:] if app_key else ''}")
    
    if app_key and env_key and app_key != env_key:
        print("⚠️ PROBLEMA: Chaves diferentes após reload!")
    elif app_key == env_key:
        print("✅ Chaves são idênticas")
    
    # Testar com a mesma estrutura do app.py
    if app_key:
        print("\n🧪 Testando com estrutura idêntica ao app.py...")
        test_result_app = test_with_app_structure(app_key)
        print(f"📊 Resultado: {'✅ FUNCIONOU' if test_result_app else '❌ FALHOU'}")

def test_api_key_direct(api_key):
    """Teste direto da chave API"""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Hello"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return False

def test_with_app_structure(api_key):
    """Teste usando exatamente a mesma estrutura do app.py"""
    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    model = "gemini-2.0-flash"
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Teste simples"
                    }
                ]
            }
        ]
    }
    
    try:
        url = f"{GEMINI_BASE_URL}/{model}:generateContent"
        print(f"📡 URL: {url}")
        print(f"🔑 Chave: {api_key[:10]}...{api_key[-4:]}")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code != 200:
            try:
                error_detail = response.json()
                print(f"📝 Erro: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"📝 Resposta: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"💥 Exceção: {e}")
        return False

if __name__ == "__main__":
    debug_api_key_issue()