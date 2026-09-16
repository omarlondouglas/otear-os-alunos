#!/usr/bin/env python3

import os
from dotenv import load_dotenv

print("=== DEBUG VARIÁVEIS DE AMBIENTE ===")

# Carrega o .env
load_dotenv()

print(f"CAROUSEL_API_URL: {os.getenv('CAROUSEL_API_URL')}")
print(f"CAROUSEL_SERVICE_URL: {os.getenv('CAROUSEL_SERVICE_URL')}")
print(f"VIDEO_EDITOR_API_URL: {os.getenv('VIDEO_EDITOR_API_URL')}")
print(f"VIDEO_SERVICE_URL: {os.getenv('VIDEO_SERVICE_URL')}")

# Verifica se o .env existe
if os.path.exists('.env'):
    print("\n=== CONTEÚDO DO .ENV ===")
    with open('.env', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'CAROUSEL' in line or 'VIDEO' in line:
                print(line.strip())
else:
    print("Arquivo .env não encontrado!")