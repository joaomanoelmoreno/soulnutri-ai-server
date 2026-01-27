"""
SoulNutri - Atualizador LOCAL de fichas (SEM IA, SEM CRÉDITOS)
Preenche TODOS os campos baseado em REGRAS LOCAIS
"""

import json
import re
from pathlib import Path

DATASET_DIR = Path("/app/datasets/organized")

# ═══════════════════════════════════════════════════════════════════════════════
# BANCO DE DADOS LOCAL COMPLETO
# ═══════════════════════════════════════════════════════════════════════════════

PRATOS_COMPLETOS = {
    # ═══════════════════════════════════════════════════════════════════════════
    # ARROZES
    # ═══════════════════════════════════════════════════════════════════════════
    "arroz branco": {
        "categoria": "vegano",
        "ingredientes": ["arroz branco", "água", "sal", "alho", "óleo"],
        "beneficios": ["Fonte de energia rápida", "Fácil digestão", "Naturalmente sem glúten"],
        "riscos": ["Alto índice glicêmico"],
        "nutricao": {"calorias": "130 kcal", "proteinas": "2.7g", "carboidratos": "28g", "gorduras": "0.3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozimento em água",
        "descricao": "Arroz branco cozido, acompanhamento clássico brasileiro.",
        # Premium
        "indice_glicemico": "alto",
        "tempo_digestao": "1-2 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Feijão", "Proteínas", "Saladas"],
        "evitar_com": ["Outros carboidratos refinados"],
    },
    "arroz integral": {
        "categoria": "vegano",
        "ingredientes": ["arroz integral", "água", "sal"],
        "beneficios": ["Rico em fibras", "Índice glicêmico moderado", "Vitaminas do complexo B", "Maior saciedade"],
        "riscos": ["Pode conter traços de glúten"],
        "nutricao": {"calorias": "111 kcal", "proteinas": "2.6g", "carboidratos": "23g", "gorduras": "0.9g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozimento em água",
        "descricao": "Arroz integral nutritivo, rico em fibras e vitaminas.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Legumes", "Proteínas magras", "Saladas"],
        "evitar_com": ["Frituras"],
    },
    "arroz 7 grãos": {
        "categoria": "vegano",
        "ingredientes": ["arroz", "quinoa", "linhaça", "aveia", "centeio", "cevada", "trigo"],
        "beneficios": ["Alto teor de fibras", "Proteína vegetal completa", "Energia prolongada"],
        "riscos": ["Contém glúten"],
        "nutricao": {"calorias": "140 kcal", "proteinas": "4g", "carboidratos": "26g", "gorduras": "2g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozimento em água",
        "descricao": "Mistura nutritiva de grãos integrais e sementes.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "3-4 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Legumes", "Proteínas"],
        "evitar_com": ["Excesso de gorduras"],
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FEIJÕES
    # ═══════════════════════════════════════════════════════════════════════════
    "feijão": {
        "categoria": "vegano",
        "ingredientes": ["feijão", "água", "sal", "alho", "cebola", "louro"],
        "beneficios": ["Rico em proteína vegetal", "Alto teor de ferro", "Fibras para saciedade"],
        "riscos": ["Pode causar gases intestinais"],
        "nutricao": {"calorias": "77 kcal", "proteinas": "5g", "carboidratos": "14g", "gorduras": "0.5g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozimento lento",
        "descricao": "Feijão cozido, base da alimentação brasileira.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "3-4 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Arroz (proteína completa)", "Couve", "Farofa"],
        "evitar_com": ["Excesso de embutidos"],
    },
    "feijão preto": {
        "categoria": "vegano",
        "ingredientes": ["feijão preto", "água", "sal", "alho", "cebola", "louro"],
        "beneficios": ["Antioxidantes da casca escura", "Rico em ferro", "Proteína vegetal"],
        "riscos": ["Pode causar gases"],
        "nutricao": {"calorias": "77 kcal", "proteinas": "5g", "carboidratos": "14g", "gorduras": "0.5g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozimento lento",
        "descricao": "Feijão preto tradicional, rico em antioxidantes.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "3-4 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Arroz", "Couve", "Laranja (vitamina C ajuda absorção de ferro)"],
        "evitar_com": ["Refrigerantes"],
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BATATAS
    # ═══════════════════════════════════════════════════════════════════════════
    "batata": {
        "categoria": "vegano",
        "ingredientes": ["batata", "sal"],
        "beneficios": ["Fonte de potássio", "Energia sustentada", "Vitamina C"],
        "riscos": ["Alto índice glicêmico se consumida sozinha"],
        "nutricao": {"calorias": "77 kcal", "proteinas": "2g", "carboidratos": "17g", "gorduras": "0.1g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozimento ou assado",
        "descricao": "Batata preparada de forma saudável.",
        "indice_glicemico": "alto",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Proteínas", "Vegetais verdes"],
        "evitar_com": ["Frituras", "Excesso de manteiga"],
    },
    "batata doce": {
        "categoria": "vegano",
        "ingredientes": ["batata doce"],
        "beneficios": ["Índice glicêmico moderado", "Rica em betacaroteno", "Fibras", "Vitamina A"],
        "riscos": ["Consumo excessivo pode elevar glicemia"],
        "nutricao": {"calorias": "86 kcal", "proteinas": "1.6g", "carboidratos": "20g", "gorduras": "0.1g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Assado ou cozido",
        "descricao": "Batata doce nutritiva, ótima para pré-treino.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Pré-treino ou almoço",
        "combina_com": ["Proteínas magras", "Canela"],
        "evitar_com": ["Açúcar adicional"],
    },
    "batata frita": {
        "categoria": "vegano",
        "ingredientes": ["batata", "óleo", "sal"],
        "beneficios": ["Fonte de energia"],
        "riscos": ["Alto teor de gordura", "Calorias elevadas", "Formação de acrilamida na fritura"],
        "nutricao": {"calorias": "312 kcal", "proteinas": "3.4g", "carboidratos": "41g", "gorduras": "15g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Fritura",
        "descricao": "Batata frita crocante. Consumir com moderação.",
        "indice_glicemico": "alto",
        "tempo_digestao": "3-4 horas",
        "melhor_horario": "Ocasionalmente no almoço",
        "combina_com": ["Proteínas grelhadas"],
        "evitar_com": ["Outras frituras", "Refrigerantes"],
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LEGUMES E VERDURAS
    # ═══════════════════════════════════════════════════════════════════════════
    "salada": {
        "categoria": "vegano",
        "ingredientes": ["alface", "tomate", "pepino", "cenoura"],
        "beneficios": ["Baixíssimas calorias", "Rica em fibras", "Vitaminas e minerais", "Hidratação"],
        "riscos": ["Verificar higienização"],
        "nutricao": {"calorias": "20 kcal", "proteinas": "1g", "carboidratos": "4g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Crua",
        "descricao": "Salada fresca e nutritiva.",
        "indice_glicemico": "muito baixo",
        "tempo_digestao": "1-2 horas",
        "melhor_horario": "Qualquer refeição",
        "combina_com": ["Proteínas", "Azeite de oliva", "Limão"],
        "evitar_com": ["Molhos industrializados calóricos"],
    },
    "brócolis": {
        "categoria": "vegano",
        "ingredientes": ["brócolis", "sal", "azeite"],
        "beneficios": ["Sulforafano anticancerígeno", "Rico em vitamina C", "Cálcio vegetal", "Fibras"],
        "riscos": ["Pode causar gases em excesso"],
        "nutricao": {"calorias": "34 kcal", "proteinas": "2.8g", "carboidratos": "7g", "gorduras": "0.4g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Vapor ou refogado",
        "descricao": "Brócolis nutritivo, um dos vegetais mais saudáveis.",
        "indice_glicemico": "muito baixo",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Proteínas", "Alho", "Azeite"],
        "evitar_com": ["Queijos gordurosos em excesso"],
    },
    "abóbora": {
        "categoria": "vegano",
        "ingredientes": ["abóbora", "sal"],
        "beneficios": ["Rica em betacaroteno", "Vitamina A", "Baixas calorias", "Fibras"],
        "riscos": ["Índice glicêmico moderado"],
        "nutricao": {"calorias": "26 kcal", "proteinas": "1g", "carboidratos": "6.5g", "gorduras": "0.1g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozida ou assada",
        "descricao": "Abóbora nutritiva, versátil na cozinha.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Curry", "Gengibre", "Coco"],
        "evitar_com": ["Açúcar em excesso"],
    },
    "curry": {
        "categoria": "vegano",
        "ingredientes": ["legumes", "leite de coco", "curry em pó", "gengibre", "alho", "cebola"],
        "beneficios": ["Cúrcuma anti-inflamatória", "Antioxidantes", "Digestivo"],
        "riscos": ["Pode ser picante para alguns"],
        "nutricao": {"calorias": "90 kcal", "proteinas": "2g", "carboidratos": "12g", "gorduras": "4g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Refogado com especiarias",
        "descricao": "Prato aromático com especiarias indianas e leite de coco.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Arroz", "Naan", "Vegetais"],
        "evitar_com": ["Excesso de pimenta se tiver gastrite"],
    },
    "abóbora ao curry": {
        "categoria": "vegano",
        "ingredientes": ["abóbora", "leite de coco", "curry em pó", "cebola", "alho", "gengibre", "azeite", "sal"],
        "beneficios": ["Rica em betacaroteno", "Cúrcuma anti-inflamatória", "Fibras", "Baixas calorias", "Digestivo"],
        "riscos": ["Pode ser picante para alguns"],
        "nutricao": {"calorias": "90 kcal", "proteinas": "2g", "carboidratos": "12g", "gorduras": "4g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Refogado com especiarias",
        "descricao": "Abóbora cozida em molho cremoso de curry com leite de coco e especiarias.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Arroz", "Pão naan", "Vegetais grelhados"],
        "evitar_com": ["Excesso de pimenta se tiver gastrite"],
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PROTEÍNAS - FRANGO
    # ═══════════════════════════════════════════════════════════════════════════
    "frango": {
        "categoria": "proteína animal",
        "ingredientes": ["frango", "sal", "temperos"],
        "beneficios": ["Proteína magra de alta qualidade", "Rico em vitaminas B", "Baixo teor de gordura"],
        "riscos": ["Verificar procedência", "Evitar pele se em dieta"],
        "nutricao": {"calorias": "165 kcal", "proteinas": "31g", "carboidratos": "0g", "gorduras": "3.6g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhado, assado ou cozido",
        "descricao": "Frango preparado de forma saudável.",
        "indice_glicemico": "zero",
        "tempo_digestao": "3-4 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Saladas", "Legumes", "Arroz integral"],
        "evitar_com": ["Molhos gordurosos", "Frituras"],
    },
    "sobrecoxa": {
        "categoria": "proteína animal",
        "ingredientes": ["sobrecoxa de frango", "sal", "temperos"],
        "beneficios": ["Proteína de qualidade", "Mais suculenta que o peito", "Ferro"],
        "riscos": ["Maior teor de gordura que peito"],
        "nutricao": {"calorias": "190 kcal", "proteinas": "26g", "carboidratos": "0g", "gorduras": "9g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Assado ou grelhado",
        "descricao": "Sobrecoxa de frango suculenta.",
        "indice_glicemico": "zero",
        "tempo_digestao": "3-4 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Saladas", "Legumes assados"],
        "evitar_com": ["Frituras"],
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PROTEÍNAS - PEIXES
    # ═══════════════════════════════════════════════════════════════════════════
    "peixe": {
        "categoria": "proteína animal",
        "ingredientes": ["peixe", "sal", "limão", "ervas"],
        "beneficios": ["Ômega-3 para o coração", "Proteína de fácil digestão", "Vitamina D"],
        "riscos": ["Alérgeno: peixe", "Verificar procedência"],
        "nutricao": {"calorias": "120 kcal", "proteinas": "22g", "carboidratos": "0g", "gorduras": "3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False, "contem_frutos_mar": True},
        "tecnica": "Grelhado, assado ou ao vapor",
        "descricao": "Peixe fresco, fonte de ômega-3.",
        "indice_glicemico": "zero",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Limão", "Legumes", "Arroz"],
        "evitar_com": ["Frituras", "Molhos pesados"],
    },
    "salmão": {
        "categoria": "proteína animal",
        "ingredientes": ["salmão", "sal", "limão", "ervas"],
        "beneficios": ["Alto teor de ômega-3", "Proteína nobre", "Vitamina D", "Antioxidante astaxantina"],
        "riscos": ["Alérgeno: peixe", "Pode conter mercúrio"],
        "nutricao": {"calorias": "208 kcal", "proteinas": "20g", "carboidratos": "0g", "gorduras": "13g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False, "contem_frutos_mar": True},
        "tecnica": "Grelhado ou assado",
        "descricao": "Salmão rico em ômega-3, excelente para saúde cardiovascular.",
        "indice_glicemico": "zero",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Legumes verdes", "Limão", "Aspargos"],
        "evitar_com": ["Frituras", "Molhos cremosos em excesso"],
    },
    "bacalhau": {
        "categoria": "proteína animal",
        "ingredientes": ["bacalhau", "azeite", "batata", "cebola", "alho"],
        "beneficios": ["Proteína magra", "Ômega-3", "Vitaminas B12 e D"],
        "riscos": ["Alérgeno: peixe", "Alto teor de sódio"],
        "nutricao": {"calorias": "150 kcal", "proteinas": "25g", "carboidratos": "0g", "gorduras": "5g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False, "contem_frutos_mar": True},
        "tecnica": "Assado ou refogado",
        "descricao": "Bacalhau tradicional português.",
        "indice_glicemico": "zero",
        "tempo_digestao": "3 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Batatas", "Azeite", "Azeitonas"],
        "evitar_com": ["Excesso de sal adicional"],
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PROTEÍNAS - CARNES
    # ═══════════════════════════════════════════════════════════════════════════
    "carne": {
        "categoria": "proteína animal",
        "ingredientes": ["carne bovina", "sal", "temperos"],
        "beneficios": ["Proteína completa", "Ferro heme de alta absorção", "Vitamina B12", "Zinco"],
        "riscos": ["Consumo excessivo associado a doenças cardiovasculares", "Gordura saturada"],
        "nutricao": {"calorias": "250 kcal", "proteinas": "26g", "carboidratos": "0g", "gorduras": "15g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhado ou assado",
        "descricao": "Carne bovina, fonte de proteína e ferro.",
        "indice_glicemico": "zero",
        "tempo_digestao": "4-5 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Saladas", "Legumes", "Arroz"],
        "evitar_com": ["Outras gorduras", "Frituras"],
    },
    "maminha": {
        "categoria": "proteína animal",
        "ingredientes": ["maminha bovina", "sal grosso", "alho"],
        "beneficios": ["Corte macio", "Rico em proteínas", "Ferro", "Zinco"],
        "riscos": ["Gordura moderada", "Consumir com moderação"],
        "nutricao": {"calorias": "220 kcal", "proteinas": "28g", "carboidratos": "0g", "gorduras": "12g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Assado ou grelhado",
        "descricao": "Maminha bovina macia e saborosa.",
        "indice_glicemico": "zero",
        "tempo_digestao": "4-5 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Farofa", "Vinagrete", "Arroz"],
        "evitar_com": ["Molhos gordurosos"],
    },
    "costela": {
        "categoria": "proteína animal",
        "ingredientes": ["costela bovina", "sal grosso"],
        "beneficios": ["Sabor intenso", "Colágeno", "Proteína"],
        "riscos": ["Alto teor de gordura", "Consumir ocasionalmente"],
        "nutricao": {"calorias": "290 kcal", "proteinas": "24g", "carboidratos": "0g", "gorduras": "21g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Assado lento",
        "descricao": "Costela bovina assada lentamente.",
        "indice_glicemico": "zero",
        "tempo_digestao": "5-6 horas",
        "melhor_horario": "Almoço (ocasionalmente)",
        "combina_com": ["Mandioca", "Farofa", "Vinagrete"],
        "evitar_com": ["Outras gorduras no mesmo dia"],
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FRUTOS DO MAR
    # ═══════════════════════════════════════════════════════════════════════════
    "camarão": {
        "categoria": "proteína animal",
        "ingredientes": ["camarão", "alho", "azeite", "sal"],
        "beneficios": ["Proteína magra", "Selênio antioxidante", "Iodo para tireoide", "Ômega-3"],
        "riscos": ["Alérgeno: crustáceo (risco grave)", "Colesterol elevado"],
        "nutricao": {"calorias": "99 kcal", "proteinas": "24g", "carboidratos": "0.2g", "gorduras": "0.3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False, "contem_frutos_mar": True},
        "tecnica": "Grelhado ou refogado",
        "descricao": "Camarão fresco, rico em proteínas.",
        "indice_glicemico": "zero",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Arroz", "Legumes", "Limão"],
        "evitar_com": ["Excesso de manteiga", "Frituras"],
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MASSAS
    # ═══════════════════════════════════════════════════════════════════════════
    "massa": {
        "categoria": "vegetariano",
        "ingredientes": ["massa de trigo", "molho de tomate", "azeite"],
        "beneficios": ["Fonte de energia", "Carboidratos complexos"],
        "riscos": ["Contém glúten", "Alto índice glicêmico"],
        "nutricao": {"calorias": "131 kcal", "proteinas": "5g", "carboidratos": "25g", "gorduras": "1g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozimento em água",
        "descricao": "Massa italiana tradicional.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Molho de tomate", "Legumes", "Proteínas"],
        "evitar_com": ["Molhos muito gordurosos"],
    },
    "lasanha": {
        "categoria": "vegetariano",
        "ingredientes": ["massa de lasanha", "molho de tomate", "queijo", "presunto", "molho branco"],
        "beneficios": ["Refeição completa", "Cálcio do queijo"],
        "riscos": ["Contém glúten", "Contém lactose", "Alto teor calórico"],
        "nutricao": {"calorias": "180 kcal", "proteinas": "10g", "carboidratos": "18g", "gorduras": "8g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": True, "contem_ovo": True},
        "tecnica": "Assado em forno",
        "descricao": "Lasanha tradicional em camadas.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "3-4 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Salada verde"],
        "evitar_com": ["Outras massas no mesmo dia"],
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SOBREMESAS
    # ═══════════════════════════════════════════════════════════════════════════
    "mousse": {
        "categoria": "vegetariano",
        "ingredientes": ["creme de leite", "leite condensado", "fruta"],
        "beneficios": ["Fonte de cálcio", "Energia rápida"],
        "riscos": ["Alto teor de açúcar", "Contém lactose", "Calórico"],
        "nutricao": {"calorias": "200 kcal", "proteinas": "4g", "carboidratos": "25g", "gorduras": "10g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": True, "contem_ovo": False},
        "tecnica": "Refrigerado",
        "descricao": "Mousse cremoso de frutas.",
        "indice_glicemico": "alto",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Sobremesa ocasional",
        "combina_com": ["Frutas frescas"],
        "evitar_com": ["Outras sobremesas"],
    },
    "pudim": {
        "categoria": "vegetariano",
        "ingredientes": ["leite condensado", "leite", "ovos", "açúcar"],
        "beneficios": ["Fonte de proteína (ovos)", "Cálcio"],
        "riscos": ["Alto teor de açúcar", "Contém lactose", "Contém ovo"],
        "nutricao": {"calorias": "240 kcal", "proteinas": "6g", "carboidratos": "35g", "gorduras": "9g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": True, "contem_ovo": True},
        "tecnica": "Banho-maria",
        "descricao": "Pudim de leite tradicional brasileiro.",
        "indice_glicemico": "alto",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Sobremesa ocasional",
        "combina_com": ["Café"],
        "evitar_com": ["Outras sobremesas no mesmo dia"],
    },
    "bolo": {
        "categoria": "vegetariano",
        "ingredientes": ["farinha de trigo", "açúcar", "ovos", "manteiga", "leite"],
        "beneficios": ["Fonte de energia"],
        "riscos": ["Contém glúten", "Alto teor de açúcar", "Calórico"],
        "nutricao": {"calorias": "260 kcal", "proteinas": "4g", "carboidratos": "40g", "gorduras": "10g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": True, "contem_ovo": True},
        "tecnica": "Assado em forno",
        "descricao": "Bolo caseiro tradicional.",
        "indice_glicemico": "alto",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Lanche da tarde (ocasional)",
        "combina_com": ["Café", "Chá"],
        "evitar_com": ["Outras sobremesas"],
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VEGANOS ESPECÍFICOS
    # ═══════════════════════════════════════════════════════════════════════════
    "vegano": {
        "categoria": "vegano",
        "ingredientes": ["ingredientes 100% vegetais"],
        "beneficios": ["Livre de produtos animais", "Rico em fibras", "Baixo colesterol"],
        "riscos": ["Verificar fonte de B12 e ferro"],
        "nutricao": {"calorias": "~120 kcal", "proteinas": "~5g", "carboidratos": "~20g", "gorduras": "~3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Variada",
        "descricao": "Prato 100% vegetal, sem ingredientes de origem animal.",
        "indice_glicemico": "variável",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Qualquer refeição",
        "combina_com": ["Outros vegetais", "Grãos", "Leguminosas"],
        "evitar_com": ["Produtos animais"],
    },
    "tofu": {
        "categoria": "vegano",
        "ingredientes": ["tofu (soja)", "temperos"],
        "beneficios": ["Proteína vegetal completa", "Cálcio", "Isoflavonas"],
        "riscos": ["Alérgeno: soja"],
        "nutricao": {"calorias": "76 kcal", "proteinas": "8g", "carboidratos": "1.9g", "gorduras": "4.8g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False, "contem_soja": True},
        "tecnica": "Grelhado ou refogado",
        "descricao": "Tofu, proteína vegetal versátil.",
        "indice_glicemico": "muito baixo",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Legumes", "Molho shoyu", "Gengibre"],
        "evitar_com": ["Frituras"],
    },
    "hambúrguer vegano": {
        "categoria": "vegano",
        "ingredientes": ["proteína vegetal", "legumes", "temperos"],
        "beneficios": ["Proteína sem colesterol", "Fibras", "Baixa gordura saturada"],
        "riscos": ["Verificar sódio", "Pode conter glúten"],
        "nutricao": {"calorias": "180 kcal", "proteinas": "15g", "carboidratos": "12g", "gorduras": "8g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhado",
        "descricao": "Hambúrguer 100% vegetal.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Salada", "Pão integral"],
        "evitar_com": ["Molhos industrializados"],
    },
}

# Palavras-chave para matching

    # ═══════════════════════════════════════════════════════════════════════════
    # ADICIONADOS AUTOMATICAMENTE
    # ═══════════════════════════════════════════════════════════════════════════
    "berinjela": {
        "categoria": "vegano",
        "ingredientes": ["berinjela", "azeite", "alho", "sal"],
        "beneficios": ["Baixas calorias", "Rica em fibras", "Antioxidantes"],
        "riscos": ["Pode causar alergia em algumas pessoas"],
        "nutricao": {"calorias": "25 kcal", "proteinas": "1g", "carboidratos": "6g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhada ou assada",
        "descricao": "Berinjela preparada de forma saudável.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Queijo", "Tomate", "Ervas"],
        "evitar_com": ["Frituras em excesso"],
    },
    "abobrinha": {
        "categoria": "vegano",
        "ingredientes": ["abobrinha", "azeite", "sal"],
        "beneficios": ["Muito baixa caloria", "Rica em água", "Vitaminas do complexo B"],
        "riscos": [],
        "nutricao": {"calorias": "17 kcal", "proteinas": "1.2g", "carboidratos": "3g", "gorduras": "0.3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhada ou refogada",
        "descricao": "Abobrinha leve e nutritiva.",
        "indice_glicemico": "muito baixo",
        "tempo_digestao": "1-2 horas",
        "melhor_horario": "Qualquer refeição",
        "combina_com": ["Queijo", "Tomate", "Alho"],
        "evitar_com": [],
    },
    "almôndega": {
        "categoria": "proteína animal",
        "ingredientes": ["carne moída", "cebola", "alho", "ovo", "farinha de rosca"],
        "beneficios": ["Rica em proteínas", "Fonte de ferro"],
        "riscos": ["Contém glúten", "Contém ovo"],
        "nutricao": {"calorias": "220 kcal", "proteinas": "15g", "carboidratos": "10g", "gorduras": "14g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": True},
        "tecnica": "Assada ou frita",
        "descricao": "Almôndegas caseiras saborosas.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "3-4 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Arroz", "Molho de tomate", "Purê"],
        "evitar_com": ["Frituras"],
    },
    "gelatina": {
        "categoria": "vegetariano",
        "ingredientes": ["gelatina", "água", "açúcar"],
        "beneficios": ["Colágeno", "Baixas calorias", "Hidratação"],
        "riscos": ["Alto teor de açúcar", "Contém gelatina animal"],
        "nutricao": {"calorias": "70 kcal", "proteinas": "2g", "carboidratos": "17g", "gorduras": "0g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Refrigerada",
        "descricao": "Sobremesa leve e refrescante.",
        "indice_glicemico": "alto",
        "tempo_digestao": "1 hora",
        "melhor_horario": "Sobremesa",
        "combina_com": ["Frutas"],
        "evitar_com": ["Outras sobremesas"],
    },
    "nhoque": {
        "categoria": "vegetariano",
        "ingredientes": ["batata", "farinha de trigo", "ovo", "sal"],
        "beneficios": ["Fonte de energia", "Carboidratos"],
        "riscos": ["Contém glúten", "Contém ovo"],
        "nutricao": {"calorias": "130 kcal", "proteinas": "3g", "carboidratos": "25g", "gorduras": "2g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": True},
        "tecnica": "Cozido em água",
        "descricao": "Nhoque de batata tradicional italiano.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Molho de tomate", "Molho branco", "Queijo"],
        "evitar_com": ["Molhos muito gordurosos"],
    },
    "gnocchi": {
        "categoria": "vegetariano",
        "ingredientes": ["batata", "farinha de trigo", "ovo", "sal"],
        "beneficios": ["Fonte de energia", "Carboidratos"],
        "riscos": ["Contém glúten", "Contém ovo"],
        "nutricao": {"calorias": "130 kcal", "proteinas": "3g", "carboidratos": "25g", "gorduras": "2g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": True},
        "tecnica": "Cozido em água",
        "descricao": "Gnocchi de batata italiano.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Molho de tomate", "Molho branco", "Gorgonzola"],
        "evitar_com": ["Molhos muito gordurosos"],
    },
    "jiló": {
        "categoria": "vegano",
        "ingredientes": ["jiló", "sal"],
        "beneficios": ["Baixas calorias", "Rico em fibras", "Auxilia digestão"],
        "riscos": ["Sabor amargo pode não agradar todos"],
        "nutricao": {"calorias": "30 kcal", "proteinas": "1g", "carboidratos": "7g", "gorduras": "0.1g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Empanado ou refogado",
        "descricao": "Jiló, vegetal típico brasileiro.",
        "indice_glicemico": "muito baixo",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Arroz", "Feijão", "Carnes"],
        "evitar_com": [],
    },
    "lentilha": {
        "categoria": "vegano",
        "ingredientes": ["lentilha", "água", "sal", "alho", "cebola"],
        "beneficios": ["Alta proteína vegetal", "Rico em ferro", "Fibras"],
        "riscos": ["Pode causar gases"],
        "nutricao": {"calorias": "116 kcal", "proteinas": "9g", "carboidratos": "20g", "gorduras": "0.4g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozida",
        "descricao": "Lentilha nutritiva, símbolo de prosperidade.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "3 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Arroz", "Legumes", "Ervas"],
        "evitar_com": [],
    },
    "farofa": {
        "categoria": "vegano",
        "ingredientes": ["farinha de mandioca", "manteiga", "sal", "cebola"],
        "beneficios": ["Fonte de energia", "Carboidratos"],
        "riscos": ["Calórica se em excesso"],
        "nutricao": {"calorias": "150 kcal", "proteinas": "1g", "carboidratos": "25g", "gorduras": "5g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": True, "contem_ovo": False},
        "tecnica": "Refogada",
        "descricao": "Farofa crocante, acompanhamento brasileiro.",
        "indice_glicemico": "alto",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Feijão", "Churrasco", "Arroz"],
        "evitar_com": ["Outras fontes de carboidrato"],
    },
    "risoto": {
        "categoria": "vegetariano",
        "ingredientes": ["arroz arbóreo", "caldo", "vinho branco", "manteiga", "queijo parmesão"],
        "beneficios": ["Fonte de energia", "Cremoso e nutritivo"],
        "riscos": ["Contém lactose", "Alto teor calórico"],
        "nutricao": {"calorias": "180 kcal", "proteinas": "5g", "carboidratos": "30g", "gorduras": "5g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": True, "contem_ovo": False},
        "tecnica": "Cozimento lento com caldo",
        "descricao": "Risoto cremoso italiano.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Cogumelos", "Vegetais", "Frutos do mar"],
        "evitar_com": ["Outras massas"],
    },
    "quiche": {
        "categoria": "vegetariano",
        "ingredientes": ["massa folhada", "ovos", "creme de leite", "queijo", "recheio variado"],
        "beneficios": ["Proteínas do ovo", "Refeição completa"],
        "riscos": ["Contém glúten", "Contém lactose", "Contém ovo", "Alto teor calórico"],
        "nutricao": {"calorias": "250 kcal", "proteinas": "8g", "carboidratos": "18g", "gorduras": "16g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": True, "contem_ovo": True},
        "tecnica": "Assada em forno",
        "descricao": "Torta salgada francesa cremosa.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "3 horas",
        "melhor_horario": "Almoço ou lanche",
        "combina_com": ["Salada verde"],
        "evitar_com": ["Outras massas"],
    },
    "feijoada": {
        "categoria": "proteína animal",
        "ingredientes": ["feijão preto", "carne seca", "linguiça", "costela", "bacon", "paio"],
        "beneficios": ["Rica em proteínas", "Ferro", "Prato completo"],
        "riscos": ["Alto teor de sódio", "Gordura elevada"],
        "nutricao": {"calorias": "250 kcal", "proteinas": "15g", "carboidratos": "18g", "gorduras": "14g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozimento lento",
        "descricao": "Feijoada tradicional brasileira.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "4-5 horas",
        "melhor_horario": "Almoço (ocasionalmente)",
        "combina_com": ["Arroz", "Couve", "Farofa", "Laranja"],
        "evitar_com": ["Outras carnes gordurosas"],
    },
    "cuscuz": {
        "categoria": "vegano",
        "ingredientes": ["farinha de milho", "água", "sal"],
        "beneficios": ["Fonte de energia", "Sem glúten", "Leve"],
        "riscos": [],
        "nutricao": {"calorias": "120 kcal", "proteinas": "3g", "carboidratos": "25g", "gorduras": "0.5g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Vapor",
        "descricao": "Cuscuz nordestino tradicional.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Café da manhã ou almoço",
        "combina_com": ["Ovo", "Manteiga", "Leite de coco"],
        "evitar_com": [],
    },
    "strogonoff": {
        "categoria": "proteína animal",
        "ingredientes": ["carne ou frango", "creme de leite", "mostarda", "ketchup", "cogumelos"],
        "beneficios": ["Rico em proteínas", "Saboroso"],
        "riscos": ["Contém lactose", "Alto teor calórico"],
        "nutricao": {"calorias": "220 kcal", "proteinas": "18g", "carboidratos": "8g", "gorduras": "14g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": True, "contem_ovo": False},
        "tecnica": "Refogado com creme",
        "descricao": "Strogonoff cremoso e saboroso.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "3-4 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Arroz", "Batata palha"],
        "evitar_com": ["Outras fontes de gordura"],
    },
    "kibe": {
        "categoria": "proteína animal",
        "ingredientes": ["carne moída", "trigo para kibe", "cebola", "hortelã", "especiarias"],
        "beneficios": ["Rico em proteínas", "Ferro"],
        "riscos": ["Contém glúten"],
        "nutricao": {"calorias": "200 kcal", "proteinas": "12g", "carboidratos": "15g", "gorduras": "10g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Assado ou frito",
        "descricao": "Kibe árabe tradicional.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "3 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Coalhada", "Salada", "Tabule"],
        "evitar_com": ["Frituras em excesso"],
    },
    "ratatouille": {
        "categoria": "vegano",
        "ingredientes": ["abobrinha", "berinjela", "tomate", "pimentão", "cebola", "azeite"],
        "beneficios": ["Baixas calorias", "Rico em fibras", "Vitaminas"],
        "riscos": [],
        "nutricao": {"calorias": "50 kcal", "proteinas": "1.5g", "carboidratos": "8g", "gorduras": "2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Assado em forno",
        "descricao": "Prato francês de legumes assados.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Proteínas", "Pão"],
        "evitar_com": [],
    },
    "vinagrete": {
        "categoria": "vegano",
        "ingredientes": ["tomate", "cebola", "pimentão", "vinagre", "azeite", "sal"],
        "beneficios": ["Baixas calorias", "Rico em vitaminas", "Refrescante"],
        "riscos": [],
        "nutricao": {"calorias": "30 kcal", "proteinas": "0.5g", "carboidratos": "5g", "gorduras": "1g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Crua",
        "descricao": "Salsa brasileira refrescante.",
        "indice_glicemico": "muito baixo",
        "tempo_digestao": "1 hora",
        "melhor_horario": "Qualquer refeição",
        "combina_com": ["Churrasco", "Feijão", "Arroz"],
        "evitar_com": [],
    },
    "torresmo": {
        "categoria": "proteína animal",
        "ingredientes": ["pele de porco", "sal"],
        "beneficios": ["Fonte de colágeno"],
        "riscos": ["Muito gorduroso", "Alto teor calórico", "Consumir com moderação"],
        "nutricao": {"calorias": "540 kcal", "proteinas": "25g", "carboidratos": "0g", "gorduras": "48g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Frito",
        "descricao": "Torresmo crocante, petisco brasileiro.",
        "indice_glicemico": "zero",
        "tempo_digestao": "4-5 horas",
        "melhor_horario": "Ocasionalmente",
        "combina_com": ["Cerveja", "Feijão"],
        "evitar_com": ["Outras frituras"],
    },
    "tiramisu": {
        "categoria": "vegetariano",
        "ingredientes": ["mascarpone", "café", "biscoito champagne", "cacau", "ovos"],
        "beneficios": ["Fonte de cálcio", "Energia"],
        "riscos": ["Contém ovo cru", "Contém lactose", "Alto teor calórico"],
        "nutricao": {"calorias": "280 kcal", "proteinas": "5g", "carboidratos": "25g", "gorduras": "18g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": True, "contem_ovo": True},
        "tecnica": "Refrigerado",
        "descricao": "Sobremesa italiana clássica com café.",
        "indice_glicemico": "alto",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Sobremesa",
        "combina_com": ["Café"],
        "evitar_com": ["Outras sobremesas"],
    },
    "cenoura": {
        "categoria": "vegano",
        "ingredientes": ["cenoura", "sal"],
        "beneficios": ["Rica em betacaroteno", "Vitamina A", "Boa para visão"],
        "riscos": [],
        "nutricao": {"calorias": "41 kcal", "proteinas": "0.9g", "carboidratos": "10g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Crua ou cozida",
        "descricao": "Cenoura nutritiva e versátil.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Qualquer refeição",
        "combina_com": ["Saladas", "Sopas", "Legumes"],
        "evitar_com": [],
    },
    "mandioquinha": {
        "categoria": "vegano",
        "ingredientes": ["mandioquinha", "sal"],
        "beneficios": ["Fonte de energia", "Rico em potássio", "Fácil digestão"],
        "riscos": [],
        "nutricao": {"calorias": "90 kcal", "proteinas": "1g", "carboidratos": "21g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozida ou como purê",
        "descricao": "Mandioquinha cremosa e nutritiva.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Carnes", "Purê"],
        "evitar_com": [],
    },
    "quiabo": {
        "categoria": "vegano",
        "ingredientes": ["quiabo", "sal"],
        "beneficios": ["Baixas calorias", "Rico em fibras", "Vitaminas"],
        "riscos": ["Textura pode não agradar todos"],
        "nutricao": {"calorias": "33 kcal", "proteinas": "2g", "carboidratos": "7g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Refogado ou empanado",
        "descricao": "Quiabo, legume típico da culinária brasileira.",
        "indice_glicemico": "muito baixo",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Frango", "Carne"],
        "evitar_com": [],
    },
    "couve-flor": {
        "categoria": "vegano",
        "ingredientes": ["couve-flor", "sal"],
        "beneficios": ["Baixíssimas calorias", "Rica em fibras", "Vitamina C"],
        "riscos": ["Pode causar gases"],
        "nutricao": {"calorias": "25 kcal", "proteinas": "2g", "carboidratos": "5g", "gorduras": "0.3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Gratinada ou cozida",
        "descricao": "Couve-flor versátil e nutritiva.",
        "indice_glicemico": "muito baixo",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Queijo", "Molho branco"],
        "evitar_com": [],
    },
    "linguiça": {
        "categoria": "proteína animal",
        "ingredientes": ["carne suína", "temperos", "tripa natural"],
        "beneficios": ["Rica em proteínas"],
        "riscos": ["Alto teor de sódio", "Gordura elevada"],
        "nutricao": {"calorias": "300 kcal", "proteinas": "15g", "carboidratos": "2g", "gorduras": "26g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhada ou frita",
        "descricao": "Linguiça suína saborosa.",
        "indice_glicemico": "zero",
        "tempo_digestao": "4 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Arroz", "Feijão", "Farofa"],
        "evitar_com": ["Outras carnes gordurosas"],
    },
    "pernil": {
        "categoria": "proteína animal",
        "ingredientes": ["pernil suíno", "alho", "sal", "ervas"],
        "beneficios": ["Rico em proteínas", "Sabor intenso"],
        "riscos": ["Gordura elevada", "Consumir com moderação"],
        "nutricao": {"calorias": "260 kcal", "proteinas": "25g", "carboidratos": "0g", "gorduras": "17g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Assado lento",
        "descricao": "Pernil assado suculento.",
        "indice_glicemico": "zero",
        "tempo_digestao": "4-5 horas",
        "melhor_horario": "Almoço especial",
        "combina_com": ["Arroz", "Farofa", "Salada"],
        "evitar_com": ["Outras carnes gordurosas"],
    },
    "portobello": {
        "categoria": "vegano",
        "ingredientes": ["cogumelo portobello", "azeite", "alho", "ervas"],
        "beneficios": ["Baixas calorias", "Proteína vegetal", "Rico em minerais"],
        "riscos": [],
        "nutricao": {"calorias": "22 kcal", "proteinas": "2g", "carboidratos": "4g", "gorduras": "0.4g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhado ou recheado",
        "descricao": "Cogumelo portobello, substituto de carne.",
        "indice_glicemico": "muito baixo",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Queijo", "Ervas", "Vegetais"],
        "evitar_com": [],
    },
    "quinoa": {
        "categoria": "vegano",
        "ingredientes": ["quinoa", "água", "sal"],
        "beneficios": ["Proteína completa", "Rico em fibras", "Sem glúten"],
        "riscos": [],
        "nutricao": {"calorias": "120 kcal", "proteinas": "4.4g", "carboidratos": "21g", "gorduras": "1.9g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozida",
        "descricao": "Quinoa nutritiva, superalimento.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "2-3 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Legumes", "Saladas"],
        "evitar_com": [],
    },
    "beterraba": {
        "categoria": "vegano",
        "ingredientes": ["beterraba", "sal"],
        "beneficios": ["Rica em ferro", "Antioxidantes", "Melhora circulação"],
        "riscos": ["Pode manchar roupas"],
        "nutricao": {"calorias": "43 kcal", "proteinas": "1.6g", "carboidratos": "10g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozida ou crua",
        "descricao": "Beterraba nutritiva e colorida.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Qualquer refeição",
        "combina_com": ["Saladas", "Sucos"],
        "evitar_com": [],
    },
    "tabule": {
        "categoria": "vegano",
        "ingredientes": ["trigo para quibe", "salsinha", "tomate", "cebola", "limão", "azeite"],
        "beneficios": ["Rico em fibras", "Vitaminas", "Refrescante"],
        "riscos": ["Contém glúten"],
        "nutricao": {"calorias": "90 kcal", "proteinas": "2g", "carboidratos": "15g", "gorduras": "3g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Crua",
        "descricao": "Salada árabe refrescante.",
        "indice_glicemico": "baixo",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Kibe", "Carnes grelhadas"],
        "evitar_com": [],
    },
    "pão de queijo": {
        "categoria": "vegetariano",
        "ingredientes": ["polvilho", "queijo", "ovos", "óleo"],
        "beneficios": ["Sem glúten", "Fonte de cálcio"],
        "riscos": ["Contém lactose", "Contém ovo", "Calórico"],
        "nutricao": {"calorias": "80 kcal", "proteinas": "2g", "carboidratos": "10g", "gorduras": "4g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": True, "contem_ovo": True},
        "tecnica": "Assado",
        "descricao": "Pão de queijo mineiro tradicional.",
        "indice_glicemico": "alto",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Café da manhã ou lanche",
        "combina_com": ["Café", "Suco"],
        "evitar_com": [],
    },
    "guacamole": {
        "categoria": "vegano",
        "ingredientes": ["abacate", "tomate", "cebola", "limão", "coentro", "sal"],
        "beneficios": ["Gorduras boas", "Rico em potássio", "Fibras"],
        "riscos": ["Calórico se em excesso"],
        "nutricao": {"calorias": "150 kcal", "proteinas": "2g", "carboidratos": "8g", "gorduras": "13g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Crua (amassado)",
        "descricao": "Guacamole mexicano cremoso.",
        "indice_glicemico": "muito baixo",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Qualquer refeição",
        "combina_com": ["Nachos", "Tacos", "Saladas"],
        "evitar_com": [],
    },
    "bolinho": {
        "categoria": "vegetariano",
        "ingredientes": ["base variada", "temperos", "óleo para fritar"],
        "beneficios": ["Fonte de energia"],
        "riscos": ["Frito", "Calórico"],
        "nutricao": {"calorias": "180 kcal", "proteinas": "4g", "carboidratos": "20g", "gorduras": "10g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": True},
        "tecnica": "Frito",
        "descricao": "Bolinho crocante e saboroso.",
        "indice_glicemico": "alto",
        "tempo_digestao": "3 horas",
        "melhor_horario": "Entrada ou lanche",
        "combina_com": ["Molhos"],
        "evitar_com": ["Outras frituras"],
    },
    "cogumelo": {
        "categoria": "vegano",
        "ingredientes": ["cogumelos", "azeite", "alho", "sal"],
        "beneficios": ["Baixas calorias", "Proteína vegetal", "Rico em vitamina D"],
        "riscos": [],
        "nutricao": {"calorias": "22 kcal", "proteinas": "3g", "carboidratos": "3g", "gorduras": "0.3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Refogado ou grelhado",
        "descricao": "Cogumelos saborosos e nutritivos.",
        "indice_glicemico": "muito baixo",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Risotos", "Massas", "Carnes"],
        "evitar_com": [],
    },
    "sushi": {
        "categoria": "proteína animal",
        "ingredientes": ["arroz japonês", "peixe cru", "alga nori", "vinagre de arroz"],
        "beneficios": ["Ômega-3", "Proteína magra"],
        "riscos": ["Alérgeno: peixe", "Peixe cru requer cuidado"],
        "nutricao": {"calorias": "150 kcal", "proteinas": "8g", "carboidratos": "25g", "gorduras": "2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False, "contem_frutos_mar": True},
        "tecnica": "Cru enrolado",
        "descricao": "Sushi japonês tradicional.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "2 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Shoyu", "Wasabi", "Gengibre"],
        "evitar_com": [],
    },
    "paella": {
        "categoria": "proteína animal",
        "ingredientes": ["arroz", "frutos do mar", "açafrão", "pimentão", "ervilhas"],
        "beneficios": ["Refeição completa", "Rico em proteínas"],
        "riscos": ["Alérgeno: frutos do mar"],
        "nutricao": {"calorias": "200 kcal", "proteinas": "12g", "carboidratos": "25g", "gorduras": "6g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False, "contem_frutos_mar": True},
        "tecnica": "Cozido em panela larga",
        "descricao": "Paella espanhola com frutos do mar.",
        "indice_glicemico": "moderado",
        "tempo_digestao": "3 horas",
        "melhor_horario": "Almoço",
        "combina_com": ["Salada", "Vinho branco"],
        "evitar_com": [],
    },
    "filé mignon": {
        "categoria": "proteína animal",
        "ingredientes": ["filé mignon", "sal", "pimenta", "manteiga"],
        "beneficios": ["Proteína nobre", "Ferro", "Baixa gordura comparada a outros cortes"],
        "riscos": ["Consumir com moderação"],
        "nutricao": {"calorias": "180 kcal", "proteinas": "26g", "carboidratos": "0g", "gorduras": "8g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhado ou selado",
        "descricao": "Filé mignon macio e suculento.",
        "indice_glicemico": "zero",
        "tempo_digestao": "4 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Arroz", "Salada", "Batatas"],
        "evitar_com": ["Molhos muito gordurosos"],
    },
    "entrecote": {
        "categoria": "proteína animal",
        "ingredientes": ["entrecôte", "sal grosso", "ervas"],
        "beneficios": ["Rico em proteínas", "Ferro", "Sabor intenso"],
        "riscos": ["Gordura moderada"],
        "nutricao": {"calorias": "250 kcal", "proteinas": "25g", "carboidratos": "0g", "gorduras": "16g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhado",
        "descricao": "Entrecôte suculento e saboroso.",
        "indice_glicemico": "zero",
        "tempo_digestao": "4 horas",
        "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Batatas", "Salada", "Chimichurri"],
        "evitar_com": [],
    },

}

PALAVRAS_CHAVE = {
    "arroz": ["arroz", "rice"],
    "arroz branco": ["arroz branco", "white rice"],
    "arroz integral": ["arroz integral", "integral", "brown rice"],
    "arroz 7 grãos": ["7 grãos", "7 graos", "sete grãos", "multigrãos"],
    "feijão": ["feijão", "feijao", "bean"],
    "feijão preto": ["feijão preto", "feijao preto", "black bean"],
    "batata": ["batata", "potato"],
    "batata doce": ["batata doce", "sweet potato"],
    "batata frita": ["batata frita", "frita", "french fries"],
    "salada": ["salada", "salad", "verde"],
    "brócolis": ["brócolis", "brocolis", "broccoli"],
        "berinjela": ["berinjela", "beringela", "eggplant"],
    "abobrinha": ["abobrinha", "zucchini"],
    "almôndega": ["almôndega", "almondega", "meatball"],
    "gelatina": ["gelatina", "jelly"],
    "nhoque": ["nhoque", "gnocchi"],
    "gnocchi": ["gnocchi"],
    "jiló": ["jiló", "jilo"],
    "lentilha": ["lentilha", "lentil"],
    "farofa": ["farofa"],
    "risoto": ["risoto", "risotto"],
    "quiche": ["quiche"],
    "feijoada": ["feijoada"],
    "cuscuz": ["cuscuz", "couscous"],
    "strogonoff": ["strogonoff", "estrogonofe", "stroganoff"],
    "kibe": ["kibe", "quibe"],
    "ratatouille": ["ratatouille"],
    "vinagrete": ["vinagrete"],
    "torresmo": ["torresmo"],
    "tiramisu": ["tiramisu"],
    "cenoura": ["cenoura", "carrot"],
    "mandioquinha": ["mandioquinha", "batata baroa"],
    "quiabo": ["quiabo"],
    "couve-flor": ["couve-flor", "couve flor", "couveflor"],
    "linguiça": ["linguiça", "linguica"],
    "pernil": ["pernil"],
    "portobello": ["portobello"],
    "quinoa": ["quinoa", "quinua"],
    "beterraba": ["beterraba"],
    "tabule": ["tabule", "tabuleh"],
    "pão de queijo": ["pão de queijo", "pao de queijo"],
    "guacamole": ["guacamole"],
    "bolinho": ["bolinho"],
    "cogumelo": ["cogumelo", "cogumelos", "mushroom"],
    "sushi": ["sushi"],
    "paella": ["paella"],
    "filé mignon": ["filé mignon", "file mignon", "mignon"],
    "entrecote": ["entrecote", "entrecôte"],
    "abóbora ao curry": ["abóbora ao curry", "abobora ao curry", "abobora curry"],
    "abóbora": ["abóbora", "abobora", "pumpkin", "squash"],
    "curry": ["curry", "ao curry"],
    "frango": ["frango", "chicken", "galinha"],
    "sobrecoxa": ["sobrecoxa", "coxa"],
    "peixe": ["peixe", "fish", "filé de peixe", "file de peixe"],
    "salmão": ["salmão", "salmao", "salmon"],
    "bacalhau": ["bacalhau", "cod"],
    "carne": ["carne", "bovina", "bife", "beef"],
    "maminha": ["maminha"],
    "costela": ["costela", "costelinha"],
    "camarão": ["camarão", "camarao", "shrimp"],
    "massa": ["massa", "espaguete", "macarrão", "pasta"],
    "lasanha": ["lasanha", "lasagna"],
    "mousse": ["mousse"],
    "pudim": ["pudim", "pudding"],
    "bolo": ["bolo", "cake", "brownie"],
    "vegano": ["vegano", "vegana", "vegan"],
    "tofu": ["tofu"],
    "hambúrguer vegano": ["hambúrguer vegano", "hamburger vegano", "burger vegano"],
}


def encontrar_tipo_prato(nome: str) -> str:
    """Encontra o tipo de prato mais próximo baseado no nome"""
    nome_lower = nome.lower()
    
    # Primeiro tenta match exato
    for tipo, palavras in PALAVRAS_CHAVE.items():
        for palavra in palavras:
            if palavra in nome_lower:
                return tipo
    
    # Fallback para categoria genérica
    if any(p in nome_lower for p in ["frango", "galinha", "chicken"]):
        return "frango"
    if any(p in nome_lower for p in ["peixe", "fish", "tilápia", "atum"]):
        return "peixe"
    if any(p in nome_lower for p in ["carne", "boi", "bovina", "beef"]):
        return "carne"
    if any(p in nome_lower for p in ["vegano", "vegana", "vegan"]):
        return "vegano"
    if any(p in nome_lower for p in ["salada", "alface", "rúcula"]):
        return "salada"
    
    return None


def atualizar_prato_local(slug: str, novo_nome: str = None) -> dict:
    """
    Atualiza um prato LOCALMENTE baseado em regras, SEM chamar IA.
    Preenche TODOS os campos: categoria, ingredientes, benefícios, riscos, etc.
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
    
    # Encontrar tipo de prato
    tipo = encontrar_tipo_prato(nome)
    
    if tipo and tipo in PRATOS_COMPLETOS:
        dados = PRATOS_COMPLETOS[tipo]
        
        # Atualizar todos os campos
        current_info['nome'] = nome
        current_info['slug'] = slug
        current_info['categoria'] = dados['categoria']
        current_info['ingredientes'] = dados['ingredientes']
        current_info['beneficios'] = dados['beneficios']
        current_info['riscos'] = dados['riscos']
        current_info['nutricao'] = dados['nutricao']
        current_info['tecnica'] = dados.get('tecnica', '')
        current_info['descricao'] = dados.get('descricao', '')
        
        # Alérgenos
        for key, value in dados.get('alergenos', {}).items():
            current_info[key] = value
        
        # Campos Premium
        current_info['indice_glicemico'] = dados.get('indice_glicemico', '')
        current_info['tempo_digestao'] = dados.get('tempo_digestao', '')
        current_info['melhor_horario'] = dados.get('melhor_horario', '')
        current_info['combina_com'] = dados.get('combina_com', [])
        current_info['evitar_com'] = dados.get('evitar_com', [])
        
        # Emoji
        if "proteína" in dados['categoria']:
            current_info['category_emoji'] = "🍖"
        elif "vegetariano" in dados['categoria']:
            current_info['category_emoji'] = "🥚"
        else:
            current_info['category_emoji'] = "🌱"
        
        status = f"Atualizado com dados de '{tipo}'"
    else:
        # Não encontrou tipo específico - usar regras básicas
        current_info['nome'] = nome
        current_info['slug'] = slug
        current_info['categoria'] = detectar_categoria_basica(nome)
        
        # Emoji
        if "proteína" in current_info['categoria']:
            current_info['category_emoji'] = "🍖"
        elif "vegetariano" in current_info['categoria']:
            current_info['category_emoji'] = "🥚"
        else:
            current_info['category_emoji'] = "🌱"
        
        status = "Atualizado com regras básicas (tipo não encontrado no banco)"
    
    # Salvar
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(current_info, f, ensure_ascii=False, indent=2)
    
    return {
        "ok": True,
        "slug": slug,
        "nome": nome,
        "tipo_detectado": tipo,
        "categoria": current_info.get('categoria'),
        "status": status,
        "message": "✅ Atualizado LOCALMENTE (sem IA, sem créditos)"
    }


def detectar_categoria_basica(nome: str) -> str:
    """Detecta categoria básica pelo nome"""
    nome_lower = nome.lower()
    
    proteinas = ["frango", "peixe", "carne", "boi", "camarão", "salmão", "atum", 
                 "bacalhau", "costela", "maminha", "filé", "bacon", "linguiça"]
    vegetarianos = ["queijo", "ovo", "leite", "iogurte", "manteiga", "gratinado"]
    
    for p in proteinas:
        if p in nome_lower:
            return "proteína animal"
    
    for v in vegetarianos:
        if v in nome_lower and "vegan" not in nome_lower:
            return "vegetariano"
    
    return "vegano"


def atualizar_todos_por_nome() -> dict:
    """Atualiza TODOS os pratos baseado no nome, SEM IA"""
    resultados = {"atualizados": 0, "erros": [], "total": 0, "por_tipo": {}}
    
    for dish_dir in DATASET_DIR.iterdir():
        if not dish_dir.is_dir():
            continue
        
        resultados["total"] += 1
        slug = dish_dir.name
        
        result = atualizar_prato_local(slug)
        if result.get("ok"):
            resultados["atualizados"] += 1
            tipo = result.get("tipo_detectado", "desconhecido")
            resultados["por_tipo"][tipo] = resultados["por_tipo"].get(tipo, 0) + 1
        else:
            resultados["erros"].append({"slug": slug, "error": result.get("error")})
    
    return resultados
