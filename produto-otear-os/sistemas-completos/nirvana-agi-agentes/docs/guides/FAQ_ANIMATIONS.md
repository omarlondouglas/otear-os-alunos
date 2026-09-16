# ❓ FAQ - Efeitos de Animação

## Perguntas Frequentes sobre os Efeitos de Legendas

### 🎨 Geral

**Q: Quantos efeitos de animação estão disponíveis?**
A: 3 efeitos - Estático (padrão), Highlight Word (karaoke) e Typewriter (digitação).

**Q: Posso usar múltiplos efeitos no mesmo vídeo?**
A: Não, escolha um efeito por operação. Mas você pode processar o mesmo vídeo múltiplas vezes.

**Q: Os efeitos funcionam em todos os idiomas?**
A: Sim! Funciona com qualquer idioma suportado pelo Whisper (100+ idiomas).

---

### ⌨️ Typewriter

**Q: Qual a velocidade ideal para typewriter?**
A: Depende do uso:
- 10-15: Dramático, lento
- 20-25: Normal, recomendado
- 30-40: Rápido, dinâmico

**Q: O typewriter funciona bem em vídeos longos?**
A: Funciona, mas pode cansar o espectador. Recomendado para vídeos até 10 minutos.

**Q: Posso fazer o typewriter mais lento que 10 chars/seg?**
A: Sim, mas valores muito baixos (< 5) podem parecer artificiais.

**Q: Como fazer efeito de terminal/hacker?**
A: Use:
```json
{
  "color": "#00FF00",
  "font": "Courier New",
  "animation": "typewriter",
  "typewriter_speed": 25
}
```

---

### ⭐ Highlight Word

**Q: Qual a diferença entre Highlight Word e Typewriter?**
A: 
- **Highlight Word**: Texto completo aparece, palavras mudam de cor
- **Typewriter**: Texto aparece caractere por caractere

**Q: Posso mudar as cores do highlight?**
A: Sim! Use `color` (texto normal) e `highlight_color` (palavra ativa).

**Q: O highlight funciona com palavras compostas?**
A: Sim, o Whisper detecta palavras automaticamente.

---

### 🎯 Performance

**Q: Qual efeito é mais rápido de processar?**
A: Estático > Highlight Word > Typewriter

**Q: O typewriter aumenta muito o tempo de processamento?**
A: Sim, cerca de 20-30% mais lento que estático devido aos eventos extras.

**Q: Posso processar múltiplos vídeos em paralelo?**
A: Sim! A API usa Celery para processamento assíncrono.

---

### 🔧 Técnico

**Q: Qual formato de legenda é usado?**
A: ASS (Advanced SubStation Alpha) para animações, SRT para estático.

**Q: As legendas são queimadas no vídeo?**
A: Sim, são permanentemente incorporadas (burned-in).

**Q: Posso extrair as legendas depois?**
A: Não, elas são queimadas. Use `keep_srt: true` para salvar o arquivo separado.

**Q: Qual modelo Whisper devo usar?**
A: 
- `tiny/base`: Rápido, menos preciso
- `small`: Balanceado (recomendado)
- `medium/large`: Mais preciso, mais lento

---

### 🎨 Estilo

**Q: Quais fontes posso usar?**
A: Qualquer fonte instalada no sistema. Comuns:
- Arial, Helvetica (limpa)
- Courier New, Consolas (terminal)
- Impact (impacto)
- Comic Sans MS (infantil)

**Q: Como centralizar as legendas?**
A: Use `"position": "center"`

**Q: Posso ajustar a margem?**
A: Sim, use `"margin_vertical": 30` (pixels)

**Q: Como fazer legendas maiores?**
A: Aumente `"font_size": 32`

---

### 🐛 Problemas Comuns

**Q: "Job failed" - O que fazer?**
A: Verifique:
1. Vídeo tem áudio?
2. Modelo Whisper está instalado?
3. Logs do worker (`docker-compose logs worker`)

**Q: Legendas não aparecem no vídeo**
A: Verifique:
1. `animation` está correto?
2. Cor tem contraste com o vídeo?
3. Teste com vídeo menor primeiro

**Q: Typewriter muito rápido/lento**
A: Ajuste `typewriter_speed`:
- Muito rápido? Diminua (ex: 15)
- Muito lento? Aumente (ex: 30)

**Q: Palavras cortadas no highlight**
A: Problema de sincronização do Whisper. Tente:
- Modelo maior (`medium`)
- Áudio mais limpo
- Verificar idioma correto

---

### 💰 Custos

**Q: Há custo adicional para usar animações?**
A: Não, tudo roda localmente com Whisper open-source.

**Q: Posso usar GPU para acelerar?**
A: Sim! Configure `USE_GPU=true` no `.env`

---

### 🚀 Uso Avançado

**Q: Posso combinar com outras operações?**
A: Sim! Exemplo:
```json
{
  "operations": [
    {"type": "trim", "params": {...}},
    {"type": "remove_silence", "params": {...}},
    {"type": "auto_subtitle", "params": {...}}
  ]
}
```

**Q: Posso usar vídeo de URL ao invés de upload?**
A: Sim! Use `"video_url": "https://..."` no request.

**Q: Como receber notificação quando terminar?**
A: Use `"webhook_url": "https://seu-site.com/callback"`

---

### 📚 Recursos

**Q: Onde encontro mais exemplos?**
A: Veja:
- [CURL_DOCUMENTATION.md](CURL_DOCUMENTATION.md)
- [ANIMATION_EFFECTS.md](ANIMATION_EFFECTS.md)
- [examples/](examples/)

**Q: Como contribuir com novos efeitos?**
A: Edite `app/utils/ass_generator.py` e adicione sua lógica!

---

**Não encontrou sua pergunta?** Abra uma issue no GitHub!
