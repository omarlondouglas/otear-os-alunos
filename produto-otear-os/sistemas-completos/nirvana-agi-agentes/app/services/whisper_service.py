import os
from typing import Dict, Any
from openai import OpenAI

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_DEFAULT_MODEL = "whisper-large-v3-turbo"
GROQ_MAX_SIZE = 25 * 1024 * 1024  # 25MB
OPENAI_DEFAULT_MODEL = "whisper-1"
OPENAI_MAX_SIZE = 25 * 1024 * 1024


class WhisperService:
    """Cascata: Groq (whisper-large-v3-turbo) -> OpenAI (whisper-1) -> faster-whisper local.

    Provider escolhido via env TRANSCRIPTION_PROVIDER (groq | openai | local).
    Quando groq/openai sao escolhidos mas a chave esta ausente, cai para local.
    """

    def __init__(self, model_size: str = "base"):
        self.provider = os.getenv("TRANSCRIPTION_PROVIDER", "openai").lower()
        self.model_size = model_size

        if self.provider == "groq":
            self.api_key = os.getenv("GROQ_API_KEY")
            self.api_model = os.getenv("GROQ_WHISPER_MODEL", GROQ_DEFAULT_MODEL)
            self.api_max_size = GROQ_MAX_SIZE
            if not self.api_key:
                print("Warning: GROQ_API_KEY not set. Falling back to OpenAI.")
                self.provider = "openai"

        if self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.api_model = OPENAI_DEFAULT_MODEL
            self.api_max_size = OPENAI_MAX_SIZE
            if not self.api_key:
                print("Warning: OPENAI_API_KEY not set. Falling back to local.")
                self.provider = "local"

        if self.provider == "local":
            from faster_whisper import WhisperModel
            device = "cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            print(f"Loading Local Whisper model: {model_size} on {device}...")
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        elif self.provider == "groq":
            print(f"Initializing Groq client ({self.api_model})...")
            self.client = OpenAI(api_key=self.api_key, base_url=GROQ_BASE_URL)
        else:
            print("Initializing OpenAI client for transcription...")
            self.client = OpenAI(api_key=self.api_key)

    def transcribe(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        if self.provider in ("openai", "groq"):
            return self._transcribe_api(audio_path, language)
        return self._transcribe_local(audio_path, language)

    def _transcribe_api(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        file_size = os.path.getsize(audio_path)
        if file_size <= self.api_max_size:
            return self._transcribe_api_simple(audio_path, language)
        print(f"File size {file_size} bytes exceeds limit. Splitting into chunks...")
        return self._transcribe_api_chunked(audio_path, language)

    def _transcribe_api_simple(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model=self.api_model,
                file=audio_file,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
            )

        return {
            "provider": self.provider,
            "model": self.api_model,
            "language": getattr(transcript, "language", "unknown"),
            "duration": getattr(transcript, "duration", 0),
            "text": transcript.text,
            "segments": [
                {"start": seg.start, "end": seg.end, "text": seg.text.strip()}
                for seg in transcript.segments
            ],
            "words": [
                {"word": w.word, "start": w.start, "end": w.end}
                for w in getattr(transcript, "words", [])
            ],
        }

    def _transcribe_api_chunked(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        import ffmpeg
        import math

        try:
            probe = ffmpeg.probe(audio_path)
            duration = float(probe["format"]["duration"])
        except ffmpeg.Error as e:
            print(f"Error probing file: {e.stderr.decode() if e.stderr else str(e)}")
            raise RuntimeError("Failed to probe audio file duration")

        CHUNK_DURATION = 600
        chunks = math.ceil(duration / CHUNK_DURATION)

        combined_segments = []
        combined_text = []
        combined_words = []
        detected_language = "unknown"

        print(f"Total duration: {duration}s. Split into {chunks} chunks.")

        for i in range(chunks):
            start_time = i * CHUNK_DURATION
            chunk_filename = f"{audio_path}.chunk{i}.mp3"
            print(f"Processing chunk {i+1}/{chunks} (Start: {start_time}s)...")
            try:
                stream = ffmpeg.input(audio_path, ss=start_time, t=CHUNK_DURATION)
                stream = ffmpeg.output(stream, chunk_filename, acodec="libmp3lame", audio_bitrate="128k")
                ffmpeg.run(stream, overwrite_output=True, quiet=True)

                chunk_result = self._transcribe_api_simple(chunk_filename, language)
                if i == 0:
                    detected_language = chunk_result["language"]
                combined_text.append(chunk_result["text"])

                for seg in chunk_result["segments"]:
                    seg["start"] += start_time
                    seg["end"] += start_time
                    combined_segments.append(seg)

                if "words" in chunk_result:
                    for w in chunk_result["words"]:
                        w["start"] += start_time
                        w["end"] += start_time
                        combined_words.append(w)
            except Exception as e:
                print(f"Error processing chunk {i}: {str(e)}")
                raise
            finally:
                if os.path.exists(chunk_filename):
                    os.remove(chunk_filename)

        return {
            "provider": self.provider,
            "model": self.api_model,
            "language": detected_language,
            "duration": duration,
            "text": " ".join(combined_text),
            "segments": combined_segments,
            "words": combined_words,
        }

    def _transcribe_local(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            word_timestamps=True,
        )

        segment_list = list(segments)
        full_text = []
        words_list = []
        output_segments = []

        for seg in segment_list:
            full_text.append(seg.text)
            output_segments.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip(),
            })
            if hasattr(seg, "words") and seg.words:
                for w in seg.words:
                    words_list.append({"word": w.word, "start": w.start, "end": w.end})

        return {
            "provider": "local",
            "model": self.model_size,
            "language": info.language,
            "duration": info.duration,
            "text": " ".join(full_text),
            "segments": output_segments,
            "words": words_list,
        }
