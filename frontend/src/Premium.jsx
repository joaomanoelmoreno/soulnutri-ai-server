import React, { useState, useEffect } from 'react';
import './Premium.css';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Componente de Registro
export function PremiumRegister({ onSuccess, onCancel }) {
  const [form, setForm] = useState({
    pin: '', nome: '', peso: '', altura: '', idade: '', sexo: 'M',
    nivel_atividade: 'moderado', objetivo: 'manter', alergias: '', restricoes: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const fd = new FormData();
    Object.keys(form).forEach(key => {
      if (key === 'restricoes') {
        fd.append(key, form[key].join(','));
      } else {
        fd.append(key, form[key]);
      }
    });

    try {
      const res = await fetch(`${API}/premium/register`, { method: 'POST', body: fd });
      const data = await res.json();
      if (data.ok) {
        localStorage.setItem('soulnutri_pin', form.pin);
        localStorage.setItem('soulnutri_user', JSON.stringify(data));
        onSuccess(data);
      } else {
        setError(data.error);
      }
    } catch (e) {
      setError('Erro de conexão');
    }
    setLoading(false);
  };

  const toggleRestricao = (r) => {
    setForm(f => ({
      ...f,
      restricoes: f.restricoes.includes(r) 
        ? f.restricoes.filter(x => x !== r)
        : [...f.restricoes, r]
    }));
  };

  return (
    <div className="premium-form" data-testid="premium-register">
      <h2>🌟 SoulNutri Premium</h2>
      <p className="subtitle">Crie seu perfil nutricional</p>
      
      {/* Disclaimer Jurídico */}
      <div style={{
        background: 'rgba(59, 130, 246, 0.1)',
        border: '1px solid rgba(59, 130, 246, 0.3)',
        borderRadius: '8px',
        padding: '10px 12px',
        marginBottom: '16px',
        fontSize: '11px',
        color: '#93c5fd',
        lineHeight: '1.5'
      }}>
        <strong>⚠️ Aviso:</strong> As informações fornecidas pelo SoulNutri são de caráter educativo e informativo. 
        Este aplicativo <strong>não substitui</strong> orientação médica, nutricional ou de outro profissional de saúde. 
        Consulte sempre um especialista para dietas específicas ou condições de saúde.
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>PIN de Acesso (4-6 dígitos)</label>
          <input 
            type="password" 
            inputMode="numeric"
            maxLength={6}
            placeholder="••••••"
            value={form.pin}
            onChange={e => setForm({...form, pin: e.target.value.replace(/\D/g, '')})}
            required
          />
        </div>

        <div className="form-group">
          <label>Seu nome</label>
          <input 
            type="text" 
            placeholder="Como quer ser chamado?"
            value={form.nome}
            onChange={e => setForm({...form, nome: e.target.value})}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Peso (kg)</label>
            <input 
              type="number" 
              placeholder="75"
              value={form.peso}
              onChange={e => setForm({...form, peso: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <label>Altura (cm)</label>
            <input 
              type="number" 
              placeholder="175"
              value={form.altura}
              onChange={e => setForm({...form, altura: e.target.value})}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Idade</label>
            <input 
              type="number" 
              placeholder="35"
              value={form.idade}
              onChange={e => setForm({...form, idade: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <label>Sexo</label>
            <select value={form.sexo} onChange={e => setForm({...form, sexo: e.target.value})}>
              <option value="M">Masculino</option>
              <option value="F">Feminino</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Nível de Atividade</label>
          <select value={form.nivel_atividade} onChange={e => setForm({...form, nivel_atividade: e.target.value})}>
            <option value="sedentario">Sedentário (pouco exercício)</option>
            <option value="leve">Leve (1-3 dias/semana)</option>
            <option value="moderado">Moderado (3-5 dias/semana)</option>
            <option value="intenso">Intenso (6-7 dias/semana)</option>
            <option value="muito_intenso">Muito intenso (atleta)</option>
          </select>
        </div>

        <div className="form-group">
          <label>Objetivo</label>
          <div className="objetivo-btns">
            {[
              { value: 'perder', label: '📉 Perder peso', color: '#ef4444' },
              { value: 'manter', label: '⚖️ Manter', color: '#3b82f6' },
              { value: 'ganhar', label: '📈 Ganhar massa', color: '#22c55e' }
            ].map(obj => (
              <button
                key={obj.value}
                type="button"
                className={`objetivo-btn ${form.objetivo === obj.value ? 'active' : ''}`}
                style={{ '--accent': obj.color }}
                onClick={() => setForm({...form, objetivo: obj.value})}
              >
                {obj.label}
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>Restrições Alimentares</label>
          <div className="restricoes-grid">
            {[
              { value: 'vegano', label: '🌱 Vegano' },
              { value: 'vegetariano', label: '🥬 Vegetariano' },
              { value: 'sem_gluten', label: '🌾 Sem glúten' },
              { value: 'sem_lactose', label: '🥛 Sem lactose' },
              { value: 'sem_ovo', label: '🥚 Sem ovo' },
              { value: 'sem_frutos_mar', label: '🦐 Sem frutos do mar' },
              { value: 'sem_oleaginosas', label: '🥜 Sem oleaginosas' },
              { value: 'sem_soja', label: '🫘 Sem soja' },
              { value: 'low_carb', label: '🍞 Low carb' },
              { value: 'sem_acucar', label: '🍬 Sem açúcar' }
            ].map(r => (
              <button
                key={r.value}
                type="button"
                className={`restricao-btn ${form.restricoes.includes(r.value) ? 'active' : ''}`}
                onClick={() => toggleRestricao(r.value)}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>Alergias Alimentares</label>
          <div className="restricoes-grid">
            {[
              { value: 'alergia_amendoim', label: '🥜 Amendoim' },
              { value: 'alergia_castanhas', label: '🌰 Castanhas' },
              { value: 'alergia_leite', label: '🥛 Leite/Laticínios' },
              { value: 'alergia_ovo', label: '🥚 Ovo' },
              { value: 'alergia_trigo', label: '🌾 Trigo' },
              { value: 'alergia_peixe', label: '🐟 Peixe' },
              { value: 'alergia_camarao', label: '🦐 Camarão/Crustáceos' },
              { value: 'alergia_soja', label: '🫘 Soja' }
            ].map(r => (
              <button
                key={r.value}
                type="button"
                className={`restricao-btn alergia ${form.restricoes.includes(r.value) ? 'active' : ''}`}
                onClick={() => toggleRestricao(r.value)}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        {error && <div className="error-msg">{error}</div>}

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? '⏳ Criando...' : '✨ Criar Perfil'}
        </button>
        
        <button type="button" className="cancel-btn" onClick={onCancel}>
          ← Voltar
        </button>
      </form>
    </div>
  );
}

// Componente de Edição de Perfil
export function PremiumEditProfile({ onSuccess, onCancel }) {
  const [form, setForm] = useState({
    peso: '', altura: '', idade: '', sexo: 'M',
    nivel_atividade: 'moderado', objetivo: 'manter', restricoes: []
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Carregar dados do perfil atual
  useEffect(() => {
    const loadProfile = async () => {
      const pin = localStorage.getItem('soulnutri_pin');
      const nome = localStorage.getItem('soulnutri_nome');
      
      if (!pin || !nome) {
        setError('Sessão expirada. Faça login novamente.');
        setLoading(false);
        return;
      }
      
      try {
        const res = await fetch(`${API}/premium/get-profile?pin=${pin}&nome=${encodeURIComponent(nome)}`);
        const data = await res.json();
        
        if (data.ok) {
          const profile = data.profile;
          setForm({
            peso: profile.peso || '',
            altura: profile.altura || '',
            idade: profile.idade || '',
            sexo: profile.sexo || 'M',
            nivel_atividade: profile.nivel_atividade || 'moderado',
            objetivo: profile.objetivo || 'manter',
            restricoes: profile.restricoes || []
          });
        } else {
          setError(data.error || 'Erro ao carregar perfil');
        }
      } catch (e) {
        setError('Erro de conexão');
      }
      setLoading(false);
    };
    
    loadProfile();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    const pin = localStorage.getItem('soulnutri_pin');
    const nome = localStorage.getItem('soulnutri_nome');

    const fd = new FormData();
    fd.append('pin', pin);
    fd.append('nome', nome);
    fd.append('peso', form.peso);
    fd.append('altura', form.altura);
    fd.append('idade', form.idade);
    fd.append('sexo', form.sexo);
    fd.append('nivel_atividade', form.nivel_atividade);
    fd.append('objetivo', form.objetivo);
    fd.append('restricoes', form.restricoes.join(','));

    try {
      const res = await fetch(`${API}/premium/update-profile`, { method: 'POST', body: fd });
      const data = await res.json();
      if (data.ok) {
        onSuccess(data);
      } else {
        setError(data.error);
      }
    } catch (e) {
      setError('Erro de conexão');
    }
    setSaving(false);
  };

  const toggleRestricao = (r) => {
    setForm(f => ({
      ...f,
      restricoes: f.restricoes.includes(r) 
        ? f.restricoes.filter(x => x !== r)
        : [...f.restricoes, r]
    }));
  };

  if (loading) return <div className="loading">Carregando perfil...</div>;

  return (
    <div className="premium-form" data-testid="premium-edit">
      <h2>✏️ Editar Perfil</h2>
      <p className="subtitle">Atualize suas informações</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Peso (kg)</label>
            <input 
              type="number" 
              placeholder="75"
              value={form.peso}
              onChange={e => setForm({...form, peso: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <label>Altura (cm)</label>
            <input 
              type="number" 
              placeholder="175"
              value={form.altura}
              onChange={e => setForm({...form, altura: e.target.value})}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Idade</label>
            <input 
              type="number" 
              placeholder="35"
              value={form.idade}
              onChange={e => setForm({...form, idade: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <label>Sexo</label>
            <select value={form.sexo} onChange={e => setForm({...form, sexo: e.target.value})}>
              <option value="M">Masculino</option>
              <option value="F">Feminino</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Nível de Atividade</label>
          <select value={form.nivel_atividade} onChange={e => setForm({...form, nivel_atividade: e.target.value})}>
            <option value="sedentario">Sedentário (pouco exercício)</option>
            <option value="leve">Leve (1-3 dias/semana)</option>
            <option value="moderado">Moderado (3-5 dias/semana)</option>
            <option value="intenso">Intenso (6-7 dias/semana)</option>
            <option value="muito_intenso">Muito intenso (atleta)</option>
          </select>
        </div>

        <div className="form-group">
          <label>Objetivo</label>
          <div className="objetivo-btns">
            {[
              { value: 'perder', label: '📉 Perder peso', color: '#ef4444' },
              { value: 'manter', label: '⚖️ Manter', color: '#3b82f6' },
              { value: 'ganhar', label: '📈 Ganhar massa', color: '#22c55e' }
            ].map(obj => (
              <button
                key={obj.value}
                type="button"
                className={`objetivo-btn ${form.objetivo === obj.value ? 'active' : ''}`}
                style={{ '--accent': obj.color }}
                onClick={() => setForm({...form, objetivo: obj.value})}
              >
                {obj.label}
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>Restrições Alimentares</label>
          <div className="restricoes-grid">
            {[
              { value: 'vegano', label: '🌱 Vegano' },
              { value: 'vegetariano', label: '🥬 Vegetariano' },
              { value: 'sem_gluten', label: '🌾 Sem glúten' },
              { value: 'sem_lactose', label: '🥛 Sem lactose' },
              { value: 'sem_ovo', label: '🥚 Sem ovo' },
              { value: 'sem_frutos_mar', label: '🦐 Sem frutos do mar' },
              { value: 'sem_oleaginosas', label: '🥜 Sem oleaginosas' },
              { value: 'sem_soja', label: '🫘 Sem soja' },
              { value: 'low_carb', label: '🍞 Low carb' },
              { value: 'sem_acucar', label: '🍬 Sem açúcar' }
            ].map(r => (
              <button
                key={r.value}
                type="button"
                className={`restricao-btn ${form.restricoes.includes(r.value) ? 'active' : ''}`}
                onClick={() => toggleRestricao(r.value)}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        {error && <div className="error-msg">{error}</div>}

        <button type="submit" className="submit-btn" disabled={saving}>
          {saving ? '⏳ Salvando...' : '💾 Salvar Alterações'}
        </button>
        
        <button type="button" className="cancel-btn" onClick={onCancel}>
          ← Voltar
        </button>
      </form>
    </div>
  );
}

// Componente de Login
export function PremiumLogin({ onSuccess, onRegister, onCancel }) {
  const [nome, setNome] = useState('');
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const fd = new FormData();
      fd.append('nome', nome);
      fd.append('pin', pin);
      const res = await fetch(`${API}/premium/login`, { method: 'POST', body: fd });
      const data = await res.json();
      
      if (data.ok) {
        localStorage.setItem('soulnutri_pin', pin);
        localStorage.setItem('soulnutri_nome', nome);
        localStorage.setItem('soulnutri_user', JSON.stringify(data.user));
        onSuccess(data);
      } else {
        setError(data.error);
      }
    } catch (e) {
      setError('Erro de conexão');
    }
    setLoading(false);
  };

  return (
    <div className="premium-form login" data-testid="premium-login">
      <h2>🔐 Entrar</h2>
      <p className="subtitle">Digite seu nome e PIN</p>
      
      <form onSubmit={handleLogin}>
        <div className="form-group">
          <label>Seu nome</label>
          <input 
            type="text"
            placeholder="Como você se cadastrou?"
            value={nome}
            onChange={e => setNome(e.target.value)}
            autoFocus
          />
        </div>
        
        <div className="form-group">
          <label>PIN</label>
          <input 
            type="password"
            inputMode="numeric"
            maxLength={6}
            placeholder="••••••"
            value={pin}
            onChange={e => setPin(e.target.value.replace(/\D/g, ''))}
            className="pin-input-small"
          />
        </div>

        {error && <div className="error-msg">{error}</div>}

        <button type="submit" className="submit-btn" disabled={loading || pin.length < 4 || !nome.trim()}>
          {loading ? '⏳' : '→'} Entrar
        </button>
      </form>

      <div className="login-footer">
        <p>Não tem conta?</p>
        <button className="register-link" onClick={onRegister}>
          Criar perfil Premium
        </button>
        <button className="cancel-btn" onClick={onCancel}>
          Voltar
        </button>
      </div>
    </div>
  );
}

// Componente do Contador Diário - EXPANDIDO
export function DailyCounter({ user, onLogout, onClose, onEditProfile }) {
  const [summary, setSummary] = useState(null);
  const [fullAnalysis, setFullAnalysis] = useState(null);
  const [weeklyAnalysis, setWeeklyAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('hoje'); // 'hoje', 'semana' ou 'perfil'
  const [userProfile, setUserProfile] = useState(null);

  const loadData = async () => {
    const pin = localStorage.getItem('soulnutri_pin');
    try {
      // Carregar resumo básico
      const res = await fetch(`${API}/premium/daily-summary?pin=${pin}`);
      const data = await res.json();
      if (data.ok) setSummary(data);
      
      // Carregar análise completa do dia
      const resFull = await fetch(`${API}/premium/daily-full?pin=${pin}`);
      const dataFull = await resFull.json();
      if (dataFull.ok) setFullAnalysis(dataFull.analise);
      
      // Carregar análise semanal
      const resWeek = await fetch(`${API}/premium/weekly-analysis?pin=${pin}`);
      const dataWeek = await resWeek.json();
      if (dataWeek.ok) setWeeklyAnalysis(dataWeek.analise);
      
    } catch (e) {
      console.error('Erro ao carregar dados:', e);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <div className="loading">Carregando...</div>;

  const percentual = summary?.percentual || 0;
  const progressColor = percentual >= 100 ? '#ef4444' : percentual >= 75 ? '#f59e0b' : '#22c55e';

  return (
    <div className="daily-counter expanded" data-testid="daily-counter">
      <div className="counter-header">
        <h3>👋 Olá, {summary?.nome}</h3>
        <button className="logout-btn" onClick={onLogout}>Sair</button>
      </div>

      {/* Toggle Hoje/Semana/Perfil */}
      <div className="view-toggle-tabs" style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '16px',
        justifyContent: 'center',
        flexWrap: 'wrap'
      }}>
        <button 
          className={`tab-btn ${activeView === 'hoje' ? 'active' : ''}`}
          onClick={() => setActiveView('hoje')}
          style={{
            padding: '8px 16px',
            border: 'none',
            borderRadius: '20px',
            background: activeView === 'hoje' ? '#22c55e' : '#333',
            color: '#fff',
            fontWeight: 'bold',
            cursor: 'pointer',
            fontSize: '13px'
          }}
        >
          📅 Hoje
        </button>
        <button 
          className={`tab-btn ${activeView === 'semana' ? 'active' : ''}`}
          onClick={() => setActiveView('semana')}
          style={{
            padding: '8px 16px',
            border: 'none',
            borderRadius: '20px',
            background: activeView === 'semana' ? '#3b82f6' : '#333',
            color: '#fff',
            fontWeight: 'bold',
            cursor: 'pointer',
            fontSize: '13px'
          }}
        >
          📊 Semana
        </button>
        <button 
          className={`tab-btn ${activeView === 'perfil' ? 'active' : ''}`}
          onClick={() => setActiveView('perfil')}
          style={{
            padding: '8px 16px',
            border: 'none',
            borderRadius: '20px',
            background: activeView === 'perfil' ? '#f59e0b' : '#333',
            color: '#fff',
            fontWeight: 'bold',
            cursor: 'pointer',
            fontSize: '13px'
          }}
        >
          👤 Perfil
        </button>
      </div>

      {activeView === 'hoje' && (
        <>
          {/* Anel de Calorias */}
          <div className="calorie-ring">
            <svg viewBox="0 0 100 100">
              <circle className="ring-bg" cx="50" cy="50" r="45" />
              <circle 
                className="ring-progress" 
                cx="50" cy="50" r="45"
                style={{
                  strokeDasharray: `${Math.min(percentual, 100) * 2.83} 283`,
                  stroke: progressColor
                }}
              />
            </svg>
            <div className="ring-content">
              <span className="consumed">{summary?.consumido?.toFixed(0) || 0}</span>
              <span className="label">kcal</span>
              <span className="meta">de {summary?.meta?.toFixed(0)} kcal</span>
            </div>
          </div>

          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${Math.min(percentual, 100)}%`, background: progressColor }}
            />
          </div>
          <p className="progress-text" style={{ color: progressColor }}>
            {percentual >= 100 
              ? '🚨 Meta atingida!' 
              : `Restam ${summary?.restante?.toFixed(0)} kcal`}
          </p>

          {/* Macros */}
          <div className="macro-grid">
            <div className="macro-item">
              <span className="macro-value">{summary?.totais?.proteinas?.toFixed(0) || 0}g</span>
              <span className="macro-label">Proteínas</span>
            </div>
            <div className="macro-item">
              <span className="macro-value">{summary?.totais?.carboidratos?.toFixed(0) || 0}g</span>
              <span className="macro-label">Carbos</span>
            </div>
            <div className="macro-item">
              <span className="macro-value">{summary?.totais?.gorduras?.toFixed(0) || 0}g</span>
              <span className="macro-label">Gorduras</span>
            </div>
          </div>

          {/* ALERTAS DO DIA */}
          {fullAnalysis?.alertas?.length > 0 && (
            <div className="alerts-section" style={{
              marginTop: '16px',
              padding: '12px',
              background: 'rgba(239, 68, 68, 0.1)',
              borderRadius: '12px',
              border: '1px solid rgba(239, 68, 68, 0.3)'
            }}>
              <h4 style={{ margin: '0 0 10px', color: '#fff', fontSize: '14px' }}>
                ⚠️ Alertas de Hoje
              </h4>
              {fullAnalysis.alertas.slice(0, 3).map((alerta, i) => (
                <div key={i} style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '8px',
                  padding: '8px',
                  marginBottom: '8px',
                  background: alerta.nivel === 'alto' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                  borderRadius: '8px'
                }}>
                  <span style={{ fontSize: '20px' }}>{alerta.emoji}</span>
                  <div>
                    <p style={{ margin: 0, color: '#fff', fontSize: '13px', fontWeight: 'bold' }}>
                      {alerta.nutriente}
                    </p>
                    <p style={{ margin: '4px 0 0', color: '#ccc', fontSize: '12px' }}>
                      {alerta.mensagem}
                    </p>
                    {alerta.dica && (
                      <p style={{ margin: '4px 0 0', color: '#22c55e', fontSize: '11px' }}>
                        💡 {alerta.dica}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Micronutrientes do dia */}
          {fullAnalysis?.percentuais && (
            <div className="micro-section" style={{ marginTop: '16px' }}>
              <h4 style={{ color: '#fff', fontSize: '14px', marginBottom: '10px' }}>
                🔬 Vitaminas e Minerais
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
                {[
                  { key: 'vitamina_c', label: 'Vit C', emoji: '🍊' },
                  { key: 'vitamina_a', label: 'Vit A', emoji: '🥕' },
                  { key: 'ferro', label: 'Ferro', emoji: '🩸' },
                  { key: 'calcio', label: 'Cálcio', emoji: '🦴' },
                  { key: 'fibras', label: 'Fibras', emoji: '🥬' },
                  { key: 'sodio', label: 'Sódio', emoji: '🧂' }
                ].map(item => {
                  const perc = fullAnalysis.percentuais[item.key] || 0;
                  const cor = perc > 100 ? '#ef4444' : perc > 70 ? '#22c55e' : '#f59e0b';
                  return (
                    <div key={item.key} style={{
                      background: 'rgba(255,255,255,0.05)',
                      padding: '8px',
                      borderRadius: '8px',
                      textAlign: 'center'
                    }}>
                      <span style={{ fontSize: '16px' }}>{item.emoji}</span>
                      <p style={{ margin: '4px 0 0', color: cor, fontSize: '14px', fontWeight: 'bold' }}>
                        {perc.toFixed(0)}%
                      </p>
                      <p style={{ margin: '2px 0 0', color: '#888', fontSize: '10px' }}>
                        {item.label}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Refeições de hoje */}
          {summary?.pratos?.length > 0 && (
            <div className="meals-list">
              <h4>📋 Refeições de hoje</h4>
              {summary.pratos.map((p, i) => (
                <div key={i} className="meal-item">
                  <span className="meal-time">{p.hora}</span>
                  <span className="meal-name">{p.nome}</span>
                  <span className="meal-cal">{p.calorias} kcal</span>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* VISÃO SEMANAL */}
      {activeView === 'semana' && (
        <div className="weekly-view">
          {weeklyAnalysis && (
            <>
              {/* Pontuação Semanal */}
              <div style={{
                textAlign: 'center',
                padding: '20px',
                background: 'linear-gradient(135deg, rgba(34,197,94,0.2), rgba(59,130,246,0.2))',
                borderRadius: '16px',
                marginBottom: '16px'
              }}>
                <span style={{ fontSize: '48px' }}>{weeklyAnalysis.classificacao?.emoji}</span>
                <h3 style={{ 
                  color: weeklyAnalysis.classificacao?.cor || '#fff', 
                  margin: '8px 0',
                  fontSize: '24px'
                }}>
                  {weeklyAnalysis.pontuacao}/100
                </h3>
                <p style={{ color: '#ccc', margin: 0 }}>
                  {weeklyAnalysis.classificacao?.texto}
                </p>
                <p style={{ color: '#888', fontSize: '12px', marginTop: '4px' }}>
                  {weeklyAnalysis.dias_registrados} dias registrados
                </p>
              </div>

              {/* Tendências */}
              {weeklyAnalysis.tendencias?.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ color: '#fff', fontSize: '14px', marginBottom: '10px' }}>
                    📈 Tendências da Semana
                  </h4>
                  {weeklyAnalysis.tendencias.map((t, i) => (
                    <div key={i} style={{
                      background: t.tipo === 'alto' ? 'rgba(239,68,68,0.15)' : 'rgba(245,158,11,0.15)',
                      padding: '12px',
                      borderRadius: '10px',
                      marginBottom: '8px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '18px' }}>{t.emoji}</span>
                        <span style={{ color: '#fff', fontWeight: 'bold', fontSize: '13px' }}>
                          {t.nutriente}
                        </span>
                      </div>
                      <p style={{ color: '#ccc', fontSize: '12px', margin: '6px 0 0' }}>
                        {t.mensagem}
                      </p>
                      <p style={{ color: '#f59e0b', fontSize: '11px', margin: '4px 0 0' }}>
                        ⚠️ {t.impacto}
                      </p>
                      <p style={{ color: '#22c55e', fontSize: '11px', margin: '4px 0 0' }}>
                        💡 {t.sugestao}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Médias Semanais */}
              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ color: '#fff', fontSize: '14px', marginBottom: '10px' }}>
                  📊 Médias Diárias
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
                  {[
                    { key: 'calorias', label: 'Calorias', unit: 'kcal', emoji: '🔥' },
                    { key: 'proteinas', label: 'Proteínas', unit: 'g', emoji: '💪' },
                    { key: 'carboidratos', label: 'Carbos', unit: 'g', emoji: '🍚' },
                    { key: 'gorduras', label: 'Gorduras', unit: 'g', emoji: '🫒' }
                  ].map(item => {
                    const valor = weeklyAnalysis.medias_diarias?.[item.key] || 0;
                    return (
                      <div key={item.key} style={{
                        background: 'rgba(255,255,255,0.05)',
                        padding: '12px',
                        borderRadius: '10px'
                      }}>
                        <span style={{ fontSize: '18px' }}>{item.emoji}</span>
                        <p style={{ color: '#fff', fontSize: '16px', fontWeight: 'bold', margin: '4px 0' }}>
                          {valor.toFixed(0)} {item.unit}
                        </p>
                        <p style={{ color: '#888', fontSize: '11px', margin: 0 }}>
                          {item.label}/dia
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {weeklyAnalysis.tendencias?.length === 0 && (
                <div style={{
                  textAlign: 'center',
                  padding: '20px',
                  background: 'rgba(34,197,94,0.1)',
                  borderRadius: '12px'
                }}>
                  <span style={{ fontSize: '32px' }}>🎉</span>
                  <p style={{ color: '#22c55e', margin: '8px 0 0' }}>
                    Parabéns! Sua alimentação está equilibrada esta semana!
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* VISÃO DO PERFIL */}
      {activeView === 'perfil' && (
        <div className="profile-view">
          <div style={{
            background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.05))',
            borderRadius: '16px',
            padding: '20px',
            marginBottom: '16px'
          }}>
            <div style={{ textAlign: 'center', marginBottom: '16px' }}>
              <span style={{ fontSize: '48px' }}>👤</span>
              <h3 style={{ color: '#f59e0b', margin: '8px 0' }}>{summary?.nome}</h3>
              <p style={{ color: '#888', fontSize: '12px' }}>Membro Premium</p>
            </div>

            {/* Meta e Objetivo */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(2, 1fr)', 
              gap: '12px',
              marginBottom: '16px' 
            }}>
              <div style={{ background: 'rgba(255,255,255,0.05)', padding: '12px', borderRadius: '10px', textAlign: 'center' }}>
                <p style={{ color: '#888', fontSize: '11px', margin: 0 }}>Meta Diária</p>
                <p style={{ color: '#22c55e', fontSize: '18px', fontWeight: 'bold', margin: '4px 0 0' }}>
                  {summary?.meta?.toFixed(0) || '2000'} kcal
                </p>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.05)', padding: '12px', borderRadius: '10px', textAlign: 'center' }}>
                <p style={{ color: '#888', fontSize: '11px', margin: 0 }}>Objetivo</p>
                <p style={{ color: '#3b82f6', fontSize: '14px', fontWeight: 'bold', margin: '4px 0 0' }}>
                  {fullAnalysis?.metas ? (
                    fullAnalysis.metas.calorias < 1800 ? '📉 Perder peso' :
                    fullAnalysis.metas.calorias > 2200 ? '📈 Ganhar massa' : '⚖️ Manter'
                  ) : '⚖️ Manter'}
                </p>
              </div>
            </div>

            {/* Info sobre preferências */}
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ color: '#fff', fontSize: '13px', marginBottom: '8px' }}>
                🏷️ Suas Preferências
              </h4>
              <p style={{ color: '#888', fontSize: '12px', lineHeight: '1.6' }}>
                As restrições e alergias que você selecionou são usadas para gerar alertas personalizados quando você consome alimentos que podem ser problemáticos.
              </p>
            </div>
          </div>

          {/* Ações do perfil */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button 
              onClick={() => onEditProfile && onEditProfile()}
              data-testid="edit-profile-btn"
              style={{
                width: '100%',
                padding: '12px',
                background: 'linear-gradient(135deg, #f59e0b, #d97706)',
                color: '#fff',
                border: 'none',
                borderRadius: '10px',
                fontWeight: 'bold',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              ✏️ Editar Perfil
            </button>
            
            <button 
              onClick={onLogout}
              data-testid="logout-btn"
              style={{
                width: '100%',
                padding: '12px',
                background: 'rgba(239, 68, 68, 0.2)',
                color: '#ef4444',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '10px',
                fontWeight: 'bold',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              🚪 Sair da Conta
            </button>
          </div>
        </div>
      )}

      {/* Botão para voltar ao início */}
      <button className="back-to-camera-btn" onClick={onClose}>
        🏠 Início
      </button>
    </div>
  );
}

export default { PremiumRegister, PremiumLogin, DailyCounter, PremiumEditProfile };
