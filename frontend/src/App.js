import React, { useState, useRef, useEffect, useCallback, useMemo, Component } from "react";
import "./App.css";
import "./Premium.css";
import "./PremiumProfile.css";
import { PremiumRegister, PremiumLogin, DailyCounter, PremiumEditProfile } from "./Premium";
import { PremiumProfileForm, generatePersonalizedTip } from "./PremiumProfile";
import CheckinRefeicao from "./CheckinRefeicao";
import "./CheckinRefeicao.css";
import { I18nProvider, useI18n, LanguageSelector } from "./I18nContext";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Timeout para requisições (evita travamentos)
const REQUEST_TIMEOUT = 15000; // 15 segundos

// Error Boundary para capturar erros da câmera
class CameraErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[CameraErrorBoundary] Erro capturado:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="camera-error-fallback" style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          padding: '20px',
          textAlign: 'center',
          backgroundColor: '#1a1a2e',
          color: '#fff'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📷</div>
          <h3 style={{ marginBottom: '12px' }}>Erro na Câmera</h3>
          <p style={{ marginBottom: '16px', color: '#aaa' }}>
            Ocorreu um problema com a câmera. Por favor, recarregue a página.
          </p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: '12px 24px',
              backgroundColor: '#4CAF50',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Recarregar Página
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Componente Welcome Popup - Boas-vindas com seleção de idioma
function WelcomePopup({ onClose }) {
  const { languages, changeLanguage, currentLang, t } = useI18n();
  
  const handleSelectLanguage = (langCode) => {
    changeLanguage(langCode);
    onClose();
  };
  
  return (
    <div className="welcome-overlay" data-testid="welcome-popup">
      <div className="welcome-popup">
        <div className="welcome-header">
          <img src="/images/soulnutri-logo.png" alt="SoulNutri" className="welcome-logo" />
          <h1>SoulNutri<span className="tm">®</span></h1>
        </div>
        
        <p className="welcome-tagline">Porque nutre também a sua alma</p>
        
        <div className="welcome-message">
          <p>🌍 Escolha seu idioma / Choose your language:</p>
        </div>
        
        <div className="welcome-languages">
          {languages.map(lang => (
            <button
              key={lang.code}
              className={`welcome-lang-btn ${lang.code === currentLang ? 'active' : ''}`}
              onClick={() => handleSelectLanguage(lang.code)}
              data-testid={`welcome-lang-${lang.code}`}
            >
              <span className="welcome-flag">{lang.flag}</span>
              <span className="welcome-lang-name">{lang.native}</span>
            </button>
          ))}
        </div>
        
        <div className="welcome-features">
          <div className="feature">📸 Aponte • Identifique • Saiba</div>
          <div className="feature">🥗 499+ pratos cadastrados</div>
          <div className="feature">⚡ Rápido e preciso</div>
        </div>
        
        <div className="welcome-location-info" style={{
          marginTop: '12px',
          padding: '10px',
          backgroundColor: 'rgba(255,255,255,0.1)',
          borderRadius: '8px',
          fontSize: '12px',
          color: '#ccc',
          textAlign: 'center'
        }}>
          📷 Aponte a câmera para o prato e o SoulNutri identifica automaticamente
        </div>
        
        <button className="welcome-start-btn" onClick={onClose} data-testid="welcome-start">
          {t('tap_to_photo', 'Começar')} →
        </button>
      </div>
    </div>
  );
}

// Componente Tutorial do Scanner Contínuo
function ScannerTutorial({ onClose }) {
  const [step, setStep] = useState(1);
  const { t } = useI18n();
  
  const steps = [
    {
      icon: "📸",
      title: t('tutorial_step1_title', 'Aponte e Fotografe'),
      desc: t('tutorial_step1_desc', 'Enquadre o prato na tela e toque para tirar uma foto. Em segundos você terá todas as informações.'),
      visual: "scan-animation"
    },
    {
      icon: "✨",
      title: t('tutorial_step2_title', 'Escolha Consciente'),
      desc: t('tutorial_step2_desc', 'Veja ingredientes, benefícios, alertas de alérgenos e muito mais. Tudo para você fazer a melhor escolha.'),
      visual: "tap-animation"
    },
    {
      icon: "🎯",
      title: t('tutorial_step3_title', 'Seu Prato, Sua Escolha'),
      desc: t('tutorial_step3_desc', 'Monte seu prato ideal com informações completas. Saiba exatamente o que está comendo!'),
      visual: "plate-animation"
    }
  ];
  
  const currentStep = steps[step - 1];
  
  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      localStorage.setItem('soulnutri_tutorial_seen', 'true');
      onClose();
    }
  };
  
  const handleSkip = () => {
    localStorage.setItem('soulnutri_tutorial_seen', 'true');
    onClose();
  };
  
  return (
    <div className="tutorial-overlay" data-testid="scanner-tutorial">
      <div className="tutorial-popup">
        <button className="tutorial-skip" onClick={handleSkip} data-testid="tutorial-skip">
          {t('skip', 'Pular')} →
        </button>
        
        <div className="tutorial-progress">
          {[1, 2, 3].map(s => (
            <div key={s} className={`progress-dot ${s === step ? 'active' : ''} ${s < step ? 'done' : ''}`} />
          ))}
        </div>
        
        <div className={`tutorial-visual ${currentStep.visual}`}>
          <span className="tutorial-icon">{currentStep.icon}</span>
          {currentStep.visual === 'scan-animation' && (
            <div className="scan-waves">
              <div className="wave"></div>
              <div className="wave"></div>
              <div className="wave"></div>
            </div>
          )}
          {currentStep.visual === 'tap-animation' && (
            <div className="tap-finger">👆</div>
          )}
          {currentStep.visual === 'plate-animation' && (
            <div className="plate-items-anim">
              <span>🍗</span><span>🥗</span><span>🍚</span>
            </div>
          )}
        </div>
        
        <h2 className="tutorial-title">{currentStep.title}</h2>
        <p className="tutorial-desc">{currentStep.desc}</p>
        
        <div className="tutorial-actions">
          {step > 1 && (
            <button className="tutorial-back" onClick={() => setStep(step - 1)}>
              ← {t('back', 'Voltar')}
            </button>
          )}
          <button className="tutorial-next" onClick={handleNext} data-testid="tutorial-next">
            {step < 3 ? t('next', 'Próximo') : t('start_using', 'Começar a usar')} →
          </button>
        </div>
      </div>
    </div>
  );
}

