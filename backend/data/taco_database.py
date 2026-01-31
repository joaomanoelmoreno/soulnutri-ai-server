# -*- coding: utf-8 -*-
"""
TABELA TACO EXPANDIDA - ~150 alimentos brasileiros
Fonte: UNICAMP/NEPA + Estimativas baseadas em literatura científica

ZERO CRÉDITOS DE IA - 100% LOCAL
"""

TACO_DATABASE = {
    # ═══════════════════════════════════════════════════════════════
    # CARNES BOVINAS
    # ═══════════════════════════════════════════════════════════════
    "carne_bovina": {"nome": "Carne Bovina (patinho grelhado)", "calorias": 219, "proteinas": 35.9, "carboidratos": 0, "gorduras": 7.3, "fibras": 0, "sodio": 45, "calcio": 4, "ferro": 3.4, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 2.6, "potassio": 340, "zinco": 6.1},
    "picanha": {"nome": "Picanha Grelhada", "calorias": 289, "proteinas": 26.0, "carboidratos": 0, "gorduras": 20.0, "fibras": 0, "sodio": 52, "calcio": 6, "ferro": 2.8, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 2.4, "potassio": 310, "zinco": 5.5},
    "alcatra": {"nome": "Alcatra Grelhada", "calorias": 235, "proteinas": 32.0, "carboidratos": 0, "gorduras": 11.0, "fibras": 0, "sodio": 48, "calcio": 5, "ferro": 3.2, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 2.5, "potassio": 330, "zinco": 5.8},
    "costela": {"nome": "Costela Bovina Assada", "calorias": 375, "proteinas": 24.0, "carboidratos": 0, "gorduras": 30.0, "fibras": 0, "sodio": 55, "calcio": 10, "ferro": 2.5, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 2.2, "potassio": 280, "zinco": 5.0},
    "figado_bovino": {"nome": "Fígado Bovino", "calorias": 140, "proteinas": 21.0, "carboidratos": 4.0, "gorduras": 4.5, "fibras": 0, "sodio": 70, "calcio": 5, "ferro": 5.8, "vitamina_a": 5070, "vitamina_c": 1, "vitamina_b12": 83.0, "potassio": 313, "zinco": 4.0},
    "carne_moida": {"nome": "Carne Moída (magra)", "calorias": 212, "proteinas": 26.0, "carboidratos": 0, "gorduras": 12.0, "fibras": 0, "sodio": 75, "calcio": 10, "ferro": 2.6, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 2.4, "potassio": 318, "zinco": 5.3},
    "maminha": {"nome": "Maminha Grelhada", "calorias": 245, "proteinas": 28.0, "carboidratos": 0, "gorduras": 14.0, "fibras": 0, "sodio": 50, "calcio": 5, "ferro": 3.0, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 2.5, "potassio": 320, "zinco": 5.6},
    "cupim": {"nome": "Cupim Assado", "calorias": 310, "proteinas": 25.0, "carboidratos": 0, "gorduras": 23.0, "fibras": 0, "sodio": 58, "calcio": 8, "ferro": 2.4, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 2.3, "potassio": 290, "zinco": 5.2},
    
    # ═══════════════════════════════════════════════════════════════
    # CARNES SUÍNAS
    # ═══════════════════════════════════════════════════════════════
    "carne_porco": {"nome": "Lombo Suíno Assado", "calorias": 210, "proteinas": 27.0, "carboidratos": 0, "gorduras": 10.9, "fibras": 0, "sodio": 56, "calcio": 6, "ferro": 0.9, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0.7, "potassio": 380, "zinco": 2.3},
    "pernil_porco": {"nome": "Pernil Suíno Assado", "calorias": 262, "proteinas": 26.0, "carboidratos": 0, "gorduras": 17.0, "fibras": 0, "sodio": 62, "calcio": 8, "ferro": 1.1, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0.8, "potassio": 350, "zinco": 2.5},
    "bacon": {"nome": "Bacon Frito", "calorias": 541, "proteinas": 37.0, "carboidratos": 1.0, "gorduras": 42.0, "fibras": 0, "sodio": 1717, "calcio": 12, "ferro": 1.4, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0.9, "potassio": 505, "zinco": 3.2},
    "linguica": {"nome": "Linguiça (frita)", "calorias": 296, "proteinas": 16.0, "carboidratos": 2.0, "gorduras": 25.0, "fibras": 0, "sodio": 870, "calcio": 10, "ferro": 1.0, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0.8, "potassio": 220, "zinco": 2.0},
    "presunto": {"nome": "Presunto", "calorias": 145, "proteinas": 21.0, "carboidratos": 2.0, "gorduras": 6.0, "fibras": 0, "sodio": 1203, "calcio": 10, "ferro": 0.9, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0.7, "potassio": 287, "zinco": 2.1},
    "salsicha": {"nome": "Salsicha", "calorias": 257, "proteinas": 10.0, "carboidratos": 3.0, "gorduras": 23.0, "fibras": 0, "sodio": 1090, "calcio": 63, "ferro": 1.2, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0.8, "potassio": 150, "zinco": 1.5},
    
    # ═══════════════════════════════════════════════════════════════
    # AVES
    # ═══════════════════════════════════════════════════════════════
    "frango": {"nome": "Peito de Frango Grelhado", "calorias": 159, "proteinas": 32.0, "carboidratos": 0, "gorduras": 3.0, "fibras": 0, "sodio": 52, "calcio": 4, "ferro": 0.4, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0.6, "potassio": 370, "zinco": 0.8},
    "coxa_frango": {"nome": "Coxa de Frango (assada)", "calorias": 209, "proteinas": 26.0, "carboidratos": 0, "gorduras": 11.0, "fibras": 0, "sodio": 88, "calcio": 12, "ferro": 1.0, "vitamina_a": 48, "vitamina_c": 0, "vitamina_b12": 0.5, "potassio": 240, "zinco": 2.4},
    "frango_frito": {"nome": "Frango Frito Empanado", "calorias": 269, "proteinas": 22.0, "carboidratos": 11.0, "gorduras": 15.0, "fibras": 0.4, "sodio": 540, "calcio": 14, "ferro": 1.1, "vitamina_a": 20, "vitamina_c": 0, "vitamina_b12": 0.4, "potassio": 230, "zinco": 1.6},
    "peru": {"nome": "Peito de Peru", "calorias": 135, "proteinas": 30.0, "carboidratos": 0, "gorduras": 1.0, "fibras": 0, "sodio": 65, "calcio": 12, "ferro": 1.4, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0.4, "potassio": 293, "zinco": 2.0},
    "pato": {"nome": "Pato Assado", "calorias": 337, "proteinas": 19.0, "carboidratos": 0, "gorduras": 28.0, "fibras": 0, "sodio": 59, "calcio": 11, "ferro": 2.7, "vitamina_a": 77, "vitamina_c": 0, "vitamina_b12": 0.4, "potassio": 204, "zinco": 2.6},
    
    # ═══════════════════════════════════════════════════════════════
    # CORDEIRO
    # ═══════════════════════════════════════════════════════════════
    "cordeiro": {"nome": "Pernil de Cordeiro Assado", "calorias": 245, "proteinas": 26.0, "carboidratos": 0, "gorduras": 15.0, "fibras": 0, "sodio": 65, "calcio": 12, "ferro": 2.0, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 2.8, "potassio": 310, "zinco": 4.5},
    "carre_cordeiro": {"nome": "Carré de Cordeiro", "calorias": 294, "proteinas": 25.0, "carboidratos": 0, "gorduras": 21.0, "fibras": 0, "sodio": 72, "calcio": 15, "ferro": 1.8, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 2.6, "potassio": 290, "zinco": 4.2},
    
    # ═══════════════════════════════════════════════════════════════
    # PEIXES
    # ═══════════════════════════════════════════════════════════════
    "salmao": {"nome": "Salmão Grelhado", "calorias": 208, "proteinas": 27.3, "carboidratos": 0, "gorduras": 10.4, "fibras": 0, "sodio": 59, "calcio": 15, "ferro": 0.5, "vitamina_a": 50, "vitamina_c": 0, "vitamina_b12": 4.9, "potassio": 460, "zinco": 0.5, "omega3": 2.3},
    "bacalhau": {"nome": "Bacalhau (dessalgado, cozido)", "calorias": 136, "proteinas": 29.0, "carboidratos": 0, "gorduras": 1.5, "fibras": 0, "sodio": 1800, "calcio": 25, "ferro": 0.8, "vitamina_a": 12, "vitamina_c": 0, "vitamina_b12": 2.0, "potassio": 520, "zinco": 0.6},
    "tilapia": {"nome": "Tilápia Grelhada", "calorias": 129, "proteinas": 26.0, "carboidratos": 0, "gorduras": 2.7, "fibras": 0, "sodio": 56, "calcio": 14, "ferro": 0.7, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 1.9, "potassio": 380, "zinco": 0.4},
    "atum": {"nome": "Atum (enlatado em água)", "calorias": 116, "proteinas": 26.0, "carboidratos": 0, "gorduras": 1.0, "fibras": 0, "sodio": 320, "calcio": 11, "ferro": 1.3, "vitamina_a": 21, "vitamina_c": 0, "vitamina_b12": 2.9, "potassio": 252, "zinco": 0.8},
    "sardinha": {"nome": "Sardinha (enlatada)", "calorias": 208, "proteinas": 25.0, "carboidratos": 0, "gorduras": 11.0, "fibras": 0, "sodio": 505, "calcio": 382, "ferro": 2.9, "vitamina_a": 32, "vitamina_c": 0, "vitamina_b12": 8.9, "potassio": 397, "zinco": 1.3, "omega3": 1.5},
    "merluza": {"nome": "Merluza Assada", "calorias": 90, "proteinas": 18.0, "carboidratos": 0, "gorduras": 1.8, "fibras": 0, "sodio": 85, "calcio": 20, "ferro": 0.5, "vitamina_a": 10, "vitamina_c": 0, "vitamina_b12": 1.5, "potassio": 350, "zinco": 0.4},
    "pescada": {"nome": "Pescada Frita", "calorias": 172, "proteinas": 19.0, "carboidratos": 5.0, "gorduras": 8.5, "fibras": 0, "sodio": 110, "calcio": 25, "ferro": 0.6, "vitamina_a": 15, "vitamina_c": 0, "vitamina_b12": 1.8, "potassio": 320, "zinco": 0.5},
    "robalo": {"nome": "Robalo Grelhado", "calorias": 124, "proteinas": 24.0, "carboidratos": 0, "gorduras": 2.5, "fibras": 0, "sodio": 75, "calcio": 18, "ferro": 0.4, "vitamina_a": 20, "vitamina_c": 0, "vitamina_b12": 2.0, "potassio": 390, "zinco": 0.5},
    "linguado": {"nome": "Linguado Grelhado", "calorias": 117, "proteinas": 24.2, "carboidratos": 0, "gorduras": 1.5, "fibras": 0, "sodio": 88, "calcio": 21, "ferro": 0.4, "vitamina_a": 10, "vitamina_c": 0, "vitamina_b12": 2.1, "potassio": 370, "zinco": 0.5},
    "dourado": {"nome": "Dourado Assado", "calorias": 145, "proteinas": 25.0, "carboidratos": 0, "gorduras": 4.5, "fibras": 0, "sodio": 70, "calcio": 20, "ferro": 0.5, "vitamina_a": 15, "vitamina_c": 0, "vitamina_b12": 1.8, "potassio": 400, "zinco": 0.6},
    
    # ═══════════════════════════════════════════════════════════════
    # FRUTOS DO MAR
    # ═══════════════════════════════════════════════════════════════
    "camarao": {"nome": "Camarão Cozido", "calorias": 99, "proteinas": 20.9, "carboidratos": 0.2, "gorduras": 1.1, "fibras": 0, "sodio": 224, "calcio": 52, "ferro": 2.4, "vitamina_a": 54, "vitamina_c": 2, "vitamina_b12": 1.9, "potassio": 182, "zinco": 1.6},
    "lula": {"nome": "Lula Grelhada", "calorias": 92, "proteinas": 18.0, "carboidratos": 3.0, "gorduras": 1.4, "fibras": 0, "sodio": 44, "calcio": 32, "ferro": 0.9, "vitamina_a": 10, "vitamina_c": 4, "vitamina_b12": 1.3, "potassio": 246, "zinco": 1.5},
    "polvo": {"nome": "Polvo Cozido", "calorias": 82, "proteinas": 15.0, "carboidratos": 2.0, "gorduras": 1.0, "fibras": 0, "sodio": 230, "calcio": 53, "ferro": 5.3, "vitamina_a": 45, "vitamina_c": 0, "vitamina_b12": 20.0, "potassio": 350, "zinco": 1.7},
    "marisco": {"nome": "Marisco Cozido", "calorias": 86, "proteinas": 15.0, "carboidratos": 4.0, "gorduras": 1.0, "fibras": 0, "sodio": 286, "calcio": 56, "ferro": 5.5, "vitamina_a": 90, "vitamina_c": 1, "vitamina_b12": 12.0, "potassio": 314, "zinco": 2.1},
    "lagosta": {"nome": "Lagosta Cozida", "calorias": 98, "proteinas": 20.5, "carboidratos": 1.0, "gorduras": 0.6, "fibras": 0, "sodio": 380, "calcio": 96, "ferro": 0.4, "vitamina_a": 4, "vitamina_c": 0, "vitamina_b12": 1.4, "potassio": 220, "zinco": 4.0},
    "ostra": {"nome": "Ostra Crua", "calorias": 68, "proteinas": 7.0, "carboidratos": 4.0, "gorduras": 2.5, "fibras": 0, "sodio": 106, "calcio": 45, "ferro": 5.1, "vitamina_a": 90, "vitamina_c": 3, "vitamina_b12": 16.0, "potassio": 168, "zinco": 16.6},
    
    # ═══════════════════════════════════════════════════════════════
    # OVOS E LATICÍNIOS
    # ═══════════════════════════════════════════════════════════════
    "ovo": {"nome": "Ovo Cozido", "calorias": 146, "proteinas": 13.3, "carboidratos": 0.6, "gorduras": 9.5, "fibras": 0, "sodio": 146, "calcio": 49, "ferro": 1.6, "vitamina_a": 149, "vitamina_c": 0, "vitamina_b12": 1.3, "potassio": 121, "zinco": 1.1},
    "ovo_frito": {"nome": "Ovo Frito", "calorias": 196, "proteinas": 13.6, "carboidratos": 0.8, "gorduras": 15.3, "fibras": 0, "sodio": 207, "calcio": 54, "ferro": 1.9, "vitamina_a": 170, "vitamina_c": 0, "vitamina_b12": 1.1, "potassio": 152, "zinco": 1.3},
    "queijo_minas": {"nome": "Queijo Minas", "calorias": 264, "proteinas": 17.4, "carboidratos": 3.2, "gorduras": 20.2, "fibras": 0, "sodio": 710, "calcio": 579, "ferro": 0.3, "vitamina_a": 177, "vitamina_c": 0, "vitamina_b12": 1.3, "potassio": 123, "zinco": 2.8},
    "queijo_prato": {"nome": "Queijo Prato", "calorias": 357, "proteinas": 26.0, "carboidratos": 1.5, "gorduras": 28.0, "fibras": 0, "sodio": 600, "calcio": 800, "ferro": 0.4, "vitamina_a": 310, "vitamina_c": 0, "vitamina_b12": 1.5, "potassio": 90, "zinco": 3.5},
    "mussarela": {"nome": "Mussarela", "calorias": 280, "proteinas": 22.0, "carboidratos": 2.5, "gorduras": 21.0, "fibras": 0, "sodio": 505, "calcio": 505, "ferro": 0.4, "vitamina_a": 225, "vitamina_c": 0, "vitamina_b12": 0.7, "potassio": 76, "zinco": 2.9},
    "ricota": {"nome": "Ricota", "calorias": 140, "proteinas": 12.6, "carboidratos": 3.5, "gorduras": 8.0, "fibras": 0, "sodio": 84, "calcio": 207, "ferro": 0.4, "vitamina_a": 120, "vitamina_c": 0, "vitamina_b12": 0.3, "potassio": 105, "zinco": 1.2},
    "requeijao": {"nome": "Requeijão", "calorias": 257, "proteinas": 8.0, "carboidratos": 3.0, "gorduras": 24.0, "fibras": 0, "sodio": 420, "calcio": 150, "ferro": 0.2, "vitamina_a": 220, "vitamina_c": 0, "vitamina_b12": 0.3, "potassio": 100, "zinco": 1.0},
    "leite": {"nome": "Leite Integral", "calorias": 61, "proteinas": 3.2, "carboidratos": 4.7, "gorduras": 3.3, "fibras": 0, "sodio": 52, "calcio": 123, "ferro": 0.1, "vitamina_a": 46, "vitamina_c": 1, "vitamina_b12": 0.4, "potassio": 150, "zinco": 0.4},
    "iogurte": {"nome": "Iogurte Natural", "calorias": 62, "proteinas": 4.2, "carboidratos": 5.0, "gorduras": 3.0, "fibras": 0, "sodio": 50, "calcio": 143, "ferro": 0.1, "vitamina_a": 30, "vitamina_c": 1, "vitamina_b12": 0.5, "potassio": 187, "zinco": 0.6},
    
    # ═══════════════════════════════════════════════════════════════
    # CEREAIS E GRÃOS
    # ═══════════════════════════════════════════════════════════════
    "arroz_branco": {"nome": "Arroz Branco Cozido", "calorias": 128, "proteinas": 2.5, "carboidratos": 28.1, "gorduras": 0.2, "fibras": 1.6, "sodio": 1, "calcio": 4, "ferro": 0.1, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 29, "zinco": 0.5},
    "arroz_integral": {"nome": "Arroz Integral Cozido", "calorias": 124, "proteinas": 2.6, "carboidratos": 25.8, "gorduras": 1.0, "fibras": 2.7, "sodio": 2, "calcio": 5, "ferro": 0.3, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 79, "zinco": 0.6},
    "feijao_preto": {"nome": "Feijão Preto Cozido", "calorias": 77, "proteinas": 4.5, "carboidratos": 14.0, "gorduras": 0.5, "fibras": 8.4, "sodio": 2, "calcio": 29, "ferro": 1.5, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 256, "zinco": 0.9},
    "feijao_carioca": {"nome": "Feijão Carioca Cozido", "calorias": 76, "proteinas": 4.8, "carboidratos": 13.6, "gorduras": 0.5, "fibras": 8.5, "sodio": 2, "calcio": 27, "ferro": 1.3, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 245, "zinco": 0.8},
    "lentilha": {"nome": "Lentilha Cozida", "calorias": 93, "proteinas": 6.3, "carboidratos": 16.3, "gorduras": 0.5, "fibras": 7.9, "sodio": 2, "calcio": 16, "ferro": 2.0, "vitamina_a": 1, "vitamina_c": 1, "vitamina_b12": 0, "potassio": 302, "zinco": 1.0},
    "grao_de_bico": {"nome": "Grão-de-bico Cozido", "calorias": 130, "proteinas": 6.8, "carboidratos": 19.5, "gorduras": 2.4, "fibras": 5.4, "sodio": 5, "calcio": 45, "ferro": 2.1, "vitamina_a": 2, "vitamina_c": 1, "vitamina_b12": 0, "potassio": 270, "zinco": 1.2},
    "quinoa": {"nome": "Quinoa Cozida", "calorias": 120, "proteinas": 4.4, "carboidratos": 21.3, "gorduras": 1.9, "fibras": 2.8, "sodio": 7, "calcio": 17, "ferro": 1.5, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 172, "zinco": 1.1},
    "aveia": {"nome": "Aveia em Flocos", "calorias": 394, "proteinas": 14.0, "carboidratos": 66.0, "gorduras": 8.0, "fibras": 9.1, "sodio": 5, "calcio": 48, "ferro": 4.0, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 355, "zinco": 3.6},
    "milho": {"nome": "Milho Verde Cozido", "calorias": 96, "proteinas": 3.2, "carboidratos": 19.0, "gorduras": 1.4, "fibras": 2.4, "sodio": 1, "calcio": 3, "ferro": 0.5, "vitamina_a": 11, "vitamina_c": 6, "vitamina_b12": 0, "potassio": 218, "zinco": 0.5},
    
    # ═══════════════════════════════════════════════════════════════
    # VEGETAIS
    # ═══════════════════════════════════════════════════════════════
    "brocolis": {"nome": "Brócolis Cozido", "calorias": 25, "proteinas": 2.1, "carboidratos": 4.4, "gorduras": 0.5, "fibras": 3.4, "sodio": 10, "calcio": 51, "ferro": 0.5, "vitamina_a": 154, "vitamina_c": 42, "vitamina_b12": 0, "potassio": 229, "zinco": 0.4},
    "couve_flor": {"nome": "Couve-flor Cozida", "calorias": 23, "proteinas": 1.8, "carboidratos": 4.1, "gorduras": 0.3, "fibras": 2.3, "sodio": 15, "calcio": 16, "ferro": 0.3, "vitamina_a": 0, "vitamina_c": 28, "vitamina_b12": 0, "potassio": 142, "zinco": 0.2},
    "cenoura": {"nome": "Cenoura Crua", "calorias": 34, "proteinas": 1.3, "carboidratos": 7.7, "gorduras": 0.2, "fibras": 3.2, "sodio": 3, "calcio": 23, "ferro": 0.2, "vitamina_a": 933, "vitamina_c": 3, "vitamina_b12": 0, "potassio": 315, "zinco": 0.2},
    "espinafre": {"nome": "Espinafre Cozido", "calorias": 22, "proteinas": 2.6, "carboidratos": 2.4, "gorduras": 0.2, "fibras": 2.1, "sodio": 53, "calcio": 104, "ferro": 1.6, "vitamina_a": 524, "vitamina_c": 16, "vitamina_b12": 0, "potassio": 466, "zinco": 0.5},
    "abobora": {"nome": "Abóbora Cozida", "calorias": 28, "proteinas": 0.8, "carboidratos": 6.0, "gorduras": 0.1, "fibras": 1.6, "sodio": 1, "calcio": 17, "ferro": 0.3, "vitamina_a": 426, "vitamina_c": 7, "vitamina_b12": 0, "potassio": 222, "zinco": 0.2},
    "tomate": {"nome": "Tomate Cru", "calorias": 15, "proteinas": 1.1, "carboidratos": 3.1, "gorduras": 0.2, "fibras": 1.2, "sodio": 2, "calcio": 7, "ferro": 0.2, "vitamina_a": 54, "vitamina_c": 21, "vitamina_b12": 0, "potassio": 222, "zinco": 0.1, "licopeno": 2.6},
    "batata": {"nome": "Batata Cozida", "calorias": 52, "proteinas": 1.2, "carboidratos": 11.9, "gorduras": 0, "fibras": 1.3, "sodio": 2, "calcio": 4, "ferro": 0.3, "vitamina_a": 0, "vitamina_c": 6, "vitamina_b12": 0, "potassio": 302, "zinco": 0.2},
    "batata_doce": {"nome": "Batata-doce Cozida", "calorias": 77, "proteinas": 0.6, "carboidratos": 18.4, "gorduras": 0.1, "fibras": 2.2, "sodio": 6, "calcio": 17, "ferro": 0.2, "vitamina_a": 709, "vitamina_c": 23, "vitamina_b12": 0, "potassio": 230, "zinco": 0.2},
    "alface": {"nome": "Alface Crua", "calorias": 11, "proteinas": 1.3, "carboidratos": 1.7, "gorduras": 0.2, "fibras": 1.0, "sodio": 3, "calcio": 38, "ferro": 0.4, "vitamina_a": 166, "vitamina_c": 16, "vitamina_b12": 0, "potassio": 267, "zinco": 0.2},
    "couve": {"nome": "Couve Refogada", "calorias": 90, "proteinas": 2.9, "carboidratos": 6.3, "gorduras": 6.5, "fibras": 5.7, "sodio": 12, "calcio": 177, "ferro": 0.5, "vitamina_a": 385, "vitamina_c": 76, "vitamina_b12": 0, "potassio": 340, "zinco": 0.3},
    "berinjela": {"nome": "Berinjela Cozida", "calorias": 19, "proteinas": 0.7, "carboidratos": 4.5, "gorduras": 0.1, "fibras": 2.9, "sodio": 1, "calcio": 8, "ferro": 0.2, "vitamina_a": 3, "vitamina_c": 1, "vitamina_b12": 0, "potassio": 127, "zinco": 0.1},
    "abobrinha": {"nome": "Abobrinha Cozida", "calorias": 15, "proteinas": 0.6, "carboidratos": 3.0, "gorduras": 0.1, "fibras": 1.6, "sodio": 1, "calcio": 12, "ferro": 0.2, "vitamina_a": 25, "vitamina_c": 5, "vitamina_b12": 0, "potassio": 182, "zinco": 0.2},
    "chuchu": {"nome": "Chuchu Cozido", "calorias": 17, "proteinas": 0.4, "carboidratos": 3.6, "gorduras": 0.1, "fibras": 1.0, "sodio": 1, "calcio": 11, "ferro": 0.2, "vitamina_a": 3, "vitamina_c": 3, "vitamina_b12": 0, "potassio": 138, "zinco": 0.1},
    "beterraba": {"nome": "Beterraba Cozida", "calorias": 32, "proteinas": 1.2, "carboidratos": 6.8, "gorduras": 0.1, "fibras": 2.0, "sodio": 59, "calcio": 11, "ferro": 0.5, "vitamina_a": 2, "vitamina_c": 1, "vitamina_b12": 0, "potassio": 256, "zinco": 0.2},
    "pepino": {"nome": "Pepino Cru", "calorias": 10, "proteinas": 0.9, "carboidratos": 2.0, "gorduras": 0.1, "fibras": 0.7, "sodio": 1, "calcio": 10, "ferro": 0.2, "vitamina_a": 4, "vitamina_c": 5, "vitamina_b12": 0, "potassio": 140, "zinco": 0.2},
    "pimentao": {"nome": "Pimentão Cru", "calorias": 21, "proteinas": 1.0, "carboidratos": 4.9, "gorduras": 0.1, "fibras": 1.6, "sodio": 2, "calcio": 8, "ferro": 0.3, "vitamina_a": 89, "vitamina_c": 100, "vitamina_b12": 0, "potassio": 175, "zinco": 0.2},
    "vagem": {"nome": "Vagem Cozida", "calorias": 25, "proteinas": 1.5, "carboidratos": 4.5, "gorduras": 0.2, "fibras": 2.6, "sodio": 2, "calcio": 41, "ferro": 0.8, "vitamina_a": 39, "vitamina_c": 10, "vitamina_b12": 0, "potassio": 123, "zinco": 0.2},
    "mandioca": {"nome": "Mandioca Cozida", "calorias": 125, "proteinas": 0.6, "carboidratos": 30.1, "gorduras": 0.3, "fibras": 1.6, "sodio": 2, "calcio": 19, "ferro": 0.2, "vitamina_a": 3, "vitamina_c": 14, "vitamina_b12": 0, "potassio": 229, "zinco": 0.2},
    "inhame": {"nome": "Inhame Cozido", "calorias": 97, "proteinas": 2.0, "carboidratos": 22.4, "gorduras": 0.1, "fibras": 1.7, "sodio": 8, "calcio": 10, "ferro": 0.3, "vitamina_a": 5, "vitamina_c": 5, "vitamina_b12": 0, "potassio": 670, "zinco": 0.2},
    
    # ═══════════════════════════════════════════════════════════════
    # FRUTAS
    # ═══════════════════════════════════════════════════════════════
    "banana": {"nome": "Banana Prata", "calorias": 98, "proteinas": 1.3, "carboidratos": 26.0, "gorduras": 0.1, "fibras": 2.0, "sodio": 0, "calcio": 8, "ferro": 0.4, "vitamina_a": 10, "vitamina_c": 22, "vitamina_b12": 0, "potassio": 376, "zinco": 0.2},
    "maca": {"nome": "Maçã", "calorias": 63, "proteinas": 0.2, "carboidratos": 16.6, "gorduras": 0, "fibras": 1.3, "sodio": 0, "calcio": 2, "ferro": 0.1, "vitamina_a": 4, "vitamina_c": 7, "vitamina_b12": 0, "potassio": 75, "zinco": 0.1},
    "laranja": {"nome": "Laranja", "calorias": 37, "proteinas": 1.0, "carboidratos": 8.9, "gorduras": 0.1, "fibras": 0.8, "sodio": 0, "calcio": 35, "ferro": 0.1, "vitamina_a": 12, "vitamina_c": 57, "vitamina_b12": 0, "potassio": 163, "zinco": 0.1},
    "abacate": {"nome": "Abacate", "calorias": 96, "proteinas": 1.2, "carboidratos": 6.0, "gorduras": 8.4, "fibras": 6.3, "sodio": 0, "calcio": 8, "ferro": 0.2, "vitamina_a": 13, "vitamina_c": 9, "vitamina_b12": 0, "potassio": 206, "zinco": 0.2},
    "mamao": {"nome": "Mamão Papaia", "calorias": 40, "proteinas": 0.5, "carboidratos": 10.4, "gorduras": 0.1, "fibras": 1.0, "sodio": 3, "calcio": 25, "ferro": 0.2, "vitamina_a": 74, "vitamina_c": 78, "vitamina_b12": 0, "potassio": 222, "zinco": 0.1},
    "melancia": {"nome": "Melancia", "calorias": 33, "proteinas": 0.9, "carboidratos": 8.1, "gorduras": 0, "fibras": 0.1, "sodio": 0, "calcio": 8, "ferro": 0.2, "vitamina_a": 47, "vitamina_c": 6, "vitamina_b12": 0, "potassio": 104, "zinco": 0.1},
    "abacaxi": {"nome": "Abacaxi", "calorias": 48, "proteinas": 0.9, "carboidratos": 12.3, "gorduras": 0.1, "fibras": 1.0, "sodio": 0, "calcio": 22, "ferro": 0.3, "vitamina_a": 4, "vitamina_c": 35, "vitamina_b12": 0, "potassio": 131, "zinco": 0.1},
    "manga": {"nome": "Manga", "calorias": 51, "proteinas": 0.4, "carboidratos": 12.8, "gorduras": 0.3, "fibras": 1.6, "sodio": 2, "calcio": 8, "ferro": 0.2, "vitamina_a": 155, "vitamina_c": 18, "vitamina_b12": 0, "potassio": 138, "zinco": 0.1},
    "uva": {"nome": "Uva", "calorias": 53, "proteinas": 0.7, "carboidratos": 13.6, "gorduras": 0.2, "fibras": 0.9, "sodio": 0, "calcio": 7, "ferro": 0.2, "vitamina_a": 4, "vitamina_c": 11, "vitamina_b12": 0, "potassio": 162, "zinco": 0.1},
    "morango": {"nome": "Morango", "calorias": 30, "proteinas": 0.9, "carboidratos": 6.8, "gorduras": 0.3, "fibras": 1.7, "sodio": 0, "calcio": 11, "ferro": 0.3, "vitamina_a": 2, "vitamina_c": 64, "vitamina_b12": 0, "potassio": 184, "zinco": 0.1},
    "acerola": {"nome": "Acerola", "calorias": 33, "proteinas": 0.9, "carboidratos": 8.0, "gorduras": 0.2, "fibras": 1.5, "sodio": 3, "calcio": 13, "ferro": 0.2, "vitamina_a": 38, "vitamina_c": 941, "vitamina_b12": 0, "potassio": 165, "zinco": 0.1},
    "goiaba": {"nome": "Goiaba", "calorias": 54, "proteinas": 1.1, "carboidratos": 13.0, "gorduras": 0.4, "fibras": 6.2, "sodio": 0, "calcio": 4, "ferro": 0.2, "vitamina_a": 72, "vitamina_c": 80, "vitamina_b12": 0, "potassio": 198, "zinco": 0.1},
    "kiwi": {"nome": "Kiwi", "calorias": 51, "proteinas": 1.3, "carboidratos": 11.5, "gorduras": 0.6, "fibras": 2.7, "sodio": 4, "calcio": 26, "ferro": 0.2, "vitamina_a": 9, "vitamina_c": 71, "vitamina_b12": 0, "potassio": 269, "zinco": 0.1},
    "limao": {"nome": "Limão", "calorias": 32, "proteinas": 0.9, "carboidratos": 11.1, "gorduras": 0.1, "fibras": 0, "sodio": 1, "calcio": 51, "ferro": 0.1, "vitamina_a": 2, "vitamina_c": 38, "vitamina_b12": 0, "potassio": 124, "zinco": 0.1},
    
    # ═══════════════════════════════════════════════════════════════
    # MASSAS E PÃES
    # ═══════════════════════════════════════════════════════════════
    "macarrao": {"nome": "Macarrão Cozido", "calorias": 102, "proteinas": 3.4, "carboidratos": 19.9, "gorduras": 0.5, "fibras": 1.4, "sodio": 1, "calcio": 6, "ferro": 0.3, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 26, "zinco": 0.4},
    "lasanha": {"nome": "Lasanha à Bolonhesa", "calorias": 132, "proteinas": 8.2, "carboidratos": 13.5, "gorduras": 5.3, "fibras": 1.2, "sodio": 285, "calcio": 86, "ferro": 0.9, "vitamina_a": 58, "vitamina_c": 2, "vitamina_b12": 0.6, "potassio": 174, "zinco": 1.4},
    "pao_frances": {"nome": "Pão Francês", "calorias": 300, "proteinas": 8.0, "carboidratos": 58.6, "gorduras": 3.1, "fibras": 2.3, "sodio": 648, "calcio": 22, "ferro": 1.0, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 106, "zinco": 0.6},
    "pao_integral": {"nome": "Pão Integral", "calorias": 253, "proteinas": 9.4, "carboidratos": 49.9, "gorduras": 2.9, "fibras": 6.9, "sodio": 532, "calcio": 50, "ferro": 2.4, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 238, "zinco": 1.6},
    "pizza": {"nome": "Pizza (fatia média)", "calorias": 266, "proteinas": 11.0, "carboidratos": 33.0, "gorduras": 10.0, "fibras": 2.3, "sodio": 640, "calcio": 200, "ferro": 2.5, "vitamina_a": 100, "vitamina_c": 4, "vitamina_b12": 0.5, "potassio": 184, "zinco": 1.5},
    "nhoque": {"nome": "Nhoque", "calorias": 133, "proteinas": 3.5, "carboidratos": 27.0, "gorduras": 1.2, "fibras": 1.0, "sodio": 280, "calcio": 12, "ferro": 0.5, "vitamina_a": 5, "vitamina_c": 3, "vitamina_b12": 0, "potassio": 200, "zinco": 0.4},
    
    # ═══════════════════════════════════════════════════════════════
    # SOBREMESAS
    # ═══════════════════════════════════════════════════════════════
    "pudim": {"nome": "Pudim de Leite", "calorias": 180, "proteinas": 4.5, "carboidratos": 28.0, "gorduras": 5.5, "fibras": 0, "sodio": 80, "calcio": 120, "ferro": 0.3, "vitamina_a": 65, "vitamina_c": 1, "vitamina_b12": 0.4, "potassio": 140, "zinco": 0.4, "acucar": 24.0},
    "mousse_chocolate": {"nome": "Mousse de Chocolate", "calorias": 230, "proteinas": 4.0, "carboidratos": 25.0, "gorduras": 13.0, "fibras": 1.5, "sodio": 45, "calcio": 65, "ferro": 1.2, "vitamina_a": 50, "vitamina_c": 0, "vitamina_b12": 0.3, "potassio": 180, "zinco": 0.6, "acucar": 20.0},
    "sorvete": {"nome": "Sorvete de Creme", "calorias": 180, "proteinas": 3.0, "carboidratos": 22.0, "gorduras": 9.0, "fibras": 0, "sodio": 60, "calcio": 100, "ferro": 0.1, "vitamina_a": 80, "vitamina_c": 1, "vitamina_b12": 0.3, "potassio": 150, "zinco": 0.4, "acucar": 18.0},
    "gelatina": {"nome": "Gelatina", "calorias": 60, "proteinas": 1.5, "carboidratos": 14.0, "gorduras": 0, "fibras": 0, "sodio": 40, "calcio": 2, "ferro": 0, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 2, "zinco": 0, "acucar": 13.0},
    "bolo_chocolate": {"nome": "Bolo de Chocolate", "calorias": 370, "proteinas": 5.0, "carboidratos": 52.0, "gorduras": 16.0, "fibras": 2.0, "sodio": 280, "calcio": 40, "ferro": 2.0, "vitamina_a": 30, "vitamina_c": 0, "vitamina_b12": 0.2, "potassio": 150, "zinco": 0.8, "acucar": 32.0},
    "brigadeiro": {"nome": "Brigadeiro", "calorias": 385, "proteinas": 5.0, "carboidratos": 58.0, "gorduras": 15.0, "fibras": 1.5, "sodio": 130, "calcio": 150, "ferro": 1.5, "vitamina_a": 80, "vitamina_c": 0, "vitamina_b12": 0.3, "potassio": 250, "zinco": 0.8, "acucar": 48.0},
    "cocada": {"nome": "Cocada", "calorias": 420, "proteinas": 3.5, "carboidratos": 55.0, "gorduras": 22.0, "fibras": 4.0, "sodio": 35, "calcio": 30, "ferro": 1.2, "vitamina_a": 0, "vitamina_c": 1, "vitamina_b12": 0, "potassio": 200, "zinco": 0.6, "acucar": 42.0},
    
    # ═══════════════════════════════════════════════════════════════
    # PREPARAÇÕES TÍPICAS
    # ═══════════════════════════════════════════════════════════════
    "salada_verde": {"nome": "Salada Verde Mista", "calorias": 15, "proteinas": 1.2, "carboidratos": 2.5, "gorduras": 0.2, "fibras": 1.8, "sodio": 10, "calcio": 35, "ferro": 0.5, "vitamina_a": 200, "vitamina_c": 20, "vitamina_b12": 0, "potassio": 280, "zinco": 0.2},
    "farofa": {"nome": "Farofa", "calorias": 400, "proteinas": 2.5, "carboidratos": 52.0, "gorduras": 20.0, "fibras": 5.6, "sodio": 520, "calcio": 15, "ferro": 1.2, "vitamina_a": 45, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 180, "zinco": 0.5},
    "pure_batata": {"nome": "Purê de Batata", "calorias": 100, "proteinas": 2.0, "carboidratos": 15.0, "gorduras": 3.5, "fibras": 1.2, "sodio": 280, "calcio": 25, "ferro": 0.3, "vitamina_a": 35, "vitamina_c": 5, "vitamina_b12": 0.1, "potassio": 280, "zinco": 0.3},
    "feijoada": {"nome": "Feijoada Completa", "calorias": 165, "proteinas": 10.0, "carboidratos": 10.5, "gorduras": 9.5, "fibras": 5.0, "sodio": 750, "calcio": 35, "ferro": 2.5, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 1.0, "potassio": 350, "zinco": 2.0},
    "strogonoff": {"nome": "Strogonoff de Frango", "calorias": 185, "proteinas": 18.0, "carboidratos": 5.0, "gorduras": 10.0, "fibras": 0.5, "sodio": 520, "calcio": 45, "ferro": 1.0, "vitamina_a": 60, "vitamina_c": 2, "vitamina_b12": 0.4, "potassio": 280, "zinco": 1.2},
    "moqueca": {"nome": "Moqueca de Peixe", "calorias": 155, "proteinas": 18.0, "carboidratos": 6.0, "gorduras": 7.0, "fibras": 1.5, "sodio": 380, "calcio": 45, "ferro": 1.5, "vitamina_a": 80, "vitamina_c": 15, "vitamina_b12": 2.0, "potassio": 420, "zinco": 0.8},
    "acaraje": {"nome": "Acarajé", "calorias": 320, "proteinas": 12.0, "carboidratos": 25.0, "gorduras": 20.0, "fibras": 3.5, "sodio": 280, "calcio": 65, "ferro": 2.5, "vitamina_a": 30, "vitamina_c": 5, "vitamina_b12": 0, "potassio": 350, "zinco": 1.5},
    "baiao_dois": {"nome": "Baião de Dois", "calorias": 155, "proteinas": 7.0, "carboidratos": 22.0, "gorduras": 4.5, "fibras": 4.5, "sodio": 380, "calcio": 35, "ferro": 1.8, "vitamina_a": 10, "vitamina_c": 2, "vitamina_b12": 0.3, "potassio": 280, "zinco": 1.0},
    "bobó_camarao": {"nome": "Bobó de Camarão", "calorias": 165, "proteinas": 12.0, "carboidratos": 14.0, "gorduras": 8.0, "fibras": 2.0, "sodio": 420, "calcio": 65, "ferro": 1.8, "vitamina_a": 90, "vitamina_c": 10, "vitamina_b12": 1.2, "potassio": 380, "zinco": 1.3},
    "escondidinho": {"nome": "Escondidinho de Carne Seca", "calorias": 210, "proteinas": 15.0, "carboidratos": 18.0, "gorduras": 9.0, "fibras": 1.5, "sodio": 850, "calcio": 45, "ferro": 2.0, "vitamina_a": 40, "vitamina_c": 8, "vitamina_b12": 1.5, "potassio": 350, "zinco": 3.0},
    
    # ═══════════════════════════════════════════════════════════════
    # BEBIDAS
    # ═══════════════════════════════════════════════════════════════
    "suco_laranja": {"nome": "Suco de Laranja Natural", "calorias": 45, "proteinas": 0.7, "carboidratos": 10.4, "gorduras": 0.2, "fibras": 0.2, "sodio": 1, "calcio": 11, "ferro": 0.2, "vitamina_a": 8, "vitamina_c": 50, "vitamina_b12": 0, "potassio": 200, "zinco": 0.1},
    "cafe": {"nome": "Café sem Açúcar", "calorias": 2, "proteinas": 0.3, "carboidratos": 0, "gorduras": 0, "fibras": 0, "sodio": 5, "calcio": 2, "ferro": 0, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 116, "zinco": 0},
    "agua_coco": {"nome": "Água de Coco", "calorias": 22, "proteinas": 0, "carboidratos": 5.3, "gorduras": 0, "fibras": 0, "sodio": 25, "calcio": 24, "ferro": 0.3, "vitamina_a": 0, "vitamina_c": 2, "vitamina_b12": 0, "potassio": 250, "zinco": 0.1},
    "cha_verde": {"nome": "Chá Verde", "calorias": 1, "proteinas": 0, "carboidratos": 0, "gorduras": 0, "fibras": 0, "sodio": 1, "calcio": 1, "ferro": 0, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 8, "zinco": 0},
    
    # ═══════════════════════════════════════════════════════════════
    # OLEAGINOSAS
    # ═══════════════════════════════════════════════════════════════
    "castanha_para": {"nome": "Castanha-do-Pará", "calorias": 656, "proteinas": 14.3, "carboidratos": 12.3, "gorduras": 66.4, "fibras": 7.5, "sodio": 2, "calcio": 160, "ferro": 2.4, "vitamina_a": 0, "vitamina_c": 1, "vitamina_b12": 0, "potassio": 659, "zinco": 4.1, "selenio": 1917},
    "amendoim": {"nome": "Amendoim Torrado", "calorias": 544, "proteinas": 27.2, "carboidratos": 20.3, "gorduras": 43.9, "fibras": 8.0, "sodio": 5, "calcio": 43, "ferro": 1.5, "vitamina_a": 0, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 580, "zinco": 3.3},
    "nozes": {"nome": "Nozes", "calorias": 620, "proteinas": 14.0, "carboidratos": 18.0, "gorduras": 59.0, "fibras": 5.0, "sodio": 3, "calcio": 90, "ferro": 2.6, "vitamina_a": 1, "vitamina_c": 1, "vitamina_b12": 0, "potassio": 500, "zinco": 2.7},
    "amendoas": {"nome": "Amêndoas", "calorias": 581, "proteinas": 18.6, "carboidratos": 19.7, "gorduras": 51.0, "fibras": 11.8, "sodio": 1, "calcio": 248, "ferro": 3.3, "vitamina_a": 1, "vitamina_c": 0, "vitamina_b12": 0, "potassio": 728, "zinco": 3.4},
}

