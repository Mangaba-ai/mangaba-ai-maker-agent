import requests
import json

def test_app_endpoint():
    print("🧪 TESTANDO ENDPOINT DA APLICAÇÃO")
    print("="*50)
    
    url = "http://127.0.0.1:5000/api/run_agent_system"
    
    # Dados de teste simples
    data = {
        'goal': 'Teste simples',
        'researcherPrompt': 'Pesquise sobre: {goal}. Contexto: {context}',
        'writerPrompt': 'Escreva sobre: {outline}. Contexto: {context}'
    }
    
    print(f"📡 URL: {url}")
    print(f"📦 Dados: {json.dumps(data, indent=2)}")
    print("\n🔄 Fazendo requisição...")
    
    try:
        response = requests.post(url, data=data, timeout=60)
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCESSO!")
            result = response.json()
            print(f"📝 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ ERRO HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📝 Erro JSON: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                print(f"📝 Resposta bruta: {response.text}")
                
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - A requisição demorou mais de 60 segundos")
    except requests.exceptions.ConnectionError:
        print("🔌 ERRO DE CONEXÃO - Servidor não está rodando?")
    except Exception as e:
        print(f"💥 ERRO INESPERADO: {e}")

if __name__ == "__main__":
    test_app_endpoint()