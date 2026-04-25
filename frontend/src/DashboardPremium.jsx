import React, { useState, useEffect, useCallback } from 'react';
import { 
  ArrowLeft, TrendingUp, Calendar, Target, Flame, 
  Beef, Wheat, Droplets, Award, ChevronDown, ChevronUp,
  Edit3, Save, X, FileText, Printer
} from 'lucide-react';
import './DashboardPremium.css';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Componente de barra de progresso circular
const CircularProgress = ({ value, max, color, label, icon: Icon }) => {
  const percent = Math.min((value / max) * 100, 100);
  const circumference = 2 * Math.PI * 40;
  const strokeDashoffset = circumference - (percent / 100) * circumference;
  
  return (
    <div className="circular-progress-item" data-testid={`progress-${label.toLowerCase()}`}>
      <svg className="circular-progress-svg" viewBox="0 0 100 100">
        <circle className="circular-bg" cx="50" cy="50" r="40" />
        <circle 
          className="circular-fill" 
          cx="50" cy="50" r="40"
          style={{ 
            stroke: color,
            strokeDasharray: circumference,
            strokeDashoffset: strokeDashoffset
          }}
        />
      </svg>
      <div className="circular-content">
        {Icon && <Icon size={16} color={color} />}
        <span className="circular-value">{value.toFixed(0)}</span>
        <span className="circular-max">/{max}</span>
      </div>
      <span className="circular-label">{label}</span>
    </div>
  );
};

