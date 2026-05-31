"""Groq AI Provider - Milestone 2"""

import os
from typing import List, Optional
from loguru import logger

class GroqProvider:
    def __init__(self, api_keys: List[str], model: str = "llama-3.1-8b-instant"):
        self.api_keys = api_keys
        self.model = model
        self.current = 0
        self._init_client()
        logger.info(f"AI Ready: {len(api_keys)} keys")
    
    def _init_client(self):
        from groq import Groq
        self.client = Groq(api_key=self.api_keys[self.current])
    
    def _next_key(self):
        self.current = (self.current + 1) % len(self.api_keys)
        self._init_client()
        logger.info(f"Switched to key #{self.current + 1}")
    
    def suggest_fix(self, issue: str, context: str = "") -> Optional[str]:
        prompt = f"Suggest a fix for: {issue}\nContext: {context}\nProvide practical fix:"
        
        for _ in range(len(self.api_keys) * 2):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=300
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Failed: {e}")
                self._next_key()
        return None
