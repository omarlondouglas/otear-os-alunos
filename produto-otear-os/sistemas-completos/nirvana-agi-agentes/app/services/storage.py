import os
import base64
import uuid
import mimetypes
import logging
from datetime import datetime
from fastapi import UploadFile

logger = logging.getLogger(__name__)


def _get_s3_client():
    """Cria client boto3 para S3/MinIO.

    Usa S3_INTERNAL_URL se definido (rede interna Docker, bypassa Traefik e seus
    limites de body size). Fallback para S3_ENDPOINT_URL (URL pública).
    """
    # Preferir URL interna para uploads server-side (evita limite 413 do Traefik)
    s3_endpoint = (
        os.getenv('S3_INTERNAL_URL', '').strip().rstrip('/')
        or os.getenv('S3_ENDPOINT_URL', '').strip().rstrip('/')
    )
    s3_access_key = os.getenv('S3_ACCESS_KEY')
    s3_secret_key = os.getenv('S3_SECRET_KEY')
    s3_region = os.getenv('S3_REGION', 'us-east-1')

    if not all([s3_endpoint, s3_access_key, s3_secret_key]):
        return None

    import boto3
    from botocore.client import Config
    return boto3.client(
        's3',
        endpoint_url=s3_endpoint,
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        config=Config(
            signature_version='s3v4',
            connect_timeout=5,      # falha rápido se MinIO não responde (evita 502 no Traefik)
            read_timeout=300,       # 5min para leitura de chunks grandes
            retries={'max_attempts': 1},
        ),
        region_name=s3_region,
    )


def _get_s3_public_url(object_key: str) -> str:
    """Gera URL pública para um objeto no S3/R2."""
    s3_bucket = os.getenv('S3_BUCKET_NAME', 'videos_agi')
    s3_endpoint = os.getenv('S3_ENDPOINT_URL', '').strip().rstrip('/')
    public_base = os.getenv('S3_PUBLIC_URL', s3_endpoint).strip().rstrip('/')
    # R2: URL pública já é bucket-scoped (pub-xxx.r2.dev/{key}, sem bucket no path)
    is_r2 = 'r2.cloudflarestorage.com' in s3_endpoint or 'r2.dev' in public_base
    if is_r2 or public_base.endswith(f"/{s3_bucket}"):
        return f"{public_base}/{object_key}"
    return f"{public_base}/{s3_bucket}/{object_key}"


