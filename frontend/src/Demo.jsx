import React, { useState, useRef } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const DEMO_DISHES = [
  {
    id: 1,
    dish_display: "Frango Grelhado com Legumes",
    image: "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=400&q=80",
    category: "proteina animal",
    category_emoji: "\ud83c\udf57",
    nutrition: { calorias: "320 kcal", proteinas: "38g", carboidratos: "12g", gorduras: "14g", fibras: "4g" },
    alergenos: { gluten: false, lactose: false, soja: false, amendoim: false },
    ingredientes: ["Peito de frango", "Abobrinha", "Cenoura", "Pimentao", "Azeite", "Ervas finas"],
    beneficios: ["Alta proteina para recuperacao muscular", "Baixo carboidrato", "Rico em vitaminas A e C"],
    score: 0.94,
    identified: true,
    source: "demo"
  },
  {
    id: 2,
    dish_display: "Salada Caesar com Croutons",
    image: "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400&q=80",
    category: "vegetariano",
    category_emoji: "\ud83e\udd6c",
    nutrition: { calorias: "210 kcal", proteinas: "8g", carboidratos: "15g", gorduras: "14g", fibras: "3g" },
    alergenos: { gluten: true, lactose: true, soja: false, amendoim: false },
    alertas_personalizados: [{ mensagem: "Contem gluten nos croutons" }, { mensagem: "Molho contem lactose (parmesao)" }],
    ingredientes: ["Alface romana", "Croutons", "Parmesao", "Molho Caesar", "Limao"],
    beneficios: ["Rica em fibras", "Fonte de calcio (parmesao)", "Baixas calorias"],
    score: 0.91,
    identified: true,
    source: "demo"
  },
  {
    id: 3,
    dish_display: "Feijoada Tradicional",
    image: "https://images.unsplash.com/photo-1612548127010-97b48ffa2aef?w=400&q=80",
    category: "proteina animal",
    category_emoji: "\ud83c\udf57",
    nutrition: { calorias: "480 kcal", proteinas: "28g", carboidratos: "32g", gorduras: "24g", fibras: "8g" },
    alergenos: { gluten: false, lactose: false, soja: false, amendoim: false },
    ingredientes: ["Feijao preto", "Carne seca", "Linguica calabresa", "Costela suina", "Louro", "Alho"],
    beneficios: ["Alto teor de ferro", "Rica em proteinas", "Fonte de fibras (feijao preto)"],
    score: 0.96,
    identified: true,
    source: "demo"
  }
];

