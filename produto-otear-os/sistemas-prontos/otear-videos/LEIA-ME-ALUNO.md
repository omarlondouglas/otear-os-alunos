# Otear Vídeos - Sistema Incluído

Esta pasta contém o sistema para pegar um vídeo ou link público e gerar transcrição.

## Para usar sem mexer em código

Abra o Otear OS e peça em linguagem natural:

```text
Otear OS, use o Otear Videos para transcrever este link:

[cole aqui o link do vídeo]

Depois transforme a transcrição em:
- resumo;
- diagnóstico do roteiro;
- ideias de próximos vídeos.
```

## O que existe aqui

- `scripts/transcrever_video.py`: ferramenta simples para baixar/transcrever um vídeo.
- `requirements.txt`: dependências técnicas para aluno avançado ou operador.
- `outputs/`: pasta onde as transcrições geradas podem ser salvas.

## Quando usar

Use Otear Videos quando o pedido envolver:

- transcrever vídeo;
- pegar a fala de um link;
- analisar vídeo de referência;
- melhorar roteiro com base em um vídeo;
- transformar vídeo em post, carrossel, e-mail ou novos roteiros.

## Observação importante

Alguns links de redes sociais podem bloquear o download automático. Se isso acontecer, baixe o arquivo de vídeo manualmente e envie o arquivo para o Otear OS analisar.
