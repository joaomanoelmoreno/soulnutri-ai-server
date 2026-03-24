import React, { useState, useEffect, useCallback } from 'react';
import { Bell, X, ExternalLink, ChevronRight, AlertTriangle, Leaf, CheckCircle, Flame, Sun, Droplets, Trophy, BarChart } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ICON_MAP = {
  'alert-triangle': AlertTriangle,
  'leaf': Leaf,
  'check-circle': CheckCircle,
  'flame': Flame,
  'sun': Sun,
  'droplets': Droplets,
  'trophy': Trophy,
  'bar-chart': BarChart,
};

const PRIORITY_COLORS = {
  high: { bg: 'rgba(239,68,68,0.15)', border: 'rgba(239,68,68,0.3)', accent: '#ef4444' },
  medium: { bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.3)', accent: '#f59e0b' },
  low: { bg: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.3)', accent: '#10b981' },
};

export default function NotificationPanel({ userPin, userName, isVisible, onClose }) {
  const [notifications, setNotifications] = useState([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [expandedId, setExpandedId] = useState(null);

  const loadNotifications = useCallback(async () => {
    if (!userPin) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/notifications/${userPin}`);
      if (!res.ok) { setLoading(false); return; }
      const data = await res.json();
      if (data.ok) {
        setNotifications(data.notifications || []);
        setUnread(data.unread || 0);
      }
    } catch (e) {
      console.error('Erro ao carregar notificacoes:', e);
    }
    setLoading(false);
  }, [userPin]);

  useEffect(() => {
    if (isVisible && userPin) {
      loadNotifications();
    }
  }, [isVisible, userPin, loadNotifications]);

  const generateNotification = async () => {
    if (!userPin) return;
    setGenerating(true);
    try {
      const res = await fetch(`${API}/notifications/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_pin: userPin, user_name: userName || '' })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.ok) {
          loadNotifications();
        }
      }
    } catch (e) {
      console.error('Erro ao gerar notificacao:', e);
    }
    setGenerating(false);
  };

  const markAsRead = async (date) => {
    try {
      await fetch(`${API}/notifications/${userPin}/read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date })
      });
      setNotifications(prev => prev.map(n =>
        n.date === date ? { ...n, read: true } : n
      ));
      setUnread(prev => Math.max(0, prev - 1));
    } catch (e) {
      console.error('Erro:', e);
    }
  };

  if (!isVisible) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      bottom: 0,
      width: '100%',
      maxWidth: '420px',
      background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)',
      borderLeft: '1px solid rgba(255,255,255,0.1)',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      boxShadow: '-8px 0 32px rgba(0,0,0,0.5)',
      animation: 'slideInRight 0.3s ease'
    }} data-testid="notification-panel">
      {/* Header */}
      <div style={{
        padding: '20px',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Bell size={22} color="#10b981" />
          <h2 style={{ margin: 0, color: '#f8fafc', fontSize: '18px', fontFamily: 'Playfair Display, serif' }}>
            Notificacoes
          </h2>
          {unread > 0 && (
            <span style={{
              background: '#ef4444',
              color: '#fff',
              borderRadius: '12px',
              padding: '2px 8px',
              fontSize: '12px',
              fontWeight: 'bold'
            }}>{unread}</span>
          )}
        </div>
        <button
          onClick={onClose}
          data-testid="notification-close"
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px' }}
        >
          <X size={22} color="#94a3b8" />
        </button>
      </div>

      {/* Generate Button */}
      <div style={{ padding: '12px 20px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <button
          onClick={generateNotification}
          disabled={generating}
          data-testid="generate-notification-btn"
          style={{
            width: '100%',
            padding: '10px',
            background: generating ? '#334155' : 'linear-gradient(135deg, #10b981, #059669)',
            color: '#fff',
            border: 'none',
            borderRadius: '10px',
            cursor: generating ? 'default' : 'pointer',
            fontWeight: 'bold',
            fontSize: '14px',
            fontFamily: 'DM Sans, sans-serif',
            transition: 'all 0.2s'
          }}
        >
          {generating ? 'Gerando...' : 'Gerar Notificacao do Dia'}
        </button>
      </div>

      {/* Notifications List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px' }}>
        {loading && (
          <div style={{ textAlign: 'center', color: '#94a3b8', padding: '40px' }}>
            Carregando...
          </div>
        )}

        {!loading && notifications.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
            <Bell size={48} style={{ marginBottom: '12px', opacity: 0.3 }} />
            <p style={{ fontSize: '14px' }}>Nenhuma notificacao ainda.</p>
            <p style={{ fontSize: '12px' }}>Clique em "Gerar" para receber sua dica diaria.</p>
          </div>
        )}

        {notifications.map((n, i) => {
          const colors = PRIORITY_COLORS[n.priority] || PRIORITY_COLORS.low;
          const IconComponent = ICON_MAP[n.icon] || Bell;
          const isExpanded = expandedId === i;

          return (
            <div
              key={i}
              data-testid={`notification-item-${i}`}
              onClick={() => {
                setExpandedId(isExpanded ? null : i);
                if (!n.read) markAsRead(n.date);
              }}
              style={{
                background: colors.bg,
                border: `1px solid ${colors.border}`,
                borderRadius: '12px',
                padding: '14px',
                marginBottom: '10px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                opacity: n.read ? 0.7 : 1
              }}
            >
              {/* Notification Header */}
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '10px',
                  background: `${colors.accent}22`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <IconComponent size={18} color={colors.accent} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h4 style={{
                      margin: 0,
                      color: '#f8fafc',
                      fontSize: '14px',
                      fontWeight: 'bold',
                      fontFamily: 'DM Sans, sans-serif'
                    }}>
                      {n.title}
                      {!n.read && (
                        <span style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: colors.accent,
                          display: 'inline-block',
                          marginLeft: '8px'
                        }} />
                      )}
                    </h4>
                    <ChevronRight
                      size={16}
                      color="#64748b"
                      style={{
                        transform: isExpanded ? 'rotate(90deg)' : 'rotate(0)',
                        transition: 'transform 0.2s'
                      }}
                    />
                  </div>
                  <p style={{
                    margin: '6px 0 0',
                    color: '#cbd5e1',
                    fontSize: '13px',
                    lineHeight: '1.5',
                    fontFamily: 'DM Sans, sans-serif'
                  }}>
                    {n.message}
                  </p>

                  {/* Date */}
                  <div style={{ marginTop: '6px', color: '#64748b', fontSize: '11px' }}>
                    {n.date || ''}
                  </div>
                </div>
              </div>

              {/* Expanded: References */}
              {isExpanded && n.references && n.references.length > 0 && (
                <div style={{
                  marginTop: '12px',
                  paddingTop: '12px',
                  borderTop: `1px solid ${colors.border}`
                }}>
                  <p style={{ color: '#94a3b8', fontSize: '11px', marginBottom: '8px', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    Fontes e Referencias
                  </p>
                  {n.references.map((ref, ri) => (
                    <a
                      key={ri}
                      href={ref.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      data-testid={`notification-ref-${i}-${ri}`}
                      onClick={e => e.stopPropagation()}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '8px 10px',
                        background: 'rgba(15,23,42,0.5)',
                        borderRadius: '8px',
                        marginBottom: '6px',
                        textDecoration: 'none',
                        transition: 'background 0.2s'
                      }}
                    >
                      <ExternalLink size={14} color="#10b981" style={{ flexShrink: 0 }} />
                      <div>
                        <div style={{ color: '#e2e8f0', fontSize: '12px', fontWeight: '600' }}>
                          {ref.source}
                        </div>
                        <div style={{ color: '#64748b', fontSize: '11px' }}>
                          {ref.title}
                        </div>
                      </div>
                    </a>
                  ))}
                </div>
              )}

              {/* Expanded: Dishes context */}
              {isExpanded && n.dishes_context && n.dishes_context.length > 0 && (
                <div style={{ marginTop: '8px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {n.dishes_context.map((dish, di) => (
                    <span key={di} style={{
                      padding: '3px 10px',
                      background: 'rgba(15,23,42,0.5)',
                      borderRadius: '20px',
                      fontSize: '11px',
                      color: '#94a3b8'
                    }}>
                      {dish}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* CSS Animation */}
      <style>{`
        @keyframes slideInRight {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
