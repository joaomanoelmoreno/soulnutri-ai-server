"""
SoulNutri - Verdade ou Mito Nutricional
Base de conhecimento científico para educar usuários Premium
"""

import random
from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# BANCO DE VERDADES E MITOS NUTRICIONAIS
# Baseado em estudos científicos e diretrizes OMS/ANVISA
# ═══════════════════════════════════════════════════════════════════════════════

MITOS_VERDADES = {
    # ─────────────────────────────────────────────────────────────────────
    # OVOS
    # ─────────────────────────────────────────────────────────────────────
    "ovo": [
        {
            "afirmacao": "Comer ovo todo dia faz mal ao coração",
            "resposta": "MITO",
            "explicacao": "Estudos recentes mostram que até 3 ovos por dia são seguros para a maioria das pessoas. O ovo é rico em colina, essencial para o cérebro.",
            "fonte": "American Heart Association, 2020"
        },
        {
            "afirmacao": "A gema do ovo é a parte mais nutritiva",
            "resposta": "VERDADE",
            "explicacao": "A gema contém a maior parte das vitaminas (A, D, E, K), minerais e antioxidantes como luteína e zeaxantina.",
            "fonte": "USDA Nutrition Database"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # CARBOIDRATOS
    # ─────────────────────────────────────────────────────────────────────
    "arroz": [
        {
            "afirmacao": "Arroz branco engorda mais que arroz integral",
            "resposta": "PARCIALMENTE VERDADE",
            "explicacao": "Ambos têm calorias similares, mas o integral tem mais fibras, o que aumenta a saciedade e controla melhor a glicemia.",
            "fonte": "Harvard School of Public Health"
        },
        {
            "afirmacao": "Deixar o arroz esfriar reduz as calorias",
            "resposta": "VERDADE",
            "explicacao": "Ao esfriar, parte do amido vira 'amido resistente', que não é digerido e alimenta bactérias boas do intestino.",
            "fonte": "European Journal of Clinical Nutrition"
        }
    ],
    
    "pao": [
        {
            "afirmacao": "Pão integral sempre é mais saudável que pão branco",
            "resposta": "DEPENDE",
            "explicacao": "Muitos 'pães integrais' têm farinha branca como ingrediente principal. Verifique se 'farinha integral' é o primeiro ingrediente.",
            "fonte": "ANVISA - Rotulagem de Alimentos"
        }
    ],
    
    "macarrao": [
        {
            "afirmacao": "Macarrão à noite engorda",
            "resposta": "MITO",
            "explicacao": "O que importa é o total de calorias do dia, não o horário. Carboidratos à noite podem até melhorar o sono.",
            "fonte": "British Journal of Nutrition"
        }
    ],
    
    "batata": [
        {
            "afirmacao": "Batata doce é muito melhor que batata inglesa",
            "resposta": "MITO",
            "explicacao": "Ambas são nutritivas! A batata inglesa tem mais potássio, enquanto a doce tem mais vitamina A. Varie entre as duas.",
            "fonte": "USDA Nutrition Comparison"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # PROTEÍNAS
    # ─────────────────────────────────────────────────────────────────────
    "frango": [
        {
            "afirmacao": "Peito de frango é a parte mais saudável",
            "resposta": "PARCIALMENTE VERDADE",
            "explicacao": "É a parte mais magra, mas coxa e sobrecoxa têm mais ferro e zinco. O segredo é remover a pele.",
            "fonte": "Academy of Nutrition and Dietetics"
        }
    ],
    
    "carne": [
        {
            "afirmacao": "Carne vermelha causa câncer",
            "resposta": "CONTEXTO IMPORTANTE",
            "explicacao": "O risco aumenta com consumo EXCESSIVO (mais de 500g/semana) e carnes PROCESSADAS. Consumo moderado é seguro.",
            "fonte": "OMS/IARC, 2015"
        }
    ],
    
    "peixe": [
        {
            "afirmacao": "Quanto mais peixe, melhor para a saúde",
            "resposta": "COM MODERAÇÃO",
            "explicacao": "2-3 porções/semana é ideal. Peixes grandes (atum, cação) podem acumular mercúrio - evite consumo diário.",
            "fonte": "FDA Fish Advice"
        },
        {
            "afirmacao": "Salmão de cativeiro não é saudável",
            "resposta": "MITO",
            "explicacao": "Salmão de cativeiro ainda é rico em ômega-3 e proteínas. A diferença nutricional é pequena.",
            "fonte": "Journal of Nutrition"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # VEGETAIS E SALADAS
    # ─────────────────────────────────────────────────────────────────────
    "salada": [
        {
            "afirmacao": "Salada sempre é a opção mais saudável",
            "resposta": "DEPENDE",
            "explicacao": "Molhos cremosos, queijos e croutons podem transformar uma salada em bomba calórica. Prefira azeite e limão.",
            "fonte": "American Dietetic Association"
        }
    ],
    
    "cenoura": [
        {
            "afirmacao": "Cenoura melhora a visão",
            "resposta": "PARCIALMENTE VERDADE",
            "explicacao": "A vitamina A da cenoura é essencial para a visão, mas não vai te dar 'super visão'. Previne deficiências.",
            "fonte": "American Academy of Ophthalmology"
        }
    ],
    
    "espinafre": [
        {
            "afirmacao": "Espinafre é a melhor fonte de ferro",
            "resposta": "MITO",
            "explicacao": "O ferro do espinafre é pouco absorvido pelo corpo. Carnes e feijão são fontes melhores. Combine espinafre com vitamina C!",
            "fonte": "Journal of Food Science"
        }
    ],
    
    "brocolis": [
        {
            "afirmacao": "Brócolis cru é mais nutritivo que cozido",
            "resposta": "DEPENDE DO PREPARO",
            "explicacao": "Cozinhar no vapor preserva nutrientes. Ferver em água perde vitaminas. Cru pode ser difícil de digerir.",
            "fonte": "Journal of Agricultural and Food Chemistry"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # LEGUMINOSAS
    # ─────────────────────────────────────────────────────────────────────
    "feijao": [
        {
            "afirmacao": "Arroz com feijão é a combinação perfeita",
            "resposta": "VERDADE",
            "explicacao": "Juntos formam proteína completa com todos os aminoácidos essenciais. É a base da dieta brasileira!",
            "fonte": "FAO - Food and Agriculture Organization"
        },
        {
            "afirmacao": "Feijão dá gases por causa das fibras",
            "resposta": "PARCIALMENTE VERDADE",
            "explicacao": "São os oligossacarídeos, não as fibras. Deixar de molho e trocar a água reduz muito os gases.",
            "fonte": "Journal of Gastroenterology"
        }
    ],
    
    "lentilha": [
        {
            "afirmacao": "Lentilha tem mais proteína que carne",
            "resposta": "MITO",
            "explicacao": "100g de lentilha cozida tem ~9g de proteína, enquanto 100g de frango tem ~25g. Mas lentilha é ótima fonte vegetal!",
            "fonte": "USDA Nutrition Database"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # GORDURAS E ÓLEOS
    # ─────────────────────────────────────────────────────────────────────
    "azeite": [
        {
            "afirmacao": "Azeite perde propriedades quando aquecido",
            "resposta": "PARCIALMENTE VERDADE",
            "explicacao": "O azeite extra virgem pode ser aquecido até 180°C. Para frituras em alta temperatura, prefira óleo de coco ou abacate.",
            "fonte": "Journal of the American Oil Chemists Society"
        }
    ],
    
    "manteiga": [
        {
            "afirmacao": "Margarina é mais saudável que manteiga",
            "resposta": "NÃO NECESSARIAMENTE",
            "explicacao": "Muitas margarinas têm gordura trans. Manteiga com moderação ou margarina SEM gordura trans são opções válidas.",
            "fonte": "Harvard Health Publishing"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # BEBIDAS
    # ─────────────────────────────────────────────────────────────────────
    "suco": [
        {
            "afirmacao": "Suco natural é tão saudável quanto a fruta",
            "resposta": "MITO",
            "explicacao": "O suco perde as fibras e concentra o açúcar. Um copo pode ter açúcar de 3-4 frutas! Prefira comer a fruta inteira.",
            "fonte": "American Diabetes Association"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # GENÉRICOS (para qualquer prato)
    # ─────────────────────────────────────────────────────────────────────
    "_geral": [
        {
            "afirmacao": "Comer à noite engorda mais",
            "resposta": "MITO",
            "explicacao": "O corpo não muda o metabolismo à noite. O que importa é o total de calorias do dia, não o horário.",
            "fonte": "American Journal of Clinical Nutrition"
        },
        {
            "afirmacao": "Beber água durante as refeições atrapalha a digestão",
            "resposta": "MITO",
            "explicacao": "Não há evidência científica. A água pode até ajudar na digestão e aumentar a saciedade.",
            "fonte": "Mayo Clinic"
        },
        {
            "afirmacao": "Alimentos orgânicos são mais nutritivos",
            "resposta": "INCONCLUSIVO",
            "explicacao": "Estudos não mostram diferença nutricional significativa. O benefício principal é menor exposição a pesticidas.",
            "fonte": "Annals of Internal Medicine"
        },
        {
            "afirmacao": "Comer devagar emagrece",
            "resposta": "VERDADE",
            "explicacao": "O cérebro leva ~20 minutos para registrar saciedade. Comer rápido faz você comer mais antes de se sentir satisfeito.",
            "fonte": "Journal of the Academy of Nutrition and Dietetics"
        },
        {
            "afirmacao": "Glúten faz mal para todos",
            "resposta": "MITO",
            "explicacao": "Apenas ~1% da população tem doença celíaca. Para os demais, glúten é seguro e grãos integrais são saudáveis.",
            "fonte": "Gastroenterology Journal"
        }
    ]
}


def buscar_mito_por_ingrediente(ingredientes: List[str]) -> Optional[Dict]:
    """
    Busca um mito/verdade relevante baseado nos ingredientes do prato.
    """
    # Normalizar ingredientes
    ingredientes_norm = [i.lower().strip() for i in ingredientes]
    
    # Buscar correspondência
    for ingrediente in ingredientes_norm:
        for chave, mitos in MITOS_VERDADES.items():
            if chave in ingrediente or ingrediente in chave:
                if mitos and chave != "_geral":
                    return random.choice(mitos)
    
    # Fallback: retornar um mito geral
    return random.choice(MITOS_VERDADES.get("_geral", []))


def buscar_mito_por_categoria(categoria: str) -> Optional[Dict]:
    """
    Busca um mito/verdade baseado na categoria do prato.
    """
    categoria_norm = categoria.lower().strip()
    
    if "vegano" in categoria_norm or "vegetariano" in categoria_norm:
        opcoes = (
            MITOS_VERDADES.get("feijao", []) +
            MITOS_VERDADES.get("salada", []) +
            MITOS_VERDADES.get("arroz", [])
        )
    elif "proteína" in categoria_norm or "animal" in categoria_norm:
        opcoes = (
            MITOS_VERDADES.get("carne", []) +
            MITOS_VERDADES.get("frango", []) +
            MITOS_VERDADES.get("peixe", []) +
            MITOS_VERDADES.get("ovo", [])
        )
    else:
        opcoes = MITOS_VERDADES.get("_geral", [])
    
    if opcoes:
        return random.choice(opcoes)
    return None


def get_mito_verdade(ingredientes: List[str] = None, categoria: str = None) -> Dict:
    """
    Retorna um mito/verdade nutricional relevante para o prato.
    
    Args:
        ingredientes: Lista de ingredientes do prato
        categoria: Categoria do prato (vegano, vegetariano, proteína animal)
    
    Returns:
        Dict com afirmação, resposta, explicação e fonte
    """
    resultado = None
    
    # Primeiro tenta por ingrediente (mais específico)
    if ingredientes:
        resultado = buscar_mito_por_ingrediente(ingredientes)
    
    # Se não encontrou, tenta por categoria
    if not resultado and categoria:
        resultado = buscar_mito_por_categoria(categoria)
    
    # Fallback: mito geral
    if not resultado:
        resultado = random.choice(MITOS_VERDADES.get("_geral", []))
    
    if resultado:
        # Formatar emoji de resposta
        resposta = resultado.get("resposta", "")
        if resposta in ["MITO", "NÃO NECESSARIAMENTE"]:
            emoji = "❌"
        elif resposta in ["VERDADE"]:
            emoji = "✅"
        else:
            emoji = "⚠️"
        
        return {
            "afirmacao": resultado.get("afirmacao"),
            "resposta": resposta,
            "resposta_emoji": emoji,
            "explicacao": resultado.get("explicacao"),
            "fonte": resultado.get("fonte")
        }
    
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# TESTE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧪 Testando Verdade ou Mito:\n")
    
    # Teste com ingredientes
    print("1. Prato com ovo:")
    result = get_mito_verdade(ingredientes=["ovo", "tomate", "cebola"])
    print(f"   {result['resposta_emoji']} {result['resposta']}: \"{result['afirmacao']}\"")
    print(f"   📚 {result['explicacao'][:60]}...")
    print()
    
    # Teste com peixe
    print("2. Prato com peixe:")
    result = get_mito_verdade(ingredientes=["salmão", "legumes"])
    print(f"   {result['resposta_emoji']} {result['resposta']}: \"{result['afirmacao']}\"")
    print()
    
    # Teste por categoria
    print("3. Categoria vegana:")
    result = get_mito_verdade(categoria="vegano")
    print(f"   {result['resposta_emoji']} {result['resposta']}: \"{result['afirmacao']}\"")
