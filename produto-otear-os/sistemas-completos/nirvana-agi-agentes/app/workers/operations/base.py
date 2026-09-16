from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseOperation(ABC):
    @staticmethod
    @abstractmethod
    def validate_params(params: Dict[str, Any]):
        """Valida os parâmetros da operação"""
        pass

    @staticmethod
    @abstractmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        """Executa a operação usando FFmpeg"""
        pass