export default function Demo() {
  const [selectedDish, setSelectedDish] = useState(null);
  const [ttsLoading, setTtsLoading] = useState(false);
  const [ttsPlaying, setTtsPlaying] = useState(false);
  const audioRef = useRef(null);

  const playAudio = async (dish) => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setTtsPlaying(false);
      return;
    }
    setTtsLoading(true);
    try {
      const res = await fetch(`${API}/ai/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dish_data: dish, voice: 'alloy' })
      });
      if (!res.ok) throw new Error('Erro');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;
      audio.onended = () => { setTtsPlaying(false); audioRef.current = null; URL.revokeObjectURL(url); };
      audio.onerror = () => { setTtsPlaying(false); audioRef.current = null; };
      setTtsPlaying(true);
      await audio.play();
    } catch (e) {
      console.error('[TTS Demo]', e);
    } finally {
      setTtsLoading(false);
    }
  };

  const stopAudio = () => {
    if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; }
    setTtsPlaying(false);
  };

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0a', color: '#f1f5f9', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' }}>
      
      {/* Header */}
      <div style={{ padding: '40px 20px 20px', textAlign: 'center' }}>
        <div style={{ fontSize: '14px', letterSpacing: '3px', color: '#10b981', fontWeight: 600, marginBottom: '8px' }}>SOULNUTRI</div>
        <h1 style={{ fontSize: '28px', fontWeight: 800, margin: '0 0 8px', lineHeight: 1.2, color: '#fff' }}>
          Experimente o SoulNutri
        </h1>
        <p style={{ fontSize: '15px', color: '#94a3b8', margin: 0, maxWidth: '340px', marginInline: 'auto' }}>
          Toque em um prato para ver a analise nutricional completa com inteligencia artificial
        </p>
      </div>

      {/* Dish Grid */}
      {!selectedDish && (
        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '500px', margin: '0 auto' }}>
          {DEMO_DISHES.map(dish => (
            <button
              key={dish.id}
              data-testid={`demo-dish-${dish.id}`}
              onClick={() => setSelectedDish(dish)}
              style={{
                display: 'flex', alignItems: 'center', gap: '16px',
                background: '#1a1a2e', border: '1px solid #1e293b',
                borderRadius: '16px', padding: '12px', cursor: 'pointer',
                textAlign: 'left', transition: 'all 0.2s',
                width: '100%'
              }}
            >
              <img
                src={dish.image}
                alt={dish.dish_display}
                style={{ width: '80px', height: '80px', borderRadius: '12px', objectFit: 'cover', flexShrink: 0 }}
              />
              <div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#fff', marginBottom: '4px' }}>
                  {dish.category_emoji} {dish.dish_display}
                </div>
                <div style={{ fontSize: '13px', color: '#10b981', fontWeight: 600 }}>
                  {dish.nutrition.calorias}
                </div>
                <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                  Toque para ver analise completa
                </div>
              </div>
            </button>
          ))}

          {/* CTA */}
          <div style={{ textAlign: 'center', marginTop: '24px', padding: '0 20px' }}>
            <div style={{ width: '40px', height: '2px', background: '#1e293b', margin: '0 auto 20px' }} />
            <p style={{ fontSize: '14px', color: '#64748b', marginBottom: '16px' }}>
              No app completo, basta apontar a camera para o prato
            </p>
            <a
              href="/"
              data-testid="demo-install-cta"
              style={{
                display: 'inline-block', padding: '14px 32px',
                background: 'linear-gradient(135deg, #10b981, #059669)',
                color: '#fff', borderRadius: '14px', fontSize: '15px',
                fontWeight: 700, textDecoration: 'none',
                boxShadow: '0 4px 16px rgba(16,185,129,0.3)'
              }}
            >
              Abrir SoulNutri
            </a>
          </div>
        </div>
      )}

      {/* Dish Detail */}
      {selectedDish && (
        <div style={{ padding: '20px', maxWidth: '500px', margin: '0 auto' }}>
          {/* Back */}
          <button
            data-testid="demo-back-btn"
            onClick={() => { setSelectedDish(null); stopAudio(); }}
            style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '15px', cursor: 'pointer', padding: '8px 0', marginBottom: '12px' }}
          >
            &larr; Voltar
          </button>

          {/* Image */}
          <img
            src={selectedDish.image}
            alt={selectedDish.dish_display}
            style={{ width: '100%', height: '200px', objectFit: 'cover', borderRadius: '16px', marginBottom: '16px' }}
          />

          {/* Name + Category */}
          <h2 style={{ fontSize: '22px', fontWeight: 800, margin: '0 0 4px', color: '#fff' }}>
            {selectedDish.category_emoji} {selectedDish.dish_display}
          </h2>
          <div style={{ fontSize: '13px', color: '#10b981', fontWeight: 600, marginBottom: '16px', textTransform: 'capitalize' }}>
            {selectedDish.category} &middot; Confianca {Math.round(selectedDish.score * 100)}%
          </div>

          {/* TTS Button */}
          <button
            data-testid="demo-tts-btn"
            onClick={() => playAudio(selectedDish)}
            disabled={ttsLoading}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
              width: '100%', padding: '14px 20px', marginBottom: '16px',
              background: ttsPlaying ? 'linear-gradient(135deg, #ef4444, #dc2626)' : 'linear-gradient(135deg, #10b981, #059669)',
              color: '#fff', border: 'none', borderRadius: '14px',
              fontSize: '16px', fontWeight: 700, cursor: ttsLoading ? 'wait' : 'pointer',
              boxShadow: '0 4px 12px rgba(16,185,129,0.3)', minHeight: '52px'
            }}
          >
            {ttsLoading ? 'Gerando audio...' : ttsPlaying ? '\u25a0 Parar' : '\ud83d\udd0a Ouvir'}
          </button>

          {/* Nutrition */}
          <div style={{ background: '#1a1a2e', borderRadius: '14px', padding: '16px', marginBottom: '12px', border: '1px solid #1e293b' }}>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff', marginBottom: '12px' }}>Informacao Nutricional</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              {Object.entries(selectedDish.nutrition).map(([key, val]) => (
                <div key={key} style={{ background: '#0f172a', borderRadius: '10px', padding: '10px', textAlign: 'center' }}>
                  <div style={{ fontSize: '16px', fontWeight: 700, color: '#10b981' }}>{val}</div>
                  <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'capitalize' }}>{key}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Allergens */}
          {selectedDish.alergenos && (
            <div style={{ background: '#1a1a2e', borderRadius: '14px', padding: '16px', marginBottom: '12px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff', marginBottom: '10px' }}>Alergenos</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {Object.entries(selectedDish.alergenos).map(([name, present]) => (
                  <span key={name} style={{
                    padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 600,
                    background: present ? '#7f1d1d' : '#0f2e1d',
                    color: present ? '#fca5a5' : '#6ee7b7',
                    border: `1px solid ${present ? '#991b1b' : '#064e3b'}`
                  }}>
                    {present ? '\u26a0\ufe0f' : '\u2705'} {name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Alerts */}
          {selectedDish.alertas_personalizados && selectedDish.alertas_personalizados.length > 0 && (
            <div style={{ background: '#2a1a1a', borderRadius: '14px', padding: '16px', marginBottom: '12px', border: '1px solid #7f1d1d' }}>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#fca5a5', marginBottom: '8px' }}>Alertas</div>
              {selectedDish.alertas_personalizados.map((a, i) => (
                <div key={i} style={{ fontSize: '13px', color: '#fca5a5', marginBottom: '4px' }}>{a.mensagem}</div>
              ))}
            </div>
          )}

          {/* Ingredients */}
          {selectedDish.ingredientes && (
            <div style={{ background: '#1a1a2e', borderRadius: '14px', padding: '16px', marginBottom: '12px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff', marginBottom: '10px' }}>Ingredientes</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {selectedDish.ingredientes.map((ing, i) => (
                  <span key={i} style={{ padding: '4px 10px', background: '#0f172a', borderRadius: '8px', fontSize: '12px', color: '#cbd5e1' }}>
                    {ing}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Benefits */}
          {selectedDish.beneficios && (
            <div style={{ background: '#1a1a2e', borderRadius: '14px', padding: '16px', marginBottom: '16px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff', marginBottom: '10px' }}>Beneficios</div>
              {selectedDish.beneficios.map((b, i) => (
                <div key={i} style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '6px', paddingLeft: '12px', borderLeft: '2px solid #10b981' }}>
                  {b}
                </div>
              ))}
            </div>
          )}

          {/* CTA */}
          <div style={{ textAlign: 'center', padding: '12px 0 32px' }}>
            <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '12px' }}>
              Quer identificar seus proprios pratos em tempo real?
            </p>
            <a
              href="/"
              data-testid="demo-cta-detail"
              style={{
                display: 'inline-block', padding: '14px 32px',
                background: 'linear-gradient(135deg, #10b981, #059669)',
                color: '#fff', borderRadius: '14px', fontSize: '15px',
                fontWeight: 700, textDecoration: 'none'
              }}
            >
              Usar SoulNutri
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
