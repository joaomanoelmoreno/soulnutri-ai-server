#!/usr/bin/env python3
"""
SoulNutri — Migration: Famílias Visuais v1
==========================================
Cria a collection 'families' no MongoDB e vincula dishes existentes
via campo 'family_id'. Operação 100% idempotente (pode ser executada N vezes).

USO:
    cd /app/backend
    python scripts/migrate_families_v1.py

ROLLBACK COMPLETO:
    db.families.drop()
    db.dishes.updateMany({}, { $unset: { family_id: "" } })
"""

import asyncio
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "soulnutri")

# ═══════════════════════════════════════════════════════════════════════════════
# FONTE DA VERDADE — validado em:
# /app/memory/diagnostics/visual_families_validation_2026-02-05.md
# ═══════════════════════════════════════════════════════════════════════════════

FAMILIES = [
    {
        "family_id": "fam_milanesa_animal",
        "family_name": "Milanesa (Frango/Peixe/Filé Mignon)",
        "category": "proteína animal",
        "kcal_min": 150,
        "kcal_max": 200,
        "kcal_estimated": True,
        "kcal_estimation_note": "Faixa provisória — recalcular após criar ficha do Filé Mignon",
        "require_confirmation": True,
        "dish_ids": ["peixe_a_milanesa", "frango_a_milanesa", "file_mignon_a_milanesa"],
        "alergenos_consolidados": ["gluten", "ovo", "peixe"],
    },
    {
        "family_id": "fam_parmegiana_animal",
        "family_name": "Parmegiana (Frango/Peixe/Filé Mignon)",
        "category": "proteína animal",
        "kcal_min": 160,
        "kcal_max": 185,
        "kcal_estimated": False,
        "kcal_estimation_note": "Baseado em Filé de Frango à Parmegiana (~174 kcal)",
        "require_confirmation": True,
        "dish_ids": [
            "file_de_frango_a_parmegiana",
            "peixe_a_parmegiana",
            "file_mignon_a_parmegiana",
        ],
        "alergenos_consolidados": ["gluten", "ovo", "lactose", "peixe"],
    },
    {
        "family_id": "fam_lasanha_vegetariano",
        "family_name": "Lasanha",
        "category": "vegetariano",
        "kcal_min": 230,
        "kcal_max": 230,
        "kcal_estimated": True,
        "kcal_estimation_note": (
            "VALOR PROVISÓRIO. Lasanha de Espinafre tem 54 kcal cadastrada — ERRO GRAVE. "
            "Usando 230 kcal/100g como provisório para a família inteira."
        ),
        "require_confirmation": True,
        "dish_ids": ["lasanha_de_espinafre", "lasanha_de_portobello"],
        "alergenos_consolidados": ["gluten", "lactose"],
    },
    {
        "family_id": "fam_risoto_vegetariano",
        "family_name": "Risoto",
        "category": "vegetariano",
        "kcal_min": 220,
        "kcal_max": 260,
        "kcal_estimated": True,
        "kcal_estimation_note": "Baseado em Risoto de Alho Poró (228 kcal) e Risoto de Pera e Gorgonzola (247 kcal)",
        "require_confirmation": True,
        "dish_ids": [
            "risoto_de_alho_poro",
            "risoto_de_pera_e_gorgonzola",
            "risoto_milanes",
        ],
        "alergenos_consolidados": ["lactose"],
    },
    {
        "family_id": "fam_gratinado_animal",
        "family_name": "Gratinado Animal",
        "category": "proteína animal",
        "kcal_min": 112,
        "kcal_max": 231,
        "kcal_estimated": False,
        "kcal_estimation_note": (
            "Escondidinho de Carne Seca = 231 kcal, Bacalhau com Natas = 112 kcal. "
            "Spread de 68% — dropdown obrigatório."
        ),
        "require_confirmation": True,
        "dish_ids": ["escondidinho_de_carne_seca", "bacalhau_com_natas"],
        "alergenos_consolidados": ["lactose", "peixe"],
    },
]

# dish_slug → family_id  (derivado de FAMILIES automaticamente)
DISH_FAMILY_MAP = {
    did: fam["family_id"] for fam in FAMILIES for did in fam["dish_ids"]
}

# ═══════════════════════════════════════════════════════════════════════════════
# PLACEHOLDER DISHES (não existem ainda no MongoDB)
# ═══════════════════════════════════════════════════════════════════════════════