# Mapeamento expandido
INGREDIENTE_PARA_TACO = {
    # Carnes bovinas
    "carne": "carne_bovina", "carne bovina": "carne_bovina", "bife": "carne_bovina", "patinho": "carne_bovina",
    "alcatra": "alcatra", "picanha": "picanha", "maminha": "maminha", "costela": "costela", "cupim": "cupim",
    "fígado": "figado_bovino", "figado": "figado_bovino", "carne moída": "carne_moida",
    # Suínos
    "porco": "carne_porco", "lombo": "carne_porco", "pernil": "pernil_porco", "bacon": "bacon",
    "linguiça": "linguica", "linguica": "linguica", "presunto": "presunto", "salsicha": "salsicha",
    # Aves
    "frango": "frango", "peito de frango": "frango", "coxa de frango": "coxa_frango", "coxa": "coxa_frango",
    "peru": "peru", "pato": "pato", "frango frito": "frango_frito",
    # Cordeiro
    "cordeiro": "cordeiro", "carneiro": "cordeiro", "carré": "carre_cordeiro",
    # Peixes
    "salmão": "salmao", "salmon": "salmao", "bacalhau": "bacalhau", "tilápia": "tilapia", "tilapia": "tilapia",
    "atum": "atum", "sardinha": "sardinha", "merluza": "merluza", "pescada": "pescada",
    "robalo": "robalo", "linguado": "linguado", "dourado": "dourado", "peixe": "tilapia",
    # Frutos do mar
    "camarão": "camarao", "camarao": "camarao", "lula": "lula", "polvo": "polvo",
    "marisco": "marisco", "lagosta": "lagosta", "ostra": "ostra",
    # Ovos e laticínios
    "ovo": "ovo", "ovos": "ovo", "ovo frito": "ovo_frito", "queijo": "queijo_minas",
    "queijo minas": "queijo_minas", "queijo prato": "queijo_prato", "mussarela": "mussarela",
    "ricota": "ricota", "requeijão": "requeijao", "leite": "leite", "iogurte": "iogurte",
    # Grãos
    "arroz": "arroz_branco", "arroz branco": "arroz_branco", "arroz integral": "arroz_integral",
    "feijão": "feijao_preto", "feijão preto": "feijao_preto", "feijão carioca": "feijao_carioca",
    "lentilha": "lentilha", "grão de bico": "grao_de_bico", "grão-de-bico": "grao_de_bico",
    "quinoa": "quinoa", "aveia": "aveia", "milho": "milho",
    # Vegetais
    "brócolis": "brocolis", "brocolis": "brocolis", "couve-flor": "couve_flor", "cenoura": "cenoura",
    "espinafre": "espinafre", "abóbora": "abobora", "tomate": "tomate", "batata": "batata",
    "batata doce": "batata_doce", "batata-doce": "batata_doce", "alface": "alface", "couve": "couve",
    "berinjela": "berinjela", "abobrinha": "abobrinha", "chuchu": "chuchu", "beterraba": "beterraba",
    "pepino": "pepino", "pimentão": "pimentao", "vagem": "vagem", "mandioca": "mandioca", "inhame": "inhame",
    # Frutas
    "banana": "banana", "maçã": "maca", "maca": "maca", "laranja": "laranja", "abacate": "abacate",
    "mamão": "mamao", "melancia": "melancia", "abacaxi": "abacaxi", "manga": "manga", "uva": "uva",
    "morango": "morango", "acerola": "acerola", "goiaba": "goiaba", "kiwi": "kiwi", "limão": "limao",
    # Massas e pães
    "macarrão": "macarrao", "massa": "macarrao", "lasanha": "lasanha", "pão": "pao_frances",
    "pão francês": "pao_frances", "pão integral": "pao_integral", "pizza": "pizza", "nhoque": "nhoque",
    # Sobremesas
    "pudim": "pudim", "mousse": "mousse_chocolate", "sorvete": "sorvete", "gelatina": "gelatina",
    "bolo": "bolo_chocolate", "brigadeiro": "brigadeiro", "cocada": "cocada",
    # Preparações
    "salada": "salada_verde", "farofa": "farofa", "purê": "pure_batata", "feijoada": "feijoada",
    "strogonoff": "strogonoff", "moqueca": "moqueca", "acarajé": "acaraje",
    "baião de dois": "baiao_dois", "bobó": "bobo_camarao", "escondidinho": "escondidinho",
    # Bebidas
    "suco": "suco_laranja", "café": "cafe", "agua de coco": "agua_coco", "chá verde": "cha_verde",
    # Oleaginosas
    "castanha": "castanha_para", "castanha-do-pará": "castanha_para", "amendoim": "amendoim",
    "nozes": "nozes", "amêndoas": "amendoas",
}


def buscar_dados_taco(ingrediente: str) -> dict:
    """Busca dados nutricionais de um ingrediente na Tabela TACO."""
    ingrediente_lower = ingrediente.lower().strip()
    
    if ingrediente_lower in TACO_DATABASE:
        return TACO_DATABASE[ingrediente_lower]
    
    if ingrediente_lower in INGREDIENTE_PARA_TACO:
        chave = INGREDIENTE_PARA_TACO[ingrediente_lower]
        return TACO_DATABASE.get(chave)
    
    for termo, chave in INGREDIENTE_PARA_TACO.items():
        if termo in ingrediente_lower or ingrediente_lower in termo:
            return TACO_DATABASE.get(chave)
    
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


VDR = {
    "calorias": 2000, "proteinas": 50, "carboidratos": 300, "gorduras": 65,
    "fibras": 25, "sodio": 2400, "calcio": 1000, "ferro": 14, "vitamina_a": 800,
    "vitamina_c": 90, "vitamina_b12": 2.4, "potassio": 4700, "zinco": 11, "acucar": 50
}


def calcular_percentual_vdr(nutriente: str, valor: float) -> float:
    if nutriente in VDR and VDR[nutriente] > 0:
        return (valor / VDR[nutriente]) * 100
    return 0
