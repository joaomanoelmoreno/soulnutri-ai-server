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
  // Consolidação e Atualização em Massa
  const [consolidating, setConsolidating] = useState(false);
  const [updatingAll, setUpdatingAll] = useState(false);
  const [massActionResult, setMassActionResult] = useState(null);
  // Revisão com IA
  const [revisandoIA, setRevisandoIA] = useState(false);
  // Criar Novo Prato
  const [showNewDishModal, setShowNewDishModal] = useState(false);
  const [newDishName, setNewDishName] = useState('');
  const [newDishFile, setNewDishFile] = useState(null);
  const [creatingDish, setCreatingDish] = useState(false);
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

  // Estado para uso de APIs
  const [apiUsage, setApiUsage] = useState(null);

  const loadApiUsage = async () => {
    try {
      const res = await fetch(`${API}/admin/api-usage`);
      const data = await res.json();
      if (data.ok) {
        setApiUsage(data);
      }
    } catch (e) {
      console.error('Erro ao carregar uso de APIs:', e);
    }
  };

  useEffect(() => {
    loadApiUsage();
  }, []);

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

  // EXCLUIR PRATO
  const deleteDish = async (slug, nome) => {
    if (!window.confirm(`🗑️ Excluir "${nome || slug}"?\n\nIsso removerá:\n• Todas as fotos\n• Informações do prato\n\n⚠️ Esta ação não pode ser desfeita!`)) {
      return;
    }
    
    try {
      const res = await fetch(`${API}/admin/dishes/${slug}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.ok) {
        loadDishes();
        runAudit();
      } else {
        alert('Erro ao excluir: ' + data.error);
      }
    } catch (e) {
      alert('Erro: ' + e.message);
    }
  };

  // CONSOLIDAR DUPLICADOS (sem créditos)
  const consolidateDuplicates = async () => {
    if (!window.confirm('🔗 Consolidar pratos duplicados?\n\nIsso vai:\n• Mesclar pratos com nomes similares\n• Unir todas as imagens\n• Preservar a informação mais completa\n\n✅ NÃO CONSOME CRÉDITOS')) {
      return;
    }
    
    setConsolidating(true);
    setMassActionResult(null);
    try {
      const res = await fetch(`${API}/admin/consolidate-all`, { method: 'POST' });
      const data = await res.json();
      if (data.ok) {
        setMassActionResult({
          type: 'consolidate',
          success: true,
          message: `✅ ${data.consolidated || 0} grupos consolidados!`
        });
        loadDishes();
        runAudit();
      } else {
        setMassActionResult({
          type: 'consolidate',
          success: false,
          message: '❌ Erro: ' + data.error
        });
      }
    } catch (e) {
      setMassActionResult({
        type: 'consolidate',
        success: false,
        message: '❌ Erro: ' + e.message
      });
    } finally {
      setConsolidating(false);
    }
  };

  // ATUALIZAR TODOS OS PRATOS LOCALMENTE (sem créditos)
  const updateAllLocal = async () => {
    if (!window.confirm('🔄 Atualizar TODOS os pratos?\n\nIsso vai preencher:\n• Categoria\n• Ingredientes\n• Benefícios e Riscos\n• Informação Nutricional\n• Alérgenos\n• Campos Premium\n\n✅ NÃO CONSOME CRÉDITOS\n⚡ Processo instantâneo')) {
      return;
    }
    
    setUpdatingAll(true);
    setMassActionResult(null);
    try {
      const res = await fetch(`${API}/admin/update-all-local`, { method: 'POST' });
      const data = await res.json();
      if (data.ok) {
        setMassActionResult({
          type: 'update',
          success: true,
          message: `✅ ${data.atualizados}/${data.total} pratos atualizados!`,
          details: data.por_tipo
        });
        loadDishes();
        runAudit();
      } else {
        setMassActionResult({
          type: 'update',
          success: false,
          message: '❌ Erro: ' + data.error
        });
      }
    } catch (e) {
      setMassActionResult({
        type: 'update',
        success: false,
        message: '❌ Erro: ' + e.message
      });
    } finally {
      setUpdatingAll(false);
    }
  };

  // REVISAR PRATOS EM LOTE COM IA GEMINI (consome créditos)
  const [revisandoLote, setRevisandoLote] = useState(false);
  const [loteProgress, setLoteProgress] = useState(null);
  
  const revisarTodosComIA = async () => {
    // Filtrar pratos que têm ingredientes
    const pratosComIngredientes = dishes.filter(d => 
      d.ingredientes && d.ingredientes.length > 0
    );
    
    if (pratosComIngredientes.length === 0) {
      alert('Nenhum prato com ingredientes para revisar');
      return;
    }
    
    const qtd = Math.min(pratosComIngredientes.length, 50);
    if (!window.confirm(
      `🤖 Revisar fichas nutricionais com IA?\n\n` +
      `📋 ${qtd} pratos serão revisados\n` +
      `⚠️ CONSOME CRÉDITOS DE IA\n\n` +
      `Isso vai corrigir:\n` +
      `• Categoria (vegano/vegetariano/proteína)\n` +
      `• Calorias e macronutrientes\n` +
      `• Benefícios e riscos\n` +
      `• Alérgenos\n\n` +
      `Continuar?`
    )) {
      return;
    }
    
    setRevisandoLote(true);
    setLoteProgress({ total: qtd, atual: 0, revisados: 0, falhas: 0 });
    setMassActionResult(null);
    
    try {
      // Processar em lotes de 10
      const slugs = pratosComIngredientes.slice(0, qtd).map(d => d.slug);
      const loteSize = 10;
      let totalRevisados = 0;
      let totalFalhas = 0;
      
      for (let i = 0; i < slugs.length; i += loteSize) {
        const lote = slugs.slice(i, i + loteSize);
        
        setLoteProgress(prev => ({ ...prev, atual: i }));
        
        const res = await fetch(`${API}/admin/revisar-lote-ia`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ slugs: lote, max_pratos: loteSize })
        });
        
        const data = await res.json();
        
        if (data.ok) {
          totalRevisados += data.revisados;
          totalFalhas += data.falhas;
          setLoteProgress(prev => ({ 
            ...prev, 
            revisados: totalRevisados,
            falhas: totalFalhas
          }));
        }
        
        // Pequena pausa entre lotes
        await new Promise(r => setTimeout(r, 500));
      }
      
      setMassActionResult({
        type: 'revisar-ia',
        success: true,
        message: `✅ Revisão concluída! ${totalRevisados} pratos atualizados, ${totalFalhas} falhas`
      });
      
      loadDishes();
      runAudit();
      
    } catch (e) {
      setMassActionResult({
        type: 'revisar-ia',
        success: false,
        message: '❌ Erro: ' + e.message
      });
    } finally {
      setRevisandoLote(false);
      setLoteProgress(null);
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
      
      // Verificar se a resposta é válida antes de parsear
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch (parseError) {
        console.error('Erro ao parsear resposta:', text);
        alert('Erro ao processar resposta do servidor');
        return;
      }
      
      if (data.ok) {
        alert('✅ Prato salvo!');
        setEditingDish(null);
        loadDishes();
      } else {
        alert('Erro: ' + (data.error || 'Erro desconhecido'));
      }
    } catch (e) {
      console.error('Erro ao salvar:', e);
      alert('Erro ao salvar: ' + e.message);
    }
  };

  // Criar novo prato com upload de foto
  const createNewDishAdmin = async () => {
    if (!newDishName.trim()) {
      alert('Digite o nome do prato');
      return;
    }
    if (!newDishFile) {
      alert('Selecione uma foto do prato');
      return;
    }
    
    setCreatingDish(true);
    try {
      const fd = new FormData();
      fd.append('file', newDishFile);
      fd.append('dish_name', newDishName.trim());
      
      const res = await fetch(`${API}/ai/create-dish-local`, {
        method: 'POST',
        body: fd
      });
      
      const data = await res.json();
      
      if (data.ok) {
        alert(`✅ Prato "${newDishName}" criado com sucesso!\n\n💰 Créditos usados: 0\n\n📝 Edite os detalhes na lista de pratos.`);
        setShowNewDishModal(false);
        setNewDishName('');
        setNewDishFile(null);
        loadDishes();
        loadStats();
      } else {
        alert('Erro: ' + data.error);
      }
    } catch (e) {
      alert('Erro ao criar: ' + e.message);
    } finally {
      setCreatingDish(false);
    }
  };

  // Revisar prato com IA (Gemini Flash)
  const revisarComIA = async () => {
    if (!editingDish) return;
    
    const ingredientes = editingDish.ingredientes || [];
    if (ingredientes.length === 0 || (ingredientes.length === 1 && !ingredientes[0].trim())) {
      alert('⚠️ Adicione os ingredientes primeiro para a IA analisar!');
      return;
    }
    
    setRevisandoIA(true);
    try {
      const res = await fetch(`${API}/admin/revisar-prato-ia`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome: editingDish.nome,
          ingredientes: ingredientes.filter(i => i.trim())
        })
      });
      
      const data = await res.json();
      
      if (data.ok && data.sugestoes) {
        const s = data.sugestoes;
        const n = s.nutricao || {};
        
        // Mostrar sugestões com nutrição
        const msg = `🤖 Sugestões da IA para "${editingDish.nome}":\n\n` +
          `📂 Categoria: ${s.categoria}\n\n` +
          `📊 Nutrição (por 100g):\n` +
          `  🔥 Calorias: ${n.calorias || 'N/A'}\n` +
          `  💪 Proteínas: ${n.proteinas || 'N/A'}\n` +
          `  🍞 Carboidratos: ${n.carboidratos || 'N/A'}\n` +
          `  🧈 Gorduras: ${n.gorduras || 'N/A'}\n` +
          `  🥬 Fibras: ${n.fibras || 'N/A'}\n\n` +
          `✅ Benefícios:\n${(s.beneficios || []).map(b => '  • ' + b).join('\n')}\n\n` +
          `⚠️ Riscos:\n${(s.riscos || []).map(r => '  • ' + r).join('\n')}\n\n` +
          `Deseja aplicar estas sugestões?`;
        
        if (window.confirm(msg)) {
          // Aplicar sugestões incluindo nutrição
          const alergenos = s.alergenos || {};
          setEditingDish({
            ...editingDish,
            categoria: s.categoria,
            beneficios: s.beneficios || [],
            riscos: s.riscos || [],
            nutricao: {
              calorias: n.calorias || '',
              proteinas: n.proteinas || '',
              carboidratos: n.carboidratos || '',
              gorduras: n.gorduras || '',
              fibras: n.fibras || ''
            },
            contem_gluten: alergenos.gluten || false,
            contem_lactose: alergenos.lactose || false,
            contem_ovo: alergenos.ovo || false,
            contem_frutos_mar: alergenos.frutos_do_mar || false,
            contem_castanhas: alergenos.oleaginosas || false
          });
          alert('✅ Sugestões aplicadas! Clique em "Salvar" para confirmar.');
        }
      } else {
        alert('❌ Erro: ' + (data.error || 'Não foi possível analisar'));
      }
    } catch (e) {
      console.error('Erro ao revisar com IA:', e);
      alert('❌ Erro ao conectar com IA: ' + e.message);
    } finally {
      setRevisandoIA(false);
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
        <button 
          className={`tab-btn ${activeTab === 'custos' ? 'active' : ''}`}
          onClick={() => { setActiveTab('custos'); loadApiUsage(); }}
        >
          💰 Custos API
        </button>
      </div>

      {/* Painel de Custos de API */}
      {activeTab === 'custos' && (
        <div className="api-usage-panel">
          <h2>💰 Controle de Custos - APIs Externas</h2>
          
          {apiUsage?.google_vision && (
            <div className="api-card">
              <h3>🔍 Google Cloud Vision</h3>
              <div className="api-stats">
                <div className="api-stat">
                  <span className="api-value">{apiUsage.google_vision.calls_this_month || 0}</span>
                  <span className="api-label">Chamadas este mês</span>
                </div>
                <div className="api-stat">
                  <span className="api-value">{apiUsage.google_vision.calls_remaining_free || 1000}</span>
                  <span className="api-label">Restantes GRÁTIS</span>
                </div>
                <div className="api-stat">
                  <span className="api-value">R$ {apiUsage.google_vision.estimated_cost_brl || '0.00'}</span>
                  <span className="api-label">Custo estimado</span>
                </div>
              </div>
              
              <div className="api-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{
                      width: `${Math.min(100, (apiUsage.google_vision.calls_this_month / 1000) * 100)}%`,
                      backgroundColor: apiUsage.google_vision.calls_this_month > 800 ? '#ff9800' : '#4CAF50'
                    }}
                  ></div>
                </div>
                <span className="progress-text">
                  {apiUsage.google_vision.calls_this_month || 0} / 1.000 grátis
                </span>
              </div>
              
              <p className="api-info">
                ℹ️ Após 1.000 chamadas: R$ 0,0075 por imagem analisada
              </p>
              
              {apiUsage.google_vision.history?.length > 0 && (
                <div className="api-history">
                  <h4>Histórico</h4>
                  {apiUsage.google_vision.history.map((h, i) => (
                    <div key={i} className="history-item">
                      <span>{h.month}</span>
                      <span>{h.calls} chamadas</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          
          {!apiUsage && (
            <p>Carregando dados de uso...</p>
          )}
          
          <button onClick={loadApiUsage} className="refresh-btn">
            🔄 Atualizar
          </button>
        </div>
      )}

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
          <button 
            className="new-dish-btn"
            onClick={() => setShowNewDishModal(true)}
            style={{
              background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
              color: '#fff',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '14px'
            }}
          >
            ➕ Novo Prato
          </button>
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

      {/* Modal Criar Novo Prato */}
      {showNewDishModal && (
        <div className="modal-overlay" onClick={() => setShowNewDishModal(false)}>
          <div className="edit-modal-full" onClick={e => e.stopPropagation()} style={{ maxWidth: '500px' }}>
            <div className="modal-header">
              <h2>➕ Cadastrar Novo Prato</h2>
              <button className="close-btn" onClick={() => setShowNewDishModal(false)}>✕</button>
            </div>
            
            <div className="modal-body" style={{ padding: '20px' }}>
              <div className="form-group">
                <label>📸 Foto do Prato:</label>
                <input 
                  type="file" 
                  accept="image/*"
                  onChange={e => setNewDishFile(e.target.files[0])}
                  style={{ marginTop: '8px' }}
                />
                {newDishFile && (
                  <p style={{ color: '#22c55e', marginTop: '8px' }}>
                    ✅ {newDishFile.name}
                  </p>
                )}
              </div>
              
              <div className="form-group" style={{ marginTop: '20px' }}>
                <label>🍽️ Nome do Prato:</label>
                <input 
                  type="text"
                  value={newDishName}
                  onChange={e => setNewDishName(e.target.value)}
                  placeholder="Ex: Frango Grelhado com Legumes"
                  style={{ width: '100%', marginTop: '8px' }}
                />
              </div>
              
              <p style={{ color: '#888', fontSize: '12px', marginTop: '20px' }}>
                💡 Após criar, edite o prato para adicionar ingredientes e usar a IA para preencher automaticamente categoria, nutrição e alérgenos.
              </p>
              
              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button 
                  onClick={createNewDishAdmin}
                  disabled={creatingDish || !newDishName.trim() || !newDishFile}
                  style={{
                    flex: 1,
                    background: creatingDish ? '#555' : '#22c55e',
                    color: '#fff',
                    border: 'none',
                    padding: '12px',
                    borderRadius: '8px',
                    cursor: creatingDish ? 'wait' : 'pointer',
                    fontWeight: 'bold'
                  }}
                >
                  {creatingDish ? '⏳ Criando...' : '✅ Criar Prato'}
                </button>
                <button 
                  onClick={() => setShowNewDishModal(false)}
                  style={{
                    background: '#444',
                    color: '#fff',
                    border: 'none',
                    padding: '12px 20px',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
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

          {/* AÇÕES EM MASSA - SEM CRÉDITOS */}
          <div className="mass-actions-panel" style={{
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '20px',
            border: '1px solid #0f3460'
          }}>
            <h3 style={{ color: '#fff', marginBottom: '15px' }}>⚡ Ações em Massa (SEM CRÉDITOS)</h3>
            
            <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
              <button
                onClick={consolidateDuplicates}
                disabled={consolidating}
                style={{
                  background: consolidating ? '#555' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: '#fff',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  cursor: consolidating ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold',
                  fontSize: '14px'
                }}
              >
                {consolidating ? '⏳ Consolidando...' : '🔗 Consolidar Duplicados'}
              </button>
              
              <button
                onClick={updateAllLocal}
                disabled={updatingAll}
                style={{
                  background: updatingAll ? '#555' : 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
                  color: '#fff',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  cursor: updatingAll ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold',
                  fontSize: '14px'
                }}
              >
                {updatingAll ? '⏳ Atualizando...' : '🔄 Atualizar Todos os Pratos'}
              </button>
            </div>
            
            <p style={{ color: '#888', fontSize: '12px', marginTop: '10px' }}>
              ✅ Essas ações são processadas localmente e NÃO consomem créditos de IA.
            </p>
          </div>
          
          {/* REVISÃO EM LOTE COM IA */}
          <div className="mass-actions-panel" style={{
            background: 'linear-gradient(135deg, #ff6b35 0%, #f7931e 100%)',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '20px',
            border: '1px solid #ff6b35'
          }}>
            <h3 style={{ color: '#fff', marginBottom: '15px' }}>🤖 Revisão com IA Gemini (CONSOME CRÉDITOS)</h3>
            
            <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', alignItems: 'center' }}>
              <button
                onClick={revisarTodosComIA}
                disabled={revisandoLote}
                style={{
                  background: revisandoLote ? '#555' : 'linear-gradient(135deg, #e91e63 0%, #f44336 100%)',
                  color: '#fff',
                  border: 'none',
                  padding: '14px 28px',
                  borderRadius: '8px',
                  cursor: revisandoLote ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold',
                  fontSize: '15px'
                }}
              >
                {revisandoLote ? '⏳ Revisando...' : '🤖 Revisar TODAS as Fichas Nutricionais'}
              </button>
              
              {loteProgress && (
                <div style={{ color: '#fff', fontSize: '14px' }}>
                  <span>Progresso: {loteProgress.atual}/{loteProgress.total}</span>
                  <br />
                  <span style={{ color: '#8f8' }}>✅ {loteProgress.revisados} OK</span>
                  {loteProgress.falhas > 0 && (
                    <span style={{ color: '#f88', marginLeft: '10px' }}>❌ {loteProgress.falhas} falhas</span>
                  )}
                </div>
              )}
            </div>
            
            <p style={{ color: 'rgba(255,255,255,0.8)', fontSize: '12px', marginTop: '10px' }}>
              ⚠️ Esta ação usa a IA Gemini Flash para corrigir calorias, macros e categorias. Consome créditos.
            </p>
          </div>
            
          {/* Resultado da ação em massa */}
          {massActionResult && (
            <div style={{
              marginTop: '15px',
              marginBottom: '20px',
              padding: '12px',
              borderRadius: '8px',
              background: massActionResult.success ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
              border: `1px solid ${massActionResult.success ? '#22c55e' : '#ef4444'}`
            }}>
              <p style={{ color: '#fff', fontWeight: 'bold', margin: 0 }}>
                {massActionResult.message}
              </p>
              {massActionResult.details && (
                <div style={{ marginTop: '10px', fontSize: '12px', color: '#aaa' }}>
                  <strong>Por tipo:</strong>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '5px' }}>
                    {Object.entries(massActionResult.details).map(([tipo, count]) => (
                      <span key={tipo} style={{
                        background: 'rgba(255,255,255,0.1)',
                          padding: '2px 8px',
                          borderRadius: '4px'
                        }}>
                          {tipo || 'outros'}: {count}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

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
                  <div className="problems-header">
                    <h3>🔴 Pratos com Nome "Unknown" (Crítico)</h3>
                    <button 
                      className="batch-fix-btn"
                      onClick={() => batchFixDishes('unknown_names')}
                      disabled={auditLoading}
                    >
                      🤖 Corrigir com IA (10 pratos)
                    </button>
                  </div>
                  <div className="problems-list">
                    {auditData.problems.unknown_names.map((p, i) => (
                      <div key={i} className="problem-item critical">
                        <span className="problem-slug">{p.slug}</span>
                        <span className="problem-issue">{p.issue}</span>
                        <button 
                          className="ai-fix-btn"
                          onClick={() => fixDishWithAI(p.slug)}
                          disabled={fixingSlug === p.slug}
                        >
                          {fixingSlug === p.slug ? '⏳' : '🤖'}
                        </button>
                        <button 
                          className="edit-btn"
                          onClick={() => {
                            const dish = dishes.find(d => d.slug === p.slug);
                            if (dish) setEditingDish(dish);
                            
                          }}
                        >
                          ✏️
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {auditData.problems.category_conflicts.length > 0 && (
                <div className="audit-problems">
                  <div className="problems-header">
                    <h3>🔴 Conflitos de Categoria (Crítico)</h3>
                    <button 
                      className="batch-fix-btn"
                      onClick={() => batchFixDishes('category_conflicts')}
                      disabled={auditLoading}
                    >
                      🤖 Corrigir com IA (10 pratos)
                    </button>
                  </div>
                  <div className="problems-list">
                    {auditData.problems.category_conflicts.map((p, i) => (
                      <div key={i} className="problem-item critical">
                        <span className="problem-slug">{p.nome}</span>
                        <span className="problem-issue">{p.issue}</span>
                        <button 
                          className="ai-fix-btn"
                          onClick={() => fixDishWithAI(p.slug)}
                          disabled={fixingSlug === p.slug}
                        >
                          {fixingSlug === p.slug ? '⏳' : '🤖'}
                        </button>
                        <button 
                          className="edit-btn"
                          onClick={() => {
                            const dish = dishes.find(d => d.slug === p.slug);
                            if (dish) setEditingDish(dish);
                            
                          }}
                        >
                          ✏️
                        </button>
                        <button 
                          className="delete-btn small"
                          onClick={() => deleteDish(p.slug, p.nome)}
                          title="Excluir prato"
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {auditData.problems.empty_nutrition.length > 0 && (
                <div className="audit-problems">
                  <div className="problems-header">
                    <h3>🟡 Pratos sem Informação Nutricional ({auditData.problems.empty_nutrition.length})</h3>
                    <button 
                      className="batch-fix-btn"
                      onClick={() => batchFixDishes('empty_nutrition')}
                      disabled={auditLoading}
                    >
                      🤖 Preencher com IA (10 pratos)
                    </button>
                  </div>
                  <p className="problems-note">Estes pratos não mostram calorias corretamente.</p>
                  <div className="problems-list scrollable">
                    {auditData.problems.empty_nutrition.slice(0, 20).map((p, i) => (
                      <div key={i} className="problem-item warning">
                        <span className="problem-slug">{p.nome || p.slug}</span>
                        <button 
                          className="ai-fix-btn small"
                          onClick={() => fixDishWithAI(p.slug)}
                          disabled={fixingSlug === p.slug}
                        >
                          {fixingSlug === p.slug ? '⏳' : '🤖'}
                        </button>
                        <button 
                          className="edit-btn small"
                          onClick={() => {
                            const dish = dishes.find(d => d.slug === p.slug);
                            if (dish) setEditingDish(dish);
                            
                          }}
                        >
                          ✏️
                        </button>
                        <button 
                          className="delete-btn small"
                          onClick={() => deleteDish(p.slug, p.nome)}
                          title="Excluir prato"
                        >
                          🗑️
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
                  <div className="problems-header">
                    <h3>🔴 Pratos sem dish_info.json ({auditData.problems.missing_info_file.length})</h3>
                    <button 
                      className="batch-fix-btn"
                      onClick={() => batchFixDishes('missing_info_file')}
                      disabled={auditLoading}
                    >
                      🤖 Criar com IA (10 pratos)
                    </button>
                  </div>
                  <p className="problems-note">Estes pratos precisam ser configurados.</p>
                  <div className="problems-list scrollable">
                    {auditData.problems.missing_info_file.slice(0, 20).map((p, i) => (
                      <div key={i} className="problem-item critical">
                        <span className="problem-slug">{p.slug}</span>
                        <button 
                          className="ai-fix-btn small"
                          onClick={() => fixDishWithAI(p.slug)}
                          disabled={fixingSlug === p.slug}
                        >
                          {fixingSlug === p.slug ? '⏳' : '🤖'}
                        </button>
                      </div>
                    ))}
                    {auditData.problems.missing_info_file.length > 20 && (
                      <p className="more-items">...e mais {auditData.problems.missing_info_file.length - 20} pratos</p>
                    )}
                  </div>
                </div>
              )}

              {/* Sem ingredientes */}
              {auditData.problems.missing_ingredients && auditData.problems.missing_ingredients.length > 0 && (
                <div className="audit-problems">
                  <div className="problems-header">
                    <h3>🟡 Pratos sem Ingredientes ({auditData.problems.missing_ingredients.length})</h3>
                  </div>
                  <div className="problems-list scrollable">
                    {auditData.problems.missing_ingredients.slice(0, 30).map((p, i) => (
                      <div key={i} className="problem-item warning">
                        <span className="problem-slug">{p.nome || p.slug}</span>
                        <button 
                          className="edit-btn small"
                          onClick={() => {
                            const dish = dishes.find(d => d.slug === p.slug);
                            if (dish) setEditingDish(dish);
                            
                          }}
                        >
                          ✏️
                        </button>
                        <button 
                          className="delete-btn small"
                          onClick={() => deleteDish(p.slug, p.nome)}
                          title="Excluir prato"
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                    {auditData.problems.missing_ingredients.length > 30 && (
                      <p className="more-items">...e mais {auditData.problems.missing_ingredients.length - 30} pratos</p>
                    )}
                  </div>
                </div>
              )}

              {/* Alérgenos incorretos */}
              {auditData.problems.allergen_conflicts && auditData.problems.allergen_conflicts.length > 0 && (
                <div className="audit-problems">
                  <div className="problems-header">
                    <h3>🟠 Alérgenos Incorretos ({auditData.problems.allergen_conflicts.length})</h3>
                  </div>
                  <div className="problems-list scrollable">
                    {auditData.problems.allergen_conflicts.slice(0, 30).map((p, i) => (
                      <div key={i} className="problem-item warning">
                        <span className="problem-slug">{p.nome || p.slug}</span>
                        <span className="problem-issue">{p.issue}</span>
                        <button 
                          className="edit-btn small"
                          onClick={() => {
                            const dish = dishes.find(d => d.slug === p.slug);
                            if (dish) setEditingDish(dish);
                            
                          }}
                        >
                          ✏️
                        </button>
                        <button 
                          className="delete-btn small"
                          onClick={() => deleteDish(p.slug, p.nome)}
                          title="Excluir prato"
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                    {auditData.problems.allergen_conflicts.length > 30 && (
                      <p className="more-items">...e mais {auditData.problems.allergen_conflicts.length - 30} pratos</p>
                    )}
                  </div>
                </div>
              )}

              {/* Sem descrição */}
              {auditData.problems.missing_description && auditData.problems.missing_description.length > 0 && (
                <div className="audit-problems">
                  <div className="problems-header">
                    <h3>🔵 Pratos sem Descrição ({auditData.problems.missing_description.length})</h3>
                  </div>
                  <div className="problems-list scrollable">
                    {auditData.problems.missing_description.slice(0, 30).map((p, i) => (
                      <div key={i} className="problem-item info">
                        <span className="problem-slug">{p.nome || p.slug}</span>
                        <button 
                          className="edit-btn small"
                          onClick={() => {
                            const dish = dishes.find(d => d.slug === p.slug);
                            if (dish) setEditingDish(dish);
                            
                          }}
                        >
                          ✏️
                        </button>
                        <button 
                          className="delete-btn small"
                          onClick={() => deleteDish(p.slug, p.nome)}
                          title="Excluir prato"
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                    {auditData.problems.missing_description.length > 30 && (
                      <p className="more-items">...e mais {auditData.problems.missing_description.length - 30} pratos</p>
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
              <div className="modal-header-actions">
                <button 
                  className="delete-dish-btn"
                  onClick={() => {
                    deleteDish(editingDish.slug, editingDish.nome);
                    setEditingDish(null);
                  }}
                  title="Excluir este prato"
                >
                  🗑️ Excluir Prato
                </button>
                <button className="close-btn" onClick={() => setEditingDish(null)}>✕</button>
              </div>
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
                      ingredientes: e.target.value.split('\n')
                    })}
                    rows={6}
                    style={{ minHeight: '120px', width: '100%' }}
                    placeholder="Digite um ingrediente por linha..."
                  />
                  <button 
                    className="ia-review-btn"
                    onClick={revisarComIA}
                    disabled={revisandoIA}
                    style={{
                      marginTop: '8px',
                      padding: '8px 16px',
                      backgroundColor: revisandoIA ? '#666' : '#4CAF50',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: revisandoIA ? 'wait' : 'pointer',
                      fontSize: '14px'
                    }}
                  >
                    {revisandoIA ? '⏳ Analisando...' : '🤖 Revisar com IA'}
                  </button>
                  <small style={{ display: 'block', marginTop: '4px', color: '#888' }}>
                    A IA sugere categoria, benefícios e riscos baseado nos ingredientes
                  </small>
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

                <div className="form-group checkbox-group allergens-group">
                  <label className="allergens-label">⚠️ Alérgenos:</label>
                  <div className="allergens-grid">
                    <label>
                      <input 
                        type="checkbox"
                        checked={editingDish.contem_gluten || false}
                        onChange={e => setEditingDish({...editingDish, contem_gluten: e.target.checked})}
                      />
                      🌾 Glúten
                    </label>
                    <label>
                      <input 
                        type="checkbox"
                        checked={editingDish.contem_lactose || false}
                        onChange={e => setEditingDish({...editingDish, contem_lactose: e.target.checked})}
                      />
                      🥛 Lactose
                    </label>
                    <label>
                      <input 
                        type="checkbox"
                        checked={editingDish.contem_ovo || false}
                        onChange={e => setEditingDish({...editingDish, contem_ovo: e.target.checked})}
                      />
                      🥚 Ovo
                    </label>
                    <label>
                      <input 
                        type="checkbox"
                        checked={editingDish.contem_castanhas || false}
                        onChange={e => setEditingDish({...editingDish, contem_castanhas: e.target.checked})}
                      />
                      🥜 Castanhas
                    </label>
                    <label>
                      <input 
                        type="checkbox"
                        checked={editingDish.contem_frutos_mar || false}
                        onChange={e => setEditingDish({...editingDish, contem_frutos_mar: e.target.checked})}
                      />
                      🦐 Frutos do Mar
                    </label>
                    <label>
                      <input 
                        type="checkbox"
                        checked={editingDish.contem_soja || false}
                        onChange={e => setEditingDish({...editingDish, contem_soja: e.target.checked})}
                      />
                      🫘 Soja
                    </label>
                  </div>
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
