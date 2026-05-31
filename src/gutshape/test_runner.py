"""Test Runner - Validate fixes don't break code"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, Any
from loguru import logger

class TestRunner:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
    
    def run_pytest(self) -> Dict[str, Any]:
        """Run pytest if available"""
        result = {
            "success": True,
            "tests_run": 0,
            "failures": 0,
            "errors": 0,
            "output": ""
        }
        
        try:
            # Check if pytest.ini or tests/ folder exists
            has_tests = (self.project_path / "tests").exists() or (self.project_path / "pytest.ini").exists()
            
            if not has_tests:
                logger.info("No tests found. Skipping...")
                return result
            
            # Run pytest
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "--tb=no"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            result["output"] = proc.stdout + proc.stderr
            result["success"] = proc.returncode == 0
            
            # Parse output (simple)
            if "failed" in proc.stdout:
                result["failures"] = 1
            
            logger.info(f"Tests {'passed' if result['success'] else 'failed'}")
            
        except Exception as e:
            logger.error(f"Test error: {e}")
            result["success"] = False
            result["errors"] = 1
        
        return result
    
    def run_npm_test(self) -> Dict[str, Any]:
        """Run npm test if package.json exists"""
        result = {"success": True, "output": ""}
        
        package_json = self.project_path / "package.json"
        if not package_json.exists():
            return result
        
        try:
            proc = subprocess.run(
                ["npm", "test", "--", "--watchAll=false"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            result["success"] = proc.returncode == 0
            result["output"] = proc.stdout + proc.stderr
            
        except Exception as e:
            logger.error(f"NPM test error: {e}")
            result["success"] = False
        
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all available tests"""
        results = {
            "pytest": self.run_pytest(),
            "npm": self.run_npm_test(),
            "overall_success": True
        }
        
        results["overall_success"] = results["pytest"]["success"] and results["npm"]["success"]
        
        return results
