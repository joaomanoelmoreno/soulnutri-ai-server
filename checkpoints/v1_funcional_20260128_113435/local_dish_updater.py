"""
SoulNutri - Atualizador LOCAL de fichas (SEM IA, SEM CRÉDITOS)
Preenche TODOS os campos baseado em REGRAS LOCAIS
"""

import json
import re
from pathlib import Path

DATASET_DIR = Path("/app/datasets/organized")

# Banco de dados local de pratos
PRATOS_COMPLETOS = {
    "arroz": {
        "categoria": "vegano",
        "ingredientes": ["arroz", "água", "sal", "alho", "óleo"],
        "beneficios": ["Fonte de energia rápida", "Fácil digestão", "Naturalmente sem glúten"],
        "riscos": ["Alto índice glicêmico"],
        "nutricao": {"calorias": "130 kcal", "proteinas": "2.7g", "carboidratos": "28g", "gorduras": "0.3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozimento em água",
        "descricao": "Arroz cozido, acompanhamento clássico brasileiro.",
        "indice_glicemico": "alto", "tempo_digestao": "1-2 horas", "melhor_horario": "Almoço",
        "combina_com": ["Feijão", "Proteínas", "Saladas"], "evitar_com": ["Outros carboidratos refinados"],
    },
    "feijão": {
        "categoria": "vegano",
        "ingredientes": ["feijão", "água", "sal", "alho", "cebola", "louro"],
        "beneficios": ["Rico em proteína vegetal", "Alto teor de ferro", "Fibras para saciedade"],
        "riscos": ["Pode causar gases intestinais"],
        "nutricao": {"calorias": "77 kcal", "proteinas": "5g", "carboidratos": "14g", "gorduras": "0.5g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozimento lento", "descricao": "Feijão cozido, base da alimentação brasileira.",
        "indice_glicemico": "baixo", "tempo_digestao": "3-4 horas", "melhor_horario": "Almoço",
        "combina_com": ["Arroz", "Couve", "Farofa"], "evitar_com": ["Excesso de embutidos"],
    },
    "batata": {
        "categoria": "vegano",
        "ingredientes": ["batata", "sal"],
        "beneficios": ["Fonte de potássio", "Energia sustentada", "Vitamina C"],
        "riscos": ["Alto índice glicêmico se consumida sozinha"],
        "nutricao": {"calorias": "77 kcal", "proteinas": "2g", "carboidratos": "17g", "gorduras": "0.1g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozimento ou assado", "descricao": "Batata preparada de forma saudável.",
        "indice_glicemico": "alto", "tempo_digestao": "2-3 horas", "melhor_horario": "Almoço",
        "combina_com": ["Proteínas", "Vegetais verdes"], "evitar_com": ["Frituras"],
    },
    "salada": {
        "categoria": "vegano",
        "ingredientes": ["alface", "tomate", "pepino", "cenoura"],
        "beneficios": ["Baixíssimas calorias", "Rica em fibras", "Vitaminas e minerais"],
        "riscos": ["Verificar higienização"],
        "nutricao": {"calorias": "20 kcal", "proteinas": "1g", "carboidratos": "4g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Crua", "descricao": "Salada fresca e nutritiva.",
        "indice_glicemico": "muito baixo", "tempo_digestao": "1-2 horas", "melhor_horario": "Qualquer",
        "combina_com": ["Proteínas", "Azeite"], "evitar_com": ["Molhos calóricos"],
    },
    "frango": {
        "categoria": "proteína animal",
        "ingredientes": ["frango", "sal", "temperos"],
        "beneficios": ["Proteína magra de alta qualidade", "Rico em vitaminas B", "Baixo teor de gordura"],
        "riscos": ["Verificar procedência"],
        "nutricao": {"calorias": "165 kcal", "proteinas": "31g", "carboidratos": "0g", "gorduras": "3.6g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhado ou assado", "descricao": "Frango preparado de forma saudável.",
        "indice_glicemico": "zero", "tempo_digestao": "3-4 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Saladas", "Legumes"], "evitar_com": ["Frituras"],
    },
    "peixe": {
        "categoria": "proteína animal",
        "ingredientes": ["peixe", "sal", "limão", "ervas"],
        "beneficios": ["Ômega-3", "Proteína de fácil digestão", "Vitamina D"],
        "riscos": ["Alérgeno: peixe"],
        "nutricao": {"calorias": "120 kcal", "proteinas": "22g", "carboidratos": "0g", "gorduras": "3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False, "contem_frutos_mar": True},
        "tecnica": "Grelhado ou assado", "descricao": "Peixe fresco, fonte de ômega-3.",
        "indice_glicemico": "zero", "tempo_digestao": "2-3 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Limão", "Legumes"], "evitar_com": ["Frituras"],
    },
    "carne": {
        "categoria": "proteína animal",
        "ingredientes": ["carne bovina", "sal", "temperos"],
        "beneficios": ["Proteína completa", "Ferro heme", "Vitamina B12", "Zinco"],
        "riscos": ["Gordura saturada"],
        "nutricao": {"calorias": "250 kcal", "proteinas": "26g", "carboidratos": "0g", "gorduras": "15g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhado ou assado", "descricao": "Carne bovina, fonte de proteína e ferro.",
        "indice_glicemico": "zero", "tempo_digestao": "4-5 horas", "melhor_horario": "Almoço",
        "combina_com": ["Saladas", "Legumes"], "evitar_com": ["Outras gorduras"],
    },
    "berinjela": {
        "categoria": "vegano",
        "ingredientes": ["berinjela", "azeite", "alho", "sal"],
        "beneficios": ["Baixas calorias", "Rica em fibras", "Antioxidantes"],
        "riscos": [],
        "nutricao": {"calorias": "25 kcal", "proteinas": "1g", "carboidratos": "6g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhada ou assada", "descricao": "Berinjela preparada de forma saudável.",
        "indice_glicemico": "baixo", "tempo_digestao": "2 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Queijo", "Tomate"], "evitar_com": [],
    },
    "abobrinha": {
        "categoria": "vegano",
        "ingredientes": ["abobrinha", "azeite", "sal"],
        "beneficios": ["Muito baixa caloria", "Rica em água", "Vitaminas B"],
        "riscos": [],
        "nutricao": {"calorias": "17 kcal", "proteinas": "1.2g", "carboidratos": "3g", "gorduras": "0.3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhada ou refogada", "descricao": "Abobrinha leve e nutritiva.",
        "indice_glicemico": "muito baixo", "tempo_digestao": "1-2 horas", "melhor_horario": "Qualquer",
        "combina_com": ["Queijo", "Tomate"], "evitar_com": [],
    },
    "almôndega": {
        "categoria": "proteína animal",
        "ingredientes": ["carne moída", "cebola", "alho", "ovo", "farinha de rosca"],
        "beneficios": ["Rica em proteínas", "Fonte de ferro"],
        "riscos": ["Contém glúten", "Contém ovo"],
        "nutricao": {"calorias": "220 kcal", "proteinas": "15g", "carboidratos": "10g", "gorduras": "14g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": True},
        "tecnica": "Assada ou frita", "descricao": "Almôndegas caseiras saborosas.",
        "indice_glicemico": "baixo", "tempo_digestao": "3-4 horas", "melhor_horario": "Almoço",
        "combina_com": ["Arroz", "Molho de tomate"], "evitar_com": ["Frituras"],
    },
    "gelatina": {
        "categoria": "vegetariano",
        "ingredientes": ["gelatina", "água", "açúcar"],
        "beneficios": ["Colágeno", "Baixas calorias", "Hidratação"],
        "riscos": ["Alto teor de açúcar"],
        "nutricao": {"calorias": "70 kcal", "proteinas": "2g", "carboidratos": "17g", "gorduras": "0g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Refrigerada", "descricao": "Sobremesa leve e refrescante.",
        "indice_glicemico": "alto", "tempo_digestao": "1 hora", "melhor_horario": "Sobremesa",
        "combina_com": ["Frutas"], "evitar_com": ["Outras sobremesas"],
    },
    "nhoque": {
        "categoria": "vegetariano",
        "ingredientes": ["batata", "farinha de trigo", "ovo", "sal"],
        "beneficios": ["Fonte de energia", "Carboidratos"],
        "riscos": ["Contém glúten", "Contém ovo"],
        "nutricao": {"calorias": "130 kcal", "proteinas": "3g", "carboidratos": "25g", "gorduras": "2g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": True},
        "tecnica": "Cozido em água", "descricao": "Nhoque de batata tradicional italiano.",
        "indice_glicemico": "moderado", "tempo_digestao": "2-3 horas", "melhor_horario": "Almoço",
        "combina_com": ["Molho de tomate", "Queijo"], "evitar_com": ["Molhos gordurosos"],
    },
    "gnocchi": {
        "categoria": "vegetariano",
        "ingredientes": ["batata", "farinha de trigo", "ovo", "sal"],
        "beneficios": ["Fonte de energia", "Carboidratos"],
        "riscos": ["Contém glúten", "Contém ovo"],
        "nutricao": {"calorias": "130 kcal", "proteinas": "3g", "carboidratos": "25g", "gorduras": "2g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": True},
        "tecnica": "Cozido em água", "descricao": "Gnocchi de batata italiano.",
        "indice_glicemico": "moderado", "tempo_digestao": "2-3 horas", "melhor_horario": "Almoço",
        "combina_com": ["Molho de tomate", "Gorgonzola"], "evitar_com": ["Molhos gordurosos"],
    },
    "jiló": {
        "categoria": "vegano",
        "ingredientes": ["jiló", "sal"],
        "beneficios": ["Baixas calorias", "Rico em fibras", "Auxilia digestão"],
        "riscos": ["Sabor amargo"],
        "nutricao": {"calorias": "30 kcal", "proteinas": "1g", "carboidratos": "7g", "gorduras": "0.1g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Empanado ou refogado", "descricao": "Jiló, vegetal típico brasileiro.",
        "indice_glicemico": "muito baixo", "tempo_digestao": "2 horas", "melhor_horario": "Almoço",
        "combina_com": ["Arroz", "Feijão"], "evitar_com": [],
    },
    "lentilha": {
        "categoria": "vegano",
        "ingredientes": ["lentilha", "água", "sal", "alho", "cebola"],
        "beneficios": ["Alta proteína vegetal", "Rico em ferro", "Fibras"],
        "riscos": ["Pode causar gases"],
        "nutricao": {"calorias": "116 kcal", "proteinas": "9g", "carboidratos": "20g", "gorduras": "0.4g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozida", "descricao": "Lentilha nutritiva, símbolo de prosperidade.",
        "indice_glicemico": "baixo", "tempo_digestao": "3 horas", "melhor_horario": "Almoço",
        "combina_com": ["Arroz", "Legumes"], "evitar_com": [],
    },
    "farofa": {
        "categoria": "vegano",
        "ingredientes": ["farinha de mandioca", "manteiga", "sal", "cebola"],
        "beneficios": ["Fonte de energia", "Carboidratos"],
        "riscos": ["Calórica se em excesso"],
        "nutricao": {"calorias": "150 kcal", "proteinas": "1g", "carboidratos": "25g", "gorduras": "5g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": True, "contem_ovo": False},
        "tecnica": "Refogada", "descricao": "Farofa crocante, acompanhamento brasileiro.",
        "indice_glicemico": "alto", "tempo_digestao": "2 horas", "melhor_horario": "Almoço",
        "combina_com": ["Feijão", "Churrasco"], "evitar_com": ["Outros carboidratos"],
    },
    "risoto": {
        "categoria": "vegetariano",
        "ingredientes": ["arroz arbóreo", "caldo", "vinho branco", "manteiga", "queijo parmesão"],
        "beneficios": ["Fonte de energia", "Cremoso e nutritivo"],
        "riscos": ["Contém lactose", "Alto teor calórico"],
        "nutricao": {"calorias": "180 kcal", "proteinas": "5g", "carboidratos": "30g", "gorduras": "5g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": True, "contem_ovo": False},
        "tecnica": "Cozimento lento com caldo", "descricao": "Risoto cremoso italiano.",
        "indice_glicemico": "moderado", "tempo_digestao": "2-3 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Cogumelos", "Vegetais"], "evitar_com": ["Outras massas"],
    },
    "quiche": {
        "categoria": "vegetariano",
        "ingredientes": ["massa folhada", "ovos", "creme de leite", "queijo"],
        "beneficios": ["Proteínas do ovo", "Refeição completa"],
        "riscos": ["Contém glúten", "Contém lactose", "Contém ovo"],
        "nutricao": {"calorias": "250 kcal", "proteinas": "8g", "carboidratos": "18g", "gorduras": "16g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": True, "contem_ovo": True},
        "tecnica": "Assada em forno", "descricao": "Torta salgada francesa cremosa.",
        "indice_glicemico": "moderado", "tempo_digestao": "3 horas", "melhor_horario": "Almoço ou lanche",
        "combina_com": ["Salada verde"], "evitar_com": ["Outras massas"],
    },
    "feijoada": {
        "categoria": "proteína animal",
        "ingredientes": ["feijão preto", "carne seca", "linguiça", "costela", "bacon"],
        "beneficios": ["Rica em proteínas", "Ferro", "Prato completo"],
        "riscos": ["Alto teor de sódio", "Gordura elevada"],
        "nutricao": {"calorias": "250 kcal", "proteinas": "15g", "carboidratos": "18g", "gorduras": "14g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozimento lento", "descricao": "Feijoada tradicional brasileira.",
        "indice_glicemico": "baixo", "tempo_digestao": "4-5 horas", "melhor_horario": "Almoço",
        "combina_com": ["Arroz", "Couve", "Farofa", "Laranja"], "evitar_com": ["Outras carnes gordurosas"],
    },
    "cuscuz": {
        "categoria": "vegano",
        "ingredientes": ["farinha de milho", "água", "sal"],
        "beneficios": ["Fonte de energia", "Sem glúten", "Leve"],
        "riscos": [],
        "nutricao": {"calorias": "120 kcal", "proteinas": "3g", "carboidratos": "25g", "gorduras": "0.5g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Vapor", "descricao": "Cuscuz nordestino tradicional.",
        "indice_glicemico": "moderado", "tempo_digestao": "2 horas", "melhor_horario": "Café ou almoço",
        "combina_com": ["Ovo", "Manteiga"], "evitar_com": [],
    },
    "strogonoff": {
        "categoria": "proteína animal",
        "ingredientes": ["carne ou frango", "creme de leite", "mostarda", "ketchup"],
        "beneficios": ["Rico em proteínas", "Saboroso"],
        "riscos": ["Contém lactose", "Alto teor calórico"],
        "nutricao": {"calorias": "220 kcal", "proteinas": "18g", "carboidratos": "8g", "gorduras": "14g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": True, "contem_ovo": False},
        "tecnica": "Refogado com creme", "descricao": "Strogonoff cremoso e saboroso.",
        "indice_glicemico": "baixo", "tempo_digestao": "3-4 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Arroz", "Batata palha"], "evitar_com": ["Outras gorduras"],
    },
    "kibe": {
        "categoria": "proteína animal",
        "ingredientes": ["carne moída", "trigo para kibe", "cebola", "hortelã"],
        "beneficios": ["Rico em proteínas", "Ferro"],
        "riscos": ["Contém glúten"],
        "nutricao": {"calorias": "200 kcal", "proteinas": "12g", "carboidratos": "15g", "gorduras": "10g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Assado ou frito", "descricao": "Kibe árabe tradicional.",
        "indice_glicemico": "moderado", "tempo_digestao": "3 horas", "melhor_horario": "Almoço",
        "combina_com": ["Coalhada", "Salada"], "evitar_com": ["Frituras"],
    },
    "cenoura": {
        "categoria": "vegano",
        "ingredientes": ["cenoura", "sal"],
        "beneficios": ["Rica em betacaroteno", "Vitamina A", "Boa para visão"],
        "riscos": [],
        "nutricao": {"calorias": "41 kcal", "proteinas": "0.9g", "carboidratos": "10g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Crua ou cozida", "descricao": "Cenoura nutritiva e versátil.",
        "indice_glicemico": "baixo", "tempo_digestao": "2 horas", "melhor_horario": "Qualquer",
        "combina_com": ["Saladas", "Sopas"], "evitar_com": [],
    },
    "mandioquinha": {
        "categoria": "vegano",
        "ingredientes": ["mandioquinha", "sal"],
        "beneficios": ["Fonte de energia", "Rico em potássio", "Fácil digestão"],
        "riscos": [],
        "nutricao": {"calorias": "90 kcal", "proteinas": "1g", "carboidratos": "21g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozida ou como purê", "descricao": "Mandioquinha cremosa e nutritiva.",
        "indice_glicemico": "moderado", "tempo_digestao": "2 horas", "melhor_horario": "Almoço",
        "combina_com": ["Carnes", "Purê"], "evitar_com": [],
    },
    "quiabo": {
        "categoria": "vegano",
        "ingredientes": ["quiabo", "sal"],
        "beneficios": ["Baixas calorias", "Rico em fibras", "Vitaminas"],
        "riscos": ["Textura pode não agradar todos"],
        "nutricao": {"calorias": "33 kcal", "proteinas": "2g", "carboidratos": "7g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Refogado ou empanado", "descricao": "Quiabo, legume típico brasileiro.",
        "indice_glicemico": "muito baixo", "tempo_digestao": "2 horas", "melhor_horario": "Almoço",
        "combina_com": ["Frango", "Carne"], "evitar_com": [],
    },
    "couve-flor": {
        "categoria": "vegano",
        "ingredientes": ["couve-flor", "sal"],
        "beneficios": ["Baixíssimas calorias", "Rica em fibras", "Vitamina C"],
        "riscos": ["Pode causar gases"],
        "nutricao": {"calorias": "25 kcal", "proteinas": "2g", "carboidratos": "5g", "gorduras": "0.3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Gratinada ou cozida", "descricao": "Couve-flor versátil e nutritiva.",
        "indice_glicemico": "muito baixo", "tempo_digestao": "2 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Queijo", "Molho branco"], "evitar_com": [],
    },
    "linguiça": {
        "categoria": "proteína animal",
        "ingredientes": ["carne suína", "temperos"],
        "beneficios": ["Rica em proteínas"],
        "riscos": ["Alto teor de sódio", "Gordura elevada"],
        "nutricao": {"calorias": "300 kcal", "proteinas": "15g", "carboidratos": "2g", "gorduras": "26g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhada ou frita", "descricao": "Linguiça suína saborosa.",
        "indice_glicemico": "zero", "tempo_digestao": "4 horas", "melhor_horario": "Almoço",
        "combina_com": ["Arroz", "Feijão"], "evitar_com": ["Outras carnes gordurosas"],
    },
    "portobello": {
        "categoria": "vegano",
        "ingredientes": ["cogumelo portobello", "azeite", "alho", "ervas"],
        "beneficios": ["Baixas calorias", "Proteína vegetal", "Rico em minerais"],
        "riscos": [],
        "nutricao": {"calorias": "22 kcal", "proteinas": "2g", "carboidratos": "4g", "gorduras": "0.4g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhado ou recheado", "descricao": "Cogumelo portobello, substituto de carne.",
        "indice_glicemico": "muito baixo", "tempo_digestao": "2 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Queijo", "Ervas"], "evitar_com": [],
    },
    "quinoa": {
        "categoria": "vegano",
        "ingredientes": ["quinoa", "água", "sal"],
        "beneficios": ["Proteína completa", "Rico em fibras", "Sem glúten"],
        "riscos": [],
        "nutricao": {"calorias": "120 kcal", "proteinas": "4.4g", "carboidratos": "21g", "gorduras": "1.9g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozida", "descricao": "Quinoa nutritiva, superalimento.",
        "indice_glicemico": "baixo", "tempo_digestao": "2-3 horas", "melhor_horario": "Almoço",
        "combina_com": ["Legumes", "Saladas"], "evitar_com": [],
    },
    "beterraba": {
        "categoria": "vegano",
        "ingredientes": ["beterraba", "sal"],
        "beneficios": ["Rica em ferro", "Antioxidantes", "Melhora circulação"],
        "riscos": [],
        "nutricao": {"calorias": "43 kcal", "proteinas": "1.6g", "carboidratos": "10g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozida ou crua", "descricao": "Beterraba nutritiva e colorida.",
        "indice_glicemico": "moderado", "tempo_digestao": "2 horas", "melhor_horario": "Qualquer",
        "combina_com": ["Saladas", "Sucos"], "evitar_com": [],
    },
    "tabule": {
        "categoria": "vegano",
        "ingredientes": ["trigo para quibe", "salsinha", "tomate", "cebola", "limão"],
        "beneficios": ["Rico em fibras", "Vitaminas", "Refrescante"],
        "riscos": ["Contém glúten"],
        "nutricao": {"calorias": "90 kcal", "proteinas": "2g", "carboidratos": "15g", "gorduras": "3g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Crua", "descricao": "Salada árabe refrescante.",
        "indice_glicemico": "baixo", "tempo_digestao": "2 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Kibe", "Carnes grelhadas"], "evitar_com": [],
    },
    "guacamole": {
        "categoria": "vegano",
        "ingredientes": ["abacate", "tomate", "cebola", "limão", "coentro", "sal"],
        "beneficios": ["Gorduras boas", "Rico em potássio", "Fibras"],
        "riscos": ["Calórico se em excesso"],
        "nutricao": {"calorias": "150 kcal", "proteinas": "2g", "carboidratos": "8g", "gorduras": "13g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Crua", "descricao": "Guacamole mexicano cremoso.",
        "indice_glicemico": "muito baixo", "tempo_digestao": "2 horas", "melhor_horario": "Qualquer",
        "combina_com": ["Nachos", "Tacos"], "evitar_com": [],
    },
    "bolinho": {
        "categoria": "vegetariano",
        "ingredientes": ["base variada", "temperos", "óleo"],
        "beneficios": ["Fonte de energia"],
        "riscos": ["Frito", "Calórico"],
        "nutricao": {"calorias": "180 kcal", "proteinas": "4g", "carboidratos": "20g", "gorduras": "10g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": True},
        "tecnica": "Frito", "descricao": "Bolinho crocante e saboroso.",
        "indice_glicemico": "alto", "tempo_digestao": "3 horas", "melhor_horario": "Entrada ou lanche",
        "combina_com": ["Molhos"], "evitar_com": ["Outras frituras"],
    },
    "cogumelo": {
        "categoria": "vegano",
        "ingredientes": ["cogumelos", "azeite", "alho", "sal"],
        "beneficios": ["Baixas calorias", "Proteína vegetal", "Rico em vitamina D"],
        "riscos": [],
        "nutricao": {"calorias": "22 kcal", "proteinas": "3g", "carboidratos": "3g", "gorduras": "0.3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Refogado ou grelhado", "descricao": "Cogumelos saborosos e nutritivos.",
        "indice_glicemico": "muito baixo", "tempo_digestao": "2 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Risotos", "Massas"], "evitar_com": [],
    },
    "camarão": {
        "categoria": "proteína animal",
        "ingredientes": ["camarão", "alho", "azeite", "sal"],
        "beneficios": ["Proteína magra", "Selênio", "Ômega-3"],
        "riscos": ["Alérgeno: crustáceo"],
        "nutricao": {"calorias": "99 kcal", "proteinas": "24g", "carboidratos": "0.2g", "gorduras": "0.3g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False, "contem_frutos_mar": True},
        "tecnica": "Grelhado ou refogado", "descricao": "Camarão fresco, rico em proteínas.",
        "indice_glicemico": "zero", "tempo_digestao": "2-3 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Arroz", "Legumes"], "evitar_com": ["Excesso de manteiga"],
    },
    "lasanha": {
        "categoria": "vegetariano",
        "ingredientes": ["massa", "molho de tomate", "queijo", "molho branco"],
        "beneficios": ["Refeição completa", "Cálcio"],
        "riscos": ["Contém glúten", "Contém lactose", "Alto teor calórico"],
        "nutricao": {"calorias": "180 kcal", "proteinas": "10g", "carboidratos": "18g", "gorduras": "8g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": True, "contem_ovo": True},
        "tecnica": "Assado em forno", "descricao": "Lasanha tradicional em camadas.",
        "indice_glicemico": "moderado", "tempo_digestao": "3-4 horas", "melhor_horario": "Almoço",
        "combina_com": ["Salada verde"], "evitar_com": ["Outras massas"],
    },
    "pernil": {
        "categoria": "proteína animal",
        "ingredientes": ["pernil suíno", "alho", "sal", "ervas"],
        "beneficios": ["Rico em proteínas", "Sabor intenso"],
        "riscos": ["Gordura elevada"],
        "nutricao": {"calorias": "260 kcal", "proteinas": "25g", "carboidratos": "0g", "gorduras": "17g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Assado lento", "descricao": "Pernil assado suculento.",
        "indice_glicemico": "zero", "tempo_digestao": "4-5 horas", "melhor_horario": "Almoço especial",
        "combina_com": ["Arroz", "Farofa"], "evitar_com": ["Outras carnes gordurosas"],
    },
    "cordeiro": {
        "categoria": "proteína animal",
        "ingredientes": ["carne de cordeiro", "alho", "alecrim", "sal", "azeite"],
        "beneficios": ["Rica em proteínas de alta qualidade", "Excelente fonte de ferro heme", "Rico em vitamina B12", "Zinco biodisponível", "Ômega-3 (carne de pasto)"],
        "riscos": ["Gordura saturada moderada", "Alto teor calórico"],
        "nutricao": {"calorias": "294 kcal", "proteinas": "25g", "carboidratos": "0g", "gorduras": "21g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Assado lento com ervas", "descricao": "Carne de cordeiro macia e aromática, típica da culinária mediterrânea.",
        "indice_glicemico": "zero", "tempo_digestao": "4-5 horas", "melhor_horario": "Almoço especial",
        "combina_com": ["Arroz", "Legumes assados", "Molho de hortelã"], "evitar_com": ["Outras carnes gordurosas"],
    },
    "gnocchi": {
        "categoria": "vegetariano",
        "ingredientes": ["batata", "farinha de trigo", "ovo", "sal", "noz-moscada"],
        "beneficios": ["Fonte de carboidratos", "Energia sustentada", "Conforto"],
        "riscos": ["Contém glúten", "Contém ovo", "Alto índice glicêmico"],
        "nutricao": {"calorias": "135 kcal", "proteinas": "3g", "carboidratos": "28g", "gorduras": "1g"},
        "alergenos": {"contem_gluten": True, "contem_lactose": False, "contem_ovo": True},
        "tecnica": "Cozido em água", "descricao": "Nhoque italiano de batata, leve e macio.",
        "indice_glicemico": "alto", "tempo_digestao": "2-3 horas", "melhor_horario": "Almoço",
        "combina_com": ["Molho de tomate", "Molho branco", "Pesto"], "evitar_com": ["Outras massas"],
    },
    "berinjela": {
        "categoria": "vegano",
        "ingredientes": ["berinjela", "azeite", "alho", "sal"],
        "beneficios": ["Baixíssimas calorias", "Rica em fibras", "Antioxidantes (nasunina)", "Ajuda no controle do colesterol"],
        "riscos": [],
        "nutricao": {"calorias": "25 kcal", "proteinas": "1g", "carboidratos": "6g", "gorduras": "0.2g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhada ou assada", "descricao": "Berinjela versátil, base de muitos pratos mediterrâneos.",
        "indice_glicemico": "muito baixo", "tempo_digestao": "2 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Tomate", "Queijo", "Azeite"], "evitar_com": [],
    },
    "vinagrete": {
        "categoria": "vegano",
        "ingredientes": ["tomate", "cebola", "pimentão", "vinagre", "azeite"],
        "beneficios": ["Baixas calorias", "Rico em vitaminas", "Refrescante"],
        "riscos": [],
        "nutricao": {"calorias": "30 kcal", "proteinas": "0.5g", "carboidratos": "5g", "gorduras": "1g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Crua", "descricao": "Salsa brasileira refrescante.",
        "indice_glicemico": "muito baixo", "tempo_digestao": "1 hora", "melhor_horario": "Qualquer",
        "combina_com": ["Churrasco", "Feijão"], "evitar_com": [],
    },
    "maminha": {
        "categoria": "proteína animal",
        "ingredientes": ["maminha bovina", "sal grosso", "alho"],
        "beneficios": ["Corte macio", "Rico em proteínas", "Ferro"],
        "riscos": ["Gordura moderada"],
        "nutricao": {"calorias": "220 kcal", "proteinas": "28g", "carboidratos": "0g", "gorduras": "12g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Assado ou grelhado", "descricao": "Maminha bovina macia e saborosa.",
        "indice_glicemico": "zero", "tempo_digestao": "4-5 horas", "melhor_horario": "Almoço",
        "combina_com": ["Farofa", "Vinagrete"], "evitar_com": ["Molhos gordurosos"],
    },
    "sobrecoxa": {
        "categoria": "proteína animal",
        "ingredientes": ["sobrecoxa de frango", "sal", "temperos"],
        "beneficios": ["Proteína de qualidade", "Mais suculenta que o peito"],
        "riscos": ["Maior teor de gordura que peito"],
        "nutricao": {"calorias": "190 kcal", "proteinas": "26g", "carboidratos": "0g", "gorduras": "9g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Assado ou grelhado", "descricao": "Sobrecoxa de frango suculenta.",
        "indice_glicemico": "zero", "tempo_digestao": "3-4 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Saladas", "Legumes"], "evitar_com": ["Frituras"],
    },
    "abóbora": {
        "categoria": "vegano",
        "ingredientes": ["abóbora", "sal"],
        "beneficios": ["Rica em betacaroteno", "Vitamina A", "Baixas calorias"],
        "riscos": [],
        "nutricao": {"calorias": "26 kcal", "proteinas": "1g", "carboidratos": "6.5g", "gorduras": "0.1g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Cozida ou assada", "descricao": "Abóbora nutritiva, versátil na cozinha.",
        "indice_glicemico": "moderado", "tempo_digestao": "2 horas", "melhor_horario": "Almoço",
        "combina_com": ["Curry", "Gengibre"], "evitar_com": [],
    },
    "curry": {
        "categoria": "vegano",
        "ingredientes": ["legumes", "leite de coco", "curry em pó", "gengibre"],
        "beneficios": ["Cúrcuma anti-inflamatória", "Antioxidantes"],
        "riscos": ["Pode ser picante"],
        "nutricao": {"calorias": "90 kcal", "proteinas": "2g", "carboidratos": "12g", "gorduras": "4g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Refogado com especiarias", "descricao": "Prato aromático com especiarias indianas.",
        "indice_glicemico": "baixo", "tempo_digestao": "2-3 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Arroz", "Pão naan"], "evitar_com": [],
    },
    "entrecote": {
        "categoria": "proteína animal",
        "ingredientes": ["entrecôte", "sal grosso", "ervas"],
        "beneficios": ["Rico em proteínas", "Ferro", "Sabor intenso"],
        "riscos": ["Gordura moderada"],
        "nutricao": {"calorias": "250 kcal", "proteinas": "25g", "carboidratos": "0g", "gorduras": "16g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhado", "descricao": "Entrecôte suculento e saboroso.",
        "indice_glicemico": "zero", "tempo_digestao": "4 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Batatas", "Salada"], "evitar_com": [],
    },
    "filé mignon": {
        "categoria": "proteína animal",
        "ingredientes": ["filé mignon", "sal", "pimenta", "manteiga"],
        "beneficios": ["Proteína nobre", "Ferro", "Macio"],
        "riscos": [],
        "nutricao": {"calorias": "180 kcal", "proteinas": "26g", "carboidratos": "0g", "gorduras": "8g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": False, "contem_ovo": False},
        "tecnica": "Grelhado ou selado", "descricao": "Filé mignon macio e suculento.",
        "indice_glicemico": "zero", "tempo_digestao": "4 horas", "melhor_horario": "Almoço ou jantar",
        "combina_com": ["Arroz", "Salada"], "evitar_com": [],
    },
    "pão de queijo": {
        "categoria": "vegetariano",
        "ingredientes": ["polvilho", "queijo", "ovos", "óleo"],
        "beneficios": ["Sem glúten", "Fonte de cálcio"],
        "riscos": ["Contém lactose", "Contém ovo"],
        "nutricao": {"calorias": "80 kcal", "proteinas": "2g", "carboidratos": "10g", "gorduras": "4g"},
        "alergenos": {"contem_gluten": False, "contem_lactose": True, "contem_ovo": True},
        "tecnica": "Assado", "descricao": "Pão de queijo mineiro tradicional.",
        "indice_glicemico": "alto", "tempo_digestao": "2 horas", "melhor_horario": "Café ou lanche",
        "combina_com": ["Café", "Suco"], "evitar_com": [],
    },
}

# Palavras-chave para matching
PALAVRAS_CHAVE = {
    "arroz": ["arroz", "rice"],
    "feijão": ["feijão", "feijao", "bean"],
    "batata": ["batata", "potato"],
    "salada": ["salada", "salad"],
    "frango": ["frango", "chicken", "galinha"],
    "peixe": ["peixe", "fish", "tilápia", "atum", "bacalhau", "salmão"],
    "carne": ["carne", "bovina", "bife", "beef"],
    "berinjela": ["berinjela", "beringela", "parmegiana"],
    "abobrinha": ["abobrinha", "zucchini"],
    "almôndega": ["almôndega", "almondega"],
    "gelatina": ["gelatina"],
    "nhoque": ["nhoque"],
    "gnocchi": ["gnocchi"],
    "jiló": ["jiló", "jilo"],
    "lentilha": ["lentilha"],
    "farofa": ["farofa"],
    "risoto": ["risoto", "risotto"],
    "quiche": ["quiche"],
    "feijoada": ["feijoada"],
    "cuscuz": ["cuscuz", "couscous"],
    "strogonoff": ["strogonoff", "estrogonofe", "stroganoff"],
    "kibe": ["kibe", "quibe"],
    "cenoura": ["cenoura"],
    "mandioquinha": ["mandioquinha"],
    "quiabo": ["quiabo"],
    "couve-flor": ["couve-flor", "couve flor", "couveflor", "gratinada"],
    "linguiça": ["linguiça", "linguica", "calabresa"],
    "portobello": ["portobello"],
    "quinoa": ["quinoa", "quinua"],
    "beterraba": ["beterraba"],
    "tabule": ["tabule", "tabuleh"],
    "guacamole": ["guacamole"],
    "bolinho": ["bolinho", "dadinho"],
    "cogumelo": ["cogumelo", "cogumelos", "mushroom"],
    "camarão": ["camarão", "camarao"],
    "lasanha": ["lasanha"],
    "pernil": ["pernil suíno", "pernil suino"],
    "cordeiro": ["cordeiro", "carneiro", "lamb"],
    "gnocchi": ["gnocchi", "nhoque"],
    "berinjela": ["berinjela", "beringela"],
    "vinagrete": ["vinagrete"],
    "maminha": ["maminha"],
    "sobrecoxa": ["sobrecoxa"],
    "abóbora": ["abóbora", "abobora"],
    "curry": ["curry"],
    "entrecote": ["entrecote", "entrecôte"],
    "filé mignon": ["filé mignon", "file mignon", "mignon"],
    "pão de queijo": ["pão de queijo", "pao de queijo"],
}


def encontrar_tipo_prato(nome: str) -> str:
    """Encontra o tipo de prato mais próximo baseado no nome"""
    nome_lower = nome.lower()
    
    for tipo, palavras in PALAVRAS_CHAVE.items():
        for palavra in palavras:
            if palavra in nome_lower:
                return tipo
    
    return None


def atualizar_prato_local(slug: str, novo_nome: str = None, forcar: bool = False) -> dict:
    """
    Atualiza um prato LOCALMENTE baseado em regras, SEM chamar IA.
    
    IMPORTANTE: Só preenche campos VAZIOS, preservando correções manuais!
    Use forcar=True para sobrescrever tudo.
    """
    dish_dir = DATASET_DIR / slug
    if not dish_dir.exists():
        return {"ok": False, "error": "Prato não encontrado"}
    
    info_path = dish_dir / "dish_info.json"
    
    current_info = {}
    if info_path.exists():
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                current_info = json.load(f)
        except:
            pass
    
    nome = novo_nome if novo_nome else current_info.get('nome', slug)
    tipo = encontrar_tipo_prato(nome)
    
    # Função helper para preencher apenas se vazio
    def preencher_se_vazio(campo, valor):
        if forcar:
            current_info[campo] = valor
        elif campo not in current_info or not current_info[campo]:
            current_info[campo] = valor
    
    # Sempre atualizar nome e slug
    current_info['nome'] = nome
    current_info['slug'] = slug
    
    if tipo and tipo in PRATOS_COMPLETOS:
        dados = PRATOS_COMPLETOS[tipo]
        
        # Preencher apenas campos vazios (preserva correções manuais)
        preencher_se_vazio('categoria', dados['categoria'])
        preencher_se_vazio('ingredientes', dados['ingredientes'])
        preencher_se_vazio('beneficios', dados['beneficios'])
        preencher_se_vazio('riscos', dados['riscos'])
        preencher_se_vazio('nutricao', dados['nutricao'])
        preencher_se_vazio('tecnica', dados.get('tecnica', ''))
        preencher_se_vazio('descricao', dados.get('descricao', ''))
        
        # Alérgenos - só preenche se não existir
        for key, value in dados.get('alergenos', {}).items():
            if key not in current_info:
                current_info[key] = value
        
        preencher_se_vazio('indice_glicemico', dados.get('indice_glicemico', ''))
        preencher_se_vazio('tempo_digestao', dados.get('tempo_digestao', ''))
        preencher_se_vazio('melhor_horario', dados.get('melhor_horario', ''))
        preencher_se_vazio('combina_com', dados.get('combina_com', []))
        preencher_se_vazio('evitar_com', dados.get('evitar_com', []))
        
        # Emoji baseado na categoria atual (pode ter sido corrigida manualmente)
        cat = current_info.get('categoria', dados['categoria'])
        if "proteína" in cat:
            current_info['category_emoji'] = "🍖"
        elif "vegetariano" in cat:
            current_info['category_emoji'] = "🥚"
        else:
            current_info['category_emoji'] = "🌱"
        
        status = f"Preenchido campos vazios com dados de '{tipo}'"
    else:
        # Sem tipo no banco - preencher apenas categoria se vazia
        if 'categoria' not in current_info or not current_info['categoria']:
            cat = detectar_categoria_basica(nome)
            current_info['categoria'] = cat
        else:
            cat = current_info['categoria']
        
        # Detectar alérgenos apenas se não existirem
        alergenos = detectar_alergenos_por_nome(nome)
        for key, value in alergenos.items():
            if key not in current_info:
                current_info[key] = value
        
        # NUTRICAO GENÉRICA por categoria (se não tiver)
        if 'nutricao' not in current_info or not current_info.get('nutricao', {}).get('calorias'):
            if "proteína" in cat:
                current_info['nutricao'] = {"calorias": "~180 kcal", "proteinas": "~20g", "carboidratos": "~5g", "gorduras": "~8g"}
            elif "vegetariano" in cat:
                current_info['nutricao'] = {"calorias": "~150 kcal", "proteinas": "~8g", "carboidratos": "~15g", "gorduras": "~6g"}
            else:  # vegano
                current_info['nutricao'] = {"calorias": "~100 kcal", "proteinas": "~4g", "carboidratos": "~18g", "gorduras": "~2g"}
        
        if "proteína" in cat:
            current_info['category_emoji'] = "🍖"
        elif "vegetariano" in cat:
            current_info['category_emoji'] = "🥚"
        else:
            current_info['category_emoji'] = "🌱"
        
        status = "Preenchido campos vazios com regras básicas"
    
    # CORREÇÃO: Se o nome tem "vegano", ajustar categoria e lactose
    nome_lower = nome.lower()
    if "vegano" in nome_lower or "vegana" in nome_lower:
        current_info['categoria'] = "vegano"
        current_info['contem_lactose'] = False
        current_info['category_emoji'] = "🌱"
    
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(current_info, f, ensure_ascii=False, indent=2)
    
    return {
        "ok": True, "slug": slug, "nome": nome, "tipo_detectado": tipo,
        "categoria": current_info.get('categoria'), "status": status,
        "message": "✅ Campos vazios preenchidos (correções manuais preservadas)"
    }


def detectar_categoria_basica(nome: str) -> str:
    """Detecta categoria básica pelo nome, considerando versões veganas"""
    nome_lower = nome.lower()
    
    # PRIMEIRO: Verificar se é explicitamente VEGANO
    # Se tiver "vegano/vegana" no nome, é vegano independente de ter "queijo", "leite" etc
    if "vegano" in nome_lower or "vegana" in nome_lower or "vegan" in nome_lower:
        return "vegano"
    
    # Versões veganas de ingredientes (não são de origem animal)
    versoes_veganas = [
        "queijo vegano", "queijo de castanha", "queijo de caju", "queijo de coco",
        "leite de coco", "leite de amêndoa", "leite de soja", "leite de aveia",
        "leite vegetal", "creme de coco", "cream cheese vegano", "requeijão vegano",
        "maionese vegana", "manteiga vegana", "iogurte vegano", "nata de coco"
    ]
    
    # Se tiver versão vegana no nome, é vegano
    for versao in versoes_veganas:
        if versao in nome_lower:
            return "vegano"
    
    # Proteínas animais
    proteinas = ["frango", "peixe", "carne", "boi", "camarão", "salmão", "atum",
                 "bacalhau", "costela", "maminha", "filé", "bacon", "linguiça", "pernil",
                 "porco", "suíno", "cordeiro", "pato", "peru"]
    
    for p in proteinas:
        if p in nome_lower:
            return "proteína animal"
    
    # Derivados animais (só se NÃO for versão vegana)
    derivados = ["queijo", "ovo", "leite", "iogurte", "manteiga", "gratinado", 
                 "cream cheese", "requeijão", "mussarela", "parmesão"]
    
    for d in derivados:
        if d in nome_lower:
            # Verificar se não é versão vegana
            eh_vegano = False
            for versao in versoes_veganas:
                if versao in nome_lower:
                    eh_vegano = True
                    break
            if not eh_vegano:
                return "vegetariano"
    
    return "vegano"


def detectar_alergenos_por_nome(nome: str) -> dict:
    """Detecta alérgenos pelo nome, considerando versões veganas"""
    nome_lower = nome.lower()
    
    # Versões veganas (não têm lactose)
    versoes_veganas_lactose = [
        "queijo vegano", "leite de coco", "leite de amêndoa", "leite de soja",
        "leite vegetal", "creme de coco", "cream cheese vegano", "requeijão vegano",
        "manteiga vegana", "iogurte vegano", "nata de coco", "vegano", "vegana"
    ]
    
    # Verificar se é versão vegana
    eh_versao_vegana = any(v in nome_lower for v in versoes_veganas_lactose)
    
    # Palavras que indicam lactose (só se não for versão vegana)
    tem_lactose = False
    if not eh_versao_vegana:
        palavras_lactose = ["queijo", "leite", "creme de leite", "manteiga", 
                           "iogurte", "nata", "requeijão", "gratinado"]
        tem_lactose = any(p in nome_lower for p in palavras_lactose)
    
    return {
        "contem_gluten": any(p in nome_lower for p in ["trigo", "farinha", "pão", "massa", "macarrão", "lasanha", "empanado"]) and "arroz" not in nome_lower and "vietnamita" not in nome_lower,
        "contem_lactose": tem_lactose,
        "contem_ovo": any(p in nome_lower for p in ["ovo", "gema", "clara", "maionese"]) and "vegano" not in nome_lower,
        "contem_castanhas": any(p in nome_lower for p in ["castanha", "amêndoa", "nozes", "amendoim"]),
        "contem_frutos_mar": any(p in nome_lower for p in ["camarão", "lagosta", "siri", "lula", "polvo"]),
        "contem_soja": any(p in nome_lower for p in ["soja", "tofu", "shoyu"]),
    }


# =============================================================================
# CONTEÚDO PREMIUM/CIENTÍFICO (informações adicionais para versão Premium)
# =============================================================================
CONTEUDO_PREMIUM = {
    "proteína animal": {
        "beneficio_principal": "Fonte completa de aminoácidos essenciais para manutenção e construção muscular",
        "curiosidade_cientifica": "Proteínas animais têm valor biológico acima de 0.9, enquanto vegetais ficam entre 0.5-0.7",
        "referencia_pesquisa": "Journal of Nutrition (2020)",
        "voce_sabia": "A proteína animal é absorvida 95% pelo corpo, enquanto a vegetal fica entre 70-80%",
        "dica_chef": "Carnes descansadas por 5 minutos após o preparo ficam mais suculentas",
        "mito_verdade": {
            "mito": "Carne vermelha sempre faz mal",
            "verdade": "Cortes magros em porções moderadas (100-150g) são nutritivos"
        }
    },
    "vegano": {
        "beneficio_principal": "Rico em fibras, antioxidantes e fitonutrientes protetores",
        "curiosidade_cientifica": "Dietas ricas em vegetais reduzem em até 30% o risco de doenças cardiovasculares",
        "referencia_pesquisa": "American Journal of Clinical Nutrition (2019)",
        "voce_sabia": "A cor dos vegetais indica seus nutrientes: verde=clorofila, laranja=betacaroteno, roxo=antocianinas",
        "dica_chef": "Vegetais cozidos no vapor por 5-7 min preservam mais nutrientes que fervidos",
        "mito_verdade": {
            "mito": "Vegano não tem proteína",
            "verdade": "Combinações como arroz+feijão fornecem todos os aminoácidos essenciais"
        }
    },
    "vegetariano": {
        "beneficio_principal": "Equilíbrio entre proteínas e nutrientes vegetais",
        "curiosidade_cientifica": "Ovos são considerados padrão-ouro de proteína, com 97% de digestibilidade",
        "referencia_pesquisa": "British Journal of Nutrition (2021)",
        "voce_sabia": "A gema do ovo contém colina, essencial para a memória e função cerebral",
        "dica_chef": "Ovos em temperatura ambiente emulsionam melhor em receitas",
        "mito_verdade": {
            "mito": "Ovo aumenta colesterol",
            "verdade": "Estudos mostram que 1-3 ovos/dia não afetam negativamente pessoas saudáveis"
        }
    },
    "cordeiro": {
        "beneficio_principal": "Uma das melhores fontes de ferro heme e vitamina B12",
        "curiosidade_cientifica": "Cordeiro de pasto tem até 50% mais ômega-3 que o criado em confinamento",
        "referencia_pesquisa": "Meat Science Journal (2018)",
        "voce_sabia": "O cordeiro é a carne mais consumida no mundo, especialmente no Oriente Médio",
        "dica_chef": "Marinar com alecrim e alho por 2h realça o sabor e amacia as fibras",
        "mito_verdade": {
            "mito": "Cordeiro é muito gorduroso",
            "verdade": "Cortes como pernil têm gordura similar ao frango com pele removida"
        },
        "alerta_saude": "Ideal para pessoas com anemia por deficiência de ferro"
    },
    "peixe": {
        "beneficio_principal": "Ômega-3 EPA/DHA para saúde cardiovascular e cerebral",
        "curiosidade_cientifica": "Consumir peixe 2x/semana reduz em 36% o risco de morte por doença cardíaca",
        "referencia_pesquisa": "Circulation Journal (2019)",
        "voce_sabia": "O salmão selvagem tem 3x mais ômega-3 que o de cativeiro",
        "dica_chef": "Peixes brancos ficam mais saborosos grelhados com limão e ervas frescas",
        "mito_verdade": {
            "mito": "Todo peixe tem mercúrio",
            "verdade": "Peixes menores (sardinha, tilápia) têm níveis muito baixos e seguros"
        }
    },
    "arroz": {
        "beneficio_principal": "Energia rápida e glicose para o cérebro",
        "curiosidade_cientifica": "Arroz integral tem 3x mais fibras e mantém mais estável a glicemia",
        "referencia_pesquisa": "Diabetes Care (2020)",
        "voce_sabia": "O arroz alimenta mais de 3,5 bilhões de pessoas diariamente no mundo",
        "dica_chef": "Lavar o arroz até a água sair clara remove o excesso de amido e deixa mais soltinho",
        "mito_verdade": {
            "mito": "Arroz engorda",
            "verdade": "A porção adequada (4-5 colheres) fornece energia sem excesso calórico"
        }
    },
    "feijão": {
        "beneficio_principal": "Combinação única de proteína vegetal + fibras + ferro",
        "curiosidade_cientifica": "Feijão com arroz forma uma proteína completa comparável à carne",
        "referencia_pesquisa": "Food Chemistry (2019)",
        "voce_sabia": "O Brasil é o maior consumidor de feijão do mundo per capita",
        "dica_chef": "Deixar de molho por 8h e trocar a água reduz substâncias que causam gases",
        "mito_verdade": {
            "mito": "Feijão dá gases em todos",
            "verdade": "Deixar de molho e trocar a água reduz 80% dos oligossacarídeos causadores"
        }
    },
    "rolinho": {
        "beneficio_principal": "Refeição leve com vegetais frescos e poucas calorias",
        "curiosidade_cientifica": "A folha de arroz é naturalmente sem glúten e de fácil digestão",
        "referencia_pesquisa": "Food Science & Nutrition (2020)",
        "voce_sabia": "O rolinho vietnamita (gỏi cuốn) é considerado um dos pratos mais saudáveis do mundo",
        "dica_chef": "Molhe a folha de arroz por apenas 2-3 segundos para não rasgar",
        "mito_verdade": {
            "mito": "Comida asiática é sempre gordurosa",
            "verdade": "Rolinhos frescos não são fritos e têm menos de 50 calorias cada"
        }
    },
    "quiche": {
        "beneficio_principal": "Proteína completa do ovo com vegetais",
        "curiosidade_cientifica": "A combinação ovo+queijo fornece cálcio de alta absorção",
        "referencia_pesquisa": "European Journal of Nutrition (2019)",
        "voce_sabia": "A quiche Lorraine original francesa leva apenas bacon, sem queijo",
        "dica_chef": "Pré-assar a massa por 10min evita que fique encharcada",
        "mito_verdade": {
            "mito": "Quiche é muito calórica",
            "verdade": "Uma fatia média (100g) tem cerca de 250 kcal - equivalente a um sanduíche"
        }
    },
    "salada": {
        "beneficio_principal": "Fibras, vitaminas e minerais com mínimas calorias",
        "curiosidade_cientifica": "Folhas verde-escuras têm 10x mais nutrientes que as claras",
        "referencia_pesquisa": "Nutrients Journal (2021)",
        "voce_sabia": "Comer salada antes da refeição principal reduz a absorção de gorduras em até 20%",
        "dica_chef": "Tempere a salada apenas na hora de servir para manter as folhas crocantes",
        "mito_verdade": {
            "mito": "Salada não sustenta",
            "verdade": "Com proteína (ovo, frango, grão-de-bico), a salada é uma refeição completa"
        }
    },
    "massa": {
        "beneficio_principal": "Carboidrato de energia sustentada para atividades físicas",
        "curiosidade_cientifica": "Massa al dente tem índice glicêmico 30% menor que a muito cozida",
        "referencia_pesquisa": "Journal of Cereal Science (2020)",
        "voce_sabia": "A Itália tem mais de 300 formatos diferentes de massa",
        "dica_chef": "Guarde 1 xícara da água do cozimento para engrossar o molho naturalmente",
        "mito_verdade": {
            "mito": "Massa engorda",
            "verdade": "A porção italiana tradicional é 80g (seco) - o problema é o excesso"
        }
    },
    "sobremesa": {
        "beneficio_principal": "Satisfação sensorial e energia rápida em pequenas porções",
        "curiosidade_cientifica": "O chocolate amargo (70%+) tem flavonoides que protegem o coração",
        "referencia_pesquisa": "Frontiers in Nutrition (2020)",
        "voce_sabia": "Uma sobremesa pequena após a refeição ajuda na saciedade e evita beliscar depois",
        "dica_chef": "Sobremesas com frutas frescas são mais leves e igualmente satisfatórias",
        "mito_verdade": {
            "mito": "Tem que cortar sobremesa para emagrecer",
            "verdade": "Porções pequenas (50-100g) cabem em qualquer dieta equilibrada"
        }
    }
}

def obter_conteudo_premium(categoria: str, tipo_prato: str = None) -> dict:
    """Retorna conteúdo Premium baseado na categoria ou tipo específico"""
    # Primeiro tenta tipo específico (ex: cordeiro, peixe)
    if tipo_prato and tipo_prato in CONTEUDO_PREMIUM:
        return CONTEUDO_PREMIUM[tipo_prato]
    
    # Depois tenta pela categoria
    if categoria in CONTEUDO_PREMIUM:
        return CONTEUDO_PREMIUM[categoria]
    
    # Fallback genérico
    return {
        "beneficio_principal": "Contribui para uma alimentação equilibrada",
        "curiosidade_cientifica": "Uma dieta variada é a melhor forma de obter todos os nutrientes",
        "referencia_pesquisa": "OMS - Diretrizes Nutricionais",
        "voce_sabia": "Comer devagar aumenta a saciedade e melhora a digestão",
        "dica_chef": "Temperos frescos realçam o sabor sem adicionar sódio",
        "mito_verdade": None
    }


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
            tipo = result.get("tipo_detectado", "null")
            resultados["por_tipo"][tipo] = resultados["por_tipo"].get(tipo, 0) + 1
        else:
            resultados["erros"].append({"slug": slug, "error": result.get("error")})
    
    return resultados
