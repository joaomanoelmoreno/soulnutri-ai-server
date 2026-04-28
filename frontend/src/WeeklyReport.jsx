import React, { useState, useEffect } from 'react';
import './WeeklyReport.css';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// 🔒 Render-safe para JSX: garante que NUNCA renderizamos um objeto direto (React error #31)
// Aceita string/number normalmente; se for objeto, extrai 'texto'/'text'/'titulo'/etc.
const renderTextSafe = (v) => {
  if (v === null || v === undefined) return '';
  if (typeof v === 'string' || typeof v === 'number') return String(v);
  if (Array.isArray(v)) return v.map(renderTextSafe).filter(Boolean).join(', ');
  if (typeof v === 'object') {
    return v.texto || v.text || v.titulo || v.title || v.mensagem || v.message || v.descricao || v.nome || '';
  }
  return '';
};

const MACRO_STATUS_ICONS = {
  ok: { icon: '✓', color: '#22c55e', label: 'Adequado' },
  excesso: { icon: '↑', color: '#f59e0b', label: 'Excesso' },
  deficit: { icon: '↓', color: '#ef4444', label: 'Deficit' }
};

export default function WeeklyReport({ pin, onClose }) {
  const [report, setReport] = useState(null);
  const [achievements, setAchievements] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('report');

  useEffect(() => {
    if (!pin) return;
    loadData();
  }, [pin]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [reportRes, achieveRes] = await Promise.all([
        fetch(`${API}/premium/weekly-report-ai?pin=${pin}`),
        fetch(`${API}/premium/achievements?pin=${pin}`)
      ]);
      
      const reportData = await reportRes.json();
      const achieveData = await achieveRes.json();
      
      if (reportData.ok) setReport(reportData);
      if (achieveData.ok) setAchievements(achieveData);
    } catch (e) {
      console.error('Erro:', e);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="wr-container" data-testid="weekly-report">
        <div className="wr-loading">
          <div className="wr-spinner"></div>
          <p>Preparando seu relatorio...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="wr-container" data-testid="weekly-report">
      {/* Header */}
      <div className="wr-header">
        <button className="wr-back" onClick={onClose} data-testid="report-back-btn">← Voltar</button>
        <h2 className="wr-title">Relatorio Semanal</h2>
        <p className="wr-subtitle">{report?.nome || 'Premium'}</p>
      </div>

      {/* Tabs */}
      <div className="wr-tabs">
        <button
          className={`wr-tab ${activeTab === 'report' ? 'active' : ''}`}
          onClick={() => setActiveTab('report')}
          data-testid="tab-report"
        >
          📊 Relatorio
        </button>
        <button
          className={`wr-tab ${activeTab === 'achievements' ? 'active' : ''}`}
          onClick={() => setActiveTab('achievements')}
          data-testid="tab-achievements"
        >
          🏆 Conquistas
        </button>
      </div>

      {/* Tab Content */}
      <div className="wr-content">
        {activeTab === 'report' ? (
          <ReportTab report={report} />
        ) : (
          <AchievementsTab achievements={achievements} />
        )}
      </div>
    </div>
  );
}

function ReportTab({ report }) {
  if (!report || !report.has_data) {
    return (
      <div className="wr-empty">
        <div className="wr-empty-icon">📝</div>
        <h3>Sem dados esta semana</h3>
        <p>Registre suas refeicoes para receber um relatorio personalizado!</p>
      </div>
    );
  }

  const ai = report.ai_report || {};
  const medias = report.medias || {};
  const metas = report.metas || {};

  return (
    <div className="wr-report">
      {/* Grade Card */}
      <div className="wr-grade-card" data-testid="report-grade">
        <div className="wr-grade-badge">{renderTextSafe(ai.nota_geral) || 'B'}</div>
        <h3 className="wr-grade-title">{renderTextSafe(ai.titulo) || 'Resumo da Semana'}</h3>
        <p className="wr-grade-period">{renderTextSafe(report.periodo)} | {renderTextSafe(report.dias_registrados)} dias registrados</p>
      </div>

      {/* Macros Overview */}
      <div className="wr-section">
        <h4 className="wr-section-title">Macronutrientes (media diaria)</h4>
        <div className="wr-macros-grid">
          {['calorias', 'proteinas', 'carboidratos', 'gorduras'].map(macro => {
            const analise = ai.analise_macros?.[macro] || {};
            const status = MACRO_STATUS_ICONS[analise.status] || MACRO_STATUS_ICONS.ok;
            const units = macro === 'calorias' ? 'kcal' : 'g';
            
            return (
              <div key={macro} className="wr-macro-card" data-testid={`macro-${macro}`}>
                <div className="wr-macro-header">
                  <span className="wr-macro-name">{macro.charAt(0).toUpperCase() + macro.slice(1)}</span>
                  <span className="wr-macro-status" style={{ color: status.color }}>
                    {status.icon} {status.label}
                  </span>
                </div>
                <div className="wr-macro-values">
                  <span className="wr-macro-current">{medias[macro] || 0}{units}</span>
                  <span className="wr-macro-meta">meta: {metas[macro] || '—'}{units}</span>
                </div>
                <div className="wr-macro-bar">
                  <div 
                    className="wr-macro-bar-fill"
                    style={{ 
                      width: `${Math.min((medias[macro] / (metas[macro] || 1)) * 100, 120)}%`,
                      backgroundColor: status.color
                    }}
                  />
                </div>
                {analise.detalhe && <p className="wr-macro-detail">{renderTextSafe(analise.detalhe)}</p>}
              </div>
            );
          })}
        </div>
      </div>

      {/* Positive Points */}
      {ai.pontos_positivos && ai.pontos_positivos.length > 0 && (
        <div className="wr-section">
          <h4 className="wr-section-title">Pontos Positivos</h4>
          <div className="wr-list-positive">
            {ai.pontos_positivos.map((p, i) => (
              <div key={i} className="wr-list-item positive">{renderTextSafe(p)}</div>
            ))}
          </div>
        </div>
      )}

      {/* Alerts */}
      {ai.alertas && ai.alertas.length > 0 && (
        <div className="wr-section">
          <h4 className="wr-section-title">Pontos de Atencao</h4>
          <div className="wr-list-alerts">
            {ai.alertas.map((a, i) => (
              <div key={i} className="wr-list-item alert">{renderTextSafe(a)}</div>
            ))}
          </div>
        </div>
      )}

      {/* Tips */}
      {ai.dicas && ai.dicas.length > 0 && (
        <div className="wr-section">
          <h4 className="wr-section-title">Dicas para Voce</h4>
          <div className="wr-list-tips">
            {ai.dicas.map((d, i) => (
              <div key={i} className="wr-list-item tip">{renderTextSafe(d)}</div>
            ))}
          </div>
        </div>
      )}

      {/* Curiosity */}
      {ai.curiosidade && (
        <div className="wr-curiosity" data-testid="report-curiosity">
          <span className="wr-curiosity-icon">💡</span>
          <p>{ai.curiosidade}</p>
        </div>
      )}

      {/* Motivational */}
      {ai.mensagem_motivacional && (
        <div className="wr-motivational" data-testid="report-motivation">
          <p>{ai.mensagem_motivacional}</p>
        </div>
      )}

      {/* Stats */}
      <div className="wr-footer-stats">
        <span>{report.pratos_unicos} pratos diferentes</span>
        <span>{report.total_pratos} refeicoes</span>
      </div>
    </div>
  );
}

