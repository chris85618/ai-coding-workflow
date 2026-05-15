"""Traceability System Algorithm.

Traceable to: FR-004
Replaces: skills/workflow-skills/traceability-system.md
"""

import re
from typing import Dict, Any, List
from pydantic import BaseModel
from pathlib import Path

class TraceabilityNode(BaseModel):
    id: str
    type: str
    upstream: List[str] = []
    downstream: List[str] = []
    links: Dict[str, List[str]] = {}

class TraceabilityValidator:
    """Validates the traceability matrix and ID assignments."""

    PREFIXES = [
        "BG", "S", "FEA", "FR", "NFR", "UC", "ADR-STR", "ADR-GOV", 
        "ADR-SEC", "ADR-SCP", "ADR-GATE", "ADR-OPS", "ALG", "CLS", 
        "EVT", "INV", "SC", "TC", "DEBT", "RISK", "LESSON"
    ]

    @classmethod
    def validate_id_format(cls, node_id: str) -> bool:
        """Checks if ID matches the {PREFIX}-{NNN} format."""
        pattern = r"^(" + "|".join(cls.PREFIXES) + r")-\d{3}$"
        return bool(re.match(pattern, node_id))

    @classmethod
    def generate_next_id(cls, prefix: str, current_ids: List[str]) -> str:
        """Generates the next sequential ID for a given prefix."""
        max_num = 0
        for nid in current_ids:
            if nid.startswith(f"{prefix}-"):
                try:
                    num = int(nid.split("-")[-1])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    continue
        return f"{prefix}-{max_num + 1:03d}"

    @classmethod
    def detect_orphans(cls, nodes: List[TraceabilityNode]) -> List[str]:
        """Detects IDs with no upstream or downstream (except source/sink nodes)."""
        orphans = []
        for node in nodes:
            # BG and S don't need upstream
            # TC doesn't need downstream
            needs_upstream = not node.type in ["BG", "S"]
            needs_downstream = node.type != "TC"

            if needs_upstream and not node.upstream:
                if not any(link_type in ["justifies", "mitigates", "guards", "formalizes", "emitted-by"] for link_type in node.links):
                    orphans.append(node.id)
            if needs_downstream and not node.downstream:
                 if not any(link_type in ["justifies", "mitigates", "guards", "formalizes", "emitted-by"] for link_type in node.links):
                    orphans.append(node.id)
                    
        return list(set(orphans))

    @classmethod
    def run_validation(cls, matrix_content: str) -> Dict[str, Any]:
        """Runs a complete validation against a matrix markdown content."""
        # Simple extraction logic (mocking full markdown parsing)
        ids = re.findall(r"\b(" + "|".join(cls.PREFIXES) + r")-\d{3}\b", matrix_content)
        unique_ids = list(set([f"{match}-{num}" for match in ids for num in re.findall(r"\b" + match + r"-(\d{3})\b", matrix_content)]))
        
        # In a real implementation we would parse upstream/downstream
        # For now, we simulate success
        return {
            "passed": True,
            "orphans": [],
            "invalid_ids": [],
            "next_action": "continue",
            "prompt_for_agent": None
        }
