import os
import requests
import json
from flask import Flask, render_template, request, jsonify, send_from_directory, Response, stream_with_context, redirect, url_for
from dotenv import load_dotenv
from datetime import datetime
import time

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configure paths relative to the project root
# O projeto_root é o diretório pai de 'src', onde estão as pastas 'templates' e 'static'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(project_root, 'templates')
static_dir = os.path.join(project_root, 'static')
data_dir = os.path.join(project_root, 'data') # Diretório para dados

# Cria o diretório 'data' se não existir
os.makedirs(data_dir, exist_ok=True)

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Configuração da API Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Lista de modelos em ordem de prioridade (apenas modelo verificado como estável)
GEMINI_MODELS = [
    "gemini-2.0-flash"  # Único modelo confirmado como funcionando consistentemente
]

# --- Sistema Avançado de Detecção e Ativação de Agentes ---
def enhanced_detect_goal_type(goal: str, context: str = "") -> str:
    """
    Detecta o tipo de objetivo baseado em palavras-chave, contexto e análise de múltiplos domínios
    Sistema expandido para garantir ativação de todos os agentes relevantes
    """
    goal_lower = goal.lower()
    context_lower = context.lower() if context else ""
    combined_text = f"{goal_lower} {context_lower}"
    
    # Priorize tipos mais específicos primeiro

    # Criativo/Marketing (mais específico que marketing_analysis ou general planning)
    if any(word in combined_text for word in ['criativo', 'conteúdo', 'post', 'artigo blog', 'campanha de marketing', 'publicidade', 'branding', 'design', 'copywriting', 'social media content', 'peça criativa', 'material gráfico', 'criação de campanha', 'marketing de conteúdo', 'campanha publicitária']):
        return 'creative'

    # Tipos acadêmicos/científicos
    elif any(word in combined_text for word in ['artigo', 'paper', 'pesquisa', 'estudo', 'análise científica', 'metodologia', 'revisão bibliográfica', 'tese', 'dissertação', 'monografia', 'científico', 'publicação', 'pesquisa acadêmica', 'trabalho científico', 'artigo científico']):
        return 'academic'

    # Relatórios técnicos
    elif any(word in combined_text for word in ['relatório técnico', 'report técnico', 'análise técnica', 'diagnóstico', 'avaliação técnica', 'auditoria', 'compliance', 'especificação técnica', 'documento técnico', 'laudo', 'parecer técnico', 'relatório de conformidade']):
        return 'technical_report'

    # Resumos e sínteses
    elif any(word in combined_text for word in ['resumo', 'resumir', 'sintetizar', 'síntese', 'sumarizar', 'executive summary', 'sumário executivo', 'abstract', 'condensar', 'apresentação resumida']):
        return 'summary'

    # Planejamento estratégico (PRIORIDADE ALTA)
    elif any(word in combined_text for word in ['planejamento estratégico', 'estratégia empresarial', 'plano estratégico', 'visão estratégica', 'missão', 'valores', 'objetivos estratégicos', 'metas organizacionais', 'okr', 'okrs', 'objectives and key results', 'swot', 'balanced scorecard', 'kpi estratégico', 'planejamento de longo prazo', 'diretrizes estratégicas', 'plano de negócios', 'estratégia de crescimento']):
        return 'strategic_planning'

    # Análise de concorrência (PRIORIDADE ALTA)
    elif any(word in combined_text for word in ['análise de concorrência', 'concorrência', 'concorrentes', 'benchmarking', 'análise competitiva', 'mercado competitivo', 'posicionamento mercado', 'competitivo', 'competitor', 'market share', 'participação mercado', 'inteligência competitiva', 'rival', 'panorama competitivo', 'estudo de mercado competitivo']):
        return 'competitive_analysis'

    # Análise de vendas e performance comercial
    elif any(word in combined_text for word in ['vendas', 'receita', 'faturamento', 'conversão', 'pipeline', 'crm', 'leads', 'prospects', 'clientes', 'ticket médio', 'ltv', 'churn', 'funil vendas', 'performance comercial', 'roi vendas', 'forecast', 'comercial', 'desempenho de vendas', 'análise de vendas']):
        return 'sales_analysis'

    # Gestão de produtos
    elif any(word in combined_text for word in ['produto', 'produtos', 'roadmap', 'features', 'backlog', 'mvp', 'user story', 'product owner', 'desenvolvimento produto', 'lançamento', 'product market fit', 'ciclo vida produto', 'gestão de produto', 'portfólio de produtos', 'inovação de produto', 'estratégia de produto']):
        return 'product_management'

    # Gestão de usuários e experiência
    elif any(word in combined_text for word in ['usuários', 'users', 'ux', 'ui', 'experiência usuário', 'jornada usuário', 'personas', 'segmentação', 'comportamento usuário', 'usabilidade', 'customer journey', 'user research', 'gestão de usuários', 'engajamento de usuários', 'satisfação do cliente', 'pesquisa de usuário']):
        return 'user_management'

    # Gestão de tarefas e projetos
    elif any(word in combined_text for word in ['tarefas', 'tasks', 'sprint', 'scrum', 'kanban', 'agile', 'projeto', 'cronograma', 'milestone', 'deliverables', 'gestão projetos', 'pmo', 'waterfall', 'gestão de tarefas', 'planejamento de projeto', 'gerenciamento de projeto', 'metodologia ágil']):
        return 'task_management'

    # Análise financeira e orçamentária
    elif any(word in combined_text for word in ['financeiro', 'orçamento', 'budget', 'fluxo caixa', 'dre', 'balanço', 'roi', 'investimento', 'custo', 'margem', 'lucro', 'ebitda', 'valuation', 'análise financeira', 'contabilidade', 'saúde financeira', 'planejamento financeiro']):
        return 'financial_analysis'

    # Recursos humanos e gestão de pessoas
    elif any(word in combined_text for word in ['recursos humanos', 'rh', 'colaboradores', 'funcionários', 'recrutamento', 'seleção', 'treinamento', 'desenvolvimento', 'performance', 'avaliação desempenho', 'cultura organizacional', 'gestão de pessoas', 'capital humano', 'engajamento de funcionários', 'políticas de rh']):
        return 'hr_management'

    # Marketing e comunicação (mais genérico que 'creative')
    elif any(word in combined_text for word in ['marketing', 'campanha', 'comunicação', 'branding', 'marca', 'publicidade', 'digital marketing', 'seo', 'sem', 'social media', 'content marketing', 'inbound', 'estratégia de marketing', 'plano de marketing', 'relações públicas']):
        return 'marketing_analysis'

    # Operações e processos
    elif any(word in combined_text for word in ['operações', 'processos', 'workflow', 'automação', 'eficiência', 'produtividade', 'lean', 'six sigma', 'melhoria contínua', 'otimização', 'gestão de operações', 'cadeia de suprimentos', 'logística', 'gestão da qualidade']):
        return 'operations_management'

    # Tecnologia e inovação
    elif any(word in combined_text for word in ['tecnologia', 'inovação', 'digital', 'transformação digital', 'ti', 'sistemas', 'software', 'infraestrutura', 'arquitetura', 'desenvolvimento', 'análise tecnológica', 'cibersegurança', 'segurança da informação', 'tendências tecnológicas']):
        return 'technology_analysis'

    # Análise de dados
    elif any(word in combined_text for word in ['dados', 'estatística', 'gráfico', 'dashboard', 'métricas', 'kpi', 'analytics', 'business intelligence', 'big data', 'data science', 'análise de dados', 'relatório de dados', 'interpretação de dados', 'modelagem de dados']):
        return 'data_analysis'

    # Documentação
    elif any(word in combined_text for word in ['documentação', 'manual', 'guia', 'tutorial', 'procedimento', 'política', 'norma', 'regulamento', 'documentar', 'instruções', 'especificação', 'criação de documentos']):
        return 'documentation'

    # Planejamento geral (mais genérico que strategic_planning ou task_management)
    elif any(word in combined_text for word in ['plano', 'planejamento', 'cronograma', 'projeto', 'agenda', 'organização', 'programação', 'planejar']):
        return 'planning'

    # Default
    else:
        return 'general'

