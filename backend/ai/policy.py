"""SoulNutri AI - Policy (Política de Decisão)

Define a política de decisão a partir do score de similaridade.
Faixas de confiança:
- alta:   >= 0.85 (identificação segura - SEM alternativas)
- média:  >= 0.50 e < 0.85 (provável, mostrar alternativas)
- baixa:  < 0.50 (incerto)

Baseado na analogia Waze: mostrar o melhor caminho em tempo real.
"""

from typing import Dict, List, Optional


# Dicionário de nomes corretos dos pratos
DISH_NAMES = {
    'aboboraaocurry': 'Abóbora ao Curry',
    'alhoporogratinadovegano': 'Alho Poró Gratinado Vegano',
    'almondegasmolhosugo': 'Almôndegas ao Molho Sugo',
    'almdegasmolhosugo': 'Almôndegas ao Molho Sugo',
    'arroz7graos': 'Arroz 7 Grãos',
    'arroz7graoscomfrutassecas': 'Arroz 7 Grãos com Frutas Secas',
    'arroz7graoscomlegumes': 'Arroz 7 Grãos com Legumes',
    'arrozbranco': 'Arroz Branco',
    'arrozde7graoscomamendoas': 'Arroz 7 Grãos com Amêndoas',
    'arrozintegral': 'Arroz Integral',
    'arrozintlegumes': 'Arroz Integral com Legumes',
    'atumaogergelim': 'Atum ao Gergelim',
    'bacalhaucomnatas': 'Bacalhau com Natas',
    'bacalhaugomesdesa': 'Bacalhau à Gomes de Sá',
    'baiaodedois': 'Baião de Dois',
    'bananacaramelizada': 'Banana Caramelizada',
    'batataassada': 'Batata Assada',
    'batatacompaprica': 'Batata com Páprica',
    'batatadoce': 'Batata Doce',
    'beringelaaolimao': 'Berinjela ao Limão',
    'beringelaaocurrykincam': 'Berinjela ao Curry',
    'beterrabaaobalsamico': 'Beterraba ao Balsâmico',
    'bolinhodebacalhau': 'Bolinho de Bacalhau',
    'bolobrownie': 'Bolo Brownie',
    'bolochocolatevegano': 'Bolo de Chocolate Vegano',
    'bolodegengibre': 'Bolo de Gengibre',
    'brocolis': 'Brócolis',
    'brocoliscomparmesao': 'Brócolis com Parmesão',
    'brocoliscouveflorgratinado': 'Brócolis e Couve-flor Gratinados',
    'brocolisgratinado': 'Brócolis Gratinado',
    'canelonedeespinafre': 'Canelone de Espinafre',
    'caponata': 'Caponata',
    'carpacciodeabobrinha': 'Carpaccio de Abobrinha',
    'carpacciodelaranja': 'Carpaccio de Laranja',
    'carpacciodeperaruculaeamendoas': 'Carpaccio de Pera com Rúcula e Amêndoas',
    'cebola': 'Cebola',
    'cenouraaoiogurte': 'Cenoura ao Iogurte',
    'cenourapalito': 'Cenoura Palito',
    'cestinhasdecamarao': 'Cestinhas de Camarão',
    'cevicheperuano': 'Ceviche Peruano',
    'cocada': 'Cocada',
    'costelinhacibisana': 'Costelinha Cibi Sana',
    'cuscuzdetapioca': 'Cuscuz de Tapioca',
    'cuscuzmarroquino': 'Cuscuz Marroquino',
    'dadinhodetapioca': 'Dadinho de Tapioca',
    'entrecotegrelhado': 'Entrecôte Grelhado',
    'ervadocecomlaranja': 'Erva Doce com Laranja',
    'escondidinhodecarneseca': 'Escondidinho de Carne Seca',
    'espaguete': 'Espaguete',
    'farofadebacon': 'Farofa de Bacon',
    'farofadebananadaterra': 'Farofa de Banana da Terra',
    'feijaocariocasemcarne': 'Feijão Carioca sem Carne',
    'feijaopretocomcarne': 'Feijão Preto com Carne',
    'feijaopretosemcarne': 'Feijão Preto sem Carne',
    'feijaotropeiro': 'Feijão Tropeiro',
    'figadoacebolado': 'Fígado Acebolado',
    'filedefrangoaparmegiana': 'Filé de Frango à Parmegiana',
    'filedepeixeaomisso': 'Filé de Peixe ao Missô',
    'filedepeixeaomolhodelimao': 'Filé de Peixe ao Molho de Limão',
    'filedepeixeaomolhomisso': 'Filé de Peixe ao Molho Missô',
    'filedepeixemolhoconfit': 'Filé de Peixe ao Molho Confit',
    'filedepeixemolhofrutassecas': 'Filé de Peixe ao Molho de Frutas Secas',
    'frangocremedelimaosalnegro': 'Frango ao Creme de Limão e Sal Negro',
    'gelatinadecereja': 'Gelatina de Cereja',
    'goiabada': 'Goiabada',
    'graodebicotomatesecoespinafre': 'Grão de Bico com Tomate Seco e Espinafre',
    'hamburgerdecarne': 'Hambúrguer de Carne',
    'hamburguervegano': 'Hambúrguer Vegano',
    'jiloempanado': 'Jiló Empanado',
    'kibe': 'Kibe',
    'lasanhadeespinafre': 'Lasanha de Espinafre',
    'lasanhadeportobello': 'Lasanha de Portobello',
    'lentilhacomtofu': 'Lentilha com Tofu',
    'maminhaaomolhomongolia': 'Maminha ao Molho Mongólia',
    'maminhaaomolhomostarda': 'Maminha ao Molho Mostarda',
    'maminhamolhocebola': 'Maminha ao Molho de Cebola',
    'maminhanacervejapreta': 'Maminha na Cerveja Preta',
    'mandioquinhaassada': 'Mandioquinha Assada',
    'mandioquinhacomcamarao': 'Mandioquinha com Camarão',
    'mechouiatunisia': 'Mechouia à Tunísia',
    'minipolpetonerecheadocomqueijo': 'Mini Polpetone Recheado com Queijo',
    'molhovinagrete': 'Molho Vinagrete',
    'moquecadebanadaterra': 'Moqueca de Banana da Terra',
    'moussedemaracuja': 'Mousse de Maracujá',
    'moussedemorango': 'Mousse de Morango',
    'nhoqueaosugo': 'Nhoque ao Sugo',
    'pancetapururuca': 'Panceta Pururuca',
    'pepinocomiogurte': 'Pepino com Iogurte',
    'pernildecordeiro': 'Pernil de Cordeiro',
    'quiaboempanado': 'Quiabo Empanado',
    'repolho': 'Repolho',
    'risoneaopesto': 'Risone ao Pesto',
    'rolinhovietnamita': 'Rolinho Vietnamita',
    'saladadefeijaobranco': 'Salada de Feijão Branco',
    'salpicaodefrango': 'Salpicão de Frango',
    'sobrecoxaaotandoori': 'Sobrecoxa ao Tandoori',
    'tabuledequinoa': 'Tabule de Quinoa',
    'umamidetomate': 'Umami de Tomate',
}