function AchievementsTab({ achievements }) {
  if (!achievements) {
    return (
      <div className="wr-empty">
        <div className="wr-empty-icon">🏆</div>
        <h3>Carregando conquistas...</h3>
      </div>
    );
  }

  const level = achievements.level || {};
  const messages = achievements.motivational_messages || [];
  const unlocked = achievements.badges_unlocked || [];
  const locked = achievements.badges_locked || [];
  const next = achievements.next_badge;

  return (
    <div className="wr-achievements">
      {/* Level Card */}
      <div className="wr-level-card" data-testid="level-card">
        <div className="wr-level-badge" style={{ borderColor: level.cor }}>
          <span className="wr-level-num">{level.nivel}</span>
        </div>
        <div className="wr-level-info">
          <h3 style={{ color: level.cor }}>{renderTextSafe(level.nome)}</h3>
          <p>{renderTextSafe(level.xp)} XP</p>
          <div className="wr-level-bar">
            <div 
              className="wr-level-bar-fill"
              style={{ width: `${level.progresso * 100}%`, backgroundColor: level.cor }}
            />
          </div>
          <span className="wr-level-next">Proximo: {renderTextSafe(level.proximo_nivel)}</span>
        </div>
      </div>

      {/* Streak */}
      <div className="wr-streak" data-testid="streak-display">
        <span className="wr-streak-fire">🔥</span>
        <span className="wr-streak-count">{achievements.streak}</span>
        <span className="wr-streak-label">dias seguidos</span>
      </div>

      {/* Motivational Message */}
      {messages.length > 0 && (
        <div className="wr-motivation-card">
          {messages.map((msg, i) => (
            <p key={i}>{renderTextSafe(msg)}</p>
          ))}
        </div>
      )}

      {/* Next Badge */}
      {next && (
        <div className="wr-next-badge">
          <span className="wr-next-label">Proxima conquista:</span>
          <div className="wr-badge-preview">
            <div className="wr-badge-icon-locked">🔒</div>
            <div>
              <strong>{renderTextSafe(next.nome)}</strong>
              <p>{renderTextSafe(next.descricao)}</p>
              <div className="wr-badge-progress-bar">
                <div 
                  className="wr-badge-progress-fill"
                  style={{ width: `${next.progress * 100}%` }}
                />
              </div>
              <span className="wr-badge-progress-text">{Math.round(next.progress * 100)}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Unlocked Badges */}
      {unlocked.length > 0 && (
        <div className="wr-badges-section">
          <h4>Conquistas Desbloqueadas ({unlocked.length}/{achievements.total_possible})</h4>
          <div className="wr-badges-grid">
            {unlocked.map(badge => (
              <div key={badge.id} className="wr-badge unlocked" style={{ borderColor: badge.cor }}>
                <span className="wr-badge-icon" style={{ color: badge.cor }}>⭐</span>
                <span className="wr-badge-name">{renderTextSafe(badge.nome)}</span>
                <span className="wr-badge-desc">{renderTextSafe(badge.descricao)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Locked Badges */}
      {locked.length > 0 && (
        <div className="wr-badges-section">
          <h4>A Desbloquear</h4>
          <div className="wr-badges-grid">
            {locked.map(badge => (
              <div key={badge.id} className="wr-badge locked">
                <span className="wr-badge-icon">🔒</span>
                <span className="wr-badge-name">{renderTextSafe(badge.nome)}</span>
                <span className="wr-badge-desc">{renderTextSafe(badge.descricao)}</span>
                <div className="wr-badge-mini-bar">
                  <div style={{ width: `${badge.progress * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
