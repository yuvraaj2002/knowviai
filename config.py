import os
from pydantic_settings import BaseSettings
from typing import List
from itertools import cycle

class Settings(BaseSettings):
    """
    Settings for the QA Finetuning project.
    """
    llama_parse_key: str
    gemini_keys: str  # Comma-separated string of Gemini API keys
    
    # Instance variable for the Gemini key cycle
    _gemini_api_key_cycle: cycle = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Split the comma-separated keys and create a cycle iterator
        if self.gemini_keys:
            self._gemini_api_key_cycle = cycle(self.gemini_keys.split(','))

    def get_next_gemini_key(self) -> str:
        """
        Get the next Gemini API key from the cycle.
        
        Returns:
            str: The next API key in the cycle
        """
        if not self._gemini_api_key_cycle:
            raise ValueError("No Gemini API keys configured")
        return next(self._gemini_api_key_cycle)

    class Config:
        # Pydantic-settings will automatically look for a .env file
        # and load the environment variables from there.
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings():
    return Settings()