"""AI Analyzer - Milestone 2 with complete responses"""

import os
import re
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from loguru import logger

from .models import Issue
from .groq_provider import GroqProvider

load_dotenv()

@dataclass
class FixSuggestion:
    suggestion: str
    confidence: float

class AIAnalyzer:
    def __init__(self):
        keys = [os.getenv(f'GROQ_API_KEY_{i}') for i in range(1, 6) if os.getenv(f'GROQ_API_KEY_{i}')]
        
        if not keys:
            logger.warning("No API keys found")
            self.provider = None
            return
        
        model = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
        self.provider = GroqProvider(keys, model)
        logger.info(f"AI Analyzer ready")
    
    def suggest_fix(self, issue: Issue) -> Optional[FixSuggestion]:
        if not self.provider:
            return None
        
        # Better prompt for complete fix
        prompt = f"""Provide a complete, practical fix for this security issue:

Issue: {issue.description}
File: {issue.file_path.name}
Line: {issue.line_number}
Code: {issue.context or 'No context provided'}

Provide a clear, step-by-step fix with example code."""
        
        response = self.provider.suggest_fix(issue.description, issue.context or "")
        if response:
            return FixSuggestion(suggestion=response, confidence=0.85)
        return None
