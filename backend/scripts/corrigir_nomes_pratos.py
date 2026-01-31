#!/usr/bin/env python3
"""
Script para corrigir nomes de pratos nos arquivos dish_info.json
Converte slugs colados para nomes com espaços
"""

import os
import json
import re

# Mapeamento manual para nomes mais complexos
NOMES_CORRIGIDOS = {
    # Gelatinas
    "gelatinadeuva": "Gelatina de Uva",
    "gelatinademorango": "Gelatina de Morango",
    "gelatinadecereja": "Gelatina de Cereja",
    "gelatinadeabacaxi": "Gelatina de Abacaxi",
    
    # Arroz
    "arrozbranco": "Arroz Branco",
    "arrozintegral": "Arroz Integral",
    "arrozintlegumes": "Arroz Integral com Legumes",
    "arroz7graos": "Arroz 7 Grãos",
    "arroz7graoscomfrutassecas": "Arroz 7 Grãos com Frutas Secas",
    "arroz7graoscomlegumes": "Arroz 7 Grãos com Legumes",
    "arrozcombrocoliseamendoas": "Arroz com Brócolis e Amêndoas",
    
    # Pudins e Sobremesas
    "pudimdeleitecondensado": "Pudim de Leite Condensado",
    "manjardecococomcaldadeameixa": "Manjar de Coco com Calda de Ameixa",
    "bolochocolatevegano": "Bolo de Chocolate Vegano",
    "tiramisuvegano": "Tiramisù Vegano",
    "bolodegengibre": "Bolo de Gengibre",
    "batatadoce": "Batata Doce",
    "docedebananavegano_semacucar": "Doce de Banana Vegano Sem Açúcar",
    
    # Almôndegas
    "almdegasmolhosugo": "Almôndegas ao Molho Sugo",
    "almôndegasaomolho": "Almôndegas ao Molho",
    
    # Bacalhau
    "bacalhaucomnatas": "Bacalhau com Natas",
    "bacalhaugomesdesa": "Bacalhau Gomes de Sá",
    "bolinhodebacalhau": "Bolinho de Bacalhau",
    
    # Berinjela
    "beringelaaocurrykincam": "Berinjela ao Curry Kincam",
    "beringelaaopuredelimaosiciliano": "Berinjela ao Purê de Limão Siciliano",
    "beringelaaopurêcomlimãosicilianoepiclesdededodemoça": "Berinjela ao Purê com Limão Siciliano e Picles de Dedo de Moça",
    
    # Vegetais
    "aboboraaocurry": "Abóbora ao Curry",
    "beterrabaaobalsamico": "Beterraba ao Balsâmico",
    "brocoliscomparmesao": "Brócolis com Parmesão",
    "brocolisgratinado": "Brócolis Gratinado",
    "cebolascaramelizadas": "Cebolas Caramelizadas",
    "cenouraaoiogurte": "Cenoura ao Iogurte",
    "cenourapalito": "Cenoura Palito",
    "couveflorgratinada": "Couve-Flor Gratinada",
    "batatacompaprica": "Batata com Páprica",
    "alhoporogratinadovegano": "Alho-Poró Gratinado Vegano",
    "jiloempanado": "Jiló Empanado",
    "quiaboempanado": "Quiabo Empanado",
    
    # Carnes
    "figadoacebolado": "Fígado Acebolado",
    "frangoaparmegiana": "Frango à Parmegiana",
    "frangoassado": "Frango Assado",
    "frangocremedelimaosalnegro": "Frango ao Creme de Limão e Sal Negro",
    "frangoàmilanesa": "Frango à Milanesa",
    "peitodefrangogrelhado": "Peito de Frango Grelhado",
    "escondidinhodecarneseca": "Escondidinho de Carne Seca",
    "atumaogergelim": "Atum ao Gergelim",
    "cestinhadecamarao": "Cestinha de Camarão",
    "hamburgerdecarne": "Hambúrguer de Carne",
    "hamburguervegano": "Hambúrguer Vegano",
    "kiberecheado": "Kibe Recheado",
    "maminhaaomolhomongolia": "Maminha ao Molho Mongólia",
    "sobrecoxaaotucupi": "Sobrecoxa ao Tucupi",
    "strogonoffdefilemignon": "Estrogonofe de Filé Mignon",
    
    # Massas
    "canelonedeespinafre": "Canelone de Espinafre",
    "conchiglionirecheados": "Conchiglioni Recheados",
    "panquecadefrango": "Panqueca de Frango",
    "macarrãodearrozcomvegetais": "Macarrão de Arroz com Vegetais",
    "lasanhadeespinafre": "Lasanha de Espinafre",
    "risoneaocremedelimao": "Risone ao Creme de Limão",
    "risoneaopesto": "Risone ao Pesto",
    
    # Peixes
    "filedepeixeaomisso": "Filé de Peixe ao Missô",
    "filedepeixemolhoconfit": "Filé de Peixe ao Molho Confit",
    
    # Saladas
    "cuscuzmarroquino": "Cuscuz Marroquino",
    "cuscuzdetapioca": "Cuscuz de Tapioca",
    "tabuledequinoa": "Tabule de Quinoa",
    "carpacciodeabobrinhacomqueijovegano": "Carpaccio de Abobrinha com Queijo Vegano",
    "carpacciodelaranja": "Carpaccio de Laranja",
    "saladamediterranea": "Salada Mediterrânea",
    "saladadebifumcompepino": "Salada de Bifum com Pepino",
    "saladadefeijaobranco": "Salada de Feijão Branco",
    "saladadefeijaobrancocomtomateecebola": "Salada de Feijão Branco com Tomate e Cebola",
    "saladadegraodebico": "Salada de Grão de Bico",
    "saladadelentilha": "Salada de Lentilha",
    "saladadeovoscombatata": "Salada de Ovos com Batata",
    "saladadequinoacomlegumes": "Salada de Quinoa com Legumes",
    "saladaderabanetecomlaranja": "Salada de Rabanete com Laranja",
    "saladadetomateemrodelas": "Salada de Tomate em Rodelas",
    "saladatailandesa": "Salada Tailandesa",
    "saladeovos": "Salada de Ovos",
    "saladadebeterrabacomlaranjaehortela": "Salada de Beterraba com Laranja e Hortelã",
    "rolinhovietnamita": "Rolinho Vietnamita",
    "sushivietnamita": "Sushi Vietnamita",
    "umamidetomates": "Umami de Tomates",
    
    # Feijões
    "feijaobranco": "Feijão Branco",
    "feijaopreto": "Feijão Preto",
    "feijaopretosemcarne": "Feijão Preto sem Carne",
    "feijaotropeirocomcouve": "Feijão Tropeiro com Couve",
    "hamcamaraocomcarnesuina": "Ham de Camarão com Carne Suína",
    "carpacciodeperaruculaeamendoas": "Carpaccio de Pera, Rúcula e Amêndoas",
    "ervadocecomlaranja": "Erva-Doce com Laranja",
    "espetinhosdelegumesgrelhados": "Espetinhos de Legumes Grelhados",
    "saladamediterranea": "Salada Mediterrânea",
    "saladadefrangocomlegumes": "Salada de Frango com Legumes",
    "saladadebifumcompepino": "Salada de Bifum com Pepino",
    "salpicaodefrango": "Salpicão de Frango",
    
    # Outros
    "baiaodedois": "Baião de Dois",
    "feijaopreto": "Feijão Preto",
    "feijaotropeirocomcouve": "Feijão Tropeiro com Couve",
    "kibbehcomarrozehomus": "Kibbeh com Arroz e Homus",
}

