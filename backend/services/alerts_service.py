"""
SoulNutri Premium - Serviço de Alertas Inteligentes
Gera alertas em tempo real baseados no perfil e histórico do usuário
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# LIMITES DIÁRIOS RECOMENDADOS (OMS/ANVISA)
# ═══════════════════════════════════════════════════════════════════════════════

LIMITES_DIARIOS = {
    "sodio": {"limite": 2000, "unidade": "mg", "nome": "Sódio", "emoji": "🧂"},
    "acucar": {"limite": 25, "unidade": "g", "nome": "Açúcar", "emoji": "🍬"},
    "gordura_saturada": {"limite": 22, "unidade": "g", "nome": "Gordura Saturada", "emoji": "🧈"},
    "fibras": {"limite": 25, "unidade": "g", "nome": "Fibras", "emoji": "🌾", "tipo": "minimo"},
    "proteinas": {"limite": 50, "unidade": "g", "nome": "Proteínas", "emoji": "💪", "tipo": "minimo"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# NUTRIENTES POR ALIMENTO (estimativas para alertas)
# ═══════════════════════════════════════════════════════════════════════════════

NUTRIENTES_ALIMENTOS = {
    # Alimentos ricos em sódio
    "bacon": {"sodio": 1500, "gordura_saturada": 15},
    "presunto": {"sodio": 1200, "gordura_saturada": 5},
    "queijo": {"sodio": 600, "gordura_saturada": 12, "lactose": True},
    "salsicha": {"sodio": 800, "gordura_saturada": 10},
    "linguiça": {"sodio": 900, "gordura_saturada": 12},
    "embutido": {"sodio": 1000, "gordura_saturada": 10},
    "molho de soja": {"sodio": 1000},
    "shoyu": {"sodio": 1000},
    "ketchup": {"sodio": 400, "acucar": 8},
    "maionese": {"sodio": 300, "gordura_saturada": 8},
    
    # Alimentos ricos em açúcar
    "refrigerante": {"acucar": 35},
    "suco industrializado": {"acucar": 25},
    "bolo": {"acucar": 30, "gordura_saturada": 8, "gluten": True},
    "doce": {"acucar": 40},
    "sorvete": {"acucar": 25, "gordura_saturada": 10, "lactose": True},
    "chocolate": {"acucar": 45, "gordura_saturada": 15},
    
    # Alimentos saudáveis (ricos em fibras/proteínas)
    "feijão": {"fibras": 8, "proteinas": 7},
    "lentilha": {"fibras": 10, "proteinas": 9},
    "grão de bico": {"fibras": 8, "proteinas": 8},
    "brócolis": {"fibras": 5, "proteinas": 3},
    "espinafre": {"fibras": 4, "proteinas": 3},
    "aveia": {"fibras": 10, "proteinas": 5, "gluten": True},
    "quinoa": {"fibras": 5, "proteinas": 8},
    "salmão": {"proteinas": 25, "omega3": True},
    "frango": {"proteinas": 30},
    "ovo": {"proteinas": 6, "ovo": True},
}

# ═══════════════════════════════════════════════════════════════════════════════
# COMBINAÇÕES INTELIGENTES
# ═══════════════════════════════════════════════════════════════════════════════

COMBINACOES_INTELIGENTES = [
    {
        "gatilho": ["feijão", "lentilha", "grão de bico", "espinafre"],
        "sugestao": "vitamina C",
        "exemplos": ["limão", "laranja", "pimentão"],
        "beneficio": "A vitamina C aumenta em até 6x a absorção do ferro vegetal!",
        "emoji": "🍋"
    },
    {
        "gatilho": ["cenoura", "tomate", "abóbora"],
        "sugestao": "gordura boa",
        "exemplos": ["azeite", "abacate", "castanhas"],
        "beneficio": "O betacaroteno é absorvido melhor com gorduras saudáveis!",
        "emoji": "🥑"
    },
    {
        "gatilho": ["brócolis", "couve", "espinafre"],
        "sugestao": "proteína",
        "exemplos": ["frango", "peixe", "ovo"],
        "beneficio": "A proteína ajuda a fixar os nutrientes das folhas verdes!",
        "emoji": "🥦"
    },
    {
        "gatilho": ["arroz"],
        "sugestao": "leguminosas",
        "exemplos": ["feijão", "lentilha", "ervilha"],
        "beneficio": "Arroz + feijão = proteína completa com todos os aminoácidos essenciais!",
        "emoji": "🍚"
    }
]

# ═══════════════════════════════════════════════════════════════════════════════
# SUBSTITUIÇÕES SAUDÁVEIS
# ═══════════════════════════════════════════════════════════════════════════════

SUBSTITUICOES = {
    "batata frita": {"substituto": "batata assada ou chips de abobrinha", "economia": "70% menos gordura"},
    "arroz branco": {"substituto": "arroz integral ou quinoa", "economia": "3x mais fibras"},
    "cream cheese": {"substituto": "ricota ou pasta de tofu", "economia": "50% menos gordura"},
    "macarrão": {"substituto": "macarrão de abobrinha ou integral", "economia": "menos carboidratos refinados"},
    "refrigerante": {"substituto": "água com gás e limão", "economia": "zero açúcar"},
    "maionese": {"substituto": "iogurte natural com ervas", "economia": "80% menos gordura"},
    "pão branco": {"substituto": "pão integral ou de fermentação natural", "economia": "mais fibras e nutrientes"},
    "açúcar": {"substituto": "mel, stevia ou frutas", "economia": "índice glicêmico menor"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE ALERTA
# ═══════════════════════════════════════════════════════════════════════════════

def analisar_nutrientes_prato(ingredientes: List[str]) -> Dict:
    """
    Analisa os nutrientes de um prato baseado nos ingredientes.
    """
    nutrientes = {
        "sodio": 0,
        "acucar": 0,
        "gordura_saturada": 0,
        "fibras": 0,
        "proteinas": 0,
        "alergenos": []
    }
    
    texto = ' '.join(ingredientes).lower()
    
    for alimento, valores in NUTRIENTES_ALIMENTOS.items():
        if alimento in texto:
            for nutriente, valor in valores.items():
                if nutriente in nutrientes and isinstance(valor, (int, float)):
                    nutrientes[nutriente] += valor
                elif valor is True:
                    if nutriente not in nutrientes["alergenos"]:
                        nutrientes["alergenos"].append(nutriente)
    
    return nutrientes


async def gerar_alertas_tempo_real(
    db,
    user_nome: str,
    prato_info: Dict,
    ingredientes: List[str]
) -> List[Dict]:
    """
    Gera alertas em tempo real baseados no histórico semanal do usuário.
    """
    alertas = []
    
    # Buscar histórico da semana
    data_inicio = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    cursor = db.daily_logs.find(
        {"user_nome": user_nome, "data": {"$gte": data_inicio}},
        {"_id": 0}
    )
    historico = await cursor.to_list(length=7)
    
    # Calcular consumo semanal acumulado
    consumo_semanal = {
        "sodio": 0,
        "acucar": 0,
        "gordura_saturada": 0,
        "fibras": 0,
        "proteinas": 0
    }
    
    for dia in historico:
        for prato in dia.get("pratos", []):
            nutrientes = prato.get("nutrientes", {})
            for key in consumo_semanal:
                consumo_semanal[key] += nutrientes.get(key, 0)
    
    # Analisar nutrientes do prato atual
    nutrientes_prato = analisar_nutrientes_prato(ingredientes)
    
    # Gerar alertas de limite
    for nutriente, info in LIMITES_DIARIOS.items():
        if nutriente in nutrientes_prato:
            valor_prato = nutrientes_prato[nutriente]
            valor_semanal = consumo_semanal.get(nutriente, 0)
            limite_semanal = info["limite"] * 7
            
            if info.get("tipo") == "minimo":
                # Nutrientes que queremos aumentar
                # SÓ mostra alerta se o prato realmente tem valor significativo
                if valor_prato > 0 and valor_semanal < limite_semanal * 0.5:
                    alertas.append({
                        "tipo": "positivo",
                        "severidade": "info",
                        "emoji": info["emoji"],
                        "titulo": f"Boa escolha de {info['nome']}!",
                        "mensagem": f"Este prato contribui com {valor_prato}{info['unidade']} de {info['nome'].lower()}. Continue assim!",
                        "nutriente": nutriente
                    })
            else:
                # Nutrientes que queremos limitar
                if valor_prato > info["limite"] * 0.3:
                    percentual_semanal = (valor_semanal / limite_semanal) * 100
                    
                    if percentual_semanal > 80:
                        alertas.append({
                            "tipo": "alerta",
                            "severidade": "alta",
                            "emoji": "🚨",
                            "titulo": f"Atenção ao {info['nome']}!",
                            "mensagem": f"Este prato tem {valor_prato}{info['unidade']} de {info['nome'].lower()}. Você já consumiu {valor_semanal:.0f}{info['unidade']} esta semana ({percentual_semanal:.0f}% do limite)!",
                            "nutriente": nutriente
                        })
                    elif percentual_semanal > 50:
                        alertas.append({
                            "tipo": "aviso",
                            "severidade": "media",
                            "emoji": "⚠️",
                            "titulo": f"Moderação com {info['nome']}",
                            "mensagem": f"Este alimento contém {valor_prato}{info['unidade']} de {info['nome'].lower()}. Consumo semanal: {valor_semanal:.0f}{info['unidade']}.",
                            "nutriente": nutriente
                        })
    
    return alertas


def gerar_combinacoes_sugeridas(ingredientes: List[str]) -> List[Dict]:
    """
    Sugere combinações inteligentes baseadas no prato identificado.
    """
    sugestoes = []
    texto = ' '.join(ingredientes).lower()
    
    for combo in COMBINACOES_INTELIGENTES:
        for gatilho in combo["gatilho"]:
            if gatilho in texto:
                sugestoes.append({
                    "emoji": combo["emoji"],
                    "titulo": f"Combine com {combo['sugestao']}!",
                    "exemplos": combo["exemplos"],
                    "beneficio": combo["beneficio"]
                })
                break
    
    return sugestoes[:2]  # Máximo 2 sugestões


def gerar_substituicoes(ingredientes: List[str]) -> List[Dict]:
    """
    Sugere substituições mais saudáveis.
    """
    sugestoes = []
    texto = ' '.join(ingredientes).lower()
    
    for alimento, info in SUBSTITUICOES.items():
        if alimento in texto:
            sugestoes.append({
                "emoji": "💡",
                "original": alimento,
                "substituto": info["substituto"],
                "beneficio": info["economia"]
            })
    
    return sugestoes[:2]  # Máximo 2 sugestões


def verificar_alergenos_perfil(perfil: Dict, ingredientes: List[str]) -> List[Dict]:
    """
    Verifica se o prato contém alérgenos do perfil do usuário.
    """
    alertas = []
    alergias_usuario = [a.lower() for a in perfil.get("alergias", [])]
    restricoes = [r.lower() for r in perfil.get("restricoes", [])]
    
    texto = ' '.join(ingredientes).lower()
    
    # Mapeamento de alérgenos
    mapa = {
        "gluten": ["trigo", "farinha", "pão", "massa", "macarrão", "bolo", "bolacha", "cerveja", "cevada"],
        "lactose": ["leite", "queijo", "creme", "manteiga", "iogurte", "requeijão", "cream cheese", "sorvete"],
        "ovo": ["ovo", "ovos", "gema", "clara", "maionese"],
        "amendoim": ["amendoim", "paçoca"],
        "castanhas": ["castanha", "nozes", "amêndoa", "avelã", "pistache", "macadâmia"],
        "peixe": ["peixe", "salmão", "atum", "bacalhau", "sardinha", "tilápia", "anchova"],
        "crustaceos": ["camarão", "lagosta", "caranguejo", "siri"],
        "soja": ["soja", "tofu", "edamame", "shoyu", "molho de soja"]
    }
    
    for alergia in alergias_usuario:
        palavras = mapa.get(alergia, [alergia])
        for palavra in palavras:
            if palavra in texto:
                alertas.append({
                    "tipo": "alergia",
                    "severidade": "critica",
                    "emoji": "🚫",
                    "titulo": f"CONTÉM {alergia.upper()}!",
                    "mensagem": f"Este prato pode conter {palavra}, que está na sua lista de alergias.",
                    "ingrediente": palavra
                })
                break
    
    # Verificar restrições
    if "vegano" in restricoes:
        produtos_animais = ["carne", "frango", "peixe", "ovo", "leite", "queijo", "mel", "bacon", "presunto"]
        for produto in produtos_animais:
            if produto in texto:
                alertas.append({
                    "tipo": "restricao",
                    "severidade": "alta",
                    "emoji": "🌱",
                    "titulo": "Não é vegano!",
                    "mensagem": f"Este prato contém {produto}.",
                    "ingrediente": produto
                })
                break
    
    if "vegetariano" in restricoes:
        carnes = ["carne", "frango", "peixe", "bacon", "presunto", "linguiça", "salsicha"]
        for carne in carnes:
            if carne in texto:
                alertas.append({
                    "tipo": "restricao",
                    "severidade": "alta",
                    "emoji": "🥬",
                    "titulo": "Contém carne!",
                    "mensagem": f"Este prato contém {carne}.",
                    "ingrediente": carne
                })
                break
    
    return alertas
