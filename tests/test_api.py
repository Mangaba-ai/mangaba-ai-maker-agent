import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Lista de modelos em ordem de prioridade
GEMINI_MODELS = [
    "gemini-1.5-flash",  # Começando com o mais estável
    "gemini-1.5-pro",
    "gemini-2.0-flash",
    "gemini-2.5-flash"
]

def test_api_key_validity():
    """Testa se a chave API é válida fazendo uma requisição simples"""
    if not GEMINI_API_KEY:
        print("❌ Chave da API Gemini não encontrada no arquivo .env")
        assert False
    
    print(f"🔑 Chave API encontrada: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
    print(f"📏 Tamanho da chave: {len(GEMINI_API_KEY)} caracteres")
    
    # Teste básico de formato da chave
    if not GEMINI_API_KEY.startswith('AIza'):
        print("⚠️ Formato da chave API pode estar incorreto (deve começar com 'AIza')")
    
    assert True

def test_simple_request():
    """Testa uma requisição simples com o modelo mais estável"""
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    # Requisição mais simples possível
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
    
    model = "gemini-1.5-flash"
    url = f"{GEMINI_BASE_URL}/{model}:generateContent"
    
    print(f"\n🧪 Testando requisição simples com {model}...")
    print(f"🌐 URL: {url}")
    print(f"📋 Headers: {headers}")
    print(f"📦 Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso! Resposta: {json.dumps(result, indent=2)}")
            assert True
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📝 Detalhes do erro: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"📝 Resposta bruta: {response.text}")
            assert False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout na requisição")
        assert False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        assert False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        assert False

def test_alternative_endpoint():
    """Testa endpoint alternativo sem versão beta"""
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
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
    
    # Tenta endpoint sem v1beta
    alternative_url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    
    print("\n🔄 Testando endpoint alternativo...")
    print(f"🌐 URL: {alternative_url}")
    
    try:
        response = requests.post(alternative_url, headers=headers, json=data, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint alternativo funcionou!")
            assert True
        else:
            print(f"❌ Endpoint alternativo também falhou: {response.status_code}")
            assert False
            
    except Exception as e:
        print(f"❌ Erro no endpoint alternativo: {e}")
        assert False

if __name__ == "__main__":
    print("=== DIAGNÓSTICO DETALHADO DA API GEMINI ===")
    
    # Teste 1: Validação da chave API
    if not test_api_key_validity():
        exit(1)
    
    # Teste 2: Requisição simples
    if test_simple_request():
        print("\n🎉 API funcionando corretamente!")
    else:
        print("\n🔄 Tentando endpoint alternativo...")
        if test_alternative_endpoint():
            print("\n🎉 Endpoint alternativo funcionou!")
        else:
            print("\n💥 Todos os testes falharam. Possíveis causas:")
            print("   1. Chave API inválida ou expirada")
            print("   2. Quota excedida em todos os modelos")
            print("   3. Problema de conectividade")
            print("   4. Mudanças na API do Google")
            print("\n🔧 Sugestões:")
            print("   - Verifique se a chave API está correta no Google AI Studio")
            print("   - Aguarde alguns minutos e tente novamente")
            print("   - Considere criar uma nova chave API")
