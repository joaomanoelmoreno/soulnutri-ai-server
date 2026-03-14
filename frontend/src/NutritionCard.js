import React, { useState } from 'react';

const NutritionCard = ({ sheet, compact = false }) => {
  const [expanded, setExpanded] = useState(false);

  if (!sheet) return null;

  const macros = [
    { label: 'Calorias', value: sheet.calorias_kcal, unit: 'kcal', color: '#f59e0b', vdr: 2000 },
    { label: 'Proteinas', value: sheet.proteinas_g, unit: 'g', color: '#3b82f6', vdr: 50 },
    { label: 'Carboidratos', value: sheet.carboidratos_g, unit: 'g', color: '#8b5cf6', vdr: 300 },
    { label: 'Gorduras', value: sheet.gorduras_g, unit: 'g', color: '#ef4444', vdr: 65 },
    { label: 'Fibras', value: sheet.fibras_g, unit: 'g', color: '#22c55e', vdr: 25 },
  ];

  const micros = [
    { label: 'Sodio', value: sheet.sodio_mg, unit: 'mg', vdr: 2400 },
    { label: 'Calcio', value: sheet.calcio_mg, unit: 'mg', vdr: 1000 },
    { label: 'Ferro', value: sheet.ferro_mg, unit: 'mg', vdr: 14 },
    { label: 'Potassio', value: sheet.potassio_mg, unit: 'mg', vdr: 4700 },
    { label: 'Zinco', value: sheet.zinco_mg, unit: 'mg', vdr: 11 },
  ];

  const fonteBadge = sheet.fonte_principal === 'TACO'
    ? { text: 'TACO', bg: 'rgba(34,197,94,0.15)', color: '#22c55e', icon: '🔬' }
    : { text: 'Gemini AI', bg: 'rgba(99,102,241,0.15)', color: '#818cf8', icon: '🤖' };

  if (compact) {
    return (
      <div
        data-testid="nutrition-card-compact"
        onClick={() => setExpanded(true)}
        style={{
          background: 'linear-gradient(135deg, rgba(245,158,11,0.12), rgba(217,119,6,0.06))',
          borderRadius: '12px',
          padding: '12px 16px',
          margin: '8px 0',
          cursor: 'pointer',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b' }}>
            {Math.round(sheet.calorias_kcal)} kcal
          </span>
          <span style={{
            fontSize: '10px', background: fonteBadge.bg, color: fonteBadge.color,
            padding: '2px 8px', borderRadius: '8px', fontWeight: 600
          }}>
            {fonteBadge.icon} {fonteBadge.text}
          </span>
        </div>
        <div style={{ display: 'flex', gap: '12px', marginTop: '6px', fontSize: '12px', color: '#a3a3a3' }}>
          <span>P: <b style={{ color: '#3b82f6' }}>{sheet.proteinas_g}g</b></span>
          <span>C: <b style={{ color: '#8b5cf6' }}>{sheet.carboidratos_g}g</b></span>
          <span>G: <b style={{ color: '#ef4444' }}>{sheet.gorduras_g}g</b></span>
          <span>F: <b style={{ color: '#22c55e' }}>{sheet.fibras_g}g</b></span>
        </div>
        <div style={{ fontSize: '11px', color: '#666', marginTop: '6px', textAlign: 'center' }}>
          Toque para ver ficha completa
        </div>
      </div>
    );
  }

  return (
    <div data-testid="nutrition-card-full" style={{
      background: '#1a1a2e',
      borderRadius: '16px',
      padding: '16px',
      margin: '12px 0',
      border: '1px solid rgba(255,255,255,0.08)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '16px' }}>📋</span>
          <span style={{ color: '#fff', fontWeight: 700, fontSize: '15px' }}>Ficha Nutricional</span>
        </div>
        <span style={{
          fontSize: '10px', background: fonteBadge.bg, color: fonteBadge.color,
          padding: '3px 10px', borderRadius: '10px', fontWeight: 600
        }}>
          {fonteBadge.icon} {fonteBadge.text}
          {sheet.cobertura_taco > 0 && sheet.fonte_principal !== 'TACO' &&
            ` + TACO ${sheet.cobertura_taco}%`}
        </span>
      </div>

      <div style={{ fontSize: '11px', color: '#666', marginBottom: '12px', textAlign: 'center' }}>
        Valores por 100g de porcao servida
      </div>

      {/* Macros */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {macros.map((m) => {
          const pct = Math.min(100, (m.value / m.vdr) * 100);
          return (
            <div key={m.label} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '80px', fontSize: '12px', color: '#a3a3a3', textAlign: 'right' }}>
                {m.label}
              </span>
              <div style={{
                flex: 1, height: '6px', background: 'rgba(255,255,255,0.06)',
                borderRadius: '3px', overflow: 'hidden'
              }}>
                <div style={{
                  width: `${pct}%`, height: '100%', background: m.color,
                  borderRadius: '3px', transition: 'width 0.6s ease'
                }} />
              </div>
              <span style={{ width: '60px', fontSize: '13px', fontWeight: 700, color: m.color, textAlign: 'right' }}>
                {m.value} {m.unit}
              </span>
              <span style={{ width: '35px', fontSize: '10px', color: '#666', textAlign: 'right' }}>
                {Math.round(pct)}%
              </span>
            </div>
          );
        })}
      </div>

      {/* Micros (expandable) */}
      {expanded && (
        <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '8px', fontWeight: 600 }}>
            Micronutrientes
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
            {micros.filter(m => m.value > 0).map((m) => (
              <div key={m.label} style={{
                display: 'flex', justifyContent: 'space-between',
                padding: '4px 8px', background: 'rgba(255,255,255,0.03)', borderRadius: '6px'
              }}>
                <span style={{ fontSize: '11px', color: '#888' }}>{m.label}</span>
                <span style={{ fontSize: '11px', color: '#ddd', fontWeight: 600 }}>
                  {m.value}{m.unit}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <button
        data-testid="nutrition-expand-btn"
        onClick={() => setExpanded(!expanded)}
        style={{
          width: '100%', background: 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px',
          padding: '6px', marginTop: '10px', cursor: 'pointer',
          color: '#888', fontSize: '11px'
        }}
      >
        {expanded ? 'Menos detalhes' : 'Ver micronutrientes'}
      </button>
    </div>
  );
};

export default NutritionCard;