PLACEHOLDER_DISHES = [
    {
        "slug": "frango_a_milanesa",
        "name": "Frango à Milanesa",
        "category": "proteína animal",
        "family_id": "fam_milanesa_animal",
        "status": "placeholder",
        "image_url": None,
        "ingredients": ["frango", "farinha de rosca", "ovo", "sal"],
        "nutrition_pending": True,
    },
    {
        "slug": "file_mignon_a_milanesa",
        "name": "Filé Mignon à Milanesa",
        "category": "proteína animal",
        "family_id": "fam_milanesa_animal",
        "status": "placeholder",
        "image_url": None,
        "ingredients": ["filé mignon", "farinha de rosca", "ovo", "sal"],
        "nutrition_pending": True,
    },
    {
        "slug": "peixe_a_parmegiana",
        "name": "Peixe à Parmegiana",
        "category": "proteína animal",
        "family_id": "fam_parmegiana_animal",
        "status": "placeholder",
        "image_url": None,
        "ingredients": ["peixe", "molho de tomate", "mussarela", "farinha"],
        "nutrition_pending": True,
    },
    {
        "slug": "file_mignon_a_parmegiana",
        "name": "Filé Mignon à Parmegiana",
        "category": "proteína animal",
        "family_id": "fam_parmegiana_animal",
        "status": "placeholder",
        "image_url": None,
        "ingredients": ["filé mignon", "molho de tomate", "mussarela", "presunto"],
        "nutrition_pending": True,
    },
    {
        "slug": "risoto_milanes",
        "name": "Risoto Milanês",
        "category": "vegetariano",
        "family_id": "fam_risoto_vegetariano",
        "status": "placeholder",
        "image_url": None,
        "ingredients": ["arroz arbóreo", "açafrão", "queijo parmesão", "manteiga"],
        "nutrition_pending": True,
        "calorias_estimadas": "240 kcal",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# FICHAS NUTRICIONAIS SUSPEITAS
# ═══════════════════════════════════════════════════════════════════════════════

SUSPICIOUS_NUTRITION = [
    {
        "slug": "lasanha_de_espinafre",
        "motivo": "kcal cadastrada = 54 kcal/100g (valor impossível para lasanha com massa+queijo+molho)",
    }
]

# ─────────────────────────────────────────────────────────────────────────────
# Mapeamento de nomes alternativos no DB (folder name → slug variantes)
# O DB pode conter o prato com diferentes formatos de nome/slug
# ─────────────────────────────────────────────────────────────────────────────
DISPLAY_NAME_MAP = {
    "peixe_a_milanesa": "Peixe a Milanesa",
    "file_de_frango_a_parmegiana": "Filé de Frango à Parmegiana",
    "lasanha_de_espinafre": "Lasanha de Espinafre",
    "lasanha_de_portobello": "Lasanha de Portobello",
    "risoto_de_alho_poro": "Risoto de Alho Poro",
    "risoto_de_pera_e_gorgonzola": "Risoto de Pera e Gorgonzola",
    "escondidinho_de_carne_seca": "Escondidinho de Carne Seca",
    "bacalhau_com_natas": "Bacalhau com Natas",
}


async def find_dish(db, dish_slug: str):
    """Busca prato por slug, slug sem underscores ou nome (case-insensitive)."""
    display_name = DISPLAY_NAME_MAP.get(dish_slug, dish_slug.replace("_", " ").title())
    slug_nospace = dish_slug.replace("_", "")

    return await db.dishes.find_one(
        {
            "$or": [
                {"slug": dish_slug},
                {"slug": slug_nospace},
                {"slug": {"$regex": f"^{dish_slug.replace('_', '[ _-]?')}$", "$options": "i"}},
                {"name": {"$regex": f"^{display_name}$", "$options": "i"}},
                {"nome": {"$regex": f"^{display_name}$", "$options": "i"}},
            ]
        },
        {"_id": 0, "slug": 1, "name": 1, "family_id": 1},
    )


async def run_migration():
    if not MONGO_URL:
        print("ERRO: MONGO_URL nao encontrado no .env. Abortando.")
        return

    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    print(f"\n{'=' * 62}")
    print("  SoulNutri — Migration: Familias Visuais v1")
    print(f"  DB: {DB_NAME}")
    print(f"{'=' * 62}\n")

    # ── PASSO 1: Criar / Atualizar collection 'families' ───────────
    print("PASSO 1 — Criando/atualizando collection 'families'...")
    for family in FAMILIES:
        result = await db.families.update_one(
            {"family_id": family["family_id"]},
            {"$set": family},
            upsert=True,
        )
        action = "CRIADO   " if result.upserted_id else "ATUALIZADO"
        print(f"  [{action}] {family['family_id']}")

    # ── PASSO 2: Vincular family_id em 'dishes' existentes ─────────
    print("\nPASSO 2 — Vinculando family_id em 'dishes' existentes...")
    for dish_slug, family_id in DISH_FAMILY_MAP.items():
        existing = await find_dish(db, dish_slug)
        if existing:
            if existing.get("family_id") == family_id:
                print(f"  [JA OK    ] {dish_slug}")
            else:
                display = DISPLAY_NAME_MAP.get(dish_slug, dish_slug)
                slug_nospace = dish_slug.replace("_", "")
                slug_hyphen = dish_slug.replace("_", "-")
                await db.dishes.update_one(
                    {
                        "$or": [
                            {"slug": dish_slug},
                            {"slug": slug_nospace},
                            {"slug": slug_hyphen},
                            {"name": {"$regex": f"^{display}$", "$options": "i"}},
                            {"nome": {"$regex": f"^{display}$", "$options": "i"}},
                        ]
                    },
                    {"$set": {"family_id": family_id}},
                )
                print(f"  [ATUALIZADO] {dish_slug} -> {family_id}")
        else:
            print(f"  [NAO ENCONTRADO] {dish_slug} — sera criado em PASSO 3 se for placeholder")

    # ── PASSO 2.5: Link direto por slug hifenado (fallback slugs no DB) ──
    print("\nPASSO 2.5 — Fallback por slug hifenado...")
    DIRECT_SLUG_MAP = {
        "peixe-a-milanesa": "fam_milanesa_animal",
        "lasanha-de-espinafre": "fam_lasanha_vegetariano",
        "lasanha-de-portobello": "fam_lasanha_vegetariano",
        "risoto-de-alho-poro": "fam_risoto_vegetariano",
        "risoto-de-pera-e-gorgonzola": "fam_risoto_vegetariano",
        "escondidinho-de-carne-seca": "fam_gratinado_animal",
        "bacalhau-com-natas": "fam_gratinado_animal",
    }
    for slug_h, fid in DIRECT_SLUG_MAP.items():
        r = await db.dishes.update_one(
            {"slug": slug_h},
            {"$set": {"family_id": fid}},
        )
        if r.matched_count:
            print(f"  [LINKED  ] {slug_h} -> {fid}")
        else:
            print(f"  [AUSENTE ] {slug_h} (nao existe com este slug)")

    # ── PASSO 3: Criar placeholder dishes ──────────────────────────
    print("\nPASSO 3 — Criando placeholder dishes (se nao existirem)...")
    for ph in PLACEHOLDER_DISHES:
        existing = await db.dishes.find_one({"slug": ph["slug"]}, {"_id": 0, "slug": 1})
        if existing:
            await db.dishes.update_one(
                {"slug": ph["slug"]},
                {"$set": {"family_id": ph["family_id"], "status": "placeholder"}},
            )
            print(f"  [JA EXISTE — atualizado] {ph['slug']}")
        else:
            doc = {k: v for k, v in ph.items()}
            await db.dishes.insert_one(doc)
            print(f"  [CRIADO   ] {ph['slug']} ({ph['name']})")

    # ── PASSO 4: Marcar fichas nutricionais suspeitas ───────────────
    print("\nPASSO 4 — Marcando fichas nutricionais suspeitas...")
    for flag in SUSPICIOUS_NUTRITION:
        display = DISPLAY_NAME_MAP.get(flag["slug"], flag["slug"].replace("_", " ").title())
        r = await db.nutrition_sheets.update_one(
            {
                "$or": [
                    {"nome": {"$regex": display, "$options": "i"}},
                    {"slug": flag["slug"]},
                ]
            },
            {
                "$set": {
                    "nutricao_suspeita": True,
                    "motivo_suspeita": flag["motivo"],
                }
            },
        )
        status = "MARCADO" if r.modified_count else "NAO ENCONTRADO (nutrition_sheet)"
        print(f"  [{status}] {flag['slug']}")

    # ── PASSO 5: Verificação final ──────────────────────────────────
    print("\nPASSO 5 — Verificacao final...")
    total_families = await db.families.count_documents({})
    total_with_family = await db.dishes.count_documents({"family_id": {"$exists": True}})
    total_placeholders = await db.dishes.count_documents({"status": "placeholder"})

    print(f"  Familias na collection 'families':  {total_families}")
    print(f"  Dishes com family_id:               {total_with_family}")
    print(f"  Placeholder dishes:                 {total_placeholders}")

    print(f"\n{'=' * 62}")
    print("  Migration concluida com sucesso!")
    print(f"{'=' * 62}")
    print()
    print("  ROLLBACK (se necessario):")
    print("    db.families.drop()")
    print("    db.dishes.updateMany({}, { $unset: { family_id: '' } })")
    print()

    client.close()


if __name__ == "__main__":
    asyncio.run(run_migration())