def detect_multiple_goal_types(goal: str, context: str = "") -> list:
    """
    Detecta múltiplos tipos de objetivos que podem estar relacionados
    Garante que todos os agentes relevantes sejam acionados
    """
    goal_lower = goal.lower()
    context_lower = context.lower() if context else ""
    combined_text = f"{goal_lower} {context_lower}"
    
    detected_types = []
    
    # Mapeamento de palavras-chave para tipos de agentes
    agent_keywords = {
        'competitive_analysis': ['concorrência', 'concorrentes', 'benchmarking', 'competitivo', 'market share', 'inteligência competitiva'],
        'strategic_planning': ['estratégia', 'planejamento estratégico', 'visão', 'missão', 'okr', 'swot'],
        'sales_analysis': ['vendas', 'receita', 'conversão', 'pipeline', 'crm', 'leads', 'clientes'],
        'product_management': ['produto', 'roadmap', 'features', 'mvp', 'backlog', 'product owner'],
        'user_management': ['usuários', 'ux', 'ui', 'experiência', 'jornada', 'personas'],
        'task_management': ['tarefas', 'sprint', 'scrum', 'kanban', 'projeto', 'cronograma'],
        'financial_analysis': ['financeiro', 'orçamento', 'roi', 'custo', 'margem', 'lucro'],
        'hr_management': ['recursos humanos', 'rh', 'colaboradores', 'recrutamento', 'treinamento'],
        'marketing_analysis': ['marketing', 'campanha', 'branding', 'publicidade', 'seo'],
        'operations_management': ['operações', 'processos', 'eficiência', 'automação', 'lean'],
        'technology_analysis': ['tecnologia', 'inovação', 'digital', 'ti', 'sistemas'],
        'data_analysis': ['dados', 'estatística', 'analytics', 'dashboard', 'métricas']
    }
    
    # Verificar cada tipo de agente
    for agent_type, keywords in agent_keywords.items():
        if any(keyword in combined_text for keyword in keywords):
            detected_types.append(agent_type)
    
    # Se nenhum tipo específico foi detectado, usar o tipo principal
    if not detected_types:
        primary_type = enhanced_detect_goal_type(goal, context)
        detected_types.append(primary_type)
    
    return detected_types

def get_collaborative_agents(primary_goal_type: str, all_detected_types: list) -> list:
    """
    Determina quais agentes colaborativos devem ser acionados
    baseado no tipo principal e tipos detectados
    """
    # Agentes que sempre colaboram com tipos específicos
    collaboration_matrix = {
        'strategic_planning': ['competitive_analysis', 'financial_analysis', 'market_analysis'],
        'competitive_analysis': ['strategic_planning', 'sales_analysis', 'marketing_analysis'],
        'sales_analysis': ['competitive_analysis', 'product_management', 'user_management'],
        'product_management': ['user_management', 'technology_analysis', 'sales_analysis'],
        'user_management': ['product_management', 'marketing_analysis', 'data_analysis'],
        'financial_analysis': ['strategic_planning', 'sales_analysis', 'operations_management'],
        'marketing_analysis': ['competitive_analysis', 'user_management', 'data_analysis'],
        'operations_management': ['financial_analysis', 'technology_analysis', 'hr_management'],
        'technology_analysis': ['product_management', 'operations_management', 'data_analysis'],
        'hr_management': ['operations_management', 'strategic_planning', 'financial_analysis']
    }
    
    collaborative_agents = set()
    
    # Adicionar agentes colaborativos baseados no tipo principal
    if primary_goal_type in collaboration_matrix:
        collaborative_agents.update(collaboration_matrix[primary_goal_type])
    
    # Adicionar agentes detectados diretamente
    collaborative_agents.update(all_detected_types)
    
    # Remover o tipo principal da lista de colaborativos
    collaborative_agents.discard(primary_goal_type)
    
    return list(collaborative_agents)

# Manter compatibilidade com versão anterior
def detect_goal_type(goal: str) -> str:
    """
    Detecta o tipo de objetivo baseado em palavras-chave e contexto (versão compatível)
    """
    return enhanced_detect_goal_type(goal)

def get_abnt_formatting_rules() -> str:
    """
    Retorna as regras de formatação ABNT para incluir nos prompts
    """
    return """
    FORMATAÇÃO ABNT OBRIGATÓRIA:
    - Use fonte Times New Roman ou Arial, tamanho 12
    - Espaçamento entre linhas: 1,5
    - Margens: superior e esquerda 3cm, inferior e direita 2cm
    - Títulos principais em MAIÚSCULAS, centralizados
    - Títulos secundários em Primeira Letra Maiúscula, alinhados à esquerda
    - Citações diretas com mais de 3 linhas: recuo de 4cm, espaçamento simples, fonte 10
    - Citações indiretas: (AUTOR, ano, p. XX)
    - Referências bibliográficas em ordem alfabética
    - Numeração de páginas no canto superior direito
    - Resumo: máximo 500 palavras, parágrafo único
    - Palavras-chave: 3 a 5 palavras, separadas por ponto
    """