// Componente de barra de progresso linear
const ProgressBar = ({ value, max, color, label, unit = '' }) => {
  const percent = Math.min((value / max) * 100, 100);
  return (
    <div className="progress-item">
      <div className="progress-label">
        <span>{label}</span>
        <span>{value.toFixed(0)}{unit} / {max}{unit}</span>
      </div>
      <div className="progress-bar-bg">
        <div 
          className="progress-bar-fill" 
          style={{ width: `${percent}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
};

// Gráfico de barras
const BarChart = ({ data, label, color, maxValue: customMax }) => {
  const maxValue = customMax || Math.max(...data.map(d => d.value || 0), 1);
  
  return (
    <div className="bar-chart">
      <div className="bar-chart-header">
        <span className="bar-chart-label">{label}</span>
        <span className="bar-chart-max">Máx: {maxValue.toFixed(0)}</span>
      </div>
      <div className="bar-chart-bars">
        {data.map((d, i) => (
          <div key={i} className="bar-chart-item">
            <div className="bar-chart-bar-container">
              <div 
                className="bar-chart-bar"
                style={{ 
                  height: `${Math.max((d.value / maxValue) * 100, 2)}%`,
                  backgroundColor: color 
                }}
                title={`${d.value?.toFixed(0) || 0}`}
              />
            </div>
            <span className="bar-chart-day">{d.day}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Modal de edição de metas
const MetasModal = ({ metas, onSave, onClose }) => {
  const [editMetas, setEditMetas] = useState(metas);
  
  return (
    <div className="metas-modal-overlay" onClick={onClose}>
      <div className="metas-modal" onClick={e => e.stopPropagation()}>
        <div className="metas-modal-header">
          <h3>🎯 Editar Metas Diárias</h3>
          <button onClick={onClose}><X size={20} /></button>
        </div>
        
        <div className="metas-modal-body">
          <div className="meta-input-group">
            <label>🔥 Calorias (kcal)</label>
            <input 
              type="number" 
              value={editMetas.calorias}
              onChange={e => setEditMetas({...editMetas, calorias: parseInt(e.target.value) || 2000})}
              min="1000" max="5000"
            />
            <span className="meta-hint">Recomendado: 1800-2500 kcal</span>
          </div>
          
          <div className="meta-input-group">
            <label>💪 Proteínas (g)</label>
            <input 
              type="number" 
              value={editMetas.proteinas}
              onChange={e => setEditMetas({...editMetas, proteinas: parseInt(e.target.value) || 50})}
              min="20" max="300"
            />
            <span className="meta-hint">Recomendado: 50-150g</span>
          </div>
          
          <div className="meta-input-group">
            <label>🍞 Carboidratos (g)</label>
            <input 
              type="number" 
              value={editMetas.carboidratos}
              onChange={e => setEditMetas({...editMetas, carboidratos: parseInt(e.target.value) || 250})}
              min="50" max="500"
            />
            <span className="meta-hint">Recomendado: 200-350g</span>
          </div>
          
          <div className="meta-input-group">
            <label>🥑 Gorduras (g)</label>
            <input 
              type="number" 
              value={editMetas.gorduras}
              onChange={e => setEditMetas({...editMetas, gorduras: parseInt(e.target.value) || 65})}
              min="20" max="200"
            />
            <span className="meta-hint">Recomendado: 50-100g</span>
          </div>
        </div>
        
        <div className="metas-modal-footer">
          <button className="btn-cancel" onClick={onClose}>Cancelar</button>
          <button className="btn-save" onClick={() => onSave(editMetas)}>
            <Save size={16} /> Salvar
          </button>
        </div>
      </div>
    </div>
  );
};

// ─── HELPERS DE INSIGHT (só leitura de dados) ────────────────────────────────
const getCalorieStatus = (atual, meta) => {
  if (!meta || meta === 0) return { cor: '#d4af37', emoji: '—', texto: 'Defina sua meta calórica' };
  const pct = ((atual - meta) / meta) * 100;
  if (pct > 10) return { cor: '#ef4444', emoji: '⚠️', texto: `${pct.toFixed(0)}% acima da meta` };
  if (pct < -10) return { cor: '#f59e0b', emoji: '⚠️', texto: `${Math.abs(pct).toFixed(0)}% abaixo da meta` };
  return { cor: '#10b981', emoji: '✔', texto: 'Dentro da meta' };
};

const getMacroStatus = (atual, meta) => {
  if (!meta || meta === 0) return { label: 'Sem meta', cor: '#666', icon: '—' };
  const pct = (atual / meta) * 100;
  if (pct < 70) return { label: 'Baixa', cor: '#f59e0b', icon: '⚠️' };
  if (pct > 120) return { label: 'Alta', cor: '#ef4444', icon: '⚠️' };
  return { label: 'Adequada', cor: '#10b981', icon: '✔' };
};

const getSugestoes = (hoje, metas) => {
  const sugs = [];
  const calPct  = metas.calorias     ? hoje.calorias     / metas.calorias     : 0;
  const gorPct  = metas.gorduras     ? hoje.gorduras     / metas.gorduras     : 0;
  const protPct = metas.proteinas    ? hoje.proteinas    / metas.proteinas    : 0;
  const carbPct = metas.carboidratos ? hoje.carboidratos / metas.carboidratos : 0;
  if (calPct > 1.1)  sugs.push('Prefira pratos leves na próxima refeição');
  if (gorPct > 1.2)  sugs.push('Evite frituras e molhos gordurosos');
  if (protPct < 0.7) sugs.push('Inclua proteína magra: frango, atum ou ovos');
  if (carbPct > 1.3) sugs.push('Reduza carboidratos na próxima refeição');
  if (carbPct < 0.5) sugs.push('Adicione grãos integrais ou tubérculos');
  if (hoje.calorias < 500 && hoje.proteinas < 20) sugs.push('Continue escaneando para ver insights completos');
  if (sugs.length === 0) sugs.push('Continue assim! Sua dieta está equilibrada hoje.');
  return sugs;
};

const dedupeAlertas = (alertas) => {
  if (!alertas || alertas.length === 0) return [];
  const seen = new Set();
  return alertas.filter(a => {
    const key = (a.msg || String(a)).toLowerCase().trim();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
};
// ─────────────────────────────────────────────────────────────────────────────

export default function DashboardPremium({ user, onClose }) {
  const [loading, setLoading] = useState(true);
  const [dashData, setDashData] = useState(null);
  const [periodo, setPeriodo] = useState('semana');
  const [activeTab, setActiveTab] = useState('resumo');
  const [showMetasModal, setShowMetasModal] = useState(false);
  const [expandedDay, setExpandedDay] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  
  const loadDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/premium/dashboard?pin=${user.pin}&periodo=${periodo}`);
      const data = await res.json();
      if (data.ok) {
        setDashData(data);
      }
    } catch (e) {
      console.error('Erro ao carregar dashboard:', e);
    }
    setLoading(false);
  }, [user.pin, periodo]);
  
  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);
  
  const saveMetas = async (novasMetas) => {
    try {
      const res = await fetch(`${API}/premium/metas?pin=${user.pin}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ metas: novasMetas })
      });
      const data = await res.json();
      if (data.ok) {
        setShowMetasModal(false);
        loadDashboard();
      } else {
        alert('Erro ao salvar metas: ' + data.error);
      }
    } catch (e) {
      alert('Erro ao salvar metas');
    }
  };

  const loadReport = useCallback(async () => {
    setReportLoading(true);
    try {
      const res = await fetch(`${API}/premium/report?pin=${user.pin}&periodo=${periodo}`);
      const data = await res.json();
      if (data.ok) setReportData(data);
    } catch (e) {
      console.error('Erro ao carregar relatório:', e);
    }
    setReportLoading(false);
  }, [user.pin, periodo]);

  useEffect(() => {
    if (activeTab === 'relatorio' && !reportData) loadReport();
  }, [activeTab, loadReport, reportData]);

  useEffect(() => {
    setReportData(null);
  }, [periodo]);
  
  if (loading) {
    return (
      <div className="dashboard-premium" data-testid="dashboard-premium">
        <div className="dashboard-loading">
          <div className="spinner"></div>
          <p>Carregando seu dashboard...</p>
        </div>
      </div>
    );
  }
  
  const metas = dashData?.metas || { calorias: 2000, proteinas: 50, carboidratos: 250, gorduras: 65 };
  const hoje = dashData?.hoje || { calorias: 0, proteinas: 0, carboidratos: 0, gorduras: 0 };
  const grafico = dashData?.grafico || dashData?.semana || [];
  const historico = dashData?.historico || [];
  const stats = dashData?.stats || {};
  
  const periodoLabels = {
    dia: 'Hoje',
    semana: '7 dias',
    mes: '30 dias',
    ano: '12 meses'
  };
  
  return (
    <div className="dashboard-premium" data-testid="dashboard-premium">
      {/* Header */}
      <div className="dashboard-header">
        <button className="back-btn" onClick={onClose} data-testid="back-btn">
          <ArrowLeft size={20} />
        </button>
        <h2>📊 Dashboard Premium</h2>
        <div className="user-badge">{user.nome}</div>
      </div>
      
      {/* Seletor de Período */}
      <div className="periodo-selector" data-testid="periodo-selector">
        {['dia', 'semana', 'mes', 'ano'].map(p => (
          <button 
            key={p}
            className={periodo === p ? 'active' : ''} 
            onClick={() => setPeriodo(p)}
            data-testid={`periodo-${p}`}
          >
            {periodoLabels[p]}
          </button>
        ))}
      </div>
      
      {/* Tabs */}
      <div className="dashboard-tabs">
        <button 
          className={activeTab === 'resumo' ? 'active' : ''} 
          onClick={() => setActiveTab('resumo')}
          data-testid="tab-resumo"
        >
          <TrendingUp size={16} /> Resumo
        </button>
        <button 
          className={activeTab === 'historico' ? 'active' : ''} 
          onClick={() => setActiveTab('historico')}
          data-testid="tab-historico"
        >
          <Calendar size={16} /> Histórico
        </button>
        <button 
          className={activeTab === 'metas' ? 'active' : ''} 
          onClick={() => setActiveTab('metas')}
          data-testid="tab-metas"
        >
          <Target size={16} /> Metas
        </button>
        <button 
          className={activeTab === 'relatorio' ? 'active' : ''} 
          onClick={() => setActiveTab('relatorio')}
          data-testid="tab-relatorio"
        >
          <FileText size={16} /> Relatorio
        </button>
      </div>
      
      {/* Conteúdo */}
      <div className="dashboard-content">
        {activeTab === 'resumo' && (
          <>
            {/* BLOCO 1 — Status Calórico */}
            {(() => {
              const calStatus = getCalorieStatus(hoje.calorias, metas.calorias);
              const barWidth = Math.min((hoje.calorias / (metas.calorias || 1)) * 100, 100);
              return (
                <div className="insight-card" data-testid="calorie-status">
                  <div className="insight-card-label">
                    <Flame size={14} color="#d4af37" />
                    <span>Calorias de Hoje</span>
                  </div>
                  <div className="insight-cal-row">
                    <span className="insight-cal-value">{hoje.calorias.toFixed(0)}</span>
                    <span className="insight-cal-unit"> kcal</span>
                    <span className="insight-cal-meta">/ {metas.calorias} meta</span>
                  </div>
                  <div className="insight-status-bar">
                    <div className="insight-status-fill" style={{ width: `${barWidth}%`, backgroundColor: calStatus.cor }} />
                  </div>
                  <span className="insight-status-badge" style={{ color: calStatus.cor }}>
                    {calStatus.emoji} {calStatus.texto}
                  </span>
                </div>
              );
            })()}

            {/* BLOCO 2 — Qualidade Nutricional */}
            <div className="insight-card" data-testid="macro-quality">
              <div className="insight-card-label">
                <Target size={14} color="#d4af37" />
                <span>Qualidade Nutricional</span>
              </div>
              <div className="macro-quality-grid">
                {[
                  { label: 'Proteína',     value: hoje.proteinas,    meta: metas.proteinas,    icon: '💪', unit: 'g' },
                  { label: 'Carboidratos', value: hoje.carboidratos, meta: metas.carboidratos, icon: '🍚', unit: 'g' },
                  { label: 'Gordura',      value: hoje.gorduras,     meta: metas.gorduras,     icon: '🫒', unit: 'g' },
                ].map(({ label, value, meta, icon, unit }) => {
                  const st = getMacroStatus(value, meta);
                  return (
                    <div key={label} className="macro-quality-row">
                      <span className="mq-icon">{icon}</span>
                      <span className="mq-label">{label}</span>
                      <span className="mq-val">{value.toFixed(0)}{unit}</span>
                      <span className="mq-status" style={{ color: st.cor }}>{st.icon} {st.label}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* BLOCO 3 — Alertas Inteligentes (deduplicados) */}
            {(() => {
              const alertas = dedupeAlertas(dashData?.alertas);
              return alertas.length > 0 ? (
                <div className="insight-card insight-card--alert" data-testid="smart-alerts">
                  <div className="insight-card-label">
                    <span style={{ fontSize: '13px' }}>⚠️</span>
                    <span>Alertas do Dia</span>
                  </div>
                  <ul className="insight-list">
                    {alertas.map((a, i) => (
                      <li key={i} className="insight-list-item insight-list-item--alert">
                        {a.msg || String(a)}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null;
            })()}

            {/* BLOCO 4 — Sugestões */}
            <div className="insight-card insight-card--sug" data-testid="suggestions">
              <div className="insight-card-label">
                <TrendingUp size={14} color="#d4af37" />
                <span>Sugestão para o Próximo Prato</span>
              </div>
              <ul className="insight-list">
                {getSugestoes(hoje, metas).map((s, i) => (
                  <li key={i} className="insight-list-item insight-list-item--sug">{s}</li>
                ))}
              </ul>
            </div>

            {/* Stats resumidos */}
            <div className="stats-mini-grid" data-testid="stats-mini">
              <div className="stats-mini-item">
                <Award size={18} color="#d4af37" />
                <span className="stats-mini-val">{stats.streak || 0}</span>
                <span className="stats-mini-lbl">Dias seguidos</span>
              </div>
              <div className="stats-mini-item">
                <Calendar size={18} color="#d4af37" />
                <span className="stats-mini-val">{stats.dias_registrados || 0}</span>
                <span className="stats-mini-lbl">Dias registrados</span>
              </div>
              <div className="stats-mini-item">
                <Flame size={18} color="#ef4444" />
                <span className="stats-mini-val">{stats.media_calorias?.toFixed(0) || 0}</span>
                <span className="stats-mini-lbl">Média kcal/dia</span>
              </div>
              <div className="stats-mini-item">
                <TrendingUp size={18} color="#10b981" />
                <span className="stats-mini-val">{stats.total_pratos || 0}</span>
                <span className="stats-mini-lbl">Pratos registrados</span>
              </div>
            </div>

            {/* Gráfico de tendência — mantido como referência secundária */}
            {grafico.length > 0 && (
              <div className="dashboard-card chart-card">
                <h3>📊 Tendência — {periodoLabels[periodo]}</h3>
                <div className="charts-grid">
                  <BarChart
                    data={grafico.map(d => ({ day: d.dia, value: d.calorias }))}
                    label="Calorias (kcal)"
                    color="#d4af37"
                    maxValue={metas.calorias * 1.2}
                  />
                  <BarChart
                    data={grafico.map(d => ({ day: d.dia, value: d.proteinas }))}
                    label="Proteínas (g)"
                    color="#ef4444"
                    maxValue={metas.proteinas * 1.5}
                  />
                </div>
              </div>
            )}
          </>
        )}
        
        {activeTab === 'historico' && (
          <div className="dashboard-card historico-card">
            <h3>📋 Histórico de Refeições</h3>
            {historico.length === 0 ? (
              <p className="empty-msg">Nenhuma refeição registrada ainda.</p>
            ) : (
              <div className="historico-list">
                {historico.map((item, i) => (
                  <div key={i} className="historico-item">
                    <div 
                      className="historico-header"
                      onClick={() => setExpandedDay(expandedDay === i ? null : i)}
                    >
                      <div className="historico-date">
                        {new Date(item.data + 'T12:00:00').toLocaleDateString('pt-BR', { 
                          weekday: 'short', 
                          day: '2-digit', 
                          month: 'short' 
                        })}
                      </div>
                      <div className="historico-summary">
                        <span className="kcal">{item.calorias_total?.toFixed(0)} kcal</span>
                        <span className="pratos">{item.pratos?.length || 0} pratos</span>
                      </div>
                      {expandedDay === i ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </div>
                    
                    {expandedDay === i && item.pratos?.length > 0 && (
                      <div className="historico-pratos">
                        {item.pratos.map((p, j) => (
                          <div key={j} className="historico-prato">
                            <span className="prato-nome">{p.nome}</span>
                            <span className="prato-info">
                              {p.calorias?.toFixed(0)} kcal • {p.proteinas?.toFixed(0)}g prot
                            </span>
                          </div>
                        ))}
                        <div className="historico-macros">
                          <span>P: {item.proteinas_total?.toFixed(0)}g</span>
                          <span>C: {item.carboidratos_total?.toFixed(0)}g</span>
                          <span>G: {item.gorduras_total?.toFixed(0)}g</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'metas' && (
          <div className="dashboard-card metas-card">
            <div className="metas-header">
              <h3>🎯 Suas Metas Diárias</h3>
              <button 
                className="btn-edit-metas"
                onClick={() => setShowMetasModal(true)}
                data-testid="edit-metas-btn"
              >
                <Edit3 size={16} /> Editar
              </button>
            </div>
            
            <div className="metas-grid">
              <div className="meta-card">
                <Flame size={24} color="#d4af37" />
                <span className="meta-value">{metas.calorias}</span>
                <span className="meta-unit">kcal</span>
                <span className="meta-label">Calorias</span>
              </div>
              <div className="meta-card">
                <Beef size={24} color="#ef4444" />
                <span className="meta-value">{metas.proteinas}</span>
                <span className="meta-unit">g</span>
                <span className="meta-label">Proteínas</span>
              </div>
              <div className="meta-card">
                <Wheat size={24} color="#d4af37" />
                <span className="meta-value">{metas.carboidratos}</span>
                <span className="meta-unit">g</span>
                <span className="meta-label">Carboidratos</span>
              </div>
              <div className="meta-card">
                <Droplets size={24} color="#10b981" />
                <span className="meta-value">{metas.gorduras}</span>
                <span className="meta-unit">g</span>
                <span className="meta-label">Gorduras</span>
              </div>
            </div>
            
            {/* Progresso vs Meta */}
            <div className="metas-progress-section">
              <h4>📊 Média do Período vs Meta</h4>
              <ProgressBar 
                value={stats.media_calorias || 0}
                max={metas.calorias}
                color="#d4af37"
                label="Calorias"
                unit=" kcal"
              />
              <ProgressBar 
                value={stats.media_proteinas || 0}
                max={metas.proteinas}
                color="#ef4444"
                label="Proteínas"
                unit="g"
              />
              <ProgressBar 
                value={stats.media_carboidratos || 0}
                max={metas.carboidratos}
                color="#d4af37"
                label="Carboidratos"
                unit="g"
              />
              <ProgressBar 
                value={stats.media_gorduras || 0}
                max={metas.gorduras}
                color="#10b981"
                label="Gorduras"
                unit="g"
              />
            </div>
            
            {/* Dica */}
            <div className="metas-tip">
              <strong>💡 Dica:</strong> Ajuste suas metas de acordo com seu objetivo. 
              Para perder peso, reduza as calorias em 15-20%. Para ganhar massa, aumente proteínas.
            </div>
          </div>
        )}

        {activeTab === 'relatorio' && (
          <div className="dashboard-card report-card" data-testid="report-section">
            {reportLoading ? (
              <div className="dashboard-loading"><div className="spinner"></div><p>Gerando relatorio...</p></div>
            ) : reportData ? (
              <>
                {/* Score de Dieta */}
                <div className="score-hero" data-testid="diet-score">
                  <div className="score-ring" style={{ '--score-color': reportData.classificacao.cor }}>
                    <span className="score-grade">{reportData.classificacao.emoji}</span>
                  </div>
                  <div className="score-number">{reportData.score}</div>
                  <div className="score-label">Score de Dieta</div>
                  <div className="score-text" style={{ color: reportData.classificacao.cor }}>
                    {reportData.classificacao.texto}
                  </div>
                </div>

                {/* Componentes do Score */}
                <div className="score-components" data-testid="score-components">
                  <h4>Composicao do Score</h4>
                  <div className="component-bars">
                    {[
                      { key: 'aderencia', label: 'Aderencia as metas', max: 40, color: '#d4af37' },
                      { key: 'consistencia', label: 'Consistencia', max: 20, color: '#e8d48b' },
                      { key: 'variedade', label: 'Variedade', max: 20, color: '#c5a028' },
                      { key: 'equilibrio', label: 'Equilibrio macro', max: 20, color: '#b8960f' }
                    ].map(comp => (
                      <div key={comp.key} className="comp-bar-item">
                        <div className="comp-bar-label">
                          <span>{comp.label}</span>
                          <span>{reportData.componentes[comp.key]}/{comp.max}</span>
                        </div>
                        <div className="comp-bar-bg">
                          <div 
                            className="comp-bar-fill"
                            style={{ 
                              width: `${(reportData.componentes[comp.key] / comp.max) * 100}%`,
                              backgroundColor: comp.color 
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Resumo Nutricional */}
                <div className="report-summary" data-testid="report-summary">
                  <h4>Resumo do Periodo ({periodoLabels[periodo]})</h4>
                  <div className="summary-grid">
                    <div className="summary-item">
                      <span className="summary-val">{reportData.resumo.dias_registrados}</span>
                      <span className="summary-lbl">Dias registrados</span>
                    </div>
                    <div className="summary-item">
                      <span className="summary-val">{reportData.resumo.streak}</span>
                      <span className="summary-lbl">Dias seguidos</span>
                    </div>
                    <div className="summary-item">
                      <span className="summary-val">{reportData.resumo.total_pratos}</span>
                      <span className="summary-lbl">Total pratos</span>
                    </div>
                    <div className="summary-item">
                      <span className="summary-val">{reportData.resumo.pratos_unicos}</span>
                      <span className="summary-lbl">Pratos unicos</span>
                    </div>
                  </div>
                </div>

                {/* Médias vs Metas */}
                <div className="report-macros" data-testid="report-macros">
                  <h4>Medias Diarias vs Metas</h4>
                  {[
                    { label: 'Calorias', media: reportData.resumo.media_calorias, meta: reportData.metas.calorias, unit: 'kcal', color: '#d4af37' },
                    { label: 'Proteinas', media: reportData.resumo.media_proteinas, meta: reportData.metas.proteinas, unit: 'g', color: '#e8d48b' },
                    { label: 'Carboidratos', media: reportData.resumo.media_carboidratos, meta: reportData.metas.carboidratos, unit: 'g', color: '#c5a028' },
                    { label: 'Gorduras', media: reportData.resumo.media_gorduras, meta: reportData.metas.gorduras, unit: 'g', color: '#b8960f' }
                  ].map(m => (
                    <div key={m.label} className="macro-compare">
                      <div className="macro-compare-label">
                        <span>{m.label}</span>
                        <span style={{ color: m.color }}>{m.media} / {m.meta} {m.unit}</span>
                      </div>
                      <div className="comp-bar-bg">
                        <div className="comp-bar-fill" style={{ 
                          width: `${Math.min((m.media / m.meta) * 100, 100)}%`, 
                          backgroundColor: m.color 
                        }} />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Distribuição Macro */}
                {reportData.resumo.distribuicao && (
                  <div className="report-dist">
                    <h4>Distribuicao Energetica</h4>
                    <div className="dist-bars">
                      <div className="dist-item">
                        <div className="dist-bar" style={{ width: `${reportData.resumo.distribuicao.proteinas_pct}%`, backgroundColor: '#e8d48b' }} />
                        <span>Prot {reportData.resumo.distribuicao.proteinas_pct}%</span>
                      </div>
                      <div className="dist-item">
                        <div className="dist-bar" style={{ width: `${reportData.resumo.distribuicao.carboidratos_pct}%`, backgroundColor: '#c5a028' }} />
                        <span>Carb {reportData.resumo.distribuicao.carboidratos_pct}%</span>
                      </div>
                      <div className="dist-item">
                        <div className="dist-bar" style={{ width: `${reportData.resumo.distribuicao.gorduras_pct}%`, backgroundColor: '#b8960f' }} />
                        <span>Gord {reportData.resumo.distribuicao.gorduras_pct}%</span>
                      </div>
                    </div>
                    <p className="dist-ideal">Ideal: Prot 15-25% | Carb 45-65% | Gord 20-35%</p>
                  </div>
                )}

                {/* Tabela Detalhada */}
                {reportData.detalhes?.length > 0 && (
                  <div className="report-table-section">
                    <h4>Detalhamento por Dia</h4>
                    <table className="report-table" data-testid="report-table">
                      <thead>
                        <tr>
                          <th>Data</th>
                          <th>Kcal</th>
                          <th>Prot</th>
                          <th>Carb</th>
                          <th>Gord</th>
                          <th>Pratos</th>
                        </tr>
                      </thead>
                      <tbody>
                        {reportData.detalhes.map((d, i) => (
                          <tr key={i}>
                            <td>{new Date(d.data + 'T12:00:00').toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}</td>
                            <td>{d.calorias}</td>
                            <td>{d.proteinas}g</td>
                            <td>{d.carboidratos}g</td>
                            <td>{d.gorduras}g</td>
                            <td>{d.pratos}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Botão Imprimir */}
                <button 
                  className="btn-print" 
                  onClick={() => window.print()}
                  data-testid="btn-print-report"
                >
                  <Printer size={16} /> Imprimir Relatorio
                </button>
              </>
            ) : (
              <div className="report-empty">
                <FileText size={48} color="#4a5568" />
                <p>Erro ao carregar relatorio.</p>
                <button className="btn-save" onClick={loadReport}>Tentar novamente</button>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Footer */}
      <div className="dashboard-footer">
        <p>Período: {periodoLabels[periodo]} • Última atualização: agora</p>
      </div>
      
      {/* Modal de Metas */}
      {showMetasModal && (
        <MetasModal 
          metas={metas}
          onSave={saveMetas}
          onClose={() => setShowMetasModal(false)}
        />
      )}
    </div>
  );
}
