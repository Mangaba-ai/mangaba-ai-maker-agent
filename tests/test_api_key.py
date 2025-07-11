import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_api_key():
    print("🔑 TESTE DE VALIDADE DA CHAVE API")
    print("="*50)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Chave API não encontrada no arquivo .env")
        assert False
    
    print(f"🔍 Chave encontrada: {api_key[:10]}...{api_key[-4:]}")
    print(f"📏 Tamanho: {len(api_key)} caracteres")
    
    # Teste 1: Verificar formato
    if not api_key.startswith('AIza'):
        print("⚠️ AVISO: Formato da chave pode estar incorreto (deveria começar com 'AIza')")
    else:
        print("✅ Formato da chave parece correto")
    
    # Teste 2: Testar com endpoint simples
    print("\n🧪 Testando chave com requisição simples...")
    
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
        print(f"📡 URL: {url}")
        print("📦 Enviando requisição...")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ CHAVE API VÁLIDA E FUNCIONANDO!")
            result = response.json()
            if 'candidates' in result:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"📝 Resposta recebida: {text[:100]}...")
            assert True
        elif response.status_code == 400:
            print("❌ CHAVE API INVÁLIDA (HTTP 400)")
            try:
                error_detail = response.json()
                error_msg = error_detail.get('error', {}).get('message', 'Erro desconhecido')
                print(f"📝 Erro: {error_msg}")
                print(f"📋 Detalhes completos: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"📝 Resposta bruta: {response.text}")
            assert False
        elif response.status_code == 403:
            print("❌ ACESSO NEGADO (HTTP 403) - Chave pode estar desabilitada")
            try:
                error_detail = response.json()
                print(f"📝 Erro: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"📝 Resposta bruta: {response.text}")
            assert False
        elif response.status_code == 429:
            print("⚠️ QUOTA EXCEDIDA (HTTP 429) - Chave válida mas sem quota")
            assert True
        else:
            print(f"❓ STATUS INESPERADO: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📝 Resposta: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"📝 Resposta bruta: {response.text}")
            assert False
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - Requisição demorou mais de 30 segundos")
        assert False
    except requests.exceptions.ConnectionError:
        print("🔌 ERRO DE CONEXÃO - Problema de rede")
        assert False
    except Exception as e:
        print(f"💥 ERRO INESPERADO: {e}")
        assert False

def main():
    is_valid = test_api_key()
    
    print("\n" + "="*50)
    print("📋 RESUMO DO TESTE")
    print("="*50)
    
    if is_valid:
        print("✅ RESULTADO: Chave API está VÁLIDA e funcionando")
        print("\n🔧 PRÓXIMOS PASSOS:")
        print("   • A chave está funcionando corretamente")
        print("   • O problema pode estar na implementação do app.py")
        print("   • Verificar se há diferenças na estrutura da requisição")
    else:
        print("❌ RESULTADO: Chave API está INVÁLIDA ou com problemas")
        print("\n🔧 AÇÕES NECESSÁRIAS:")
        print("   1. Gerar nova chave API no Google AI Studio")
        print("   2. Atualizar o arquivo .env com a nova chave")
        print("   3. Reiniciar a aplicação")
        print("\n🌐 Link para gerar nova chave:")
        print("   https://aistudio.google.com/app/apikey")

if __name__ == "__main__":
    main()