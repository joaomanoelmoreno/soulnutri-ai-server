"""
SoulNutri Premium - Serviço de Perfil do Usuário
Gerencia perfil, metas calóricas e histórico
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List
from pydantic import BaseModel
import hashlib

# =====================
# MODELS
# =====================

class UserProfile(BaseModel):
    pin_hash: str
    nome: str
    peso: float  # kg
    altura: float  # cm
    idade: int
    sexo: str  # 'M' ou 'F'
    nivel_atividade: str  # 'sedentario', 'leve', 'moderado', 'intenso', 'muito_intenso'
    objetivo: str  # 'perder', 'manter', 'ganhar'
    alergias: List[str] = []
    restricoes: List[str] = []  # 'vegano', 'vegetariano', 'sem_gluten', 'sem_lactose'
    meta_calorica_manual: Optional[int] = None  # Se o usuário definir manualmente
    # Campos Premium
    plano: str = "free"  # 'free', 'premium', 'premium_trial'
    premium_ate: Optional[datetime] = None  # Data de expiração do Premium
    premium_liberado_por: Optional[str] = None  # Quem liberou (admin)
    premium_liberado_em: Optional[datetime] = None  # Quando foi liberado
    created_at: datetime = None
    updated_at: datetime = None

class DailyLog(BaseModel):
    user_id: str
    data: str  # YYYY-MM-DD
    pratos: List[dict] = []  # Lista de pratos identificados
    calorias_total: float = 0
    proteinas_total: float = 0
    carboidratos_total: float = 0
    gorduras_total: float = 0


# =====================
# FUNÇÕES PREMIUM
# =====================

def verificar_premium_ativo(user: dict) -> dict:
    """
    Verifica se o usuário tem Premium ativo e válido.
    Retorna status e informações.
    """
    if not user:
        return {"ativo": False, "motivo": "Usuário não encontrado"}
    
    plano = user.get("plano", "free")
    premium_ate = user.get("premium_ate")
    
    # Se não tem plano premium
    if plano == "free":
        return {"ativo": False, "motivo": "Plano gratuito"}
    
    # Se é premium sem data de expiração (vitalício)
    if plano == "premium" and not premium_ate:
        return {
            "ativo": True, 
            "plano": "premium",
            "expira": None,
            "motivo": "Premium vitalício"
        }
    
    # Verificar se não expirou
    if premium_ate:
        # Converter string para datetime se necessário
        if isinstance(premium_ate, str):
            premium_ate = datetime.fromisoformat(premium_ate.replace('Z', '+00:00'))
        
        agora = datetime.now(timezone.utc)
        
        if premium_ate > agora:
            dias_restantes = (premium_ate - agora).days
            return {
                "ativo": True,
                "plano": plano,
                "expira": premium_ate.isoformat(),
                "dias_restantes": dias_restantes,
                "motivo": f"Premium válido por mais {dias_restantes} dias"
            }
        else:
            return {
                "ativo": False,
                "plano": plano,
                "expirou_em": premium_ate.isoformat(),
                "motivo": "Premium expirado"
            }
    
    return {"ativo": False, "motivo": "Status indefinido"}


def liberar_premium(dias: int = 7, liberado_por: str = "admin") -> dict:
    """
    Gera dados para liberar Premium por X dias.
    Retorna dict com campos para atualizar no usuário.
    """
    agora = datetime.now(timezone.utc)
    expira = agora + timedelta(days=dias)
    
    return {
        "plano": "premium_trial" if dias <= 30 else "premium",
        "premium_ate": expira,
        "premium_liberado_por": liberado_por,
        "premium_liberado_em": agora
    }

# =====================
# CÁLCULOS NUTRICIONAIS
# =====================

def calcular_tmb(peso: float, altura: float, idade: int, sexo: str) -> float:
    """
    Calcula Taxa Metabólica Basal usando fórmula de Harris-Benedict revisada.
    """
    if sexo == 'M':
        # Homens: TMB = 88.362 + (13.397 × peso) + (4.799 × altura) - (5.677 × idade)
        tmb = 88.362 + (13.397 * peso) + (4.799 * altura) - (5.677 * idade)
    else:
        # Mulheres: TMB = 447.593 + (9.247 × peso) + (3.098 × altura) - (4.330 × idade)
        tmb = 447.593 + (9.247 * peso) + (3.098 * altura) - (4.330 * idade)
    
    return round(tmb, 0)

def calcular_meta_calorica(tmb: float, nivel_atividade: str, objetivo: str) -> dict:
    """
    Calcula meta calórica diária baseada no nível de atividade e objetivo.
    Retorna meta sugerida e faixa recomendada.
    """
    # Fatores de atividade
    fatores = {
        'sedentario': 1.2,      # Pouco ou nenhum exercício
        'leve': 1.375,          # Exercício leve 1-3 dias/semana
        'moderado': 1.55,       # Exercício moderado 3-5 dias/semana
        'intenso': 1.725,       # Exercício pesado 6-7 dias/semana
        'muito_intenso': 1.9    # Exercício muito pesado, trabalho físico
    }
    
    fator = fatores.get(nivel_atividade, 1.55)
    necessidade_diaria = tmb * fator
    
    # Ajuste por objetivo
    ajustes = {
        'perder': -500,    # Déficit de 500 kcal para perder ~0.5kg/semana
        'manter': 0,
        'ganhar': 300      # Superávit de 300 kcal para ganho muscular
    }
    
    ajuste = ajustes.get(objetivo, 0)
    meta = necessidade_diaria + ajuste
    
    return {
        'tmb': round(tmb, 0),
        'necessidade_diaria': round(necessidade_diaria, 0),
        'meta_sugerida': round(meta, 0),
        'faixa_minima': round(meta - 200, 0),
        'faixa_maxima': round(meta + 200, 0),
        'objetivo': objetivo,
        'nivel_atividade': nivel_atividade
    }

def hash_pin(pin: str) -> str:
    """Cria hash seguro do PIN"""
    return hashlib.sha256(pin.encode()).hexdigest()

def verificar_pin(pin: str, pin_hash: str) -> bool:
    """Verifica se o PIN está correto"""
    return hash_pin(pin) == pin_hash

# =====================
# ALERTAS PERSONALIZADOS
# =====================

def verificar_alertas_perfil(perfil: dict, prato: dict) -> List[dict]:
    """
    Verifica se um prato contém ingredientes que conflitam com
    as alergias/restrições do usuário.
    """
    alertas = []
    
    alergias = perfil.get('alergias', [])
    restricoes = perfil.get('restricoes', [])
    
    # Verificar alérgenos no prato
    riscos = prato.get('riscos', []) or []
    ingredientes = prato.get('ingredientes', []) or []
    
    # Converter para texto para busca
    texto_prato = ' '.join(riscos + ingredientes).lower()
    
    # Mapeamento de alergias para palavras-chave
    mapa_alergias = {
        'gluten': ['glúten', 'trigo', 'cevada', 'centeio', 'aveia'],
        'lactose': ['lactose', 'leite', 'queijo', 'creme', 'manteiga', 'iogurte'],
        'ovo': ['ovo', 'ovos', 'clara', 'gema'],
        'amendoim': ['amendoim', 'amendoins'],
        'castanhas': ['castanha', 'nozes', 'amêndoa', 'avelã', 'pistache'],
        'soja': ['soja', 'tofu', 'edamame'],
        'peixe': ['peixe', 'salmão', 'atum', 'bacalhau', 'sardinha'],
        'crustaceos': ['camarão', 'caranguejo', 'lagosta', 'crustáceo'],
        'mariscos': ['marisco', 'ostra', 'mexilhão', 'lula', 'polvo']
    }
    
    for alergia in alergias:
        alergia_lower = alergia.lower()
        palavras = mapa_alergias.get(alergia_lower, [alergia_lower])
        
        for palavra in palavras:
            if palavra in texto_prato:
                alertas.append({
                    'tipo': 'alergia',
                    'severidade': 'alta',
                    'mensagem': f'⚠️ ATENÇÃO: Este prato pode conter {alergia.upper()}!',
                    'ingrediente': palavra
                })
                break
    
    # Verificar restrições alimentares
    categoria = prato.get('category', '').lower()
    
    if 'vegano' in restricoes and categoria == 'proteína animal':
        alertas.append({
            'tipo': 'restricao',
            'severidade': 'media',
            'mensagem': '🚫 Este prato contém proteína animal (você é vegano)',
            'ingrediente': categoria
        })
    
    if 'vegetariano' in restricoes and categoria == 'proteína animal':
        if any(p in texto_prato for p in ['carne', 'frango', 'peixe', 'porco', 'boi']):
            alertas.append({
                'tipo': 'restricao',
                'severidade': 'media',
                'mensagem': '🚫 Este prato contém carne (você é vegetariano)',
                'ingrediente': 'carne'
            })
    
    return alertas
