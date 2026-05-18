# -*- coding: utf-8 -*-
"""
Testes unitarios para services/slug_service.py — Duas Camadas.
Execucao: cd /app/backend && python -m pytest tests/test_slug_service.py -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.slug_service import to_canonical_slug, to_display_name


# ══════════════════════════════════════════════════════════════════
# CAMADA 1 — to_canonical_slug
# NUNCA exibir ao cliente. Uso: MongoDB key, dedup, URL, cache.
# ══════════════════════════════════════════════════════════════════

class TestCanonicalSlug:

    # Casos do plano
    def test_feijao_do_chef(self):
        assert to_canonical_slug("Feijão do Chef") == "feijao_do_chef"

    def test_arroz_7_graos(self):
        assert to_canonical_slug("Arroz 7 Grãos") == "arroz_7_graos"

    def test_file_de_peixe_ao_misso(self):
        assert to_canonical_slug("Filé de Peixe ao Missô") == "file_de_peixe_ao_misso"

    def test_alho_poro_gratinado(self):
        assert to_canonical_slug("Alho Poró Gratinado") == "alho_poro_gratinado"

    def test_rolinho_vietnamita(self):
        assert to_canonical_slug("Rolinho Vietnamita de Camarão") == "rolinho_vietnamita_de_camarao"

    # Separadores multiplos
    def test_espacos_duplos(self):
        assert to_canonical_slug("Arroz  com  Brocolis") == "arroz_com_brocolis"

    def test_hifens_duplos(self):
        assert to_canonical_slug("Filé--de--Peixe") == "file_de_peixe"

    def test_mix_separadores(self):
        assert to_canonical_slug("Frango - Grelhado_ao Limão") == "frango_grelhado_ao_limao"

    def test_underscore_nas_bordas(self):
        assert to_canonical_slug("___Arroz___Branco___") == "arroz_branco"

    # Formatos legados
    def test_hifen_legado(self):
        assert to_canonical_slug("feijao-do-chef") == "feijao_do_chef"

    def test_folder_clip_com_espaco(self):
        assert to_canonical_slug("Feijao do Chef") == "feijao_do_chef"

    def test_variantes_arroz_branco(self):
        assert to_canonical_slug("arroz-branco") == "arroz_branco"
        assert to_canonical_slug("arroz_branco") == "arroz_branco"
        assert to_canonical_slug("Arroz Branco") == "arroz_branco"

    def test_variantes_tomate(self):
        assert to_canonical_slug("Tomate") == "tomate"
        assert to_canonical_slug("tomate") == "tomate"

    def test_feijao_do_chef_hifen(self):
        assert to_canonical_slug("feijao-do-chef") == "feijao_do_chef"

    # Edge cases
    def test_string_vazia(self):
        assert to_canonical_slug("") == ""

    def test_apenas_espacos(self):
        assert to_canonical_slug("   ") == ""

    def test_apenas_hifens(self):
        assert to_canonical_slug("---") == ""

    def test_apenas_underscores(self):
        assert to_canonical_slug("___") == ""

    def test_numeros(self):
        assert to_canonical_slug("Arroz 7 Grãos com Legumes") == "arroz_7_graos_com_legumes"

    def test_caracteres_especiais(self):
        assert to_canonical_slug("Prato (especial)") == "prato_especial"
        assert to_canonical_slug("Frango & Legumes") == "frango_legumes"

    def test_idempotencia(self):
        inputs = [
            "Feijão do Chef",
            "Arroz 7 Grãos",
            "feijao_do_chef",
            "FRANGO GRELHADO",
            "feijao-do-chef",
            "Filé de Peixe ao Missô",
        ]
        for v in inputs:
            primeira = to_canonical_slug(v)
            segunda = to_canonical_slug(primeira)
            assert primeira == segunda, f"Nao idempotente: {v!r} -> {primeira!r} -> {segunda!r}"


# ══════════════════════════════════════════════════════════════════
# CAMADA 2 — to_display_name
# NUNCA usar como chave de banco. Uso: telas, cards, scan, radar.
# ══════════════════════════════════════════════════════════════════

class TestDisplayName:

    # Fallback puro (sem nome_from_db, sem DISH_NAMES)
    def test_slug_para_display(self):
        assert to_display_name("feijao_do_chef") == "Feijao do Chef"

    def test_slug_com_particulas(self):
        assert to_display_name("file_de_peixe_ao_misso") == "File de Peixe ao Misso"

    def test_slug_rolinho(self):
        assert to_display_name("rolinho_vietnamita_de_camarao") == "Rolinho Vietnamita de Camarao"

    def test_slug_alho_poro(self):
        assert to_display_name("alho_poro_gratinado") == "Alho Poro Gratinado"

    def test_hifen_para_display(self):
        assert to_display_name("feijao-do-chef") == "Feijao do Chef"

    # Prioridade 1: nome_from_db
    def test_db_remove_acento(self):
        result = to_display_name("feijao_do_chef", nome_from_db="Feijão do Chef")
        assert result == "Feijao do Chef"
        assert "ã" not in result

    def test_db_nome_diferente_vence(self):
        # DB vence; _format_display aplica Title Case — "Carne" maiusculo e correto
        result = to_display_name("feijao_branco", nome_from_db="Feijao (s/ carne)")
        assert result == "Feijao (s/ Carne)"
        assert "_" not in result

    def test_db_acento_complexo(self):
        result = to_display_name("arroz_7_graos", nome_from_db="Arroz 7 Grãos")
        assert result == "Arroz 7 Graos"
        assert "ã" not in result

    def test_db_none_usa_fallback(self):
        result = to_display_name("feijao_do_chef", nome_from_db=None)
        assert "_" not in result
        assert result != ""

    def test_db_string_vazia_usa_fallback(self):
        result = to_display_name("feijao_do_chef", nome_from_db="")
        assert result != ""
        assert "_" not in result

    # Input ja e display name
    def test_input_display_com_espaco(self):
        result = to_display_name("Feijao do Chef")
        assert result == "Feijao do Chef"
        assert "_" not in result

    def test_input_com_acento_sem_db(self):
        result = to_display_name("Feijão do Chef")
        assert "ã" not in result
        assert result == "Feijao do Chef"

    # Sem acento na saida — SEMPRE
    def test_sem_acento_em_qualquer_caso(self):
        acentos = "àáâãäèéêëìíîïòóôõöùúûüýç"
        cases = [
            to_display_name("feijao_do_chef"),
            to_display_name("alho_poro_gratinado"),
            to_display_name("misso", nome_from_db="Missô"),
            to_display_name("graos", nome_from_db="Grãos"),
        ]
        for result in cases:
            for acento in acentos:
                assert acento not in result, f"Acento '{acento}' encontrado em: {result!r}"

    # Sem underscore na saida — SEMPRE
    def test_sem_underscore_na_saida(self):
        cases = [
            to_display_name("feijao_do_chef"),
            to_display_name("arroz_7_graos"),
            to_display_name("rolinho_vietnamita_de_camarao"),
        ]
        for result in cases:
            assert "_" not in result, f"Underscore encontrado em: {result!r}"

    # Edge cases
    def test_string_vazia(self):
        assert to_display_name("") == ""

    def test_apenas_underscore(self):
        assert to_display_name("___") == ""

    def test_idempotencia_display(self):
        primeira = to_display_name("feijao_do_chef")
        segunda = to_display_name(primeira)
        assert primeira == segunda


# ══════════════════════════════════════════════════════════════════
# CONTRATO ENTRE CAMADAS
# ══════════════════════════════════════════════════════════════════

class TestContratoEntreCamadas:
    """Garante que as duas camadas nao se contaminam."""

    def test_slug_nunca_tem_espaco(self):
        inputs = ["Feijão do Chef", "Arroz 7 Grãos", "feijao-do-chef"]
        for v in inputs:
            slug = to_canonical_slug(v)
            assert " " not in slug, f"Espaco no slug: {slug!r}"

    def test_display_nunca_tem_underscore(self):
        inputs = ["feijao_do_chef", "arroz_7_graos", "rolinho_vietnamita_de_camarao"]
        for v in inputs:
            display = to_display_name(v)
            assert "_" not in display, f"Underscore no display: {display!r}"

    def test_ciclo_slug_display_slug(self):
        """to_canonical_slug(to_display_name(slug)) deve retornar o slug original."""
        slugs = [
            "feijao_do_chef",
            "arroz_7_graos",
            "file_de_peixe_ao_misso",
            "rolinho_vietnamita_de_camarao",
            "alho_poro_gratinado",
        ]
        for original in slugs:
            display = to_display_name(original)
            re_slug = to_canonical_slug(display)
            assert re_slug == original, (
                f"Ciclo quebrado: slug={original!r} -> "
                f"display={display!r} -> re-slug={re_slug!r}"
            )
