"""SoulNutri - Serviço de Auditoria de Dados dos Pratos
Analisa os dish_info.json e identifica problemas de qualidade
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

DATASET_DIR = Path("/app/datasets/organized")

# Ingredientes que indicam categoria específica
# NOTA: Leite de coco, leite de amêndoas, etc. NÃO são de origem animal
INGREDIENTES_ANIMAL = [
    'frango', 'carne', 'boi', 'porco', 'bacon', 'linguiça', 'salsicha',
    'peixe', 'camarão', 'atum', 'salmão', 'bacalhau', 'tilápia',
    'ovo', 'leite de vaca', 'queijo', 'creme de leite', 'manteiga', 'nata',
    'presunto', 'peito de peru', 'costela', 'maminha', 'picanha',
    'fígado', 'coração', 'moela', 'rabada', 'rabo'
]

# Ingredientes que NÃO são de origem animal (veganos)
INGREDIENTES_VEGANOS = [
    'leite de coco', 'creme de coco', 'óleo de coco',
    'leite de amêndoas', 'leite de soja', 'leite de aveia',
    'leite de arroz', 'leite vegetal', 'tofu', 'tempeh', 'seitan'
]

INGREDIENTES_LACTOSE = [
    'leite de vaca', 'queijo', 'creme de leite', 'manteiga', 'nata',
    'iogurte', 'requeijão', 'cream cheese', 'parmesão', 'mussarela',
    'ricota', 'cottage', 'gorgonzola', 'provolone', 'cheddar'
]

INGREDIENTES_GLUTEN = [
    'farinha de trigo', 'pão', 'massa', 'macarrão', 'espaguete',
    'lasanha', 'torrada', 'biscoito', 'cerveja', 'empanado',
    'milanesa', 'coxinha', 'pastel', 'croissant'
]


def audit_all_dishes() -> Dict[str, Any]:
    """Audita todos os pratos e retorna relatório de problemas.
    Usa MongoDB como fonte de verdade para a lista de pratos."""
    import pymongo
    import unicodedata
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / '.env')
    
    client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
    db = client[os.environ.get("DB_NAME", "soulnutri")]
    db_dishes = {d['slug'] for d in db.dishes.find({}, {'_id': 0, 'slug': 1})}
    client.close()
    
    def _normalize(name):
        n = name.lower().replace('-', '').replace('_', '').replace(' ', '').replace('(', '').replace(')', '')
        nfkd = unicodedata.normalize('NFKD', n)
        return ''.join(c for c in nfkd if not unicodedata.combining(c))
    
    # Build normalized lookup: norm_slug -> original_slug
    db_norm = {_normalize(s): s for s in db_dishes}
    
    problems = {
        'missing_info_file': [],
        'empty_nutrition': [],
        'unknown_names': [],
        'category_conflicts': [],
        'missing_ingredients': [],
        'missing_description': [],
        'allergen_conflicts': []
    }
    
    total_dishes = 0
    dishes_with_issues = 0
    
    # Build mapping: db_slug -> first matching folder on disk
    slug_to_folder = {}
    for dish_dir in DATASET_DIR.iterdir():
        if not dish_dir.is_dir():
            continue
        folder_norm = _normalize(dish_dir.name)
        if folder_norm in db_norm:
            db_slug = db_norm[folder_norm]
            if db_slug not in slug_to_folder:
                slug_to_folder[db_slug] = dish_dir
    
    # Pre-carregar TODOS os pratos do MongoDB de uma vez (performance)
    db_dishes = {}
    try:
        import pymongo
        client2 = pymongo.MongoClient(os.environ.get("MONGO_URL"), serverSelectionTimeoutMS=5000)
        db2 = client2[os.environ.get("DB_NAME", "soulnutri")]
        for doc in db2.dishes.find({}, {"_id": 0}):
            slug = doc.get("slug", "")
            if slug:
                db_dishes[slug] = doc
        client2.close()
        logger.info(f"[AUDIT] Carregados {len(db_dishes)} pratos do MongoDB")
    except Exception as e:
        logger.warning(f"[AUDIT] Erro ao carregar MongoDB: {e}")

    for db_slug, dish_dir in slug_to_folder.items():
        total_dishes += 1
        
        # Fonte de verdade: MongoDB. Fallback: dish_info.json local.
        info = None
        
        # 1. Tentar ler do MongoDB (já carregado em memória)
        db_doc = db_dishes.get(db_slug)
        if db_doc:
            info = {
                "nome": db_doc.get("nome") or db_doc.get("name", ""),
                "categoria": db_doc.get("categoria") or db_doc.get("category", ""),
                "ingredientes": db_doc.get("ingredientes", []),
                "descricao": db_doc.get("descricao", ""),
                "nutricao": db_doc.get("nutricao") or db_doc.get("nutrition", {}),
                "alergenos": db_doc.get("alergenos", []),
            }
        
        # 2. Fallback: dish_info.json local
        if not info:
            info_path = dish_dir / "dish_info.json"
            if not info_path.exists():
                problems['missing_info_file'].append({
                    'slug': db_slug,
                    'issue': 'Sem dados no MongoDB e sem dish_info.json local',
                    'severity': 'high'
                })
                dishes_with_issues += 1
                continue
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    info = json.load(f)
            except Exception as e:
                problems['missing_info_file'].append({
                    'slug': db_slug,
                    'issue': f'Erro ao ler arquivo: {str(e)}',
                    'severity': 'high'
                })
                dishes_with_issues += 1
                continue
        
        has_issue = False
        
        # Verificar nome Unknown
        nome = info.get('nome', '')
        if 'unknown' in nome.lower() or not nome:
            problems['unknown_names'].append({
                'slug': db_slug,
                'nome': nome,
                'issue': 'Nome contém "Unknown" ou está vazio',
                'severity': 'high'
            })
            has_issue = True
        
        # Verificar nutrição vazia
        nutricao = info.get('nutricao', {})
        if not nutricao or not nutricao.get('calorias') or nutricao.get('calorias') == '':
            problems['empty_nutrition'].append({
                'slug': db_slug,
                'nome': nome,
                'issue': 'Informações nutricionais vazias',
                'severity': 'medium'
            })
            has_issue = True
        
        # Verificar ingredientes (só se prato tem dados preenchidos no MongoDB)
        ingredientes = info.get('ingredientes', [])
        has_some_data = bool(info.get('descricao') or info.get('categoria') or nutricao)
        if has_some_data and (not ingredientes or len(ingredientes) == 0):
            problems['missing_ingredients'].append({
                'slug': db_slug,
                'nome': nome,
                'issue': 'Lista de ingredientes vazia',
                'severity': 'medium'
            })
            has_issue = True
        
        # Verificar descrição (só se prato tem dados preenchidos)
        desc_raw = info.get('descricao', '')
        descricao = desc_raw if isinstance(desc_raw, str) else str(desc_raw or '')
        if has_some_data and (not descricao or len(descricao) < 10):
            problems['missing_description'].append({
                'slug': db_slug,
                'nome': nome,
                'issue': 'Descrição ausente ou muito curta',
                'severity': 'low'
            })
            has_issue = True
        
        # Verificar conflitos de categoria
        cat_raw = info.get('categoria', '')
        categoria = (cat_raw if isinstance(cat_raw, str) else str(cat_raw or '')).lower()
        ingredientes_list = ingredientes if isinstance(ingredientes, list) else []
        ingredientes_lower = [str(i).lower() for i in ingredientes_list if i]
        ingredientes_text = ' '.join(ingredientes_lower)
        
        # Função para verificar se ingrediente é de origem animal (excluindo versões vegetais)
        def tem_ingrediente_animal(ing, texto):
            # Lista de termos que indicam versão vegana/vegetal
            termos_veganos = ['vegano', 'vegetal', 'de coco', 'de soja', 'de amêndoas', 
                             'de aveia', 'de arroz', 'de castanha', 'plant-based']
            
            # Se o ingrediente está no texto
            if ing in texto:
                # Verificar se não é uma versão vegana
                # Ex: "queijo vegano", "manteiga vegetal", "leite de coco"
                for termo in termos_veganos:
                    # Busca padrões como "queijo vegano", "manteiga vegetal"
                    if f"{ing} {termo}" in texto or f"{ing}{termo}" in texto:
                        return False
                    # Busca padrões como "leite de coco" 
                    if termo in texto and ing in termo.split():
                        return False
                
                # Casos especiais
                if ing == 'leite':
                    # "leite de coco", "leite de soja", etc. são veganos
                    if any(v in texto for v in ['leite de coco', 'leite de soja', 'leite de amêndoas', 
                                                 'leite de aveia', 'leite de arroz', 'leite vegetal',
                                                 'leite de castanha', 'leite de caju']):
                        return False
                
                if ing == 'queijo':
                    # "queijo vegano", "queijo de castanha" são veganos
                    if any(v in texto for v in ['queijo vegano', 'queijo de castanha', 'queijo de caju',
                                                 'queijo vegetal', 'queijo plant']):
                        return False
                
                if ing == 'manteiga':
                    # "manteiga vegetal", "manteiga de coco" são veganos
                    if any(v in texto for v in ['manteiga vegetal', 'manteiga de coco', 'manteiga vegana',
                                                 'manteiga de cacau', 'manteiga de amendoim']):
                        return False
                
                if ing == 'creme':
                    # "creme de coco", "creme vegetal" são veganos  
                    if any(v in texto for v in ['creme de coco', 'creme vegetal', 'creme vegano']):
                        return False
                
                if ing == 'mel':
                    # Alguns veganos evitam mel, mas não vamos considerar como conflito crítico
                    # Mel de agave, melado de cana são veganos
                    if any(v in texto for v in ['mel de agave', 'melado', 'maple', 'xarope']):
                        return False
                    # Se tem apenas "mel" simples, não considerar conflito (é debatível)
                    return False
                
                return True
            return False
        
        if categoria == 'vegano':
            for ing in INGREDIENTES_ANIMAL:
                if tem_ingrediente_animal(ing, ingredientes_text):
                    problems['category_conflicts'].append({
                        'slug': db_slug,
                        'nome': nome,
                        'issue': f'Prato marcado como VEGANO mas contém "{ing}"',
                        'severity': 'high'
                    })
                    has_issue = True
                    break
        
        elif categoria == 'vegetariano':
            for ing in ['frango', 'carne', 'boi', 'porco', 'bacon', 'peixe', 'camarão']:
                if ing in ingredientes_text:
                    problems['category_conflicts'].append({
                        'slug': db_slug,
                        'nome': nome,
                        'issue': f'Prato marcado como VEGETARIANO mas contém "{ing}"',
                        'severity': 'high'
                    })
                    has_issue = True
                    break
        
        # Verificar conflitos de alérgenos
        contem_gluten = info.get('contem_gluten', False)
        for ing in INGREDIENTES_GLUTEN:
            if ing in ingredientes_text and not contem_gluten:
                problems['allergen_conflicts'].append({
                    'slug': db_slug,
                    'nome': nome,
                    'issue': f'Contém "{ing}" mas não está marcado como contém glúten',
                    'severity': 'medium'
                })
                has_issue = True
                break
        
        if has_issue:
            dishes_with_issues += 1
    
    # Calcular estatísticas
    return {
        'total_dishes': total_dishes,
        'dishes_with_issues': dishes_with_issues,
        'health_score': round((1 - dishes_with_issues / total_dishes) * 100, 1) if total_dishes > 0 else 0,
        'problems': problems,
        'summary': {
            'missing_info_file': len(problems['missing_info_file']),
            'empty_nutrition': len(problems['empty_nutrition']),
            'unknown_names': len(problems['unknown_names']),
            'category_conflicts': len(problems['category_conflicts']),
            'missing_ingredients': len(problems['missing_ingredients']),
            'missing_description': len(problems['missing_description']),
            'allergen_conflicts': len(problems['allergen_conflicts'])
        }
    }


async def fix_dish_with_ai(slug: str) -> Dict[str, Any]:
    """Usa IA para corrigir/completar informações de um prato"""
    from services.generic_ai import analyze_dish_for_correction
    
    info_path = DATASET_DIR / slug / "dish_info.json"
    
    # Carregar info atual
    current_info = {}
    if info_path.exists():
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                current_info = json.load(f)
        except:
            pass
    
    # Buscar primeira imagem do prato
    dish_dir = DATASET_DIR / slug
    images = list(dish_dir.glob("*.jpg")) + list(dish_dir.glob("*.jpeg"))
    
    if not images:
        return {'ok': False, 'error': 'Nenhuma imagem encontrada para o prato'}
    
    # Ler imagem
    with open(images[0], 'rb') as f:
        image_bytes = f.read()
    
    # Chamar IA para análise
    ai_result = await analyze_dish_for_correction(image_bytes, current_info)
    
    if not ai_result.get('ok'):
        return ai_result
    
    # Mesclar informações (IA complementa o que está faltando)
    suggestions = ai_result.get('suggestions', {})
    
    return {
        'ok': True,
        'slug': db_slug,
        'current_info': current_info,
        'suggestions': suggestions,
        'changes_needed': ai_result.get('changes_needed', [])
    }


def apply_ai_suggestions(slug: str, suggestions: Dict) -> Dict[str, Any]:
    """Aplica as sugestões da IA ao dish_info.json"""
    
    info_path = DATASET_DIR / slug / "dish_info.json"
    
    # Carregar info atual
    current_info = {}
    if info_path.exists():
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                current_info = json.load(f)
        except:
            pass
    
    # Aplicar sugestões (apenas campos vazios ou marcados para correção)
    updated_info = {**current_info}
    
    for key, value in suggestions.items():
        if key not in current_info or not current_info.get(key):
            updated_info[key] = value
    
    # Garantir slug
    updated_info['slug'] = slug
    
    # Salvar
    try:
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(updated_info, f, ensure_ascii=False, indent=2)
        
        return {'ok': True, 'message': f'Informações de {slug} atualizadas'}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


async def consolidate_duplicate_dishes(group: list) -> dict:
    """
    Consolida um grupo de pratos duplicados:
    1. Usa IA para mesclar as informações
    2. Move todas as imagens para a pasta principal
    3. Remove pastas vazias
    """
    import shutil
    from services.generic_ai import fix_dish_data_with_ai
    
    if len(group) < 2:
        return {"ok": False, "error": "Grupo precisa ter pelo menos 2 pratos"}
    
    # Escolher o slug principal (o primeiro ou o mais curto/limpo)
    main_slug = min(group, key=lambda x: len(x))
    main_dir = DATASET_DIR / main_slug
    
    # Coletar todas as informações existentes
    all_info = []
    all_images = []
    
    for slug in group:
        dish_dir = DATASET_DIR / slug
        if not dish_dir.exists():
            continue
        
        # Coletar info
        info_path = dish_dir / "dish_info.json"
        if info_path.exists():
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    info['_slug'] = slug
                    all_info.append(info)
            except:
                pass
        
        # Coletar imagens
        for img in dish_dir.glob("*.jpg"):
            all_images.append((slug, img))
        for img in dish_dir.glob("*.jpeg"):
            all_images.append((slug, img))
    
    if not all_info:
        return {"ok": False, "error": "Nenhuma informação encontrada nos pratos"}
    
    # Mesclar informações - pegar o mais completo de cada campo
    merged_info = {
        "slug": main_slug,
        "nome": "",
        "categoria": "",
        "descricao": "",
        "ingredientes": [],
        "beneficios": [],
        "riscos": [],
        "nutricao": {},
        "contem_gluten": False,
        "contem_lactose": False,
        "contem_ovo": False,
        "contem_castanhas": False,
        "contem_frutos_mar": False,
        "contem_soja": False
    }
    
    for info in all_info:
        # Nome - pegar o mais limpo (sem "unknown", sem underscore)
        nome = info.get('nome', '')
        if nome and not 'unknown' in nome.lower():
            if not merged_info['nome'] or '_' in merged_info['nome']:
                merged_info['nome'] = nome
        
        # Categoria - pegar qualquer uma definida
        if info.get('categoria') and not merged_info['categoria']:
            merged_info['categoria'] = info['categoria']
        
        # Descrição - pegar a mais longa
        if len(info.get('descricao', '')) > len(merged_info.get('descricao', '')):
            merged_info['descricao'] = info['descricao']
        
        # Ingredientes - unir todos únicos
        for ing in info.get('ingredientes', []):
            if ing and ing.lower() not in [i.lower() for i in merged_info['ingredientes']]:
                merged_info['ingredientes'].append(ing)
        
        # Benefícios - unir todos únicos
        for ben in info.get('beneficios', []):
            if ben and ben not in merged_info['beneficios']:
                merged_info['beneficios'].append(ben)
        
        # Riscos - unir todos únicos
        for risk in info.get('riscos', []):
            if risk and risk not in merged_info['riscos']:
                merged_info['riscos'].append(risk)
        
        # Nutrição - pegar valores preenchidos
        nut = info.get('nutricao', {})
        for key in ['calorias', 'proteinas', 'carboidratos', 'gorduras']:
            if nut.get(key) and not merged_info['nutricao'].get(key):
                merged_info['nutricao'][key] = nut[key]
        
        # Alérgenos - OR lógico
        for allergen in ['contem_gluten', 'contem_lactose', 'contem_ovo', 'contem_castanhas', 'contem_frutos_mar', 'contem_soja']:
            if info.get(allergen):
                merged_info[allergen] = True
    
    # Garantir que a pasta principal existe
    main_dir.mkdir(parents=True, exist_ok=True)
    
    # Mover todas as imagens para a pasta principal
    moved_images = 0
    for slug, img_path in all_images:
        if slug != main_slug:
            new_path = main_dir / img_path.name
            # Se já existe, adicionar sufixo
            if new_path.exists():
                new_path = main_dir / f"{img_path.stem}_{slug}{img_path.suffix}"
            try:
                shutil.copy2(img_path, new_path)
                moved_images += 1
            except:
                pass
    
    # Salvar info consolidada
    info_path = main_dir / "dish_info.json"
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(merged_info, f, ensure_ascii=False, indent=2)
    
    # Remover pastas duplicadas (manter apenas a principal)
    removed_dirs = []
    for slug in group:
        if slug != main_slug:
            dish_dir = DATASET_DIR / slug
            if dish_dir.exists():
                try:
                    shutil.rmtree(dish_dir)
                    removed_dirs.append(slug)
                except:
                    pass
    
    return {
        "ok": True,
        "main_slug": main_slug,
        "merged_info": merged_info,
        "images_moved": moved_images,
        "dirs_removed": removed_dirs,
        "original_group": group
    }


def find_duplicate_groups() -> list:
    """Encontra grupos de pratos duplicados baseado em similaridade de nome"""
    from difflib import SequenceMatcher
    
    pratos = []
    for dish_dir in DATASET_DIR.iterdir():
        if not dish_dir.is_dir():
            continue
        info_path = dish_dir / "dish_info.json"
        if info_path.exists():
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    nome = info.get('nome', dish_dir.name).lower().strip()
                    if 'unknown' in nome:
                        continue
                    pratos.append({'nome': nome, 'slug': dish_dir.name})
            except:
                pass
    
    grupos = []
    usados = set()
    
    for i, p1 in enumerate(pratos):
        if p1['slug'] in usados:
            continue
        
        similares = [p1['slug']]
        for j, p2 in enumerate(pratos):
            if i >= j or p2['slug'] in usados:
                continue
            
            ratio = SequenceMatcher(None, p1['nome'], p2['nome']).ratio()
            if ratio > 0.80:
                similares.append(p2['slug'])
                usados.add(p2['slug'])
        
        if len(similares) > 1:
            usados.add(p1['slug'])
            grupos.append(similares)
    
    return grupos