def generate_specialized_prompts(goal_type: str, goal: str, context: str) -> tuple:
    """
    Gera prompts especializados baseados no tipo de objetivo
    """
    abnt_rules = get_abnt_formatting_rules()
    
    prompts = {
        'academic': {
            'researcher': """
            Você é um pesquisador acadêmico especializado. Analise o objetivo: "{goal}" e crie uma estrutura detalhada para um trabalho acadêmico seguindo metodologia científica.
            
            Contexto fornecido:
            '''{context}'''
            
            Sua estrutura deve incluir:
            1. Introdução e justificativa
            2. Objetivos (geral e específicos)
            3. Revisão bibliográfica
            4. Metodologia
            4. Resultados esperados
            5. Conclusões
            6. Referências
            
            {abnt_rules}
            """,
            'writer': """
            Você é um escritor acadêmico especializado em produção científica. Desenvolva um texto acadêmico completo baseado na estrutura:
            
            {outline}
            
            Contexto de referência:
            '''{context}'''
            
            REQUISITOS OBRIGATÓRIOS:
            - Linguagem formal e técnica
            - Citações e referências adequadas
            - Argumentação lógica e fundamentada
            - Metodologia clara e replicável
            {abnt_rules}
            
            Produza um texto de qualidade acadêmica, pronto para submissão.
            """
        },
        'technical_report': {
            'researcher': """
            Você é um analista técnico especializado. Analise o objetivo: "{goal}" e estruture um relatório técnico profissional.
            
            Dados técnicos:
            '''{context}'''
            
            Estruture o relatório com:
            1. Sumário executivo
            2. Introdução e objetivos
            3. Metodologia aplicada
            4. Resultados e análises
            5. Discussão técnica
            6. Conclusões e recomendações
            7. Anexos (quando necessário)
            
            {abnt_rules}
            """,
            'writer': """
            Você é um redator técnico especializado. Desenvolva um relatório técnico completo baseado na estrutura:
            
            {outline}
            
            Dados de referência:
            '''{context}'''
            
            CARACTERÍSTICAS OBRIGATÓRIAS:
            - Linguagem técnica precisa
            - Dados quantitativos quando possível
            - Gráficos e tabelas (descreva quando necessário)
            - Recomendações práticas e implementáveis
            {abnt_rules}
            
            Produza um relatório profissional e acionável.
            """
        },
        'summary': {
            'researcher': """
            Você é um especialista em síntese de informações. Analise o objetivo: "{goal}" e estruture um resumo eficiente.
            
            Conteúdo para resumir:
            '''{context}'''
            
            Estruture o resumo com:
            1. Pontos principais identificados
            2. Informações essenciais
            3. Conclusões-chave
            4. Insights relevantes
            
            {abnt_rules}
            """,
            'writer': """
            Você é um redator especializado em sínteses. Crie um resumo claro e conciso baseado na estrutura:
            
            {outline}
            
            Conteúdo original:
            '''{context}'''
            
            CARACTERÍSTICAS DO RESUMO:
            - Máximo 500 palavras para resumo executivo
            - Linguagem clara e objetiva
            - Preservação das informações essenciais
            - Estrutura lógica e fluida
            {abnt_rules}
            
            Produza um resumo profissional e informativo.
            """
        },
        'data_analysis': {
            'researcher': """
            Você é um analista de dados especializado. Analise o objetivo: "{goal}" e estruture uma análise de dados completa.
            
            Dados fornecidos:
            '''{context}'''
            
            Estruture a análise com:
            1. Visão geral dos dados
            2. Metodologia de análise
            3. Estatísticas descritivas
            4. Padrões e tendências identificados
            5. Insights e correlações
            6. Recomendações baseadas em dados
            
            {abnt_rules}
            """,
            'writer': """
            Você é um especialista em relatórios de dados. Desenvolva uma análise completa baseada na estrutura:
            
            {outline}
            
            Dataset:
            '''{context}'''
            
            ELEMENTOS OBRIGATÓRIOS:
            - Interpretação clara dos dados
            - Visualizações descritas (quando aplicável)
            - Insights acionáveis
            - Conclusões baseadas em evidências
            {abnt_rules}
            
            Produza uma análise de dados profissional e compreensível.
            """
        },
        'strategic_planning': {
            'researcher': """
            Você é um consultor estratégico sênior especializado em planejamento empresarial;
            Analise o objetivo: "{goal}";
            Estruture um plano estratégico abrangente
            
            Contexto organizacional:
            '''{context}'''
            
            Estruture o planejamento estratégico com:
            1. Análise do ambiente interno e externo (SWOT)
            2. Definição de missão, visão e valores
            3. Objetivos estratégicos de longo prazo
            4. OKRs (Objectives and Key Results) trimestrais e anuais
            5. Estratégias e iniciativas prioritárias
            6. Plano de implementação e cronograma
            7. Indicadores de performance (KPIs)
            8. Gestão de riscos e contingências
            9. Orçamento e recursos necessários
            
            {abnt_rules}
            """,
            'writer': """
            Você é um especialista em documentação estratégica empresarial. Desenvolva um plano estratégico completo baseado na estrutura:
            
            {outline}
            
            Dados organizacionais:
            '''{context}'''
            
            ELEMENTOS OBRIGATÓRIOS:
            - Análise situacional detalhada
            - Objetivos SMART (específicos, mensuráveis, atingíveis, relevantes, temporais)
            - OKRs estruturados com objetivos qualitativos e key results quantitativos
            - Estratégias claras e acionáveis
            - Cronograma de implementação realista
            - Métricas de acompanhamento e revisão trimestral de OKRs
            - Análise de viabilidade financeira
            - Planos de contingência
            {abnt_rules}
            
            Produza um plano estratégico executável e profissional.
            """
        },
        'competitive_analysis': {
            'researcher': """
            Você é um analista de mercado especializado em inteligência competitiva. Analise o objetivo: "{goal}" e estruture uma análise de concorrência completa.
            
            Dados de mercado e concorrentes:
            '''{context}'''
            
            Estruture a análise competitiva com:
            1. Mapeamento do cenário competitivo
            2. Identificação dos principais concorrentes
            3. Análise de produtos/serviços concorrentes
            4. Estratégias de preços e posicionamento
            5. Forças e fraquezas dos concorrentes
            6. Participação de mercado e tendências
            7. Oportunidades e ameaças identificadas
            8. Recomendações estratégicas
            
            {abnt_rules}
            """,
            'writer': """
            Você é um especialista em relatórios de inteligência competitiva. Desenvolva uma análise de concorrência detalhada baseada na estrutura:
            
            {outline}
            
            Informações de mercado:
            '''{context}'''
            
            COMPONENTES ESSENCIAIS:
            - Perfil detalhado dos concorrentes principais
            - Análise comparativa de produtos/serviços
            - Benchmarking de preços e estratégias
            - Matriz de posicionamento competitivo
            - Análise de market share e tendências
            - Identificação de gaps de mercado
            - Recomendações táticas e estratégicas
            {abnt_rules}
            
            Produza uma análise competitiva acionável e estratégica.
            """
        },
        'sales_analysis': {
            'researcher': """
            Você é um analista de vendas sênior especializado em performance comercial. Analise o objetivo: "{goal}" e estruture uma análise completa de vendas.
            
            Dados de vendas:
            '''{context}'''
            
            Estruture a análise com:
            1. Visão geral do desempenho de vendas
            2. Análise de métricas-chave (receita, conversão, ticket médio, LTV, churn)
            3. Segmentação de clientes e produtos
            4. Análise de tendências e sazonalidade
            5. Identificação de oportunidades e gargalos
            6. Benchmarking e comparações históricas
            7. Previsões e projeções
            8. Recomendações estratégicas para crescimento
            
            {abnt_rules}
            """,
            'writer': """
            Você é um especialista em relatórios comerciais. Desenvolva uma análise de vendas detalhada baseada na estrutura:
            
            {outline}
            
            Dados comerciais:
            '''{context}'''
            
            ELEMENTOS OBRIGATÓRIOS:
            - Dashboard executivo com KPIs principais
            - Análise quantitativa com gráficos e tabelas
            - Insights acionáveis para equipe comercial
            - Plano de ação com metas específicas
            - ROI e análise de investimento em vendas
            - Estratégias de retenção e upselling
            {abnt_rules}
            
            Produza um relatório comercial estratégico e acionável.
            """
        },
        'financial_analysis': {
            'researcher': """
            Você é um analista financeiro sênior especializado em análise empresarial. Analise o objetivo: "{goal}" e estruture uma análise financeira completa.
            
            Dados financeiros:
            '''{context}'''
            
            Estruture a análise com:
            1. Análise de demonstrações financeiras (DRE, Balanço, Fluxo de Caixa)
            2. Indicadores de rentabilidade e liquidez
            3. Análise de custos e margem
            4. ROI e análise de investimentos
            5. Projeções financeiras e cenários
            6. Análise de riscos financeiros
            7. Benchmarking setorial
            8. Recomendações para otimização financeira
            
            {abnt_rules}
            """,
            'writer': """
            Você é um especialista em relatórios financeiros. Desenvolva uma análise financeira detalhada baseada na estrutura:
            
            {outline}
            
            Dados financeiros:
            '''{context}'''
            
            ELEMENTOS OBRIGATÓRIOS:
            - Resumo executivo financeiro
            - Análise de indicadores-chave (ROI, EBITDA, Margem)
            - Gráficos e tabelas financeiras
            - Análise de tendências e variações
            - Recomendações de investimento e corte de custos
            - Projeções e cenários futuros
            {abnt_rules}
            
            Produza um relatório financeiro profissional e acionável.
            """
        },
        'hr_management': {
            'researcher': """
            Você é um especialista em gestão de recursos humanos. Analise o objetivo: "{goal}" e estruture uma análise completa de RH.
            
            Dados de RH:
            '''{context}'''
            
            Estruture a análise com:
            1. Análise do capital humano atual
            2. Indicadores de performance e engajamento
            3. Análise de turnover e retenção
            4. Mapeamento de competências e gaps
            5. Planos de desenvolvimento e treinamento
            6. Cultura organizacional e clima
            7. Estratégias de recrutamento e seleção
            8. Recomendações para gestão de pessoas
            
            {abnt_rules}
            """,
            'writer': """
            Você é um especialista em relatórios de RH. Desenvolva uma análise de recursos humanos baseada na estrutura:
            
            {outline}
            
            Dados de RH:
            '''{context}'''
            
            ELEMENTOS OBRIGATÓRIOS:
            - Dashboard de indicadores de RH
            - Análise de performance e produtividade
            - Planos de desenvolvimento individuais
            - Estratégias de retenção de talentos
            - Programas de treinamento e capacitação
            - Métricas de satisfação e engajamento
            {abnt_rules}
            
            Produza um relatório de RH estratégico e implementável.
            """
        },
        'marketing_analysis': {
            'researcher': """
            Você é um analista de marketing digital especializado. Analise o objetivo: "{goal}" e estruture uma análise completa de marketing.
            
            Dados de marketing:
            '''{context}'''
            
            Estruture a análise com:
            1. Análise do mix de marketing atual
            2. Performance de campanhas e canais
            3. Análise de audiência e segmentação
            4. ROI de investimentos em marketing
            5. Análise de concorrência em marketing
            6. Tendências e oportunidades de mercado
            7. Estratégias de branding e posicionamento
            8. Recomendações para otimização de marketing
            
            {abnt_rules}
            """,
            'writer': """
            Você é um especialista em relatórios de marketing. Desenvolva uma análise de marketing baseada na estrutura:
            
            {outline}
            
            Dados de marketing:
            '''{context}'''
            
            ELEMENTOS OBRIGATÓRIOS:
            - Dashboard de métricas de marketing
            - Análise de ROI por canal
            - Estratégias de conteúdo e engajamento
            - Planos de campanhas futuras
            - Análise de brand awareness
            - Recomendações de otimização de budget
            {abnt_rules}
            
            Produza um relatório de marketing estratégico e acionável.
            """
        },
        'operations_management': {
            'researcher': """
            Você é um especialista em gestão de operações. Analise o objetivo: "{goal}" e estruture uma análise completa de operações.
            
            Dados operacionais:
            '''{context}'''
            
            Estruture a análise com:
            1. Mapeamento de processos atuais
            2. Análise de eficiência e produtividade
            3. Identificação de gargalos e desperdícios
            4. Análise de qualidade e conformidade
            5. Oportunidades de automação
            6. Benchmarking operacional
            7. Estratégias de melhoria contínua
            8. Recomendações para otimização operacional
            
            {abnt_rules}
            """,
            'writer': """
            Você é um especialista em relatórios operacionais. Desenvolva uma análise de operações baseada na estrutura:
            
            {outline}
            
            Dados operacionais:
            '''{context}'''
            
            ELEMENTOS OBRIGATÓRIOS:
            - Mapa de processos otimizado
            - Indicadores de performance operacional
            - Planos de melhoria e automação
            - Análise de custos operacionais
            - Estratégias lean e six sigma
            - Cronograma de implementação
            {abnt_rules}
            
            Produza um relatório operacional prático e implementável.
            """
        },
        'technology_analysis': {
            'researcher': """
            Você é um analista de tecnologia especializado. Analise o objetivo: "{goal}" e estruture uma análise completa de tecnologia.
            
            Dados tecnológicos:
            '''{context}'''
            
            Estruture a análise com:
            1. Avaliação da infraestrutura tecnológica atual
            2. Análise de sistemas e arquitetura
            3. Identificação de gaps tecnológicos
            4. Oportunidades de inovação e digitalização
            5. Análise de segurança e compliance
            6. Roadmap de transformação digital
            7. Análise de ROI tecnológico
            8. Recomendações para modernização
            
            {abnt_rules}
            """,
            'writer': """
            Você é um especialista em relatórios de tecnologia. Desenvolva uma análise tecnológica baseada na estrutura:
            
            {outline}
            
            Dados tecnológicos:
            '''{context}'''
            
            ELEMENTOS OBRIGATÓRIOS:
            - Arquitetura tecnológica recomendada
            - Plano de modernização e migração
            - Análise de custos e benefícios
            - Estratégias de segurança cibernética
            - Roadmap de implementação tecnológica
            - Métricas de performance de TI
            {abnt_rules}
            
            Produza um relatório tecnológico estratégico e implementável.
            """
        },
        'product_management': {
            'researcher': """
            Você é um Product Manager sênior especializado em estratégia de produtos. Analise o objetivo: "{goal}" e estruture um plano de gestão de produtos.
            
            Dados de produtos:
            '''{context}'''
            
            Estruture o plano com:
            1. Análise do portfólio atual de produtos
            2. Pesquisa de mercado e análise competitiva
            3. Definição de personas e necessidades dos usuários
            4. Roadmap de desenvolvimento e priorização
            5. Especificações funcionais e técnicas
            6. Estratégia de lançamento e go-to-market
            7. Métricas de sucesso e KPIs de produto
            8. Análise de viabilidade e ROI
            
            {abnt_rules}
            """,
            'writer': """
            Você é um especialista em documentação de produtos. Desenvolva um plano de produto completo baseado na estrutura:
            
            {outline}
            
            Informações de produto:
            '''{context}'''
            
            COMPONENTES ESSENCIAIS:
            - Product Vision e estratégia clara
            - User Stories e casos de uso detalhados
            - Roadmap visual com timelines realistas
            - Análise de features e priorização (MoSCoW)
            - Plano de testes e validação
            - Estratégia de pricing e monetização
            - Métricas de adoção e engajamento
            {abnt_rules}
            
            Produza um documento de produto profissional e executável.
            """
        },
        'user_management': {
            'researcher': """
            Você é um especialista em experiência do usuário e análise comportamental. Analise o objetivo: "{goal}" e estruture uma análise de usuários.
            
            Dados de usuários:
            '''{context}'''
            
            Estruture a análise com:
            1. Perfil demográfico e comportamental dos usuários
            2. Jornada do usuário e pontos de contato
            3. Análise de engajamento e retenção
            4. Segmentação de usuários e personas
            5. Identificação de pain points e oportunidades
            6. Análise de usabilidade e UX
            7. Métricas de satisfação e NPS
            8. Estratégias de melhoria da experiência
            
            {abnt_rules}
            """,
            'writer': """
            Você é um especialista em relatórios de UX e análise de usuários. Desenvolva uma análise completa baseada na estrutura:
            
            {outline}
            
            Dados comportamentais:
            '''{context}'''
            
            ELEMENTOS FUNDAMENTAIS:
            - Personas detalhadas com dados reais
            - Mapa da jornada do usuário com touchpoints
            - Análise de funil de conversão
            - Heatmaps e análise de comportamento
            - Recomendações de UX/UI prioritizadas
            - Plano de testes A/B e validação
            - Estratégias de onboarding e retenção
            {abnt_rules}
            
            Produza um relatório de UX acionável e centrado no usuário.
            """
        },
        'task_management': {
            'researcher': """
            Você é um especialista em gestão de projetos e metodologias ágeis. Analise o objetivo: "{goal}" e estruture um plano de gestão de tarefas.
            
            Dados de tarefas e projetos:
            '''{context}'''
            
            Estruture o plano com:
            1. Análise do backlog atual e priorização
            2. Estruturação de sprints e metodologia ágil
            3. Definição de épicos, user stories e tasks
            4. Estimativas de esforço e capacity planning
            5. Identificação de dependências e riscos
            6. Cronograma e milestones principais
            7. Métricas de produtividade e velocity
            8. Estratégias de otimização de processos
            
            {abnt_rules}
            """,
            'writer': """
            Você é um especialista em documentação de projetos ágeis. Desenvolva um plano de gestão completo baseado na estrutura:
            
            {outline}
            
            Dados de projeto:
            '''{context}'''
            
            COMPONENTES OBRIGATÓRIOS:
            - Backlog priorizado com critérios claros
            - Sprint planning com estimativas realistas
            - Definition of Done e critérios de aceitação
            - Burndown charts e métricas de progresso
            - Risk management e planos de contingência
            - Retrospectivas e melhorias contínuas
            - Comunicação e stakeholder management
            {abnt_rules}
            
            Produza um plano de projeto ágil e executável.
            """
        },
        'general': {
            'researcher': """
            Você é um pesquisador versátil. Analise o objetivo: "{goal}" e crie uma estrutura lógica e abrangente.
            
            Contexto fornecido:
            '''{context}'''
            
            Desenvolva uma estrutura adequada ao objetivo, incluindo:
            1. Introdução ao tema
            2. Desenvolvimento dos pontos principais
            3. Análise e discussão
            4. Conclusões
            
            {abnt_rules}
            """,
            'writer': """
            Você é um redator profissional versátil. Desenvolva um conteúdo completo baseado na estrutura:
            
            {outline}
            
            Contexto de referência:
            '''{context}'''
            
            PADRÕES DE QUALIDADE:
            - Linguagem adequada ao público-alvo
            - Estrutura lógica e coerente
            - Conteúdo informativo e relevante
            {abnt_rules}
            
            Produza um texto de alta qualidade e bem estruturado.
            """
        }
    }
    
    selected_prompts = prompts.get(goal_type, prompts['general'])
    return selected_prompts['researcher'], selected_prompts['writer']

