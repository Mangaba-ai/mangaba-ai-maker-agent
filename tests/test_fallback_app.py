import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Configurações idênticas ao app.py
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Lista de modelos atual do app.py
GEMINI_MODELS = [
    "gemini-2.0-flash",  # Mais estável conforme diagnóstico
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite-preview-06-17"
]

def run_generative_model(prompt):
    """Função idêntica ao app.py para testar o sistema de fallback"""
    if not GEMINI_API_KEY:
        raise ConnectionError("Chave da API Gemini não encontrada.")
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    last_error = None
    
    print(f"🔄 Iniciando sistema de fallback com {len(GEMINI_MODELS)} modelos...")
    
    # Tenta cada modelo na ordem de prioridade
    for i, model in enumerate(GEMINI_MODELS, 1):
        try:
            url = f"{GEMINI_BASE_URL}/{model}:generateContent"
            print(f"\n[{i}/{len(GEMINI_MODELS)}] Tentando modelo: {model}")
            print(f"📍 URL: {url}")
            
            response = requests.post(url, headers=headers, json=data)
            print(f"📊 Status Code: {response.status_code}")
            
            # Se o modelo funcionou, retorna o resultado
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ SUCESSO! Modelo {model} funcionou!")
                    print(f"📝 Resposta: {text_response[:100]}...")
                    return text_response
            
            # Se deu erro 429 (quota) ou 400 (modelo não disponível), tenta o próximo
            elif response.status_code in [400, 429]:
                error_detail = ""
                try:
                    error_json = response.json()
                    error_detail = error_json.get('error', {}).get('message', 'Erro desconhecido')
                except:
                    error_detail = response.text[:100]
                
                print(f"⚠️  Modelo {model} indisponível (HTTP {response.status_code}): {error_detail}")
                last_error = f"Modelo {model}: HTTP {response.status_code} - {error_detail}"
                
                if i < len(GEMINI_MODELS):
                    print("🔄 Tentando próximo modelo...")
                continue
            else:
                # Outros erros HTTP
                print(f"❌ Erro HTTP {response.status_code} com modelo {model}")
                last_error = f"Modelo {model}: HTTP {response.status_code}"
                continue
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão com modelo {model}: {e}")
            last_error = f"Modelo {model}: {e}"
            continue
        except (KeyError, IndexError) as e:
            print(f"❌ Erro ao processar resposta do modelo {model}: {e}")
            last_error = f"Modelo {model}: {e}"
            continue
    
    # Se chegou aqui, nenhum modelo funcionou
    print("\n💥 FALHA TOTAL: Todos os modelos falharam!")
    raise ConnectionError(f"Todos os modelos Gemini falharam. Último erro: {last_error}")

def test_fallback_system():
    print("="*60)
    print(" TESTE DO SISTEMA DE FALLBACK DO APP.PY ")
    print("="*60)
    
    print("🔧 Configuração atual:")
    print(f"   • Modelos configurados: {len(GEMINI_MODELS)}")
    for i, model in enumerate(GEMINI_MODELS, 1):
        print(f"   {i}. {model}")
    
    print("\n🧪 Testando com prompt simples...")
    
    try:
        result = run_generative_model("Diga apenas 'Sistema de fallback funcionando!'")
        print("\n🎉 RESULTADO FINAL:")
        print("✅ Sistema de fallback FUNCIONOU!")
        print(f"📝 Resposta completa: {result}")
        assert True
        
    except ConnectionError as e:
        print("\n💥 RESULTADO FINAL:")
        print("❌ Sistema de fallback FALHOU!")
        print(f"📝 Erro: {e}")
        assert False
    except Exception as e:
        print("\n💥 RESULTADO FINAL:")
        print(f"❌ Erro inesperado: {e}")
        assert False

def test_app_endpoint():
    print("\n" + "="*60)
    print(" TESTE DO ENDPOINT DA APLICAÇÃO ")
    print("="*60)
    
    print("🌐 Testando endpoint: http://127.0.0.1:5000/api/run_agent_system")
    
    try:
        # Dados de teste para o endpoint
        test_data = {
            'goal': 'Teste do sistema de fallback',
            'researcherPrompt': 'Crie um outline simples para: {goal}. Contexto: {context}',
            'writerPrompt': 'Escreva um texto baseado no outline: {outline}. Contexto: {context}'
        }
        
        response = requests.post(
            'http://127.0.0.1:5000/api/run_agent_system',
            data=test_data,
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint funcionando!")
            print(f"📝 Logs: {result.get('logs', [])}")
            print(f"📄 Resultado: {result.get('result', '')[:200]}...")
            assert True
        else:
            print(f"❌ Erro no endpoint: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📝 Detalhes: {error_detail}")
            except:
                print(f"📝 Resposta: {response.text}")
            assert False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor")
        print("💡 Verifique se o servidor está rodando em http://127.0.0.1:5000")
        assert False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        assert False

if __name__ == "__main__":
    print("🚀 TESTE COMPLETO DO SISTEMA DE FALLBACK")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S') if 'time' in globals() else 'N/A'}")
    
    # Teste 1: Sistema de fallback isolado
    fallback_ok = test_fallback_system()
    
    # Teste 2: Endpoint da aplicação
    endpoint_ok = test_app_endpoint()
    
    print("\n" + "="*60)
    print(" RESUMO FINAL ")
    print("="*60)
    print(f"🔄 Sistema de fallback isolado: {'✅ OK' if fallback_ok else '❌ FALHOU'}")
    print(f"🌐 Endpoint da aplicação: {'✅ OK' if endpoint_ok else '❌ FALHOU'}")
    
    if fallback_ok and endpoint_ok:
        print("\n🎉 TUDO FUNCIONANDO! O sistema de fallback está operacional.")
    elif fallback_ok:
        print("\n⚠️  Sistema de fallback OK, mas há problema no endpoint da aplicação.")
    else:
        print("\n💥 Sistema de fallback com problemas. Verifique a configuração dos modelos.")