function App() {
  const { t, currentLang } = useI18n();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [stream, setStream] = useState(null);
  const streamRef = useRef(null); // Ref para acessar stream no cleanup
  const [error, setError] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [dishes, setDishes] = useState([]);
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [lastImageBlob, setLastImageBlob] = useState(null);
  const [newDishName, setNewDishName] = useState("");
  const [creatingDish, setCreatingDish] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");
  const [multiMode, setMultiMode] = useState(false);
  const [multiResult, setMultiResult] = useState(null);
  const [cameraError, setCameraError] = useState(null);
  const [previewImageUrl, setPreviewImageUrl] = useState(null); // Preview da imagem selecionada
  const [showMultiCorrection, setShowMultiCorrection] = useState(false); // Modal correção multi
  const [multiCorrections, setMultiCorrections] = useState({ principal: '', acompanhamentos: '' }); // Correções
  // Fluxo Único Inteligente - acumula itens do prato
  const [plateItems, setPlateItems] = useState([]); // Lista de itens identificados
  const [showAddMore, setShowAddMore] = useState(false); // Modal "Adicionar mais?"
  const [showFirstTimeHelp, setShowFirstTimeHelp] = useState(false); // Popup explicativo primeira vez
  const [viewMode, setViewMode] = useState('buffet'); // 'buffet' = vista rápida, 'mesa' = vista completa
  // IA sob demanda
  const [loadingIA, setLoadingIA] = useState(false); // Carregando IA
  // Galeria de fotos capturadas
  const [photoGallery, setPhotoGallery] = useState(() => {
    const saved = localStorage.getItem('soulnutri_gallery');
    return saved ? JSON.parse(saved) : [];
  });
  const [showGalleryView, setShowGalleryView] = useState(false); // Modal galeria
  // Modo Scanner Contínuo para Buffet (DESATIVADO - usando modo foto simples)
  const [scannerMode, setScannerMode] = useState(false); // Desativado por padrão
  const [lastScanTime, setLastScanTime] = useState(0);
  const [scannerResult, setScannerResult] = useState(null); // Resultado do scanner (overlay)
  const scanIntervalRef = useRef(null);
  // Premium states
  const [showPremium, setShowPremium] = useState(null); // null, 'login', 'register', 'dashboard', 'profile'
  
  // Radar de Notícias - Fatos sobre alimentos
  const [radarInfo, setRadarInfo] = useState(null); // {has_alert, message, facts}
  const [showRadarDetails, setShowRadarDetails] = useState(false); // Modal com fatos detalhados
  
  const [premiumUser, setPremiumUser] = useState(null);
  const [dailySummary, setDailySummary] = useState(null);
  const [showCheckin, setShowCheckin] = useState(false); // Check-in de refeição
  const [personalizedTips, setPersonalizedTips] = useState(null); // Dicas personalizadas
  // Menu e PWA
  const [showMenu, setShowMenu] = useState(false);
  const [mealRegistered, setMealRegistered] = useState(false); // Confirmação de registro
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstalled, setIsInstalled] = useState(false);
  // Tela de permissões unificada
  const [showPermissions, setShowPermissions] = useState(() => {
    return !localStorage.getItem('soulnutri_permissions_granted');
  });
  const [permissionsStatus, setPermissionsStatus] = useState({
    camera: 'pending',
    location: 'pending'
  });
  // Welcome popup com seleção de idioma
  const [showWelcome, setShowWelcome] = useState(() => {
    return !localStorage.getItem('soulnutri_welcomed');
  });
  // Tutorial do Scanner Contínuo
  const [showScannerTutorial, setShowScannerTutorial] = useState(false);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const loadingRef = useRef(false);
  const abortControllerRef = useRef(null);
  const mountedRef = useRef(true);
  const lastTouchRef = useRef(0);

  // Função para solicitar todas as permissões de uma vez
  const requestAllPermissions = async () => {
    let cameraGranted = false;
    let locationGranted = false;
    
    // 1. Solicitar permissão de câmera
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      stream.getTracks().forEach(t => t.stop());
      cameraGranted = true;
      setPermissionsStatus(prev => ({ ...prev, camera: 'granted' }));
    } catch (e) {
      setPermissionsStatus(prev => ({ ...prev, camera: 'denied' }));
    }
    
    // Marcar permissões como solicitadas
    localStorage.setItem('soulnutri_permissions_granted', 'true');
    setShowPermissions(false);
    
    // Iniciar câmera se permitido
    if (cameraGranted) {
      startCamera();
    }
  };

  useEffect(() => { 
    mountedRef.current = true;
    checkStatus(); 
    
    // Só inicia câmera automaticamente se as permissões já foram concedidas
    if (!showPermissions) {
      startCamera();
    }
    
    loadDishes();
    checkPremiumSession();
    
    // Detectar se já está instalado como PWA
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
    }
    
    // Capturar evento de instalação PWA
    const handleBeforeInstall = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };
    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    
    // Gerenciar câmera quando o app perde/ganha foco (previne travamentos)
    let cameraWasActive = false;
    const handleVisibility = () => {
      if (document.hidden) {
        // Salvar estado antes de parar
        cameraWasActive = !!streamRef.current;
        if (cameraWasActive) {
          console.log('[Camera] App em background, pausando...');
          stopCameraInternal();
        }
      } else if (cameraWasActive) {
        // Só reinicia se estava ativa antes
        console.log('[Camera] App em foreground, retomando...');
        setTimeout(() => startCamera(), 500);
      }
    };
    document.addEventListener('visibilitychange', handleVisibility);
    
    return () => {
      mountedRef.current = false;
      stopCameraInternal();
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
      document.removeEventListener('visibilitychange', handleVisibility);
      // Cancelar requisições pendentes
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const checkStatus = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      const res = await fetch(`${API}/ai/status`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (mountedRef.current) setStatus(await res.json());
    } catch { 
      if (mountedRef.current) setStatus({ ok: false }); 
    }
  };

  const loadDishes = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      const res = await fetch(`${API}/ai/dishes`, { signal: controller.signal });
      clearTimeout(timeoutId);
      const data = await res.json();
      if (data.ok && mountedRef.current) setDishes(data.dishes || []);
    } catch (e) { console.error('Erro ao carregar pratos:', e); }
  };

  // Verificar sessão Premium salva
  const checkPremiumSession = async () => {
    try {
      const pin = localStorage.getItem('soulnutri_pin');
      const nome = localStorage.getItem('soulnutri_nome');
      if (pin && nome) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);
        const fd = new FormData();
        fd.append('pin', pin);
        fd.append('nome', nome);
        const res = await fetch(`${API}/premium/login`, { 
          method: 'POST', 
          body: fd,
          signal: controller.signal 
        });
        clearTimeout(timeoutId);
        const data = await res.json();
        if (data.ok && mountedRef.current) {
          setPremiumUser(data.user);
          loadDailySummary();
        }
      }
    } catch (e) {
      console.error('Erro ao verificar sessão:', e);
    }
  };

  // Carregar resumo diário
  const loadDailySummary = async () => {
    try {
      const pin = localStorage.getItem('soulnutri_pin');
      const nome = localStorage.getItem('soulnutri_nome');
      if (!pin || !nome) return;
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      const fd = new FormData();
      fd.append('pin', pin);
      fd.append('nome', nome);
      const res = await fetch(`${API}/premium/login`, { 
        method: 'POST', 
        body: fd,
        signal: controller.signal 
      });
      clearTimeout(timeoutId);
      const data = await res.json();
      
      if (!mountedRef.current) return;
      
      if (data.ok && data.daily_log) {
        setDailySummary({
          nome: data.user.nome,
          meta: data.user.meta_calorica?.meta_sugerida || 2000,
          consumido: data.daily_log.calorias_total || 0,
          restante: (data.user.meta_calorica?.meta_sugerida || 2000) - (data.daily_log.calorias_total || 0),
          percentual: ((data.daily_log.calorias_total || 0) / (data.user.meta_calorica?.meta_sugerida || 2000)) * 100,
          pratos: data.daily_log.pratos || [],
          totais: {
            calorias: data.daily_log.calorias_total || 0,
            proteinas: data.daily_log.proteinas_total || 0,
            carboidratos: data.daily_log.carboidratos_total || 0,
            gorduras: data.daily_log.gorduras_total || 0
          }
        });
      } else if (data.ok) {
        setDailySummary({
          nome: data.user.nome,
          meta: data.user.meta_calorica?.meta_sugerida || 2000,
          consumido: 0,
          restante: data.user.meta_calorica?.meta_sugerida || 2000,
          percentual: 0,
          pratos: [],
          totais: { calorias: 0, proteinas: 0, carboidratos: 0, gorduras: 0 }
        });
      }
    } catch (e) {
      console.error('Erro ao carregar resumo:', e);
    }
  };

  // Registrar refeição automaticamente após identificar
  const logMealToPremium = async (prato) => {
    if (!premiumUser || !mountedRef.current) return false;
    
    try {
      const pin = localStorage.getItem('soulnutri_pin');
      if (!pin) return false;
      
      const fd = new FormData();
      fd.append('pin', pin);
      fd.append('prato_nome', prato.dish_display || prato.nome || 'Prato');
      fd.append('calorias', parseFloat(prato.nutrition?.calorias?.replace(/[^\d]/g, '') || prato.calorias?.replace?.(/[^\d]/g, '') || 200));
      fd.append('proteinas', parseFloat(prato.nutrition?.proteinas?.replace(/[^\d]/g, '') || prato.proteinas?.replace?.(/[^\d]/g, '') || 10));
      fd.append('carboidratos', parseFloat(prato.nutrition?.carboidratos?.replace(/[^\d]/g, '') || prato.carboidratos?.replace?.(/[^\d]/g, '') || 25));
      fd.append('gorduras', parseFloat(prato.nutrition?.gorduras?.replace(/[^\d]/g, '') || prato.gorduras?.replace?.(/[^\d]/g, '') || 8));
      
      console.log('[PREMIUM] Registrando refeição:', prato.dish_display);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      const res = await fetch(`${API}/premium/log-meal`, { 
        method: 'POST', 
        body: fd,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if (!mountedRef.current) return false;
      
      const data = await res.json();
      console.log('[PREMIUM] Resposta log-meal:', data);
      
      if (data.ok) {
        setDailySummary(prev => ({
          ...prev,
          consumido: data.consumido,
          restante: data.restante,
          percentual: data.percentual,
          pratos: [...(prev?.pratos || []), { nome: prato.dish_display, calorias: fd.get('calorias'), hora: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) }]
        }));
        return true;
      }
      return false;
    } catch (e) {
      console.error('Erro ao registrar refeição:', e);
      return false;
    }
  };

  // Logout Premium
  const handlePremiumLogout = () => {
    localStorage.removeItem('soulnutri_pin');
    localStorage.removeItem('soulnutri_nome');
    localStorage.removeItem('soulnutri_user');
    setPremiumUser(null);
    setDailySummary(null);
    setShowPremium(null);
  };

  const startCamera = async () => {
    try {
      setCameraError(null);
      console.log('[Camera] Iniciando...');
      
      // Verificar se componente ainda está montado
      if (!mountedRef.current) {
        console.log('[Camera] Componente desmontado, abortando...');
        return;
      }
      
      // Verificar se mediaDevices está disponível
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error('[Camera] mediaDevices não disponível');
        setCameraError('not_supported');
        return;
      }
      
      // Parar stream anterior se existir (com try-catch para evitar erros)
      try {
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(t => {
            try { t.stop(); } catch(e) { console.warn('[Camera] Erro ao parar track:', e); }
          });
          streamRef.current = null;
        }
      } catch (e) {
        console.warn('[Camera] Erro ao limpar stream anterior:', e);
      }
      
      // Resolução reduzida para economizar memória em celulares
      // Safari/Mac: tentar primeiro com facingMode, depois sem
      let s;
      try {
        s = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            facingMode: 'environment', 
            width: { ideal: 640, max: 1280 }, 
            height: { ideal: 480, max: 720 } 
          } 
        });
      } catch (firstError) {
        console.warn('[Camera] Falhou com facingMode environment, tentando sem:', firstError);
        // Fallback: tentar sem facingMode (para webcams de Mac/desktop)
        try {
          s = await navigator.mediaDevices.getUserMedia({ 
            video: { 
              width: { ideal: 640, max: 1280 }, 
              height: { ideal: 480, max: 720 } 
            } 
          });
        } catch (secondError) {
          console.warn('[Camera] Falhou sem facingMode, tentando básico:', secondError);
          // Último recurso: apenas video: true
          s = await navigator.mediaDevices.getUserMedia({ video: true });
        }
      }
      
      // Verificar novamente se ainda está montado após await
      if (!mountedRef.current) {
        console.log('[Camera] Componente desmontado durante inicialização, liberando recursos...');
        s.getTracks().forEach(t => t.stop());
        return;
      }
      
      console.log('[Camera] Stream obtido:', s);
      streamRef.current = s;
      setStream(s);
      
      if (videoRef.current) {
        videoRef.current.srcObject = s;
        // Aguardar video estar pronto
        videoRef.current.onloadedmetadata = () => {
          console.log('[Camera] Video conectado e pronto');
        };
      }
    } catch (err) { 
      console.error("[Camera] Erro:", err);
      if (mountedRef.current) {
        setCameraError(err.name === 'NotAllowedError' ? 'permission_denied' : 'camera_error');
      }
    }
  };
  
  // Função interna para parar câmera sem depender de state
  const stopCameraInternal = () => {
    try {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => {
          try { t.stop(); } catch(e) { console.warn('[Camera] Erro ao parar track:', e); }
        });
        streamRef.current = null;
      }
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    } catch (e) {
      console.warn('[Camera] Erro ao parar câmera:', e);
    }
  };

  const stopCamera = () => { 
    stopCameraInternal();
    setStream(null);
  };
  
  const handleCameraTouch = useCallback(() => {
    // Prevenir cliques múltiplos (debounce de 1s)
    const now = Date.now();
    if (now - lastTouchRef.current < 1000) return;
    lastTouchRef.current = now;
    
    if (loadingRef.current || !videoRef.current || !canvasRef.current) return;
    
    const v = videoRef.current, c = canvasRef.current;
    // Verificar se o vídeo está pronto
    if (v.videoWidth === 0 || v.videoHeight === 0) {
      console.warn('Vídeo ainda não está pronto');
      return;
    }
    
    // Limitar tamanho máximo do canvas para economizar memória
    const maxSize = 800;
    let w = v.videoWidth;
    let h = v.videoHeight;
    if (w > maxSize || h > maxSize) {
      const ratio = Math.min(maxSize / w, maxSize / h);
      w = Math.round(w * ratio);
      h = Math.round(h * ratio);
    }
    
    c.width = w; 
    c.height = h;
    const ctx = c.getContext('2d');
    ctx.drawImage(v, 0, 0, w, h);
    
    // Qualidade reduzida para economizar memória
    c.toBlob(b => {
      if (b && mountedRef.current) {
        setLastImageBlob(b);
        identifyImage(b);
      }
      // Limpar canvas após uso
      ctx.clearRect(0, 0, w, h);
    }, 'image/jpeg', 0.7);
  }, [multiMode]);

  const identifyImage = async (blob) => {
    // Cancelar requisição anterior se existir
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    loadingRef.current = true;
    setLoading(true);
    setResult(null);
    setMultiResult(null);
    setError(null);
    setFeedbackSent(false);
    setShowFeedback(false);
    
    const fd = new FormData(); 
    fd.append("file", blob, "photo.jpg");
    fd.append("country", "BR");
    
    // Se for Premium, enviar credenciais para receber dados exclusivos
    try {
      const pin = localStorage.getItem('soulnutri_pin');
      const nome = localStorage.getItem('soulnutri_nome');
      if (pin && nome && !multiMode) {
        fd.append("pin", pin);
        fd.append("nome", nome);
      }
    } catch (e) {
      console.warn('localStorage não disponível:', e);
    }
    
    // Criar AbortController com timeout
    abortControllerRef.current = new AbortController();
    const timeoutId = setTimeout(() => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    }, REQUEST_TIMEOUT);
    
    try {
      const t = Date.now();
      const endpoint = multiMode ? `${API}/ai/identify-multi` : `${API}/ai/identify`;
      const res = await fetch(endpoint, { 
        method: "POST", 
        body: fd,
        signal: abortControllerRef.current.signal
      });
      clearTimeout(timeoutId);
      
      if (!mountedRef.current) return;
      
      // Verificar se a resposta foi bem sucedida
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Erro do servidor: ${res.status} - ${errorText.substring(0, 100)}`);
      }
      
      const data = await res.json();
      
      if (multiMode) {
        setMultiResult({ ...data, totalTime: Date.now() - t });
      } else {
        const resultWithTime = { ...data, totalTime: Date.now() - t };
        setResult(resultWithTime);
        // Salvar foto na galeria se identificou com sucesso
        if (resultWithTime.ok && resultWithTime.identified && previewImageUrl) {
          saveToGallery(previewImageUrl, resultWithTime.dish_display, resultWithTime);
        }
        // Buscar informações do Radar de Notícias (sem consumir créditos)
        if (resultWithTime.ok && resultWithTime.identified) {
          try {
            const ingredientes = resultWithTime.ingredientes?.join(',') || '';
            console.log('[RADAR] Buscando para:', resultWithTime.dish_display, 'ingredientes:', ingredientes);
            const radarRes = await fetch(`${API}/radar/alimentos/${encodeURIComponent(resultWithTime.dish_display)}?ingredientes=${encodeURIComponent(ingredientes)}`);
            const radarData = await radarRes.json();
            console.log('[RADAR] Resposta:', radarData);
            // Mostrar Radar se tiver QUALQUER conteúdo (alerta, voce_sabia, combinacoes)
            if (radarData.ok && radarData.radar && 
                (radarData.radar.has_alert || radarData.radar.voce_sabia || radarData.radar.combinacoes?.length > 0)) {
              console.log('[RADAR] ✅ Definindo radarInfo:', radarData.radar);
              setRadarInfo(radarData.radar);
            } else {
              console.log('[RADAR] ❌ Sem conteúdo relevante');
              setRadarInfo(null);
            }
          } catch (radarErr) {
            console.log('[RADAR] Erro ao buscar fatos:', radarErr);
            setRadarInfo(null);
          }
        }
        // NÃO mostrar modal automaticamente - deixar usuário ver as informações primeiro
      }
    } catch (e) { 
      clearTimeout(timeoutId);
      if (!mountedRef.current) return;
      
      if (e.name === 'AbortError') {
        setError('Tempo limite excedido. Tente novamente.');
      } else if (e.message && e.message.includes('postMessage')) {
        // Erro do preview iframe - ignorar silenciosamente
        console.warn('[IDENTIFY] Erro postMessage ignorado (preview iframe)');
      } else {
        setError(e.message || 'Erro de conexão');
      }
    } finally { 
      loadingRef.current = false;
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  };

  // Fluxo Único: Adicionar item atual à lista e preparar para próximo
  const addItemToPlate = async () => {
    if (result?.ok && result?.identified) {
      const newItem = {
        id: Date.now(),
        dish: result.dish,
        dish_display: result.dish_display,
        category: result.category,
        calorias: result.nutrition?.calorias || result.calorias_estimadas || '0 kcal',
        proteinas: result.nutrition?.proteinas || '0g',
        carboidratos: result.nutrition?.carboidratos || '0g',
        gorduras: result.nutrition?.gorduras || '0g',
        ingredientes: result.ingredientes || [],
        beneficios: result.beneficios || [],
        riscos: result.riscos || [],
        alergenos: {
          gluten: result.contem_gluten,
          lactose: result.contem_lactose,
          ovo: result.contem_ovo,
          castanhas: result.contem_castanhas,
          frutosMar: result.contem_frutos_mar
        },
        score: result.score
      };
      console.log('[DEBUG] Adicionando item ao prato:', newItem.dish_display, 'Calorias:', newItem.calorias);
      setPlateItems(prev => {
        const updated = [...prev, newItem];
        console.log('[DEBUG] plateItems agora tem', updated.length, 'itens');
        return updated;
      });
      
      // Registrar no contador Premium se usuário estiver logado
      if (premiumUser) {
        const registered = await logMealToPremium({
          dish_display: newItem.dish_display,
          nutrition: {
            calorias: newItem.calorias,
            proteinas: newItem.proteinas,
            carboidratos: newItem.carboidratos,
            gorduras: newItem.gorduras
          }
        });
        if (registered) {
          setMealRegistered(true);
          // Esconder após 3 segundos
          setTimeout(() => setMealRegistered(false), 3000);
        }
      }
    }
    setShowAddMore(false);
    setResult(null);
    setPreviewImageUrl(null);
  };

  // Fluxo Único: Finalizar prato e mostrar resumo consolidado
  const finishPlate = () => {
    console.log('[DEBUG] finishPlate chamado, result:', result?.dish_display);
    console.log('[DEBUG] plateItems antes:', plateItems.length, 'itens');
    
    if (result?.ok && result?.identified) {
      // Adicionar último item se houver
      const newItem = {
        id: Date.now(),
        dish: result.dish,
        dish_display: result.dish_display,
        category: result.category,
        calorias: result.nutrition?.calorias || result.calorias_estimadas || '0 kcal',
        proteinas: result.nutrition?.proteinas || '0g',
        carboidratos: result.nutrition?.carboidratos || '0g',
        gorduras: result.nutrition?.gorduras || '0g',
        ingredientes: result.ingredientes || [],
        beneficios: result.beneficios || [],
        riscos: result.riscos || [],
        alergenos: {
          gluten: result.contem_gluten,
          lactose: result.contem_lactose,
          ovo: result.contem_ovo,
          castanhas: result.contem_castanhas,
          frutosMar: result.contem_frutos_mar
        },
        score: result.score
      };
      console.log('[DEBUG] Adicionando último item:', newItem.dish_display, 'Calorias:', newItem.calorias);
      setPlateItems(prev => {
        const updated = [...prev, newItem];
        console.log('[DEBUG] plateItems final:', updated.length, 'itens');
        return updated;
      });
    }
    setShowAddMore(false);
    setResult(null);
    setViewMode('mesa'); // Mudar para vista consolidada
  };

  // Fluxo Único: Limpar prato e começar novo
  const clearPlate = () => {
    setPlateItems([]);
    setResult(null);
    setMultiResult(null);
    setPreviewImageUrl(null);
    setShowAddMore(false);
    setScannerResult(null);
  };

  // ═══════════════════════════════════════════════════════════════
  // GALERIA - Salvar e visualizar fotos capturadas
  // ═══════════════════════════════════════════════════════════════
  
  const saveToGallery = (imageUrl, dishName, result) => {
    const newPhoto = {
      id: Date.now(),
      imageUrl,
      dishName: dishName || 'Prato não identificado',
      date: new Date().toLocaleString('pt-BR'),
      result: result ? {
        calorias: result.nutrition?.calorias || result.calorias_estimadas,
        categoria: result.category
      } : null
    };
    
    setPhotoGallery(prev => {
      const updated = [newPhoto, ...prev].slice(0, 50); // Máximo 50 fotos
      localStorage.setItem('soulnutri_gallery', JSON.stringify(updated));
      return updated;
    });
  };
  
  const deleteFromGallery = (photoId) => {
    setPhotoGallery(prev => {
      const updated = prev.filter(p => p.id !== photoId);
      localStorage.setItem('soulnutri_gallery', JSON.stringify(updated));
      return updated;
    });
  };
  
  const clearGallery = () => {
    if (window.confirm('Apagar todas as fotos da galeria?')) {
      setPhotoGallery([]);
      localStorage.removeItem('soulnutri_gallery');
    }
  };

  // ═══════════════════════════════════════════════════════════════
  // MODO SCANNER CONTÍNUO - Detecta mudança de imagem e identifica
  // ═══════════════════════════════════════════════════════════════
  
  const lastFrameDataRef = useRef(null);
  const scanningRef = useRef(false);
  const lastScanResultRef = useRef(null); // Cache do último resultado
  const scanCooldownRef = useRef(false); // Cooldown entre scans
  
  // Função para calcular diferença entre frames
  const calculateFrameDifference = (currentData, previousData) => {
    if (!previousData || currentData.length !== previousData.length) return 1;
    
    let diff = 0;
    const sampleSize = Math.min(1000, currentData.length / 4); // Amostra de pixels
    const step = Math.floor(currentData.length / 4 / sampleSize);
    
    for (let i = 0; i < currentData.length; i += step * 4) {
      diff += Math.abs(currentData[i] - previousData[i]); // R
      diff += Math.abs(currentData[i + 1] - previousData[i + 1]); // G
      diff += Math.abs(currentData[i + 2] - previousData[i + 2]); // B
    }
    
    return diff / (sampleSize * 3 * 255); // Normalizado 0-1
  };

  const performScan = useCallback(async () => {
    // Não escanear se já está escaneando, carregando, em cooldown, ou sem câmera
    if (scanningRef.current || loadingRef.current || scanCooldownRef.current || !videoRef.current || !canvasRef.current || !stream) return;
    
    const v = videoRef.current;
    const c = canvasRef.current;
    
    // Verificar se o vídeo está pronto
    if (v.videoWidth === 0 || v.videoHeight === 0) return;
    
    // Tamanho pequeno para detecção de mudança (rápido)
    const detectSize = 160;
    c.width = detectSize;
    c.height = detectSize;
    const ctx = c.getContext('2d');
    ctx.drawImage(v, 0, 0, detectSize, detectSize);
    
    // Obter dados do frame atual
    const imageData = ctx.getImageData(0, 0, detectSize, detectSize);
    const currentData = imageData.data;
    
    // Calcular diferença com frame anterior
    const difference = calculateFrameDifference(currentData, lastFrameDataRef.current);
    
    // Se mudança significativa (> 30%), fazer reconhecimento
    // Threshold maior = menos scans desnecessários
    if (difference > 0.30) {
      // Salvar frame atual
      lastFrameDataRef.current = new Uint8ClampedArray(currentData);
      
      // Ativar cooldown (evita múltiplos scans seguidos)
      scanCooldownRef.current = true;
      setTimeout(() => { scanCooldownRef.current = false; }, 2000);
      
      // Capturar em maior resolução para identificação
      const scanSize = 640;
      let w = v.videoWidth;
      let h = v.videoHeight;
      if (w > scanSize || h > scanSize) {
        const ratio = Math.min(scanSize / w, scanSize / h);
        w = Math.round(w * ratio);
        h = Math.round(h * ratio);
      }
      
      c.width = w;
      c.height = h;
      ctx.drawImage(v, 0, 0, w, h);
      
      // Converter e identificar
      c.toBlob(async (blob) => {
        if (!blob || !mountedRef.current || scanningRef.current) return;
        
        scanningRef.current = true;
        
        try {
          const fd = new FormData();
          fd.append("file", blob, "scan.jpg");
          fd.append("country", "BR");
          
          const res = await fetch(`${API}/ai/identify`, {
            method: "POST",
            body: fd
          });
          
          if (!mountedRef.current) return;
          
          const data = await res.json();
          
          // Só mostrar se score >= 0.7 (mais confiável)
          if (data.ok && data.identified && data.score >= 0.7) {
            // Verificar se é diferente do último resultado (evita repetições)
            const newDish = data.dish_display;
            if (newDish !== lastScanResultRef.current) {
              lastScanResultRef.current = newDish;
              setScannerResult({
                dish: data.dish,
                dish_display: data.dish_display,
                categoria: data.category || data.categoria,
                calorias: data.nutrition?.calorias || '~150 kcal',
                score: data.score,
                confidence: data.confidence,
                beneficios: data.beneficios || [],
                riscos: data.riscos || [],
                contem_gluten: data.contem_gluten,
                timestamp: Date.now()
              });
            }
          } else if (difference > 0.5) {
            // Mudança muito grande mas não identificado - limpar resultado anterior
            setScannerResult(null);
            lastScanResultRef.current = null;
          }
        } catch (e) {
          console.warn('Scanner error:', e);
        } finally {
          scanningRef.current = false;
        }
        
        // Limpar canvas
        ctx.clearRect(0, 0, w, h);
      }, 'image/jpeg', 0.7);
    }
  }, [stream]);

  // Loop de detecção de mudança (verifica a cada 1.5s se imagem mudou)
  // Intervalo maior para reduzir requisições e dar tempo para IA processar
  useEffect(() => {
    if (scannerMode && stream && !result && !loading) {
      scanIntervalRef.current = setInterval(performScan, 1500);
      // Primeiro scan após 500ms
      setTimeout(performScan, 500);
    }
    
    return () => {
      if (scanIntervalRef.current) {
        clearInterval(scanIntervalRef.current);
        scanIntervalRef.current = null;
      }
    };
  }, [scannerMode, stream, result, loading, performScan]);

  // Toque no overlay para ver detalhes completos
  const handleScannerTap = useCallback(() => {
    if (scannerResult) {
      // Converter scanner result para result completo
      setResult({
        ok: true,
        identified: true,
        ...scannerResult
      });
      setScannerResult(null);
    }
  }, [scannerResult]);

  // Calcular dados CONSOLIDADOS do prato (para vista "mesa")
  const plateConsolidated = useMemo(() => {
    if (plateItems.length === 0) return null;
    
    // Função para extrair número de string tipo "120 kcal" ou "15g"
    const parseNum = (val) => {
      if (typeof val === 'number') return val;
      if (typeof val === 'string') return parseFloat(val.replace(/[^\d.]/g, '')) || 0;
      return 0;
    };
    
    // Somar nutrientes
    const totals = plateItems.reduce((acc, item) => ({
      calorias: acc.calorias + parseNum(item.calorias),
      proteinas: acc.proteinas + parseNum(item.proteinas),
      carboidratos: acc.carboidratos + parseNum(item.carboidratos),
      gorduras: acc.gorduras + parseNum(item.gorduras)
    }), { calorias: 0, proteinas: 0, carboidratos: 0, gorduras: 0 });
    
    // Coletar todos os ingredientes únicos
    const allIngredientes = [...new Set(plateItems.flatMap(item => item.ingredientes || []))];
    
    // Coletar benefícios únicos (máx 5)
    const allBeneficios = [...new Set(plateItems.flatMap(item => item.beneficios || []))].slice(0, 5);
    
    // Coletar riscos únicos (máx 3)
    const allRiscos = [...new Set(plateItems.flatMap(item => item.riscos || []))].slice(0, 3);
    
    // Verificar alérgenos presentes em qualquer item (objeto alergenos ou texto nos riscos)
    const riscosLower = allRiscos.join(' ').toLowerCase();
    const contemGluten = plateItems.some(item => item.alergenos?.gluten) || 
                         riscosLower.includes('glúten') || riscosLower.includes('gluten');
    const contemLactose = plateItems.some(item => item.alergenos?.lactose) || 
                          riscosLower.includes('lactose') || riscosLower.includes('leite');
    const contemOvo = plateItems.some(item => item.alergenos?.ovo) || 
                      riscosLower.includes('ovo');
    const contemCastanhas = plateItems.some(item => item.alergenos?.castanhas) || 
                            riscosLower.includes('castanha') || riscosLower.includes('amendoim') || riscosLower.includes('nozes');
    const contemFrutosMar = plateItems.some(item => item.alergenos?.frutosMar) || 
                            riscosLower.includes('peixe') || riscosLower.includes('camarão') || 
                            riscosLower.includes('crustáceo') || riscosLower.includes('frutos do mar');
    const contemSoja = plateItems.some(item => item.alergenos?.soja) || 
                       riscosLower.includes('soja');
    
    // Filtrar riscos que NÃO são sobre alérgenos (para evitar duplicação)
    const riscosNaoAlergenos = allRiscos.filter(r => {
      const lower = r.toLowerCase();
      return !(lower.includes('alérgeno') || lower.includes('glúten') || lower.includes('lactose') || 
               lower.includes('ovo') || lower.includes('castanha') || lower.includes('peixe') ||
               lower.includes('camarão') || lower.includes('soja'));
    });
    
    // Categorias presentes
    const categorias = [...new Set(plateItems.map(item => item.category).filter(Boolean))];
    
    return {
      itens: plateItems.map(i => i.dish_display),
      totalItens: plateItems.length,
      nutrition: {
        calorias: `${Math.round(totals.calorias)} kcal`,
        proteinas: `${Math.round(totals.proteinas)}g`,
        carboidratos: `${Math.round(totals.carboidratos)}g`,
        gorduras: `${Math.round(totals.gorduras)}g`
      },
      ingredientes: allIngredientes,
      beneficios: allBeneficios,
      riscos: riscosNaoAlergenos.length > 0 ? riscosNaoAlergenos : allRiscos.slice(0, 2),
      contemGluten,
      contemLactose,
      contemOvo,
      contemCastanhas,
      contemFrutosMar,
      contemSoja,
      categorias
    };
  }, [plateItems]);

  // Totais simples para exibição rápida
  const plateTotals = {
    calorias: plateConsolidated?.nutrition?.calorias ? parseFloat(plateConsolidated.nutrition.calorias) : 0,
    itens: plateItems.length
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Criar URL de preview para mostrar a imagem
      const previewUrl = URL.createObjectURL(file);
      setPreviewImageUrl(previewUrl);
      setLastImageBlob(file);
      identifyImage(file);
    }
  };

  const clearResult = () => {
    // Cancelar requisições pendentes
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setResult(null);
    setMultiResult(null);
    setError(null);
    setShowFeedback(false);
    setFeedbackSent(false);
    // Limpar preview da imagem
    if (previewImageUrl) {
      URL.revokeObjectURL(previewImageUrl);
      setPreviewImageUrl(null);
    }
    // Liberar memória do blob
    if (lastImageBlob) {
      URL.revokeObjectURL(URL.createObjectURL(lastImageBlob));
    }
    setLastImageBlob(null);
    setNewDishName("");
    setSearchFilter("");
  };

  // Enviar feedback - CORRETO
  const sendFeedbackCorrect = async () => {
    if (!lastImageBlob || !result?.dish) return;
    
    const fd = new FormData();
    fd.append("file", lastImageBlob, "photo.jpg");
    fd.append("dish_slug", result.dish);
    fd.append("is_correct", "true");
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const res = await fetch(`${API}/ai/feedback`, { 
        method: "POST", 
        body: fd,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if (!mountedRef.current) return;
      
      const data = await res.json();
      if (data.ok) {
        setFeedbackSent(true);
        setShowFeedback(false);
      }
    } catch (e) {
      console.error('Erro ao enviar feedback:', e);
    }
  };

  // Enviar feedback - INCORRETO (com correção) - VERSÃO LOCAL (SEM CRÉDITOS)
  const sendFeedbackIncorrect = async (correctSlug) => {
    if (!lastImageBlob) return;
    
    const fd = new FormData();
    fd.append("file", lastImageBlob, "photo.jpg");
    fd.append("dish_slug", correctSlug);
    fd.append("is_correct", "false");
    fd.append("original_dish", result?.dish || "");
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const res = await fetch(`${API}/ai/feedback`, { 
        method: "POST", 
        body: fd,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if (!mountedRef.current) return;
      
      const data = await res.json();
      if (data.ok) {
        setFeedbackSent(true);
        setShowFeedback(false);
        // Mostrar confirmação
        alert(`✅ Correção salva!\n\nA foto foi adicionada ao prato correto.\n💰 Créditos usados: 0`);
      }
    } catch (e) {
      console.error('Erro ao enviar feedback:', e);
    }
  };

  // SALVAR CORREÇÃO DE PRATO MÚLTIPLO
  const saveMultiCorrection = async () => {
    if (!lastImageBlob || !multiCorrections.principal.trim()) {
      alert('Por favor, informe pelo menos o prato principal');
      return;
    }
    
    setCreatingDish(true);
    
    try {
      // Converter blob para array buffer para evitar "body already read"
      const arrayBuffer = await lastImageBlob.arrayBuffer();
      const blob = new Blob([arrayBuffer], { type: 'image/jpeg' });
      
      // Salvar prato principal
      const fdPrincipal = new FormData();
      fdPrincipal.append("file", blob, "photo.jpg");
      fdPrincipal.append("dish_name", multiCorrections.principal.trim());
      
      // Adicionar acompanhamentos se existirem
      if (multiCorrections.acompanhamentos.trim()) {
        fdPrincipal.append("acompanhamentos", multiCorrections.acompanhamentos.trim());
      }
      
      const res = await fetch(`${API}/ai/create-dish`, { 
        method: "POST", 
        body: fdPrincipal
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      const data = await res.json();
      
      if (data.ok) {
        const pratoNome = multiCorrections.principal;
        setFeedbackSent(true);
        setShowMultiCorrection(false);
        setMultiCorrections({ principal: '', acompanhamentos: '' });
        alert(`✅ Prato "${pratoNome}" salvo com sucesso!\n\nA IA vai aprender com esta correção.`);
        loadDishes(); // Atualizar lista
      } else {
        alert(data.error || 'Erro ao salvar correção');
      }
    } catch (e) {
      console.error('Erro ao salvar correção:', e);
      alert('Erro ao salvar: ' + (e.message || 'Tente novamente'));
    } finally {
      setCreatingDish(false);
    }
  };

  // CRIAR PRATO NOVO - VERSÃO LOCAL (SEM CRÉDITOS)
  const createNewDish = async () => {
    if (!lastImageBlob || !newDishName.trim()) return;
    
    setCreatingDish(true);
    
    const fd = new FormData();
    fd.append("file", lastImageBlob, "photo.jpg");
    fd.append("dish_name", newDishName.trim());
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);
      
      // USAR ENDPOINT LOCAL (SEM CRÉDITOS)
      const res = await fetch(`${API}/ai/create-dish-local`, { 
        method: "POST", 
        body: fd,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if (!mountedRef.current) return;
      
      const data = await res.json();
      if (data.ok) {
        setFeedbackSent(true);
        setShowFeedback(false);
        const nomeSalvo = newDishName;
        setNewDishName("");
        
        // Atualizar lista de pratos
        loadDishes();
        
        // Mostrar confirmação clara ao usuário
        alert(`✅ ${data.message}\n\n📝 Prato: ${nomeSalvo}\n💰 Créditos usados: 0`);
        
        // Mostrar resultado do novo prato se tiver dados
        if (data.dish_info) {
          setResult({
            ok: true,
            identified: true,
            dish: data.dish_slug,
            dish_display: data.dish_name,
            confidence: 'alta',
            score: 1.0,
            message: 'Prato cadastrado com sucesso!',
            ...data.dish_info,
            source: 'new_dish'
          });
        }
      } else {
        alert(data.error || 'Erro ao criar prato');
      }
    } catch (e) {
      console.error('Erro ao criar prato:', e);
      if (e.name === 'AbortError') {
        alert('Tempo limite excedido. Tente novamente.');
      } else {
        alert('Erro ao criar prato: ' + (e.message || 'Erro de conexão'));
      }
    } finally {
      if (mountedRef.current) {
        setCreatingDish(false);
      }
    }
  };

  // MELHORAR IDENTIFICAÇÃO COM IA (sob demanda - consome créditos)
  const melhorarComIA = async () => {
    if (!lastImageBlob) {
      alert('Nenhuma imagem para analisar');
      return;
    }
    
    // Confirmar com usuário
    const confirmar = window.confirm(
      '🤖 Usar IA para melhorar identificação?\n\n' +
      '⚠️ Isso consome créditos do sistema.\n\n' +
      'Continuar?'
    );
    
    if (!confirmar) return;
    
    setLoadingIA(true);
    
    const fd = new FormData();
    fd.append("file", lastImageBlob, "photo.jpg");
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);
      
      const res = await fetch(`${API}/ai/identify-with-ai`, {
        method: "POST",
        body: fd,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      const data = await res.json();
      
      if (data.ok && data.identified) {
        // Atualizar resultado com dados da IA
        setResult(prev => ({
          ...prev,
          ...data,
          dish_display: data.dish_display,
          category: data.category,
          category_emoji: data.category_emoji,
          confidence: data.confidence || 'alta',
          ingredientes: data.ingredientes,
          beneficios: data.beneficios,
          descricao: data.descricao,
          source: 'gemini_ai',
          ia_disponivel: false // Já usou IA
        }));
        
        alert(`✅ IA identificou: ${data.dish_display}\n\n💰 Créditos consumidos`);
      } else {
        alert(`❌ IA não conseguiu identificar\n\n${data.error || 'Tente corrigir manualmente'}`);
      }
    } catch (e) {
      console.error('Erro ao chamar IA:', e);
      if (e.name === 'AbortError') {
        alert('Tempo limite excedido. Tente novamente.');
      } else {
        alert('Erro ao chamar IA: ' + (e.message || 'Erro de conexão'));
      }
    } finally {
      setLoadingIA(false);
    }
  };

  // Descartar foto
  const discardPhoto = () => {
    setShowFeedback(false);
    setFeedbackSent(true);
    setNewDishName("");
  };

  // Função para fechar welcome e mostrar tutorial se for primeira vez
  const handleWelcomeClose = () => {
    localStorage.setItem('soulnutri_welcomed', 'true');
    setShowWelcome(false);
    // Mostrar tutorial se nunca viu
    if (!localStorage.getItem('soulnutri_tutorial_seen')) {
      setTimeout(() => setShowScannerTutorial(true), 300);
    }
  };

  const r = result;
  
  // Config de confiança
  const confidenceConfig = {
    alta: { color: "#10b981", label: "ALTA CONFIANÇA", bg: "rgba(16,185,129,0.15)" },
    média: { color: "#f59e0b", label: "MÉDIA CONFIANÇA", bg: "rgba(245,158,11,0.15)" },
    baixa: { color: "#ef4444", label: "BAIXA CONFIANÇA", bg: "rgba(239,68,68,0.15)" }
  };
  
  const confData = confidenceConfig[r?.confidence] || confidenceConfig.baixa;
  
  // Cores das categorias
  const getCategoryStyle = (cat) => {
    switch(cat) {
      case 'vegano': return { bg: '#22c55e', color: '#fff' };
      case 'vegetariano': return { bg: '#fff', color: '#333', border: '1px solid #333' };
      case 'proteína animal': return { bg: '#f97316', color: '#fff' };
      default: return { bg: '#666', color: '#fff' };
    }
  };
  
  const catStyle = getCategoryStyle(r?.category);

  // Formatar alertas de alérgenos - SEMPRE MOSTRAR
  const getAllergenDisplay = (riscos) => {
    if (!riscos || riscos.length === 0) {
      return { hasAllergens: false, text: "✅ Não contém alérgenos conhecidos" };
    }
    
    const allergenRisks = riscos.filter(r => 
      r.toLowerCase().includes('alérgeno') || 
      r.toLowerCase().includes('contém') ||
      r.toLowerCase().includes('glúten') ||
      r.toLowerCase().includes('lactose') ||
      r.toLowerCase().includes('crustáceo') ||
      r.toLowerCase().includes('camarão') ||
      r.toLowerCase().includes('amendoim') ||
      r.toLowerCase().includes('soja') ||
      r.toLowerCase().includes('ovo')
    );
    
    if (allergenRisks.length === 0) {
      return { hasAllergens: false, text: "✅ Não contém alérgenos conhecidos" };
    }
    
    // Remover duplicações - priorizar "contém" sobre "pode conter"
    const seen = new Set();
    const uniqueAlerts = allergenRisks.filter(risco => {
      const key = risco.toLowerCase()
        .replace('pode conter traços de ', '')
        .replace('contém ', '')
        .replace('pode conter ', '')
        .trim();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
    
    return { 
      hasAllergens: true, 
      alerts: uniqueAlerts.map(risco => ({
        type: risco.toLowerCase().includes('pode conter') ? 'possible' : 'definite',
        text: risco
      }))
    };
  };

  const allergenInfo = getAllergenDisplay(r?.riscos);

  // Filtrar pratos na busca
  const filteredDishes = dishes.filter(d => 
    d.name.toLowerCase().includes(searchFilter.toLowerCase())
  );

  // Função para instalar PWA
  const handleInstallApp = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === 'accepted') {
        setIsInstalled(true);
      }
      setDeferredPrompt(null);
    }
    setShowMenu(false);
  };

  return (
    <div className="app">
      {/* Tela de Permissões Unificada */}
      {showPermissions && (
        <div className="permissions-screen" style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000,
          padding: '20px'
        }}>
          <img src="/images/soulnutri-logo.png" alt="SoulNutri" style={{ width: '120px', marginBottom: '24px' }} />
          <h2 style={{ color: '#fff', fontSize: '24px', marginBottom: '16px', textAlign: 'center' }}>
            Bem-vindo ao SoulNutri
          </h2>
          <p style={{ color: '#aaa', textAlign: 'center', marginBottom: '32px', maxWidth: '300px' }}>
            Para identificar seus pratos, precisamos de acesso à câmera.
          </p>
          
          <div style={{ 
            background: 'rgba(255,255,255,0.1)', 
            borderRadius: '16px', 
            padding: '24px',
            width: '100%',
            maxWidth: '320px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px', color: '#fff' }}>
              <span style={{ fontSize: '28px', marginRight: '16px' }}>📷</span>
              <div>
                <div style={{ fontWeight: 'bold' }}>Câmera</div>
                <div style={{ fontSize: '13px', color: '#aaa' }}>Para fotografar os pratos</div>
              </div>
              {permissionsStatus.camera === 'granted' && <span style={{ marginLeft: 'auto', color: '#22c55e' }}>✓</span>}
            </div>
          </div>
          
          <button
            onClick={requestAllPermissions}
            style={{
              marginTop: '32px',
              padding: '16px 48px',
              fontSize: '18px',
              fontWeight: 'bold',
              background: 'linear-gradient(135deg, #22c55e, #16a34a)',
              color: '#fff',
              border: 'none',
              borderRadius: '12px',
              cursor: 'pointer',
              boxShadow: '0 4px 20px rgba(34, 197, 94, 0.4)'
            }}
          >
            Permitir e Continuar
          </button>
          
          <button
            onClick={() => {
              localStorage.setItem('soulnutri_permissions_granted', 'true');
              setShowPermissions(false);
            }}
            style={{
              marginTop: '16px',
              padding: '12px 24px',
              fontSize: '14px',
              background: 'transparent',
              color: '#888',
              border: '1px solid #444',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            Pular por agora
          </button>
        </div>
      )}

      {/* Header com Logo e Menu */}
      <header className="hdr">
        <div className="logo-container">
          <img src="/images/soulnutri-logo.png" alt="SoulNutri" className="logo" />
          <span className="trademark">®</span>
        </div>
        <div className="header-right">
          <LanguageSelector />
          {status?.ready && <span className="st">✓ {status.total_dishes} pratos</span>}
          <button 
            className="menu-btn" 
            onClick={() => setShowMenu(!showMenu)}
            data-testid="menu-button"
          >
            ☰
          </button>
        </div>
      </header>

      {/* Toast de confirmação - Refeição registrada */}
      {mealRegistered && (
        <div 
          className="meal-registered-toast"
          data-testid="meal-registered-toast"
          style={{
            position: 'fixed',
            top: '70px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'linear-gradient(135deg, #22c55e, #16a34a)',
            color: 'white',
            padding: '16px 24px',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(34, 197, 94, 0.4)',
            zIndex: 9999,
            textAlign: 'center',
            animation: 'slideDown 0.3s ease-out'
          }}
        >
          <div style={{ fontSize: '24px', marginBottom: '4px' }}>✅</div>
          <div style={{ fontWeight: 'bold', fontSize: '16px' }}>Registrado com sucesso!</div>
          <div style={{ fontSize: '13px', opacity: 0.9, marginTop: '4px' }}>
            🍽️ Aproveite sua refeição!
          </div>
        </div>
      )}

      {/* Menu dropdown */}
      {showMenu && (
        <div className="menu-dropdown" data-testid="menu-dropdown">
          {!isInstalled && deferredPrompt && (
            <button className="menu-item install" onClick={handleInstallApp}>
              📲 Adicionar à tela inicial
            </button>
          )}
          {isInstalled && (
            <div className="menu-item installed">
              ✅ App instalado
            </div>
          )}
          {!deferredPrompt && !isInstalled && (
            <div className="menu-item info">
              📱 Para instalar: use o menu do navegador → &quot;Adicionar à tela inicial&quot;
            </div>
          )}
          <button className="menu-item" onClick={() => { setShowMenu(false); setShowScannerTutorial(true); }} data-testid="menu-tutorial">
            📸 {t('how_scanner_works', 'Como usar o SoulNutri')}
          </button>
          <button className="menu-item" onClick={() => { setShowMenu(false); checkStatus(); loadDishes(); }}>
            🔄 Atualizar pratos
          </button>
          <button className="menu-item" onClick={() => setShowMenu(false)}>
            ✕ Fechar
          </button>
        </div>
      )}

      {/* Câmera com moldura guia */}
      <div 
        className="cam-box" 
        onClick={cameraError ? startCamera : handleCameraTouch}
        data-testid="camera-container"
      >
        <video ref={videoRef} autoPlay playsInline muted />
        <canvas ref={canvasRef} hidden />
        
        {/* Erro de câmera */}
        {cameraError && (
          <div className="cam-error" data-testid="camera-error">
            <span>📷</span>
            <p>{cameraError === 'permission_denied' 
              ? t('permission_denied', 'Permissão negada. Toque para permitir.') 
              : t('camera_error', 'Câmera não disponível')}</p>
            <button onClick={(e) => { e.stopPropagation(); startCamera(); }}>
              🔄 {t('try_again', 'Tentar novamente')}
            </button>
          </div>
        )}
        
        {!cameraError && (
          <div className="cam-guide">
            <div className="guide-frame"></div>
            <span className="guide-text">{t('position_dish', 'Posicione o prato aqui')}</span>
          </div>
        )}
        
        {loading && (
          <div className="cam-loading">
            <span>🔍</span>
            <p>{t('loading', 'Identificando...')}</p>
          </div>
        )}
        
        {!loading && !r && !cameraError && (
          <div className="cam-hint">
            <span>👆</span>
            <p>Toque para fotografar</p>
          </div>
        )}

        {/* SCANNER OVERLAY - Mostra info em tempo real */}
        {scannerResult && !loading && !r && (
          <div 
            className="scanner-overlay" 
            onClick={handleScannerTap}
            data-testid="scanner-overlay"
          >
            <div className="scanner-result">
              <div className="scanner-header">
                <span className="scanner-icon">✅</span>
                <span className="scanner-dish">{scannerResult.dish_display}</span>
              </div>
              <div className="scanner-info">
                <span className="scanner-cal">{scannerResult.calorias}</span>
                <span className="scanner-cat">{scannerResult.categoria}</span>
              </div>
              {scannerResult.contem_gluten === false && (
                <span className="scanner-badge gluten-free">Sem glúten</span>
              )}
              {scannerResult.riscos?.length > 0 && (
                <span className="scanner-badge warning">⚠️ {scannerResult.riscos[0]}</span>
              )}
              <p className="scanner-tap">Toque para mais detalhes</p>
            </div>
          </div>
        )}
      </div>

      {/* Botões de ação */}
      <div className="action-btns">
        <button 
          className="action-btn upload" 
          onClick={() => fileInputRef.current?.click()}
          data-testid="upload-button"
          style={{ background: '#4a9eff' }}
        >
          📁 Foto
        </button>
        <button 
          className="action-btn gallery" 
          onClick={() => setShowGalleryView(true)}
          data-testid="gallery-button"
        >
          🖼️ {t('gallery', 'Galeria')} {photoGallery.length > 0 && `(${photoGallery.length})`}
        </button>
        <button 
          className="action-btn clear" 
          onClick={() => { clearResult(); clearPlate(); setViewMode('buffet'); }}
          disabled={!r && !multiResult && !error && plateItems.length === 0}
          data-testid="clear-button"
        >
          🗑️ Limpar
        </button>
      </div>

      {/* ══════════════════════════════════════════════════════════
          MODAL GALERIA DE FOTOS
          ══════════════════════════════════════════════════════════ */}
      {showGalleryView && (
        <div className="gallery-modal-overlay" onClick={() => setShowGalleryView(false)}>
          <div className="gallery-modal" onClick={e => e.stopPropagation()}>
            <div className="gallery-header">
              <h2>🖼️ Minhas Fotos</h2>
              <button className="close-btn" onClick={() => setShowGalleryView(false)}>✕</button>
            </div>
            
            {photoGallery.length === 0 ? (
              <div className="gallery-empty">
                <p>📷 Nenhuma foto ainda</p>
                <p>Suas fotos de pratos aparecerão aqui</p>
              </div>
            ) : (
              <>
                <div className="gallery-grid">
                  {photoGallery.map(photo => (
                    <div key={photo.id} className="gallery-item">
                      <img src={photo.imageUrl} alt={photo.dishName} />
                      <div className="gallery-item-info">
                        <span className="gallery-item-name">{photo.dishName}</span>
                        <span className="gallery-item-date">{photo.date}</span>
                        {photo.result?.calorias && (
                          <span className="gallery-item-cal">{photo.result.calorias}</span>
                        )}
                      </div>
                      <button 
                        className="gallery-delete-btn"
                        onClick={() => deleteFromGallery(photo.id)}
                      >
                        🗑️
                      </button>
                    </div>
                  ))}
                </div>
                <button className="gallery-clear-btn" onClick={clearGallery}>
                  Limpar todas as fotos
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════
          RESUMO DO PRATO - VISTA MESA (informações CONSOLIDADAS)
          ══════════════════════════════════════════════════════════ */}
      {plateItems.length > 0 && viewMode === 'mesa' && (
        <div className="plate-mesa-view" data-testid="plate-mesa">
          {/* BOTÃO VOLTAR */}
          <button 
            className="back-btn"
            onClick={() => { setViewMode('buffet'); }}
            data-testid="mesa-back-btn"
          >
            ← Voltar ao buffet
          </button>
          
          <h2 className="mesa-title">🍽️ Seu Prato Completo</h2>
          <p className="mesa-subtitle">{plateItems.length} itens selecionados</p>
          
          {/* Lista dos itens escolhidos */}
          <div className="mesa-items-list">
            {plateItems.map((item, i) => (
              <span key={item.id} className="mesa-item-tag">{item.dish_display}</span>
            ))}
          </div>

          {/* ALÉRGENOS CONSOLIDADOS */}
          <div className="mesa-allergens">
            <h4>⚠️ Alérgenos no seu prato</h4>
            {plateConsolidated?.contemGluten && <span className="allergen-tag warning">🌾 Glúten</span>}
            {plateConsolidated?.contemLactose && <span className="allergen-tag warning">🥛 Lactose</span>}
            {plateConsolidated?.contemOvo && <span className="allergen-tag warning">🥚 Ovo</span>}
            {plateConsolidated?.contemCastanhas && <span className="allergen-tag warning">🥜 Castanhas</span>}
            {plateConsolidated?.contemFrutosMar && <span className="allergen-tag warning">🦐 Frutos do Mar</span>}
            {plateConsolidated?.contemSoja && <span className="allergen-tag warning">🫘 Soja</span>}
            {!plateConsolidated?.contemGluten && !plateConsolidated?.contemLactose && 
             !plateConsolidated?.contemOvo && !plateConsolidated?.contemCastanhas && 
             !plateConsolidated?.contemFrutosMar && !plateConsolidated?.contemSoja && (
              <span className="allergen-tag neutral">✅ Nenhum alérgeno comum detectado</span>
            )}
          </div>

          {/* DETALHES POR ITEM */}
          <div className="mesa-section">
            <h4>📋 Detalhes por item</h4>
            <div className="mesa-items-details">
              {plateItems.map((item, i) => (
                <div key={item.id} className="mesa-item-detail">
                  <span className="item-name">{item.dish_display}</span>
                  <span className="item-cal">{item.calorias}</span>
                  <span className="item-cat">{item.category || 'N/A'}</span>
                </div>
              ))}
            </div>
          </div>

          {/* FICHA NUTRICIONAL CONSOLIDADA */}
          <div className="mesa-nutrition">
            <h4>Ficha Nutricional (por 100g)</h4>
            <div className="nutr-grid">
              <div><b>{plateConsolidated?.nutrition?.calorias}</b><small>Calorias</small></div>
              <div><b>{plateConsolidated?.nutrition?.proteinas}</b><small>Proteinas</small></div>
              <div><b>{plateConsolidated?.nutrition?.carboidratos}</b><small>Carbos</small></div>
              <div><b>{plateConsolidated?.nutrition?.gorduras}</b><small>Gorduras</small></div>
            </div>
            {/* Micronutrientes - apenas se tiver dados precisos da ficha */}
            {plateConsolidated?.nutrition?.fibras_g != null && (
              <div className="nutr-grid" style={{marginTop: '8px', opacity: 0.85}}>
                <div><b>{plateConsolidated.nutrition.fibras_g?.toFixed(1)}g</b><small>Fibras</small></div>
                <div><b>{plateConsolidated.nutrition.calcio_mg?.toFixed(0) || '-'}mg</b><small>Calcio</small></div>
                <div><b>{plateConsolidated.nutrition.ferro_mg?.toFixed(1) || '-'}mg</b><small>Ferro</small></div>
                <div><b>{plateConsolidated.nutrition.sodio_mg?.toFixed(0) || '-'}mg</b><small>Sodio</small></div>
              </div>
            )}
            {plateConsolidated?.nutrition?.fonte && (
              <div style={{fontSize: '11px', color: '#94a3b8', marginTop: '6px', textAlign: 'right'}}>
                Fonte: {plateConsolidated.nutrition.fonte}
              </div>
            )}
          </div>

          {/* INGREDIENTES CONSOLIDADOS */}
          {plateConsolidated?.ingredientes?.length > 0 && (
            <div className="mesa-section">
              <h4>🥗 Ingredientes do seu prato</h4>
              <p>{plateConsolidated.ingredientes.join(', ')}</p>
            </div>
          )}

          {/* BENEFÍCIOS CONSOLIDADOS */}
          {plateConsolidated?.beneficios?.length > 0 && (
            <div className="mesa-section good">
              <h4>✅ Benefícios da sua refeição</h4>
              <ul>{plateConsolidated.beneficios.map((b,i) => <li key={i}>{b}</li>)}</ul>
            </div>
          )}

          {/* ══════════════════════════════════════════════════════════
              CONTEÚDO PREMIUM - Radar de Notícias (apenas na vista completa)
              ══════════════════════════════════════════════════════════ */}
          
          {/* AVISO PARA USUÁRIOS FREE */}
          {!premiumUser && (
            <div className="premium-upsell" style={{
              background: 'linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 165, 0, 0.1))',
              border: '1px solid rgba(255, 215, 0, 0.3)',
              borderRadius: '12px',
              padding: '16px',
              textAlign: 'center',
              margin: '12px 0'
            }}>
              <h4 style={{ color: '#ffd700', marginBottom: '8px' }}>⭐ Versão Premium</h4>
              <p style={{ color: '#ccc', fontSize: '13px', margin: '0 0 12px' }}>
                Desbloqueie: Curiosidades científicas, Combinações inteligentes, Alertas personalizados e mais!
              </p>
              <button 
                onClick={() => setShowPremiumModal(true)}
                style={{
                  background: 'linear-gradient(135deg, #ffd700, #ff8c00)',
                  color: '#000',
                  border: 'none',
                  borderRadius: '20px',
                  padding: '8px 24px',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                Conhecer Premium
              </button>
            </div>
          )}
          
          {/* CONTEÚDO EXCLUSIVO PREMIUM */}
          {premiumUser && (
            <>
              {/* VOCÊ SABIA? */}
              {radarInfo?.voce_sabia && (
                <div className="mesa-section voce-sabia" style={{
                  background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(139, 92, 246, 0.15))',
                  borderLeft: '3px solid #3b82f6',
                  borderRadius: '8px',
                  padding: '12px'
                }}>
                  <h4 style={{ color: '#60a5fa', marginBottom: '8px' }}>💡 Você sabia?</h4>
                  <p style={{ color: '#d1d5db', fontSize: '13px', lineHeight: '1.5', margin: 0 }}>
                    {radarInfo.voce_sabia}
                  </p>
                </div>
              )}

              {/* COMBINAÇÕES QUE POTENCIALIZAM */}
              {radarInfo?.combinacoes?.length > 0 && (
                <div className="mesa-section combinacoes" style={{
                  background: 'rgba(34, 197, 94, 0.1)',
                  borderLeft: '3px solid #22c55e',
                  borderRadius: '8px',
                  padding: '12px'
                }}>
                  <h4 style={{ color: '#22c55e', marginBottom: '8px' }}>🔗 Combinações que potencializam</h4>
                  {radarInfo.combinacoes.map((combo, i) => (
                    <p key={i} style={{ color: '#ccc', fontSize: '12px', margin: '4px 0' }}>• {combo}</p>
                  ))}
                </div>
              )}

              {/* FATOS INTERESSANTES / ALERTAS */}
              {radarInfo?.has_alert && radarInfo?.facts?.length > 0 && (
                <div className="mesa-section fatos" style={{
                  background: radarInfo.type === 'alerta' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                  borderLeft: `3px solid ${radarInfo.type === 'alerta' ? '#ef4444' : '#f59e0b'}`,
                  borderRadius: '8px',
                  padding: '12px'
                }}>
                  <h4 style={{ 
                    color: radarInfo.type === 'alerta' ? '#f87171' : '#fbbf24', 
                    marginBottom: '8px' 
                  }}>
                    {radarInfo.type === 'alerta' ? '⚠️ Alerta Nutricional' : '📰 Fatos Interessantes'}
                  </h4>
                  {radarInfo.facts.slice(0, 2).map((fato, i) => (
                    <div key={i} style={{ marginBottom: '8px' }}>
                      {fato.fatos?.slice(0, 1).map((f, j) => (
                        <div key={j}>
                          <p style={{ color: '#fff', fontSize: '13px', fontWeight: 'bold', margin: '0 0 4px' }}>
                            {fato.emoji} {f.titulo}
                          </p>
                          <p style={{ color: '#ccc', fontSize: '12px', margin: '0 0 4px', lineHeight: '1.4' }}>
                            {f.resumo}
                          </p>
                          <small style={{ color: '#888', fontSize: '10px' }}>Fonte: {f.fonte}</small>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {/* RISCOS CONSOLIDADOS */}
          {plateConsolidated?.riscos?.length > 0 && (
            <div className="mesa-section warning">
              <h4>⚠️ Pontos de atenção</h4>
              <ul>{plateConsolidated.riscos.map((r,i) => <li key={i}>{r}</li>)}</ul>
            </div>
          )}

          {/* BOTÃO COMPARTILHAR */}
          <button 
            className="share-btn"
            onClick={() => {
              const itens = plateItems.map(i => `• ${i.dish_display}`).join('\n');
              const beneficios = plateConsolidated?.beneficios?.slice(0, 2).join('\n• ') || '';
              const alergenos = [];
              if (plateConsolidated?.contemGluten) alergenos.push('Glúten');
              if (plateConsolidated?.contemLactose) alergenos.push('Lactose');
              
              const text = `🍽️ Minha refeição consciente:\n\n${itens}\n\n` +
                (beneficios ? `✅ Benefícios:\n• ${beneficios}\n\n` : '') +
                (alergenos.length > 0 ? `⚠️ Contém: ${alergenos.join(', ')}\n\n` : '') +
                `📊 ${plateConsolidated?.nutrition?.calorias} | ${plateConsolidated?.nutrition?.proteinas} proteínas\n\n` +
                `💡 Escolhi com informação! Conheça o SoulNutri - seu agente de nutrição virtual que te ajuda a fazer escolhas conscientes.\n\nsoulnutri.app.br`;
              
              if (navigator.share) {
                navigator.share({ title: 'SoulNutri - Minha Escolha', text });
              } else {
                navigator.clipboard.writeText(text);
                alert('Texto copiado!');
              }
            }}
          >
            📤 Compartilhar minha escolha
          </button>

          {/* BOTÕES DE AÇÃO */}
          <div className="mesa-actions">
            <button 
              className="add-more-btn"
              onClick={() => { setViewMode('buffet'); }}
            >
              + Adicionar mais itens
            </button>
            <button 
              className="clear-plate-btn"
              onClick={() => { clearPlate(); setViewMode('buffet'); }}
            >
              🗑️ Limpar prato
            </button>
          </div>
          
          {/* BOTÃO SAIR */}
          <button 
            className="exit-btn"
            onClick={() => { clearPlate(); clearResult(); setViewMode('buffet'); }}
            style={{
              marginTop: '16px',
              padding: '12px 24px',
              background: '#666',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              cursor: 'pointer',
              width: '100%'
            }}
            data-testid="exit-button"
          >
            ✕ Sair
          </button>
        </div>
      )}

      {/* Mini resumo do prato (quando está no buffet adicionando itens) */}
      {plateItems.length > 0 && viewMode === 'buffet' && !r && (
        <div className="plate-mini-summary" data-testid="plate-mini">
          <div className="mini-header">
            <span>🍽️ Seu Prato ({plateItems.length})</span>
            <span>{plateConsolidated?.nutrition?.calorias}</span>
          </div>
          <div className="mini-items">
            {plateItems.map((item) => (
              <span key={item.id} className="mini-tag">{item.dish_display}</span>
            ))}
          </div>
          <button 
            className="finish-plate-btn"
            onClick={() => setViewMode('mesa')}
          >
            ✓ Prato completo - Ver análise
          </button>
        </div>
      )}

      <input 
        ref={fileInputRef} 
        type="file" 
        accept="image/*"
        hidden 
        onChange={handleFileSelect} 
      />

      {/* RESULTADO */}
      {r?.ok && (
        <div className={`res ${r.confidence}`} data-testid="result-container">
          
          {/* BOTÃO VOLTAR */}
          <button 
            className="back-btn"
            onClick={() => { setResult(null); setPreviewImageUrl(null); setFeedbackSent(false); }}
            data-testid="back-btn"
          >
            ← Voltar
          </button>
          
          {/* Preview da imagem */}
          {previewImageUrl && (
            <div className="preview-image-container">
              <img src={previewImageUrl} alt="Foto do prato" className="preview-image" />
            </div>
          )}
          
          {/* FAMILIA DE PRATOS - quando há ambiguidade */}
          {r.family_candidates && r.family_candidates.length > 0 ? (
            <div className="family-ambiguity-box" data-testid="family-ambiguity-box" style={{
              background: 'linear-gradient(135deg, rgba(251, 191, 36, 0.15), rgba(245, 158, 11, 0.08))',
              border: '2px solid rgba(245, 158, 11, 0.4)',
              borderRadius: '16px',
              padding: '20px',
              margin: '8px 0 16px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>&#x26A0;&#xFE0F;</div>
              {r.family_name ? (
                <h2 className="dish-name" data-testid="dish-name" style={{ fontSize: '18px', margin: '0 0 8px' }}>
                  Familia: {r.family_name}
                </h2>
              ) : (
                <h2 className="dish-name" data-testid="dish-name" style={{ fontSize: '18px', margin: '0 0 8px' }}>
                  Prato nao identificado com certeza
                </h2>
              )}
              <p style={{ fontSize: '13px', color: '#b45309', margin: '0 0 12px', fontWeight: '500' }}>
                Pratos visualmente similares detectados. Pode ser:
              </p>
              <div data-testid="family-candidates-list" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {(r.family_candidates_detail || r.family_candidates.map(c => ({ nome: c }))).map((candidate, i) => (
                  <div key={i} data-testid={`family-candidate-${i}`} style={{
                    background: 'rgba(255,255,255,0.85)',
                    borderRadius: '12px',
                    padding: '12px 16px',
                    textAlign: 'left',
                    border: '1px solid rgba(245, 158, 11, 0.25)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: candidate.ingredientes?.length ? '6px' : '0' }}>
                      <span style={{ fontSize: '15px', fontWeight: '700', color: '#92400e' }}>
                        {candidate.categoria_emoji || ''} {candidate.nome || candidate}
                      </span>
                      {candidate.categoria && (
                        <span style={{ fontSize: '10px', color: '#a16207', background: 'rgba(245,158,11,0.15)', padding: '2px 8px', borderRadius: '8px', fontWeight: '600', textTransform: 'uppercase' }}>
                          {candidate.categoria}
                        </span>
                      )}
                    </div>
                    {candidate.ingredientes && candidate.ingredientes.length > 0 && (
                      <div style={{ fontSize: '12px', color: '#78716c', lineHeight: '1.4' }}>
                        {candidate.ingredientes.slice(0, 5).join(', ')}
                        {candidate.ingredientes.length > 5 ? '...' : ''}
                      </div>
                    )}
                    {candidate.descricao && (
                      <div style={{ fontSize: '11px', color: '#a8a29e', marginTop: '4px', fontStyle: 'italic' }}>
                        {candidate.descricao.length > 80 ? candidate.descricao.substring(0, 80) + '...' : candidate.descricao}
                      </div>
                    )}
                  </div>
                ))}
              </div>
              <p style={{ fontSize: '12px', color: '#78716c', margin: '12px 0 0', fontStyle: 'italic' }}>
                Confirme pela plaquinha ou com o atendente
              </p>
            </div>
          ) : (
            <>
              {/* Nome do Prato — v1.3: exibe diferente conforme confiança */}
              {r.confidence === 'baixa' && !r.identified ? (
                <div data-testid="not-recognized-box" style={{
                  background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05))',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: '16px',
                  padding: '20px',
                  margin: '8px 0 16px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '16px', fontWeight: '600', color: '#dc2626', marginBottom: '6px' }}>
                    Prato nao reconhecido
                  </div>
                  <div style={{ fontSize: '13px', color: '#888' }}>
                    Tente outra foto ou consulte o atendente
                  </div>
                </div>
              ) : r.confidence === 'média' ? (
                <div data-testid="medium-confidence-box">
                  <div style={{
                    background: 'linear-gradient(135deg, rgba(251, 191, 36, 0.12), rgba(245, 158, 11, 0.06))',
                    border: '1px solid rgba(245, 158, 11, 0.35)',
                    borderRadius: '16px',
                    padding: '16px 20px',
                    margin: '8px 0 12px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '13px', color: '#b45309', marginBottom: '6px', fontWeight: '500' }}>
                      Parece ser:
                    </div>
                    <h2 className="dish-name" data-testid="dish-name" style={{ margin: '0 0 8px', fontSize: '20px' }}>
                      {r.dish_display}
                    </h2>
                    <div style={{ fontSize: '12px', color: '#a16207' }}>
                      Verifique se o prato esta correto ({Math.round(r.score * 100)}%)
                    </div>
                  </div>
                  {r.alternatives && r.alternatives.length > 0 && (
                    <div data-testid="alternatives-list" style={{ margin: '8px 0' }}>
                      <div style={{ fontSize: '12px', color: '#888', marginBottom: '6px', textAlign: 'center' }}>
                        Tambem pode ser:
                      </div>
                      {r.alternatives.slice(0, 2).map((alt, i) => (
                        <div key={i} data-testid={`alternative-${i}`} style={{
                          background: 'rgba(245, 158, 11, 0.08)',
                          border: '1px solid rgba(245, 158, 11, 0.2)',
                          borderRadius: '10px',
                          padding: '8px 14px',
                          marginBottom: '4px',
                          fontSize: '14px',
                          fontWeight: '500',
                          color: '#92400e',
                          textAlign: 'center'
                        }}>
                          {alt}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <>
                  <h2 className="dish-name" data-testid="dish-name">{r.dish_display}</h2>
              
                  {/* CALORIAS - Destaque principal */}
                  {(r.nutrition?.calorias || r.calorias_estimadas) && (
                    <div 
                      className="calories-highlight" 
                      data-testid="calories-highlight"
                      style={{
                        background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.1))',
                        borderRadius: '12px',
                        padding: '12px 20px',
                        margin: '8px 0 12px',
                        textAlign: 'center'
                      }}
                    >
                      <span style={{ fontSize: '28px', fontWeight: 'bold', color: '#f59e0b' }}>
                        {r.nutrition?.calorias || r.calorias_estimadas}
                      </span>
                      <div style={{ fontSize: '11px', color: '#888', marginTop: '2px' }}>
                        {r.nutrition?.proteinas && `P: ${r.nutrition.proteinas}`}
                        {r.nutrition?.carboidratos && ` • C: ${r.nutrition.carboidratos}`}
                        {r.nutrition?.gorduras && ` • G: ${r.nutrition.gorduras}`}
                      </div>
                    </div>
                  )}
                </>
              )}
              
              {/* NÍVEL DE CONFIANÇA - Sistema de 3 níveis */}
              {r.confidence_level && r.confidence !== 'baixa' && (
                <div 
                  className={`confidence-level-badge ${r.confidence}`}
                  style={{ 
                    background: confData.bg, 
                    color: confData.color,
                    border: `1px solid ${confData.color}`,
                    padding: '8px 16px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: '600',
                    margin: '8px 0',
                    textAlign: 'center'
                  }}
                  data-testid="confidence-level-badge"
                >
                  {r.confidence_level} ({Math.round(r.score * 100)}%)
                </div>
              )}
              
              {/* CATEGORIA - não mostrar na baixa */}
              {r.confidence !== 'baixa' && (
                <div 
                  className="category-badge" 
                  style={{ background: catStyle.bg, color: catStyle.color, border: catStyle.border || 'none' }}
                  data-testid="category-badge"
                >
                  {r.category_emoji} {r.category?.toUpperCase()}
                </div>
              )}
            </>
          )}

          {/* BOTÃO CORRIGIR - Aparece quando confiança é BAIXA ou MÉDIA */}
          {(r.confidence === 'baixa' || r.confidence === 'média') && (
            <div className="ia-disponivel-box" data-testid="ia-disponivel-box">
              <p className="ia-hint">{r.confidence === 'média' ? 'Nao esta correto?' : 'Prato nao reconhecido'}</p>
              <button 
                className="corrigir-manual-btn"
                onClick={() => setShowFeedback(true)}
                data-testid="corrigir-manual-btn"
              >
                Corrigir manualmente
              </button>
            </div>
          )}

          {/* ══════════════════════════════════════════════════════════
              VISTA BUFFET - Informações para DECISÃO RÁPIDA
              ══════════════════════════════════════════════════════════ */}
          
          {/* ALÉRGENOS */}
          <div className={`allergen-section ${allergenInfo.hasAllergens ? 'has-allergens' : 'no-allergens'}`}>
            {allergenInfo.hasAllergens ? (
              allergenInfo.alerts.map((alert, i) => (
                <div key={i} className={`alert-item ${alert.type}`}>
                  ⚠️ {alert.text}
                </div>
              ))
            ) : (
              <div className="alert-item safe">
                {allergenInfo.text}
              </div>
            )}
          </div>

          {/* DICAS PERSONALIZADAS - Baseadas no perfil do usuário Premium */}
          {premiumUser?.perfil && (() => {
            const tips = generatePersonalizedTip(r, premiumUser.perfil);
            if (tips && tips.length > 0) {
              return (
                <div className="personalized-tips" data-testid="personalized-tips">
                  <h4>💡 Para você</h4>
                  {tips.map((tip, i) => (
                    <div key={i} className={`tip-item ${tip.tipo}`}>
                      <span className="tip-icon">{tip.icone}</span>
                      <span className="tip-text">{tip.texto}</span>
                    </div>
                  ))}
                </div>
              );
            }
            return null;
          })()}

          {/* Ingredientes */}
          {r.ingredientes?.length > 0 && (
            <div className="info-box" data-testid="ingredients-box">
              <h4>🥗 Ingredientes</h4>
              <p>{Array.isArray(r.ingredientes) ? r.ingredientes.join(', ') : r.ingredientes}</p>
            </div>
          )}

          {/* Benefícios - Resumo rápido */}
          {r.beneficios?.length > 0 && (
            <div className="info-box good" data-testid="benefits-box">
              <h4>✅ Benefícios</h4>
              <ul>{r.beneficios.slice(0, 2).map((b,i) => <li key={i}>{b}</li>)}</ul>
            </div>
          )}

          {/* ALERTA PERSONALIZADO - Baseado nas restrições do perfil Premium */}
          {premiumUser && (() => {
            const restricoes = premiumUser.restricoes || [];
            const alertasPersonalizados = [];
            
            // Verificar glúten
            if (restricoes.includes('sem_gluten') && r.contem_gluten) {
              alertasPersonalizados.push({ icone: '🌾', texto: 'Contém GLÚTEN - você registrou restrição!' });
            }
            // Verificar lactose
            if (restricoes.includes('sem_lactose') && r.contem_lactose) {
              alertasPersonalizados.push({ icone: '🥛', texto: 'Contém LACTOSE - você registrou restrição!' });
            }
            // Verificar ovo
            if (restricoes.includes('sem_ovo') && r.contem_ovo) {
              alertasPersonalizados.push({ icone: '🥚', texto: 'Contém OVO - você registrou restrição!' });
            }
            // Verificar frutos do mar
            if (restricoes.includes('sem_frutos_mar') && r.contem_frutos_mar) {
              alertasPersonalizados.push({ icone: '🦐', texto: 'Contém FRUTOS DO MAR - você registrou restrição!' });
            }
            // Verificar oleaginosas/castanhas
            if (restricoes.includes('sem_oleaginosas') && r.contem_castanhas) {
              alertasPersonalizados.push({ icone: '🥜', texto: 'Contém OLEAGINOSAS - você registrou restrição!' });
            }
            // Verificar soja
            if (restricoes.includes('sem_soja') && r.contem_soja) {
              alertasPersonalizados.push({ icone: '🫘', texto: 'Contém SOJA - você registrou restrição!' });
            }
            // Verificar vegano/vegetariano
            if ((restricoes.includes('vegano') || restricoes.includes('vegetariano')) && 
                (r.category === 'proteína animal' || r.ingredientes?.some(i => 
                  i.toLowerCase().includes('carne') || i.toLowerCase().includes('frango') || 
                  i.toLowerCase().includes('peixe') || i.toLowerCase().includes('bacon')))) {
              alertasPersonalizados.push({ icone: '🥬', texto: 'Contém PROTEÍNA ANIMAL - você é vegetariano/vegano!' });
            }
            
            if (alertasPersonalizados.length > 0) {
              return (
                <div className="personal-alert-box" data-testid="personal-alert" style={{
                  background: 'rgba(239, 68, 68, 0.15)',
                  border: '2px solid #ef4444',
                  borderRadius: '12px',
                  padding: '12px',
                  marginTop: '8px'
                }}>
                  <h4 style={{ color: '#ef4444', margin: '0 0 8px', fontSize: '14px' }}>
                    ⚠️ ATENÇÃO - Restrição no seu perfil!
                  </h4>
                  {alertasPersonalizados.map((alerta, i) => (
                    <div key={i} style={{ 
                      color: '#fca5a5', 
                      fontSize: '13px', 
                      marginBottom: '4px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}>
                      <span>{alerta.icone}</span>
                      <span>{alerta.texto}</span>
                    </div>
                  ))}
                </div>
              );
            }
            return null;
          })()}

          {/* BOTÕES DE AÇÃO - BUFFET */}
          <div className="buffet-actions">
            <button 
              className="add-to-plate-btn"
              onClick={() => setShowAddMore(true)}
              data-testid="add-to-plate-btn"
            >
              ✓ Adicionar ao prato
            </button>
          </div>

          {/* BOTÕES DE FEEDBACK */}
          {!feedbackSent && r.source !== 'new_dish' && (
            <div className="feedback-section">
              <p className="feedback-question">Este reconhecimento está correto?</p>
              <div className="feedback-btns">
                <button className="fb-btn correct" onClick={sendFeedbackCorrect}>
                  ✅ Sim
                </button>
                <button className="fb-btn incorrect" onClick={() => setShowFeedback(true)}>
                  ❌ Corrigir
                </button>
              </div>
            </div>
          )}

          <div className="time" data-testid="response-time">⚡ {r.search_time_ms?.toFixed(0)}ms</div>
        </div>
      )}

      {/* RESULTADO MULTI-ITEM */}
      {multiResult?.ok && (() => {
        // Determinar item principal (proteína > vegetariano > vegano)
        const itens = multiResult.itens || [];
        const proteinas = itens.filter(i => i.categoria === 'proteína animal');
        const vegetarianos = itens.filter(i => i.categoria === 'vegetariano');
        const veganos = itens.filter(i => i.categoria === 'vegano');
        
        const principal = proteinas[0] || vegetarianos[0] || veganos[0] || itens[0];
        const acompanhamentos = itens.filter(i => i.nome !== principal?.nome);
        
        const getCategoryEmoji = (cat) => {
          if (cat === 'proteína animal') return '🍖';
          if (cat === 'vegetariano') return '🥚';
          if (cat === 'vegano') return '🥬';
          return '🍽️';
        };
        
        return (
          <div className="res multi-result" data-testid="multi-result-container">
            
            {/* Preview da imagem selecionada da galeria */}
            {previewImageUrl && (
              <div className="preview-image-container">
                <img src={previewImageUrl} alt="Foto do prato" className="preview-image" />
              </div>
            )}
            
            {/* Header com item principal */}
            {principal && (
              <div className="prato-principal">
                <span className="principal-emoji">{getCategoryEmoji(principal.categoria)}</span>
                <div className="principal-info">
                  <h2 className="principal-nome">{principal.nome}</h2>
                  {acompanhamentos.length > 0 && (
                    <span className="acompanhamentos-count">+ {acompanhamentos.length} acompanhamento{acompanhamentos.length > 1 ? 's' : ''}</span>
                  )}
                </div>
              </div>
            )}
            
            {/* Lista de acompanhamentos */}
            {acompanhamentos.length > 0 && (
              <div className="acompanhamentos-lista">
                {acompanhamentos.map((item, idx) => (
                  <span key={idx} className={`acomp-tag ${item.categoria?.replace(' ', '-')}`}>
                    {getCategoryEmoji(item.categoria)} {item.nome}
                  </span>
                ))}
              </div>
            )}

            {/* Resumo nutricional */}
            {multiResult.resumo_nutricional && (
              <div className="multi-summary" data-testid="multi-summary">
                <div className="summary-grid">
                  <div className="summary-item">
                    <span className="summary-value">{multiResult.resumo_nutricional.calorias_totais || '~' + (itens.length * 150) + ' kcal'}</span>
                    <span className="summary-label">Calorias</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-value">{multiResult.resumo_nutricional.proteinas_totais || '~' + (proteinas.length * 20) + 'g'}</span>
                    <span className="summary-label">Proteínas</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-value">{multiResult.resumo_nutricional.carboidratos_totais || '~' + (veganos.length * 15) + 'g'}</span>
                    <span className="summary-label">Carbos</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-value">{multiResult.resumo_nutricional.gorduras_totais || '~10g'}</span>
                    <span className="summary-label">Gorduras</span>
                  </div>
                </div>
              </div>
            )}

            {/* Equilíbrio */}
            {multiResult.equilibrio && (
              <div className={`equilibrio-badge ${multiResult.equilibrio}`}>
                {multiResult.equilibrio === 'balanceado' && '⚖️ Refeição Balanceada'}
                {multiResult.equilibrio === 'rico_em_carboidratos' && '🍞 Rico em Carboidratos'}
                {multiResult.equilibrio === 'rico_em_proteinas' && '💪 Rico em Proteínas'}
                {multiResult.equilibrio === 'rico_em_gorduras' && '🧈 Rico em Gorduras'}
              </div>
            )}

            {/* Alertas */}
            {multiResult.alertas_combinados?.length > 0 && (
              <div className="multi-alerts">
                {multiResult.alertas_combinados.map((alert, i) => (
                  <span key={i} className="alert-tag">⚠️ {alert}</span>
                ))}
              </div>
            )}

            {/* Dica */}
            {multiResult.dica_nutricional && (
              <div className="dica-box">
                <p>💡 {multiResult.dica_nutricional}</p>
              </div>
            )}

            <div className="time" data-testid="multi-response-time">
              ⚡ {multiResult.search_time_ms?.toFixed(0)}ms
            </div>

            {/* Compartilhar */}
            <button 
              className="share-btn"
              onClick={() => {
                const acompText = acompanhamentos.map(i => i.nome).join(', ');
                const text = `🍽️ Meu prato no Cibi Sana:\n\n${getCategoryEmoji(principal?.categoria)} ${principal?.nome}${acompText ? `\n+ ${acompText}` : ''}\n\n📊 ${multiResult.resumo_nutricional?.calorias_totais || 'Calculando calorias...'}\n\nAnalisado pelo SoulNutri!`;
                if (navigator.share) {
                  navigator.share({ title: 'SoulNutri', text });
                } else {
                  navigator.clipboard.writeText(text);
                  alert('Texto copiado! Cole para compartilhar.');
                }
              }}
              data-testid="multi-share-button"
            >
              📤 Compartilhar meu prato
            </button>

            {/* BOTÕES DE FEEDBACK - MULTI - Removido do fluxo de montagem */}
            {/* A correção fica disponível via botão de editar se necessário */}
            {feedbackSent && (
              <div className="feedback-thanks">
                ✅ Prato registrado!
              </div>
            )}
          </div>
        );
      })()}

      {/* MODAL "ADICIONAR MAIS ITENS?" - Fluxo Único Inteligente */}
      {showAddMore && result?.ok && result?.identified && (
        <div className="modal-overlay add-more-overlay" data-testid="add-more-modal">
          <div className="modal-content add-more-modal" onClick={e => e.stopPropagation()}>
            {/* BOTÃO VOLTAR */}
            <button 
              className="modal-back-btn"
              onClick={() => setShowAddMore(false)}
            >
              ← Voltar
            </button>
            
            <div className="add-more-success">
              <span className="add-more-emoji">✅</span>
              <h3>{result.dish_display}</h3>
              <p className="add-more-confidence">
                {result.confidence === 'alta' ? '🎯 Alta confiança' : 
                 result.confidence === 'media' ? '👍 Boa confiança' : '🤔 Verificar'}
              </p>
            </div>
            
            {/* RADAR DE NOTÍCIAS - Fatos sobre o alimento */}
            {radarInfo?.has_alert && (
              <div 
                className="radar-alert"
                onClick={() => setShowRadarDetails(true)}
                style={{
                  background: radarInfo.type === 'alerta' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(34, 197, 94, 0.15)',
                  border: `1px solid ${radarInfo.type === 'alerta' ? 'rgba(239, 68, 68, 0.4)' : 'rgba(34, 197, 94, 0.4)'}`,
                  borderRadius: '12px',
                  padding: '12px',
                  marginBottom: '12px',
                  cursor: 'pointer'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '20px' }}>{radarInfo.emoji || '📰'}</span>
                  <span style={{ 
                    color: '#fff', 
                    fontSize: '11px', 
                    background: radarInfo.type === 'alerta' ? '#ef4444' : '#22c55e',
                    padding: '2px 8px',
                    borderRadius: '10px',
                    fontWeight: 'bold'
                  }}>
                    RADAR
                  </span>
                </div>
                <p style={{ color: '#fff', fontSize: '13px', margin: '8px 0 0', lineHeight: '1.4' }}>
                  {radarInfo.message}
                </p>
                <p style={{ color: '#888', fontSize: '11px', margin: '6px 0 0' }}>
                  Toque para ver mais informações →
                </p>
              </div>
            )}
            
            <div className="add-more-question">
              <p>Seu prato está completo?</p>
              {plateItems.length > 0 && (
                <small className="plate-count">
                  ({plateItems.length} {plateItems.length === 1 ? 'item' : 'itens'} já adicionado{plateItems.length > 1 ? 's' : ''})
                </small>
              )}
            </div>
            
            <div className="add-more-actions">
              <button 
                className="add-more-finish-btn"
                onClick={finishPlate}
                data-testid="finish-plate-btn"
              >
                ✓ Sim, está completo
              </button>
              <button 
                className="add-more-continue-btn"
                onClick={addItemToPlate}
                data-testid="add-more-btn"
              >
                + Adicionar mais itens
              </button>
            </div>
            
            <p className="add-more-tip">
              💡 Dica: Para buffet, fotografe cada item separadamente
            </p>
          </div>
        </div>
      )}

      {/* MODAL RADAR DE NOTÍCIAS - Detalhes */}
      {showRadarDetails && radarInfo && (
        <div className="modal-overlay" onClick={() => setShowRadarDetails(false)}>
          <div className="modal-content radar-details" onClick={e => e.stopPropagation()} style={{
            maxWidth: '400px',
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            borderRadius: '16px',
            padding: '20px'
          }}>
            <button 
              className="modal-back-btn"
              onClick={() => setShowRadarDetails(false)}
              style={{ position: 'absolute', top: '10px', left: '10px' }}
            >
              ← Voltar
            </button>
            
            <div style={{ textAlign: 'center', marginBottom: '20px', marginTop: '20px' }}>
              <span style={{ fontSize: '32px' }}>{radarInfo.emoji || '📰'}</span>
              <h3 style={{ color: '#fff', margin: '10px 0 0' }}>Radar Nutricional</h3>
              <p style={{ color: '#888', fontSize: '12px' }}>Informações sobre este alimento</p>
            </div>
            
            {radarInfo.titulo && (
              <div style={{
                background: 'rgba(34, 197, 94, 0.1)',
                padding: '12px',
                borderRadius: '10px',
                marginBottom: '12px'
              }}>
                <h4 style={{ color: '#22c55e', margin: '0 0 6px', fontSize: '14px' }}>
                  {radarInfo.titulo}
                </h4>
                <p style={{ color: '#ccc', fontSize: '13px', margin: 0, lineHeight: '1.5' }}>
                  {radarInfo.message}
                </p>
                {radarInfo.fonte && (
                  <p style={{ color: '#888', fontSize: '11px', margin: '8px 0 0' }}>
                    📚 Fonte: {radarInfo.fonte}
                  </p>
                )}
              </div>
            )}
            
            {/* Você Sabia? */}
            {radarInfo.voce_sabia && (
              <div style={{
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2))',
                padding: '12px',
                borderRadius: '10px',
                marginTop: '12px',
                borderLeft: '3px solid #3b82f6'
              }}>
                <h4 style={{ color: '#3b82f6', margin: '0 0 6px', fontSize: '12px' }}>
                  💡 Você sabia?
                </h4>
                <p style={{ color: '#e0e0e0', fontSize: '12px', margin: 0, lineHeight: '1.5' }}>
                  {radarInfo.voce_sabia}
                </p>
              </div>
            )}
            
            {/* Combinações Benéficas */}
            {radarInfo.combinacoes?.length > 0 && (
              <div style={{
                background: 'rgba(34, 197, 94, 0.1)',
                padding: '12px',
                borderRadius: '10px',
                marginTop: '12px'
              }}>
                <h4 style={{ color: '#22c55e', margin: '0 0 8px', fontSize: '12px' }}>
                  🔗 Combinações que potencializam nutrientes:
                </h4>
                {radarInfo.combinacoes.map((combo, i) => (
                  <p key={i} style={{ color: '#ccc', fontSize: '11px', margin: '4px 0', paddingLeft: '8px' }}>
                    • {combo}
                  </p>
                ))}
              </div>
            )}
            
            {radarInfo.facts?.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <h4 style={{ color: '#fff', fontSize: '13px', marginBottom: '10px' }}>
                  📌 Mais informações
                </h4>
                {radarInfo.facts.map((grupo, i) => (
                  <div key={i} style={{ marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                      <span>{grupo.emoji}</span>
                      <span style={{ color: '#fff', fontWeight: 'bold', fontSize: '13px' }}>
                        {grupo.ingrediente}
                      </span>
                    </div>
                    {grupo.voce_sabia && !radarInfo.voce_sabia && (
                      <p style={{ 
                        color: '#3b82f6', 
                        fontSize: '11px', 
                        margin: '0 0 6px',
                        paddingLeft: '22px'
                      }}>
                        💡 {grupo.voce_sabia}
                      </p>
                    )}
                    {grupo.dica_rapida && (
                      <p style={{ 
                        color: '#22c55e', 
                        fontSize: '12px', 
                        margin: '0 0 8px',
                        paddingLeft: '22px'
                      }}>
                        ✓ {grupo.dica_rapida}
                      </p>
                    )}
                    {grupo.fatos?.map((fato, j) => (
                      <div key={j} style={{
                        background: fato.tipo === 'alerta' ? 'rgba(239, 68, 68, 0.1)' : 
                                   fato.tipo === 'beneficio' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(255,255,255,0.05)',
                        padding: '10px',
                        borderRadius: '8px',
                        marginBottom: '6px',
                        marginLeft: '22px',
                        borderLeft: fato.tipo === 'alerta' ? '3px solid #ef4444' : 
                                   fato.tipo === 'beneficio' ? '3px solid #22c55e' : '3px solid #666'
                      }}>
                        <p style={{ 
                          color: fato.tipo === 'alerta' ? '#f87171' : 
                                fato.tipo === 'beneficio' ? '#4ade80' : '#fff', 
                          fontSize: '12px', 
                          fontWeight: 'bold', 
                          margin: '0 0 4px' 
                        }}>
                          {fato.tipo === 'alerta' ? '⚠️ ' : fato.tipo === 'beneficio' ? '✅ ' : ''}{fato.titulo}
                        </p>
                        <p style={{ color: '#ccc', fontSize: '11px', margin: 0, lineHeight: '1.4' }}>
                          {fato.resumo}
                        </p>
                        <p style={{ color: '#666', fontSize: '10px', margin: '4px 0 0' }}>
                          📚 {fato.fonte} • {fato.data}
                        </p>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            )}
            
            <button 
              onClick={() => setShowRadarDetails(false)}
              style={{
                width: '100%',
                padding: '12px',
                background: '#22c55e',
                color: '#fff',
                border: 'none',
                borderRadius: '10px',
                fontWeight: 'bold',
                cursor: 'pointer',
                marginTop: '16px'
              }}
            >
              Entendi
            </button>
          </div>
        </div>
      )}

      {/* MODAL DE CORREÇÃO MULTI */}
      {showMultiCorrection && (
        <div className="modal-overlay" onClick={() => setShowMultiCorrection(false)}>
          <div className="modal-content multi-correction" onClick={e => e.stopPropagation()}>
            {/* BOTÃO VOLTAR */}
            <button 
              className="modal-back-btn"
              onClick={() => setShowMultiCorrection(false)}
            >
              ← Voltar
            </button>
            
            <h3>✏️ Corrigir Identificação</h3>
            
            <div className="correction-form">
              <div className="form-group">
                <label>🍽️ Item Principal (ou primeiro item):</label>
                <input 
                  type="text"
                  placeholder="Ex: Maminha ao Molho, Peixe Grelhado..."
                  value={multiCorrections.principal}
                  onChange={e => setMultiCorrections({...multiCorrections, principal: e.target.value})}
                  autoFocus
                />
              </div>
              
              <div className="form-group">
                <label>🥗 Outros itens do prato (separados por vírgula):</label>
                <textarea 
                  placeholder="Ex: Arroz, Salada, Feijão, Camarão..."
                  value={multiCorrections.acompanhamentos}
                  onChange={e => setMultiCorrections({...multiCorrections, acompanhamentos: e.target.value})}
                  rows={4}
                />
              </div>
              
              <small className="help-text">
                💡 Edite apenas o que está errado. O cliente pode misturar proteínas e veganos no mesmo prato.
              </small>
            </div>
            
            <div className="modal-actions-fixed">
              <button 
                className="save-correction-btn" 
                onClick={saveMultiCorrection}
                disabled={creatingDish || !multiCorrections.principal.trim()}
              >
                {creatingDish ? '⏳ Salvando...' : '💾 Salvar Correção'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL DE CORREÇÃO */}
      {showFeedback && (
        <div className="modal-overlay" onClick={() => setShowFeedback(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            {/* BOTÃO VOLTAR */}
            <button 
              className="modal-back-btn"
              onClick={() => setShowFeedback(false)}
            >
              ← Voltar
            </button>
            
            <h3>Corrigir identificação</h3>
            
            {/* Campo para NOVO PRATO */}
            <div className="new-dish-section">
              <p className="section-label">📝 Cadastrar prato novo:</p>
              <div className="new-dish-input">
                <input 
                  type="text"
                  placeholder="Digite o nome do prato..."
                  value={newDishName}
                  onChange={e => setNewDishName(e.target.value)}
                />
                <button 
                  onClick={createNewDish} 
                  disabled={!newDishName.trim() || creatingDish}
                  className="create-btn"
                >
                  {creatingDish ? '⏳' : '➕'} {creatingDish ? 'Criando...' : 'Criar'}
                </button>
              </div>
              <small>A IA vai gerar automaticamente: categoria, ingredientes, benefícios, riscos e alérgenos</small>
            </div>

            <div className="divider">ou selecione um prato existente:</div>

            {/* Busca */}
            <input 
              type="text"
              className="search-input"
              placeholder="🔍 Buscar prato..."
              value={searchFilter}
              onChange={e => setSearchFilter(e.target.value)}
            />

            {/* Lista de pratos */}
            <div className="dishes-list">
              {filteredDishes.map(d => (
                <button 
                  key={d.slug} 
                  className="dish-option"
                  onClick={() => sendFeedbackIncorrect(d.slug)}
                >
                  {d.category_emoji} {d.name}
                </button>
              ))}
            </div>
            
            {/* Ações do modal - FIXAS NO FINAL */}
            <div className="modal-actions-fixed">
              <button className="discard-btn" onClick={discardPhoto}>
                🗑️ Descartar foto (inutilizável)
              </button>
            </div>
          </div>
        </div>
      )}

      {r && !r.ok && (
        <div className="err" data-testid="error-message">❌ {r.message}</div>
      )}

      {error && (
        <div className="err" data-testid="network-error">❌ Erro de conexão: {error}</div>
      )}

      {/* PREMIUM - Mini contador flutuante */}
      {premiumUser && dailySummary && !showPremium && (
        <div className="mini-counter" onClick={() => setShowPremium('dashboard')} data-testid="mini-counter">
          <div className="mini-value">{dailySummary.consumido?.toFixed(0) || 0}</div>
          <div className="mini-label">de {dailySummary.meta?.toFixed(0)} kcal</div>
          <div className="mini-progress">
            <div 
              className="mini-fill" 
              style={{ 
                width: `${Math.min(dailySummary.percentual || 0, 100)}%`,
                background: dailySummary.percentual >= 100 ? '#ef4444' : dailySummary.percentual >= 75 ? '#f59e0b' : '#22c55e'
              }} 
            />
          </div>
        </div>
      )}

      {/* PREMIUM - Botão flutuante */}
      <button 
        className={`premium-btn ${premiumUser ? 'logged-in' : ''}`}
        onClick={() => setShowPremium(premiumUser ? 'dashboard' : 'login')}
        data-testid="premium-button"
      >
        {premiumUser ? 'Dieta' : 'Premium'}
      </button>

      {/* PREMIUM - Modal */}
      {showPremium && (
        <div className="modal-overlay" onClick={() => setShowPremium(null)}>
          <div className="modal-content premium-modal" onClick={e => e.stopPropagation()}>
            {showPremium === 'login' && (
              <PremiumLogin 
                onSuccess={(data) => {
                  const user = { ...data.user, pin: localStorage.getItem('soulnutri_pin') };
                  setPremiumUser(user);
                  loadDailySummary();
                  // Se não tem dados físicos preenchidos, mostrar formulário
                  // Dados podem estar em user.peso ou user.perfil.peso
                  const temDadosFisicos = user.peso || (user.perfil && user.perfil.peso);
                  if (!temDadosFisicos) {
                    setShowPremium('profile');
                  } else {
                    setShowPremium('dashboard');
                  }
                }}
                onRegister={() => setShowPremium('register')}
                onCancel={() => setShowPremium(null)}
              />
            )}
            
            {showPremium === 'register' && (
              <PremiumRegister 
                onSuccess={(data) => {
                  setPremiumUser({ nome: data.nome, pin: data.pin, meta_calorica: data.meta_calorica });
                  setDailySummary({ nome: data.nome, meta: data.meta_calorica.meta_sugerida, consumido: 0, restante: data.meta_calorica.meta_sugerida, percentual: 0, pratos: [] });
                  // Ir direto para o dashboard - dados já foram coletados no registro
                  setShowPremium('dashboard');
                }}
                onCancel={() => setShowPremium('login')}
              />
            )}
            
            {/* Formulário de Perfil Premium */}
            {showPremium === 'profile' && premiumUser && (
              <PremiumProfileForm 
                user={premiumUser}
                onSave={(perfil) => {
                  setPremiumUser(prev => ({ ...prev, perfil }));
                  setShowPremium('dashboard');
                }}
                onSkip={() => setShowPremium('dashboard')}
              />
            )}
            
            {showPremium === 'dashboard' && premiumUser && (
              <DailyCounter 
                user={premiumUser}
                onLogout={handlePremiumLogout}
                onClose={() => setShowPremium(null)}
                onEditProfile={() => setShowPremium('edit-profile')}
              />
            )}
            
            {showPremium === 'edit-profile' && premiumUser && (
              <PremiumEditProfile 
                onSuccess={(data) => {
                  // Atualizar dados do usuário com nova meta calórica
                  setPremiumUser(prev => ({ ...prev, meta_calorica: data.meta_calorica }));
                  loadDailySummary();
                  setShowPremium('dashboard');
                }}
                onCancel={() => setShowPremium('dashboard')}
              />
            )}
          </div>
        </div>
      )}

      {/* Modal Check-in de Refeição (Premium) */}
      {showCheckin && premiumUser && (
        <div className="modal-overlay" onClick={() => setShowCheckin(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <CheckinRefeicao 
              pin={premiumUser.pin}
              nome={premiumUser.nome}
              onClose={() => setShowCheckin(false)}
              onSuccess={(data) => {
                // Atualizar o resumo diário após check-in
                loadDailySummary();
              }}
            />
          </div>
        </div>
      )}

      {/* Welcome Popup - Seleção de idioma para novos usuários */}
      {showWelcome && (
        <WelcomePopup onClose={handleWelcomeClose} />
      )}

      {/* Tutorial do Scanner Contínuo */}
      {showScannerTutorial && (
        <ScannerTutorial onClose={() => setShowScannerTutorial(false)} />
      )}

      {/* Rodapé */}
      <footer className="footer">
        <small>Powered by Emergent</small>
      </footer>
    </div>
  );
}

// Componente principal com Provider de internacionalização
function AppWithI18n() {
  return (
    <I18nProvider>
      <CameraErrorBoundary>
        <App />
      </CameraErrorBoundary>
    </I18nProvider>
  );
}

export default AppWithI18n;
