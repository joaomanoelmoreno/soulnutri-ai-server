"""
SoulNutri - Verdade ou Mito Nutricional (Versão Premium)
Conteúdo sofisticado para público de alto nível cultural
Foco em curiosidades SURPREENDENTES e pouco conhecidas
"""

import random
from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# BANCO DE CONHECIMENTO NUTRICIONAL AVANÇADO
# Curiosidades surpreendentes, cientificamente embasadas
# ═══════════════════════════════════════════════════════════════════════════════

CONHECIMENTO_AVANCADO = {
    # ─────────────────────────────────────────────────────────────────────
    # OVOS - Curiosidades Surpreendentes
    # ─────────────────────────────────────────────────────────────────────
    "ovo": [
        {
            "afirmacao": "A cor da casca do ovo indica seu valor nutricional",
            "resposta": "MITO",
            "explicacao": "A cor depende apenas da raça da galinha. Ovos brancos e marrons têm exatamente o mesmo perfil nutricional. A diferença é puramente genética.",
            "fonte": "USDA - Egg Nutrition Center"
        },
        {
            "afirmacao": "Comer ovo cru aumenta a absorção de proteínas",
            "resposta": "MITO (e risco!)",
            "explicacao": "O corpo absorve apenas 51% da proteína do ovo cru, contra 91% do ovo cozido. A avidina do ovo cru ainda bloqueia a absorção de biotina. Além do risco de Salmonella.",
            "fonte": "Journal of Nutrition, 1998"
        },
        {
            "afirmacao": "O ovo é uma das poucas fontes alimentares de vitamina D",
            "resposta": "VERDADE",
            "explicacao": "Um ovo fornece 6% da vitamina D diária. Galinhas criadas ao sol livre produzem ovos com até 4x mais vitamina D que galinhas de granja fechada.",
            "fonte": "Food Chemistry Journal"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # CAFÉ E BEBIDAS
    # ─────────────────────────────────────────────────────────────────────
    "cafe": [
        {
            "afirmacao": "Café desidrata o corpo",
            "resposta": "MITO",
            "explicacao": "Estudos mostram que até 4 xícaras/dia não causam desidratação. O leve efeito diurético é compensado pelo volume de água do próprio café.",
            "fonte": "PLOS One, 2014"
        },
        {
            "afirmacao": "Café depois do almoço atrapalha a absorção de ferro",
            "resposta": "VERDADE",
            "explicacao": "Os polifenóis do café podem reduzir a absorção de ferro em até 80% se consumido junto à refeição. Espere pelo menos 1 hora após comer.",
            "fonte": "American Journal of Clinical Nutrition"
        }
    ],
    
    "cappuccino": [
        {
            "afirmacao": "Cappuccino tem menos cafeína que café expresso",
            "resposta": "VERDADE",
            "explicacao": "O leite não só dilui a cafeína, como a caseína do leite se liga às moléculas de cafeína, retardando sua absorção. Efeito mais suave e prolongado.",
            "fonte": "European Journal of Clinical Nutrition"
        }
    ],
    
    "chocolate": [
        {
            "afirmacao": "Chocolate causa acne",
            "resposta": "PARCIALMENTE MITO",
            "explicacao": "Estudos não encontram relação direta. O que piora a acne é o açúcar e leite do chocolate ao leite. Chocolate 70%+ cacau pode até beneficiar a pele pelos flavonoides.",
            "fonte": "Journal of the American Academy of Dermatology"
        },
        {
            "afirmacao": "Chocolate amargo melhora a função cognitiva",
            "resposta": "VERDADE",
            "explicacao": "Flavonoides do cacau aumentam o fluxo sanguíneo cerebral em até 8%. Estudos mostram melhora em memória e tempo de reação após consumo regular.",
            "fonte": "Frontiers in Nutrition, 2017"
        },
        {
            "afirmacao": "O chocolate foi usado como moeda pelos Maias",
            "resposta": "VERDADE HISTÓRICA",
            "explicacao": "Sementes de cacau eram tão valiosas que serviam como moeda. Um coelho custava 10 sementes, um escravo 100. Falsificar sementes era crime grave.",
            "fonte": "Smithsonian Institution"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # PROTEÍNAS - Informações Avançadas
    # ─────────────────────────────────────────────────────────────────────
    "frango": [
        {
            "afirmacao": "Frango orgânico tem mais proteína que convencional",
            "resposta": "MITO",
            "explicacao": "O teor proteico é praticamente idêntico. A diferença está no perfil de gorduras (orgânico tem mais ômega-3) e menor resíduo de antibióticos.",
            "fonte": "Poultry Science Journal"
        },
        {
            "afirmacao": "A carne de frango mais perto do osso é mais nutritiva",
            "resposta": "VERDADE",
            "explicacao": "A carne junto ao osso absorve minerais durante o cozimento, especialmente cálcio, fósforo e magnésio. Caldos de osso são particularmente ricos.",
            "fonte": "Food & Nutrition Research"
        }
    ],
    
    "peixe": [
        {
            "afirmacao": "Peixes de água fria têm mais ômega-3",
            "resposta": "VERDADE",
            "explicacao": "Peixes de águas geladas produzem mais gordura insaturada para manter as membranas celulares flexíveis no frio. Salmão do Alasca > Salmão do Chile.",
            "fonte": "Journal of the American Dietetic Association"
        },
        {
            "afirmacao": "Sushi de salmão sempre é salmão de verdade",
            "resposta": "NEM SEMPRE",
            "explicacao": "Estudo da UCLA encontrou que 47% do 'salmão' em restaurantes era na verdade truta ou outros peixes. Mercado de substituição é grande.",
            "fonte": "Conservation Biology, 2017"
        }
    ],
    
    "carne": [
        {
            "afirmacao": "A cor vermelha da carne indica frescor",
            "resposta": "NEM SEMPRE",
            "explicacao": "Supermercados usam embalagens com atmosfera modificada (mais oxigênio) para manter a cor vermelha. Carne marrom pode ser tão fresca quanto a vermelha.",
            "fonte": "Journal of Food Science"
        },
        {
            "afirmacao": "Deixar a carne 'descansar' depois de assar é frescura de chef",
            "resposta": "CIÊNCIA REAL",
            "explicacao": "Durante o descanso, as proteínas relaxam e reabsorvem os sucos. Cortar imediatamente faz perder até 40% dos líquidos. 5-10 minutos fazem diferença.",
            "fonte": "Food Science & Technology"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # CARBOIDRATOS - Curiosidades Científicas
    # ─────────────────────────────────────────────────────────────────────
    "arroz": [
        {
            "afirmacao": "Reaquecer arroz pode ser perigoso",
            "resposta": "VERDADE (com ressalvas)",
            "explicacao": "Arroz contém esporos de Bacillus cereus que sobrevivem ao cozimento. Se deixado em temperatura ambiente por horas, produzem toxinas. Refrigere em até 1 hora.",
            "fonte": "NHS UK - Food Safety"
        },
        {
            "afirmacao": "Arroz parboilizado tem mais nutrientes que o branco",
            "resposta": "VERDADE",
            "explicacao": "O processo de parboilização força vitaminas e minerais da casca para dentro do grão antes da polimento. Tem 80% mais vitaminas B que o branco comum.",
            "fonte": "Journal of Food Composition and Analysis"
        }
    ],
    
    "pao": [
        {
            "afirmacao": "Pão torrado tem menos calorias",
            "resposta": "PRATICAMENTE MITO",
            "explicacao": "A diferença é mínima (~2-3 calorias por fatia). O que muda é o índice glicêmico - pão torrado é digerido um pouco mais lentamente devido à modificação do amido.",
            "fonte": "European Journal of Clinical Nutrition"
        },
        {
            "afirmacao": "Pão de fermentação natural (sourdough) é mais saudável",
            "resposta": "VERDADE",
            "explicacao": "A fermentação lenta reduz fitatos (que bloqueiam minerais), produz ácidos orgânicos benéficos e pode reduzir o índice glicêmico em até 25%.",
            "fonte": "British Journal of Nutrition"
        }
    ],
    
    "batata": [
        {
            "afirmacao": "Batata tem mais potássio que banana",
            "resposta": "VERDADE",
            "explicacao": "Uma batata média tem 926mg de potássio, uma banana média 422mg. A batata é uma das maiores fontes de potássio, mas ninguém fala dela.",
            "fonte": "USDA Nutrient Database"
        },
        {
            "afirmacao": "Batatas verdes são tóxicas",
            "resposta": "VERDADE",
            "explicacao": "A cor verde indica presença de solanina, uma toxina natural. Em grandes quantidades causa náusea e vômito. Sempre descarte partes verdes ou brotadas.",
            "fonte": "Journal of Agricultural and Food Chemistry"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # VEGETAIS E SALADAS
    # ─────────────────────────────────────────────────────────────────────
    "salada": [
        {
            "afirmacao": "Salada com azeite absorve mais vitaminas",
            "resposta": "VERDADE",
            "explicacao": "Vitaminas A, D, E e K são lipossolúveis - precisam de gordura para serem absorvidas. Salada com azeite pode aumentar absorção de carotenoides em até 15x.",
            "fonte": "American Journal of Clinical Nutrition"
        }
    ],
    
    "tomate": [
        {
            "afirmacao": "Tomate cozido é mais nutritivo que cru",
            "resposta": "DEPENDE DO NUTRIENTE",
            "explicacao": "Cozinhar aumenta o licopeno disponível em até 35%, mas reduz vitamina C em 29%. Para máximo benefício, consuma de ambas as formas.",
            "fonte": "Journal of Agricultural and Food Chemistry"
        }
    ],
    
    "cenoura": [
        {
            "afirmacao": "Pilotos da RAF comiam cenoura para enxergar à noite",
            "resposta": "PROPAGANDA DE GUERRA",
            "explicacao": "Os britânicos inventaram essa história para esconder que tinham desenvolvido o radar. A vitamina A ajuda a visão, mas não dá superpoderes.",
            "fonte": "Smithsonian Magazine"
        }
    ],
    
    "espinafre": [
        {
            "afirmacao": "Popeye popularizou o espinafre por seu ferro",
            "resposta": "BASEADO EM ERRO",
            "explicacao": "Um cientista errou a vírgula em 1870, registrando 35mg de ferro em vez de 3.5mg. O erro durou décadas. Espinafre tem ferro, mas não é excepcional.",
            "fonte": "British Medical Journal"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # LEGUMINOSAS
    # ─────────────────────────────────────────────────────────────────────
    "feijao": [
        {
            "afirmacao": "O caldo do feijão é a parte mais nutritiva",
            "resposta": "VERDADE",
            "explicacao": "O caldo contém vitaminas B, ferro e potássio que migraram dos grãos durante o cozimento. Jogar o caldo fora desperdiça até 40% dos nutrientes.",
            "fonte": "Revista de Nutrição (Unicamp)"
        },
        {
            "afirmacao": "Brasil e Índia são os maiores consumidores de feijão",
            "resposta": "VERDADE CULTURAL",
            "explicacao": "O Brasil consome ~16kg/pessoa/ano, a maior média mundial. A combinação arroz+feijão fornece proteína completa equivalente à carne, a custo muito menor.",
            "fonte": "FAO - Food and Agriculture Organization"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # DOCES E SOBREMESAS
    # ─────────────────────────────────────────────────────────────────────
    "bombom": [
        {
            "afirmacao": "Chocolate belga é obrigatoriamente melhor",
            "resposta": "MARKETING",
            "explicacao": "Não há regulamentação especial. O que importa é o teor de cacau e a qualidade dos ingredientes. Chocolates brasileiros premium competem em qualidade.",
            "fonte": "Cocoa Research Centre"
        }
    ],
    
    "acucar": [
        {
            "afirmacao": "Açúcar mascavo é muito mais saudável que refinado",
            "resposta": "EXAGERO",
            "explicacao": "A diferença de minerais é mínima em termos práticos. Para obter benefício significativo do ferro do mascavo, precisaria comer quilos. Ambos são açúcar.",
            "fonte": "Harvard T.H. Chan School of Public Health"
        },
        {
            "afirmacao": "Seu corpo não diferencia açúcar natural do adicionado",
            "resposta": "MOLECULARMENTE VERDADE",
            "explicacao": "Glicose é glicose. A diferença é que frutas vêm com fibras, vitaminas e água, que moderam a absorção. Suco de fruta sem fibra age como refrigerante.",
            "fonte": "Journal of the American Medical Association"
        }
    ],
    
    # ─────────────────────────────────────────────────────────────────────
    # CONHECIMENTO GERAL AVANÇADO
    # ─────────────────────────────────────────────────────────────────────
    "_geral": [
        {
            "afirmacao": "O microbioma intestinal pesa mais que o cérebro",
            "resposta": "VERDADE SURPREENDENTE",
            "explicacao": "Suas bactérias intestinais pesam cerca de 2kg, mais que o cérebro (1.4kg). Elas produzem 95% da serotonina do corpo e influenciam seu humor.",
            "fonte": "Nature Reviews Microbiology"
        },
        {
            "afirmacao": "Alimentos 'naturais' não contêm químicos",
            "resposta": "IMPOSSÍVEL",
            "explicacao": "Tudo é químico. Uma banana contém acetato de isoamila, ácido málico e formaldeído naturalmente. 'Natural' e 'químico' não são opostos.",
            "fonte": "Royal Society of Chemistry"
        },
        {
            "afirmacao": "Nossos ancestrais tinham dieta mais saudável",
            "resposta": "ROMANTIZAÇÃO",
            "explicacao": "Análises de múmias mostram aterosclerose em egípcios antigos. A expectativa de vida baixa não era só por doenças - má nutrição era comum.",
            "fonte": "The Lancet, 2013"
        },
        {
            "afirmacao": "Mastigar mais vezes ajuda a emagrecer",
            "resposta": "VERDADE",
            "explicacao": "Estudo japonês mostrou que mastigar 40x por garfada (vs 15x) reduziu a ingestão calórica em 12%. O cérebro precisa de tempo para registrar saciedade.",
            "fonte": "American Journal of Clinical Nutrition"
        },
        {
            "afirmacao": "A cor do prato influencia quanto você come",
            "resposta": "VERDADE",
            "explicacao": "Pratos vermelhos reduzem o consumo em até 40% (associação com 'pare'). Pratos grandes fazem servir 30% mais. Restaurantes sabem disso.",
            "fonte": "Journal of Consumer Research"
        },
        {
            "afirmacao": "Jejum intermitente funciona por restrição calórica",
            "resposta": "PRINCIPALMENTE SIM",
            "explicacao": "A maioria dos benefícios vem de comer menos no total. Benefícios metabólicos adicionais existem, mas são menores que o marketing sugere.",
            "fonte": "New England Journal of Medicine"
        },
        {
            "afirmacao": "Superalimentos são uma categoria científica",
            "resposta": "TERMO DE MARKETING",
            "explicacao": "Não existe definição científica de 'superalimento'. É termo criado para vender. Todos os vegetais são 'super' quando parte de dieta equilibrada.",
            "fonte": "European Food Information Council"
        },
        {
            "afirmacao": "Seu estômago pode 'encolher' com dieta",
            "resposta": "MITO ANATÔMICO",
            "explicacao": "O estômago é um músculo elástico que retorna ao tamanho original. O que muda é a sensação de saciedade - seu cérebro se adapta a porções menores.",
            "fonte": "British Journal of Surgery"
        }
    ]
}


def buscar_conhecimento_por_ingrediente(ingredientes: List[str]) -> Optional[Dict]:
    """Busca conhecimento relevante baseado nos ingredientes do prato."""
    ingredientes_norm = [i.lower().strip() for i in ingredientes]
    
    for ingrediente in ingredientes_norm:
        for chave, items in CONHECIMENTO_AVANCADO.items():
            if chave != "_geral" and (chave in ingrediente or ingrediente in chave):
                if items:
                    return random.choice(items)
    
    return random.choice(CONHECIMENTO_AVANCADO.get("_geral", []))


def buscar_conhecimento_por_categoria(categoria: str) -> Optional[Dict]:
    """Busca conhecimento baseado na categoria do prato."""
    categoria_norm = categoria.lower().strip()
    
    if "vegano" in categoria_norm or "vegetariano" in categoria_norm:
        opcoes = (
            CONHECIMENTO_AVANCADO.get("feijao", []) +
            CONHECIMENTO_AVANCADO.get("salada", []) +
            CONHECIMENTO_AVANCADO.get("arroz", []) +
            CONHECIMENTO_AVANCADO.get("tomate", [])
        )
    elif "proteína" in categoria_norm or "animal" in categoria_norm:
        opcoes = (
            CONHECIMENTO_AVANCADO.get("carne", []) +
            CONHECIMENTO_AVANCADO.get("frango", []) +
            CONHECIMENTO_AVANCADO.get("peixe", []) +
            CONHECIMENTO_AVANCADO.get("ovo", [])
        )
    else:
        opcoes = CONHECIMENTO_AVANCADO.get("_geral", [])
    
    return random.choice(opcoes) if opcoes else None


def get_mito_verdade(ingredientes: List[str] = None, categoria: str = None) -> Dict:
    """
    Retorna conhecimento nutricional avançado relevante para o prato.
    Prioriza curiosidades surpreendentes e pouco conhecidas.
    """
    resultado = None
    
    if ingredientes:
        resultado = buscar_conhecimento_por_ingrediente(ingredientes)
    
    if not resultado and categoria:
        resultado = buscar_conhecimento_por_categoria(categoria)
    
    if not resultado:
        resultado = random.choice(CONHECIMENTO_AVANCADO.get("_geral", []))
    
    if resultado:
        resposta = resultado.get("resposta", "")
        
        # Determinar emoji e classe CSS
        if resposta in ["MITO", "MITO (e risco!)", "PRATICAMENTE MITO", "MITO ANATÔMICO"]:
            emoji = "❌"
            tipo = "mito"
        elif resposta in ["VERDADE", "VERDADE SURPREENDENTE", "VERDADE HISTÓRICA", "VERDADE CULTURAL", "CIÊNCIA REAL"]:
            emoji = "✅"
            tipo = "verdade"
        else:
            emoji = "⚠️"
            tipo = "parcial"
        
        return {
            "afirmacao": resultado.get("afirmacao"),
            "resposta": resposta,
            "resposta_emoji": emoji,
            "tipo": tipo,
            "explicacao": resultado.get("explicacao"),
            "fonte": resultado.get("fonte")
        }
    
    return None


if __name__ == "__main__":
    print("🧪 Testando Conhecimento Avançado:\n")
    
    # Teste com chocolate
    print("1. Prato com chocolate:")
    result = get_mito_verdade(ingredientes=["chocolate", "leite"])
    if result:
        print(f"   {result['resposta_emoji']} {result['resposta']}")
        print(f"   \"{result['afirmacao']}\"")
        print(f"   → {result['explicacao'][:80]}...")
    print()
    
    # Teste geral
    print("2. Conhecimento geral:")
    result = get_mito_verdade(ingredientes=["algo desconhecido"])
    if result:
        print(f"   {result['resposta_emoji']} {result['resposta']}")
        print(f"   \"{result['afirmacao']}\"")
