"""
Script para enriquecer pratos com informações científicas balanceadas.
Usa GPT-4o para gerar:
- beneficio_principal (algo que o cliente NAO sabe, com dados)
- curiosidade_cientifica (fato interessante ou alerta equilibrado)
- referencia_pesquisa (fonte científica)
- alerta_saude (se relevante, com equilíbrio)
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

sys.path.insert(0, '/app/backend')
load_dotenv('/app/backend/.env')

# Emergent Integrations
from emergentintegrations.llm.chat import LlmChat, UserMessage

EMERGENT_KEY = os.environ.get('EMERGENT_LLM_KEY')

SYSTEM_PROMPT = """Você é um nutricionista especializado em educação alimentar científica.
Sua missão é fornecer informações RELEVANTES que o cliente NÃO conhece.

REGRAS IMPORTANTES:
1. NUNCA diga o óbvio (ex: "gordura faz mal", "açúcar engorda")
2. SEMPRE inclua DADOS NUMÉRICOS quando possível
3. EQUILIBRE: 50% benefícios/curiosidades positivas, 50% alertas quando relevante
4. Cite FONTES reais (OMS, ANVISA, UNICAMP, Harvard, Nature, etc.)
5. Seja EDUCATIVO, não alarmista
6. Use linguagem acessível mas precisa

FORMATO DE RESPOSTA (JSON):
{
  "beneficio_principal": "Informação científica positiva com dados. Ex: 'Betacaroteno (485mcg/100g) - converte em vitamina A no fígado, essencial para visão noturna. Estudo USP 2021 mostrou que...'",
  "curiosidade_cientifica": "Fato interessante ou dica prática. Ex: 'Cozinhar cenoura AUMENTA absorção de betacaroteno em 6x vs crua - o calor quebra paredes celulares'",
  "referencia_pesquisa": "Fonte científica. Ex: 'Tabela TACO - UNICAMP, 2011'",
  "alerta_saude": "Se relevante, alerta EQUILIBRADO. Ex: 'Alto teor de oxalato (espinafre) pode reduzir absorção de cálcio - combinar com vitamina C ajuda' OU null se não houver alerta"
}

EXEMPLOS DE BOAS INFORMAÇÕES:
- "Curry contém curcumina - anti-inflamatório natural que estudos mostram ser tão eficaz quanto ibuprofeno para artrite (Journal of Medicinal Food, 2019)"
- "Licopeno do tomate cozido é 4x mais biodisponível que do cru - o calor rompe membranas celulares"
- "Peixes grandes (atum, peixe-espada) acumulam mercúrio - FDA recomenda máx 340g/semana"

EXEMPLOS DE INFORMAÇÕES RUINS (EVITAR):
- "Rico em vitaminas" (genérico)
- "Faz bem para saúde" (óbvio)
- "Contém proteínas" (todos sabem)
- "Evitar em excesso" (vale para tudo)"""


async def enrich_single_dish(dish: dict) -> dict:
    """Enriquece um único prato com informações científicas"""
    
    nome = dish.get('nome', '')
    categoria = dish.get('categoria', '')
    ingredientes = dish.get('ingredientes', [])
    beneficios_existentes = dish.get('beneficios', [])
    riscos_existentes = dish.get('riscos', [])
    
    user_prompt = f"""Analise este prato e gere informações científicas EDUCATIVAS e BALANCEADAS:

PRATO: {nome}
CATEGORIA: {categoria}
INGREDIENTES: {', '.join(ingredientes) if ingredientes else 'não especificados'}
BENEFÍCIOS JÁ CONHECIDOS: {', '.join(beneficios_existentes) if beneficios_existentes else 'nenhum'}
RISCOS JÁ CONHECIDOS: {', '.join(riscos_existentes) if riscos_existentes else 'nenhum'}

Gere informações que o cliente NÃO sabe, com dados numéricos e fontes reais.
Responda APENAS com o JSON no formato especificado."""

    import uuid
    session_id = str(uuid.uuid4())
    
    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id=session_id,
        system_message=SYSTEM_PROMPT
    ).with_model("openai", "gpt-4o")
    
    response = await chat.send_message(UserMessage(text=user_prompt))
    
    # Extrair JSON da resposta
    import json
    import re
    
    # Tentar encontrar JSON na resposta
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return data
        except json.JSONDecodeError:
            pass
    
    # Se não conseguir parsear, retornar estrutura padrão
    return {
        "beneficio_principal": f"Informação científica sobre {nome} - consulte um nutricionista",
        "curiosidade_cientifica": f"Cada ingrediente de {nome} tem propriedades únicas",
        "referencia_pesquisa": "Tabela TACO - UNICAMP",
        "alerta_saude": None
    }


async def enrich_all_dishes(batch_size: int = 10, max_dishes: int = None):
    """Enriquece todos os pratos que ainda não têm informações científicas"""
    
    print("="*60)
    print("SOULNUTRI - ENRIQUECIMENTO DE DADOS CIENTÍFICOS")
    print("="*60)
    
    # Conectar ao MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['soulnutri']
    
    # Buscar pratos sem informações científicas
    query = {
        '$or': [
            {'beneficio_principal': {'$exists': False}},
            {'beneficio_principal': None},
            {'beneficio_principal': ''}
        ]
    }
    
    dishes_to_enrich = await db.dishes.find(query).to_list(length=500)
    total = len(dishes_to_enrich)
    
    if max_dishes:
        dishes_to_enrich = dishes_to_enrich[:max_dishes]
    
    print(f"\nPratos para enriquecer: {len(dishes_to_enrich)} de {total}")
    
    if not dishes_to_enrich:
        print("Todos os pratos já estão enriquecidos!")
        return
    
    success_count = 0
    error_count = 0
    
    for i, dish in enumerate(dishes_to_enrich, 1):
        nome = dish.get('nome', dish.get('slug', 'desconhecido'))
        print(f"\n[{i}/{len(dishes_to_enrich)}] Enriquecendo: {nome}...")
        
        try:
            enriched_data = await enrich_single_dish(dish)
            
            # Atualizar no MongoDB
            update_result = await db.dishes.update_one(
                {'_id': dish['_id']},
                {'$set': {
                    'beneficio_principal': enriched_data.get('beneficio_principal'),
                    'curiosidade_cientifica': enriched_data.get('curiosidade_cientifica'),
                    'referencia_pesquisa': enriched_data.get('referencia_pesquisa'),
                    'alerta_saude': enriched_data.get('alerta_saude'),
                    'updated_at': datetime.utcnow()
                }}
            )
            
            if update_result.modified_count > 0:
                print(f"   Benefício: {enriched_data.get('beneficio_principal', '')[:60]}...")
                print(f"   Curiosidade: {enriched_data.get('curiosidade_cientifica', '')[:60]}...")
                success_count += 1
            else:
                print(f"   AVISO: Nenhuma modificação feita")
                
        except Exception as e:
            print(f"   ERRO: {e}")
            error_count += 1
        
        # Pausa entre requisições para não sobrecarregar
        await asyncio.sleep(0.5)
    
    print("\n" + "="*60)
    print(f"CONCLUÍDO!")
    print(f"  Sucesso: {success_count}")
    print(f"  Erros: {error_count}")
    print("="*60)
    
    client.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', type=int, default=10, help='Tamanho do lote')
    parser.add_argument('--max', type=int, default=None, help='Máximo de pratos a processar')
    args = parser.parse_args()
    
    asyncio.run(enrich_all_dishes(batch_size=args.batch, max_dishes=args.max))
