# Otear Videos

Sistema pronto do Otear OS para transcricao e analise inicial de videos.

## Entrada

- link publico de video;
- arquivo de video local;
- arquivo de audio local.

## Saida

- transcricao em JSON;
- transcricao legivel em Markdown;
- base para resumo, diagnostico de roteiro e proximos conteudos.

## Uso avancado

Instale as dependencias:

```bash
pip install -r produto-otear-os/sistemas-prontos/otear-videos/requirements.txt
```

Transcrever um link:

```bash
python produto-otear-os/sistemas-prontos/otear-videos/scripts/transcrever_video.py "https://exemplo.com/video"
```

Transcrever um arquivo:

```bash
python produto-otear-os/sistemas-prontos/otear-videos/scripts/transcrever_video.py caminho/do/video.mp4
```

Por padrao, o script usa OpenAI se `OPENAI_API_KEY` estiver configurada. Sem chave, tenta usar `faster-whisper` local.

