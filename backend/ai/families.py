"""SoulNutri AI - Familias de Pratos
Baseado nos documentos:
- /app/docs/PLANO_ORGANIZACAO_SOULNUTRI.md
- /app/docs/REVISAO_COMPLETA_SOULNUTRI.md

Familias agrupam pratos VISUALMENTE similares.
Quando o CLIP retorna top matches de uma mesma familia com scores proximos,
o sistema e HONESTO e sugere candidatos ao inves de afirmar.
"""

DISH_FAMILIES = {
    "Tabules": [
        "Tabule",
    ],
    "Salada de Ovos e Batatas": [
        "Salada de Ovos",
        "Salada de Batatas e Ovos",
    ],
    "Vinagretes": [
        "Molho Vinagrete",
        "Vinagrete de Lula",
    ],
    "Maminhas com Molho Escuro": [
        "Maminha ao Molho Mongolia",
        "Maminha na Cerveja Preta",
        "Maminha Molho Madeira",
    ],
    "Bacalhaus Desfiados": [
        "Bacalhau a Bras",
        "Bacalhau com Natas",
    ],
    "Gratinados e Assadeiras": [
        "Lasanha de Espinafre",
        "Lasanha de Berinjela",
        "Lasanha de Portobello",
        "Escondidinho de Carne Seca",
        "Berinjela a Parmegiana",
        "Couve-flor Gratinada",
        "Brocolis Gratinado",
        "Alho Poro Gratinado",
        "Canelone 4 Queijos",
        "Canelone de Espinafre",
        "Conchiglione ao Creme de Avelas",
        "Torta de Legumes",
        "Tortilha Espanhola de Batata",
    ],
    "Empanados e Milanesas": [
        "Peixe a Milanesa",
    ],
    "Pasteis": [
        "Pastel",
    ],
    "Tomates": [
        "Tomate",
        "Tomate Seco",
        "Umami de Tomates",
    ],
    "Pures": [
        "Pure de Batata",
        "Pure de Mandioquinha",
        "Pure de Maca Verde",
        "Pure de Abobora",
        "Aligot",
    ],
    "Quiches": [
        "Quiche de Alho Poro",
        "Quiche de Mussarela de Bufala com Tomate Seco",
        "Quiche de Tomate",
        "Tortinha de Gorgonzola e Figo",
    ],
    "Feijoes": [
        "Feijao Branco",
        "Feijao Tropeiro",
        "Feijao do Chef",
    ],
    "Mousses": [
        "Mousse de Chocolate sem Acucar",
        "Mousse de Limao",
        "Mousse de Maracuja",
    ],
    "Gelatinas": [
        "Gelatina de Abacaxi",
        "Gelatina de Cereja",
        "Gelatina de Limao",
        "Gelatina de Uva",
    ],
    "Rolinhos Vietnamitas": [
        "Rolinho Vietnamita",
        "Rolinho Vietnamita de Camarao",
        "Sushi Vietnamita",
    ],
    "Strogonoffs Animais": [
        "Estrogonofe de File Mignon",
        "Strogonoff de File Mignon",
    ],
    # Strogonoff Vegano mantido como dish individual (viola R1 — nao misturar vegano+animal)
    "Hamburgers": [
        "Hamburger Bovino",
        "Hamburger de Camarao com Pernil Suino",
        "Hamburguer Vegano",
    ],
    "Sobrecoxas": [
        "Sobrecoxa ao Limao",
        "Sobrecoxa ao Tandoori",
        "Sobrecoxa ao Tucupi",
    ],
    "Costelas": [
        "Costela Assada",
        "Costela Cibi Sana",
    ],
    "Carpaccios": [
        "Carpaccio de Laranja",
        "Carpaccio de Pera com Rucula e Amendoas",
    ],
    "Risones": [
        "Risone ao Creme de Limao",
        "Risone ao Pesto",
    ],
    "Ceviches": [
        "Ceviche",
        "Ceviche de Banana da Terra",
        "Ceviche de Manga",
    ],
    "Files de Peixe": [
        "File de Peixe ao Misso",
        "File de Peixe ao Molho Confit",
        "File de Peixe ao Molho de Frutas Secas",
        "File de Peixe ao Molho de Limao",
        "File de Peixe em Manteiga de Tomates",
        "Grelhado dos Pescadores",
    ],
    "Nhoques": [
        "Nhoque Vegano",
        "Nhoque ao Sugo",
        "Gnocchi ao Molho Branco",
    ],
    "Pudins e Doces Cremosos": [
        "Pudim",
        "Pannacotta com Frutas Vermelhas",
        "Manjar de Coco",
        "Tiramisu",
    ],
    "Bolos e Brownies": [
        "Bolo Brownie de Chocolate",
        "Bolo de Gengibre",
        "Frutas ao Ganache de Chocolate",
    ],
    "Guacamoles": [
        "Guacamole",
        "Guacamole com Manga",
    ],
    "Romeus": [
        "Romeu",
        "Romeu e Julieta",
    ],
    "Saladas Compostas": [
        "Salada Mediterranea",
        "Salada Oriental",
        "Salada Tailandesa",
        "Salada de Feijao Branco",
        "Salada de Grao de Bico",
        "Salada de Lentilha",
    ],
    "Maminha ao Molho Mostarda e Cebola": [
        "Maminha ao Molho Mostarda",
    ],
    "Feijoada": [
        "Feijoada",
        "Lentilha com Tofu",
    ],
    "Arrozes Compostos": [
        "Arroz 7 Graos",
        "Arroz Integral com Legumes",
        "Arroz Mar e Campo",
        "Arroz com Brocolis e Amendoas",
        "Baiao de Dois",
    ],
}