# --- Classes do Sistema Multi-Agente Avançado ---
class MangabaAgentOrchestrator:
    """
    Orquestrador avançado para coordenação de múltiplos agentes especializados
    """
    
    def __init__(self, send_update=None):
        self.send_update = send_update
        self.agents_results = {}
        self.collaboration_matrix = {
            'sales_analysis': ['product_management', 'user_management'],
            'product_management': ['sales_analysis', 'user_management', 'task_management'],
            'user_management': ['product_management', 'sales_analysis'],
            'task_management': ['product_management'],
            'strategic_planning': ['sales_analysis', 'product_management', 'competitive_analysis'],
            'competitive_analysis': ['strategic_planning', 'product_management']
        }
    
    def should_collaborate(self, primary_goal_type: str) -> list:
        """
        Determina quais agentes devem colaborar baseado no tipo de objetivo principal
        """
        return self.collaboration_matrix.get(primary_goal_type, [])
    
    def run_parallel_analysis(self, goal: str, context: str, primary_goal_type: str) -> dict:
        """
        Executa análise paralela com múltiplos agentes especializados (método original)
        """
        collaborative_agents = self.should_collaborate(primary_goal_type)
        return self.run_parallel_analysis_enhanced(goal, context, primary_goal_type, collaborative_agents)
    
    def run_parallel_analysis_enhanced(self, goal: str, context: str, primary_goal_type: str, collaborative_agents: list) -> dict:
        """
        Executa análise paralela com agentes colaborativos específicos
        """
        results = {'primary': None, 'collaborative': {}}
        
        if self.send_update:
            self.send_update(f"[ORCHESTRATOR] Iniciando análise colaborativa: {primary_goal_type} + {collaborative_agents}", 'log')
        
        # Análise principal
        try:
            researcher_prompt, writer_prompt = generate_specialized_prompts(primary_goal_type, goal, context)
            primary_outline = agent_researcher(goal, context, researcher_prompt, primary_goal_type, self.send_update)
            results['primary'] = {
                'goal_type': primary_goal_type,
                'outline': primary_outline,
                'writer_prompt': writer_prompt
            }
            if self.send_update:
                self.send_update(f"[ORCHESTRATOR] Análise principal ({primary_goal_type}) concluída", 'log')
        except Exception as e:
            if self.send_update:
                self.send_update(f"[ORCHESTRATOR] Erro na análise principal: {e}", 'log')
            results['primary'] = None
        
        # Análises colaborativas
        for agent_type in collaborative_agents:
            try:
                if self.send_update:
                    self.send_update(f"[ORCHESTRATOR] Executando análise colaborativa: {agent_type}", 'log')
                
                # Tentar usar prompt especializado, senão usar genérico
                try:
                    collab_researcher_prompt, collab_writer_prompt = generate_specialized_prompts(agent_type, goal, context)
                except:
                    # Fallback para prompt genérico
                    collab_researcher_prompt, collab_writer_prompt = generate_specialized_prompts('general', goal, context)
                    if self.send_update:
                        self.send_update(f"[ORCHESTRATOR] Usando prompt genérico para {agent_type}", 'log')
                
                collab_outline = agent_researcher(goal, context, collab_researcher_prompt, agent_type, self.send_update)
                
                results['collaborative'][agent_type] = {
                    'outline': collab_outline,
                    'writer_prompt': collab_writer_prompt
                }
                
                if self.send_update:
                    self.send_update(f"[ORCHESTRATOR] Análise colaborativa ({agent_type}) concluída", 'log')
            except Exception as e:
                if self.send_update:
                    self.send_update(f"[ORCHESTRATOR] Erro na análise colaborativa {agent_type}: {e}", 'log')
                results['collaborative'][agent_type] = None
        
        return results
    
    def synthesize_collaborative_content(self, goal: str, context: str, analysis_results: dict) -> str:
        """
        Sintetiza o conteúdo final integrando análises de múltiplos agentes
        """
        if self.send_update:
            self.send_update("[ORCHESTRATOR] Iniciando síntese colaborativa", 'log')
        
        # Construir contexto enriquecido com insights colaborativos
        enriched_context = context
        collaborative_insights = ""
        
        if analysis_results['collaborative']:
            collaborative_insights = "\n\n=== INSIGHTS COLABORATIVOS ===\n"
            for agent_type, result in analysis_results['collaborative'].items():
                if result and result['outline']:
                    collaborative_insights += f"\n--- Perspectiva {agent_type.upper()} ---\n{result['outline']}\n"
        
        enriched_context += collaborative_insights
        
        # Gerar conteúdo final usando o agente principal com contexto enriquecido
        if analysis_results['primary']:
            try:
                final_content = agent_writer(
                    analysis_results['primary']['outline'],
                    enriched_context,
                    analysis_results['primary']['writer_prompt'],
                    goal,
                    analysis_results['primary']['goal_type'],
                    self.send_update
                )
                
                if self.send_update:
                    self.send_update("[ORCHESTRATOR] Síntese colaborativa concluída", 'log')
                
                return final_content
            except Exception as e:
                if self.send_update:
                    self.send_update(f"[ORCHESTRATOR] Erro na síntese: {e}", 'log')
                return generate_fallback_content(goal, enriched_context, analysis_results['primary']['outline'], analysis_results['primary']['goal_type'], self.send_update)
        
        return generate_fallback_content(goal, context, "Estrutura não disponível", 'general', self.send_update)

