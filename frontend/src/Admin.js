import React, { useState, useEffect, useCallback } from 'react';
import './Admin.css';

const API = '/api';
const BUILD_VERSION = 'v3.28-' + Date.now();

// XHR direto - contorna o wrapper fetch da plataforma Emergent
function xhrGet(url) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.timeout = 20000;
    xhr.onload = () => resolve({
      ok: xhr.status >= 200 && xhr.status < 300,
      status: xhr.status,
      json: () => Promise.resolve(JSON.parse(xhr.responseText)),
      text: () => Promise.resolve(xhr.responseText)
    });
    xhr.onerror = () => reject(new Error('Network error'));
    xhr.ontimeout = () => reject(new Error('Timeout'));
    xhr.send();
  });
}

function xhrPost(url, body) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.timeout = 30000;
    xhr.onload = () => resolve({
      ok: xhr.status >= 200 && xhr.status < 300,
      status: xhr.status,
      json: () => Promise.resolve(JSON.parse(xhr.responseText)),
      text: () => Promise.resolve(xhr.responseText)
    });
    xhr.onerror = () => reject(new Error('Erro de rede ao mover'));
    xhr.ontimeout = () => reject(new Error('Timeout ao mover'));
    xhr.send(JSON.stringify(body));
  });
}

function xhrDelete(url) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('DELETE', url);
    xhr.timeout = 20000;
    xhr.onload = () => resolve({
      ok: xhr.status >= 200 && xhr.status < 300,
      status: xhr.status,
      json: () => Promise.resolve(JSON.parse(xhr.responseText)),
      text: () => Promise.resolve(xhr.responseText)
    });
    xhr.onerror = () => reject(new Error('Erro de rede'));
    xhr.ontimeout = () => reject(new Error('Timeout'));
    xhr.send();
  });
}

