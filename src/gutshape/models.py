from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

class IssueSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class IssueType(Enum):
    HARDCODED_SECRET = "hardcoded_secret"
    OUTDATED_DEPENDENCY = "outdated_dependency"
    MISSING_CONFIG = "missing_config"

@dataclass
class Issue:
    type: IssueType
    severity: IssueSeverity
    file_path: Path
    line_number: int
    description: str
    suggestion: Optional[str] = None
    context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScanResult:
    timestamp: datetime
    total_files_scanned: int
    issues: List[Issue]
    scan_duration_ms: int
    
    @property
    def total_issues(self) -> int:
        return len(self.issues)
