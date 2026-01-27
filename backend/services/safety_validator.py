"""
SoulNutri - Sistema de Segurança para Classificação de Pratos
Garante que proteínas animais NUNCA sejam classificadas como veganas
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# BANCO DE DADOS DE INGREDIENTES POR CATEGORIA
# ═══════════════════════════════════════════════════════════════════════════════

# 🍖 PROTEÍNA ANIMAL - Se encontrar QUALQUER um, NÃO é vegano nem vegetariano
PROTEINA_ANIMAL = {
    # Carnes
    "carne", "bife", "filé", "file", "picanha", "alcatra", "patinho", "acém", "acem",
    "costela", "cupim", "maminha", "contrafilé", "contrafile", "lagarto", "músculo", "musculo",
    "carne moída", "carne moida", "hambúrguer", "hamburger", "almôndega", "almondega",
    "boi", "vaca", "vitela", "cordeiro", "carneiro", "cabrito", "porco", "suíno", "suino",
    "lombo", "pernil", "bisteca", "costelinha",
    
    # Aves
    "frango", "galinha", "peru", "pato", "chester", "coxa", "sobrecoxa", "peito de frango",
    "asa", "coxinha da asa", "filé de frango", "file de frango", "nuggets", "empanado",
    
    # Peixes
    "peixe", "tilápia", "tilapia", "salmão", "salmao", "atum", "bacalhau", "sardinha",
    "pescada", "robalo", "dourado", "pintado", "surubim", "tucunaré", "tucunare",
    "merluza", "linguado", "truta", "anchova", "anchova", "cavala",
    
    # Frutos do mar
    "camarão", "camarao", "lagosta", "caranguejo", "siri", "lula", "polvo",
    "marisco", "mexilhão", "mexilhao", "ostra", "vieira", "frutos do mar",
    
    # Embutidos e processados
    "bacon", "presunto", "mortadela", "salame", "salsicha", "linguiça", "linguica",
    "copa", "pancetta", "paio", "calabresa", "pepperoni", "chorizo",
    "blanquet", "peito de peru",
    
    # Outros
    "gelatina", "tutano", "mocotó", "mocoto", "rabada", "dobradinha", "bucho",
    "fígado", "figado", "rim", "coração", "coracao", "moela",
}

# 🥬 VEGETARIANO (não vegano) - Se encontrar, é vegetariano mas NÃO vegano
DERIVADOS_ANIMAIS = {
    # Ovos
    "ovo", "ovos", "gema", "clara", "omelete", "omelette", "ovo frito",
    "ovo cozido", "ovo pochê", "ovo poche", "ovo mexido",
    
    # Laticínios (NOTA: queijo vegano será tratado separadamente)
    "leite", "queijo", "mussarela", "mozzarella", "parmesão", "parmesan", "parmesao",
    "provolone", "gorgonzola", "brie", "camembert", "cheddar", "coalho",
    "ricota", "cottage", "cream cheese", "requeijão", "requeijao",
    "manteiga", "nata", "creme de leite", "chantilly", "iogurte", "yogurt",
    "coalhada", "kefir", "queijo minas", "queijo prato", "catupiry",
    
    # Outros derivados
    "mel", "própolis", "propolis", "geleia real",
    "maionese", "aioli",  # contém ovo
}

# 🌱 VERSÕES VEGANAS - Se encontrar, NÃO é derivado animal
VERSOES_VEGANAS = {
    # Queijos veganos
    "queijo vegano", "queijo de castanha", "queijo de caju", "queijo de amêndoa",
    "queijo de macadâmia", "queijo de coco", "queijo plant-based", "queijo sem lactose vegano",
    "mussarela vegana", "parmesão vegano", "cheddar vegano", "cream cheese vegano",
    "requeijão vegano", "ricota vegana",
    
    # Maionese vegana
    "maionese vegana", "maionese de aquafaba", "aioli vegano",
    
    # Manteigas veganas  
    "manteiga vegana", "manteiga de coco", "margarina vegana",
    
    # Leites vegetais
    "leite de coco", "leite de amêndoas", "leite de soja", "leite de aveia",
    "leite de arroz", "leite vegetal", "leite de castanha", "leite de caju",
    
    # Cremes vegetais
    "creme de coco", "creme vegetal", "chantilly vegano", "nata de coco",
    "creme de leite de coco", "creme de soja",
    
    # Iogurtes vegetais
    "iogurte vegano", "iogurte de coco", "iogurte de soja", "iogurte vegetal",
}

# 🎨 IGNORAR NA ANÁLISE - Palavras que aparecem no contexto mas NÃO são ingredientes reais
IGNORAR_CONTEXTO = {
    # Decorações e apresentação
    "decoração", "decorado", "decorar", "decorada", "decorados",
    "enfeite", "enfeitado", "guarnição", "para decorar",
    "finalização", "finalizar", "para finalizar",
    
    # Contexto não-alimentar
    "molde", "forma", "recipiente", "prato", "tigela",
    "sirva", "servir", "acompanhe", "acompanhamento sugerido",
}

# 🚨 ALÉRGENOS CRÍTICOS
ALERGENOS = {
    "glúten": ["trigo", "centeio", "cevada", "aveia", "pão", "pao", "massa", "macarrão", "macarrao", 
               "farinha", "biscoito", "bolacha", "bolo", "torta", "pizza", "cerveja"],
    "lactose": ["leite", "queijo", "manteiga", "creme", "iogurte", "requeijão", "requeijao", 
                "mussarela", "parmesão", "parmesao", "nata", "chantilly"],
    "ovo": ["ovo", "ovos", "gema", "clara", "maionese", "aioli", "merengue"],
    "crustáceos": ["camarão", "camarao", "lagosta", "caranguejo", "siri"],
    "peixe": ["peixe", "salmão", "salmao", "atum", "bacalhau", "sardinha", "anchova"],
    "amendoim": ["amendoim", "paçoca", "pacoca", "manteiga de amendoim"],
    "nozes": ["noz", "nozes", "castanha", "amêndoa", "amendoa", "avelã", "avela", "pistache", "macadâmia", "macadamia"],
    "soja": ["soja", "tofu", "molho shoyu", "edamame", "missô", "misso"],
    "gergelim": ["gergelim", "tahine", "tahini"],
}


def normalizar_texto(texto: str) -> str:
    """Normaliza texto para comparação (lowercase, remove acentos básicos)"""
    if not texto:
        return ""
    texto = texto.lower().strip()
    # Substituições básicas de acentos
    substituicoes = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'ü': 'u',
        'ç': 'c'
    }
    for acentuado, sem_acento in substituicoes.items():
        texto = texto.replace(acentuado, sem_acento)
    return texto


def detectar_ingredientes_texto(texto: str, banco: set) -> List[str]:
    """Detecta ingredientes de um banco em um texto"""
    texto_norm = normalizar_texto(texto)
    encontrados = []
    
    for ingrediente in banco:
        ing_norm = normalizar_texto(ingrediente)
        # Busca por palavra completa ou parte significativa
        if ing_norm in texto_norm:
            encontrados.append(ingrediente)
        # Busca por padrão de palavra
        elif re.search(r'\b' + re.escape(ing_norm) + r'\b', texto_norm):
            encontrados.append(ingrediente)
    
    return encontrados


def validar_categoria(
    categoria_ia: str,
    nome_prato: str,
    ingredientes: List[str],
    descricao: str = ""
) -> Tuple[str, List[str], List[str]]:
    """
    Valida e corrige a categoria do prato baseado nos ingredientes detectados.
    
    Returns:
        Tuple[categoria_corrigida, proteinas_encontradas, derivados_encontrados]
    """
    # Concatenar todo texto para análise
    texto_completo = f"{nome_prato} {' '.join(ingredientes)} {descricao}"
    texto_norm = normalizar_texto(texto_completo)
    
    # Detectar proteínas animais
    proteinas = detectar_ingredientes_texto(texto_completo, PROTEINA_ANIMAL)
    
    # Detectar derivados animais (ovo, leite, etc)
    derivados = detectar_ingredientes_texto(texto_completo, DERIVADOS_ANIMAIS)
    
    categoria_original = normalizar_texto(categoria_ia)
    categoria_corrigida = categoria_ia
    
    # ═══════════════════════════════════════════════════════════════════════════
    # REGRA 1: Se tem proteína animal → SEMPRE "proteína animal"
    # ═══════════════════════════════════════════════════════════════════════════
    if proteinas:
        if categoria_original in ["vegano", "vegetariano"]:
            logger.warning(
                f"[SEGURANÇA] ⚠️ CORREÇÃO: '{nome_prato}' classificado como '{categoria_ia}' "
                f"mas contém PROTEÍNA ANIMAL: {proteinas}. Corrigindo para 'proteína animal'"
            )
        categoria_corrigida = "proteína animal"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # REGRA 2: Se tem derivados (ovo/leite) mas sem carne → "vegetariano"
    # ═══════════════════════════════════════════════════════════════════════════
    elif derivados:
        if categoria_original == "vegano":
            logger.warning(
                f"[SEGURANÇA] ⚠️ CORREÇÃO: '{nome_prato}' classificado como 'vegano' "
                f"mas contém DERIVADOS ANIMAIS: {derivados}. Corrigindo para 'vegetariano'"
            )
        categoria_corrigida = "vegetariano"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # REGRA 3: Se não tem nada animal → pode ser "vegano"
    # ═══════════════════════════════════════════════════════════════════════════
    else:
        # Mantém a classificação da IA se não encontrou nada animal
        if categoria_original == "vegano":
            categoria_corrigida = "vegano"
        elif categoria_original == "vegetariano":
            categoria_corrigida = "vegetariano"
    
    return categoria_corrigida, proteinas, derivados


def detectar_alergenos(
    nome_prato: str,
    ingredientes: List[str],
    descricao: str = ""
) -> Dict[str, List[str]]:
    """
    Detecta todos os alérgenos presentes no prato.
    
    Returns:
        Dict com alérgeno -> lista de ingredientes que o contém
    """
    texto_completo = f"{nome_prato} {' '.join(ingredientes)} {descricao}"
    
    alergenos_detectados = {}
    
    for alergeno, gatilhos in ALERGENOS.items():
        encontrados = detectar_ingredientes_texto(texto_completo, set(gatilhos))
        if encontrados:
            alergenos_detectados[alergeno] = encontrados
    
    return alergenos_detectados


def gerar_alertas_seguranca(
    nome_prato: str,
    categoria_ia: str,
    ingredientes: List[str],
    descricao: str = ""
) -> Dict:
    """
    Gera relatório completo de segurança do prato.
    
    Returns:
        Dict com categoria corrigida, alertas e recomendações
    """
    # Validar categoria
    categoria_corrigida, proteinas, derivados = validar_categoria(
        categoria_ia, nome_prato, ingredientes, descricao
    )
    
    # Detectar alérgenos
    alergenos = detectar_alergenos(nome_prato, ingredientes, descricao)
    
    # Gerar alertas
    alertas = []
    
    # Alerta de correção de categoria
    if categoria_corrigida != categoria_ia:
        alertas.append({
            "tipo": "CORREÇÃO_CATEGORIA",
            "severidade": "ALTA",
            "mensagem": f"Categoria corrigida de '{categoria_ia}' para '{categoria_corrigida}'",
            "motivo": proteinas if proteinas else derivados
        })
    
    # Alertas de alérgenos
    for alergeno, gatilhos in alergenos.items():
        alertas.append({
            "tipo": "ALERGENO",
            "severidade": "ALTA" if alergeno in ["amendoim", "crustáceos", "peixe"] else "MÉDIA",
            "mensagem": f"Contém {alergeno.upper()}",
            "ingredientes": gatilhos
        })
    
    # Alertas específicos
    if proteinas:
        alertas.append({
            "tipo": "PROTEINA_ANIMAL",
            "severidade": "INFO",
            "mensagem": f"Contém proteína animal: {', '.join(proteinas[:3])}"
        })
    
    resultado = {
        "categoria_original": categoria_ia,
        "categoria_corrigida": categoria_corrigida,
        "categoria_alterada": categoria_corrigida != categoria_ia,
        "proteinas_detectadas": proteinas,
        "derivados_detectados": derivados,
        "alergenos": alergenos,
        "alertas": alertas,
        "seguro_para_veganos": len(proteinas) == 0 and len(derivados) == 0,
        "seguro_para_vegetarianos": len(proteinas) == 0,
        "total_alertas": len(alertas)
    }
    
    # Log se houve correção crítica
    if proteinas and categoria_ia == "vegano":
        logger.error(
            f"[SEGURANÇA CRÍTICA] 🚨 Prato '{nome_prato}' QUASE foi classificado como VEGANO "
            f"mas contém: {proteinas}. CORRIGIDO para 'proteína animal'."
        )
    
    return resultado


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÃO PRINCIPAL DE VALIDAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

def validar_resultado_ia(resultado: Dict) -> Dict:
    """
    Valida e corrige o resultado da IA antes de retornar ao usuário.
    
    Args:
        resultado: Dict com resultado da identificação da IA
        
    Returns:
        Dict corrigido com validações de segurança
    """
    nome = resultado.get("nome") or resultado.get("dish_display") or ""
    categoria = resultado.get("categoria") or resultado.get("category") or ""
    ingredientes = resultado.get("ingredientes_provaveis") or resultado.get("ingredientes") or []
    descricao = resultado.get("descricao") or ""
    
    # Se não tem dados suficientes, retorna sem alteração
    if not nome and not ingredientes:
        return resultado
    
    # Gerar relatório de segurança
    seguranca = gerar_alertas_seguranca(nome, categoria, ingredientes, descricao)
    
    # Aplicar correções
    resultado_corrigido = resultado.copy()
    
    # Corrigir categoria se necessário
    if seguranca["categoria_alterada"]:
        resultado_corrigido["categoria"] = seguranca["categoria_corrigida"]
        resultado_corrigido["category"] = seguranca["categoria_corrigida"]
        
        # Atualizar emoji
        if seguranca["categoria_corrigida"] == "proteína animal":
            resultado_corrigido["category_emoji"] = "🍖"
        elif seguranca["categoria_corrigida"] == "vegetariano":
            resultado_corrigido["category_emoji"] = "🥬"
        else:
            resultado_corrigido["category_emoji"] = "🌱"
    
    # Adicionar alertas de alérgenos aos riscos
    riscos = resultado_corrigido.get("riscos") or []
    for alergeno, gatilhos in seguranca["alergenos"].items():
        alerta = f"Alérgeno: {alergeno.upper()} ({', '.join(gatilhos[:2])})"
        if alerta not in riscos:
            riscos.append(alerta)
    resultado_corrigido["riscos"] = riscos
    
    # Adicionar metadados de segurança
    resultado_corrigido["_seguranca"] = {
        "validado": True,
        "categoria_alterada": seguranca["categoria_alterada"],
        "proteinas_detectadas": seguranca["proteinas_detectadas"],
        "derivados_detectados": seguranca["derivados_detectados"],
        "alergenos_detectados": list(seguranca["alergenos"].keys()),
        "seguro_veganos": seguranca["seguro_para_veganos"],
        "seguro_vegetarianos": seguranca["seguro_para_vegetarianos"]
    }
    
    return resultado_corrigido


# ═══════════════════════════════════════════════════════════════════════════════
# TESTES RÁPIDOS
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Teste 1: Peixe classificado como vegano (ERRO que deve ser corrigido)
    teste1 = {
        "nome": "Filé de Tilápia Grelhada",
        "categoria": "vegano",  # ERRO da IA
        "ingredientes_provaveis": ["tilápia", "limão", "azeite", "ervas"],
        "descricao": "Peixe grelhado com ervas"
    }
    
    resultado1 = validar_resultado_ia(teste1)
    print("Teste 1 - Peixe como vegano:")
    print(f"  Categoria original: {teste1['categoria']}")
    print(f"  Categoria corrigida: {resultado1['categoria']}")
    print(f"  Proteínas detectadas: {resultado1['_seguranca']['proteinas_detectadas']}")
    print()
    
    # Teste 2: Salada com ovo classificada como vegana
    teste2 = {
        "nome": "Salada Caesar",
        "categoria": "vegano",  # ERRO da IA
        "ingredientes_provaveis": ["alface", "croutons", "parmesão", "molho caesar"],
        "descricao": "Salada com queijo parmesão"
    }
    
    resultado2 = validar_resultado_ia(teste2)
    print("Teste 2 - Salada Caesar como vegana:")
    print(f"  Categoria original: {teste2['categoria']}")
    print(f"  Categoria corrigida: {resultado2['categoria']}")
    print(f"  Derivados detectados: {resultado2['_seguranca']['derivados_detectados']}")
    print()
    
    # Teste 3: Prato realmente vegano
    teste3 = {
        "nome": "Arroz com Legumes",
        "categoria": "vegano",
        "ingredientes_provaveis": ["arroz", "cenoura", "brócolis", "abobrinha"],
        "descricao": "Arroz integral com legumes salteados"
    }
    
    resultado3 = validar_resultado_ia(teste3)
    print("Teste 3 - Arroz com Legumes (vegano correto):")
    print(f"  Categoria original: {teste3['categoria']}")
    print(f"  Categoria corrigida: {resultado3['categoria']}")
    print(f"  Seguro para veganos: {resultado3['_seguranca']['seguro_veganos']}")