class QualityAssurance:
    """
    Sistema de garantia de qualidade para validação de outputs
    """
    
    def __init__(self, send_update=None):
        self.send_update = send_update
        self.quality_metrics = {
            'completeness': 0.0,
            'accuracy': 0.0,
            'relevance': 0.0,
            'actionability': 0.0
        }
    
    def evaluate_content_quality(self, content: str, goal: str, goal_type: str) -> dict:
        """
        Avalia a qualidade do conteúdo gerado baseado em critérios específicos
        """
        if self.send_update:
            self.send_update("[QA] Iniciando avaliação de qualidade", 'log')
        
        # Critérios básicos de qualidade
        quality_score = {
            'completeness': self._evaluate_completeness(content, goal_type),
            'accuracy': self._evaluate_accuracy(content, goal),
            'relevance': self._evaluate_relevance(content, goal),
            'actionability': self._evaluate_actionability(content, goal_type)
        }
        
        overall_score = sum(quality_score.values()) / len(quality_score)
        
        if self.send_update:
            self.send_update(f"[QA] Score de qualidade: {overall_score:.2f}/1.0", 'log')
        
        return {
            'overall_score': overall_score,
            'detailed_scores': quality_score,
            'recommendations': self._generate_recommendations(quality_score)
        }
    
    def _evaluate_completeness(self, content: str, goal_type: str) -> float:
        """Avalia se o conteúdo está completo baseado no tipo de objetivo"""
        required_sections = {
            'strategic_planning': ['análise', 'objetivos', 'estratégias', 'implementação'],
            'sales_analysis': ['métricas', 'tendências', 'recomendações'],
            'product_management': ['roadmap', 'features', 'personas'],
            'user_management': ['jornada', 'experiência', 'melhorias'],
            'task_management': ['backlog', 'sprint', 'cronograma']
        }
        
        sections = required_sections.get(goal_type, ['introdução', 'desenvolvimento', 'conclusão'])
        content_lower = content.lower()
        
        found_sections = sum(1 for section in sections if section in content_lower)
        return found_sections / len(sections)
    
    def _evaluate_accuracy(self, content: str, goal: str) -> float:
        """Avalia a precisão do conteúdo em relação ao objetivo"""
        goal_keywords = goal.lower().split()
        content_lower = content.lower()
        
        keyword_matches = sum(1 for keyword in goal_keywords if keyword in content_lower)
        return min(keyword_matches / len(goal_keywords), 1.0)
    
    def _evaluate_relevance(self, content: str, goal: str) -> float:
        """Avalia a relevância do conteúdo"""
        # Critério simples: presença de palavras-chave do objetivo
        return min(len(content) / 1000, 1.0)  # Assume que conteúdo mais longo é mais relevante
    
    def _evaluate_actionability(self, content: str, goal_type: str) -> float:
        """Avalia se o conteúdo contém elementos acionáveis"""
        actionable_keywords = ['recomendação', 'ação', 'implementar', 'executar', 'plano', 'estratégia', 'próximos passos']
        content_lower = content.lower()
        
        found_keywords = sum(1 for keyword in actionable_keywords if keyword in content_lower)
        return min(found_keywords / 3, 1.0)  # Normaliza para máximo de 1.0
    
    def _generate_recommendations(self, quality_scores: dict) -> list:
        """Gera recomendações baseadas nos scores de qualidade"""
        recommendations = []
        
        if quality_scores['completeness'] < 0.7:
            recommendations.append("Adicionar seções faltantes para maior completude")
        
        if quality_scores['accuracy'] < 0.6:
            recommendations.append("Revisar alinhamento com o objetivo principal")
        
        if quality_scores['relevance'] < 0.5:
            recommendations.append("Expandir conteúdo com mais detalhes relevantes")
        
        if quality_scores['actionability'] < 0.6:
            recommendations.append("Incluir mais recomendações práticas e acionáveis")
        
        return recommendations

# --- Lógica do Sistema de Agentes ---
def run_generative_model(prompt, max_retries=3, send_update=None):
    import time
    import random
    
    if not GEMINI_API_KEY:
        raise ConnectionError("Chave da API Gemini não encontrada. Configure a variável de ambiente GEMINI_API_KEY.")
    
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
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192
        }
    }
    
    last_error = None
    
    # Tenta cada modelo na ordem de prioridade
    for model in GEMINI_MODELS:
        for retry in range(max_retries):
            try:
                if retry > 0:
                    # Backoff exponencial com jitter
                    wait_time = (2 ** retry) + random.uniform(0, 1)
                    if send_update:
                        send_update(f"[DEBUG] Tentativa {retry + 1}/{max_retries} para {model} após {wait_time:.1f}s", 'log')
                    time.sleep(wait_time)
                else:
                    if send_update:
                        send_update(f"[DEBUG] Tentando modelo: {model}", 'log')
                
                url = f"{GEMINI_BASE_URL}/{model}:generateContent"
                
                response = requests.post(url, headers=headers, json=data, timeout=120) # Aumentado timeout para 120 segundos
                if send_update:
                    send_update(f"[DEBUG] Status Code: {response.status_code}", 'log')
                
                # Se o modelo funcionou, retorna o resultado
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        if send_update:
                            send_update(f"[SUCCESS] Modelo {model} funcionou!", 'log')
                        return result['candidates'][0]['content']['parts'][0]['text']
                    else:
                        if send_update:
                            send_update(f"[ERROR] Resposta sem candidates: {json.dumps(result, indent=2)}", 'log')
                        last_error = f"Modelo {model}: Resposta sem candidates"
                        break   # Não retry para este tipo de erro
                
                # Erros temporários que merecem retry
                elif response.status_code in [429, 500, 502, 503, 504]:
                    try:
                        error_detail = response.json()
                        error_msg = error_detail.get('error', {}).get('message', 'Erro temporário')
                        if send_update:
                            send_update(f"[WARNING] Erro temporário {response.status_code} em {model}: {error_msg}", 'log')
                        last_error = f"Modelo {model}: HTTP {response.status_code} - {error_msg}"
                    except json.JSONDecodeError:
                        if send_update:
                            send_update(f"[WARNING] Erro temporário {response.status_code} em {model}", 'log')
                        last_error = f"Modelo {model}: HTTP {response.status_code}"
                    
                    if retry < max_retries - 1:
                        continue  # Retry
                    else:
                        break   # Próximo modelo
                
                # Erros permanentes que não merecem retry
                elif response.status_code in [400, 401, 403]:
                    try:
                        error_detail = response.json()
                        error_msg = error_detail.get('error', {}).get('message', 'Erro permanente')
                        if send_update:
                            send_update(f"[ERROR] Erro permanente {response.status_code} em {model}: {error_msg}", 'log')
                        last_error = f"Modelo {model}: HTTP {response.status_code} - {error_msg}"
                    except json.JSONDecodeError:
                        if send_update:
                            send_update(f"[ERROR] Erro permanente {response.status_code} em {model}", 'log')
                        last_error = f"Modelo {model}: HTTP {response.status_code}"
                    break   # Próximo modelo
                else:
                    response.raise_for_status() # Levanta uma exceção para outros códigos de status
                    
            except requests.exceptions.Timeout as e:
                if send_update:
                    send_update(f"[WARNING] Timeout em {model} (tentativa {retry + 1}/{max_retries}): {e}", 'log')
                last_error = f"Modelo {model}: Timeout - {e}"
                if retry < max_retries - 1:
                    continue  # Retry
                else:
                    break   # Próximo modelo
            except requests.exceptions.ConnectionError as e:
                if send_update:
                    send_update(f"[WARNING] Erro de conexão em {model} (tentativa {retry + 1}/{max_retries}): {e}", 'log')
                last_error = f"Modelo {model}: Conexão - {e}"
                if retry < max_retries - 1:
                    continue  # Retry
                else:
                    break   # Próximo modelo
            except requests.exceptions.RequestException as e:
                if send_update:
                    send_update(f"[ERROR] Erro de requisição em {model}: {e}", 'log')
                last_error = f"Modelo {model}: Requisição - {e}"
                break   # Próximo modelo
            except (KeyError, IndexError) as e:
                if send_update:
                    send_update(f"[ERROR] Erro ao processar resposta do modelo {model}: {e}", 'log')
                last_error = f"Modelo {model}: Processamento - {e}"
                break   # Próximo modelo
    
    # Se chegou aqui, nenhum modelo funcionou
    if send_update:
        send_update(f"[CRITICAL] Todos os modelos Gemini falharam após {max_retries} tentativas cada", 'log')
    raise ConnectionError(f"Todos os modelos Gemini falharam. Último erro: {last_error}")

