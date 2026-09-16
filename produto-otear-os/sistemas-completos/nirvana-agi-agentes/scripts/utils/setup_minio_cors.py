"""
Script para configurar MinIO para upload direto do browser.

O que este script faz:
  1. Configura política pública de leitura nos vídeos (via minio SDK)
  2. Instrui como configurar CORS manualmente (necessário para upload direto)

Uso: python setup_minio_cors.py

CORS precisa ser configurado manualmente via mc (MinIO Client):
  mc alias set myminio <S3_ENDPOINT_URL> <S3_ACCESS_KEY> <S3_SECRET_KEY>
  mc anonymous set download myminio/agi/videos
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()


def setup():
    from minio import Minio

    endpoint = os.getenv("S3_ENDPOINT_URL", "").replace("https://", "").replace("http://", "").rstrip("/")
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")
    bucket = os.getenv("S3_BUCKET_NAME", "agi")
    secure = not os.getenv("S3_ENDPOINT_URL", "https://").startswith("http://")

    if not all([endpoint, access_key, secret_key]):
        print("ERRO: S3_ENDPOINT_URL, S3_ACCESS_KEY e S3_SECRET_KEY são necessárias.")
        return

    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    # Política pública de leitura para vídeos (worker e player conseguem acessar)
    policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"AWS": ["*"]},
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket}/videos/*"],
        }],
    })
    client.set_bucket_policy(bucket, policy)
    print(f"✅ Política pública de leitura configurada para '{bucket}/videos/*'")

    print()
    print("=" * 60)
    print("CORS — configuração manual necessária")
    print("=" * 60)
    print("Esta versão do MinIO não suporta configurar CORS via API.")
    print("Configure via MinIO Web Console ou via mc:")
    print()
    print(f"  mc alias set myminio https://{endpoint} {access_key} {secret_key}")
    print(f"  mc anonymous set download myminio/{bucket}/videos")
    print()
    print("Ou acesse o MinIO console e configure CORS manualmente no bucket.")
    print()
    print("Alternativamente, adicione no serviço MinIO do EasyPanel:")
    print("  Variável de ambiente: MINIO_API_CORS_ALLOW_ORIGIN=*")


if __name__ == "__main__":
    setup()
