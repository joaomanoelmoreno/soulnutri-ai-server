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
          <label>Alergias (separadas por vírgula)</label>
          <input 
            type="text" 
            placeholder="gluten, lactose, amendoim..."
            value={form.alergias}
            onChange={e => setForm({...form, alergias: e.target.value})}
          />
        </div>

        <div className="form-group">
          <label>Restrições Alimentares</label>
          <div className="restricoes-grid">
            {[
              { value: 'vegano', label: '🌱 Vegano' },
              { value: 'vegetariano', label: '🥬 Vegetariano' },
              { value: 'sem_gluten', label: '🌾 Sem glúten' },
              { value: 'sem_lactose', label: '🥛 Sem lactose' }
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

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? '⏳ Criando...' : '✨ Criar Perfil'}
        </button>
        
        <button type="button" className="cancel-btn" onClick={onCancel}>
          Voltar
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

// Componente do Contador Diário
export function DailyCounter({ user, onLogout, onClose }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    const pin = localStorage.getItem('soulnutri_pin');
    try {
      const res = await fetch(`${API}/premium/daily-summary?pin=${pin}`);
      const data = await res.json();
      if (data.ok) setSummary(data);
    } catch (e) {
      console.error('Erro ao carregar resumo:', e);
    }
    setLoading(false);
  };

  if (loading) return <div className="loading">Carregando...</div>;

  const percentual = summary?.percentual || 0;
  const progressColor = percentual >= 100 ? '#ef4444' : percentual >= 75 ? '#f59e0b' : '#22c55e';

  return (
    <div className="daily-counter" data-testid="daily-counter">
      <div className="counter-header">
        <h3>👋 Olá, {summary?.nome}</h3>
        <button className="logout-btn" onClick={onLogout}>Sair</button>
      </div>

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

      {/* Botão para voltar à câmera */}
      <button className="back-to-camera-btn" onClick={onClose}>
        📷 Voltar para Câmera
      </button>
    </div>
  );
}

export default { PremiumRegister, PremiumLogin, DailyCounter };
