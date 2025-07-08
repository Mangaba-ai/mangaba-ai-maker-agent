import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

def print_separator(title):
    print("\n" + "="*70)
    print(f" {title} ")
    print("="*70)

def test_api_key_status():
    print_separator("VERIFICAÇÃO DA CHAVE API")
    
    if not GEMINI_API_KEY:
        print("❌ Chave API não encontrada")
        return False
    
    print(f"✅ Chave encontrada: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
    print(f"📏 Tamanho: {len(GEMINI_API_KEY)} caracteres")
    
    # Verificar se a chave ainda é válida
    if not GEMINI_API_KEY.startswith('AIza'):
        print("⚠️ Formato da chave pode estar incorreto")
    
    return True

def test_different_endpoints():
    print_separator("TESTE DE DIFERENTES ENDPOINTS")
    
    endpoints = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    ]
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    simple_data = {
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
    
    working_endpoints = []
    
    for i, url in enumerate(endpoints, 1):
        print(f"\n[{i}/{len(endpoints)}] Testando: {url}")
        
        try:
            response = requests.post(url, headers=headers, json=simple_data, timeout=30)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ FUNCIONANDO!")
                working_endpoints.append(url)
                try:
                    result = response.json()
                    if 'candidates' in result:
                        text = result['candidates'][0]['content']['parts'][0]['text']
                        print(f"📝 Resposta: {text[:50]}...")
                except:
                    pass
            else:
                print("❌ Falhou")
                try:
                    error_detail = response.json()
                    print(f"📝 Erro: {json.dumps(error_detail, indent=2)}")
                except Exception as e:
                    print(f"Erro ao processar resposta JSON: {e}")
                    print(f"📝 Resposta bruta: {response.text[:200]}")
                    
        except Exception as e:
            print(f"❌ Exceção: {e}")
        
        time.sleep(1)
    
    return working_endpoints

def test_different_payloads():
    print_separator("TESTE DE DIFERENTES PAYLOADS")
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    payloads = [
        # Payload 1: Mínimo
        {
            "name": "Mínimo",
            "data": {
                "contents": [
                    {
                        "parts": [
                            {"text": "Hi"}
                        ]
                    }
                ]
            }
        },
        # Payload 2: Com role
        {
            "name": "Com role",
            "data": {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": "Hello"}
                        ]
                    }
                ]
            }
        },
        # Payload 3: Com configurações
        {
            "name": "Com configurações",
            "data": {
                "contents": [
                    {
                        "parts": [
                            {"text": "Hello"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 100
                }
            }
        },
        # Payload 4: Sem array aninhado
        {
            "name": "Estrutura alternativa",
            "data": {
                "prompt": {
                    "text": "Hello"
                }
            }
        }
    ]
    
    working_payloads = []
    
    for i, payload_info in enumerate(payloads, 1):
        print(f"\n[{i}/{len(payloads)}] Testando payload: {payload_info['name']}")
        print(f"📦 Estrutura: {json.dumps(payload_info['data'], indent=2)}")
        
        try:
            response = requests.post(url, headers=headers, json=payload_info['data'], timeout=30)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ FUNCIONOU!")
                working_payloads.append(payload_info['name'])
                try:
                    result = response.json()
                    if 'candidates' in result:
                        text = result['candidates'][0]['content']['parts'][0]['text']
                        print(f"📝 Resposta: {text[:50]}...")
                except:
                    pass
            else:
                print("❌ Falhou")
                try:
                    error_detail = response.json()
                    error_msg = error_detail.get('error', {}).get('message', 'Erro desconhecido')
                    print(f"📝 Erro: {error_msg}")
                    print(f"📋 Detalhes completos: {json.dumps(error_detail, indent=2)}")
                except Exception as e:
                    print(f"Erro ao processar resposta JSON: {e}")
                    print(f"📝 Resposta bruta: {response.text[:300]}")
                    
        except Exception as e:
            print(f"❌ Exceção: {e}")
        
        time.sleep(1)
    
    return working_payloads

def test_quota_and_limits():
    print_separator("VERIFICAÇÃO DE QUOTA E LIMITES")
    
    # Teste com múltiplas requisições rápidas para verificar rate limiting
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {"text": "Test"}
                ]
            }
        ]
    }
    
    print("🔄 Fazendo 5 requisições rápidas para testar rate limiting...")
    
    for i in range(5):
        try:
            start_time = time.time()
            response = requests.post(url, headers=headers, json=data, timeout=10)
            end_time = time.time()
            
            print(f"Req {i+1}: Status {response.status_code} ({int((end_time-start_time)*1000)}ms)")
            
            if response.status_code == 429:
                print(f"⚠️ Rate limit atingido na requisição {i+1}")
                try:
                    error_detail = response.json()
                    print(f"📝 Detalhes: {error_detail}")
                except:
                    pass
                break
            elif response.status_code != 200:
                print(f"❌ Erro {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"📝 Detalhes: {error_detail}")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Erro na requisição {i+1}: {e}")
        
        time.sleep(0.5)

def main():
    print("🔍 INVESTIGAÇÃO DETALHADA DO ERRO HTTP 400")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar chave API
    if not test_api_key_status():
        return
    
    # Testar diferentes endpoints
    print("\n🌐 Testando diferentes endpoints...")
    working_endpoints = test_different_endpoints()
    
    # Testar diferentes payloads
    print("\n📦 Testando diferentes estruturas de payload...")
    working_payloads = test_different_payloads()
    
    # Testar quota e limites
    print("\n📊 Verificando quota e rate limits...")
    test_quota_and_limits()
    
    # Relatório final
    print_separator("RELATÓRIO DE INVESTIGAÇÃO")
    
    print(f"🌐 Endpoints funcionando: {len(working_endpoints)}")
    for endpoint in working_endpoints:
        print(f"   ✅ {endpoint}")
    
    print(f"\n📦 Payloads funcionando: {len(working_payloads)}")
    for payload in working_payloads:
        print(f"   ✅ {payload}")
    
    if not working_endpoints and not working_payloads:
        print("\n💥 PROBLEMA CRÍTICO IDENTIFICADO:")
        print("   • Nenhum endpoint ou payload funcionou")
        print("   • Possíveis causas:")
        print("     1. Chave API expirada ou inválida")
        print("     2. Conta suspensa ou com problemas")
        print("     3. Mudanças na API do Google")
        print("     4. Problemas de conectividade")
        print("\n🔧 Ações recomendadas:")
        print("   1. Gerar nova chave API no Google AI Studio")
        print("   2. Verificar status da conta Google")
        print("   3. Testar com uma conta diferente")
    elif working_endpoints:
        print("\n✅ SOLUÇÃO ENCONTRADA:")
        print(f"   • Use o endpoint: {working_endpoints[0]}")
        if working_payloads:
            print(f"   • Use o payload: {working_payloads[0]}")
    
    print("\n🏁 Investigação concluída.")

if __name__ == "__main__":
    main()