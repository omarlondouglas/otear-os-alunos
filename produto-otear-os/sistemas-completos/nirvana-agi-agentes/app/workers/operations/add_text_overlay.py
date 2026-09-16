import ffmpeg
from app.workers.operations.base import BaseOperation
from typing import Dict, Any

class AddTextOverlayOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        if 'text' not in params:
            raise ValueError("AddTextOverlay requires 'text' parameter")

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        AddTextOverlayOperation.validate_params(params)
        
        text = params['text']
        
        # Posição
        position = params.get('position', 'bottom')  # top, bottom, center, custom
        x = params.get('x', None)
        y = params.get('y', None)
        
        # Estilo do texto
        font = params.get('font', 'Arial')
        font_size = params.get('font_size', 10)
        font_color = params.get('font_color', 'white')
        line_spacing = params.get('line_spacing', 0)  # Espaçamento entre linhas
        
        # Tarja/Background
        box = params.get('box', True)  # Mostrar tarja
        box_color = params.get('box_color', 'black')
        box_opacity = params.get('box_opacity', 0.7)  # 0.0 a 1.0
        box_padding = params.get('box_padding', 20)  # Padding em pixels (espaçamento interno da tarja)
        box_full_width = params.get('box_full_width', False)  # Tarja de largura completa
        box_height = params.get('box_height', None)  # Altura customizada da tarja (para full width)
        
        # Timing
        start_time = params.get('start_time', 0)
        duration = params.get('duration', None)  # None = até o fim
        
        # Alinhamento
        alignment = params.get('alignment', 'center')  # left, center, right
        
        try:
            # Calcular posição baseado no preset
            if x is None or y is None:
                if position == 'top':
                    x_pos = '(w-text_w)/2'  # Centralizado horizontalmente
                    y_pos = f'{box_padding}'
                elif position == 'bottom':
                    x_pos = '(w-text_w)/2'
                    y_pos = f'h-text_h-{box_padding}'
                elif position == 'center':
                    x_pos = '(w-text_w)/2'
                    y_pos = '(h-text_h)/2'
                elif position == 'top-left':
                    x_pos = f'{box_padding}'
                    y_pos = f'{box_padding}'
                elif position == 'top-right':
                    x_pos = f'w-text_w-{box_padding}'
                    y_pos = f'{box_padding}'
                elif position == 'bottom-left':
                    x_pos = f'{box_padding}'
                    y_pos = f'h-text_h-{box_padding}'
                elif position == 'bottom-right':
                    x_pos = f'w-text_w-{box_padding}'
                    y_pos = f'h-text_h-{box_padding}'
                else:
                    x_pos = '(w-text_w)/2'
                    y_pos = 'h-text_h-50'
            else:
                x_pos = str(x)
                y_pos = str(y)
            
            # Converter opacidade para alpha (0-1 para 0-255)
            box_alpha = int(box_opacity * 255)
            box_color_with_alpha = f'{box_color}@{box_alpha/255:.2f}'
            
            # Construir filtro drawtext
            drawtext_params = {
                'text': text.replace(':', '\\:').replace("'", "\\'"),
                'font': font,
                'fontsize': font_size,
                'fontcolor': font_color,
                'x': x_pos,
                'y': y_pos
            }
            
            # Adicionar espaçamento entre linhas se especificado
            if line_spacing > 0:
                drawtext_params['line_spacing'] = line_spacing
            
            # Adicionar tarja se habilitado
            if box:
                drawtext_params['box'] = 1
                drawtext_params['boxcolor'] = box_color_with_alpha
                drawtext_params['boxborderw'] = box_padding
            
            # Adicionar timing se especificado
            if start_time > 0 or duration is not None:
                enable_expr = f'gte(t,{start_time})'
                if duration is not None:
                    enable_expr += f'*lte(t,{start_time + duration})'
                drawtext_params['enable'] = enable_expr
            
            # Aplicar filtro
            input_stream = ffmpeg.input(input_path)
            video = input_stream.video
            audio = input_stream.audio
            
            # Se box_full_width, adicionar retângulo de fundo primeiro
            if box_full_width:
                # Calcular altura do retângulo
                if box_height:
                    rect_height = box_height
                else:
                    # Estimar altura baseado no texto (aproximado)
                    num_lines = text.count('\n') + 1
                    rect_height = int(font_size * num_lines * 1.5 + box_padding * 2)
                
                # Calcular posição Y do retângulo
                if position == 'top':
                    rect_y = 0
                elif position == 'center':
                    rect_y = f'(h-{rect_height})/2'
                else:  # bottom
                    rect_y = f'h-{rect_height}'
                
                # Converter opacidade para alpha (0-255)
                alpha_value = int(box_opacity * 255)
                
                # Adicionar retângulo de fundo
                video = video.filter(
                    'drawbox',
                    x=0,
                    y=rect_y,
                    width='iw',
                    height=rect_height,
                    color=f'{box_color}@{box_opacity}',
                    thickness='fill'
                )
                
                # Desabilitar box do drawtext (já temos o retângulo)
                drawtext_params['box'] = 0
            
            # Aplicar drawtext
            video = video.filter('drawtext', **drawtext_params)
            
            # Output
            output = ffmpeg.output(
                video, audio, output_path,
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                movflags='+faststart'
            )
            
            ffmpeg.run(output, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            
        except ffmpeg.Error as e:
            error_log = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"FFmpeg add text overlay failed: {error_log}")
