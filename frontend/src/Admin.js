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

  useEffect(() => {
    loadDishes();
    loadStats();
  }, []);

  const loadDishes = async () => {
    try {
      const res = await fetch(`${API}/admin/dishes`);
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

  const loadStats = async () => {
    try {
      const res = await fetch(`${API}/ai/status`);
      const data = await res.json();
      setStats(data);
    } catch (e) {
      console.error('Erro ao carregar status:', e);
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
    if (!window.confirm(`Excluir "${slug}"?`)) return;
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
    } catch (e) {
      alert('Erro: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredDishes = dishes.filter(d => 
    d.nome?.toLowerCase().includes(search.toLowerCase()) ||
    d.slug?.toLowerCase().includes(search.toLowerCase())
  );

  const getCategoryColor = (cat) => {
    if (cat === 'proteína animal') return '#ef4444';
    if (cat === 'vegetariano') return '#f59e0b';
    if (cat === 'vegano') return '#22c55e';
    return '#6b7280';
  };

  return (
    <div className="admin-container">
      <header className="admin-header">
        <h1>🍽️ SoulNutri Admin</h1>
        <a href="/" className="back-link">← Voltar ao App</a>
      </header>

      {/* Stats */}
      {stats && (
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

      {/* Search */}
      <div className="search-bar">
        <input 
          type="text"
          placeholder="🔍 Buscar pratos..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <span className="result-count">{filteredDishes.length} pratos</span>
      </div>

      {/* Dishes List */}
      {loading ? (
        <div className="loading">Carregando...</div>
      ) : (
        <div className="dishes-grid">
          {filteredDishes.map(dish => (
            <div key={dish.slug} className="dish-card">
              <div className="dish-header">
                <span className="dish-emoji">{dish.category_emoji || '🍽️'}</span>
                <div className="dish-info">
                  <h3>{dish.nome || dish.slug}</h3>
                  <span 
                    className="dish-category"
                    style={{ backgroundColor: getCategoryColor(dish.categoria) }}
                  >
                    {dish.categoria || 'Não classificado'}
                  </span>
                </div>
              </div>
              
              <div className="dish-details">
                <p className="dish-slug">📁 {dish.slug}</p>
                <p className="dish-images">🖼️ {dish.image_count || '?'} fotos</p>
                {dish.ingredientes?.length > 0 && (
                  <p className="dish-ingredients">
                    📝 {dish.ingredientes.slice(0, 3).join(', ')}
                    {dish.ingredientes.length > 3 && '...'}
                  </p>
                )}
              </div>

              <div className="dish-actions">
                <button onClick={() => setEditingDish({...dish})}>✏️ Editar</button>
                <button className="delete" onClick={() => deleteDish(dish.slug)}>🗑️</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Edit Modal */}
      {editingDish && (
        <div className="modal-overlay" onClick={() => setEditingDish(null)}>
          <div className="edit-modal" onClick={e => e.stopPropagation()}>
            <h2>✏️ Editar: {editingDish.nome}</h2>
            
            <div className="form-group">
              <label>Nome:</label>
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

            <div className="form-group">
              <label>Descrição:</label>
              <textarea 
                value={editingDish.descricao || ''}
                onChange={e => setEditingDish({...editingDish, descricao: e.target.value})}
                rows={2}
              />
            </div>

            <div className="modal-actions">
              <button className="save-btn" onClick={() => saveDish(editingDish)}>
                💾 Salvar
              </button>
              <button className="cancel-btn" onClick={() => setEditingDish(null)}>
                ✕ Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