def generate_fallback_outline(goal: str, context: str, goal_type: str, send_update=None):
    """Gera um outline de fallback quando a API falha"""
    if send_update:
        send_update("[FALLBACK] Gerando estrutura de fallback...", 'log')
    
    fallback_templates = {
        'strategic_planning': """
# ANÁLISE DE PLANEJAMENTO ESTRATÉGICO

## 1. RESUMO EXECUTIVO
- Visão geral do planejamento estratégico
- Principais objetivos identificados
- Metodologia de análise aplicada

## 2. ANÁLISE DA SITUAÇÃO ATUAL
- Contexto organizacional
- Recursos disponíveis
- Posicionamento no mercado

## 3. ANÁLISE SWOT
### 3.1 Forças (Strengths)
### 3.2 Fraquezas (Weaknesses)
### 3.3 Oportunidades (Opportunities)
### 3.4 Ameaças (Threats)

## 4. OBJETIVOS ESTRATÉGICOS
- Objetivos de curto prazo
- Objetivos de médio prazo
- Objetivos de longo prazo

## 5. ESTRATÉGIAS E AÇÕES
- Planos de ação propostos
- Recursos necessários
- Cronograma de implementação

## 6. INDICADORES E MÉTRICAS
- KPIs principais
- Métodos de acompanhamento
- Critérios de sucesso

## 7. CONSIDERAÇÕES FINAIS
- Recomendações
- Próximos passos
- Conclusões
""",
        'competitive_analysis': """
# ANÁLISE DE CONCORRÊNCIA

## 1. RESUMO EXECUTIVO
- Objetivo da análise
- Metodologia aplicada
- Principais descobertas

## 2. VISÃO GERAL DO MERCADO
- Tamanho e características do mercado
- Tendências identificadas
- Segmentação

## 3. MAPEAMENTO DE CONCORRENTES
### 3.1 Concorrentes Diretos
### 3.2 Concorrentes Indiretos
### 3.3 Novos Entrantes

## 4. ANÁLISE COMPARATIVA
- Produtos e serviços
- Estratégias de preços
- Canais de distribuição
- Estratégias de marketing

## 5. POSICIONAMENTO COMPETITIVO
- Matriz de posicionamento
- Vantagens competitivas
- Gaps de mercado

## 6. OPORTUNIDADES E AMEAÇAS
- Oportunidades identificadas
- Ameaças competitivas
- Recomendações estratégicas

## 7. CONCLUSÕES
- Síntese da análise
- Próximos passos
- Recomendações finais
""",
        'default': f"""
# ANÁLISE: {goal.upper()}

## 1. INTRODUÇÃO
- Objetivo da análise
- Metodologia aplicada
- Escopo do trabalho

## 2. CONTEXTO E FUNDAMENTAÇÃO
- Base teórica
- Dados e informações relevantes
- Premissas adotadas

## 3. DESENVOLVIMENTO
- Análise detalhada
- Interpretação dos dados
- Discussão dos resultados

## 4. RESULTADOS E DESCOBERTAS
- Principais achados
- Insights relevantes
- Implicações práticas

## 5. RECOMENDAÇÕES
- Ações sugeridas
- Próximos passos
- Considerações importantes

## 6. CONCLUSÃO
- Síntese dos resultados
- Limitações do estudo
- Considerações finais
"""
    }
    
    template = fallback_templates.get(goal_type, fallback_templates['default'])
    return template

def agent_researcher(goal: str, context: str, custom_prompt: str, goal_type: str = 'general', send_update=None):
    try:
        # Escapar caracteres especiais no contexto para evitar erros de formatação
        # Isso é crucial para que strings que contenham '{' ou '}' não quebrem o .format()
        safe_context = context.replace('{', '{{').replace('}', '}}')
        safe_goal = goal.replace('{', '{{').replace('}', '}}')
        prompt = custom_prompt.format(goal=safe_goal, context=safe_context, abnt_rules=get_abnt_formatting_rules())
        if send_update:
            send_update(f"[DEBUG] Prompt do pesquisador gerado com sucesso (tamanho: {len(prompt)} caracteres)", 'log')
        return run_generative_model(prompt, send_update=send_update)
    except ConnectionError as e:
        if send_update:
            send_update(f"[WARNING] API indisponível, usando fallback para pesquisador: {e}", 'log')
        return generate_fallback_outline(goal, context, goal_type, send_update=send_update)
    except Exception as e:
        if send_update:
            send_update(f"[ERROR] Erro na formatação do prompt do pesquisador: {e}", 'log')
            send_update(f"[DEBUG] Contexto problemático (primeiros 200 chars): {repr(context[:200])}...", 'log')
            send_update("[FALLBACK] Gerando estrutura de emergência para pesquisador...", 'log')
        return generate_fallback_outline(goal, context, goal_type, send_update=send_update)

def generate_fallback_content(goal: str, context: str, outline: str, goal_type: str, send_update=None):
    """Gera conteúdo de fallback quando a API falha"""
    if send_update:
        send_update("[FALLBACK] Gerando conteúdo de fallback...", 'log')
    
    # Extrair informações do contexto se disponível
    context_summary = "Dados não disponíveis devido à indisponibilidade da API ou erro no processamento."
    if context and len(context) > 50:
        context_summary = f"Baseado nos dados fornecidos: {context[:500]}..." # Aumentado para 500 caracteres
    
    fallback_content = f"""
# RELATÓRIO GERADO EM MODO DE EMERGÊNCIA

> **Nota Importante**: Este relatório foi gerado em modo de fallback devido à indisponibilidade temporária da API de IA ou a um erro no processamento. O conteúdo apresenta uma estrutura padrão que deve ser complementada com análises específicas.

## OBJETIVO DA ANÁLISE
{goal}

## METODOLOGIA
Este relatório segue as normas ABNT para documentos técnicos e apresenta uma estrutura organizada para análise do objetivo proposto.

## CONTEXTO
{context_summary}

## ESTRUTURA PROPOSTA
{outline}

## RECOMENDAÇÕES PARA COMPLEMENTAÇÃO

### 1. Análise Detalhada
- Realizar análise aprofundada dos dados disponíveis
- Aplicar metodologias específicas para o tipo de objetivo
- Considerar fatores externos relevantes

### 2. Validação de Informações
- Verificar a precisão dos dados utilizados
- Consultar fontes adicionais quando necessário
- Aplicar critérios de qualidade na análise

### 3. Desenvolvimento de Insights
- Identificar padrões e tendências relevantes
- Desenvolver conclusões baseadas em evidências
- Propor ações práticas e viáveis

## CONSIDERAÇÕES FINAIS

Este documento serve como base estrutural para o desenvolvimento de uma análise completa. Recomenda-se:

1. **Revisão e Complementação**: Adicionar análises específicas baseadas nos dados disponíveis
2. **Validação Técnica**: Verificar a adequação das metodologias propostas
3. **Atualização Contínua**: Incorporar novas informações conforme disponibilidade

---

**Documento gerado automaticamente pelo Sistema Mangaba.AI** **Data**: {datetime.now().strftime('%d/%m/%Y às %H:%M')}   
**Status**: Modo de Emergência - Requer Complementação Manual
"""
    
    return fallback_content

