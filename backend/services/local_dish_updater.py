"""
SoulNutri - Atualizador LOCAL de fichas (SEM IA, SEM CRÉDITOS)
Atualiza categoria, alérgenos e nutrição baseado em REGRAS LOCAIS
"""

import json
import re
from pathlib import Path

DATASET_DIR = Path("/app/datasets/organized")

# Banco de dados local de nutrição por tipo de prato
NUTRICAO_POR_TIPO = {
    "arroz": {"calorias": "130 kcal", "proteinas": "2.7g", "carboidratos": "28g", "gorduras": "0.3g"},
    "feijao": {"calorias": "77 kcal", "proteinas": "5g", "carboidratos": "14g", "gorduras": "0.5g"},
    "batata": {"calorias": "90 kcal", "proteinas": "2g", "carboidratos": "20g", "gorduras": "0.1g"},
    "frango": {"calorias": "165 kcal", "proteinas": "31g", "carboidratos": "0g", "gorduras": "3.6g"},
    "peixe": {"calorias": "120 kcal", "proteinas": "22g", "carboidratos": "0g", "gorduras": "3g"},
    "carne": {"calorias": "250 kcal", "proteinas": "26g", "carboidratos": "0g", "gorduras": "15g"},
    "salada": {"calorias": "25 kcal", "proteinas": "1.5g", "carboidratos": "4g", "gorduras": "0.2g"},
    "legume": {"calorias": "50 kcal", "proteinas": "2g", "carboidratos": "10g", "gorduras": "0.5g"},
    "massa": {"calorias": "131 kcal", "proteinas": "5g", "carboidratos": "25g", "gorduras": "1g"},
    "sobremesa": {"calorias": "180 kcal", "proteinas": "3g", "carboidratos": "30g", "gorduras": "5g"},
}

# Palavras que indicam categoria
PALAVRAS_PROTEINA = ["frango", "peixe", "carne", "boi", "porco", "camarão", "atum", "bacalhau", 
                     "salmão", "tilápia", "costela", "maminha", "filé", "sobrecoxa", "bacon",
                     "linguiça", "presunto", "almôndega", "kibe", "hambúrguer de carne"]
PALAVRAS_VEGETARIANO = ["queijo", "ovo", "leite", "iogurte", "manteiga", "creme de leite", 
                        "parmesão", "mussarela", "ricota"]
PALAVRAS_VEGANO = ["vegano", "vegana", "plant-based", "sem lactose vegano"]

# Palavras para alérgenos
PALAVRAS_GLUTEN = ["trigo", "farinha", "pão", "massa", "macarrão", "lasanha", "nhoque", "empanado"]
PALAVRAS_LACTOSE = ["queijo", "leite", "creme", "manteiga", "iogurte", "nata", "requeijão"]
PALAVRAS_OVO = ["ovo", "gema", "clara", "maionese"]
PALAVRAS_CASTANHAS = ["castanha", "amêndoa", "nozes", "amendoim", "pistache"]
PALAVRAS_FRUTOS_MAR = ["camarão", "lagosta", "caranguejo", "siri", "lula", "polvo", "marisco"]
PALAVRAS_SOJA = ["soja", "tofu", "shoyu", "missô"]


def detectar_categoria_por_nome(nome: str) -> str:
    """Detecta categoria baseado no nome do prato"""
    nome_lower = nome.lower()
    
    # Primeiro verifica se é explicitamente vegano
    for palavra in PALAVRAS_VEGANO:
        if palavra in nome_lower:
            return "vegano"
    
    # Verifica proteína animal
    for palavra in PALAVRAS_PROTEINA:
        if palavra in nome_lower:
            return "proteína animal"
    
    # Verifica vegetariano (tem derivado animal mas não carne)
    for palavra in PALAVRAS_VEGETARIANO:
        # Ignora se for versão vegana
        if palavra in nome_lower and "vegan" not in nome_lower:
            return "vegetariano"
    
    # Se não encontrou nada, assume vegano (legumes, grãos, etc)
    return "vegano"


