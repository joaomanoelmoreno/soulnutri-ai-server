"""SoulNutri AI - Policy (Política de Decisão)

Define a política de decisão a partir do score de similaridade.
Faixas de confiança:
- alta:   >= 0.85 (identificação segura - SEM alternativas)
- média:  >= 0.50 e < 0.85 (provável, mostrar alternativas)
- baixa:  < 0.50 (incerto)

Baseado na analogia Waze: mostrar o melhor caminho em tempo real.

CIBI SANA - PREMISSAS GASTRONÔMICAS:
- Sem aditivos químicos e alimentos ou bases industrializados
- Legumes e verduras orgânicos
- Peixes e carnes frescos (recebidos a cada 1-2 dias)
- Técnicas: sous vide, vapor, braseamento, banho maria, grelhas, azeite
- Creme de leite fresco, bases e molhos feitos na cozinha
- Especiarias importadas (Índia, Arábia, Israel, China, Japão)
- Ervas frescas orgânicas recebidas diariamente
- Forno combinado ao invés de fritadeira (exceto bolinho de bacalhau)
- Feijão demolhado antes do preparo
- Maple light e Maple Canadense para adoçar
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
    'sobremesa': {'calorias': '180 kcal', 'proteinas': '3g', 'carboidratos': '30g', 'gorduras': '5g'},
    'batata': {'calorias': '90 kcal', 'proteinas': '2g', 'carboidratos': '20g', 'gorduras': '0.1g'},
}

# =============================================================================
# CIBI SANA - AVISOS PADRÃO
# =============================================================================
AVISO_CIBI_SANA = "Cibi Sana: Sem aditivos químicos e alimentos ou bases industrializados."
AVISO_GLUTEN = "Pode haver presença de traços de glúten em alguns preparos."

# =============================================================================
# INFORMAÇÕES DETALHADAS DOS PRATOS - CIBI SANA
# =============================================================================
DISH_INFO = {
    # ===================== VEGANOS =====================
    'aboboraaocurry': {
        'descricao': 'Abóbora orgânica cozida no vapor com especiarias indianas importadas em molho cremoso de leite de coco',
        'ingredientes': ['abóbora orgânica', 'curry indiano importado', 'leite de coco', 'gengibre fresco', 'cúrcuma importada', 'cebola orgânica', 'alho orgânico'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Rico em betacaroteno', 'Antioxidantes naturais', 'Anti-inflamatório natural', 'Baixa caloria', 'Fonte de vitamina A', 'Especiarias com propriedades medicinais'],
        'riscos': ['Pode conter traços de glúten', 'Alérgeno: pode conter coco']
    },
    'alhoporogratinadovegano': {
        'descricao': 'Alho poró orgânico gratinado no forno combinado com creme vegetal e ervas frescas orgânicas',
        'ingredientes': ['alho poró orgânico', 'creme vegetal artesanal', 'ervas frescas orgânicas', 'azeite extravirgem'],
        'tecnica': 'Gratinado em forno combinado',
        'beneficios': ['Prebiótico natural', 'Rico em fibras', 'Baixo teor calórico', 'Fonte de vitamina K', 'Vegetais orgânicos'],
        'riscos': ['Pode conter traços de glúten']
    },
    'arroz7graos': {
        'descricao': 'Mistura artesanal de arroz com grãos integrais e sementes nutritivas',
        'ingredientes': ['arroz integral', 'quinoa', 'linhaça', 'aveia', 'centeio', 'cevada', 'trigo'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Alto teor de fibras', 'Proteína vegetal completa', 'Energia de longa duração', 'Rico em minerais'],
        'riscos': ['Contém glúten (trigo, cevada, centeio)', 'Pode conter traços de glúten']
    },
    'arroz7graoscomfrutassecas': {
        'descricao': 'Arroz 7 grãos enriquecido com frutas secas selecionadas',
        'ingredientes': ['arroz 7 grãos', 'uva passa', 'damasco', 'castanhas', 'amêndoas'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Rico em antioxidantes', 'Energia natural', 'Fibras e proteínas', 'Fonte de ferro'],
        'riscos': ['Contém glúten', 'Alérgeno: oleaginosas', 'Pode conter traços de glúten']
    },
    'arroz7graoscomlegumes': {
        'descricao': 'Arroz 7 grãos salteado com legumes orgânicos frescos',
        'ingredientes': ['arroz 7 grãos', 'cenoura orgânica', 'ervilha', 'milho', 'brócolis orgânico', 'abobrinha orgânica'],
        'tecnica': 'Cozimento e salteado',
        'beneficios': ['Rico em fibras', 'Vitaminas variadas', 'Baixa gordura', 'Refeição completa', 'Vegetais orgânicos'],
        'riscos': ['Contém glúten', 'Pode conter traços de glúten']
    },
    'arrozbranco': {
        'descricao': 'Arroz branco cozido no vapor, acompanhamento clássico preparado artesanalmente',
        'ingredientes': ['arroz branco selecionado', 'sal', 'alho orgânico', 'azeite extravirgem'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Fonte de energia rápida', 'Fácil digestão', 'Sem glúten naturalmente'],
        'riscos': ['Pode conter traços de glúten']
    },
    'arrozde7graoscomamendoas': {
        'descricao': 'Arroz 7 grãos com amêndoas tostadas artesanalmente',
        'ingredientes': ['arroz 7 grãos', 'amêndoas tostadas', 'azeite extravirgem', 'sal', 'ervas frescas orgânicas'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Rico em ômega-3', 'Proteína e fibras', 'Vitamina E das amêndoas'],
        'riscos': ['Contém glúten', 'Alérgeno: amêndoas (oleaginosas)', 'Pode conter traços de glúten']
    },
    'arrozintegral': {
        'descricao': 'Arroz integral rico em fibras e nutrientes, cozido no vapor',
        'ingredientes': ['arroz integral selecionado', 'sal'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Alto teor de fibras', 'Baixo índice glicêmico', 'Rico em vitaminas B', 'Sem glúten'],
        'riscos': ['Pode conter traços de glúten']
    },
    'arrozintlegumes': {
        'descricao': 'Arroz integral salteado com legumes orgânicos variados',
        'ingredientes': ['arroz integral', 'cenoura orgânica', 'brócolis orgânico', 'ervilha', 'abobrinha orgânica', 'azeite extravirgem'],
        'tecnica': 'Cozimento no vapor e salteado',
        'beneficios': ['Refeição completa', 'Rico em fibras e vitaminas', 'Baixo índice glicêmico', 'Vegetais orgânicos'],
        'riscos': ['Pode conter traços de glúten']
    },
    'batataassada': {
        'descricao': 'Batatas assadas em forno combinado com ervas frescas orgânicas aromáticas',
        'ingredientes': ['batata', 'azeite extravirgem', 'alecrim fresco orgânico', 'alho orgânico', 'sal'],
        'tecnica': 'Assado em forno combinado (sem fritura)',
        'beneficios': ['Fonte de potássio', 'Energia complexa', 'Vitamina C', 'Sem glúten', 'Sem fritura'],
        'riscos': ['Pode conter traços de glúten']
    },
    'batatacompaprica': {
        'descricao': 'Batatas temperadas com páprica defumada importada, assadas em forno combinado',
        'ingredientes': ['batata', 'páprica defumada importada', 'azeite extravirgem', 'alho orgânico', 'sal'],
        'tecnica': 'Assado em forno combinado (sem fritura)',
        'beneficios': ['Antioxidantes da páprica', 'Fonte de potássio', 'Energia sustentada', 'Sem fritura'],
        'riscos': ['Pode conter traços de glúten']
    },
    'batatadoce': {
        'descricao': 'Batata doce orgânica assada em forno combinado, naturalmente doce',
        'ingredientes': ['batata doce orgânica'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Baixo índice glicêmico', 'Rica em betacaroteno', 'Fibras', 'Vitamina A', 'Antioxidantes', 'Orgânica'],
        'riscos': ['Pode conter traços de glúten']
    },
    'beringelaaolimao': {
        'descricao': 'Berinjela orgânica grelhada com molho cítrico de limão fresco',
        'ingredientes': ['berinjela orgânica', 'limão fresco', 'azeite extravirgem', 'alho orgânico', 'salsinha orgânica'],
        'tecnica': 'Grelhado na grelha',
        'beneficios': ['Baixíssima caloria', 'Rica em fibras', 'Antioxidantes', 'Ajuda na digestão', 'Vegetal orgânico'],
        'riscos': ['Pode conter traços de glúten']
    },
    'beringelaaocurrykincam': {
        'descricao': 'Berinjela orgânica ao curry indiano importado com especiarias aromáticas',
        'ingredientes': ['berinjela orgânica', 'curry indiano importado', 'leite de coco', 'gengibre fresco', 'coentro orgânico'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Anti-inflamatório', 'Baixa caloria', 'Fibras', 'Especiarias medicinais importadas'],
        'riscos': ['Pode conter traços de glúten', 'Pode conter coco (alérgeno)']
    },
    'beterrabaaobalsamico': {
        'descricao': 'Beterraba orgânica assada em forno combinado com redução de vinagre balsâmico',
        'ingredientes': ['beterraba orgânica', 'vinagre balsâmico', 'azeite extravirgem', 'maple light', 'tomilho orgânico'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Rica em ferro', 'Nitratos naturais', 'Melhora circulação', 'Antioxidantes', 'Adoçado com maple'],
        'riscos': ['Pode conter traços de glúten']
    },
    'bolochocolatevegano': {
        'descricao': 'Bolo de chocolate vegano preparado artesanalmente com cacau de qualidade, adoçado com maple',
        'ingredientes': ['farinha (uso controlado)', 'cacau em pó', 'maple canadense', 'óleo vegetal', 'leite vegetal'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Livre de lactose', 'Antioxidantes do cacau', 'Sem colesterol', 'Adoçado com maple natural'],
        'riscos': ['Contém glúten', 'Pode conter traços de glúten']
    },
    'brocolis': {
        'descricao': 'Brócolis orgânico fresco cozido no vapor, nutritivo e saboroso',
        'ingredientes': ['brócolis orgânico fresco', 'sal', 'azeite extravirgem'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Superalimento', 'Rico em vitamina C e K', 'Fibras', 'Cálcio', 'Anticancerígeno', 'Orgânico'],
        'riscos': ['Pode conter traços de glúten']
    },
    'caponata': {
        'descricao': 'Prato siciliano de berinjela orgânica com tomate sem pele e especiarias importadas',
        'ingredientes': ['berinjela orgânica', 'tomate sem pele', 'cebola orgânica', 'aipo orgânico', 'azeitonas', 'alcaparras', 'vinagre'],
        'tecnica': 'Refogado em azeite',
        'beneficios': ['Rico em fibras', 'Antioxidantes', 'Baixa caloria', 'Tomate sem pele para melhor digestão'],
        'riscos': ['Pode conter traços de glúten']
    },
    'carpacciodeabobrinha': {
        'descricao': 'Finas fatias de abobrinha orgânica crua com azeite extravirgem e limão',
        'ingredientes': ['abobrinha orgânica', 'azeite extravirgem', 'limão fresco', 'sal', 'rúcula orgânica'],
        'tecnica': 'Preparo a frio (crudo)',
        'beneficios': ['Baixíssima caloria', 'Hidratante', 'Rico em potássio', 'Fácil digestão', 'Orgânico'],
        'riscos': ['Pode conter traços de glúten']
    },
    'cebola': {
        'descricao': 'Cebola orgânica caramelizada lentamente em azeite',
        'ingredientes': ['cebola orgânica', 'azeite extravirgem', 'sal'],
        'tecnica': 'Caramelização lenta em azeite',
        'beneficios': ['Prebiótico', 'Anti-inflamatório', 'Rico em antioxidantes', 'Melhora imunidade'],
        'riscos': ['Pode conter traços de glúten']
    },
    'cenourapalito': {
        'descricao': 'Cenouras orgânicas cortadas em palito, cozidas no vapor',
        'ingredientes': ['cenoura orgânica', 'sal'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Rica em betacaroteno', 'Vitamina A', 'Boa para visão', 'Fibras', 'Baixa caloria', 'Orgânica'],
        'riscos': ['Pode conter traços de glúten']
    },
    'cuscuzmarroquino': {
        'descricao': 'Semolina de trigo cozida no vapor com especiarias importadas do Oriente Médio',
        'ingredientes': ['semolina de trigo', 'caldo de legumes artesanal', 'azeite extravirgem', 'especiarias importadas'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Fonte de carboidratos', 'Rápido preparo', 'Especiarias importadas'],
        'riscos': ['Contém glúten', 'Pode conter traços de glúten']
    },
    'ervadocecomlaranja': {
        'descricao': 'Erva doce (funcho) orgânica salteada em azeite com suco de laranja fresco',
        'ingredientes': ['erva doce orgânica', 'suco de laranja fresco', 'azeite extravirgem', 'sal'],
        'tecnica': 'Salteado em azeite',
        'beneficios': ['Digestivo natural', 'Rico em vitamina C', 'Baixa caloria', 'Anti-inflamatório', 'Orgânico'],
        'riscos': ['Pode conter traços de glúten']
    },
    'farofadebananadaterra': {
        'descricao': 'Farofa artesanal com banana da terra assada em forno combinado (sem fritura)',
        'ingredientes': ['farinha de mandioca', 'banana da terra', 'cebola orgânica', 'azeite extravirgem', 'sal'],
        'tecnica': 'Banana assada em forno combinado (sem fritura)',
        'beneficios': ['Fonte de potássio', 'Energia', 'Sem glúten (farinha de mandioca)', 'Sem fritura'],
        'riscos': ['Pode conter traços de glúten']
    },
    'feijaocariocasemcarne': {
        'descricao': 'Feijão carioca demolhado e cozido em caldo temperado artesanal, versão vegetariana',
        'ingredientes': ['feijão carioca demolhado', 'alho orgânico', 'cebola orgânica', 'louro', 'sal'],
        'tecnica': 'Feijão demolhado + cozimento tradicional',
        'beneficios': ['Rico em fibras', 'Proteína vegetal', 'Fonte de ferro', 'Baixa gordura', 'Feijão demolhado para melhor digestão'],
        'riscos': ['Pode conter traços de glúten']
    },
    'feijaopretosemcarne': {
        'descricao': 'Feijão preto demolhado e cozido sem carne, rico e saboroso',
        'ingredientes': ['feijão preto demolhado', 'alho orgânico', 'cebola orgânica', 'louro', 'sal'],
        'tecnica': 'Feijão demolhado + cozimento tradicional',
        'beneficios': ['Alto teor de fibras', 'Proteína vegetal', 'Rico em ferro', 'Antioxidantes', 'Demolhado'],
        'riscos': ['Pode conter traços de glúten']
    },
    'graodebicotomatesecoespinafre': {
        'descricao': 'Grão de bico sem pele salteado com tomate seco e espinafre orgânico',
        'ingredientes': ['grão de bico sem pele', 'tomate seco', 'espinafre orgânico', 'alho orgânico', 'azeite extravirgem'],
        'tecnica': 'Grão de bico sem pele + salteado em azeite',
        'beneficios': ['Proteína completa', 'Rico em ferro', 'Fibras', 'Vitaminas A e K', 'Sem pele para melhor digestão'],
        'riscos': ['Pode conter traços de glúten']
    },
    'hamburguervegano': {
        'descricao': 'Hambúrguer de proteína vegetal artesanal com especiarias importadas, grelhado',
        'ingredientes': ['proteína de grão de bico sem pele', 'cebola orgânica', 'alho orgânico', 'especiarias importadas'],
        'tecnica': 'Grelhado na grelha (sem fritura)',
        'beneficios': ['Proteína vegetal', 'Sem colesterol', 'Fibras', 'Sem fritura'],
        'riscos': ['Pode conter traços de glúten']
    },
    'lentilhacomtofu': {
        'descricao': 'Lentilha cozida com cubos de tofu temperado com especiarias indianas importadas',
        'ingredientes': ['lentilha', 'tofu', 'tomate sem pele', 'cebola orgânica', 'curry indiano importado', 'coentro orgânico'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Proteína completa', 'Rico em ferro', 'Fibras', 'Baixa gordura', 'Especiarias importadas'],
        'riscos': ['Pode conter traços de glúten', 'Soja (tofu) pode ser alérgeno']
    },
    'molhovinagrete': {
        'descricao': 'Molho fresco de tomate sem pele, cebola orgânica e pimentão picados',
        'ingredientes': ['tomate sem pele', 'cebola orgânica', 'pimentão orgânico', 'vinagre', 'azeite extravirgem', 'coentro orgânico'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Baixíssima caloria', 'Rico em vitamina C', 'Antioxidantes', 'Fresco', 'Orgânico'],
        'riscos': ['Pode conter traços de glúten']
    },
    'repolho': {
        'descricao': 'Repolho orgânico refogado em azeite',
        'ingredientes': ['repolho orgânico', 'sal', 'azeite extravirgem'],
        'tecnica': 'Refogado em azeite',
        'beneficios': ['Baixíssima caloria', 'Rico em vitamina C', 'Fibras', 'Anticancerígeno', 'Orgânico'],
        'riscos': ['Pode conter traços de glúten']
    },
    'saladadefeijaobranco': {
        'descricao': 'Salada fria de feijão branco demolhado com ervas frescas orgânicas',
        'ingredientes': ['feijão branco demolhado', 'tomate sem pele', 'cebola orgânica', 'salsinha orgânica', 'azeite extravirgem', 'limão'],
        'tecnica': 'Feijão demolhado + preparo a frio',
        'beneficios': ['Proteína vegetal', 'Fibras', 'Vitaminas', 'Baixa gordura', 'Demolhado'],
        'riscos': ['Pode conter traços de glúten']
    },
    'tabuledequinoa': {
        'descricao': 'Salada libanesa com quinoa, ervas frescas orgânicas e especiarias do Oriente Médio',
        'ingredientes': ['quinoa', 'tomate sem pele', 'pepino orgânico', 'hortelã orgânica', 'salsinha orgânica', 'limão', 'azeite extravirgem'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Proteína completa', 'Sem glúten', 'Rico em fibras', 'Vitaminas', 'Ervas orgânicas'],
        'riscos': ['Pode conter traços de glúten']
    },
    'umamidetomate': {
        'descricao': 'Tomates sem pele concentrados com sabor umami intenso',
        'ingredientes': ['tomate sem pele', 'azeite extravirgem', 'alho orgânico', 'ervas orgânicas', 'sal'],
        'tecnica': 'Concentração lenta',
        'beneficios': ['Licopeno (antioxidante)', 'Baixa caloria', 'Vitamina C', 'Tomate sem pele'],
        'riscos': ['Pode conter traços de glúten']
    },

    # ===================== VEGETARIANOS =====================
    'brocoliscomparmesao': {
        'descricao': 'Brócolis orgânico cozido no vapor e gratinado com queijo parmesão',
        'ingredientes': ['brócolis orgânico', 'queijo parmesão', 'azeite extravirgem', 'alho orgânico'],
        'tecnica': 'Vapor + gratinado em forno combinado',
        'beneficios': ['Rico em cálcio', 'Vitamina C e K', 'Proteína do queijo', 'Orgânico'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'brocoliscouveflorgratinado': {
        'descricao': 'Brócolis e couve-flor orgânicos no vapor, gratinados com molho branco artesanal',
        'ingredientes': ['brócolis orgânico', 'couve-flor orgânica', 'queijo', 'creme de leite fresco', 'noz-moscada importada'],
        'tecnica': 'Vapor + gratinado em forno combinado',
        'beneficios': ['Rico em fibras', 'Cálcio', 'Vitaminas C e K', 'Molho artesanal', 'Creme fresco'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'brocolisgratinado': {
        'descricao': 'Brócolis orgânico ao forno combinado com queijo gratinado e creme fresco',
        'ingredientes': ['brócolis orgânico', 'queijo mussarela', 'creme de leite fresco', 'parmesão'],
        'tecnica': 'Vapor + gratinado em forno combinado',
        'beneficios': ['Rico em vitamina C', 'Fibras', 'Cálcio do queijo', 'Antioxidantes', 'Creme fresco'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'canelonedeespinafre': {
        'descricao': 'Massa recheada com espinafre orgânico e ricota fresca, molho artesanal',
        'ingredientes': ['massa de canelone', 'espinafre orgânico', 'ricota fresca', 'molho de tomate artesanal', 'queijo'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Rico em ferro', 'Cálcio', 'Vitamina A', 'Proteína', 'Molho artesanal'],
        'riscos': ['Contém glúten', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'carpacciodelaranja': {
        'descricao': 'Fatias finas de laranja fresca com maple canadense e hortelã orgânica',
        'ingredientes': ['laranja fresca', 'maple canadense', 'hortelã orgânica', 'canela importada'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Rico em vitamina C', 'Antioxidantes', 'Hidratante', 'Adoçado com maple natural'],
        'riscos': ['Pode conter traços de glúten']
    },
    'carpacciodeperaruculaeamendoas': {
        'descricao': 'Fatias de pera fresca com rúcula orgânica e amêndoas tostadas',
        'ingredientes': ['pera fresca', 'rúcula orgânica', 'amêndoas tostadas', 'azeite extravirgem', 'queijo parmesão'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Rico em fibras', 'Vitamina E', 'Antioxidantes', 'Ômega-3', 'Orgânico'],
        'riscos': ['Alérgeno: amêndoas', 'Contém lactose (queijo)', 'Pode conter traços de glúten']
    },
    'cenouraaoiogurte': {
        'descricao': 'Cenoura orgânica ralada com molho de iogurte fresco artesanal',
        'ingredientes': ['cenoura orgânica', 'iogurte natural fresco', 'maple light', 'gengibre fresco'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Probióticos', 'Vitamina A', 'Cálcio', 'Digestivo', 'Adoçado com maple'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'cocada': {
        'descricao': 'Doce tradicional de coco artesanal, adoçado com maple canadense',
        'ingredientes': ['coco ralado fresco', 'maple canadense', 'leite condensado artesanal'],
        'tecnica': 'Banho maria',
        'beneficios': ['Energia', 'Fibras do coco', 'Sabor tradicional', 'Adoçado com maple'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'cuscuzdetapioca': {
        'descricao': 'Cuscuz doce de tapioca artesanal com coco, adoçado com maple',
        'ingredientes': ['tapioca', 'leite de coco', 'maple canadense', 'coco ralado fresco'],
        'tecnica': 'Vapor + banho maria',
        'beneficios': ['Sem glúten', 'Fonte de energia', 'Tradição brasileira', 'Adoçado com maple'],
        'riscos': ['Pode conter coco (alérgeno)', 'Pode conter traços de glúten']
    },
    'dadinhodetapioca': {
        'descricao': 'Cubos de tapioca artesanal com queijo coalho, assados em forno combinado',
        'ingredientes': ['tapioca', 'queijo coalho', 'sal'],
        'tecnica': 'Assado em forno combinado (sem fritura)',
        'beneficios': ['Sem glúten', 'Proteína do queijo', 'Petisco saboroso', 'Sem fritura'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'espaguete': {
        'descricao': 'Massa italiana artesanal servida com molho de tomate feito em nossa cozinha',
        'ingredientes': ['massa de trigo', 'molho de tomate artesanal', 'azeite extravirgem', 'alho orgânico', 'manjericão orgânico'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Fonte de carboidratos', 'Energia', 'Molho artesanal feito na cozinha'],
        'riscos': ['Contém glúten', 'Pode conter traços de glúten']
    },
    'gelatinadecereja': {
        'descricao': 'Sobremesa de gelatina artesanal sabor cereja',
        'ingredientes': ['gelatina', 'suco de cereja', 'maple light'],
        'tecnica': 'Refrigeração',
        'beneficios': ['Baixa caloria', 'Colágeno', 'Hidratante', 'Adoçado com maple'],
        'riscos': ['Pode conter traços de glúten', 'Gelatina de origem animal']
    },
    'goiabada': {
        'descricao': 'Doce tradicional de goiaba artesanal em bloco',
        'ingredientes': ['goiaba fresca', 'açúcar', 'maple canadense'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Rico em vitamina C', 'Fibras', 'Energia', 'Artesanal'],
        'riscos': ['Pode conter traços de glúten']
    },
    'jiloempanado': {
        'descricao': 'Jiló orgânico empanado artesanalmente, assado em forno combinado (sem fritura)',
        'ingredientes': ['jiló orgânico', 'farinha (uso controlado)', 'ovo', 'sal'],
        'tecnica': 'Empanado e assado em forno combinado (SEM FRITURA)',
        'beneficios': ['Fibras', 'Vitaminas', 'Ácido fólico', 'Sem fritura', 'Orgânico'],
        'riscos': ['Contém glúten (controlado)', 'Contém ovo', 'Pode conter traços de glúten']
    },
    'lasanhadeespinafre': {
        'descricao': 'Lasanha verde com camadas de espinafre orgânico, ricota fresca e molho branco artesanal',
        'ingredientes': ['massa de lasanha', 'espinafre orgânico', 'ricota fresca', 'mussarela', 'molho branco artesanal'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Rico em ferro', 'Cálcio', 'Proteína', 'Vitaminas', 'Molhos artesanais', 'Creme fresco'],
        'riscos': ['Contém glúten', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'lasanhadeportobello': {
        'descricao': 'Lasanha com cogumelos portobello frescos e molho branco artesanal',
        'ingredientes': ['massa', 'cogumelo portobello fresco', 'queijo', 'molho branco artesanal', 'cebola orgânica'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Proteína do cogumelo', 'Vitamina D', 'Fibras', 'Umami natural', 'Molho artesanal'],
        'riscos': ['Contém glúten', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'mandioquinhaassada': {
        'descricao': 'Mandioquinha assada em forno combinado com ervas frescas orgânicas',
        'ingredientes': ['mandioquinha', 'azeite extravirgem', 'alecrim orgânico', 'sal'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Fácil digestão', 'Fonte de potássio', 'Vitaminas', 'Sem glúten', 'Sem fritura'],
        'riscos': ['Pode conter traços de glúten']
    },
    'moussedemaracuja': {
        'descricao': 'Mousse cremoso de maracujá fresco com creme de leite fresco, adoçado com maple',
        'ingredientes': ['maracujá fresco', 'creme de leite fresco', 'leite condensado artesanal', 'maple light'],
        'tecnica': 'Banho maria + refrigeração',
        'beneficios': ['Rico em vitamina C', 'Relaxante natural', 'Sabor tropical', 'Creme fresco', 'Adoçado com maple'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'moussedemorango': {
        'descricao': 'Mousse cremoso de morango fresco com creme de leite fresco, adoçado com maple',
        'ingredientes': ['morango fresco', 'creme de leite fresco', 'leite condensado artesanal', 'maple light'],
        'tecnica': 'Banho maria + refrigeração',
        'beneficios': ['Antioxidantes', 'Vitamina C', 'Refrescante', 'Creme fresco', 'Adoçado com maple'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'nhoqueaosugo': {
        'descricao': 'Nhoque de batata artesanal com molho de tomate feito em nossa cozinha',
        'ingredientes': ['batata', 'farinha (uso controlado)', 'ovo', 'molho de tomate artesanal', 'manjericão orgânico'],
        'tecnica': 'Preparo artesanal',
        'beneficios': ['Fonte de carboidratos', 'Energia', 'Potássio da batata', 'Molho artesanal'],
        'riscos': ['Contém glúten (controlado)', 'Contém ovo', 'Pode conter traços de glúten']
    },
    'pepinocomiogurte': {
        'descricao': 'Pepino orgânico fresco com molho de iogurte artesanal (tipo tzatziki)',
        'ingredientes': ['pepino orgânico', 'iogurte fresco', 'alho orgânico', 'hortelã orgânica', 'azeite extravirgem'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Hidratante', 'Probióticos', 'Baixíssima caloria', 'Refrescante', 'Orgânico'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'risoneaopesto': {
        'descricao': 'Massa risone com molho pesto artesanal de manjericão orgânico',
        'ingredientes': ['massa risone', 'manjericão orgânico', 'parmesão', 'pinoli', 'azeite extravirgem', 'alho orgânico'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Antioxidantes', 'Gorduras boas do azeite', 'Sabor aromático', 'Pesto artesanal', 'Ervas orgânicas'],
        'riscos': ['Contém glúten', 'Contém lactose', 'Alérgeno: pinoli (oleaginosa)', 'Pode conter traços de glúten']
    },
    'bananacaramelizada': {
        'descricao': 'Banana grelhada com maple canadense caramelizado',
        'ingredientes': ['banana', 'maple canadense', 'manteiga fresca', 'canela importada'],
        'tecnica': 'Grelhado + caramelização',
        'beneficios': ['Potássio', 'Energia', 'Sabor doce natural', 'Adoçado com maple'],
        'riscos': ['Contém lactose (manteiga)', 'Pode conter traços de glúten']
    },
    'bolobrownie': {
        'descricao': 'Bolo denso de chocolate artesanal tipo brownie, adoçado com maple',
        'ingredientes': ['chocolate', 'manteiga fresca', 'maple canadense', 'ovos', 'farinha (uso controlado)', 'nozes'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Antioxidantes do cacau', 'Energia', 'Sabor intenso', 'Adoçado com maple'],
        'riscos': ['Contém glúten (controlado)', 'Contém ovo', 'Contém lactose', 'Alérgeno: nozes', 'Pode conter traços de glúten']
    },
    'bolodegengibre': {
        'descricao': 'Bolo aromático de gengibre fresco com especiarias importadas, adoçado com maple',
        'ingredientes': ['farinha (uso controlado)', 'gengibre fresco', 'maple canadense', 'ovos', 'manteiga fresca', 'especiarias importadas'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Anti-inflamatório', 'Digestivo', 'Sabor único', 'Especiarias importadas', 'Adoçado com maple'],
        'riscos': ['Contém glúten (controlado)', 'Contém ovo', 'Contém lactose', 'Pode conter traços de glúten']
    },

    # ===================== PROTEÍNA ANIMAL =====================
    'almondegasmolhosugo': {
        'descricao': 'Almôndegas de carne bovina fresca ao molho de tomate artesanal feito em nossa cozinha',
        'ingredientes': ['carne bovina fresca', 'cebola orgânica', 'alho orgânico', 'ovo', 'farinha (uso controlado)', 'molho de tomate artesanal'],
        'tecnica': 'Braseado',
        'beneficios': ['Rica em proteína', 'Ferro', 'Vitaminas B', 'Zinco', 'Carne fresca', 'Molho artesanal'],
        'riscos': ['Contém glúten (controlado)', 'Contém ovo', 'Pode conter traços de glúten']
    },
    'almdegasmolhosugo': {
        'descricao': 'Almôndegas de carne bovina fresca ao molho de tomate artesanal feito em nossa cozinha',
        'ingredientes': ['carne bovina fresca', 'cebola orgânica', 'alho orgânico', 'ovo', 'farinha (uso controlado)', 'molho de tomate artesanal'],
        'tecnica': 'Braseado',
        'beneficios': ['Rica em proteína', 'Ferro', 'Vitaminas B', 'Zinco', 'Carne fresca', 'Molho artesanal'],
        'riscos': ['Contém glúten (controlado)', 'Contém ovo', 'Pode conter traços de glúten']
    },
    'atumaogergelim': {
        'descricao': 'Atum fresco (recebido a cada 1-2 dias) selado com crosta de gergelim importado',
        'ingredientes': ['atum fresco', 'gergelim importado', 'shoyu', 'gengibre fresco', 'wasabi importado do Japão'],
        'tecnica': 'Selado na grelha',
        'beneficios': ['Rico em ômega-3', 'Proteína magra', 'Selênio', 'Vitamina D', 'Peixe fresco', 'Especiarias japonesas'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: gergelim', 'Pode conter traços de glúten']
    },
    'bacalhaucomnatas': {
        'descricao': 'Bacalhau fresco desfiado gratinado com creme de leite fresco artesanal',
        'ingredientes': ['bacalhau fresco', 'batata', 'creme de leite fresco', 'cebola orgânica', 'alho orgânico', 'azeitonas'],
        'tecnica': 'Gratinado em forno combinado',
        'beneficios': ['Proteína de alta qualidade', 'Ômega-3', 'Cálcio', 'Peixe fresco', 'Creme fresco'],
        'riscos': ['Alérgeno: peixe', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'bacalhaugomesdesa': {
        'descricao': 'Prato tradicional português de bacalhau fresco com batatas e ovos',
        'ingredientes': ['bacalhau fresco', 'batata', 'cebola orgânica', 'ovos', 'azeitonas', 'azeite extravirgem'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Rico em proteína', 'Ômega-3', 'Vitaminas B12 e D', 'Peixe fresco'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: ovo', 'Pode conter traços de glúten']
    },
    'baiaodedois': {
        'descricao': 'Prato típico nordestino com arroz e feijão-de-corda demolhado cozidos juntos',
        'ingredientes': ['arroz', 'feijão-de-corda demolhado', 'bacon artesanal', 'queijo coalho', 'manteiga fresca', 'temperos'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Rico em proteínas', 'Fonte de fibras', 'Energia de longa duração', 'Feijão demolhado'],
        'riscos': ['Contém lactose (queijo)', 'Pode conter traços de glúten']
    },
    'bolinhodebacalhau': {
        'descricao': 'Bolinho artesanal de bacalhau fresco com batata - ÚNICO ITEM FRITO',
        'ingredientes': ['bacalhau fresco', 'batata', 'ovo', 'cebola orgânica', 'salsinha orgânica'],
        'tecnica': 'Frito em óleo (ÚNICA EXCEÇÃO de fritura)',
        'beneficios': ['Proteína', 'Ômega-3', 'Sabor tradicional', 'Peixe fresco'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: ovo', 'Fritura', 'Pode conter traços de glúten']
    },
    'cestinhasdecamarao': {
        'descricao': 'Cestinhas assadas em forno combinado recheadas com camarão fresco',
        'ingredientes': ['camarão fresco', 'massa wonton', 'cream cheese artesanal', 'cebolinha orgânica'],
        'tecnica': 'Assado em forno combinado (sem fritura)',
        'beneficios': ['Proteína magra', 'Selênio', 'Zinco', 'Camarão fresco', 'Sem fritura'],
        'riscos': ['Alérgeno: crustáceo (camarão)', 'Contém lactose', 'Contém glúten', 'Pode conter traços de glúten']
    },
    'cevicheperuano': {
        'descricao': 'Peixe fresco (recebido a cada 1-2 dias) marinado em limão com cebola roxa orgânica',
        'ingredientes': ['peixe branco fresco', 'limão fresco', 'cebola roxa orgânica', 'coentro orgânico', 'pimenta importada', 'milho'],
        'tecnica': 'Marinado a frio (crudo)',
        'beneficios': ['Proteína magra', 'Vitamina C', 'Ômega-3', 'Baixa caloria', 'Peixe fresco'],
        'riscos': ['Alérgeno: peixe', 'Pode conter traços de glúten']
    },
    'costelinhacibisana': {
        'descricao': 'Costelinha suína preparada sous vide e finalizada na grelha com molho especial artesanal',
        'ingredientes': ['costela de porco fresca', 'alho orgânico', 'maple canadense', 'shoyu', 'gengibre fresco'],
        'tecnica': 'Sous vide + finalização na grelha',
        'beneficios': ['Alto teor proteico', 'Vitaminas B', 'Colágeno', 'Carne fresca', 'Técnica sous vide', 'Adoçado com maple'],
        'riscos': ['Pode conter traços de glúten']
    },
    'entrecotegrelhado': {
        'descricao': 'Corte nobre de carne bovina fresca grelhado na grelha',
        'ingredientes': ['entrecôte bovino fresco', 'sal grosso', 'pimenta importada', 'alho orgânico'],
        'tecnica': 'Grelhado na grelha',
        'beneficios': ['Alto teor proteico', 'Rico em ferro e zinco', 'Vitaminas B12', 'Carne fresca'],
        'riscos': ['Pode conter traços de glúten']
    },
    'escondidinhodecarneseca': {
        'descricao': 'Purê de mandioca artesanal com carne seca desfiada gratinada em forno combinado',
        'ingredientes': ['mandioca', 'carne seca', 'queijo', 'manteiga fresca', 'creme de leite fresco'],
        'tecnica': 'Gratinado em forno combinado',
        'beneficios': ['Alto teor proteico', 'Energia', 'Sabor intenso', 'Creme fresco'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'farofadebacon': {
        'descricao': 'Farofa artesanal com bacon de preparo próprio',
        'ingredientes': ['farinha de mandioca', 'bacon artesanal', 'cebola orgânica', 'manteiga fresca', 'ovos'],
        'tecnica': 'Preparo tradicional',
        'beneficios': ['Energia', 'Proteína do bacon', 'Sabor defumado', 'Bacon artesanal'],
        'riscos': ['Contém ovo', 'Pode conter traços de glúten']
    },
    'feijaopretocomcarne': {
        'descricao': 'Feijão preto demolhado cozido com carne bovina fresca',
        'ingredientes': ['feijão preto demolhado', 'carne bovina fresca', 'alho orgânico', 'cebola orgânica', 'louro'],
        'tecnica': 'Feijão demolhado + cozimento tradicional',
        'beneficios': ['Rico em proteína', 'Ferro', 'Fibras', 'Feijão demolhado', 'Carne fresca'],
        'riscos': ['Pode conter traços de glúten']
    },
    'feijaotropeiro': {
        'descricao': 'Prato mineiro tradicional com feijão demolhado, bacon artesanal e couve orgânica',
        'ingredientes': ['feijão demolhado', 'bacon artesanal', 'linguiça artesanal', 'farinha de mandioca', 'ovos', 'couve orgânica'],
        'tecnica': 'Preparo tradicional',
        'beneficios': ['Muito proteico', 'Energia', 'Tradição mineira', 'Feijão demolhado', 'Couve orgânica'],
        'riscos': ['Contém ovo', 'Pode conter traços de glúten']
    },
    'figadoacebolado': {
        'descricao': 'Fígado bovino fresco grelhado com cebolas orgânicas',
        'ingredientes': ['fígado bovino fresco', 'cebola orgânica', 'alho orgânico', 'sal', 'azeite extravirgem'],
        'tecnica': 'Grelhado na grelha',
        'beneficios': ['Riquíssimo em ferro', 'Vitamina A', 'Vitamina B12', 'Proteína', 'Fígado fresco'],
        'riscos': ['Pode conter traços de glúten']
    },
    'filedefrangoaparmegiana': {
        'descricao': 'Filé de frango sous vide, empanado artesanalmente e finalizado em forno combinado',
        'ingredientes': ['peito de frango fresco', 'farinha (uso controlado)', 'ovo', 'molho de tomate artesanal', 'mussarela', 'presunto'],
        'tecnica': 'Sous vide + empanado assado em forno combinado (SEM FRITURA)',
        'beneficios': ['Alto teor proteico', 'Cálcio do queijo', 'Frango fresco', 'Sous vide', 'Sem fritura'],
        'riscos': ['Contém glúten (controlado)', 'Contém ovo', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'filedepeixeaomisso': {
        'descricao': 'Filé de peixe fresco (recebido a cada 1-2 dias) ao vapor com molho de missô japonês',
        'ingredientes': ['peixe branco fresco', 'missô importado do Japão', 'saquê', 'gengibre fresco', 'cebolinha orgânica'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Proteína magra', 'Ômega-3', 'Probióticos do missô', 'Peixe fresco', 'Ingredientes japoneses'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: soja (missô)', 'Pode conter traços de glúten']
    },
    'filedepeixeaomolhodelimao': {
        'descricao': 'Filé de peixe fresco ao vapor com molho cítrico de limão e manteiga fresca',
        'ingredientes': ['peixe branco fresco', 'limão fresco', 'manteiga fresca', 'alcaparras', 'salsinha orgânica'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Rico em ômega-3', 'Proteína magra', 'Baixa caloria', 'Bom para coração', 'Peixe fresco'],
        'riscos': ['Alérgeno: peixe', 'Contém lactose (manteiga)', 'Pode conter traços de glúten']
    },
    'filedepeixeaomolhomisso': {
        'descricao': 'Filé de peixe fresco ao vapor com molho missô importado',
        'ingredientes': ['peixe fresco', 'missô importado do Japão', 'gengibre fresco', 'cebolinha orgânica', 'gergelim importado'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Proteína magra', 'Ômega-3', 'Probióticos', 'Peixe fresco', 'Ingredientes importados'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: soja', 'Alérgeno: gergelim', 'Pode conter traços de glúten']
    },
    'filedepeixemolhoconfit': {
        'descricao': 'Filé de peixe fresco ao vapor com tomate sem pele confit',
        'ingredientes': ['peixe fresco', 'tomate sem pele', 'azeite extravirgem', 'alho orgânico', 'ervas orgânicas'],
        'tecnica': 'Cozimento no vapor + tomate confit em azeite',
        'beneficios': ['Proteína magra', 'Ômega-3', 'Licopeno', 'Baixa caloria', 'Peixe fresco', 'Tomate sem pele'],
        'riscos': ['Alérgeno: peixe', 'Pode conter traços de glúten']
    },
    'filedepeixemolhofrutassecas': {
        'descricao': 'Filé de peixe fresco ao vapor com molho artesanal de frutas secas',
        'ingredientes': ['peixe fresco', 'uva passa', 'damasco', 'vinho branco', 'manteiga fresca'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Ômega-3', 'Antioxidantes das frutas', 'Proteína', 'Peixe fresco', 'Molho artesanal'],
        'riscos': ['Alérgeno: peixe', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'frangocremedelimaosalnegro': {
        'descricao': 'Frango sous vide ao creme de limão com sal negro do Havaí importado',
        'ingredientes': ['frango fresco', 'creme de leite fresco', 'limão fresco', 'sal negro do Havaí', 'ervas orgânicas'],
        'tecnica': 'Sous vide',
        'beneficios': ['Proteína magra', 'Vitamina C', 'Minerais do sal negro', 'Frango fresco', 'Técnica sous vide', 'Creme fresco'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'hamburgerdecarne': {
        'descricao': 'Hambúrguer artesanal de carne bovina fresca, grelhado',
        'ingredientes': ['carne bovina fresca moída', 'sal', 'pimenta importada', 'cebola orgânica'],
        'tecnica': 'Grelhado na grelha',
        'beneficios': ['Alto teor proteico', 'Ferro', 'Zinco', 'Vitaminas B', 'Carne fresca', 'Artesanal'],
        'riscos': ['Pode conter traços de glúten']
    },
    'kibe': {
        'descricao': 'Bolinho de origem árabe de carne fresca e trigo, assado em forno combinado',
        'ingredientes': ['carne moída fresca', 'trigo para quibe', 'cebola orgânica', 'hortelã orgânica', 'especiarias importadas da Arábia'],
        'tecnica': 'Assado em forno combinado (sem fritura)',
        'beneficios': ['Proteína', 'Ferro', 'Fibras do trigo', 'Carne fresca', 'Especiarias árabes', 'Sem fritura'],
        'riscos': ['Contém glúten', 'Pode conter traços de glúten']
    },
    'maminhaaomolhomongolia': {
        'descricao': 'Maminha bovina fresca sous vide ao molho agridoce mongoliano com maple',
        'ingredientes': ['maminha fresca', 'shoyu', 'gengibre fresco', 'alho orgânico', 'maple canadense', 'cebolinha orgânica'],
        'tecnica': 'Sous vide + finalização',
        'beneficios': ['Alto teor proteico', 'Ferro', 'Zinco', 'Carne fresca', 'Sous vide', 'Adoçado com maple'],
        'riscos': ['Pode conter traços de glúten']
    },
    'maminhaaomolhomostarda': {
        'descricao': 'Corte bovino nobre fresco preparado sous vide com molho de mostarda e creme fresco',
        'ingredientes': ['maminha bovina fresca', 'mostarda', 'creme de leite fresco', 'vinho branco'],
        'tecnica': 'Sous vide',
        'beneficios': ['Alto teor proteico', 'Rico em ferro e zinco', 'Vitaminas do complexo B', 'Carne fresca', 'Sous vide', 'Creme fresco'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'maminhamolhocebola': {
        'descricao': 'Maminha fresca sous vide com molho de cebola orgânica caramelizada',
        'ingredientes': ['maminha fresca', 'cebola orgânica', 'vinho', 'manteiga fresca', 'tomilho orgânico'],
        'tecnica': 'Sous vide + caramelização',
        'beneficios': ['Proteína', 'Ferro', 'Zinco', 'Sabor intenso', 'Carne fresca', 'Sous vide'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'maminhanacervejapreta': {
        'descricao': 'Maminha bovina fresca braseada na cerveja preta',
        'ingredientes': ['maminha fresca', 'cerveja preta', 'cebola orgânica', 'alho orgânico', 'louro'],
        'tecnica': 'Braseamento',
        'beneficios': ['Proteína', 'Ferro', 'Carne macia', 'Sabor intenso', 'Carne fresca', 'Técnica de braseamento'],
        'riscos': ['Contém álcool residual', 'Pode conter traços de glúten']
    },
    'mandioquinhacomcamarao': {
        'descricao': 'Purê de mandioquinha artesanal com camarões frescos salteados em azeite',
        'ingredientes': ['mandioquinha', 'camarão fresco', 'alho orgânico', 'manteiga fresca', 'salsinha orgânica'],
        'tecnica': 'Purê artesanal + camarão salteado em azeite',
        'beneficios': ['Proteína do camarão', 'Selênio', 'Vitaminas', 'Camarão fresco'],
        'riscos': ['Alérgeno: crustáceo', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'minipolpetonerecheadocomqueijo': {
        'descricao': 'Polpetone artesanal de carne fresca recheado com queijo',
        'ingredientes': ['carne moída fresca', 'queijo mussarela', 'ovo', 'farinha (uso controlado)', 'molho de tomate artesanal'],
        'tecnica': 'Braseado',
        'beneficios': ['Alto teor proteico', 'Cálcio do queijo', 'Carne fresca', 'Molho artesanal'],
        'riscos': ['Contém glúten (controlado)', 'Contém ovo', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'moquecadebanadaterra': {
        'descricao': 'Moqueca de peixe fresco com banana da terra e leite de coco',
        'ingredientes': ['peixe fresco', 'banana da terra', 'leite de coco', 'azeite de dendê', 'pimentão orgânico', 'tomate sem pele'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Ômega-3', 'Potássio', 'Gorduras boas do dendê', 'Peixe fresco', 'Tomate sem pele'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: coco', 'Pode conter traços de glúten']
    },
    'pancetapururuca': {
        'descricao': 'Panceta suína fresca preparada sous vide e finalizada em forno combinado para crocância',
        'ingredientes': ['panceta de porco fresca', 'sal grosso', 'alho orgânico', 'ervas orgânicas'],
        'tecnica': 'Sous vide + finalização em forno combinado',
        'beneficios': ['Alto teor proteico', 'Colágeno', 'Sabor intenso', 'Carne fresca', 'Sous vide'],
        'riscos': ['Pode conter traços de glúten']
    },
    'pernildecordeiro': {
        'descricao': 'Pernil de cordeiro fresco braseado com ervas frescas orgânicas',
        'ingredientes': ['pernil de cordeiro fresco', 'alecrim orgânico', 'alho orgânico', 'vinho', 'azeite extravirgem'],
        'tecnica': 'Braseamento',
        'beneficios': ['Proteína de alta qualidade', 'Ferro', 'Zinco', 'Vitaminas B', 'Cordeiro fresco', 'Ervas orgânicas'],
        'riscos': ['Pode conter traços de glúten']
    },
    'quiaboempanado': {
        'descricao': 'Quiabo orgânico empanado artesanalmente, assado em forno combinado (sem fritura)',
        'ingredientes': ['quiabo orgânico', 'farinha (uso controlado)', 'ovo', 'sal'],
        'tecnica': 'Empanado e assado em forno combinado (SEM FRITURA)',
        'beneficios': ['Fibras', 'Vitaminas', 'Ácido fólico', 'Sem fritura', 'Orgânico'],
        'riscos': ['Contém glúten (controlado)', 'Contém ovo', 'Pode conter traços de glúten']
    },
    'rolinhovietnamita': {
        'descricao': 'Rolinho primavera vietnamita com camarão fresco e vegetais orgânicos',
        'ingredientes': ['papel de arroz', 'camarão fresco', 'vegetais orgânicos', 'macarrão de arroz', 'ervas orgânicas'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Baixa caloria', 'Proteína do camarão', 'Vegetais frescos', 'Camarão fresco', 'Orgânicos'],
        'riscos': ['Alérgeno: crustáceo', 'Pode conter traços de glúten']
    },
    'salpicaodefrango': {
        'descricao': 'Salada de frango sous vide desfiado com maionese artesanal e legumes orgânicos',
        'ingredientes': ['frango sous vide desfiado', 'maionese artesanal', 'cenoura orgânica', 'batata palha', 'milho', 'ervilha'],
        'tecnica': 'Frango sous vide + preparo a frio',
        'beneficios': ['Proteína do frango', 'Vitaminas dos legumes', 'Frango sous vide', 'Maionese artesanal'],
        'riscos': ['Alérgeno: ovo (maionese)', 'Pode conter traços de glúten']
    },
    'sobrecoxaaotandoori': {
        'descricao': 'Sobrecoxa de frango fresco marinada em especiarias tandoori importadas da Índia',
        'ingredientes': ['sobrecoxa de frango fresco', 'iogurte fresco', 'garam masala importado', 'cúrcuma importada', 'páprica importada', 'gengibre fresco'],
        'tecnica': 'Marinado em iogurte + assado em forno combinado',
        'beneficios': ['Proteína', 'Especiarias anti-inflamatórias', 'Probióticos do iogurte', 'Frango fresco', 'Especiarias indianas importadas'],
        'riscos': ['Contém lactose (iogurte)', 'Pode conter traços de glúten']
    },

    # Fallback padrão
    'default': {
        'descricao': 'Prato preparado com ingredientes frescos e técnicas artesanais Cibi Sana',
        'ingredientes': ['Ingredientes frescos selecionados'],
        'tecnica': 'Técnica artesanal',
        'beneficios': ['Sem aditivos químicos', 'Ingredientes frescos', 'Preparo artesanal'],
        'riscos': ['Pode conter traços de glúten', 'Consulte sobre alérgenos específicos']
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
    
    # Adicionar riscos padrão Cibi Sana aos riscos existentes
    riscos = dish_info.get('riscos', [])
    if not any('traços de glúten' in r.lower() for r in riscos):
        riscos = riscos + [AVISO_GLUTEN]
    
    # DECISÃO DE CONFIANÇA
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
            'tecnica': dish_info.get('tecnica'),
            'beneficios': dish_info.get('beneficios'),
            'riscos': riscos,
            'aviso_cibi_sana': AVISO_CIBI_SANA,
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
            'tecnica': dish_info.get('tecnica'),
            'beneficios': dish_info.get('beneficios'),
            'riscos': riscos,
            'aviso_cibi_sana': AVISO_CIBI_SANA,
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
            'tecnica': None,
            'beneficios': None,
            'riscos': None,
            'aviso_cibi_sana': None,
            'alternatives': alternatives
        }


def get_risk_alert(dish: str, user_restrictions: List[str] = None) -> Optional[str]:
    """
    Verifica se o prato tem riscos para o usuário.
    (Placeholder para funcionalidade Premium)
    """
    # TODO: Implementar cruzamento com base de ingredientes/alérgenos
    return None
