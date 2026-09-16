
import os

file_path = r"d:\agi-agentes\frontend-react\src\components\ui\video-editor-panel.tsx"

replacements = {
    121: '                            content: `❌ **Erro no processamento:** ${status.error || status.error_message || "Falha desconhecida"}`,',
    154: '                        `🎬 **Vídeo carregado!** \`${result.filename}\` (${formatFileSize(result.size)})\n\n` +',
    155: '                        `Agora você pode pedir edições. Tente comandos como:\n` +',
    156: '                        `• **Adicionar legendas**\n` +',
    157: '                        `• **Cortar respiros** (remove silêncios)\n` +',
    158: '                        `• **Preset VIRAL** (legendas + corte de silêncio)\n` +',
    159: '                        `• **Preset CLEAN** (legendas estáticas + corte)`,',
    211: '                        content: `⏳ **${response.message}**\\n\\nAguarde enquanto o vídeo é processado...`,',
    235: '                        content: `❌ ${response.message}`,',
    247: '                    content: `❌ Erro: ${err instanceof Error ? err.message : "Falha na comunicação"}`,',
}

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # defined lines are 1-based, list is 0-based
    for line_num, new_content in replacements.items():
        if line_num - 1 < len(lines):
            # Keep original indentation
            original_line = lines[line_num - 1]
            leading_space = original_line[:len(original_line) - len(original_line.lstrip())]
            lines[line_num - 1] = leading_space + new_content.strip() + '\n'
            print(f"Replaced line {line_num}")
        else:
            print(f"Line {line_num} out of range")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Successfully updated video-editor-panel.tsx")

except Exception as e:
    print(f"Error: {e}")
