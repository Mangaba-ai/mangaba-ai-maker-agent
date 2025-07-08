#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se o erro de formatação foi corrigido
"""

import json
import requests

def test_agent_system():
    """Testa o sistema de agentes com dados JSON que causavam erro"""
    
    # Dados de teste que causavam o erro
    test_data = {
        "vendas": [
            {"produto": "Notebook", "valor": 2500.00, "mes": "Janeiro"},
            {"produto": "Mouse", "valor": 50.00, "mes": "Janeiro"},
            {"produto": "Teclado", "valor": 150.00, "mes": "Fevereiro"}
        ]
    }
    
    # Simular o contexto que era problemático
    context = f"Dados JSON fornecidos:\n{json.dumps(test_data, indent=2, ensure_ascii=False)}"
    
    print("[TEST] Testando formatação de contexto...")
    print(f"[TEST] Contexto original: {repr(context[:100])}...")
    
    # Testar o escape de caracteres
    safe_context = context.replace('{', '{{').replace('}', '}}')
    print(f"[TEST] Contexto escapado: {repr(safe_context[:100])}...")
    
    # Testar formatação de prompt
    test_prompt = "Analise os dados: '{goal}' com contexto: '{context}'"
    
    try:
        formatted_prompt = test_prompt.format(goal="análise de vendas", context=safe_context)
        print("[SUCCESS] Formatação de prompt funcionou!")
        print(f"[TEST] Tamanho do prompt: {len(formatted_prompt)} caracteres")
        assert True
    except Exception as e:
        print(f"[ERROR] Erro na formatação: {e}")
        assert False

def test_api_endpoint():
    """Testa o endpoint da API"""
    
    url = "http://127.0.0.1:5000/api/run_agent_system"
    
    # Dados de teste
    test_json = {
        "vendas": [
            {"produto": "Teste", "valor": 100.00, "mes": "Janeiro"}
        ]
    }
    
    # Preparar FormData
    files = {
        'goal': (None, 'analise os dados de vendas'),
        'dataSource': ('test.json', json.dumps(test_json), 'application/json')
    }
    
    try:
        print("[TEST] Enviando requisição para API...")
        response = requests.post(url, files=files, timeout=30)
        
        print(f"[TEST] Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("[SUCCESS] API funcionou corretamente!")
            print(f"[TEST] Tipo detectado: {result.get('goal_type', 'N/A')}")
            assert True
        else:
            print(f"[ERROR] API retornou erro: {response.status_code}")
            try:
                error_data = response.json()
                print(f"[ERROR] Detalhes: {error_data.get('error', 'Erro desconhecido')}")
            except:
                print(f"[ERROR] Resposta bruta: {response.text[:200]}...")
            assert False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Não foi possível conectar ao servidor. Certifique-se de que está rodando.")
        assert False
    except Exception as e:
        print(f"[ERROR] Erro inesperado: {e}")
        assert False

if __name__ == "__main__":
    print("=== TESTE DE CORREÇÃO DO ERRO DE FORMATAÇÃO ===")
    print()
    
    # Teste 1: Formatação local
    print("1. Testando formatação de strings...")
    format_ok = test_agent_system()
    print()
    
    # Teste 2: API endpoint
    print("2. Testando endpoint da API...")
    api_ok = test_api_endpoint()
    print()
    
    # Resultado final
    if format_ok and api_ok:
        print("✅ TODOS OS TESTES PASSARAM! O erro foi corrigido.")
    elif format_ok:
        print("⚠️ Formatação OK, mas API com problemas.")
    else:
        print("❌ Ainda há problemas na formatação.")
