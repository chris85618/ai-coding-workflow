"""Change Management Protocol Algorithm.

Traceable to: FR-024, FR-025
Replaces: skills/workflow-skills/change-management-protocol.md
"""

from typing import Dict, Any, List
from enum import Enum

class ChangeType(str, Enum):
    CREATE = "CREATE"
    MODIFY = "MODIFY"
    FIX = "FIX"

class ChangeManagement:
    """Enforces the change management protocol for all mutations."""

    @classmethod
    def validate_pgvg(cls, content: str, original_content: str, change_type: ChangeType) -> List[str]:
        """Post-Generation Validation Gate (PGVG) checks."""
        failures = []
        
        # Format validation
        if "```" in content and content.count("```") % 2 != 0:
            failures.append("Markdown formatting error: unbalanced backticks.")
            
        # Count validation (if applicable)
        # ID check (if applicable)
        
        return failures

    @classmethod
    def verify_cm_gate_declaration(cls, response_content: str, expected_files: List[str]) -> bool:
        """Verifies that the inline CM-GATE declaration was made before writing."""
        
        # Fast fail if no declaration
        if "CM-GATE" not in response_content and "BATCH-CM" not in response_content:
            return False
            
        # Check coverage
        for file in expected_files:
            if file not in response_content:
                return False
                
        return True

    @classmethod
    def assert_session_end_hooks(cls, session_changes: List[Dict[str, Any]]) -> bool:
        """Step 6 closure protocol assertion."""
        
        for change in session_changes:
            if not change.get("step_0_classified"): return False
            if not change.get("step_1_generated"): return False
            if not change.get("step_2_pgvg"): return False
            if not change.get("step_3_micro_val"): return False
            if not change.get("step_4_rca_done"): return False
            
            if change.get("is_cross_cutting") and not change.get("step_5_done"):
                return False
                
        return True
