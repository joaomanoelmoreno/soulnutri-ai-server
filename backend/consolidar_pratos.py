#!/usr/bin/env python3
"""
Script para consolidar pastas de pratos duplicados
"""
import os
import shutil
from pathlib import Path

DATASET_DIR = "/app/datasets/organized"

def consolidar(origem, destino):
    """Move fotos da origem para destino e remove pasta origem"""
    origem_path = os.path.join(DATASET_DIR, origem)
    destino_path = os.path.join(DATASET_DIR, destino)
    
    if not os.path.exists(origem_path):
        return f"  [SKIP] {origem} não existe"
    
    # Se destino não existe, apenas renomear
    if not os.path.exists(destino_path):
        os.rename(origem_path, destino_path)
        return f"  ✓ Renomeada: {origem} -> {destino}"
    
    # Se destino existe, mover arquivos
    moved = 0
    for f in os.listdir(origem_path):
        src = os.path.join(origem_path, f)
        dst = os.path.join(destino_path, f)
        if os.path.isfile(src):
            if not os.path.exists(dst):
                shutil.move(src, dst)
                moved += 1
    
    # Remover pasta origem
    shutil.rmtree(origem_path, ignore_errors=True)
    return f"  ✓ Consolidada: {origem} -> {destino} ({moved} arquivos)"

def deletar(pasta):
    """Remove pasta completamente"""
    path = os.path.join(DATASET_DIR, pasta)
    if os.path.exists(path):
        shutil.rmtree(path)
        return f"  ✓ Deletada: {pasta}"
    return f"  [SKIP] {pasta} não existe"

