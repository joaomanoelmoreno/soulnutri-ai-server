# -*- coding: utf-8 -*-
"""
TABELA BRASILEIRA DE COMPOSIÇÃO DE ALIMENTOS (TACO)
Fonte: NEPA/UNICAMP - 4ª Edição Revisada e Ampliada
Total: 597 alimentos com dados nutricionais completos

Valores por 100g do alimento.
ZERO CRÉDITOS DE IA - 100% LOCAL
"""

TACO_DATABASE = {
    # ═══════════════════════════════════════════════════════════════
    # ALIMENTOS PREPARADOS
    # ═══════════════════════════════════════════════════════════════
    "acaraje": {"nome": "Acarajé", "calorias": 289.0, "proteinas": 8.3, "carboidratos": 19.1, "gorduras": 19.9, "fibras": 9.4, "sodio": 305.0, "calcio": 124.0, "ferro": 1.9, "potassio": 354.0, "zinco": 1.2, "colesterol": 25.0, "vitamina_c": 0},
    "arroz_carreteiro": {"nome": "Arroz carreteiro", "calorias": 154.0, "proteinas": 10.8, "carboidratos": 11.6, "gorduras": 7.1, "fibras": 1.5, "sodio": 1622.0, "calcio": 13.0, "ferro": 1.0, "potassio": 87.0, "zinco": 2.7, "colesterol": 36.0, "vitamina_c": 0},
    "baiao_de_dois_arroz_e_feijao_de_corda": {"nome": "Baião de dois, arroz e feijão-de-corda", "calorias": 136.0, "proteinas": 6.2, "carboidratos": 20.4, "gorduras": 3.2, "fibras": 5.1, "sodio": 93.0, "calcio": 33.0, "ferro": 0.6, "potassio": 157.0, "zinco": 0.6, "colesterol": 4.0, "vitamina_c": 0},
    "barreado": {"nome": "Barreado", "calorias": 165.0, "proteinas": 18.3, "carboidratos": 0.2, "gorduras": 9.5, "fibras": 0.1, "sodio": 48.0, "calcio": 15.0, "ferro": 2.4, "potassio": 295.0, "zinco": 4.8, "colesterol": 60.0, "vitamina_c": 0},
    "bife_a_cavalo_com_contra_file": {"nome": "Bife à cavalo, com contra filé", "calorias": 291.0, "proteinas": 23.7, "carboidratos": 0.0, "gorduras": 21.1, "fibras": 0, "sodio": 83.0, "calcio": 26.0, "ferro": 2.1, "potassio": 272.0, "zinco": 3.2, "colesterol": 257.0, "vitamina_c": 0},
    "bolinho_de_arroz": {"nome": "Bolinho de arroz", "calorias": 274.0, "proteinas": 8.0, "carboidratos": 41.7, "gorduras": 8.3, "fibras": 2.7, "sodio": 59.0, "calcio": 24.0, "ferro": 2.1, "potassio": 96.0, "zinco": 0.9, "colesterol": 70.0, "vitamina_c": 0},
    "camarao_a_baiana": {"nome": "Camarão à baiana", "calorias": 101.0, "proteinas": 7.9, "carboidratos": 3.2, "gorduras": 6.0, "fibras": 0.4, "sodio": 85.0, "calcio": 43.0, "ferro": 1.4, "potassio": 139.0, "zinco": 0.5, "colesterol": 117.0, "vitamina_c": 4.1},
    "charuto_de_repolho": {"nome": "Charuto, de repolho", "calorias": 78.0, "proteinas": 6.8, "carboidratos": 10.1, "gorduras": 1.1, "fibras": 1.5, "sodio": 12.0, "calcio": 23.0, "ferro": 0.9, "potassio": 184.0, "zinco": 1.8, "colesterol": 21.0, "vitamina_c": 4.8},
    "cuscuz_de_milho_cozido_com_sal": {"nome": "Cuscuz, de milho, cozido com sal", "calorias": 113.0, "proteinas": 2.2, "carboidratos": 25.3, "gorduras": 0.7, "fibras": 2.1, "sodio": 248.0, "calcio": 2.0, "ferro": 0.2, "potassio": 11.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 0},
    "cuscuz_paulista": {"nome": "Cuscuz, paulista", "calorias": 142.0, "proteinas": 2.6, "carboidratos": 22.5, "gorduras": 4.6, "fibras": 2.4, "sodio": 236.0, "calcio": 14.0, "ferro": 0.3, "potassio": 53.0, "zinco": 0.2, "colesterol": 15.0, "vitamina_c": 0},
    "cuxa_molho": {"nome": "Cuxá, molho", "calorias": 80.0, "proteinas": 5.6, "carboidratos": 5.7, "gorduras": 3.6, "fibras": 3.0, "sodio": 1344.0, "calcio": 105.0, "ferro": 0.9, "potassio": 124.0, "zinco": 0.6, "colesterol": 58.0, "vitamina_c": 10.3},
    "dobradinha": {"nome": "Dobradinha", "calorias": 125.0, "proteinas": 19.8, "carboidratos": 0.0, "gorduras": 4.4, "fibras": 0, "sodio": 29.0, "calcio": 11.0, "ferro": 1.0, "potassio": 58.0, "zinco": 2.7, "colesterol": 144.0, "vitamina_c": 0},
    "estrogonofe_de_carne": {"nome": "Estrogonofe de carne", "calorias": 173.0, "proteinas": 15.0, "carboidratos": 3.0, "gorduras": 10.8, "fibras": 0, "sodio": 123.0, "calcio": 28.0, "ferro": 2.7, "potassio": 322.0, "zinco": 2.0, "colesterol": 66.0, "vitamina_c": 0},
    "estrogonofe_de_frango": {"nome": "Estrogonofe de frango", "calorias": 157.0, "proteinas": 17.6, "carboidratos": 2.6, "gorduras": 8.0, "fibras": 0, "sodio": 99.0, "calcio": 26.0, "ferro": 1.5, "potassio": 307.0, "zinco": 0.6, "colesterol": 80.0, "vitamina_c": 0},
    "feijao_tropeiro_mineiro": {"nome": "Feijão tropeiro mineiro", "calorias": 152.0, "proteinas": 10.2, "carboidratos": 19.6, "gorduras": 6.8, "fibras": 3.6, "sodio": 365.0, "calcio": 41.0, "ferro": 2.2, "potassio": 349.0, "zinco": 1.4, "colesterol": 68.0, "vitamina_c": 0},
    "feijoada": {"nome": "Feijoada", "calorias": 117.0, "proteinas": 8.7, "carboidratos": 11.6, "gorduras": 6.5, "fibras": 5.1, "sodio": 278.0, "calcio": 32.0, "ferro": 1.3, "potassio": 303.0, "zinco": 0.8, "colesterol": 22.0, "vitamina_c": 0},
    "frango_com_acafrao": {"nome": "Frango, com açafrão", "calorias": 113.0, "proteinas": 9.7, "carboidratos": 4.1, "gorduras": 6.2, "fibras": 0.2, "sodio": 29.0, "calcio": 13.0, "ferro": 0.8, "potassio": 256.0, "zinco": 0.5, "colesterol": 50.0, "vitamina_c": 5.3},
    "macarrao_molho_bolognesa": {"nome": "Macarrão, molho bolognesa", "calorias": 120.0, "proteinas": 4.9, "carboidratos": 22.5, "gorduras": 0.9, "fibras": 0.8, "sodio": 9.0, "calcio": 11.0, "ferro": 1.4, "potassio": 84.0, "zinco": 0.8, "colesterol": 7.0, "vitamina_c": 0},
    "manicoba": {"nome": "Maniçoba", "calorias": 134.0, "proteinas": 10.0, "carboidratos": 3.4, "gorduras": 8.7, "fibras": 2.2, "sodio": 407.0, "calcio": 66.0, "ferro": 3.2, "potassio": 148.0, "zinco": 2.0, "colesterol": 43.0, "vitamina_c": 0},
    "quibebe": {"nome": "Quibebe", "calorias": 86.0, "proteinas": 8.6, "carboidratos": 6.6, "gorduras": 2.7, "fibras": 1.7, "sodio": 247.0, "calcio": 8.0, "ferro": 0.8, "potassio": 153.0, "zinco": 1.6, "colesterol": 0, "vitamina_c": 0},
    "salada_de_legumes_com_maionese": {"nome": "Salada, de legumes, com maionese", "calorias": 96.0, "proteinas": 1.1, "carboidratos": 8.9, "gorduras": 7.0, "fibras": 2.2, "sodio": 228.0, "calcio": 12.0, "ferro": 0.2, "potassio": 141.0, "zinco": 0.2, "colesterol": 7.0, "vitamina_c": 0},
    "salada_de_legumes_cozida_no_vapor": {"nome": "Salada, de legumes, cozida no vapor", "calorias": 35.0, "proteinas": 2.0, "carboidratos": 7.1, "gorduras": 0.3, "fibras": 2.5, "sodio": 3.0, "calcio": 33.0, "ferro": 0.4, "potassio": 244.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 29.4},
    "salpicao_de_frango": {"nome": "Salpicão, de frango", "calorias": 148.0, "proteinas": 13.9, "carboidratos": 4.6, "gorduras": 7.8, "fibras": 0.4, "sodio": 248.0, "calcio": 9.0, "ferro": 0.3, "potassio": 149.0, "zinco": 0.4, "colesterol": 53.0, "vitamina_c": 9.3},
    "sarapatel": {"nome": "Sarapatel", "calorias": 123.0, "proteinas": 18.5, "carboidratos": 1.1, "gorduras": 4.4, "fibras": 0, "sodio": 216.0, "calcio": 12.0, "ferro": 7.2, "potassio": 199.0, "zinco": 1.8, "colesterol": 315.0, "vitamina_c": 0},
    "tabule": {"nome": "Tabule", "calorias": 57.0, "proteinas": 2.0, "carboidratos": 10.6, "gorduras": 1.2, "fibras": 2.1, "sodio": 1.0, "calcio": 19.0, "ferro": 0.6, "potassio": 188.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 16.2},
    "tacaca": {"nome": "Tacacá", "calorias": 47.0, "proteinas": 7.0, "carboidratos": 3.4, "gorduras": 0.4, "fibras": 0.2, "sodio": 1349.0, "calcio": 45.0, "ferro": 0.9, "potassio": 240.0, "zinco": 0.8, "colesterol": 71.0, "vitamina_c": 0},
    "tapioca_com_manteiga": {"nome": "Tapioca, com manteiga", "calorias": 348.0, "proteinas": 0.1, "carboidratos": 63.6, "gorduras": 10.9, "fibras": 0, "sodio": 158.0, "calcio": 30.0, "ferro": 0.2, "potassio": 19.0, "zinco": 0.0, "colesterol": 31.0, "vitamina_c": 0},
    "tucupi_com_pimenta_de_cheiro": {"nome": "Tucupi, com pimenta-de-cheiro", "calorias": 27.0, "proteinas": 2.1, "carboidratos": 4.7, "gorduras": 0.3, "fibras": 0.2, "sodio": 5.0, "calcio": 28.0, "ferro": 1.1, "potassio": 391.0, "zinco": 0.9, "colesterol": 0, "vitamina_c": 46.4},
    "vaca_atolada": {"nome": "Vaca atolada", "calorias": 145.0, "proteinas": 5.1, "carboidratos": 10.1, "gorduras": 9.3, "fibras": 2.3, "sodio": 26.0, "calcio": 63.0, "ferro": 0.7, "potassio": 220.0, "zinco": 1.2, "colesterol": 19.0, "vitamina_c": 0},
    "vatapa": {"nome": "Vatapá", "calorias": 255.0, "proteinas": 6.0, "carboidratos": 9.7, "gorduras": 23.2, "fibras": 1.7, "sodio": 880.0, "calcio": 47.0, "ferro": 1.4, "potassio": 209.0, "zinco": 0.9, "colesterol": 44.0, "vitamina_c": 0},
    "virado_a_paulista": {"nome": "Virado à paulista", "calorias": 307.0, "proteinas": 10.2, "carboidratos": 14.1, "gorduras": 25.6, "fibras": 2.2, "sodio": 346.0, "calcio": 41.0, "ferro": 1.1, "potassio": 237.0, "zinco": 1.0, "colesterol": 66.0, "vitamina_c": 0},
    "yakisoba": {"nome": "Yakisoba", "calorias": 113.0, "proteinas": 7.5, "carboidratos": 18.3, "gorduras": 2.6, "fibras": 1.1, "sodio": 794.0, "calcio": 14.0, "ferro": 0.6, "potassio": 159.0, "zinco": 0.7, "colesterol": 0, "vitamina_c": 0},

    # ═══════════════════════════════════════════════════════════════
    # BEBIDAS (ALCOÓLICAS E NÃO ALCOÓLICAS)
    # ═══════════════════════════════════════════════════════════════
    "bebida_isotonica_sabores_variados": {"nome": "Bebida isotônica, sabores variados", "calorias": 26.0, "proteinas": 0.0, "carboidratos": 6.4, "gorduras": 0.0, "fibras": 0, "sodio": 44.0, "calcio": 1.0, "ferro": 0.7, "potassio": 13.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "cafe_infusao_10": {"nome": "Café, infusão 10%", "calorias": 9.0, "proteinas": 0.7, "carboidratos": 1.5, "gorduras": 0.1, "fibras": 0, "sodio": 1.0, "calcio": 3.0, "ferro": 0, "potassio": 156.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "cana_aguardente_1": {"nome": "Cana, aguardente 1", "calorias": 216.0, "proteinas": 0, "carboidratos": 0, "gorduras": 0, "fibras": 0, "sodio": 3.0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "cana_caldo_de": {"nome": "Cana, caldo de", "calorias": 65.0, "proteinas": 0, "carboidratos": 18.2, "gorduras": 0, "fibras": 0.1, "sodio": 0, "calcio": 9.0, "ferro": 0.8, "potassio": 18.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 2.8},
    "cerveja_pilsen_2": {"nome": "Cerveja, pilsen 2", "calorias": 41.0, "proteinas": 0.6, "carboidratos": 3.3, "gorduras": 0, "fibras": 0, "sodio": 4.0, "calcio": 5.0, "ferro": 0, "potassio": 29.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "cha_erva_doce_infusao_5": {"nome": "Chá, erva-doce, infusão 5%", "calorias": 1.0, "proteinas": 0.0, "carboidratos": 0.4, "gorduras": 0.0, "fibras": 0, "sodio": 1.0, "calcio": 2.0, "ferro": 0, "potassio": 10.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "cha_mate_infusao_5": {"nome": "Chá, mate, infusão 5%", "calorias": 3.0, "proteinas": 0.0, "carboidratos": 0.6, "gorduras": 0.1, "fibras": 0, "sodio": 0, "calcio": 1.0, "ferro": 0, "potassio": 5.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "cha_preto_infusao_5": {"nome": "Chá, preto, infusão 5%", "calorias": 2.0, "proteinas": 0.0, "carboidratos": 0.6, "gorduras": 0.0, "fibras": 0, "sodio": 0, "calcio": 0.0, "ferro": 0, "potassio": 13.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "coco_agua_de": {"nome": "Coco, água de", "calorias": 22.0, "proteinas": 0.0, "carboidratos": 5.3, "gorduras": 0.0, "fibras": 0.1, "sodio": 2.0, "calcio": 19.0, "ferro": 0, "potassio": 162.0, "zinco": 0, "colesterol": 0, "vitamina_c": 2.4},
    "refrigerante_tipo_agua_tonica": {"nome": "Refrigerante, tipo água tônica", "calorias": 31.0, "proteinas": 0.0, "carboidratos": 8.0, "gorduras": 0.0, "fibras": 0, "sodio": 8.0, "calcio": 1.0, "ferro": 0, "potassio": 2.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "refrigerante_tipo_cola": {"nome": "Refrigerante, tipo cola", "calorias": 34.0, "proteinas": 0.0, "carboidratos": 8.7, "gorduras": 0.0, "fibras": 0, "sodio": 7.0, "calcio": 1.0, "ferro": 0, "potassio": 1.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "refrigerante_tipo_guarana": {"nome": "Refrigerante, tipo guaraná", "calorias": 39.0, "proteinas": 0.0, "carboidratos": 10.0, "gorduras": 0.0, "fibras": 0, "sodio": 9.0, "calcio": 1.0, "ferro": 0, "potassio": 1.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "refrigerante_tipo_laranja": {"nome": "Refrigerante, tipo laranja", "calorias": 46.0, "proteinas": 0.0, "carboidratos": 11.8, "gorduras": 0.0, "fibras": 0, "sodio": 9.0, "calcio": 2.0, "ferro": 0, "potassio": 16.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "refrigerante_tipo_limao": {"nome": "Refrigerante, tipo limão", "calorias": 40.0, "proteinas": 0.0, "carboidratos": 10.3, "gorduras": 0.0, "fibras": 0, "sodio": 9.0, "calcio": 2.0, "ferro": 0, "potassio": 4.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},

    # ═══════════════════════════════════════════════════════════════
    # CARNES E DERIVADOS
    # ═══════════════════════════════════════════════════════════════
    "apresuntado": {"nome": "Apresuntado", "calorias": 129.0, "proteinas": 13.5, "carboidratos": 2.9, "gorduras": 6.7, "fibras": 0, "sodio": 943.0, "calcio": 23.0, "ferro": 0.9, "potassio": 270.0, "zinco": 1.6, "colesterol": 38.0, "vitamina_c": 0},
    "caldo_de_carne_tablete": {"nome": "Caldo de carne, tablete", "calorias": 241.0, "proteinas": 7.8, "carboidratos": 15.1, "gorduras": 16.6, "fibras": 0.6, "sodio": 22180.0, "calcio": 129.0, "ferro": 0, "potassio": 218.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "caldo_de_galinha_tablete": {"nome": "Caldo de galinha, tablete", "calorias": 251.0, "proteinas": 6.3, "carboidratos": 10.6, "gorduras": 20.4, "fibras": 11.8, "sodio": 22300.0, "calcio": 16.0, "ferro": 0.7, "potassio": 68.0, "zinco": 0.3, "colesterol": 2.0, "vitamina_c": 0},
    "carne_bovina_acem_moido_cozido": {"nome": "Carne, bovina, acém, moído, cozido", "calorias": 212.0, "proteinas": 26.7, "carboidratos": 0.0, "gorduras": 10.9, "fibras": 0, "sodio": 52.0, "calcio": 4.0, "ferro": 2.7, "potassio": 256.0, "zinco": 8.1, "colesterol": 103.0, "vitamina_c": 0},
    "carne_bovina_acem_moido_cru": {"nome": "Carne, bovina, acém, moído, cru", "calorias": 137.0, "proteinas": 19.4, "carboidratos": 0.0, "gorduras": 5.9, "fibras": 0, "sodio": 49.0, "calcio": 3.0, "ferro": 1.8, "potassio": 237.0, "zinco": 6.3, "colesterol": 58.0, "vitamina_c": 0},
    "carne_bovina_acem_sem_gordura_cozido": {"nome": "Carne, bovina, acém, sem gordura, cozido", "calorias": 215.0, "proteinas": 27.3, "carboidratos": 0.0, "gorduras": 10.9, "fibras": 0, "sodio": 56.0, "calcio": 7.0, "ferro": 2.4, "potassio": 254.0, "zinco": 8.0, "colesterol": 107.0, "vitamina_c": 0},
    "carne_bovina_acem_sem_gordura_cru": {"nome": "Carne, bovina, acém, sem gordura, cru", "calorias": 144.0, "proteinas": 20.8, "carboidratos": 0.0, "gorduras": 6.1, "fibras": 0, "sodio": 50.0, "calcio": 5.0, "ferro": 1.5, "potassio": 234.0, "zinco": 5.2, "colesterol": 53.0, "vitamina_c": 0},
    "carne_bovina_almondegas_cruas": {"nome": "Carne, bovina, almôndegas, cruas", "calorias": 189.0, "proteinas": 12.3, "carboidratos": 9.8, "gorduras": 11.2, "fibras": 0, "sodio": 621.0, "calcio": 22.0, "ferro": 1.6, "potassio": 328.0, "zinco": 2.3, "colesterol": 34.0, "vitamina_c": 0},
    "carne_bovina_almondegas_fritas": {"nome": "Carne, bovina, almôndegas, fritas", "calorias": 272.0, "proteinas": 18.2, "carboidratos": 14.3, "gorduras": 15.8, "fibras": 0, "sodio": 1030.0, "calcio": 27.0, "ferro": 1.9, "potassio": 536.0, "zinco": 2.6, "colesterol": 36.0, "vitamina_c": 0},
    "carne_bovina_bucho_cozido": {"nome": "Carne, bovina, bucho, cozido", "calorias": 133.0, "proteinas": 21.6, "carboidratos": 0.0, "gorduras": 4.5, "fibras": 0, "sodio": 38.0, "calcio": 13.0, "ferro": 0.6, "potassio": 70.0, "zinco": 2.5, "colesterol": 245.0, "vitamina_c": 0},
    "carne_bovina_bucho_cru": {"nome": "Carne, bovina, bucho, cru", "calorias": 137.0, "proteinas": 20.5, "carboidratos": 0.0, "gorduras": 5.5, "fibras": 0, "sodio": 45.0, "calcio": 9.0, "ferro": 0.5, "potassio": 85.0, "zinco": 2.1, "colesterol": 145.0, "vitamina_c": 0},
    "carne_bovina_capa_de_contra_file_com_gordura_crua": {"nome": "Carne, bovina, capa de contra-filé, com gordura, crua", "calorias": 217.0, "proteinas": 19.2, "carboidratos": 0.0, "gorduras": 15.0, "fibras": 0, "sodio": 58.0, "calcio": 6.0, "ferro": 1.5, "potassio": 267.0, "zinco": 3.5, "colesterol": 63.0, "vitamina_c": 0},
    "carne_bovina_capa_de_contra_file_com_gordura_grelhada": {"nome": "Carne, bovina, capa de contra-filé, com gordura, grelhada", "calorias": 312.0, "proteinas": 30.7, "carboidratos": 0.0, "gorduras": 20.0, "fibras": 0, "sodio": 81.0, "calcio": 7.0, "ferro": 2.6, "potassio": 323.0, "zinco": 6.2, "colesterol": 120.0, "vitamina_c": 0},
    "carne_bovina_capa_de_contra_file_sem_gordura_crua": {"nome": "Carne, bovina, capa de contra-filé, sem gordura, crua", "calorias": 131.0, "proteinas": 21.5, "carboidratos": 0.0, "gorduras": 4.3, "fibras": 0, "sodio": 79.0, "calcio": 6.0, "ferro": 2.0, "potassio": 325.0, "zinco": 4.6, "colesterol": 58.0, "vitamina_c": 0},
    "carne_bovina_capa_de_contra_file_sem_gordura_grelhada": {"nome": "Carne, bovina, capa de contra-filé, sem gordura, grelhada", "calorias": 239.0, "proteinas": 35.1, "carboidratos": 0.0, "gorduras": 10.0, "fibras": 0, "sodio": 83.0, "calcio": 9.0, "ferro": 2.8, "potassio": 385.0, "zinco": 7.6, "colesterol": 80.0, "vitamina_c": 0},
    "carne_bovina_charque_cozido": {"nome": "Carne, bovina, charque, cozido", "calorias": 263.0, "proteinas": 36.4, "carboidratos": 0.0, "gorduras": 11.9, "fibras": 0, "sodio": 1443.0, "calcio": 15.0, "ferro": 3.5, "potassio": 90.0, "zinco": 6.1, "colesterol": 113.0, "vitamina_c": 0},
    "carne_bovina_charque_cru": {"nome": "Carne, bovina, charque, cru", "calorias": 249.0, "proteinas": 22.7, "carboidratos": 0.0, "gorduras": 16.8, "fibras": 0, "sodio": 5875.0, "calcio": 15.0, "ferro": 1.5, "potassio": 236.0, "zinco": 3.9, "colesterol": 81.0, "vitamina_c": 0},
    "carne_bovina_contra_file_a_milanesa": {"nome": "Carne, bovina, contra-filé, à milanesa", "calorias": 352.0, "proteinas": 20.6, "carboidratos": 12.2, "gorduras": 24.0, "fibras": 0.4, "sodio": 77.0, "calcio": 15.0, "ferro": 2.9, "potassio": 271.0, "zinco": 2.9, "colesterol": 99.0, "vitamina_c": 0},
    "carne_bovina_contra_file_com_gordura_cru": {"nome": "Carne, bovina, contra-filé, com gordura, cru", "calorias": 206.0, "proteinas": 21.2, "carboidratos": 0.0, "gorduras": 12.8, "fibras": 0, "sodio": 44.0, "calcio": 4.0, "ferro": 1.3, "potassio": 285.0, "zinco": 2.8, "colesterol": 73.0, "vitamina_c": 0},
    "carne_bovina_contra_file_com_gordura_grelhado": {"nome": "Carne, bovina, contra-filé, com gordura, grelhado", "calorias": 278.0, "proteinas": 32.4, "carboidratos": 0.0, "gorduras": 15.5, "fibras": 0, "sodio": 57.0, "calcio": 4.0, "ferro": 2.4, "potassio": 352.0, "zinco": 4.8, "colesterol": 144.0, "vitamina_c": 0},
    "carne_bovina_contra_file_de_costela_cru": {"nome": "Carne, bovina, contra-filé de costela, cru", "calorias": 202.0, "proteinas": 19.8, "carboidratos": 0.0, "gorduras": 13.1, "fibras": 0, "sodio": 39.0, "calcio": 3.0, "ferro": 1.6, "potassio": 245.0, "zinco": 4.4, "colesterol": 52.0, "vitamina_c": 0},
    "carne_bovina_contra_file_de_costela_grelhado": {"nome": "Carne, bovina, contra-filé de costela, grelhado", "calorias": 275.0, "proteinas": 29.9, "carboidratos": 0.0, "gorduras": 16.3, "fibras": 0, "sodio": 51.0, "calcio": 4.0, "ferro": 2.8, "potassio": 383.0, "zinco": 6.7, "colesterol": 98.0, "vitamina_c": 0},
    "carne_bovina_contra_file_sem_gordura_cru": {"nome": "Carne, bovina, contra-filé, sem gordura, cru", "calorias": 157.0, "proteinas": 24.0, "carboidratos": 0.0, "gorduras": 6.0, "fibras": 0, "sodio": 53.0, "calcio": 4.0, "ferro": 1.7, "potassio": 335.0, "zinco": 3.2, "colesterol": 59.0, "vitamina_c": 0},
    "carne_bovina_contra_file_sem_gordura_grelhado": {"nome": "Carne, bovina, contra-filé, sem gordura, grelhado", "calorias": 194.0, "proteinas": 35.9, "carboidratos": 0.0, "gorduras": 4.5, "fibras": 0, "sodio": 58.0, "calcio": 5.0, "ferro": 2.4, "potassio": 386.0, "zinco": 5.1, "colesterol": 102.0, "vitamina_c": 0},
    "carne_bovina_costela_assada": {"nome": "Carne, bovina, costela, assada", "calorias": 373.0, "proteinas": 28.8, "carboidratos": 0.0, "gorduras": 27.7, "fibras": 0, "sodio": 92.0, "calcio": 28.0, "ferro": 2.2, "potassio": 270.0, "zinco": 5.5, "colesterol": 95.0, "vitamina_c": 0},
    "carne_bovina_costela_crua": {"nome": "Carne, bovina, costela, crua", "calorias": 358.0, "proteinas": 16.7, "carboidratos": 0.0, "gorduras": 31.8, "fibras": 0, "sodio": 70.0, "calcio": 0, "ferro": 1.2, "potassio": 151.0, "zinco": 2.7, "colesterol": 44.0, "vitamina_c": 0},
    "carne_bovina_coxao_duro_sem_gordura_cozido": {"nome": "Carne, bovina, coxão duro, sem gordura, cozido", "calorias": 217.0, "proteinas": 31.9, "carboidratos": 0.0, "gorduras": 8.9, "fibras": 0, "sodio": 41.0, "calcio": 4.0, "ferro": 1.7, "potassio": 252.0, "zinco": 5.0, "colesterol": 71.0, "vitamina_c": 0},
    "carne_bovina_coxao_duro_sem_gordura_cru": {"nome": "Carne, bovina, coxão duro, sem gordura, cru", "calorias": 148.0, "proteinas": 21.5, "carboidratos": 0.0, "gorduras": 6.2, "fibras": 0, "sodio": 49.0, "calcio": 3.0, "ferro": 1.9, "potassio": 358.0, "zinco": 2.8, "colesterol": 60.0, "vitamina_c": 0},
    "carne_bovina_coxao_mole_sem_gordura_cozido": {"nome": "Carne, bovina, coxão mole, sem gordura, cozido", "calorias": 219.0, "proteinas": 32.4, "carboidratos": 0.0, "gorduras": 8.9, "fibras": 0, "sodio": 44.0, "calcio": 4.0, "ferro": 2.6, "potassio": 239.0, "zinco": 4.7, "colesterol": 84.0, "vitamina_c": 0},
    "carne_bovina_coxao_mole_sem_gordura_cru": {"nome": "Carne, bovina, coxão mole, sem gordura, cru", "calorias": 169.0, "proteinas": 21.2, "carboidratos": 0.0, "gorduras": 8.7, "fibras": 0, "sodio": 61.0, "calcio": 3.0, "ferro": 1.9, "potassio": 335.0, "zinco": 2.6, "colesterol": 84.0, "vitamina_c": 0},
    "carne_bovina_cupim_assado": {"nome": "Carne, bovina, cupim, assado", "calorias": 330.0, "proteinas": 28.6, "carboidratos": 0.0, "gorduras": 23.0, "fibras": 0, "sodio": 72.0, "calcio": 8.0, "ferro": 2.7, "potassio": 321.0, "zinco": 5.3, "colesterol": 91.0, "vitamina_c": 0},
    "carne_bovina_cupim_cru": {"nome": "Carne, bovina, cupim, cru", "calorias": 221.0, "proteinas": 19.5, "carboidratos": 0.0, "gorduras": 15.3, "fibras": 0, "sodio": 47.0, "calcio": 4.0, "ferro": 1.1, "potassio": 151.0, "zinco": 2.4, "colesterol": 51.0, "vitamina_c": 0},
    "carne_bovina_figado_cru": {"nome": "Carne, bovina, fígado, cru", "calorias": 141.0, "proteinas": 20.7, "carboidratos": 1.1, "gorduras": 5.4, "fibras": 0, "sodio": 76.0, "calcio": 4.0, "ferro": 5.6, "potassio": 265.0, "zinco": 3.5, "colesterol": 393.0, "vitamina_c": 0},
    "carne_bovina_figado_grelhado": {"nome": "Carne, bovina, fígado, grelhado", "calorias": 225.0, "proteinas": 29.9, "carboidratos": 4.2, "gorduras": 9.0, "fibras": 0, "sodio": 82.0, "calcio": 6.0, "ferro": 5.8, "potassio": 309.0, "zinco": 4.0, "colesterol": 601.0, "vitamina_c": 0},
    "carne_bovina_file_mingnon_sem_gordura_cru": {"nome": "Carne, bovina, filé mingnon, sem gordura, cru", "calorias": 143.0, "proteinas": 21.6, "carboidratos": 0.0, "gorduras": 5.6, "fibras": 0, "sodio": 49.0, "calcio": 3.0, "ferro": 1.9, "potassio": 322.0, "zinco": 2.8, "colesterol": 55.0, "vitamina_c": 0},
    "carne_bovina_file_mingnon_sem_gordura_grelhado": {"nome": "Carne, bovina, filé mingnon, sem gordura, grelhado", "calorias": 220.0, "proteinas": 32.8, "carboidratos": 0.0, "gorduras": 8.8, "fibras": 0, "sodio": 58.0, "calcio": 4.0, "ferro": 2.9, "potassio": 326.0, "zinco": 4.1, "colesterol": 103.0, "vitamina_c": 0},
    "carne_bovina_flanco_sem_gordura_cozido": {"nome": "Carne, bovina, flanco, sem gordura, cozido", "calorias": 196.0, "proteinas": 29.4, "carboidratos": 0.0, "gorduras": 7.8, "fibras": 0, "sodio": 42.0, "calcio": 4.0, "ferro": 2.8, "potassio": 249.0, "zinco": 5.6, "colesterol": 62.0, "vitamina_c": 0},
    "carne_bovina_flanco_sem_gordura_cru": {"nome": "Carne, bovina, flanco, sem gordura, cru", "calorias": 141.0, "proteinas": 20.0, "carboidratos": 0.0, "gorduras": 6.2, "fibras": 0, "sodio": 54.0, "calcio": 3.0, "ferro": 1.6, "potassio": 324.0, "zinco": 4.5, "colesterol": 50.0, "vitamina_c": 0},
    "carne_bovina_fraldinha_com_gordura_cozida": {"nome": "Carne, bovina, fraldinha, com gordura, cozida", "calorias": 338.0, "proteinas": 24.2, "carboidratos": 0.0, "gorduras": 26.0, "fibras": 0, "sodio": 39.0, "calcio": 3.0, "ferro": 2.0, "potassio": 207.0, "zinco": 6.5, "colesterol": 65.0, "vitamina_c": 0},
    "carne_bovina_fraldinha_com_gordura_crua": {"nome": "Carne, bovina, fraldinha, com gordura, crua", "calorias": 221.0, "proteinas": 17.6, "carboidratos": 0.0, "gorduras": 16.1, "fibras": 0, "sodio": 51.0, "calcio": 3.0, "ferro": 1.5, "potassio": 274.0, "zinco": 4.2, "colesterol": 54.0, "vitamina_c": 0},
    "carne_bovina_lagarto_cozido": {"nome": "Carne, bovina, lagarto, cozido", "calorias": 222.0, "proteinas": 32.9, "carboidratos": 0.0, "gorduras": 9.1, "fibras": 0, "sodio": 48.0, "calcio": 4.0, "ferro": 1.9, "potassio": 254.0, "zinco": 7.0, "colesterol": 56.0, "vitamina_c": 0},
    "carne_bovina_lagarto_cru": {"nome": "Carne, bovina, lagarto, cru", "calorias": 135.0, "proteinas": 20.5, "carboidratos": 0.0, "gorduras": 5.2, "fibras": 0, "sodio": 54.0, "calcio": 3.0, "ferro": 1.3, "potassio": 362.0, "zinco": 2.4, "colesterol": 56.0, "vitamina_c": 0},
    "carne_bovina_lingua_cozida": {"nome": "Carne, bovina, língua, cozida", "calorias": 315.0, "proteinas": 21.4, "carboidratos": 0.0, "gorduras": 24.8, "fibras": 0, "sodio": 59.0, "calcio": 6.0, "ferro": 2.1, "potassio": 175.0, "zinco": 4.1, "colesterol": 105.0, "vitamina_c": 0},
    "carne_bovina_lingua_crua": {"nome": "Carne, bovina, língua, crua", "calorias": 215.0, "proteinas": 17.1, "carboidratos": 0.0, "gorduras": 15.8, "fibras": 0, "sodio": 73.0, "calcio": 5.0, "ferro": 1.7, "potassio": 251.0, "zinco": 2.9, "colesterol": 118.0, "vitamina_c": 0},
    "carne_bovina_maminha_crua": {"nome": "Carne, bovina, maminha, crua", "calorias": 153.0, "proteinas": 20.9, "carboidratos": 0.0, "gorduras": 7.0, "fibras": 0, "sodio": 37.0, "calcio": 3.0, "ferro": 1.1, "potassio": 274.0, "zinco": 3.5, "colesterol": 51.0, "vitamina_c": 0},
    "carne_bovina_maminha_grelhada": {"nome": "Carne, bovina, maminha, grelhada", "calorias": 153.0, "proteinas": 30.7, "carboidratos": 0.0, "gorduras": 2.4, "fibras": 0, "sodio": 58.0, "calcio": 4.0, "ferro": 2.4, "potassio": 386.0, "zinco": 5.6, "colesterol": 88.0, "vitamina_c": 0},
    "carne_bovina_miolo_de_alcatra_sem_gordura_cru": {"nome": "Carne, bovina, miolo de alcatra, sem gordura, cru", "calorias": 163.0, "proteinas": 21.6, "carboidratos": 0.0, "gorduras": 7.8, "fibras": 0, "sodio": 43.0, "calcio": 3.0, "ferro": 2.0, "potassio": 299.0, "zinco": 3.0, "colesterol": 60.0, "vitamina_c": 0},
    "carne_bovina_miolo_de_alcatra_sem_gordura_grelhado": {"nome": "Carne, bovina, miolo de alcatra, sem gordura, grelhado", "calorias": 241.0, "proteinas": 31.9, "carboidratos": 0.0, "gorduras": 11.6, "fibras": 0, "sodio": 52.0, "calcio": 5.0, "ferro": 3.2, "potassio": 385.0, "zinco": 4.8, "colesterol": 92.0, "vitamina_c": 0},
    "carne_bovina_musculo_sem_gordura_cozido": {"nome": "Carne, bovina, músculo, sem gordura, cozido", "calorias": 194.0, "proteinas": 31.2, "carboidratos": 0.0, "gorduras": 6.7, "fibras": 0, "sodio": 62.0, "calcio": 5.0, "ferro": 2.4, "potassio": 253.0, "zinco": 6.4, "colesterol": 56.0, "vitamina_c": 0},
    "carne_bovina_musculo_sem_gordura_cru": {"nome": "Carne, bovina, músculo, sem gordura, cru", "calorias": 142.0, "proteinas": 21.6, "carboidratos": 0.0, "gorduras": 5.5, "fibras": 0, "sodio": 66.0, "calcio": 4.0, "ferro": 1.9, "potassio": 296.0, "zinco": 3.7, "colesterol": 51.0, "vitamina_c": 0},
    "carne_bovina_paleta_com_gordura_crua": {"nome": "Carne, bovina, paleta, com gordura, crua", "calorias": 159.0, "proteinas": 21.4, "carboidratos": 0.0, "gorduras": 7.5, "fibras": 0, "sodio": 65.0, "calcio": 4.0, "ferro": 1.8, "potassio": 250.0, "zinco": 3.7, "colesterol": 58.0, "vitamina_c": 0},
    "carne_bovina_paleta_sem_gordura_cozida": {"nome": "Carne, bovina, paleta, sem gordura, cozida", "calorias": 194.0, "proteinas": 29.7, "carboidratos": 0.0, "gorduras": 7.4, "fibras": 0, "sodio": 58.0, "calcio": 6.0, "ferro": 2.2, "potassio": 250.0, "zinco": 6.8, "colesterol": 56.0, "vitamina_c": 0},
    "carne_bovina_paleta_sem_gordura_crua": {"nome": "Carne, bovina, paleta, sem gordura, crua", "calorias": 141.0, "proteinas": 21.0, "carboidratos": 0.0, "gorduras": 5.7, "fibras": 0, "sodio": 66.0, "calcio": 4.0, "ferro": 1.9, "potassio": 319.0, "zinco": 3.3, "colesterol": 42.0, "vitamina_c": 0},
    "carne_bovina_patinho_sem_gordura_cru": {"nome": "Carne, bovina, patinho, sem gordura, cru", "calorias": 133.0, "proteinas": 21.7, "carboidratos": 0.0, "gorduras": 4.5, "fibras": 0, "sodio": 49.0, "calcio": 3.0, "ferro": 1.8, "potassio": 318.0, "zinco": 4.5, "colesterol": 56.0, "vitamina_c": 0},
    "carne_bovina_patinho_sem_gordura_grelhado": {"nome": "Carne, bovina, patinho, sem gordura, grelhado", "calorias": 219.0, "proteinas": 35.9, "carboidratos": 0.0, "gorduras": 7.3, "fibras": 0, "sodio": 60.0, "calcio": 5.0, "ferro": 3.0, "potassio": 421.0, "zinco": 8.1, "colesterol": 126.0, "vitamina_c": 0},
    "carne_bovina_peito_sem_gordura_cozido": {"nome": "Carne, bovina, peito, sem gordura, cozido", "calorias": 338.0, "proteinas": 22.2, "carboidratos": 0.0, "gorduras": 27.0, "fibras": 0, "sodio": 56.0, "calcio": 4.0, "ferro": 1.6, "potassio": 204.0, "zinco": 3.9, "colesterol": 100.0, "vitamina_c": 0},
    "carne_bovina_peito_sem_gordura_cru": {"nome": "Carne, bovina, peito, sem gordura, cru", "calorias": 259.0, "proteinas": 17.6, "carboidratos": 0.0, "gorduras": 20.4, "fibras": 0, "sodio": 64.0, "calcio": 4.0, "ferro": 1.3, "potassio": 241.0, "zinco": 2.6, "colesterol": 59.0, "vitamina_c": 0},
    "carne_bovina_picanha_com_gordura_crua": {"nome": "Carne, bovina, picanha, com gordura, crua", "calorias": 213.0, "proteinas": 18.8, "carboidratos": 0.0, "gorduras": 14.7, "fibras": 0, "sodio": 38.0, "calcio": 2.0, "ferro": 1.7, "potassio": 232.0, "zinco": 3.8, "colesterol": 60.0, "vitamina_c": 0},
    "carne_bovina_picanha_com_gordura_grelhada": {"nome": "Carne, bovina, picanha, com gordura, grelhada", "calorias": 289.0, "proteinas": 26.4, "carboidratos": 0.0, "gorduras": 19.5, "fibras": 0, "sodio": 60.0, "calcio": 4.0, "ferro": 3.2, "potassio": 355.0, "zinco": 5.5, "colesterol": 92.0, "vitamina_c": 0},
    "carne_bovina_picanha_sem_gordura_crua": {"nome": "Carne, bovina, picanha, sem gordura, crua", "calorias": 134.0, "proteinas": 21.3, "carboidratos": 0.0, "gorduras": 4.7, "fibras": 0, "sodio": 61.0, "calcio": 3.0, "ferro": 2.1, "potassio": 322.0, "zinco": 4.2, "colesterol": 75.0, "vitamina_c": 0},
    "carne_bovina_picanha_sem_gordura_grelhada": {"nome": "Carne, bovina, picanha, sem gordura, grelhada", "calorias": 238.0, "proteinas": 31.9, "carboidratos": 0.0, "gorduras": 11.3, "fibras": 0, "sodio": 61.0, "calcio": 4.0, "ferro": 3.6, "potassio": 377.0, "zinco": 6.7, "colesterol": 100.0, "vitamina_c": 0},
    "carne_bovina_seca_cozida": {"nome": "Carne, bovina, seca, cozida", "calorias": 313.0, "proteinas": 26.9, "carboidratos": 0.0, "gorduras": 21.9, "fibras": 0, "sodio": 1943.0, "calcio": 13.0, "ferro": 1.9, "potassio": 86.0, "zinco": 7.7, "colesterol": 100.0, "vitamina_c": 0},
    "carne_bovina_seca_crua": {"nome": "Carne, bovina, seca, crua", "calorias": 313.0, "proteinas": 19.7, "carboidratos": 0.0, "gorduras": 25.4, "fibras": 0, "sodio": 4440.0, "calcio": 14.0, "ferro": 1.3, "potassio": 190.0, "zinco": 3.7, "colesterol": 92.0, "vitamina_c": 0},
    "coxinha_de_frango_frita": {"nome": "Coxinha de frango, frita", "calorias": 283.0, "proteinas": 9.6, "carboidratos": 34.5, "gorduras": 11.8, "fibras": 5.0, "sodio": 532.0, "calcio": 18.0, "ferro": 1.3, "potassio": 166.0, "zinco": 0.5, "colesterol": 15.0, "vitamina_c": 0},
    "croquete_de_carne_cru": {"nome": "Croquete, de carne, cru", "calorias": 246.0, "proteinas": 12.0, "carboidratos": 13.9, "gorduras": 15.6, "fibras": 0, "sodio": 711.0, "calcio": 15.0, "ferro": 2.5, "potassio": 221.0, "zinco": 2.7, "colesterol": 30.0, "vitamina_c": 0},
    "croquete_de_carne_frito": {"nome": "Croquete, de carne, frito", "calorias": 347.0, "proteinas": 16.9, "carboidratos": 18.1, "gorduras": 22.7, "fibras": 0, "sodio": 916.0, "calcio": 18.0, "ferro": 2.3, "potassio": 313.0, "zinco": 3.3, "colesterol": 38.0, "vitamina_c": 0},
    "empada_de_frango_pre_cozida": {"nome": "Empada, de frango, pré-cozida", "calorias": 377.0, "proteinas": 7.3, "carboidratos": 35.5, "gorduras": 22.9, "fibras": 2.2, "sodio": 771.0, "calcio": 14.0, "ferro": 0.7, "potassio": 156.0, "zinco": 0.5, "colesterol": 23.0, "vitamina_c": 0},
    "empada_de_frango_pre_cozida_assada": {"nome": "Empada de frango, pré-cozida, assada", "calorias": 358.0, "proteinas": 6.9, "carboidratos": 47.5, "gorduras": 15.6, "fibras": 2.2, "sodio": 525.0, "calcio": 16.0, "ferro": 1.2, "potassio": 138.0, "zinco": 0.6, "colesterol": 23.0, "vitamina_c": 0},
    "frango_asa_com_pele_crua": {"nome": "Frango, asa, com pele, crua", "calorias": 213.0, "proteinas": 18.1, "carboidratos": 0.0, "gorduras": 15.1, "fibras": 0, "sodio": 96.0, "calcio": 11.0, "ferro": 0.6, "potassio": 211.0, "zinco": 1.2, "colesterol": 113.0, "vitamina_c": 0},
    "frango_caipira_inteiro_com_pele_cozido": {"nome": "Frango, caipira, inteiro, com pele, cozido", "calorias": 243.0, "proteinas": 23.9, "carboidratos": 0.0, "gorduras": 15.6, "fibras": 0, "sodio": 56.0, "calcio": 17.0, "ferro": 1.7, "potassio": 210.0, "zinco": 1.7, "colesterol": 110.0, "vitamina_c": 0},
    "frango_caipira_inteiro_sem_pele_cozido": {"nome": "Frango, caipira, inteiro, sem pele, cozido", "calorias": 196.0, "proteinas": 29.6, "carboidratos": 0.0, "gorduras": 7.7, "fibras": 0, "sodio": 53.0, "calcio": 66.0, "ferro": 2.1, "potassio": 224.0, "zinco": 2.7, "colesterol": 106.0, "vitamina_c": 0},
    "frango_coracao_cru": {"nome": "Frango, coração, cru", "calorias": 222.0, "proteinas": 12.6, "carboidratos": 0.0, "gorduras": 18.6, "fibras": 0, "sodio": 95.0, "calcio": 6.0, "ferro": 4.1, "potassio": 220.0, "zinco": 2.0, "colesterol": 159.0, "vitamina_c": 0},
    "frango_coracao_grelhado": {"nome": "Frango, coração, grelhado", "calorias": 207.0, "proteinas": 22.4, "carboidratos": 0.6, "gorduras": 12.1, "fibras": 0, "sodio": 128.0, "calcio": 8.0, "ferro": 6.5, "potassio": 243.0, "zinco": 3.4, "colesterol": 280.0, "vitamina_c": 0},
    "frango_coxa_com_pele_assada": {"nome": "Frango, coxa, com pele, assada", "calorias": 215.0, "proteinas": 28.5, "carboidratos": 0.1, "gorduras": 10.4, "fibras": 0, "sodio": 95.0, "calcio": 8.0, "ferro": 1.2, "potassio": 318.0, "zinco": 2.6, "colesterol": 145.0, "vitamina_c": 0},
    "frango_coxa_com_pele_crua": {"nome": "Frango, coxa, com pele, crua", "calorias": 161.0, "proteinas": 17.1, "carboidratos": 0.0, "gorduras": 9.8, "fibras": 0, "sodio": 95.0, "calcio": 8.0, "ferro": 0.7, "potassio": 275.0, "zinco": 2.0, "colesterol": 97.0, "vitamina_c": 0},
    "frango_coxa_sem_pele_cozida": {"nome": "Frango, coxa, sem pele, cozida", "calorias": 167.0, "proteinas": 26.9, "carboidratos": 0.0, "gorduras": 5.8, "fibras": 0, "sodio": 64.0, "calcio": 12.0, "ferro": 0.8, "potassio": 191.0, "zinco": 2.8, "colesterol": 133.0, "vitamina_c": 0},
    "frango_coxa_sem_pele_crua": {"nome": "Frango, coxa, sem pele, crua", "calorias": 120.0, "proteinas": 17.8, "carboidratos": 0.0, "gorduras": 4.9, "fibras": 0, "sodio": 98.0, "calcio": 8.0, "ferro": 0.8, "potassio": 291.0, "zinco": 2.2, "colesterol": 91.0, "vitamina_c": 0},
    "frango_figado_cru": {"nome": "Frango, fígado, cru", "calorias": 106.0, "proteinas": 17.6, "carboidratos": 0.0, "gorduras": 3.5, "fibras": 0, "sodio": 82.0, "calcio": 6.0, "ferro": 9.5, "potassio": 281.0, "zinco": 3.7, "colesterol": 341.0, "vitamina_c": 0},
    "frango_file_a_milanesa": {"nome": "Frango, filé, à milanesa", "calorias": 221.0, "proteinas": 28.5, "carboidratos": 7.5, "gorduras": 7.8, "fibras": 1.1, "sodio": 122.0, "calcio": 9.0, "ferro": 1.1, "potassio": 408.0, "zinco": 0.8, "colesterol": 84.0, "vitamina_c": 0},
    "frango_inteiro_com_pele_cru": {"nome": "Frango, inteiro, com pele, cru", "calorias": 226.0, "proteinas": 16.4, "carboidratos": 0.0, "gorduras": 17.3, "fibras": 0, "sodio": 63.0, "calcio": 6.0, "ferro": 0.6, "potassio": 217.0, "zinco": 1.1, "colesterol": 85.0, "vitamina_c": 0},
    "frango_inteiro_sem_pele_assado": {"nome": "Frango, inteiro, sem pele, assado", "calorias": 187.0, "proteinas": 28.0, "carboidratos": 0.0, "gorduras": 7.5, "fibras": 0, "sodio": 70.0, "calcio": 9.0, "ferro": 0.6, "potassio": 283.0, "zinco": 1.6, "colesterol": 111.0, "vitamina_c": 0},
    "frango_inteiro_sem_pele_cozido": {"nome": "Frango, inteiro, sem pele, cozido", "calorias": 170.0, "proteinas": 25.0, "carboidratos": 0.0, "gorduras": 7.1, "fibras": 0, "sodio": 51.0, "calcio": 8.0, "ferro": 0.5, "potassio": 217.0, "zinco": 1.2, "colesterol": 99.0, "vitamina_c": 0},
    "frango_inteiro_sem_pele_cru": {"nome": "Frango, inteiro, sem pele, cru", "calorias": 129.0, "proteinas": 20.6, "carboidratos": 0.0, "gorduras": 4.6, "fibras": 0, "sodio": 73.0, "calcio": 7.0, "ferro": 0.5, "potassio": 238.0, "zinco": 1.2, "colesterol": 78.0, "vitamina_c": 0},
    "frango_peito_com_pele_assado": {"nome": "Frango, peito, com pele, assado", "calorias": 212.0, "proteinas": 33.4, "carboidratos": 0.0, "gorduras": 7.6, "fibras": 0, "sodio": 56.0, "calcio": 8.0, "ferro": 0.5, "potassio": 380.0, "zinco": 1.0, "colesterol": 109.0, "vitamina_c": 0},
    "frango_peito_com_pele_cru": {"nome": "Frango, peito, com pele, cru", "calorias": 149.0, "proteinas": 20.8, "carboidratos": 0.0, "gorduras": 6.7, "fibras": 0, "sodio": 62.0, "calcio": 8.0, "ferro": 0.4, "potassio": 252.0, "zinco": 0.6, "colesterol": 80.0, "vitamina_c": 0},
    "frango_peito_sem_pele_cozido": {"nome": "Frango, peito, sem pele, cozido", "calorias": 163.0, "proteinas": 31.5, "carboidratos": 0.0, "gorduras": 3.2, "fibras": 0, "sodio": 36.0, "calcio": 6.0, "ferro": 0.3, "potassio": 231.0, "zinco": 0.9, "colesterol": 89.0, "vitamina_c": 0},
    "frango_peito_sem_pele_cru": {"nome": "Frango, peito, sem pele, cru", "calorias": 119.0, "proteinas": 21.5, "carboidratos": 0.0, "gorduras": 3.0, "fibras": 0, "sodio": 56.0, "calcio": 7.0, "ferro": 0.4, "potassio": 267.0, "zinco": 0.7, "colesterol": 59.0, "vitamina_c": 0},
    "frango_peito_sem_pele_grelhado": {"nome": "Frango, peito, sem pele, grelhado", "calorias": 159.0, "proteinas": 32.0, "carboidratos": 0.0, "gorduras": 2.5, "fibras": 0, "sodio": 50.0, "calcio": 5.0, "ferro": 0.3, "potassio": 387.0, "zinco": 0.8, "colesterol": 89.0, "vitamina_c": 0},
    "frango_sobrecoxa_com_pele_assada": {"nome": "Frango, sobrecoxa, com pele, assada", "calorias": 260.0, "proteinas": 28.7, "carboidratos": 0.0, "gorduras": 15.2, "fibras": 0, "sodio": 96.0, "calcio": 11.0, "ferro": 1.2, "potassio": 323.0, "zinco": 2.2, "colesterol": 158.0, "vitamina_c": 0},
    "frango_sobrecoxa_com_pele_crua": {"nome": "Frango, sobrecoxa, com pele, crua", "calorias": 255.0, "proteinas": 15.5, "carboidratos": 0.0, "gorduras": 20.9, "fibras": 0, "sodio": 68.0, "calcio": 7.0, "ferro": 0.7, "potassio": 190.0, "zinco": 1.3, "colesterol": 88.0, "vitamina_c": 0},
    "frango_sobrecoxa_sem_pele_assada": {"nome": "Frango, sobrecoxa, sem pele, assada", "calorias": 233.0, "proteinas": 29.2, "carboidratos": 0.0, "gorduras": 12.0, "fibras": 0, "sodio": 106.0, "calcio": 12.0, "ferro": 1.2, "potassio": 382.0, "zinco": 2.2, "colesterol": 145.0, "vitamina_c": 0},
    "frango_sobrecoxa_sem_pele_crua": {"nome": "Frango, sobrecoxa, sem pele, crua", "calorias": 162.0, "proteinas": 17.6, "carboidratos": 0.0, "gorduras": 9.6, "fibras": 0, "sodio": 80.0, "calcio": 6.0, "ferro": 0.9, "potassio": 241.0, "zinco": 1.7, "colesterol": 84.0, "vitamina_c": 0},
    "hamburguer_bovino_cru": {"nome": "Hambúrguer, bovino, cru", "calorias": 215.0, "proteinas": 13.2, "carboidratos": 4.2, "gorduras": 16.2, "fibras": 0, "sodio": 869.0, "calcio": 34.0, "ferro": 1.9, "potassio": 383.0, "zinco": 1.7, "colesterol": 70.0, "vitamina_c": 0},
    "hamburguer_bovino_frito": {"nome": "Hambúrguer, bovino, frito", "calorias": 258.0, "proteinas": 20.0, "carboidratos": 6.3, "gorduras": 17.0, "fibras": 0, "sodio": 1252.0, "calcio": 62.0, "ferro": 3.0, "potassio": 660.0, "zinco": 3.2, "colesterol": 49.0, "vitamina_c": 0},
    "hamburguer_bovino_grelhado": {"nome": "Hambúrguer, bovino, grelhado", "calorias": 210.0, "proteinas": 13.2, "carboidratos": 11.3, "gorduras": 12.4, "fibras": 0, "sodio": 1090.0, "calcio": 56.0, "ferro": 2.6, "potassio": 538.0, "zinco": 3.0, "colesterol": 59.0, "vitamina_c": 0},
    "linguica_frango_crua": {"nome": "Lingüiça, frango, crua", "calorias": 218.0, "proteinas": 14.2, "carboidratos": 0.0, "gorduras": 17.4, "fibras": 0, "sodio": 1126.0, "calcio": 11.0, "ferro": 0.5, "potassio": 280.0, "zinco": 0.7, "colesterol": 64.0, "vitamina_c": 0},
    "linguica_frango_frita": {"nome": "Lingüiça, frango, frita", "calorias": 245.0, "proteinas": 18.3, "carboidratos": 0.0, "gorduras": 18.5, "fibras": 0, "sodio": 1374.0, "calcio": 15.0, "ferro": 0.8, "potassio": 364.0, "zinco": 1.2, "colesterol": 76.0, "vitamina_c": 0},
    "linguica_frango_grelhada": {"nome": "Lingüiça, frango, grelhada", "calorias": 244.0, "proteinas": 18.2, "carboidratos": 0.0, "gorduras": 18.4, "fibras": 0, "sodio": 1351.0, "calcio": 14.0, "ferro": 0.7, "potassio": 356.0, "zinco": 1.0, "colesterol": 80.0, "vitamina_c": 0},
    "linguica_porco_crua": {"nome": "Lingüiça, porco, crua", "calorias": 227.0, "proteinas": 16.1, "carboidratos": 0.0, "gorduras": 17.6, "fibras": 0, "sodio": 1176.0, "calcio": 6.0, "ferro": 0.4, "potassio": 316.0, "zinco": 1.4, "colesterol": 53.0, "vitamina_c": 0},
    "linguica_porco_frita": {"nome": "Lingüiça, porco, frita", "calorias": 280.0, "proteinas": 20.5, "carboidratos": 0.0, "gorduras": 21.3, "fibras": 0, "sodio": 1432.0, "calcio": 8.0, "ferro": 0.9, "potassio": 409.0, "zinco": 3.1, "colesterol": 75.0, "vitamina_c": 0},
    "linguica_porco_grelhada": {"nome": "Lingüiça, porco, grelhada", "calorias": 296.0, "proteinas": 23.2, "carboidratos": 0.0, "gorduras": 21.9, "fibras": 0, "sodio": 1456.0, "calcio": 8.0, "ferro": 1.0, "potassio": 427.0, "zinco": 3.5, "colesterol": 82.0, "vitamina_c": 0},
    "mortadela": {"nome": "Mortadela", "calorias": 269.0, "proteinas": 12.0, "carboidratos": 5.8, "gorduras": 21.6, "fibras": 0, "sodio": 1212.0, "calcio": 67.0, "ferro": 1.5, "potassio": 247.0, "zinco": 1.0, "colesterol": 83.0, "vitamina_c": 0},
    "peru_congelado_assado": {"nome": "Peru, congelado, assado", "calorias": 163.0, "proteinas": 26.2, "carboidratos": 0.0, "gorduras": 5.7, "fibras": 0, "sodio": 628.0, "calcio": 14.0, "ferro": 0.6, "potassio": 175.0, "zinco": 1.2, "colesterol": 91.0, "vitamina_c": 0},
    "peru_congelado_cru": {"nome": "Peru, congelado, cru", "calorias": 94.0, "proteinas": 18.1, "carboidratos": 0.0, "gorduras": 1.8, "fibras": 0, "sodio": 711.0, "calcio": 10.0, "ferro": 0.9, "potassio": 281.0, "zinco": 1.4, "colesterol": 68.0, "vitamina_c": 0},
    "porco_bisteca_crua": {"nome": "Porco, bisteca, crua", "calorias": 164.0, "proteinas": 21.5, "carboidratos": 0.0, "gorduras": 8.0, "fibras": 0, "sodio": 54.0, "calcio": 6.0, "ferro": 0.5, "potassio": 335.0, "zinco": 1.4, "colesterol": 56.0, "vitamina_c": 0},
    "porco_bisteca_frita": {"nome": "Porco, bisteca, frita", "calorias": 311.0, "proteinas": 33.7, "carboidratos": 0.0, "gorduras": 18.5, "fibras": 0, "sodio": 63.0, "calcio": 69.0, "ferro": 0.8, "potassio": 404.0, "zinco": 2.2, "colesterol": 126.0, "vitamina_c": 0},
    "porco_bisteca_grelhada": {"nome": "Porco, bisteca, grelhada", "calorias": 280.0, "proteinas": 28.9, "carboidratos": 0.0, "gorduras": 17.4, "fibras": 0, "sodio": 51.0, "calcio": 34.0, "ferro": 0.9, "potassio": 366.0, "zinco": 2.3, "colesterol": 82.0, "vitamina_c": 0},
    "porco_costela_assada": {"nome": "Porco, costela, assada", "calorias": 402.0, "proteinas": 30.2, "carboidratos": 0.0, "gorduras": 30.3, "fibras": 0, "sodio": 63.0, "calcio": 17.0, "ferro": 1.0, "potassio": 246.0, "zinco": 3.1, "colesterol": 113.0, "vitamina_c": 0},
    "porco_costela_crua": {"nome": "Porco, costela, crua", "calorias": 256.0, "proteinas": 18.0, "carboidratos": 0.0, "gorduras": 19.8, "fibras": 0, "sodio": 88.0, "calcio": 15.0, "ferro": 0.9, "potassio": 248.0, "zinco": 2.3, "colesterol": 69.0, "vitamina_c": 0},
    "porco_lombo_assado": {"nome": "Porco, lombo, assado", "calorias": 210.0, "proteinas": 35.7, "carboidratos": 0.0, "gorduras": 6.4, "fibras": 0, "sodio": 39.0, "calcio": 20.0, "ferro": 0.5, "potassio": 311.0, "zinco": 1.8, "colesterol": 103.0, "vitamina_c": 0},
    "porco_lombo_cru": {"nome": "Porco, lombo, cru", "calorias": 176.0, "proteinas": 22.6, "carboidratos": 0.0, "gorduras": 8.8, "fibras": 0, "sodio": 53.0, "calcio": 4.0, "ferro": 0.5, "potassio": 334.0, "zinco": 0.9, "colesterol": 55.0, "vitamina_c": 0},
    "porco_orelha_salgada_crua": {"nome": "Porco, orelha, salgada, crua", "calorias": 258.0, "proteinas": 18.5, "carboidratos": 0.0, "gorduras": 19.9, "fibras": 0, "sodio": 616.0, "calcio": 5.0, "ferro": 1.4, "potassio": 228.0, "zinco": 0.6, "colesterol": 83.0, "vitamina_c": 0},
    "porco_pernil_assado": {"nome": "Porco, pernil, assado", "calorias": 262.0, "proteinas": 32.1, "carboidratos": 0.0, "gorduras": 13.9, "fibras": 0, "sodio": 62.0, "calcio": 18.0, "ferro": 1.3, "potassio": 395.0, "zinco": 3.3, "colesterol": 110.0, "vitamina_c": 0},
    "porco_pernil_cru": {"nome": "Porco, pernil, cru", "calorias": 186.0, "proteinas": 20.1, "carboidratos": 0.0, "gorduras": 11.1, "fibras": 0, "sodio": 102.0, "calcio": 13.0, "ferro": 0.9, "potassio": 256.0, "zinco": 1.7, "colesterol": 59.0, "vitamina_c": 0},
    "porco_rabo_salgado_cru": {"nome": "Porco, rabo, salgado, cru", "calorias": 377.0, "proteinas": 15.6, "carboidratos": 0.0, "gorduras": 34.5, "fibras": 0, "sodio": 1158.0, "calcio": 22.0, "ferro": 0.6, "potassio": 24.0, "zinco": 1.4, "colesterol": 89.0, "vitamina_c": 0},
    "presunto_com_capa_de_gordura": {"nome": "Presunto, com capa de gordura", "calorias": 128.0, "proteinas": 14.4, "carboidratos": 1.4, "gorduras": 6.8, "fibras": 0, "sodio": 1021.0, "calcio": 12.0, "ferro": 0.7, "potassio": 295.0, "zinco": 1.3, "colesterol": 40.0, "vitamina_c": 0},
    "presunto_sem_capa_de_gordura": {"nome": "Presunto, sem capa de gordura", "calorias": 94.0, "proteinas": 14.3, "carboidratos": 2.1, "gorduras": 2.7, "fibras": 0, "sodio": 1039.0, "calcio": 23.0, "ferro": 0.8, "potassio": 307.0, "zinco": 1.5, "colesterol": 36.0, "vitamina_c": 0},
    "quibe_assado": {"nome": "Quibe, assado", "calorias": 136.0, "proteinas": 14.6, "carboidratos": 12.9, "gorduras": 2.7, "fibras": 1.9, "sodio": 40.0, "calcio": 16.0, "ferro": 2.2, "potassio": 288.0, "zinco": 4.1, "colesterol": 34.0, "vitamina_c": 0},
    "quibe_cru": {"nome": "Quibe, cru", "calorias": 109.0, "proteinas": 12.4, "carboidratos": 10.8, "gorduras": 1.7, "fibras": 1.6, "sodio": 39.0, "calcio": 12.0, "ferro": 1.7, "potassio": 242.0, "zinco": 2.8, "colesterol": 27.0, "vitamina_c": 0},
    "quibe_frito": {"nome": "Quibe, frito", "calorias": 254.0, "proteinas": 14.9, "carboidratos": 12.3, "gorduras": 15.8, "fibras": 0, "sodio": 836.0, "calcio": 22.0, "ferro": 2.0, "potassio": 322.0, "zinco": 2.8, "colesterol": 38.0, "vitamina_c": 0},
    "salame": {"nome": "Salame", "calorias": 398.0, "proteinas": 25.8, "carboidratos": 2.9, "gorduras": 30.6, "fibras": 0, "sodio": 1574.0, "calcio": 87.0, "ferro": 1.3, "potassio": 548.0, "zinco": 3.2, "colesterol": 85.0, "vitamina_c": 0},
    "toucinho_cru": {"nome": "Toucinho, cru", "calorias": 593.0, "proteinas": 11.5, "carboidratos": 0.0, "gorduras": 60.3, "fibras": 0, "sodio": 50.0, "calcio": 2.0, "ferro": 0.4, "potassio": 58.0, "zinco": 0.2, "colesterol": 73.0, "vitamina_c": 0},
    "toucinho_frito": {"nome": "Toucinho, frito", "calorias": 697.0, "proteinas": 27.3, "carboidratos": 0.0, "gorduras": 64.3, "fibras": 0, "sodio": 125.0, "calcio": 9.0, "ferro": 0.9, "potassio": 171.0, "zinco": 0.8, "colesterol": 89.0, "vitamina_c": 0},

    # ═══════════════════════════════════════════════════════════════
    # CEREAIS E DERIVADOS
    # ═══════════════════════════════════════════════════════════════
    "arroz_integral_cozido": {"nome": "Arroz, integral, cozido", "calorias": 124.0, "proteinas": 2.6, "carboidratos": 25.8, "gorduras": 1.0, "fibras": 2.7, "sodio": 1.0, "calcio": 5.0, "ferro": 0.3, "potassio": 75.0, "zinco": 0.7, "colesterol": 0, "vitamina_c": 0},
    "arroz_integral_cru": {"nome": "Arroz, integral, cru", "calorias": 360.0, "proteinas": 7.3, "carboidratos": 77.5, "gorduras": 1.9, "fibras": 4.8, "sodio": 2.0, "calcio": 8.0, "ferro": 0.9, "potassio": 173.0, "zinco": 1.4, "colesterol": 0, "vitamina_c": 0},
    "arroz_tipo_1_cozido": {"nome": "Arroz, tipo 1, cozido", "calorias": 128.0, "proteinas": 2.5, "carboidratos": 28.1, "gorduras": 0.2, "fibras": 1.6, "sodio": 1.0, "calcio": 4.0, "ferro": 0.1, "potassio": 15.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 0},
    "arroz_tipo_1_cru": {"nome": "Arroz, tipo 1, cru", "calorias": 358.0, "proteinas": 7.2, "carboidratos": 78.8, "gorduras": 0.3, "fibras": 1.6, "sodio": 1.0, "calcio": 4.0, "ferro": 0.7, "potassio": 62.0, "zinco": 1.2, "colesterol": 0, "vitamina_c": 0},
    "arroz_tipo_2_cozido": {"nome": "Arroz, tipo 2, cozido", "calorias": 130.0, "proteinas": 2.6, "carboidratos": 28.2, "gorduras": 0.4, "fibras": 1.1, "sodio": 2.0, "calcio": 3.0, "ferro": 0.1, "potassio": 20.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 0},
    "arroz_tipo_2_cru": {"nome": "Arroz, tipo 2, cru", "calorias": 358.0, "proteinas": 7.2, "carboidratos": 78.9, "gorduras": 0.3, "fibras": 1.7, "sodio": 1.0, "calcio": 5.0, "ferro": 0.6, "potassio": 57.0, "zinco": 1.3, "colesterol": 0, "vitamina_c": 0},
    "aveia_flocos_crua": {"nome": "Aveia, flocos, crua", "calorias": 394.0, "proteinas": 13.9, "carboidratos": 66.6, "gorduras": 8.5, "fibras": 9.1, "sodio": 5.0, "calcio": 48.0, "ferro": 4.4, "potassio": 336.0, "zinco": 2.6, "colesterol": 0, "vitamina_c": 1.4},
    "biscoito_doce_maisena": {"nome": "Biscoito, doce, maisena", "calorias": 443.0, "proteinas": 8.1, "carboidratos": 75.2, "gorduras": 12.0, "fibras": 2.1, "sodio": 352.0, "calcio": 54.0, "ferro": 1.8, "potassio": 142.0, "zinco": 1.0, "colesterol": 0, "vitamina_c": 6.2},
    "biscoito_doce_recheado_com_chocolate": {"nome": "Biscoito, doce, recheado com chocolate", "calorias": 472.0, "proteinas": 6.4, "carboidratos": 70.5, "gorduras": 19.6, "fibras": 3.0, "sodio": 239.0, "calcio": 27.0, "ferro": 2.3, "potassio": 232.0, "zinco": 1.0, "colesterol": 0, "vitamina_c": 3.5},
    "biscoito_doce_recheado_com_morango": {"nome": "Biscoito, doce, recheado com morango", "calorias": 471.0, "proteinas": 5.7, "carboidratos": 71.0, "gorduras": 19.6, "fibras": 1.5, "sodio": 230.0, "calcio": 36.0, "ferro": 1.5, "potassio": 113.0, "zinco": 0.7, "colesterol": 0, "vitamina_c": 0},
    "biscoito_doce_wafer_recheado_de_chocolate": {"nome": "Biscoito, doce, wafer, recheado de chocolate", "calorias": 502.0, "proteinas": 5.6, "carboidratos": 67.5, "gorduras": 24.7, "fibras": 1.8, "sodio": 137.0, "calcio": 23.0, "ferro": 2.4, "potassio": 240.0, "zinco": 0.9, "colesterol": 0, "vitamina_c": 0},
    "biscoito_doce_wafer_recheado_de_morango": {"nome": "Biscoito, doce, wafer, recheado de morango", "calorias": 513.0, "proteinas": 4.5, "carboidratos": 67.4, "gorduras": 26.4, "fibras": 0.8, "sodio": 120.0, "calcio": 14.0, "ferro": 1.1, "potassio": 75.0, "zinco": 0.5, "colesterol": 1.0, "vitamina_c": 0},
    "biscoito_salgado_cream_cracker": {"nome": "Biscoito, salgado, cream cracker", "calorias": 432.0, "proteinas": 10.1, "carboidratos": 68.7, "gorduras": 14.4, "fibras": 2.5, "sodio": 854.0, "calcio": 20.0, "ferro": 2.2, "potassio": 181.0, "zinco": 1.1, "colesterol": 0, "vitamina_c": 0},
    "bolo_mistura_para": {"nome": "Bolo, mistura para", "calorias": 419.0, "proteinas": 6.2, "carboidratos": 84.7, "gorduras": 6.1, "fibras": 1.7, "sodio": 463.0, "calcio": 59.0, "ferro": 1.2, "potassio": 75.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 0},
    "bolo_pronto_aipim": {"nome": "Bolo, pronto, aipim", "calorias": 324.0, "proteinas": 4.4, "carboidratos": 47.9, "gorduras": 12.7, "fibras": 0.7, "sodio": 111.0, "calcio": 85.0, "ferro": 0.5, "potassio": 135.0, "zinco": 0.4, "colesterol": 73.0, "vitamina_c": 0},
    "bolo_pronto_chocolate": {"nome": "Bolo, pronto, chocolate", "calorias": 410.0, "proteinas": 6.2, "carboidratos": 54.7, "gorduras": 18.5, "fibras": 1.4, "sodio": 283.0, "calcio": 75.0, "ferro": 2.1, "potassio": 212.0, "zinco": 0.7, "colesterol": 77.0, "vitamina_c": 0},
    "bolo_pronto_coco": {"nome": "Bolo, pronto, coco", "calorias": 333.0, "proteinas": 5.7, "carboidratos": 52.3, "gorduras": 11.3, "fibras": 1.1, "sodio": 190.0, "calcio": 57.0, "ferro": 0.8, "potassio": 143.0, "zinco": 0.7, "colesterol": 63.0, "vitamina_c": 0},
    "bolo_pronto_milho": {"nome": "Bolo, pronto, milho", "calorias": 311.0, "proteinas": 4.8, "carboidratos": 45.1, "gorduras": 12.4, "fibras": 0.7, "sodio": 134.0, "calcio": 83.0, "ferro": 0.7, "potassio": 118.0, "zinco": 0.4, "colesterol": 82.0, "vitamina_c": 0},
    "canjica_branca_crua": {"nome": "Canjica, branca, crua", "calorias": 358.0, "proteinas": 7.2, "carboidratos": 78.1, "gorduras": 1.0, "fibras": 5.5, "sodio": 1.0, "calcio": 2.0, "ferro": 0.3, "potassio": 93.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 0},
    "canjica_com_leite_integral": {"nome": "Canjica, com leite integral", "calorias": 112.0, "proteinas": 2.4, "carboidratos": 23.6, "gorduras": 1.2, "fibras": 1.2, "sodio": 28.0, "calcio": 43.0, "ferro": 0.1, "potassio": 70.0, "zinco": 0.3, "colesterol": 1.0, "vitamina_c": 0},
    "cereais_milho_flocos_com_sal": {"nome": "Cereais, milho, flocos, com sal", "calorias": 370.0, "proteinas": 7.3, "carboidratos": 80.8, "gorduras": 1.6, "fibras": 5.3, "sodio": 272.0, "calcio": 2.0, "ferro": 0.5, "potassio": 69.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 0},
    "cereais_milho_flocos_sem_sal": {"nome": "Cereais, milho, flocos, sem sal", "calorias": 363.0, "proteinas": 6.9, "carboidratos": 80.4, "gorduras": 1.2, "fibras": 1.8, "sodio": 31.0, "calcio": 2.0, "ferro": 1.7, "potassio": 29.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 0},
    "cereais_mingau_milho_infantil": {"nome": "Cereais, mingau, milho, infantil", "calorias": 394.0, "proteinas": 6.4, "carboidratos": 87.3, "gorduras": 1.1, "fibras": 3.2, "sodio": 399.0, "calcio": 219.0, "ferro": 3.0, "potassio": 82.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 109.4},
    "cereais_mistura_para_vitamina_trigo_cevada_e_aveia": {"nome": "Cereais, mistura para vitamina, trigo, cevada e aveia", "calorias": 381.0, "proteinas": 8.9, "carboidratos": 81.6, "gorduras": 2.1, "fibras": 5.0, "sodio": 1163.0, "calcio": 584.0, "ferro": 12.6, "potassio": 244.0, "zinco": 2.0, "colesterol": 0, "vitamina_c": 13.1},
    "cereal_matinal_milho": {"nome": "Cereal matinal, milho", "calorias": 365.0, "proteinas": 7.2, "carboidratos": 83.8, "gorduras": 1.0, "fibras": 4.1, "sodio": 655.0, "calcio": 143.0, "ferro": 3.1, "potassio": 83.0, "zinco": 7.6, "colesterol": 0, "vitamina_c": 17.3},
    "cereal_matinal_milho_acucar": {"nome": "Cereal matinal, milho, açúcar", "calorias": 377.0, "proteinas": 4.7, "carboidratos": 88.8, "gorduras": 0.7, "fibras": 2.1, "sodio": 405.0, "calcio": 56.0, "ferro": 3.9, "potassio": 52.0, "zinco": 8.5, "colesterol": 0, "vitamina_c": 14.6},
    "creme_de_arroz_po": {"nome": "Creme de arroz, pó", "calorias": 386.0, "proteinas": 7.0, "carboidratos": 83.9, "gorduras": 1.2, "fibras": 1.1, "sodio": 1.0, "calcio": 7.0, "ferro": 0.6, "potassio": 115.0, "zinco": 1.9, "colesterol": 0, "vitamina_c": 0},
    "creme_de_milho_po": {"nome": "Creme de milho, pó", "calorias": 333.0, "proteinas": 4.8, "carboidratos": 86.1, "gorduras": 1.6, "fibras": 3.7, "sodio": 594.0, "calcio": 323.0, "ferro": 4.3, "potassio": 166.0, "zinco": 0.8, "colesterol": 0, "vitamina_c": 96.3},
    "curau_milho_verde": {"nome": "Curau, milho verde", "calorias": 78.0, "proteinas": 2.4, "carboidratos": 13.9, "gorduras": 1.6, "fibras": 0.5, "sodio": 21.0, "calcio": 53.0, "ferro": 0.4, "potassio": 162.0, "zinco": 0.4, "colesterol": 5.0, "vitamina_c": 0},
    "curau_milho_verde_mistura_para": {"nome": "Curau, milho verde, mistura para", "calorias": 402.0, "proteinas": 2.2, "carboidratos": 79.8, "gorduras": 13.4, "fibras": 2.5, "sodio": 223.0, "calcio": 31.0, "ferro": 0.9, "potassio": 55.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 0},
    "farinha_de_arroz_enriquecida": {"nome": "Farinha, de arroz, enriquecida", "calorias": 363.0, "proteinas": 1.3, "carboidratos": 85.5, "gorduras": 0.3, "fibras": 0.6, "sodio": 17.0, "calcio": 1.0, "ferro": 31.4, "potassio": 13.0, "zinco": 8.5, "colesterol": 0, "vitamina_c": 173.6},
    "farinha_de_centeio_integral": {"nome": "Farinha, de centeio, integral", "calorias": 336.0, "proteinas": 12.5, "carboidratos": 73.3, "gorduras": 1.8, "fibras": 15.5, "sodio": 41.0, "calcio": 34.0, "ferro": 4.7, "potassio": 334.0, "zinco": 2.7, "colesterol": 0, "vitamina_c": 0},
    "farinha_de_milho_amarela": {"nome": "Farinha, de milho, amarela", "calorias": 351.0, "proteinas": 7.2, "carboidratos": 79.1, "gorduras": 1.5, "fibras": 5.5, "sodio": 45.0, "calcio": 1.0, "ferro": 2.3, "potassio": 58.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 0},
    "farinha_de_rosca": {"nome": "Farinha, de rosca", "calorias": 371.0, "proteinas": 11.4, "carboidratos": 75.8, "gorduras": 1.5, "fibras": 4.8, "sodio": 333.0, "calcio": 35.0, "ferro": 6.7, "potassio": 212.0, "zinco": 1.7, "colesterol": 0, "vitamina_c": 0},
    "farinha_de_trigo": {"nome": "Farinha, de trigo", "calorias": 360.0, "proteinas": 9.8, "carboidratos": 75.1, "gorduras": 1.4, "fibras": 2.3, "sodio": 1.0, "calcio": 18.0, "ferro": 1.0, "potassio": 151.0, "zinco": 0.8, "colesterol": 0, "vitamina_c": 0},
    "farinha_lactea_de_cereais": {"nome": "Farinha, láctea, de cereais", "calorias": 415.0, "proteinas": 11.9, "carboidratos": 77.8, "gorduras": 5.8, "fibras": 1.9, "sodio": 125.0, "calcio": 196.0, "ferro": 8.7, "potassio": 366.0, "zinco": 1.7, "colesterol": 11.0, "vitamina_c": 24.3},
    "lasanha_massa_fresca_cozida": {"nome": "Lasanha, massa fresca, cozida", "calorias": 164.0, "proteinas": 5.8, "carboidratos": 32.5, "gorduras": 1.2, "fibras": 1.6, "sodio": 207.0, "calcio": 10.0, "ferro": 1.2, "potassio": 54.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 0},
    "lasanha_massa_fresca_crua": {"nome": "Lasanha, massa fresca, crua", "calorias": 220.0, "proteinas": 7.0, "carboidratos": 45.1, "gorduras": 1.3, "fibras": 1.6, "sodio": 667.0, "calcio": 17.0, "ferro": 1.9, "potassio": 137.0, "zinco": 0.8, "colesterol": 0, "vitamina_c": 0},
    "macarrao_instantaneo": {"nome": "Macarrão, instantâneo", "calorias": 436.0, "proteinas": 8.8, "carboidratos": 62.4, "gorduras": 17.2, "fibras": 5.6, "sodio": 1516.0, "calcio": 18.0, "ferro": 0.8, "potassio": 148.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 0},
    "macarrao_trigo_cru": {"nome": "Macarrão, trigo, cru", "calorias": 371.0, "proteinas": 10.0, "carboidratos": 77.9, "gorduras": 1.3, "fibras": 2.9, "sodio": 7.0, "calcio": 17.0, "ferro": 0.9, "potassio": 147.0, "zinco": 0.8, "colesterol": 0, "vitamina_c": 0},
    "macarrao_trigo_cru_com_ovos": {"nome": "Macarrão, trigo, cru, com ovos", "calorias": 371.0, "proteinas": 10.3, "carboidratos": 76.6, "gorduras": 2.0, "fibras": 2.3, "sodio": 15.0, "calcio": 19.0, "ferro": 0.9, "potassio": 134.0, "zinco": 0.8, "colesterol": 18.0, "vitamina_c": 0},
    "milho_amido_cru": {"nome": "Milho, amido, cru", "calorias": 361.0, "proteinas": 0.6, "carboidratos": 87.1, "gorduras": 0, "fibras": 0.7, "sodio": 8.0, "calcio": 1.0, "ferro": 0.1, "potassio": 9.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0},
    "milho_fuba_cru": {"nome": "Milho, fubá, cru", "calorias": 353.0, "proteinas": 7.2, "carboidratos": 78.9, "gorduras": 1.9, "fibras": 4.7, "sodio": 0, "calcio": 3.0, "ferro": 0.9, "potassio": 168.0, "zinco": 1.1, "colesterol": 0, "vitamina_c": 0},
    "milho_verde_cru": {"nome": "Milho, verde, cru", "calorias": 138.0, "proteinas": 6.6, "carboidratos": 28.6, "gorduras": 0.6, "fibras": 3.9, "sodio": 1.0, "calcio": 2.0, "ferro": 0.4, "potassio": 185.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 0},
    "milho_verde_enlatado_drenado": {"nome": "Milho, verde, enlatado, drenado", "calorias": 98.0, "proteinas": 3.2, "carboidratos": 17.1, "gorduras": 2.4, "fibras": 4.6, "sodio": 260.0, "calcio": 2.0, "ferro": 0.6, "potassio": 162.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 1.7},
    "mingau_tradicional_po": {"nome": "Mingau tradicional, pó", "calorias": 373.0, "proteinas": 0.6, "carboidratos": 89.3, "gorduras": 0.4, "fibras": 0.9, "sodio": 15.0, "calcio": 522.0, "ferro": 42.0, "potassio": 0, "zinco": 15.2, "colesterol": 0, "vitamina_c": 0},
    "pamonha_barra_para_cozimento_pre_cozida": {"nome": "Pamonha, barra para cozimento, pré-cozida", "calorias": 171.0, "proteinas": 2.6, "carboidratos": 30.7, "gorduras": 4.8, "fibras": 2.4, "sodio": 132.0, "calcio": 4.0, "ferro": 0.4, "potassio": 125.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 0},
    "pao_aveia_forma": {"nome": "Pão, aveia, forma", "calorias": 343.0, "proteinas": 12.4, "carboidratos": 59.6, "gorduras": 5.7, "fibras": 6.0, "sodio": 606.0, "calcio": 109.0, "ferro": 4.7, "potassio": 210.0, "zinco": 1.7, "colesterol": 0, "vitamina_c": 0},
    "pao_de_soja": {"nome": "Pão, de soja", "calorias": 309.0, "proteinas": 11.3, "carboidratos": 56.5, "gorduras": 3.6, "fibras": 5.7, "sodio": 663.0, "calcio": 90.0, "ferro": 3.3, "potassio": 296.0, "zinco": 1.5, "colesterol": 0, "vitamina_c": 0},
    "pao_gluten_forma": {"nome": "Pão, glúten, forma", "calorias": 253.0, "proteinas": 12.0, "carboidratos": 44.1, "gorduras": 2.7, "fibras": 2.5, "sodio": 22.0, "calcio": 156.0, "ferro": 5.7, "potassio": 65.0, "zinco": 1.3, "colesterol": 0, "vitamina_c": 0},
    "pao_milho_forma": {"nome": "Pão, milho, forma", "calorias": 292.0, "proteinas": 8.3, "carboidratos": 56.4, "gorduras": 3.1, "fibras": 4.3, "sodio": 507.0, "calcio": 78.0, "ferro": 3.0, "potassio": 89.0, "zinco": 0.8, "colesterol": 6.0, "vitamina_c": 0},
    "pao_trigo_forma_integral": {"nome": "Pão, trigo, forma, integral", "calorias": 253.0, "proteinas": 9.4, "carboidratos": 49.9, "gorduras": 3.7, "fibras": 6.9, "sodio": 506.0, "calcio": 132.0, "ferro": 3.0, "potassio": 163.0, "zinco": 1.6, "colesterol": 0, "vitamina_c": 0},
    "pao_trigo_frances": {"nome": "Pão, trigo, francês", "calorias": 300.0, "proteinas": 8.0, "carboidratos": 58.6, "gorduras": 3.1, "fibras": 2.3, "sodio": 648.0, "calcio": 16.0, "ferro": 1.0, "potassio": 142.0, "zinco": 0.8, "colesterol": 0, "vitamina_c": 0},
    "pao_trigo_sovado": {"nome": "Pão, trigo, sovado", "calorias": 311.0, "proteinas": 8.4, "carboidratos": 61.5, "gorduras": 2.8, "fibras": 2.4, "sodio": 431.0, "calcio": 52.0, "ferro": 2.3, "potassio": 91.0, "zinco": 2.7, "colesterol": 17.0, "vitamina_c": 0},
    "pastel_de_carne_cru": {"nome": "Pastel, de carne, cru", "calorias": 289.0, "proteinas": 10.7, "carboidratos": 42.0, "gorduras": 8.8, "fibras": 1.0, "sodio": 1309.0, "calcio": 17.0, "ferro": 2.0, "potassio": 166.0, "zinco": 1.7, "colesterol": 18.0, "vitamina_c": 0},
    "pastel_de_carne_frito": {"nome": "Pastel, de carne, frito", "calorias": 388.0, "proteinas": 10.1, "carboidratos": 43.8, "gorduras": 20.1, "fibras": 1.0, "sodio": 1040.0, "calcio": 13.0, "ferro": 2.5, "potassio": 156.0, "zinco": 1.2, "colesterol": 25.0, "vitamina_c": 0},
    "pastel_de_queijo_cru": {"nome": "Pastel, de queijo, cru", "calorias": 308.0, "proteinas": 9.9, "carboidratos": 45.9, "gorduras": 9.6, "fibras": 1.1, "sodio": 985.0, "calcio": 155.0, "ferro": 1.0, "potassio": 103.0, "zinco": 1.0, "colesterol": 14.0, "vitamina_c": 0},
    "pastel_de_queijo_frito": {"nome": "Pastel, de queijo, frito", "calorias": 422.0, "proteinas": 8.7, "carboidratos": 48.1, "gorduras": 22.7, "fibras": 0.9, "sodio": 821.0, "calcio": 126.0, "ferro": 1.3, "potassio": 124.0, "zinco": 0.8, "colesterol": 15.0, "vitamina_c": 0},
    "pastel_massa_crua": {"nome": "Pastel, massa, crua", "calorias": 310.0, "proteinas": 6.9, "carboidratos": 57.4, "gorduras": 5.5, "fibras": 1.4, "sodio": 1344.0, "calcio": 13.0, "ferro": 1.1, "potassio": 167.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 0},
    "pastel_massa_frita": {"nome": "Pastel, massa, frita", "calorias": 570.0, "proteinas": 6.0, "carboidratos": 49.3, "gorduras": 40.9, "fibras": 1.3, "sodio": 1175.0, "calcio": 11.0, "ferro": 1.4, "potassio": 143.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 0},
    "pipoca_com_oleo_de_soja_sem_sal": {"nome": "Pipoca, com óleo de soja, sem sal", "calorias": 448.0, "proteinas": 9.9, "carboidratos": 70.3, "gorduras": 15.9, "fibras": 14.3, "sodio": 4.0, "calcio": 3.0, "ferro": 1.2, "potassio": 256.0, "zinco": 2.0, "colesterol": 0, "vitamina_c": 0},
    "polenta_pre_cozida": {"nome": "Polenta, pré-cozida", "calorias": 103.0, "proteinas": 2.3, "carboidratos": 23.3, "gorduras": 0.3, "fibras": 2.4, "sodio": 442.0, "calcio": 1.0, "ferro": 0, "potassio": 100.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0},
    "torrada_pao_frances": {"nome": "Torrada, pão francês", "calorias": 377.0, "proteinas": 10.5, "carboidratos": 74.6, "gorduras": 3.3, "fibras": 3.4, "sodio": 829.0, "calcio": 19.0, "ferro": 1.2, "potassio": 189.0, "zinco": 0.9, "colesterol": 0, "vitamina_c": 0},

    # ═══════════════════════════════════════════════════════════════
    # FRUTAS E DERIVADOS
    # ═══════════════════════════════════════════════════════════════
    "abacate_cru": {"nome": "Abacate, cru", "calorias": 96.0, "proteinas": 1.2, "carboidratos": 6.0, "gorduras": 8.4, "fibras": 6.3, "sodio": 0, "calcio": 8.0, "ferro": 0.2, "potassio": 206.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 8.7},
    "abacaxi_cru": {"nome": "Abacaxi, cru", "calorias": 48.0, "proteinas": 0.9, "carboidratos": 12.3, "gorduras": 0.1, "fibras": 1.0, "sodio": 0, "calcio": 22.0, "ferro": 0.3, "potassio": 131.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 34.6},
    "abacaxi_polpa_congelada": {"nome": "Abacaxi, polpa, congelada", "calorias": 31.0, "proteinas": 0.5, "carboidratos": 7.8, "gorduras": 0.1, "fibras": 0.3, "sodio": 1.0, "calcio": 14.0, "ferro": 0.4, "potassio": 107.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 1.2},
    "abiu_cru": {"nome": "Abiu, cru", "calorias": 62.0, "proteinas": 0.8, "carboidratos": 14.9, "gorduras": 0.7, "fibras": 1.7, "sodio": 0, "calcio": 6.0, "ferro": 0.2, "potassio": 128.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 10.3},
    "acai_polpa_com_xarope_de_guarana_e_glucose": {"nome": "Açaí, polpa, com xarope de guaraná e glucose", "calorias": 110.0, "proteinas": 0.7, "carboidratos": 21.5, "gorduras": 3.7, "fibras": 1.7, "sodio": 15.0, "calcio": 22.0, "ferro": 0.3, "potassio": 75.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 10.3},
    "acai_polpa_congelada": {"nome": "Açaí, polpa, congelada", "calorias": 58.0, "proteinas": 0.8, "carboidratos": 6.2, "gorduras": 3.9, "fibras": 2.6, "sodio": 5.0, "calcio": 35.0, "ferro": 0.4, "potassio": 124.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 0},
    "acerola_crua": {"nome": "Acerola, crua", "calorias": 33.0, "proteinas": 0.9, "carboidratos": 8.0, "gorduras": 0.2, "fibras": 1.5, "sodio": 0, "calcio": 13.0, "ferro": 0.2, "potassio": 165.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 941.4},
    "acerola_polpa_congelada": {"nome": "Acerola, polpa, congelada", "calorias": 22.0, "proteinas": 0.6, "carboidratos": 5.5, "gorduras": 0, "fibras": 0.7, "sodio": 1.0, "calcio": 8.0, "ferro": 0.2, "potassio": 112.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 623.2},
    "ameixa_calda_enlatada": {"nome": "Ameixa, calda, enlatada ", "calorias": 183.0, "proteinas": 0.4, "carboidratos": 46.9, "gorduras": 0, "fibras": 0.5, "sodio": 3.0, "calcio": 13.0, "ferro": 2.2, "potassio": 221.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 4.3},
    "ameixa_crua": {"nome": "Ameixa, crua", "calorias": 53.0, "proteinas": 0.8, "carboidratos": 13.9, "gorduras": 0, "fibras": 2.4, "sodio": 0, "calcio": 6.0, "ferro": 0.1, "potassio": 134.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 7.6},
    "ameixa_em_calda_enlatada_drenada": {"nome": "Ameixa, em calda, enlatada, drenada ", "calorias": 177.0, "proteinas": 1.0, "carboidratos": 47.7, "gorduras": 0.3, "fibras": 4.5, "sodio": 3.0, "calcio": 39.0, "ferro": 2.7, "potassio": 263.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 5.2},
    "atemoia_crua": {"nome": "Atemóia, crua", "calorias": 97.0, "proteinas": 1.0, "carboidratos": 25.3, "gorduras": 0.3, "fibras": 2.1, "sodio": 1.0, "calcio": 23.0, "ferro": 0.2, "potassio": 300.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 10.1},
    "banana_da_terra_crua": {"nome": "Banana, da terra, crua", "calorias": 128.0, "proteinas": 1.4, "carboidratos": 33.7, "gorduras": 0.2, "fibras": 1.5, "sodio": 0, "calcio": 4.0, "ferro": 0.3, "potassio": 328.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 15.7},
    "banana_doce_em_barra": {"nome": "Banana, doce em barra", "calorias": 280.0, "proteinas": 2.2, "carboidratos": 75.7, "gorduras": 0.1, "fibras": 3.8, "sodio": 10.0, "calcio": 12.0, "ferro": 0.6, "potassio": 518.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 0},
    "banana_figo_crua": {"nome": "Banana, figo, crua", "calorias": 105.0, "proteinas": 1.1, "carboidratos": 27.8, "gorduras": 0.1, "fibras": 2.8, "sodio": 0, "calcio": 6.0, "ferro": 0.2, "potassio": 387.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 17.5},
    "banana_maca_crua": {"nome": "Banana, maçã, crua", "calorias": 87.0, "proteinas": 1.8, "carboidratos": 22.3, "gorduras": 0.1, "fibras": 2.6, "sodio": 0, "calcio": 3.0, "ferro": 0.2, "potassio": 264.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 10.5},
    "banana_nanica_crua": {"nome": "Banana, nanica, crua", "calorias": 92.0, "proteinas": 1.4, "carboidratos": 23.8, "gorduras": 0.1, "fibras": 1.9, "sodio": 0, "calcio": 3.0, "ferro": 0.3, "potassio": 376.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 5.9},
    "banana_ouro_crua": {"nome": "Banana, ouro, crua", "calorias": 112.0, "proteinas": 1.5, "carboidratos": 29.3, "gorduras": 0.2, "fibras": 2.0, "sodio": 0, "calcio": 3.0, "ferro": 0.3, "potassio": 355.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 7.6},
    "banana_pacova_crua": {"nome": "Banana, pacova, crua", "calorias": 78.0, "proteinas": 1.2, "carboidratos": 20.3, "gorduras": 0.1, "fibras": 2.0, "sodio": 1.0, "calcio": 5.0, "ferro": 0.4, "potassio": 267.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0},
    "banana_prata_crua": {"nome": "Banana, prata, crua", "calorias": 98.0, "proteinas": 1.3, "carboidratos": 26.0, "gorduras": 0.1, "fibras": 2.0, "sodio": 0, "calcio": 8.0, "ferro": 0.4, "potassio": 358.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 21.6},
    "cacau_cru": {"nome": "Cacau, cru", "calorias": 74.0, "proteinas": 1.0, "carboidratos": 19.4, "gorduras": 0.1, "fibras": 2.2, "sodio": 1.0, "calcio": 12.0, "ferro": 0.3, "potassio": 72.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 13.6},
    "caja_manga_cru": {"nome": "Cajá-Manga, cru", "calorias": 46.0, "proteinas": 1.3, "carboidratos": 11.4, "gorduras": 0, "fibras": 2.6, "sodio": 1.0, "calcio": 13.0, "ferro": 0.2, "potassio": 119.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 26.7},
    "caja_polpa_congelada": {"nome": "Cajá, polpa, congelada", "calorias": 26.0, "proteinas": 0.6, "carboidratos": 6.4, "gorduras": 0.2, "fibras": 1.4, "sodio": 7.0, "calcio": 9.0, "ferro": 0.3, "potassio": 148.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0},
    "caju_cru": {"nome": "Caju, cru", "calorias": 43.0, "proteinas": 1.0, "carboidratos": 10.3, "gorduras": 0.3, "fibras": 1.7, "sodio": 3.0, "calcio": 1.0, "ferro": 0.2, "potassio": 124.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 219.3},
    "caju_polpa_congelada": {"nome": "Caju, polpa, congelada", "calorias": 37.0, "proteinas": 0.5, "carboidratos": 9.4, "gorduras": 0.2, "fibras": 0.8, "sodio": 4.0, "calcio": 1.0, "ferro": 0.1, "potassio": 88.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 119.7},
    "caju_suco_concentrado_envasado": {"nome": "Caju, suco concentrado, envasado", "calorias": 45.0, "proteinas": 0.4, "carboidratos": 10.7, "gorduras": 0.2, "fibras": 0.6, "sodio": 45.0, "calcio": 1.0, "ferro": 0.1, "potassio": 107.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 138.7},
    "caqui_chocolate_cru": {"nome": "Caqui, chocolate, cru", "calorias": 71.0, "proteinas": 0.4, "carboidratos": 19.3, "gorduras": 0.1, "fibras": 6.5, "sodio": 2.0, "calcio": 18.0, "ferro": 0.1, "potassio": 164.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 29.6},
    "carambola_crua": {"nome": "Carambola, crua", "calorias": 46.0, "proteinas": 0.9, "carboidratos": 11.5, "gorduras": 0.2, "fibras": 2.0, "sodio": 4.0, "calcio": 5.0, "ferro": 0.2, "potassio": 133.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 60.9},
    "ciriguela_crua": {"nome": "Ciriguela, crua", "calorias": 76.0, "proteinas": 1.4, "carboidratos": 18.9, "gorduras": 0.4, "fibras": 3.9, "sodio": 2.0, "calcio": 27.0, "ferro": 0.4, "potassio": 248.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 27.0},
    "cupuacu_cru": {"nome": "Cupuaçu, cru", "calorias": 49.0, "proteinas": 1.2, "carboidratos": 10.4, "gorduras": 1.0, "fibras": 3.1, "sodio": 3.0, "calcio": 13.0, "ferro": 0.5, "potassio": 331.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 24.5},
    "cupuacu_polpa_congelada": {"nome": "Cupuaçu, polpa, congelada", "calorias": 49.0, "proteinas": 0.8, "carboidratos": 11.4, "gorduras": 0.6, "fibras": 1.6, "sodio": 1.0, "calcio": 5.0, "ferro": 0.3, "potassio": 291.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 10.5},
    "figo_cru": {"nome": "Figo, cru", "calorias": 41.0, "proteinas": 1.0, "carboidratos": 10.2, "gorduras": 0.2, "fibras": 1.8, "sodio": 0, "calcio": 27.0, "ferro": 0.2, "potassio": 174.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0.8},
    "figo_enlatado_em_calda": {"nome": "Figo, enlatado, em calda", "calorias": 184.0, "proteinas": 0.6, "carboidratos": 50.3, "gorduras": 0.2, "fibras": 2.0, "sodio": 7.0, "calcio": 33.0, "ferro": 0.5, "potassio": 39.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 5.2},
    "fruta_pao_crua": {"nome": "Fruta-pão, crua", "calorias": 67.0, "proteinas": 1.1, "carboidratos": 17.2, "gorduras": 0.2, "fibras": 5.5, "sodio": 1.0, "calcio": 34.0, "ferro": 0.2, "potassio": 188.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 9.9},
    "goiaba_branca_com_casca_crua": {"nome": "Goiaba, branca, com casca, crua", "calorias": 52.0, "proteinas": 0.9, "carboidratos": 12.4, "gorduras": 0.5, "fibras": 6.3, "sodio": 0, "calcio": 5.0, "ferro": 0.2, "potassio": 220.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 99.2},
    "goiaba_doce_cascao": {"nome": "Goiaba, doce, cascão", "calorias": 286.0, "proteinas": 0.4, "carboidratos": 78.7, "gorduras": 0.1, "fibras": 4.4, "sodio": 11.0, "calcio": 15.0, "ferro": 0.4, "potassio": 251.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 34.3},
    "goiaba_doce_em_pasta": {"nome": "Goiaba, doce em pasta", "calorias": 269.0, "proteinas": 0.6, "carboidratos": 74.1, "gorduras": 0.0, "fibras": 3.7, "sodio": 4.0, "calcio": 10.0, "ferro": 0.4, "potassio": 165.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 23.1},
    "goiaba_vermelha_com_casca_crua": {"nome": "Goiaba, vermelha, com casca, crua", "calorias": 54.0, "proteinas": 1.1, "carboidratos": 13.0, "gorduras": 0.4, "fibras": 6.2, "sodio": 0, "calcio": 4.0, "ferro": 0.2, "potassio": 198.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 80.6},
    "graviola_crua": {"nome": "Graviola, crua", "calorias": 62.0, "proteinas": 0.8, "carboidratos": 15.8, "gorduras": 0.2, "fibras": 1.9, "sodio": 4.0, "calcio": 40.0, "ferro": 0.2, "potassio": 250.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 19.1},
    "graviola_polpa_congelada": {"nome": "Graviola, polpa, congelada", "calorias": 38.0, "proteinas": 0.6, "carboidratos": 9.8, "gorduras": 0.1, "fibras": 1.2, "sodio": 3.0, "calcio": 6.0, "ferro": 0.1, "potassio": 170.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 10.5},
    "jabuticaba_crua": {"nome": "Jabuticaba, crua", "calorias": 58.0, "proteinas": 0.6, "carboidratos": 15.3, "gorduras": 0.1, "fibras": 2.3, "sodio": 0, "calcio": 8.0, "ferro": 0.1, "potassio": 130.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 16.2},
    "jaca_crua": {"nome": "Jaca, crua", "calorias": 88.0, "proteinas": 1.4, "carboidratos": 22.5, "gorduras": 0.3, "fibras": 2.4, "sodio": 2.0, "calcio": 11.0, "ferro": 0.4, "potassio": 234.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 14.8},
    "jambo_cru": {"nome": "Jambo, cru", "calorias": 27.0, "proteinas": 0.9, "carboidratos": 6.5, "gorduras": 0.1, "fibras": 5.1, "sodio": 22.0, "calcio": 14.0, "ferro": 0.1, "potassio": 135.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 3.8},
    "jamelao_cru": {"nome": "Jamelão, cru", "calorias": 41.0, "proteinas": 0.5, "carboidratos": 10.6, "gorduras": 0.1, "fibras": 1.8, "sodio": 1.0, "calcio": 3.0, "ferro": 0.0, "potassio": 394.0, "zinco": 0.0, "colesterol": 0, "vitamina_c": 27.1},
    "kiwi_cru": {"nome": "Kiwi, cru", "calorias": 51.0, "proteinas": 1.3, "carboidratos": 11.5, "gorduras": 0.6, "fibras": 2.7, "sodio": 0, "calcio": 24.0, "ferro": 0.3, "potassio": 269.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 70.8},
    "laranja_baia_crua": {"nome": "Laranja, baía, crua", "calorias": 45.0, "proteinas": 1.0, "carboidratos": 11.5, "gorduras": 0.1, "fibras": 1.1, "sodio": 0, "calcio": 35.0, "ferro": 0.1, "potassio": 174.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 56.9},
    "laranja_baia_suco": {"nome": "Laranja, baía, suco", "calorias": 37.0, "proteinas": 0.7, "carboidratos": 8.7, "gorduras": 0, "fibras": 0, "sodio": 0, "calcio": 6.0, "ferro": 0.1, "potassio": 173.0, "zinco": 0, "colesterol": 0, "vitamina_c": 94.5},
    "laranja_da_terra_crua": {"nome": "Laranja, da terra, crua", "calorias": 51.0, "proteinas": 1.1, "carboidratos": 12.9, "gorduras": 0.2, "fibras": 4.0, "sodio": 1.0, "calcio": 51.0, "ferro": 0.1, "potassio": 173.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 34.7},
    "laranja_da_terra_suco": {"nome": "Laranja, da terra, suco", "calorias": 41.0, "proteinas": 0.7, "carboidratos": 9.6, "gorduras": 0.1, "fibras": 1.0, "sodio": 0, "calcio": 13.0, "ferro": 0.1, "potassio": 145.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 44.3},
    "laranja_lima_crua": {"nome": "Laranja, lima, crua", "calorias": 46.0, "proteinas": 1.1, "carboidratos": 11.5, "gorduras": 0.1, "fibras": 1.8, "sodio": 1.0, "calcio": 31.0, "ferro": 0.1, "potassio": 130.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 43.5},
    "laranja_lima_suco": {"nome": "Laranja, lima, suco", "calorias": 39.0, "proteinas": 0.7, "carboidratos": 9.2, "gorduras": 0.1, "fibras": 0.4, "sodio": 0, "calcio": 8.0, "ferro": 0, "potassio": 129.0, "zinco": 0.0, "colesterol": 0, "vitamina_c": 41.3},
    "laranja_pera_crua": {"nome": "Laranja, pêra, crua", "calorias": 37.0, "proteinas": 1.0, "carboidratos": 8.9, "gorduras": 0.1, "fibras": 0.8, "sodio": 0, "calcio": 22.0, "ferro": 0.1, "potassio": 163.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 53.7},
    "laranja_pera_suco": {"nome": "Laranja, pêra, suco", "calorias": 33.0, "proteinas": 0.7, "carboidratos": 7.6, "gorduras": 0.1, "fibras": 0, "sodio": 0, "calcio": 7.0, "ferro": 0, "potassio": 149.0, "zinco": 0, "colesterol": 0, "vitamina_c": 73.3},
    "laranja_valencia_crua": {"nome": "Laranja, valência, crua", "calorias": 46.0, "proteinas": 0.8, "carboidratos": 11.7, "gorduras": 0.2, "fibras": 1.7, "sodio": 1.0, "calcio": 34.0, "ferro": 0.1, "potassio": 158.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 47.8},
    "laranja_valencia_suco": {"nome": "Laranja, valência, suco", "calorias": 36.0, "proteinas": 0.5, "carboidratos": 8.6, "gorduras": 0.1, "fibras": 0.4, "sodio": 0, "calcio": 9.0, "ferro": 0, "potassio": 143.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "limao_cravo_suco": {"nome": "Limão, cravo, suco", "calorias": 14.0, "proteinas": 0.3, "carboidratos": 5.2, "gorduras": 0, "fibras": 0, "sodio": 0, "calcio": 10.0, "ferro": 0.1, "potassio": 120.0, "zinco": 0, "colesterol": 0, "vitamina_c": 32.8},
    "limao_galego_suco": {"nome": "Limão, galego, suco", "calorias": 22.0, "proteinas": 0.6, "carboidratos": 7.3, "gorduras": 0.1, "fibras": 0, "sodio": 0, "calcio": 5.0, "ferro": 0.1, "potassio": 113.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 34.5},
    "limao_tahiti_cru": {"nome": "Limão, tahiti, cru", "calorias": 32.0, "proteinas": 0.9, "carboidratos": 11.1, "gorduras": 0.1, "fibras": 1.2, "sodio": 1.0, "calcio": 51.0, "ferro": 0.2, "potassio": 128.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 38.2},
    "maca_argentina_com_casca_crua": {"nome": "Maçã, Argentina, com casca, crua", "calorias": 63.0, "proteinas": 0.2, "carboidratos": 16.6, "gorduras": 0.2, "fibras": 2.0, "sodio": 1.0, "calcio": 3.0, "ferro": 0.1, "potassio": 117.0, "zinco": 0, "colesterol": 0, "vitamina_c": 1.5},
    "maca_fuji_com_casca_crua": {"nome": "Maçã, Fuji, com casca, crua", "calorias": 56.0, "proteinas": 0.3, "carboidratos": 15.2, "gorduras": 0, "fibras": 1.3, "sodio": 0, "calcio": 2.0, "ferro": 0.1, "potassio": 75.0, "zinco": 0, "colesterol": 0, "vitamina_c": 2.4},
    "macauba_crua": {"nome": "Macaúba, crua", "calorias": 404.0, "proteinas": 2.1, "carboidratos": 13.9, "gorduras": 40.7, "fibras": 13.4, "sodio": 1.0, "calcio": 67.0, "ferro": 0.8, "potassio": 306.0, "zinco": 0.7, "colesterol": 0, "vitamina_c": 13.4},
    "mamao_doce_em_calda_drenado": {"nome": " Mamão, doce em calda, drenado", "calorias": 196.0, "proteinas": 0.2, "carboidratos": 54.0, "gorduras": 0.1, "fibras": 1.3, "sodio": 3.0, "calcio": 20.0, "ferro": 0.1, "potassio": 68.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 3.9},
    "mamao_formosa_cru": {"nome": "Mamão, Formosa, cru", "calorias": 45.0, "proteinas": 0.8, "carboidratos": 11.6, "gorduras": 0.1, "fibras": 1.8, "sodio": 3.0, "calcio": 25.0, "ferro": 0.2, "potassio": 222.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 78.5},
    "mamao_papaia_cru": {"nome": "Mamão, Papaia, cru", "calorias": 40.0, "proteinas": 0.5, "carboidratos": 10.4, "gorduras": 0.1, "fibras": 1.0, "sodio": 2.0, "calcio": 22.0, "ferro": 0.2, "potassio": 126.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 82.2},
    "mamao_verde_doce_em_calda_drenado": {"nome": " Mamão verde, doce em calda, drenado", "calorias": 209.0, "proteinas": 0.3, "carboidratos": 57.6, "gorduras": 0.1, "fibras": 1.2, "sodio": 5.0, "calcio": 12.0, "ferro": 0.2, "potassio": 9.0, "zinco": 0.0, "colesterol": 0, "vitamina_c": 0},
    "manga_haden_crua": {"nome": "Manga, Haden, crua", "calorias": 64.0, "proteinas": 0.4, "carboidratos": 16.7, "gorduras": 0.3, "fibras": 1.6, "sodio": 1.0, "calcio": 12.0, "ferro": 0.1, "potassio": 148.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 17.4},
    "manga_palmer_crua": {"nome": "Manga, Palmer, crua", "calorias": 72.0, "proteinas": 0.4, "carboidratos": 19.4, "gorduras": 0.2, "fibras": 1.6, "sodio": 2.0, "calcio": 12.0, "ferro": 0.1, "potassio": 157.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 65.5},
    "manga_polpa_congelada": {"nome": "Manga, polpa, congelada", "calorias": 48.0, "proteinas": 0.4, "carboidratos": 12.5, "gorduras": 0.2, "fibras": 1.1, "sodio": 7.0, "calcio": 7.0, "ferro": 0.1, "potassio": 131.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 24.9},
    "manga_tommy_atkins_crua": {"nome": "Manga, Tommy Atkins, crua", "calorias": 51.0, "proteinas": 0.9, "carboidratos": 12.8, "gorduras": 0.2, "fibras": 2.1, "sodio": 0, "calcio": 8.0, "ferro": 0.1, "potassio": 138.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 7.9},
    "maracuja_cru": {"nome": "Maracujá, cru", "calorias": 68.0, "proteinas": 2.0, "carboidratos": 12.3, "gorduras": 2.1, "fibras": 1.1, "sodio": 2.0, "calcio": 5.0, "ferro": 0.6, "potassio": 338.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 19.8},
    "maracuja_polpa_congelada": {"nome": "Maracujá, polpa, congelada", "calorias": 39.0, "proteinas": 0.8, "carboidratos": 9.6, "gorduras": 0.2, "fibras": 0.5, "sodio": 8.0, "calcio": 5.0, "ferro": 0.3, "potassio": 228.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 7.3},
    "maracuja_suco_concentrado_envasado": {"nome": "Maracujá, suco concentrado, envasado", "calorias": 42.0, "proteinas": 0.8, "carboidratos": 9.6, "gorduras": 0.2, "fibras": 0.4, "sodio": 22.0, "calcio": 4.0, "ferro": 0.3, "potassio": 201.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 13.7},
    "melancia_crua": {"nome": "Melancia, crua", "calorias": 33.0, "proteinas": 0.9, "carboidratos": 8.1, "gorduras": 0, "fibras": 0.1, "sodio": 0, "calcio": 8.0, "ferro": 0.2, "potassio": 104.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 6.1},
    "melao_cru": {"nome": "Melão, cru", "calorias": 29.0, "proteinas": 0.7, "carboidratos": 7.5, "gorduras": 0, "fibras": 0.3, "sodio": 11.0, "calcio": 3.0, "ferro": 0.2, "potassio": 216.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 8.7},
    "mexerica_murcote_crua": {"nome": "Mexerica, Murcote, crua", "calorias": 58.0, "proteinas": 0.9, "carboidratos": 14.9, "gorduras": 0.1, "fibras": 3.1, "sodio": 1.0, "calcio": 33.0, "ferro": 0.1, "potassio": 159.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 21.8},
    "mexerica_rio_crua": {"nome": "Mexerica, Rio, crua", "calorias": 37.0, "proteinas": 0.7, "carboidratos": 9.3, "gorduras": 0.1, "fibras": 2.7, "sodio": 2.0, "calcio": 17.0, "ferro": 0.1, "potassio": 125.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 112.0},
    "morango_cru": {"nome": "Morango, cru", "calorias": 30.0, "proteinas": 0.9, "carboidratos": 6.8, "gorduras": 0.3, "fibras": 1.7, "sodio": 0, "calcio": 11.0, "ferro": 0.3, "potassio": 184.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 63.6},
    "nespera_crua": {"nome": "Nêspera, crua", "calorias": 43.0, "proteinas": 0.3, "carboidratos": 11.5, "gorduras": 0, "fibras": 3.0, "sodio": 0, "calcio": 20.0, "ferro": 0.1, "potassio": 113.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 3.2},
    "pequi_cru": {"nome": "Pequi, cru", "calorias": 205.0, "proteinas": 2.3, "carboidratos": 13.0, "gorduras": 18.0, "fibras": 19.0, "sodio": 0, "calcio": 32.0, "ferro": 0.3, "potassio": 298.0, "zinco": 1.0, "colesterol": 0, "vitamina_c": 8.3},
    "pera_park_crua": {"nome": "Pêra, Park, crua", "calorias": 61.0, "proteinas": 0.2, "carboidratos": 16.1, "gorduras": 0.2, "fibras": 3.0, "sodio": 1.0, "calcio": 9.0, "ferro": 0.3, "potassio": 102.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 2.4},
    "pera_williams_crua": {"nome": "Pêra, Williams, crua", "calorias": 53.0, "proteinas": 0.6, "carboidratos": 14.0, "gorduras": 0.1, "fibras": 3.0, "sodio": 0, "calcio": 8.0, "ferro": 0.1, "potassio": 116.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 2.8},
    "pessego_aurora_cru": {"nome": "Pêssego, Aurora, cru", "calorias": 36.0, "proteinas": 0.8, "carboidratos": 9.3, "gorduras": 0, "fibras": 1.4, "sodio": 0, "calcio": 3.0, "ferro": 0.2, "potassio": 124.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 3.3},
    "pessego_enlatado_em_calda": {"nome": "Pêssego, enlatado, em calda", "calorias": 63.0, "proteinas": 0.7, "carboidratos": 16.9, "gorduras": 0, "fibras": 1.0, "sodio": 3.0, "calcio": 4.0, "ferro": 0.6, "potassio": 95.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0},
    "pinha_crua": {"nome": "Pinha, crua", "calorias": 88.0, "proteinas": 1.5, "carboidratos": 22.4, "gorduras": 0.3, "fibras": 3.4, "sodio": 1.0, "calcio": 21.0, "ferro": 0.2, "potassio": 283.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 35.9},
    "pitanga_crua": {"nome": "Pitanga, crua", "calorias": 41.0, "proteinas": 0.9, "carboidratos": 10.2, "gorduras": 0.2, "fibras": 3.2, "sodio": 2.0, "calcio": 18.0, "ferro": 0.4, "potassio": 113.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 24.9},
    "pitanga_polpa_congelada": {"nome": "Pitanga, polpa, congelada", "calorias": 19.0, "proteinas": 0.3, "carboidratos": 4.8, "gorduras": 0.1, "fibras": 0.7, "sodio": 5.0, "calcio": 8.0, "ferro": 0.4, "potassio": 87.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0},
    "roma_crua": {"nome": "Romã, crua", "calorias": 56.0, "proteinas": 0.4, "carboidratos": 15.1, "gorduras": 0, "fibras": 0.4, "sodio": 1.0, "calcio": 5.0, "ferro": 0.3, "potassio": 485.0, "zinco": 0.7, "colesterol": 0, "vitamina_c": 8.1},
    "tamarindo_cru": {"nome": "Tamarindo, cru", "calorias": 276.0, "proteinas": 3.2, "carboidratos": 72.5, "gorduras": 0.5, "fibras": 6.4, "sodio": 0.0, "calcio": 37.0, "ferro": 0.6, "potassio": 723.0, "zinco": 0.7, "colesterol": 0, "vitamina_c": 7.2},
    "tangerina_ponca_crua": {"nome": "Tangerina, Poncã, crua", "calorias": 38.0, "proteinas": 0.8, "carboidratos": 9.6, "gorduras": 0.1, "fibras": 0.9, "sodio": 0, "calcio": 13.0, "ferro": 0.1, "potassio": 131.0, "zinco": 0, "colesterol": 0, "vitamina_c": 48.8},
    "tangerina_ponca_suco": {"nome": "Tangerina, Poncã, suco", "calorias": 36.0, "proteinas": 0.5, "carboidratos": 8.8, "gorduras": 0, "fibras": 0, "sodio": 0, "calcio": 4.0, "ferro": 0, "potassio": 119.0, "zinco": 0, "colesterol": 0, "vitamina_c": 41.8},
    "tucuma_cru": {"nome": "Tucumã, cru", "calorias": 262.0, "proteinas": 2.1, "carboidratos": 26.5, "gorduras": 19.1, "fibras": 12.7, "sodio": 4.0, "calcio": 46.0, "ferro": 0.6, "potassio": 401.0, "zinco": 0.9, "colesterol": 0, "vitamina_c": 18.0},
    "umbu_cru": {"nome": "Umbu, cru", "calorias": 37.0, "proteinas": 0.8, "carboidratos": 9.4, "gorduras": 0, "fibras": 2.0, "sodio": 0, "calcio": 12.0, "ferro": 0.1, "potassio": 152.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 24.1},
    "umbu_polpa_congelada": {"nome": "Umbu, polpa, congelada", "calorias": 34.0, "proteinas": 0.5, "carboidratos": 8.8, "gorduras": 0.1, "fibras": 1.3, "sodio": 6.0, "calcio": 11.0, "ferro": 0.2, "potassio": 154.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 4.0},
    "uva_italia_crua": {"nome": "Uva, Itália, crua", "calorias": 53.0, "proteinas": 0.7, "carboidratos": 13.6, "gorduras": 0.2, "fibras": 0.9, "sodio": 0, "calcio": 7.0, "ferro": 0.1, "potassio": 162.0, "zinco": 0, "colesterol": 0, "vitamina_c": 3.3},
    "uva_rubi_crua": {"nome": "Uva, Rubi, crua", "calorias": 49.0, "proteinas": 0.6, "carboidratos": 12.7, "gorduras": 0.2, "fibras": 0.9, "sodio": 8.0, "calcio": 8.0, "ferro": 0.2, "potassio": 159.0, "zinco": 0, "colesterol": 0, "vitamina_c": 1.9},
    "uva_suco_concentrado_envasado": {"nome": "Uva, suco concentrado, envasado", "calorias": 58.0, "proteinas": 0, "carboidratos": 14.7, "gorduras": 0, "fibras": 0.2, "sodio": 10.0, "calcio": 9.0, "ferro": 0.1, "potassio": 54.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 21.0},

    # ═══════════════════════════════════════════════════════════════
    # GORDURAS E ÓLEOS
    # ═══════════════════════════════════════════════════════════════
    "azeite_de_dende": {"nome": "Azeite, de dendê", "calorias": 884.0, "proteinas": 0, "carboidratos": 0, "gorduras": 100.0, "fibras": 0, "sodio": 0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "azeite_de_oliva_extra_virgem": {"nome": "Azeite, de oliva, extra virgem", "calorias": 884.0, "proteinas": 0, "carboidratos": 0, "gorduras": 100.0, "fibras": 0, "sodio": 0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "manteiga_com_sal": {"nome": "Manteiga, com sal", "calorias": 726.0, "proteinas": 0.4, "carboidratos": 0.1, "gorduras": 82.4, "fibras": 0, "sodio": 579.0, "calcio": 9.0, "ferro": 0.2, "potassio": 15.0, "zinco": 0, "colesterol": 201.0, "vitamina_c": 0},
    "manteiga_sem_sal": {"nome": "Manteiga, sem sal", "calorias": 758.0, "proteinas": 0.4, "carboidratos": 0.0, "gorduras": 86.0, "fibras": 0, "sodio": 4.0, "calcio": 4.0, "ferro": 0, "potassio": 5.0, "zinco": 0, "colesterol": 214.0, "vitamina_c": 0},
    "margarina_com_oleo_hidrogenado_com_sal_65_de_lipideos": {"nome": "Margarina, com óleo hidrogenado, com sal (65% de lipídeos)", "calorias": 596.0, "proteinas": 0, "carboidratos": 0.0, "gorduras": 67.4, "fibras": 0, "sodio": 894.0, "calcio": 6.0, "ferro": 0.1, "potassio": 21.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "margarina_com_oleo_hidrogenado_sem_sal_80_de_lipideos": {"nome": "Margarina, com óleo hidrogenado, sem sal (80% de lipídeos)", "calorias": 723.0, "proteinas": 0, "carboidratos": 0.0, "gorduras": 81.7, "fibras": 0, "sodio": 78.0, "calcio": 3.0, "ferro": 0.1, "potassio": 2.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "margarina_com_oleo_interesterificado_com_sal_65_de_lipideos": {"nome": "Margarina, com óleo interesterificado, com sal (65%de lipídeos)", "calorias": 594.0, "proteinas": 0, "carboidratos": 0.0, "gorduras": 67.2, "fibras": 0, "sodio": 561.0, "calcio": 5.0, "ferro": 0, "potassio": 15.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "margarina_com_oleo_interesterificado_sem_sal_65_de_lipideos": {"nome": "Margarina, com óleo interesterificado, sem sal (65% de lipídeos)", "calorias": 593.0, "proteinas": 0, "carboidratos": 0.0, "gorduras": 67.1, "fibras": 0, "sodio": 33.0, "calcio": 5.0, "ferro": 0.1, "potassio": 5.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "oleo_de_babacu": {"nome": "Óleo, de babaçu", "calorias": 884.0, "proteinas": 0, "carboidratos": 0, "gorduras": 100.0, "fibras": 0, "sodio": 0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "oleo_de_canola": {"nome": "Óleo, de canola", "calorias": 884.0, "proteinas": 0, "carboidratos": 0, "gorduras": 100.0, "fibras": 0, "sodio": 0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "oleo_de_girassol": {"nome": "Óleo, de girassol", "calorias": 884.0, "proteinas": 0, "carboidratos": 0, "gorduras": 100.0, "fibras": 0, "sodio": 0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "oleo_de_milho": {"nome": "Óleo, de milho", "calorias": 884.0, "proteinas": 0, "carboidratos": 0, "gorduras": 100.0, "fibras": 0, "sodio": 0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "oleo_de_pequi": {"nome": "Óleo, de pequi", "calorias": 884.0, "proteinas": 0, "carboidratos": 0, "gorduras": 100.0, "fibras": 0, "sodio": 0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "oleo_de_soja": {"nome": "Óleo, de soja", "calorias": 884.0, "proteinas": 0, "carboidratos": 0, "gorduras": 100.0, "fibras": 0, "sodio": 0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},

    # ═══════════════════════════════════════════════════════════════
    # LEGUMINOSAS E DERIVADOS
    # ═══════════════════════════════════════════════════════════════
    "amendoim_grao_cru": {"nome": "Amendoim, grão, cru", "calorias": 544.0, "proteinas": 27.2, "carboidratos": 20.3, "gorduras": 43.9, "fibras": 8.0, "sodio": 0, "calcio": 0, "ferro": 2.5, "potassio": 580.0, "zinco": 3.2, "colesterol": 0, "vitamina_c": 0},
    "amendoim_torrado_salgado": {"nome": "Amendoim, torrado, salgado", "calorias": 606.0, "proteinas": 22.5, "carboidratos": 18.7, "gorduras": 54.0, "fibras": 7.8, "sodio": 376.0, "calcio": 39.0, "ferro": 1.3, "potassio": 496.0, "zinco": 2.1, "colesterol": 0, "vitamina_c": 0},
    "ervilha_em_vagem": {"nome": "Ervilha, em vagem", "calorias": 88.0, "proteinas": 7.5, "carboidratos": 14.2, "gorduras": 0.5, "fibras": 9.7, "sodio": 0, "calcio": 24.0, "ferro": 1.4, "potassio": 311.0, "zinco": 1.2, "colesterol": 0, "vitamina_c": 12.4},
    "ervilha_enlatada_drenada": {"nome": "Ervilha, enlatada, drenada", "calorias": 74.0, "proteinas": 4.6, "carboidratos": 13.4, "gorduras": 0.4, "fibras": 5.1, "sodio": 372.0, "calcio": 22.0, "ferro": 1.4, "potassio": 147.0, "zinco": 0.9, "colesterol": 0, "vitamina_c": 0},
    "feijao_carioca_cozido": {"nome": "Feijão, carioca, cozido", "calorias": 76.0, "proteinas": 4.8, "carboidratos": 13.6, "gorduras": 0.5, "fibras": 8.5, "sodio": 2.0, "calcio": 27.0, "ferro": 1.3, "potassio": 255.0, "zinco": 0.7, "colesterol": 0, "vitamina_c": 0},
    "feijao_carioca_cru": {"nome": "Feijão, carioca, cru", "calorias": 329.0, "proteinas": 20.0, "carboidratos": 61.2, "gorduras": 1.3, "fibras": 18.4, "sodio": 0, "calcio": 123.0, "ferro": 8.0, "potassio": 1352.0, "zinco": 2.9, "colesterol": 0, "vitamina_c": 0},
    "feijao_fradinho_cozido": {"nome": "Feijão, fradinho, cozido", "calorias": 78.0, "proteinas": 5.1, "carboidratos": 13.5, "gorduras": 0.6, "fibras": 7.5, "sodio": 1.0, "calcio": 17.0, "ferro": 1.1, "potassio": 253.0, "zinco": 1.1, "colesterol": 0, "vitamina_c": 0},
    "feijao_fradinho_cru": {"nome": "Feijão, fradinho, cru", "calorias": 339.0, "proteinas": 20.2, "carboidratos": 61.2, "gorduras": 2.4, "fibras": 23.6, "sodio": 10.0, "calcio": 78.0, "ferro": 5.1, "potassio": 1083.0, "zinco": 3.9, "colesterol": 0, "vitamina_c": 0},
    "feijao_jalo_cozido": {"nome": "Feijão, jalo, cozido", "calorias": 93.0, "proteinas": 6.1, "carboidratos": 16.5, "gorduras": 0.5, "fibras": 13.9, "sodio": 1.0, "calcio": 29.0, "ferro": 1.9, "potassio": 348.0, "zinco": 1.0, "colesterol": 0, "vitamina_c": 0},
    "feijao_jalo_cru": {"nome": "Feijão, jalo, cru", "calorias": 328.0, "proteinas": 20.1, "carboidratos": 61.5, "gorduras": 0.9, "fibras": 30.3, "sodio": 25.0, "calcio": 98.0, "ferro": 7.0, "potassio": 1276.0, "zinco": 3.0, "colesterol": 0, "vitamina_c": 0},
    "feijao_preto_cozido": {"nome": "Feijão, preto, cozido", "calorias": 77.0, "proteinas": 4.5, "carboidratos": 14.0, "gorduras": 0.5, "fibras": 8.4, "sodio": 2.0, "calcio": 29.0, "ferro": 1.5, "potassio": 256.0, "zinco": 0.7, "colesterol": 0, "vitamina_c": 0},
    "feijao_preto_cru": {"nome": "Feijão, preto, cru", "calorias": 324.0, "proteinas": 21.3, "carboidratos": 58.8, "gorduras": 1.2, "fibras": 21.8, "sodio": 0, "calcio": 111.0, "ferro": 6.5, "potassio": 1416.0, "zinco": 2.9, "colesterol": 0, "vitamina_c": 0},
    "feijao_rajado_cozido": {"nome": "Feijão, rajado, cozido", "calorias": 85.0, "proteinas": 5.5, "carboidratos": 15.3, "gorduras": 0.4, "fibras": 9.3, "sodio": 1.0, "calcio": 29.0, "ferro": 1.4, "potassio": 315.0, "zinco": 0.9, "colesterol": 0, "vitamina_c": 0},
    "feijao_rajado_cru": {"nome": "Feijão, rajado, cru", "calorias": 326.0, "proteinas": 17.3, "carboidratos": 62.9, "gorduras": 1.2, "fibras": 24.0, "sodio": 14.0, "calcio": 111.0, "ferro": 18.6, "potassio": 1135.0, "zinco": 2.6, "colesterol": 0, "vitamina_c": 0},
    "feijao_rosinha_cozido": {"nome": "Feijão, rosinha, cozido", "calorias": 68.0, "proteinas": 4.5, "carboidratos": 11.8, "gorduras": 0.5, "fibras": 4.8, "sodio": 2.0, "calcio": 19.0, "ferro": 1.2, "potassio": 241.0, "zinco": 1.3, "colesterol": 0, "vitamina_c": 0},
    "feijao_rosinha_cru": {"nome": "Feijão, rosinha, cru", "calorias": 337.0, "proteinas": 20.9, "carboidratos": 62.2, "gorduras": 1.3, "fibras": 20.6, "sodio": 24.0, "calcio": 68.0, "ferro": 5.3, "potassio": 1109.0, "zinco": 4.0, "colesterol": 0, "vitamina_c": 0},
    "feijao_roxo_cozido": {"nome": "Feijão, roxo, cozido", "calorias": 77.0, "proteinas": 5.7, "carboidratos": 12.9, "gorduras": 0.5, "fibras": 11.5, "sodio": 1.0, "calcio": 23.0, "ferro": 1.4, "potassio": 268.0, "zinco": 1.0, "colesterol": 0, "vitamina_c": 0},
    "feijao_roxo_cru": {"nome": "Feijão, roxo, cru", "calorias": 331.0, "proteinas": 22.2, "carboidratos": 60.0, "gorduras": 1.2, "fibras": 33.8, "sodio": 10.0, "calcio": 120.0, "ferro": 6.9, "potassio": 1221.0, "zinco": 3.3, "colesterol": 0, "vitamina_c": 0},
    "grao_de_bico_cru": {"nome": "Grão-de-bico, cru", "calorias": 355.0, "proteinas": 21.2, "carboidratos": 57.9, "gorduras": 5.4, "fibras": 12.4, "sodio": 5.0, "calcio": 114.0, "ferro": 5.4, "potassio": 1116.0, "zinco": 3.2, "colesterol": 0, "vitamina_c": 0},
    "guandu_cru": {"nome": "Guandu, cru", "calorias": 344.0, "proteinas": 19.0, "carboidratos": 64.0, "gorduras": 2.1, "fibras": 21.3, "sodio": 2.0, "calcio": 129.0, "ferro": 1.9, "potassio": 1215.0, "zinco": 2.0, "colesterol": 0, "vitamina_c": 1.5},
    "lentilha_cozida": {"nome": "Lentilha, cozida", "calorias": 93.0, "proteinas": 6.3, "carboidratos": 16.3, "gorduras": 0.5, "fibras": 7.9, "sodio": 1.0, "calcio": 16.0, "ferro": 1.5, "potassio": 220.0, "zinco": 1.1, "colesterol": 0, "vitamina_c": 0},
    "lentilha_crua": {"nome": "Lentilha, crua", "calorias": 339.0, "proteinas": 23.2, "carboidratos": 62.0, "gorduras": 0.8, "fibras": 16.9, "sodio": 0, "calcio": 54.0, "ferro": 7.0, "potassio": 887.0, "zinco": 3.5, "colesterol": 0, "vitamina_c": 0},
    "pacoca_amendoim": {"nome": "Paçoca, amendoim", "calorias": 487.0, "proteinas": 16.0, "carboidratos": 52.4, "gorduras": 26.1, "fibras": 7.3, "sodio": 167.0, "calcio": 22.0, "ferro": 1.1, "potassio": 348.0, "zinco": 1.6, "colesterol": 0, "vitamina_c": 0},
    "pe_de_moleque_amendoim": {"nome": "Pé-de-moleque, amendoim", "calorias": 503.0, "proteinas": 13.2, "carboidratos": 54.7, "gorduras": 28.0, "fibras": 3.4, "sodio": 16.0, "calcio": 27.0, "ferro": 1.3, "potassio": 355.0, "zinco": 1.4, "colesterol": 0, "vitamina_c": 0},
    "soja_extrato_soluvel_natural_fluido": {"nome": "Soja, extrato solúvel, natural, fluido", "calorias": 39.0, "proteinas": 2.4, "carboidratos": 4.3, "gorduras": 1.6, "fibras": 0.4, "sodio": 57.0, "calcio": 17.0, "ferro": 0.4, "potassio": 121.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 0},
    "soja_extrato_soluvel_po": {"nome": "Soja, extrato solúvel, pó", "calorias": 459.0, "proteinas": 35.7, "carboidratos": 28.5, "gorduras": 26.2, "fibras": 7.3, "sodio": 83.0, "calcio": 359.0, "ferro": 7.0, "potassio": 1607.0, "zinco": 5.8, "colesterol": 0, "vitamina_c": 9.2},
    "soja_farinha": {"nome": "Soja, farinha", "calorias": 404.0, "proteinas": 36.0, "carboidratos": 38.4, "gorduras": 14.6, "fibras": 20.2, "sodio": 6.0, "calcio": 206.0, "ferro": 13.1, "potassio": 1922.0, "zinco": 4.5, "colesterol": 0, "vitamina_c": 0},
    "soja_queijo_tofu": {"nome": "Soja, queijo (tofu)", "calorias": 64.0, "proteinas": 6.6, "carboidratos": 2.1, "gorduras": 4.0, "fibras": 0.8, "sodio": 1.0, "calcio": 81.0, "ferro": 1.4, "potassio": 182.0, "zinco": 0.9, "colesterol": 0, "vitamina_c": 0},
    "tremoco_cru": {"nome": "Tremoço, cru", "calorias": 381.0, "proteinas": 33.6, "carboidratos": 43.8, "gorduras": 10.3, "fibras": 32.3, "sodio": 3.0, "calcio": 177.0, "ferro": 2.8, "potassio": 708.0, "zinco": 4.2, "colesterol": 0, "vitamina_c": 25.0},
    "tremoco_em_conserva": {"nome": "Tremoço, em conserva", "calorias": 121.0, "proteinas": 11.1, "carboidratos": 12.4, "gorduras": 3.8, "fibras": 14.4, "sodio": 1809.0, "calcio": 16.0, "ferro": 0.3, "potassio": 5.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 0},

    # ═══════════════════════════════════════════════════════════════
    # LEITE E DERIVADOS
    # ═══════════════════════════════════════════════════════════════
    "bebida_lactea_pessego": {"nome": "Bebida láctea, pêssego", "calorias": 55.0, "proteinas": 2.1, "carboidratos": 7.6, "gorduras": 1.9, "fibras": 0.3, "sodio": 46.0, "calcio": 89.0, "ferro": 0, "potassio": 62.0, "zinco": 0.2, "colesterol": 5.0, "vitamina_c": 2.1},
    "creme_de_leite": {"nome": "Creme de Leite", "calorias": 221.0, "proteinas": 1.5, "carboidratos": 4.5, "gorduras": 22.5, "fibras": 0, "sodio": 52.0, "calcio": 83.0, "ferro": 0.3, "potassio": 119.0, "zinco": 0.3, "colesterol": 66.0, "vitamina_c": 0},
    "iogurte_natural": {"nome": "Iogurte, natural", "calorias": 51.0, "proteinas": 4.1, "carboidratos": 1.9, "gorduras": 3.0, "fibras": 0, "sodio": 52.0, "calcio": 143.0, "ferro": 0, "potassio": 71.0, "zinco": 0.4, "colesterol": 14.0, "vitamina_c": 0.9},
    "iogurte_natural_desnatado": {"nome": "Iogurte, natural, desnatado", "calorias": 41.0, "proteinas": 3.8, "carboidratos": 5.8, "gorduras": 0.3, "fibras": 0, "sodio": 60.0, "calcio": 157.0, "ferro": 0, "potassio": 182.0, "zinco": 0.5, "colesterol": 3.0, "vitamina_c": 0.3},
    "iogurte_sabor_abacaxi": {"nome": "Iogurte, sabor abacaxi", "calorias": 0, "proteinas": 0, "carboidratos": 0, "gorduras": 0, "fibras": 0, "sodio": 0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 6.0, "vitamina_c": 0},
    "iogurte_sabor_morango": {"nome": "Iogurte, sabor morango", "calorias": 70.0, "proteinas": 2.7, "carboidratos": 9.7, "gorduras": 2.3, "fibras": 0.2, "sodio": 38.0, "calcio": 101.0, "ferro": 0, "potassio": 52.0, "zinco": 0.3, "colesterol": 7.0, "vitamina_c": 0},
    "iogurte_sabor_pessego": {"nome": "Iogurte, sabor pêssego", "calorias": 68.0, "proteinas": 2.5, "carboidratos": 9.4, "gorduras": 2.3, "fibras": 0.7, "sodio": 37.0, "calcio": 95.0, "ferro": 0.1, "potassio": 52.0, "zinco": 0.3, "colesterol": 8.0, "vitamina_c": 0},
    "leite_condensado": {"nome": "Leite, condensado", "calorias": 313.0, "proteinas": 7.7, "carboidratos": 57.0, "gorduras": 6.7, "fibras": 0, "sodio": 94.0, "calcio": 246.0, "ferro": 0.1, "potassio": 329.0, "zinco": 0.9, "colesterol": 28.0, "vitamina_c": 2.1},
    "leite_de_cabra": {"nome": "Leite, de cabra", "calorias": 66.0, "proteinas": 3.1, "carboidratos": 5.2, "gorduras": 3.8, "fibras": 0, "sodio": 74.0, "calcio": 112.0, "ferro": 0.1, "potassio": 140.0, "zinco": 0.4, "colesterol": 14.0, "vitamina_c": 0},
    "leite_de_vaca_achocolatado": {"nome": "Leite, de vaca, achocolatado", "calorias": 83.0, "proteinas": 2.1, "carboidratos": 14.2, "gorduras": 2.2, "fibras": 0.6, "sodio": 72.0, "calcio": 70.0, "ferro": 0.5, "potassio": 155.0, "zinco": 0.3, "colesterol": 6.0, "vitamina_c": 3.3},
    "leite_de_vaca_desnatado_po": {"nome": "Leite, de vaca, desnatado, pó", "calorias": 362.0, "proteinas": 34.7, "carboidratos": 53.0, "gorduras": 0.9, "fibras": 0, "sodio": 432.0, "calcio": 1363.0, "ferro": 0.9, "potassio": 1556.0, "zinco": 3.8, "colesterol": 25.0, "vitamina_c": 0},
    "leite_de_vaca_desnatado_uht": {"nome": "Leite, de vaca, desnatado, UHT", "calorias": 0, "proteinas": 0, "carboidratos": 0, "gorduras": 0, "fibras": 0, "sodio": 51.0, "calcio": 134.0, "ferro": 0, "potassio": 140.0, "zinco": 0.4, "colesterol": 4.0, "vitamina_c": 0},
    "leite_de_vaca_integral": {"nome": "Leite, de vaca, integral", "calorias": 0, "proteinas": 0, "carboidratos": 0, "gorduras": 0, "fibras": 0, "sodio": 64.0, "calcio": 123.0, "ferro": 0, "potassio": 133.0, "zinco": 0.4, "colesterol": 10.0, "vitamina_c": 0},
    "leite_de_vaca_integral_po": {"nome": "Leite, de vaca, integral, pó", "calorias": 497.0, "proteinas": 25.4, "carboidratos": 39.2, "gorduras": 26.9, "fibras": 0, "sodio": 323.0, "calcio": 890.0, "ferro": 0.5, "potassio": 1132.0, "zinco": 2.7, "colesterol": 85.0, "vitamina_c": 0},
    "leite_fermentado": {"nome": "Leite, fermentado", "calorias": 70.0, "proteinas": 1.9, "carboidratos": 15.7, "gorduras": 0.1, "fibras": 0, "sodio": 33.0, "calcio": 72.0, "ferro": 0, "potassio": 94.0, "zinco": 0.3, "colesterol": 2.0, "vitamina_c": 0.5},
    "queijo_minas_frescal": {"nome": "Queijo, minas, frescal", "calorias": 264.0, "proteinas": 17.4, "carboidratos": 3.2, "gorduras": 20.2, "fibras": 0, "sodio": 31.0, "calcio": 579.0, "ferro": 0.9, "potassio": 105.0, "zinco": 0.3, "colesterol": 62.0, "vitamina_c": 0},
    "queijo_minas_meia_cura": {"nome": "Queijo, minas, meia cura", "calorias": 321.0, "proteinas": 21.2, "carboidratos": 3.6, "gorduras": 24.6, "fibras": 0, "sodio": 501.0, "calcio": 696.0, "ferro": 0.2, "potassio": 120.0, "zinco": 2.7, "colesterol": 76.0, "vitamina_c": 0},
    "queijo_mozarela": {"nome": "Queijo, mozarela", "calorias": 330.0, "proteinas": 22.6, "carboidratos": 3.0, "gorduras": 25.2, "fibras": 0, "sodio": 581.0, "calcio": 875.0, "ferro": 0.3, "potassio": 62.0, "zinco": 3.5, "colesterol": 80.0, "vitamina_c": 0},
    "queijo_parmesao": {"nome": "Queijo, parmesão", "calorias": 453.0, "proteinas": 35.6, "carboidratos": 1.7, "gorduras": 33.5, "fibras": 0, "sodio": 1844.0, "calcio": 992.0, "ferro": 0.5, "potassio": 96.0, "zinco": 4.4, "colesterol": 106.0, "vitamina_c": 0},
    "queijo_pasteurizado": {"nome": "Queijo, pasteurizado", "calorias": 303.0, "proteinas": 9.4, "carboidratos": 5.7, "gorduras": 27.4, "fibras": 0, "sodio": 780.0, "calcio": 323.0, "ferro": 0.3, "potassio": 194.0, "zinco": 1.3, "colesterol": 82.0, "vitamina_c": 0},
    "queijo_petit_suisse_morango": {"nome": "Queijo, petit suisse, morango", "calorias": 121.0, "proteinas": 5.8, "carboidratos": 18.5, "gorduras": 2.8, "fibras": 0, "sodio": 412.0, "calcio": 731.0, "ferro": 0.1, "potassio": 121.0, "zinco": 2.7, "colesterol": 12.0, "vitamina_c": 0},
    "queijo_prato": {"nome": "Queijo, prato", "calorias": 360.0, "proteinas": 22.7, "carboidratos": 1.9, "gorduras": 29.1, "fibras": 0, "sodio": 580.0, "calcio": 940.0, "ferro": 0.3, "potassio": 73.0, "zinco": 3.5, "colesterol": 91.0, "vitamina_c": 0},
    "queijo_requeijao_cremoso": {"nome": "Queijo, requeijão, cremoso", "calorias": 257.0, "proteinas": 9.6, "carboidratos": 2.4, "gorduras": 23.4, "fibras": 0, "sodio": 558.0, "calcio": 259.0, "ferro": 0.1, "potassio": 93.0, "zinco": 1.3, "colesterol": 74.0, "vitamina_c": 0},
    "queijo_ricota": {"nome": "Queijo, ricota", "calorias": 140.0, "proteinas": 12.6, "carboidratos": 3.8, "gorduras": 8.1, "fibras": 0, "sodio": 283.0, "calcio": 253.0, "ferro": 0.1, "potassio": 112.0, "zinco": 0.5, "colesterol": 49.0, "vitamina_c": 0},

    # ═══════════════════════════════════════════════════════════════
    # MISCELÂNEAS
    # ═══════════════════════════════════════════════════════════════
    "cafe_po_torrado": {"nome": "Café, pó, torrado", "calorias": 419.0, "proteinas": 14.7, "carboidratos": 65.8, "gorduras": 11.9, "fibras": 51.2, "sodio": 1.0, "calcio": 107.0, "ferro": 8.1, "potassio": 1609.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 0},
    "capuccino_po": {"nome": "Capuccino, pó", "calorias": 417.0, "proteinas": 11.3, "carboidratos": 73.6, "gorduras": 8.6, "fibras": 2.4, "sodio": 382.0, "calcio": 467.0, "ferro": 2.3, "potassio": 886.0, "zinco": 1.1, "colesterol": 29.0, "vitamina_c": 0},
    "fermento_biologico_levedura_tablete": {"nome": "Fermento, biológico, levedura, tablete", "calorias": 90.0, "proteinas": 17.0, "carboidratos": 7.7, "gorduras": 1.5, "fibras": 4.2, "sodio": 40.0, "calcio": 18.0, "ferro": 2.6, "potassio": 576.0, "zinco": 11.0, "colesterol": 0, "vitamina_c": 0},
    "fermento_em_po_quimico": {"nome": "Fermento em pó, químico", "calorias": 90.0, "proteinas": 0.5, "carboidratos": 43.9, "gorduras": 0.1, "fibras": 0, "sodio": 10052.0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "gelatina_sabores_variados_po": {"nome": "Gelatina, sabores variados, pó", "calorias": 380.0, "proteinas": 8.9, "carboidratos": 89.2, "gorduras": 0, "fibras": 0, "sodio": 235.0, "calcio": 27.0, "ferro": 0.3, "potassio": 7.0, "zinco": 0, "colesterol": 0, "vitamina_c": 40.0},
    "sal_dietetico": {"nome": "Sal, dietético", "calorias": 0, "proteinas": 0, "carboidratos": 0, "gorduras": 0, "fibras": 0, "sodio": 23432.0, "calcio": 0, "ferro": 0, "potassio": 20468.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "sal_grosso": {"nome": "Sal, grosso", "calorias": 0, "proteinas": 0, "carboidratos": 0, "gorduras": 0, "fibras": 0, "sodio": 39943.0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "shoyu": {"nome": "Shoyu", "calorias": 61.0, "proteinas": 3.3, "carboidratos": 11.6, "gorduras": 0.3, "fibras": 0, "sodio": 5024.0, "calcio": 15.0, "ferro": 0.5, "potassio": 165.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 0},
    "tempero_a_base_de_sal": {"nome": "Tempero a base de sal", "calorias": 21.0, "proteinas": 2.7, "carboidratos": 2.1, "gorduras": 0.3, "fibras": 0.6, "sodio": 32560.0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},

    # ═══════════════════════════════════════════════════════════════
    # NOZES E SEMENTES
    # ═══════════════════════════════════════════════════════════════
    "amendoa_torrada_salgada": {"nome": "Amêndoa, torrada, salgada", "calorias": 581.0, "proteinas": 18.6, "carboidratos": 29.5, "gorduras": 47.3, "fibras": 11.6, "sodio": 279.0, "calcio": 237.0, "ferro": 3.1, "potassio": 640.0, "zinco": 2.6, "colesterol": 0, "vitamina_c": 0},
    "castanha_de_caju_torrada_salgada": {"nome": "Castanha-de-caju, torrada, salgada", "calorias": 570.0, "proteinas": 18.5, "carboidratos": 29.1, "gorduras": 46.3, "fibras": 3.7, "sodio": 125.0, "calcio": 33.0, "ferro": 5.2, "potassio": 671.0, "zinco": 4.7, "colesterol": 0, "vitamina_c": 0},
    "castanha_do_brasil_crua": {"nome": "Castanha-do-Brasil, crua", "calorias": 643.0, "proteinas": 14.5, "carboidratos": 15.1, "gorduras": 63.5, "fibras": 7.9, "sodio": 1.0, "calcio": 146.0, "ferro": 2.3, "potassio": 651.0, "zinco": 4.2, "colesterol": 0, "vitamina_c": 0},
    "coco_cru": {"nome": "Coco, cru", "calorias": 406.0, "proteinas": 3.7, "carboidratos": 10.4, "gorduras": 42.0, "fibras": 5.4, "sodio": 15.0, "calcio": 6.0, "ferro": 1.8, "potassio": 354.0, "zinco": 0.9, "colesterol": 0, "vitamina_c": 2.5},
    "coco_verde_cru": {"nome": "Coco,  verde, cru", "calorias": 0, "proteinas": 0, "carboidratos": 0, "gorduras": 0, "fibras": 0, "sodio": 0, "calcio": 0, "ferro": 0, "potassio": 0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "farinha_de_mesocarpo_de_babacu_crua": {"nome": "Farinha, de mesocarpo de babaçu, crua", "calorias": 329.0, "proteinas": 1.4, "carboidratos": 79.2, "gorduras": 0.2, "fibras": 17.9, "sodio": 12.0, "calcio": 61.0, "ferro": 18.3, "potassio": 362.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 0},
    "gergelim_semente": {"nome": "Gergelim, semente", "calorias": 584.0, "proteinas": 21.2, "carboidratos": 21.6, "gorduras": 50.4, "fibras": 11.9, "sodio": 3.0, "calcio": 825.0, "ferro": 5.4, "potassio": 546.0, "zinco": 5.2, "colesterol": 0, "vitamina_c": 0},
    "linhaca_semente": {"nome": "Linhaça, semente", "calorias": 495.0, "proteinas": 14.1, "carboidratos": 43.3, "gorduras": 32.3, "fibras": 33.5, "sodio": 9.0, "calcio": 211.0, "ferro": 4.7, "potassio": 869.0, "zinco": 4.4, "colesterol": 0, "vitamina_c": 0},
    "noz_crua": {"nome": "Noz, crua", "calorias": 620.0, "proteinas": 14.0, "carboidratos": 18.4, "gorduras": 59.4, "fibras": 7.2, "sodio": 5.0, "calcio": 105.0, "ferro": 2.0, "potassio": 533.0, "zinco": 2.1, "colesterol": 0, "vitamina_c": 0},
    "pinhao_cozido": {"nome": "Pinhão, cozido", "calorias": 174.0, "proteinas": 3.0, "carboidratos": 43.9, "gorduras": 0.7, "fibras": 15.6, "sodio": 1.0, "calcio": 16.0, "ferro": 0.8, "potassio": 727.0, "zinco": 0.8, "colesterol": 0, "vitamina_c": 27.7},
    "pupunha_cozida": {"nome": "Pupunha, cozida", "calorias": 219.0, "proteinas": 2.5, "carboidratos": 29.6, "gorduras": 12.8, "fibras": 4.3, "sodio": 1.0, "calcio": 28.0, "ferro": 0.5, "potassio": 303.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 2.2},

    # ═══════════════════════════════════════════════════════════════
    # OUTROS ALIMENTOS INDUSTRIALIZADOS
    # ═══════════════════════════════════════════════════════════════
    "azeitona_preta_conserva": {"nome": "Azeitona, preta, conserva", "calorias": 194.0, "proteinas": 1.2, "carboidratos": 5.5, "gorduras": 20.3, "fibras": 4.6, "sodio": 1567.0, "calcio": 59.0, "ferro": 5.5, "potassio": 79.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 0},
    "azeitona_verde_conserva": {"nome": "Azeitona, verde, conserva", "calorias": 137.0, "proteinas": 0.9, "carboidratos": 4.1, "gorduras": 14.2, "fibras": 3.8, "sodio": 1347.0, "calcio": 46.0, "ferro": 0.2, "potassio": 20.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0},
    "chantilly_spray_com_gordura_vegetal": {"nome": "Chantilly, spray, com gordura vegetal", "calorias": 315.0, "proteinas": 0.5, "carboidratos": 16.9, "gorduras": 27.3, "fibras": 0, "sodio": 110.0, "calcio": 2.0, "ferro": 0, "potassio": 5.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0},
    "leite_de_coco": {"nome": "Leite, de coco", "calorias": 166.0, "proteinas": 1.0, "carboidratos": 2.2, "gorduras": 18.4, "fibras": 0.7, "sodio": 44.0, "calcio": 6.0, "ferro": 0.5, "potassio": 144.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 0},
    "maionese_tradicional_com_ovos": {"nome": "Maionese, tradicional com ovos", "calorias": 302.0, "proteinas": 0.6, "carboidratos": 7.9, "gorduras": 30.5, "fibras": 0, "sodio": 787.0, "calcio": 3.0, "ferro": 0.1, "potassio": 16.0, "zinco": 0.1, "colesterol": 42.0, "vitamina_c": 0},

    # ═══════════════════════════════════════════════════════════════
    # OVOS E DERIVADOS
    # ═══════════════════════════════════════════════════════════════
    "omelete_de_queijo": {"nome": "Omelete, de queijo", "calorias": 268.0, "proteinas": 15.6, "carboidratos": 0.4, "gorduras": 22.0, "fibras": 0, "sodio": 216.0, "calcio": 166.0, "ferro": 1.4, "potassio": 127.0, "zinco": 1.4, "colesterol": 384.0, "vitamina_c": 0},
    "ovo_de_codorna_inteiro_cru": {"nome": "Ovo, de codorna, inteiro, cru", "calorias": 177.0, "proteinas": 13.7, "carboidratos": 0.8, "gorduras": 12.7, "fibras": 0, "sodio": 129.0, "calcio": 79.0, "ferro": 3.3, "potassio": 79.0, "zinco": 2.1, "colesterol": 568.0, "vitamina_c": 0},
    "ovo_de_galinha_clara_cozida_10minutos": {"nome": "Ovo, de galinha, clara, cozida/10minutos", "calorias": 59.0, "proteinas": 13.4, "carboidratos": 0.0, "gorduras": 0.1, "fibras": 0, "sodio": 181.0, "calcio": 6.0, "ferro": 0.1, "potassio": 146.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "ovo_de_galinha_gema_cozida_10minutos": {"nome": "Ovo, de galinha, gema, cozida/10minutos", "calorias": 353.0, "proteinas": 15.9, "carboidratos": 1.6, "gorduras": 30.8, "fibras": 0, "sodio": 45.0, "calcio": 114.0, "ferro": 2.9, "potassio": 87.0, "zinco": 2.9, "colesterol": 1272.0, "vitamina_c": 0},
    "ovo_de_galinha_inteiro_cozido_10minutos": {"nome": "Ovo, de galinha, inteiro, cozido/10minutos", "calorias": 146.0, "proteinas": 13.3, "carboidratos": 0.6, "gorduras": 9.5, "fibras": 0, "sodio": 146.0, "calcio": 49.0, "ferro": 1.5, "potassio": 139.0, "zinco": 1.2, "colesterol": 397.0, "vitamina_c": 0},
    "ovo_de_galinha_inteiro_cru": {"nome": "Ovo, de galinha, inteiro, cru", "calorias": 143.0, "proteinas": 13.0, "carboidratos": 1.6, "gorduras": 8.9, "fibras": 0, "sodio": 168.0, "calcio": 42.0, "ferro": 1.6, "potassio": 150.0, "zinco": 1.1, "colesterol": 356.0, "vitamina_c": 0},
    "ovo_de_galinha_inteiro_frito": {"nome": "Ovo, de galinha, inteiro, frito", "calorias": 240.0, "proteinas": 15.6, "carboidratos": 1.2, "gorduras": 18.6, "fibras": 0, "sodio": 166.0, "calcio": 73.0, "ferro": 2.1, "potassio": 184.0, "zinco": 1.5, "colesterol": 516.0, "vitamina_c": 0},

    # ═══════════════════════════════════════════════════════════════
    # PESCADOS E FRUTOS DO MAR
    # ═══════════════════════════════════════════════════════════════
    "abadejo_file_congelado_assado": {"nome": "Abadejo, filé, congelado, assado", "calorias": 112.0, "proteinas": 23.5, "carboidratos": 0.0, "gorduras": 1.2, "fibras": 0, "sodio": 334.0, "calcio": 23.0, "ferro": 0.5, "potassio": 156.0, "zinco": 0.5, "colesterol": 103.0, "vitamina_c": 0},
    "abadejo_file_congelado_cozido": {"nome": "Abadejo, filé, congelado,cozido", "calorias": 91.0, "proteinas": 19.3, "carboidratos": 0.0, "gorduras": 0.9, "fibras": 0, "sodio": 189.0, "calcio": 17.0, "ferro": 0.3, "potassio": 146.0, "zinco": 0.4, "colesterol": 87.0, "vitamina_c": 0},
    "abadejo_file_congelado_cru": {"nome": "Abadejo, filé, congelado, cru", "calorias": 59.0, "proteinas": 13.1, "carboidratos": 0.0, "gorduras": 0.4, "fibras": 0, "sodio": 79.0, "calcio": 10.0, "ferro": 0.1, "potassio": 148.0, "zinco": 0.4, "colesterol": 31.0, "vitamina_c": 0},
    "abadejo_file_congelado_grelhado": {"nome": "Abadejo, filé, congelado, grelhado", "calorias": 130.0, "proteinas": 27.6, "carboidratos": 0.0, "gorduras": 1.3, "fibras": 0, "sodio": 305.0, "calcio": 20.0, "ferro": 0.3, "potassio": 279.0, "zinco": 0.4, "colesterol": 136.0, "vitamina_c": 0},
    "atum_conserva_em_oleo": {"nome": "Atum, conserva em óleo", "calorias": 166.0, "proteinas": 26.2, "carboidratos": 0.0, "gorduras": 6.0, "fibras": 0, "sodio": 362.0, "calcio": 7.0, "ferro": 1.2, "potassio": 280.0, "zinco": 0.6, "colesterol": 53.0, "vitamina_c": 0},
    "atum_fresco_cru": {"nome": "Atum, fresco, cru", "calorias": 118.0, "proteinas": 25.7, "carboidratos": 0.0, "gorduras": 0.9, "fibras": 0, "sodio": 30.0, "calcio": 7.0, "ferro": 1.3, "potassio": 308.0, "zinco": 0.4, "colesterol": 48.0, "vitamina_c": 0},
    "bacalhau_salgado_cru": {"nome": "Bacalhau, salgado, cru", "calorias": 136.0, "proteinas": 29.0, "carboidratos": 0.0, "gorduras": 1.3, "fibras": 0, "sodio": 13585.0, "calcio": 157.0, "ferro": 0.9, "potassio": 434.0, "zinco": 0.7, "colesterol": 139.0, "vitamina_c": 0},
    "bacalhau_salgado_refogado": {"nome": "Bacalhau, salgado, refogado", "calorias": 140.0, "proteinas": 24.0, "carboidratos": 1.2, "gorduras": 3.6, "fibras": 0, "sodio": 1256.0, "calcio": 59.0, "ferro": 0.2, "potassio": 50.0, "zinco": 0.6, "colesterol": 112.0, "vitamina_c": 0},
    "cacao_posta_com_farinha_de_trigo_frita": {"nome": "Cação, posta, com farinha de trigo, frita", "calorias": 208.0, "proteinas": 25.0, "carboidratos": 3.1, "gorduras": 10.0, "fibras": 0.5, "sodio": 160.0, "calcio": 30.0, "ferro": 1.0, "potassio": 420.0, "zinco": 0.6, "colesterol": 75.0, "vitamina_c": 0},
    "cacao_posta_cozida": {"nome": "Cação, posta, cozida", "calorias": 116.0, "proteinas": 25.6, "carboidratos": 0.0, "gorduras": 0.7, "fibras": 0, "sodio": 115.0, "calcio": 10.0, "ferro": 0.3, "potassio": 249.0, "zinco": 0.6, "colesterol": 83.0, "vitamina_c": 0},
    "cacao_posta_crua": {"nome": "Cação, posta, crua", "calorias": 83.0, "proteinas": 17.9, "carboidratos": 0.0, "gorduras": 0.8, "fibras": 0, "sodio": 176.0, "calcio": 9.0, "ferro": 0.2, "potassio": 299.0, "zinco": 0.3, "colesterol": 36.0, "vitamina_c": 0},
    "camarao_rio_grande_grande_cozido": {"nome": "Camarão, Rio Grande, grande, cozido", "calorias": 90.0, "proteinas": 19.0, "carboidratos": 0.0, "gorduras": 1.0, "fibras": 0, "sodio": 367.0, "calcio": 90.0, "ferro": 1.3, "potassio": 102.0, "zinco": 1.2, "colesterol": 241.0, "vitamina_c": 0},
    "camarao_rio_grande_grande_cru": {"nome": "Camarão, Rio Grande, grande, cru", "calorias": 47.0, "proteinas": 10.0, "carboidratos": 0.0, "gorduras": 0.5, "fibras": 0, "sodio": 201.0, "calcio": 51.0, "ferro": 0.7, "potassio": 72.0, "zinco": 0.7, "colesterol": 124.0, "vitamina_c": 0},
    "camarao_sete_barbas_sem_cabeca_com_casca_frito": {"nome": "Camarão, Sete Barbas, sem cabeça, com casca, frito", "calorias": 231.0, "proteinas": 18.4, "carboidratos": 2.9, "gorduras": 15.6, "fibras": 0, "sodio": 99.0, "calcio": 960.0, "ferro": 2.4, "potassio": 107.0, "zinco": 1.1, "colesterol": 283.0, "vitamina_c": 0},
    "caranguejo_cozido": {"nome": "Caranguejo, cozido", "calorias": 83.0, "proteinas": 18.5, "carboidratos": 0.0, "gorduras": 0.4, "fibras": 0, "sodio": 360.0, "calcio": 357.0, "ferro": 2.9, "potassio": 186.0, "zinco": 5.7, "colesterol": 85.0, "vitamina_c": 0},
    "corimba_cru": {"nome": "Corimba, cru", "calorias": 128.0, "proteinas": 17.4, "carboidratos": 0.0, "gorduras": 6.0, "fibras": 0, "sodio": 47.0, "calcio": 40.0, "ferro": 0.5, "potassio": 317.0, "zinco": 0.4, "colesterol": 40.0, "vitamina_c": 0},
    "corimbata_assado": {"nome": "Corimbatá, assado", "calorias": 261.0, "proteinas": 19.9, "carboidratos": 0.0, "gorduras": 19.6, "fibras": 0, "sodio": 40.0, "calcio": 22.0, "ferro": 1.0, "potassio": 326.0, "zinco": 0.7, "colesterol": 80.0, "vitamina_c": 0},
    "corimbata_cozido": {"nome": "Corimbatá, cozido", "calorias": 239.0, "proteinas": 20.1, "carboidratos": 0.0, "gorduras": 16.9, "fibras": 0, "sodio": 37.0, "calcio": 65.0, "ferro": 0.6, "potassio": 254.0, "zinco": 1.0, "colesterol": 75.0, "vitamina_c": 0},
    "corvina_de_agua_doce_crua": {"nome": "Corvina de água doce, crua", "calorias": 101.0, "proteinas": 18.9, "carboidratos": 0.0, "gorduras": 2.2, "fibras": 0, "sodio": 45.0, "calcio": 39.0, "ferro": 0.3, "potassio": 293.0, "zinco": 0.4, "colesterol": 73.0, "vitamina_c": 0},
    "corvina_do_mar_crua": {"nome": "Corvina do mar, crua", "calorias": 94.0, "proteinas": 18.6, "carboidratos": 0.0, "gorduras": 1.6, "fibras": 0, "sodio": 68.0, "calcio": 0, "ferro": 0.4, "potassio": 339.0, "zinco": 0.4, "colesterol": 67.0, "vitamina_c": 0},
    "corvina_grande_assada": {"nome": "Corvina grande, assada", "calorias": 147.0, "proteinas": 26.8, "carboidratos": 0.0, "gorduras": 3.6, "fibras": 0, "sodio": 85.0, "calcio": 60.0, "ferro": 0.5, "potassio": 291.0, "zinco": 0.7, "colesterol": 117.0, "vitamina_c": 0},
    "corvina_grande_cozida": {"nome": "Corvina grande, cozida", "calorias": 100.0, "proteinas": 23.4, "carboidratos": 0.0, "gorduras": 2.6, "fibras": 0, "sodio": 68.0, "calcio": 69.0, "ferro": 0.6, "potassio": 194.0, "zinco": 0.7, "colesterol": 123.0, "vitamina_c": 0},
    "dourada_de_agua_doce_fresca": {"nome": "Dourada de água doce, fresca", "calorias": 131.0, "proteinas": 18.8, "carboidratos": 0.0, "gorduras": 5.6, "fibras": 0, "sodio": 40.0, "calcio": 12.0, "ferro": 0.2, "potassio": 393.0, "zinco": 0.5, "colesterol": 52.0, "vitamina_c": 0},
    "lambari_congelado_cru": {"nome": "Lambari, congelado, cru", "calorias": 131.0, "proteinas": 16.8, "carboidratos": 0.0, "gorduras": 6.5, "fibras": 0, "sodio": 48.0, "calcio": 1181.0, "ferro": 0.9, "potassio": 244.0, "zinco": 3.3, "colesterol": 159.0, "vitamina_c": 0},
    "lambari_congelado_frito": {"nome": "Lambari, congelado, frito", "calorias": 327.0, "proteinas": 28.4, "carboidratos": 0.0, "gorduras": 22.8, "fibras": 0, "sodio": 65.0, "calcio": 1881.0, "ferro": 0.8, "potassio": 331.0, "zinco": 5.6, "colesterol": 246.0, "vitamina_c": 0},
    "lambari_fresco_cru": {"nome": "Lambari, fresco, cru", "calorias": 152.0, "proteinas": 15.7, "carboidratos": 0.0, "gorduras": 9.4, "fibras": 0, "sodio": 41.0, "calcio": 590.0, "ferro": 0.6, "potassio": 207.0, "zinco": 2.4, "colesterol": 144.0, "vitamina_c": 0},
    "manjuba_com_farinha_de_trigo_frita": {"nome": "Manjuba, com farinha de trigo, frita", "calorias": 344.0, "proteinas": 23.5, "carboidratos": 10.2, "gorduras": 22.6, "fibras": 0.4, "sodio": 37.0, "calcio": 763.0, "ferro": 3.0, "potassio": 319.0, "zinco": 3.8, "colesterol": 282.0, "vitamina_c": 0},
    "manjuba_frita": {"nome": "Manjuba, frita", "calorias": 349.0, "proteinas": 30.1, "carboidratos": 0.0, "gorduras": 24.5, "fibras": 0, "sodio": 41.0, "calcio": 575.0, "ferro": 0.9, "potassio": 318.0, "zinco": 3.2, "colesterol": 270.0, "vitamina_c": 0},
    "merluza_file_assado": {"nome": "Merluza, filé, assado", "calorias": 122.0, "proteinas": 26.6, "carboidratos": 0.0, "gorduras": 0.9, "fibras": 0, "sodio": 120.0, "calcio": 36.0, "ferro": 0.4, "potassio": 364.0, "zinco": 0.9, "colesterol": 91.0, "vitamina_c": 0},
    "merluza_file_cru": {"nome": "Merluza, filé, cru", "calorias": 89.0, "proteinas": 16.6, "carboidratos": 0.0, "gorduras": 2.0, "fibras": 0, "sodio": 80.0, "calcio": 20.0, "ferro": 0.2, "potassio": 340.0, "zinco": 0.3, "colesterol": 57.0, "vitamina_c": 0},
    "merluza_file_frito": {"nome": "Merluza, filé, frito", "calorias": 192.0, "proteinas": 26.9, "carboidratos": 0.0, "gorduras": 8.5, "fibras": 0, "sodio": 90.0, "calcio": 36.0, "ferro": 0.4, "potassio": 447.0, "zinco": 0.6, "colesterol": 109.0, "vitamina_c": 0},
    "pescada_branca_crua": {"nome": "Pescada, branca, crua", "calorias": 111.0, "proteinas": 16.3, "carboidratos": 0.0, "gorduras": 4.6, "fibras": 0, "sodio": 76.0, "calcio": 16.0, "ferro": 0.2, "potassio": 261.0, "zinco": 0.3, "colesterol": 51.0, "vitamina_c": 0},
    "pescada_branca_frita": {"nome": "Pescada, branca, frita", "calorias": 223.0, "proteinas": 27.4, "carboidratos": 0.0, "gorduras": 11.8, "fibras": 0, "sodio": 107.0, "calcio": 378.0, "ferro": 0.5, "potassio": 355.0, "zinco": 1.1, "colesterol": 165.0, "vitamina_c": 0},
    "pescada_file_com_farinha_de_trigo_frito": {"nome": "Pescada, filé, com farinha de trigo, frito", "calorias": 283.0, "proteinas": 21.4, "carboidratos": 5.0, "gorduras": 19.1, "fibras": 0, "sodio": 91.0, "calcio": 26.0, "ferro": 0.9, "potassio": 216.0, "zinco": 0.4, "colesterol": 73.0, "vitamina_c": 0},
    "pescada_file_cru": {"nome": "Pescada, filé, cru", "calorias": 107.0, "proteinas": 16.7, "carboidratos": 0.0, "gorduras": 4.0, "fibras": 0, "sodio": 77.0, "calcio": 14.0, "ferro": 0.2, "potassio": 253.0, "zinco": 0.3, "colesterol": 65.0, "vitamina_c": 0},
    "pescada_file_frito": {"nome": "Pescada, filé, frito", "calorias": 154.0, "proteinas": 28.6, "carboidratos": 0.0, "gorduras": 3.6, "fibras": 0, "sodio": 115.0, "calcio": 10.0, "ferro": 0.3, "potassio": 249.0, "zinco": 0.6, "colesterol": 81.0, "vitamina_c": 0},
    "pescada_file_molho_escabeche": {"nome": "Pescada, filé, molho escabeche", "calorias": 142.0, "proteinas": 11.8, "carboidratos": 5.0, "gorduras": 8.0, "fibras": 0.8, "sodio": 51.0, "calcio": 20.0, "ferro": 1.5, "potassio": 208.0, "zinco": 0.3, "colesterol": 43.0, "vitamina_c": 6.9},
    "pescadinha_crua": {"nome": "Pescadinha, crua", "calorias": 76.0, "proteinas": 15.5, "carboidratos": 0.0, "gorduras": 1.1, "fibras": 0, "sodio": 120.0, "calcio": 332.0, "ferro": 0.5, "potassio": 304.0, "zinco": 0.6, "colesterol": 84.0, "vitamina_c": 0},
    "pintado_assado": {"nome": "Pintado, assado", "calorias": 192.0, "proteinas": 36.5, "carboidratos": 0.0, "gorduras": 4.0, "fibras": 0, "sodio": 81.0, "calcio": 114.0, "ferro": 0.8, "potassio": 527.0, "zinco": 2.1, "colesterol": 126.0, "vitamina_c": 0},
    "pintado_cru": {"nome": "Pintado, cru", "calorias": 91.0, "proteinas": 18.6, "carboidratos": 0.0, "gorduras": 1.3, "fibras": 0, "sodio": 43.0, "calcio": 12.0, "ferro": 0.2, "potassio": 294.0, "zinco": 0.4, "colesterol": 50.0, "vitamina_c": 0},
    "pintado_grelhado": {"nome": "Pintado, grelhado", "calorias": 152.0, "proteinas": 30.8, "carboidratos": 0.0, "gorduras": 2.3, "fibras": 0, "sodio": 53.0, "calcio": 69.0, "ferro": 0.5, "potassio": 360.0, "zinco": 0.8, "colesterol": 99.0, "vitamina_c": 0},
    "porquinho_cru": {"nome": "Porquinho, cru", "calorias": 93.0, "proteinas": 20.5, "carboidratos": 0.0, "gorduras": 0.6, "fibras": 0, "sodio": 67.0, "calcio": 26.0, "ferro": 0.4, "potassio": 313.0, "zinco": 0.7, "colesterol": 49.0, "vitamina_c": 0},
    "salmao_file_com_pele_fresco_grelhado": {"nome": "Salmão, filé, com pele, fresco,  grelhado", "calorias": 229.0, "proteinas": 23.9, "carboidratos": 0.0, "gorduras": 14.0, "fibras": 0, "sodio": 85.0, "calcio": 29.0, "ferro": 0.5, "potassio": 384.0, "zinco": 0.6, "colesterol": 85.0, "vitamina_c": 0},
    "salmao_sem_pele_fresco_cru": {"nome": "Salmão, sem pele, fresco, cru", "calorias": 170.0, "proteinas": 19.3, "carboidratos": 0.0, "gorduras": 9.7, "fibras": 0, "sodio": 64.0, "calcio": 9.0, "ferro": 0.2, "potassio": 376.0, "zinco": 0.3, "colesterol": 53.0, "vitamina_c": 0},
    "salmao_sem_pele_fresco_grelhado": {"nome": "Salmão, sem pele, fresco, grelhado", "calorias": 243.0, "proteinas": 26.1, "carboidratos": 0.0, "gorduras": 14.5, "fibras": 0, "sodio": 96.0, "calcio": 15.0, "ferro": 0.4, "potassio": 518.0, "zinco": 0.5, "colesterol": 73.0, "vitamina_c": 0},
    "sardinha_assada": {"nome": "Sardinha, assada", "calorias": 164.0, "proteinas": 32.2, "carboidratos": 0.0, "gorduras": 3.0, "fibras": 0, "sodio": 74.0, "calcio": 438.0, "ferro": 1.3, "potassio": 574.0, "zinco": 1.8, "colesterol": 109.0, "vitamina_c": 0},
    "sardinha_conserva_em_oleo": {"nome": "Sardinha, conserva em óleo", "calorias": 285.0, "proteinas": 15.9, "carboidratos": 0.0, "gorduras": 24.0, "fibras": 0, "sodio": 666.0, "calcio": 550.0, "ferro": 3.5, "potassio": 367.0, "zinco": 1.6, "colesterol": 73.0, "vitamina_c": 0},
    "sardinha_frita": {"nome": "Sardinha, frita", "calorias": 257.0, "proteinas": 33.4, "carboidratos": 0.0, "gorduras": 12.7, "fibras": 0, "sodio": 60.0, "calcio": 482.0, "ferro": 1.1, "potassio": 460.0, "zinco": 1.6, "colesterol": 103.0, "vitamina_c": 0},
    "sardinha_inteira_crua": {"nome": "Sardinha, inteira, crua", "calorias": 114.0, "proteinas": 21.1, "carboidratos": 0.0, "gorduras": 2.7, "fibras": 0, "sodio": 60.0, "calcio": 167.0, "ferro": 1.3, "potassio": 312.0, "zinco": 1.3, "colesterol": 61.0, "vitamina_c": 0},
    "tucunare_file_congelado_cru": {"nome": "Tucunaré, filé, congelado, cru", "calorias": 88.0, "proteinas": 18.0, "carboidratos": 0.0, "gorduras": 1.2, "fibras": 0, "sodio": 57.0, "calcio": 19.0, "ferro": 0.3, "potassio": 288.0, "zinco": 0.4, "colesterol": 47.0, "vitamina_c": 0},

    # ═══════════════════════════════════════════════════════════════
    # PRODUTOS AÇUCARADOS
    # ═══════════════════════════════════════════════════════════════
    "achocolatado_po": {"nome": "Achocolatado, pó", "calorias": 401.0, "proteinas": 4.2, "carboidratos": 91.2, "gorduras": 2.2, "fibras": 3.9, "sodio": 65.0, "calcio": 44.0, "ferro": 5.4, "potassio": 496.0, "zinco": 1.0, "colesterol": 0, "vitamina_c": 0},
    "acucar_cristal": {"nome": "Açúcar, cristal", "calorias": 387.0, "proteinas": 0.3, "carboidratos": 99.6, "gorduras": 0, "fibras": 0, "sodio": 0, "calcio": 8.0, "ferro": 0.2, "potassio": 3.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "acucar_mascavo": {"nome": "Açúcar, mascavo", "calorias": 369.0, "proteinas": 0.8, "carboidratos": 94.5, "gorduras": 0.1, "fibras": 0, "sodio": 25.0, "calcio": 127.0, "ferro": 8.3, "potassio": 522.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 0},
    "acucar_refinado": {"nome": "Açúcar, refinado", "calorias": 387.0, "proteinas": 0.3, "carboidratos": 99.5, "gorduras": 0, "fibras": 0, "sodio": 12.0, "calcio": 4.0, "ferro": 0.1, "potassio": 6.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "chocolate_ao_leite": {"nome": "Chocolate, ao leite", "calorias": 540.0, "proteinas": 7.2, "carboidratos": 59.6, "gorduras": 30.3, "fibras": 2.2, "sodio": 77.0, "calcio": 191.0, "ferro": 1.6, "potassio": 355.0, "zinco": 1.1, "colesterol": 17.0, "vitamina_c": 0},
    "chocolate_ao_leite_com_castanha_do_para": {"nome": "Chocolate, ao leite, com castanha do Pará", "calorias": 559.0, "proteinas": 7.4, "carboidratos": 55.4, "gorduras": 34.2, "fibras": 2.5, "sodio": 64.0, "calcio": 171.0, "ferro": 1.5, "potassio": 431.0, "zinco": 1.3, "colesterol": 16.0, "vitamina_c": 1.4},
    "chocolate_ao_leite_dietetico": {"nome": "Chocolate, ao leite, dietético", "calorias": 557.0, "proteinas": 6.9, "carboidratos": 56.3, "gorduras": 33.8, "fibras": 2.8, "sodio": 85.0, "calcio": 188.0, "ferro": 3.3, "potassio": 458.0, "zinco": 1.1, "colesterol": 13.0, "vitamina_c": 2.0},
    "chocolate_meio_amargo": {"nome": "Chocolate, meio amargo", "calorias": 475.0, "proteinas": 4.9, "carboidratos": 62.4, "gorduras": 29.9, "fibras": 4.9, "sodio": 9.0, "calcio": 45.0, "ferro": 3.6, "potassio": 432.0, "zinco": 1.5, "colesterol": 2.0, "vitamina_c": 2.1},
    "cocada_branca": {"nome": "Cocada branca", "calorias": 449.0, "proteinas": 1.1, "carboidratos": 81.4, "gorduras": 13.6, "fibras": 3.6, "sodio": 29.0, "calcio": 7.0, "ferro": 1.2, "potassio": 183.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 0},
    "doce_de_abobora_cremoso": {"nome": "Doce, de abóbora, cremoso", "calorias": 199.0, "proteinas": 0.9, "carboidratos": 54.6, "gorduras": 0.2, "fibras": 2.3, "sodio": 0, "calcio": 13.0, "ferro": 0.9, "potassio": 137.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0.1},
    "doce_de_leite_cremoso": {"nome": "Doce, de leite, cremoso", "calorias": 306.0, "proteinas": 5.5, "carboidratos": 59.5, "gorduras": 6.0, "fibras": 0, "sodio": 120.0, "calcio": 195.0, "ferro": 0.1, "potassio": 259.0, "zinco": 0.5, "colesterol": 20.0, "vitamina_c": 0},
    "geleia_mocoto_natural": {"nome": "Geléia, mocotó, natural", "calorias": 106.0, "proteinas": 2.1, "carboidratos": 24.2, "gorduras": 0.1, "fibras": 0, "sodio": 43.0, "calcio": 4.0, "ferro": 0.1, "potassio": 2.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "glicose_de_milho": {"nome": "Glicose de milho", "calorias": 292.0, "proteinas": 0.0, "carboidratos": 79.4, "gorduras": 0.0, "fibras": 0, "sodio": 59.0, "calcio": 6.0, "ferro": 0.1, "potassio": 5.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "maria_mole": {"nome": "Maria mole", "calorias": 301.0, "proteinas": 3.8, "carboidratos": 73.6, "gorduras": 0.2, "fibras": 0.7, "sodio": 15.0, "calcio": 13.0, "ferro": 0.4, "potassio": 24.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0},
    "maria_mole_coco_queimado": {"nome": "Maria mole, coco queimado", "calorias": 307.0, "proteinas": 3.9, "carboidratos": 75.1, "gorduras": 0.1, "fibras": 0.6, "sodio": 14.0, "calcio": 19.0, "ferro": 0.5, "potassio": 36.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0},
    "marmelada": {"nome": "Marmelada", "calorias": 257.0, "proteinas": 0.4, "carboidratos": 70.8, "gorduras": 0.1, "fibras": 4.1, "sodio": 11.0, "calcio": 11.0, "ferro": 0.7, "potassio": 83.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0},
    "mel_de_abelha": {"nome": "Mel, de abelha", "calorias": 309.0, "proteinas": 0.0, "carboidratos": 84.0, "gorduras": 0.0, "fibras": 0, "sodio": 6.0, "calcio": 10.0, "ferro": 0.3, "potassio": 99.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 0.7},
    "melado": {"nome": "Melado", "calorias": 297.0, "proteinas": 0.0, "carboidratos": 76.6, "gorduras": 0.0, "fibras": 0, "sodio": 4.0, "calcio": 102.0, "ferro": 5.4, "potassio": 395.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 0},
    "quindim": {"nome": "Quindim", "calorias": 411.0, "proteinas": 4.7, "carboidratos": 46.3, "gorduras": 24.4, "fibras": 3.2, "sodio": 27.0, "calcio": 37.0, "ferro": 1.4, "potassio": 111.0, "zinco": 1.1, "colesterol": 271.0, "vitamina_c": 0},
    "rapadura": {"nome": "Rapadura", "calorias": 352.0, "proteinas": 1.0, "carboidratos": 90.8, "gorduras": 0.1, "fibras": 0, "sodio": 22.0, "calcio": 30.0, "ferro": 4.4, "potassio": 459.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 0},

    # ═══════════════════════════════════════════════════════════════
    # VERDURAS, HORTALIÇAS E DERIVADOS
    # ═══════════════════════════════════════════════════════════════
    "abobora_cabotian_cozida": {"nome": "Abóbora, cabotian, cozida", "calorias": 48.0, "proteinas": 1.4, "carboidratos": 10.8, "gorduras": 0.7, "fibras": 2.5, "sodio": 1.0, "calcio": 8.0, "ferro": 0.3, "potassio": 199.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 7.5},
    "abobora_cabotian_crua": {"nome": "Abóbora, cabotian, crua", "calorias": 39.0, "proteinas": 1.7, "carboidratos": 8.4, "gorduras": 0.5, "fibras": 2.2, "sodio": 0, "calcio": 18.0, "ferro": 0.4, "potassio": 351.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 5.1},
    "abobora_menina_brasileira_crua": {"nome": "Abóbora, menina brasileira, crua", "calorias": 14.0, "proteinas": 0.6, "carboidratos": 3.3, "gorduras": 0, "fibras": 1.2, "sodio": 0, "calcio": 9.0, "ferro": 0.2, "potassio": 165.0, "zinco": 0, "colesterol": 0, "vitamina_c": 1.5},
    "abobora_moranga_crua": {"nome": "Abóbora, moranga, crua", "calorias": 12.0, "proteinas": 1.0, "carboidratos": 2.7, "gorduras": 0.1, "fibras": 1.7, "sodio": 0, "calcio": 3.0, "ferro": 0, "potassio": 125.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 9.6},
    "abobora_moranga_refogada": {"nome": "Abóbora, moranga, refogada", "calorias": 29.0, "proteinas": 0.4, "carboidratos": 6.0, "gorduras": 0.8, "fibras": 1.5, "sodio": 3.0, "calcio": 19.0, "ferro": 0.1, "potassio": 183.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 6.7},
    "abobora_pescoco_crua": {"nome": "Abóbora, pescoço, crua", "calorias": 24.0, "proteinas": 0.7, "carboidratos": 6.1, "gorduras": 0.1, "fibras": 2.3, "sodio": 1.0, "calcio": 9.0, "ferro": 0.3, "potassio": 264.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 2.1},
    "abobrinha_italiana_cozida": {"nome": "Abobrinha, italiana, cozida", "calorias": 15.0, "proteinas": 1.1, "carboidratos": 3.0, "gorduras": 0.2, "fibras": 1.6, "sodio": 1.0, "calcio": 17.0, "ferro": 0.2, "potassio": 126.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 2.1},
    "abobrinha_italiana_crua": {"nome": "Abobrinha, italiana, crua", "calorias": 19.0, "proteinas": 1.1, "carboidratos": 4.3, "gorduras": 0.1, "fibras": 1.4, "sodio": 0, "calcio": 15.0, "ferro": 0.2, "potassio": 253.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 6.9},
    "abobrinha_italiana_refogada": {"nome": "Abobrinha, italiana, refogada", "calorias": 24.0, "proteinas": 1.1, "carboidratos": 4.2, "gorduras": 0.8, "fibras": 1.4, "sodio": 2.0, "calcio": 21.0, "ferro": 0.4, "potassio": 194.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 7.5},
    "abobrinha_paulista_crua": {"nome": "Abobrinha, paulista, crua", "calorias": 31.0, "proteinas": 0.6, "carboidratos": 7.9, "gorduras": 0.1, "fibras": 2.6, "sodio": 1.0, "calcio": 19.0, "ferro": 0.2, "potassio": 213.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 17.5},
    "acelga_crua": {"nome": "Acelga, crua", "calorias": 21.0, "proteinas": 1.4, "carboidratos": 4.6, "gorduras": 0.1, "fibras": 1.1, "sodio": 1.0, "calcio": 43.0, "ferro": 0.3, "potassio": 240.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 22.6},
    "agriao_cru": {"nome": "Agrião, cru", "calorias": 17.0, "proteinas": 2.7, "carboidratos": 2.3, "gorduras": 0.2, "fibras": 2.1, "sodio": 7.0, "calcio": 133.0, "ferro": 3.1, "potassio": 218.0, "zinco": 0.7, "colesterol": 0, "vitamina_c": 60.1},
    "aipo_cru": {"nome": "Aipo, cru", "calorias": 19.0, "proteinas": 0.8, "carboidratos": 4.3, "gorduras": 0.1, "fibras": 1.0, "sodio": 10.0, "calcio": 65.0, "ferro": 0.7, "potassio": 274.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 5.9},
    "alface_americana_crua": {"nome": "Alface, americana, crua", "calorias": 9.0, "proteinas": 0.6, "carboidratos": 1.7, "gorduras": 0.1, "fibras": 1.0, "sodio": 7.0, "calcio": 14.0, "ferro": 0.3, "potassio": 136.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 11.0},
    "alface_crespa_crua": {"nome": "Alface, crespa, crua", "calorias": 11.0, "proteinas": 1.3, "carboidratos": 1.7, "gorduras": 0.2, "fibras": 1.8, "sodio": 3.0, "calcio": 38.0, "ferro": 0.4, "potassio": 267.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 15.6},
    "alface_lisa_crua": {"nome": "Alface, lisa, crua", "calorias": 14.0, "proteinas": 1.7, "carboidratos": 2.4, "gorduras": 0.1, "fibras": 2.3, "sodio": 4.0, "calcio": 28.0, "ferro": 0.6, "potassio": 349.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 21.4},
    "alface_roxa_crua": {"nome": "Alface, roxa, crua", "calorias": 13.0, "proteinas": 0.9, "carboidratos": 2.5, "gorduras": 0.2, "fibras": 2.0, "sodio": 7.0, "calcio": 34.0, "ferro": 2.5, "potassio": 308.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 13.5},
    "alfavaca_crua": {"nome": "Alfavaca, crua", "calorias": 29.0, "proteinas": 2.7, "carboidratos": 5.2, "gorduras": 0.5, "fibras": 4.1, "sodio": 5.0, "calcio": 258.0, "ferro": 1.3, "potassio": 261.0, "zinco": 0.7, "colesterol": 0, "vitamina_c": 0},
    "alho_cru": {"nome": "Alho, cru", "calorias": 113.0, "proteinas": 7.0, "carboidratos": 23.9, "gorduras": 0.2, "fibras": 4.3, "sodio": 5.0, "calcio": 14.0, "ferro": 0.8, "potassio": 535.0, "zinco": 0.8, "colesterol": 0, "vitamina_c": 0},
    "alho_poro_cru": {"nome": "Alho-poró, cru", "calorias": 32.0, "proteinas": 1.4, "carboidratos": 6.9, "gorduras": 0.1, "fibras": 2.5, "sodio": 2.0, "calcio": 34.0, "ferro": 0.6, "potassio": 224.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 14.1},
    "almeirao_cru": {"nome": "Almeirão, cru", "calorias": 18.0, "proteinas": 1.8, "carboidratos": 3.3, "gorduras": 0.2, "fibras": 2.6, "sodio": 2.0, "calcio": 19.0, "ferro": 0.7, "potassio": 369.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 1.7},
    "almeirao_refogado": {"nome": "Almeirão, refogado", "calorias": 65.0, "proteinas": 1.7, "carboidratos": 5.7, "gorduras": 4.8, "fibras": 3.4, "sodio": 15.0, "calcio": 63.0, "ferro": 1.6, "potassio": 315.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 1.5},
    "batata_baroa_cozida": {"nome": "Batata, baroa, cozida", "calorias": 80.0, "proteinas": 0.9, "carboidratos": 18.9, "gorduras": 0.2, "fibras": 1.8, "sodio": 2.0, "calcio": 12.0, "ferro": 0.4, "potassio": 258.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 17.1},
    "batata_baroa_crua": {"nome": "Batata, baroa, crua", "calorias": 101.0, "proteinas": 1.0, "carboidratos": 24.0, "gorduras": 0.2, "fibras": 2.1, "sodio": 0, "calcio": 17.0, "ferro": 0.3, "potassio": 505.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 7.6},
    "batata_doce_cozida": {"nome": "Batata, doce, cozida", "calorias": 77.0, "proteinas": 0.6, "carboidratos": 18.4, "gorduras": 0.1, "fibras": 2.2, "sodio": 3.0, "calcio": 17.0, "ferro": 0.2, "potassio": 148.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 23.8},
    "batata_doce_crua": {"nome": "Batata, doce, crua", "calorias": 118.0, "proteinas": 1.3, "carboidratos": 28.2, "gorduras": 0.1, "fibras": 2.6, "sodio": 9.0, "calcio": 21.0, "ferro": 0.4, "potassio": 340.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 16.5},
    "batata_frita_tipo_chips_industrializada": {"nome": "Batata, frita, tipo chips, industrializada", "calorias": 543.0, "proteinas": 5.6, "carboidratos": 51.2, "gorduras": 36.6, "fibras": 2.5, "sodio": 607.0, "calcio": 12.0, "ferro": 0.7, "potassio": 1014.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 0},
    "batata_inglesa_cozida": {"nome": "Batata, inglesa, cozida", "calorias": 52.0, "proteinas": 1.2, "carboidratos": 11.9, "gorduras": 0, "fibras": 1.3, "sodio": 2.0, "calcio": 4.0, "ferro": 0.2, "potassio": 161.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 3.8},
    "batata_inglesa_crua": {"nome": "Batata, inglesa, crua", "calorias": 64.0, "proteinas": 1.8, "carboidratos": 14.7, "gorduras": 0, "fibras": 1.2, "sodio": 0, "calcio": 4.0, "ferro": 0.4, "potassio": 302.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 31.1},
    "batata_inglesa_frita": {"nome": "Batata, inglesa, frita", "calorias": 267.0, "proteinas": 5.0, "carboidratos": 35.6, "gorduras": 13.1, "fibras": 8.1, "sodio": 2.0, "calcio": 6.0, "ferro": 0.4, "potassio": 489.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 16.3},
    "batata_inglesa_saute": {"nome": "Batata, inglesa, sauté", "calorias": 68.0, "proteinas": 1.3, "carboidratos": 14.1, "gorduras": 0.9, "fibras": 1.4, "sodio": 8.0, "calcio": 4.0, "ferro": 0.3, "potassio": 199.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 0},
    "berinjela_cozida": {"nome": "Berinjela, cozida", "calorias": 19.0, "proteinas": 0.7, "carboidratos": 4.5, "gorduras": 0.1, "fibras": 2.5, "sodio": 1.0, "calcio": 11.0, "ferro": 0.2, "potassio": 105.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0},
    "berinjela_crua": {"nome": "Berinjela, crua", "calorias": 20.0, "proteinas": 1.2, "carboidratos": 4.4, "gorduras": 0.1, "fibras": 2.9, "sodio": 0, "calcio": 9.0, "ferro": 0.2, "potassio": 205.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 3.0},
    "beterraba_cozida": {"nome": "Beterraba, cozida", "calorias": 32.0, "proteinas": 1.3, "carboidratos": 7.2, "gorduras": 0.1, "fibras": 1.9, "sodio": 23.0, "calcio": 15.0, "ferro": 0.2, "potassio": 245.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 1.2},
    "beterraba_crua": {"nome": "Beterraba, crua", "calorias": 49.0, "proteinas": 1.9, "carboidratos": 11.1, "gorduras": 0.1, "fibras": 3.4, "sodio": 10.0, "calcio": 18.0, "ferro": 0.3, "potassio": 375.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 3.1},
    "biscoito_polvilho_doce": {"nome": "Biscoito, polvilho doce", "calorias": 438.0, "proteinas": 1.3, "carboidratos": 80.5, "gorduras": 12.2, "fibras": 1.2, "sodio": 98.0, "calcio": 30.0, "ferro": 1.8, "potassio": 54.0, "zinco": 0.1, "colesterol": 9.0, "vitamina_c": 0},
    "brocolis_cozido": {"nome": "Brócolis, cozido", "calorias": 25.0, "proteinas": 2.1, "carboidratos": 4.4, "gorduras": 0.5, "fibras": 3.4, "sodio": 2.0, "calcio": 51.0, "ferro": 0.5, "potassio": 119.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 42.0},
    "brocolis_cru": {"nome": "Brócolis, cru", "calorias": 25.0, "proteinas": 3.6, "carboidratos": 4.0, "gorduras": 0.3, "fibras": 2.9, "sodio": 3.0, "calcio": 86.0, "ferro": 0.6, "potassio": 322.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 34.3},
    "cara_cozido": {"nome": "Cará, cozido", "calorias": 78.0, "proteinas": 1.5, "carboidratos": 18.9, "gorduras": 0.1, "fibras": 2.6, "sodio": 1.0, "calcio": 5.0, "ferro": 0.3, "potassio": 203.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 0},
    "cara_cru": {"nome": "Cará, cru", "calorias": 96.0, "proteinas": 2.3, "carboidratos": 23.0, "gorduras": 0.1, "fibras": 7.3, "sodio": 0, "calcio": 4.0, "ferro": 0.2, "potassio": 212.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 8.8},
    "caruru_cru": {"nome": "Caruru, cru", "calorias": 34.0, "proteinas": 3.2, "carboidratos": 6.0, "gorduras": 0.6, "fibras": 4.5, "sodio": 14.0, "calcio": 455.0, "ferro": 4.5, "potassio": 279.0, "zinco": 6.0, "colesterol": 0, "vitamina_c": 5.4},
    "catalonha_crua": {"nome": "Catalonha, crua", "calorias": 24.0, "proteinas": 1.9, "carboidratos": 4.8, "gorduras": 0.3, "fibras": 2.0, "sodio": 9.0, "calcio": 57.0, "ferro": 3.1, "potassio": 412.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 7.3},
    "catalonha_refogada": {"nome": "Catalonha, refogada", "calorias": 63.0, "proteinas": 2.0, "carboidratos": 4.8, "gorduras": 4.8, "fibras": 3.7, "sodio": 25.0, "calcio": 63.0, "ferro": 1.2, "potassio": 452.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 0},
    "cebola_crua": {"nome": "Cebola, crua", "calorias": 39.0, "proteinas": 1.7, "carboidratos": 8.9, "gorduras": 0.1, "fibras": 2.2, "sodio": 1.0, "calcio": 14.0, "ferro": 0.2, "potassio": 176.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 4.7},
    "cebolinha_crua": {"nome": "Cebolinha, crua", "calorias": 20.0, "proteinas": 1.9, "carboidratos": 3.4, "gorduras": 0.4, "fibras": 3.6, "sodio": 2.0, "calcio": 80.0, "ferro": 0.6, "potassio": 206.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 31.8},
    "cenoura_cozida": {"nome": "Cenoura, cozida", "calorias": 30.0, "proteinas": 0.8, "carboidratos": 6.7, "gorduras": 0.2, "fibras": 2.6, "sodio": 8.0, "calcio": 26.0, "ferro": 0.1, "potassio": 176.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 0},
    "cenoura_crua": {"nome": "Cenoura, crua", "calorias": 34.0, "proteinas": 1.3, "carboidratos": 7.7, "gorduras": 0.2, "fibras": 3.2, "sodio": 3.0, "calcio": 23.0, "ferro": 0.2, "potassio": 315.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 5.1},
    "chicoria_crua": {"nome": "Chicória, crua", "calorias": 14.0, "proteinas": 1.1, "carboidratos": 2.9, "gorduras": 0.1, "fibras": 2.2, "sodio": 14.0, "calcio": 45.0, "ferro": 0.5, "potassio": 425.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 6.5},
    "chuchu_cozido": {"nome": "Chuchu, cozido", "calorias": 19.0, "proteinas": 0.4, "carboidratos": 4.8, "gorduras": 0, "fibras": 1.0, "sodio": 2.0, "calcio": 8.0, "ferro": 0.1, "potassio": 54.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 5.6},
    "chuchu_cru": {"nome": "Chuchu, cru", "calorias": 17.0, "proteinas": 0.7, "carboidratos": 4.1, "gorduras": 0.1, "fibras": 1.3, "sodio": 0, "calcio": 12.0, "ferro": 0.2, "potassio": 126.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 10.6},
    "coentro_folhas_desidratadas": {"nome": "Coentro, folhas desidratadas", "calorias": 309.0, "proteinas": 20.9, "carboidratos": 48.0, "gorduras": 10.4, "fibras": 37.3, "sodio": 18.0, "calcio": 784.0, "ferro": 81.4, "potassio": 3223.0, "zinco": 4.7, "colesterol": 0, "vitamina_c": 40.8},
    "couve_flor_cozida": {"nome": "Couve-flor, cozida", "calorias": 19.0, "proteinas": 1.2, "carboidratos": 3.9, "gorduras": 0.3, "fibras": 2.1, "sodio": 2.0, "calcio": 16.0, "ferro": 0.1, "potassio": 80.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 23.7},
    "couve_flor_crua": {"nome": "Couve-flor, crua", "calorias": 23.0, "proteinas": 1.9, "carboidratos": 4.5, "gorduras": 0.2, "fibras": 2.4, "sodio": 3.0, "calcio": 18.0, "ferro": 0.5, "potassio": 256.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 36.1},
    "couve_manteiga_crua": {"nome": "Couve, manteiga, crua", "calorias": 27.0, "proteinas": 2.9, "carboidratos": 4.3, "gorduras": 0.5, "fibras": 3.1, "sodio": 6.0, "calcio": 131.0, "ferro": 0.5, "potassio": 403.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 96.7},
    "couve_manteiga_refogada": {"nome": "Couve, manteiga, refogada ", "calorias": 90.0, "proteinas": 1.7, "carboidratos": 8.7, "gorduras": 6.6, "fibras": 5.7, "sodio": 11.0, "calcio": 177.0, "ferro": 0.5, "potassio": 315.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 76.9},
    "espinafre_nova_zelandia_cru": {"nome": "Espinafre, Nova Zelândia, cru", "calorias": 16.0, "proteinas": 2.0, "carboidratos": 2.6, "gorduras": 0.2, "fibras": 2.1, "sodio": 17.0, "calcio": 98.0, "ferro": 0.4, "potassio": 336.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 2.4},
    "espinafre_nova_zelandia_refogado": {"nome": "Espinafre, Nova Zelândia, refogado", "calorias": 67.0, "proteinas": 2.7, "carboidratos": 4.2, "gorduras": 5.4, "fibras": 2.5, "sodio": 47.0, "calcio": 112.0, "ferro": 0.6, "potassio": 149.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 5.3},
    "farinha_de_mandioca_crua": {"nome": "Farinha, de mandioca, crua", "calorias": 361.0, "proteinas": 1.6, "carboidratos": 87.9, "gorduras": 0.3, "fibras": 6.4, "sodio": 1.0, "calcio": 65.0, "ferro": 1.1, "potassio": 340.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 0},
    "farinha_de_mandioca_torrada": {"nome": "Farinha, de mandioca, torrada", "calorias": 365.0, "proteinas": 1.2, "carboidratos": 89.2, "gorduras": 0.3, "fibras": 6.5, "sodio": 10.0, "calcio": 76.0, "ferro": 1.2, "potassio": 328.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 0},
    "farinha_de_puba": {"nome": "Farinha, de puba", "calorias": 360.0, "proteinas": 1.6, "carboidratos": 87.3, "gorduras": 0.5, "fibras": 4.2, "sodio": 4.0, "calcio": 41.0, "ferro": 1.4, "potassio": 338.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 0},
    "fecula_de_mandioca": {"nome": "Fécula, de mandioca", "calorias": 331.0, "proteinas": 0.5, "carboidratos": 81.1, "gorduras": 0.3, "fibras": 0.6, "sodio": 2.0, "calcio": 12.0, "ferro": 0.1, "potassio": 48.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "feijao_broto_cru": {"nome": "Feijão, broto, cru", "calorias": 39.0, "proteinas": 4.2, "carboidratos": 7.8, "gorduras": 0.1, "fibras": 2.0, "sodio": 2.0, "calcio": 14.0, "ferro": 0.8, "potassio": 189.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 12.0},
    "inhame_cru": {"nome": "Inhame, cru", "calorias": 97.0, "proteinas": 2.1, "carboidratos": 23.2, "gorduras": 0.2, "fibras": 1.7, "sodio": 0, "calcio": 12.0, "ferro": 0.4, "potassio": 568.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 5.6},
    "jilo_cru": {"nome": "Jiló, cru", "calorias": 27.0, "proteinas": 1.4, "carboidratos": 6.2, "gorduras": 0.2, "fibras": 4.8, "sodio": 0, "calcio": 20.0, "ferro": 0.3, "potassio": 213.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 6.8},
    "jurubeba_crua": {"nome": "Jurubeba, crua", "calorias": 126.0, "proteinas": 4.4, "carboidratos": 23.1, "gorduras": 3.9, "fibras": 23.9, "sodio": 1.0, "calcio": 151.0, "ferro": 0.9, "potassio": 619.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 13.8},
    "mandioca_cozida": {"nome": "Mandioca, cozida", "calorias": 125.0, "proteinas": 0.6, "carboidratos": 30.1, "gorduras": 0.3, "fibras": 1.6, "sodio": 1.0, "calcio": 19.0, "ferro": 0.1, "potassio": 100.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 11.1},
    "mandioca_crua": {"nome": "Mandioca, crua", "calorias": 151.0, "proteinas": 1.1, "carboidratos": 36.2, "gorduras": 0.3, "fibras": 1.9, "sodio": 2.0, "calcio": 15.0, "ferro": 0.3, "potassio": 208.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 16.5},
    "mandioca_farofa_temperada": {"nome": "Mandioca, farofa, temperada", "calorias": 406.0, "proteinas": 2.1, "carboidratos": 80.3, "gorduras": 9.1, "fibras": 7.8, "sodio": 575.0, "calcio": 66.0, "ferro": 1.4, "potassio": 201.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 0},
    "mandioca_frita": {"nome": "Mandioca, frita", "calorias": 300.0, "proteinas": 1.4, "carboidratos": 50.3, "gorduras": 11.2, "fibras": 1.9, "sodio": 9.0, "calcio": 23.0, "ferro": 0.3, "potassio": 176.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 0},
    "manjericao_cru": {"nome": "Manjericão, cru", "calorias": 21.0, "proteinas": 2.0, "carboidratos": 3.6, "gorduras": 0.4, "fibras": 3.3, "sodio": 4.0, "calcio": 211.0, "ferro": 1.0, "potassio": 252.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 2.3},
    "maxixe_cru": {"nome": "Maxixe, cru", "calorias": 14.0, "proteinas": 1.4, "carboidratos": 2.7, "gorduras": 0.1, "fibras": 2.2, "sodio": 11.0, "calcio": 21.0, "ferro": 0.4, "potassio": 328.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 9.6},
    "mostarda_folha_crua": {"nome": "Mostarda, folha, crua", "calorias": 18.0, "proteinas": 2.1, "carboidratos": 3.2, "gorduras": 0.2, "fibras": 1.9, "sodio": 3.0, "calcio": 68.0, "ferro": 1.1, "potassio": 364.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 38.6},
    "nabo_cru": {"nome": "Nabo, cru", "calorias": 18.0, "proteinas": 1.2, "carboidratos": 4.1, "gorduras": 0.1, "fibras": 2.6, "sodio": 2.0, "calcio": 42.0, "ferro": 0.2, "potassio": 280.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 9.6},
    "nhoque_batata_cozido": {"nome": "Nhoque, batata, cozido", "calorias": 181.0, "proteinas": 5.9, "carboidratos": 36.8, "gorduras": 1.9, "fibras": 1.8, "sodio": 7.0, "calcio": 11.0, "ferro": 1.6, "potassio": 164.0, "zinco": 0.5, "colesterol": 15.0, "vitamina_c": 0},
    "palmito_jucara_em_conserva": {"nome": "Palmito, juçara, em conserva", "calorias": 23.0, "proteinas": 1.8, "carboidratos": 4.3, "gorduras": 0.4, "fibras": 3.2, "sodio": 514.0, "calcio": 58.0, "ferro": 0.3, "potassio": 244.0, "zinco": 0.7, "colesterol": 0, "vitamina_c": 2.0},
    "palmito_pupunha_em_conserva": {"nome": "Palmito, pupunha, em conserva", "calorias": 29.0, "proteinas": 2.5, "carboidratos": 5.5, "gorduras": 0.5, "fibras": 2.6, "sodio": 563.0, "calcio": 32.0, "ferro": 0.2, "potassio": 206.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 8.7},
    "pao_de_queijo_assado": {"nome": "Pão, de queijo, assado", "calorias": 363.0, "proteinas": 5.1, "carboidratos": 34.2, "gorduras": 24.6, "fibras": 0.6, "sodio": 773.0, "calcio": 102.0, "ferro": 0.3, "potassio": 93.0, "zinco": 0.6, "colesterol": 68.0, "vitamina_c": 0},
    "pao_de_queijo_cru": {"nome": "Pão, de queijo, cru", "calorias": 295.0, "proteinas": 3.6, "carboidratos": 38.5, "gorduras": 14.0, "fibras": 1.0, "sodio": 405.0, "calcio": 88.0, "ferro": 0.3, "potassio": 58.0, "zinco": 0.4, "colesterol": 63.0, "vitamina_c": 0},
    "pepino_cru": {"nome": "Pepino, cru", "calorias": 10.0, "proteinas": 0.9, "carboidratos": 2.0, "gorduras": 0, "fibras": 1.1, "sodio": 0, "calcio": 10.0, "ferro": 0.1, "potassio": 154.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 5.0},
    "pimentao_amarelo_cru": {"nome": "Pimentão, amarelo, cru", "calorias": 28.0, "proteinas": 1.2, "carboidratos": 6.0, "gorduras": 0.4, "fibras": 1.9, "sodio": 0, "calcio": 10.0, "ferro": 0.4, "potassio": 221.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 201.4},
    "pimentao_verde_cru": {"nome": "Pimentão, verde, cru", "calorias": 21.0, "proteinas": 1.1, "carboidratos": 4.9, "gorduras": 0.2, "fibras": 2.6, "sodio": 0, "calcio": 9.0, "ferro": 0.4, "potassio": 174.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 100.2},
    "pimentao_vermelho_cru": {"nome": "Pimentão, vermelho, cru", "calorias": 23.0, "proteinas": 1.0, "carboidratos": 5.5, "gorduras": 0.1, "fibras": 1.6, "sodio": 0, "calcio": 6.0, "ferro": 0.3, "potassio": 211.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 158.2},
    "polvilho_doce": {"nome": "Polvilho, doce", "calorias": 351.0, "proteinas": 0.4, "carboidratos": 86.8, "gorduras": 0, "fibras": 0.2, "sodio": 2.0, "calcio": 27.0, "ferro": 0.5, "potassio": 38.0, "zinco": 0, "colesterol": 0, "vitamina_c": 0},
    "quiabo_cru": {"nome": "Quiabo, cru", "calorias": 30.0, "proteinas": 1.9, "carboidratos": 6.4, "gorduras": 0.3, "fibras": 4.6, "sodio": 1.0, "calcio": 112.0, "ferro": 0.4, "potassio": 249.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 5.6},
    "rabanete_cru": {"nome": "Rabanete, cru", "calorias": 14.0, "proteinas": 1.4, "carboidratos": 2.7, "gorduras": 0.1, "fibras": 2.2, "sodio": 11.0, "calcio": 21.0, "ferro": 0.4, "potassio": 328.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 9.6},
    "repolho_branco_cru": {"nome": "Repolho, branco, cru", "calorias": 17.0, "proteinas": 0.9, "carboidratos": 3.9, "gorduras": 0.1, "fibras": 1.9, "sodio": 4.0, "calcio": 35.0, "ferro": 0.2, "potassio": 150.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 18.7},
    "repolho_roxo_cru": {"nome": "Repolho, roxo, cru", "calorias": 31.0, "proteinas": 1.9, "carboidratos": 7.2, "gorduras": 0.1, "fibras": 2.0, "sodio": 2.0, "calcio": 44.0, "ferro": 0.5, "potassio": 328.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 43.2},
    "repolho_roxo_refogado": {"nome": "Repolho, roxo, refogado", "calorias": 42.0, "proteinas": 1.8, "carboidratos": 7.6, "gorduras": 1.2, "fibras": 1.8, "sodio": 3.0, "calcio": 43.0, "ferro": 0.5, "potassio": 321.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 40.5},
    "rucula_crua": {"nome": "Rúcula, crua", "calorias": 13.0, "proteinas": 1.8, "carboidratos": 2.2, "gorduras": 0.1, "fibras": 1.7, "sodio": 9.0, "calcio": 117.0, "ferro": 0.9, "potassio": 233.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 46.3},
    "salsa_crua": {"nome": "Salsa, crua", "calorias": 33.0, "proteinas": 3.3, "carboidratos": 5.7, "gorduras": 0.6, "fibras": 1.9, "sodio": 2.0, "calcio": 179.0, "ferro": 3.2, "potassio": 711.0, "zinco": 1.3, "colesterol": 0, "vitamina_c": 51.7},
    "seleta_de_legumes_enlatada": {"nome": "Seleta de legumes, enlatada", "calorias": 57.0, "proteinas": 3.4, "carboidratos": 12.7, "gorduras": 0.4, "fibras": 3.1, "sodio": 398.0, "calcio": 16.0, "ferro": 1.1, "potassio": 122.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 0},
    "serralha_crua": {"nome": "Serralha, crua", "calorias": 30.0, "proteinas": 2.7, "carboidratos": 4.9, "gorduras": 0.7, "fibras": 3.5, "sodio": 19.0, "calcio": 126.0, "ferro": 1.3, "potassio": 265.0, "zinco": 1.3, "colesterol": 0, "vitamina_c": 1.5},
    "taioba_crua": {"nome": "Taioba, crua", "calorias": 34.0, "proteinas": 2.9, "carboidratos": 5.4, "gorduras": 0.9, "fibras": 4.5, "sodio": 1.0, "calcio": 141.0, "ferro": 1.9, "potassio": 290.0, "zinco": 0.6, "colesterol": 0, "vitamina_c": 17.9},
    "tomate_com_semente_cru": {"nome": "Tomate, com semente, cru", "calorias": 15.0, "proteinas": 1.1, "carboidratos": 3.1, "gorduras": 0.2, "fibras": 1.2, "sodio": 1.0, "calcio": 7.0, "ferro": 0.2, "potassio": 222.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 21.2},
    "tomate_extrato": {"nome": "Tomate, extrato", "calorias": 61.0, "proteinas": 2.4, "carboidratos": 15.0, "gorduras": 0.2, "fibras": 2.8, "sodio": 498.0, "calcio": 29.0, "ferro": 2.1, "potassio": 680.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 18.0},
    "tomate_molho_industrializado": {"nome": "Tomate, molho industrializado", "calorias": 38.0, "proteinas": 1.4, "carboidratos": 7.7, "gorduras": 0.9, "fibras": 3.1, "sodio": 418.0, "calcio": 12.0, "ferro": 1.6, "potassio": 388.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 2.7},
    "tomate_pure": {"nome": "Tomate, purê", "calorias": 28.0, "proteinas": 1.4, "carboidratos": 6.9, "gorduras": 0, "fibras": 1.0, "sodio": 104.0, "calcio": 13.0, "ferro": 1.3, "potassio": 308.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 5.4},
    "tomate_salada": {"nome": "Tomate, salada", "calorias": 21.0, "proteinas": 0.8, "carboidratos": 5.1, "gorduras": 0, "fibras": 2.3, "sodio": 5.0, "calcio": 7.0, "ferro": 0.3, "potassio": 161.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 12.8},
    "vagem_crua": {"nome": "Vagem, crua", "calorias": 25.0, "proteinas": 1.8, "carboidratos": 5.3, "gorduras": 0.2, "fibras": 2.4, "sodio": 0, "calcio": 41.0, "ferro": 0.4, "potassio": 208.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 1.2},

    # === Entradas adicionais (valores TACO/referência nutricional) ===
    "azeite_de_oliva": {"nome": "Azeite de oliva", "calorias": 884.0, "proteinas": 0.0, "carboidratos": 0.0, "gorduras": 100.0, "fibras": 0.0, "sodio": 2, "calcio": 1.0, "ferro": 0.5, "potassio": 1.0, "zinco": 0.0, "colesterol": 0, "vitamina_c": 0.0},
    "canela_em_po": {"nome": "Canela em pó", "calorias": 261.0, "proteinas": 4.0, "carboidratos": 56.0, "gorduras": 3.2, "fibras": 24.4, "sodio": 26, "calcio": 1228.0, "ferro": 38.1, "potassio": 500.0, "zinco": 1.9, "colesterol": 0, "vitamina_c": 28.5},
    "gengibre_cru": {"nome": "Gengibre, cru", "calorias": 80.0, "proteinas": 1.8, "carboidratos": 18.0, "gorduras": 0.8, "fibras": 2.0, "sodio": 13, "calcio": 16.0, "ferro": 0.6, "potassio": 415.0, "zinco": 0.3, "colesterol": 0, "vitamina_c": 5.0},
    "curry_em_po": {"nome": "Curry em pó", "calorias": 325.0, "proteinas": 14.3, "carboidratos": 55.8, "gorduras": 14.0, "fibras": 33.2, "sodio": 52, "calcio": 525.0, "ferro": 29.6, "potassio": 1170.0, "zinco": 4.1, "colesterol": 0, "vitamina_c": 11.4},
    "cogumelo_champignon_conserva": {"nome": "Cogumelo champignon, conserva", "calorias": 22.0, "proteinas": 1.9, "carboidratos": 3.3, "gorduras": 0.3, "fibras": 1.5, "sodio": 400, "calcio": 8.0, "ferro": 0.9, "potassio": 115.0, "zinco": 0.5, "colesterol": 0, "vitamina_c": 0.0},
    "vinagre": {"nome": "Vinagre", "calorias": 18.0, "proteinas": 0.0, "carboidratos": 0.7, "gorduras": 0.0, "fibras": 0.0, "sodio": 2, "calcio": 6.0, "ferro": 0.0, "potassio": 2.0, "zinco": 0.0, "colesterol": 0, "vitamina_c": 0.0},
    "alho_cru": {"nome": "Alho, cru", "calorias": 113.0, "proteinas": 7.0, "carboidratos": 23.9, "gorduras": 0.2, "fibras": 4.3, "sodio": 3, "calcio": 14.0, "ferro": 0.8, "potassio": 535.0, "zinco": 1.0, "colesterol": 0, "vitamina_c": 17.0},
    "extrato_de_tomate": {"nome": "Tomate, extrato", "calorias": 61.0, "proteinas": 2.8, "carboidratos": 11.3, "gorduras": 0.7, "fibras": 2.0, "sodio": 580, "calcio": 20.0, "ferro": 1.5, "potassio": 400.0, "zinco": 0.4, "colesterol": 0, "vitamina_c": 15.0},
    "achocolatado_em_po": {"nome": "Achocolatado em pó", "calorias": 401.0, "proteinas": 5.0, "carboidratos": 83.5, "gorduras": 5.8, "fibras": 3.4, "sodio": 110, "calcio": 46.0, "ferro": 3.6, "potassio": 400.0, "zinco": 1.5, "colesterol": 0, "vitamina_c": 0.0},
    "mel": {"nome": "Mel de abelha", "calorias": 309.0, "proteinas": 0.3, "carboidratos": 84.0, "gorduras": 0.0, "fibras": 0.0, "sodio": 7, "calcio": 4.0, "ferro": 0.4, "potassio": 52.0, "zinco": 0.2, "colesterol": 0, "vitamina_c": 0.8},
    "sal_grosso": {"nome": "Sal grosso", "calorias": 0.0, "proteinas": 0.0, "carboidratos": 0.0, "gorduras": 0.0, "fibras": 0.0, "sodio": 38758, "calcio": 24.0, "ferro": 0.3, "potassio": 8.0, "zinco": 0.1, "colesterol": 0, "vitamina_c": 0.0},
    "esfirra_de_carne_assada": {"nome": "Esfirra de carne, assada", "calorias": 280.0, "proteinas": 10.0, "carboidratos": 30.0, "gorduras": 13.0, "fibras": 1.5, "sodio": 350, "calcio": 30.0, "ferro": 2.0, "potassio": 150.0, "zinco": 1.5, "colesterol": 25, "vitamina_c": 0.0},
    "peixe_galo_file_cru": {"nome": "Peixe, filé, cru", "calorias": 96.0, "proteinas": 19.4, "carboidratos": 0.0, "gorduras": 2.0, "fibras": 0.0, "sodio": 65, "calcio": 12.0, "ferro": 0.5, "potassio": 350.0, "zinco": 0.4, "colesterol": 50, "vitamina_c": 0.0},

}


# ═══════════════════════════════════════════════════════════════════════════════
# MAPEAMENTO DE INGREDIENTES COMUNS PARA CHAVES TACO
# ═══════════════════════════════════════════════════════════════════════════════
INGREDIENTE_PARA_TACO = {
    # Carnes bovinas
    "carne": "carne_bovina_acem_moido_cozido", "carne bovina": "carne_bovina_acem_moido_cozido",
    "carne moída": "carne_bovina_acem_moido_cozido", "carne moida": "carne_bovina_acem_moido_cozido",
    "alcatra": "carne_bovina_miolo_de_alcatra_sem_gordura_grelhado",
    "picanha": "carne_bovina_picanha_sem_gordura_grelhada",
    "maminha": "carne_bovina_maminha_grelhada", "costela": "carne_bovina_costela_assada",
    "fígado": "carne_bovina_figado_grelhado", "figado": "carne_bovina_figado_grelhado",
    "acém": "carne_bovina_acem_moido_cru",
    "patinho": "carne_bovina_patinho_sem_gordura_grelhado",
    "contra filé": "carne_bovina_contra_file_sem_gordura_grelhado",
    "contra file": "carne_bovina_contra_file_sem_gordura_grelhado",
    "cupim": "carne_bovina_cupim_assado",
    "filé mignon": "carne_bovina_file_mingnon_sem_gordura_grelhado",
    "file mignon": "carne_bovina_file_mingnon_sem_gordura_grelhado",
    "carne seca": "carne_bovina_seca_cozida", "charque": "carne_bovina_charque_cozido",
    "frango/peixe/filé mignon": "frango_peito_sem_pele_grelhado",
    "frango/peixe/f mignon": "frango_peito_sem_pele_grelhado",
    
    # Carnes suínas
    "porco": "porco_lombo_assado", "lombo": "porco_lombo_assado",
    "bacon": "toucinho_frito", "bacon artesanal": "toucinho_frito",
    "toucinho": "toucinho_frito",
    "linguiça": "linguica_porco_grelhada", "linguica": "linguica_porco_grelhada",
    "presunto": "presunto_sem_capa_de_gordura", "salsicha": "linguica_frango_crua",
    "pernil": "porco_pernil_assado", "bisteca": "porco_bisteca_grelhada",
    
    # Aves
    "frango": "frango_peito_sem_pele_grelhado", "peito de frango": "frango_peito_sem_pele_grelhado",
    "coxa de frango": "frango_coxa_sem_pele_cozida", "coxa": "frango_coxa_sem_pele_cozida",
    "asa de frango": "frango_asa_com_pele_crua", "sobrecoxa": "frango_coxa_sem_pele_cozida",
    "peru": "peru_congelado_assado", "pato": "peru_congelado_assado",
    "frango frito": "frango_inteiro_sem_pele_cru",
    
    # Peixes
    "salmão": "salmao_sem_pele_fresco_grelhado", "salmon": "salmao_sem_pele_fresco_grelhado",
    "salmao": "salmao_sem_pele_fresco_grelhado",
    "bacalhau": "bacalhau_salgado_cru",
    "tilápia": "peixe_galo_file_cru", "tilapia": "peixe_galo_file_cru",
    "atum": "atum_fresco_cru", "atum fresco": "atum_fresco_cru",
    "sardinha": "sardinha_inteira_crua", "merluza": "merluza_file_assado",
    "pescada": "pescada_file_frito", "peixe": "peixe_galo_file_cru",
    
    # Frutos do mar
    "camarão": "camarao_rio_grande_grande_cozido", "camarao": "camarao_rio_grande_grande_cozido",
    "camaroes": "camarao_rio_grande_grande_cozido",
    "lula": "camarao_rio_grande_grande_cru",
    "polvo": "camarao_rio_grande_grande_cozido",
    "marisco": "camarao_rio_grande_grande_cru",
    "lagosta": "camarao_rio_grande_grande_cozido",
    "ostra": "camarao_rio_grande_grande_cru",
    
    # Ovos e laticínios
    "ovo": "ovo_de_galinha_inteiro_cozido_10minutos", "ovos": "ovo_de_galinha_inteiro_cozido_10minutos",
    "ovo frito": "ovo_de_galinha_inteiro_frito",
    "clara": "ovo_de_galinha_clara_cozida_10minutos",
    "queijo": "queijo_minas_frescal", "queijo minas": "queijo_minas_frescal",
    "queijo prato": "queijo_prato",
    "mussarela": "queijo_prato", "mozzarella": "queijo_prato",
    "queijo coalho": "queijo_minas_meia_cura", "queijo vegano": "queijo_minas_frescal",
    "parmesao": "queijo_prato", "queijo parmesao": "queijo_prato",
    "parmesan": "queijo_prato", "parmigiano": "queijo_prato",
    "gorgonzola": "queijo_prato",
    "ricota": "queijo_minas_frescal",
    "requeijão": "queijo_minas_frescal", "requeijao": "queijo_minas_frescal",
    "leite": "leite_de_vaca_integral", "iogurte": "iogurte_natural",
    "manteiga": "manteiga_com_sal",
    "creme de leite": "creme_de_leite", "creme de leite fresco": "creme_de_leite",
    "creme vegetal": "margarina_com_oleo_interesterificado_com_sal_65_de_lipideos",
    "natas": "creme_de_leite",
    
    # Grãos e cereais
    "arroz": "arroz_tipo_1_cozido", "arroz branco": "arroz_tipo_1_cozido",
    "arroz integral": "arroz_integral_cozido", "arroz integral selecionado": "arroz_integral_cozido",
    "arroz arboreo": "arroz_tipo_1_cozido",
    "feijão": "feijao_preto_cozido", "feijão preto": "feijao_preto_cozido",
    "feijão carioca": "feijao_carioca_cozido", "feijao": "feijao_preto_cozido",
    "feijao-de-corda": "feijao_carioca_cozido", "feijão-de-corda": "feijao_carioca_cozido",
    "lentilha": "lentilha_cozida", "grão de bico": "grao_de_bico_cru",
    "grão-de-bico": "grao_de_bico_cru", "quinoa": "farinha_de_centeio_integral",
    "aveia": "aveia_flocos_crua", "milho": "milho_verde_enlatado_drenado",
    "ervilha": "ervilha_em_vagem", "linhaca": "aveia_flocos_crua",
    "centeio": "farinha_de_centeio_integral", "cevada": "farinha_de_centeio_integral",
    "trigo": "farinha_de_trigo",
    
    # Vegetais
    "brócolis": "brocolis_cozido", "brocolis": "brocolis_cozido",
    "couve-flor": "couve_flor_crua", "couve flor": "couve_flor_crua",
    "cenoura": "cenoura_crua", "cenouras": "cenoura_crua",
    "espinafre": "espinafre_nova_zelandia_cru",
    "abóbora": "abobora_moranga_crua", "abobora": "abobora_moranga_crua",
    "tomate": "tomate_com_semente_cru", "tomates": "tomate_com_semente_cru",
    "batata": "batata_inglesa_cozida", "batatas": "batata_inglesa_cozida",
    "batata doce": "batata_doce_cozida", "batata-doce": "batata_doce_cozida",
    "alface": "alface_americana_crua", "couve": "couve_manteiga_crua",
    "berinjela": "berinjela_crua", "beringela": "berinjela_crua",
    "abobrinha": "abobrinha_italiana_crua",
    "chuchu": "chuchu_cozido", "beterraba": "beterraba_crua",
    "pepino": "pepino_cru", "pimentão": "pimentao_verde_cru", "pimentao": "pimentao_verde_cru",
    "vagem": "vagem_crua", "mandioca": "mandioca_cozida",
    "inhame": "inhame_cru", "cebola": "cebola_crua",
    "repolho": "repolho_branco_cru",
    "mandioquinha": "batata_inglesa_cozida", "baroa": "batata_inglesa_cozida",
    "alho poro": "cebola_crua",
    "champignon": "cogumelo_champignon_conserva", "cogumelo": "cogumelo_champignon_conserva",
    "funghi secchi": "cogumelo_champignon_conserva",
    "azeitonas": "azeitona_preta_conserva", "azeitona": "azeitona_preta_conserva",
    
    # Frutas
    "banana": "banana_prata_crua", "maçã": "maca_fuji_com_casca_crua", "maca": "maca_fuji_com_casca_crua",
    "laranja": "laranja_pera_crua", "abacate": "abacate_cru",
    "mamão": "mamao_papaia_cru", "mamao": "mamao_papaia_cru",
    "melancia": "melancia_crua", "abacaxi": "abacaxi_cru",
    "manga": "manga_palmer_crua", "uva": "uva_italia_crua",
    "morango": "morango_cru", "acerola": "acerola_crua",
    "goiaba": "goiaba_branca_com_casca_crua", "kiwi": "kiwi_cru",
    "limão": "limao_tahiti_cru", "limao": "limao_tahiti_cru",
    "melao": "melao_cru",
    "uva passa": "uva_italia_crua", "damasco": "manga_palmer_crua",
    "laranja kimcan": "laranja_pera_crua",
    
    # Massas e pães
    "macarrão": "macarrao_trigo_cru", "macarrao": "macarrao_trigo_cru",
    "massa": "macarrao_trigo_cru",
    "lasanha": "lasanha_massa_fresca_cozida",
    "pão": "pao_trigo_frances", "pão francês": "pao_trigo_frances", "pao": "pao_trigo_frances",
    "pão integral": "pao_trigo_forma_integral",
    "pizza": "pao_trigo_frances", "nhoque": "nhoque_batata_cozido",
    "farinha de rosca": "farinha_de_rosca", "farinha de trigo": "farinha_de_trigo",
    "farinha": "farinha_de_trigo",
    
    # Temperos e condimentos
    "sal": "sal_grosso", "alho": "alho_cru", "alho ": "alho_cru",
    "gengibre": "gengibre_cru", "gengibre fresco": "gengibre_cru",
    "canela": "canela_em_po",
    "noz-moscada": "noz_crua", "noz moscada": "noz_crua",
    "vinagre": "vinagre", "vinagre balsamico": "vinagre",
    "salsinha": "salsa_crua", "salsa": "salsa_crua", "cheiro verde": "salsa_crua",
    "manjericao": "salsa_crua", "ervas frescas": "salsa_crua", "ervas secas": "salsa_crua",
    "tomilho": "salsa_crua",
    "curry indiano": "curry_em_po", "curry indiano importado": "curry_em_po", "curry": "curry_em_po",
    "paprica defumada": "pimentao_verde_cru", "paprica": "pimentao_verde_cru",
    "temperos": "cebola_crua",
    "especiarias": "canela_em_po", "especiarias importadas": "canela_em_po",
    "oregano": "salsa_crua",
    
    # Óleos e gorduras
    "azeite": "azeite_de_oliva", "azeite de oliva": "azeite_de_oliva",
    "oleo vegetal": "oleo_de_soja", "oleo": "oleo_de_soja",
    "manteiga vegana": "margarina_com_oleo_interesterificado_com_sal_65_de_lipideos",
    "manteiga vegetal": "margarina_com_oleo_interesterificado_com_sal_65_de_lipideos",
    "manteiga fresca": "manteiga_com_sal",
    
    # Doces e outros
    "acucar": "acucar_cristal", "açúcar": "acucar_cristal",
    "chocolate": "achocolatado_em_po", "cacau em po": "achocolatado_em_po",
    "maple": "mel", "maple canadense": "mel",
    "tahine": "amendoim_torrado_salgado",
    "molho de tomate": "extrato_de_tomate", "molho de tomate artesanal": "extrato_de_tomate",
    "kewpie": "maionese_tradicional_com_ovos",
    "caldo de carne": "caldo_de_carne_tablete", "caldo de legumes": "caldo_de_carne_tablete",
    "vinho branco": "cerveja_pilsen_2",
    "molho tare": "acucar_cristal",
    "fermento": "farinha_de_trigo",
    "leite vegetal": "leite_de_vaca_integral",
    "leite de coco": "leite_de_coco",
    
    # Preparações típicas
    "feijoada": "feijoada", "estrogonofe": "estrogonofe_de_frango",
    "strogonoff": "estrogonofe_de_frango",
    "farofa": "mandioca_farofa_temperada",
    "baião de dois": "baiao_de_dois_arroz_e_feijao_de_corda",
    "coxinha": "coxinha_de_frango_frita",
    "esfiha": "esfirra_de_carne_assada",
    "salpicão": "salpicao_de_frango",
    "maionese": "maionese_tradicional_com_ovos",
    
    # Sobremesas
    "pudim": "leite_condensado", "bolo": "bolo_pronto_chocolate",
    "sorvete": "iogurte_natural",
    "gelatina": "gelatina_sabores_variados_po",
    
    # Bebidas
    "suco": "laranja_baia_suco", "café": "cafe_infusao_10",
    "refrigerante": "refrigerante_tipo_cola", "cha": "cha_mate_infusao_5",
    "cerveja": "cerveja_pilsen_2",
    
    # Oleaginosas
    "castanha": "castanha_do_brasil_crua", "castanha-do-pará": "castanha_do_brasil_crua",
    "castanhas de caju": "castanha_de_caju_torrada_salgada",
    "castanha de caju": "castanha_de_caju_torrada_salgada",
    "amendoim": "amendoim_torrado_salgado", "nozes": "noz_crua",
    "amêndoas": "amendoa_torrada_salgada", "amendoas": "amendoa_torrada_salgada",
}


def buscar_dados_taco(ingrediente: str) -> dict:
    """Busca dados nutricionais de um ingrediente na Tabela TACO."""
    import unicodedata
    import re
    
    # Normalizar input
    ingrediente_norm = unicodedata.normalize('NFKD', ingrediente.lower().strip())
    ingrediente_norm = ingrediente_norm.encode('ASCII', 'ignore').decode('ASCII')
    ingrediente_key = re.sub(r'[^\w\s]', ' ', ingrediente_norm)
    ingrediente_key = re.sub(r'\s+', '_', ingrediente_key.strip())
    
    # 1. Busca direta no TACO_DATABASE
    if ingrediente_key in TACO_DATABASE:
        return TACO_DATABASE[ingrediente_key]
    
    # 2. Busca via mapeamento
    ingrediente_lower = ingrediente.lower().strip()
    if ingrediente_lower in INGREDIENTE_PARA_TACO:
        chave = INGREDIENTE_PARA_TACO[ingrediente_lower]
        return TACO_DATABASE.get(chave)
    
    # 3. Busca parcial no mapeamento
    for termo, chave in INGREDIENTE_PARA_TACO.items():
        if termo in ingrediente_lower or ingrediente_lower in termo:
            return TACO_DATABASE.get(chave)
    
    # 4. Busca parcial direta no TACO_DATABASE (melhorada)
    palavras = ingrediente_key.split('_')
    for taco_key in TACO_DATABASE.keys():
        # Busca se todas as palavras do ingrediente estão na chave TACO
        if all(p in taco_key for p in palavras if len(p) > 2):
            return TACO_DATABASE[taco_key]
    
    # 5. Busca por palavra principal (para carnes)
    palavra_principal = max(palavras, key=len) if palavras else ''
    if len(palavra_principal) >= 4:
        for taco_key in TACO_DATABASE.keys():
            if palavra_principal in taco_key:
                # Preferir versão grelhada/cozida
                if 'grelhad' in taco_key or 'cozid' in taco_key:
                    return TACO_DATABASE[taco_key]
        # Se não achou grelhada, pegar qualquer uma
        for taco_key in TACO_DATABASE.keys():
            if palavra_principal in taco_key:
                return TACO_DATABASE[taco_key]
    
    return None


def calcular_nutricao_prato(ingredientes: list, porcao_gramas: int = 200) -> dict:
    """Calcula a nutrição total de um prato baseado nos ingredientes."""
    if not ingredientes:
        return None
    
    gramas_por_ingrediente = porcao_gramas / len(ingredientes)
    
    totais = {
        "calorias": 0, "proteinas": 0, "carboidratos": 0, "gorduras": 0, "fibras": 0,
        "sodio": 0, "calcio": 0, "ferro": 0, "vitamina_a": 0, "vitamina_c": 0,
        "vitamina_b12": 0, "potassio": 0, "zinco": 0, "acucar": 0,
        "ingredientes_encontrados": [], "ingredientes_nao_encontrados": []
    }
    
    for ingrediente in ingredientes:
        dados = buscar_dados_taco(ingrediente)
        if dados:
            fator = gramas_por_ingrediente / 100
            for key in ["calorias", "proteinas", "carboidratos", "gorduras", "fibras",
                       "sodio", "calcio", "ferro", "vitamina_a", "vitamina_c",
                       "vitamina_b12", "potassio", "zinco", "acucar"]:
                totais[key] += dados.get(key, 0) * fator
            totais["ingredientes_encontrados"].append(ingrediente)
        else:
            totais["ingredientes_nao_encontrados"].append(ingrediente)
    
    return totais


# Valores Diários de Referência (VDR) - base para %
VDR = {
    "calorias": 2000, "proteinas": 50, "carboidratos": 300, "gorduras": 65,
    "fibras": 25, "sodio": 2400, "calcio": 1000, "ferro": 14, "vitamina_a": 800,
    "vitamina_c": 90, "vitamina_b12": 2.4, "potassio": 4700, "zinco": 11, "acucar": 50
}


def calcular_percentual_vdr(nutriente: str, valor: float) -> float:
    """Calcula o percentual do VDR para um nutriente."""
    if nutriente in VDR and VDR[nutriente] > 0:
        return (valor / VDR[nutriente]) * 100
    return 0


def get_taco_info(alimento_key: str) -> dict:
    """Alias para buscar_dados_taco."""
    return buscar_dados_taco(alimento_key)


def search_taco(termo: str, limit: int = 10) -> list:
    """Busca alimentos por termo. Retorna lista de matches."""
    import unicodedata
    termo_norm = unicodedata.normalize('NFKD', termo.lower()).encode('ASCII', 'ignore').decode('ASCII')
    
    results = []
    for key, data in TACO_DATABASE.items():
        nome_norm = unicodedata.normalize('NFKD', data['nome'].lower()).encode('ASCII', 'ignore').decode('ASCII')
        if termo_norm in nome_norm or termo_norm in key:
            results.append({"key": key, "nome": data["nome"], "calorias": data["calorias"]})
            if len(results) >= limit:
                break
    
    return results
