import React, { useState, useRef, useEffect, useCallback, useMemo } from "react";
import "./App.css";
import "./Premium.css";
import { PremiumRegister, PremiumLogin, DailyCounter } from "./Premium";
import CheckinRefeicao from "./CheckinRefeicao";
import "./CheckinRefeicao.css";
import { I18nProvider, useI18n, LanguageSelector } from "./I18nContext";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Timeout para requisições (evita travamentos)
const REQUEST_TIMEOUT = 15000; // 15 segundos

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
  const [showPremium, setShowPremium] = useState(null); // null, 'login', 'register', 'dashboard'
  const [premiumUser, setPremiumUser] = useState(null);
  const [dailySummary, setDailySummary] = useState(null);
  const [showCheckin, setShowCheckin] = useState(false); // Check-in de refeição
  // Menu e PWA
  const [showMenu, setShowMenu] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstalled, setIsInstalled] = useState(false);
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

  useEffect(() => { 
    mountedRef.current = true;
    checkStatus(); 
    startCamera();
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
    const handleVisibility = () => {
      if (document.hidden) {
        stopCamera();
      } else {
        startCamera();
      }
    };
    document.addEventListener('visibilitychange', handleVisibility);
    
    return () => {
      mountedRef.current = false;
      stopCamera();
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
    if (!premiumUser || !mountedRef.current) return;
    
    try {
      const pin = localStorage.getItem('soulnutri_pin');
      if (!pin) return;
      
      const fd = new FormData();
      fd.append('pin', pin);
      fd.append('prato_nome', prato.dish_display || prato.nome || 'Prato');
      fd.append('calorias', parseFloat(prato.nutrition?.calorias?.replace(/[^\d]/g, '') || 200));
      fd.append('proteinas', parseFloat(prato.nutrition?.proteinas?.replace(/[^\d]/g, '') || 10));
      fd.append('carboidratos', parseFloat(prato.nutrition?.carboidratos?.replace(/[^\d]/g, '') || 25));
      fd.append('gorduras', parseFloat(prato.nutrition?.gorduras?.replace(/[^\d]/g, '') || 8));
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      const res = await fetch(`${API}/premium/log-meal`, { 
        method: 'POST', 
        body: fd,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if (!mountedRef.current) return;
      
      const data = await res.json();
      if (data.ok) {
        setDailySummary(prev => ({
          ...prev,
          consumido: data.consumido,
          restante: data.restante,
          percentual: data.percentual,
          pratos: [...(prev?.pratos || []), { nome: prato.dish_display, calorias: fd.get('calorias'), hora: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) }]
        }));
      }
    } catch (e) {
      console.error('Erro ao registrar refeição:', e);
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
      // Resolução reduzida para economizar memória em celulares
      const s = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment', 
          width: { ideal: 640, max: 1280 }, 
          height: { ideal: 480, max: 720 } 
        } 
      });
      setStream(s);
      if (videoRef.current) videoRef.current.srcObject = s;
    } catch (err) { 
      console.error("Câmera não disponível:", err);
      setCameraError(err.name === 'NotAllowedError' ? 'permission_denied' : 'camera_error');
    }
  };

  const stopCamera = () => { 
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
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
        // NÃO mostrar modal automaticamente - deixar usuário ver as informações primeiro
      }
    } catch (e) { 
      clearTimeout(timeoutId);
      if (!mountedRef.current) return;
      
      if (e.name === 'AbortError') {
        setError('Tempo limite excedido. Tente novamente.');
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
  const addItemToPlate = () => {
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
          lactose: result.contem_lactose
        },
        score: result.score
      };
      console.log('[DEBUG] Adicionando último item:', newItem.dish_display);
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
    
    // Verificar alérgenos presentes em qualquer item
    const contemGluten = plateItems.some(item => item.alergenos?.gluten);
    const contemLactose = plateItems.some(item => item.alergenos?.lactose);
    const contemOvo = plateItems.some(item => item.alergenos?.ovo);
    const contemCastanhas = plateItems.some(item => item.alergenos?.castanhas);
    const contemFrutosMar = plateItems.some(item => item.alergenos?.frutosMar);
    
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
      riscos: allRiscos,
      contemGluten,
      contemLactose,
      contemOvo,
      contemCastanhas,
      contemFrutosMar,
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

  // Enviar feedback - INCORRETO (com correção)
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

  // CRIAR PRATO NOVO com IA
  const createNewDish = async () => {
    if (!lastImageBlob || !newDishName.trim()) return;
    
    setCreatingDish(true);
    
    const fd = new FormData();
    fd.append("file", lastImageBlob, "photo.jpg");
    fd.append("dish_name", newDishName.trim());
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s para criação
      const res = await fetch(`${API}/ai/create-dish`, { 
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
        setNewDishName("");
        // Atualizar lista de pratos
        loadDishes();
        // Mostrar resultado do novo prato
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
            {!plateConsolidated?.contemGluten && !plateConsolidated?.contemLactose && 
             !plateConsolidated?.contemOvo && !plateConsolidated?.contemCastanhas && 
             !plateConsolidated?.contemFrutosMar && (
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
            <h4>📊 Ficha Nutricional (base 100g)</h4>
            <div className="nutr-grid">
              <div><b>{plateConsolidated?.nutrition?.calorias}</b><small>Calorias</small></div>
              <div><b>{plateConsolidated?.nutrition?.proteinas}</b><small>Proteínas</small></div>
              <div><b>{plateConsolidated?.nutrition?.carboidratos}</b><small>Carbos</small></div>
              <div><b>{plateConsolidated?.nutrition?.gorduras}</b><small>Gorduras</small></div>
            </div>
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
          
          {/* Nome do Prato */}
          <h2 className="dish-name" data-testid="dish-name">{r.dish_display}</h2>
          
          {/* CATEGORIA */}
          <div 
            className="category-badge" 
            style={{ background: catStyle.bg, color: catStyle.color, border: catStyle.border || 'none' }}
            data-testid="category-badge"
          >
            {r.category_emoji} {r.category?.toUpperCase()}
          </div>

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

          {/* Ingredientes */}
          {r.ingredientes?.length > 0 && (
            <div className="info-box" data-testid="ingredients-box">
              <h4>🥗 Ingredientes</h4>
              <p>{Array.isArray(r.ingredientes) ? r.ingredientes.join(', ') : r.ingredientes}</p>
            </div>
          )}

          {/* Benefícios */}
          {r.beneficios?.length > 0 && (
            <div className="info-box good" data-testid="benefits-box">
              <h4>✅ Benefícios</h4>
              <ul>{r.beneficios.slice(0, 3).map((b,i) => <li key={i}>{b}</li>)}</ul>
            </div>
          )}

          {/* Combinações sugeridas */}
          {r.premium?.combinacoes_sugeridas?.length > 0 && (
            <div className="info-box combo" data-testid="combo-box">
              <h4>💡 Combine com</h4>
              <div className="combo-list">
                {r.premium.combinacoes_sugeridas.slice(0, 2).map((c, i) => (
                  <div key={i} className="combo-item">
                    <span>{c.emoji} <strong>{c.titulo}</strong></span>
                  </div>
                ))}
              </div>
            </div>
          )}

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
                  setPremiumUser(data.user);
                  loadDailySummary();
                  setShowPremium('dashboard');
                }}
                onRegister={() => setShowPremium('register')}
                onCancel={() => setShowPremium(null)}
              />
            )}
            
            {showPremium === 'register' && (
              <PremiumRegister 
                onSuccess={(data) => {
                  setPremiumUser({ nome: data.nome, meta_calorica: data.meta_calorica });
                  setDailySummary({ nome: data.nome, meta: data.meta_calorica.meta_sugerida, consumido: 0, restante: data.meta_calorica.meta_sugerida, percentual: 0, pratos: [] });
                  setShowPremium('dashboard');
                }}
                onCancel={() => setShowPremium('login')}
              />
            )}
            
            {showPremium === 'dashboard' && premiumUser && (
              <DailyCounter 
                user={premiumUser}
                onLogout={handlePremiumLogout}
                onClose={() => setShowPremium(null)}
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
      <App />
    </I18nProvider>
  );
}

export default AppWithI18n;