# Lista de consolidações baseada no documento do usuário
consolidacoes = [
    # (origem, destino)
    ("abóbora_assada", "aboboraaocurry"),
    ("abobrinha_caramelizada_vegana", "abobrinha_grelhada"),
    ("aligot_purê_de_batata_inglesa_com_queijo", "aligot"),
    ("almôndegas_com_especiarias_indiana", "almondegas_com_especiarias_indiana"),
    ("arroz_7_grãos_com_legumes", "arroz7graoscomlegumes"),
    ("arroz_de_7_graos", "arroz7graos"),
    ("atum_ao_gergelim", "atumaogergelim"),
    ("bacalhau_com_natas_e_champions", "bacalhaucomnatas"),
    ("bacalhau_com_natsa", "bacalhaucomnatas"),
    ("bacalhau_gomes_de_sá", "bacalhaugomesdesa"),
    ("baião_de_dois", "baiaodedois"),
    ("batata_com_paprika", "batatacompaprica"),
    ("beringela_a_parmegiana", "beringelaaoparmegiana"),
    ("beringela_ao_purê_de_limão_siciliano", "beringelaaolimao"),
    ("beringela_ao_purê_de_limão_siciliano_picles_de_dedo_de_moça", "beringelaaolimao"),
    ("beterraba", "beterrabaaobalsamico"),
    ("beterraba_com_laranja", "beterrabaaobalsamico"),
    ("bolinho_de_bacalhau", "bolinhodebacalhau"),
    ("bolinho_de_camarao", "bolinhodebacalhau"),
    ("bolinho_de_camarão_peixe", "bolinhodebacalhau"),
    ("bolo_de_gengibre", "bolodegengibre"),
    ("bolo_vegano_de_chocolate", "bolochocolatevegano"),
    ("caneleira_quatro_queijos", "canelone4queijos"),
    ("caneloni_de_espinafre", "canelonedeespinafre"),
    ("carne_seca_com_abóbora", "carne_seca_com_abobora"),
    ("carpaccio_de_abobrinha_com_queijo_vegano", "carpacciodeabobrinhacomqueijovegano"),
    ("cenoura_com_iogurte_e_especiarias", "cenouraaoiogurte"),
    ("cestinha_de_camarao", "cestinhasdecamarao"),
    ("cestinha_de_camarão", "cestinhasdecamarao"),
    ("ceviche_cibi_sana", "cevicheperuano"),
    ("ceviche_cibi_sana_filé_de_tilápia", "cevicheperuano"),
    ("cogumelo_recheado_com_legumes_e_queijo_vegano", "cogumelo_recheado_de_com_legumes"),
    ("conchiglione_ao_creme_com_sálvia_e_avelã", "conchiglione_recheados"),
    ("costela__cibi_sana", "costelinhacibisana"),
    ("costela_assada_com_mandioca", "costela_com_mandioca"),
    ("costela_com_mandioca", "costelacommandioca"),
    ("costelinha_cibi_sana", "costelinhacibisana"),
    ("couve_flor_gratinada", "couveflorgratinada"),
    ("couveflor_gratinada", "couveflorgratinada"),
    ("coxinha_saudável_de_frango", "coxinhasaudaveldefrango"),
    ("cuscuz_marroquino_com_amêndoas", "cuscuzmarroquino"),
    ("entrecôte", "entrecote"),
    ("estrogonofe_de_frango", "strogonoffdefrango"),
    ("estrogonofe_vegano", "strogonoffvegano"),
    ("farofa_de_banana_da_terra_vegana", "farofadebananadaterravegana"),
    ("farofa_de_banana_vegana", "farofadebananadaterravegana"),
    ("feijão_do_chef", "feijao_do_chef"),
    ("feijão_sem_carne", "feijaosemcarne"),
    ("feijão_tropeiro", "feijaotropeiro"),
    ("file_de__peixe_em_manteiga_de_tomates", "filedepeixeemmanteigatomates"),
    ("file_de_peixe_em_manteiga_de_tomates", "filedepeixeemmanteigatomates"),
    ("filé_de_frango_parmegiana", "filedefrangoaparmegiana"),
    ("filé_de_peixe_ao_confir_de_tomates", "filedepeixeaoconfitdetomates"),
    ("filé_de_peixe_ao_molho_confit", "filedepeixeaoconfitdetomates"),
    ("filé_de_tilápia_a_milanesa", "file_de_tilapia_a_milanesa"),
    ("frango_assado", "frango_no_tacho"),
    ("frutas_ao_ganache_de_chocolate", "frutasaoganache"),
    ("fígado_acebolad9", "figadoacebolado"),
    ("fígado_acebolado", "figadoacebolado"),
    ("ganache_de_chocolate_com_frutas", "frutasaoganache"),
    ("grelahdo_dos_pescaodres", "grelhado_dos_pescadores"),
    ("grelhado_dos_pescadores", "grelhadodospescadores"),
    ("hambúrguer_bovino", "hamburgerdecarne"),
    ("hambúrguer_vegano_de_nozes", "hamburguer_vegano_de_nozes"),
    ("lasanha_vegana_beringela_e_proteína_de_soja", "lasanhaveganadeberinjela"),
    ("lasanha_vegana_de_berinjela_e_proteína_de_soja", "lasanhaveganadeberinjela"),
    ("linguiça_de_lombo", "linguica_de_lombo"),
    ("maminha_ao_molho_de_cebola", "maminhaaocebolado"),
    ("maminha_ao_molho_madeira", "maminhamolhomadeira"),
    ("maminha_ao_molho_mostarda", "maminhaaomolhomostarda"),
    ("mamão", "mamao"),
    ("manjar_de_coco_com_calda_de_frutas_vermelhas", "manjardecococomcaldadeameixa"),
    ("marinha_ao_molho_madeira", "maminhamolhomadeira"),
    ("mechouia_tunísia", "saladamichouiatunísia"),
    ("melhoria_tunísia", "saladamichouiatunísia"),
    ("molho_tártaro", "molho_tartaro"),
    ("mousse_de_maracujá", "moussedemaracuja"),
    ("muqueca_de_banana_da_terra", "muquecadebananadaterra"),
    ("muqueca_de_banana_da_terra_vegana", "muquecadebananadaterra"),
    ("nhoque", "gnocchi"),
    ("nhoque_de_banana_da_terra_vegana", "nhoquedebananadaterravegana"),
    ("panceta_pururca", "pancettacrocante"),
    ("panceta_pururuca", "pancettacrocante"),
    ("peixe_ao_confit_de_tomates", "filedepeixeaoconfitdetomates"),
    ("peixe_ao_molho_de_três_alhos_manteiga_e_tomate", "peixe_ao_molho_de_tres_alhos_manteiga_e_tomate"),
    ("purê_de_batata_doce", "puredebatatadoce"),
    ("purê_de_madioquinha_vegano_com_leite_de_coco", "puredemandioquinha"),
    ("pão_de_alho_negro_e_cumaru", "pao_de_alho_negro_e_cumaru"),
    ("queijo_parmesão_ralado", "queijo_parmesao_ralado"),
    ("quiche_de_escarola_com_azeitonas_pretas", "quichedeescarola"),
    ("quiche_de_escarola_e_azeitona_preta", "quichedeescarola"),
    ("quiche_de_escarola_e_azeitonas_pretas", "quichedeescarola"),
    ("radicchio_ao_molho_de_mel_e_lamina_de_amendoas", "radicchioaomolhodemel"),
    ("radicchio_ao_molho_de_mel_e_lâmina_de_amêndoas", "radicchioaomolhodemel"),
    ("requeijão", "requeijao"),
    ("risoto_de_alho_poró", "risoto_de_alho_poro"),
    ("risoto_de_pêra_e_gorgonzola", "risoto_de_pera_e_gorgonzola"),
    ("rolinho_vietnamita_de_camarão", "rolinho_vietnamita_de_camarao"),
    ("salada_mediterrânea", "saladamediterranea"),
    ("salada_michouia_tunísia", "saladamichouiatunísia"),
    ("sobrecoxa_ao_tandoori", "sobrecoxaaotandoori"),
    ("sobrecoxa_ao_tandori", "sobrecoxaaotandoori"),
    ("umame_de_tomate", "umamidetomate"),
    ("umami_de_tomate", "umamidetomate"),
    ("umami_de_tomates", "umamidetomate"),
    ("vol_au_vent_de_pimentão", "volauventdepimentao"),
    ("vol_aí_vent_de_pimentão", "volauventdepimentao"),
]

# Pastas para deletar
deletar_lista = [
    "capuccino",
    "capuccino_com_chocolate",
    "file_de_peixe_rm_manteiga_de_tomates",
    "filé_a_parmegiana__acompanhamentos",
    "alface_frisée",  # duplicada de alface_frisee
]

print("=" * 60)
print("CONSOLIDAÇÃO DE PRATOS - SoulNutri")
print("=" * 60)

# Executar consolidações
print("\n📁 Consolidando pastas duplicadas...")
for origem, destino in consolidacoes:
    result = consolidar(origem, destino)
    if "[SKIP]" not in result:
        print(result)

# Deletar pastas
print("\n🗑️ Deletando pastas desnecessárias...")
for pasta in deletar_lista:
    result = deletar(pasta)
    if "[SKIP]" not in result:
        print(result)

# Contar resultado final
print("\n" + "=" * 60)
total_pastas = len([d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))])
vazias = 0
for d in os.listdir(DATASET_DIR):
    path = os.path.join(DATASET_DIR, d)
    if os.path.isdir(path):
        imgs = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        if len(imgs) == 0:
            vazias += 1

print(f"✅ Total de pastas agora: {total_pastas}")
print(f"📸 Pastas sem fotos: {vazias}")
print("=" * 60)