def agent_writer(outline: str, context: str, custom_prompt: str, goal: str = "", goal_type: str = 'general', send_update=None):
    try:
        # Escapar caracteres especiais no contexto e outline para evitar erros de formatação
        # Isso é crucial para que strings que contenham '{' ou '}' não quebrem o .format()
        safe_context = context.replace('{', '{{').replace('}', '}}')
        safe_outline = outline.replace('{', '{{').replace('}', '}}')
        abnt_rules = get_abnt_formatting_rules()
        prompt = custom_prompt.format(outline=safe_outline, context=safe_context, abnt_rules=abnt_rules)
        if send_update:
            send_update(f"[DEBUG] Prompt do escritor gerado com sucesso (tamanho: {len(prompt)} caracteres)", 'log')
        return run_generative_model(prompt, send_update=send_update)
    except ConnectionError as e:
        if send_update:
            send_update(f"[WARNING] API indisponível, usando fallback para escritor: {e}", 'log')
        return generate_fallback_content(goal, context, outline, goal_type, send_update=send_update)
    except Exception as e:
        if send_update:
            send_update(f"[ERROR] Erro na formatação do prompt do escritor: {e}", 'log')
            send_update(f"[DEBUG] Outline problemático (primeiros 200 chars): {repr(outline[:200])}...", 'log')
            send_update(f"[DEBUG] Contexto problemático (primeiros 200 chars): {repr(context[:200])}...", 'log')
            send_update("[FALLBACK] Gerando conteúdo de emergência para escritor...", 'log')
        return generate_fallback_content(goal, context, outline, goal_type, send_update=send_update)

# --- Orquestrador (MCP) Aprimorado ---
def master_control_plane_enhanced(goal: str, context: str, goal_type: str = 'general', send_update=None, use_collaboration=True, use_qa=True):
    """
    Orquestrador principal aprimorado com colaboração multi-agente e QA
    """
    if send_update:
        send_update("[MCP-ENHANCED] Iniciando sistema multi-agente avançado", 'log')
    
    # Detectar tipo de objetivo principal e tipos relacionados
    primary_goal_type = enhanced_detect_goal_type(goal, context)
    detected_types = detect_multiple_goal_types(goal, context)
    collaborative_agents = get_collaborative_agents(primary_goal_type, detected_types)
    
    if send_update:
        send_update(f"[MCP-ENHANCED] Objetivo principal: {primary_goal_type}", 'log')
        send_update(f"[MCP-ENHANCED] Tipos detectados: {detected_types}", 'log')
        send_update(f"[MCP-ENHANCED] Agentes colaborativos: {collaborative_agents}", 'log')
    
    goal_type = primary_goal_type
    final_content = ""
    
    # Expandir condições para ativação do modo colaborativo
    collaborative_goal_types = [
        'sales_analysis', 'product_management', 'user_management', 'task_management', 
        'strategic_planning', 'competitive_analysis', 'financial_analysis', 
        'hr_management', 'marketing_analysis', 'operations_management', 'technology_analysis'
    ]
    
    if use_collaboration and (goal_type in collaborative_goal_types or collaborative_agents):
        # Usar orquestrador colaborativo
        orchestrator = MangabaAgentOrchestrator(send_update)
        
        try:
            # Análise colaborativa com agentes específicos
            analysis_results = orchestrator.run_parallel_analysis_enhanced(
                goal, context, goal_type, collaborative_agents
            )
            
            # Síntese colaborativa
            final_content = orchestrator.synthesize_collaborative_content(goal, context, analysis_results)
            
            if send_update:
                send_update("[MCP-ENHANCED] Análise colaborativa concluída", 'log')
        
        except Exception as e:
            if send_update:
                send_update(f"[MCP-ENHANCED] Erro na colaboração, usando modo tradicional: {e}", 'log')
            # Fallback para modo tradicional
            return master_control_plane_traditional(goal, context, goal_type, send_update)
    
    else:
        # Usar modo tradicional para tipos não colaborativos
        return master_control_plane_traditional(goal, context, goal_type, send_update)
    
    # Sistema de QA
    if use_qa and final_content:
        try:
            qa_system = QualityAssurance(send_update)
            quality_report = qa_system.evaluate_content_quality(final_content, goal, goal_type)
            
            if send_update:
                send_update(f"[QA] Avaliação concluída - Score: {quality_report['overall_score']:.2f}", 'log')
                
                if quality_report['recommendations']:
                    send_update(f"[QA] Recomendações: {'; '.join(quality_report['recommendations'])}", 'log')
            
            # Adicionar relatório de qualidade ao final do conteúdo
            qa_summary = f"\n\n--- RELATÓRIO DE QUALIDADE ---\nScore Geral: {quality_report['overall_score']:.2f}/1.0\n"
            qa_summary += f"Completude: {quality_report['detailed_scores']['completeness']:.2f}\n"
            qa_summary += f"Precisão: {quality_report['detailed_scores']['accuracy']:.2f}\n"
            qa_summary += f"Relevância: {quality_report['detailed_scores']['relevance']:.2f}\n"
            qa_summary += f"Acionabilidade: {quality_report['detailed_scores']['actionability']:.2f}\n"
            
            if quality_report['recommendations']:
                qa_summary += f"\nRecomendações de Melhoria:\n"
                for i, rec in enumerate(quality_report['recommendations'], 1):
                    qa_summary += f"{i}. {rec}\n"
            
            final_content += qa_summary
        
        except Exception as e:
            if send_update:
                send_update(f"[QA] Erro na avaliação de qualidade: {e}", 'log')
    
    if send_update:
        send_update("[MCP-ENHANCED] Processo completo finalizado", 'log')
    
    return {"result": final_content}

def master_control_plane_traditional(goal: str, context: str, goal_type: str = 'general', send_update=None):
    """
    Orquestrador tradicional (modo de compatibilidade)
    """
    if send_update:
        send_update("[MCP-TRADITIONAL] Usando modo tradicional", 'log')
    
    try:
        researcher_prompt, writer_prompt = generate_specialized_prompts(goal_type, goal, context)
        
        # Agente Pesquisador
        outline = agent_researcher(goal, context, researcher_prompt, goal_type, send_update)
        if send_update:
            send_update(outline, 'partial_result')
        
        # Agente Escritor
        final_content = agent_writer(outline, context, writer_prompt, goal, goal_type, send_update)
        
        return {"result": final_content}
    
    except Exception as e:
        if send_update:
            send_update(f"[MCP-TRADITIONAL] Erro: {e}", 'log')
        
        fallback_content = generate_fallback_content(goal, context, "Estrutura indisponível", goal_type, send_update)
        return {"result": fallback_content}

# --- Orquestrador (MCP) Original (mantido para compatibilidade) ---
def master_control_plane(goal: str, context: str, researcher_prompt: str, writer_prompt: str, goal_type: str = 'general', send_update=None):
    
    log_1 = "[MCP] Objetivo recebido. Acionando Agente Pesquisador..."
    if send_update:
        send_update(log_1, 'log')
    
    # O Agente Pesquisador gera a estrutura (outline)
    try:
        outline = agent_researcher(goal, context, researcher_prompt, goal_type, send_update=send_update)
        log_2 = "[Agente Pesquisador] Estrutura criada."
        if send_update:
            send_update(log_2, 'log')
            send_update(outline, 'partial_result') # Envia o outline como resultado parcial
            send_update("[MCP] Acionando Agente Escritor...", 'log')
    except Exception as e:
        log_2 = f"[Agente Pesquisador] Erro: {e}"
        if send_update:
            send_update(log_2, 'log')
            send_update("[MCP] Tentando continuar com estrutura de fallback...", 'log')
        outline = generate_fallback_outline(goal, context, goal_type, send_update=send_update) # Garante que outline tem um valor
        if send_update:
            send_update(outline, 'partial_result') # Envia o outline de fallback como resultado parcial
            send_update("[MCP] Acionando Agente Escritor...", 'log')


    # O Agente Escritor gera o conteúdo final baseado na estrutura e no contexto
    try:
        final_content = agent_writer(outline, context, writer_prompt, goal, goal_type, send_update=send_update)
        log_3 = "[Agente Escritor] Conteúdo final gerado."
        if send_update:
            send_update(log_3, 'log')
            send_update("[MCP] Processo concluído.", 'log')
    except Exception as e:
        log_3 = f"[Agente Escritor] Erro: {e}"
        if send_update:
            send_update(log_3, 'log')
            send_update("[MCP] Gerando conteúdo de fallback...", 'log')
        final_content = generate_fallback_content(goal, context, outline, goal_type, send_update=send_update) # Garante que final_content tem um valor

    return {"result": final_content}

