# -*- coding: utf-8 -*-
"""
SoulNutri — Servico de naming em duas camadas.

CAMADA 1 — SLUG TECNICO INTERNO
  to_canonical_slug(name) -> "feijao_do_chef"
  Uso: chaves MongoDB, dedup, URL, cache. NUNCA exibir ao cliente.

CAMADA 2 — DISPLAY NAME PARA CLIENTE
  to_display_name(slug_or_name, nome_from_db) -> "Feijao do Chef"
  Uso: telas, cards, scan, radar, mensagens. NUNCA como chave de banco.

Ambas as funcoes sao puras (sem I/O, sem imports de projeto).
Dependencias: apenas re e unicodedata (stdlib).
"""
import re
import unicodedata


# ---------------------------------------------------------------------------
# HELPER PRIVADO
# ---------------------------------------------------------------------------

def _strip_accents(s: str) -> str:
    """
    Remove acentos via decomposicao NFD.
    "Graos" -> "Graos"   "Limao" -> "Limao"   "Misso" -> "Misso"
    Preserva numeros, letras e estrutura da string.
    """
    nfd = unicodedata.normalize("NFD", s)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


# ---------------------------------------------------------------------------
# CAMADA 1 — SLUG TECNICO INTERNO
# ---------------------------------------------------------------------------

def to_canonical_slug(name: str) -> str:
    """
    CAMADA 1: Converte qualquer string para slug tecnico canonico.

    Regras:
      - lowercase
      - sem acentos (NFD)
      - espacos, hifens, underscores -> underscore unico
      - apenas [a-z0-9_] permitido
      - sem underscore duplo, inicio ou fim

    Idempotente: to_canonical_slug(to_canonical_slug(x)) == to_canonical_slug(x)

    Exemplos:
      "Feijao do Chef"               -> "feijao_do_chef"
      "Arroz 7 Graos"                -> "arroz_7_graos"
      "File de Peixe ao Misso"       -> "file_de_peixe_ao_misso"
      "Alho Poro Gratinado"          -> "alho_poro_gratinado"
      "Rolinho Vietnamita de Camarao"-> "rolinho_vietnamita_de_camarao"
      "feijao-do-chef"               -> "feijao_do_chef"
      "Feijao do Chef"               -> "feijao_do_chef"  (folder CLIP)
    """
    if not name or not name.strip():
        return ""

    s = name.strip()
    s = _strip_accents(s)
    s = s.lower()
    s = re.sub(r"[\s\-_]+", "_", s)   # separadores -> underscore
    s = re.sub(r"[^a-z0-9_]", "", s)  # remove tudo fora do padrao
    s = re.sub(r"_+", "_", s)         # colapso
    s = s.strip("_")

    return s


# ---------------------------------------------------------------------------
# CAMADA 2 — DISPLAY NAME PARA CLIENTE
# ---------------------------------------------------------------------------

# Particulas que ficam em minusculo no meio do nome
_PARTICLES = {"ao", "a", "o", "de", "do", "da", "dos", "das",
              "com", "sem", "em", "no", "na", "e", "por", "ou"}


def to_display_name(slug_or_name: str, nome_from_db: str = None) -> str:
    """
    CAMADA 2: Converte slug tecnico ou nome bruto para display name legivel.

    Prioridade de lookup:
      1. nome_from_db  — dishes.nome / dishes.name pre-buscado pelo caller.
                         Se fornecido, tem prioridade (strip acento aplicado).
      2. DISH_NAMES    — dicionario em policy.py, importado localmente.
                         Se encontrado, strip acento aplicado.
      3. Fallback puro — slug tecnico -> underscore->espaco -> Title Case
                         sem acento por construcao.

    Regras de saida (SEMPRE):
      - sem acento
      - sem underscore
      - sem hifen tecnico
      - Title Case com particulas (ao, de, do, da, com, sem...) em minusculo

    Exemplos:
      "feijao_do_chef"  + None           -> "Feijao do Chef"
      "feijao_do_chef"  + "Feijao Chef"  -> "Feijao Chef"  (db tem prioridade)
      "arroz_7_graos"   + None           -> via DISH_NAMES -> "Arroz 7 Graos"
      "Feijao do Chef"  + None           -> "Feijao do Chef"  (strip acento)
      "feijao-do-chef"  + None           -> "Feijao do Chef"
      ""                + None           -> ""

    NUNCA usar o retorno como chave de banco, dedup ou URL.
    """
    if not slug_or_name and not nome_from_db:
        return ""

    # Prioridade 1: nome do banco de dados
    if nome_from_db and nome_from_db.strip():
        return _format_display(_strip_accents(nome_from_db.strip()))

    # Prioridade 2: DISH_NAMES (lookup local em policy.py)
    canonical = to_canonical_slug(slug_or_name)
    if not canonical:
        return ""  # slug_or_name era vazio ou so separadores

    collapsed = canonical.replace("_", "")  # chave do DISH_NAMES: "feijodochef"
    try:
        # Import local para evitar circular: slug_service nunca e importado por policy
        from ai.policy import DISH_NAMES
        if collapsed in DISH_NAMES:
            return _format_display(_strip_accents(DISH_NAMES[collapsed]))
    except ImportError:
        pass  # ambiente de teste sem policy.py — continua para fallback

    # Prioridade 3: fallback puro (slug -> legivel)
    readable = canonical.replace("_", " ").strip()
    return _format_display(readable)


def _format_display(name: str) -> str:
    """
    Aplica Title Case com particulas em minusculo.
    Input ja deve estar sem acento.
    "feijao do chef" -> "Feijao do Chef"
    "arroz 7 graos"  -> "Arroz 7 Graos"
    """
    if not name:
        return ""
    parts = name.split()
    out = []
    for i, w in enumerate(parts):
        wl = w.lower()
        if i > 0 and wl in _PARTICLES:
            out.append(wl)
        else:
            out.append(wl[0].upper() + wl[1:] if wl else wl)
    return " ".join(out)
