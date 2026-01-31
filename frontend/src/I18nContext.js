import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Contexto de internacionalização
const I18nContext = createContext(null);

// Idiomas suportados (fallback se API falhar)
const DEFAULT_LANGUAGES = [
  { code: 'pt', name: 'Português', flag: '🇧🇷', native: 'Português' },
  { code: 'en', name: 'English', flag: '🇺🇸', native: 'English' },
  { code: 'es', name: 'Español', flag: '🇪🇸', native: 'Español' },
  { code: 'fr', name: 'Français', flag: '🇫🇷', native: 'Français' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪', native: 'Deutsch' },
  { code: 'zh', name: '中文', flag: '🇨🇳', native: '中文' },
];

// Traduções padrão (fallback)
const DEFAULT_TRANSLATIONS = {
  identify_dish: "Identificar Prato",
  gallery: "Galeria",
  new_scan: "Nova",
  loading: "Identificando...",
  position_dish: "Posicione o prato aqui",
  tap_to_photo: "Toque para fotografar",
  high_confidence: "ALTA CONFIANÇA",
  medium_confidence: "MÉDIA CONFIANÇA",
  low_confidence: "BAIXA CONFIANÇA",
  ingredients: "Ingredientes",
  benefits: "Benefícios para a Saúde",
  risks: "Riscos e Alertas",
  nutrition_info: "Informação Nutricional (100g)",
  calories: "Calorias",
  proteins: "Proteínas",
  carbs: "Carboidratos",
  fats: "Gorduras",
  no_allergens: "Não contém alérgenos conhecidos",
  share: "Compartilhar",
  feedback_question: "Este reconhecimento está correto?",
  yes_correct: "Sim, correto",
  no_correct: "Não, corrigir",
  thanks_feedback: "Obrigado pelo feedback!",
  premium: "Premium",
  diet: "Dieta",
  your_plate: "Seu Prato",
  items: "itens",
  add_more: "Adicionar mais",
  plate_complete: "Prato completo",
  scientific_info: "Você Sabia?",
  curiosity: "Curiosidade Científica",
  truth_or_myth: "Verdade ou Mito?",
  truth: "VERDADE",
  myth: "MITO",
  partial: "PARCIALMENTE",
  camera_error: "Câmera não disponível",
  try_again: "Tentar novamente",
  vegan: "vegano",
  vegetarian: "vegetariano",
  animal_protein: "proteína animal",
  select_language: "Selecionar idioma",
};

export function I18nProvider({ children }) {
  const [currentLang, setCurrentLang] = useState(() => {
    // Tentar recuperar do localStorage
    const saved = localStorage.getItem('soulnutri_lang');
    if (saved) return saved;
    
    // Detectar idioma do navegador
    const browserLang = navigator.language?.split('-')[0] || 'pt';
    const supported = ['pt', 'en', 'es', 'fr', 'de', 'zh'];
    return supported.includes(browserLang) ? browserLang : 'pt';
  });
  
  const [translations, setTranslations] = useState(DEFAULT_TRANSLATIONS);
  const [languages, setLanguages] = useState(DEFAULT_LANGUAGES);
  const [loading, setLoading] = useState(false);

  // Carregar idiomas disponíveis
  useEffect(() => {
    const loadLanguages = async () => {
      try {
        const res = await fetch(`${API}/i18n/languages`);
        const data = await res.json();
        if (data.ok && data.languages) {
          setLanguages(data.languages);
        }
      } catch (e) {
        console.warn('Usando idiomas padrão:', e);
      }
    };
    loadLanguages();
  }, []);

  // Carregar traduções quando idioma mudar
  useEffect(() => {
    const loadTranslations = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API}/i18n/ui/${currentLang}`);
        const data = await res.json();
        if (data.ok && data.translations) {
          setTranslations(data.translations);
        }
      } catch (e) {
        console.warn('Usando traduções padrão:', e);
      } finally {
        setLoading(false);
      }
    };
    
    loadTranslations();
    localStorage.setItem('soulnutri_lang', currentLang);
  }, [currentLang]);

  // Função para traduzir uma chave
  const t = useCallback((key, fallback = '') => {
    return translations[key] || fallback || key;
  }, [translations]);

  // Função para mudar idioma
  const changeLanguage = useCallback((lang) => {
    if (languages.some(l => l.code === lang)) {
      setCurrentLang(lang);
    }
  }, [languages]);

  // Obter informações do idioma atual
  const getCurrentLanguage = useCallback(() => {
    return languages.find(l => l.code === currentLang) || languages[0];
  }, [languages, currentLang]);

  const value = {
    currentLang,
    translations,
    languages,
    loading,
    t,
    changeLanguage,
    getCurrentLanguage,
  };

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
}

// Hook para usar internacionalização
export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
}

// Componente seletor de idioma
export function LanguageSelector({ className = '' }) {
  const { currentLang, languages, changeLanguage, loading } = useI18n();
  const [isOpen, setIsOpen] = useState(false);

  const currentLanguage = languages.find(l => l.code === currentLang) || languages[0];

  return (
    <div className={`language-selector ${className}`} data-testid="language-selector">
      <button
        className="lang-current"
        onClick={() => setIsOpen(!isOpen)}
        disabled={loading}
        data-testid="lang-toggle"
      >
        <span className="lang-flag">{currentLanguage?.flag}</span>
        <span className="lang-code">{currentLang.toUpperCase()}</span>
        <span className="lang-arrow">{isOpen ? '▲' : '▼'}</span>
      </button>
      
      {isOpen && (
        <div className="lang-dropdown" data-testid="lang-dropdown">
          {languages.map(lang => (
            <button
              key={lang.code}
              className={`lang-option ${lang.code === currentLang ? 'active' : ''}`}
              onClick={() => {
                changeLanguage(lang.code);
                setIsOpen(false);
              }}
              data-testid={`lang-${lang.code}`}
            >
              <span className="lang-flag">{lang.flag}</span>
              <span className="lang-native">{lang.native}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default I18nContext;
