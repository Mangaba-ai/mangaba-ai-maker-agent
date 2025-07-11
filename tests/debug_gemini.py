import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Lista completa de modelos para testar
ALL_GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro", 
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite-preview-06-17",
    "gemini-2.0-flash-preview-image-generation",
    "gemini-2.0-flash-lite"
]

def print_separator(title):
    print("\n" + "="*60)
    print(f" {title} ")
    print("="*60)

def test_api_key():
    print_separator("STEP 1: VERIFICAÇÃO DA CHAVE API")
    
    if not GEMINI_API_KEY:
        print("❌ ERRO: Chave da API Gemini não encontrada no arquivo .env")
        return False
    
    print("✅ Chave API encontrada")
    print(f"📏 Tamanho: {len(GEMINI_API_KEY)} caracteres")
    print(f"🔑 Formato: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
    
    if not GEMINI_API_KEY.startswith('AIza'):
        print("⚠️  AVISO: Formato da chave pode estar incorreto (deve começar com 'AIza')")
    else:
        print("✅ Formato da chave parece correto")
    
    return True

def test_single_model(model_name, test_prompt="Hello"):
    print(f"\n🧪 Testando modelo: {model_name}")
    print(f"📍 URL: {GEMINI_BASE_URL}/{model_name}:generateContent")
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": test_prompt
                    }
                ]
            }
        ]
    }
    
    try:
        print("📤 Enviando requisição...")
        start_time = time.time()
        
        response = requests.post(
            f"{GEMINI_BASE_URL}/{model_name}:generateContent",
            headers=headers,
            json=data,
            timeout=30
        )
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)
        
        print(f"⏱️  Tempo de resposta: {response_time}ms")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ SUCESSO! Resposta: {text_response[:100]}...")
                    print(f"📈 Tokens usados: {result.get('usageMetadata', {}).get('totalTokenCount', 'N/A')}")
                    return True, "Sucesso"
                else:
                    print("❌ ERRO: Resposta sem candidatos válidos")
                    print(f"📝 Resposta completa: {json.dumps(result, indent=2)}")
                    return False, "Resposta inválida"
            except json.JSONDecodeError as e:
                print(f"❌ ERRO: Não foi possível decodificar JSON: {e}")
                print(f"📝 Resposta bruta: {response.text}")
                return False, f"JSON inválido: {e}"
        else:
            print(f"❌ ERRO HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📝 Detalhes do erro: {json.dumps(error_detail, indent=2)}")
                error_message = error_detail.get('error', {}).get('message', 'Erro desconhecido')
                return False, f"HTTP {response.status_code}: {error_message}"
            except Exception as e:
                print(f"📝 Erro ao processar resposta JSON: {e}")
                print(f"📝 Resposta bruta: {response.text}")
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
                
    except requests.exceptions.Timeout:
        print("❌ ERRO: Timeout na requisição (30s)")
        return False, "Timeout"
    except requests.exceptions.ConnectionError as e:
        print(f"❌ ERRO: Problema de conexão: {e}")
        return False, f"Conexão: {e}"
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRO: Erro na requisição: {e}")
        return False, f"Requisição: {e}"
    except Exception as e:
        print(f"❌ ERRO: Erro inesperado: {e}")
        return False, f"Inesperado: {e}"

def test_all_models():
    print_separator("STEP 2: TESTE INDIVIDUAL DE TODOS OS MODELOS")
    
    results = {}
    working_models = []
    failed_models = []
    
    for i, model in enumerate(ALL_GEMINI_MODELS, 1):
        print(f"\n[{i}/{len(ALL_GEMINI_MODELS)}] " + "-"*40)
        success, error_msg = test_single_model(model)
        
        results[model] = {
            'success': success,
            'error': error_msg
        }
        
        if success:
            working_models.append(model)
            print(f"✅ {model}: FUNCIONANDO")
        else:
            failed_models.append(model)
            print(f"❌ {model}: FALHOU - {error_msg}")
        
        # Pequena pausa entre requisições
        time.sleep(1)
    
    return results, working_models, failed_models

def test_fallback_system():
    print_separator("STEP 3: TESTE DO SISTEMA DE FALLBACK")
    
    print("🔄 Simulando o sistema de fallback da aplicação...")
    
    # Usar a mesma ordem do app.py atual
    app_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash", "gemini-2.5-flash"]
    
    for i, model in enumerate(app_models, 1):
        print(f"\n[Tentativa {i}] Testando {model}...")
        success, error_msg = test_single_model(model, "Diga apenas 'Teste funcionando!'")
        
        if success:
            print(f"🎉 Sistema de fallback funcionou! Modelo {model} respondeu com sucesso.")
            return True, model
        else:
            print(f"⚠️  Modelo {model} falhou: {error_msg}")
            if i < len(app_models):
                print("🔄 Tentando próximo modelo...")
    
    print("💥 ERRO: Todos os modelos do sistema de fallback falharam!")
    return False, None

def generate_summary_report(results, working_models, failed_models, fallback_result, fallback_model):
    print_separator("RELATÓRIO FINAL DE DIAGNÓSTICO")
    
    print("📊 RESUMO GERAL:")
    print(f"   • Total de modelos testados: {len(ALL_GEMINI_MODELS)}")
    print(f"   • Modelos funcionando: {len(working_models)}")
    print(f"   • Modelos com falha: {len(failed_models)}")
    print(f"   • Taxa de sucesso: {len(working_models)/len(ALL_GEMINI_MODELS)*100:.1f}%")
    
    if working_models:
        print("\n✅ MODELOS FUNCIONANDO:")
        for model in working_models:
            print(f"   • {model}")
    
    if failed_models:
        print("\n❌ MODELOS COM FALHA:")
        for model in failed_models:
            error = results[model]['error']
            print(f"   • {model}: {error}")
    
    print("\n🔄 SISTEMA DE FALLBACK:")
    if fallback_result:
        print(f"   ✅ FUNCIONANDO - Modelo ativo: {fallback_model}")
    else:
        print("   ❌ FALHOU - Nenhum modelo da lista funcionou")
    
    print("\n💡 RECOMENDAÇÕES:")
    if working_models:
        print(f"   1. Use o modelo mais estável: {working_models[0]}")
        print(f"   2. Configure fallback com modelos funcionando: {', '.join(working_models[:3])}")
    else:
        print("   1. Verifique sua chave API no Google AI Studio")
        print("   2. Aguarde alguns minutos e tente novamente")
        print("   3. Considere gerar uma nova chave API")
    
    if 'HTTP 429' in str(results):
        print("   4. Você atingiu o limite de quota - aguarde ou upgrade sua conta")
    
    if 'HTTP 400' in str(results):
        print("   5. Alguns modelos podem não estar disponíveis na sua região")

def main():
    print("🚀 INICIANDO DIAGNÓSTICO COMPLETO DA API GEMINI")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Verificar chave API
    if not test_api_key():
        print("\n💥 DIAGNÓSTICO INTERROMPIDO: Problema com a chave API")
        return
    
    # Step 2: Testar todos os modelos
    results, working_models, failed_models = test_all_models()
    
    # Step 3: Testar sistema de fallback
    fallback_result, fallback_model = test_fallback_system()
    
    # Step 4: Gerar relatório
    generate_summary_report(results, working_models, failed_models, fallback_result, fallback_model)
    
    print("\n🏁 DIAGNÓSTICO CONCLUÍDO")
    print("📄 Para mais detalhes, revise os logs acima.")

if __name__ == "__main__":
    main()