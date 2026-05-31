import re
import time
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from loguru import logger
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from .models import Issue, IssueType, IssueSeverity, ScanResult

class CodeScanner:
    """Scans codebase for security issues"""
    
    SECRET_PATTERNS = {
        'password': re.compile(r'(password|passwd|pwd)\s*=\s*["\']([^"\']{8,})', re.IGNORECASE),
        'api_key': re.compile(r'(api[_-]?key|apikey)\s*=\s*["\']([a-zA-Z0-9]{16,})', re.IGNORECASE),
        'token': re.compile(r'(token|bearer|jwt)\s*=\s*["\']([a-zA-Z0-9_\-\.]{20,})', re.IGNORECASE),
    }
    
    IGNORE_PATTERNS = [
        "*.pyc", "__pycache__/", ".git/", ".env", "venv/", ".venv/",
        "node_modules/", "dist/", "build/", "*.egg-info/"
    ]
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.ignore_spec = PathSpec.from_lines(GitWildMatchPattern, self.IGNORE_PATTERNS)
        
    def scan(self) -> ScanResult:
        logger.info(f"Scanning {self.project_root}")
        start_time = time.time()
        
        all_issues = []
        files_scanned = 0
        
        for file_path in self.project_root.rglob("*"):
            if self._should_ignore(file_path):
                continue
            if file_path.is_file():
                files_scanned += 1
                issues = self._scan_file(file_path)
                all_issues.extend(issues)
        
        return ScanResult(
            timestamp=datetime.now(),
            total_files_scanned=files_scanned,
            issues=all_issues,
            scan_duration_ms=int((time.time() - start_time) * 1000)
        )
    
    def _should_ignore(self, path: Path) -> bool:
        try:
            rel_path = str(path.relative_to(self.project_root))
            return self.ignore_spec.match_file(rel_path)
        except ValueError:
            return False
    
    def _scan_file(self, file_path: Path) -> List[Issue]:
        issues = []
        if file_path.suffix in ['.py', '.js', '.ts', '.java', '.go']:
            issues.extend(self._scan_for_secrets(file_path))
        return issues
    
    def _scan_for_secrets(self, file_path: Path) -> List[Issue]:
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f.readlines(), 1):
                    for secret_type, pattern in self.SECRET_PATTERNS.items():
                        if pattern.search(line):
                            if 'example' not in line.lower() and 'test' not in line.lower():
                                issues.append(Issue(
                                    type=IssueType.HARDCODED_SECRET,
                                    severity=IssueSeverity.CRITICAL,
                                    file_path=file_path,
                                    line_number=line_num,
                                    description=f"Hardcoded {secret_type} found",
                                    suggestion="Use environment variables",
                                    context=line.strip()[:200]
                                ))
        except Exception as e:
            logger.debug(f"Error scanning {file_path}: {e}")
        return issues
