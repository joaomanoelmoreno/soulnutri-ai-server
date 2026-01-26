import React, { useState, useEffect } from 'react';
import './Admin.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Admin() {
  const [dishes, setDishes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [editingDish, setEditingDish] = useState(null);
  const [stats, setStats] = useState(null);
  const [filterCategory, setFilterCategory] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // grid ou list
  const [activeTab, setActiveTab] = useState('dishes'); // dishes, novidades, premium, audit
  const [novidades, setNovidades] = useState([]);
  const [editingNovidade, setEditingNovidade] = useState(null);
  // Auditoria
  const [auditData, setAuditData] = useState(null);
  const [auditLoading, setAuditLoading] = useState(false);
  const [fixingSlug, setFixingSlug] = useState(null);
  const [novidadeForm, setNovidadeForm] = useState({
    dish_slug: '',
    tipo: 'info',
    titulo: '',
    mensagem: '',
    emoji: '📢',
    severidade: 'info',
    ativa: true
  });
  // Premium management
  const [premiumUsers, setPremiumUsers] = useState([]);
  const [premiumNome, setPremiumNome] = useState('');
  const [premiumDias, setPremiumDias] = useState(30);

  useEffect(() => {
    loadDishes();
    loadStats();
    loadNovidades();
    loadPremiumUsers();
  }, []);

  const loadDishes = async () => {
    try {
      const res = await fetch(`${API}/admin/dishes-full`);
      const data = await res.json();
      if (data.ok) {
        setDishes(data.dishes || []);
      }
    } catch (e) {
      console.error('Erro ao carregar pratos:', e);
    } finally {
      setLoading(false);
    }
  };

  const loadPremiumUsers = async () => {
    try {
      const res = await fetch(`${API}/admin/premium/users`);
      const data = await res.json();
      if (data.ok) {
        setPremiumUsers(data.users || []);
      }
    } catch (e) {
      console.error('Erro ao carregar usuários Premium:', e);
    }
  };

  const liberarPremium = async () => {
    if (!premiumNome.trim()) {
      alert('Digite o nome do usuário');
      return;
    }
    try {
      const formData = new FormData();
      formData.append('nome', premiumNome);
      formData.append('dias', premiumDias);
      
      const res = await fetch(`${API}/admin/premium/liberar`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.ok) {
        alert(`✅ Premium liberado para ${premiumNome} por ${premiumDias} dias!`);
        setPremiumNome('');
        loadPremiumUsers();
      } else {
        alert('Erro: ' + data.error);
      }
    } catch (e) {
      alert('Erro: ' + e.message);
    }
  };

  const bloquearPremium = async (nome) => {
    if (!window.confirm(`Bloquear Premium de "${nome}"?`)) return;
    try {
      const formData = new FormData();
      formData.append('nome', nome);
      
      const res = await fetch(`${API}/admin/premium/bloquear`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.ok) {
        alert(`✅ Premium bloqueado para ${nome}`);
        loadPremiumUsers();
      } else {
        alert('Erro: ' + data.error);
      }
    } catch (e) {
      alert('Erro: ' + e.message);
    }
  };

  // Auditoria de dados
  const runAudit = async () => {
    setAuditLoading(true);
    try {
      const res = await fetch(`${API}/admin/audit`);
      const data = await res.json();
      if (data.ok) {
        setAuditData(data);
      } else {
        alert('Erro na auditoria: ' + data.error);
      }
    } catch (e) {
      alert('Erro: ' + e.message);
    } finally {
      setAuditLoading(false);
    }
  };

  // Corrigir prato individual com IA
  const fixDishWithAI = async (slug) => {
    setFixingSlug(slug);
    try {
      const res = await fetch(`${API}/admin/audit/fix-single/${slug}`, { method: 'POST' });
      const data = await res.json();
      if (data.ok) {
        alert(`✅ Prato "${slug}" corrigido com sucesso!`);
        runAudit(); // Atualizar auditoria
        loadDishes(); // Atualizar lista
      } else {
        alert('Erro: ' + data.error);
      }
    } catch (e) {
      alert('Erro: ' + e.message);
    } finally {
      setFixingSlug(null);
    }
  };

  // Corrigir pratos em lote
  const batchFixDishes = async (problemType) => {
    if (!auditData) return;
    
    const problems = auditData.problems[problemType] || [];
    const slugs = problems.slice(0, 10).map(p => p.slug);
    
    if (slugs.length === 0) {
      alert('Nenhum prato para corrigir');
      return;
    }
    
    if (!window.confirm(`Corrigir ${slugs.length} pratos com IA? Isso pode levar alguns minutos.`)) {
      return;
    }
    
    setAuditLoading(true);
    try {
      const res = await fetch(`${API}/admin/audit/batch-fix`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slugs })
      });
      const data = await res.json();
      if (data.ok) {
        alert(`✅ Corrigidos: ${data.fixed?.length || 0}\n❌ Falhas: ${data.failed?.length || 0}\n⏭️ Pulados: ${data.skipped?.length || 0}`);
        runAudit();
        loadDishes();
      } else {
        alert('Erro: ' + data.error);
      }
    } catch (e) {
      alert('Erro: ' + e.message);
    } finally {
      setAuditLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const res = await fetch(`${API}/ai/status`);
      const data = await res.json();
      setStats(data);
    } catch (e) {
      console.error('Erro ao carregar status:', e);
    }
  };

  const loadNovidades = async () => {
    try {
      const res = await fetch(`${API}/novidades`);
      const data = await res.json();
      if (data.ok) {
        setNovidades(data.novidades || []);
      }
    } catch (e) {
      console.error('Erro ao carregar novidades:', e);
    }
  };

  const saveNovidade = async () => {
    if (!novidadeForm.dish_slug || !novidadeForm.titulo || !novidadeForm.mensagem) {
      alert('Preencha todos os campos obrigatórios');
      return;
    }
    
    try {
      const formData = new FormData();
      Object.entries(novidadeForm).forEach(([k, v]) => formData.append(k, v));
      
      const res = await fetch(`${API}/admin/novidades`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.ok) {
        alert('✅ Novidade salva!');
        setNovidadeForm({
          dish_slug: '',
          tipo: 'info',
          titulo: '',
          mensagem: '',
          emoji: '📢',
          severidade: 'info',
          ativa: true
        });
        setEditingNovidade(null);
        loadNovidades();
      } else {
        alert('Erro: ' + data.error);
      }
    } catch (e) {
      alert('Erro ao salvar: ' + e.message);
    }
  };

  const deleteNovidade = async (slug) => {
    if (!window.confirm(`Remover novidade de "${slug}"?`)) return;
    try {
      const res = await fetch(`${API}/admin/novidades/${slug}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.ok) {
        alert('✅ Novidade removida!');
        loadNovidades();
      }
    } catch (e) {
      alert('Erro ao remover: ' + e.message);
    }
  };

  const saveDish = async (dish) => {
    try {
      const res = await fetch(`${API}/admin/dishes/${dish.slug}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dish)
      });
      const data = await res.json();
      if (data.ok) {
        alert('✅ Prato salvo!');
        setEditingDish(null);
        loadDishes();
      } else {
        alert('Erro: ' + data.error);
      }
    } catch (e) {
      alert('Erro ao salvar: ' + e.message);
    }
  };

  const deleteDish = async (slug) => {
    if (!window.confirm(`Excluir "${slug}" e todas as fotos?`)) return;
    try {
      const res = await fetch(`${API}/admin/dishes/${slug}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.ok) {
        alert('✅ Prato excluído!');
        loadDishes();
      }
    } catch (e) {
      alert('Erro ao excluir: ' + e.message);
    }
  };

  const reindex = async () => {
    if (!window.confirm('Reindexar todo o dataset? Isso pode levar alguns minutos.')) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/ai/reindex?max_per_dish=10`, { method: 'POST' });
      const data = await res.json();
      alert(`✅ Reindexado: ${data.total_dishes} pratos, ${data.total_images} imagens`);
      loadStats();
      loadDishes();
    } catch (e) {
      alert('Erro: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  // Filtros
  const filteredDishes = dishes.filter(d => {
    const matchSearch = d.nome?.toLowerCase().includes(search.toLowerCase()) ||
                       d.slug?.toLowerCase().includes(search.toLowerCase());
    const matchCategory = !filterCategory || d.categoria === filterCategory;
    return matchSearch && matchCategory;
  });

  // Categorias únicas
  const categories = [...new Set(dishes.map(d => d.categoria).filter(Boolean))];

  const getCategoryColor = (cat) => {
    if (cat === 'proteína animal') return '#ef4444';
    if (cat === 'vegetariano') return '#f59e0b';
    if (cat === 'vegano') return '#22c55e';
    if (cat === 'sobremesa') return '#ec4899';
    return '#6b7280';
  };

  return (
    <div className="admin-container">
      <header className="admin-header">
        <h1>🍽️ SoulNutri Admin</h1>
        <a href="/" className="back-link">← Voltar ao App</a>
      </header>

      {/* Tabs */}
      <div className="admin-tabs">
        <button 
          className={`tab-btn ${activeTab === 'dishes' ? 'active' : ''}`}
          onClick={() => setActiveTab('dishes')}
        >
          🍽️ Pratos ({dishes.length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => { setActiveTab('audit'); if (!auditData) runAudit(); }}
        >
          🔍 Auditoria
        </button>
        <button 
          className={`tab-btn ${activeTab === 'novidades' ? 'active' : ''}`}
          onClick={() => setActiveTab('novidades')}
        >
          📢 Novidades ({novidades.length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'premium' ? 'active' : ''}`}
          onClick={() => setActiveTab('premium')}
        >
          ⭐ Premium ({premiumUsers.filter(u => u.premium_ativo).length})
        </button>
      </div>

      {/* Stats */}
      {stats && activeTab === 'dishes' && (
        <div className="stats-bar">
          <div className="stat">
            <span className="stat-value">{stats.total_dishes}</span>
            <span className="stat-label">Pratos</span>
          </div>
          <div className="stat">
            <span className="stat-value">{stats.total_embeddings}</span>
            <span className="stat-label">Imagens</span>
          </div>
          <div className="stat">
            <span className={`stat-value ${stats.ready ? 'ready' : 'not-ready'}`}>
              {stats.ready ? '✅' : '⏳'}
            </span>
            <span className="stat-label">Status</span>
          </div>
          <button className="reindex-btn" onClick={reindex} disabled={loading}>
            🔄 Reindexar
          </button>
        </div>
      )}

      {/* Search & Filters */}
      {activeTab === 'dishes' && (
        <div className="filters-bar">
          <input 
            type="text"
            placeholder="🔍 Buscar pratos..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="search-input"
          />
          <select 
            value={filterCategory} 
            onChange={e => setFilterCategory(e.target.value)}
            className="filter-select"
          >
            <option value="">Todas categorias</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          <div className="view-toggle">
            <button 
              className={viewMode === 'grid' ? 'active' : ''} 
              onClick={() => setViewMode('grid')}
            >▦</button>
            <button 
              className={viewMode === 'list' ? 'active' : ''} 
              onClick={() => setViewMode('list')}
            >☰</button>
          </div>
          <span className="result-count">{filteredDishes.length} pratos</span>
        </div>
      )}

      {/* Dishes */}
      {activeTab === 'dishes' && (loading ? (
        <div className="loading">Carregando...</div>
      ) : (
        <div className={`dishes-container ${viewMode}`}>
          {filteredDishes.map(dish => (
            <div key={dish.slug} className="dish-card-full" onClick={() => setEditingDish({...dish})}>
              {/* Foto */}
              <div className="dish-photo">
                {dish.first_image ? (
                  <img src={`${API}/admin/dish-image/${dish.slug}`} alt={dish.nome} />
                ) : (
                  <div className="no-photo">{dish.category_emoji || '🍽️'}</div>
                )}
                <span className="photo-count">📷 {dish.image_count}</span>
              </div>
              
              {/* Info */}
              <div className="dish-content">
                <div className="dish-title">
                  <span className="dish-emoji">{dish.category_emoji || '🍽️'}</span>
                  <h3>{dish.nome || dish.slug}</h3>
                </div>
                
                <span 
                  className="dish-category-badge"
                  style={{ backgroundColor: getCategoryColor(dish.categoria) }}
                >
                  {dish.categoria || '❓ Não classificado'}
                </span>
                
                <p className="dish-slug-text">📁 {dish.slug}</p>
                
                {dish.descricao && (
                  <p className="dish-desc">{dish.descricao.slice(0, 100)}...</p>
                )}
                
                {/* Ingredientes */}
                {dish.ingredientes?.length > 0 && (
                  <div className="dish-ingredients">
                    <strong>📝 Ingredientes:</strong>
                    <p>{dish.ingredientes.slice(0, 5).join(', ')}{dish.ingredientes.length > 5 ? '...' : ''}</p>
                  </div>
                )}
                
                {/* Nutrição */}
                {dish.nutricao && (
                  <div className="dish-nutrition">
                    <span>🔥 {dish.nutricao.calorias || '?'}</span>
                    <span>💪 {dish.nutricao.proteinas || '?'}</span>
                    <span>🍞 {dish.nutricao.carboidratos || '?'}</span>
                  </div>
                )}
                
                {/* Benefícios */}
                {dish.beneficios?.length > 0 && (
                  <div className="dish-benefits">
                    {dish.beneficios.slice(0, 2).map((b, i) => (
                      <span key={i} className="benefit-tag">✨ {b}</span>
                    ))}
                  </div>
                )}
                
                {/* Riscos/Alertas */}
                {dish.riscos?.length > 0 && (
                  <div className="dish-risks">
                    {dish.riscos.slice(0, 2).map((r, i) => (
                      <span key={i} className="risk-tag">⚠️ {r}</span>
                    ))}
                  </div>
                )}
                
                {/* Glúten */}
                <div className="dish-gluten">
                  {dish.contem_gluten ? '🌾 Contém glúten' : '✅ Sem glúten'}
                </div>
              </div>
              
              {/* Actions */}
              <div className="dish-actions-bar">
                <button onClick={(e) => { e.stopPropagation(); setEditingDish({...dish}); }}>
                  ✏️ Editar
                </button>
                <button className="delete-btn" onClick={(e) => { e.stopPropagation(); deleteDish(dish.slug); }}>
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      ))}

      {/* Novidades Tab */}
      {activeTab === 'novidades' && (
        <div className="novidades-section">
          {/* Form para criar/editar novidade */}
          <div className="novidade-form">
            <h3>{editingNovidade ? '✏️ Editar Novidade' : '➕ Nova Novidade'}</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label>Prato:</label>
                <select 
                  value={novidadeForm.dish_slug}
                  onChange={e => setNovidadeForm({...novidadeForm, dish_slug: e.target.value})}
                >
                  <option value="">Selecione um prato...</option>
                  {dishes.map(d => (
                    <option key={d.slug} value={d.slug}>{d.nome}</option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label>Tipo:</label>
                <select 
                  value={novidadeForm.tipo}
                  onChange={e => setNovidadeForm({...novidadeForm, tipo: e.target.value})}
                >
                  <option value="info">ℹ️ Informação</option>
                  <option value="alerta">⚠️ Alerta</option>
                  <option value="dica">💡 Dica</option>
                  <option value="estudo">📚 Estudo Científico</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Severidade:</label>
                <select 
                  value={novidadeForm.severidade}
                  onChange={e => setNovidadeForm({...novidadeForm, severidade: e.target.value})}
                >
                  <option value="info">🔵 Info</option>
                  <option value="warning">🟡 Atenção</option>
                  <option value="danger">🔴 Crítico</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Emoji:</label>
                <input 
                  value={novidadeForm.emoji}
                  onChange={e => setNovidadeForm({...novidadeForm, emoji: e.target.value})}
                  placeholder="📢"
                  maxLength={4}
                  style={{width: '60px', textAlign: 'center', fontSize: '1.5rem'}}
                />
              </div>
              
              <div className="form-group" style={{flex: 1}}>
                <label>Título:</label>
                <input 
                  value={novidadeForm.titulo}
                  onChange={e => setNovidadeForm({...novidadeForm, titulo: e.target.value})}
                  placeholder="Título da novidade..."
                />
              </div>
            </div>

            <div className="form-group">
              <label>Mensagem:</label>
              <textarea 
                value={novidadeForm.mensagem}
                onChange={e => setNovidadeForm({...novidadeForm, mensagem: e.target.value})}
                placeholder="Mensagem detalhada para os usuários Premium..."
                rows={3}
              />
            </div>

            <div className="form-row">
              <label className="checkbox-inline">
                <input 
                  type="checkbox"
                  checked={novidadeForm.ativa}
                  onChange={e => setNovidadeForm({...novidadeForm, ativa: e.target.checked})}
                />
                Ativa
              </label>
              
              <button className="save-btn" onClick={saveNovidade}>
                💾 Salvar Novidade
              </button>
              
              {editingNovidade && (
                <button className="cancel-btn" onClick={() => {
                  setEditingNovidade(null);
                  setNovidadeForm({
                    dish_slug: '',
                    tipo: 'info',
                    titulo: '',
                    mensagem: '',
                    emoji: '📢',
                    severidade: 'info',
                    ativa: true
                  });
                }}>
                  Cancelar
                </button>
              )}
            </div>
          </div>

          {/* Lista de novidades */}
          <div className="novidades-list">
            <h3>📋 Novidades Ativas ({novidades.length})</h3>
            
            {novidades.length === 0 ? (
              <p className="no-items">Nenhuma novidade cadastrada. Crie uma acima!</p>
            ) : (
              novidades.map(n => (
                <div key={n.dish_slug} className={`novidade-card ${n.severidade}`}>
                  <div className="novidade-header">
                    <span className="novidade-emoji">{n.emoji}</span>
                    <span className="novidade-dish">{n.dish_slug}</span>
                    <span className={`novidade-tipo ${n.tipo}`}>{n.tipo}</span>
                  </div>
                  <h4>{n.titulo}</h4>
                  <p>{n.mensagem}</p>
                  <div className="novidade-actions">
                    <button onClick={() => {
                      setEditingNovidade(n);
                      setNovidadeForm(n);
                    }}>
                      ✏️ Editar
                    </button>
                    <button className="delete-btn" onClick={() => deleteNovidade(n.dish_slug)}>
                      🗑️ Remover
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Audit Tab */}
      {activeTab === 'audit' && (
        <div className="audit-section">
          <div className="audit-header">
            <h2>🔍 Auditoria de Qualidade dos Dados</h2>
            <button 
              className="refresh-btn" 
              onClick={runAudit}
              disabled={auditLoading}
            >
              {auditLoading ? '⏳ Analisando...' : '🔄 Atualizar Auditoria'}
            </button>
          </div>

          {auditLoading && (
            <div className="audit-loading">
              <p>⏳ Analisando {dishes.length} pratos... Isso pode levar alguns segundos.</p>
            </div>
          )}

          {auditData && !auditLoading && (
            <>
              {/* Score de Saúde */}
              <div className="health-score-card">
                <div className="health-score" style={{
                  color: auditData.health_score >= 70 ? '#22c55e' : 
                         auditData.health_score >= 40 ? '#f59e0b' : '#ef4444'
                }}>
                  {auditData.health_score}%
                </div>
                <div className="health-label">Saúde dos Dados</div>
                <p>{auditData.dishes_with_issues} de {auditData.total_dishes} pratos com problemas</p>
              </div>

              {/* Resumo de Problemas */}
              <div className="audit-summary">
                <h3>📊 Resumo dos Problemas</h3>
                <div className="audit-stats-grid">
                  <div className="audit-stat critical">
                    <span className="stat-number">{auditData.summary.missing_info_file}</span>
                    <span className="stat-label">Sem arquivo de info</span>
                  </div>
                  <div className="audit-stat critical">
                    <span className="stat-number">{auditData.summary.unknown_names}</span>
                    <span className="stat-label">Nomes "Unknown"</span>
                  </div>
                  <div className="audit-stat critical">
                    <span className="stat-number">{auditData.summary.category_conflicts}</span>
                    <span className="stat-label">Conflitos de categoria</span>
                  </div>
                  <div className="audit-stat warning">
                    <span className="stat-number">{auditData.summary.empty_nutrition}</span>
                    <span className="stat-label">Nutrição vazia</span>
                  </div>
                  <div className="audit-stat warning">
                    <span className="stat-number">{auditData.summary.missing_ingredients}</span>
                    <span className="stat-label">Sem ingredientes</span>
                  </div>
                  <div className="audit-stat warning">
                    <span className="stat-number">{auditData.summary.allergen_conflicts}</span>
                    <span className="stat-label">Alérgenos incorretos</span>
                  </div>
                  <div className="audit-stat info">
                    <span className="stat-number">{auditData.summary.missing_description}</span>
                    <span className="stat-label">Sem descrição</span>
                  </div>
                </div>
              </div>

              {/* Lista de Problemas Críticos */}
              {auditData.problems.unknown_names.length > 0 && (
                <div className="audit-problems">
                  <h3>🔴 Pratos com Nome "Unknown" (Crítico)</h3>
                  <div className="problems-list">
                    {auditData.problems.unknown_names.map((p, i) => (
                      <div key={i} className="problem-item critical">
                        <span className="problem-slug">{p.slug}</span>
                        <span className="problem-issue">{p.issue}</span>
                        <button 
                          className="edit-btn"
                          onClick={() => {
                            const dish = dishes.find(d => d.slug === p.slug);
                            if (dish) setEditingDish(dish);
                            setActiveTab('dishes');
                          }}
                        >
                          ✏️ Editar
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {auditData.problems.category_conflicts.length > 0 && (
                <div className="audit-problems">
                  <h3>🔴 Conflitos de Categoria (Crítico)</h3>
                  <div className="problems-list">
                    {auditData.problems.category_conflicts.map((p, i) => (
                      <div key={i} className="problem-item critical">
                        <span className="problem-slug">{p.nome}</span>
                        <span className="problem-issue">{p.issue}</span>
                        <button 
                          className="edit-btn"
                          onClick={() => {
                            const dish = dishes.find(d => d.slug === p.slug);
                            if (dish) setEditingDish(dish);
                            setActiveTab('dishes');
                          }}
                        >
                          ✏️ Corrigir
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {auditData.problems.empty_nutrition.length > 0 && (
                <div className="audit-problems">
                  <h3>🟡 Pratos sem Informação Nutricional ({auditData.problems.empty_nutrition.length})</h3>
                  <p className="problems-note">Estes pratos não mostram calorias corretamente.</p>
                  <div className="problems-list scrollable">
                    {auditData.problems.empty_nutrition.slice(0, 20).map((p, i) => (
                      <div key={i} className="problem-item warning">
                        <span className="problem-slug">{p.nome || p.slug}</span>
                        <button 
                          className="edit-btn small"
                          onClick={() => {
                            const dish = dishes.find(d => d.slug === p.slug);
                            if (dish) setEditingDish(dish);
                            setActiveTab('dishes');
                          }}
                        >
                          ✏️
                        </button>
                      </div>
                    ))}
                    {auditData.problems.empty_nutrition.length > 20 && (
                      <p className="more-items">...e mais {auditData.problems.empty_nutrition.length - 20} pratos</p>
                    )}
                  </div>
                </div>
              )}

              {auditData.problems.missing_info_file.length > 0 && (
                <div className="audit-problems">
                  <h3>🔴 Pratos sem dish_info.json ({auditData.problems.missing_info_file.length})</h3>
                  <p className="problems-note">Estes pratos precisam ser configurados manualmente.</p>
                  <div className="problems-list scrollable">
                    {auditData.problems.missing_info_file.slice(0, 20).map((p, i) => (
                      <div key={i} className="problem-item critical">
                        <span className="problem-slug">{p.slug}</span>
                      </div>
                    ))}
                    {auditData.problems.missing_info_file.length > 20 && (
                      <p className="more-items">...e mais {auditData.problems.missing_info_file.length - 20} pratos</p>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Premium Tab */}
      {activeTab === 'premium' && (
        <div className="premium-admin-section">
          {/* Formulário para liberar Premium */}
          <div className="premium-form">
            <h3>⭐ Liberar Acesso Premium</h3>
            
            <div className="form-row">
              <div className="form-group" style={{flex: 2}}>
                <label>Nome do Usuário:</label>
                <input 
                  value={premiumNome}
                  onChange={e => setPremiumNome(e.target.value)}
                  placeholder="Digite o nome exato do usuário..."
                />
              </div>
              
              <div className="form-group" style={{flex: 1}}>
                <label>Dias de Acesso:</label>
                <select value={premiumDias} onChange={e => setPremiumDias(Number(e.target.value))}>
                  <option value={7}>7 dias</option>
                  <option value={30}>30 dias</option>
                  <option value={90}>90 dias</option>
                  <option value={365}>1 ano</option>
                  <option value={9999}>Ilimitado</option>
                </select>
              </div>
              
              <button className="save-btn" onClick={liberarPremium}>
                ✅ Liberar Premium
              </button>
            </div>
          </div>

          {/* Lista de usuários */}
          <div className="premium-users-list">
            <h3>👥 Usuários Cadastrados ({premiumUsers.length})</h3>
            
            {premiumUsers.length === 0 ? (
              <p className="no-items">Nenhum usuário cadastrado ainda.</p>
            ) : (
              <table className="premium-table">
                <thead>
                  <tr>
                    <th>Nome</th>
                    <th>Status</th>
                    <th>Expira em</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {premiumUsers.map((user, i) => (
                    <tr key={i} className={user.premium_ativo ? 'ativo' : 'inativo'}>
                      <td>{user.nome}</td>
                      <td>
                        {user.premium_ativo ? (
                          <span className="badge ativo">✅ Ativo</span>
                        ) : (
                          <span className="badge inativo">🔒 Bloqueado</span>
                        )}
                      </td>
                      <td>
                        {user.premium_expira_em 
                          ? new Date(user.premium_expira_em).toLocaleDateString('pt-BR')
                          : '-'}
                      </td>
                      <td>
                        {user.premium_ativo ? (
                          <button className="delete-btn" onClick={() => bloquearPremium(user.nome)}>
                            🔒 Bloquear
                          </button>
                        ) : (
                          <button className="save-btn" onClick={() => {
                            setPremiumNome(user.nome);
                            setPremiumDias(30);
                          }}>
                            ✅ Liberar
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* Edit Modal - Completo */}
      {editingDish && (
        <div className="modal-overlay" onClick={() => setEditingDish(null)}>
          <div className="edit-modal-full" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>✏️ Editar: {editingDish.nome}</h2>
              <button className="close-btn" onClick={() => setEditingDish(null)}>✕</button>
            </div>
            
            <div className="modal-body">
              {/* Foto do prato */}
              <div className="edit-photo-section">
                {editingDish.first_image ? (
                  <img src={`${API}/admin/dish-image/${editingDish.slug}`} alt={editingDish.nome} />
                ) : (
                  <div className="no-photo-large">{editingDish.category_emoji || '🍽️'}</div>
                )}
                <p className="photo-info">📷 {editingDish.image_count} fotos</p>
              </div>
              
              <div className="edit-fields">
                <div className="form-row">
                  <div className="form-group">
                    <label>Nome do Prato:</label>
                    <input 
                      value={editingDish.nome || ''}
                      onChange={e => setEditingDish({...editingDish, nome: e.target.value})}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Categoria:</label>
                    <select 
                      value={editingDish.categoria || ''}
                      onChange={e => setEditingDish({...editingDish, categoria: e.target.value})}
                    >
                      <option value="">Selecione...</option>
                      <option value="proteína animal">🍖 Proteína Animal</option>
                      <option value="vegetariano">🥚 Vegetariano</option>
                      <option value="vegano">🥬 Vegano</option>
                      <option value="sobremesa">🍰 Sobremesa</option>
                      <option value="outros">🍽️ Outros</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label>Descrição:</label>
                  <textarea 
                    value={editingDish.descricao || ''}
                    onChange={e => setEditingDish({...editingDish, descricao: e.target.value})}
                    rows={2}
                  />
                </div>

                <div className="form-group">
                  <label>Ingredientes (um por linha):</label>
                  <textarea 
                    value={(editingDish.ingredientes || []).join('\n')}
                    onChange={e => setEditingDish({
                      ...editingDish, 
                      ingredientes: e.target.value.split('\n').filter(i => i.trim())
                    })}
                    rows={4}
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Benefícios (um por linha):</label>
                    <textarea 
                      value={(editingDish.beneficios || []).join('\n')}
                      onChange={e => setEditingDish({
                        ...editingDish, 
                        beneficios: e.target.value.split('\n').filter(i => i.trim())
                      })}
                      rows={3}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Riscos/Alertas (um por linha):</label>
                    <textarea 
                      value={(editingDish.riscos || []).join('\n')}
                      onChange={e => setEditingDish({
                        ...editingDish, 
                        riscos: e.target.value.split('\n').filter(i => i.trim())
                      })}
                      rows={3}
                    />
                  </div>
                </div>

                <div className="form-row nutrition-row">
                  <div className="form-group small">
                    <label>🔥 Calorias:</label>
                    <input 
                      value={editingDish.nutricao?.calorias || ''}
                      onChange={e => setEditingDish({
                        ...editingDish, 
                        nutricao: {...(editingDish.nutricao || {}), calorias: e.target.value}
                      })}
                      placeholder="~200 kcal"
                    />
                  </div>
                  <div className="form-group small">
                    <label>💪 Proteínas:</label>
                    <input 
                      value={editingDish.nutricao?.proteinas || ''}
                      onChange={e => setEditingDish({
                        ...editingDish, 
                        nutricao: {...(editingDish.nutricao || {}), proteinas: e.target.value}
                      })}
                      placeholder="~15g"
                    />
                  </div>
                  <div className="form-group small">
                    <label>🍞 Carbos:</label>
                    <input 
                      value={editingDish.nutricao?.carboidratos || ''}
                      onChange={e => setEditingDish({
                        ...editingDish, 
                        nutricao: {...(editingDish.nutricao || {}), carboidratos: e.target.value}
                      })}
                      placeholder="~20g"
                    />
                  </div>
                  <div className="form-group small">
                    <label>🧈 Gorduras:</label>
                    <input 
                      value={editingDish.nutricao?.gorduras || ''}
                      onChange={e => setEditingDish({
                        ...editingDish, 
                        nutricao: {...(editingDish.nutricao || {}), gorduras: e.target.value}
                      })}
                      placeholder="~8g"
                    />
                  </div>
                </div>

                <div className="form-group checkbox-group">
                  <label>
                    <input 
                      type="checkbox"
                      checked={editingDish.contem_gluten || false}
                      onChange={e => setEditingDish({...editingDish, contem_gluten: e.target.checked})}
                    />
                    🌾 Contém Glúten
                  </label>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="save-btn" onClick={() => saveDish(editingDish)}>
                💾 Salvar Alterações
              </button>
              <button className="cancel-btn" onClick={() => setEditingDish(null)}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