// Retry com XHR para GET requests
async function retryFetch(url, options, retries = 2) {
  for (let i = 0; i <= retries; i++) {
    try {
      const res = await xhrGet(url);
      if (res.ok || i === retries) return res;
      await new Promise(r => setTimeout(r, 1000));
    } catch (err) {
      if (i === retries) throw err;
      await new Promise(r => setTimeout(r, 1000));
    }
  }
}

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
  // Métricas de Processamento
  const [metricsEnabled, setMetricsEnabled] = useState(false);
  const [metricsDate, setMetricsDate] = useState(new Date().toISOString().split('T')[0]);
  const [metricsData, setMetricsData] = useState(null);
  const [metricsLoading, setMetricsLoading] = useState(false);
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
  // Upload de fotos
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadFiles, setUploadFiles] = useState(null);
  const [uploadZipFile, setUploadZipFile] = useState(null);
  const [uploadDishName, setUploadDishName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [folderUploadStatus, setFolderUploadStatus] = useState(null);
  const [folderUploading, setFolderUploading] = useState(false);
  // Moderação
  const [moderationItems, setModerationItems] = useState([]);
  const [moderationLoading, setModerationLoading] = useState(false);
  const [moderationFilter, setModerationFilter] = useState('pending');
  const [correctingItemId, setCorrectingItemId] = useState(null);
  const [correctionName, setCorrectionName] = useState('');
  const [moderationPendingCount, setModerationPendingCount] = useState(0);
  // Calibração CLIP
  const [calibrationData, setCalibrationData] = useState(null);
  const [calibrationLoading, setCalibrationLoading] = useState(false);
  // Mover/Deletar imagens (substitui window.confirm/prompt bloqueados no iframe)
  const [moveImageState, setMoveImageState] = useState(null); // { idx, img, slug }
  const [moveDestination, setMoveDestination] = useState('');
  const [deleteImageState, setDeleteImageState] = useState(null); // { idx, img, slug }
  // Confirmação inline (substitui window.confirm bloqueado no iframe)
  const [pendingConfirm, setPendingConfirm] = useState(null); // { id, action, label }
  // Paginação
  const [dishesPage, setDishesPage] = useState(1);
  const DISHES_PER_PAGE = 30;
  // Notificação inline (substitui alert() bloqueado no iframe)
  const [notification, setNotification] = useState(null); // { message, type: 'success'|'error'|'info' }
  const notify = useCallback((message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  }, []);
  
  // Retorna true se a ação está pendente de confirmação, false se já confirmada
  const needsConfirm = (actionId) => {
    if (pendingConfirm && pendingConfirm.id === actionId) {
      return false; // Já confirmado, pode executar
    }
    setPendingConfirm({ id: actionId });
    setTimeout(() => setPendingConfirm(prev => prev?.id === actionId ? null : prev), 5000);
    return true; // Precisa confirmar
  };

  // Estado de erro global
  const [loadError, setLoadError] = useState(null);

  // Carregar dados essenciais na montagem
  useEffect(() => {
    loadDishes();
    loadStats();
    loadModerationCount();
  }, []);

  // Carregar dados ao trocar de aba
  useEffect(() => {
    if (activeTab === 'dishes') return;
    if (activeTab === 'novidades' && novidades.length === 0) loadNovidades();
    if (activeTab === 'premium' && premiumUsers.length === 0) loadPremiumUsers();
    if (activeTab === 'metricas') loadMetricsSetting();
    if (activeTab === 'custos' && !apiUsage) loadApiUsage();
    if (activeTab === 'upload') loadUploadStatus();
    if (activeTab === 'moderation') loadModerationQueue();
    if (activeTab === 'audit' && !auditData) runAudit();
    if (activeTab === 'calibration') loadCalibrationData();
  }, [activeTab]);

  // Apenas contagem de moderação (leve)
  const loadModerationCount = async () => {
    try {
      const res = await retryFetch(`${API}/admin/moderation-queue?status=pending`);
      if (res && res.ok) {
        const data = await res.json();
        if (data && data.ok) setModerationPendingCount(data.pending_count || 0);
      }
    } catch (e) { /* silent */ }
  };

  const loadUploadStatus = async () => {
    try {
      const res = await retryFetch(`${API}/upload/status`);
      if (!res.ok) return;
      const data = await res.json();
      setUploadStatus(data);
    } catch (e) {
      console.error('Erro ao carregar status:', e);
    }
  };

  const handleUploadPhotos = async () => {
    if (!uploadDishName.trim() || !uploadFiles?.length) return;
    setUploading(true);
    setUploadResult(null);
    setUploadProgress(0);
    
    try {
      const formData = new FormData();
      formData.append('dish_name', uploadDishName.trim());
      for (let f of uploadFiles) {
        formData.append('files', f);
      }
      
      const res = await fetch(`${API}/upload/photos`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      setUploadResult(data);
      setUploadProgress(100);
      if (data.ok) {
        setUploadFiles(null);
        setUploadDishName('');
        loadUploadStatus();
      }
    } catch (e) {
      setUploadResult({ ok: false, error: e.message });
    }
    setUploading(false);
  };

  const handleUploadZip = async () => {
    if (!uploadZipFile) return;
    setUploading(true);
    setUploadResult(null);
    setUploadProgress(0);
    
    try {
      const formData = new FormData();
      formData.append('file', uploadZipFile);
      
      const res = await fetch(`${API}/upload/zip`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      setUploadResult(data);
      setUploadProgress(100);
      if (data.ok) {
        setUploadZipFile(null);
        loadUploadStatus();
      }
    } catch (e) {
      setUploadResult({ ok: false, error: e.message });
    }
    setUploading(false);
  };

  const handleFolderUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    
    // Group files by subfolder
    const dishes = {};
    for (const file of files) {
      const path = file.webkitRelativePath || file.name;
      const parts = path.split('/');
      if (parts.length < 2) continue;
      const dishName = parts[parts.length - 2]; // subfolder name
      const ext = file.name.split('.').pop().toLowerCase();
      if (!['jpg','jpeg','png','webp'].includes(ext)) continue;
      if (!dishes[dishName]) dishes[dishName] = [];
      dishes[dishName].push(file);
    }
    
    const dishNames = Object.keys(dishes);
    if (!dishNames.length) {
      setUploadResult({ ok: false, error: 'Nenhuma subpasta com fotos encontrada' });
      return;
    }
    
    setFolderUploading(true);
    setFolderUploadStatus({ total: dishNames.length, done: 0, current: '', results: [] });
    setUploadResult(null);
    
    let totalSaved = 0;
    let totalErrors = 0;
    
    for (let i = 0; i < dishNames.length; i++) {
      const dishName = dishNames[i];
      const dishFiles = dishes[dishName];
      setFolderUploadStatus(prev => ({ ...prev, done: i, current: dishName }));
      
      // Upload in batches of 10
      for (let j = 0; j < dishFiles.length; j += 10) {
        const batch = dishFiles.slice(j, j + 10);
        const formData = new FormData();
        formData.append('dish_name', dishName);
        for (const f of batch) formData.append('files', f);
        
        try {
          const res = await fetch(`${API}/upload/photos`, { method: 'POST', body: formData });
          const data = await res.json();
          if (data.ok) {
            totalSaved += data.saved || 0;
            totalErrors += (data.errors?.length || 0);
          }
        } catch (err) {
          totalErrors += batch.length;
        }
      }
      
      setFolderUploadStatus(prev => ({
        ...prev,
        done: i + 1,
        results: [...prev.results, { dish: dishName, count: dishFiles.length }]
      }));
    }
    
    setFolderUploading(false);
    setFolderUploadStatus(null);
    setUploadResult({
      ok: true,
      total_saved: totalSaved,
      dishes: dishes,
      folder_count: dishNames.length,
      errors: totalErrors > 0 ? [`${totalErrors} erro(s) no total`] : []
    });
    loadUploadStatus();
    e.target.value = '';
  };

  const loadMetricsSetting = async () => {
    try {
      const res = await retryFetch(`${API}/admin/settings`);
      if (!res.ok) return;
      const data = await res.json();
      if (data && data.ok) setMetricsEnabled(!!data.ENABLE_PROCESSING_METRICS);
    } catch (e) { /* silent */ }
  };

  // ═══ MODERAÇÃO ═══
  const loadModerationQueue = async (filter) => {
    const statusFilter = filter || moderationFilter;
    setModerationLoading(true);
    try {
      const res = await retryFetch(`${API}/admin/moderation-queue?status=${statusFilter}`);
      if (!res.ok) { setModerationLoading(false); return; }
      const data = await res.json();
      if (data && data.ok) {
        setModerationItems(data.items || []);
        setModerationPendingCount(data.pending_count || 0);
      }
    } catch (e) { /* silent */ }
    setModerationLoading(false);
  };

  const [confirmAction, setConfirmAction] = useState(null); // {type: 'approve'|'reject', itemId: string}

  // Carregar dados de calibração CLIP
  const loadCalibrationData = async () => {
    setCalibrationLoading(true);
    try {
      const res = await retryFetch(`${API}/ai/calibration`);
      if (!res.ok) { setCalibrationLoading(false); return; }
      const data = await res.json();
      if (data && data.ok) {
        setCalibrationData(data);
      }
    } catch (e) { /* silent */ }
    setCalibrationLoading(false);
  };

  // Deletar amostra de calibração
  const deleteCalibrationSample = async (sampleId) => {
    try {
      const res = await xhrDelete(`${API}/ai/calibration/${sampleId}`);
      const data = await res.json();
      if (data.ok) {
        notify('Amostra deletada', 'success');
        loadCalibrationData();
      } else {
        notify('Erro ao deletar: ' + (data.error || data.message), 'error');
      }
    } catch (e) {
      notify('Erro: ' + e.message, 'error');
    }
  };

  const approveModerationItem = async (itemId) => {
    try {
      const res = await fetch(`${API}/admin/moderation/${itemId}/approve`, { method: 'POST' });
      const data = await res.json();
      if (data.ok) {
        setConfirmAction(null);
        loadModerationQueue();
      } else {
        notify('Erro: ' + data.error, 'error');
      }
    } catch (e) {
      notify('Erro: ' + e.message, 'error');
    }
  };

  const rejectModerationItem = async (itemId) => {
    try {
      const res = await fetch(`${API}/admin/moderation/${itemId}/reject`, { method: 'POST' });
      const data = await res.json();
      if (data.ok) {
        setConfirmAction(null);
        loadModerationQueue();
      } else {
        notify('Erro: ' + data.error, 'error');
      }
    } catch (e) {
      notify('Erro: ' + e.message, 'error');
    }
  };

  const correctModerationItem = async (itemId) => {
    if (!correctionName.trim()) {
      notify('Digite o nome correto do prato', 'error');
      return;
    }
    try {
      const res = await fetch(`${API}/admin/moderation/${itemId}/correct`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correct_dish_name: correctionName.trim() })
      });
      const data = await res.json();
      if (data.ok) {
        setCorrectingItemId(null);
        setCorrectionName('');
        loadModerationQueue();
      } else {
        notify('Erro: ' + data.error, 'error');
      }
    } catch (e) {
      notify('Erro: ' + e.message, 'error');
    }
  };

  const toggleMetrics = async () => {
    try {
      const newValue = !metricsEnabled;
      const res = await fetch(`${API}/admin/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: 'ENABLE_PROCESSING_METRICS', value: newValue })
      });
      const data = await res.json();
      if (data.ok) setMetricsEnabled(newValue);
    } catch (e) { console.error('Erro ao alterar métrica:', e); }
  };

  const loadMetricsReport = async () => {
    setMetricsLoading(true);
    try {
      const res = await retryFetch(`${API}/admin/processing-metrics?date=${metricsDate}`);
      if (!res.ok) return;
      const data = await res.json();
      if (data.ok) setMetricsData(data);
    } catch (e) { console.error('Erro ao carregar métricas:', e); }
    finally { setMetricsLoading(false); }
  };

  const loadDishes = async () => {
    try {
      const res = await retryFetch(`${API}/admin/dishes-full`);
      if (!res.ok) { setLoading(false); return; }
      const data = await res.json();
      if (data.ok) setDishes(data.dishes || []);
    } catch (e) {
      console.error('Erro ao carregar pratos:', e);
    }
    setLoading(false);
  };

  const loadPremiumUsers = async () => {
    try {
      const res = await retryFetch(`${API}/admin/premium/users`);
      if (!res.ok) return;
      const data = await res.json();
      if (data && data.ok) setPremiumUsers(data.users || []);
    } catch (e) { /* silent */ }
  };

  // Estado para uso de APIs
  const [apiUsage, setApiUsage] = useState(null);

  const loadApiUsage = async () => {
    try {
      const res = await retryFetch(`${API}/admin/api-usage`);
      if (!res.ok) return;
      const data = await res.json();
      if (data && data.ok) setApiUsage(data);
    } catch (e) { /* silent */ }
  };

  const liberarPremium = async () => {
    if (!premiumNome.trim()) {
      notify('Digite o nome do usuário', 'error');
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
        notify(`✅ Premium liberado para ${premiumNome} por ${premiumDias} dias!`, 'success');
        setPremiumNome('');
        loadPremiumUsers();
      } else {
        notify('Erro: ' + data.error, 'error');
      }
    } catch (e) {
      notify('Erro: ' + e.message, 'error');
    }
  };

  const bloquearPremium = async (nome) => {
    if (needsConfirm(`block-premium-${nome}`)) return;
    setPendingConfirm(null);
    try {
      const formData = new FormData();
      formData.append('nome', nome);
      
      const res = await fetch(`${API}/admin/premium/bloquear`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.ok) {
        notify(`✅ Premium bloqueado para ${nome}`, 'success');
        loadPremiumUsers();
      } else {
        notify('Erro: ' + data.error, 'error');
      }
    } catch (e) {
      notify('Erro: ' + e.message, 'error');
    }
  };

  // Auditoria de dados
  const runAudit = async () => {
    setAuditLoading(true);
    try {
      const res = await retryFetch(`${API}/admin/audit`);
      const data = await res.json();
      if (data.ok) {
        setAuditData(data);
      } else {
        notify('Erro na auditoria: ' + data.error, 'error');
      }
    } catch (e) {
      notify('Erro: ' + e.message, 'error');
    } finally {
      setAuditLoading(false);
    }
  };

  // Corrigir prato individual com IA
  const fixDishWithAI = async (slug) => {
    setFixingSlug(slug);
    try {
      const res = await fetch(`${API}/admin/audit/fix-single/${encodeURIComponent(slug)}`, { method: 'POST' });
      const data = await res.json();
      if (data.ok) {
        notify(`✅ Prato "${slug}" corrigido com sucesso!`, 'success');
        runAudit(); // Atualizar auditoria
        loadDishes(); // Atualizar lista
      } else {
        notify('Erro: ' + data.error, 'error');
      }
    } catch (e) {
      notify('Erro: ' + e.message, 'error');
    } finally {
      setFixingSlug(null);
    }
  };

  // EXCLUIR PRATO
  const deleteDish = async (slug, nome) => {
    if (needsConfirm(`delete-dish-${slug}`)) return;
    setPendingConfirm(null);
    
    try {
      const res = await fetch(`${API}/admin/dishes/${encodeURIComponent(slug)}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.ok) {
        loadDishes();
        runAudit();
      }
    } catch (e) {
      console.error('Erro ao excluir:', e);
    }
  };

  // CONSOLIDAR DUPLICADOS (sem créditos)
  const consolidateDuplicates = async () => {
    if (needsConfirm('consolidate')) return;
    setPendingConfirm(null);
    
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
    if (needsConfirm('update-all')) return;
    setPendingConfirm(null);
    
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
      notify('Nenhum prato com ingredientes para revisar', 'info');
      return;
    }
    
    const qtd = Math.min(pratosComIngredientes.length, 50);
    if (needsConfirm('review-ia')) return;
    setPendingConfirm(null);
    
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
      notify('Nenhum prato para corrigir', 'info');
      return;
    }
    
    if (needsConfirm('batch-fix-ia')) return;
    setPendingConfirm(null);
    
    setAuditLoading(true);
    try {
      const res = await fetch(`${API}/admin/audit/batch-fix`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slugs })
      });
      const data = await res.json();
      if (data.ok) {
        notify(`✅ Corrigidos: ${data.fixed?.length || 0}\n❌ Falhas: ${data.failed?.length || 0}\n⏭️ Pulados: ${data.skipped?.length || 0}`, 'success');
        runAudit();
        loadDishes();
      } else {
        notify('Erro: ' + data.error, 'error');
      }
    } catch (e) {
      notify('Erro: ' + e.message, 'error');
    } finally {
      setAuditLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const res = await retryFetch(`${API}/ai/status`);
      if (!res.ok) return;
      const data = await res.json();
      if (data) setStats(data);
    } catch (e) { /* silent */ }
  };

  const loadNovidades = async () => {
    try {
      const res = await retryFetch(`${API}/novidades`);
      if (!res.ok) return;
      const data = await res.json();
      if (data && data.ok) setNovidades(data.novidades || []);
    } catch (e) { /* silent */ }
  };

  const saveNovidade = async () => {
    if (!novidadeForm.dish_slug || !novidadeForm.titulo || !novidadeForm.mensagem) {
      notify('Preencha todos os campos obrigatórios', 'error');
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
        notify('✅ Novidade salva!', 'success');
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
        notify('Erro: ' + data.error, 'error');
      }
    } catch (e) {
      notify('Erro ao salvar: ' + e.message, 'error');
    }
  };

  const deleteNovidade = async (slug) => {
    if (needsConfirm(`delete-novidade-${slug}`)) return;
    setPendingConfirm(null);
    try {
      const res = await fetch(`${API}/admin/novidades/${encodeURIComponent(slug)}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.ok) {
        notify('✅ Novidade removida!', 'success');
        loadNovidades();
      }
    } catch (e) {
      notify('Erro ao remover: ' + e.message, 'error');
    }
  };

  const saveDish = async (dish) => {
    try {
      // Remover campos que não devem ser enviados ao backend
      const { all_images, first_image, image_count, ...dishData } = dish;
      
      const res = await fetch(`${API}/admin/dishes/${encodeURIComponent(dish.slug)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dishData)
      });
      
      // Verificar se a resposta é válida antes de parsear
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch (parseError) {
        console.error('Erro ao parsear resposta:', text);
        notify('Erro ao processar resposta do servidor', 'error');
        return;
      }
      
      if (data.ok) {
        notify('✅ Prato salvo!', 'success');
        setEditingDish(null);
        loadDishes();
      } else {
        notify('Erro: ' + (data.error || 'Erro desconhecido'), 'error');
      }
    } catch (e) {
      console.error('Erro ao salvar:', e);
      notify('Erro ao salvar: ' + e.message, 'error');
    }
  };

  // Criar novo prato com upload de foto
  const createNewDishAdmin = async () => {
    if (!newDishName.trim()) {
      notify('Digite o nome do prato', 'error');
      return;
    }
    if (!newDishFile) {
      notify('Selecione uma foto do prato', 'error');
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
        notify(`✅ Prato "${newDishName}" criado com sucesso!\n\n💰 Créditos usados: 0\n\n📝 Edite os detalhes na lista de pratos.`, 'success');
        setShowNewDishModal(false);
        setNewDishName('');
        setNewDishFile(null);
        loadDishes();
        loadStats();
      } else {
        notify('Erro: ' + data.error, 'error');
      }
    } catch (e) {
      notify('Erro ao criar: ' + e.message, 'error');
    } finally {
      setCreatingDish(false);
    }
  };

  // Revisar prato com TACO (ZERO CRÉDITOS)
  const revisarComTACO = async () => {
    if (!editingDish) return;
    
    const ingredientes = editingDish.ingredientes || [];
    if (ingredientes.length === 0 || (ingredientes.length === 1 && !ingredientes[0].trim())) {
      notify('⚠️ Adicione os ingredientes primeiro!', 'error');
      return;
    }
    
    setRevisandoIA(true);
    try {
      const res = await fetch(`${API}/admin/revisar-prato-taco`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome: editingDish.nome,
          ingredientes: ingredientes.filter(i => i.trim())
        })
      });
      
      const data = await res.json();
      
      if (data.ok) {
        const n = data.nutricao || {};
        
        // Mostrar resultado
        const msg = `📊 Dados da Tabela TACO (ZERO CRÉDITOS):\n\n` +
          `📂 Categoria: ${data.categoria}\n\n` +
          `📊 Nutrição (por 100g):\n` +
          `  🔥 Calorias: ${n.calorias || 'N/A'}\n` +
          `  💪 Proteínas: ${n.proteinas || 'N/A'}\n` +
          `  🍞 Carboidratos: ${n.carboidratos || 'N/A'}\n` +
          `  🧈 Gorduras: ${n.gorduras || 'N/A'}\n` +
          `  🥬 Fibras: ${n.fibras || 'N/A'}\n\n` +
          `Deseja aplicar estes dados?`;
        
        // Auto-aplicar dados TACO (usuario confirma clicando Salvar)
        {
          setEditingDish({
            ...editingDish,
            categoria: data.categoria,
            nutricao: {
              calorias: n.calorias || '',
              proteinas: n.proteinas || '',
              carboidratos: n.carboidratos || '',
              gorduras: n.gorduras || '',
              fibras: n.fibras || ''
            },
            contem_gluten: data.contem_gluten || false,
            contem_lactose: data.contem_lactose || false,
            contem_ovo: data.contem_ovo || false,
            contem_frutos_mar: data.contem_frutos_mar || false,
            contem_castanhas: data.contem_castanhas || false
          });
        }
      } else {
        notify('❌ Erro: ' + (data.error || 'Não foi possível calcular'), 'error');
      }
    } catch (e) {
      console.error('Erro ao buscar TACO:', e);
      notify('❌ Erro: ' + e.message, 'error');
    } finally {
      setRevisandoIA(false);
    }
  };

  // Revisar prato com IA (Gemini Flash) - GASTA CRÉDITOS
  const revisarComIA = async () => {
    if (!editingDish) return;
    
    const ingredientes = editingDish.ingredientes || [];
    if (ingredientes.length === 0 || (ingredientes.length === 1 && !ingredientes[0].trim())) {
      notify('⚠️ Adicione os ingredientes primeiro para a IA analisar!', 'error');
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
        
        // Auto-aplicar sugestões da IA (usuario confirma clicando Salvar)
        {
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
        }
      } else {
        notify('❌ Erro: ' + (data.error || 'Não foi possível analisar'), 'error');
      }
    } catch (e) {
      console.error('Erro ao revisar com IA:', e);
      notify('❌ Erro ao conectar com IA: ' + e.message, 'error');
    } finally {
      setRevisandoIA(false);
    }
  };

  const reindex = async () => {
    if (needsConfirm('reindex')) return;
    setPendingConfirm(null);
    setLoading(true);
    try {
      // Iniciar reconstrução em background
      const res = await fetch(`${API}/ai/reindex-background?max_per_dish=10`, { method: 'POST' });
      const data = await res.json();
      
      if (!data.ok) {
        throw new Error(data.error || 'Erro ao iniciar');
      }
      
      notify('⏳ Reconstrução iniciada em background!\n\nAguarde 2-3 minutos e clique em "Verificar Status".', 'info');
      
      // Polling para verificar status
      const checkStatus = async () => {
        try {
          const statusRes = await fetch(`${API}/ai/reindex-status`);
          const statusData = await statusRes.json();
          
          if (statusData.completed) {
            notify(`✅ Reindexação concluída!\n\n${statusData.stats?.total_dishes || '?'} pratos\n${statusData.stats?.total_images || '?'} imagens`, 'success');
            loadStats();
            loadDishes();
            setLoading(false);
          } else if (statusData.in_progress) {
            // Continuar verificando
            setTimeout(checkStatus, 5000);
          } else {
            setLoading(false);
          }
        } catch (e) {
          setLoading(false);
        }
      };
      
      // Começar a verificar após 10 segundos
      setTimeout(checkStatus, 10000);
      
    } catch (e) {
      notify('Erro: ' + e.message, 'error');
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
      {/* Versao visivel para debug */}
      <div data-testid="build-version" style={{position:'fixed',bottom:'4px',right:'8px',zIndex:9999,fontSize:'10px',color:'#666',opacity:0.6}}>{BUILD_VERSION}</div>
      {/* Notificação inline (substitui alert bloqueado no iframe) */}
      {notification && (
        <div 
          data-testid="admin-notification"
          onClick={() => setNotification(null)}
          style={{
            position: 'fixed', top: '16px', right: '16px', zIndex: 10000,
            padding: '12px 20px', borderRadius: '8px', maxWidth: '400px',
            color: '#fff', cursor: 'pointer', fontSize: '14px', lineHeight: '1.4',
            boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
            background: notification.type === 'success' ? '#16a34a' : 
                       notification.type === 'error' ? '#dc2626' : '#2563eb',
            animation: 'slideIn 0.3s ease-out'
          }}
        >
          {notification.message}
        </div>
      )}
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
          onClick={() => { setActiveTab('audit'); }}
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
          onClick={() => { setActiveTab('custos'); }}
        >
          Custos API
        </button>
        <button 
          className={`tab-btn ${activeTab === 'metricas' ? 'active' : ''}`}
          onClick={() => setActiveTab('metricas')}
          data-testid="tab-metricas"
        >
          Metricas
        </button>
        <button 
          className={`tab-btn ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => { setActiveTab('upload'); }}
          data-testid="tab-upload"
        >
          Upload Fotos
        </button>
        <button 
          className={`tab-btn ${activeTab === 'moderation' ? 'active' : ''}`}
          onClick={() => { setActiveTab('moderation'); }}
          data-testid="tab-moderation"
          style={moderationPendingCount > 0 ? { position: 'relative' } : {}}
        >
          Moderação
          {moderationPendingCount > 0 && (
            <span style={{
              position: 'absolute',
              top: '-4px',
              right: '-4px',
              background: '#ef4444',
              color: '#fff',
              borderRadius: '50%',
              width: '20px',
              height: '20px',
              fontSize: '11px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold'
            }}>{moderationPendingCount}</span>
          )}
        </button>
        <button 
          className={`tab-btn ${activeTab === 'calibration' ? 'active' : ''}`}
          onClick={() => { setActiveTab('calibration'); }}
          data-testid="tab-calibration"
        >
          Calibracao CLIP
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
            <span className="stat-value">{dishes.length}</span>
            <span className="stat-label">Pratos</span>
          </div>
          <div className="stat">
            <span className="stat-value">{stats.total_embeddings}</span>
            <span className="stat-label">Imagens IA</span>
          </div>
          <div className="stat">
            <span className="stat-value">{stats.total_dishes}</span>
            <span className="stat-label">Pratos IA</span>
          </div>
          <div className="stat">
            <span className="stat-value">{dishes.reduce((sum, d) => sum + (d.image_count || 0), 0)}</span>
            <span className="stat-label">Total Fotos</span>
          </div>
          <div className="stat">
            <span className={`stat-value ${stats.ready ? 'ready' : 'not-ready'}`}>
              {stats.ready ? '✅' : '⏳'}
            </span>
            <span className="stat-label">Status</span>
          </div>
          <button className="reindex-btn" onClick={reindex} disabled={loading}>
            {loading ? '⏳ Aguarde...' : '🔄 Aplicar Correções'}
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
            onChange={e => { setSearch(e.target.value); setDishesPage(1); }}
            className="search-input"
          />
          <select 
            value={filterCategory} 
            onChange={e => { setFilterCategory(e.target.value); setDishesPage(1); }}
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
        <div className="loading" style={{ textAlign: 'center', padding: '40px' }}>
          <p>Carregando...</p>
          <button 
            onClick={loadDishes}
            data-testid="retry-dishes"
            style={{ marginTop: '12px', padding: '8px 20px', background: '#10b981', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer' }}
          >
            Tentar Novamente
          </button>
        </div>
      ) : (
        <>
        <div className={`dishes-container ${viewMode}`}>
          {filteredDishes.slice(0, dishesPage * DISHES_PER_PAGE).map(dish => (
            <div key={dish.slug} className="dish-card-full" onClick={async () => {
              setEditingDish({...dish, all_images: null, _loading_images: true});
              try {
                const res = await retryFetch(`${API}/admin/dish-images-list/${encodeURIComponent(dish.slug)}`);
                const data = await res.json();
                if (data.ok) {
                  setEditingDish(prev => prev && prev.slug === dish.slug ? {...prev, all_images: data.images, image_count: data.count, _loading_images: false} : prev);
                }
              } catch(e) {
                setEditingDish(prev => prev ? {...prev, _loading_images: false, all_images: []} : prev);
              }
            }}>
              {/* Foto */}
              <div className="dish-photo">
                {dish.first_image ? (
                  <img loading="lazy" src={`${API}/admin/dish-image/${encodeURIComponent(dish.slug)}?thumb=1`} alt={dish.nome} />
                ) : (
                  <div className="no-photo">{dish.category_emoji || '🍽️'}</div>
                )}
                <span className="photo-count">{dish.image_count}</span>
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
                <button onClick={async (e) => {
                  e.stopPropagation();
                  setEditingDish({...dish, all_images: null, _loading_images: true});
                  try {
                    const res = await retryFetch(`${API}/admin/dish-images-list/${encodeURIComponent(dish.slug)}`);
                    const data = await res.json();
                    if (data.ok) {
                      setEditingDish(prev => prev && prev.slug === dish.slug ? {...prev, all_images: data.images, image_count: data.count, _loading_images: false} : prev);
                    }
                  } catch(err) {
                    setEditingDish(prev => prev ? {...prev, _loading_images: false, all_images: []} : prev);
                  }
                }}>
                  ✏️ Editar
                </button>
                <button 
                  className="delete-btn" 
                  onClick={(e) => { e.stopPropagation(); deleteDish(dish.slug); }}
                  style={pendingConfirm?.id === `delete-dish-${dish.slug}` ? { background: '#ff0000', color: '#fff', fontWeight: 'bold', borderRadius: '4px', padding: '2px 8px' } : {}}
                >
                  {pendingConfirm?.id === `delete-dish-${dish.slug}` ? 'CONFIRMAR?' : '🗑️'}
                </button>
              </div>
            </div>
          ))}
        </div>
        {/* Botão Carregar Mais */}
        {dishesPage * DISHES_PER_PAGE < filteredDishes.length && (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <button
              onClick={() => setDishesPage(p => p + 1)}
              data-testid="load-more-dishes"
              style={{ padding: '10px 30px', background: '#1e3a5f', color: '#fff', border: '1px solid #3b82f6', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' }}
            >
              Carregar Mais ({filteredDishes.length - dishesPage * DISHES_PER_PAGE} restantes)
            </button>
          </div>
        )}
        </>
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
                            if (dish) { setEditingDish(dish); }
                            else { notify('Prato nao encontrado no banco de dados. Verifique se o slug esta correto.', 'error'); }
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
                            if (dish) { setEditingDish(dish); }
                            else { notify('Prato nao encontrado no banco de dados. Verifique se o slug esta correto.', 'error'); }
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
                            if (dish) { setEditingDish(dish); }
                            else { notify('Prato nao encontrado no banco de dados. Verifique se o slug esta correto.', 'error'); }
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
                        <button 
                          className="edit-btn"
                          onClick={() => {
                            const dish = dishes.find(d => d.slug === p.slug);
                            if (dish) { setEditingDish(dish); }
                            else { notify('Prato nao encontrado no banco de dados. Verifique se o slug esta correto.', 'error'); }
                          }}
                        >
                          ✏️
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
                            if (dish) { setEditingDish(dish); }
                            else { notify('Prato nao encontrado no banco de dados. Verifique se o slug esta correto.', 'error'); }
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
                            if (dish) { setEditingDish(dish); }
                            else { notify('Prato nao encontrado no banco de dados. Verifique se o slug esta correto.', 'error'); }
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
                            if (dish) { setEditingDish(dish); }
                            else { notify('Prato nao encontrado no banco de dados. Verifique se o slug esta correto.', 'error'); }
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

      {/* Métricas de Processamento Tab */}
      {activeTab === 'metricas' && (
        <div className="metrics-section" data-testid="metrics-section">
          <h2>Metricas de Processamento</h2>
          
          <div className="metrics-toggle" data-testid="metrics-toggle-container">
            <label className="toggle-label">
              <span>Ativar Metricas de Processamento</span>
              <button 
                className={`toggle-btn ${metricsEnabled ? 'active' : ''}`}
                onClick={toggleMetrics}
                data-testid="metrics-toggle-btn"
              >
                {metricsEnabled ? 'ON' : 'OFF'}
              </button>
            </label>
            <p className="toggle-hint">
              {metricsEnabled 
                ? 'Metricas ativas. Cada identificacao sera registrada.' 
                : 'Metricas desativadas. Zero impacto na performance.'}
            </p>
          </div>

          <div className="metrics-report" data-testid="metrics-report">
            <h3>Relatorio</h3>
            <div className="metrics-controls">
              <input 
                type="date" 
                value={metricsDate} 
                onChange={e => setMetricsDate(e.target.value)}
                data-testid="metrics-date-input"
              />
              <button 
                className="save-btn" 
                onClick={loadMetricsReport} 
                disabled={metricsLoading}
                data-testid="metrics-load-btn"
              >
                {metricsLoading ? 'Carregando...' : 'Carregar Relatorio'}
              </button>
            </div>

            {metricsData && (
              <>
                <div className="metrics-summary" data-testid="metrics-summary">
                  <div className="metric-card">
                    <span className="metric-value">{metricsData.total}</span>
                    <span className="metric-label">Total</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">{metricsData.average_ms}</span>
                    <span className="metric-label">Media (ms)</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">{metricsData.min_ms}</span>
                    <span className="metric-label">Minimo (ms)</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">{metricsData.max_ms}</span>
                    <span className="metric-label">Maximo (ms)</span>
                  </div>
                </div>

                {metricsData.entries && metricsData.entries.length > 0 && (
                  <table className="metrics-table" data-testid="metrics-table">
                    <thead>
                      <tr>
                        <th>Horario</th>
                        <th>Prato</th>
                        <th>Score</th>
                        <th>Tempo (ms)</th>
                        <th>Engine</th>
                      </tr>
                    </thead>
                    <tbody>
                      {metricsData.entries.map((entry, idx) => (
                        <tr key={idx}>
                          <td>{new Date(entry.timestamp).toLocaleTimeString('pt-BR')}</td>
                          <td>{entry.dish_name}</td>
                          <td>{(entry.confidence_score * 100).toFixed(1)}%</td>
                          <td>{entry.processing_time_ms}</td>
                          <td>
                            <span className={`engine-badge ${entry.engine_used.toLowerCase().split(' ')[0]}`}>
                              {entry.engine_used}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}

                {metricsData.total === 0 && (
                  <p className="no-data">Nenhuma metrica registrada para esta data.</p>
                )}
              </>
            )}
          </div>
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

      {/* Upload de Fotos */}
      {activeTab === 'upload' && (
        <div className="upload-panel" data-testid="upload-panel">
          <h2>Upload de Fotos</h2>
          
          {/* Status do Dataset */}
          {uploadStatus && (
            <div style={{background:'#1a1a2e',borderRadius:'12px',padding:'20px',marginBottom:'24px'}}>
              <div style={{display:'flex',gap:'24px',flexWrap:'wrap'}}>
                <div style={{textAlign:'center'}}>
                  <div style={{fontSize:'28px',fontWeight:'bold',color:'#4ade80'}}>{uploadStatus.total_dishes}</div>
                  <div style={{fontSize:'13px',color:'#94a3b8'}}>Pratos</div>
                </div>
                <div style={{textAlign:'center'}}>
                  <div style={{fontSize:'28px',fontWeight:'bold',color:'#60a5fa'}}>{uploadStatus.total_images}</div>
                  <div style={{fontSize:'13px',color:'#94a3b8'}}>Imagens</div>
                </div>
                <div style={{textAlign:'center'}}>
                  <div style={{fontSize:'28px',fontWeight:'bold',color:'#f59e0b'}}>
                    {uploadStatus.total_dishes > 0 ? Math.round(uploadStatus.total_images / uploadStatus.total_dishes) : 0}
                  </div>
                  <div style={{fontSize:'13px',color:'#94a3b8'}}>Media/prato</div>
                </div>
              </div>
            </div>
          )}

          {/* PRINCIPAL: Upload de Pasta Inteira */}
          <div style={{background:'#1a1a2e',borderRadius:'12px',padding:'24px',marginBottom:'24px',border:'2px solid #4ade80'}}>
            <h3 style={{marginBottom:'8px',color:'#4ade80',fontSize:'18px'}}>Enviar pasta com subpastas</h3>
            <p style={{fontSize:'14px',color:'#94a3b8',marginBottom:'16px'}}>
              Selecione a pasta principal. Cada subpasta vira um prato automaticamente.<br/>
              <span style={{color:'#60a5fa'}}>Estrutura: MinhaPasta / NomePrato / foto1.jpg, foto2.jpg...</span>
            </p>
            <div style={{display:'flex',gap:'12px',alignItems:'center',flexWrap:'wrap'}}>
              <input
                data-testid="upload-folder-input"
                type="file"
                webkitdirectory=""
                directory=""
                multiple
                onChange={handleFolderUpload}
                disabled={folderUploading}
                style={{flex:'1',padding:'12px',borderRadius:'8px',border:'2px dashed #4ade80',background:'#0f172a',color:'#e2e8f0',fontSize:'14px',cursor:'pointer'}}
              />
            </div>
            
            {/* Progress */}
            {folderUploading && folderUploadStatus && (
              <div style={{marginTop:'16px'}}>
                <div style={{display:'flex',justifyContent:'space-between',marginBottom:'6px'}}>
                  <span style={{color:'#e2e8f0',fontSize:'14px'}}>
                    Enviando: <strong>{folderUploadStatus.current}</strong>
                  </span>
                  <span style={{color:'#94a3b8',fontSize:'14px'}}>
                    {folderUploadStatus.done}/{folderUploadStatus.total} pratos
                  </span>
                </div>
                <div style={{width:'100%',height:'8px',background:'#1e293b',borderRadius:'4px',overflow:'hidden'}}>
                  <div style={{
                    width:`${(folderUploadStatus.done / folderUploadStatus.total * 100)}%`,
                    height:'100%',
                    background:'linear-gradient(90deg, #4ade80, #60a5fa)',
                    borderRadius:'4px',
                    transition:'width 0.3s'
                  }}/>
                </div>
              </div>
            )}
          </div>

          {/* Upload ZIP */}
          <div style={{background:'#1a1a2e',borderRadius:'12px',padding:'20px',marginBottom:'24px'}}>
            <h3 style={{marginBottom:'8px',color:'#e2e8f0'}}>Ou enviar ZIP</h3>
            <p style={{fontSize:'13px',color:'#94a3b8',marginBottom:'12px'}}>
              ZIP com pastas: NomePrato/foto1.jpg...
            </p>
            <div style={{display:'flex',gap:'12px',alignItems:'flex-end',flexWrap:'wrap'}}>
              <div style={{flex:'1'}}>
                <input
                  data-testid="upload-zip-input"
                  type="file"
                  accept=".zip"
                  onChange={e => setUploadZipFile(e.target.files?.[0])}
                  style={{width:'100%',padding:'8px',borderRadius:'8px',border:'1px solid #334155',background:'#0f172a',color:'#e2e8f0',fontSize:'13px'}}
                />
              </div>
              <button
                data-testid="upload-zip-btn"
                onClick={handleUploadZip}
                disabled={uploading || !uploadZipFile}
                style={{padding:'10px 24px',borderRadius:'8px',border:'none',background: uploading ? '#475569' : '#60a5fa',color:'#fff',fontWeight:'bold',cursor: uploading ? 'wait' : 'pointer',whiteSpace:'nowrap'}}
              >
                {uploading ? 'Enviando...' : 'Enviar ZIP'}
              </button>
            </div>
          </div>

          {/* Upload de fotos para um prato */}
          <div style={{background:'#1a1a2e',borderRadius:'12px',padding:'20px',marginBottom:'24px',border:'1px solid #334155'}}>
            <h3 style={{color:'#e2e8f0',marginBottom:'12px',fontSize:'16px'}}>Enviar fotos para um prato</h3>
            <div style={{marginTop:'12px',display:'flex',gap:'12px',alignItems:'flex-end',flexWrap:'wrap'}}>
              <div style={{flex:'1',minWidth:'200px'}}>
                <label style={{display:'block',fontSize:'13px',color:'#94a3b8',marginBottom:'4px'}}>Nome do Prato (exato como na pasta)</label>
                <input
                  data-testid="upload-dish-name"
                  value={uploadDishName}
                  onChange={e => setUploadDishName(e.target.value)}
                  placeholder="Ex: Arroz Branco, Feijao Preto..."
                  list="dish-names-list"
                  style={{width:'100%',padding:'10px 12px',borderRadius:'8px',border:'1px solid #334155',background:'#0f172a',color:'#e2e8f0',fontSize:'14px'}}
                />
                <datalist id="dish-names-list">
                  {uploadStatus?.dishes && Object.keys(uploadStatus.dishes).sort().map(d => (
                    <option key={d} value={d} />
                  ))}
                </datalist>
              </div>
              <div style={{flex:'1',minWidth:'200px'}}>
                <input
                  data-testid="upload-files-input"
                  type="file"
                  multiple
                  accept="image/jpeg,image/png,image/webp"
                  onChange={e => setUploadFiles(e.target.files)}
                  style={{width:'100%',padding:'8px',borderRadius:'8px',border:'1px solid #334155',background:'#0f172a',color:'#e2e8f0',fontSize:'13px'}}
                />
              </div>
              <button
                data-testid="upload-photos-btn"
                onClick={handleUploadPhotos}
                disabled={uploading || !uploadDishName.trim() || !uploadFiles?.length}
                style={{padding:'10px 24px',borderRadius:'8px',border:'none',background: uploading ? '#475569' : '#4ade80',color:'#0f172a',fontWeight:'bold',cursor: uploading ? 'wait' : 'pointer',whiteSpace:'nowrap'}}
              >
                {uploading ? 'Enviando...' : `Enviar ${uploadFiles?.length || 0} foto(s)`}
              </button>
            </div>
          </div>

          {/* Resultado do upload */}
          {uploadResult && (
            <div style={{background: uploadResult.ok ? '#064e3b' : '#7f1d1d',borderRadius:'12px',padding:'16px',marginBottom:'24px'}}>
              {uploadResult.ok ? (
                <div>
                  <div style={{fontWeight:'bold',color:'#4ade80',marginBottom:'8px'}}>
                    Upload concluido!
                  </div>
                  <div style={{fontSize:'14px',color:'#e2e8f0'}}>
                    {uploadResult.saved !== undefined && <span>{uploadResult.saved} foto(s) salva(s). </span>}
                    {uploadResult.total_saved !== undefined && <span>{uploadResult.total_saved} foto(s) salva(s). </span>}
                    {uploadResult.folder_count && <span>{uploadResult.folder_count} prato(s) enviado(s). </span>}
                    {uploadResult.total_images && <span>Total no prato: {uploadResult.total_images}</span>}
                  </div>
                  {uploadResult.errors?.length > 0 && (
                    <div style={{marginTop:'8px',fontSize:'12px',color:'#fbbf24'}}>
                      {uploadResult.errors.slice(0, 5).join(', ')}
                    </div>
                  )}
                </div>
              ) : (
                <div style={{color:'#fca5a5'}}>Erro: {uploadResult.error}</div>
              )}
            </div>
          )}

          {/* Lista de pratos */}
          {uploadStatus?.dishes && (
            <div style={{background:'#1a1a2e',borderRadius:'12px',padding:'20px'}}>
              <h3 style={{marginBottom:'16px',color:'#e2e8f0'}}>
                Dataset ({Object.keys(uploadStatus.dishes).length} pratos)
              </h3>
              <div style={{maxHeight:'400px',overflowY:'auto'}}>
                <table style={{width:'100%',borderCollapse:'collapse',fontSize:'13px'}}>
                  <thead>
                    <tr style={{borderBottom:'1px solid #334155'}}>
                      <th style={{textAlign:'left',padding:'8px',color:'#94a3b8'}}>Prato</th>
                      <th style={{textAlign:'right',padding:'8px',color:'#94a3b8'}}>Fotos</th>
                      <th style={{textAlign:'center',padding:'8px',color:'#94a3b8'}}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(uploadStatus.dishes).sort((a,b) => a[0].localeCompare(b[0])).map(([dish, count]) => (
                      <tr key={dish} style={{borderBottom:'1px solid #1e293b'}}>
                        <td style={{padding:'6px 8px',color:'#e2e8f0'}}>{dish}</td>
                        <td style={{padding:'6px 8px',textAlign:'right',color: count < 5 ? '#f87171' : count < 10 ? '#fbbf24' : '#4ade80', fontWeight:'bold'}}>{count}</td>
                        <td style={{padding:'6px 8px',textAlign:'center'}}>
                          {count < 5 ? '🔴' : count < 10 ? '🟡' : '🟢'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Moderação Tab */}
      {activeTab === 'moderation' && (
        <div className="moderation-section" data-testid="moderation-panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ margin: 0, color: '#f8fafc' }}>Fila de Moderação</h2>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <select
                value={moderationFilter}
                onChange={e => { setModerationFilter(e.target.value); loadModerationQueue(e.target.value); }}
                style={{ background: '#1e293b', color: '#e2e8f0', border: '1px solid #334155', borderRadius: '8px', padding: '8px 12px' }}
                data-testid="moderation-filter"
              >
                <option value="pending">Pendentes</option>
                <option value="approved">Aprovados</option>
                <option value="rejected">Rejeitados</option>
                <option value="corrected">Corrigidos</option>
                <option value="all">Todos</option>
              </select>
              <button
                onClick={() => loadModerationQueue()}
                style={{ background: '#334155', color: '#e2e8f0', border: 'none', borderRadius: '8px', padding: '8px 16px', cursor: 'pointer' }}
              >
                Atualizar
              </button>
            </div>
          </div>

          {moderationLoading && (
            <div style={{ textAlign: 'center', color: '#94a3b8', padding: '40px' }}>
              <p>Carregando...</p>
              <button 
                onClick={() => loadModerationQueue()}
                data-testid="retry-moderation"
                style={{ marginTop: '12px', padding: '8px 20px', background: '#10b981', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer' }}
              >
                Tentar Novamente
              </button>
            </div>
          )}

          {!moderationLoading && moderationItems.length === 0 && (
            <div style={{
              textAlign: 'center',
              padding: '60px 20px',
              background: 'rgba(30, 41, 59, 0.7)',
              borderRadius: '16px',
              border: '1px solid rgba(255,255,255,0.1)'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
              <h3 style={{ color: '#f8fafc', marginBottom: '8px' }}>Fila vazia</h3>
              <p style={{ color: '#94a3b8' }}>Nenhum item {moderationFilter !== 'all' ? `com status "${moderationFilter}"` : ''} na fila.</p>
            </div>
          )}

          {!moderationLoading && moderationItems.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {moderationItems.map(item => (
                <div
                  key={item.id}
                  data-testid={`moderation-item-${item.id}`}
                  style={{
                    background: 'rgba(30, 41, 59, 0.7)',
                    borderRadius: '16px',
                    border: '1px solid rgba(255,255,255,0.1)',
                    overflow: 'hidden',
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '0'
                  }}
                >
                  {/* Imagem */}
                  <div style={{ width: '200px', minHeight: '150px', background: '#0f172a', flexShrink: 0 }}>
                    <img
                      src={`${API}/admin/moderation-image/${item.id}`}
                      alt="Foto reportada"
                      style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                      onError={e => { e.target.style.display = 'none'; }}
                    />
                  </div>

                  {/* Info */}
                  <div style={{ flex: 1, padding: '16px', minWidth: '250px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                      <div>
                        <h3 style={{ color: '#f8fafc', margin: '0 0 4px', fontSize: '18px' }}>
                          {item.original_dish_display || 'Prato não identificado'}
                        </h3>
                        <span style={{
                          display: 'inline-block',
                          padding: '2px 10px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: 'bold',
                          background: item.status === 'pending' ? 'rgba(245,158,11,0.2)' :
                                     item.status === 'approved' ? 'rgba(16,185,129,0.2)' :
                                     item.status === 'rejected' ? 'rgba(239,68,68,0.2)' :
                                     'rgba(139,92,246,0.2)',
                          color: item.status === 'pending' ? '#f59e0b' :
                                 item.status === 'approved' ? '#10b981' :
                                 item.status === 'rejected' ? '#ef4444' :
                                 '#8b5cf6',
                          border: `1px solid ${item.status === 'pending' ? 'rgba(245,158,11,0.3)' :
                                   item.status === 'approved' ? 'rgba(16,185,129,0.3)' :
                                   item.status === 'rejected' ? 'rgba(239,68,68,0.3)' :
                                   'rgba(139,92,246,0.3)'}`
                        }}>
                          {item.status === 'pending' ? 'Pendente' :
                           item.status === 'approved' ? 'Aprovado' :
                           item.status === 'rejected' ? 'Rejeitado' :
                           'Corrigido'}
                        </span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: '16px', color: '#94a3b8', fontSize: '13px', marginBottom: '8px', flexWrap: 'wrap' }}>
                      <span>Score: <strong style={{ color: item.score >= 0.7 ? '#10b981' : item.score >= 0.5 ? '#f59e0b' : '#ef4444' }}>
                        {(item.score * 100).toFixed(0)}%
                      </strong></span>
                      <span>Confiança: <strong>{item.confidence || '-'}</strong></span>
                      <span>Fonte: <strong>{item.source || '-'}</strong></span>
                    </div>

                    <div style={{ color: '#64748b', fontSize: '12px', marginBottom: '12px' }}>
                      {item.created_at ? new Date(item.created_at).toLocaleString('pt-BR') : '-'}
                    </div>

                    {item.correction && (
                      <div style={{ padding: '8px 12px', background: 'rgba(139,92,246,0.15)', borderRadius: '8px', marginBottom: '12px', fontSize: '13px', color: '#c4b5fd' }}>
                        Corrigido para: <strong>{item.correction}</strong>
                      </div>
                    )}

                    {/* Ações - apenas para pendentes */}
                    {item.status === 'pending' && (
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        {confirmAction?.itemId === item.id && confirmAction?.type === 'approve' ? (
                          <div style={{ display: 'flex', gap: '6px' }}>
                            <button onClick={() => approveModerationItem(item.id)} data-testid={`moderation-confirm-approve-${item.id}`}
                              style={{ background: '#10b981', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' }}>
                              Confirmar Aprovar
                            </button>
                            <button onClick={() => setConfirmAction(null)} style={{ background: '#475569', color: '#fff', border: 'none', padding: '8px 12px', borderRadius: '8px', cursor: 'pointer', fontSize: '13px' }}>
                              Cancelar
                            </button>
                          </div>
                        ) : confirmAction?.itemId === item.id && confirmAction?.type === 'reject' ? (
                          <div style={{ display: 'flex', gap: '6px' }}>
                            <button onClick={() => rejectModerationItem(item.id)} data-testid={`moderation-confirm-reject-${item.id}`}
                              style={{ background: '#ef4444', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' }}>
                              Confirmar Rejeitar
                            </button>
                            <button onClick={() => setConfirmAction(null)} style={{ background: '#475569', color: '#fff', border: 'none', padding: '8px 12px', borderRadius: '8px', cursor: 'pointer', fontSize: '13px' }}>
                              Cancelar
                            </button>
                          </div>
                        ) : (
                          <>
                            <button
                              onClick={() => setConfirmAction({ type: 'approve', itemId: item.id })}
                              data-testid={`moderation-approve-${item.id}`}
                              style={{ background: 'linear-gradient(135deg, #10b981, #059669)', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' }}>
                              Aprovar
                            </button>
                            <button
                              onClick={() => setConfirmAction({ type: 'reject', itemId: item.id })}
                              data-testid={`moderation-reject-${item.id}`}
                              style={{ background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' }}>
                              Rejeitar
                            </button>
                          </>
                        )}
                        {correctingItemId === item.id ? (
                          <div style={{ display: 'flex', gap: '8px', flex: 1, minWidth: '200px', flexWrap: 'wrap' }}>
                            <select
                              value={correctionName}
                              onChange={e => setCorrectionName(e.target.value)}
                              data-testid={`moderation-correction-select-${item.id}`}
                              style={{
                                flex: 1,
                                minWidth: '200px',
                                background: '#0f172a',
                                color: '#e2e8f0',
                                border: '1px solid #334155',
                                borderRadius: '8px',
                                padding: '8px 12px',
                                fontSize: '13px',
                                cursor: 'pointer'
                              }}
                            >
                              <option value="">Selecione o prato correto...</option>
                              {dishes
                                .sort((a, b) => (a.nome || a.name || '').localeCompare(b.nome || b.name || ''))
                                .map(d => (
                                  <option key={d.slug} value={d.nome || d.name || d.slug}>
                                    {d.nome || d.name || d.slug}
                                  </option>
                                ))
                              }
                            </select>
                            <button
                              onClick={() => correctModerationItem(item.id)}
                              data-testid={`moderation-save-correction-${item.id}`}
                              disabled={!correctionName}
                              style={{
                                background: correctionName ? 'linear-gradient(135deg, #8b5cf6, #7c3aed)' : '#334155',
                                color: '#fff',
                                border: 'none',
                                padding: '8px 16px',
                                borderRadius: '8px',
                                cursor: correctionName ? 'pointer' : 'not-allowed',
                                fontWeight: 'bold',
                                fontSize: '13px'
                              }}
                            >
                              Salvar
                            </button>
                            <button
                              onClick={() => { setCorrectingItemId(null); setCorrectionName(''); }}
                              style={{
                                background: '#334155',
                                color: '#e2e8f0',
                                border: 'none',
                                padding: '8px 12px',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                fontSize: '13px'
                              }}
                            >
                              ✕
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => { setCorrectingItemId(item.id); setCorrectionName(''); }}
                            data-testid={`moderation-correct-${item.id}`}
                            style={{
                              background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
                              color: '#fff',
                              border: 'none',
                              padding: '8px 16px',
                              borderRadius: '8px',
                              cursor: 'pointer',
                              fontWeight: 'bold',
                              fontSize: '13px'
                            }}
                          >
                            ✏️ Corrigir
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Calibração CLIP Tab */}
      {activeTab === 'calibration' && (
        <div className="calibration-section" data-testid="calibration-section">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 data-testid="calibration-title" style={{ margin: 0, color: '#e2e8f0' }}>Calibracao CLIP - Youden's J</h2>
            <button onClick={loadCalibrationData} data-testid="calibration-refresh" style={{
              padding: '8px 16px', background: '#3b82f6', color: '#fff', border: 'none',
              borderRadius: '8px', cursor: 'pointer', fontSize: '14px'
            }}>Atualizar</button>
          </div>

          {calibrationLoading && <p style={{ color: '#94a3b8' }}>Carregando dados...</p>}

          {!calibrationLoading && calibrationData && (
            <>
              {/* Thresholds Atuais */}
              <div data-testid="current-thresholds" style={{
                background: '#1e293b', borderRadius: '12px', padding: '16px', marginBottom: '20px', border: '1px solid #334155'
              }}>
                <h3 style={{ color: '#94a3b8', margin: '0 0 12px', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Thresholds Atuais</h3>
                <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
                  <div style={{ flex: 1, minWidth: '120px', textAlign: 'center', padding: '12px', background: '#0f172a', borderRadius: '8px' }}>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#22c55e' }}>{((calibrationData.current_thresholds?.alta || 0.85) * 100).toFixed(0)}%</div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>Alta Confianca</div>
                  </div>
                  <div style={{ flex: 1, minWidth: '120px', textAlign: 'center', padding: '12px', background: '#0f172a', borderRadius: '8px' }}>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b' }}>{((calibrationData.current_thresholds?.media || 0.50) * 100).toFixed(0)}%</div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>Media Confianca</div>
                  </div>
                  <div style={{ flex: 1, minWidth: '120px', textAlign: 'center', padding: '12px', background: '#0f172a', borderRadius: '8px' }}>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ef4444' }}>&lt;{((calibrationData.current_thresholds?.rejeicao || 0.50) * 100).toFixed(0)}%</div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>Rejeicao</div>
                  </div>
                </div>
              </div>

              {/* Estatísticas */}
              <div data-testid="calibration-stats" style={{
                background: '#1e293b', borderRadius: '12px', padding: '16px', marginBottom: '20px', border: '1px solid #334155'
              }}>
                <h3 style={{ color: '#94a3b8', margin: '0 0 12px', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Amostras Coletadas</h3>
                <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
                  <div style={{ flex: 1, minWidth: '100px', textAlign: 'center', padding: '12px', background: '#0f172a', borderRadius: '8px' }}>
                    <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#e2e8f0' }}>{calibrationData.stats?.total_samples || 0}</div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>Total</div>
                  </div>
                  <div style={{ flex: 1, minWidth: '100px', textAlign: 'center', padding: '12px', background: '#0f172a', borderRadius: '8px' }}>
                    <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#22c55e' }}>{calibrationData.stats?.correct_count || 0}</div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>Corretos</div>
                  </div>
                  <div style={{ flex: 1, minWidth: '100px', textAlign: 'center', padding: '12px', background: '#0f172a', borderRadius: '8px' }}>
                    <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#ef4444' }}>{calibrationData.stats?.incorrect_count || 0}</div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>Incorretos</div>
                  </div>
                </div>
                {calibrationData.stats?.correct_scores?.avg && (
                  <div style={{ marginTop: '12px', display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
                    <div style={{ flex: 1, padding: '8px', background: '#0f172a', borderRadius: '6px', fontSize: '13px', color: '#94a3b8' }}>
                      Scores Corretos: min <strong style={{ color: '#22c55e' }}>{(calibrationData.stats.correct_scores.min * 100).toFixed(1)}%</strong> | 
                      media <strong style={{ color: '#22c55e' }}>{(calibrationData.stats.correct_scores.avg * 100).toFixed(1)}%</strong> | 
                      max <strong style={{ color: '#22c55e' }}>{(calibrationData.stats.correct_scores.max * 100).toFixed(1)}%</strong>
                    </div>
                    {calibrationData.stats?.incorrect_scores?.avg && (
                      <div style={{ flex: 1, padding: '8px', background: '#0f172a', borderRadius: '6px', fontSize: '13px', color: '#94a3b8' }}>
                        Scores Incorretos: min <strong style={{ color: '#ef4444' }}>{(calibrationData.stats.incorrect_scores.min * 100).toFixed(1)}%</strong> | 
                        media <strong style={{ color: '#ef4444' }}>{(calibrationData.stats.incorrect_scores.avg * 100).toFixed(1)}%</strong> | 
                        max <strong style={{ color: '#ef4444' }}>{(calibrationData.stats.incorrect_scores.max * 100).toFixed(1)}%</strong>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Youden's J */}
              {calibrationData.youden ? (
                <div data-testid="youden-result" style={{
                  background: 'linear-gradient(135deg, #1e3a5f, #1e293b)', borderRadius: '12px', padding: '20px',
                  marginBottom: '20px', border: '2px solid #3b82f6'
                }}>
                  <h3 style={{ color: '#60a5fa', margin: '0 0 12px', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Threshold Otimo (Youden's J)</h3>
                  <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', alignItems: 'center' }}>
                    <div style={{ textAlign: 'center', padding: '16px 24px', background: '#0f172a', borderRadius: '12px' }}>
                      <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#60a5fa' }}>{(calibrationData.youden.optimal_threshold * 100).toFixed(1)}%</div>
                      <div style={{ fontSize: '12px', color: '#94a3b8' }}>Threshold Sugerido</div>
                    </div>
                    <div style={{ flex: 1, fontSize: '14px', color: '#cbd5e1', lineHeight: 1.6 }}>
                      <div>Indice J: <strong>{calibrationData.youden.j_index.toFixed(3)}</strong></div>
                      <div>Sensibilidade: <strong style={{ color: '#22c55e' }}>{(calibrationData.youden.sensitivity * 100).toFixed(0)}%</strong> dos corretos aceitos</div>
                      <div>Especificidade: <strong style={{ color: '#f59e0b' }}>{(calibrationData.youden.specificity * 100).toFixed(0)}%</strong> dos errados rejeitados</div>
                      <div style={{ marginTop: '8px', fontSize: '12px', color: '#64748b' }}>{calibrationData.youden.interpretation}</div>
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{
                  background: '#1e293b', borderRadius: '12px', padding: '20px', marginBottom: '20px',
                  border: '1px dashed #475569', textAlign: 'center'
                }}>
                  <p style={{ color: '#94a3b8', margin: 0, fontSize: '14px' }}>
                    Minimo de 5 amostras corretas e 5 incorretas necessarias para calcular o threshold otimo.
                    <br/><span style={{ color: '#64748b', fontSize: '12px' }}>Escaneie pratos no app e confirme/corrija os resultados.</span>
                  </p>
                </div>
              )}

              {/* Distribuição por faixa */}
              {calibrationData.distribution && (
                <div data-testid="calibration-distribution" style={{
                  background: '#1e293b', borderRadius: '12px', padding: '16px', marginBottom: '20px', border: '1px solid #334155'
                }}>
                  <h3 style={{ color: '#94a3b8', margin: '0 0 12px', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Distribuicao de Scores</h3>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #334155' }}>
                        <th style={{ textAlign: 'left', padding: '8px', color: '#94a3b8' }}>Faixa</th>
                        <th style={{ textAlign: 'center', padding: '8px', color: '#22c55e' }}>Corretos</th>
                        <th style={{ textAlign: 'center', padding: '8px', color: '#ef4444' }}>Incorretos</th>
                        <th style={{ textAlign: 'center', padding: '8px', color: '#94a3b8' }}>Barra</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(calibrationData.distribution).map(([range, counts]) => {
                        const total = (counts.correct || 0) + (counts.incorrect || 0);
                        const maxTotal = Math.max(...Object.values(calibrationData.distribution).map(c => (c.correct || 0) + (c.incorrect || 0)), 1);
                        const label = range.replace('_', '-').replace('0.', '').replace('0.', '');
                        const displayLabel = range.split('_').map(v => (parseFloat(v) * 100).toFixed(0) + '%').join(' - ');
                        return (
                          <tr key={range} style={{ borderBottom: '1px solid #1e293b' }}>
                            <td style={{ padding: '6px 8px', color: '#e2e8f0', fontFamily: 'monospace' }}>{displayLabel}</td>
                            <td style={{ textAlign: 'center', padding: '6px 8px', color: '#22c55e', fontWeight: counts.correct > 0 ? 'bold' : 'normal' }}>{counts.correct || 0}</td>
                            <td style={{ textAlign: 'center', padding: '6px 8px', color: '#ef4444', fontWeight: counts.incorrect > 0 ? 'bold' : 'normal' }}>{counts.incorrect || 0}</td>
                            <td style={{ padding: '6px 8px' }}>
                              <div style={{ display: 'flex', height: '16px', borderRadius: '4px', overflow: 'hidden', background: '#0f172a' }}>
                                {counts.correct > 0 && <div style={{ width: `${(counts.correct / maxTotal) * 100}%`, background: '#22c55e', minWidth: '2px' }} />}
                                {counts.incorrect > 0 && <div style={{ width: `${(counts.incorrect / maxTotal) * 100}%`, background: '#ef4444', minWidth: '2px' }} />}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Tabela de amostras */}
              {calibrationData.samples && calibrationData.samples.length > 0 && (
                <div data-testid="calibration-samples" style={{
                  background: '#1e293b', borderRadius: '12px', padding: '16px', border: '1px solid #334155'
                }}>
                  <h3 style={{ color: '#94a3b8', margin: '0 0 12px', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Ultimas Amostras ({calibrationData.samples.length})
                  </h3>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid #334155' }}>
                          <th style={{ textAlign: 'left', padding: '8px', color: '#94a3b8' }}>Prato CLIP</th>
                          <th style={{ textAlign: 'left', padding: '8px', color: '#94a3b8' }}>Prato Real</th>
                          <th style={{ textAlign: 'center', padding: '8px', color: '#94a3b8' }}>Score</th>
                          <th style={{ textAlign: 'center', padding: '8px', color: '#94a3b8' }}>Acertou?</th>
                          <th style={{ textAlign: 'center', padding: '8px', color: '#94a3b8' }}>Fonte</th>
                          <th style={{ textAlign: 'right', padding: '8px', color: '#94a3b8' }}>Data</th>
                          <th style={{ textAlign: 'center', padding: '8px', color: '#94a3b8' }}>Acao</th>
                        </tr>
                      </thead>
                      <tbody>
                        {calibrationData.samples.map((s, i) => (
                          <tr key={s._id || i} style={{ borderBottom: '1px solid #1e293b', background: s.is_correct ? 'transparent' : 'rgba(239,68,68,0.05)' }}>
                            <td style={{ padding: '6px 8px', color: '#e2e8f0' }}>{s.dish_clip || s.dish_slug || '-'}</td>
                            <td style={{ padding: '6px 8px', color: s.is_correct ? '#22c55e' : '#ef4444' }}>{s.dish_real || s.original_dish || s.dish_clip || '-'}</td>
                            <td style={{ textAlign: 'center', padding: '6px 8px', color: '#e2e8f0', fontFamily: 'monospace', fontWeight: 'bold' }}>
                              {s.score ? (s.score * 100).toFixed(1) + '%' : '-'}
                            </td>
                            <td style={{ textAlign: 'center', padding: '6px 8px' }}>
                              <span style={{ color: s.is_correct ? '#22c55e' : '#ef4444', fontWeight: 'bold' }}>{s.is_correct ? 'SIM' : 'NAO'}</span>
                            </td>
                            <td style={{ textAlign: 'center', padding: '6px 8px', color: '#94a3b8', fontSize: '11px' }}>{s.source || '-'}</td>
                            <td style={{ textAlign: 'right', padding: '6px 8px', color: '#64748b', fontSize: '11px' }}>
                              {s.created_at ? new Date(s.created_at).toLocaleString('pt-BR') : '-'}
                            </td>
                            <td style={{ textAlign: 'center', padding: '6px 8px' }}>
                              {s._id && (
                                <button
                                  data-testid={`calibration-delete-${i}`}
                                  onClick={() => deleteCalibrationSample(s._id)}
                                  style={{
                                    background: 'transparent', border: '1px solid #475569', color: '#ef4444',
                                    borderRadius: '4px', cursor: 'pointer', padding: '2px 8px', fontSize: '11px'
                                  }}
                                  title="Deletar amostra"
                                >
                                  Deletar
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {(!calibrationData.samples || calibrationData.samples.length === 0) && !calibrationLoading && (
                <div style={{
                  background: '#1e293b', borderRadius: '12px', padding: '30px', textAlign: 'center',
                  border: '1px dashed #475569'
                }}>
                  <p style={{ color: '#94a3b8', margin: '0 0 8px', fontSize: '16px' }}>Nenhuma amostra coletada ainda</p>
                  <p style={{ color: '#64748b', margin: 0, fontSize: '13px' }}>
                    Escaneie pratos pelo app e use os botoes "Correto" / "Incorreto" para alimentar a calibracao.
                    <br/>Os scores serao registrados automaticamente.
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      )}

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
              {/* Galeria de fotos do prato */}
              <div className="edit-photo-section">
                <div className="photo-gallery" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
                  {editingDish._loading_images ? (
                    <p style={{ color: '#94a3b8', textAlign: 'center' }}>Carregando fotos...</p>
                  ) : editingDish.all_images && editingDish.all_images.length > 0 ? (
                    editingDish.all_images.map((img, idx) => (
                      <div key={idx} style={{ position: 'relative' }}>
                        <img 
                          src={`${API}/admin/dish-image/${editingDish.slug}?img=${encodeURIComponent(img)}&thumb=1`} 
                          alt={`${editingDish.nome} ${idx + 1}`}
                          style={{ width: '100px', height: '100px', objectFit: 'cover', borderRadius: '8px', cursor: 'pointer' }}
                          onClick={() => window.open(`${API}/admin/dish-image/${editingDish.slug}?img=${encodeURIComponent(img)}`, '_blank')}
                        />
                        <span style={{ position: 'absolute', bottom: '2px', right: '2px', background: 'rgba(0,0,0,0.6)', color: '#fff', fontSize: '10px', padding: '2px 4px', borderRadius: '4px' }}>
                          {idx + 1}
                        </span>
                        {/* Botão MOVER */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setMoveImageState({ idx, img, slug: editingDish.slug });
                            setMoveDestination('');
                          }}
                          style={{
                            position: 'absolute',
                            top: '2px',
                            left: '2px',
                            background: 'rgba(59,130,246,0.9)',
                            color: '#fff',
                            border: 'none',
                            borderRadius: '50%',
                            width: '20px',
                            height: '20px',
                            fontSize: '10px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                          title="Mover para outro prato"
                        >
                          ↗
                        </button>
                        {/* Botão DELETAR */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            if (deleteImageState && deleteImageState.idx === idx && deleteImageState.slug === editingDish.slug) {
                              // Second click = confirm delete
                              (async () => {
                                try {
                                  const res = await xhrDelete(`${API}/admin/dish-image/${encodeURIComponent(editingDish.slug)}?img=${encodeURIComponent(img)}`);
                                  const data = await res.json();
                                  if (data.ok) {
                                    notify('Foto removida!', 'success');
                                    setEditingDish({
                                      ...editingDish,
                                      all_images: editingDish.all_images.filter((_, i) => i !== idx),
                                      image_count: data.remaining_images
                                    });
                                  } else {
                                    notify(`Erro ao deletar: ${data.error || 'Falha'}`, 'error');
                                  }
                                } catch (err) {
                                  notify(`Erro ao deletar: ${err.message}`, 'error');
                                }
                                setDeleteImageState(null);
                              })();
                            } else {
                              // First click = show confirmation
                              setDeleteImageState({ idx, img, slug: editingDish.slug });
                              setMoveImageState(null);
                              setTimeout(() => setDeleteImageState(null), 5000);
                            }
                          }}
                          style={{
                            position: 'absolute',
                            top: '2px',
                            right: '2px',
                            background: deleteImageState && deleteImageState.idx === idx && deleteImageState.slug === editingDish.slug
                              ? 'rgba(255,0,0,1)' : 'rgba(220,53,69,0.9)',
                            color: '#fff',
                            border: deleteImageState && deleteImageState.idx === idx && deleteImageState.slug === editingDish.slug
                              ? '2px solid #fff' : 'none',
                            borderRadius: deleteImageState && deleteImageState.idx === idx && deleteImageState.slug === editingDish.slug
                              ? '4px' : '50%',
                            width: deleteImageState && deleteImageState.idx === idx && deleteImageState.slug === editingDish.slug
                              ? 'auto' : '20px',
                            height: '20px',
                            fontSize: deleteImageState && deleteImageState.idx === idx && deleteImageState.slug === editingDish.slug
                              ? '9px' : '12px',
                            padding: deleteImageState && deleteImageState.idx === idx && deleteImageState.slug === editingDish.slug
                              ? '0 6px' : '0',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            zIndex: 2
                          }}
                          title={deleteImageState && deleteImageState.idx === idx ? 'Clique de novo para CONFIRMAR' : 'Deletar foto'}
                        >
                          {deleteImageState && deleteImageState.idx === idx && deleteImageState.slug === editingDish.slug
                            ? 'DELETAR?' : '✕'}
                        </button>
                      </div>
                    ))
                  ) : editingDish.first_image ? (
                    <img 
                      src={`${API}/admin/dish-image/${encodeURIComponent(editingDish.slug)}?thumb=1`} 
                      alt={editingDish.nome}
                      style={{ maxWidth: '200px', borderRadius: '8px' }}
                    />
                  ) : (
                    <div className="no-photo-large">{editingDish.category_emoji || '🍽️'}</div>
                  )}
                </div>
                <p className="photo-info">📷 {editingDish.image_count} fotos - Clique para ampliar</p>
                <p style={{ fontSize: '11px', color: '#888', margin: '4px 0' }}>
                  <span style={{ color: '#3b82f6' }}>↗ Azul</span> = Mover para outro prato | 
                  <span style={{ color: '#dc3545' }}> ✕ Vermelho</span> = Deletar
                </p>
                {/* Modal inline para MOVER imagem */}
                {moveImageState && moveImageState.slug === editingDish.slug && (
                  <div style={{ background: '#1a2744', border: '2px solid #3b82f6', borderRadius: '8px', padding: '12px', marginTop: '8px' }}>
                    <p style={{ color: '#fff', margin: '0 0 8px', fontSize: '13px' }}>
                      Mover foto {moveImageState.idx + 1} para qual prato?
                    </p>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <select
                        data-testid="move-destination-select"
                        value={moveDestination}
                        onChange={e => setMoveDestination(e.target.value)}
                        style={{ flex: 1, padding: '6px 10px', borderRadius: '4px', border: '1px solid #4a5568', background: '#0f172a', color: '#fff', fontSize: '13px' }}
                        autoFocus
                      >
                        <option value="">-- Selecione o prato destino --</option>
                        {dishes.filter(d => d.slug !== editingDish.slug).sort((a,b) => (a.nome||'').localeCompare(b.nome||'')).map(d => (
                          <option key={d.slug} value={d.slug}>{d.nome || d.slug} ({d.image_count} fotos)</option>
                        ))}
                      </select>
                      <button
                        data-testid="move-image-confirm-btn"
                        onClick={() => {
                          if (!moveDestination.trim()) {
                            setNotification({ message: 'Selecione um prato destino!', type: 'error' });
                            setTimeout(() => setNotification(null), 4000);
                            return;
                          }
                          // Mostrar loading
                          setNotification({ message: 'Movendo foto, aguarde...', type: 'info' });
                          
                          // XHR INLINE - sem dependencias externas
                          const xhr = new XMLHttpRequest();
                          xhr.open('POST', '/api/admin/move-image');
                          xhr.setRequestHeader('Content-Type', 'application/json');
                          xhr.timeout = 30000;
                          
                          const moveSlug = moveImageState.slug;
                          const moveIdx = moveImageState.idx;
                          const moveImg = moveImageState.img;
                          const dest = moveDestination.trim();
                          
                          xhr.onload = () => {
                            try {
                              const data = JSON.parse(xhr.responseText);
                              if (data.ok) {
                                setNotification({ message: 'Foto movida com sucesso!', type: 'success' });
                                setEditingDish(prev => prev ? {
                                  ...prev,
                                  all_images: prev.all_images.filter((_, i) => i !== moveIdx),
                                  image_count: data.remaining_in_source
                                } : prev);
                                setDishes(prev => prev.map(d => {
                                  if (d.slug === moveSlug) return {...d, image_count: data.remaining_in_source};
                                  if (d.slug === dest) return {...d, image_count: (d.image_count || 0) + 1};
                                  return d;
                                }));
                              } else {
                                setNotification({ message: 'Erro: ' + (data.error || 'falha'), type: 'error' });
                              }
                            } catch(e) {
                              setNotification({ message: 'Erro parse: ' + e.message, type: 'error' });
                            }
                            setTimeout(() => setNotification(null), 5000);
                          };
                          xhr.onerror = () => {
                            setNotification({ message: 'Erro de rede ao mover', type: 'error' });
                            setTimeout(() => setNotification(null), 5000);
                          };
                          xhr.ontimeout = () => {
                            setNotification({ message: 'Timeout ao mover (30s)', type: 'error' });
                            setTimeout(() => setNotification(null), 5000);
                          };
                          
                          xhr.send(JSON.stringify({
                            source_dish: moveSlug,
                            target_dish: dest,
                            image_name: moveImg
                          }));
                          
                          setMoveImageState(null);
                          setMoveDestination('');
                        }}
                        style={{ padding: '6px 14px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '13px', fontWeight: 'bold' }}
                      >
                        MOVER AGORA
                      </button>
                      <button
                        onClick={() => { setMoveImageState(null); setMoveDestination(''); }}
                        style={{ padding: '6px 10px', background: '#4a5568', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '13px' }}
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                )}
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
                  <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                    <button 
                      className="taco-review-btn"
                      onClick={revisarComTACO}
                      disabled={revisandoIA}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: revisandoIA ? '#666' : '#2196F3',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: revisandoIA ? 'wait' : 'pointer',
                        fontSize: '14px',
                        flex: 1
                      }}
                    >
                      {revisandoIA ? '⏳ Calculando...' : '📊 Nutrição TACO (grátis)'}
                    </button>
                    <button 
                      className="ia-review-btn"
                      onClick={revisarComIA}
                      disabled={revisandoIA}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: revisandoIA ? '#666' : '#ff9800',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: revisandoIA ? 'wait' : 'pointer',
                        fontSize: '14px'
                      }}
                    >
                      🤖 IA (💰)
                    </button>
                  </div>
                  <small style={{ display: 'block', marginTop: '4px', color: '#888' }}>
                    📊 TACO: Tabela Brasileira (GRÁTIS) | 🤖 IA: Gemini (GASTA CRÉDITOS)
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
