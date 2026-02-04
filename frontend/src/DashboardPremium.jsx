import React, { useState, useEffect } from 'react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Componente de barra de progresso
const ProgressBar = ({ value, max, color, label }) => {
  const percent = Math.min((value / max) * 100, 100);
  return (
    <div className="progress-item">
      <div className="progress-label">
        <span>{label}</span>
        <span>{value.toFixed(0)} / {max} {label === 'Calorias' ? 'kcal' : 'g'}</span>
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

// Gráfico de barras simples
const BarChart = ({ data, label, color }) => {
  const maxValue = Math.max(...data.map(d => d.value), 1);
  
  return (
    <div className="bar-chart">
      <div className="bar-chart-label">{label}</div>
      <div className="bar-chart-bars">
        {data.map((d, i) => (
          <div key={i} className="bar-chart-item">
            <div 
              className="bar-chart-bar"
              style={{ 
                height: `${(d.value / maxValue) * 100}%`,
                backgroundColor: color 
              }}
            />
            <span className="bar-chart-day">{d.day}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default function DashboardPremium({ user, onClose }) {
  const [loading, setLoading] = useState(true);
  const [dashData, setDashData] = useState(null);
  const [periodo, setPeriodo] = useState('semana'); // semana, mes
  const [activeTab, setActiveTab] = useState('resumo'); // resumo, historico, metas
  
  useEffect(() => {
    loadDashboard();
  }, [periodo]);
  
  const loadDashboard = async () => {
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
  };
  
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
  
  const metas = user.meta_calorica || { calorias: 2000, proteinas: 50, carboidratos: 250, gorduras: 65 };
  const hoje = dashData?.hoje || { calorias: 0, proteinas: 0, carboidratos: 0, gorduras: 0 };
  const semana = dashData?.semana || [];
  const historico = dashData?.historico || [];
  
  return (
    <div className="dashboard-premium" data-testid="dashboard-premium">
      {/* Header */}
      <div className="dashboard-header">
        <button className="back-btn" onClick={onClose}>← Voltar</button>
        <h2>📊 Meu Dashboard</h2>
        <div className="periodo-selector">
          <button 
            className={periodo === 'semana' ? 'active' : ''} 
            onClick={() => setPeriodo('semana')}
          >
            7 dias
          </button>
          <button 
            className={periodo === 'mes' ? 'active' : ''} 
            onClick={() => setPeriodo('mes')}
          >
            30 dias
          </button>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="dashboard-tabs">
        <button 
          className={activeTab === 'resumo' ? 'active' : ''} 
          onClick={() => setActiveTab('resumo')}
        >
          📈 Resumo
        </button>
        <button 
          className={activeTab === 'historico' ? 'active' : ''} 
          onClick={() => setActiveTab('historico')}
        >
          📋 Histórico
        </button>
        <button 
          className={activeTab === 'metas' ? 'active' : ''} 
          onClick={() => setActiveTab('metas')}
        >
          🎯 Metas
        </button>
      </div>
      
      {/* Conteúdo */}
      <div className="dashboard-content">
        {activeTab === 'resumo' && (
          <>
            {/* Card Hoje */}
            <div className="dashboard-card">
              <h3>🍽️ Consumo de Hoje</h3>
              <div className="macro-grid">
                <ProgressBar 
                  value={hoje.calorias} 
                  max={metas.calorias} 
                  color="#f59e0b" 
                  label="Calorias" 
                />
                <ProgressBar 
                  value={hoje.proteinas} 
                  max={metas.proteinas} 
                  color="#ef4444" 
                  label="Proteínas" 
                />
                <ProgressBar 
                  value={hoje.carboidratos} 
                  max={metas.carboidratos} 
                  color="#3b82f6" 
                  label="Carboidratos" 
                />
                <ProgressBar 
                  value={hoje.gorduras} 
                  max={metas.gorduras} 
                  color="#10b981" 
                  label="Gorduras" 
                />
              </div>
            </div>
            
            {/* Gráficos Semanais */}
            <div className="dashboard-card">
              <h3>📊 Últimos {periodo === 'semana' ? '7' : '30'} dias</h3>
              <div className="charts-grid">
                <BarChart 
                  data={semana.map(d => ({ day: d.dia, value: d.calorias }))} 
                  label="Calorias" 
                  color="#f59e0b" 
                />
                <BarChart 
                  data={semana.map(d => ({ day: d.dia, value: d.proteinas }))} 
                  label="Proteínas" 
                  color="#ef4444" 
                />
              </div>
            </div>
            
            {/* Estatísticas */}
            <div className="dashboard-card stats-card">
              <h3>📈 Estatísticas do Período</h3>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-value">{dashData?.stats?.dias_registrados || 0}</span>
                  <span className="stat-label">Dias registrados</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{dashData?.stats?.media_calorias?.toFixed(0) || 0}</span>
                  <span className="stat-label">Média kcal/dia</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{dashData?.stats?.total_pratos || 0}</span>
                  <span className="stat-label">Pratos consumidos</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{dashData?.stats?.streak || 0}</span>
                  <span className="stat-label">Dias seguidos</span>
                </div>
              </div>
            </div>
          </>
        )}
        
        {activeTab === 'historico' && (
          <div className="dashboard-card historico-card">
            <h3>📋 Histórico de Refeições</h3>
            {historico.length === 0 ? (
              <p className="empty-msg">Nenhuma refeição registrada ainda. Use o app para identificar pratos!</p>
            ) : (
              <div className="historico-list">
                {historico.map((item, i) => (
                  <div key={i} className="historico-item">
                    <div className="historico-date">{item.data}</div>
                    <div className="historico-pratos">
                      {item.pratos?.map((p, j) => (
                        <div key={j} className="historico-prato">
                          <span className="prato-nome">{p.nome}</span>
                          <span className="prato-calorias">{p.calorias?.toFixed(0)} kcal</span>
                        </div>
                      ))}
                    </div>
                    <div className="historico-total">
                      Total: {item.calorias_total?.toFixed(0)} kcal
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'metas' && (
          <div className="dashboard-card metas-card">
            <h3>🎯 Suas Metas Diárias</h3>
            <div className="metas-info">
              <p>Baseado no seu perfil:</p>
              <ul>
                <li><strong>Objetivo:</strong> {user.objetivo === 'perder' ? 'Perder peso' : user.objetivo === 'ganhar' ? 'Ganhar massa' : 'Manter peso'}</li>
                <li><strong>Nível de atividade:</strong> {user.nivel_atividade}</li>
                <li><strong>TMB estimada:</strong> {metas.tmb?.toFixed(0) || '?'} kcal</li>
              </ul>
            </div>
            
            <div className="metas-grid">
              <div className="meta-item">
                <div className="meta-icon">🔥</div>
                <div className="meta-value">{metas.calorias} kcal</div>
                <div className="meta-label">Meta calórica</div>
              </div>
              <div className="meta-item">
                <div className="meta-icon">💪</div>
                <div className="meta-value">{metas.proteinas}g</div>
                <div className="meta-label">Proteínas</div>
              </div>
              <div className="meta-item">
                <div className="meta-icon">🍞</div>
                <div className="meta-value">{metas.carboidratos}g</div>
                <div className="meta-label">Carboidratos</div>
              </div>
              <div className="meta-item">
                <div className="meta-icon">🥑</div>
                <div className="meta-value">{metas.gorduras}g</div>
                <div className="meta-label">Gorduras</div>
              </div>
            </div>
            
            {/* Alertas */}
            <div className="alertas-section">
              <h4>⚠️ Alertas da Semana</h4>
              {dashData?.alertas?.length > 0 ? (
                <ul className="alertas-list">
                  {dashData.alertas.map((a, i) => (
                    <li key={i} className={`alerta-item ${a.tipo}`}>{a.msg}</li>
                  ))}
                </ul>
              ) : (
                <p className="no-alertas">Nenhum alerta. Continue assim! 🎉</p>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Footer com info */}
      <div className="dashboard-footer">
        <p>Dados atualizados em tempo real • {user.nome}</p>
      </div>
    </div>
  );
}
