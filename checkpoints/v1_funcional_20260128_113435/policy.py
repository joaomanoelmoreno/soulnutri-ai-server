"""SoulNutri AI - Policy (Política de Decisão)

Define a política de decisão a partir do score de similaridade.
Faixas de confiança:
- alta:   >= 0.85 (identificação segura - SEM alternativas)
- média:  >= 0.50 e < 0.85 (provável, mostrar alternativas)
- baixa:  < 0.50 (incerto)

CIBI SANA - PREMISSAS GASTRONÔMICAS:
- Sem aditivos químicos e/ou alimentos industrializados/processados
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

# Pratos que CONTÉM glúten (não apenas traços)
PRATOS_COM_GLUTEN = {
    'arroz7graos', 'arroz7graoscomfrutassecas', 'arroz7graoscomlegumes',
    'arrozde7graoscomamendoas', 'bolochocolatevegano', 'cuscuzmarroquino',
    'canelonedeespinafre', 'espaguete', 'lasanhadeespinafre', 'lasanhadeportobello',
    'nhoqueaosugo', 'risoneaopesto', 'bolobrownie', 'bolodegengibre',
    'almondegasmolhosugo', 'almdegasmolhosugo', 'cestinhasdecamarao',
    'filedefrangoaparmegiana', 'kibe', 'minipolpetonerecheadocomqueijo',
    'jiloempanado', 'quiaboempanado'
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
# CIBI SANA - AVISO PADRÃO
# =============================================================================
AVISO_CIBI_SANA = "Sem aditivos químicos e/ou alimentos industrializados/processados"

# =============================================================================
# INFORMAÇÕES DETALHADAS DOS PRATOS - CIBI SANA
# Benefícios revisados: apenas benefícios reais para saúde
# =============================================================================
DISH_INFO = {
    # ===================== VEGANOS =====================
    'aboboraaocurry': {
        'descricao': 'Abóbora orgânica cozida no vapor com especiarias indianas importadas em molho cremoso de leite de coco',
        'ingredientes': ['abóbora orgânica', 'curry indiano importado', 'leite de coco', 'gengibre fresco', 'cúrcuma importada', 'cebola orgânica', 'alho orgânico'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Betacaroteno: fortalece a visão e a pele', 'Cúrcuma: poderoso anti-inflamatório natural', 'Baixo valor calórico: auxilia no controle de peso'],
        'riscos': ['Alérgeno: coco']
    },
    'alhoporogratinadovegano': {
        'descricao': 'Alho poró orgânico gratinado no forno combinado com creme vegetal e ervas frescas orgânicas',
        'ingredientes': ['alho poró orgânico', 'creme vegetal artesanal', 'ervas frescas orgânicas', 'azeite extravirgem'],
        'tecnica': 'Gratinado em forno combinado',
        'beneficios': ['Prebiótico: alimenta as bactérias benéficas do intestino', 'Vitamina K: essencial para coagulação sanguínea', 'Fibras: promovem saciedade e regulam o intestino'],
        'riscos': ['Pode conter traços de glúten']
    },
    'arroz7graos': {
        'descricao': 'Mistura artesanal de arroz com grãos integrais e sementes nutritivas',
        'ingredientes': ['arroz integral', 'quinoa', 'linhaça', 'aveia', 'centeio', 'cevada', 'trigo'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Fibras: regulam o trânsito intestinal', 'Proteína vegetal: boa para músculos', 'Carboidratos complexos: energia prolongada'],
        'riscos': ['Contém glúten']
    },
    'arroz7graoscomfrutassecas': {
        'descricao': 'Arroz 7 grãos enriquecido com frutas secas selecionadas',
        'ingredientes': ['arroz 7 grãos', 'uva passa', 'damasco', 'castanhas', 'amêndoas'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Antioxidantes: combatem o envelhecimento celular', 'Ferro: previne anemia', 'Fibras: promovem saciedade'],
        'riscos': ['Contém glúten', 'Alérgeno: oleaginosas']
    },
    'arroz7graoscomlegumes': {
        'descricao': 'Arroz 7 grãos salteado com legumes orgânicos frescos',
        'ingredientes': ['arroz 7 grãos', 'cenoura orgânica', 'ervilha', 'milho', 'brócolis orgânico', 'abobrinha orgânica'],
        'tecnica': 'Cozimento e salteado',
        'beneficios': ['Vitaminas diversas: fortalecem o sistema imunológico', 'Fibras: regulam o intestino', 'Baixo teor de gordura'],
        'riscos': ['Contém glúten']
    },
    'arrozbranco': {
        'descricao': 'Arroz branco cozido no vapor, acompanhamento clássico preparado artesanalmente',
        'ingredientes': ['arroz branco selecionado', 'sal', 'alho orgânico', 'azeite extravirgem'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Energia rápida: ideal para reposição energética', 'Fácil digestão: gentil com o estômago', 'Naturalmente sem glúten'],
        'riscos': ['Pode conter traços de glúten']
    },
    'arrozde7graoscomamendoas': {
        'descricao': 'Arroz 7 grãos com amêndoas tostadas artesanalmente',
        'ingredientes': ['arroz 7 grãos', 'amêndoas tostadas', 'azeite extravirgem', 'sal', 'ervas frescas orgânicas'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Vitamina E: protege as células contra oxidação', 'Gorduras boas: beneficiam o coração', 'Fibras: auxiliam na digestão'],
        'riscos': ['Contém glúten', 'Alérgeno: amêndoas']
    },
    'arrozintegral': {
        'descricao': 'Arroz integral rico em fibras e nutrientes, cozido no vapor',
        'ingredientes': ['arroz integral selecionado', 'sal'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Fibras: promovem saciedade prolongada', 'Índice glicêmico baixo: controla açúcar no sangue', 'Vitaminas do complexo B: energia e bem-estar'],
        'riscos': ['Pode conter traços de glúten']
    },
    'arrozintlegumes': {
        'descricao': 'Arroz integral salteado com legumes orgânicos variados',
        'ingredientes': ['arroz integral', 'cenoura orgânica', 'brócolis orgânico', 'ervilha', 'abobrinha orgânica', 'azeite extravirgem'],
        'tecnica': 'Cozimento no vapor e salteado',
        'beneficios': ['Refeição completa: carboidratos, fibras e vitaminas', 'Controle glicêmico: libera energia gradualmente', 'Vitaminas: fortalecem a imunidade'],
        'riscos': ['Pode conter traços de glúten']
    },
    'batataassada': {
        'descricao': 'Batatas assadas em forno combinado com ervas frescas orgânicas aromáticas',
        'ingredientes': ['batata', 'azeite extravirgem', 'alecrim fresco orgânico', 'alho orgânico', 'sal'],
        'tecnica': 'Assado em forno combinado (sem fritura)',
        'beneficios': ['Potássio: regula a pressão arterial', 'Vitamina C: fortalece a imunidade', 'Energia sustentada: carboidratos complexos'],
        'riscos': ['Pode conter traços de glúten']
    },
    'batatacompaprica': {
        'descricao': 'Batatas temperadas com páprica defumada importada, assadas em forno combinado',
        'ingredientes': ['batata', 'páprica defumada importada', 'azeite extravirgem', 'alho orgânico', 'sal'],
        'tecnica': 'Assado em forno combinado (sem fritura)',
        'beneficios': ['Capsaicina da páprica: acelera o metabolismo', 'Potássio: saúde cardiovascular', 'Preparado sem fritura: mais leve e saudável'],
        'riscos': ['Pode conter traços de glúten']
    },
    'batatadoce': {
        'descricao': 'Batata doce orgânica assada em forno combinado, naturalmente doce',
        'ingredientes': ['batata doce orgânica'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Índice glicêmico baixo: energia sem picos de açúcar', 'Betacaroteno: saúde da pele e visão', 'Fibras: auxiliam no emagrecimento'],
        'riscos': ['Pode conter traços de glúten']
    },
    'beringelaaolimao': {
        'descricao': 'Berinjela orgânica grelhada com molho cítrico de limão fresco',
        'ingredientes': ['berinjela orgânica', 'limão fresco', 'azeite extravirgem', 'alho orgânico', 'salsinha orgânica'],
        'tecnica': 'Grelhado na grelha',
        'beneficios': ['Muito baixa caloria: apenas 25kcal/100g', 'Antocianinas: protegem o coração', 'Fibras: promovem saciedade'],
        'riscos': ['Pode conter traços de glúten']
    },
    'beringelaaocurrykincam': {
        'descricao': 'Berinjela orgânica ao curry indiano importado com especiarias aromáticas',
        'ingredientes': ['berinjela orgânica', 'curry indiano importado', 'leite de coco', 'gengibre fresco', 'coentro orgânico'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Cúrcuma do curry: anti-inflamatório natural', 'Gengibre: melhora a digestão', 'Baixo valor calórico'],
        'riscos': ['Pode conter traços de glúten', 'Alérgeno: coco']
    },
    'beterrabaaobalsamico': {
        'descricao': 'Beterraba orgânica assada em forno combinado com redução de vinagre balsâmico',
        'ingredientes': ['beterraba orgânica', 'vinagre balsâmico', 'azeite extravirgem', 'maple light', 'tomilho orgânico'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Nitratos naturais: melhoram a circulação sanguínea', 'Ferro: previne anemia', 'Antioxidantes: combatem radicais livres'],
        'riscos': ['Pode conter traços de glúten']
    },
    'bolochocolatevegano': {
        'descricao': 'Bolo de chocolate vegano preparado artesanalmente com cacau de qualidade, adoçado com maple',
        'ingredientes': ['farinha (uso controlado)', 'cacau em pó', 'maple canadense', 'óleo vegetal', 'leite vegetal'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Flavonoides do cacau: protegem o coração', 'Livre de lactose: ideal para intolerantes', 'Sem colesterol'],
        'riscos': ['Contém glúten']
    },
    'brocolis': {
        'descricao': 'Brócolis orgânico fresco cozido no vapor, nutritivo e saboroso',
        'ingredientes': ['brócolis orgânico fresco', 'sal', 'azeite extravirgem'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Sulforafano: composto anticancerígeno', 'Vitamina C: fortalece o sistema imune', 'Cálcio: fortalece ossos e dentes'],
        'riscos': ['Pode conter traços de glúten']
    },
    'caponata': {
        'descricao': 'Prato siciliano de berinjela orgânica com tomate sem pele e especiarias importadas',
        'ingredientes': ['berinjela orgânica', 'tomate sem pele', 'cebola orgânica', 'aipo orgânico', 'azeitonas', 'alcaparras', 'vinagre'],
        'tecnica': 'Refogado em azeite',
        'beneficios': ['Licopeno do tomate: protege a próstata', 'Fibras: regulam o intestino', 'Antioxidantes: combatem envelhecimento'],
        'riscos': ['Pode conter traços de glúten']
    },
    'carpacciodeabobrinha': {
        'descricao': 'Finas fatias de abobrinha orgânica crua com azeite extravirgem e limão',
        'ingredientes': ['abobrinha orgânica', 'azeite extravirgem', 'limão fresco', 'sal', 'rúcula orgânica'],
        'tecnica': 'Preparo a frio (crudo)',
        'beneficios': ['Apenas 17kcal/100g: extremamente leve', 'Hidratação: 95% de água', 'Potássio: equilíbrio dos fluidos corporais'],
        'riscos': ['Pode conter traços de glúten']
    },
    'cebola': {
        'descricao': 'Cebola orgânica caramelizada lentamente em azeite',
        'ingredientes': ['cebola orgânica', 'azeite extravirgem', 'sal'],
        'tecnica': 'Caramelização lenta em azeite',
        'beneficios': ['Quercetina: flavonoide anti-inflamatório', 'Prebiótico: alimenta bactérias boas do intestino', 'Fortalece a imunidade'],
        'riscos': ['Pode conter traços de glúten']
    },
    'cenourapalito': {
        'descricao': 'Cenouras orgânicas cortadas em palito, cozidas no vapor',
        'ingredientes': ['cenoura orgânica', 'sal'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Betacaroteno: essencial para saúde ocular', 'Vitamina A: mantém pele saudável', 'Fibras: auxiliam na digestão'],
        'riscos': ['Pode conter traços de glúten']
    },
    'cuscuzmarroquino': {
        'descricao': 'Semolina de trigo cozida no vapor com especiarias importadas do Oriente Médio',
        'ingredientes': ['semolina de trigo', 'caldo de legumes artesanal', 'azeite extravirgem', 'especiarias importadas'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Carboidratos: fonte de energia', 'Selênio: antioxidante importante', 'Preparo leve no vapor'],
        'riscos': ['Contém glúten']
    },
    'ervadocecomlaranja': {
        'descricao': 'Erva doce (funcho) orgânica salteada em azeite com suco de laranja fresco',
        'ingredientes': ['erva doce orgânica', 'suco de laranja fresco', 'azeite extravirgem', 'sal'],
        'tecnica': 'Salteado em azeite',
        'beneficios': ['Anetol: auxilia na digestão e reduz gases', 'Vitamina C: fortalece imunidade', 'Potássio: regula pressão arterial'],
        'riscos': ['Pode conter traços de glúten']
    },
    'farofadebananadaterra': {
        'descricao': 'Farofa artesanal com banana da terra assada em forno combinado (sem fritura)',
        'ingredientes': ['farinha de mandioca', 'banana da terra', 'cebola orgânica', 'azeite extravirgem', 'sal'],
        'tecnica': 'Banana assada em forno combinado (sem fritura)',
        'beneficios': ['Potássio da banana: saúde muscular', 'Energia de liberação lenta', 'Preparada sem fritura'],
        'riscos': ['Pode conter traços de glúten']
    },
    'feijaocariocasemcarne': {
        'descricao': 'Feijão carioca demolhado e cozido em caldo temperado artesanal, versão vegetariana',
        'ingredientes': ['feijão carioca demolhado', 'alho orgânico', 'cebola orgânica', 'louro', 'sal'],
        'tecnica': 'Feijão demolhado + cozimento tradicional',
        'beneficios': ['Proteína vegetal: essencial para vegetarianos', 'Ferro: previne anemia', 'Fibras: promovem saciedade', 'Demolhado: melhor digestibilidade'],
        'riscos': ['Pode conter traços de glúten']
    },
    'feijaopretosemcarne': {
        'descricao': 'Feijão preto demolhado e cozido sem carne, rico e saboroso',
        'ingredientes': ['feijão preto demolhado', 'alho orgânico', 'cebola orgânica', 'louro', 'sal'],
        'tecnica': 'Feijão demolhado + cozimento tradicional',
        'beneficios': ['Antocianinas: antioxidantes da casca preta', 'Ferro: combate anemia', 'Proteína vegetal de qualidade'],
        'riscos': ['Pode conter traços de glúten']
    },
    'graodebicotomatesecoespinafre': {
        'descricao': 'Grão de bico sem pele salteado com tomate seco e espinafre orgânico',
        'ingredientes': ['grão de bico sem pele', 'tomate seco', 'espinafre orgânico', 'alho orgânico', 'azeite extravirgem'],
        'tecnica': 'Grão de bico sem pele + salteado em azeite',
        'beneficios': ['Proteína completa: contém todos aminoácidos essenciais', 'Ferro do espinafre: combate anemia', 'Sem pele: digestão mais fácil'],
        'riscos': ['Pode conter traços de glúten']
    },
    'hamburguervegano': {
        'descricao': 'Hambúrguer de proteína vegetal artesanal com especiarias importadas, grelhado',
        'ingredientes': ['proteína de grão de bico sem pele', 'cebola orgânica', 'alho orgânico', 'especiarias importadas'],
        'tecnica': 'Grelhado na grelha (sem fritura)',
        'beneficios': ['Proteína vegetal: alternativa saudável à carne', 'Zero colesterol', 'Fibras: promovem saciedade'],
        'riscos': ['Pode conter traços de glúten']
    },
    'lentilhacomtofu': {
        'descricao': 'Lentilha cozida com cubos de tofu temperado com especiarias indianas importadas',
        'ingredientes': ['lentilha', 'tofu', 'tomate sem pele', 'cebola orgânica', 'curry indiano importado', 'coentro orgânico'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Proteína completa: lentilha + tofu', 'Ferro: essencial para energia', 'Isoflavonas do tofu: equilíbrio hormonal'],
        'riscos': ['Pode conter traços de glúten', 'Alérgeno: soja']
    },
    'molhovinagrete': {
        'descricao': 'Molho fresco de tomate sem pele, cebola orgânica e pimentão picados',
        'ingredientes': ['tomate sem pele', 'cebola orgânica', 'pimentão orgânico', 'vinagre', 'azeite extravirgem', 'coentro orgânico'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Vitamina C: fortalece a imunidade', 'Licopeno: protetor cardiovascular', 'Baixíssimas calorias'],
        'riscos': ['Pode conter traços de glúten']
    },
    'repolho': {
        'descricao': 'Repolho orgânico refogado em azeite',
        'ingredientes': ['repolho orgânico', 'sal', 'azeite extravirgem'],
        'tecnica': 'Refogado em azeite',
        'beneficios': ['Vitamina C: mais que a laranja por porção', 'Compostos anticancerígenos', 'Muito baixa caloria: apenas 25kcal/100g'],
        'riscos': ['Pode conter traços de glúten']
    },
    'saladadefeijaobranco': {
        'descricao': 'Salada fria de feijão branco demolhado com ervas frescas orgânicas',
        'ingredientes': ['feijão branco demolhado', 'tomate sem pele', 'cebola orgânica', 'salsinha orgânica', 'azeite extravirgem', 'limão'],
        'tecnica': 'Feijão demolhado + preparo a frio',
        'beneficios': ['Proteína vegetal de alta qualidade', 'Fibras solúveis: reduzem colesterol', 'Potássio: saúde cardiovascular'],
        'riscos': ['Pode conter traços de glúten']
    },
    'tabuledequinoa': {
        'descricao': 'Salada libanesa com quinoa, ervas frescas orgânicas e especiarias do Oriente Médio',
        'ingredientes': ['quinoa', 'tomate sem pele', 'pepino orgânico', 'hortelã orgânica', 'salsinha orgânica', 'limão', 'azeite extravirgem'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Quinoa: única proteína vegetal completa', 'Sem glúten naturalmente', 'Ferro e magnésio: energia e disposição'],
        'riscos': ['Pode conter traços de glúten']
    },
    'umamidetomate': {
        'descricao': 'Tomates sem pele concentrados com sabor umami intenso',
        'ingredientes': ['tomate sem pele', 'azeite extravirgem', 'alho orgânico', 'ervas orgânicas', 'sal'],
        'tecnica': 'Concentração lenta',
        'beneficios': ['Licopeno concentrado: poderoso antioxidante', 'Vitamina C: fortalece imunidade', 'Baixa caloria'],
        'riscos': ['Pode conter traços de glúten']
    },

    # ===================== VEGETARIANOS =====================
    'brocoliscomparmesao': {
        'descricao': 'Brócolis orgânico cozido no vapor e gratinado com queijo parmesão',
        'ingredientes': ['brócolis orgânico', 'queijo parmesão', 'azeite extravirgem', 'alho orgânico'],
        'tecnica': 'Vapor + gratinado em forno combinado',
        'beneficios': ['Cálcio: fortalece ossos e dentes', 'Vitamina K: essencial para coagulação', 'Sulforafano: composto anticancerígeno'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'brocoliscouveflorgratinado': {
        'descricao': 'Brócolis e couve-flor orgânicos no vapor, gratinados com molho branco artesanal',
        'ingredientes': ['brócolis orgânico', 'couve-flor orgânica', 'queijo', 'creme de leite fresco', 'noz-moscada importada'],
        'tecnica': 'Vapor + gratinado em forno combinado',
        'beneficios': ['Vitamina C: fortalece imunidade', 'Fibras: regulam intestino', 'Cálcio do queijo: saúde óssea'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'brocolisgratinado': {
        'descricao': 'Brócolis orgânico ao forno combinado com queijo gratinado e creme fresco',
        'ingredientes': ['brócolis orgânico', 'queijo mussarela', 'creme de leite fresco', 'parmesão'],
        'tecnica': 'Vapor + gratinado em forno combinado',
        'beneficios': ['Sulforafano: protetor contra câncer', 'Vitamina C: antioxidante natural', 'Cálcio: fortalece a estrutura óssea'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'canelonedeespinafre': {
        'descricao': 'Massa recheada com espinafre orgânico e ricota fresca, molho artesanal',
        'ingredientes': ['massa de canelone', 'espinafre orgânico', 'ricota fresca', 'molho de tomate artesanal', 'queijo'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Ferro do espinafre: combate anemia', 'Cálcio da ricota: saúde dos ossos', 'Vitamina A: saúde ocular'],
        'riscos': ['Contém glúten', 'Contém lactose']
    },
    'carpacciodelaranja': {
        'descricao': 'Fatias finas de laranja fresca com maple canadense e hortelã orgânica',
        'ingredientes': ['laranja fresca', 'maple canadense', 'hortelã orgânica', 'canela importada'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Vitamina C: fortalece o sistema imunológico', 'Flavonoides: protegem o coração', 'Hidratação: alto teor de água'],
        'riscos': ['Pode conter traços de glúten']
    },
    'carpacciodeperaruculaeamendoas': {
        'descricao': 'Fatias de pera fresca com rúcula orgânica e amêndoas tostadas',
        'ingredientes': ['pera fresca', 'rúcula orgânica', 'amêndoas tostadas', 'azeite extravirgem', 'queijo parmesão'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Fibras da pera: regulam o intestino', 'Vitamina E das amêndoas: antioxidante', 'Ômega-3: saúde cerebral'],
        'riscos': ['Alérgeno: amêndoas', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'cenouraaoiogurte': {
        'descricao': 'Cenoura orgânica ralada com molho de iogurte fresco artesanal',
        'ingredientes': ['cenoura orgânica', 'iogurte natural fresco', 'maple light', 'gengibre fresco'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Probióticos do iogurte: saúde intestinal', 'Betacaroteno: saúde da visão', 'Cálcio: fortalece os ossos'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'cocada': {
        'descricao': 'Doce tradicional de coco artesanal, adoçado com maple canadense',
        'ingredientes': ['coco ralado fresco', 'maple canadense', 'leite condensado artesanal'],
        'tecnica': 'Banho maria',
        'beneficios': ['TCM do coco: energia rápida para o cérebro', 'Fibras: auxiliam digestão', 'Adoçado com maple: mais natural'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'cuscuzdetapioca': {
        'descricao': 'Cuscuz doce de tapioca artesanal com coco, adoçado com maple',
        'ingredientes': ['tapioca', 'leite de coco', 'maple canadense', 'coco ralado fresco'],
        'tecnica': 'Vapor + banho maria',
        'beneficios': ['Naturalmente sem glúten', 'Energia de rápida absorção', 'Adoçado com maple natural'],
        'riscos': ['Alérgeno: coco', 'Pode conter traços de glúten']
    },
    'dadinhodetapioca': {
        'descricao': 'Cubos de tapioca artesanal com queijo coalho, assados em forno combinado',
        'ingredientes': ['tapioca', 'queijo coalho', 'sal'],
        'tecnica': 'Assado em forno combinado (sem fritura)',
        'beneficios': ['Sem glúten naturalmente', 'Cálcio do queijo: saúde óssea', 'Assado: mais leve que frito'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'espaguete': {
        'descricao': 'Massa italiana artesanal servida com molho de tomate feito em nossa cozinha',
        'ingredientes': ['massa de trigo', 'molho de tomate artesanal', 'azeite extravirgem', 'alho orgânico', 'manjericão orgânico'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Carboidratos: energia para atividades físicas', 'Licopeno do molho: antioxidante', 'Baixo teor de gordura'],
        'riscos': ['Contém glúten']
    },
    'gelatinadecereja': {
        'descricao': 'Sobremesa de gelatina artesanal sabor cereja',
        'ingredientes': ['gelatina', 'suco de cereja', 'maple light'],
        'tecnica': 'Refrigeração',
        'beneficios': ['Colágeno: beneficia pele e articulações', 'Baixíssimas calorias', 'Antocianinas da cereja: antioxidantes'],
        'riscos': ['Gelatina de origem animal', 'Pode conter traços de glúten']
    },
    'goiabada': {
        'descricao': 'Doce tradicional de goiaba artesanal em bloco',
        'ingredientes': ['goiaba fresca', 'açúcar', 'maple canadense'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Vitamina C: até 4x mais que laranja', 'Licopeno: antioxidante poderoso', 'Fibras: regulam o intestino'],
        'riscos': ['Pode conter traços de glúten']
    },
    'jiloempanado': {
        'descricao': 'Jiló orgânico empanado artesanalmente, assado em forno combinado (sem fritura)',
        'ingredientes': ['jiló orgânico', 'farinha (uso controlado)', 'ovo', 'sal'],
        'tecnica': 'Empanado e assado em forno combinado (SEM FRITURA)',
        'beneficios': ['Auxilia na digestão', 'Estimula o fígado', 'Assado: muito mais leve que frito'],
        'riscos': ['Contém glúten', 'Alérgeno: ovo']
    },
    'lasanhadeespinafre': {
        'descricao': 'Lasanha verde com camadas de espinafre orgânico, ricota fresca e molho branco artesanal',
        'ingredientes': ['massa de lasanha', 'espinafre orgânico', 'ricota fresca', 'mussarela', 'molho branco artesanal', 'creme de leite fresco'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Ferro do espinafre: previne anemia', 'Cálcio: fortalece ossos e dentes', 'Vitaminas A e K: saúde geral'],
        'riscos': ['Contém glúten', 'Contém lactose']
    },
    'lasanhadeportobello': {
        'descricao': 'Lasanha com cogumelos portobello frescos e molho branco artesanal',
        'ingredientes': ['massa', 'cogumelo portobello fresco', 'queijo', 'molho branco artesanal', 'cebola orgânica', 'creme de leite fresco'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Vitamina D do cogumelo: saúde óssea', 'Selênio: antioxidante importante', 'Fibras: regulam o intestino'],
        'riscos': ['Contém glúten', 'Contém lactose']
    },
    'mandioquinhaassada': {
        'descricao': 'Mandioquinha assada em forno combinado com ervas frescas orgânicas',
        'ingredientes': ['mandioquinha', 'azeite extravirgem', 'alecrim orgânico', 'sal'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Digestão fácil: ideal para estômagos sensíveis', 'Potássio: regula pressão arterial', 'Naturalmente sem glúten'],
        'riscos': ['Pode conter traços de glúten']
    },
    'moussedemaracuja': {
        'descricao': 'Mousse cremoso de maracujá fresco com creme de leite fresco, adoçado com maple',
        'ingredientes': ['maracujá fresco', 'creme de leite fresco', 'leite condensado artesanal', 'maple light'],
        'tecnica': 'Banho maria + refrigeração',
        'beneficios': ['Maracujá: calmante natural que reduz ansiedade', 'Vitamina C: fortalece imunidade', 'Flavonoides: protegem o coração'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'moussedemorango': {
        'descricao': 'Mousse cremoso de morango fresco com creme de leite fresco, adoçado com maple',
        'ingredientes': ['morango fresco', 'creme de leite fresco', 'leite condensado artesanal', 'maple light'],
        'tecnica': 'Banho maria + refrigeração',
        'beneficios': ['Antocianinas: protegem o coração', 'Vitamina C: fortalece a imunidade', 'Manganês: saúde dos ossos'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'nhoqueaosugo': {
        'descricao': 'Nhoque de batata artesanal com molho de tomate feito em nossa cozinha',
        'ingredientes': ['batata', 'farinha (uso controlado)', 'ovo', 'molho de tomate artesanal', 'manjericão orgânico'],
        'tecnica': 'Preparo artesanal',
        'beneficios': ['Potássio da batata: saúde cardiovascular', 'Licopeno do molho: antioxidante', 'Energia de carboidratos'],
        'riscos': ['Contém glúten', 'Alérgeno: ovo']
    },
    'pepinocomiogurte': {
        'descricao': 'Pepino orgânico fresco com molho de iogurte artesanal (tipo tzatziki)',
        'ingredientes': ['pepino orgânico', 'iogurte fresco', 'alho orgânico', 'hortelã orgânica', 'azeite extravirgem'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Hidratação: pepino é 96% água', 'Probióticos: saúde intestinal', 'Apenas 15kcal/100g: extremamente leve'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'risoneaopesto': {
        'descricao': 'Massa risone com molho pesto artesanal de manjericão orgânico',
        'ingredientes': ['massa risone', 'manjericão orgânico', 'parmesão', 'pinoli', 'azeite extravirgem', 'alho orgânico'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Gorduras boas do azeite: protegem o coração', 'Eugenol do manjericão: anti-inflamatório', 'Magnésio do pinoli: relaxamento muscular'],
        'riscos': ['Contém glúten', 'Contém lactose', 'Alérgeno: pinoli']
    },
    'bananacaramelizada': {
        'descricao': 'Banana grelhada com maple canadense caramelizado',
        'ingredientes': ['banana', 'maple canadense', 'manteiga fresca', 'canela importada'],
        'tecnica': 'Grelhado + caramelização',
        'beneficios': ['Potássio: previne cãibras e regula pressão', 'Triptofano: precursor da serotonina (bem-estar)', 'Energia natural de rápida absorção'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'bolobrownie': {
        'descricao': 'Bolo denso de chocolate artesanal tipo brownie, adoçado com maple',
        'ingredientes': ['chocolate', 'manteiga fresca', 'maple canadense', 'ovos', 'farinha (uso controlado)', 'nozes'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Flavonoides do cacau: melhoram humor e cognição', 'Magnésio: relaxamento e bem-estar', 'Antioxidantes: combatem radicais livres'],
        'riscos': ['Contém glúten', 'Alérgeno: ovo', 'Contém lactose', 'Alérgeno: nozes']
    },
    'bolodegengibre': {
        'descricao': 'Bolo aromático de gengibre fresco com especiarias importadas, adoçado com maple',
        'ingredientes': ['farinha (uso controlado)', 'gengibre fresco', 'maple canadense', 'ovos', 'manteiga fresca', 'especiarias importadas'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Gengibre: poderoso anti-inflamatório e digestivo', 'Gingerol: alivia náuseas', 'Termogênico: acelera metabolismo'],
        'riscos': ['Contém glúten', 'Alérgeno: ovo', 'Contém lactose']
    },

    # ===================== PROTEÍNA ANIMAL =====================
    'almondegasmolhosugo': {
        'descricao': 'Almôndegas de carne bovina fresca ao molho de tomate artesanal feito em nossa cozinha',
        'ingredientes': ['carne bovina fresca', 'cebola orgânica', 'alho orgânico', 'ovo', 'farinha (uso controlado)', 'molho de tomate artesanal'],
        'tecnica': 'Braseado',
        'beneficios': ['Proteína de alto valor biológico: construção muscular', 'Ferro heme: absorção 3x maior que ferro vegetal', 'Vitaminas B12: essencial para sistema nervoso'],
        'riscos': ['Contém glúten', 'Alérgeno: ovo']
    },
    'almdegasmolhosugo': {
        'descricao': 'Almôndegas de carne bovina fresca ao molho de tomate artesanal feito em nossa cozinha',
        'ingredientes': ['carne bovina fresca', 'cebola orgânica', 'alho orgânico', 'ovo', 'farinha (uso controlado)', 'molho de tomate artesanal'],
        'tecnica': 'Braseado',
        'beneficios': ['Proteína de alto valor biológico: construção muscular', 'Ferro heme: absorção 3x maior que ferro vegetal', 'Vitaminas B12: essencial para sistema nervoso'],
        'riscos': ['Contém glúten', 'Alérgeno: ovo']
    },
    'atumaogergelim': {
        'descricao': 'Atum fresco (recebido a cada 1-2 dias) selado com crosta de gergelim importado',
        'ingredientes': ['atum fresco', 'gergelim importado', 'shoyu', 'gengibre fresco', 'wasabi importado do Japão'],
        'tecnica': 'Selado na grelha',
        'beneficios': ['Ômega-3: protege coração e cérebro', 'Proteína magra: ideal para músculos', 'Selênio: antioxidante que protege células'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: gergelim', 'Pode conter traços de glúten']
    },
    'bacalhaucomnatas': {
        'descricao': 'Bacalhau fresco desfiado gratinado com creme de leite fresco artesanal',
        'ingredientes': ['bacalhau fresco', 'batata', 'creme de leite fresco', 'cebola orgânica', 'alho orgânico', 'azeitonas'],
        'tecnica': 'Gratinado em forno combinado',
        'beneficios': ['Ômega-3: saúde cardiovascular e cerebral', 'Proteína completa de alta qualidade', 'Vitamina D: fortalece ossos'],
        'riscos': ['Alérgeno: peixe', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'bacalhaugomesdesa': {
        'descricao': 'Prato tradicional português de bacalhau fresco com batatas e ovos',
        'ingredientes': ['bacalhau fresco', 'batata', 'cebola orgânica', 'ovos', 'azeitonas', 'azeite extravirgem'],
        'tecnica': 'Assado em forno combinado',
        'beneficios': ['Ômega-3: reduz inflamação', 'Vitamina B12: energia e sistema nervoso', 'Fósforo: saúde dos ossos'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: ovo', 'Pode conter traços de glúten']
    },
    'baiaodedois': {
        'descricao': 'Prato típico nordestino com arroz e feijão-de-corda demolhado cozidos juntos',
        'ingredientes': ['arroz', 'feijão-de-corda demolhado', 'bacon artesanal', 'queijo coalho', 'manteiga fresca', 'temperos'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Proteína completa: arroz + feijão', 'Fibras: saciedade prolongada', 'Energia de longa duração'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'bolinhodebacalhau': {
        'descricao': 'Bolinho artesanal de bacalhau fresco com batata - ÚNICO ITEM FRITO',
        'ingredientes': ['bacalhau fresco', 'batata', 'ovo', 'cebola orgânica', 'salsinha orgânica'],
        'tecnica': 'Frito em óleo (ÚNICA EXCEÇÃO de fritura)',
        'beneficios': ['Ômega-3 do bacalhau: saúde do coração', 'Proteína de alta qualidade', 'Vitamina D: saúde óssea'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: ovo', 'Fritura', 'Pode conter traços de glúten']
    },
    'cestinhasdecamarao': {
        'descricao': 'Cestinhas assadas em forno combinado recheadas com camarão fresco',
        'ingredientes': ['camarão fresco', 'massa wonton', 'cream cheese artesanal', 'cebolinha orgânica'],
        'tecnica': 'Assado em forno combinado (sem fritura)',
        'beneficios': ['Proteína magra: baixo teor de gordura', 'Selênio: antioxidante poderoso', 'Zinco: fortalece imunidade'],
        'riscos': ['Alérgeno: crustáceo', 'Contém lactose', 'Contém glúten']
    },
    'cevicheperuano': {
        'descricao': 'Peixe fresco (recebido a cada 1-2 dias) marinado em limão com cebola roxa orgânica',
        'ingredientes': ['peixe branco fresco', 'limão fresco', 'cebola roxa orgânica', 'coentro orgânico', 'pimenta importada', 'milho'],
        'tecnica': 'Marinado a frio (crudo)',
        'beneficios': ['Ômega-3: proteção cardiovascular', 'Vitamina C do limão: fortalece imunidade', 'Proteína magra: baixíssima gordura'],
        'riscos': ['Alérgeno: peixe', 'Pode conter traços de glúten']
    },
    'costelinhacibisana': {
        'descricao': 'Costelinha suína preparada sous vide e finalizada na grelha com molho especial artesanal',
        'ingredientes': ['costela de porco fresca', 'alho orgânico', 'maple canadense', 'shoyu', 'gengibre fresco'],
        'tecnica': 'Sous vide + finalização na grelha',
        'beneficios': ['Colágeno: beneficia pele e articulações', 'Vitaminas do complexo B: energia', 'Zinco: fortalece sistema imune'],
        'riscos': ['Pode conter traços de glúten']
    },
    'entrecotegrelhado': {
        'descricao': 'Corte nobre de carne bovina fresca grelhado na grelha',
        'ingredientes': ['entrecôte bovino fresco', 'sal grosso', 'pimenta importada', 'alho orgânico'],
        'tecnica': 'Grelhado na grelha',
        'beneficios': ['Proteína completa: todos aminoácidos essenciais', 'Ferro heme: combate anemia eficientemente', 'Creatina natural: energia muscular'],
        'riscos': ['Pode conter traços de glúten']
    },
    'escondidinhodecarneseca': {
        'descricao': 'Purê de mandioca artesanal com carne seca desfiada gratinada em forno combinado',
        'ingredientes': ['mandioca', 'carne seca', 'queijo', 'manteiga fresca', 'creme de leite fresco'],
        'tecnica': 'Gratinado em forno combinado',
        'beneficios': ['Proteína concentrada da carne seca', 'Carboidratos da mandioca: energia', 'Cálcio do queijo: saúde óssea'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'farofadebacon': {
        'descricao': 'Farofa artesanal com bacon de preparo próprio',
        'ingredientes': ['farinha de mandioca', 'bacon artesanal', 'cebola orgânica', 'manteiga fresca', 'ovos'],
        'tecnica': 'Preparo tradicional',
        'beneficios': ['Energia dos carboidratos', 'Proteína do bacon e ovos', 'Tiamina (B1): metabolismo energético'],
        'riscos': ['Alérgeno: ovo', 'Pode conter traços de glúten']
    },
    'feijaopretocomcarne': {
        'descricao': 'Feijão preto demolhado cozido com carne bovina fresca',
        'ingredientes': ['feijão preto demolhado', 'carne bovina fresca', 'alho orgânico', 'cebola orgânica', 'louro'],
        'tecnica': 'Feijão demolhado + cozimento tradicional',
        'beneficios': ['Proteína completa: carne + feijão', 'Ferro de dupla fonte: absorção otimizada', 'Fibras: saciedade e intestino regulado'],
        'riscos': ['Pode conter traços de glúten']
    },
    'feijaotropeiro': {
        'descricao': 'Prato mineiro tradicional com feijão demolhado, bacon artesanal e couve orgânica',
        'ingredientes': ['feijão demolhado', 'bacon artesanal', 'linguiça artesanal', 'farinha de mandioca', 'ovos', 'couve orgânica'],
        'tecnica': 'Preparo tradicional',
        'beneficios': ['Proteína de múltiplas fontes', 'Ferro: combate anemia', 'Vitamina K da couve: coagulação sanguínea'],
        'riscos': ['Alérgeno: ovo', 'Pode conter traços de glúten']
    },
    'figadoacebolado': {
        'descricao': 'Fígado bovino fresco grelhado com cebolas orgânicas',
        'ingredientes': ['fígado bovino fresco', 'cebola orgânica', 'alho orgânico', 'sal', 'azeite extravirgem'],
        'tecnica': 'Grelhado na grelha',
        'beneficios': ['Vitamina A: uma porção supre necessidade semanal', 'Ferro heme: absorção superior', 'Vitamina B12: saúde neurológica'],
        'riscos': ['Colesterol elevado: consumir com moderação', 'Pode conter traços de glúten']
    },
    'filedefrangoaparmegiana': {
        'descricao': 'Filé de frango preparado sous vide, empanado artesanalmente e finalizado em forno combinado',
        'ingredientes': ['peito de frango fresco', 'farinha (uso controlado)', 'ovo', 'molho de tomate artesanal', 'mussarela', 'presunto'],
        'tecnica': 'Sous vide + empanado assado em forno combinado (SEM FRITURA)',
        'beneficios': ['Proteína magra: ideal para dietas', 'Cálcio do queijo: fortalece ossos', 'Assado: mais leve que a versão tradicional frita'],
        'riscos': ['Contém glúten', 'Alérgeno: ovo', 'Contém lactose']
    },
    'filedepeixeaomisso': {
        'descricao': 'Filé de peixe fresco (recebido a cada 1-2 dias) ao vapor com molho de missô japonês',
        'ingredientes': ['peixe branco fresco', 'missô importado do Japão', 'saquê', 'gengibre fresco', 'cebolinha orgânica'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Ômega-3: protege coração e artérias', 'Probióticos do missô: saúde intestinal', 'Proteína magra de fácil digestão'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: soja', 'Pode conter traços de glúten']
    },
    'filedepeixeaomolhodelimao': {
        'descricao': 'Filé de peixe fresco ao vapor com molho cítrico de limão e manteiga fresca',
        'ingredientes': ['peixe branco fresco', 'limão fresco', 'manteiga fresca', 'alcaparras', 'salsinha orgânica'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Ômega-3: reduz triglicerídeos', 'Proteína de alta digestibilidade', 'Vitamina D: fortalece ossos'],
        'riscos': ['Alérgeno: peixe', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'filedepeixeaomolhomisso': {
        'descricao': 'Filé de peixe fresco ao vapor com molho missô importado',
        'ingredientes': ['peixe fresco', 'missô importado do Japão', 'gengibre fresco', 'cebolinha orgânica', 'gergelim importado'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Ômega-3: anti-inflamatório natural', 'Probióticos: equilíbrio da flora intestinal', 'Selênio: proteção antioxidante'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: soja', 'Alérgeno: gergelim', 'Pode conter traços de glúten']
    },
    'filedepeixemolhoconfit': {
        'descricao': 'Filé de peixe fresco ao vapor com tomate sem pele confit',
        'ingredientes': ['peixe fresco', 'tomate sem pele', 'azeite extravirgem', 'alho orgânico', 'ervas orgânicas'],
        'tecnica': 'Cozimento no vapor + tomate confit em azeite',
        'beneficios': ['Ômega-3: saúde cardiovascular', 'Licopeno do tomate: antioxidante', 'Baixíssimas calorias'],
        'riscos': ['Alérgeno: peixe', 'Pode conter traços de glúten']
    },
    'filedepeixemolhofrutassecas': {
        'descricao': 'Filé de peixe fresco ao vapor com molho artesanal de frutas secas',
        'ingredientes': ['peixe fresco', 'uva passa', 'damasco', 'vinho branco', 'manteiga fresca'],
        'tecnica': 'Cozimento no vapor',
        'beneficios': ['Ômega-3: proteção do coração', 'Antioxidantes das frutas secas', 'Potássio: equilíbrio de fluidos'],
        'riscos': ['Alérgeno: peixe', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'frangocremedelimaosalnegro': {
        'descricao': 'Frango preparado sous vide ao creme de limão com sal negro do Havaí importado',
        'ingredientes': ['frango fresco', 'creme de leite fresco', 'limão fresco', 'sal negro do Havaí', 'ervas orgânicas'],
        'tecnica': 'Sous vide',
        'beneficios': ['Proteína magra: construção muscular', 'Vitamina B6: metabolismo proteico', 'Minerais do sal negro: carvão ativado'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'hamburgerdecarne': {
        'descricao': 'Hambúrguer artesanal de carne bovina fresca, grelhado',
        'ingredientes': ['carne bovina fresca moída', 'sal', 'pimenta importada', 'cebola orgânica'],
        'tecnica': 'Grelhado na grelha',
        'beneficios': ['Proteína completa: todos aminoácidos', 'Ferro heme: previne anemia', 'Zinco: fortalece imunidade'],
        'riscos': ['Pode conter traços de glúten']
    },
    'kibe': {
        'descricao': 'Bolinho de origem árabe de carne fresca e trigo, assado em forno combinado',
        'ingredientes': ['carne moída fresca', 'trigo para quibe', 'cebola orgânica', 'hortelã orgânica', 'especiarias importadas da Arábia'],
        'tecnica': 'Assado em forno combinado (sem fritura)',
        'beneficios': ['Proteína de alto valor biológico', 'Fibras do trigo: saciedade', 'Assado: mais saudável que frito'],
        'riscos': ['Contém glúten']
    },
    'maminhaaomolhomongolia': {
        'descricao': 'Maminha bovina fresca preparada sous vide ao molho agridoce mongoliano com maple',
        'ingredientes': ['maminha fresca', 'shoyu', 'gengibre fresco', 'alho orgânico', 'maple canadense', 'cebolinha orgânica'],
        'tecnica': 'Sous vide + finalização',
        'beneficios': ['Proteína de alta qualidade: regeneração muscular', 'Ferro: oxigenação do sangue', 'Zinco: cicatrização e imunidade'],
        'riscos': ['Pode conter traços de glúten']
    },
    'maminhaaomolhomostarda': {
        'descricao': 'Corte bovino nobre fresco preparado sous vide com molho de mostarda e creme fresco',
        'ingredientes': ['maminha bovina fresca', 'mostarda', 'creme de leite fresco', 'vinho branco'],
        'tecnica': 'Sous vide',
        'beneficios': ['Proteína completa: construção e reparo muscular', 'Ferro heme: energia e vitalidade', 'Vitamina B12: saúde do sistema nervoso'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'maminhamolhocebola': {
        'descricao': 'Maminha fresca preparada sous vide com molho de cebola orgânica caramelizada',
        'ingredientes': ['maminha fresca', 'cebola orgânica', 'vinho', 'manteiga fresca', 'creme de leite fresco', 'tomilho orgânico'],
        'tecnica': 'Sous vide + caramelização',
        'beneficios': ['Proteína de alto valor biológico', 'Ferro: combate fadiga e anemia', 'Quercetina da cebola: anti-inflamatório'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },
    'maminhanacervejapreta': {
        'descricao': 'Maminha bovina fresca braseada na cerveja preta',
        'ingredientes': ['maminha fresca', 'cerveja preta', 'cebola orgânica', 'alho orgânico', 'louro'],
        'tecnica': 'Braseamento',
        'beneficios': ['Proteína que se desfaz: fácil mastigação', 'Ferro heme: previne anemia', 'Vitaminas do complexo B'],
        'riscos': ['Contém álcool residual', 'Pode conter traços de glúten']
    },
    'mandioquinhacomcamarao': {
        'descricao': 'Purê de mandioquinha artesanal com camarões frescos salteados em azeite',
        'ingredientes': ['mandioquinha', 'camarão fresco', 'alho orgânico', 'manteiga fresca', 'salsinha orgânica'],
        'tecnica': 'Purê artesanal + camarão salteado em azeite',
        'beneficios': ['Proteína do camarão: baixa caloria', 'Selênio: antioxidante poderoso', 'Iodo: saúde da tireoide'],
        'riscos': ['Alérgeno: crustáceo', 'Contém lactose', 'Pode conter traços de glúten']
    },
    'minipolpetonerecheadocomqueijo': {
        'descricao': 'Polpetone artesanal de carne fresca recheado com queijo',
        'ingredientes': ['carne moída fresca', 'queijo mussarela', 'ovo', 'farinha (uso controlado)', 'molho de tomate artesanal'],
        'tecnica': 'Braseado',
        'beneficios': ['Proteína completa: carne + queijo', 'Cálcio do queijo: saúde óssea', 'Licopeno do molho: antioxidante'],
        'riscos': ['Contém glúten', 'Alérgeno: ovo', 'Contém lactose']
    },
    'moquecadebanadaterra': {
        'descricao': 'Moqueca de peixe fresco com banana da terra e leite de coco',
        'ingredientes': ['peixe fresco', 'banana da terra', 'leite de coco', 'azeite de dendê', 'pimentão orgânico', 'tomate sem pele'],
        'tecnica': 'Cozimento tradicional',
        'beneficios': ['Ômega-3: saúde cerebral', 'Potássio da banana: saúde cardiovascular', 'Betacaroteno do dendê: antioxidante'],
        'riscos': ['Alérgeno: peixe', 'Alérgeno: coco', 'Pode conter traços de glúten']
    },
    'pancetapururuca': {
        'descricao': 'Panceta suína fresca preparada sous vide e finalizada em forno combinado para crocância',
        'ingredientes': ['panceta de porco fresca', 'sal grosso', 'alho orgânico', 'ervas orgânicas'],
        'tecnica': 'Sous vide + finalização em forno combinado',
        'beneficios': ['Colágeno: beneficia pele e articulações', 'Vitamina B1: metabolismo energético', 'Selênio: proteção antioxidante'],
        'riscos': ['Pode conter traços de glúten']
    },
    'pernildecordeiro': {
        'descricao': 'Pernil de cordeiro fresco braseado com ervas frescas orgânicas',
        'ingredientes': ['pernil de cordeiro fresco', 'alecrim orgânico', 'alho orgânico', 'vinho', 'azeite extravirgem'],
        'tecnica': 'Braseamento',
        'beneficios': ['Proteína de alta qualidade', 'Ferro heme: absorção eficiente', 'Zinco: fortalece sistema imunológico'],
        'riscos': ['Pode conter traços de glúten']
    },
    'quiaboempanado': {
        'descricao': 'Quiabo orgânico empanado artesanalmente, assado em forno combinado (sem fritura)',
        'ingredientes': ['quiabo orgânico', 'farinha (uso controlado)', 'ovo', 'sal'],
        'tecnica': 'Empanado e assado em forno combinado (SEM FRITURA)',
        'beneficios': ['Fibras solúveis: regulam colesterol', 'Vitamina C: fortalece imunidade', 'Assado: muito mais leve'],
        'riscos': ['Contém glúten', 'Alérgeno: ovo']
    },
    'rolinhovietnamita': {
        'descricao': 'Rolinho primavera vietnamita com camarão fresco e vegetais orgânicos',
        'ingredientes': ['papel de arroz', 'camarão fresco', 'vegetais orgânicos', 'macarrão de arroz', 'ervas orgânicas'],
        'tecnica': 'Preparo a frio',
        'beneficios': ['Proteína magra do camarão', 'Baixíssimas calorias', 'Sem fritura: versão saudável'],
        'riscos': ['Alérgeno: crustáceo', 'Pode conter traços de glúten']
    },
    'salpicaodefrango': {
        'descricao': 'Salada de frango preparado sous vide, desfiado com maionese artesanal e legumes orgânicos',
        'ingredientes': ['frango sous vide desfiado', 'maionese artesanal', 'cenoura orgânica', 'batata palha', 'milho', 'ervilha'],
        'tecnica': 'Frango sous vide + preparo a frio',
        'beneficios': ['Proteína magra: ideal para dietas', 'Vitaminas dos legumes: imunidade', 'Frango macio: técnica sous vide'],
        'riscos': ['Alérgeno: ovo (maionese)', 'Pode conter traços de glúten']
    },
    'sobrecoxaaotandoori': {
        'descricao': 'Sobrecoxa de frango fresco marinada em especiarias tandoori importadas da Índia',
        'ingredientes': ['sobrecoxa de frango fresco', 'iogurte fresco', 'garam masala importado', 'cúrcuma importada', 'páprica importada', 'gengibre fresco'],
        'tecnica': 'Marinado em iogurte + assado em forno combinado',
        'beneficios': ['Cúrcuma: poderoso anti-inflamatório', 'Probióticos do iogurte: saúde intestinal', 'Proteína de qualidade'],
        'riscos': ['Contém lactose', 'Pode conter traços de glúten']
    },

    # Fallback padrão
    'default': {
        'descricao': 'Prato preparado com ingredientes frescos e técnicas artesanais Cibi Sana',
        'ingredientes': ['Ingredientes frescos selecionados'],
        'tecnica': 'Técnica artesanal',
        'beneficios': ['Preparado sem aditivos químicos', 'Ingredientes frescos de qualidade'],
        'riscos': ['Consulte sobre alérgenos específicos', 'Pode conter traços de glúten']
    }
}


def get_dish_info(slug: str) -> dict:
    """Retorna informações completas do prato - busca primeiro no dish_info.json"""
    import os
    import json
    
    # Primeiro tenta ler do dish_info.json na pasta do prato
    info_path = f"/app/datasets/organized/{slug}/dish_info.json"
    if os.path.exists(info_path):
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
                # Filtrar benefícios genéricos do Cibi Sana
                beneficios = info.get('beneficios', [])
                if isinstance(beneficios, list):
                    beneficios = [b for b in beneficios if 
                        'sem aditivos' not in b.lower() and 
                        'ingredientes frescos' not in b.lower() and
                        'preparo artesanal' not in b.lower() and
                        'sem conservantes' not in b.lower()]
                    info['beneficios'] = beneficios
                return info
        except:
            pass
    
    # Fallback para dicionário em memória
    info = DISH_INFO.get(slug, DISH_INFO.get('default', {})).copy()
    
    # Filtrar benefícios genéricos
    beneficios = info.get('beneficios', [])
    if isinstance(beneficios, list):
        beneficios = [b for b in beneficios if 
            'sem aditivos' not in b.lower() and 
            'ingredientes frescos' not in b.lower() and
            'preparo artesanal' not in b.lower() and
            'sem conservantes' not in b.lower()]
        info['beneficios'] = beneficios
    
    return info


def get_dish_name(slug: str) -> str:
    """Retorna o nome correto do prato lendo do dish_info.json"""
    import os
    import json
    
    # Primeiro tenta do dicionário em memória
    if slug in DISH_NAMES:
        return DISH_NAMES[slug]
    
    # Se não encontrar, tenta ler do dish_info.json
    info_path = f"/app/datasets/organized/{slug}/dish_info.json"
    if os.path.exists(info_path):
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
                nome = info.get('nome', '')
                if nome:
                    # Cachear para próximas consultas
                    DISH_NAMES[slug] = nome
                    return nome
        except:
            pass
    
    return format_dish_name_fallback(slug)


def format_dish_name_fallback(slug: str) -> str:
    """Fallback para formatar nomes não mapeados"""
    if not slug:
        return ''
    
    name = slug.replace('ao', ' ao ').replace('de', ' de ').replace('com', ' com ')
    name = name.replace('sem', ' sem ').replace('_', ' ')
    name = ' '.join(name.split()).title()
    
    return name


def get_category(slug: str) -> str:
    """Retorna a categoria do prato lendo do dish_info.json"""
    import os
    import json
    
    # Primeiro tenta do dicionário em memória
    if slug in DISH_CATEGORIES:
        return DISH_CATEGORIES[slug]
    
    # Se não encontrar, tenta ler do dish_info.json
    info_path = f"/app/datasets/organized/{slug}/dish_info.json"
    if os.path.exists(info_path):
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
                categoria = info.get('categoria', 'não classificado')
                # Cachear para próximas consultas
                DISH_CATEGORIES[slug] = categoria
                return categoria
        except:
            pass
    
    return 'não classificado'


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
    
    dish_display = get_dish_name(dish)
    category = get_category(dish)
    category_emoji = get_category_emoji(category)
    dish_info = get_dish_info(dish)
    
    # Nutrição: priorizar dados do dish_info.json, fallback para tipo genérico
    if dish_info.get('nutricao') and dish_info['nutricao'].get('calorias'):
        nutrition = dish_info['nutricao']
    else:
        nutrition_type = get_nutrition_type(dish)
        nutrition = DISH_NUTRITION.get(nutrition_type, DISH_NUTRITION['default'])
    
    # Lógica de riscos - não duplicar aviso de glúten
    riscos = dish_info.get('riscos', [])
    contem_gluten = dish in PRATOS_COM_GLUTEN
    
    # Se contém glúten, remover "pode conter traços" dos riscos
    if contem_gluten:
        riscos = [r for r in riscos if 'traços de glúten' not in r.lower()]
    
    # DECISÃO DE CONFIANÇA
    if score >= 0.85:
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
            'alternatives': []
        }
    
    elif score >= 0.50:
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
    """Verifica se o prato tem riscos para o usuário."""
    return None
