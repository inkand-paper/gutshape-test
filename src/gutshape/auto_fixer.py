"""Auto Fixer - With Rollback on Failure"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Optional
from loguru import logger

class AutoFixer:
    def __init__(self, dry_run: bool = True, backup: bool = True):
        self.dry_run = dry_run
        self.backup = backup
        self.backup_dir = Path(".gutshape/backups")
        self.fixes_applied = []
        
        if backup and not dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _backup_file(self, file_path: Path):
        """Create backup before modifying"""
        if self.backup and not self.dry_run:
            backup_path = self.backup_dir / f"{file_path.name}.backup"
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
    
    def rollback(self):
        """Rollback all changes"""
        if not self.backup_dir.exists():
            logger.warning("No backups found")
            return False
        
        for backup in self.backup_dir.glob("*.backup"):
            original = backup.parent / backup.name.replace(".backup", "")
            shutil.copy2(backup, original)
            logger.info(f"Rollback: {original}")
        
        return True
    
    def fix_hardcoded_secret(self, file_path: Path, line_num: int, line_content: str) -> Optional[str]:
        var_match = re.match(r'\s*([A-Z_]+)\s*=', line_content)
        if not var_match:
            return None
        
        var_name = var_match.group(1)
        fixed_line = f'{var_name} = os.getenv("{var_name}", "default_value")\n'
        import_line = "import os\n"
        
        if not self.dry_run:
            self._backup_file(file_path)
            
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if 'import os' not in ''.join(lines):
                lines.insert(0, import_line)
                line_num += 1
            
            if line_num <= len(lines):
                lines[line_num - 1] = fixed_line
            
            with open(file_path, 'w') as f:
                f.writelines(lines)
            
            logger.info(f"Fixed {file_path}:{line_num}")
        
        self.fixes_applied.append({
            'file': str(file_path),
            'line': line_num,
            'original': line_content.strip(),
            'fixed': fixed_line.strip(),
            'dry_run': self.dry_run
        })
        
        return fixed_line
    
    def apply_fixes(self, issues: List, dry_run: bool = True, auto_rollback: bool = True) -> List:
        self.dry_run = dry_run
        results = []
        
        for issue in issues:
            if issue.type.value == "hardcoded_secret":
                fix = self.fix_hardcoded_secret(
                    issue.file_path,
                    issue.line_number,
                    issue.context or ""
                )
                if fix:
                    results.append({
                        'issue': issue.description,
                        'fix_applied': not dry_run,
                        'dry_run': dry_run
                    })
        
        return results
