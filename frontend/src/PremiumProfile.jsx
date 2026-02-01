import React, { useState, useEffect } from 'react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

/**
 * Formulário de Perfil Premium
 * Coleta dados para personalização das dicas nutricionais
 */
export function PremiumProfileForm({ user, onSave, onSkip }) {
  const [formData, setFormData] = useState({
    peso: user?.perfil?.peso || '',
    altura: user?.perfil?.altura || '',
    idade: user?.perfil?.idade || '',
    sexo: user?.perfil?.sexo || '',
    nivel_atividade: user?.perfil?.nivel_atividade || '',
    restricoes: user?.perfil?.restricoes || []
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const restricoesOpcoes = [
    { id: 'vegetariano', label: '🥬 Vegetariano', desc: 'Não como carne' },
    { id: 'vegano', label: '🌱 Vegano', desc: 'Não como derivados animais' },
    { id: 'sem_gluten', label: '🌾 Sem Glúten', desc: 'Intolerância/Celíaco' },
    { id: 'sem_lactose', label: '🥛 Sem Lactose', desc: 'Intolerância à lactose' },
    { id: 'sem_frutos_mar', label: '🦐 Sem Frutos do Mar', desc: 'Alergia' },
    { id: 'sem_amendoim', label: '🥜 Sem Amendoim/Castanhas', desc: 'Alergia' }
    // REMOVIDO: diabetico e hipertenso - questões jurídicas
  ];

  const handleRestricaoToggle = (id) => {
    setFormData(prev => ({
      ...prev,
      restricoes: prev.restricoes.includes(id)
        ? prev.restricoes.filter(r => r !== id)
        : [...prev.restricoes, id]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    // Pegar PIN do localStorage se não estiver no user
    const userPin = user.pin || localStorage.getItem('soulnutri_pin');
    
    if (!userPin) {
      setError('PIN não encontrado. Faça login novamente.');
      setSaving(false);
      return;
    }

    try {
      const res = await fetch(`${API}/premium/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome: user.nome,
          pin: userPin,
          perfil: {
            peso: parseFloat(formData.peso) || null,
            altura: parseFloat(formData.altura) || null,
            idade: parseInt(formData.idade) || null,
            sexo: formData.sexo || null,
            nivel_atividade: formData.nivel_atividade || null,
            restricoes: formData.restricoes
          }
        })
      });

      const data = await res.json();
      if (data.ok) {
        onSave(data.perfil);
      } else {
        setError(data.error || 'Erro ao salvar perfil');
      }
    } catch (err) {
      setError('Erro de conexão');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="premium-profile-form" data-testid="premium-profile-form">
      <h2>📋 Complete seu Perfil</h2>
      <p className="profile-subtitle">
        Suas informações ajudam a personalizar as dicas nutricionais em tempo real
      </p>

      <form onSubmit={handleSubmit}>
        {/* Dados Físicos */}
        <div className="profile-section">
          <h3>📏 Dados Físicos</h3>
          <div className="profile-row">
            <div className="profile-field">
              <label>Peso (kg)</label>
              <input
                type="number"
                placeholder="Ex: 70"
                value={formData.peso}
                onChange={(e) => setFormData({...formData, peso: e.target.value})}
                min="30"
                max="250"
                data-testid="profile-peso"
              />
            </div>
            <div className="profile-field">
              <label>Altura (cm)</label>
              <input
                type="number"
                placeholder="Ex: 170"
                value={formData.altura}
                onChange={(e) => setFormData({...formData, altura: e.target.value})}
                min="100"
                max="250"
                data-testid="profile-altura"
              />
            </div>
          </div>
          <div className="profile-row">
            <div className="profile-field">
              <label>Idade</label>
              <input
                type="number"
                placeholder="Ex: 35"
                value={formData.idade}
                onChange={(e) => setFormData({...formData, idade: e.target.value})}
                min="10"
                max="120"
                data-testid="profile-idade"
              />
            </div>
            <div className="profile-field">
              <label>Sexo</label>
              <select
                value={formData.sexo}
                onChange={(e) => setFormData({...formData, sexo: e.target.value})}
                data-testid="profile-sexo"
              >
                <option value="">Selecione...</option>
                <option value="masculino">Masculino</option>
                <option value="feminino">Feminino</option>
                <option value="outro">Prefiro não informar</option>
              </select>
            </div>
          </div>
        </div>

        {/* Nível de Atividade */}
        <div className="profile-section">
          <h3>🏃 Nível de Atividade</h3>
          <div className="activity-options">
            {[
              { id: 'sedentario', label: '🛋️ Sedentário', desc: 'Pouca ou nenhuma atividade' },
              { id: 'leve', label: '🚶 Leve', desc: '1-2x por semana' },
              { id: 'moderado', label: '🏃 Moderado', desc: '3-5x por semana' },
              { id: 'intenso', label: '💪 Intenso', desc: '6-7x por semana' }
            ].map(opt => (
              <button
                key={opt.id}
                type="button"
                className={`activity-btn ${formData.nivel_atividade === opt.id ? 'active' : ''}`}
                onClick={() => setFormData({...formData, nivel_atividade: opt.id})}
                data-testid={`activity-${opt.id}`}
              >
                <span className="activity-label">{opt.label}</span>
                <span className="activity-desc">{opt.desc}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Restrições Alimentares */}
        <div className="profile-section">
          <h3>⚠️ Restrições Alimentares</h3>
          <p className="section-hint">Selecione todas que se aplicam:</p>
          <div className="restricoes-grid">
            {restricoesOpcoes.map(opt => (
              <button
                key={opt.id}
                type="button"
                className={`restricao-btn ${formData.restricoes.includes(opt.id) ? 'active' : ''}`}
                onClick={() => handleRestricaoToggle(opt.id)}
                data-testid={`restricao-${opt.id}`}
              >
                <span className="restricao-label">{opt.label}</span>
              </button>
            ))}
          </div>
        </div>

        {error && <p className="profile-error">{error}</p>}

        <div className="profile-actions">
          <button
            type="button"
            className="profile-skip-btn"
            onClick={onSkip}
            disabled={saving}
          >
            Pular por agora
          </button>
          <button
            type="submit"
            className="profile-save-btn"
            disabled={saving}
            data-testid="profile-save"
          >
            {saving ? 'Salvando...' : '✓ Salvar Perfil'}
          </button>
        </div>
      </form>
    </div>
  );
}

/**
 * Gera dica personalizada baseada no perfil do usuário e no prato
 */
export function generatePersonalizedTip(prato, perfil) {
  if (!perfil || !prato) return null;

  const tips = [];
  const categoria = prato.category?.toLowerCase() || '';
  const calorias = parseInt(prato.nutrition?.calorias) || 150;
  const proteinas = parseFloat(prato.nutrition?.proteinas) || 5;
  const carboidratos = parseFloat(prato.nutrition?.carboidratos) || 20;

  // Calcular necessidades baseadas no perfil
  let tmb = 0; // Taxa Metabólica Basal
  if (perfil.peso && perfil.altura && perfil.idade && perfil.sexo) {
    if (perfil.sexo === 'masculino') {
      tmb = 88.36 + (13.4 * perfil.peso) + (4.8 * perfil.altura) - (5.7 * perfil.idade);
    } else {
      tmb = 447.6 + (9.2 * perfil.peso) + (3.1 * perfil.altura) - (4.3 * perfil.idade);
    }
    
    // Ajustar por nível de atividade
    const fatores = { sedentario: 1.2, leve: 1.375, moderado: 1.55, intenso: 1.725 };
    tmb *= fatores[perfil.nivel_atividade] || 1.2;
  }

  // Restrições alimentares
  const restricoes = perfil.restricoes || [];
  
  // Alertas de restrição
  if (restricoes.includes('vegetariano') && categoria === 'proteína animal') {
    tips.push({
      tipo: 'alerta',
      icone: '⚠️',
      texto: 'Este prato contém proteína animal'
    });
  }
  
  if (restricoes.includes('vegano') && (categoria === 'proteína animal' || categoria === 'vegetariano')) {
    tips.push({
      tipo: 'alerta',
      icone: '⚠️',
      texto: 'Este prato não é vegano'
    });
  }
  
  if (restricoes.includes('sem_gluten') && prato.riscos?.some(r => r.toLowerCase().includes('glúten'))) {
    tips.push({
      tipo: 'alerta',
      icone: '🌾',
      texto: 'Atenção: pode conter glúten'
    });
  }
  
  if (restricoes.includes('sem_lactose') && prato.riscos?.some(r => r.toLowerCase().includes('lactose'))) {
    tips.push({
      tipo: 'alerta',
      icone: '🥛',
      texto: 'Atenção: pode conter lactose'
    });
  }

  // NOTA: Lógica de diabético/hipertenso removida por questões jurídicas
  // O código permanece comentado para referência futura se necessário

  // Dicas baseadas em atividade física
  if (perfil.nivel_atividade === 'intenso' && proteinas > 15) {
    tips.push({
      tipo: 'positivo',
      icone: '💪',
      texto: `Ótima fonte de proteína (${proteinas}g) para sua rotina intensa!`
    });
  }

  if (perfil.nivel_atividade === 'sedentario' && calorias > 300) {
    tips.push({
      tipo: 'atencao',
      icone: '⚡',
      texto: `Porção calórica (~${calorias}kcal). Considere uma porção menor.`
    });
  }

  // Dica de calorias diárias
  if (tmb > 0) {
    const percentual = Math.round((calorias / tmb) * 100);
    if (percentual > 20) {
      tips.push({
        tipo: 'info',
        icone: '📊',
        texto: `Este prato representa ~${percentual}% das suas calorias diárias`
      });
    }
  }

  // Dica positiva para pratos saudáveis
  if (categoria === 'vegano' && calorias < 150) {
    tips.push({
      tipo: 'positivo',
      icone: '🌱',
      texto: 'Excelente escolha! Leve e nutritivo.'
    });
  }

  return tips.length > 0 ? tips : null;
}

export default PremiumProfileForm;