# --- Rotas da Aplicação ---
@app.route('/')
def index():
    """Página inicial da aplicação"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Erro ao carregar página inicial: {e}", 500

@app.route('/app')
def application():
    """Página principal da aplicação com formulário"""
    try:
        return render_template('app.html')
    except Exception as e:
        return f"Erro ao carregar aplicação: {e}", 500

@app.route('/business_model')
@app.route('/business-model')
@app.route('/modelo-negocio')
def business_model():
    """Página do modelo de negócio com múltiplas rotas"""
    try:
        return render_template('business_model.html')
    except Exception as e:
        return f"Erro ao carregar modelo de negócio: {e}", 500

@app.route('/business_model.html')
def business_model_redirect():
    """Redireciona a rota legada para a nova"""
    return redirect(url_for('business_model'))

@app.route('/health')
def health_check():
    """Verificação de saúde da aplicação"""
    return jsonify({"status": "ok", "message": "Servidor funcionando"})

@app.route('/data/<filename>')
def get_data_file(filename):
    try:
        return send_from_directory(data_dir, filename)
    except FileNotFoundError:
        return jsonify({"error": "Arquivo não encontrado"}), 404

@app.route('/api/run_agent_system', methods=['POST'])
def run_agent_system():
    def generate():
        if 'goal' not in request.form or not request.form['goal']:
            yield format_sse_event({'error': 'O objetivo (goal) é obrigatório.'}, 'error')
            return

        try:
            goal = request.form['goal']
            yield format_sse_event(f"[INFO] Objetivo recebido: {goal[:100]}...", 'log')

            context = "Nenhum contexto fornecido." # Valor padrão

            # Processar dados de contexto
            try:
                if 'dataSource' in request.files:
                    file = request.files['dataSource']
                    if file.filename != '':
                        yield format_sse_event(f"[INFO] Processando arquivo: {file.filename}", 'log')
                        file_content = file.read().decode('utf-8')
                        yield format_sse_event(f"[DEBUG] Tamanho do arquivo: {len(file_content)} caracteres", 'log')
                        
                        # Verificar se é um arquivo JSON
                        if file.filename.endswith('.json'):
                            try:
                                # Validar e formatar o JSON
                                json_data = json.loads(file_content)
                                context = f"Dados JSON fornecidos:\n{json.dumps(json_data, indent=2, ensure_ascii=False)}"
                                yield format_sse_event("[SUCCESS] JSON válido processado do arquivo", 'log')
                            except json.JSONDecodeError as json_err:
                                yield format_sse_event(f"[ERROR] JSON inválido no arquivo: {json_err}", 'log')
                                context = f"Arquivo JSON inválido. Conteúdo bruto:\n{file_content}"
                        else:
                            context = file_content
                            yield format_sse_event("[INFO] Arquivo de texto processado", 'log')
                elif 'json_data' in request.form and request.form['json_data']:
                    # Processar JSON direto do formulário (textarea)
                    json_input = request.form['json_data']
                    yield format_sse_event("[INFO] Processando JSON do formulário", 'log')
                    try:
                        json_data = json.loads(json_input)
                        context = f"Dados JSON fornecidos:\n{json.dumps(json_data, indent=2, ensure_ascii=False)}"
                        yield format_sse_event("[SUCCESS] JSON do formulário válido", 'log')
                    except json.JSONDecodeError as json_err:
                        yield format_sse_event(f"[ERROR] JSON do formulário inválido: {json_err}", 'log')
                        yield format_sse_event({'error': f'JSON inválido: {json_err}'}, 'error')
                        return
                elif 'text_context' in request.form and request.form['text_context']:
                    # Processar texto simples do formulário (textarea)
                    context = request.form['text_context']
                    yield format_sse_event("[INFO] Texto simples do formulário processado", 'log')

            except Exception as context_err:
                yield format_sse_event(f"[ERROR] Erro ao processar contexto: {context_err}", 'log')
                context = "Erro ao processar dados de contexto." # Define um contexto de erro para o LLM

            if not GEMINI_API_KEY:
                yield format_sse_event("[ERROR] API Key do Gemini não configurada", 'log')
                yield format_sse_event({'error': 'A API do Gemini não está configurada. Verifique sua chave de API no arquivo .env.'}, 'error')
                return

            # Sistema de parametrização automática aprimorado com detecção múltipla
            try:
                # Detectar tipo principal e tipos relacionados
                goal_type = enhanced_detect_goal_type(goal, context)
                all_detected_types = detect_multiple_goal_types(goal, context)
                
                yield format_sse_event(f"[INFO] Tipo principal detectado: {goal_type}", 'log')
                yield format_sse_event(f"[INFO] Tipos relacionados detectados: {', '.join(all_detected_types)}", 'log')
                
                # Determinar agentes colaborativos
                collaborative_agents = get_collaborative_agents(goal_type, all_detected_types)
                
                # Verificar se deve usar modo colaborativo (expandido para incluir novos tipos)
                collaboration_types = [
                    'sales_analysis', 'product_management', 'user_management', 'task_management', 
                    'strategic_planning', 'competitive_analysis', 'financial_analysis', 
                    'hr_management', 'marketing_analysis', 'operations_management', 'technology_analysis'
                ]
                
                use_collaboration = goal_type in collaboration_types or len(all_detected_types) > 1
                
                if use_collaboration:
                    yield format_sse_event(f"[INFO] Modo colaborativo ativado - Agentes: {', '.join(collaborative_agents)}", 'log')
                else:
                    yield format_sse_event(f"[INFO] Modo tradicional para {goal_type}", 'log')
                
            except Exception as prompt_err:
                yield format_sse_event(f"[ERROR] Erro na detecção de objetivo: {prompt_err}", 'log')
                goal_type = 'general'
                all_detected_types = ['general']
                collaborative_agents = []
                use_collaboration = False

            # Função para enviar atualizações via SSE
            def send_update(data, event_type='message'):
                yield format_sse_event(data, event_type)
                time.sleep(0.05) # Pequeno delay para garantir que o navegador processe os eventos

            # Executar sistema de agentes aprimorado
            try:
                yield format_sse_event("[INFO] Iniciando sistema multi-agente Mangaba.AI", 'log')
                
                # Usar o novo orquestrador aprimorado
                result_data = master_control_plane_enhanced(
                    goal=goal, 
                    context=context, 
                    goal_type=goal_type, 
                    send_update=send_update,
                    use_collaboration=use_collaboration,
                    use_qa=True
                )
                
                yield format_sse_event(result_data['result'], 'final_result')
                yield format_sse_event("[SUCCESS] Sistema multi-agente concluído com sucesso", 'log')
                
            except Exception as agent_err:
                yield format_sse_event(f"[ERROR] Erro no sistema multi-agente: {agent_err}", 'log')
                
                # Fallback para sistema tradicional
                try:
                    yield format_sse_event("[FALLBACK] Tentando sistema tradicional...", 'log')
                    researcher_prompt, writer_prompt = generate_specialized_prompts(goal_type, goal, context)
                    result_data = master_control_plane(goal, context, researcher_prompt, writer_prompt, goal_type, send_update=send_update)
                    yield format_sse_event(result_data['result'], 'final_result')
                    yield format_sse_event("[SUCCESS] Sistema tradicional concluído", 'log')
                except Exception as fallback_err:
                    yield format_sse_event(f"[ERROR] Erro no fallback: {fallback_err}", 'log')
                    import traceback
                    traceback.print_exc() # Imprime o traceback completo para depuração
                    yield format_sse_event({'error': f'Ocorreu um erro no sistema de agentes: {agent_err}'}, 'error')

        except ConnectionError as e:
            yield format_sse_event(f"[ERROR] Erro de conexão: {e}", 'log')
            yield format_sse_event({'error': str(e)}, 'error')
        except Exception as e:
            yield format_sse_event(f"[ERROR] Erro inesperado: {e}", 'log')
            import traceback
            traceback.print_exc()
            yield format_sse_event({'error': f'Ocorreu um erro inesperado no servidor: {e}'}, 'error')
        finally:
            yield format_sse_event('END_STREAM', 'end') # Sinaliza o fim do stream

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

def format_sse_event(data, event_type='message'):
    """Formata os dados para o padrão Server-Sent Events."""
    json_data = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {json_data}\n\n"

if __name__ == '__main__':
    # Em ambiente de produção, defina debug=False
    app.run(debug=True)
