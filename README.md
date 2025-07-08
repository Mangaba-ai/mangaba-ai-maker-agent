# Mangaba.AI: Multi-Agent AI System

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**Orquestre uma equipe de agentes de IA para automatizar tarefas complexas, gerar conteúdo estratégico e extrair insights poderosos de seus dados.**

O Mangaba.AI é uma plataforma de código aberto que permite transformar um simples objetivo em um resultado completo e profissional, utilizando um sistema colaborativo de agentes de IA especializados.

---

### ✨ Por que escolher o Mangaba.AI?

*   **🧠 Inteligência Colaborativa:** Em vez de um único modelo de IA, o Mangaba.AI utiliza um orquestrador (Master Control Plane) que seleciona e coordena múltiplos agentes (Pesquisador, Analista de Vendas, Gerente de Produto, etc.) para trabalhar em conjunto, garantindo um resultado mais rico e completo.

*   **🎯 Alta Especialização:** O sistema detecta automaticamente o tipo de objetivo (são 13 categorias, de planejamento estratégico a análise de código) e aciona os agentes mais adequados para a tarefa, utilizando prompts especializados para máxima eficácia.

*   **✅ Qualidade Garantida:** Um sistema de Garantia de Qualidade (QA) integrado avalia o conteúdo gerado em tempo real, fornecendo um score de qualidade e recomendações de melhoria, garantindo que o resultado final seja acionável e relevante.

*   **🔌 Flexibilidade Total:** Traga seus próprios dados! A plataforma suporta o upload de arquivos de contexto (`.txt`, `.json`) ou a inserção direta de dados, permitindo que a IA trabalhe com suas informações para gerar resultados personalizados.

*   **🚀 Interface Intuitiva:** Uma interface web moderna e responsiva guia o usuário em um processo simples de 3 passos: definir o objetivo, fornecer o contexto e receber a solução completa, com um console que exibe o raciocínio da IA em tempo real.

### 🎯 Ideal Para

*   **Analistas de Negócios e Estrategistas:** Para criar análises de concorrência, planejamentos estratégicos e OKRs em minutos.
*   **Desenvolvedores e Tech Leaders:** Para gerar documentação técnica, relatórios de análise de código e planos de projeto.
*   **Criadores de Conteúdo e Marketing:** Para produzir artigos, posts de blog e campanhas criativas com base em dados.
*   **Estudantes e Pesquisadores:** Para estruturar trabalhos acadêmicos, artigos científicos e revisões bibliográficas com formatação ABNT.

### 🏷️ Tags

`IA` `Multi-Agente` `Agentes-IA` `LLM` `IA-Generativa` `Python` `Flask` `Gemini` `Automação` `Produtividade` `Conteúdo` `Relatórios` `Análise-de-Concorrência` `Planejamento-Estratégico` `OKR` `Business-Intelligence` `Análise-de-Dados` `SaaS`

### 🛠️ Estrutura do Projeto

O projeto está organizado da seguinte forma:

```
/mangaba-ai-maker-agent
|-- /src
|   |-- __init__.py
|   |-- app.py
|-- /data
|-- /static
|-- /templates
|-- /tests
|-- .env
|-- main.py
|-- requirements.txt
```

### 🚀 Como Executar a Aplicação

1.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure a chave da API**:
    *   Renomeie o arquivo `.env.example` para `.env`.
    *   Insira sua chave da API Gemini no arquivo `.env`:
        ```
        GEMINI_API_KEY=SUA_CHAVE_API
        ```

3.  **Inicie a aplicação**:
    ```bash
    python main.py
    ```

4.  **Acesse a aplicação**:
    *   Abra o navegador e acesse `http://127.0.0.1:5000`.

### 🤝 Como Contribuir

Para contribuir com o projeto, siga estas etapas:

1.  **Crie um fork** do repositório.
2.  **Crie um branch** para sua feature (`git checkout -b feature/nova-feature`).
3.  **Faça commit** de suas alterações (`git commit -m 'Adiciona nova feature'`).
4.  **Faça push** para o branch (`git push origin feature/nova-feature`).
5.  **Abra um Pull Request**.

---

**Desenvolvido com ❤️ pela Mangaba AI**