# Categorias dos pratos
DISH_CATEGORIES = {
    # VEGANO
    'aboboraaocurry': 'vegano',
    'alhoporogratinadovegano': 'vegano',
    'arroz7graos': 'vegano',
    'arroz7graoscomfrutassecas': 'vegano',
    'arroz7graoscomlegumes': 'vegano',
    'arrozbranco': 'vegano',
    'arrozde7graoscomamendoas': 'vegano',
    'arrozintegral': 'vegano',
    'arrozintlegumes': 'vegano',
    'batataassada': 'vegano',
    'batatacompaprica': 'vegano',
    'batatadoce': 'vegano',
    'beringelaaolimao': 'vegano',
    'beringelaaocurrykincam': 'vegano',
    'beterrabaaobalsamico': 'vegano',
    'bolochocolatevegano': 'vegano',
    'brocolis': 'vegano',
    'caponata': 'vegano',
    'carpacciodeabobrinha': 'vegano',
    'cebola': 'vegano',
    'cenourapalito': 'vegano',
    'cuscuzmarroquino': 'vegano',
    'ervadocecomlaranja': 'vegano',
    'farofadebananadaterra': 'vegano',
    'feijaocariocasemcarne': 'vegano',
    'feijaopretosemcarne': 'vegano',
    'graodebicotomatesecoespinafre': 'vegano',
    'hamburguervegano': 'vegano',
    'lentilhacomtofu': 'vegano',
    'molhovinagrete': 'vegano',
    'repolho': 'vegano',
    'saladadefeijaobranco': 'vegano',
    'tabuledequinoa': 'vegano',
    'umamidetomate': 'vegano',
    
    # VEGETARIANO
    'brocoliscomparmesao': 'vegetariano',
    'brocoliscouveflorgratinado': 'vegetariano',
    'brocolisgratinado': 'vegetariano',
    'canelonedeespinafre': 'vegetariano',
    'carpacciodelaranja': 'vegetariano',
    'carpacciodeperaruculaeamendoas': 'vegetariano',
    'cenouraaoiogurte': 'vegetariano',
    'cocada': 'vegetariano',
    'cuscuzdetapioca': 'vegetariano',
    'dadinhodetapioca': 'vegetariano',
    'espaguete': 'vegetariano',
    'gelatinadecereja': 'vegetariano',
    'goiabada': 'vegetariano',
    'jiloempanado': 'vegetariano',
    'lasanhadeespinafre': 'vegetariano',
    'lasanhadeportobello': 'vegetariano',
    'mandioquinhaassada': 'vegetariano',
    'moussedemaracuja': 'vegetariano',
    'moussedemorango': 'vegetariano',
    'nhoqueaosugo': 'vegetariano',
    'pepinocomiogurte': 'vegetariano',
    'risoneaopesto': 'vegetariano',
    'bananacaramelizada': 'vegetariano',
    'bolobrownie': 'vegetariano',
    'bolodegengibre': 'vegetariano',
    
    # PROTEÍNA ANIMAL
    'almondegasmolhosugo': 'proteína animal',
    'almdegasmolhosugo': 'proteína animal',
    'atumaogergelim': 'proteína animal',
    'bacalhaucomnatas': 'proteína animal',
    'bacalhaugomesdesa': 'proteína animal',
    'baiaodedois': 'proteína animal',
    'bolinhodebacalhau': 'proteína animal',
    'cestinhasdecamarao': 'proteína animal',
    'cevicheperuano': 'proteína animal',
    'costelinhacibisana': 'proteína animal',
    'entrecotegrelhado': 'proteína animal',
    'escondidinhodecarneseca': 'proteína animal',
    'farofadebacon': 'proteína animal',
    'feijaopretocomcarne': 'proteína animal',
    'feijaotropeiro': 'proteína animal',
    'figadoacebolado': 'proteína animal',
    'filedefrangoaparmegiana': 'proteína animal',
    'filedepeixeaomisso': 'proteína animal',
    'filedepeixeaomolhodelimao': 'proteína animal',
    'filedepeixeaomolhomisso': 'proteína animal',
    'filedepeixemolhoconfit': 'proteína animal',
    'filedepeixemolhofrutassecas': 'proteína animal',
    'frangocremedelimaosalnegro': 'proteína animal',
    'hamburgerdecarne': 'proteína animal',
    'kibe': 'proteína animal',
    'maminhaaomolhomongolia': 'proteína animal',
    'maminhaaomolhomostarda': 'proteína animal',
    'maminhamolhocebola': 'proteína animal',
    'maminhanacervejapreta': 'proteína animal',
    'mandioquinhacomcamarao': 'proteína animal',
    'minipolpetonerecheadocomqueijo': 'proteína animal',
    'moquecadebanadaterra': 'proteína animal',
    'pancetapururuca': 'proteína animal',
    'pernildecordeiro': 'proteína animal',
    'quiaboempanado': 'proteína animal',
    'rolinhovietnamita': 'proteína animal',
    'salpicaodefrango': 'proteína animal',
    'sobrecoxaaotandoori': 'proteína animal',
}

# Informações nutricionais básicas (por 100g aproximado)
DISH_NUTRITION = {
    'default': {'calorias': '~150 kcal', 'proteinas': '~5g', 'carboidratos': '~20g', 'gorduras': '~5g'},
    'arroz': {'calorias': '130 kcal', 'proteinas': '2.7g', 'carboidratos': '28g', 'gorduras': '0.3g'},
    'feijao': {'calorias': '77 kcal', 'proteinas': '5g', 'carboidratos': '14g', 'gorduras': '0.5g'},
    'peixe': {'calorias': '120 kcal', 'proteinas': '22g', 'carboidratos': '0g', 'gorduras': '3g'},
    'frango': {'calorias': '165 kcal', 'proteinas': '31g', 'carboidratos': '0g', 'gorduras': '3.6g'},
    'carne': {'calorias': '250 kcal', 'proteinas': '26g', 'carboidratos': '0g', 'gorduras': '15g'},
    'vegetal': {'calorias': '50 kcal', 'proteinas': '2g', 'carboidratos': '10g', 'gorduras': '0.5g'},
    'massa': {'calorias': '131 kcal', 'proteinas': '5g', 'carboidratos': '25g', 'gorduras': '1g'},
    'sobremesa': {'calorias': '200 kcal', 'proteinas': '3g', 'carboidratos': '35g', 'gorduras': '6g'},
    'batata': {'calorias': '90 kcal', 'proteinas': '2g', 'carboidratos': '20g', 'gorduras': '0.1g'},
}

