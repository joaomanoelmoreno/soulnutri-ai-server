import React, { useState, useCallback } from 'react';
import { Camera, Plus, Minus, Check, X, ChevronDown, ChevronUp } from 'lucide-react';
import './CheckinRefeicao.css';

const API = process.env.REACT_APP_BACKEND_URL;

// Porções disponíveis
const PORCOES = [
  { id: 'pequena', label: 'Pequena', gramas: 50, emoji: '🥄' },
  { id: 'media', label: 'Média', gramas: 100, emoji: '🍽️' },
  { id: 'grande', label: 'Grande', gramas: 150, emoji: '🥣' }
];

export default function CheckinRefeicao({ pin, nome, onClose, onSuccess }) {
  const [itens, setItens] = useState([]);
  const [loading, setLoading] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState('');
  const [resultado, setResultado] = useState(null);
  const [mostrarCandidatos, setMostrarCandidatos] = useState(false);
  const [candidatos, setCandidatos] = useState([]);

  // Normalizar imagem antes de enviar (R3: 512px max, JPEG 82%, alinhado App.js)
  const normalizeImage = (file) => {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        const maxSize = 512;
        let w = img.width;
        let h = img.height;
        if (w > maxSize || h > maxSize) {
          const ratio = Math.min(maxSize / w, maxSize / h);
          w = Math.round(w * ratio);
          h = Math.round(h * ratio);
        }
        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        canvas.getContext('2d').drawImage(img, 0, 0, w, h);
        canvas.toBlob((blob) => resolve(blob || file), 'image/jpeg', 0.82);
      };
      img.onerror = () => resolve(file);
      img.src = URL.createObjectURL(file);
    });
  };

  // Identificar foto e mostrar candidatos
  const handleFoto = useCallback(async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError('');
    setCandidatos([]);

    try {
      const normalized = await normalizeImage(file);
      const formData = new FormData();
      formData.append('file', normalized, 'photo.jpg');

      const res = await fetch(`${API}/api/ai/identify`, {
        method: 'POST',
        body: formData
      });

      const data = await res.json();

      if (data.identified && data.score >= 0.5) {
        // Mostrar os top 5 candidatos para o usuário escolher
        const topCandidatos = data.top_matches?.slice(0, 5) || [
          { dish: data.dish, dish_display: data.dish_display, score: data.score }
        ];
        
        setCandidatos(topCandidatos);
        setMostrarCandidatos(true);
      } else {
        setError('Não foi possível identificar o prato. Tente novamente com melhor iluminação.');
      }
    } catch (err) {
      setError('Erro ao processar imagem. Tente novamente.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Adicionar item à lista
  const adicionarItem = useCallback((candidato) => {
    setItens(prev => [...prev, {
      id: Date.now(),
      nome: candidato.dish_display || candidato.dish,
      slug: candidato.dish,
      porcao: 'media',
      score: candidato.score
    }]);
    setMostrarCandidatos(false);
    setCandidatos([]);
  }, []);

  // Remover item
  const removerItem = useCallback((id) => {
    setItens(prev => prev.filter(item => item.id !== id));
  }, []);

  // Alterar porção
  const alterarPorcao = useCallback((id, novaPorcao) => {
    setItens(prev => prev.map(item => 
      item.id === id ? { ...item, porcao: novaPorcao } : item
    ));
  }, []);

  // Enviar check-in
  const enviarCheckin = useCallback(async () => {
    if (itens.length === 0) {
      setError('Adicione pelo menos um item ao prato');
      return;
    }

    setEnviando(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('pin', pin);
      formData.append('nome', nome);
      formData.append('itens', JSON.stringify(itens.map(i => ({
        nome: i.nome,
        porcao: i.porcao
      }))));

      const res = await fetch(`${API}/api/premium/checkin`, {
        method: 'POST',
        body: formData
      });

      const data = await res.json();

      if (data.ok) {
        setResultado(data);
        if (onSuccess) onSuccess(data);
      } else {
        setError(data.error || 'Erro ao registrar check-in');
      }
    } catch (err) {
      setError('Erro de conexão. Tente novamente.');
    } finally {
      setEnviando(false);
    }
  }, [itens, pin, nome, onSuccess]);

  // Fechar e limpar
  const handleClose = useCallback(() => {
    setItens([]);
    setResultado(null);
    setCandidatos([]);
    setMostrarCandidatos(false);
    if (onClose) onClose();
  }, [onClose]);

  return (
    <div className="checkin-container" data-testid="checkin-refeicao">
      <div className="checkin-header">
        <h2>🍽️ Check-in de Refeição</h2>
        <button className="close-btn" onClick={handleClose} data-testid="checkin-close">
          <X size={20} />
        </button>
      </div>

      {/* Resultado do check-in */}
      {resultado ? (
        <div className="checkin-resultado" data-testid="checkin-resultado">
          <div className="resultado-success">
            <Check size={40} />
            <h3>Registrado!</h3>
          </div>
          
          <div className="resultado-refeicao">
            <h4>Esta refeição:</h4>
            {resultado.refeicao?.itens?.map((item, i) => (
              <div key={i} className="resultado-item">
                <span>{item.nome}</span>
                <span className="item-calorias">{item.calorias} kcal</span>
              </div>
            ))}
            <div className="resultado-total">
              <strong>Total: {resultado.refeicao?.total_calorias} kcal</strong>
            </div>
          </div>

          <div className="resultado-dia">
            <h4>📊 Seu dia:</h4>
            <div className="dia-progress">
              <div className="dia-bar">
                <div 
                  className="dia-fill" 
                  style={{ width: `${Math.min(resultado.dia?.percentual || 0, 100)}%` }}
                />
              </div>
              <span className="dia-texto">
                {resultado.dia?.consumido} / {resultado.dia?.meta} kcal ({resultado.dia?.percentual}%)
              </span>
            </div>
            <p className="dia-restante">
              {resultado.dia?.restante > 0 
                ? `Restam ${resultado.dia?.restante} kcal para a meta` 
                : `Meta atingida! Excedido em ${Math.abs(resultado.dia?.restante)} kcal`}
            </p>
          </div>

          <button className="btn-novo-checkin" onClick={() => setResultado(null)}>
            + Novo Check-in
          </button>
        </div>
      ) : (
        <>
          {/* Instruções */}
          <p className="checkin-instrucao">
            Tire uma foto de cada item do seu prato ou adicione manualmente. 
            Ajuste as porções conforme necessário.
          </p>

          {/* Botão de captura */}
          <label className="capture-btn" data-testid="checkin-capture-btn">
            <Camera size={24} />
            <span>{loading ? 'Identificando...' : 'Fotografar Item'}</span>
            <input 
              type="file" 
              accept="image/*" 
              capture="environment"
              onChange={handleFoto}
              disabled={loading}
              hidden
            />
          </label>

          {/* Lista de candidatos */}
          {mostrarCandidatos && candidatos.length > 0 && (
            <div className="candidatos-lista" data-testid="candidatos-lista">
              <p className="candidatos-titulo">
                <ChevronDown size={16} /> Selecione o item correto:
              </p>
              {candidatos.map((c, i) => (
                <button 
                  key={i}
                  className="candidato-btn"
                  onClick={() => adicionarItem(c)}
                  data-testid={`candidato-${i}`}
                >
                  <span className="candidato-nome">{c.dish_display || c.dish}</span>
                  <span className="candidato-score">{(c.score * 100).toFixed(0)}%</span>
                </button>
              ))}
              <button 
                className="candidato-btn cancelar"
                onClick={() => { setMostrarCandidatos(false); setCandidatos([]); }}
              >
                Cancelar
              </button>
            </div>
          )}

          {/* Lista de itens adicionados */}
          {itens.length > 0 && (
            <div className="itens-lista" data-testid="itens-lista">
              <h4>
                <ChevronUp size={16} /> Itens do prato ({itens.length})
              </h4>
              {itens.map(item => (
                <div key={item.id} className="item-card" data-testid={`item-${item.id}`}>
                  <div className="item-info">
                    <span className="item-nome">{item.nome}</span>
                    <span className="item-confianca">{(item.score * 100).toFixed(0)}%</span>
                  </div>
                  
                  <div className="item-porcao">
                    {PORCOES.map(p => (
                      <button
                        key={p.id}
                        className={`porcao-btn ${item.porcao === p.id ? 'active' : ''}`}
                        onClick={() => alterarPorcao(item.id, p.id)}
                        title={`${p.label} (~${p.gramas}g)`}
                      >
                        {p.emoji}
                      </button>
                    ))}
                  </div>

                  <button 
                    className="remover-btn"
                    onClick={() => removerItem(item.id)}
                    title="Remover item"
                  >
                    <Minus size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Erro */}
          {error && (
            <div className="checkin-error" data-testid="checkin-error">
              {error}
            </div>
          )}

          {/* Botão de enviar */}
          {itens.length > 0 && (
            <button 
              className="enviar-btn"
              onClick={enviarCheckin}
              disabled={enviando}
              data-testid="checkin-enviar"
            >
              {enviando ? 'Registrando...' : `✓ Registrar ${itens.length} ${itens.length === 1 ? 'item' : 'itens'}`}
            </button>
          )}
        </>
      )}
    </div>
  );
}
