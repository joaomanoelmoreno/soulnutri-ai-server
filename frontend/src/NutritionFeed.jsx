import React, { useState, useEffect, useCallback } from 'react';
import './NutritionFeed.css';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CATEGORY_CONFIG = {
  curiosidade: { icon: '💡', color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', label: 'Curiosidade' },
  alerta: { icon: '⚠️', color: '#ef4444', bg: 'rgba(239,68,68,0.1)', label: 'Alerta' },
  dica: { icon: '💚', color: '#22c55e', bg: 'rgba(34,197,94,0.1)', label: 'Dica' },
  ciencia: { icon: '🔬', color: '#6366f1', bg: 'rgba(99,102,241,0.1)', label: 'Ciencia' },
  tendencia: { icon: '📈', color: '#06b6d4', bg: 'rgba(6,182,212,0.1)', label: 'Tendencia' },
  mito_vs_fato: { icon: '⚖️', color: '#ec4899', bg: 'rgba(236,72,153,0.1)', label: 'Mito vs Fato' }
};

const TONE_BADGE = {
  otimista: { icon: '☀️', label: 'Otimista', color: '#22c55e' },
  realista: { icon: '📊', label: 'Realista', color: '#f59e0b' }
};

export default function NutritionFeed({ onClose }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState(null);
  const [expandedItem, setExpandedItem] = useState(null);
  const [stats, setStats] = useState(null);
  const [generating, setGenerating] = useState(false);

  const loadFeed = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit: '30' });
      if (activeCategory) params.set('categoria', activeCategory);
      
      const res = await fetch(`${API}/news/feed?${params}`);
      const data = await res.json();
      
      if (data.ok) {
        setItems(data.items || []);
        setStats(data.stats || null);
      }
    } catch (e) {
      console.error('Erro ao carregar feed:', e);
    }
    setLoading(false);
  }, [activeCategory]);

  useEffect(() => {
    loadFeed();
  }, [loadFeed]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await fetch(`${API}/news/generate`, { method: 'POST' });
      const data = await res.json();
      if (data.ok) {
        loadFeed();
      }
    } catch (e) {
      console.error('Erro ao gerar:', e);
    }
    setGenerating(false);
  };

  const handleLike = async (hash) => {
    try {
      await fetch(`${API}/news/like/${hash}`, { method: 'POST' });
      setItems(prev => prev.map(item => 
        item.content_hash === hash ? { ...item, likes: (item.likes || 0) + 1 } : item
      ));
    } catch (e) { /* silent */ }
  };

  const handleView = async (hash) => {
    try {
      await fetch(`${API}/news/view/${hash}`, { method: 'POST' });
    } catch (e) { /* silent */ }
  };

  const toggleExpand = (hash) => {
    if (expandedItem === hash) {
      setExpandedItem(null);
    } else {
      setExpandedItem(hash);
      handleView(hash);
    }
  };

  return (
    <div className="nf-container" data-testid="nutrition-feed">
      {/* Header */}
      <div className="nf-header">
        <button className="nf-back" onClick={onClose} data-testid="feed-back-btn">
          ← Voltar
        </button>
        <div className="nf-title-area">
          <h2 className="nf-title">Nutri News</h2>
          <p className="nf-subtitle">Curiosidades e alertas nutricionais verificados</p>
        </div>
      </div>

      {/* Stats Bar */}
      {stats && stats.total > 0 && (
        <div className="nf-stats-bar">
          <span className="nf-stat-item">{stats.total} artigos</span>
          <span className="nf-stat-divider">|</span>
          <span className="nf-stat-item">☀️ {stats.by_tone?.otimista || 0}</span>
          <span className="nf-stat-item">📊 {stats.by_tone?.realista || 0}</span>
        </div>
      )}

      {/* Category Filters */}
      <div className="nf-categories">
        <button 
          className={`nf-cat-btn ${!activeCategory ? 'active' : ''}`}
          onClick={() => setActiveCategory(null)}
          data-testid="feed-cat-all"
        >
          Todos
        </button>
        {Object.entries(CATEGORY_CONFIG).map(([key, cfg]) => (
          <button
            key={key}
            className={`nf-cat-btn ${activeCategory === key ? 'active' : ''}`}
            onClick={() => setActiveCategory(activeCategory === key ? null : key)}
            style={activeCategory === key ? { borderColor: cfg.color, color: cfg.color } : {}}
            data-testid={`feed-cat-${key}`}
          >
            {cfg.icon} {cfg.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="nf-content">
        {loading ? (
          <div className="nf-loading">
            <div className="nf-spinner"></div>
            <p>Carregando noticias...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="nf-empty">
            <div className="nf-empty-icon">📰</div>
            <h3>Nenhuma noticia ainda</h3>
            <p>Clique em "Gerar Noticias" para criar conteudo verificado com IA</p>
            <button 
              className="nf-generate-btn"
              onClick={handleGenerate}
              disabled={generating}
              data-testid="feed-generate-btn"
            >
              {generating ? 'Gerando...' : '✨ Gerar Noticias'}
            </button>
          </div>
        ) : (
          <>
            {/* Generate button at top when there are items */}
            <button 
              className="nf-generate-floating"
              onClick={handleGenerate}
              disabled={generating}
              data-testid="feed-generate-more-btn"
            >
              {generating ? '⏳ Gerando...' : '✨ Mais noticias'}
            </button>

            {/* News Cards */}
            <div className="nf-cards">
              {items.map((item, idx) => {
                const cat = CATEGORY_CONFIG[item.categoria] || CATEGORY_CONFIG.curiosidade;
                const tone = TONE_BADGE[item.tom] || TONE_BADGE.otimista;
                const isExpanded = expandedItem === item.content_hash;
                
                return (
                  <div 
                    key={item.content_hash || idx}
                    className={`nf-card ${isExpanded ? 'expanded' : ''}`}
                    style={{ '--card-accent': cat.color }}
                    onClick={() => toggleExpand(item.content_hash)}
                    data-testid={`feed-card-${idx}`}
                  >
                    {/* Card Header */}
                    <div className="nf-card-header">
                      <span className="nf-card-cat" style={{ background: cat.bg, color: cat.color }}>
                        {cat.icon} {cat.label}
                      </span>
                      <span className="nf-card-tone" style={{ color: tone.color }}>
                        {tone.icon}
                      </span>
                    </div>

                    {/* Card Title */}
                    <h3 className="nf-card-title">{item.titulo}</h3>

                    {/* Card Summary */}
                    <p className="nf-card-summary">{item.resumo}</p>

                    {/* Expanded Content */}
                    {isExpanded && (
                      <div className="nf-card-expanded">
                        <p className="nf-card-content">{item.conteudo}</p>
                        
                        {/* Source with clickable link */}
                        <div className="nf-card-source">
                          <span className="nf-source-verified">
                            {item.verificado ? '✓ Verificado' : '? Nao verificado'}
                          </span>
                          <div className="nf-source-detail">
                            <span className="nf-source-name">
                              📚 {item.fonte_nome} {item.fonte_ano ? `(${item.fonte_ano})` : ''}
                            </span>
                            {item.fonte_descricao && (
                              <span className="nf-source-desc">{item.fonte_descricao}</span>
                            )}
                            {item.fonte_url && item.fonte_url.startsWith('http') && (
                              <a 
                                href={item.fonte_url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="nf-source-link"
                                onClick={(e) => e.stopPropagation()}
                                data-testid={`feed-link-${idx}`}
                              >
                                🔗 Ver fonte original
                              </a>
                            )}
                          </div>
                        </div>

                        {/* Tags */}
                        {item.tags && item.tags.length > 0 && (
                          <div className="nf-card-tags">
                            {item.tags.map((tag, i) => (
                              <span key={i} className="nf-tag">#{tag}</span>
                            ))}
                          </div>
                        )}

                        {/* Confidence */}
                        <div className="nf-card-confidence">
                          <span className={`nf-confidence-badge ${item.nivel_confianca}`}>
                            {item.nivel_confianca === 'alto' ? '🟢 Alta confianca' : '🟡 Media confianca'}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Card Footer */}
                    <div className="nf-card-footer">
                      <button 
                        className="nf-like-btn"
                        onClick={(e) => { e.stopPropagation(); handleLike(item.content_hash); }}
                        data-testid={`feed-like-${idx}`}
                      >
                        ❤️ {item.likes || 0}
                      </button>
                      <span className="nf-card-expand-hint">
                        {isExpanded ? '▲ menos' : '▼ ler mais'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
