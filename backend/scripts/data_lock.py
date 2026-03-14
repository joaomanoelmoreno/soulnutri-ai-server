#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE TRAVAMENTO DE DADOS - SoulNutri
Gera e verifica checksums de todas as pastas, fotos e dish_info.json.
Impede qualquer alteracao nao autorizada nos dados dos pratos.

Uso:
  python3 data_lock.py lock     # Gera checksums e trava
  python3 data_lock.py verify   # Verifica integridade
  python3 data_lock.py diff     # Mostra diferencas
"""

import os
import sys
import json
import hashlib
from datetime import datetime

DATASETS_DIR = "/app/datasets/organized"
LOCK_FILE = "/app/datasets/DATA_LOCK.json"


def file_hash(filepath: str) -> str:
    """Gera SHA256 de um arquivo."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_all_dishes() -> dict:
    """Escaneia todas as pastas e gera inventario completo."""
    inventory = {}

    for folder in sorted(os.listdir(DATASETS_DIR)):
        folder_path = os.path.join(DATASETS_DIR, folder)
        if not os.path.isdir(folder_path):
            continue

        dish = {
            "folder": folder,
            "files": {},
        }

        # dish_info.json
        info_path = os.path.join(folder_path, "dish_info.json")
        if os.path.exists(info_path):
            dish["files"]["dish_info.json"] = file_hash(info_path)
            try:
                with open(info_path, encoding="utf-8") as f:
                    data = json.load(f)
                dish["nome"] = data.get("nome", "")
                dish["slug"] = data.get("slug", "")
                dish["ingredientes_count"] = len(data.get("ingredientes", []))
            except json.JSONDecodeError:
                dish["nome"] = "CORROMPIDO"
                dish["slug"] = ""
                dish["ingredientes_count"] = 0

        # Fotos
        for fname in sorted(os.listdir(folder_path)):
            if fname.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                fpath = os.path.join(folder_path, fname)
                dish["files"][fname] = file_hash(fpath)

        dish["total_files"] = len(dish["files"])
        inventory[folder] = dish

    return inventory


def lock():
    """Gera o arquivo de travamento."""
    print("Escaneando todas as pastas de pratos...")
    inventory = scan_all_dishes()

    lock_data = {
        "version": "v1.5_LOCKED",
        "locked_at": datetime.now().isoformat(),
        "locked_by": "SoulNutri Data Lock System",
        "total_dishes": len(inventory),
        "total_files": sum(d["total_files"] for d in inventory.values()),
        "inventory": inventory,
    }

    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, ensure_ascii=False, indent=2)

    print(f"\nTRAVADO!")
    print(f"  Pratos: {lock_data['total_dishes']}")
    print(f"  Arquivos: {lock_data['total_files']}")
    print(f"  Arquivo: {LOCK_FILE}")
    print(f"  Data: {lock_data['locked_at']}")
    return lock_data


def verify() -> dict:
    """Verifica integridade contra o arquivo de travamento."""
    if not os.path.exists(LOCK_FILE):
        print("ERRO: Arquivo de travamento nao encontrado!")
        print(f"Execute: python3 {__file__} lock")
        return {"ok": False, "error": "lock_file_missing"}

    with open(LOCK_FILE, encoding="utf-8") as f:
        lock_data = json.load(f)

    current = scan_all_dishes()
    locked = lock_data.get("inventory", {})

    issues = []

    # Pastas removidas
    for folder in locked:
        if folder not in current:
            issues.append({
                "tipo": "PASTA_REMOVIDA",
                "pasta": folder,
                "nome": locked[folder].get("nome", ""),
                "severidade": "CRITICA"
            })

    # Pastas adicionadas
    for folder in current:
        if folder not in locked:
            issues.append({
                "tipo": "PASTA_ADICIONADA",
                "pasta": folder,
                "nome": current[folder].get("nome", ""),
                "severidade": "ALERTA"
            })

    # Arquivos modificados/removidos/adicionados
    for folder in locked:
        if folder not in current:
            continue

        locked_files = locked[folder].get("files", {})
        current_files = current[folder].get("files", {})

        # Arquivos removidos
        for fname in locked_files:
            if fname not in current_files:
                issues.append({
                    "tipo": "ARQUIVO_REMOVIDO",
                    "pasta": folder,
                    "arquivo": fname,
                    "severidade": "CRITICA"
                })

        # Arquivos modificados
        for fname in locked_files:
            if fname in current_files and locked_files[fname] != current_files[fname]:
                issues.append({
                    "tipo": "ARQUIVO_MODIFICADO",
                    "pasta": folder,
                    "arquivo": fname,
                    "severidade": "CRITICA"
                })

        # Arquivos adicionados
        for fname in current_files:
            if fname not in locked_files:
                issues.append({
                    "tipo": "ARQUIVO_ADICIONADO",
                    "pasta": folder,
                    "arquivo": fname,
                    "severidade": "ALERTA"
                })

        # Nome alterado
        if locked[folder].get("nome") != current[folder].get("nome"):
            issues.append({
                "tipo": "NOME_ALTERADO",
                "pasta": folder,
                "antes": locked[folder].get("nome"),
                "depois": current[folder].get("nome"),
                "severidade": "CRITICA"
            })

    result = {
        "ok": len(issues) == 0,
        "locked_at": lock_data.get("locked_at"),
        "version": lock_data.get("version"),
        "total_issues": len(issues),
        "criticas": len([i for i in issues if i["severidade"] == "CRITICA"]),
        "alertas": len([i for i in issues if i["severidade"] == "ALERTA"]),
        "issues": issues,
    }

    if result["ok"]:
        print("INTEGRIDADE OK - Nenhuma alteracao detectada")
    else:
        print(f"ALTERACOES DETECTADAS: {result['total_issues']} problemas")
        print(f"  Criticas: {result['criticas']}")
        print(f"  Alertas: {result['alertas']}")
        for i in issues:
            sev = "🔴" if i["severidade"] == "CRITICA" else "🟡"
            print(f"  {sev} {i['tipo']}: {i.get('pasta', '')} {i.get('arquivo', '')} {i.get('nome', '')}")
            if i["tipo"] == "NOME_ALTERADO":
                print(f"     '{i['antes']}' → '{i['depois']}'")

    return result


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"

    if cmd == "lock":
        lock()
    elif cmd == "verify":
        verify()
    elif cmd == "diff":
        result = verify()
        if not result["ok"]:
            print("\nDetalhes:")
            for i in result["issues"]:
                print(json.dumps(i, ensure_ascii=False, indent=2))
    else:
        print(f"Uso: python3 {__file__} [lock|verify|diff]")
