#!/usr/bin/env python3
"""
Disparo em massa via Evolution API (O Tear CRM)
Envia mensagens WhatsApp com delay configurável e salva log incremental.

Uso:
  python3 bulk_disparo.py --leads /tmp/leads_disparo.json --delay 180 --log-dir /tmp/disparos_log

Formato do JSON de entrada:
[
  {
    "nome": "Empresa X",
    "telefone": "5521999999999",
    "mensagem": "Olá! ...",
    "task_id": "wdu9v75nvx"
  }
]
"""

import argparse
import json
import os
import sys
import time
import requests
from datetime import datetime

# Config padrão (Evolution API)
DEFAULT_URL = os.environ.get("EVOLUTION_API_URL", "http://localhost:8080")
DEFAULT_INSTANCE = os.environ.get("EVOLUTION_INSTANCE", "default")
DEFAULT_KEY = os.environ.get("EVOLUTION_API_KEY", "")
DEFAULT_DELAY = 180  # 3 minutos


def clean_phone(phone: str) -> str:
    """Remove formatação e adiciona código do país se necessário."""
    digits = ''.join(c for c in phone if c.isdigit())
    # Se já começa com 55 e tem 11+ dígitos, está ok
    if digits.startswith('55') and len(digits) >= 11:
        return digits
    # Se tem 10 ou 11 dígitos (sem código), adiciona 55
    if len(digits) in [10, 11]:
        return '55' + digits
    return digits


def is_valid_whatsapp(phone: str) -> bool:
    """Verifica se o número provavelmente aceita WhatsApp."""
    digits = ''.join(c for c in phone if c.isdigit())
    # Números 0800 não aceitam WhatsApp
    if digits.startswith('550800') or digits.startswith('0800'):
        return False
    # Precisa ter pelo menos 11 dígitos (55 + DDD + 8 ou 9 dígitos)
    if len(digits) < 11:
        return False
    return True


def send_message(url, instance, key, phone, text):
    """Envia mensagem via Evolution API."""
    endpoint = f"{url}/message/sendText/{instance}"
    headers = {
        "Content-Type": "application/json",
        "apikey": key
    }
    payload = {
        "number": phone,
        "text": text,
        "options": {
            "delay": 1000,
            "presence": "composing",
            "linkPreview": True
        }
    }
    resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
    return resp


def main():
    parser = argparse.ArgumentParser(description="Disparo em massa via Evolution API")
    parser.add_argument("--leads", required=True, help="Arquivo JSON com lista de leads")
    parser.add_argument("--delay", type=int, default=DEFAULT_DELAY, help="Delay entre disparos (segundos)")
    parser.add_argument("--log-dir", default="/tmp/disparos_log", help="Diretório de log")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL da Evolution API")
    parser.add_argument("--instance", default=DEFAULT_INSTANCE, help="Instância")
    parser.add_argument("--key", default=DEFAULT_KEY, help="API Key")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem enviar")
    args = parser.parse_args()

    os.makedirs(args.log_dir, exist_ok=True)
    timestamp = int(time.time())
    log_file = os.path.join(args.log_dir, f"disparos_{timestamp}.log")

    # Carregar leads
    with open(args.leads, 'r') as f:
        leads = json.load(f)

    total = len(leads)
    enviados = 0
    falhas = 0
    skipped = 0
    resultados = []

    print("=" * 50)
    print(f" DISPAROS WHATSAPP - Evolution API")
    print(f" Total: {total} leads")
    print(f" Delay: {args.delay}s ({args.delay//60} min)")
    print(f" Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if args.dry_run:
        print(f" ⚠️  DRY RUN — não enviando mensagens")
    print("=" * 50)

    for idx, lead in enumerate(leads):
        seq = idx + 1
        nome = lead.get("nome", "Sem nome")
        telefone_raw = lead.get("telefone", "")
        msg = lead.get("mensagem", "")
        task_id = lead.get("task_id", "")

        telefone = clean_phone(telefone_raw)
        print(f"\n[{seq}/{total}] {nome}")
        print(f"  Telefone: {telefone_raw} → {telefone}")

        # Validação
        if not is_valid_whatsapp(telefone):
            print(f"  → SKIPPED (não aceita WhatsApp: {telefone_raw})")
            skipped += 1
            resultados.append({
                "seq": seq, "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "nome": nome, "telefone": telefone, "status": "skipped",
                "reason": "Número não aceita WhatsApp (0800 ou inválido)"
            })
            continue

        if args.dry_run:
            print(f"  → DRY RUN (pularia envio)")
            continue

        # Enviar
        try:
            resp = send_message(args.url, args.instance, args.key, telefone, msg)
            status_code = resp.status_code
            resp_text = resp.text[:300] if resp.text else "(vazio)"

            if status_code in [200, 201]:
                enviados += 1
                status_str = f"ENVIADO ✓ (HTTP {status_code})"
            else:
                falhas += 1
                status_str = f"FALHOU (HTTP {status_code})"

            print(f"  → {status_str}")
            print(f"     {resp_text[:150]}")

            resultados.append({
                "seq": seq, "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "nome": nome, "telefone": telefone, "task_id": task_id,
                "http_status": status_code, "response": resp_text,
                "success": status_code in [200, 201]
            })

        except requests.exceptions.Timeout:
            falhas += 1
            print(f"  → FALHOU (timeout)")
            resultados.append({
                "seq": seq, "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "nome": nome, "telefone": telefone, "task_id": task_id,
                "http_status": "timeout", "success": False
            })
        except Exception as e:
            falhas += 1
            print(f"  → FALHOU (erro: {str(e)[:100]})")
            resultados.append({
                "seq": seq, "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "nome": nome, "telefone": telefone, "task_id": task_id,
                "http_status": "error", "error": str(e)[:100], "success": False
            })

        # Salvar log incremental
        with open(log_file, 'w') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)

        # Delay entre disparos
        if idx < total - 1 and not args.dry_run:
            print(f"  Aguardando {args.delay}s...")
            time.sleep(args.delay)

    # Resumo final
    print(f"\n{'=' * 50}")
    print("  DISPARO FINALIZADO")
    print(f"  Enviados: {enviados}")
    print(f"  Falhas:   {falhas}")
    print(f"  Skipped:  {skipped}")
    print(f"  Total:    {total}")
    print(f"  Log:      {log_file}")
    print(f"{'=' * 50}")

    # Output JSON para captura
    print("\n=== RESULTADO_JSON ===")
    print(json.dumps({
        "enviados": enviados, "falhas": falhas, "skipped": skipped,
        "total": total, "log_file": log_file
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