def detectar_alergenos_por_nome(nome: str) -> dict:
    """Detecta alérgenos baseado no nome do prato"""
    nome_lower = nome.lower()
    
    alergenos = {
        "contem_gluten": any(p in nome_lower for p in PALAVRAS_GLUTEN),
        "contem_lactose": any(p in nome_lower for p in PALAVRAS_LACTOSE) and "vegan" not in nome_lower,
        "contem_ovo": any(p in nome_lower for p in PALAVRAS_OVO),
        "contem_castanhas": any(p in nome_lower for p in PALAVRAS_CASTANHAS),
        "contem_frutos_mar": any(p in nome_lower for p in PALAVRAS_FRUTOS_MAR),
        "contem_soja": any(p in nome_lower for p in PALAVRAS_SOJA),
    }
    
    return alergenos


def detectar_nutricao_por_nome(nome: str) -> dict:
    """Detecta nutrição aproximada baseado no nome"""
    nome_lower = nome.lower()
    
    for tipo, nutricao in NUTRICAO_POR_TIPO.items():
        if tipo in nome_lower:
            return nutricao.copy()
    
    # Default para prato genérico
    return {"calorias": "~100 kcal", "proteinas": "~5g", "carboidratos": "~15g", "gorduras": "~3g"}


def atualizar_prato_local(slug: str, novo_nome: str = None) -> dict:
    """
    Atualiza um prato LOCALMENTE baseado em regras, SEM chamar IA.
    
    Args:
        slug: ID do prato
        novo_nome: Novo nome (se for renomear)
    
    Returns:
        Resultado da atualização
    """
    dish_dir = DATASET_DIR / slug
    if not dish_dir.exists():
        return {"ok": False, "error": "Prato não encontrado"}
    
    info_path = dish_dir / "dish_info.json"
    
    # Carregar info atual
    current_info = {}
    if info_path.exists():
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                current_info = json.load(f)
        except:
            pass
    
    # Determinar nome a usar
    nome = novo_nome if novo_nome else current_info.get('nome', slug)
    
    # Detectar categoria
    nova_categoria = detectar_categoria_por_nome(nome)
    
    # Detectar alérgenos
    alergenos = detectar_alergenos_por_nome(nome)
    
    # Detectar nutrição se estiver vazia
    nutricao = current_info.get('nutricao', {})
    if not nutricao or not nutricao.get('calorias'):
        nutricao = detectar_nutricao_por_nome(nome)
    
    # Atualizar info
    current_info['nome'] = nome
    current_info['categoria'] = nova_categoria
    current_info['slug'] = slug
    current_info.update(alergenos)
    current_info['nutricao'] = nutricao
    
    # Emoji
    if "proteína" in nova_categoria:
        current_info['category_emoji'] = "🍖"
    elif "vegetariano" in nova_categoria:
        current_info['category_emoji'] = "🥚"
    else:
        current_info['category_emoji'] = "🌱"
    
    # Salvar
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(current_info, f, ensure_ascii=False, indent=2)
    
    return {
        "ok": True,
        "slug": slug,
        "nome": nome,
        "categoria": nova_categoria,
        "alergenos": alergenos,
        "nutricao": nutricao,
        "message": "Atualizado LOCALMENTE (sem IA, sem créditos)"
    }


def atualizar_todos_por_nome() -> dict:
    """Atualiza TODOS os pratos baseado no nome, SEM IA"""
    resultados = {"atualizados": 0, "erros": [], "total": 0}
    
    for dish_dir in DATASET_DIR.iterdir():
        if not dish_dir.is_dir():
            continue
        
        resultados["total"] += 1
        slug = dish_dir.name
        
        result = atualizar_prato_local(slug)
        if result.get("ok"):
            resultados["atualizados"] += 1
        else:
            resultados["erros"].append({"slug": slug, "error": result.get("error")})
    
    return resultados
