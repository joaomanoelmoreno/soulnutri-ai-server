#!/usr/bin/env python3
"""
Renomeia todas as pastas para o padrão "Nome Com Espacos"
"""
import os
import re

DATASET_DIR = "/app/datasets/organized"

def to_title_case(name):
    """Converte nome para Title Case com espaços"""
    # Remove underscores e substitui por espaços
    name = name.replace('_', ' ')
    
    # Separa palavras coladas (camelCase ou tudo junto)
    # Ex: "aboboraaocurry" -> "abobora ao curry"
    
    # Lista de preposições/artigos para manter minúsculo
    lowercase_words = {'de', 'do', 'da', 'dos', 'das', 'ao', 'a', 'o', 'e', 'com', 'em', 'no', 'na', 'por'}
    
    # Dicionário de palavras conhecidas para separação
    known_words = [
        'abobora', 'abobrinha', 'acelga', 'acucar', 'agriao', 'alface', 'alho', 'almondega',
        'ameixa', 'amendoa', 'amendoim', 'arroz', 'atum', 'azeite', 'azeitona', 'bacalhau',
        'bacon', 'baiao', 'banana', 'batata', 'berinjela', 'beringela', 'beterraba', 'bife',
        'bolo', 'brocolis', 'brownie', 'camarao', 'canelone', 'carne', 'carpaccio', 'cebola',
        'cenoura', 'cestinha', 'ceviche', 'chocolate', 'cogumelo', 'costelinha', 'costela',
        'couve', 'coxa', 'coxinha', 'creme', 'croquete', 'curry', 'cuscuz', 'doce', 'dois',
        'espaguete', 'espinafre', 'farofa', 'feijao', 'figo', 'figado', 'file', 'flor',
        'frango', 'frita', 'fritas', 'frutas', 'funghi', 'ganache', 'gergelim', 'gnocchi',
        'gorgonzola', 'graos', 'gratinada', 'gratinado', 'grelhado', 'hamburguer', 'integral',
        'iogurte', 'lasanha', 'legumes', 'limao', 'linguica', 'lombo', 'madeira', 'maminha',
        'mandioca', 'mandioquinha', 'manjar', 'maracuja', 'marroquino', 'mel', 'milanesa',
        'molho', 'moqueca', 'mostarda', 'mousse', 'muqueca', 'nhoque', 'nozes', 'ovo', 'ovos',
        'palmito', 'pancetta', 'pao', 'paprica', 'parmegiana', 'parmesao', 'pastel', 'pato',
        'peixe', 'pera', 'pernil', 'peru', 'pescadores', 'picles', 'pimentao', 'poro',
        'portobello', 'preto', 'proteina', 'pure', 'queijo', 'quiche', 'quinoa', 'radicchio',
        'repolho', 'requeijao', 'risoto', 'rolinho', 'romeu', 'roxa', 'rucula', 'salada',
        'salmao', 'salpicao', 'seca', 'sete', 'siciliano', 'sobrecoxa', 'soja', 'strogonoff',
        'sugo', 'tahine', 'tandoori', 'tartaro', 'terra', 'tilapia', 'tiramisu', 'tomate',
        'torta', 'tortilha', 'tropeiro', 'umami', 'vegana', 'vegano', 'verde', 'vermelha',
        'vietnamita', 'vol', 'vent', 'au', 'quatro', 'sana', 'cibi', 'assada', 'assado',
        'carioca', 'fradinho', 'branco', 'negro', 'frescas', 'secos', 'ervas', 'especiarias',
        'indiana', 'mediterranea', 'peruana', 'peruano', 'tunísia', 'cordeiro', 'chef',
        'tres', 'alhos', 'manteiga', 'confit', 'laranja', 'caramelizada', 'granola', 'julieta'
    ]
    
    # Tentar separar palavras conhecidas
    result = name.lower()
    
    # Se já tem espaços, apenas capitalizar
    if ' ' in result:
        words = result.split()
        capitalized = []
        for i, word in enumerate(words):
            if i == 0 or word not in lowercase_words:
                capitalized.append(word.capitalize())
            else:
                capitalized.append(word)
        return ' '.join(capitalized)
    
    # Tentar separar palavras coladas
    words_found = []
    remaining = result
    
    while remaining:
        found = False
        # Tentar encontrar a maior palavra conhecida no início
        for length in range(min(len(remaining), 15), 1, -1):
            candidate = remaining[:length]
            if candidate in known_words:
                words_found.append(candidate)
                remaining = remaining[length:]
                found = True
                break
        
        if not found:
            # Se não encontrou palavra conhecida, pega o primeiro caractere
            words_found.append(remaining[0])
            remaining = remaining[1:]
    
    # Juntar caracteres soltos com a palavra anterior
    merged = []
    for word in words_found:
        if len(word) == 1 and merged:
            merged[-1] += word
        else:
            merged.append(word)
    
    # Capitalizar
    capitalized = []
    for i, word in enumerate(merged):
        if i == 0 or word not in lowercase_words:
            capitalized.append(word.capitalize())
        else:
            capitalized.append(word)
    
    return ' '.join(capitalized)

def main():
    print("=" * 60)
    print("RENOMEANDO PASTAS PARA PADRÃO COM ESPAÇOS")
    print("=" * 60)
    
    renamed = 0
    errors = []
    
    folders = sorted(os.listdir(DATASET_DIR))
    
    for folder in folders:
        old_path = os.path.join(DATASET_DIR, folder)
        if not os.path.isdir(old_path):
            continue
        
        new_name = to_title_case(folder)
        new_path = os.path.join(DATASET_DIR, new_name)
        
        if old_path != new_path:
            try:
                # Se já existe pasta com novo nome, mesclar
                if os.path.exists(new_path):
                    # Mover arquivos
                    for f in os.listdir(old_path):
                        src = os.path.join(old_path, f)
                        dst = os.path.join(new_path, f)
                        if os.path.isfile(src) and not os.path.exists(dst):
                            os.rename(src, dst)
                    os.rmdir(old_path)
                else:
                    os.rename(old_path, new_path)
                
                print(f"  {folder} -> {new_name}")
                renamed += 1
            except Exception as e:
                errors.append(f"{folder}: {e}")
    
    print(f"\n✅ Renomeadas: {renamed} pastas")
    if errors:
        print(f"❌ Erros: {len(errors)}")
        for e in errors[:5]:
            print(f"  - {e}")

if __name__ == "__main__":
    main()