class StorageService:
    def __init__(self):
        self.storage_path = os.getenv("STORAGE_PATH", "/app/storage")
        self.public_url = os.getenv("PUBLIC_URL", "http://localhost:8000")
        os.makedirs(self.storage_path, exist_ok=True)

    def _get_url(self, filename: str) -> str:
        base = self.public_url.rstrip("/")
        return f"{base}/static/{filename}"

    async def save_upload_file(self, file: UploadFile) -> str:
        """Save an UploadFile to storage and return its public URL."""
        url, _ = await self.save_upload_file_streaming(file)
        return url

    async def save_upload_file_streaming(
        self, file: UploadFile, max_size: int = 0
    ) -> tuple[str, int]:
        """
        Save an UploadFile via streaming. Tenta upload para S3 primeiro.
        Se S3 não configurado, salva localmente. Returns (url, file_size).
        """
        if not file.filename:
            ext = mimetypes.guess_extension(file.content_type or "") or ".bin"
            base_name = f"upload_{uuid.uuid4().hex}"
        else:
            ext = os.path.splitext(file.filename)[1]
            if not ext:
                ext = mimetypes.guess_extension(file.content_type or "") or ".bin"
            base_name = os.path.splitext(file.filename)[0].replace(" ", "_").lower()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        vid_id = uuid.uuid4().hex[:8]
        filename = f"{base_name}_{timestamp}_{vid_id}{ext}"

        # Tentar upload direto para S3 via multipart
        s3_client = _get_s3_client()
        if s3_client:
            try:
                return await self._upload_to_s3_multipart(
                    s3_client, file, filename, max_size,
                    content_type=file.content_type or "video/mp4",
                )
            except Exception as e:
                logger.warning(f"S3 upload falhou, fallback para local: {e}")

        # Fallback: salvar localmente
        filepath = os.path.join(self.storage_path, filename)
        total_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks

        with open(filepath, "wb") as f:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                total_size += len(chunk)
                if max_size and total_size > max_size:
                    f.close()
                    os.remove(filepath)
                    from fastapi import HTTPException
                    raise HTTPException(
                        413,
                        f"Arquivo muito grande. Máximo: {max_size // (1024*1024)}MB"
                    )
                f.write(chunk)

        return self._get_url(filename), total_size

    async def _upload_to_s3_multipart(
        self, s3_client, file: UploadFile, filename: str,
        max_size: int, content_type: str,
    ) -> tuple[str, int]:
        """Upload via S3 multipart — suporta arquivos grandes (1GB+).

        Usa run_in_executor para não bloquear o event loop do FastAPI durante
        as chamadas síncronas do boto3 (create_multipart_upload, upload_part, etc.).
        """
        import asyncio
        loop = asyncio.get_event_loop()

        bucket = os.getenv('S3_BUCKET_NAME', 'videos_agi')
        object_key = f"videos/{filename}"
        chunk_size = 10 * 1024 * 1024  # 10MB parts (mínimo S3 é 5MB)

        # Iniciar multipart upload sem bloquear o event loop
        mpu = await loop.run_in_executor(
            None,
            lambda: s3_client.create_multipart_upload(
                Bucket=bucket, Key=object_key, ContentType=content_type,
            )
        )
        upload_id = mpu["UploadId"]

        parts = []
        part_number = 1
        total_size = 0
        first_chunk = None  # Guardado para fallback de arquivo < 10MB (1 parte)

        try:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                total_size += len(chunk)
                if max_size and total_size > max_size:
                    raise ValueError(f"Arquivo excede {max_size // (1024*1024)}MB")

                # Guardar primeiro chunk para evitar re-leitura bugada (seek em stream)
                if part_number == 1:
                    first_chunk = chunk

                part_num = part_number
                chunk_data = chunk  # captura local para lambda
                resp = await loop.run_in_executor(
                    None,
                    lambda: s3_client.upload_part(
                        Bucket=bucket, Key=object_key,
                        UploadId=upload_id, PartNumber=part_num,
                        Body=chunk_data,
                    )
                )
                parts.append({"ETag": resp["ETag"], "PartNumber": part_num})
                part_number += 1

            if not parts:
                raise ValueError("Arquivo vazio")

            # Arquivo pequeno (<10MB, 1 parte): cancelar multipart e usar put_object.
            # IMPORTANTE: não faz seek(0) + re-leitura pois o stream já foi consumido.
            # Usa first_chunk que foi guardado em memória.
            if len(parts) == 1:
                await loop.run_in_executor(
                    None,
                    lambda: s3_client.abort_multipart_upload(
                        Bucket=bucket, Key=object_key, UploadId=upload_id,
                    )
                )
                chunk_to_upload = first_chunk
                await loop.run_in_executor(
                    None,
                    lambda: s3_client.put_object(
                        Bucket=bucket, Key=object_key,
                        Body=chunk_to_upload, ContentType=content_type,
                    )
                )
            else:
                # Completar multipart
                parts_snapshot = list(parts)
                await loop.run_in_executor(
                    None,
                    lambda: s3_client.complete_multipart_upload(
                        Bucket=bucket, Key=object_key,
                        UploadId=upload_id,
                        MultipartUpload={"Parts": parts_snapshot},
                    )
                )

            logger.info(f"S3 upload OK: {object_key} ({total_size / (1024*1024):.1f}MB, {len(parts)} parts)")
            return _get_s3_public_url(object_key), total_size

        except Exception:
            # Cancelar multipart em caso de erro (não bloqueia event loop)
            try:
                await loop.run_in_executor(
                    None,
                    lambda: s3_client.abort_multipart_upload(
                        Bucket=bucket, Key=object_key, UploadId=upload_id,
                    )
                )
            except Exception:
                pass
            raise

    def upload_base64(self, b64_data: str, ext: str, mimetype: str) -> str:
        """Save a base64 string to storage and optionally to S3, returning its public URL."""
        try:
            # Remove header if present (data:image/png;base64,...)
            if "," in b64_data:
                header, b64_data = b64_data.split(",", 1)
            
            file_data = base64.b64decode(b64_data)
            
            filename = f"upload_{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(self.storage_path, filename)
            
            with open(filepath, "wb") as f:
                f.write(file_data)
                
            s3_url = self.upload_bytes_to_s3(file_data, filename, mimetype)
            if s3_url:
                return s3_url
                
            return self._get_url(filename)
        except Exception as e:
            print(f"Error saving base64: {e}")
            return ""

    def upload_bytes_to_s3(self, file_data: bytes, filename: str, content_type: str) -> str:
        """Uploads bytes to S3 and returns the public URL if S3 is configured."""
        try:
            s3_endpoint = os.getenv('S3_ENDPOINT_URL', '').strip().rstrip('/')
            s3_access_key = os.getenv('S3_ACCESS_KEY')
            s3_secret_key = os.getenv('S3_SECRET_KEY')
            s3_bucket = os.getenv('S3_BUCKET_NAME', 'videos_agi')
            s3_region = os.getenv('S3_REGION', 'auto')

            if not all([s3_endpoint, s3_access_key, s3_secret_key]):
                return ""

            import boto3
            from botocore.client import Config
            
            s3_client = boto3.client(
                's3',
                endpoint_url=s3_endpoint,
                aws_access_key_id=s3_access_key,
                aws_secret_access_key=s3_secret_key,
                config=Config(signature_version='s3v4'),
                region_name=s3_region
            )

            # Define a key path inside the bucket, e.g. images/<filename>
            object_key = f"images/{filename}"

            s3_client.put_object(
                Bucket=s3_bucket,
                Key=object_key,
                Body=file_data,
                ContentType=content_type,
            )
            
            # Construct public URL.
            # Cloudflare R2 public domains are already bucket-scoped, so adding
            # the bucket once more produces a valid-looking URL that is not an
            # image (404/XML response in the browser).
            # Supabase: S3_PUBLIC_URL=https://<ref>.supabase.co/storage/v1/object/public/<bucket>
            # MinIO: S3_PUBLIC_URL=https://minio.example.com
            public_base = os.getenv('S3_PUBLIC_URL', s3_endpoint).strip().rstrip('/')
            is_r2 = 'r2.cloudflarestorage.com' in s3_endpoint or 'r2.dev' in public_base
            if is_r2 or public_base.endswith(f"/{s3_bucket}"):
                public_url = f"{public_base}/{object_key}"
            else:
                public_url = f"{public_base}/{s3_bucket}/{object_key}"
            
            return public_url
            
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return ""
