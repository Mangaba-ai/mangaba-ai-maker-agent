<div align="center">
  <img src="assets/mangaba-logo.svg" alt="Mangaba AI" width="140"/>

  [![Mangaba AI](https://img.shields.io/badge/Mangaba-AI-F97518?style=for-the-badge)](https://www.mangaba.ia.br)
  [![Site](https://img.shields.io/badge/mangaba.ia.br-1E0D01?style=for-the-badge)](https://www.mangaba.ia.br)
</div>

# Mangaba.AI Multi-Agent System

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**Sistema multi-agente de IA para automatização de tarefas complexas e geração de conteúdo estratégico.**

## 📁 Estrutura do Repositório

```
mangaba-ai-maker-agent/
├── mangaba-ai-maker-agent/     # Código principal da aplicação
│   ├── src/                    # Código fonte
│   ├── data/                   # Dados e arquivos de contexto
│   ├── static/                 # Arquivos estáticos (CSS, JS, imagens)
│   ├── templates/              # Templates HTML (incluindo exemplos_objetivos_ui.html)
│   ├── tests/                  # Testes unitários e de integração
│   ├── docs/                   # Documentação técnica e melhorias
│   ├── main.py                 # Ponto de entrada da aplicação
│   ├── requirements.txt        # Dependências básicas
│   ├── requirements_melhorias.txt  # Dependências completas
│   └── README.md               # Documentação principal
└── README.md                   # Este arquivo
```

## 🚀 Início Rápido

1. **Clone o repositório:**
   ```bash
   git clone <repository-url>
   cd mangaba-ai-maker-agent
   ```

2. **Navegue para o diretório principal:**
   ```bash
   cd mangaba-ai-maker-agent
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com sua chave da API Gemini
   ```

5. **Execute a aplicação:**
   ```bash
   python main.py
   ```

6. **Acesse:** http://127.0.0.1:5000

## 📚 Documentação

- **Documentação Principal:** [mangaba-ai-maker-agent/README.md](mangaba-ai-maker-agent/README.md)
- **Melhorias Implementadas:** [mangaba-ai-maker-agent/docs/README_MELHORIAS.md](mangaba-ai-maker-agent/docs/README_MELHORIAS.md)
- **Melhorias Propostas:** [mangaba-ai-maker-agent/docs/10_MELHORIAS_PROPOSTAS.md](mangaba-ai-maker-agent/docs/10_MELHORIAS_PROPOSTAS.md)
- **Integração de Exemplos:** [mangaba-ai-maker-agent/docs/INTEGRACAO_EXEMPLOS_OBJETIVOS.md](mangaba-ai-maker-agent/docs/INTEGRACAO_EXEMPLOS_OBJETIVOS.md)
- **Melhorias Estratégicas:** [mangaba-ai-maker-agent/docs/STRATEGIC_IMPROVEMENTS.md](mangaba-ai-maker-agent/docs/STRATEGIC_IMPROVEMENTS.md)

## 🛠️ Desenvolvimento

### Versão Básica
Para desenvolvimento básico, use:
```bash
pip install -r requirements.txt
```

### Versão Completa com Melhorias
Para todas as funcionalidades avançadas:
```bash
pip install -r requirements_melhorias.txt
```

## 🧪 Testes

```bash
# Executar testes
pytest tests/

# Executar testes com cobertura
pytest tests/ --cov=src
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**Desenvolvido com ❤️ pela Mangaba AI**