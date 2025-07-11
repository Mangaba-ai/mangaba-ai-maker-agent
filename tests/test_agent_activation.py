
import pytest
import sys
import os

# Adiciona o diretório 'src' ao PYTHONPATH para que app.py possa ser importado
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mangaba-ai-maker-agent/src')))

from app import enhanced_detect_goal_type

@pytest.mark.parametrize("goal, context, expected_type", [
    ("Análise de concorrência para o novo produto", "", "competitive_analysis"),
    ("Planejamento estratégico para o próximo ano fiscal", "", "strategic_planning"),
    ("Relatório de vendas do último trimestre", "", "sales_analysis"),
    ("Gerenciamento de backlog de features do aplicativo", "", "product_management"),
    ("Análise de comportamento de usuários no site", "", "user_management"),
    ("Criação de um cronograma para o projeto X", "", "task_management"),
    ("Análise financeira da empresa", "", "financial_analysis"),
    ("Plano de recrutamento e seleção de novos talentos", "", "hr_management"),
    ("Campanha de marketing digital para o lançamento", "", "marketing_analysis"),
    ("Otimização de processos operacionais", "", "operations_management"),
    ("Avaliação de novas tecnologias para a infraestrutura", "", "technology_analysis"),
    ("Escrever um artigo científico sobre IA", "", "academic"),
    ("Preparar um relatório técnico sobre a falha do sistema", "", "technical_report"),
    ("Resumir o documento de 50 páginas", "", "summary"),
    ("Análise de dados de clientes", "", "data_analysis"),
    ("Criar documentação para a API", "", "documentation"),
    ("Planejamento de eventos para o próximo semestre", "", "planning"),
    ("Desenvolver um criativo para a campanha de natal", "", "creative"),
    ("Qualquer coisa que não se encaixe em categorias específicas", "", "general"),
    ("Análise de concorrência com foco em market share", "dados de mercado", "competitive_analysis"),
    ("OKR para o planejamento estratégico", "visão da empresa", "strategic_planning"),
    ("Análise de vendas e faturamento", "dados de crm", "sales_analysis"),
    ("Gestão de produto e roadmap", "features e backlog", "product_management"),
    ("Gestão de usuários e UX", "jornada do cliente", "user_management"),
    ("Gestão de tarefas e sprint", "projeto agile", "task_management"),
    ("Análise financeira e orçamento", "fluxo de caixa", "financial_analysis"),
    ("Gestão de RH e recrutamento", "colaboradores e treinamento", "hr_management"),
    ("Análise de marketing e campanha", "branding e publicidade", "marketing_analysis"),
    ("Gestão de operações e processos", "workflow e automação", "operations_management"),
    ("Análise de tecnologia e inovação", "sistemas e infraestrutura", "technology_analysis"),
    ("Pesquisa acadêmica sobre machine learning", "artigo científico", "academic"),
    ("Relatório técnico de auditoria", "compliance", "technical_report"),
    ("Resumo executivo do projeto", "sumarizar", "summary"),
    ("Análise de dados e métricas", "dashboard", "data_analysis"),
    ("Documentação de procedimentos", "manual", "documentation"),
    ("Plano de projeto", "cronograma", "planning"),
    ("Conteúdo criativo para redes sociais", "post", "creative"),
])
def test_enhanced_detect_goal_type(goal, context, expected_type):
    detected_type = enhanced_detect_goal_type(goal, context)
    assert detected_type == expected_type

