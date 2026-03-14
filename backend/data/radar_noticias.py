# -*- coding: utf-8 -*-
"""
RADAR DE NOTÍCIAS EXPANDIDO - Fatos relevantes e balanceados
SoulNutri - Informação em tempo real com credibilidade

Conteúdo balanceado: benefícios + alertas de saúde pública
Fontes: ANVISA, FDA, OMS, Harvard Health, periódicos científicos

ZERO CRÉDITOS DE IA - 100% LOCAL
"""

# Base de dados expandida de fatos sobre alimentos
FATOS_ALIMENTOS = {
    # ═══════════════════════════════════════════════════════════════
    # PEIXES - Benefícios e alertas sobre contaminantes
    # ═══════════════════════════════════════════════════════════════
    "salmao": {
        "fatos": [
            {
                "titulo": "Ômega-3: Proteção Cardiovascular Comprovada",
                "resumo": "Estudos com 40.000 participantes confirmam: 2 porções semanais de salmão reduzem risco de infarto em 25% e melhoram cognição",
                "fonte": "American Heart Association 2024",
                "tipo": "beneficio",
                "data": "2025"
            },
            {
                "titulo": "Salmão de Cativeiro: Atenção à Procedência",
                "resumo": "Salmão de criação pode conter corantes artificiais (astaxantina sintética), resíduos de antibióticos e até 7x mais gordura. Prefira salmão selvagem ou de produtores certificados (ASC/MSC)",
                "fonte": "Environmental Working Group / ANVISA",
                "tipo": "alerta",
                "data": "2025"
            },
            {
                "titulo": "Salmão Selvagem: Opção Mais Nutritiva",
                "resumo": "Salmão selvagem tem até 3x mais ômega-3, menos gordura saturada e cor natural (sem corantes). Se possível, escolha Sockeye ou Coho do Pacífico",
                "fonte": "USDA / Marine Stewardship Council",
                "tipo": "dica",
                "data": "2025"
            },
            {
                "titulo": "Você sabia? DHA e Memória",
                "resumo": "O DHA do salmão é componente estrutural do cérebro. Consumo regular melhora memória e pode reduzir risco de Alzheimer",
                "fonte": "Journal of Neuroscience",
                "tipo": "curiosidade",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": ["Salmão + limão = absorção de ferro aumentada em 3x", "Salmão + vegetais verdes = absorção de ômega-3 otimizada"],
        "voce_sabia": "O salmão de cativeiro recebe corante na ração para ficar rosado - naturalmente ele seria cinza. O selvagem tem cor natural de carotenoides da dieta marinha",
        "dica_rapida": "Prefira salmão selvagem ou certificado ASC/MSC - evite de cativeiro sem procedência",
        "emoji": "🐟"
    },
    
    "bacalhau": {
        "fatos": [
            {
                "titulo": "Atenção ao Sódio",
                "resumo": "Bacalhau salgado pode ter 1800mg de sódio por 100g (75% do limite diário). Dessalgue bem: 24-48h em água trocada",
                "fonte": "ANVISA - Tabela TACO",
                "tipo": "alerta",
                "data": "2025"
            },
            {
                "titulo": "Proteína de Alta Qualidade",
                "resumo": "29g de proteína com apenas 1.5g de gordura por 100g - uma das melhores relações proteína/gordura entre peixes",
                "fonte": "UNICAMP/NEPA",
                "tipo": "beneficio",
                "data": "2025"
            }
        ],
        "combinacoes_beneficas": ["Bacalhau + batatas = refeição completa e balanceada"],
        "voce_sabia": "O bacalhau não é uma espécie, mas sim um método de conservação aplicado a vários peixes (gadus morhua é o mais comum)",
        "dica_rapida": "Alto sódio - dessalgue bem antes de consumir",
        "emoji": "🐟"
    },
    
    "atum": {
        "fatos": [
            {
                "titulo": "Mercúrio: Atenção ao Consumo Frequente",
                "resumo": "Atum (especialmente albacora) acumula mercúrio. FDA recomenda máximo de 1 porção/semana para adultos, menos para gestantes",
                "fonte": "FDA - Mercury Levels in Fish",
                "tipo": "alerta",
                "data": "2025"
            },
            {
                "titulo": "Excelente Fonte de Selênio",
                "resumo": "O selênio do atum ajuda a neutralizar parte do mercúrio e é essencial para tireoide e sistema imune",
                "fonte": "Harvard Health",
                "tipo": "beneficio",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": ["Atum + verduras = selênio protege células dos radicais livres"],
        "voce_sabia": "Atum light (skipjack) tem 3x menos mercúrio que atum branco (albacora)",
        "dica_rapida": "Moderar consumo por mercúrio - preferir atum light",
        "emoji": "🐟"
    },
    
    "peixe": {
        "fatos": [
            {
                "titulo": "Ômega-3: Proteção Cardiovascular",
                "resumo": "Peixes são a principal fonte de ômega-3 EPA e DHA, que reduzem inflamação e protegem o coração. 2 porções semanais são recomendadas",
                "fonte": "American Heart Association",
                "tipo": "beneficio",
                "data": "2025"
            },
            {
                "titulo": "Proteína de Alta Qualidade",
                "resumo": "Peixe fornece proteína completa de fácil digestão, ideal para refeições leves e nutritivas",
                "fonte": "Harvard Health",
                "tipo": "beneficio",
                "data": "2025"
            }
        ],
        "combinacoes_beneficas": ["Peixe + limão = vitamina C aumenta absorção de ferro", "Peixe + vegetais = refeição equilibrada e leve"],
        "voce_sabia": "Peixes de água fria (salmão, sardinha) têm mais ômega-3 que os de água quente (tilápia)",
        "dica_rapida": "Excelente fonte de ômega-3 e proteína magra",
        "emoji": "🐟"
    },
    
    "limao": {
        "fatos": [
            {
                "titulo": "Vitamina C Poderosa",
                "resumo": "Limão contém 53mg de vitamina C por 100g - antioxidante que fortalece imunidade e melhora absorção de ferro",
                "fonte": "USDA Nutrient Database",
                "tipo": "beneficio",
                "data": "2025"
            },
            {
                "titulo": "Potencializa Nutrientes",
                "resumo": "Adicionar limão ao peixe ou carnes aumenta em até 3x a absorção do ferro não-heme presente nos alimentos",
                "fonte": "Journal of Nutrition",
                "tipo": "beneficio",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": ["Limão + peixe = combina perfeitamente e potencializa absorção de nutrientes", "Limão + ferro = absorção triplicada"],
        "voce_sabia": "O ácido cítrico do limão pode ajudar na digestão de proteínas e gorduras",
        "dica_rapida": "Vitamina C natural - potencializa absorção de ferro",
        "emoji": "🍋"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # CARNES - Foco em processados e qualidade
    # ═══════════════════════════════════════════════════════════════
    "carne_bovina": {
        "fatos": [
            {
                "titulo": "Ferro Heme: 3x Mais Absorvido",
                "resumo": "O ferro da carne vermelha (ferro heme) é absorvido 3x mais que o ferro vegetal (não-heme). O ferro heme está ligado à hemoglobina/mioglobina, sendo absorvido diretamente. Essencial para prevenir anemia",
                "fonte": "American Journal of Clinical Nutrition",
                "tipo": "beneficio",
                "data": "2025"
            },
            {
                "titulo": "O que é Ferro Heme?",
                "resumo": "Ferro Heme = ferro de origem animal (carnes, vísceras, sangue). É absorvido em 15-35% pelo corpo. Ferro Não-Heme = ferro de vegetais (feijão, espinafre). Absorvido em apenas 2-20%. Por isso carnes são mais eficientes para combater anemia",
                "fonte": "NIH - Office of Dietary Supplements",
                "tipo": "explicacao",
                "data": "2025"
            },
            {
                "titulo": "B12 Natural Essencial",
                "resumo": "Carne bovina é a melhor fonte natural de vitamina B12 - nutriente crítico que vegetarianos/veganos precisam suplementar",
                "fonte": "Harvard Health",
                "tipo": "beneficio",
                "data": "2024"
            },
            {
                "titulo": "Consumo Moderado Recomendado",
                "resumo": "OMS recomenda máximo 500g de carne vermelha/semana. Estudos associam consumo excessivo a risco cardiovascular",
                "fonte": "OMS - IARC 2024",
                "tipo": "moderacao",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": ["Carne + vitamina C (limão/laranja) = absorção de ferro maximizada", "Carne + salada = fibras ajudam na digestão"],
        "voce_sabia": "A cor vermelha da carne não indica frescor - é a mioglobina, proteína que transporta oxigênio nos músculos. O ferro heme está presente nessa mioglobina",
        "dica_rapida": "Excelente fonte de ferro heme (absorção 3x maior) e B12 - consumo moderado",
        "emoji": "🥩"
    },
    
    "bacon": {
        "fatos": [
            {
                "titulo": "Carnes Processadas: Grupo 1 Carcinogênico (OMS)",
                "resumo": "Em 2015, OMS classificou carnes processadas (bacon, salsicha, presunto) como carcinogênicas. 50g/dia aumenta risco de câncer colorretal em 18%",
                "fonte": "OMS/IARC - Monografia 114",
                "tipo": "alerta",
                "data": "2024"
            },
            {
                "titulo": "Sódio e Nitritos",
                "resumo": "Uma fatia de bacon (8g) tem ~135mg de sódio. Nitritos usados na cura podem formar nitrosaminas (carcinogênicas) em altas temperaturas",
                "fonte": "ANVISA",
                "tipo": "alerta",
                "data": "2025"
            }
        ],
        "combinacoes_beneficas": [],
        "voce_sabia": "Bacon 'não curado' ainda usa nitratos de fontes naturais (aipo) - o efeito é similar",
        "dica_rapida": "Consumo ocasional - evitar frequente por classificação OMS",
        "emoji": "🥓"
    },
    
    "linguica": {
        "fatos": [
            {
                "titulo": "Embutidos: Risco Classificado pela OMS",
                "resumo": "Linguiças, salsichas e embutidos estão no Grupo 1 de carcinogênicos da OMS junto com cigarro (não significa mesmo risco, mas mesma certeza)",
                "fonte": "OMS/IARC",
                "tipo": "alerta",
                "data": "2024"
            },
            {
                "titulo": "Alto Teor de Sódio",
                "resumo": "100g de linguiça = 870mg de sódio (36% do limite diário). Hipertensos devem evitar",
                "fonte": "ANVISA - Tabela TACO",
                "tipo": "alerta",
                "data": "2025"
            }
        ],
        "combinacoes_beneficas": [],
        "voce_sabia": "Linguiças artesanais sem conservantes são opção mais saudável, mas ainda são carnes processadas",
        "dica_rapida": "Consumo ocasional - alto sódio e classificação OMS",
        "emoji": "🌭"
    },
    
    "salsicha": {
        "fatos": [
            {
                "titulo": "Processamento Industrial",
                "resumo": "Salsichas comerciais podem conter até 30% de partes não-carne (pele, cartilagem, gordura). Verifique lista de ingredientes",
                "fonte": "ANVISA - Regulamento Técnico",
                "tipo": "alerta",
                "data": "2025"
            },
            {
                "titulo": "Aditivos Químicos",
                "resumo": "Nitritos (E250), fosfatos, glutamato monossódico são comuns. Nitritos em excesso podem formar compostos carcinogênicos",
                "fonte": "EFSA - European Food Safety",
                "tipo": "alerta",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": [],
        "voce_sabia": "Salsichas 'de frango' muitas vezes têm menos proteína e mais gordura que as convencionais",
        "dica_rapida": "Verificar ingredientes - preferir sem nitritos",
        "emoji": "🌭"
    },
    
    "frango": {
        "fatos": [
            {
                "titulo": "Proteína Completa e Magra",
                "resumo": "Peito de frango: 32g proteína, apenas 3g gordura por 100g. Uma das melhores fontes proteicas para atletas e dietas",
                "fonte": "Tabela TACO",
                "tipo": "beneficio",
                "data": "2025"
            },
            {
                "titulo": "Antibióticos na Produção",
                "resumo": "Brasil proibiu promotores de crescimento em 2020, mas ainda usa antibióticos terapêuticos. Prefira frango orgânico/caipira quando possível",
                "fonte": "MAPA - Ministério da Agricultura",
                "tipo": "info",
                "data": "2024"
            },
            {
                "titulo": "Você sabia? Frango Caipira",
                "resumo": "Frango caipira tem 30% menos gordura e mais ômega-3 que frango convencional, além de melhor sabor",
                "fonte": "EMBRAPA",
                "tipo": "curiosidade",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": ["Frango + arroz integral = aminoácidos completos", "Frango + vegetais = refeição balanceada"],
        "voce_sabia": "A cor amarela do frango caipira vem do milho na alimentação, não de corantes",
        "dica_rapida": "Proteína magra de qualidade - preferir peito sem pele",
        "emoji": "🍗"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # OVOS - Desmistificação do colesterol
    # ═══════════════════════════════════════════════════════════════
    "ovo": {
        "fatos": [
            {
                "titulo": "Colesterol: Mito Derrubado",
                "resumo": "Estudos com 500.000 pessoas mostram: ovo NÃO aumenta colesterol ruim na maioria das pessoas. Pode consumir 1-3/dia com segurança",
                "fonte": "American Heart Association 2024",
                "tipo": "beneficio",
                "data": "2024"
            },
            {
                "titulo": "Colina: Nutriente Esquecido",
                "resumo": "Gema é a melhor fonte de colina (147mg/ovo) - essencial para memória, fígado e desenvolvimento fetal. 90% dos brasileiros não consomem colina suficiente",
                "fonte": "NIH - National Institutes of Health",
                "tipo": "beneficio",
                "data": "2025"
            },
            {
                "titulo": "Proteína Padrão-Ouro",
                "resumo": "Ovo tem valor biológico 100 - é a referência para medir qualidade proteica de outros alimentos",
                "fonte": "FAO/OMS",
                "tipo": "curiosidade",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": ["Ovo + vegetais = luteína e zeaxantina protegem visão", "Ovo + torrada integral = café da manhã completo"],
        "voce_sabia": "A cor da casca (branca ou marrom) não afeta valor nutricional - depende da raça da galinha",
        "dica_rapida": "Proteína completa e econômica - pode consumir diariamente",
        "emoji": "🥚"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # VEGETAIS - Agrotóxicos e benefícios
    # ═══════════════════════════════════════════════════════════════
    "brocolis": {
        "fatos": [
            {
                "titulo": "Sulforafano: Potente Anticâncer",
                "resumo": "Brócolis contém sulforafano, composto com propriedades anticancerígenas comprovadas em mais de 2000 estudos científicos",
                "fonte": "Journal of Cancer Prevention",
                "tipo": "beneficio",
                "data": "2025"
            },
            {
                "titulo": "Modo de Preparo Importa",
                "resumo": "Cozinhar no vapor por 3-4 minutos preserva 90% dos nutrientes. Ferver em água perde até 50% das vitaminas",
                "fonte": "Food Chemistry Journal",
                "tipo": "dica",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": ["Brócolis + azeite = absorção de vitaminas lipossolúveis", "Brócolis + mostarda = potencializa sulforafano em 4x"],
        "voce_sabia": "Mastigar bem o brócolis cru ativa mais sulforafano - a enzima mirosinase está nas células",
        "dica_rapida": "Super alimento - rico em vitamina C e anticâncer",
        "emoji": "🥦"
    },
    
    "tomate": {
        "fatos": [
            {
                "titulo": "Licopeno: Antioxidante Poderoso",
                "resumo": "Tomate cozido tem 4x mais licopeno biodisponível que cru. Licopeno reduz risco de câncer de próstata em até 30%",
                "fonte": "Cancer Prevention Research",
                "tipo": "beneficio",
                "data": "2025"
            },
            {
                "titulo": "Agrotóxicos: Atenção",
                "resumo": "Tomate está entre os 10 alimentos com mais resíduos de agrotóxicos no Brasil. Prefira orgânico ou lave muito bem",
                "fonte": "ANVISA - PARA 2023",
                "tipo": "alerta",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": ["Tomate + azeite = licopeno absorvido 200% melhor", "Molho de tomate cozido = mais nutritivo que tomate cru"],
        "voce_sabia": "Tomates vermelhos bem maduros têm até 5x mais licopeno que os pálidos",
        "dica_rapida": "Cozido é mais nutritivo - lavar bem se não for orgânico",
        "emoji": "🍅"
    },
    
    "morango": {
        "fatos": [
            {
                "titulo": "Campeão de Agrotóxicos no Brasil",
                "resumo": "Morango lidera ranking de agrotóxicos da ANVISA há 5 anos. 63% das amostras têm resíduos acima do permitido",
                "fonte": "ANVISA - PARA 2023",
                "tipo": "alerta",
                "data": "2024"
            },
            {
                "titulo": "Rico em Antioxidantes",
                "resumo": "Morango tem mais vitamina C que laranja (64mg vs 57mg por 100g) e antocianinas que protegem o coração",
                "fonte": "USDA Nutrient Database",
                "tipo": "beneficio",
                "data": "2025"
            }
        ],
        "combinacoes_beneficas": ["Morango + iogurte = probióticos + antioxidantes"],
        "voce_sabia": "Morango orgânico tem 50% mais antioxidantes que convencional, além de ser livre de agrotóxicos",
        "dica_rapida": "Preferir orgânico - convencional tem muito agrotóxico",
        "emoji": "🍓"
    },
    
    "pimentao": {
        "fatos": [
            {
                "titulo": "Top 3 em Agrotóxicos",
                "resumo": "Pimentão está entre os 3 alimentos com mais agrotóxicos no Brasil. 80% das amostras têm resíduos",
                "fonte": "ANVISA - PARA 2023",
                "tipo": "alerta",
                "data": "2024"
            },
            {
                "titulo": "Campeão de Vitamina C",
                "resumo": "Pimentão vermelho tem 3x mais vitamina C que laranja (128mg vs 45mg por 100g). Antioxidante poderoso",
                "fonte": "Tabela TACO",
                "tipo": "beneficio",
                "data": "2025"
            }
        ],
        "combinacoes_beneficas": ["Pimentão + carne = vitamina C aumenta absorção de ferro"],
        "voce_sabia": "Pimentões verdes são os mesmos que os vermelhos, só que colhidos antes de amadurecer",
        "dica_rapida": "Rico em vitamina C - preferir orgânico",
        "emoji": "🫑"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # GRÃOS E LEGUMINOSAS
    # ═══════════════════════════════════════════════════════════════
    "feijao": {
        "fatos": [
            {
                "titulo": "Combinação Perfeita Brasileira",
                "resumo": "Arroz + feijão = proteína completa equivalente à carne. Os aminoácidos se complementam perfeitamente",
                "fonte": "British Journal of Nutrition",
                "tipo": "beneficio",
                "data": "2025"
            },
            {
                "titulo": "Fibras para Longevidade",
                "resumo": "Feijão tem 8g de fibras por porção - associado a menor risco de diabetes, doenças cardíacas e maior expectativa de vida",
                "fonte": "Harvard School of Public Health",
                "tipo": "beneficio",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": ["Arroz + feijão = proteína completa", "Feijão + vitamina C = absorção de ferro aumentada"],
        "voce_sabia": "Deixar o feijão de molho por 8-12h reduz antinutrientes e melhora digestão",
        "dica_rapida": "Base da alimentação brasileira - combo perfeito com arroz",
        "emoji": "🫘"
    },
    
    "arroz": {
        "fatos": [
            {
                "titulo": "Arsênio Natural",
                "resumo": "Arroz absorve arsênio do solo naturalmente. Lavar bem e cozinhar com excesso de água (como macarrão) reduz em 60%",
                "fonte": "FDA - Arsenic in Rice",
                "tipo": "info",
                "data": "2025"
            },
            {
                "titulo": "Integral vs Branco",
                "resumo": "Arroz integral tem 3x mais fibras e índice glicêmico 30% menor - melhor para diabéticos e emagrecimento",
                "fonte": "Diabetes Care Journal",
                "tipo": "beneficio",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": ["Arroz + feijão = proteína completa", "Arroz integral + vegetais = refeição de baixo índice glicêmico"],
        "voce_sabia": "O Brasil é o 9º maior produtor de arroz do mundo e o arroz brasileiro tem baixos níveis de arsênio",
        "dica_rapida": "Base alimentar brasileira - integral é mais nutritivo",
        "emoji": "🍚"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # SOBREMESAS E AÇÚCAR
    # ═══════════════════════════════════════════════════════════════
    "sobremesa": {
        "fatos": [
            {
                "titulo": "Limite Diário de Açúcar OMS",
                "resumo": "OMS recomenda máximo 25g de açúcar adicionado/dia (6 colheres de chá). Um brigadeiro tem ~12g",
                "fonte": "OMS 2024",
                "tipo": "moderacao",
                "data": "2024"
            },
            {
                "titulo": "Momento Certo Reduz Impacto",
                "resumo": "Consumir doces após refeição reduz pico glicêmico em 30% comparado a comer em jejum",
                "fonte": "Diabetes Research",
                "tipo": "dica",
                "data": "2025"
            }
        ],
        "combinacoes_beneficas": ["Sobremesa após refeição = menor pico de açúcar"],
        "voce_sabia": "O paladar para doce é evolutivo - nossos ancestrais associavam doce a alimentos seguros e calóricos",
        "dica_rapida": "Consumir após refeição para menor impacto glicêmico",
        "emoji": "🍮"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # SALADA E VEGETAIS FOLHOSOS
    # ═══════════════════════════════════════════════════════════════
    "salada": {
        "fatos": [
            {
                "titulo": "Regra do Prato Saudável Harvard",
                "resumo": "Metade do prato deve ser vegetais e frutas. Estudos mostram redução de 30% em doenças crônicas",
                "fonte": "Harvard Healthy Eating Plate",
                "tipo": "beneficio",
                "data": "2025"
            },
            {
                "titulo": "Absorção de Vitaminas",
                "resumo": "Adicionar azeite ou abacate à salada aumenta absorção de vitaminas A, D, E e K em até 500%",
                "fonte": "Journal of Nutrition",
                "tipo": "dica",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": ["Salada + azeite = vitaminas absorvidas", "Vegetais coloridos = variedade de antioxidantes"],
        "voce_sabia": "Vegetais de cores diferentes têm antioxidantes diferentes - quanto mais cores no prato, melhor",
        "dica_rapida": "Excelente escolha - sempre com azeite para absorver vitaminas",
        "emoji": "🥗"
    },
    
    # ═══════════════════════════════════════════════════════════════
    # OLEAGINOSAS
    # ═══════════════════════════════════════════════════════════════
    "castanha": {
        "fatos": [
            {
                "titulo": "Selênio: Superdose em 1 Castanha",
                "resumo": "Uma única castanha-do-pará fornece 100% do selênio diário necessário. Mineral essencial para tireoide e imunidade",
                "fonte": "NIH - Office of Dietary Supplements",
                "tipo": "beneficio",
                "data": "2025"
            },
            {
                "titulo": "Cuidado com Excesso",
                "resumo": "Mais de 3-4 castanhas/dia pode causar selenose (intoxicação por selênio). Sintomas: queda de cabelo, unhas quebradiças",
                "fonte": "ANVISA",
                "tipo": "moderacao",
                "data": "2024"
            }
        ],
        "combinacoes_beneficas": ["1-2 castanhas/dia = dose ideal de selênio"],
        "voce_sabia": "O Brasil é o maior produtor mundial de castanha-do-pará, mas 95% é exportado",
        "dica_rapida": "1-2 por dia = selênio suficiente. Evite excesso",
        "emoji": "🥜"
    }
}

# Mapeamento expandido de ingredientes para fatos
MAPEAMENTO_FATOS = {
    # Peixes
    "salmão": "salmao", "salmon": "salmao", "salmao": "salmao", "bacalhau": "bacalhau",
    "atum": "atum", "peixe": "peixe", "tilápia": "peixe", "tilapia": "peixe", "sardinha": "peixe",
    "ceviche": "peixe", "filé de peixe": "peixe", "file de peixe": "peixe",
    # Carnes
    "frango": "frango", "peito de frango": "frango", "carne": "carne_bovina",
    "bife": "carne_bovina", "carne bovina": "carne_bovina", "alcatra": "carne_bovina",
    "picanha": "carne_bovina", "costela": "carne_bovina", "maminha": "carne_bovina",
    "cibi sana": "carne_bovina", "costela cibi": "carne_bovina",
    # Processados (alertas)
    "bacon": "bacon", "linguiça": "linguica", "linguica": "linguica",
    "salsicha": "salsicha", "presunto": "linguica", "mortadela": "linguica",
    "embutido": "linguica", "hambúrguer": "linguica",
    # Ovos
    "ovo": "ovo", "ovos": "ovo", "omelete": "ovo",
    # Vegetais
    "brócolis": "brocolis", "brocolis": "brocolis", "tomate": "tomate",
    "morango": "morango", "pimentão": "pimentao", "pimentao": "pimentao",
    "salada": "salada", "alface": "salada", "limão": "limao", "limao": "limao",
    # Grãos
    "arroz": "arroz", "feijão": "feijao", "feijao": "feijao",
    # Doces
    "pudim": "sobremesa", "mousse": "sobremesa", "sorvete": "sobremesa",
    "bolo": "sobremesa", "doce": "sobremesa", "brigadeiro": "sobremesa",
    # Oleaginosas
    "castanha": "castanha", "castanha-do-pará": "castanha",
}


def buscar_fatos_ingrediente(ingrediente: str) -> dict:
    """Busca fatos/notícias relevantes sobre um ingrediente."""
    ingrediente_lower = ingrediente.lower().strip()
    
    if ingrediente_lower in FATOS_ALIMENTOS:
        return FATOS_ALIMENTOS[ingrediente_lower]
    
    if ingrediente_lower in MAPEAMENTO_FATOS:
        chave = MAPEAMENTO_FATOS[ingrediente_lower]
        return FATOS_ALIMENTOS.get(chave)
    
    for termo, chave in MAPEAMENTO_FATOS.items():
        if termo in ingrediente_lower or ingrediente_lower in termo:
            return FATOS_ALIMENTOS.get(chave)
    
    return None


def buscar_fatos_prato(nome_prato: str, ingredientes: list = None) -> list:
    """Busca fatos relevantes para um prato baseado no nome e ingredientes."""
    fatos_encontrados = []
    ingredientes_checados = set()
    
    # Verificar nome do prato
    nome_lower = nome_prato.lower()
    for termo, chave in MAPEAMENTO_FATOS.items():
        if termo in nome_lower and chave not in ingredientes_checados:
            dados = FATOS_ALIMENTOS.get(chave)
            if dados:
                fatos_encontrados.append({
                    "ingrediente": termo.capitalize(),
                    "emoji": dados.get("emoji", "📌"),
                    "dica_rapida": dados.get("dica_rapida", ""),
                    "voce_sabia": dados.get("voce_sabia", ""),
                    "combinacoes_beneficas": dados.get("combinacoes_beneficas", []),
                    "fatos": dados.get("fatos", [])[:2]
                })
                ingredientes_checados.add(chave)
    
    # Verificar ingredientes
    if ingredientes:
        for ing in ingredientes:
            ing_lower = ing.lower()
            for termo, chave in MAPEAMENTO_FATOS.items():
                if termo in ing_lower and chave not in ingredientes_checados:
                    dados = FATOS_ALIMENTOS.get(chave)
                    if dados:
                        fatos_encontrados.append({
                            "ingrediente": ing.capitalize(),
                            "emoji": dados.get("emoji", "📌"),
                            "dica_rapida": dados.get("dica_rapida", ""),
                            "voce_sabia": dados.get("voce_sabia", ""),
                            "combinacoes_beneficas": dados.get("combinacoes_beneficas", []),
                            "fatos": dados.get("fatos", [])[:2]
                        })
                        ingredientes_checados.add(chave)
    
    return fatos_encontrados[:3]


def gerar_alerta_radar(nome_prato: str, ingredientes: list = None) -> dict:
    """Gera alerta do Radar se houver informação relevante sobre o prato."""
    fatos = buscar_fatos_prato(nome_prato, ingredientes)
    
    if not fatos:
        return {"has_alert": False, "message": None, "facts": []}
    
    primeiro = fatos[0]
    fatos_list = primeiro.get("fatos", [])
    
    # Priorizar alertas importantes
    for f in fatos_list:
        if f.get("tipo") == "alerta":
            return {
                "has_alert": True,
                "type": "alerta",
                "emoji": "⚠️",
                "message": f"{primeiro['emoji']} {primeiro['ingrediente']}: {f['resumo'][:100]}...",
                "titulo": f["titulo"],
                "fonte": f.get("fonte", ""),
                "voce_sabia": primeiro.get("voce_sabia", ""),
                "combinacoes": primeiro.get("combinacoes_beneficas", []),
                "facts": fatos
            }
    
    # Se tiver "você sabia" ou combinação benéfica, mostrar
    if primeiro.get("voce_sabia"):
        return {
            "has_alert": True,
            "type": "curiosidade",
            "emoji": primeiro['emoji'],
            "message": f"💡 Você sabia? {primeiro['voce_sabia'][:100]}...",
            "titulo": "Você sabia?",
            "fonte": "",
            "voce_sabia": primeiro.get("voce_sabia", ""),
            "combinacoes": primeiro.get("combinacoes_beneficas", []),
            "facts": fatos
        }
    
    # Senão mostrar benefício ou info
    if fatos_list:
        f = fatos_list[0]
        return {
            "has_alert": True,
            "type": f.get("tipo", "info"),
            "emoji": primeiro['emoji'],
            "message": f"{primeiro['emoji']} {primeiro.get('dica_rapida', f['resumo'][:80])}",
            "titulo": f["titulo"],
            "fonte": f.get("fonte", ""),
            "voce_sabia": primeiro.get("voce_sabia", ""),
            "combinacoes": primeiro.get("combinacoes_beneficas", []),
            "facts": fatos
        }
    
    return {"has_alert": False, "message": None, "facts": []}
