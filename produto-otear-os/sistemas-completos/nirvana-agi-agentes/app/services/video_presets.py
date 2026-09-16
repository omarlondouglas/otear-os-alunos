from typing import Dict, Any, List

class VideoPresets:
    # Normalize as first step — converts HEVC→H.264, 30fps, keyframe 1s
    _NORMALIZE_OP = {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}}

    PRESETS = {
        "VIRAL": [
            {
                "type": "remove_silence",
                "params": {
                    "threshold": -40,
                    "padding": 0.3,
                    "min_silence_duration": 1.0
                }
            },
            {
                "type": "auto_subtitle",
                "params": {
                    "style": {
                        "font_size": 12,
                        "color": "#FFFF00",  # Yellow
                        "position": "bottom",
                        "animation": "typewriter",
                        "margin_vertical": 80
                    }
                }
            }
        ],
        "MODERN_SUBTITLES": [
            {
                "type": "auto_subtitle",
                "params": {
                    "style": {
                        "font_size": 10,
                        "color": "#FFFFFF",
                        "position": "bottom",
                        "animation": "highlight-word",
                        "margin_vertical": 60
                    }
                }
            }
        ],
        "REACTION": [
            {
                "type": "video_overlay",
                "params": {
                    "position": "bottom-right",
                    "scale": 0.3,
                    "chroma_key": True,
                    "chroma_color": "green",
                    "audio_mode": "mix",
                    "overlay_volume": 0.5
                }
            },
            {
                "type": "auto_subtitle",
                "params": {
                    "style": {
                        "font_size": 8,
                        "color": "#FFFFFF",
                        "position": "bottom",
                        "margin_vertical": 20
                    }
                }
            }
        ],
        "TITLE_BAR": [
            {
                "type": "add_text_overlay",
                "params": {
                    "text": "",
                    "position": "top",
                    "font_size": 28,
                    "font_color": "white",
                    "box": True,
                    "box_color": "black",
                    "box_opacity": 0.7,
                    "box_full_width": True,
                    "box_padding": 20,
                    "box_height": 80,
                }
            }
        ],
        "CLEAN": [
            {
                "type": "remove_silence",
                "params": {
                    "threshold": -35,
                    "padding": 0.08,
                    "min_silence_duration": 0.45
                }
            },
            {
                "type": "auto_subtitle",
                "params": {
                    "style": {
                        "font_size": 10,
                        "color": "#FFFFFF",
                        "position": "bottom",
                        "animation": "highlight-word",
                        "margin_vertical": 50
                    }
                }
            }
        ],
        "AULA": [
            {
                "type": "remove_silence",
                "params": {
                    "threshold": -42,
                    "padding": 0.3,
                    "min_silence_duration": 1.2
                }
            },
            {
                "type": "auto_subtitle",
                "params": {
                    "style": {
                        "font_size": 10,
                        "color": "#FFFFFF",
                        "position": "bottom",
                        "animation": "highlight-word",
                        "margin_vertical": 60
                    }
                }
            }
        ],
        "VIRAL_PRO": [
            {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}},
            {"type": "remove_silence", "params": {"threshold": -35, "padding": 0.1, "min_silence_duration": 0.5}},
            {
                "type": "remotion_render",
                "params": {
                    "mode": "viral",
                    "subtitles": {
                        "mode": "hormozi",
                        "fontSize": 52,
                        "primaryColor": "#FFFFFF",
                        "highlightColor": "#FFFF00",
                        "backgroundBlur": True,
                        "position": "center",
                        "maxWordsPerLine": 3
                    },
                    "transition": {"type": "zoom", "duration": 10},
                    "zoom": {"type": "slow-zoom-in", "intensity": 1.05},
                    "progressBar": {"style": "line", "color": "#FFFF00", "position": "top", "height": 3},
                    "quality": "high"
                }
            }
        ],
        "AULA_PRO": [
            {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}},
            {
                "type": "remove_silence",
                "params": {
                    "threshold": -42,
                    "padding": 0.3,
                    "min_silence_duration": 1.2
                }
            },
            {
                "type": "remotion_render",
                "params": {
                    "mode": "aula",
                    "subtitles": {
                        "mode": "karaoke",
                        "fontSize": 36,
                        "primaryColor": "#FFFFFF",
                        "highlightColor": "#4FC3F7",
                        "position": "bottom",
                        "maxWordsPerLine": 6
                    },
                    "transition": {"type": "none", "duration": 0},
                    "quality": "high"
                }
            }
        ],
        "HORMOZI": [
            {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}},
            {"type": "remove_silence", "params": {"threshold": -35, "padding": 0.08, "min_silence_duration": 0.45}},
            {
                "type": "remotion_render",
                "params": {
                    "mode": "viral",
                    "subtitles": {
                        "mode": "hormozi",
                        "fontSize": 56,
                        "fontFamily": "Arial Black",
                        "primaryColor": "#FFFFFF",
                        "highlightColor": "#FF0000",
                        "backgroundBlur": True,
                        "position": "center",
                        "maxWordsPerLine": 3,
                        "shadow": True
                    },
                    "transition": {"type": "zoom", "duration": 8},
                    "zoom": {"type": "punch", "intensity": 1.3},
                    "hookVisuals": [{"type": "watch-till-end", "startFrame": 0, "durationFrames": 60, "color": "#FF0000", "animation": "pulse"}],
                    "progressBar": {"style": "line", "color": "#FF0000", "position": "top", "height": 4},
                    "quality": "high"
                }
            }
        ],
        "PODCAST": [
            {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}},
            {"type": "remove_silence", "params": {"threshold": -42, "padding": 0.35, "min_silence_duration": 1.2}},
            {
                "type": "remotion_render",
                "params": {
                    "mode": "custom",
                    "template": "YouTubeVideo",
                    "subtitles": {
                        "mode": "karaoke",
                        "fontSize": 40,
                        "primaryColor": "#FFFFFF",
                        "highlightColor": "#FFFF00",
                        "position": "bottom",
                        "maxWordsPerLine": 5,
                        "outline": True
                    },
                    "transition": {"type": "fade", "duration": 15},
                    "zoom": {"type": "auto-face", "intensity": 1.1},
                    "branding": {"introTemplate": "minimal", "outroTemplate": "subscribe"},
                    "quality": "high"
                }
            }
        ],
        # ─── Full AI Pipeline: normalize → transcribe → plan_scenes → remotion ───
        "VIRAL_AI": [
            {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}},
            {"type": "remove_silence", "params": {"threshold": -40, "padding": 0.3, "min_silence_duration": 1.0}},
            {"type": "transcribe", "params": {"language": None, "word_timestamps": True}},
            {"type": "plan_scenes", "params": {"provider": "auto"}},
            {
                "type": "remotion_render",
                "params": {
                    "mode": "viral",
                    "subtitles": {
                        "mode": "hormozi",
                        "fontSize": 52,
                        "primaryColor": "#FFFFFF",
                        "highlightColor": "#FFFF00",
                        "backgroundBlur": True,
                        "position": "center",
                        "maxWordsPerLine": 3,
                    },
                    "transition": {"type": "zoom", "duration": 10},
                    "zoom": {"type": "slow-zoom-in", "intensity": 1.05},
                    "progressBar": {"style": "line", "color": "#FFFF00", "position": "top", "height": 3},
                    "quality": "high",
                }
            }
        ],
        # ─── editordofuturo pipeline: normalize → transcribe → select_clips (cascata LLM) ───
        # Output: JSON {source, clips:[{title, start, end, hook, reason}]} para review humano
        # antes de chamar extract_clips/remotion_render.
        "VIRAL_FUTURO": [
            {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}},
            {"type": "transcribe", "params": {"language": None, "word_timestamps": True}},
            {
                "type": "select_clips",
                "params": {
                    "max_clips": 5,
                    "min_duration": 30,
                    "max_duration": 75,
                },
            },
        ],
        # VIRAL_FUTURO_PRO: select_clips + eval_cuts (com snap automatico).
        # Saida final = relatorio eval.json com clipes ja ajustados aos boundaries de palavras.
        "VIRAL_FUTURO_PRO": [
            {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}},
            {"type": "transcribe", "params": {"language": None, "word_timestamps": True}},
            {
                "type": "select_clips",
                "params": {"max_clips": 5, "min_duration": 30, "max_duration": 75},
            },
            {
                "type": "eval_cuts",
                "params": {"apply": True},  # auto-snap aos boundaries de palavras
            },
        ],
        # CLEAN_PRO: silencio + filler words ("uh", "tipo", "ne") detectados via transcript.
        # Saida = JSON {keep, removed} pronto pra alimentar smart_cut.
        "CLEAN_PRO": [
            {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}},
            {"type": "transcribe", "params": {"language": None, "word_timestamps": True}},
            {
                "type": "detect_fillers",
                "params": {"silence_threshold": 0.6, "padding": 0.08},
            },
        ],
        # FAST_HORMOZI: legendas word-by-word via FFmpeg+libass (10x mais rapido que Remotion).
        # Sem motion graphics — ideal pra previews ou render em massa.
        "FAST_HORMOZI": [
            {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}},
            {"type": "transcribe", "params": {"language": None, "word_timestamps": True}},
            {
                "type": "fast_subtitles",
                "params": {
                    "position": "center",
                    "vertical": True,
                    "font": "Urbanist",
                    "font_size": 72,
                    "color_primary": "FFFFFF",
                    "color_highlight": "FFD600",
                    "max_words": 3,
                },
            },
        ],
        "AULA_AI": [
            {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}},
            {"type": "remove_silence", "params": {"threshold": -42, "padding": 0.3, "min_silence_duration": 1.2}},
            {"type": "transcribe", "params": {"language": None, "word_timestamps": True}},
            {"type": "plan_scenes", "params": {"provider": "auto", "custom_prompt": "This is educational content. Use card, flow, and split scenes. Avoid fullscreen and stickfigure."}},
            {
                "type": "remotion_render",
                "params": {
                    "mode": "aula",
                    "subtitles": {
                        "mode": "karaoke",
                        "fontSize": 36,
                        "primaryColor": "#FFFFFF",
                        "highlightColor": "#4FC3F7",
                        "position": "bottom",
                        "maxWordsPerLine": 6,
                    },
                    "transition": {"type": "fade", "duration": 10},
                    "quality": "high",
                }
            }
        ],
    }

    @classmethod
    def get_operations(cls, preset_name: str) -> List[Dict[str, Any]]:
        return cls.PRESETS.get(preset_name.upper(), [])

    @classmethod
    def list_available(cls) -> List[str]:
        return list(cls.PRESETS.keys())
