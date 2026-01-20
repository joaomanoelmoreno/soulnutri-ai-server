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
}

# Descrição, ingredientes, benefícios e riscos dos pratos
DISH_INFO = {
    'baiaodedois': {
        'descricao': 'Prato típico nordestino com arroz e feijão-de-corda cozidos juntos',
        'ingredientes': ['arroz', 'feijão-de-corda', 'bacon', 'queijo coalho', 'manteiga', 'temperos'],
        'beneficios': ['Rico em proteínas', 'Fonte de fibras', 'Energia de longa duração'],
        'riscos': ['Alto teor de sódio', 'Contém lactose (queijo)', 'Gordura saturada (bacon)']
    },
    'espaguete': {
        'descricao': 'Massa italiana longa servida com molho',
        'ingredientes': ['massa de trigo', 'molho de tomate', 'azeite', 'alho', 'manjericão'],
        'beneficios': ['Fonte de carboidratos', 'Energia rápida', 'Baixo teor de gordura'],
        'riscos': ['Contém glúten', 'Alto índice glicêmico']
    },
    'feijaocariocasemcarne': {
        'descricao': 'Feijão carioca cozido em caldo temperado, versão vegetariana',
        'ingredientes': ['feijão carioca', 'alho', 'cebola', 'louro', 'sal'],
        'beneficios': ['Rico em fibras', 'Proteína vegetal', 'Fonte de ferro', 'Baixa gordura'],
        'riscos': ['Pode causar gases', 'Moderado em carboidratos']
    },
    'aboboraaocurry': {
        'descricao': 'Abóbora cozida com especiarias indianas em molho cremoso',
        'ingredientes': ['abóbora', 'curry', 'leite de coco', 'gengibre', 'cúrcuma'],
        'beneficios': ['Rico em betacaroteno', 'Antioxidantes', 'Anti-inflamatório', 'Baixa caloria'],
        'riscos': ['Pode conter leite de coco (alérgenos)']
    },
    'filedepeixeaomolhodelimao': {
        'descricao': 'Filé de peixe branco grelhado com molho cítrico de limão',
        'ingredientes': ['peixe branco', 'limão', 'manteiga', 'alcaparras', 'salsinha'],
        'beneficios': ['Rico em ômega-3', 'Proteína magra', 'Baixa caloria', 'Bom para coração'],
        'riscos': ['Contém lactose (manteiga)', 'Alérgeno: peixe']
    },
    'maminhaaomolhomostarda': {
        'descricao': 'Corte bovino nobre assado com molho de mostarda',
        'ingredientes': ['maminha bovina', 'mostarda', 'creme de leite', 'vinho branco'],
        'beneficios': ['Alto teor proteico', 'Rico em ferro e zinco', 'Vitaminas do complexo B'],
        'riscos': ['Gordura saturada', 'Contém lactose', 'Alto colesterol']
    },
    'brocolisgratinado': {
        'descricao': 'Brócolis ao forno com queijo gratinado',
        'ingredientes': ['brócolis', 'queijo mussarela', 'creme de leite', 'parmesão'],
        'beneficios': ['Rico em vitamina C', 'Fibras', 'Cálcio do queijo', 'Antioxidantes'],
        'riscos': ['Contém lactose', 'Gordura do queijo']
    },
    'default': {
        'descricao': 'Prato preparado com ingredientes frescos',
        'ingredientes': ['Ingredientes variados conforme preparo'],
        'beneficios': ['Verifique informações com o atendente'],
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
    elif 'carne' in slug_lower or 'maminha' in slug_lower or 'costela' in slug_lower or 'entrecote' in slug_lower:
        return 'carne'
    elif 'espaguete' in slug_lower or 'nhoque' in slug_lower or 'lasanha' in slug_lower or 'canelone' in slug_lower:
        return 'massa'
    elif 'bolo' in slug_lower or 'mousse' in slug_lower or 'cocada' in slug_lower or 'goiabada' in slug_lower:
        return 'sobremesa'
    elif any(v in slug_lower for v in ['brocoli', 'cenoura', 'beterraba', 'repolho', 'berinjela', 'abobrinha']):
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
            'alternatives': alternatives
        }


def get_risk_alert(dish: str, user_restrictions: List[str] = None) -> Optional[str]:
    """
    Verifica se o prato tem riscos para o usuário.
    (Placeholder para funcionalidade Premium)
    """
    # TODO: Implementar cruzamento com base de ingredientes/alérgenos
    return None