def _build_dish_to_family_map():
    """Constroi mapa reverso: nome_do_prato -> nome_da_familia"""
    dish_map = {}
    for family_name, dishes in DISH_FAMILIES.items():
        for dish in dishes:
            dish_map[dish] = family_name
    return dish_map


DISH_TO_FAMILY = _build_dish_to_family_map()


def get_family(dish_name: str):
    """Retorna o nome da familia de um prato, ou None se nao pertence a nenhuma."""
    return DISH_TO_FAMILY.get(dish_name)


def get_family_members(dish_name: str):
    """Retorna a lista de membros da familia de um prato."""
    family = DISH_TO_FAMILY.get(dish_name)
    if family:
        return DISH_FAMILIES[family]
    return []


def detect_family_ambiguity(results: list, raw_gap_threshold: float = 0.03):
    """
    Detecta ambiguidade de familia nos resultados do CLIP.
    
    Args:
        results: Lista de resultados do CLIP search [{dish, score, raw_score, ...}]
        raw_gap_threshold: Gap maximo entre top-1 e top-2 raw scores para considerar ambiguo
        
    Returns:
        dict com:
        - is_ambiguous: bool
        - family_name: str ou None
        - candidates: lista de nomes de pratos candidatos
        - reason: str explicando a ambiguidade
    """
    if len(results) < 2:
        return {"is_ambiguous": False, "family_name": None, "candidates": [], "reason": ""}
    
    top1 = results[0]
    top2 = results[1]
    top1_dish = top1.get("dish", "")
    top2_dish = top2.get("dish", "")
    top1_raw = top1.get("raw_score", 0)
    top2_raw = top2.get("raw_score", 0)
    gap = top1_raw - top2_raw
    
    top1_family = get_family(top1_dish)
    top2_family = get_family(top2_dish)
    
    # CASO 1: Top-1 e Top-2 sao da MESMA familia e gap e pequeno
    if top1_family and top1_family == top2_family and gap < 0.05:
        candidates = []
        for r in results[:5]:
            r_dish = r.get("dish", "")
            if get_family(r_dish) == top1_family and r_dish not in candidates:
                candidates.append(r_dish)
        
        if len(candidates) < 2:
            return {"is_ambiguous": False, "family_name": None, "candidates": [], "reason": ""}
        
        return {
            "is_ambiguous": True,
            "family_name": top1_family,
            "candidates": candidates[:4],
            "reason": f"same_family_close_scores (gap={gap:.3f})"
        }
    
    # CASO 2: Top-1 e Top-2 tem scores muito proximos (qualquer familia)
    if gap < raw_gap_threshold and top1_raw < 0.95:
        candidates = [top1_dish]
        if top2_dish not in candidates:
            candidates.append(top2_dish)
        if len(results) > 2:
            top3 = results[2]
            top3_raw = top3.get("raw_score", 0)
            if top1_raw - top3_raw < 0.06:
                top3_dish = top3.get("dish", "")
                if top3_dish not in candidates:
                    candidates.append(top3_dish)
        
        family_counts = {}
        for c in candidates:
            fam = get_family(c)
            if fam:
                family_counts[fam] = family_counts.get(fam, 0) + 1
        
        family_name = None
        if family_counts:
            best_fam = max(family_counts, key=family_counts.get)
            if family_counts[best_fam] >= len(candidates) / 2:
                family_name = best_fam
        
        return {
            "is_ambiguous": True,
            "family_name": family_name,
            "candidates": candidates[:4],
            "reason": f"very_close_scores (gap={gap:.3f})"
        }
    
    # CASO 3: Top-1 pertence a uma familia e o score nao e altissimo
    if top1_family and top1_raw < 0.95 and gap < 0.05:
        family_members = get_family_members(top1_dish)
        candidates_in_results = []
        for r in results[:5]:
            r_dish = r.get("dish", "")
            if r_dish in family_members:
                candidates_in_results.append(r_dish)
        
        if len(candidates_in_results) >= 2:
            return {
                "is_ambiguous": True,
                "family_name": top1_family,
                "candidates": candidates_in_results[:4],
                "reason": f"family_members_in_results (gap={gap:.3f})"
            }
    
    return {"is_ambiguous": False, "family_name": None, "candidates": [], "reason": ""}