# =============================================================================
# INFORMAÇÕES DETALHADAS DOS PRATOS
# =============================================================================
DISH_INFO = {
    # ===================== VEGANOS =====================
    'aboboraaocurry': {
        'descricao': 'Abóbora cozida com especiarias indianas em molho cremoso de leite de coco',
        'ingredientes': ['abóbora', 'curry', 'leite de coco', 'gengibre', 'cúrcuma', 'cebola', 'alho'],
        'beneficios': ['Rico em betacaroteno', 'Antioxidantes naturais', 'Anti-inflamatório', 'Baixa caloria', 'Fonte de vitamina A'],
        'riscos': ['Alérgeno: pode conter coco', 'Contém especiarias fortes']
    },
    'alhoporogratinadovegano': {
        'descricao': 'Alho poró gratinado com creme vegetal e ervas',
        'ingredientes': ['alho poró', 'creme vegetal', 'farinha de rosca', 'azeite', 'ervas finas'],
        'beneficios': ['Prebiótico natural', 'Rico em fibras', 'Baixo teor calórico', 'Fonte de vitamina K'],
        'riscos': ['Pode conter glúten (farinha de rosca)', 'Flatulência em excesso']
    },
    'arroz7graos': {
        'descricao': 'Mistura de arroz com grãos integrais e sementes nutritivas',
        'ingredientes': ['arroz integral', 'quinoa', 'linhaça', 'aveia', 'centeio', 'cevada', 'trigo'],
        'beneficios': ['Alto teor de fibras', 'Proteína vegetal completa', 'Energia de longa duração', 'Rico em minerais'],
        'riscos': ['Contém glúten (trigo, cevada, centeio)', 'Índice glicêmico moderado']
    },
    'arroz7graoscomfrutassecas': {
        'descricao': 'Arroz 7 grãos enriquecido com frutas secas',
        'ingredientes': ['arroz 7 grãos', 'uva passa', 'damasco', 'castanhas', 'amêndoas'],
        'beneficios': ['Rico em antioxidantes', 'Energia natural', 'Fibras e proteínas', 'Fonte de ferro'],
        'riscos': ['Contém glúten', 'Alérgeno: castanhas', 'Alto teor de açúcar das frutas']
    },
    'arroz7graoscomlegumes': {
        'descricao': 'Arroz 7 grãos salteado com legumes frescos',
        'ingredientes': ['arroz 7 grãos', 'cenoura', 'ervilha', 'milho', 'brócolis', 'abobrinha'],
        'beneficios': ['Rico em fibras', 'Vitaminas variadas', 'Baixa gordura', 'Refeição completa'],
        'riscos': ['Contém glúten', 'Pode causar gases']
    },
    'arrozbranco': {
        'descricao': 'Arroz branco cozido no vapor, acompanhamento clássico',
        'ingredientes': ['arroz branco', 'sal', 'alho', 'óleo'],
        'beneficios': ['Fonte de energia rápida', 'Fácil digestão', 'Sem glúten naturalmente'],
        'riscos': ['Alto índice glicêmico', 'Baixo teor de fibras']
    },
    'arrozde7graoscomamendoas': {
        'descricao': 'Arroz 7 grãos com amêndoas tostadas',
        'ingredientes': ['arroz 7 grãos', 'amêndoas', 'azeite', 'sal', 'ervas'],
        'beneficios': ['Rico em ômega-3', 'Proteína e fibras', 'Vitamina E das amêndoas'],
        'riscos': ['Contém glúten', 'Alérgeno: amêndoas (oleaginosas)']
    },
    'arrozintegral': {
        'descricao': 'Arroz integral rico em fibras e nutrientes',
        'ingredientes': ['arroz integral', 'sal'],
        'beneficios': ['Alto teor de fibras', 'Baixo índice glicêmico', 'Rico em vitaminas B', 'Sem glúten'],
        'riscos': ['Digestão mais lenta', 'Pode conter arsênio em excesso']
    },
    'arrozintlegumes': {
        'descricao': 'Arroz integral salteado com legumes variados',
        'ingredientes': ['arroz integral', 'cenoura', 'brócolis', 'ervilha', 'abobrinha', 'azeite'],
        'beneficios': ['Refeição completa', 'Rico em fibras e vitaminas', 'Baixo índice glicêmico'],
        'riscos': ['Digestão lenta', 'Pode causar flatulência']
    },
    'batataassada': {
        'descricao': 'Batatas assadas com ervas aromáticas',
        'ingredientes': ['batata', 'azeite', 'alecrim', 'alho', 'sal'],
        'beneficios': ['Fonte de potássio', 'Energia complexa', 'Vitamina C', 'Sem glúten'],
        'riscos': ['Alto índice glicêmico', 'Cuidado com fritura em excesso']
    },
    'batatacompaprica': {
        'descricao': 'Batatas temperadas com páprica defumada',
        'ingredientes': ['batata', 'páprica defumada', 'azeite', 'alho', 'sal'],
        'beneficios': ['Antioxidantes da páprica', 'Fonte de potássio', 'Energia sustentada'],
        'riscos': ['Alto índice glicêmico', 'Páprica pode irritar estômago sensível']
    },
    'batatadoce': {
        'descricao': 'Batata doce assada ou cozida, naturalmente doce',
        'ingredientes': ['batata doce'],
        'beneficios': ['Baixo índice glicêmico', 'Rica em betacaroteno', 'Fibras', 'Vitamina A', 'Antioxidantes'],
        'riscos': ['Moderação para diabéticos', 'Alto teor de carboidratos']
    },
    'beringelaaolimao': {
        'descricao': 'Berinjela grelhada com molho cítrico de limão',
        'ingredientes': ['berinjela', 'limão', 'azeite', 'alho', 'salsinha'],
        'beneficios': ['Baixíssima caloria', 'Rica em fibras', 'Antioxidantes', 'Ajuda na digestão'],
        'riscos': ['Pode absorver muito óleo', 'Evitar se tiver problemas renais']
    },
    'beringelaaocurrykincam': {
        'descricao': 'Berinjela ao curry com especiarias aromáticas',
        'ingredientes': ['berinjela', 'curry', 'leite de coco', 'gengibre', 'coentro'],
        'beneficios': ['Anti-inflamatório', 'Baixa caloria', 'Fibras', 'Especiarias benéficas'],
        'riscos': ['Pode conter coco (alérgeno)', 'Especiarias fortes']
    },
    'beterrabaaobalsamico': {
        'descricao': 'Beterraba assada com redução de vinagre balsâmico',
        'ingredientes': ['beterraba', 'vinagre balsâmico', 'azeite', 'mel', 'tomilho'],
        'beneficios': ['Rica em ferro', 'Nitratos naturais', 'Melhora circulação', 'Antioxidantes'],
        'riscos': ['Alto teor de açúcar natural', 'Pode tingir urina/fezes (normal)']
    },
    'bolochocolatevegano': {
        'descricao': 'Bolo de chocolate sem ingredientes de origem animal',
        'ingredientes': ['farinha', 'cacau', 'açúcar', 'óleo vegetal', 'leite vegetal', 'fermento'],
        'beneficios': ['Livre de lactose', 'Antioxidantes do cacau', 'Sem colesterol'],
        'riscos': ['Contém glúten', 'Alto teor de açúcar', 'Calórico']
    },
    'brocolis': {
        'descricao': 'Brócolis cozido no vapor, nutritivo e saboroso',
        'ingredientes': ['brócolis', 'sal', 'azeite'],
        'beneficios': ['Superalimento', 'Rico em vitamina C e K', 'Fibras', 'Cálcio', 'Anticancerígeno'],
        'riscos': ['Pode causar gases', 'Evitar em hipotireoidismo não tratado']
    },
    'caponata': {
        'descricao': 'Prato siciliano de berinjela com tomate e especiarias',
        'ingredientes': ['berinjela', 'tomate', 'cebola', 'aipo', 'azeitonas', 'alcaparras', 'vinagre'],
        'beneficios': ['Rico em fibras', 'Antioxidantes', 'Baixa caloria', 'Probióticos naturais'],
        'riscos': ['Alto teor de sódio', 'Acidez do vinagre']
    },
    'carpacciodeabobrinha': {
        'descricao': 'Finas fatias de abobrinha crua com azeite e limão',
        'ingredientes': ['abobrinha', 'azeite extravirgem', 'limão', 'parmesão vegano', 'rúcula'],
        'beneficios': ['Baixíssima caloria', 'Hidratante', 'Rico em potássio', 'Fácil digestão'],
        'riscos': ['Sensibilidade a alimentos crus', 'Atenção à procedência']
    },
    'cebola': {
        'descricao': 'Cebola caramelizada ou grelhada',
        'ingredientes': ['cebola', 'azeite', 'sal'],
        'beneficios': ['Prebiótico', 'Anti-inflamatório', 'Rico em antioxidantes', 'Melhora imunidade'],
        'riscos': ['Pode causar azia', 'Flatulência', 'Mau hálito']
    },
    'cenourapalito': {
        'descricao': 'Cenouras cortadas em palito, cozidas ou cruas',
        'ingredientes': ['cenoura', 'sal'],
        'beneficios': ['Rica em betacaroteno', 'Vitamina A', 'Boa para visão', 'Fibras', 'Baixa caloria'],
        'riscos': ['Em excesso pode deixar pele amarelada (carotenemia)']
    },
    'cuscuzmarroquino': {
        'descricao': 'Semolina de trigo cozida no vapor com temperos',
        'ingredientes': ['semolina de trigo', 'caldo de legumes', 'azeite', 'especiarias'],
        'beneficios': ['Fonte de carboidratos', 'Rápido preparo', 'Leve'],
        'riscos': ['Contém glúten', 'Baixo teor de fibras']
    },
    'ervadocecomlaranja': {
        'descricao': 'Erva doce (funcho) salteada com suco de laranja',
        'ingredientes': ['erva doce', 'suco de laranja', 'azeite', 'sal'],
        'beneficios': ['Digestivo natural', 'Rico em vitamina C', 'Baixa caloria', 'Anti-inflamatório'],
        'riscos': ['Pode causar alergia em sensíveis', 'Interação com alguns medicamentos']
    },
    'farofadebananadaterra': {
        'descricao': 'Farofa com banana da terra frita',
        'ingredientes': ['farinha de mandioca', 'banana da terra', 'cebola', 'manteiga vegana', 'sal'],
        'beneficios': ['Fonte de potássio', 'Energia', 'Sem glúten (se usar farinha de mandioca)'],
        'riscos': ['Alto teor calórico', 'Gordura da fritura']
    },
    'feijaocariocasemcarne': {
        'descricao': 'Feijão carioca cozido em caldo temperado, versão vegetariana',
        'ingredientes': ['feijão carioca', 'alho', 'cebola', 'louro', 'sal'],
        'beneficios': ['Rico em fibras', 'Proteína vegetal', 'Fonte de ferro', 'Baixa gordura'],
        'riscos': ['Pode causar gases', 'Moderado em carboidratos']
    },
    'feijaopretosemcarne': {
        'descricao': 'Feijão preto cozido sem carne, rico e saboroso',
        'ingredientes': ['feijão preto', 'alho', 'cebola', 'louro', 'sal'],
        'beneficios': ['Alto teor de fibras', 'Proteína vegetal', 'Rico em ferro', 'Antioxidantes'],
        'riscos': ['Pode causar flatulência', 'Digestão mais lenta']
    },
    'graodebicotomatesecoespinafre': {
        'descricao': 'Grão de bico salteado com tomate seco e espinafre',
        'ingredientes': ['grão de bico', 'tomate seco', 'espinafre', 'alho', 'azeite'],
        'beneficios': ['Proteína completa', 'Rico em ferro', 'Fibras', 'Vitaminas A e K'],
        'riscos': ['Pode causar gases', 'Alto teor de sódio do tomate seco']
    },
    'hamburguervegano': {
        'descricao': 'Hambúrguer de proteína vegetal com especiarias',
        'ingredientes': ['proteína de soja ou grão de bico', 'cebola', 'alho', 'especiarias', 'farinha'],
        'beneficios': ['Proteína vegetal', 'Sem colesterol', 'Fibras'],
        'riscos': ['Pode conter glúten', 'Alto teor de sódio', 'Soja pode ser alérgeno']
    },
    'lentilhacomtofu': {
        'descricao': 'Lentilha cozida com cubos de tofu temperado',
        'ingredientes': ['lentilha', 'tofu', 'tomate', 'cebola', 'curry', 'coentro'],
        'beneficios': ['Proteína completa', 'Rico em ferro', 'Fibras', 'Baixa gordura'],
        'riscos': ['Soja (tofu) pode ser alérgeno', 'Pode causar gases']
    },
    'molhovinagrete': {
        'descricao': 'Molho fresco de tomate, cebola e pimentão picados',
        'ingredientes': ['tomate', 'cebola', 'pimentão', 'vinagre', 'azeite', 'coentro'],
        'beneficios': ['Baixíssima caloria', 'Rico em vitamina C', 'Antioxidantes', 'Fresco'],
        'riscos': ['Acidez pode irritar estômago', 'Cebola crua pode causar gases']
    },
    'repolho': {
        'descricao': 'Repolho refogado ou cru em salada',
        'ingredientes': ['repolho', 'sal', 'azeite'],
        'beneficios': ['Baixíssima caloria', 'Rico em vitamina C', 'Fibras', 'Anticancerígeno'],
        'riscos': ['Pode causar gases', 'Evitar em hipotireoidismo']
    },
    'saladadefeijaobranco': {
        'descricao': 'Salada fria de feijão branco com ervas',
        'ingredientes': ['feijão branco', 'tomate', 'cebola', 'salsinha', 'azeite', 'limão'],
        'beneficios': ['Proteína vegetal', 'Fibras', 'Vitaminas', 'Baixa gordura'],
        'riscos': ['Pode causar gases', 'Digestão lenta']
    },
    'tabuledequinoa': {
        'descricao': 'Salada libanesa com quinoa no lugar do trigo',
        'ingredientes': ['quinoa', 'tomate', 'pepino', 'hortelã', 'salsinha', 'limão', 'azeite'],
        'beneficios': ['Proteína completa', 'Sem glúten', 'Rico em fibras', 'Vitaminas'],
        'riscos': ['Saponinas podem irritar intestino (lavar bem)']
    },
    'umamidetomate': {
        'descricao': 'Tomates concentrados com sabor umami intenso',
        'ingredientes': ['tomate', 'azeite', 'alho', 'ervas', 'sal'],
        'beneficios': ['Licopeno (antioxidante)', 'Baixa caloria', 'Vitamina C'],
        'riscos': ['Acidez', 'Alto teor de sódio se concentrado']
    },

    # ===================== VEGETARIANOS =====================
    'brocoliscomparmesao': {
        'descricao': 'Brócolis gratinado com queijo parmesão',
        'ingredientes': ['brócolis', 'queijo parmesão', 'azeite', 'alho'],
        'beneficios': ['Rico em cálcio', 'Vitamina C e K', 'Proteína do queijo'],
        'riscos': ['Contém lactose', 'Gordura saturada do queijo']
    },
    'brocoliscouveflorgratinado': {
        'descricao': 'Brócolis e couve-flor gratinados com queijo',
        'ingredientes': ['brócolis', 'couve-flor', 'queijo', 'creme de leite', 'noz-moscada'],
        'beneficios': ['Rico em fibras', 'Cálcio', 'Vitaminas C e K', 'Proteína'],
        'riscos': ['Contém lactose', 'Gordura do creme', 'Pode causar gases']
    },
    'brocolisgratinado': {
        'descricao': 'Brócolis ao forno com queijo gratinado',
        'ingredientes': ['brócolis', 'queijo mussarela', 'creme de leite', 'parmesão'],
        'beneficios': ['Rico em vitamina C', 'Fibras', 'Cálcio do queijo', 'Antioxidantes'],
        'riscos': ['Contém lactose', 'Gordura do queijo']
    },
    'canelonedeespinafre': {
        'descricao': 'Massa recheada com espinafre e ricota',
        'ingredientes': ['massa de canelone', 'espinafre', 'ricota', 'molho de tomate', 'queijo'],
        'beneficios': ['Rico em ferro', 'Cálcio', 'Vitamina A', 'Proteína'],
        'riscos': ['Contém glúten', 'Contém lactose', 'Calórico']
    },
    'carpacciodelaranja': {
        'descricao': 'Fatias finas de laranja com mel e hortelã',
        'ingredientes': ['laranja', 'mel', 'hortelã', 'canela'],
        'beneficios': ['Rico em vitamina C', 'Antioxidantes', 'Hidratante', 'Baixa caloria'],
        'riscos': ['Alto teor de açúcar', 'Acidez pode irritar estômago']
    },
    'carpacciodeperaruculaeamendoas': {
        'descricao': 'Fatias de pera com rúcula e amêndoas',
        'ingredientes': ['pera', 'rúcula', 'amêndoas', 'azeite', 'queijo parmesão'],
        'beneficios': ['Rico em fibras', 'Vitamina E', 'Antioxidantes', 'Ômega-3'],
        'riscos': ['Alérgeno: amêndoas', 'Contém lactose (queijo)']
    },
    'cenouraaoiogurte': {
        'descricao': 'Cenoura ralada com molho de iogurte',
        'ingredientes': ['cenoura', 'iogurte natural', 'mel', 'gengibre'],
        'beneficios': ['Probióticos', 'Vitamina A', 'Cálcio', 'Digestivo'],
        'riscos': ['Contém lactose']
    },
    'cocada': {
        'descricao': 'Doce tradicional de coco com açúcar',
        'ingredientes': ['coco ralado', 'açúcar', 'leite condensado'],
        'beneficios': ['Energia rápida', 'Fibras do coco', 'Sabor tradicional'],
        'riscos': ['Muito alto em açúcar', 'Alto teor calórico', 'Contém lactose']
    },
    'cuscuzdetapioca': {
        'descricao': 'Cuscuz doce de tapioca com coco',
        'ingredientes': ['tapioca', 'leite de coco', 'açúcar', 'coco ralado'],
        'beneficios': ['Sem glúten', 'Fonte de energia', 'Tradição brasileira'],
        'riscos': ['Alto teor de açúcar', 'Calórico', 'Pode conter coco (alérgeno)']
    },
    'dadinhodetapioca': {
        'descricao': 'Cubos crocantes de tapioca com queijo',
        'ingredientes': ['tapioca', 'queijo coalho', 'sal'],
        'beneficios': ['Sem glúten', 'Proteína do queijo', 'Petisco saboroso'],
        'riscos': ['Contém lactose', 'Alto teor de gordura', 'Fritura']
    },
    'espaguete': {
        'descricao': 'Massa italiana longa servida com molho',
        'ingredientes': ['massa de trigo', 'molho de tomate', 'azeite', 'alho', 'manjericão'],
        'beneficios': ['Fonte de carboidratos', 'Energia rápida', 'Baixo teor de gordura'],
        'riscos': ['Contém glúten', 'Alto índice glicêmico']
    },
    'gelatinadecereja': {
        'descricao': 'Sobremesa de gelatina sabor cereja',
        'ingredientes': ['gelatina', 'açúcar', 'aroma de cereja'],
        'beneficios': ['Baixa caloria', 'Colágeno', 'Hidratante'],
        'riscos': ['Alto teor de açúcar', 'Corantes artificiais', 'Gelatina de origem animal']
    },
    'goiabada': {
        'descricao': 'Doce tradicional de goiaba em bloco',
        'ingredientes': ['goiaba', 'açúcar'],
        'beneficios': ['Rico em vitamina C', 'Fibras', 'Energia'],
        'riscos': ['Muito alto em açúcar', 'Alto índice glicêmico']
    },
    'jiloempanado': {
        'descricao': 'Jiló empanado e frito, crocante',
        'ingredientes': ['jiló', 'farinha', 'ovo', 'sal', 'óleo'],
        'beneficios': ['Fibras', 'Baixa caloria (sem empanamento)', 'Digestivo'],
        'riscos': ['Contém glúten', 'Contém ovo', 'Gordura da fritura']
    },
    'lasanhadeespinafre': {
        'descricao': 'Lasanha verde com camadas de espinafre e queijo',
        'ingredientes': ['massa de lasanha', 'espinafre', 'ricota', 'mussarela', 'molho branco'],
        'beneficios': ['Rico em ferro', 'Cálcio', 'Proteína', 'Vitaminas'],
        'riscos': ['Contém glúten', 'Contém lactose', 'Alto teor calórico']
    },
    'lasanhadeportobello': {
        'descricao': 'Lasanha com cogumelos portobello',
        'ingredientes': ['massa', 'cogumelo portobello', 'queijo', 'molho branco', 'cebola'],
        'beneficios': ['Proteína do cogumelo', 'Vitamina D', 'Fibras', 'Umami natural'],
        'riscos': ['Contém glúten', 'Contém lactose', 'Calórico']
    },
    'mandioquinhaassada': {
        'descricao': 'Mandioquinha assada com ervas',
        'ingredientes': ['mandioquinha', 'azeite', 'alecrim', 'sal'],
        'beneficios': ['Fácil digestão', 'Fonte de potássio', 'Vitaminas', 'Sem glúten'],
        'riscos': ['Alto teor de carboidratos', 'Índice glicêmico moderado']
    },
    'moussedemaracuja': {
        'descricao': 'Mousse cremoso de maracujá',
        'ingredientes': ['maracujá', 'creme de leite', 'leite condensado', 'gelatina'],
        'beneficios': ['Rico em vitamina C', 'Relaxante natural', 'Sabor tropical'],
        'riscos': ['Alto teor de açúcar', 'Contém lactose', 'Calórico']
    },
    'moussedemorango': {
        'descricao': 'Mousse cremoso de morango',
        'ingredientes': ['morango', 'creme de leite', 'leite condensado', 'gelatina'],
        'beneficios': ['Antioxidantes', 'Vitamina C', 'Refrescante'],
        'riscos': ['Alto teor de açúcar', 'Contém lactose', 'Calórico']
    },
    'nhoqueaosugo': {
        'descricao': 'Nhoque de batata com molho de tomate',
        'ingredientes': ['batata', 'farinha', 'ovo', 'molho de tomate', 'manjericão'],
        'beneficios': ['Fonte de carboidratos', 'Energia', 'Potássio da batata'],
        'riscos': ['Contém glúten', 'Contém ovo', 'Alto índice glicêmico']
    },
    'pepinocomiogurte': {
        'descricao': 'Pepino fresco com molho de iogurte (tipo tzatziki)',
        'ingredientes': ['pepino', 'iogurte', 'alho', 'hortelã', 'azeite'],
        'beneficios': ['Hidratante', 'Probióticos', 'Baixíssima caloria', 'Refrescante'],
        'riscos': ['Contém lactose']
    },
    'risoneaopesto': {
        'descricao': 'Massa risone com molho pesto de manjericão',
        'ingredientes': ['massa risone', 'manjericão', 'parmesão', 'pinoli', 'azeite', 'alho'],
        'beneficios': ['Antioxidantes', 'Gorduras boas do azeite', 'Sabor aromático'],
        'riscos': ['Contém glúten', 'Contém lactose', 'Alérgeno: pinoli (oleaginosa)']
    },
    'bananacaramelizada': {
        'descricao': 'Banana grelhada com açúcar caramelizado',
        'ingredientes': ['banana', 'açúcar', 'manteiga', 'canela'],
        'beneficios': ['Potássio', 'Energia rápida', 'Sabor doce natural'],
        'riscos': ['Alto teor de açúcar', 'Contém lactose (manteiga)', 'Calórico']
    },
    'bolobrownie': {
        'descricao': 'Bolo denso de chocolate tipo brownie',
        'ingredientes': ['chocolate', 'manteiga', 'açúcar', 'ovos', 'farinha', 'nozes'],
        'beneficios': ['Antioxidantes do cacau', 'Energia', 'Sabor intenso'],
        'riscos': ['Contém glúten', 'Contém ovo', 'Contém lactose', 'Alérgeno: nozes', 'Alto teor calórico']
    },
    'bolodegengibre': {
        'descricao': 'Bolo aromático de gengibre',
        'ingredientes': ['farinha', 'gengibre', 'açúcar', 'ovos', 'manteiga', 'especiarias'],
        'beneficios': ['Anti-inflamatório', 'Digestivo', 'Sabor único'],
        'riscos': ['Contém glúten', 'Contém ovo', 'Contém lactose', 'Alto teor de açúcar']
    },

    # ===================== PROTEÍNA ANIMAL =====================
    'almondegasmolhosugo': {
        'descricao': 'Almôndegas de carne bovina ao molho de tomate',
        'ingredientes': ['carne moída', 'cebola', 'alho', 'ovo', 'farinha de rosca', 'molho de tomate'],
        'beneficios': ['Rica em proteína', 'Ferro', 'Vitaminas B', 'Zinco'],
        'riscos': ['Gordura saturada', 'Contém glúten', 'Contém ovo', 'Alto teor de sódio']
    },
    'almdegasmolhosugo': {
        'descricao': 'Almôndegas de carne bovina ao molho de tomate',
        'ingredientes': ['carne moída', 'cebola', 'alho', 'ovo', 'farinha de rosca', 'molho de tomate'],
        'beneficios': ['Rica em proteína', 'Ferro', 'Vitaminas B', 'Zinco'],
        'riscos': ['Gordura saturada', 'Contém glúten', 'Contém ovo', 'Alto teor de sódio']
    },
    'atumaogergelim': {
        'descricao': 'Atum fresco selado com crosta de gergelim',
        'ingredientes': ['atum fresco', 'gergelim', 'shoyu', 'gengibre', 'wasabi'],
        'beneficios': ['Rico em ômega-3', 'Proteína magra', 'Selênio', 'Vitamina D'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: gergelim', 'Alto teor de sódio (shoyu)', 'Mercúrio em excesso']
    },
    'bacalhaucomnatas': {
        'descricao': 'Bacalhau desfiado gratinado com creme de leite',
        'ingredientes': ['bacalhau', 'batata', 'creme de leite', 'cebola', 'alho', 'azeitonas'],
        'beneficios': ['Proteína de alta qualidade', 'Ômega-3', 'Cálcio'],
        'riscos': ['Alérgeno: peixe', 'Contém lactose', 'Alto teor de sódio', 'Calórico']
    },
    'bacalhaugomesdesa': {
        'descricao': 'Prato tradicional português de bacalhau com batatas',
        'ingredientes': ['bacalhau', 'batata', 'cebola', 'ovos', 'azeitonas', 'azeite'],
        'beneficios': ['Rico em proteína', 'Ômega-3', 'Vitaminas B12 e D'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: ovo', 'Alto teor de sódio']
    },
    'baiaodedois': {
        'descricao': 'Prato típico nordestino com arroz e feijão-de-corda cozidos juntos',
        'ingredientes': ['arroz', 'feijão-de-corda', 'bacon', 'queijo coalho', 'manteiga', 'temperos'],
        'beneficios': ['Rico em proteínas', 'Fonte de fibras', 'Energia de longa duração'],
        'riscos': ['Alto teor de sódio', 'Contém lactose (queijo)', 'Gordura saturada (bacon)']
    },
    'bolinhodebacalhau': {
        'descricao': 'Bolinho frito de bacalhau com batata',
        'ingredientes': ['bacalhau', 'batata', 'ovo', 'cebola', 'salsinha'],
        'beneficios': ['Proteína', 'Ômega-3', 'Sabor tradicional'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: ovo', 'Fritura', 'Alto teor de sódio']
    },
    'cestinhasdecamarao': {
        'descricao': 'Cestinhas crocantes recheadas com camarão',
        'ingredientes': ['camarão', 'massa wonton', 'cream cheese', 'cebolinha'],
        'beneficios': ['Proteína magra', 'Selênio', 'Zinco'],
        'riscos': ['Alérgeno: crustáceo (camarão)', 'Contém lactose', 'Fritura']
    },
    'cevicheperuano': {
        'descricao': 'Peixe cru marinado em limão com cebola roxa',
        'ingredientes': ['peixe branco', 'limão', 'cebola roxa', 'coentro', 'pimenta', 'milho'],
        'beneficios': ['Proteína magra', 'Vitamina C', 'Ômega-3', 'Baixa caloria'],
        'riscos': ['Alérgeno: peixe', 'Peixe cru requer frescor', 'Acidez alta']
    },
    'costelinhacibisana': {
        'descricao': 'Costelinha de porco assada com molho especial',
        'ingredientes': ['costela de porco', 'alho', 'mel', 'shoyu', 'gengibre'],
        'beneficios': ['Alto teor proteico', 'Vitaminas B', 'Colágeno'],
        'riscos': ['Alto teor de gordura saturada', 'Calórico', 'Alto sódio']
    },
    'entrecotegrelhado': {
        'descricao': 'Corte nobre de carne bovina grelhado',
        'ingredientes': ['entrecôte', 'sal grosso', 'pimenta', 'alho'],
        'beneficios': ['Alto teor proteico', 'Rico em ferro e zinco', 'Vitaminas B12'],
        'riscos': ['Gordura saturada', 'Colesterol', 'Excesso pode ser prejudicial']
    },
    'escondidinhodecarneseca': {
        'descricao': 'Purê de mandioca com carne seca desfiada gratinada',
        'ingredientes': ['mandioca', 'carne seca', 'queijo', 'manteiga', 'creme de leite'],
        'beneficios': ['Alto teor proteico', 'Energia', 'Sabor intenso'],
        'riscos': ['Alto teor de sódio', 'Gordura saturada', 'Contém lactose', 'Muito calórico']
    },
    'farofadebacon': {
        'descricao': 'Farofa com bacon crocante',
        'ingredientes': ['farinha de mandioca', 'bacon', 'cebola', 'manteiga', 'ovos'],
        'beneficios': ['Energia', 'Proteína do bacon', 'Sabor defumado'],
        'riscos': ['Alto teor de gordura saturada', 'Alto sódio', 'Contém ovo']
    },
    'feijaopretocomcarne': {
        'descricao': 'Feijão preto cozido com carne bovina',
        'ingredientes': ['feijão preto', 'carne bovina', 'alho', 'cebola', 'louro'],
        'beneficios': ['Rico em proteína', 'Ferro', 'Fibras'],
        'riscos': ['Pode causar gases', 'Gordura da carne', 'Alto sódio']
    },
    'feijaotropeiro': {
        'descricao': 'Prato mineiro com feijão, bacon, linguiça e farinha',
        'ingredientes': ['feijão', 'bacon', 'linguiça', 'farinha de mandioca', 'ovos', 'couve'],
        'beneficios': ['Muito proteico', 'Energia', 'Tradição mineira'],
        'riscos': ['Alto teor de gordura', 'Alto sódio', 'Contém ovo', 'Muito calórico']
    },
    'figadoacebolado': {
        'descricao': 'Fígado bovino grelhado com cebolas',
        'ingredientes': ['fígado bovino', 'cebola', 'alho', 'sal', 'azeite'],
        'beneficios': ['Riquíssimo em ferro', 'Vitamina A', 'Vitamina B12', 'Proteína'],
        'riscos': ['Muito alto em colesterol', 'Alto em vitamina A (não exceder)', 'Purina alta']
    },
    'filedefrangoaparmegiana': {
        'descricao': 'Filé de frango empanado com molho e queijo',
        'ingredientes': ['peito de frango', 'farinha de rosca', 'ovo', 'molho de tomate', 'mussarela', 'presunto'],
        'beneficios': ['Alto teor proteico', 'Cálcio do queijo'],
        'riscos': ['Contém glúten', 'Contém ovo', 'Contém lactose', 'Fritura', 'Calórico']
    },
    'filedepeixeaomisso': {
        'descricao': 'Filé de peixe com molho de missô japonês',
        'ingredientes': ['peixe branco', 'missô', 'saquê', 'gengibre', 'cebolinha'],
        'beneficios': ['Proteína magra', 'Ômega-3', 'Probióticos do missô'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: soja (missô)', 'Alto sódio']
    },
    'filedepeixeaomolhodelimao': {
        'descricao': 'Filé de peixe branco grelhado com molho cítrico de limão',
        'ingredientes': ['peixe branco', 'limão', 'manteiga', 'alcaparras', 'salsinha'],
        'beneficios': ['Rico em ômega-3', 'Proteína magra', 'Baixa caloria', 'Bom para coração'],
        'riscos': ['Alérgeno: peixe', 'Contém lactose (manteiga)']
    },
    'filedepeixeaomolhomisso': {
        'descricao': 'Filé de peixe ao molho missô',
        'ingredientes': ['peixe', 'missô', 'gengibre', 'cebolinha', 'gergelim'],
        'beneficios': ['Proteína magra', 'Ômega-3', 'Probióticos'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: soja', 'Alérgeno: gergelim', 'Alto sódio']
    },
    'filedepeixemolhoconfit': {
        'descricao': 'Filé de peixe com tomate confit',
        'ingredientes': ['peixe', 'tomate', 'azeite', 'alho', 'ervas'],
        'beneficios': ['Proteína magra', 'Ômega-3', 'Licopeno', 'Baixa caloria'],
        'riscos': ['Alérgeno: peixe']
    },
    'filedepeixemolhofrutassecas': {
        'descricao': 'Filé de peixe com molho de frutas secas',
        'ingredientes': ['peixe', 'uva passa', 'damasco', 'vinho branco', 'manteiga'],
        'beneficios': ['Ômega-3', 'Antioxidantes das frutas', 'Proteína'],
        'riscos': ['Alérgeno: peixe', 'Contém lactose', 'Açúcar das frutas secas']
    },
    'frangocremedelimaosalnegro': {
        'descricao': 'Frango ao creme de limão com sal negro do Havaí',
        'ingredientes': ['frango', 'creme de leite', 'limão', 'sal negro', 'ervas'],
        'beneficios': ['Proteína magra', 'Vitamina C', 'Minerais do sal negro'],
        'riscos': ['Contém lactose', 'Gordura do creme']
    },
    'hamburgerdecarne': {
        'descricao': 'Hambúrguer artesanal de carne bovina',
        'ingredientes': ['carne bovina moída', 'sal', 'pimenta', 'cebola'],
        'beneficios': ['Alto teor proteico', 'Ferro', 'Zinco', 'Vitaminas B'],
        'riscos': ['Gordura saturada', 'Colesterol', 'Alto sódio']
    },
    'kibe': {
        'descricao': 'Bolinho de origem árabe de carne e trigo',
        'ingredientes': ['carne moída', 'trigo para quibe', 'cebola', 'hortelã', 'especiarias'],
        'beneficios': ['Proteína', 'Ferro', 'Fibras do trigo'],
        'riscos': ['Contém glúten', 'Gordura da carne', 'Fritura (se frito)']
    },
    'maminhaaomolhomongolia': {
        'descricao': 'Maminha bovina ao molho agridoce mongoliano',
        'ingredientes': ['maminha', 'shoyu', 'gengibre', 'alho', 'açúcar mascavo', 'cebolinha'],
        'beneficios': ['Alto teor proteico', 'Ferro', 'Zinco'],
        'riscos': ['Alto sódio', 'Açúcar do molho', 'Gordura']
    },
    'maminhaaomolhomostarda': {
        'descricao': 'Corte bovino nobre assado com molho de mostarda',
        'ingredientes': ['maminha bovina', 'mostarda', 'creme de leite', 'vinho branco'],
        'beneficios': ['Alto teor proteico', 'Rico em ferro e zinco', 'Vitaminas do complexo B'],
        'riscos': ['Gordura saturada', 'Contém lactose', 'Alto colesterol']
    },
    'maminhamolhocebola': {
        'descricao': 'Maminha com molho de cebola caramelizada',
        'ingredientes': ['maminha', 'cebola', 'vinho', 'manteiga', 'tomilho'],
        'beneficios': ['Proteína', 'Ferro', 'Zinco', 'Sabor intenso'],
        'riscos': ['Gordura saturada', 'Contém lactose', 'Colesterol']
    },
    'maminhanacervejapreta': {
        'descricao': 'Maminha assada na cerveja preta',
        'ingredientes': ['maminha', 'cerveja preta', 'cebola', 'alho', 'louro'],
        'beneficios': ['Proteína', 'Ferro', 'Carne macia', 'Sabor intenso'],
        'riscos': ['Gordura saturada', 'Contém álcool residual', 'Colesterol']
    },
    'mandioquinhacomcamarao': {
        'descricao': 'Purê de mandioquinha com camarões salteados',
        'ingredientes': ['mandioquinha', 'camarão', 'alho', 'manteiga', 'salsinha'],
        'beneficios': ['Proteína do camarão', 'Selênio', 'Vitaminas'],
        'riscos': ['Alérgeno: crustáceo', 'Contém lactose', 'Colesterol do camarão']
    },
    'minipolpetonerecheadocomqueijo': {
        'descricao': 'Polpetone de carne recheado com queijo',
        'ingredientes': ['carne moída', 'queijo mussarela', 'ovo', 'farinha de rosca', 'molho de tomate'],
        'beneficios': ['Alto teor proteico', 'Cálcio do queijo'],
        'riscos': ['Contém glúten', 'Contém ovo', 'Contém lactose', 'Gordura saturada']
    },
    'moquecadebanadaterra': {
        'descricao': 'Moqueca com banana da terra',
        'ingredientes': ['peixe', 'banana da terra', 'leite de coco', 'azeite de dendê', 'pimentão', 'tomate'],
        'beneficios': ['Ômega-3', 'Potássio', 'Gorduras boas do dendê'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: coco', 'Calórico']
    },
    'pancetapururuca': {
        'descricao': 'Panceta de porco com pele crocante',
        'ingredientes': ['panceta de porco', 'sal grosso', 'alho', 'ervas'],
        'beneficios': ['Alto teor proteico', 'Colágeno', 'Sabor intenso'],
        'riscos': ['Muito alto em gordura saturada', 'Alto sódio', 'Alto colesterol', 'Muito calórico']
    },
    'pernildecordeiro': {
        'descricao': 'Pernil de cordeiro assado com ervas',
        'ingredientes': ['pernil de cordeiro', 'alecrim', 'alho', 'vinho', 'azeite'],
        'beneficios': ['Proteína de alta qualidade', 'Ferro', 'Zinco', 'Vitaminas B'],
        'riscos': ['Gordura saturada', 'Colesterol', 'Calórico']
    },
    'quiaboempanado': {
        'descricao': 'Quiabo empanado e frito',
        'ingredientes': ['quiabo', 'farinha', 'ovo', 'sal', 'óleo'],
        'beneficios': ['Fibras', 'Vitaminas', 'Ácido fólico'],
        'riscos': ['Contém glúten', 'Contém ovo', 'Fritura']
    },
    'rolinhovietnamita': {
        'descricao': 'Rolinho primavera vietnamita',
        'ingredientes': ['papel de arroz', 'camarão', 'vegetais', 'macarrão de arroz', 'ervas'],
        'beneficios': ['Baixa caloria', 'Proteína do camarão', 'Vegetais frescos'],
        'riscos': ['Alérgeno: crustáceo', 'Pode conter amendoim no molho']
    },
    'salpicaodefrango': {
        'descricao': 'Salada de frango desfiado com maionese e legumes',
        'ingredientes': ['frango desfiado', 'maionese', 'cenoura', 'batata palha', 'milho', 'ervilha'],
        'beneficios': ['Proteína do frango', 'Vitaminas dos legumes'],
        'riscos': ['Alto teor de gordura (maionese)', 'Alérgeno: ovo (maionese)', 'Calórico']
    },
    'sobrecoxaaotandoori': {
        'descricao': 'Sobrecoxa de frango marinada em especiarias tandoori',
        'ingredientes': ['sobrecoxa de frango', 'iogurte', 'garam masala', 'cúrcuma', 'páprica', 'gengibre'],
        'beneficios': ['Proteína', 'Especiarias anti-inflamatórias', 'Probióticos do iogurte'],
        'riscos': ['Contém lactose (iogurte)', 'Especiarias fortes']
    },

    # Fallback padrão
    'default': {
        'descricao': 'Prato preparado com ingredientes frescos',
        'ingredientes': ['Ingredientes variados conforme preparo'],
        'beneficios': ['Consulte informações com o atendente'],
        'riscos': ['Consulte sobre alérgenos específicos']
    }
}


def get_dish_info(slug: str) -> dict:
    """Retorna informações completas do prato"""
    return DISH_INFO.get(slug, DISH_INFO['default'])


def get_dish_name(slug: str) -> str:
    """Retorna o nome correto do prato"""
    return DISH_NAMES.get(slug, format_dish_name_fallback(slug))


def format_dish_name_fallback(slug: str) -> str:
    """Fallback para formatar nomes não mapeados"""
    if not slug:
        return ''
    
    # Substitui padrões comuns
    name = slug.replace('ao', ' ao ').replace('de', ' de ').replace('com', ' com ')
    name = name.replace('sem', ' sem ').replace('_', ' ')
    
    # Remove espaços extras e capitaliza
    name = ' '.join(name.split()).title()
    
    return name


def get_category(slug: str) -> str:
    """Retorna a categoria do prato"""
    return DISH_CATEGORIES.get(slug, 'não classificado')


def get_category_emoji(category: str) -> str:
    """Retorna emoji da categoria"""
    emojis = {
        'vegano': '🌱',
        'vegetariano': '🥬',
        'proteína animal': '🍖',
        'não classificado': '🍽️'
    }
    return emojis.get(category, '🍽️')


def get_nutrition_type(slug: str) -> str:
    """Determina o tipo nutricional do prato"""
    slug_lower = slug.lower()
    
    if 'arroz' in slug_lower:
        return 'arroz'
    elif 'feij' in slug_lower:
        return 'feijao'
    elif 'peixe' in slug_lower or 'bacalhau' in slug_lower or 'atum' in slug_lower or 'camar' in slug_lower:
        return 'peixe'
    elif 'frango' in slug_lower or 'sobrecoxa' in slug_lower:
        return 'frango'
    elif 'carne' in slug_lower or 'maminha' in slug_lower or 'costela' in slug_lower or 'entrecote' in slug_lower or 'panceta' in slug_lower or 'cordeiro' in slug_lower:
        return 'carne'
    elif 'espaguete' in slug_lower or 'nhoque' in slug_lower or 'lasanha' in slug_lower or 'canelone' in slug_lower or 'risone' in slug_lower:
        return 'massa'
    elif 'bolo' in slug_lower or 'mousse' in slug_lower or 'cocada' in slug_lower or 'goiabada' in slug_lower or 'brownie' in slug_lower or 'gelatina' in slug_lower:
        return 'sobremesa'
    elif 'batata' in slug_lower or 'mandioquinha' in slug_lower:
        return 'batata'
    elif any(v in slug_lower for v in ['brocoli', 'cenoura', 'beterraba', 'repolho', 'berinjela', 'abobrinha', 'abobora', 'pepino', 'jilo', 'quiabo']):
        return 'vegetal'
    else:
        return 'default'


def analyze_result(results: List[Dict]) -> Dict:
    """
    Analisa os resultados da busca e decide a resposta.
    
    REGRA PRINCIPAL:
    - Score >= 85% = Confiança ALTA (sem alternativas, sem confirmar)
    - Score >= 50% e < 85% = Confiança MÉDIA (mostrar alternativas)
    - Score < 50% = Confiança BAIXA
    """
    
    if not results or 'error' in results[0]:
        return {
            'identified': False,
            'dish': None,
            'dish_display': None,
            'confidence': 'baixa',
            'score': 0.0,
            'message': 'Não foi possível identificar o prato.',
            'category': None,
            'category_emoji': '❓',
            'alternatives': []
        }
    
    top_result = results[0]
    score = top_result.get('score', 0)
    dish = top_result.get('dish', '')
    
    # Nome correto do prato
    dish_display = get_dish_name(dish)
    
    # Categoria
    category = get_category(dish)
    category_emoji = get_category_emoji(category)
    
    # Informações do prato
    dish_info = get_dish_info(dish)
    
    # Informações nutricionais
    nutrition_type = get_nutrition_type(dish)
    nutrition = DISH_NUTRITION.get(nutrition_type, DISH_NUTRITION['default'])
    
    # DECISÃO DE CONFIANÇA (CORRIGIDA)
    if score >= 0.85:
        # ALTA CONFIANÇA - identificação segura
        return {
            'identified': True,
            'dish': dish,
            'dish_display': dish_display,
            'confidence': 'alta',
            'score': score,
            'message': 'Prato identificado.',
            'category': category,
            'category_emoji': category_emoji,
            'nutrition': nutrition,
            'descricao': dish_info.get('descricao'),
            'ingredientes': dish_info.get('ingredientes'),
            'beneficios': dish_info.get('beneficios'),
            'riscos': dish_info.get('riscos'),
            'alternatives': []  # SEM alternativas quando confiança é alta
        }
    
    elif score >= 0.50:
        # MÉDIA CONFIANÇA - mostrar alternativas
        alternatives = [get_dish_name(r['dish']) for r in results[1:4] if r.get('dish')]
        return {
            'identified': True,
            'dish': dish,
            'dish_display': dish_display,
            'confidence': 'média',
            'score': score,
            'message': 'Provável identificação.',
            'category': category,
            'category_emoji': category_emoji,
            'nutrition': nutrition,
            'descricao': dish_info.get('descricao'),
            'ingredientes': dish_info.get('ingredientes'),
            'beneficios': dish_info.get('beneficios'),
            'riscos': dish_info.get('riscos'),
            'alternatives': alternatives
        }
    
    else:
        # BAIXA CONFIANÇA
        alternatives = [get_dish_name(r['dish']) for r in results[:5] if r.get('dish')]
        return {
            'identified': False,
            'dish': dish,
            'dish_display': dish_display,
            'confidence': 'baixa',
            'score': score,
            'message': 'Identificação incerta.',
            'category': category,
            'category_emoji': category_emoji,
            'nutrition': None,
            'descricao': None,
            'ingredientes': None,
            'beneficios': None,
            'riscos': None,
            'alternatives': alternatives
        }


def get_risk_alert(dish: str, user_restrictions: List[str] = None) -> Optional[str]:
    """
    Verifica se o prato tem riscos para o usuário.
    (Placeholder para funcionalidade Premium)
    """
    # TODO: Implementar cruzamento com base de ingredientes/alérgenos
    return None
