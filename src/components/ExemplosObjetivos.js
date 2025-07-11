import React, { useState, useEffect } from 'react';
import './ExemplosObjetivos.css';

const ExemplosObjetivos = ({ onSelectExample, isVisible = true }) => {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [animationDelay, setAnimationDelay] = useState(0);

  const exemplos = {
    'analise-negocios': {
      title: '📊 Análise de Negócios',
      items: [
        {
          text: 'Analisar o desempenho de vendas do último trimestre e identificar oportunidades de melhoria',
          tag: 'Vendas',
          color: '#e3f2fd'
        },
        {
          text: 'Criar um relatório de análise de mercado para lançamento de novo produto',
          tag: 'Produto',
          color: '#f3e5f5'
        },
        {
          text: 'Desenvolver estratégia de marketing digital para aumentar conversões em 30%',
          tag: 'Marketing',
          color: '#e8f5e8'
        },
        {
          text: 'Avaliar ROI de campanhas publicitárias e otimizar investimentos',
          tag: 'ROI',
          color: '#fff3e0'
        }
      ]
    },
    'academico': {
      title: '🎓 Acadêmico e Pesquisa',
      items: [
        {
          text: 'Escrever um artigo científico sobre inteligência artificial aplicada à educação',
          tag: 'Acadêmico',
          color: '#e3f2fd'
        },
        {
          text: 'Criar uma revisão bibliográfica sobre sustentabilidade empresarial',
          tag: 'Pesquisa',
          color: '#f3e5f5'
        },
        {
          text: 'Desenvolver um projeto de TCC sobre transformação digital',
          tag: 'TCC',
          color: '#e8f5e8'
        },
        {
          text: 'Elaborar dissertação de mestrado sobre inovação tecnológica',
          tag: 'Mestrado',
          color: '#fff3e0'
        }
      ]
    },
    'estrategico': {
      title: '🚀 Planejamento Estratégico',
      items: [
        {
          text: 'Elaborar plano estratégico de 5 anos para expansão da empresa',
          tag: 'Estratégia',
          color: '#e3f2fd'
        },
        {
          text: 'Criar roadmap de implementação de tecnologias emergentes',
          tag: 'Tecnologia',
          color: '#f3e5f5'
        },
        {
          text: 'Desenvolver plano de gestão de riscos para projeto crítico',
          tag: 'Gestão',
          color: '#e8f5e8'
        },
        {
          text: 'Definir OKRs trimestrais para equipe de desenvolvimento',
          tag: 'OKRs',
          color: '#fff3e0'
        }
      ]
    },
    'criativo': {
      title: '💡 Criativo e Inovação',
      items: [
        {
          text: 'Criar campanha publicitária inovadora para produto sustentável',
          tag: 'Criativo',
          color: '#e3f2fd'
        },
        {
          text: 'Desenvolver conceito de aplicativo mobile para delivery de comida saudável',
          tag: 'UX/UI',
          color: '#f3e5f5'
        },
        {
          text: 'Escrever roteiro para vídeo institucional sobre cultura empresarial',
          tag: 'Conteúdo',
          color: '#e8f5e8'
        },
        {
          text: 'Criar identidade visual completa para startup de tecnologia',
          tag: 'Branding',
          color: '#fff3e0'
        }
      ]
    },
    'dados': {
      title: '📈 Análise de Dados',
      items: [
        {
          text: 'Analisar dados de comportamento do usuário para otimizar experiência no site',
          tag: 'UX',
          color: '#e3f2fd'
        },
        {
          text: 'Criar dashboard executivo com KPIs de performance da empresa',
          tag: 'BI',
          color: '#f3e5f5'
        },
        {
          text: 'Desenvolver modelo preditivo para forecast de vendas',
          tag: 'ML',
          color: '#e8f5e8'
        },
        {
          text: 'Implementar sistema de análise de sentimento para feedback de clientes',
          tag: 'NLP',
          color: '#fff3e0'
        }
      ]
    },
    'operacional': {
      title: '⚙️ Operacional e Processos',
      items: [
        {
          text: 'Otimizar processo de onboarding de novos funcionários',
          tag: 'RH',
          color: '#e3f2fd'
        },
        {
          text: 'Implementar metodologia ágil na equipe de desenvolvimento',
          tag: 'Agile',
          color: '#f3e5f5'
        },
        {
          text: 'Criar manual de procedimentos para atendimento ao cliente',
          tag: 'Processos',
          color: '#e8f5e8'
        },
        {
          text: 'Desenvolver sistema de gestão de qualidade ISO 9001',
          tag: 'Qualidade',
          color: '#fff3e0'
        }
      ]
    }
  };

  const handleSelectExample = (exampleText) => {
    if (onSelectExample) {
      onSelectExample(exampleText);
    }
  };

  const toggleCategory = (categoryKey) => {
    setSelectedCategory(selectedCategory === categoryKey ? null : categoryKey);
  };

  useEffect(() => {
    setAnimationDelay(0);
  }, []);

  if (!isVisible) return null;

  return (
    <div className="exemplos-container">
      <div className="exemplos-header">
        <h3 className="exemplos-title">
          💡 Exemplos de Objetivos
        </h3>
        <p className="exemplos-subtitle">
          Clique em qualquer exemplo para usá-lo como base
        </p>
      </div>

      <div className="exemplos-categories">
        {Object.entries(exemplos).map(([categoryKey, category], categoryIndex) => (
          <div key={categoryKey} className="category-section">
            <button 
              className={`category-header ${selectedCategory === categoryKey ? 'active' : ''}`}
              onClick={() => toggleCategory(categoryKey)}
            >
              <span className="category-title">{category.title}</span>
              <span className="category-toggle">
                {selectedCategory === categoryKey ? '−' : '+'}
              </span>
            </button>
            
            <div className={`category-content ${selectedCategory === categoryKey ? 'expanded' : ''}`}>
              {category.items.map((item, itemIndex) => (
                <div 
                  key={itemIndex}
                  className="example-item"
                  onClick={() => handleSelectExample(item.text)}
                  style={{
                    animationDelay: `${(categoryIndex * 4 + itemIndex) * 50}ms`
                  }}
                >
                  <div className="example-text">{item.text}</div>
                  <span 
                    className="example-tag"
                    style={{ backgroundColor: item.color }}
                  >
                    {item.tag}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="exemplos-footer">
        <div className="quick-tips">
          <h4>💡 Dicas Rápidas:</h4>
          <ul>
            <li>Seja específico sobre o que você quer alcançar</li>
            <li>Inclua contexto relevante (setor, público-alvo, prazo)</li>
            <li>Mencione o formato desejado (relatório, apresentação, etc.)</li>
            <li>Defina métricas de sucesso quando aplicável</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ExemplosObjetivos;