def corrigir_nome(slug):
    """Retorna nome corrigido ou tenta gerar automaticamente"""
    # Primeiro tenta o mapeamento manual
    if slug.lower() in NOMES_CORRIGIDOS:
        return NOMES_CORRIGIDOS[slug.lower()]
    
    # Se tem underscore, converte normalmente
    if '_' in slug:
        name = slug.replace('_', ' ')
        words = name.split()
        small_words = {'de', 'do', 'da', 'dos', 'das', 'com', 'ao', 'e', 'a', 'o', 'à'}
        result = []
        for i, word in enumerate(words):
            if i == 0:
                result.append(word.capitalize())
            elif word.lower() in small_words:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
        return ' '.join(result)
    
    # Se não tem underscore e não está no mapeamento, retorna capitalizado
    return slug.capitalize()


def main():
    datasets_dir = "/app/datasets/organized"
    
    if not os.path.exists(datasets_dir):
        print(f"Diretório não encontrado: {datasets_dir}")
        return
    
    corrigidos = 0
    erros = 0
    
    for folder in sorted(os.listdir(datasets_dir)):
        folder_path = os.path.join(datasets_dir, folder)
        info_file = os.path.join(folder_path, "dish_info.json")
        
        if not os.path.isdir(folder_path):
            continue
        
        if not os.path.exists(info_file):
            continue
        
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            nome_atual = data.get('nome', '')
            nome_corrigido = corrigir_nome(folder)
            
            # Só atualiza se o nome mudou
            if nome_atual != nome_corrigido:
                data['nome'] = nome_corrigido
                
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ {folder}: '{nome_atual}' -> '{nome_corrigido}'")
                corrigidos += 1
        
        except Exception as e:
            print(f"❌ Erro em {folder}: {e}")
            erros += 1
    
    print(f"\n📊 Resumo: {corrigidos} corrigidos, {erros} erros")


if __name__ == "__main__":
    main()
